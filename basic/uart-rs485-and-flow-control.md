# UART RS485 和流控专题

## 目标

UART 在工业 / 长距离 / 多设备场景下, 关键的两个技术:
- **RS485**: 长距离 (1km+), 差分, 多设备
- **流控**: 高速场景下防止接收方溢出

本文讲清楚:
- RS485 物理层和收发器
- RS485 方向控制的关键时序
- 硬件流控 (RTS/CTS) 和软件流控 (XON/XOFF)
- 实战代码骨架 (可拷)
- 产线常见坑

## RS485 物理层

### 拓扑

```text
Master  +-------+         +-------+ Slave 1
         |       |         |       |
         | RS485 |---------| RS485 |
         |       |         |       |
         |       |---------|       |
         |       |         |       |
Master  +-------+         +-------+ Slave 2
              |
              |         +-------+ Slave 3
              +---------|
                        |       |
                        |       |
                        +-------+
```

**关键**:
- 差分 A/B 两根线 (A+, B-)
- 总线两端各加 120 ohm 终端电阻
- 总线最长 1200m @ 9600 baud
- 半双工 (2 线) 或全双工 (4 线)
- 最多 32 个设备 (普通收发器), 用中继可扩

### 电平

```text
逻辑 1 (mark):  VA - VB >= +200mV (B 比 A 低)
逻辑 0 (space): VA - VB <= -200mV (A 比 B 低)
```

**注意**: 真正的 RS485 收发器 (e.g. MAX485) 输出是差分, MCU UART 的 TTL 信号经过收发器转成 A/B 差分。

### 典型收发器

| 型号 | 速率 | 节点数 | 隔离 | 备注 |
| --- | --- | --- | --- | --- |
| MAX485 | 2.5M | 32 | 无 | 经典 |
| MAX3485 | 12M | 32 | 无 | 高速 |
| MAX13487E | 500K | 32 | 无 | 自动方向控制 |
| ADM2483 | 500K | 32 | 有 (数字隔离) | 工业 |
| ADM2587E | 500K | 32 | 有 (磁隔离) | 工业级 |
| ISL3179E | 32M | 32 | 无 | 高速 |
| THVD1450 | 50M | 256 | 无 | TI 工业级 |

### 接线

```text
MCU  UART_TX ----+--- DI 收发器
                 |
MCU  UART_RX <---+--- RO 收发器
                 |
MCU  GPIO   -----+--- DE + RE 收发器 (DIR 控制)
                 |
A 差分线        +--- A 总线
B 差分线        +--- B 总线
```

**关键**:
- DE (Driver Enable) 高 = 发送模式
- RE (Receiver Enable) 低 = 接收模式 (注意是低有效)
- 多数应用把 DE + RE 接一起, 软件控制
- 收发器电源旁路电容要近

## RS485 方向控制

### 4 种方向控制模式

#### 模式 1: 软件控制 (最常见)

```c
#define RS485_DIR_TX  1
#define RS485_DIR_RX  0

void rs485_set_dir(uint8_t dir) {
    HAL_GPIO_WritePin(RS485_DIR_PORT, RS485_DIR_PIN, 
                      dir ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

int rs485_send(uint8_t *data, int len) {
    rs485_set_dir(RS485_DIR_TX);
    HAL_UART_Transmit(&huart1, data, len, 1000);
    rs485_set_dir(RS485_DIR_RX);  /* 立刻切回? 错! */
    return 0;
}
```

**问题**: 立刻切回接收, 但最后一字节还没真正从收发器发出。

#### 模式 2: TC 标志控制 (推荐)

```c
/* 关键: 等 TC (Transmission Complete) 再切回接收 */
int rs485_send(uint8_t *data, int len) {
    rs485_set_dir(RS485_DIR_TX);
    HAL_UART_Transmit(&huart1, data, len, 1000);
    /* 等 TC 标志, 最后一字节真正从移位寄存器发出 */
    while (!__HAL_UART_GET_FLAG(&huart1, UART_FLAG_TC));
    rs485_set_dir(RS485_DIR_RX);
    return 0;
}
```

**优点**: 严格保证最后一字节发完再切回。

#### 模式 3: HAL 库 TC 中断 (推荐)

```c
int rs485_send_async(uint8_t *data, int len) {
    rs485_set_dir(RS485_DIR_TX);
    HAL_UART_Transmit_IT(&huart1, data, len);
    /* TC 中断里切回 */
    return 0;
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        rs485_set_dir(RS485_DIR_RX);
    }
}
```

**注意**: HAL 库的 `TxCpltCallback` 触发的是 TXE (TX buffer 空), 不是 TC。
**真正要用 `UART_TxCpltCallback` 但其中调用 `__HAL_UART_GET_FLAG(huart, UART_FLAG_TC)` 等到 TC。**

```c
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        /* 严格等到 TC */
        while (!__HAL_UART_GET_FLAG(huart, UART_FLAG_TC));
        rs485_set_dir(RS485_DIR_RX);
    }
}
```

#### 模式 4: 自动方向控制 (硬件)

```text
某些收发器 (e.g. MAX13487E) 有自动方向控制:
  - 收到 TX 下降沿自动拉高 DE
  - TX 拉高后自动延迟切回
  - 不需要 MCU 控制 DIR
```

**优点**: 软件简单, 不需要管时序。
**缺点**: 收发器成本高, 适用场景有限。

### 方向切换时序细节

```text
              ┌── tx data ──┐
DIR:    _____|             |________
              ↑             ↑
              DE 拉高      等 TC 后拉低

要求:
  1. DIR 拉高 后, 等几个 bit 时间 (1-2 bit) 再发数据
     (让收发器内部电路稳定)
  2. 数据发完, 等 TC 标志 (最后一字节移位寄存器发出)
  3. 等几个 bit 时间 (guard time) 再切回接收
     (让差分线稳定, 防止回声)
```

**关键时序参数**:
- tR (DE 拉到输出有效): < 100ns
- tD (数据稳定时间): 1-2 bit
- tPLH (传播延迟): < 100ns
- Guard time: 1-3 bit

### 实战代码: 严格时序的 RS485 发送

```c
#define RS485_DIR_PORT    GPIOA
#define RS485_DIR_PIN     GPIO_PIN_8
#define RS485_DIR_TX      1
#define RS485_DIR_RX      0
#define RS485_GUARD_BITS  2  /* 等待 2 bit 时间 */

static inline void rs485_dir(uint8_t dir) {
    HAL_GPIO_WritePin(RS485_DIR_PORT, RS485_DIR_PIN, 
                      dir ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

int rs485_send_strict(uint8_t *data, int len) {
    /* 1. 切到发送模式 */
    rs485_dir(RS485_DIR_TX);
    
    /* 2. 等待收发器稳定 (1-2 bit 时间) */
    delay_us(20);  /* 115200 baud: 1 bit = 8.68us, 2 bit = 17.4us */
    
    /* 3. 发送 */
    HAL_UART_Transmit(&huart1, data, len, 1000);
    
    /* 4. 等 TC 标志 (最后一字节真正从移位寄存器发出) */
    while (!__HAL_UART_GET_FLAG(&huart1, UART_FLAG_TC));
    
    /* 5. Guard time (1-3 bit) */
    delay_us(20);
    
    /* 6. 切回接收 */
    rs485_dir(RS485_DIR_RX);
    
    return 0;
}
```

### 实战代码: DMA + TC 中断

```c
typedef enum {
    RS485_STATE_IDLE = 0,
    RS485_STATE_TX,
    RS485_STATE_WAIT_TC,
    RS485_STATE_RX,
} rs485_state_t;

volatile rs485_state_t g_rs485_state = RS485_STATE_IDLE;

int rs485_send_dma(uint8_t *data, int len) {
    if (g_rs485_state != RS485_STATE_IDLE) return -EBUSY;
    g_rs485_state = RS485_STATE_TX;
    
    rs485_dir(RS485_DIR_TX);
    delay_us(20);
    HAL_UART_Transmit_DMA(&huart1, data, len);
    return 0;
}

/* DMA 完成回调 */
void HAL_UART_TxCpltCallback(SPI_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        g_rs485_state = RS485_STATE_WAIT_TC;
        /* HAL 默认触发 TXE callback, 不是 TC */
        /* 需要手动等 TC */
    }
}

/* 定时器或主循环轮询 TC */
void rs485_poll(void) {
    if (g_rs485_state == RS485_STATE_WAIT_TC) {
        if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_TC)) {
            delay_us(20);  /* guard time */
            rs485_dir(RS485_DIR_RX);
            g_rs485_state = RS485_STATE_RX;
        }
    }
}
```

## RS485 关键参数

### 距离 vs 速率

```text
距离       最大速率          备注
10m        10M+              短距离, 高速
100m       1M                中等距离
500m       100K              长距离
1000m      10K               极限距离
1200m      9600              规范上限
```

**关键**: 距离每翻 10 倍, 速率降 10 倍左右。

### 终端电阻

```text
必须: 总线两端各 120 ohm 电阻 (A-B 之间)
不要: 中间加终端电阻 (会形成反射)
不要: 多个终端电阻并联 (等效阻值过小)
```

**判断**: 如果总线波形有反射 (上升沿有阶梯), 加终端电阻。

### 偏置电阻

```text
总线空闲时, A 和 B 应该保持稳定的差分电平 (逻辑 1)
否则: 收发器可能输出不确定
解决: 加偏置电阻, 总线一端
  A 接 560 ohm 到 VCC
  B 接 560 ohm 到 GND
```

### 拓扑

```text
推荐: 菊花链 (总线一端到另一端)
不推荐: 星形 (T 型分支)
不推荐: 长分支 (> 1m)
```

## RS485 收发器选型

### 关键参数

```text
1. 节点数: 32 (普通) / 256 (高负载)
2. 速率: 2.5M / 12M / 50M
3. 隔离: 无 / 数字隔离 / 磁隔离
4. 电源: 5V / 3.3V
5. 封装: SO-8 / DIP-8
6. ESD 保护: ±15kV (工业)
7. 共模电压: -7V ~ +12V
```

### 隔离 vs 非隔离

```text
非隔离: 简单, 便宜, 适合板内
隔离: 抗干扰, 工业级, 防地电位差
  - 数字隔离 (ADM2483): 简单, 成本低
  - 磁隔离 (ADM2587E): 强抗干扰, 工业级
  - 光耦隔离: 传统, 速度低
```

## 硬件流控 (RTS/CTS)

### 信号

```text
RTS (Request To Send): 接收方告诉发送方"我准备好接收了"
CTS (Clear To Send): 发送方告诉接收方"我可以发送了"
```

### 工作流程

```text
场景: Device A 发数据到 Device B, A 是发送方, B 是接收方

1. A 设 RTS 高 (B 收到, 表示"我可以发了")
2. A 等 CTS 高 (B 同意, 表示"我准备好了")
3. A 开始发数据
4. B 接收 buffer 快满时, 设 RTS 低 (告诉 A 暂停)
5. A 收到 RTS 低, 暂停发送
6. B 处理完, 设 RTS 高
7. A 恢复发送
```

**注意**: RTS/CTS 是**交叉连**:
- A.RTS → B.CTS
- A.CTS ← B.RTS

### 硬件流控配置

```c
/* STM32 HAL */
huart1.Init.HwFlowCtl = UART_HWCONTROL_RTS_CTS;
HAL_UART_Init(&huart1);
/* 硬件自动管理 RTS/CTS, 不需要软件干预 */
```

### 何时需要流控

```text
需要流控:
  - 高速 (>= 1M baud) 持续传输
  - 接收方处理慢 (e.g. 业务 task 阻塞)
  - 接收 buffer 较小

不需要流控:
  - 低速 (<= 115200)
  - 短消息
  - 接收 buffer 足够大 (>= 4KB)
  - 单向通信
```

### 实战: 带流控的接收

```c
typedef struct {
    UART_HandleTypeDef *huart;
    uint8_t *rx_buf;
    int rx_size;
    volatile int rx_count;
    SemaphoreHandle_t done_sem;
} uart_rx_ctx_t;

int uart_rx_start(uart_rx_ctx_t *ctx) {
    ctx->rx_count = 0;
    /* 用 DMA 接收, 硬件自动用 RTS 流控 */
    HAL_UART_Receive_DMA(ctx->huart, ctx->rx_buf, ctx->rx_size);
    return 0;
}

void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size) {
    /* 处理 Size 字节 */
    process(rx_buf, Size);
    /* 重新启动接收 */
    HAL_UART_Receive_DMA(huart, rx_buf, RX_BUF_SIZE);
}
```

## 软件流控 (XON/XOFF)

### 原理

```text
接收方 buffer 快满, 发 XOFF (0x13) 给发送方, 让它暂停
接收方 buffer 处理完, 发 XON (0x11) 给发送方, 恢复发送
```

**优点**: 不需要额外线
**缺点**: 占用 2 字节 (0x11, 0x13), 不能出现在数据中 (需要转义)

### 实现

```c
#define XON  0x11
#define XOFF 0x13

volatile bool g_xoff_received = false;

void uart_rx_byte_with_xoff(uint8_t byte) {
    if (byte == XOFF) {
        g_xoff_received = true;
        return;
    }
    if (byte == XON) {
        g_xoff_received = false;
        return;
    }
    /* 正常数据, 检查是否需要发 XOFF */
    if (rx_buf_count > RX_THRESHOLD && !g_xoff_sent) {
        uart_send_byte(XOFF);
        g_xoff_sent = true;
    }
    if (rx_buf_count < RX_THRESHOLD_LOW && g_xoff_sent) {
        uart_send_byte(XON);
        g_xoff_sent = false;
    }
    /* 写入 buffer */
    ring_buf_put(&g_rx_buf, byte);
}

void uart_tx_check_xoff(uint8_t byte) {
    /* 发送前检查 XOFF */
    while (g_xoff_received) {
        delay_us(10);
    }
    uart_send_byte(byte);
}
```

### 软件流控 vs 硬件流控

| 维度 | 硬件 RTS/CTS | 软件 XON/XOFF |
| --- | --- | --- |
| 额外线 | 2 根 | 0 根 |
| 速度 | 实时 | 有延迟 |
| 字节开销 | 0 | 2 字节转义 |
| 实现复杂度 | 低 (硬件自动) | 中 (软件处理) |
| 适用场景 | 高速, 工业 | 简单, 调试 |

**推荐**: 优先用硬件流控, 除非硬件限制。

## RS485 + 流控的组合

工业场景常组合:
- RS485 物理层 (长距离, 差分)
- RTS/CTS 流控 (高速)
- Modbus RTU 协议 (主从)

详细见 `modbus-rs485-deep-dive.md`。

## RS485 实战代码骨架

```c
typedef struct {
    UART_HandleTypeDef *huart;
    GPIO_TypeDef *dir_port;
    uint16_t dir_pin;
    uint32_t baud;
    uint8_t tx_buf[256];
    uint8_t rx_buf[256];
    SemaphoreHandle_t tx_done_sem;
    SemaphoreHandle_t rx_done_sem;
    volatile bool tx_busy;
    volatile bool rx_busy;
} rs485_ctx_t;

int rs485_init(rs485_ctx_t *ctx, UART_HandleTypeDef *huart,
               GPIO_TypeDef *dir_port, uint16_t dir_pin, uint32_t baud) {
    ctx->huart = huart;
    ctx->dir_port = dir_port;
    ctx->dir_pin = dir_pin;
    ctx->baud = baud;
    ctx->tx_done_sem = xSemaphoreCreateBinary();
    ctx->rx_done_sem = xSemaphoreCreateBinary();
    
    /* UART 配置 */
    huart->Init.BaudRate = baud;
    huart->Init.HwFlowCtl = UART_HWCONTROL_NONE;  /* 不需要, RS485 用 DIR */
    HAL_UART_Init(huart);
    
    /* DIR GPIO */
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = dir_pin;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(dir_port, &gpio);
    HAL_GPIO_WritePin(dir_port, dir_pin, GPIO_PIN_RESET);  /* 默认接收 */
    
    /* 启动接收 */
    HAL_UARTEx_ReceiveToIdle_DMA(huart, ctx->rx_buf, sizeof(ctx->rx_buf));
    
    return 0;
}

int rs485_send(rs485_ctx_t *ctx, uint8_t *data, int len) {
    if (ctx->tx_busy) return -EBUSY;
    ctx->tx_busy = true;
    
    /* 1. 切发送 */
    HAL_GPIO_WritePin(ctx->dir_port, ctx->dir_pin, GPIO_PIN_SET);
    delay_us(20);  /* guard time */
    
    /* 2. DMA 发送 */
    if (HAL_UART_Transmit_DMA(ctx->huart, data, len) != HAL_OK) {
        ctx->tx_busy = false;
        HAL_GPIO_WritePin(ctx->dir_port, ctx->dir_pin, GPIO_PIN_RESET);
        return -EIO;
    }
    
    /* 3. 等完成 */
    if (xSemaphoreTake(ctx->tx_done_sem, pdMS_TO_TICKS(1000)) != pdTRUE) {
        HAL_UART_Abort(ctx->huart);
        ctx->tx_busy = false;
        HAL_GPIO_WritePin(ctx->dir_port, ctx->dir_pin, GPIO_PIN_RESET);
        return -ETIMEDOUT;
    }
    
    /* 4. 严格等 TC */
    while (!__HAL_UART_GET_FLAG(ctx->huart, UART_FLAG_TC));
    delay_us(20);  /* guard time */
    
    /* 5. 切回接收 */
    HAL_GPIO_WritePin(ctx->dir_port, ctx->dir_pin, GPIO_PIN_RESET);
    ctx->tx_busy = false;
    
    return 0;
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
    BaseType_t hp_woken = pdFALSE;
    xSemaphoreGiveFromISR(g_rs485_ctx.tx_done_sem, &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
}
```

## 产线常见问题

### 问题 1: 总线两端有 120 ohm 电阻, 实际是 60 ohm (并联)

```text
错: 总线两端各 120 ohm, 中间还有一个 120 ohm
     -> 总线等效 60 ohm, 信号衰减
对: 只有两端 120 ohm, 中间不加
```

### 问题 2: A/B 接反

```text
错: Master A 接 Slave B
对: Master A 接 Slave A
     (很多收发器对 A/B 反接不响应, 但也有兼容的)
```

### 问题 3: 收发器电源没加旁路电容

```text
错: VCC 直接接, 没有 100nF 旁路
对: VCC 引脚近 100nF + VCC 引脚 10uF
```

### 问题 4: DE / RE 引脚接错

```text
错: DE 接 GND, RE 接 GND
     -> 收发器一直发送, 永远收不到
对: DE 接 GPIO, RE 接 GND 或 GPIO
```

### 问题 5: 总线只有 1 个 120 ohm 终端

```text
错: 总线一端有 120 ohm
对: 总线两端各 120 ohm
```

## 调试技巧

### 1. 量总线电压

```text
A - B 差分电压:
  - 逻辑 1:  +200mV ~ +6V
  - 逻辑 0:  -200mV ~ -6V
  - 空闲:    +200mV (有偏置) 或不确定 (无偏置)
```

### 2. 量 DIR 时序

```text
示波器同时看:
  - Channel 1: DIR GPIO
  - Channel 2: UART TX
  - Channel 3: 总线 A-B 差分
```

### 3. 协议解码

```text
逻辑分析仪:
  - 接 A, B 两线
  - 用 "RS485" 协议解码
  - 配 baud, parity, stop
  - 看实际数据
```

## 关联文档

- `uart-deep-dive.md` 原理
- `uart-practical.md` 速查
- `uart-failure-cases.md` 产线案例 (RS485 方向控制错 案例 4)
- `uart-dma-circular-and-rtos.md` DMA + 环形缓冲 + RTOS
- `uart-index.md` 导航
- `rs232-rs485.md` 物理层基础
- `rs485-modbus-rtu-deep-dive.md` Modbus RTU 详细
- `modbus.md` Modbus 概览
