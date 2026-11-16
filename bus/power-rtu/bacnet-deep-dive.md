# BACnet Deep Dive

## 目标

本文深入 BACnet 协议栈细节，重点解决 BVLC/NPDU/APDU 编码、对象属性建模、COV 订阅实现、Who-Is 设备发现、MS/TP 令牌环、BBMD 跨子网和现场排障。

## 协议栈分层

```text
物理层：Ethernet / RS485 / ARCNET / LonTalk
链路层：对应物理层
网络层：BACnet/IP（基于 IP）/ BACnet 虚拟链路
应用层：BACnet 服务
```

BACnet/IP 是基于 UDP 的简单协议栈；MS/TP 是基于 RS485 的令牌环。

## BACnet/IP 详解

### UDP 端口

```text
47808（0xBAC0）
UDP 单播 + 广播
```

### BVLC 帧

BVLC（6 字节头）：

```text
[Type 1 字节] [Function 1 字节] [Length 2 字节] [NPDU]
```

Type：

```text
0x81 = BVLC for BACnet/IP
```

Function：

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

### Foreign Device

```text
1. Foreign Device 通过 Register-Foreign-Device 注册 BBMD
3. BBMD 分配 TTL
5. Foreign Device 通过 BBMD 转发广播
7. 定期（< TTL / 2）重新注册
```

## NPDU 详解

NPDU 头部：

```text
[Version 1 字节 = 0x01] [Control 1 字节] [可选 DNET/DADR] [可选 SNET/SADR] [Hop Count 1 字节] [APDU]
```

Control 字节：

```text
bit 7：Network Layer Message (0 = BACnet APDU)
bit 6：Reserved
bit 5：Destination present
bit 4：Source present
bit 3：Reason
```

DNET/DADR（目的网络 / 目的地址）：

```text
DNET (2 字节)：目的网络
DADR (1 字节)：目的 MAC 地址
```

SNET/SADR（源网络 / 源地址）：

```text
SNET (2 字节)
SADR (1 字节)
```

Hop Count（1 字节）：最大跳数（通常 255）。

## APDU 详解

PDU Type 字节：

```text
bit 7：PDU 类型（0 = Confirmed / Unconfirmed, 1 = Ack/Error）
bit 6..4：保留
bit 3..0：详细类型
```

Confirmed Request APDU：

```text
PDU Type = 0x00
Seg (bit 7..4)：分段控制
Mor (bit 3)：More Segments
Invoke ID (1 字节)：请求标识
Service Choice (1 字节)：服务码
Service Request：服务参数
```

Unconfirmed Request APDU：

```text
PDU Type = 0x10
Service Choice (1 字节)
Service Request：服务参数
```

Complex ACK：

```text
PDU Type = 0x30
Invoke ID
Service Choice
Service ACK
```

Simple ACK：

```text
PDU Type = 0x20
Invoke ID
Service Choice
```

Error APDU：

```text
PDU Type = 0x50
Invoke ID
Service Choice
Error Class
Error Code
```

Reject APDU：

```text
PDU Type = 0x60
Invoke ID
Reject Reason
```

Abort APDU：

```text
PDU Type = 0x70
Invoke ID
Abort Reason
```

## Service Choice 完整列表

Confirmed 服务：

```text
0x00  AcknowledgeAlarm
0x01  ConfirmedCovNotification
0x02  ConfirmedEventNotification
0x03  GetAlarmSummary
0x04  GetEnrollmentSummary
0x05  SubscribeCOV
0x06  AtomicReadFile
0x07  AtomicWriteFile
0x08  AddListElement
0x09  RemoveListElement
0x0A  CreateObject
0x0B  DeleteObject
0x0C  ReadProperty
0x0D  ReadPropertyMultiple
0x0E  ReadPropertyConditional
0x0F  WriteProperty
0x10  WritePropertyMultiple
0x11  DeviceCommunicationControl
0x12  ConfirmedPrivateTransfer
0x13  ConfirmedTextMessage
0x14  ReinitializeDevice
0x15  VTOTransfer
0x16  ReadRange
0x17  UtcTimeSynchronization
0x18  ReadRange
0x19  ConfirmedAuditLogNotification
0x1A  AuditLogQuery
0x1B  AuditLogRetrieval
```

Unconfirmed 服务：

```text
0x00  I-Am
0x01  I-Have
0x02  UnconfirmedCovNotification
0x03  UnconfirmedEventNotification
0x04  UnconfirmedPrivateTransfer
0x05  UnconfirmedTextMessage
0x06  TimeSynchronization
0x07  Who-Has
0x08  Who-Is
0x09  I-Read
0x0A  I-Write
```

## 对象详解

### Device 对象

```text
属性：
  Object_Identifier
  Object_Name
  Object_Type
  System_Status
  Vendor_Name
  Vendor_Identifier
  Model_Name
  Firmware_Revision
  Application_Software_Version
  Protocol_Version
  Protocol_Revision
  Database_Revision
  Max_APDU_Length_Accepted
  Segmentation_Supported
  Device_Address_Binding
  Active_COV_Subscriptions
  Protocol_Services_Supported
  Protocol_Object_Types_Supported
  Max_Segments_Accepted
  Description
  Local_Time
  Local_Date
  UTC_Offset
  Daylight_Saving_Status
  APDU_Segment_Timeout
  APDU_Timeout
  Number_Of_APDU_Retries
```

### Analog Input / Output / Value

```text
属性：
  Object_Identifier
  Object_Name
  Object_Type
  Present_Value
  Description
  Status_Flags
  Event_State
  Reliability
  Out_Of_Service
  Units
  Min_Present_Value
  Max_Present_Value
  Resolution
  COV_Increment
  Deadband
```

### Binary Input / Output / Value

```text
属性：
  Object_Identifier
  Object_Name
  Object_Type
  Present_Value (0 / 1 / 2)
  Description
  Status_Flags
  Event_State
  Reliability
  Out_Of_Service
  Polarity (Normal / Inverted)
  Active_Text
  Inactive_Text
```

### Multi-state Input / Output / Value

```text
属性：
  Object_Identifier
  Object_Name
  Object_Type
  Present_Value (1..N)
  Number_Of_States
  Description
  Status_Flags
  Event_State
  Reliability
  Out_Of_Service
  State_Text
```

### Schedule

```text
属性：
  Object_Identifier
  Object_Name
  Object_Type
  Present_Value
  Effective_Period
  Weekly_Schedule
  Exception_Schedule
  List_Of_Object_Property_References
  Priority_For_Writing
  Out_Of_Service
```

### Trend Log

```text
属性：
  Object_Identifier
  Object_Name
  Object_Type
  Description
  Log_Enable
  Log_Interval
  Stop_When_Full
  Buffer_Size
  Log_Buffer
  Recording_Interval
  Number_Of_Records
  Total_Record_Count
  Last_Record_Time
  Log_Device_Object_Property
```

## 服务详解

### ReadProperty

```text
Confirmed Request:
  Service Choice 0x0C
  Service Request:
    Object Identifier
    Property Identifier
    Property Array Index (optional)
```

响应：

```text
Complex ACK:
  Service Choice 0x0C
  Service ACK:
    Object Identifier
    Property Identifier
    Property Value
```

### ReadPropertyMultiple

```text
Service Choice 0x0D
Service Request:
  List of Property References:
    Object Identifier
    Property Identifier (multiple)
```

响应：

```text
Complex ACK:
  List of Results:
    Object Identifier
    Property Identifier
    Property Value (or Error)
```

### WriteProperty

```text
Service Choice 0x0F
Service Request:
  Object Identifier
  Property Identifier
  Property Value
  Priority (1..16, optional)
```

### SubscribeCOV

```text
Service Choice 0x05
Service Request:
  Subscriber Process Identifier
  Monitored Object Identifier
  Issue Confirmed Notifications (boolean)
  Lifetime (seconds)
```

设备周期性检测变化并发送 COV Notification。

### AtomicWriteFile

```text
Service Choice 0x07
Service Request:
  File Identifier
  Start Position
  File Data
```

## COV 订阅机制

```text
1. BACS 订阅 AI 1 的 Present_Value（60 秒）
3. 设备记录订阅
5. 设备检测 Present_Value 变化（超 COV_Increment）
7. 设备发 COV Notification（Unconfirmed 或 Confirmed）
9. BACS 收到 → 处理
11. 定期续订（< Lifetime）
```

COV_Increment：

```text
AI 的 COV_Increment = 0.5
  Present_Value 变化超过 0.5 → 触发 COV
```

工程实现：

```text
1. 启动 BACS
3. 订阅对象 COV
5. 监听 COV Notification
7. 更新显示 / 触发逻辑
```

## 设备发现

### Who-Is / I-Am

```text
1. BACS 发 Who-Is 广播
3. 所有设备 → I-Am
5. BACS 记录设备
```

### Who-Has / I-Have

```text
1. BACS 发 Who-Has + Object Name
5. 设备 → I-Have（匹配对象）
```

工程实践：

- 启动时全网 Who-Is 扫描。
- 维护设备列表。
- 定期 Who-Is 检查设备存活。

## BBMD 跨子网

BBMD 部署：

```text
1. 在每个子网部署 BBMD
3. BBMD 互相同步 BDT
5. Foreign Device 注册到 BBMD
```

Foreign Device 流程：

```text
1. Foreign Device 通过 Register-Foreign-Device 注册 BBMD
3. Foreign Device 通过 BBMD 发送广播
5. BBMD 转发广播到其他 BBMD
7. BBMD 转发广播到 Foreign Device
```

工程实现：

```text
1. BBMD 配置（IP / 端口 / BDT）
3. Foreign Device 注册
5. 定期续期（< TTL / 2）
7. 广播通过 BBMD 转发
```

## MS/TP 详解

MS/TP 是 RS485 上的令牌环协议：

```text
节点 0..127
波特率：9600 / 19200 / 38400 / 76800 / 115200
```

帧格式：

```text
[前导 2 字节] [帧类型 1] [目的地址 1] [源地址 1] [数据长度 2] [数据 N] [CRC8]
```

前导：

```text
0x55 0xFF
```

帧类型：

```text
0x00  Token（持有者发送）
0x01  Poll For Master
0x02  Reply To Poll For Master
0x03  Test Request
0x04  Test Response
0x05  Data Expecting Reply
0x06  Data Not Expecting Reply
0x07  Reply Postponed
```

令牌环流程：

```text
1. 节点初始化：地址 0..127 顺序
3. 节点持有令牌 → 可发送
5. 令牌到达 → 节点判断是否要发送
7. Token 转下一个节点
9. Poll For Master → 找新节点
```

MS/TP 帧：

```text
Token Frame：
  0x55 0xFF 0x00 dest src 0x00 0x00 CRC

Poll For Master：
  0x55 0xFF 0x01 dest src 0x00 0x00 CRC

Data Frame：
  0x55 0xFF 0x05/06 dest src len lo/hi data CRC
```

CRC8 计算：

```text
CRC = 0xFF
for each byte:
  CRC = table[CRC XOR byte]
```

## 工程实现

### 主站（BACS）实现要点

```text
1. UDP client/server（47808）
3. BVLC 解析
4. NPDU 解析
5. APDU 解析
6. 服务编码
7. 对象模型管理
8. 设备列表（Who-Is）
9. COV 订阅
10. 定期轮询
11. BBMD 注册（如需要）
```

### 设备（控制器）实现要点

```text
1. UDP server（47808）
3. BVLC 响应
4. NPDU 响应
5. APDU 服务
6. 对象模型（AI/AO/BI/BO/Schedule/Trend Log）
7. ReadProperty 实现
8. WriteProperty 实现
9. COV 检测
10. Who-Is 响应
11. ReadPropertyMultiple 实现
```

## 抓包排障

Wireshark BACnet dissector：

```text
1. UDP 47808
3. BVLC 解析
5. NPDU 解析
7. APDU 解析
9. 对象 ID / 属性 ID
11. 服务码
```

工程排障清单：

```text
1. UDP 端口未开
3. BVLC 编码错
5. NPDU 编码错
7. APDU 编码错
9. 对象 ID 不存在
11. 属性 ID 错
13. 服务未实现
15. COV 不触发
17. MS/TP 令牌环异常
19. BBMD 注册失败
```

## 现场常见故障

| 现象 | 优先检查 |
| --- | --- |
| UDP 无响应 | 端口 / 防火墙 |
| Who-Is 无响应 | 设备支持 / 网络 |
| I-Am 格式错 | NPDU / APDU |
| ReadProperty 失败 | 对象 ID / 属性 ID |
| COV 不触发 | 订阅 / 阈值 |
| MS/TP 不通 | 令牌环 / 波特率 |
| BBMD 注册失败 | IP / 端口 |

## 深度检查清单

- UDP 端口 47808 已开（BACnet/IP）。
- BVLC 编码正确。
- NPDU 编码正确。
- APDU 编码正确。
- Device 对象存在。
- AI/AO/BI/BO 对象模型完整。
- ReadProperty / ReadPropertyMultiple 支持。
- WriteProperty 支持。
- SubscribeCOV 支持。
- COV_Increment 配置。
- Who-Is / I-Am 支持。
- Object_Identifier 编码正确。
- Property_Identifier 编码正确。
- BBMD 配置（跨子网）。
- MS/TP 令牌环（RS485 场景）。
- MS/TP CRC8 计算正确。
- 设备发现 / 状态管理。
- 定期轮询 / COV 订阅协同。