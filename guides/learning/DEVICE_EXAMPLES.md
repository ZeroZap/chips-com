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
