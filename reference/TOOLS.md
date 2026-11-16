---
tags:
  - layer/reference
  - type/reference
---

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

## 基础电子工具

| 工具            | 主要用途                             |
| --------------- | ------------------------------------ |
| 数字万用表      | 电压、电流、通断、阻抗、二极管压降   |
| 直流电源        | 给 DUT 供电，观察电流和功耗          |
| 电子负载        | 模拟负载变化，验证电源和线缆压降     |
| 示波器          | 电平、时序、上升沿、噪声、差分信号   |
| 差分探头        | 安全测量 CAN、RS485、LVDS 等差分信号 |
| 电流探头        | 观察动态电流、浪涌和功耗波形         |
| 热风枪 / 烙铁   | 返修、飞线、替换器件                 |
| 放大镜 / 显微镜 | 检查虚焊、连锡、BGA 和连接器         |

## I2C / SPI 工具

| 工具                          | 主要用途                                  |
| ----------------------------- | ----------------------------------------- |
| USB-I2C/SPI 适配器            | 总线扫描、寄存器读写、脚本化测试          |
| Bus Pirate                    | 低成本多协议探测，适合快速验证            |
| FT2232H / FT232H              | USB 转 I2C/SPI/JTAG，适合自动化和量产治具 |
| Total Phase Aardvark / Beagle | I2C/SPI 主机与协议分析                    |
| Saleae / DSLogic / sigrok     | 逻辑分析、协议解码、长时间抓取            |
| 示波器                        | 上拉、边沿、时钟质量、总线电容影响        |

重点看：

```text
地址是否 ACK
时钟频率和占空比
SCL/SDA 上升沿
CS 建立/保持时间
CPOL/CPHA 与采样点
MISO 竞争和 dummy cycle
```

## UART / RS485 / Modbus 工具

| 工具                     | 主要用途                            |
| ------------------------ | ----------------------------------- |
| USB-UART 转换器          | 串口日志、AT 命令、Bootloader       |
| RS485/RS422 转换器       | 差分总线接入，注意 DE/RE 和隔离     |
| 隔离转换器               | 消除地电位差和共模干扰              |
| 串口助手                 | 收发原始字节、HEX 显示、定时发送    |
| Modbus Poll / QModMaster | Modbus RTU/TCP 主站模拟与寄存器读写 |
| 逻辑分析仪               | 帧间隔、DE/RE 时序、字节边界        |
| 示波器                   | 差分电平、终端、偏置、浪涌          |

## CAN / LIN 工具

| 工具                   | 主要用途                             |
| ---------------------- | ------------------------------------ |
| CAN 分析仪             | 收发帧、错误帧、总线负载、DBC 解码   |
| PCAN / Kvaser / Vector | 高可靠 CAN/CAN FD 接口与驱动         |
| CANable / candleLight  | 低成本 SocketCAN 适配器              |
| CANoe / CANalyzer      | 总线仿真、诊断、自动化测试           |
| Linux can-utils        | candump、cansend、cangen、canbusload |
| LIN 分析仪 / 示波器    | Break、Sync、PID、Checksum、调度周期 |

重点看：

```text
波特率和采样点
终端电阻和差分电平
TEC/REC 与 Bus Off
ACK Error 和错误帧
CAN FD BRS 与数据段速率
LIN 主从调度和帧间隔
```

## 工业以太网工具

| 工具                       | 主要用途                                                      |
| -------------------------- | ------------------------------------------------------------- |
| Wireshark                  | Ethernet、IP、TCP/UDP、Modbus TCP、PROFINET、EtherNet/IP 抓包 |
| TwinCAT                    | EtherCAT 主站、从站扫描、PDO 映射、DC 同步                    |
| SOEM / IgH EtherCAT Master | 开源 EtherCAT 主站                                            |
| PRONETA                    | PROFINET 网络扫描和诊断                                       |
| Studio 5000 / RSLinx       | EtherNet/IP 设备调试                                          |
| UaExpert                   | OPC UA 节点浏览、读写和订阅                                   |
| Modbus Poll                | Modbus TCP 寄存器读写                                         |

重点看：

```text
Link 状态和速率
VLAN / PCP / QoS
EtherCAT WKC 和状态机
PROFINET 设备名和 IP
EtherNet/IP CIP 连接
OPC UA 安全策略和订阅
```

## 电力 / 水务 / RTU 工具

| 工具                     | 主要用途                                 |
| ------------------------ | ---------------------------------------- |
| IEC 60870-5-104 客户端   | 总召、遥测、遥信、遥控、对时             |
| IEC 60870-5-101 串口主站 | 串行远动规约调试                         |
| lib60870 / opendnp3      | 开源 101/104/DNP3 协议栈和测试工具       |
| DNP3 主站模拟器          | 轮询、事件、控制、时间同步               |
| Modbus Poll              | 电表、水表、RTU 寄存器调试               |
| 串口监听器               | 101、Modbus RTU、DL/T 645 等串行规约抓包 |
| 点表工具                 | 点位映射、缩放、死区、报警配置           |

重点看：

```text
链路建立和超时
公共地址 / 链路地址 / 点号
ASDU 类型和传送原因
遥测死区与变化上报
SOE 时间戳和对时
遥控选择/执行流程
```

## USB / PCIe 工具

| 工具                           | 主要用途                           |
| ------------------------------ | ---------------------------------- |
| USB 协议分析仪                 | 枚举、描述符、端点、传输和错误     |
| Wireshark + USBPcap            | Windows 下 USB 抓包                |
| Linux usbmon / lsusb           | 内核侧枚举和端点信息               |
| dfu-util / STM32CubeProgrammer | DFU 下载、状态查询、回退验证       |
| lspci / setpci                 | PCIe 设备、配置空间、BAR、链路状态 |
| PCIe 协议分析仪                | TLP/DLLP、链路训练、AER            |
| 高速示波器                     | PCIe/USB 高速信号质量              |

## 显示 / 摄像头工具

| 工具                      | 主要用途                            |
| ------------------------- | ----------------------------------- |
| MIPI D-PHY/CSI/DSI 分析仪 | Lane 状态、包解析、错误计数         |
| V4L2 工具                 | 摄像头枚举、格式设置、抓帧          |
| read-edid / edid-decode   | 读取和解析显示器 EDID               |
| Panel test pattern        | 屏幕纯色、灰阶、坏点测试            |
| 示波器 / 差分探头         | MIPI、LVDS、FPD-Link、HDMI 信号质量 |
| 光功率计 / 眼图仪         | 高速链路和光模块测试                |

## 无线 / IoT / 卫星工具

| 工具                        | 主要用途                           |
| --------------------------- | ---------------------------------- |
| nRF Connect / nRF Sniffer   | BLE 广播、连接、GATT 读写和抓包    |
| Ellisys / Ubertooth         | BLE 协议分析和嗅探                 |
| Zigbee2MQTT + CC2652/CC2531 | ZigBee 网络抓包、入网和端点调试    |
| ot-br-posix / chip-tool     | Thread 边界路由和 Matter 设备调试  |
| LoRa 网关 + ChirpStack      | LoRaWAN 入网、上下行、ADR 和帧日志 |
| LTE 模块 AT 口 / QXDM       | 附着、APN、信号质量、PSM/eDRX      |
| GNSS 模拟器 / 频谱仪        | 定位、灵敏度、干扰和卫星链路测试   |
| SDR（RTL-SDR / HackRF）     | 卫星、PLB、遥控和未知信号初步分析  |

## EMC / 可靠性工具

| 工具                | 主要用途                       |
| ------------------- | ------------------------------ |
| 频谱分析仪          | 辐射发射、干扰源定位           |
| 矢量网络分析仪      | 阻抗、S 参数、线缆和滤波器     |
| 近场探头            | 定位 PCB 上的辐射热点          |
| TDR                 | 线缆和阻抗不连续点定位         |
| ESD 枪 / 浪涌发生器 | ESD、EFT、浪涌抗扰度           |
| 温箱 / 振动台       | 高低温、温循、振动和可靠性试验 |
| 电源扰动模拟器      | 掉电、跌落、浪涌和电压暂降     |

## 自动化与 CI 工具

| 工具                           | 主要用途                       |
| ------------------------------ | ------------------------------ |
| Python + pytest                | 测试用例组织、断言和报告       |
| PyVISA                         | 控制示波器、电源、万用表等仪器 |
| Saleae Automation / sigrok CLI | 逻辑分析仪自动化抓取           |
| can-utils / python-can         | CAN 自动化收发和回归           |
| pyserial / pymodbus            | 串口和 Modbus 自动化           |
| Wireshark tshark               | 抓包、过滤和自动解析           |
| GitLab CI / GitHub Actions     | 编译、静态检查、回归和报告归档 |

## 工具选型矩阵

| 问题                | 首选工具          | 补充工具                |
| ------------------- | ----------------- | ----------------------- |
| I2C 无 ACK          | 逻辑分析仪        | 示波器、USB-I2C 适配器  |
| SPI 数据错位        | 逻辑分析仪        | 示波器、协议解码        |
| UART 乱码           | USB-UART + 示波器 | 逻辑分析仪、波特率扫描  |
| RS485 最后字节丢失  | 逻辑分析仪        | 示波器、DE/RE 时序      |
| CAN Bus Off         | CAN 分析仪        | 示波器、错误计数器日志  |
| LIN 调度异常        | LIN 分析仪        | 示波器、主站日志        |
| Modbus 寄存器错位   | Modbus Poll       | 串口监听、点表          |
| EtherCAT 从站掉线   | TwinCAT           | Wireshark、WKC 日志     |
| PROFINET 设备名冲突 | PRONETA           | Wireshark、PLC 诊断     |
| IEC 104 总召失败    | 104 客户端        | Wireshark、ASDU 日志    |
| BLE 连接不稳定      | nRF Sniffer       | 频谱仪、RSSI 日志       |
| LoRa 入网失败       | LoRa 网关日志     | 频谱仪、ADR/SNR 记录    |
| USB 枚举失败        | USB 协议分析仪    | dmesg、lsusb            |
| PCIe 链路不到 L0    | lspci + 示波器    | PCIe 分析仪、LTSSM 日志 |
| MIPI 黑屏/花屏      | MIPI 分析仪       | V4L2、示波器、EDID      |

## 测量安全

- 差分信号优先使用差分探头，避免单端探头造成误判。
- 测量市电或隔离电源时使用隔离探头和隔离变压器。
- 探头地线要短，避免形成大环路引入噪声。
- 高速信号测量注意带宽、采样率和探头负载效应。
- 故障注入前先确认保护边界，避免损坏 DUT 或测试设备。

## 关联文档

- [ACRONYMS](ACRONYMS.md)：缩写与标准编号速查。
- [GLOSSARY](GLOSSARY.md)：协议机制与工程术语。
- [STANDARDS](STANDARDS.md)：标准编号、范围与对应文档。
- [DOC_TEMPLATES](DOC_TEMPLATES.md)：测量报告与评审模板。
- [知识库索引](../INDEX.md)：按协议查找正文。
