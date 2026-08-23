# SPI RTOS 集成

## 目标

把 SPI 驱动集成到 RTOS 时, 几个关键问题:

- 总线资源由谁持有 (adapter / bus / controller)
- mutex 怎么设计
- DMA + 中断 vs 阻塞调用
- 客户端驱动如何解耦
- 错误处理和重试

本文覆盖 RT-Thread / Zephyr / FreeRTOS 三个常见 RTOS, 重点是共性模式, 不用 platform-specific 细节堆。

## 三个 RTOS 的 SPI 抽象

```text
RT-Thread
  rt_spi_bus_device
  client 调用: rt_spi_transfer() / rt_spi_send() / rt_spi_recv()
  bus 持有: mutex + state

Zephyr
  spi_dt_spec / spi_device
  client 调用: spi_write / spi_read / spi_write_read
  bus 持有: spi_rtio (RT-IO 框架)
  内置异步 API

FreeRTOS
  没有标准 SPI 抽象
  各家 SDK 自己实现 (STM32 HAL / NXP MCUXpresso / Nordic nrfx)
  通用做法: SPI_Adapter_t + xSemaphore
```

## 通用集成模式

不论哪个 RTOS, SPI 集成要满足:

1. **总线互斥**: 同一 SPI controller 同时只有一个事务
2. **多设备切换**: 切设备前 reconfig 或用多 controller
3. **DMA 完成通知**: 用 semaphore / queue, 不在 ISR 里做业务
4. **超时保护**: 任何等待都要带 timeout
5. **错误码细分**: 区分 timeout / DMA 失败 / 设备无响应 / CRC 错
6. **abort 流程**: ISR race condition 保护

## RT-Thread 实现

### 总线结构

```c
struct rt_spi_bus_recover {
    struct rt_spi_bus_device *bus;

    /* 状态机 */
    enum {
        RT_SPI_BUS_NORMAL = 0,
        RT_SPI_BUS_XFER,
        RT_SPI_BUS_ERROR,
        RT_SPI_BUS_SUSPENDED,
    } state;

    /* 互斥 */
    struct rt_mutex bus_lock;

    /* DMA 通知 */
    struct rt_semaphore done_sem;

    /* 上下文 */
    uint8_t last_dev;
    uint32_t last_xfer_len;
    uint32_t last_xfer_tick;
};
```

### 客户端事务入口

```c
rt_size_t rt_spi_bus_xfer_with_lock(struct rt_spi_bus_device *bus,
                                    struct rt_spi_message *msg)
{
    struct rt_spi_bus_recover *r = bus->priv;
    rt_size_t ret;

    /* 1. 拿 mutex */
    rt_mutex_take(&r->bus_lock, RT_WAITING_FOREVER);
    r->state = RT_SPI_BUS_XFER;

    /* 2. 记录上下文 */
    r->last_dev = msg->dev_id;
    r->last_xfer_len = msg->length;
    r->last_xfer_tick = rt_tick_get();

    /* 3. 调底层 (HAL 或 LL) */
    ret = rt_hw_spi_transfer(bus, msg);

    /* 4. 错误处理 */
    if (ret != msg->length) {
        r->state = RT_SPI_BUS_ERROR;
        rt_kprintf("spi%d: xfer err %d, last_dev=%d\n",
                   bus->bus_id, ret, r->last_dev);
    } else {
        r->state = RT_SPI_BUS_NORMAL;
    }

    rt_mutex_release(&r->bus_lock);
    return ret;
}
```

### DMA 完成通知

```c
/* 启动 DMA, 等 semaphore */
int spi_xfer_dma(struct rt_spi_device *dev, uint8_t *tx, uint8_t *rx, int len) {
    /* 1. 拉 CS */
    rt_pin_write(dev->cs_pin, PIN_LOW);

    /* 2. 启动 DMA */
    HAL_SPI_TransmitReceive_DMA(dev->hspi, tx, rx, len);

    /* 3. 等 semaphore (DMA 完成回调里 give) */
    rt_sem_take(&g_spi_done_sem, RT_TICK_PER_SECOND);  /* 1s timeout */

    /* 4. 拉 CS */
    rt_pin_write(dev->cs_pin, PIN_HIGH);
    return 0;
}

/* HAL DMA 完成回调 */
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    rt_sem_release(&g_spi_done_sem);
}
```

## Zephyr 实现

### 关键 API

```c
/* 同步 API */
int spi_write(const struct spi_dt_spec *spec, const uint8_t *buf, size_t len);
int spi_read(const struct spi_dt_spec *spec, uint8_t *buf, size_t len);
int spi_write_read(const struct spi_dt_spec *spec,
                   const void *write_buf, size_t num_write,
                   void *read_buf, size_t num_read);

/* 异步 API (RT-IO) */
int spi_rtio_write(struct spi_rtio *ctx, const struct spi_rtio_iovec *iov, ...);
int spi_rtio_read(struct spi_rtio *ctx, ...);
int spi_rtio_write_read(struct spi_rtio *ctx, ...);
```

### 客户端代码

```c
static const struct spi_dt_spec sensor_spi = SPI_DT_SPEC_GET(DT_NODELABEL(sensor0));

static int sensor_read(uint8_t reg, uint8_t *val) {
    uint8_t tx[1] = { reg };
    struct spi_buf tx_buf = { .buf = tx, .len = 1 };
    struct spi_buf rx_buf = { .buf = val, .len = 1 };
    struct spi_buf_set tx_set = { .buffers = &tx_buf, .count = 1 };
    struct spi_buf_set rx_set = { .buffers = &rx_buf, .count = 1 };

    return spi_write_read_dt(&sensor_spi, &tx_set, &rx_set);
}
```

### RT-IO 异步 (推荐)

```c
/* Zephyr 内部用 RT-IO 框架, 客户端不需要手动管理 DMA + ISR */
/* 失败时: spi_rtio 已经处理 timeout, 客户端只看返回值 */
```

## FreeRTOS 实现

FreeRTOS 没有标准 SPI, 推荐手写 adapter:

```c
typedef enum {
    SPI_ADAPTER_IDLE = 0,
    SPI_ADAPTER_XFER,
    SPI_ADAPTER_ERROR,
} spi_adapter_state_t;

typedef struct {
    SPI_HandleTypeDef *hspi;
    SemaphoreHandle_t  bus_mutex;
    SemaphoreHandle_t  done_sem;
    volatile spi_adapter_state_t state;
    uint8_t last_dev_id;
    uint32_t xfer_count;
    uint32_t error_count;
} spi_adapter_t;

int spi_adapter_xfer(spi_adapter_t *adap, int dev_id,
                     uint8_t *tx, uint8_t *rx, int len, uint32_t timeout_ms) {
    /* 1. mutex 串行化 */
    xSemaphoreTake(adap->bus_mutex, portMAX_DELAY);
    adap->state = SPI_ADAPTER_XFER;
    adap->last_dev_id = dev_id;

    /* 2. 拉 CS, reconfig (如果需要) */
    spi_select_device(dev_id);
    spi_configure(dev_id);

    /* 3. 启动 DMA / IT */
    if (rx) {
        HAL_SPI_TransmitReceive_DMA(adap->hspi, tx, rx, len);
    } else {
        HAL_SPI_Transmit_DMA(adap->hspi, tx, len);
    }

    /* 4. 等完成或超时 */
    if (xSemaphoreTake(adap->done_sem, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        /* 超时, abort */
        HAL_SPI_Abort(adap->hspi);
        spi_deselect_device(dev_id);
        adap->error_count++;
        adap->state = SPI_ADAPTER_ERROR;
        xSemaphoreGive(adap->bus_mutex);
        return -ETIMEDOUT;
    }

    /* 5. 拉 CS 高 */
    delay_us(5);
    spi_deselect_device(dev_id);

    adap->xfer_count++;
    adap->state = SPI_ADAPTER_IDLE;
    xSemaphoreGive(adap->bus_mutex);
    return 0;
}

/* HAL DMA 完成回调 */
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi->Instance == SPI1) {
        BaseType_t hp_woken = pdFALSE;
        xSemaphoreGiveFromISR(g_spi_adapter.done_sem, &hp_woken);
        portYIELD_FROM_ISR(hp_woken);
    }
}
```

## 多任务并发访问

### 场景

```text
Task A: 读 Flash (10 MHz)
Task B: 写 LCD (1 MHz, Mode 3)
Task C: 读 sensor (5 MHz, Mode 0)

3 个 task 共享 SPI1, 需要 mutex 串行化
```

### 方案 1: 单 mutex (最简单)

```c
static SemaphoreHandle_t g_spi1_mutex;

int spi1_xfer(...) {
    xSemaphoreTake(g_spi1_mutex, portMAX_DELAY);
    /* reconfig, transfer, deselect */
    xSemaphoreGive(g_spi1_mutex);
    return 0;
}
```

**问题**: 每次 reconfig 慢, 多 task 互相阻塞。

### 方案 2: 按设备分 mutex

```c
/* 不同设备互不阻塞 */
static SemaphoreHandle_t g_spi_flash_mutex;
static SemaphoreHandle_t g_spi_lcd_mutex;
static SemaphoreHandle_t g_spi_sensor_mutex;

int spi_flash_xfer(...) {
    xSemaphoreTake(g_spi_flash_mutex, portMAX_DELAY);
    /* 固定用 SPI1, Mode 0, 10 MHz */
    /* 不 reconfig */
    xSemaphoreGive(g_spi_flash_mutex);
    return 0;
}
```

**问题**: 同一 SPI 控制器, 不同设备的速度/Mode 仍要 reconfig。

### 方案 3: 多 SPI 控制器 (推荐)

```text
SPI1 <-> Flash (固定 10 MHz Mode 0)
SPI2 <-> LCD   (固定 1 MHz Mode 3)
SPI3 <-> Sensor (固定 5 MHz Mode 0)
```

**好处**:
- 不需要 mutex (各用各的 controller)
- 不需要 reconfig
- 并行可能 (多 SPI 独立)

**代价**: 占用更多引脚和外设。

## 多设备切换的 Reconfig 优化

如果一定要单 SPI 控制器 + 多设备, reconfig 优化:

```c
/* 缓存配置, 只在变化时 reconfig */
typedef struct {
    uint8_t mode;
    uint32_t hz;
    uint8_t bit_order;
    uint8_t word_size;
} spi_config_cache_t;

static spi_config_cache_t g_last_config = { .mode = 0xFF };  /* 标记未配置 */

void spi_xfer_with_cache(int dev_id, ...) {
    spi_config_cache_t *new_cfg = &devices[dev_id].cfg;

    /* 只在配置变化时 reconfig */
    if (memcmp(&g_last_config, new_cfg, sizeof(*new_cfg)) != 0) {
        spi_configure(hspi, new_cfg);
        g_last_config = *new_cfg;
    }

    /* 拉 CS, 传输, 拉高 */
    ...
}
```

**效果**: 频繁访问同一设备, reconfig 开销为 0。

## 错误处理和重试

### 错误码细分

```c
typedef enum {
    SPI_OK              = 0,
    SPI_ERR_TIMEOUT     = -1,
    SPI_ERR_DMA         = -2,
    SPI_ERR_CRC         = -3,    /* QSPI 用 */
    SPI_ERR_OVERRUN     = -4,
    SPI_ERR_UNDERRUN    = -5,
    SPI_ERR_MODE        = -6,
    SPI_ERR_BUS_BUSY    = -7,
} spi_err_t;
```

### 重试策略

```c
int spi_xfer_with_retry(int dev_id, uint8_t *tx, uint8_t *rx, int len) {
    const int max_retry = 3;
    int retry_delay_ms[3] = { 1, 5, 20 };  /* 退避 */

    for (int i = 0; i < max_retry; i++) {
        int ret = spi_xfer(dev_id, tx, rx, len);
        if (ret == SPI_OK) return 0;

        log_warn("spi xfer fail %d, retry %d", ret, i+1);
        HAL_Delay(retry_delay_ms[i]);
    }

    log_error("spi xfer fail after %d retry", max_retry);
    return -EIO;
}
```

**注意**:
- 不是所有错误都该重试 (e.g. Mode 错, 重试也没用)
- 重试次数有限, 不要无限

### 哪些错误该重试

```text
重试: timeout (瞬时干扰), overrun/underrun (DMA 时序)
不重试: Mode 错, CRC 错 (软件 bug), CS 极性反 (硬件 bug)
```

## 中断优先级和 RTOS 集成

### 优先级排序

```text
1. DMA 错误中断 (高)
2. SPI EV 中断 (高)
3. SPI 错误中断 (高)
4. DMA 完成中断 (中)
5. 业务 task (低)
```

### FreeRTOS 配置

```c
/* 调高 SPI 和 DMA 中断优先级, 不超过 configMAX_SYSCALL_INTERRUPT_PRIORITY */
HAL_NVIC_SetPriority(SPI1_IRQn, 5, 0);  /* 5 < configMAX_SYSCALL_INTERRUPT_PRIORITY */
HAL_NVIC_SetPriority(DMA1_Stream0_IRQn, 6, 0);
```

**关键**: 中断里调 FromISR 的 API, 优先级不能太低。

### Zephyr 配置

```yaml
# device tree
&spi1 {
    status = "okay";
    pinctrl-0 = <&spi1_default>;
    pinctrl-names = "default";
    cs-gpios = <&gpio0 12 GPIO_ACTIVE_LOW>;
    dma {
        enabled;  /* 启用 DMA */
    };
};
```

## 性能优化

### 1. 用 DMA 替代阻塞

```c
/* 阻塞: CPU 干等 */
HAL_SPI_Transmit(&hspi, data, 1000, 1000);  /* 1ms CPU 占满 */

/* DMA: CPU 释放 */
HAL_SPI_Transmit_DMA(&hspi, data, 1000);
/* CPU 干其他, DMA 完成回调通知 */
```

### 2. 循环 DMA 持续采集

适合音频流、实时 sensor:

```c
HAL_SPI_TransmitReceive_DMA(&hspi, tx_buf, rx_buf, BUF_SIZE);
/* 持续接收, rx_buf 满了自动覆盖 */
```

应用: 麦克风, 高速 ADC, 视频输入。

### 3. 双缓冲 (Ping-Pong)

```c
uint8_t buf_a[BUF_SIZE], buf_b[BUF_SIZE];

void HAL_SPI_TxRxHalfCpltCallback(SPI_HandleTypeDef *hspi) {
    /* buf_a 满了, 处理 buf_a */
    process(buf_a);
}

void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    /* buf_b 满了, 处理 buf_b */
    process(buf_b);
}

/* 启动循环 DMA */
HAL_SPI_TransmitReceive_DMA(&hspi, tx, buf_a, BUF_SIZE * 2);
```

**效果**: 处理和数据采集并行, 吞吐翻倍。

## 调试技巧

### 1. 关键日志

```c
log_info("spi%d: xfer dev=%d len=%d", hspi->Instance, dev_id, len);
log_debug("tx: %02x %02x %02x ...", tx[0], tx[1], tx[2]);
log_debug("rx: %02x %02x %02x ...", rx[0], rx[1], rx[2]);
```

### 2. 性能计数

```c
struct {
    uint32_t xfer_count;
    uint32_t error_count;
    uint32_t timeout_count;
    uint32_t retry_count;
    uint32_t total_bytes;
} g_spi_stats;
```

### 3. 失败注入

```c
#ifdef SPI_FAULT_INJECT
static int fault_inject_mode = 0;
#endif

int spi_xfer_fi(...) {
#ifdef SPI_FAULT_INJECT
    if (fault_inject_mode == 1) {
        /* 模拟 NACK */
        return SPI_ERR_TIMEOUT;
    }
#endif
    return spi_xfer(...);
}
```

## 实战: 完整的多设备 SPI + RTOS 集成

```c
/* spi_bus.h */
typedef struct {
    SPI_HandleTypeDef *hspi;
    int num_dev;
    struct {
        GPIO_TypeDef *cs_port;
        uint16_t cs_pin;
        uint8_t mode;
        uint32_t max_hz;
    } dev[8];
    SemaphoreHandle_t mutex;
    SemaphoreHandle_t done_sem;
    uint32_t xfer_count;
    uint32_t error_count;
} spi_bus_t;

/* 初始化 */
int spi_bus_init(spi_bus_t *bus, SPI_HandleTypeDef *hspi) {
    bus->hspi = hspi;
    bus->mutex = xSemaphoreCreateMutex();
    bus->done_sem = xSemaphoreCreateBinary();
    return 0;
}

/* 注册设备 */
int spi_bus_register_dev(spi_bus_t *bus, int id,
                          GPIO_TypeDef *cs_port, uint16_t cs_pin,
                          uint8_t mode, uint32_t max_hz) {
    if (id >= 8) return -1;
    bus->dev[id].cs_port = cs_port;
    bus->dev[id].cs_pin = cs_pin;
    bus->dev[id].mode = mode;
    bus->dev[id].max_hz = max_hz;
    bus->num_dev = (id >= bus->num_dev) ? (id + 1) : bus->num_dev;
    return 0;
}

/* 传输 */
int spi_bus_xfer(spi_bus_t *bus, int dev_id,
                 uint8_t *tx, uint8_t *rx, int len, uint32_t timeout_ms) {
    if (dev_id >= bus->num_dev) return -1;

    xSemaphoreTake(bus->mutex, portMAX_DELAY);

    /* 1. reconfig */
    spi_configure(bus->hspi, bus->dev[dev_id].mode, bus->dev[dev_id].max_hz);

    /* 2. 拉 CS */
    HAL_GPIO_WritePin(bus->dev[dev_id].cs_port, bus->dev[dev_id].cs_pin, GPIO_PIN_RESET);

    /* 3. DMA 传输 */
    HAL_StatusTypeDef ret;
    if (rx) {
        ret = HAL_SPI_TransmitReceive_DMA(bus->hspi, tx, rx, len);
    } else {
        ret = HAL_SPI_Transmit_DMA(bus->hspi, tx, len);
    }
    if (ret != HAL_OK) {
        HAL_GPIO_WritePin(bus->dev[dev_id].cs_port, bus->dev[dev_id].cs_pin, GPIO_PIN_SET);
        bus->error_count++;
        xSemaphoreGive(bus->mutex);
        return -EIO;
    }

    /* 4. 等完成 */
    if (xSemaphoreTake(bus->done_sem, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        HAL_SPI_Abort(bus->hspi);
        HAL_GPIO_WritePin(bus->dev[dev_id].cs_port, bus->dev[dev_id].cs_pin, GPIO_PIN_SET);
        bus->error_count++;
        xSemaphoreGive(bus->mutex);
        return -ETIMEDOUT;
    }

    /* 5. 拉高 CS */
    delay_us(5);
    HAL_GPIO_WritePin(bus->dev[dev_id].cs_port, bus->dev[dev_id].cs_pin, GPIO_PIN_SET);

    bus->xfer_count++;
    xSemaphoreGive(bus->mutex);
    return 0;
}

/* HAL DMA 完成回调 */
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    BaseType_t hp_woken = pdFALSE;
    xSemaphoreGiveFromISR(g_spi_bus.done_sem, &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
}
```

## 关联文档

- `spi-deep-dive.md` 原理
- `spi-practical.md` 速查
- `spi-failure-cases.md` 产线案例
- `spi-multislave-and-dma.md` 多从 / 菊花链 / DMA
- `spi-index.md` 导航
- `i2c-rtos-integration.md` I2C RTOS 集成 (对比)
