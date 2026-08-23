# SPI 多从 / 菊花链 / DMA 专题

## 目标

SPI 是点对点总线, 但工程上经常遇到:

- **多从设备共享**: 一条 SPI 总线挂 2-N 个从设备
- **菊花链**: 多个从设备串联, 数据沿链传递
- **DMA 高吞吐**: 高速 (10MHz+) 大量数据传输
- **中断协作**: SPI EV / DMA / GPIO 中断的优先级

本文讲清楚:

- 多从设备的硬件拓扑和软件隔离
- 菊花链的数据流方向和时序
- DMA + 中断的协作模式
- 4 类常见 race condition 和解决方案
- 实战代码骨架 (可拷贝)

## 多从设备共享

### 硬件拓扑

```text
                       +-- CS1 ---> Device 1 (Flash)
                       |
Controller -- SCLK ---+-- (共享 SCLK)
        |
        +-- MOSI  ---+-- (共享 MOSI)
        |
        +-- MISO  ---+-- (共享 MISO, 设备必须三态)
                       |
                       +-- CS2 ---> Device 2 (LCD)
                       |
                       +-- CS3 ---> Device 3 (Sensor)
                       |
                       +-- CS4 ---> Device 4 (ADC)
```

**关键约束**:

1. **每个设备独立 CS**: 单独 GPIO 控制
2. **同一时刻只能 1 个 CS 拉低**: 多设备选中会总线冲突
3. **未选中的 MISO 必须三态**: 否则会拉低总线
4. **所有设备共享 SCLK / MOSI / MISO**

### 软件配置

```c
struct spi_device {
    SPI_HandleTypeDef *hspi;
    GPIO_TypeDef *cs_port;
    uint16_t cs_pin;
    uint8_t mode;             /* SPI Mode 0/1/2/3 */
    uint32_t max_hz;          /* 最大速度 */
    uint8_t bit_order;        /* MSB / LSB first */
    uint8_t word_size;        /* 8 / 16 bit */
};

struct spi_device devices[] = {
    { &hspi1, GPIOB, GPIO_PIN_12, SPI_MODE_0, 10000000, MSB_FIRST, 8 },  /* Flash */
    { &hspi1, GPIOB, GPIO_PIN_13, SPI_MODE_3,  1000000, MSB_FIRST, 8 },  /* LCD */
    { &hspi1, GPIOB, GPIO_PIN_14, SPI_MODE_0,  5000000, MSB_FIRST, 8 },  /* Sensor */
    { &hspi1, GPIOB, GPIO_PIN_15, SPI_MODE_0,  2000000, MSB_FIRST, 16}, /* ADC */
};
```

### 多从设备操作流程

```c
int spi_xfer_to_device(int dev_id, uint8_t *tx, uint8_t *rx, int len) {
    struct spi_device *dev = &devices[dev_id];

    /* 1. 配置 SPI 控制器参数 (Mode, speed, bit order) */
    spi_configure(dev->hspi, dev->mode, dev->max_hz, dev->bit_order, dev->word_size);

    /* 2. 切设备前显式关所有其他 CS (保险) */
    for (int i = 0; i < NUM_DEVICES; i++) {
        if (i != dev_id) {
            HAL_GPIO_WritePin(devices[i].cs_port, devices[i].cs_pin, GPIO_PIN_SET);
        }
    }

    /* 3. 拉目标 CS */
    HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_RESET);

    /* 4. 传输 */
    HAL_StatusTypeDef ret;
    if (rx) {
        ret = HAL_SPI_TransmitReceive(dev->hspi, tx, rx, len, HAL_MAX_DELAY);
    } else {
        ret = HAL_SPI_Transmit(dev->hspi, tx, len, HAL_MAX_DELAY);
    }

    /* 5. 拉高 CS (事务结束) */
    HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_SET);

    return ret;
}
```

### 多从设备速度切换

不同设备速度不同时, 每次切换都要 reconfig:

```c
void spi_configure(SPI_HandleTypeDef *hspi, uint8_t mode, uint32_t hz,
                   uint8_t bit_order, uint8_t word_size) {
    /* 1. Deinit */
    HAL_SPI_DeInit(hspi);

    /* 2. 改参数 */
    hspi->Init.Mode = SPI_MODE_MASTER;
    hspi->Init.Direction = SPI_DIRECTION_2LINES;
    hspi->Init.DataSize = (word_size == 8) ? SPI_DATASIZE_8BIT : SPI_DATASIZE_16BIT;
    hspi->Init.CLKPolarity = (mode & 0x2) ? SPI_POLARITY_HIGH : SPI_POLARITY_LOW;
    hspi->Init.CLKPhase = (mode & 0x1) ? SPI_PHASE_2EDGE : SPI_PHASE_1EDGE;
    hspi->Init.NSS = SPI_NSS_SOFT;
    hspi->Init.BaudRatePrescaler = spi_calc_prescaler(hz);
    hspi->Init.FirstBit = (bit_order == MSB_FIRST) ? SPI_FIRSTBIT_MSB : SPI_FIRSTBIT_LSB;

    /* 3. Init */
    HAL_SPI_Init(hspi);
}
```

**问题**: 频繁 reconfig 慢, 而且某些 MCU 切换不彻底。

**优化**: 用多个 SPI 外设, 每个设备独占一个:

```c
/* 多 SPI 外设, 互不干扰 */
SPI1 <-> Flash (10 MHz, Mode 0)
SPI2 <-> LCD  (1 MHz, Mode 3)
SPI3 <-> Sensor (5 MHz, Mode 0)
```

**好处**: 不需要 reconfig, 每个 SPI 独立配置, mutex 也按外设分。

## 菊花链

### 拓扑

```text
Controller -- SCLK ----+---> 所有设备
        |
        +-- MOSI ----> Device 1 DO ---> Device 2 DO ---> ... ---> Device N DO
                                                       (最后设备的 DO 悬空)
```

**关键约束**:
1. 链中所有设备**共享 CS** (一个 GPIO)
2. 设备 N 的 DO 接设备 N+1 的 DI
3. 链尾设备的 DO 悬空
4. 数据流是单向的

### 数据流方向

```text
Controller 发送 N 字节 -> 设备 1 接收 1 字节, 1 字节从 DO 出去
                        -> 设备 2 接收 1 字节, 1 字节从 DO 出去
                        -> ...
                        -> 设备 N 接收 1 字节
```

**关键**: 控制器发送的**第一个字节**到达**链尾**设备。

### 数据发送顺序

```c
/* 错: 设备 1 数据先发 */
tx[0] = dev1_data;
tx[1] = dev2_data;
tx[2] = dev3_data;
tx[3] = dev4_data;

/* 对: 链尾数据先发 */
tx[0] = dev4_data;  /* 链尾先收 */
tx[1] = dev3_data;
tx[2] = dev2_data;
tx[3] = dev1_data;  /* 链头最后收 */
```

**为什么**: 数据在链中是"流动"的, 链尾先收, 链头最后收。

### 菊花链读取

菊花链是单向, 读取需要把所有命令发完, 然后再读。

```c
/* 菊花链读取: 双字节命令 */
uint8_t cmd[2] = { 0x80, 0x00 };  /* 读命令 */
HAL_SPI_Transmit(&hspi1, cmd, 2, 1000);
uint8_t rx[NUM_DEVICES * DATA_LEN];
HAL_SPI_Receive(&hspi1, rx, NUM_DEVICES * DATA_LEN, 1000);
```

### 菊花链应用

- LED 驱动 (TLC5947)
- ADC 阵列 (多个 ADC 级联)
- 移位寄存器扩展 GPIO
- 多 sensor 数据采集

## SPI + DMA 模式

### 4 种 DMA 模式

```text
模式 1: 全双工 DMA (主推)
  HAL_SPI_TransmitReceive_DMA(&hspi, tx, rx, len)
  TX + RX 同时 DMA
  适合: 高速, 双向, 大量数据

模式 2: 半双工 DMA (发送)
  HAL_SPI_Transmit_DMA(&hspi, tx, len)
  只 DMA 发送
  适合: Flash 写, LCD 命令

模式 3: 半双工 DMA (接收)
  HAL_SPI_Receive_DMA(&hspi, rx, len)
  只 DMA 接收
  适合: ADC 读, sensor 数据

模式 4: 循环 DMA
  HAL_SPI_TransmitReceive_DMA(&hspi, tx, rx, len)
  + HAL_SPI_DMAPause / DMAResume
  适合: 持续音频流, 实时 sensor 采集
```

### 完整 DMA 代码骨架

```c
typedef struct {
    SPI_HandleTypeDef *hspi;
    DMA_HandleTypeDef *hdma_tx;
    DMA_HandleTypeDef *hdma_rx;
    volatile bool     busy;
    SemaphoreHandle_t done_sem;
} spi_dma_ctx_t;

static spi_dma_ctx_t g_spi_dma;

int spi_dma_init(spi_dma_ctx_t *ctx, SPI_HandleTypeDef *hspi) {
    ctx->hspi     = hspi;
    ctx->hdma_tx  = hspi->hdmatx;
    ctx->hdma_rx  = hspi->hdmarx;
    ctx->done_sem = xSemaphoreCreateBinary();
    ctx->busy     = false;
    return 0;
}

int spi_dma_xfer(spi_dma_ctx_t *ctx, uint8_t *tx, uint8_t *rx, int len, uint32_t timeout_ms) {
    if (ctx->busy) return -EBUSY;
    ctx->busy = true;

    /* 拉 CS */
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_RESET);

    /* 启动 DMA */
    HAL_StatusTypeDef ret;
    if (rx) {
        ret = HAL_SPI_TransmitReceive_DMA(ctx->hspi, tx, rx, len);
    } else {
        ret = HAL_SPI_Transmit_DMA(ctx->hspi, tx, len);
    }
    if (ret != HAL_OK) {
        HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);
        ctx->busy = false;
        return -EIO;
    }

    /* 等 DMA 完成 */
    if (xSemaphoreTake(ctx->done_sem, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        /* 超时, 强制 abort */
        HAL_SPI_Abort(ctx->hspi);
        HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);
        ctx->busy = false;
        return -ETIMEDOUT;
    }

    /* 等最后字节锁存 */
    delay_us(5);

    /* 拉高 CS */
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);
    ctx->busy = false;
    return 0;
}

/* ISR 回调: DMA 完成 */
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi->Instance == SPI1) {
        BaseType_t hp_woken = pdFALSE;
        xSemaphoreGiveFromISR(g_spi_dma.done_sem, &hp_woken);
        portYIELD_FROM_ISR(hp_woken);
    }
}
```

### 循环 DMA 模式 (持续采集)

```c
/* 配置循环 DMA */
HAL_SPI_TransmitReceive_DMA(&hspi1, tx_buf, rx_buf, BUF_SIZE);

/* 暂停 */
HAL_SPI_DMAPause(&hspi1);

/* 恢复 */
HAL_SPI_DMAResume(&hspi1);

/* 停止 */
HAL_SPI_DMAStop(&hspi1);
```

应用: 音频流, 实时 sensor 采样, 视频输入。

### DMA + Cache 一致性

Cortex-M7 等带 D-Cache 的 MCU, DMA 前后要维护 cache 一致性:

```c
/* DMA 发送前: 清 cache, 让 CPU 写入能进内存 */
SCB_CleanDCache_by_Addr((uint32_t *)tx_buf, len);

/* DMA 接收后: 失效 cache, 让 CPU 读到的从内存最新 */
SCB_InvalidateDCache_by_Addr((uint32_t *)rx_buf, len);
```

**关键**: 没维护 cache 一致性, DMA 数据看不到或被覆盖。

## SPI + 中断并发模型

### 中断优先级

```text
SPI EV 中断:  优先级 2 (高)
DMA 中断:     优先级 3
GPIO 中断:    优先级 4 (低, 给 CS 错误处理)
```

**关键**: SPI EV 中断**不能**比 DMA 中断优先级低, 否则 overrun / underrun。

### 4 类常见 race condition

#### 竞态 1: DMA 完成回调和 SPI EV 中断

```c
/* 问题: DMA 完成和 SPI EV 同时触发, 状态错位 */
/* 解决: 提高 SPI EV 优先级, 或用 volatile 同步标志位 */
volatile bool dma_tx_done = false;

void DMA1_Stream0_IRQHandler(void) {
    if (DMA1->LISR & DMA_LISR_TCIF0) {
        DMA1->LIFCR = DMA_LIFCR_CTCIF0;
        dma_tx_done = true;  /* volatile 标志 */
    }
}

void SPI1_IRQHandler(void) {
    if (SPI1->SR & SPI_SR_TXE) {
        if (dma_tx_done) {
            /* DMA 完成了, SPI 准备发最后一帧 */
            spi_finish();
        }
    }
}
```

#### 竞态 2: 中断里调 HAL 回调, HAL 内部用了 mutex

```c
/* 错 */
void SPI1_IRQHandler(void) {
    HAL_SPI_IRQHandler(&hspi1);
    /* HAL 内部调 xSemaphoreGiveFromISR, 但在 ISR 里 mutex 行为未定义 */
}

/* 对: 简化 HAL 回调, 用 flag 同步 */
volatile bool spi_done = false;
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    spi_done = true;
}

void spi_thread() {
    while (1) {
        if (spi_done) {
            spi_done = false;
            /* 线程里处理 */
        }
    }
}
```

#### 竞态 3: 多 task 共享 SPI 控制器

见 `spi-rtos-integration.md` 的 mutex 部分。

#### 竞态 4: CS 在事务中途被外部中断拉高

```c
/* 问题: 某个 GPIO 中断 (e.g. 外部事件) 拉高了 CS, 事务中断 */
/* 解决: 中断优先级 + 临界区 */

void spi_critical_xfer(uint8_t *tx, int len) {
    /* 关闭可能操作 CS 的中断 */
    __disable_irq();
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_RESET);
    HAL_SPI_Transmit(&hspi1, tx, len, 1000);
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);
    __enable_irq();
}
```

**注意**: 临界区不能太长, 否则影响实时性。

## SPI 状态机

```c
typedef enum {
    SPI_STATE_IDLE = 0,
    SPI_STATE_CS_LOW,
    SPI_STATE_XFER,
    SPI_STATE_CS_HIGH,
    SPI_STATE_DONE,
    SPI_STATE_ERROR,
} spi_state_t;

typedef struct {
    spi_state_t state;
    uint8_t *tx_buf;
    uint8_t *rx_buf;
    int len;
    int pos;
    uint32_t start_tick;
    uint32_t deadline;
} spi_xfer_ctx_t;

/* 状态转移 */
void spi_state_machine(spi_xfer_ctx_t *ctx) {
    switch (ctx->state) {
    case SPI_STATE_IDLE:
        /* 等待发起 */
        break;
    case SPI_STATE_CS_LOW:
        HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_RESET);
        ctx->state = SPI_STATE_XFER;
        break;
    case SPI_STATE_XFER:
        if (ctx->rx_buf) {
            HAL_SPI_TransmitReceive_DMA(...);
        } else {
            HAL_SPI_Transmit_DMA(...);
        }
        ctx->state = SPI_STATE_DONE;
        break;
    case SPI_STATE_DONE:
        /* 等 DMA 完成, 进 CS_HIGH */
        if (dma_complete) {
            ctx->state = SPI_STATE_CS_HIGH;
        } else if (tick_elapsed(ctx->deadline)) {
            ctx->state = SPI_STATE_ERROR;
        }
        break;
    case SPI_STATE_CS_HIGH:
        delay_us(5);
        HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);
        ctx->state = SPI_STATE_IDLE;
        break;
    case SPI_STATE_ERROR:
        HAL_SPI_Abort(...);
        HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);
        ctx->state = SPI_STATE_IDLE;
        break;
    }
}
```

## 调试技巧

### 逻辑分析仪必备信号

```text
- CS: 看事务边界
- SCLK: 看时钟连续性
- MOSI: 看命令和数据
- MISO: 看从设备响应
- GPIO (用于触发): 标记事务开始
```

### 示波器触发

```text
- 在 CS 下降沿触发
- 看 4 根线一起
- 测上升/下降时间
- 测时序裕量
```

### 协议解码

```text
- 逻辑分析仪: SPI 协议解码, 直接看到命令和数据
- Saleae / Kingst / 总线分析仪
- 看是否是预期的命令和数据
```

## 实战代码: 多设备 + DMA + 互斥

```c
typedef struct {
    SPI_HandleTypeDef *hspi;
    struct {
        GPIO_TypeDef *port;
        uint16_t pin;
        uint8_t mode;
        uint32_t max_hz;
    } dev[8];
    int num_dev;
    SemaphoreHandle_t mutex;
    SemaphoreHandle_t done_sem;
} spi_bus_t;

int spi_bus_xfer(spi_bus_t *bus, int dev_id,
                 uint8_t *tx, uint8_t *rx, int len) {
    if (dev_id >= bus->num_dev) return -EINVAL;

    xSemaphoreTake(bus->mutex, portMAX_DELAY);

    /* 1. 配置 (如果需要) */
    spi_configure(bus->hspi, bus->dev[dev_id].mode, bus->dev[dev_id].max_hz);

    /* 2. 拉 CS */
    HAL_GPIO_WritePin(bus->dev[dev_id].port, bus->dev[dev_id].pin, GPIO_PIN_RESET);

    /* 3. DMA 传输 */
    HAL_StatusTypeDef ret;
    if (rx) {
        ret = HAL_SPI_TransmitReceive_DMA(bus->hspi, tx, rx, len, HAL_MAX_DELAY);
    } else {
        ret = HAL_SPI_Transmit_DMA(bus->hspi, tx, len, HAL_MAX_DELAY);
    }

    /* 4. 等完成 */
    if (ret == HAL_OK) {
        xSemaphoreTake(bus->done_sem, portMAX_DELAY);
    }

    /* 5. 拉高 CS */
    delay_us(5);
    HAL_GPIO_WritePin(bus->dev[dev_id].port, bus->dev[dev_id].pin, GPIO_PIN_SET);

    xSemaphoreGive(bus->mutex);

    return (ret == HAL_OK) ? 0 : -EIO;
}

void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    BaseType_t hp_woken = pdFALSE;
    xSemaphoreGiveFromISR(g_spi_bus.done_sem, &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
}
```

## 关键参数选择

| 参数 | 选型建议 |
| --- | --- |
| SPI Mode | 看设备 datasheet, 多数 sensor 是 Mode 0 或 3 |
| 速度 | 低速调试, 提产线速度, 验证信号完整性 |
| 字长 | 多数 8 bit, 部分 ADC 是 16/24 bit |
| 位序 | 多数 MSB first, 部分 sensor LSB first |
| CS 极性 | 多数 active low, 部分 active high (少见) |

## 关联文档

- `spi-deep-dive.md` 原理
- `spi-practical.md` 速查
- `spi-failure-cases.md` 产线案例
- `spi-rtos-integration.md` RTOS 集成
- `qspi-ospi.md` 高速 SPI Flash
- `i2c-state-machine.md` 类似 race condition
