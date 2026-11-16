# Protocol Selection Matrix

## 目标

本文提供芯片间通信协议选型矩阵，帮助根据距离、速度、设备数量、实时性、抗干扰、软件复杂度和生态要求选择合适接口。

## 快速选型表

| 场景 | 优先考虑 |
| --- | --- |
| 简单点对点调试 | UART |
| 多个低速板内设备 | I2C / I3C |
| 高速简单外设 | SPI / QSPI / OSPI |
| 温度或身份识别 | 1-Wire |
| 电源管理 | SMBus / PMBus |
| 工业长距离低成本 | RS485 + Modbus RTU |
| 车载/工业实时控制 | CAN / CANopen |
| 低成本车身节点 | LIN |
| 通用外设接 PC | USB |
| 局域网通信 | Ethernet + TCP/UDP |
| 简单工业以太网 | Modbus TCP |
| 高速实时运动控制 | EtherCAT |
| 摄像头 | MIPI CSI |
| 显示屏 | MIPI DSI |
| Wi-Fi 模块 | SDIO / USB / PCIe |
| 高速系统扩展 | PCIe |

## 按距离选择

板内短距离：

```text
GPIO / UART TTL / I2C / I3C / SPI / SDIO / MIPI / PCIe / SMBus / PMBus
```

板间或设备内连接：

```text
UART / RS485 / CAN / USB / Ethernet / LVDS
```

设备间或工业现场：

```text
RS485 / CAN / Ethernet / 工业以太网 / LIN
```

## 按速度选择

低速管理：

```text
GPIO / 1-Wire / UART / I2C / SMBus / PMBus / LIN
```

中速外设：

```text
SPI / I3C / SDIO / CAN FD / USB FS / 100M Ethernet
```

高速数据：

```text
USB HS/SS / Gigabit Ethernet / MIPI / PCIe / EtherCAT / QSPI / OSPI
```

## 按设备数量选择

点对点：

```text
UART / SPI / USB / PCIe / MIPI CSI / MIPI DSI / RS232
```

多设备共享：

```text
I2C / I3C / 1-Wire / RS485 / CAN / LIN / Ethernet / EtherCAT
```

## 按实时性选择

低实时：

```text
UART / I2C / SMBus / PMBus / HTTP / MQTT / Modbus TCP
```

中实时：

```text
SPI / CAN / CANopen / UDP / RS485 自定义协议
```

强实时：

```text
EtherCAT / PROFINET IRT / TSN / FPGA 专用链路
```

## 按软件复杂度选择

低复杂度：

```text
GPIO / UART / SPI / I2C / 1-Wire
```

中复杂度：

```text
RS485 + Modbus / CAN / CANopen / I3C / SMBus / PMBus / SDIO
```

高复杂度：

```text
USB / Ethernet TCP/IP / EtherCAT / PROFINET / EtherNet/IP / PCIe / MIPI
```

## 选型问题清单

1. 通信距离多远？
2. 是板内、板间还是设备间？
3. 需要多少带宽？
4. 是否需要实时性或同步？
5. 有多少设备？
6. 设备是否需要主动上报？
7. 环境干扰强不强？
8. 是否需要隔离和防护？
9. 客户是否指定协议？
10. 主控芯片是否支持？
11. 软件栈是否成熟？
12. 调试工具是否可用？
13. 成本和引脚数量是否可接受？
14. 是否有认证或授权要求？

## 结论

协议选型不是选择最先进的，而是选择：

```text
距离合适
速度够用
实时性满足
抗干扰可靠
成本可接受
软件栈成熟
调试工具可用
生态符合客户要求
```
