# Layered Protocol Map

## 目标

本文按层级整理本知识库中的通信技术，帮助理解它们之间的关系。

## 基础电平和 GPIO

```text
GPIO
Pull-up / Pull-down
Push-pull / Open-drain
Interrupt
PWM
ADC / DAC
```

这些是最底层的引脚能力。

## 板内基础总线

```text
UART TTL
I2C
SPI
I2S
1-Wire
SMBus
PMBus
I3C
SDIO
QSPI / OSPI
```

特点：

- 距离短。
- 板内为主。
- 依赖 PCB 和电平域。
- 多用于芯片和外设。

## 物理层扩展

```text
RS232
RS485
CAN PHY
Ethernet PHY
MIPI D-PHY
PCIe PHY
```

它们解决电气传输问题，不一定定义完整应用协议。

## 工业和车载总线

```text
Modbus RTU
CAN
CANopen
LIN
EtherCAT
PROFINET
EtherNet/IP
Modbus TCP
```

特点：

- 多设备。
- 强调可靠性。
- 常涉及设备模型、状态机、实时性。

## 通用主机外设

```text
USB
PCIe
SDIO
```

特点：

- Host/Device 或 RC/EP 角色明确。
- 需要枚举。
- 强依赖驱动栈。

## 网络通信

```text
Ethernet
ARP
IP
TCP
UDP
HTTP
MQTT
Modbus TCP
```

特点：

- 分层清晰。
- 工具成熟。
- 支持多设备和跨网段。

## 图像和显示

```text
MIPI CSI
MIPI DSI
I2C sensor/panel control
GPIO reset/power
PWM backlight
```

特点：

- 高速 Lane 传数据。
- 低速控制接口初始化设备。
- 强依赖电源时序和格式匹配。

## 分层示例

Modbus RTU：

```text
Modbus RTU
UART 字节流
RS485 差分物理层
```

CANopen：

```text
CANopen
CAN 帧和仲裁
CAN PHY
```

Modbus TCP：

```text
Modbus TCP
TCP
IP
Ethernet
PHY
```

USB CDC：

```text
虚拟串口 API
USB CDC
USB Endpoint
USB PHY
```

MIPI 摄像头：

```text
V4L2/Camera driver
CSI Receiver / ISP
MIPI CSI-2
D-PHY
I2C 配置 + GPIO + MCLK
```
