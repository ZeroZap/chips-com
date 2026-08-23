# UART DMA + 环形缓冲 + RTOS 集成

## 目标

UART 在 RTOS + 高速 + 长数据场景下, 必须用 DMA + 环形缓冲。本文讲清楚:
- DMA 接收 vs 中断接收
- 环形缓冲实现
- Idle 中断实现"不定长接收"
- RTOS 集成模式 (FreeRTOS / Zephyr / RT-Thread)
- 多任务并发访问
- 实战代码骨架

## 为什么需要 DMA + 环形缓冲

### 3 种接收模式对比

```text
模式 1: 轮询接收
  - CPU 死等 UART, 完全占用
  - 不能干其他事
  - 产线禁用

模式 2: 中断接收 (字节中断)
  - 每字节进一次中断
  - 高速 (>= 115200) 时中断频繁
  - CPU 浪费在中断上下文
  - 适合低速

模式 3: DMA + 环形缓冲 (推荐)
  - DMA 搬运, CPU 0 负担
  - 中断只在 idle 或 DMA 半满/全满时触发
  - 适合高速 + 大数据
```

### 性能对比

| 模式 | 1M baud 接收 1KB 数据 | CPU 占用 |
| --- | --- | --- |
| 轮询 | 8.68ms 全占 | 100% |
| 字节中断 | 8.68ms, 1000 次中断 | ~30% |
| DMA + idle | 8.68ms, 1 次中断 | < 1% |

## 环形缓冲 (Ring Buffer)

### 数据结构

```c
typedef struct {
    uint8_t *buf;
    uint16_t size;        /* 必须是 2 的幂, 方便 mod */
    volatile uint16_t head;  /* 写指针 (生产者) */
    volatile uint16_t tail;  /* 读指针 (消费者) */
} ring_buf_t;

void ring_buf_init(ring_buf_t *rb, uint8_t *buf, uint16_t size) {
    rb->buf = buf;
    rb->size = size;
    rb->head = 0;
    rb->tail = 0;
}

int ring_buf_put(ring_buf_t *rb, uint8_t byte) {
    uint16_t next = (rb->head + 1) % rb->size;
    if (next == rb->tail) {
        return -1;  /* 满 */
    }
    rb->buf[rb->head] = byte;
    rb->head = next;
    return 0;
}

int ring_buf_get(ring_buf_t *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return 0;  /* 空 */
    }
    *byte = rb->buf[rb->tail];
    rb->tail = (rb->tail + 1) % rb->size;
    return 1;
}

int ring_buf_size(ring_buf_t *rb) {
    return (rb->head - rb->tail + rb->size) % rb->size;
}
```

### 线程安全

```c
/* 多线程: 用 atomic 或 mutex 保护 */
/* 单生产者 (ISR) + 单消费者 (thread): volatile 够用 */
```

## DMA + Idle 中断实现

### Idle 中断原理

```text
UART 一段时间 (1 字符时间) 无数据, 触发 idle 中断
这表示"一帧数据已收完"
```

**关键**: 利用 idle 中断实现"不定长"接收, 不用预设长度。

### STM32 HAL 实现

```c
/* 启动 DMA 接收 + idle 中断 */
HAL_UARTEx_ReceiveToIdle_DMA(&huart1, rx_buf, RX_BUF_SIZE);

/* Idle 中断回调 */
void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size) {
    if (huart->Instance == USART1) {
        /* Size 字节已收到 rx_buf */
        /* 写入环形缓冲 */
        for (uint16_t i = 0; i < Size; i++) {
            ring_buf_put(&g_rx_ring, rx_buf[i]);
        }
        /* 通知 task */
        BaseType_t hp_woken = pdFALSE;
        xSemaphoreGiveFromISR(g_rx_sem, &hp_woken);
        portYIELD_FROM_ISR(hp_woken);
        /* 重新启动接收 */
        HAL_UARTEx_ReceiveToIdle_DMA(huart, rx_buf, RX_BUF_SIZE);
    }
}
```

### 完整代码骨架

```c
#define RX_BUF_SIZE  1024
static uint8_t rx_buf[RX_BUF_SIZE];
static ring_buf_t g_rx_ring;
static uint8_t g_rx_storage[2048];  /* 环形缓冲 */
static SemaphoreHandle_t g_rx_sem;

void uart_init() {
    /* 初始化环形缓冲 */
    ring_buf_init(&g_rx_ring, g_rx_storage, sizeof(g_rx_storage));
    
    /* 信号量 */
    g_rx_sem = xSemaphoreCreateBinary();
    
    /* UART 配置 */
    huart1.Init.BaudRate = 115200;
    huart1.Init.Mode = UART_MODE_TX_RX;
    HAL_UART_Init(&huart1);
    
    /* 启动 DMA + idle 接收 */
    HAL_UARTEx_ReceiveToIdle_DMA(&huart1, rx_buf, RX_BUF_SIZE);
}

/* 发送 */
int uart_send(uint8_t *data, int len, uint32_t timeout_ms) {
    /* 用 DMA 发送 */
    HAL_StatusTypeDef ret = HAL_UART_Transmit_DMA(&huart1, data, len);
    if (ret != HAL_OK) return -EIO;
    
    /* 等完成 (可以用 semaphore 或 IT 回调) */
    /* 这里简化: 轮询 TC */
    uint32_t start = HAL_GetTick();
    while (!__HAL_UART_GET_FLAG(&huart1, UART_FLAG_TC)) {
        if (HAL_GetTick() - start > timeout_ms) {
            HAL_UART_Abort(&huart1);
            return -ETIMEDOUT;
        }
    }
    return 0;
}

/* 接收: task 调用 */
int uart_receive(uint8_t *data, int max_len, uint32_t timeout_ms) {
    /* 阻塞等数据 */
    if (xSemaphoreTake(g_rx_sem, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        return 0;  /* timeout, 无数据 */
    }
    
    /* 从环形缓冲读 */
    int n = 0;
    while (n < max_len && ring_buf_get(&g_rx_ring, &data[n])) {
        n++;
    }
    return n;
}

/* 后台 task 处理接收 */
void uart_thread(void *arg) {
    uint8_t buf[256];
    while (1) {
        int n = uart_receive(buf, sizeof(buf), 1000);
        if (n > 0) {
            /* 协议解析 */
            process(buf, n);
        }
    }
}
```

## Idle 中断的时序

```text
正常情况:
  RX:  [byte0][byte1][byte2]...[byteN-1][idle]
                                 ↑
                            idle 中断触发
                            (1 字符时间无数据)

异常情况:
  RX:  [byte0][byte1][byte2]...[永远不结束]
       ↑ DMA 一直运行, 永不触发 idle
       应用层可能卡死

解决: 加总 timeout 保护, 例如 5s 没新数据就强制返回
```

### 实战: 5s timeout 保护

```c
volatile uint32_t g_last_rx_tick = 0;
volatile bool g_rx_idle = false;

void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size) {
    if (huart->Instance == USART1) {
        for (uint16_t i = 0; i < Size; i++) {
            ring_buf_put(&g_rx_ring, rx_buf[i]);
        }
        g_last_rx_tick = HAL_GetTick();
        g_rx_idle = true;
        BaseType_t hp_woken = pdFALSE;
        xSemaphoreGiveFromISR(g_rx_sem, &hp_woken);
        portYIELD_FROM_ISR(hp_woken);
        HAL_UARTEx_ReceiveToIdle_DMA(huart, rx_buf, RX_BUF_SIZE);
    }
}

int uart_receive_with_timeout(uint8_t *data, int max_len, uint32_t timeout_ms) {
    if (xSemaphoreTake(g_rx_sem, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        return 0;
    }
    int n = 0;
    while (n < max_len && ring_buf_get(&g_rx_ring, &data[n])) {
        n++;
    }
    return n;
}
```

## 环形缓冲 + 协议解析

### 文本协议 (\r\n 分帧)

```c
void uart_thread(void *arg) {
    uint8_t buf[256];
    char line[256];
    int line_pos = 0;
    while (1) {
        int n = uart_receive(buf, sizeof(buf), 1000);
        for (int i = 0; i < n; i++) {
            if (buf[i] == '\n') {
                line[line_pos] = '\0';
                /* 处理一行命令 */
                process_line(line);
                line_pos = 0;
            } else if (buf[i] != '\r' && line_pos < sizeof(line) - 1) {
                line[line_pos++] = buf[i];
            }
        }
    }
}
```

### 二进制协议 (SOF + LEN + DATA + CRC)

```c
typedef enum {
    RX_SOF = 0,
    RX_LEN_L,
    RX_LEN_H,
    RX_DATA,
    RX_CRC,
} rx_state_t;

typedef struct {
    rx_state_t state;
    uint16_t len;
    uint16_t pos;
    uint8_t crc;
    uint8_t buf[256];
} rx_parser_t;

void uart_thread(void *arg) {
    uint8_t buf[256];
    rx_parser_t p = {0};
    while (1) {
        int n = uart_receive(buf, sizeof(buf), 1000);
        for (int i = 0; i < n; i++) {
            parse_byte(&p, buf[i]);
        }
    }
}

void parse_byte(rx_parser_t *p, uint8_t byte) {
    switch (p->state) {
    case RX_SOF:
        if (byte == 0xAA) {
            p->state = RX_LEN_L;
            p->crc = 0;
        }
        break;
    case RX_LEN_L:
        p->len = byte;
        p->crc += byte;
        p->state = RX_LEN_H;
        break;
    case RX_LEN_H:
        p->len |= (byte << 8);
        p->crc += byte;
        p->state = RX_DATA;
        p->pos = 0;
        break;
    case RX_DATA:
        p->buf[p->pos++] = byte;
        p->crc += byte;
        if (p->pos >= p->len) {
            p->state = RX_CRC;
        }
        break;
    case RX_CRC:
        if (p->crc == byte) {
            /* 完整帧, 处理 */
            process_frame(p->buf, p->len);
        }
        p->state = RX_SOF;
        break;
    }
}
```

## RTOS 集成

### FreeRTOS 模式

```c
typedef struct {
    UART_HandleTypeDef *huart;
    ring_buf_t rx_ring;
    SemaphoreHandle_t rx_sem;
    SemaphoreHandle_t tx_sem;
    uint8_t *rx_buf;
    int rx_size;
} uart_ctx_t;

int uart_init_freertos(uart_ctx_t *ctx, UART_HandleTypeDef *huart,
                       uint8_t *rx_storage, int rx_storage_size,
                       uint8_t *dma_buf, int dma_buf_size) {
    ctx->huart = huart;
    ctx->rx_buf = dma_buf;
    ctx->rx_size = dma_buf_size;
    ctx->rx_sem = xSemaphoreCreateBinary();
    ctx->tx_sem = xSemaphoreCreateBinary();
    ring_buf_init(&ctx->rx_ring, rx_storage, rx_storage_size);
    HAL_UARTEx_ReceiveToIdle_DMA(huart, dma_buf, dma_buf_size);
    return 0;
}

void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size) {
    uart_ctx_t *ctx = huart_to_ctx(huart);
    for (int i = 0; i < Size; i++) {
        ring_buf_put(&ctx->rx_ring, ctx->rx_buf[i]);
    }
    BaseType_t hp_woken = pdFALSE;
    xSemaphoreGiveFromISR(ctx->rx_sem, &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
    HAL_UARTEx_ReceiveToIdle_DMA(huart, ctx->rx_buf, ctx->rx_size);
}
```

### Zephyr 模式

Zephyr 内置 UART API, 自动处理环形缓冲:

```c
const struct device *uart_dev = DEVICE_DT_GET(DT_NODELABEL(uart0));

/* 接收回调 */
static void uart_cb(const struct device *dev, struct uart_event *evt, void *user_data) {
    switch (evt->type) {
    case UART_RX_RDY:
        /* evt->data.rx.buf, evt->data.rx.len, evt->data.rx.offset */
        process(evt->data.rx.buf + evt->data.rx.offset, evt->data.rx.len);
        break;
    case UART_RX_BUF_RELEASED:
        /* buffer released */
        break;
    case UART_RX_DISABLED:
        /* rx disabled */
        break;
    }
}

int uart_zephyr_init() {
    uart_callback_set(uart_dev, uart_cb, NULL);
    uart_rx_enable(uart_dev, rx_buf, sizeof(rx_buf), 100);
    return 0;
}
```

### RT-Thread 模式

```c
/* RT-Thread 内置 UART 设备驱动 */

static rt_device_t uart_dev;

static rt_err_t uart_rx_ind(rt_device_t dev, rt_size_t size) {
    /* size 字节收到 */
    rt_sem_release(&g_rx_sem);
    return RT_EOK;
}

int uart_rtthread_init() {
    uart_dev = rt_device_find("uart1");
    rt_device_open(uart_dev, RT_DEVICE_FLAG_DMA_RX);
    rt_device_set_rx_indicate(uart_dev, uart_rx_ind);
    return 0;
}

/* 接收 task */
void uart_thread() {
    while (1) {
        rt_sem_take(&g_rx_sem, RT_WAITING_FOREVER);
        rt_size_t size = rt_device_read(uart_dev, 0, buf, sizeof(buf));
        process(buf, size);
    }
}
```

## 多任务并发

### 场景

```text
Task A: 读 GPS 模块 (UART1)
Task B: 调试 printf (UART2)
Task C: 蓝牙模块 (UART3)

3 个 task 用不同 UART, 不冲突
```

### 单 UART 多 task

```text
Task A: 业务日志
Task B: 协议解析
Task C: 调试输出
3 个 task 共享 UART1, 需要 mutex
```

### 方案 1: 单 mutex (最简单)

```c
static SemaphoreHandle_t g_uart1_mutex;

int uart1_send_safe(uint8_t *data, int len) {
    xSemaphoreTake(g_uart1_mutex, portMAX_DELAY);
    HAL_UART_Transmit_DMA(&huart1, data, len);
    /* 等 TC */
    while (!__HAL_UART_GET_FLAG(&huart1, UART_FLAG_TC));
    xSemaphoreGive(g_uart1_mutex);
    return 0;
}
```

### 方案 2: 异步日志 task (推荐)

```c
typedef struct {
    char *buf;
    uint16_t pos;
} log_msg_t;

static QueueHandle_t g_log_queue;

int log_async(const char *fmt, ...) {
    log_msg_t msg;
    msg.buf = pvPortMalloc(256);
    va_list args;
    va_start(args, fmt);
    vsnprintf(msg.buf, 256, fmt, args);
    va_end(args);
    xQueueSend(g_log_queue, &msg, portMAX_DELAY);
    return 0;
}

void log_task(void *arg) {
    while (1) {
        log_msg_t msg;
        if (xQueueReceive(g_log_queue, &msg, portMAX_DELAY) == pdTRUE) {
            /* 串口输出 */
            HAL_UART_Transmit_DMA(&huart1, (uint8_t *)msg.buf, strlen(msg.buf));
            while (!__HAL_UART_GET_FLAG(&huart1, UART_FLAG_TC));
            vPortFree(msg.buf);
        }
    }
}
```

**优点**: 调用者不阻塞, log 在后台 task 排队。

## 实战: 完整 FreeRTOS UART 驱动

```c
/* uart_drv.h */
typedef struct {
    UART_HandleTypeDef *huart;
    ring_buf_t rx_ring;
    uint8_t *dma_buf;
    int dma_size;
    SemaphoreHandle_t rx_sem;
    SemaphoreHandle_t tx_sem;
    volatile bool tx_busy;
    volatile uint32_t err_overrun;
    volatile uint32_t err_parity;
    volatile uint32_t err_framing;
} uart_drv_t;

int uart_drv_init(uart_drv_t *drv, UART_HandleTypeDef *huart,
                  uint8_t *rx_storage, int rx_storage_size,
                  uint8_t *dma_buf, int dma_size);
int uart_drv_send(uart_drv_t *drv, uint8_t *data, int len, uint32_t timeout_ms);
int uart_drv_recv(uart_drv_t *drv, uint8_t *data, int max_len, uint32_t timeout_ms);

/* uart_drv.c */
int uart_drv_init(uart_drv_t *drv, UART_HandleTypeDef *huart,
                  uint8_t *rx_storage, int rx_storage_size,
                  uint8_t *dma_buf, int dma_size) {
    drv->huart = huart;
    drv->dma_buf = dma_buf;
    drv->dma_size = dma_size;
    drv->rx_sem = xSemaphoreCreateBinary();
    drv->tx_sem = xSemaphoreCreateBinary();
    ring_buf_init(&drv->rx_ring, rx_storage, rx_storage_size);
    HAL_UARTEx_ReceiveToIdle_DMA(huart, dma_buf, dma_size);
    return 0;
}

int uart_drv_send(uart_drv_t *drv, uint8_t *data, int len, uint32_t timeout_ms) {
    if (drv->tx_busy) return -EBUSY;
    drv->tx_busy = true;
    HAL_StatusTypeDef ret = HAL_UART_Transmit_DMA(drv->huart, data, len);
    if (ret != HAL_OK) {
        drv->tx_busy = false;
        return -EIO;
    }
    if (xSemaphoreTake(drv->tx_sem, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        HAL_UART_Abort(drv->huart);
        drv->tx_busy = false;
        return -ETIMEDOUT;
    }
    /* 严格等 TC */
    while (!__HAL_UART_GET_FLAG(drv->huart, UART_FLAG_TC));
    drv->tx_busy = false;
    return 0;
}

int uart_drv_recv(uart_drv_t *drv, uint8_t *data, int max_len, uint32_t timeout_ms) {
    if (xSemaphoreTake(drv->rx_sem, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        return 0;
    }
    int n = 0;
    while (n < max_len && ring_buf_get(&drv->rx_ring, &data[n])) {
        n++;
    }
    return n;
}

/* 中断回调 */
void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size) {
    uart_drv_t *drv = huart_to_drv(huart);
    for (int i = 0; i < Size; i++) {
        ring_buf_put(&drv->rx_ring, drv->dma_buf[i]);
    }
    BaseType_t hp_woken = pdFALSE;
    xSemaphoreGiveFromISR(drv->rx_sem, &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
    HAL_UARTEx_ReceiveToIdle_DMA(huart, drv->dma_buf, drv->dma_size);
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
    uart_drv_t *drv = huart_to_drv(huart);
    BaseType_t hp_woken = pdFALSE;
    xSemaphoreGiveFromISR(drv->tx_sem, &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
}

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart) {
    uart_drv_t *drv = huart_to_drv(huart);
    uint32_t err = huart->ErrorCode;
    if (err & HAL_UART_ERROR_ORE) drv->err_overrun++;
    if (err & HAL_UART_ERROR_PE)  drv->err_parity++;
    if (err & HAL_UART_ERROR_FE)  drv->err_framing++;
    /* 关键: 清错误, 重启接收 */
    HAL_UARTEx_ReceiveToIdle_DMA(huart, drv->dma_buf, drv->dma_size);
}
```

## 中断优先级

```c
/* UART 中断优先级配置 */
HAL_NVIC_SetPriority(USART1_IRQn, 5, 0);   /* 中等 */
HAL_NVIC_SetPriority(DMA1_Stream0_IRQn, 6, 0);  /* 低 */
HAL_NVIC_SetPriority(DMA1_Stream1_IRQn, 6, 0);  /* 低 */
```

**关键**:
- UART 中断必须比 DMA 中断高 (或同优先级)
- 优先级不能超过 `configMAX_SYSCALL_INTERRUPT_PRIORITY`

## 性能优化

### 1. 环形缓冲双缓冲

```c
/* 双缓冲: 在 DMA 完成后, 立即切换 buffer */
typedef struct {
    uint8_t *buf_a;
    uint8_t *buf_b;
    uint8_t *active;
} double_buf_t;

/* DMA 半满 + 全满 回调 */
void HAL_UART_TxRxHalfCpltCallback(...) { /* buf_a 满 */ }
void HAL_UART_TxRxCpltCallback(...) { /* buf_b 满 */ }
```

### 2. 零拷贝

```c
/* 业务直接从环形缓冲读, 不拷贝 */
int uart_get_buffer(uart_drv_t *drv, const uint8_t **data, int *len) {
    /* 返回环形缓冲的指针, 不拷贝 */
}
```

### 3. 异步通知 (而不是轮询)

```c
/* 用 task notification 而不是 semaphore, 性能更好 */
void uart_thread_notify(void *arg) {
    while (1) {
        /* 阻塞等通知 */
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        /* 处理 */
    }
}
```

## 调试技巧

### 1. 关键日志

```c
log_info("uart%d: rx %d bytes, err_or=%d pe=%d fe=%d",
         huart->Instance, Size,
         drv->err_overrun, drv->err_parity, drv->err_framing);
```

### 2. 性能计数

```c
struct {
    uint32_t rx_bytes_total;
    uint32_t tx_bytes_total;
    uint32_t rx_overrun;
    uint32_t rx_parity;
    uint32_t rx_framing;
    uint32_t rx_dropped;  /* 环形缓冲满 */
} g_uart_stats;
```

### 3. 失败注入

```c
#ifdef UART_FAULT_INJECT
static int fault_inject = 0;
#endif

int uart_drv_recv_fi(...) {
#ifdef UART_FAULT_INJECT
    if (fault_inject == 1) {
        return 0;  /* 模拟丢数据 */
    }
#endif
    return uart_drv_recv(...);
}
```

## 关联文档

- `uart-deep-dive.md` 原理
- `uart-practical.md` 速查
- `uart-failure-cases.md` 产线案例
- `uart-rs485-and-flow-control.md` RS485 / 流控
- `uart-index.md` 导航
- `i2c-rtos-integration.md` I2C RTOS 集成 (对比)
- `spi-rtos-integration.md` SPI RTOS 集成 (对比)
