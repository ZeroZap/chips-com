# Application Scenarios

## 目标

本文按应用场景整理通信协议选型，帮助从产品需求反推接口方案。

## 传感器采集

低速环境传感器：

```text
I2C / SPI / 1-Wire
```

多传感器且需要减少中断线：

```text
I3C
```

远距离工业传感器：

```text
RS485 + Modbus RTU
CAN
Ethernet
```

## 存储器

小容量配置：

```text
I2C EEPROM
```

MCU 外部程序或资源：

```text
SPI NOR
QSPI NOR
OSPI NOR
```

大容量高速存储：

```text
eMMC
SD/SDIO
PCIe NVMe
```

## 电源管理

简单电源芯片：

```text
I2C
GPIO Enable
ADC 监控
```

系统管理和服务器电源：

```text
SMBus
PMBus
```

数字电源模块：

```text
PMBus
```

## 电机和运动控制

简单 PWM 控制：

```text
PWM + GPIO + ADC
```

工业电机驱动：

```text
CANopen
RS485 + Modbus RTU
```

多轴高速同步：

```text
EtherCAT
```

## 车载节点

低成本车身节点：

```text
LIN
```

车身和动力控制：

```text
CAN
CAN FD
```

复杂诊断和上层协议：

```text
UDS over CAN
J1939
```

## 显示和摄像头

小屏：

```text
SPI
RGB 并口
```

中高分辨率屏：

```text
MIPI DSI
LVDS
eDP
```

板内摄像头：

```text
MIPI CSI
```

外接 USB 摄像头：

```text
USB Video Class
```

## 无线模块

低速 AT 模块：

```text
UART
```

嵌入式 Wi-Fi 模块：

```text
SDIO
USB
PCIe
```

蓝牙音频或控制：

```text
UART
PCM/I2S
USB
```

## 工业联网

简单仪表联网：

```text
Modbus TCP
```

西门子生态：

```text
PROFINET
```

Rockwell 生态：

```text
EtherNet/IP
```

高速运动控制：

```text
EtherCAT
```

## 调试和维护

开发日志：

```text
UART
USB CDC
Ethernet log
```

固件升级：

```text
UART bootloader
USB DFU/MSC
Ethernet OTA
CAN bootloader
```

现场诊断：

```text
Modbus
CAN diagnostics
Ethernet service port
```
