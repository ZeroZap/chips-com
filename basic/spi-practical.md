# SPI Practical Guide

## 目标

本文用于 SPI 工程调试：接线、模式、片选、读写流程、多设备共享和常见故障定位。

## 标准接线

```text
Controller SCLK -> Target SCLK
Controller MOSI -> Target SDI/MOSI
Controller MISO <- Target SDO/MISO
Controller CS   -> Target CS
Controller GND  -- Target GND
```

注意不同芯片命名：

```text
SDI：从设备输入，接主控 MOSI
SDO：从设备输出，接主控 MISO
```

## 关键参数

SPI 通信前必须确认：

```text
clock frequency
CPOL
CPHA
bit order
CS active level
word length
```

常见模式：

| Mode | CPOL | CPHA | SCLK 空闲 |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 低 |
| 1 | 0 | 1 | 低 |
| 2 | 1 | 0 | 高 |
| 3 | 1 | 1 | 高 |

## 读数据为什么也要写

SPI 主控必须产生时钟，目标设备才会移出数据。

所以读取时通常发送 dummy byte：

```c
rx = spi_transfer(0x00);
```

这里 `0x00` 的作用是产生 8 个时钟。

## 片选规则

很多设备要求一次命令期间 `CS` 保持低电平。

错误做法：

```text
CS low -> send command -> CS high -> CS low -> read data -> CS high
```

正确做法通常是：

```text
CS low -> send command -> read data -> CS high
```

以手册时序图为准。

## 多设备共享

多设备可共享：

```text
SCLK
MOSI
MISO
```

每个设备独立：

```text
CS
```

要求未选中设备释放 `MISO`，否则会总线冲突。

## 调试步骤

1. 先降到低频，例如 100 kHz 或 1 MHz。
2. 确认 CS 默认高，通信时拉低。
3. 读取固定 ID 寄存器，例如 Flash 的 JEDEC ID。
4. 如果读值错，尝试切换 SPI Mode。
5. 检查 MOSI/MISO 是否接反。
6. 提高速度前用示波器看 SCLK 和数据边沿。
7. 多设备时逐个单独验证。

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| 读不到 ID | CS、Mode、MOSI/MISO、供电 |
| 数据错位 | CPHA、采样边沿、时钟过快 |
| 全 0xFF | MISO 悬空、设备未选中 |
| 全 0x00 | MISO 被拉低、设备异常 |
| 多设备互相影响 | MISO 未三态、CS 漏拉 |

## 实战检查清单

- Mode 与手册一致。
- CS 时序满足完整事务要求。
- 读数据时发送 dummy byte。
- SPI 速度低速跑通后再提升。
- 多设备 MISO 无冲突。
- 电平兼容。

## 速查要点

### 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 读不到 ID | CS / Mode / MOSI-MISO 接反 | 检查硬件接线, 示波器看波形 |
| 数据错位 | CPHA / 采样边沿错 | 切换 SPI Mode 0/1/2/3 试 |
| 全 0xFF | MISO 悬空 / 设备未选中 | 拉 CS, 查 MISO 上拉 |
| 全 0x00 | MISO 拉低 / 设备异常 | 量 MISO 电平, 查设备状态 |
| 多设备互影响 | MISO 未三态 / CS 漏拉 | 单独 CS 控制 |
| DMA 跑到一半挂 | DMA TCIF 误触发 / ISR race | 拆 DMA, 用 IT 模式对比 |
| 高速通信失败 | 信号完整性 | 降速, 短走线, 加 series 电阻 |
| 偶发 CRC 错 | 噪声 / 时序裕量不足 | 降速, 加屏蔽, 改采样边沿 |

### SPI vs I2C 选型速查

| 场景 | 推荐 |
| --- | --- |
| 高速 (10MHz+) sensor / Flash | SPI |
| 低速 (<= 400kHz) sensor | I2C |
| 多设备 (>4 个) | I2C (省引脚) |
| 少量高速设备 (Flash / ADC) | SPI |
| 板内管理 (PMIC, 温度) | I2C |
| 显示 (LCD) | SPI (高速) |
| 音频 codec | I2S 或 SPI |
| SD 卡 | SPI 或 SDIO |
| 长距离 (>10cm) | 都不推荐, 改 RS485 / 差分 |

### 速度档位参考

```text
低速档 (调试用):     100 kHz ~ 1 MHz
中速档 (多数应用):    1 MHz ~ 10 MHz
高速档 (Flash, LCD):  10 MHz ~ 50 MHz
超高速 (QSPI):       50 MHz ~ 200 MHz+
```

### 片选 (CS) 决策

```text
场景 1: 1 个从设备
  -> CS 可以直接硬件拉低, 不用 GPIO
  -> 或者用普通 GPIO, 不参与 SPI 控制器

场景 2: 2-4 个从设备
  -> 每个 CS 独立 GPIO
  -> 控制器自己管 CS 极性 (active low / high)

场景 3: > 4 个从设备
  -> 用 SPI MUX (74HC4051 之类) 或者 3-to-8 decoder (74HC138)
  -> 或者改用 I2C (MUX 内置)

场景 4: 菊花链
  -> 多设备共享 CS, 数据串联
  -> 适合输入/输出链 (LED 驱动, ADC 阵列)
```

### DMA 触发

```text
适合 DMA:
  - 数据长度 > 8 字节
  - 高速 (10MHz+) 持续传输
  - CPU 忙其他任务

不适合 DMA:
  - 数据长度 < 4 字节
  - 调试 (排障难)
  - 多设备切换 (DMA setup 开销)
```

## 关联文档

- `spi-deep-dive.md` 原理和体系
- `spi-failure-cases.md` 产线死机案例
- `spi-multislave-and-dma.md` 多从 / 菊花链 / DMA
- `spi-rtos-integration.md` RTOS 集成
- `spi-index.md` 总览导航
- `qspi-ospi.md` 高速 SPI Flash
- `i2c-deep-dive.md` I2C 原理 (与 SPI 对比)
