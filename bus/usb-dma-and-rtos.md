# USB DMA + RTOS 集成

## 目标

USB 高速 / 大量数据场景下, 必须用 DMA + RTOS 任务调度。本文讲清楚:
- USB DMA 模式 (双缓冲 / 循环 / Scatter-Gather)
- 端点状态机和 DMA 协作
- 三个 RTOS (FreeRTOS / Zephyr / RT-Thread) 集成
- 实战代码骨架

## USB DMA 模式

### 3 种 DMA 模式

```text
单次 DMA (Single):
  - 每次传输手动启动 DMA
  - 适合: 短数据, 偶尔传输

双缓冲 (Double Buffer):
  - 2 个 buffer 交替使用
  - 一个 DMA 写入, 另一个被 CPU 处理
  - 适合: 中等吞吐 (USB Full Speed)

循环 DMA (Circular):
  - 持续接收, 不断循环 buffer
  - 适合: USB 高速等时传输 (音频, 视频)
```

### 端点 DMA 模式

```c
/* STM32 HAL */
typedef struct {
    /* EP0 总是单次, 不用 DMA */
    
    /* Bulk EP 用双缓冲 */
    hdma_usb_rx.Instance = DMA1_Stream0;
    hdma_usb_rx.Init.Mode = DMA_NORMAL;  /* 配合 USB 控制器双缓冲 */
    
    /* Interrupt EP 用循环 */
    hdma_usb_audio.Instance = DMA1_Stream1;
    hdma_usb_audio.Init.Mode = DMA_CIRCULAR;
} usb_dma_ctx_t;
```

### STM32 USB DMA 实战

```c
/* Bulk OUT 接收 (双缓冲) */
uint8_t rx_buf_a[512], rx_buf_b[512];

void usb_start_bulk_out(uint8_t ep_num) {
    /* 启动双缓冲 DMA */
    HAL_PCDEx_PMAConfig(&hpcd, 0x00 + ep_num, PCD_SNG_BUF, 0);  /* buf A */
    HAL_PCDEx_PMAConfig(&hpcd, 0x00 + ep_num, PCD_DBL_BUF, 0x100);  /* buf B */
    HAL_PCD_EP_Receive(&hpcd, ep_num, rx_buf_a, 512);
}

/* Bulk IN 发送 (单次) */
void usb_start_bulk_in(uint8_t ep_num, uint8_t *data, int len) {
    HAL_PCD_EP_Transmit(&hpcd, ep_num, data, len);
}
```

### 高速 ISO 传输 (DMA 双缓冲)

```c
/* USB Audio Speaker 例: 高速 ISO OUT */
uint8_t audio_buf_a[1024], audio_buf_b[1024];

void usb_start_audio_out() {
    /* 配置双缓冲 */
    HAL_PCDEx_PMAConfig(&hpcd, AUDIO_EP_OUT, PCD_SNG_BUF, 0);
    HAL_PCDEx_PMAConfig(&hpcd, AUDIO_EP_OUT, PCD_DBL_BUF, 0x400);
    HAL_PCD_EP_Receive(&hpcd, AUDIO_EP_OUT, audio_buf_a, 1024);
}

/* DMA 完成回调 */
void HAL_PCD_DataOutStageCallback(PCD_HandleTypeDef *hpcd, uint8_t epnum) {
    if (epnum == AUDIO_EP_OUT) {
        /* 切换 buffer */
        if (current_buf == BUF_A) {
            HAL_PCD_EP_Receive(hpcd, epnum, audio_buf_b, 1024);
            process_audio(audio_buf_a, 1024);
        } else {
            HAL_PCD_EP_Receive(hpcd, epnum, audio_buf_a, 1024);
            process_audio(audio_buf_b, 1024);
        }
    }
}
```

## 端点状态机

### 4 个状态

```text
IDLE:    空闲, 可以收发
BUSY:    正在 DMA 传输
HALT:    端点停止, host 发 CLEAR_FEATURE 才恢复
STALL:   错误, 需要 host 干预
```

### 状态转移

```text
IDLE
  |   ↓ usb_ep_transmit / receive
  |
BUSY
  |   ↓ DMA 完成
  |
IDLE
  |
  |   ↓ 错误
  |
STALL (host 发 CLEAR_FEATURE -> IDLE)
  |
  |   ↓ 主动停
  |
HALT (host 发 CLEAR_FEATURE -> IDLE)
```

### 实战: 端点管理

```c
typedef enum {
    EP_STATE_IDLE = 0,
    EP_STATE_BUSY,
    EP_STATE_HALT,
    EP_STATE_STALL,
} ep_state_t;

typedef struct {
    uint8_t ep_addr;
    ep_state_t state;
    uint16_t max_packet_size;
    uint8_t type;  /* Control, Bulk, Interrupt, Iso */
    uint8_t *xfer_buf;
    uint32_t xfer_len;
    uint32_t xfer_actual;
    bool double_buf;
    uint8_t *alt_buf;
} ep_ctx_t;

void ep_start_xfer(ep_ctx_t *ep, uint8_t *buf, uint32_t len) {
    if (ep->state != EP_STATE_IDLE) return;
    ep->xfer_buf = buf;
    ep->xfer_len = len;
    ep->xfer_actual = 0;
    ep->state = EP_STATE_BUSY;
    HAL_PCD_EP_Receive(&hpcd, ep->ep_addr, buf, len);
}

void ep_xfer_complete(ep_ctx_t *ep, uint32_t actual) {
    ep->xfer_actual = actual;
    ep->state = EP_STATE_IDLE;
    if (ep->on_complete) {
        ep->on_complete(ep);
    }
}
```

## FreeRTOS 集成

### USB Adapter 模式

```c
typedef struct {
    PCD_HandleTypeDef *hpcd;
    SemaphoreHandle_t bus_mutex;
    SemaphoreHandle_t ep_in_sem[4];   /* IN 端点发送完成 */
    SemaphoreHandle_t ep_out_sem[4];  /* OUT 端点接收完成 */
    QueueHandle_t ctrl_queue;         /* 控制请求队列 */
} usb_adapter_t;

int usb_adapter_init(usb_adapter_t *adap, PCD_HandleTypeDef *hpcd) {
    adap->hpcd = hpcd;
    adap->bus_mutex = xSemaphoreCreateMutex();
    for (int i = 0; i < 4; i++) {
        adap->ep_in_sem[i] = xSemaphoreCreateBinary();
        adap->ep_out_sem[i] = xSemaphoreCreateBinary();
    }
    adap->ctrl_queue = xQueueCreate(8, sizeof(usb_setup_t));
    return 0;
}

int usb_send_bulk(usb_adapter_t *adap, uint8_t ep, uint8_t *data, int len, uint32_t timeout) {
    xSemaphoreTake(adap->bus_mutex, portMAX_DELAY);
    HAL_PCD_EP_Transmit(adap->hpcd, ep, data, len);
    if (xSemaphoreTake(adap->ep_in_sem[ep & 0x7F], pdMS_TO_TICKS(timeout)) != pdTRUE) {
        xSemaphoreGive(adap->bus_mutex);
        return -ETIMEDOUT;
    }
    xSemaphoreGive(adap->bus_mutex);
    return 0;
}

int usb_recv_bulk(usb_adapter_t *adap, uint8_t ep, uint8_t *data, int len, uint32_t timeout) {
    xSemaphoreTake(adap->bus_mutex, portMAX_DELAY);
    HAL_PCD_EP_Receive(adap->hpcd, ep, data, len);
    if (xSemaphoreTake(adap->ep_out_sem[ep & 0x7F], pdMS_TO_TICKS(timeout)) != pdTRUE) {
        xSemaphoreGive(adap->bus_mutex);
        return -ETIMEDOUT;
    }
    xSemaphoreGive(adap->bus_mutex);
    return 0;
}

/* 中断回调 */
void HAL_PCD_DataInStageCallback(PCD_HandleTypeDef *hpcd, uint8_t epnum) {
    BaseType_t hp_woken = pdFALSE;
    xSemaphoreGiveFromISR(g_usb_adapter.ep_in_sem[epnum], &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
}

void HAL_PCD_DataOutStageCallback(PCD_HandleTypeDef *hpcd, uint8_t epnum) {
    BaseType_t hp_woken = pdFALSE;
    xSemaphoreGiveFromISR(g_usb_adapter.ep_out_sem[epnum], &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
}
```

## Zephyr USB 集成

Zephyr 内置 USB 协议栈, 推荐使用:

```c
#include <zephyr/usb/usb_device.h>
#include <zephyr/usb/class/usb_cdc.h>

/* 启用 USB 设备 */
USB_DEVICE_DEFINE(usb_dev,
                 DEVICE_DT_GET(DT_NODELABEL(zephyr_udc0)),
                 0x1234, 0x5678,  /* VID / PID */
                 "ACME Corp",
                 "ACME USB Device",
                 "0001"
);

/* CDC ACM 类 */
USB_CDC_ACM_DEFINE(cdc_acm, &usb_dev);

/* 回调 */
static void cdc_rx_handler(const struct device *dev) {
    uint8_t buf[64];
    int len = cdc_acm_read(dev, buf, sizeof(buf), NULL);
    if (len > 0) {
        cdc_acm_write(dev, buf, len, NULL);
    }
}

int main() {
    /* 注册接收回调 */
    cdc_acm_set_rx_handler(&cdc_acm, cdc_rx_handler);
    /* 启用 USB */
    usb_enable(&usb_dev);
    return 0;
}
```

## RT-Thread USB 集成

```c
#include <rtthread.h>
#include <rtdevice.h>

/* RT-Thread USB device 框架 */
struct udevice udev;
struct ufunction_ops ops;

/* 注册 CDC ACM 类 */
rt_device_t cdc_dev = rt_device_find("cdc0");
rt_device_open(cdc_dev, RT_DEVICE_FLAG_RDWR);

/* 接收 */
uint8_t buf[64];
rt_size_t len = rt_device_read(cdc_dev, 0, buf, sizeof(buf));

/* 发送 */
rt_device_write(cdc_dev, 0, buf, len);
```

## 多任务并发

### 场景

```text
Task A: USB CDC 串口 (printf)
Task B: USB HID 触摸数据处理
Task C: USB MSC 文件读写
Task D: USB DFU 升级模式

多个 Class 在同一个 USB 控制器
```

### 单 mutex + 端点分

```c
static SemaphoreHandle_t g_usb_mutex;

int usb_send(ep_ctx_t *ep, uint8_t *data, int len) {
    xSemaphoreTake(g_usb_mutex, portMAX_DELAY);
    HAL_PCD_EP_Transmit(&hpcd, ep->ep_addr, data, len);
    /* 等发送完成 */
    xSemaphoreTake(ep->done_sem, pdMS_TO_TICKS(1000));
    xSemaphoreGive(g_usb_mutex);
    return 0;
}
```

### 端点分 mutex (推荐)

```c
/* 不同端点互不阻塞 */
static SemaphoreHandle_t g_ep_mutex[8];

int usb_send_ep(ep_ctx_t *ep, uint8_t *data, int len) {
    xSemaphoreTake(g_ep_mutex[ep->ep_num], portMAX_DELAY);
    HAL_PCD_EP_Transmit(&hpcd, ep->ep_addr, data, len);
    xSemaphoreTake(ep->done_sem, pdMS_TO_TICKS(1000));
    xSemaphoreGive(g_ep_mutex[ep->ep_num]);
    return 0;
}
```

## 中断优先级

### 关键原则

```text
USB 中断优先级:
  - USB 事件中断: 优先级高 (1-2)
  - USB 错误中断: 优先级高 (1-2)
  - USB EP DMA 中断: 优先级中 (3-4)
  - USB SOF 中断: 优先级低 (5-6, 高速 ISO 传输必须)

其他外设:
  - SysTick: 最低
  - 业务 task: 最低
```

### STM32 HAL 配置

```c
/* USB 中断优先级 */
HAL_NVIC_SetPriority(USB_LP_IRQn, 1, 0);     /* USB 事件, 高优先级 */
HAL_NVIC_SetPriority(USB_HP_IRQn, 1, 0);     /* USB 高速 ISO, 高优先级 */
HAL_NVIC_SetPriority(USBWakeUp_IRQn, 1, 0);  /* USB 唤醒, 高优先级 */

/* DMA 中断 */
HAL_NVIC_SetPriority(DMA1_Stream0_IRQn, 3, 0);  /* USB RX DMA */
HAL_NVIC_SetPriority(DMA1_Stream1_IRQn, 3, 0);  /* USB TX DMA */
```

## 缓存一致性 (Cortex-M7)

### Cache + DMA 问题

```text
Cortex-M7 带 D-Cache:
  - CPU 写数据先到 cache, 不一定到主存
  - DMA 读主存, 读不到最新数据
  - CPU 读 cache, 看不到 DMA 写入

解决:
  - DMA 发送前: SCB_CleanDCache_by_Addr (CPU -> 主存)
  - DMA 接收后: SCB_InvalidateDCache_by_Addr (主存 -> CPU)
```

### 实战

```c
/* DMA 发送前 */
uint8_t tx_buf[64] = "Hello, USB!";
SCB_CleanDCache_by_Addr((uint32_t *)tx_buf, sizeof(tx_buf));
HAL_PCD_EP_Transmit(&hpcd, EP_IN, tx_buf, sizeof(tx_buf));

/* DMA 接收后 */
HAL_PCD_EP_Receive(&hpcd, EP_OUT, rx_buf, sizeof(rx_buf));
/* 等接收完成 */
SCB_InvalidateDCache_by_Addr((uint32_t *)rx_buf, sizeof(rx_buf));
/* 现在 rx_buf 是 DMA 写入的最新数据 */
```

## 性能优化

### 1. DMA 双缓冲

适合 USB 高速等时传输:

```c
/* USB Audio: 高速 ISO OUT, 双缓冲 */
uint8_t audio_buf_a[1024], audio_buf_b[1024];

void audio_isr(uint8_t ep_num) {
    if (current_buf == BUF_A) {
        HAL_PCD_EP_Receive(&hpcd, ep_num, audio_buf_b, 1024);
        /* 处理 audio_buf_a */
        audio_process(audio_buf_a, 1024);
    } else {
        HAL_PCD_EP_Receive(&hpcd, ep_num, audio_buf_a, 1024);
        audio_process(audio_buf_b, 1024);
    }
}
```

### 2. 零拷贝 (Zero Copy)

```c
/* 接收时直接给应用层指针, 不拷贝 */
int usb_recv_zc(ep_ctx_t *ep, const uint8_t **data, uint32_t *len) {
    *data = ep->xfer_buf;
    *len = ep->xfer_actual;
    return 0;
}
```

### 3. 批量预取

```c
/* 多个请求打包发 */
int usb_send_batch(ep_ctx_t *ep, usb_request_t *reqs, int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        memcpy(ep->xfer_buf + total, reqs[i].data, reqs[i].len);
        total += reqs[i].len;
    }
    return usb_send(ep, ep->xfer_buf, total);
}
```

## 实战: USB CDC 串口 RTOS 完整集成

```c
/* usb_cdc_rtos.c - USB CDC 串口 RTOS 完整实现 */

#include "FreeRTOS.h"
#include "semphr.h"

typedef struct {
    PCD_HandleTypeDef *hpcd;
    uint8_t ep_in;
    uint8_t ep_out;
    SemaphoreHandle_t tx_done_sem;
    SemaphoreHandle_t rx_done_sem;
    QueueHandle_t rx_queue;
    volatile bool tx_busy;
} usb_cdc_ctx_t;

usb_cdc_ctx_t g_cdc;

int usb_cdc_init(usb_cdc_ctx_t *ctx, PCD_HandleTypeDef *hpcd) {
    ctx->hpcd = hpcd;
    ctx->ep_in = 0x81;
    ctx->ep_out = 0x01;
    ctx->tx_done_sem = xSemaphoreCreateBinary();
    ctx->rx_done_sem = xSemaphoreCreateBinary();
    ctx->rx_queue = xQueueCreate(256, 1);
    return 0;
}

int usb_cdc_tx(usb_cdc_ctx_t *ctx, const uint8_t *data, int len, uint32_t timeout_ms) {
    if (ctx->tx_busy) return -EBUSY;
    ctx->tx_busy = true;
    
    SCB_CleanDCache_by_Addr((uint32_t *)data, len);
    HAL_PCD_EP_Transmit(ctx->hpcd, ctx->ep_in, (uint8_t *)data, len);
    
    if (xSemaphoreTake(ctx->tx_done_sem, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        HAL_PCD_EP_SetStall(ctx->hpcd, ctx->ep_in);
        ctx->tx_busy = false;
        return -ETIMEDOUT;
    }
    
    ctx->tx_busy = false;
    return len;
}

int usb_cdc_rx(usb_cdc_ctx_t *ctx, uint8_t *data, int max_len, uint32_t timeout_ms) {
    if (xQueueReceive(ctx->rx_queue, data, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        return 0;
    }
    return 1;
}

/* 中断回调 */
void HAL_PCD_DataInStageCallback(PCD_HandleTypeDef *hpcd, uint8_t epnum) {
    if (epnum == (g_cdc.ep_in & 0x7F)) {
        BaseType_t hp_woken = pdFALSE;
        xSemaphoreGiveFromISR(g_cdc.tx_done_sem, &hp_woken);
        portYIELD_FROM_ISR(hp_woken);
    }
}

void HAL_PCD_DataOutStageCallback(PCD_HandleTypeDef *hpcd, uint8_t epnum) {
    if (epnum == g_cdc.ep_out) {
        /* 启动下次接收 */
        uint8_t buf[64];
        HAL_PCD_EP_Receive(hpcd, epnum, buf, 64);
        SCB_InvalidateDCache_by_Addr((uint32_t *)buf, 64);
        /* 写入队列 */
        for (int i = 0; i < 64; i++) {
            xQueueSendFromISR(g_cdc.rx_queue, &buf[i], NULL);
        }
    }
}

/* RX 任务 */
void usb_cdc_rx_task(void *arg) {
    uint8_t byte;
    while (1) {
        if (usb_cdc_rx(&g_cdc, &byte, 1, portMAX_DELAY) > 0) {
            /* 处理字节 (e.g. printf 转发) */
            process_byte(byte);
        }
    }
}
```

## 7 条 USB DMA 常见错误

| # | 错误 | 后果 |
| --- | --- | --- |
| 1 | DMA 收发前未 Clean/Invalidate Cache | 数据不一致 (Cortex-M7) |
| 2 | 中断优先级错 (USB < DMA) | 端点 stall |
| 3 | 双缓冲配错 | 丢数据 |
| 4 | DMA 通道冲突 | 系统死机 |
| 5 | EP 地址错 (1 vs 0x81) | 枚举失败 |
| 6 | 端点未及时重启接收 | 后续数据丢失 |
| 7 | 大量数据用单次 DMA | 长时间 CPU 占用 |

## 关联文档

- `usb-deep-dive.md` 原理
- `usb-practical.md` 速查
- `usb-failure-cases.md` 产线案例
- `usb-enumeration-and-descriptors.md` 枚举
- `usb-class-drivers.md` CDC / HID / MSC / DFU
- `usb-vs-other-bus.md` 跨总线对比
- `usb-index.md` 导航
- `usb-dfu-deep-dive.md` DFU 协议
- `usb-dfu-practical.md` DFU 实战
- `i2c-state-machine.md` I2C 状态机 (对比)
- `uart-dma-circular-and-rtos.md` UART DMA (对比)
