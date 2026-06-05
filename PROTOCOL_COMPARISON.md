# Protocol Comparison Tables

## 目标

本文用表格对比常见芯片间通信协议，快速建立选型直觉。

## 基础接口对比

| 协议 | 线数 | 时钟 | 多设备 | 典型用途 |
| --- | --- | --- | --- | --- |
| UART | TX/RX/GND | 无 | 通常点对点 | 调试、模块通信 |
| I2C | SCL/SDA | 有 | 支持地址 | 传感器、EEPROM、PMIC |
| SPI | SCLK/MOSI/MISO/CS | 有 | 每设备 CS | Flash、屏幕、ADC |
| I3C | SCL/SDA | 有 | 动态地址 | 新一代传感器总线 |
| 1-Wire | DQ/GND | 无独立时钟 | 支持 ROM ID | 温度、身份识别 |

## 工业总线对比

| 协议 | 物理层 | 通信模型 | 实时性 | 典型用途 |
| --- | --- | --- | --- | --- |
| Modbus RTU | RS485 | 主站轮询 | 一般 | 仪表、采集模块 |
| CAN | CANH/CANL | 多主广播 | 较好 | 车载、BMS、电机 |
| CANopen | CAN | 对象模型 + PDO/SDO | 较好 | 工业设备、运动控制 |
| LIN | 单线 | 主从调度 | 一般 | 车身低成本节点 |
| EtherCAT | Ethernet PHY | 主站周期帧 | 强 | 多轴伺服、高速 IO |

## 主机外设对比

| 协议 | 主机角色 | 枚举 | 典型设备 | 软件复杂度 |
| --- | --- | --- | --- | --- |
| USB | Host/Device | 有 | U 盘、CDC、HID | 高 |
| PCIe | RC/Endpoint | 有 | SSD、网卡、FPGA | 高 |
| SDIO | Host/Function | 有 | Wi-Fi 模块 | 中高 |

## 网络协议对比

| 协议 | 层级 | 可靠性 | 典型用途 |
| --- | --- | --- | --- |
| UDP | 传输层 | 不保证 | 低延迟、广播发现 |
| TCP | 传输层 | 可靠字节流 | HTTP、MQTT、Modbus TCP |
| Modbus TCP | 应用层 | 依赖 TCP | 工业寄存器读写 |
| EtherCAT | 工业以太网 | 主站控制 | 强实时控制 |

## 显示接口对比

| 接口 | 复杂度 | 典型分辨率 | 场景 |
| --- | --- | --- | --- |
| SPI 屏 | 低 | 小屏 | MCU 显示 |
| RGB 并口 | 中 | 中低 | TFT 屏 |
| LVDS | 中 | 中高 | 工业屏 |
| MIPI DSI | 高 | 中高 | 移动/嵌入式高清屏 |
| eDP | 高 | 高 | 笔记本/高分屏 |
| HDMI | 高 | 高 | 外接显示器 |

## 关键误区

- UART 不等于 RS232，也不等于 RS485。
- RS485 不等于 Modbus。
- Ethernet 不等于 TCP/IP。
- CAN 不等于 CANopen。
- USB CDC 看起来像串口，但不是 UART。
- MIPI 数据 Lane 通了，不代表设备初始化正确。
