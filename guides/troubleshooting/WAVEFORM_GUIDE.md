---
tags:
  - layer/guides
  - type/guide
  - topic/troubleshooting
---

# Waveform Observation Guide

## 目标

本文整理常见通信接口的波形观察重点，帮助用示波器和逻辑分析仪判断问题。

## UART

观察重点：

- 空闲为高。
- 起始位为低。
- bit 宽度是否匹配波特率。
- 电平幅度是否正确。
- 是否有毛刺或反相。

常见判断：

```text
bit 时间 = 1 / baud rate
115200 baud 每 bit 约 8.68 us
```

## I2C

观察重点：

- SCL/SDA 空闲为高。
- START：SCL 高时 SDA 下降。
- STOP：SCL 高时 SDA 上升。
- ACK 位是否被拉低。
- 上升沿是否过慢。

示波器重点看上升沿时间和高低电平幅度。

## SPI

观察重点：

- SCLK 空闲电平。
- 数据在哪个边沿稳定。
- CS 是否覆盖完整事务。
- MISO 是否在 dummy 后输出。
- 高速下是否有振铃。

逻辑分析仪 Mode 设置错会导致解码错误。

## RS485

观察重点：

- A/B 差分电压。
- DE 控制是否覆盖完整发送。
- 总线空闲偏置。
- 长线反射和振铃。

如果最后字节坏，重点看 DE 是否过早关闭。

## CAN

观察重点：

- CANH/CANL 差分变化。
- 终端后波形是否稳定。
- 错误帧。
- ACK 位是否存在。

断电测阻抗比上电看波形更适合初步确认终端。

## Ethernet

普通示波器很难完整分析高速以太网质量。

优先看：

- PHY 时钟。
- RMII/RGMII 数字接口。
- Link 状态。
- MDIO 访问。

协议层用 Wireshark。

## USB

观察重点：

- D+/D- 是否有连接检测电平。
- 插入后是否有 reset 和枚举活动。
- FS/HS 硬件需要对应带宽探头。

复杂 USB 问题优先用协议分析仪和系统日志。

## MIPI

MIPI 高速 Lane 不适合普通探头随意测量。

优先通过：

- SoC 错误计数。
- Sensor ID。
- DSI/CSI 控制器状态。
- 厂商调试工具。

硬件测量需高速差分探头和正确夹具。

## I2S

观察重点：

- MCLK、BCLK、LRCLK 是否存在且频率正确。
- BCLK 与 LRCLK 的比例是否符合采样率/声道/位宽。
- 数据相对 LRCLK 的对齐方式。
- 左右声道和 24/32 bit 槽宽。
- DMA underflow 时的周期性断点。

## QSPI / OSPI

观察重点：

- CS、SCK、IO0~IO7 的边沿和过冲。
- 命令/地址/dummy/数据阶段的线宽变化。
- 读数据采样边沿和建立/保持时间。
- DDR 模式下时钟与数据的相位关系。
- 高频下的振铃、串扰和电源噪声。

## LIN

观察重点：

- Break 长度和 Sync 字节。
- PID 和校验。
- 帧间隔和调度周期。
- 从节点响应时间和总线电平。
- 主站上拉/从站终端。

## FPD-Link / GMSL

观察重点：

- 高速差分 Lane 的眼图和幅度。
- Link Lock、lock drop 和错误计数。
- PoC 供电电压、纹波和负载瞬态。
- 反向通道/I2C 访问。
- 线束长度、连接器和 equalizer 设置。

## HDMI / eDP

观察重点：

- HDMI 5V、HPD、DDC。
- TMDS/FRL 或 eDP Main Link 眼图。
- AUX/DPCD 和 Link Training。
- EDID 读取和 HPD 抖动。
- Panel power/reset/backlight 时序。

HDMI/eDP 高速链路优先用协议分析仪、眼图仪和厂商工具；普通示波器只适合电源/控制信号和初步检查。

## PCIe

观察重点：

- PERST#、REFCLK、Link 状态。
- LTSSM 是否到 L0。
- TX/RX 差分对和 AC 耦合电容。
- 链路速率/宽度和 AER 错误。
- 高速眼图需协议分析仪/高速示波器。

## 电源与地

观察重点：

- 上电/掉电时序。
- 电源纹波和负载瞬态。
- 地弹、回流路径和共模电压。
- ESD/浪涌前后的器件状态。
- 探头地线长度和测量环路。

## 观测原则

- 先低速验证再高速验证。
- 先看电平再看协议。
- 先看单设备再看多设备。
- 探头本身会增加负载，尤其 I2C/MIPI 高速场景。
