# Communication Debug Tools

## 目标

本文整理芯片间通信常用调试工具，以及它们适合解决的问题。

## 示波器

适合观察：

- 电平幅度。
- 上升沿/下降沿。
- 过冲和振铃。
- 噪声。
- 差分信号质量。
- 时钟稳定性。

优先用于：

```text
I2C 上升沿慢
SPI 高速不稳定
RS485/CAN 差分波形异常
MIPI/PCIe 硬件初步检查
```

## 逻辑分析仪

适合观察：

- UART 字节。
- I2C 地址和 ACK/NACK。
- SPI 命令和数据。
- 1-Wire 时序。
- LIN 帧。

注意：

```text
逻辑分析仪看到的是数字判定结果，不代表电气质量一定好。
```

波形边沿质量仍要用示波器确认。

## CAN 分析仪

适合：

- CAN 帧收发。
- CANopen SDO/PDO 调试。
- 错误帧观察。
- 总线负载统计。
- DBC 解析。

排查重点：

- 波特率。
- 标准帧/扩展帧。
- ACK Error。
- Bus Off。
- ID 过滤。

## USB 工具

常用：

- Windows 设备管理器。
- Linux `dmesg`。
- `lsusb`。
- USB 协议分析仪。
- Wireshark USB capture。

适合排查：

- 枚举失败。
- 描述符错误。
- Endpoint 配置。
- CDC/HID/MSC 类协议。

## Wireshark

适合：

- Ethernet。
- ARP。
- IP。
- TCP/UDP。
- Modbus TCP。
- HTTP/MQTT。

常用过滤：

```text
arp
ip.addr == 192.168.1.50
tcp.port == 502
udp
modbus
```

## EtherCAT 工具

常见：

- TwinCAT。
- IgH EtherCAT Master。
- SOEM。
- Codesys EtherCAT。

重点看：

- 从站扫描。
- ESI 匹配。
- 状态机。
- WKC。
- DC 同步。
- PDO 映射。

## PCIe 工具

常见：

- `lspci`。
- `setpci`。
- 内核日志。
- LTSSM 状态寄存器。
- PCIe 协议分析仪。
- 高速示波器。

重点看：

- 链路是否到 L0。
- Vendor ID 是否可读。
- Link Speed/Width。
- BAR 分配。
- MSI/MSI-X。
- AER 错误。

## MIPI 调试工具

常见：

- SoC CSI/DSI 错误计数。
- 图像采集工具。
- Panel test pattern。
- 厂商 ISP 工具。
- 高速示波器。

重点看：

- Sensor ID。
- MCLK。
- Lane 错误。
- RAW/YUV 格式。
- DSI 初始化命令。
- 显示时序。

## 工具选择原则

```text
怀疑电气问题，用示波器
怀疑协议字节问题，用逻辑分析仪
怀疑网络问题，用 Wireshark
怀疑 CAN 问题，用 CAN 分析仪
怀疑 USB/PCIe/EtherCAT，优先用专用协议工具和系统日志
```
