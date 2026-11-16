---
tags:
  - layer/bus
  - type/overview
  - protocol/bacnet
  - topic/power-rtu
---

# BACnet

## 定位

BACnet（Building Automation and Control Networks）是楼宇自动化国际标准，ASHRAE / ANSI / ISO 16484-5 标准。用于暖通空调（HVAC）、照明、安防、能源管理。

```text
BACnet 1.0: 1995
BACnet 2016: 当前
ISO 16484-5: 国际标准
```

## 应用领域

- 暖通空调（HVAC）：空调机组、新风机组、冷热源。
- 照明控制。
- 安防监控（门禁、报警）。
- 能源管理。
- 给排水。
- 电梯监控。
- 智能建筑集成。

## 协议栈

```text
物理层：Ethernet / RS485 / ARCNET / LonTalk / ZigBee
链路层：Ethernet / MS/TP / ARCNET / LonTalk / ZigBee
网络层：BACnet/IP（基于 IP）/ BACnet 虚拟链路
应用层：BACnet 服务
```

## 三种主流物理

| 版本 | 物理 | 速率 |
| --- | --- | --- |
| BACnet/IP | Ethernet / IP | 10/100/1000 Mbps |
| BACnet MS/TP | RS485 | 9.6 kbps - 115.2 kbps |
| BACnet Ethernet | 10BASE5/2 | 10 Mbps |

## 通信模型

BACnet 是 Client / Server 模型，但与 HTTP 不同：

```text
Client（BACS = Building Automation and Control System）
  → ReadProperty / ReadPropertyMultiple
  → WriteProperty
  → SubscribeCOV

Server（设备 / 控制器）
  → 回 ReadProperty / ReadPropertyMultiple 响应
  → 发 COV Notification
```

## BACnet/IP

```text
UDP 端口 47808（0xBAC0）
BVLC（BACnet Virtual Link Control）
```

BVLC 类型：

```text
0x00  BVLC-Result
0x01  Write-Broadcast-Distribution-Table
0x02  Read-Broadcast-Distribution-Table
0x03  Read-Broadcast-Distribution-Table-Ack
0x04  Forwarded-NPDU
0x05  Register-Foreign-Device
0x06  Read-Foreign-Device-Table
0x07  Read-Foreign-Device-Table-Ack
0x08  Delete-Foreign-Device-Table-Entry
0x09  Distribute-Broadcast-To-Network
0x0A  Original-Unicast-NPDU
0x0B  Original-Broadcast-NPDU
```

BBMD（BACnet/IP Broadcast Management Device）：

```text
跨子网广播管理
BBMD 注册 / 转发 / 广播分发
```

## BACnet MS/TP

```text
RS485 半双工
令牌环（Master-Slave Token Passing）
最大节点数：127
```

波特率：

```text
9600 / 19200 / 38400 / 76800 / 115200
```

帧格式：

```text
[前导 0x55 0xFF] [帧类型] [目的地址] [源地址] [长度] [数据] [CRC8]
```

帧类型：

```text
0x00  Token
0x01  Poll For Master
0x02  Reply To Poll For Master
0x03  Test Request
0x04  Test Response
0x05  BACnet Data Expecting Reply
0x06  BACnet Data Not Expecting Reply
0x07  Reply Postponed
```

## BACnet 对象模型

BACnet 设备模型化为对象集合：

```text
Device 1
  ├─ Analog Input 1（温度）
  ├─ Analog Input 2（湿度）
  ├─ Analog Output 1（阀门开度）
  ├─ Binary Input 1（开关状态）
  ├─ Binary Output 1（灯光）
  ├─ Schedule 1（定时调度）
  └─ Trend Log 1（历史记录）
```

常用对象类型：

```text
0  Analog Input      AI
1  Analog Output     AO
2  Analog Value      AV
3  Binary Input      BI
4  Binary Output     BO
5  Binary Value      BV
6  Calendar          CAL
7  Command           CMD
8  Device            DEV
13  Multi-state Input  MI
14  Multi-state Output MO
15  Notification Class NC
16  Program           PG
17  Schedule         SCH
20  Trend Log         TL
23  File              F
24  Loop              LOOP
28  Event Enrollment  EE
29  Group             G
```

## 对象属性

每个对象有标准属性：

```text
Object Identifier
Object Name
Object Type
Present Value
Status Flags
Event State
Out of Scope（呈现值）
Reliability
Description
Location
Vendor Name
```

不同对象有不同属性：

```text
Analog Input:
  Present_Value
  Units
  Resolution
  COV_Increment
  Deadband

Schedule:
  Effective_Period
  Weekly_Schedule
  Exception_Schedule
  List_Of_Object_Property_References

Trend Log:
  Log_Buffer
  Log_Interval
  Stop_When_Full
  Record_Count
  Total_Record_Count
```

## BACnet 服务

数据访问：

```text
ReadProperty
ReadPropertyMultiple
WriteProperty
AddListElement
RemoveListElement
CreateObject
DeleteObject
```

报警 / 事件：

```text
AcknowledgeAlarm
ConfirmedEventNotification
UnconfirmedEventNotification
GetAlarmSummary
GetEventInformation
```

文件：

```text
AtomicReadFile
AtomicWriteFile
```

COV（Change Of Value）：

```text
SubscribeCOV
SubscribeCOVPermanent
ConfirmedCOVNotification
UnconfirmedCOVNotification
```

设备管理：

```text
Who-Is / I-Am
Who-Has / I-Have
ReadRange
```

## APDU 编码

BACnet APDU（应用层协议数据单元）：

```text
[PDU Type] [Service Choice / Invoke ID] [Service Request / Confirmed Service Ack]
```

PDU 类型：

```text
0x00  Confirmed Request
0x10  Unconfirmed Request
0x20  Simple ACK
0x30  Complex ACK
0x40  Segment ACK
0x50  Error
0x60  Reject
0x70  Abort
```

Confirmed Request：

```text
PDU Type: 0x00
Segment: 0x00 (not segmented)
Mor: 0x00
Invoke ID: 0x01
Service Choice: ReadProperty = 12
Service Request:
  Object Identifier
  Property Identifier
  Property Array Index (optional)
```

## 报文示例

### Who-Is

```text
APDU: Unconfirmed Request
Service Choice: Who-Is = 8
Service Request: (无) 或 [Low-Limit, High-Limit]
```

设备响应：

```text
I-Am (Unconfirmed Request, Service Choice 0)
Service Request:
  Object Identifier: Device, 100
  Max APDUs (1)
  Segmentation Support (0)
  Vendor ID (0x1337)
```

### ReadProperty

```text
Confirmed Request (Service Choice 12):
  Object Identifier: Analog Input, 1
  Property Identifier: Present_Value = 85
```

响应：

```text
Complex ACK:
  Object Identifier: Analog Input, 1
  Property Identifier: Present_Value
  Property Value: REAL = 23.5
```

### COV Notification

```text
Unconfirmed Request (Service Choice 0x02 = Unconfirmed COV Notification):
  Subscriber Process Identifier
  Initiating Device Identifier: Device, 100
  Monitored Object Identifier: Analog Input, 1
  Time Remaining
  List of Values:
    Property Identifier: Present_Value
    Property Value: REAL = 23.7
```

## 适用场景

- 楼宇 HVAC 控制。
- 楼宇能源管理。
- 楼宇照明控制。
- 楼宇集成系统。
- 智慧城市。
- 工业园区。
- 数据中心机房。

## 延伸阅读

- `bus/power-rtu/rtu-protocols.md`：RTU 设备协议全集。
- `bus/industrial/modbus.md`：与 Modbus 系列对比。
- `bus/industrial/opcua.md`：与 OPC UA 对比。

## 检查清单

- UDP 端口 47808 已开（BACnet/IP）。
- BVLC 解析正确。
- APDU 编码正确。
- Device 对象存在。
- 对象集合（AI/AO/BI/BO 等）。
- ReadPropertyMultiple 支持。
- COV Subscription 支持。
- Who-Is / I-Am 支持。
- BBMD 配置（跨子网时）。
- MS/TP 令牌环（RS485 场景）。