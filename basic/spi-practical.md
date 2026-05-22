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
