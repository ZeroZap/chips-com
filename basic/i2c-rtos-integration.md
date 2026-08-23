# I2C RTOS 集成

## 目标

把 I2C Bus Recovery 集成到 RTOS 驱动框架里。覆盖 RT-Thread / Zephyr / FreeRTOS 三个常见 RTOS 的不同抽象层级, 重点是:

- 总线资源由谁持有 (adapter / bus / controller)
- mutex 怎么设计才能避免恢复动作被并发打断
- 恢复动作放哪里: ISR / 线程 / workqueue
- 客户端驱动如何与 bus 层解耦

## 三个 RTOS 的总线抽象差异

```text
RT-Thread
  rt_i2c_bus_device
    -> ops: master_xfer / slave_xfer / i2c_bus_control
  client 调用: rt_i2c_transfer()
  bus 持有: mutex + state

Zephyr
  i2c_dt_spec / i2c_device
  client 调用: i2c_write / i2c_read / i2c_write_read / i2c_rtio_write
  bus 持有: i2c_rtio (RT-IO 框架)
  recovery: i2c_recover_bus() (内核 API)

FreeRTOS
  没有标准 I2C 抽象
  各家 SDK 自己实现 (STM32 HAL / NXP MCUXpresso / Nordic nrfx)
  通用做法: I2C_Adapter_t 结构体 + xSemaphore + xTask
```

## 通用集成模式

不论哪个 RTOS, bus recovery 的集成都要满足:

1. **总线互斥**: 同一 bus 同一时刻只有一个事务在跑
2. **恢复互斥**: recovery 期间禁止普通事务
3. **恢复在工作线程**: 严禁在 ISR 里跑 9 个 SCL + STOP
4. **状态机**: Normal / Transfer / Recovering / Failed / Suspended
5. **错误码**: 必须区分 NACK / timeout / arbitration / busy / recover_fail
6. **可观测**: 计数器 + 日志, 不能 "恢复完就算了"

## RT-Thread 实现

### 总线结构

```c
struct rt_i2c_bus_recover {
    /* 平台无关 ops */
    const struct i2c_recovery_ops *ops;
    void *ctx;

    /* 状态机 */
    enum {
        RT_I2C_BUS_NORMAL = 0,
        RT_I2C_BUS_XFER,
        RT_I2C_BUS_RECOVERING,
        RT_I2C_BUS_FAILED,
        RT_I2C_BUS_SUSPENDED,
    } state;

    /* 恢复触发 */
    struct rt_work recover_work;     /* 恢复动作放在 workqueue */
    struct rt_mutex bus_lock;        /* 总线锁 */
    rt_tick_t recover_deadline;      /* 恢复超时 */

    /* 计数 */
    atomic_t recover_count;
    atomic_t recover_fail_count;
    atomic_t xfer_timeout_count;
    atomic_t xfer_nack_count;
    atomic_t xfer_arbitration_lost;

    /* 上下文 (产线定位用) */
    uint8_t  last_addr;
    uint8_t  last_reg;
    uint16_t last_xfer_stage;
    uint32_t last_xfer_flags;
};
```

### 客户端事务入口

```c
rt_size_t rt_i2c_bus_xfer_recoverable(struct rt_i2c_bus_device *bus,
                                      struct rt_i2c_msg msgs[],
                                      rt_size_t num)
{
    struct rt_i2c_bus_recover *r = bus->priv;
    rt_size_t ret;
    rt_tick_t deadline = rt_tick_get() + RT_TICK_PER_SECOND;  /* 1s */

    /* 1. 等总线空闲, 不允许绕过 */
    while (atomic_load(&r->state) != RT_I2C_BUS_NORMAL) {
        if (r->state == RT_I2C_BUS_RECOVERING) {
            rt_kprintf("i2c%d: bus recovering, retry later\n", bus->bus_id);
            rt_thread_mdelay(5);
        } else if (r->state == RT_I2C_BUS_FAILED) {
            return -EIO;
        } else if (r->state == RT_I2C_BUS_SUSPENDED) {
            return -ENODEV;
        }
        if (rt_tick_get() > deadline) {
            atomic_fetch_add(&r->xfer_timeout_count, 1);
            return -ETIMEDOUT;
        }
    }

    /* 2. 拿 bus lock */
    rt_mutex_take(&r->bus_lock, RT_WAITING_FOREVER);
    atomic_store(&r->state, RT_I2C_BUS_XFER);

    /* 3. 记上下文 */
    r->last_addr = msgs[0].addr;
    r->last_reg  = (msgs[0].flags & RT_I2C_WR)
                   ? msgs[0].buf[0] : 0;
    r->last_xfer_stage = XFER_STAGE_START;

    /* 4. 跑事务, 带 deadline */
    ret = bus->ops->master_xfer(bus, msgs, num);

    /* 5. 失败判定: 哪些错误触发恢复 */
    if (ret != num) {
        if (ret == -ETIMEDOUT) {
            atomic_fetch_add(&r->xfer_timeout_count, 1);
            r->last_xfer_stage = XFER_STAGE_TIMEOUT;
            /* 异步触发恢复 */
            rt_work_submit(&r->recover_work, 0);
        } else if (ret == -ENACK) {
            atomic_fetch_add(&r->xfer_nack_count, 1);
            /* NACK 不一定需要恢复, 由 caller 决定重试 */
        } else if (ret == -EIO) {
            /* ARLO 等, 视情况 */
        }
    }

    atomic_store(&r->state, RT_I2C_BUS_NORMAL);
    rt_mutex_release(&r->bus_lock);

    return ret;
}
```

### 恢复 workqueue

```c
static void i2c_recover_work_handler(struct rt_work *work, void *data)
{
    struct rt_i2c_bus_recover *r =
        rt_container_of(work, struct rt_i2c_bus_recover, recover_work);
    struct rt_i2c_bus_device *bus = r->bus;

    /* 1. 切状态, 禁止新事务 */
    atomic_store(&r->state, RT_I2C_BUS_RECOVERING);

    /* 2. 拿 mutex (此时可能其他线程正持有, 等) */
    rt_mutex_take(&r->bus_lock, RT_WAITING_FOREVER);

    /* 3. 调平台无关的恢复函数 */
    int ret = i2c_bus_recover(r->ops, r->ctx);
    atomic_fetch_add(&r->recover_count, 1);

    if (ret != 0) {
        atomic_fetch_add(&r->recover_fail_count, 1);
        atomic_store(&r->state, RT_I2C_BUS_FAILED);
        /* 上报 */
        rt_kprintf("i2c%d: recovery failed err=%d addr=0x%02x\n",
                   bus->bus_id, ret, r->last_addr);
    } else {
        atomic_store(&r->state, RT_I2C_BUS_NORMAL);
        rt_kprintf("i2c%d: recovery ok addr=0x%02x\n",
                   bus->bus_id, r->last_addr);
    }

    rt_mutex_release(&r->bus_lock);
}

void rt_i2c_bus_recover_init(struct rt_i2c_bus_device *bus,
                             const struct i2c_recovery_ops *ops,
                             void *ctx)
{
    struct rt_i2c_bus_recover *r = rt_calloc(1, sizeof(*r));
    rt_work_init(&r->recover_work, i2c_recover_work_handler, NULL);
    rt_mutex_init(&r->bus_lock, "i2c_bus", RT_IPC_FLAG_PRIO);
    atomic_store(&r->state, RT_I2C_BUS_NORMAL);
    r->ops = ops;
    r->ctx = ctx;
    r->bus = bus;
    bus->priv = r;
}
```

### 调用流程

```text
sensor client 调 rt_i2c_transfer()
  -> rt_i2c_bus_xfer_recoverable()
       -> 拿 mutex, 记上下文
       -> 调 master_xfer (带 timeout)
            失败: rt_work_submit(&recover_work)
       -> 释放 mutex
  -> 异步: workqueue 跑 recover_work_handler
            -> 切 RECOVERING 状态
            -> 拿 mutex
            -> i2c_bus_recover()
            -> 释放 mutex
            -> 切 NORMAL 或 FAILED
```

## Zephyr 实现

### 关键 API

```c
/* 内核恢复 API (Zephyr 3.4+) */
int i2c_recover_bus(const struct device *dev);

/* 客户端 API (常规) */
int i2c_write(const struct device *dev, const uint8_t *buf, size_t num_bytes, uint16_t addr);
int i2c_read(const struct device *dev, uint8_t *buf, size_t num_bytes, uint16_t addr);
int i2c_write_read(const struct device *dev, uint16_t addr,
                   const void *write_buf, size_t num_write,
                   void *read_buf, size_t num_read);

/* RT-IO 异步 API (推荐) */
int i2c_rtio_write(struct i2c_rtio *ctx, const struct i2c_rtio_iovec *iov,
                   size_t niov, uint8_t *buf, size_t buf_len, int flags);
int i2c_rtio_read(struct i2c_rtio *ctx, const struct i2c_rtio_iovec *iov, ...);
int i2c_rtio_write_read(struct i2c_rtio *ctx, const struct i2c_rtio_iovec *iov, ...);
```

### 客户端用 RT-IO

```c
static int sensor_read_reg(struct i2c_rtio *ctx, uint8_t addr, uint8_t reg, uint8_t *val)
{
    uint8_t buf[2];
    int ret;

    buf[0] = reg;

    ret = i2c_rtio_write_read(ctx,
                                &(struct i2c_rtio_iovec){
                                    .addr = addr,
                                    .buf = buf, .len = 1,
                                }, 1,
                                val, 1,
                                I2C_RTIO_IOVEC_RX);
    if (ret < 0) {
        /* Zephyr 内部已经处理 recovery, 客户端不需要手动调 */
        /* 但可以自己再调一次 i2c_recover_bus() 验证 */
        LOG_WRN("i2c rtio read fail: %d", ret);
    }
    return ret;
}
```

### 驱动层开启 recovery

Zephyr 驱动通过 `i2c_recovery_api` 自动支持:

```c
/* drivers/i2c/i2c_stm32.c (Zephyr 3.4+) */
static const struct i2c_driver_api stm32_i2c_driver_api = {
    .configure   = stm32_i2c_configure,
    .transfer    = stm32_i2c_transfer,
    .recover_bus = stm32_i2c_recover_bus,   /* 关键: 驱动实现这个 */
};
```

驱动内实现 `recover_bus`:

```c
static int stm32_i2c_recover_bus(const struct device *dev)
{
    const struct stm32_i2c_config *cfg = dev->config;
    struct stm32_i2c_data *data = dev->data;
    int ret;

    /* 1. 关 I2C */
    LL_I2C_Disable(cfg->i2c);
    /* 2. 停 DMA */
    /* 3. RCC reset */
    LL_APB1_GRP1_ForceReset(cfg->rcc_reset);
    LL_APB1_GRP1_ReleaseReset(cfg->rcc_reset);
    /* 4. GPIO 切开漏 */
    /* 5. 9~16 SCL 脉冲 + STOP */
    /* 6. 恢复 init */
    /* 7. 恢复 pinmux */

    return ret;
}
```

### Zephyr RT-IO + workqueue

```c
/* Zephyr 把恢复放在 system workqueue, 自动线程化, 不需要自己写 */
/* 客户端只需要: */
/* 1. 调 i2c_rtio_* 异步 API */
/* 2. 失败时打日志 */
/* 3. 需要 reset 设备时, 调 device_init() 或 power 域控制 */
```

## FreeRTOS 实现

FreeRTOS 没有标准 I2C, 推荐手写 adapter:

```c
typedef enum {
    I2C_ADAPTER_IDLE = 0,
    I2C_ADAPTER_XFER,
    I2C_ADAPTER_RECOVERING,
    I2C_ADAPTER_FAILED,
    I2C_ADAPTER_SUSPENDED,
} i2c_adapter_state_t;

typedef struct {
    I2C_HandleTypeDef *hi2c;
    SemaphoreHandle_t  bus_mutex;
    TaskHandle_t       recover_task;
    QueueHandle_t      recover_queue;
    volatile i2c_adapter_state_t state;
    const i2c_recovery_ops_t *recovery_ops;
    void *recovery_ctx;
} i2c_adapter_t;

static void i2c_recover_task(void *arg) {
    i2c_adapter_t *adap = (i2c_adapter_t *)arg;
    for (;;) {
        uint32_t reason;
        xQueueReceive(adap->recover_queue, &reason, portMAX_DELAY);
        xSemaphoreTake(adap->bus_mutex, portMAX_DELAY);
        adap->state = I2C_ADAPTER_RECOVERING;
        int ret = i2c_bus_recover(adap->recovery_ops, adap->recovery_ctx);
        if (ret != 0) {
            adap->state = I2C_ADAPTER_FAILED;
            log_e("i2c recovery fail %d", ret);
        } else {
            adap->state = I2C_ADAPTER_IDLE;
            log_i("i2c recovery ok");
        }
        xSemaphoreGive(adap->bus_mutex);
    }
}

int i2c_adapter_init(i2c_adapter_t *adap, I2C_HandleTypeDef *hi2c,
                     const i2c_recovery_ops_t *ops, void *ctx) {
    adap->hi2c = hi2c;
    adap->bus_mutex = xSemaphoreCreateMutex();
    adap->recover_queue = xQueueCreate(4, sizeof(uint32_t));
    adap->recovery_ops = ops;
    adap->recovery_ctx = ctx;
    xTaskCreate(i2c_recover_task, "i2c_recov", 512, adap, 5, &adap->recover_task);
    return 0;
}
```

## 三个 RTOS 的对比

| 项 | RT-Thread | Zephyr | FreeRTOS |
| --- | --- | --- | --- |
| 标准抽象 | rt_i2c_bus_device | i2c_dt_spec | 无 (各家 SDK) |
| 客户端 API | rt_i2c_transfer | i2c_write_read | 各家 |
| 同步 API | ✓ | ✓ (i2c_*) | ✓ |
| 异步 API | ✗ (用 workqueue 自实现) | ✓ (i2c_rtio_*) | ✗ (自实现) |
| 内置 recovery | ✗ (自实现) | ✓ (i2c_recover_bus) | ✗ |
| 内置 fault injection | ✗ | ✗ | ✗ |
| 适合实时性 | 中 | 高 | 取决于实现 |

**推荐**:

- 资源紧张 (Flash/RAM) → FreeRTOS + 手写 adapter
- 想要标准抽象 + 异步 → **Zephyr**
- 国产 MCU 生态 (RT-Thread) → RT-Thread, 自己加 workqueue

## 通用避坑

### 不要在 ISR 跑 recovery

```c
/* 错 */
void I2C1_ER_IRQHandler(void) {
    /* ... 错误处理 ... */
    i2c_bus_recover(&ops, &ctx);  /* 错! 9 个 SCL + STOP 在 ISR 里 = 系统崩 */
}

/* 对: ISR 只标记, 调度到 workqueue */
void I2C1_ER_IRQHandler(void) {
    BaseType_t hp_woken = pdFALSE;
    uint32_t reason = ERR_SDA_LOW;
    xQueueSendFromISR(adap->recover_queue, &reason, &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
}
```

### mutex vs 状态判断

```c
/* 错: 只看状态, 不用 mutex */
if (adap->state == I2C_ADAPTER_IDLE) {
    /* 这里可能其他线程已经切到 XFER 了 */
    adap->state = I2C_ADAPTER_XFER;
    run_xfer();
}

/* 对: mutex 串行化所有 bus 访问 */
xSemaphoreTake(adap->bus_mutex, portMAX_DELAY);
adap->state = I2C_ADAPTER_XFER;
run_xfer();
adap->state = I2C_ADAPTER_IDLE;
xSemaphoreGive(adap->bus_mutex);
```

### 客户端层不要直接调 recovery

```c
/* 错: client driver 直接调 GPIO */
int sensor_read() {
    if (HAL_I2C_Master_Transmit(...) != HAL_OK) {
        i2c_bus_recover(...);  /* 错! 多 client 并发恢复会冲突 */
    }
}

/* 对: client 只负责报告, bus 层决定何时恢复 */
int sensor_read() {
    if (HAL_I2C_Master_Transmit(...) != HAL_OK) {
        adap->xfer_err_count++;
        return -EIO;  /* bus 层会异步处理 */
    }
}
```

## 关联文档

- `i2c-bus-recovery-playbook.md` 通用 SOP + 代码骨架
- `i2c-deep-dive.md` 原理
- `i2c-state-machine.md` 状态机详解
