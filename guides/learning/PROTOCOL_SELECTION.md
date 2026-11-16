---
tags:
  - layer/guides
  - type/selection
  - topic/learning
---

# Protocol Selection Matrix

## 目标

本文提供芯片间通信协议选型矩阵，帮助根据距离、速度、设备数量、实时性、抗干扰、软件复杂度和生态要求选择合适接口。

## 快速选型表

| 场景              | 优先考虑           |
| ----------------- | ------------------ |
| 简单点对点调试    | UART               |
| 多个低速板内设备  | I2C / I3C          |
| 高速简单外设      | SPI / QSPI / OSPI  |
| 温度或身份识别    | 1-Wire             |
| 电源管理          | SMBus / PMBus      |
| 工业长距离低成本  | RS485 + Modbus RTU |
| 车载/工业实时控制 | CAN / CANopen      |
| 低成本车身节点    | LIN                |
| 通用外设接 PC     | USB                |
| 局域网通信        | Ethernet + TCP/UDP |
| 简单工业以太网    | Modbus TCP         |
| 高速实时运动控制  | EtherCAT           |
| 摄像头            | MIPI CSI           |
| 显示屏            | MIPI DSI           |
| Wi-Fi 模块        | SDIO / USB / PCIe  |
| 高速系统扩展      | PCIe               |

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

## 汽车与诊断选型

| 场景                  | 优先考虑        | 说明                    |
| --------------------- | --------------- | ----------------------- |
| 车身低成本节点        | LIN             | 单线、主从调度、成本低  |
| 车身/动力实时控制     | CAN / CAN FD    | 多主、仲裁、错误检测    |
| 大 payload/高带宽车载 | CAN FD / CAN XL | 需控制器/收发器支持     |
| 工业设备对象模型      | CANopen         | 对象字典、PDO/SDO       |
| 商用车网络            | J1939           | PGN/SPN、地址声明       |
| 多帧诊断传输          | ISO-TP          | UDS/OBD 的公共底座      |
| OEM 诊断/刷写         | UDS             | 会话、安全访问、DID/DTC |
| 乘用车法规诊断        | OBD-II          | 排放相关、PID/DTC       |
| 商用车全球诊断        | WWH-OBD         | UDS 子集、3 字节 DTC    |

## 电力 / 水务 / 表计 / 楼宇选型

| 场景                | 优先考虑           | 说明                     |
| ------------------- | ------------------ | ------------------------ |
| 电网远动/调度       | IEC 60870-5-104    | TCP/IP、ASDU、总召/遥控  |
| 串行远动            | IEC 60870-5-101    | 串口、链路地址           |
| 变电站自动化        | IEC 61850          | 信息模型、GOOSE、SV      |
| 电力/水务主站       | DNP3               | 对象模型、事件、时间同步 |
| 电表集抄            | DL/T 645           | 数据标识、RS485/红外     |
| 水表/热表/燃气表    | CJ/T 188           | 户用计量仪表             |
| 水文监测            | SL 651             | 测站-中心站              |
| 水资源监测          | SZY 206 + SL/T 427 | 配套使用                 |
| 环保在线监控        | HJ 212             | 污染物因子、命令码       |
| 楼宇自控            | BACnet             | 对象/服务、BBMD          |
| 工业信息模型/跨系统 | OPC UA             | 信息模型、安全、订阅     |
| 简单仪表/采集       | Modbus RTU/TCP     | 成本低、生态广           |

## 无线 / IoT 选型

| 场景             | 优先考虑            | 说明                      |
| ---------------- | ------------------- | ------------------------- |
| 手机周边/可穿戴  | BLE                 | 低功耗、GATT、生态成熟    |
| 智能家居 Mesh    | ZigBee / Thread     | Mesh、低功耗              |
| 多生态智能家居   | Matter              | 跨生态、基于 Thread/Wi-Fi |
| 远距离低功耗传感 | LoRaWAN             | 长距离、低速率、网关      |
| 蜂窝中速率 IoT   | LTE Cat-1           | 成本/速率平衡             |
| 蜂窝低功耗广域   | LTE Cat-M1 / NB-IoT | 覆盖、功耗、时延权衡      |
| 海洋/边远地区    | Satellite-IoT       | 卫星覆盖、成本/时延       |
| 应急定位/求救    | PLB / Rescue-Comms  | 法规、注册、可靠性        |
| 私有 2.4 GHz     | nRF2401             | 低成本、私有协议          |

## 工业以太网选型

| 场景             | 优先考虑    | 说明            |
| ---------------- | ----------- | --------------- |
| 西门子生态       | PROFINET    | RT/IRT、GSDML   |
| 多轴运动控制     | EtherCAT    | 周期帧、DC 同步 |
| Rockwell/AB 生态 | EtherNet/IP | CIP、EDS        |
| 简单监控         | Modbus TCP  | 成本低、工具多  |
| 确定性以太网     | TSN         | gPTP、Qbv、Qav  |

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

- 是否有认证或授权要求？
- 是车载法规诊断还是 OEM 诊断？
- 是电力远动、变电站自动化还是楼宇自控？
- 设备是电池供电还是市电供电？
- 是否需要 Mesh、漫游或卫星覆盖？
- 是否需要确定性延迟和时间同步？
- 是否需要网关/协议转换？

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
