# I2C 状态机与 DMA / 中断并发模型

## 目标

I2C 控制器 + DMA + 中断 + 多任务 并发场景下, 状态机设计是产线死机的根因区。本文讲清楚:

- 完整的状态机应该有哪些状态
- 状态转移图
- 与 DMA / 中断的协作
- 常见死锁和竞态
- 推荐的实现模式

## 为什么需要状态机

裸机 + while 轮询写法在产线遇到的问题:

```c
/* 错的裸机写法 */
HAL_I2C_Master_Transmit(..., 1000);  /* 1000ms 死等 */
if (HAL_OK != HAL_ERROR) { ... }

/* 问题:
   1. 1000ms 死等期间, 高优先级任务无法抢占 -> sensor 采样延迟
   2. ISR 已经完成了事务, 但 caller 还在 while 循环
   3. 没有状态机, 错误处理散落
   4. 重入和并发靠运气 */
```

状态机解决的问题:

- 事务进度有显式状态, 容易定位卡死点
- ISR 和线程通过状态交互, 不共享局部变量
- 超时和恢复有清晰的进入点
- 支持 cancel / abort

## 完整状态机

### 状态定义

```c
typedef enum {
    I2C_XFER_STATE_IDLE = 0,         /* 空闲, 可以发起新事务 */
    I2C_XFER_STATE_STARTING,         /* 等待 START 完成 */
    I2C_XFER_STATE_ADDR,             /* 等待地址 ACK */
    I2C_XFER_STATE_TX_DATA,          /* 发送数据中 */
    I2C_XFER_STATE_TX_ACK,           /* 等待 byte ACK */
    I2C_XFER_STATE_RX_DATA,          /* 接收数据中 */
    I2C_XFER_STATE_RX_ACK,           /* 准备发送 ACK/NACK */
    I2C_XFER_STATE_REPEATED_START,   /* Repeated START 中 */
    I2C_XFER_STATE_STOPPING,         /* 等待 STOP 完成 */
    I2C_XFER_STATE_COMPLETE,         /* 正常完成 */
    I2C_XFER_STATE_ERROR,            /* 出错 */
    I2C_XFER_STATE_ABORTING,         /* 主动 abort 中 */
    I2C_XFER_STATE_TIMEOUT,          /* 等待超时 */
    I2C_XFER_STATE_BUS_RECOVERY,     /* Bus recovery 中 */
} i2c_xfer_state_t;
```

### 状态转移图

```text
IDLE
  -> (发起事务) -> STARTING
STARTING
  -> (START 完成) -> ADDR
  -> (START 失败) -> ERROR
ADDR
  -> (ACK) -> TX_DATA (写) | RX_DATA (读) | REPEATED_START
  -> (NACK) -> ERROR
  -> (timeout) -> TIMEOUT
TX_DATA / RX_DATA
  -> (字节完成) -> TX_ACK / RX_ACK
  -> (timeout) -> TIMEOUT
  -> (ARLO) -> ABORTING
TX_ACK / RX_ACK
  -> (ACK/NACK 完成) -> TX_DATA / RX_DATA / STOPPING (最后一字节) / REPEATED_START
  -> (timeout) -> TIMEOUT
REPEATED_START
  -> (完成) -> ADDR
STOPPING
  -> (STOP 完成) -> COMPLETE
  -> (timeout) -> TIMEOUT
COMPLETE
  -> (回调) -> IDLE
ERROR / TIMEOUT
  -> (通知 caller) -> IDLE
  -> (触发 recovery) -> BUS_RECOVERY
ABORTING
  -> (abort 完成) -> ERROR
BUS_RECOVERY
  -> (成功) -> IDLE
  -> (失败) -> FAILED
```

## 实现: 状态 + ISR + 线程

### 数据结构

```c
typedef struct {
    i2c_xfer_state_t state;
    uint32_t         start_tick;        /* 事务开始时间 */
    uint32_t         stage_deadline;    /* 当前阶段 deadline */
    uint8_t          addr;
    uint8_t         *buf;
    uint16_t         len;
    uint16_t         pos;               /* 当前读写位置 */
    uint8_t          reg;               /* 寄存器地址 (可空) */
    uint8_t          flags;
    int              result;            /* 事务结果 */

    /* DMA 相关 */
    DMA_HandleTypeDef *hdma_tx;
    DMA_HandleTypeDef *hdma_rx;
    volatile bool     dma_complete_tx;
    volatile bool     dma_complete_rx;

    /* 通知机制 */
    SemaphoreHandle_t done_sem;
    TaskHandle_t      caller;
} i2c_xfer_ctx_t;
```

### 线程调用方

```c
int i2c_xfer_async(i2c_xfer_ctx_t *ctx,
                   uint8_t addr, uint8_t *buf, uint16_t len,
                   uint32_t timeout_ms)
{
    /* 1. 参数检查 + 上下文初始化 */
    memset(ctx, 0, sizeof(*ctx));
    ctx->state     = I2C_XFER_STATE_STARTING;
    ctx->addr      = addr;
    ctx->buf       = buf;
    ctx->len       = len;
    ctx->pos       = 0;
    ctx->caller    = xTaskGetCurrentTaskHandle();
    ctx->done_sem  = xSemaphoreCreateBinary();
    ctx->start_tick = xTaskGetTickCount();
    ctx->stage_deadline = ctx->start_tick + pdMS_TO_TICKS(timeout_ms);

    /* 2. 触发 START (会进 ISR) */
    LL_I2C_GenerateStart(I2C1);
    LL_I2C_EnableIT_EVT(I2C1);

    /* 3. 等事务完成 */
    if (xSemaphoreTake(ctx->done_sem, pdMS_TO_TICKS(timeout_ms + 50)) != pdTRUE) {
        /* 4. 超时, 强制 abort */
        ctx->state = I2C_XFER_STATE_ABORTING;
        i2c_force_abort(ctx);
        return -ETIMEDOUT;
    }

    return ctx->result;
}
```

### ISR 处理

```c
void I2C1_EV_IRQHandler(void)
{
    i2c_xfer_ctx_t *ctx = &g_xfer_ctx;  /* 单例, 实际从 adapter 取 */
    uint32_t isr = I2C1->ISR;

    switch (ctx->state) {
    case I2C_XFER_STATE_STARTING:
        if (isr & I2C_ISR_TXIS) {
            /* START 完成, 发地址 */
            LL_I2C_TransmitData8(I2C1, (ctx->addr << 1) | 0);
            ctx->state = I2C_XFER_STATE_ADDR;
        }
        break;

    case I2C_XFER_STATE_ADDR:
        if (isr & I2C_ISR_TXIS) {
            /* 地址已发, 等 ACK 体现在 ADDR flag */
        }
        if (isr & I2C_ISR_ADDR) {
            LL_I2C_ClearFlag_ADDR(I2C1);
            /* 判定: 写还是读 */
            if (ctx->flags & I2C_FLAG_READ) {
                ctx->state = I2C_XFER_STATE_RX_DATA;
                LL_I2C_EnableIT_RX(I2C1);
            } else {
                ctx->state = I2C_XFER_STATE_TX_DATA;
                if (ctx->len > 1) {
                    /* 启动 DMA */
                    HAL_DMA_Start_IT(ctx->hdma_tx, (uint32_t)ctx->buf, (uint32_t)&I2C1->TXDR, ctx->len);
                    LL_I2C_EnableDMAReq_TX(I2C1);
                } else {
                    LL_I2C_TransmitData8(I2C1, ctx->buf[0]);
                }
            }
            ctx->stage_deadline = xTaskGetTickCountFromISR() + pdMS_TO_TICKS(50);
        }
        break;

    case I2C_XFER_STATE_TX_DATA:
        /* DMA 模式: 字节完成由 DMA TCIF 触发, 进 DMA ISR */
        /* IT 模式: 每次 TXIS 进 ISR */
        if (isr & I2C_ISR_TC) {
            /* 全部字节发完, 发 STOP */
            ctx->state = I2C_XFER_STATE_STOPPING;
            LL_I2C_GenerateStop(I2C1);
        }
        break;

    case I2C_XFER_STATE_RX_DATA:
        if (isr & I2C_ISR_RXNE) {
            ctx->buf[ctx->pos++] = LL_I2C_ReceiveData8(I2C1);
            if (ctx->pos == ctx->len) {
                /* 最后一字节, 发 NACK */
                LL_I2C_AcknowledgeNextData(I2C1, LL_I2C_NACK);
            }
        }
        if (isr & I2C_ISR_TC) {
            ctx->state = I2C_XFER_STATE_STOPPING;
            LL_I2C_GenerateStop(I2C1);
        }
        break;

    case I2C_XFER_STATE_STOPPING:
        if (isr & I2C_ISR_STOPF) {
            LL_I2C_ClearFlag_STOP(I2C1);
            ctx->state = I2C_XFER_STATE_COMPLETE;
            ctx->result = 0;
            i2c_notify_done(ctx);  /* give semaphore */
        }
        break;

    case I2C_XFER_STATE_ABORTING:
        /* 用户层强制 abort, ISR 配合清状态 */
        LL_I2C_GenerateStop(I2C1);
        ctx->result = -ECANCELED;
        i2c_notify_done(ctx);
        break;
    }
}

void I2C1_ER_IRQHandler(void)
{
    uint32_t isr = I2C1->ISR;
    if (isr & I2C_ISR_BERR) {
        LL_I2C_ClearFlag_BERR(I2C1);
        g_xfer_ctx.result = -EIO;
        g_xfer_ctx.state  = I2C_XFER_STATE_ERROR;
        i2c_notify_done(&g_xfer_ctx);
    }
    if (isr & I2C_ISR_ARLO) {
        LL_I2C_ClearFlag_ARLO(I2C1);
        g_xfer_ctx.result = -EAGAIN;
        g_xfer_ctx.state  = I2C_XFER_STATE_ERROR;
        i2c_notify_done(&g_xfer_ctx);
    }
    if (isr & I2C_ISR_NACK) {
        LL_I2C_ClearFlag_NACK(I2C1);
        g_xfer_ctx.result = -ENACK;
        g_xfer_ctx.state  = I2C_XFER_STATE_ERROR;
        i2c_notify_done(&g_xfer_ctx);
    }
}
```

### DMA ISR

```c
void DMA1_Stream0_IRQHandler(void)  /* I2C1 TX DMA */
{
    if (DMA1->LISR & DMA_LISR_TCIF0) {
        DMA1->LIFCR = DMA_LIFCR_CTCIF0;
        /* DMA 完成, 告诉 I2C EV ISR: 数据已发完 */
        g_xfer_ctx.dma_complete_tx = true;
        /* 等待 EV ISR 处理 TC */
    }
}
```

## 常见死锁和竞态

### 竞态 1: ISR 已经 done, 但线程还在等

```c
/* 错 */
void I2C1_EV_IRQHandler(void) {
    if (isr & I2C_ISR_STOPF) {
        ctx->result = 0;             /* ISR 设置 result */
        xSemaphoreGiveFromISR(ctx->done_sem, NULL);  /* 通知 */
    }
}

int i2c_xfer_async(...) {
    xSemaphoreTake(ctx->done_sem, timeout);
    return ctx->result;  /* 可能 ISR 还没设完 result, 内存屏障没加 */
}

/* 对: 内存屏障 */
void I2C1_EV_IRQHandler(void) {
    if (isr & I2C_ISR_STOPF) {
        ctx->result = 0;
        __DSB();  /* 数据同步屏障, 确保 result 写入后再通知 */
        xSemaphoreGiveFromISR(ctx->done_sem, NULL);
    }
}

int i2c_xfer_async(...) {
    if (xSemaphoreTake(ctx->done_sem, timeout) == pdTRUE) {
        __DMB();  /* 确保读 ctx->result 前看到 ISR 的写入 */
        return ctx->result;
    }
}
```

### 竞态 2: abort 与 ISR 状态不一致

```c
/* 错: abort 时直接改 state, ISR 还在中间状态 */
void i2c_force_abort(i2c_xfer_ctx_t *ctx) {
    ctx->state = I2C_XFER_STATE_ABORTING;  /* ISR 还在 RUN */
    LL_I2C_SoftwareReset(I2C1);  /* 控制器 reset */
    /* 此时 ISR 还在等 flag, 永远不会触发 */
}

/* 对: abort 流程 */
void i2c_force_abort(i2c_xfer_ctx_t *ctx) {
    /* 1. 关闭中断, 防止 ISR 继续 */
    NVIC_DisableIRQ(I2C1_EV_IRQn);
    NVIC_DisableIRQ(I2C1_ER_IRQn);
    /* 2. 关闭 DMA */
    HAL_DMA_Abort(ctx->hdma_tx);
    HAL_DMA_Abort(ctx->hdma_rx);
    /* 3. 软件 reset I2C */
    LL_I2C_SoftwareReset(I2C1);
    /* 4. 重新 enable */
    LL_I2C_Disable(I2C1);
    LL_I2C_Enable(I2C1);
    /* 5. 清状态 */
    ctx->state = I2C_XFER_STATE_IDLE;
    ctx->result = -ECANCELED;
    /* 6. 通知 caller */
    xSemaphoreGive(ctx->done_sem);
    /* 7. 重新开中断 */
    NVIC_EnableIRQ(I2C1_EV_IRQn);
    NVIC_EnableIRQ(I2C1_ER_IRQn);
}
```

### 竞态 3: 多线程同时访问 adapter

```c
/* 错: 没 mutex, 两个线程同时用 */
void thread1() { i2c_xfer_async(...); }
void thread2() { i2c_xfer_async(...); }  /* 错! ctx 单例 */

/* 对: 用 mutex 串行化 */
static SemaphoreHandle_t g_i2c_mutex;

int i2c_xfer_async_locked(...) {
    xSemaphoreTake(g_i2c_mutex, portMAX_DELAY);
    int ret = i2c_xfer_async(...);
    xSemaphoreGive(g_i2c_mutex);
    return ret;
}
```

### 竞态 4: recovery 与普通事务并发

```c
/* 错: recovery 期间有普通事务发起 */
void i2c_xfer_async(...) {
    /* 没检查 state, 直接进 */
    if (ctx->state == I2C_XFER_STATE_BUS_RECOVERY) {
        /* 错! recovery 中不应有事务 */
    }
}

/* 对: 检查状态 */
int i2c_xfer_async(...) {
    if (ctx->state == I2C_XFER_STATE_BUS_RECOVERY) {
        return -EAGAIN;  /* 让 caller 退避重试 */
    }
    xSemaphoreTake(g_i2c_mutex, portMAX_DELAY);
    /* ... */
}
```

## 与 DMA 的协作

### 何时用 DMA

```text
适合 DMA:
  - 数据长度 > 4 字节
  - CPU 负担重 (RTOS, 多任务)
  - 高吞吐需求

不适合 DMA:
  - 数据长度 <= 4 字节 (DMA 启动开销不划算)
  - 中断很少的环境 (单任务, 中断可以处理)
  - 调试 (DMA 链路复杂, 排障难)
```

### DMA + 中断的同步

```text
场景: 用 DMA 发 100 字节

1. 线程: HAL_DMA_Start_IT(..., 100)
2. 线程: 等 done_sem
3. DMA 完成 100 字节 -> DMA TCIF
4. DMA ISR: clear TCIF, 告诉 I2C
5. I2C ISR (或下一个 DMA 中断): 检测到 TC
6. I2C ISR: generate STOP
7. I2C ISR: notify done_sem
8. 线程: 醒, 读 result
```

**关键**: 步骤 4 和 5 之间有 race condition, 必须用 volatile 标志位同步:

```c
void DMA1_Stream0_IRQHandler(void) {
    if (DMA1->LISR & DMA_LISR_TCIF0) {
        DMA1->LIFCR = DMA_LIFCR_CTCIF0;
        ctx->dma_complete_tx = true;  /* volatile, ISR 看到 */
    }
}

void I2C1_EV_IRQHandler(void) {
    /* ... */
    case I2C_XFER_STATE_TX_DATA:
        if (ctx->dma_complete_tx && (isr & I2C_ISR_TC)) {
            ctx->dma_complete_tx = false;
            ctx->state = I2C_XFER_STATE_STOPPING;
            LL_I2C_GenerateStop(I2C1);
        }
        break;
}
```

## 状态机的扩展性

### 取消 / 重试

```c
int i2c_xfer_cancel(i2c_xfer_ctx_t *ctx) {
    if (ctx->state == I2C_XFER_STATE_IDLE) {
        return 0;
    }
    ctx->state = I2C_XFER_STATE_ABORTING;
    /* 等 ISR 处理 abort */
    return 0;
}

int i2c_xfer_retry_after_error(i2c_xfer_ctx_t *ctx) {
    if (ctx->result == -EAGAIN) {
        /* 仲裁失败, 退避重试 */
        return i2c_xfer_async(ctx, ctx->addr, ctx->buf, ctx->len, ...);
    }
    if (ctx->result == -ETIMEDOUT) {
        /* 触发 recovery 然后重试 */
        schedule_recovery();
        return -EAGAIN;
    }
    return ctx->result;
}
```

### 多事务排队

```c
/* 简单队列: 事务排队, 串行执行 */
typedef struct {
    i2c_xfer_ctx_t items[8];
    uint8_t        head;
    uint8_t        tail;
    uint8_t        count;
} i2c_xfer_queue_t;

int i2c_xfer_queue(i2c_xfer_queue_t *q, i2c_xfer_ctx_t *xfer) {
    if (q->count >= 8) return -EBUSY;
    q->items[q->tail] = *xfer;
    q->tail = (q->tail + 1) % 8;
    q->count++;
    /* 如果当前空闲, 启动 */
    if (q->count == 1) {
        i2c_xfer_start(&q->items[q->head]);
    }
    return 0;
}

void i2c_xfer_done_isr() {
    /* 当前事务完成 */
    q->head = (q->head + 1) % 8;
    q->count--;
    if (q->count > 0) {
        i2c_xfer_start(&q->items[q->head]);
    }
}
```

## 测试

### 单元测试

```c
/* test_state_machine.c */
void test_normal_xfer() {
    init_ctx(&ctx);
    ctx.state = IDLE;
    /* 模拟 START 完成 */
    i2c_isr_simulate_start_complete();
    assert(ctx.state == ADDR);
    /* 模拟 ACK */
    i2c_isr_simulate_ack();
    assert(ctx.state == TX_DATA);
    /* 模拟 byte 完成 */
    i2c_isr_simulate_tx_byte();
    assert(ctx.state == TX_ACK);
    /* 模拟最后一个 byte */
    i2c_isr_simulate_tx_last_byte();
    assert(ctx.state == STOPPING);
    /* 模拟 STOP */
    i2c_isr_simulate_stop();
    assert(ctx.state == COMPLETE);
}

void test_timeout() {
    init_ctx(&ctx);
    ctx.state = ADDR;
    /* 等 deadline 过期 */
    vTaskDelay(pdMS_TO_TICKS(100));
    i2c_check_deadline(&ctx);
    assert(ctx.state == TIMEOUT);
}
```

### 集成测试

```text
- 正常事务 1000 次
- 注入 NACK, 验证 -ENACK 返回
- 注入 ARLO, 验证 -EAGAIN + retry
- 注入 SDA 低, 验证 timeout + recovery
- 高优先级任务抢占, 验证状态机不乱
- DMA 被打断, 验证 abort 流程
```

## 关联文档

- `i2c-deep-dive.md` 原理
- `i2c-bus-recovery-playbook.md` 实战 SOP
- `i2c-rtos-integration.md` RTOS 集成
- `i2c-multimaster.md` 多 master
- `i2c-smbus-timeout.md` SMBus timeout
