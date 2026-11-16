---
tags:
  - layer/guides
  - type/scenarios
  - topic/learning
---

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

## 电力 / 水务 / 表计 / 楼宇

电网远动和调度：

```text
IEC 60870-5-104 / IEC 60870-5-101
DNP3
```

变电站自动化：

```text
IEC 61850（MMS / GOOSE / SV）
```

电表集抄：

```text
DL/T 645 + RS485/红外
```

水表/热表/燃气表：

```text
CJ/T 188 + RS485/M-Bus
```

水文/水资源监测：

```text
SL 651 / SZY 206 / SL/T 427 + 4G/北斗
```

环保在线监控：

```text
HJ 212 + TCP/4G
```

楼宇自控和工业信息：

```text
BACnet / OPC UA / Modbus TCP
```

## 车载诊断与刷写

法规排放诊断：

```text
OBD-II（乘用车）
WWH-OBD（商用车）
```

OEM 诊断/刷写：

```text
UDS over ISO-TP / DoIP
```

商用车网络：

```text
SAE J1939
```

刷写链路：

```text
UDS + ISO-TP + CAN/CAN FD
UDS + DoIP + Ethernet
USB DFU / UART Bootloader / OTA
```

## 无线 IoT / 可穿戴

手机周边和可穿戴：

```text
BLE
```

智能家居 Mesh：

```text
ZigBee / Thread
```

跨生态智能家居：

```text
Matter over Thread / Wi-Fi
```

远距离低功耗传感：

```text
LoRaWAN
```

蜂窝 IoT：

```text
LTE Cat-1 / Cat-M1 / NB-IoT
```

## 卫星 / 应急

海洋/边远地区数据回传：

```text
Satellite-IoT（北斗短报文 / Iridium SBD / NTN）
```

人员/资产应急定位：

```text
PLB / Rescue-Comms / 406 MHz 信标
```

## 工业以太网与运动控制

工厂自动化：

```text
PROFINET / EtherNet/IP / Modbus TCP
```

多轴运动控制：

```text
EtherCAT
```

确定性网络：

```text
TSN（gPTP / Qbv / Qav）
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
