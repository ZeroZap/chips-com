---
tags:
  - layer/guides
  - type/examples
  - topic/learning
---

# Device Examples

## 目标

本文按典型设备列出常见通信接口，帮助建立“设备类型 -> 常见协议”的直觉。

## 传感器

温湿度传感器：

```text
I2C / 1-Wire / UART
```

IMU：

```text
I2C / SPI / I3C
```

气压计：

```text
I2C / SPI
```

工业温度采集模块：

```text
RS485 + Modbus RTU
```

## 存储

EEPROM：

```text
I2C / SPI
```

NOR Flash：

```text
SPI / QSPI / OSPI
```

SD 卡：

```text
SD / SPI mode
```

NVMe SSD：

```text
PCIe
```

## 电源和电池

PMIC：

```text
I2C / SMBus
```

数字电源：

```text
PMBus
```

智能电池：

```text
SMBus
```

BMS：

```text
CAN / RS485 / isoSPI，视芯片生态
```

## 显示和图像

小尺寸 TFT/OLED：

```text
SPI / RGB
```

手机类屏幕：

```text
MIPI DSI
```

摄像头 Sensor：

```text
MIPI CSI + I2C + MCLK + GPIO
```

USB 摄像头：

```text
USB UVC
```

## 通信模块

GPS 模块：

```text
UART
```

蜂窝模块：

```text
UART / USB / PCIe
```

Wi-Fi 模块：

```text
SDIO / USB / PCIe / UART AT
```

蓝牙模块：

```text
UART / USB / PCM / I2S
```

## 工业设备

PLC：

```text
RS485 / Ethernet / PROFINET / EtherNet/IP
```

变频器：

```text
RS485 + Modbus RTU / CANopen / PROFINET / EtherCAT
```

伺服驱动：

```text
CANopen / EtherCAT / PROFINET
```

远程 IO：

```text
Modbus RTU / Modbus TCP / PROFINET / EtherCAT
```

## 电力 / 水务 / 表计 / 楼宇

多功能电表：

```text
DL/T 645 + RS485/红外
Modbus RTU（部分表计）
```

水表/热表/燃气表：

```text
CJ/T 188 + RS485/M-Bus
LoRaWAN/NB-IoT（智能表计）
```

水文/水资源 RTU：

```text
SL 651 / SZY 206 / SL/T 427 + 4G/北斗
```

环保监测终端：

```text
HJ 212 + TCP/4G
```

电网远动 RTU/网关：

```text
IEC 60870-5-104 / IEC 60870-5-101 / DNP3
```

变电站保护/测控：

```text
IEC 61850（MMS / GOOSE / SV）
```

楼宇控制器/网关：

```text
BACnet / Modbus / OPC UA
```

## 车载与诊断设备

OBD 诊断仪：

```text
OBD-II + CAN/ISO-TP
```

OEM 诊断/刷写工具：

```text
UDS + ISO-TP / DoIP
```

商用车车队终端：

```text
SAE J1939 + CAN
```

车载网关：

```text
CAN/CAN FD + LIN + Ethernet/TSN
```

## 无线 / IoT 设备

BLE 手环/标签：

```text
BLE GATT
```

ZigBee/Thread 传感器：

```text
ZigBee / Thread + Matter
```

LoRaWAN 传感节点：

```text
LoRaWAN + LoRa 网关
```

蜂窝表计/追踪器：

```text
LTE Cat-1 / Cat-M1 / NB-IoT
```

私有 2.4 GHz 遥控/传感器：

```text
nRF2401 / 私有协议
```

## 卫星 / 应急设备

卫星数据终端：

```text
北斗短报文 / Iridium SBD / NTN
```

个人定位信标：

```text
PLB / 406 MHz + GNSS
```

应急通信终端：

```text
Satellite-IoT + PLB + Rescue-Comms
```

## 工业以太网设备

PLC：

```text
PROFINET / EtherNet/IP / Modbus TCP
```

伺服驱动/多轴控制器：

```text
EtherCAT / PROFINET IRT
```

远程 IO：

```text
PROFINET / EtherNet/IP / EtherCAT / Modbus TCP
```

OPC UA 网关：

```text
OPC UA + Modbus/Profinet/EtherNet-IP
```

## 计算和扩展

FPGA 加速卡：

```text
PCIe
```

高速网卡：

```text
PCIe
```

调试器：

```text
USB / SWD / JTAG / UART
```

外部音频 Codec：

```text
I2S + I2C/SPI control
```
