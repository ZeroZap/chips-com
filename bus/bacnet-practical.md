# BACnet Practical Guide

## 目标

本文用于把 BACnet 工程链路调通：BACnet/IP UDP 接入、BVLC 解析、APDU 编码、对象读写、COV 订阅、Who-Is / I-Am 设备发现和 MS/TP 令牌环。

## BACnet/IP 接入

```text
BACS（client）→ UDP:47808 → 设备（server）
```

默认端口：47808（0xBAC0）

工程注意：

- BACnet/IP 是 UDP 协议。
- 广播地址：子网广播。
- BBMD：跨子网广播管理。

## BVLC 帧

```text
[BVLC Type 1 字节] [BVLC Function 1 字节] [BVLC Length 2 字节] [NPDU]
```

BVLC Type：

```text
0x81 = BVLC for BACnet/IP
```

BVLC Function（部分）：

```text
0x0A  Original-Unicast-NPDU
0x0B  Original-Broadcast-NPDU
0x04  Forwarded-NPDU（用于 BBMD）
0x05  Register-Foreign-Device
```

## NPDU 编码

NPDU（Network Protocol Data Unit）：

```text
[Version 1 字节 = 0x01] [Control 1 字节] [DNET 2 字节] [DADR 1 字节] [SNET 2 字节] [SADR 1 字节] [Hop Count 1 字节] [APDU]
```

Control 字节：

```text
bit 7：Network layer message (0 = BACnet APDU)
bit 6：Reserved (0)
bit 5：Destination present
bit 4：Source present
bit 3：Reason (0 = normal)
```

## APDU 解析

Confirmed Request APDU：

```text
[0x00] [0x00] [Invoke ID 1 字节] [Service Choice 1 字节] [Service Request]
```

Unconfirmed Request APDU：

```text
[0x10] [Service Choice 1 字节] [Service Request]
```

Complex ACK APDU：

```text
[0x30] [Invoke ID 1 字节] [Service Choice 1 字节] [Service ACK]
```

## 报文示例

### Who-Is（设备发现）

BACS → 设备：

```text
BVLC (0x0B Original-Broadcast)
NPDU
  Version 0x01
  Control 0x00
APDU (Unconfirmed Request, Service Choice 0x08 = Who-Is)
```

设备 → BACS（响应）：

```text
BVLC (0x0A Original-Unicast)
NPDU
  Version 0x01
  Control 0x00
APDU (Unconfirmed Request, Service Choice 0x00 = I-Am):
  Object Identifier: Device, 100
  Max APDUs (1 byte): 0x01
  Segmentation Support (1 byte): 0x00
  Vendor ID (2 bytes): 0x1337
```

### ReadProperty（读 AI 1 Present_Value）

BACS → 设备：

```text
BVLC (0x0A Original-Unicast)
NPDU
APDU (Confirmed Request, Service Choice 0x0C = ReadProperty):
  Invoke ID: 0x01
  Object Identifier: (Object Type AI = 0, Instance 1)
    Tag 0: Context 0 (Object Identifier)
    Length 4
    0x00 0x00 0x00 0x01
  Property Identifier: (Present_Value = 85)
    Tag 1: Context 1 (Property Identifier)
    Length 1
    0x55 = 85
```

设备 → BACS（响应）：

```text
BVLC (0x0A Original-Unicast)
NPDU
APDU (Complex ACK, Service Choice 0x0C):
  Invoke ID: 0x01
  Service ACK:
    Object Identifier: AI 1
    Property Identifier: Present_Value (85)
    Property Value: REAL = 23.5
      Tag 4: Application 4 (Real)
      Length 4
      0x41 0xBC 0x00 0x00 (IEEE 754 float)
```

### ReadPropertyMultiple

BACS → 设备：

```text
APDU (Confirmed Request, Service Choice 0x0E = ReadPropertyMultiple):
  Invoke ID: 0x02
  Object Identifier: Device, 100
  Property References:
    Property Identifier: Object_Name (77)
    Property Identifier: Vendor_Name (121)
```

设备 → BACS：

```text
APDU (Complex ACK):
  Invoke ID: 0x02
  Service ACK:
    Object Identifier: Device, 100
    Property Values:
      Object_Name: Character String "AHU_01"
      Vendor_Name: Character String "VendorX"
```

### SubscribeCOV

BACS → 设备：

```text
APDU (Confirmed Request, Service Choice 0x05 = SubscribeCOV):
  Invoke ID: 0x03
  Subscriber Process Identifier: 0x01
  Monitored Object Identifier: AI 1
  Issue Confirmed Notifications: false
  Lifetime (s): 60
```

设备 → BACS（响应）：

```text
APDU (Simple ACK, Service Choice 0x05):
  Invoke ID: 0x03
```

设备 → BACS（变位通知）：

```text
APDU (Unconfirmed Request, Service Choice 0x02 = Unconfirmed COV Notification):
  Subscriber Process Identifier: 0x01
  Initiating Device Identifier: Device, 100
  Monitored Object Identifier: AI 1
  Time Remaining: 60
  List of Values:
    Property Identifier: Present_Value
    Value: REAL = 23.7
```

### WriteProperty

BACS → 设备：

```text
APDU (Confirmed Request, Service Choice 0x0F = WriteProperty):
  Invoke ID: 0x04
  Object Identifier: AO 1
  Property Identifier: Present_Value
  Property Value: REAL = 50.0
```

设备 → BACS：

```text
APDU (Simple ACK, Service Choice 0x0F):
  Invoke ID: 0x04
```

## 对象编码

BACnet 对象标识符 4 字节：

```text
Tag: 0x00 (Application 0) Context 0
Value: 12 字节长度（实际 4 字节）

例：AI 1
  Object Type: 0 (Analog Input)
  Instance: 1
  
  Tag 0x00 (Context 0): Object Identifier
  Length 4
  Value: 0x00 0x00 0x00 0x01
  
  解码：
    Object Type = (0x00 >> 12) = 0 (AI)
    Instance = (0x00 & 0xFFF) << 16 + ...
    实际：Bit 31..22 = Object Type, Bit 21..0 = Instance
```

常用对象 ID 编码：

```text
Device 100: 0x00 0x00 0x00 0x64
AI 1: 0x00 0x00 0x00 0x01
AO 1: 0x00 0x00 0x01 0x00
BI 1: 0x00 0x00 0x02 0x00
BO 1: 0x00 0x00 0x03 0x00
```

## BACnet/IP 设备发现

Who-Is 流程：

```text
1. BACS 发 Who-Is 广播
3. 设备收到 → 回 I-Am
5. BACS 记录设备 Object Identifier / IP / 端口
```

工程实现：

```text
1. 启动 BACS
3. 发 Who-Is 广播到 UDP 47808
5. 等待 I-Am 响应（超时 5s）
7. 建立设备列表
9. 读 Device Object 属性（Vendor_Name / Object_Name / 等）
```

## BBMD（跨子网）

BBMD 配置：

```text
1. 配置 BBMD IP / 端口
3. BBMD 注册 Foreign Device
5. Foreign Device 通过 BBMD 转发广播
```

工程实践：

- 多子网互联需要 BBMD。
- BBMD 之间互相同步 BDT。

## BACnet MS/TP

帧格式：

```text
[前导 0x55 0xFF] [帧类型] [目的地址] [源地址] [长度] [数据] [CRC8]
```

前导 2 字节（用于同步）。

帧类型：

```text
0x00  Token（令牌）
0x01  Poll For Master（查找主机）
0x02  Reply To Poll For Master
0x03  Test Request
0x04  Test Response
0x05  BACnet Data Expecting Reply
0x06  BACnet Data Not Expecting Reply
0x07  Reply Postponed
```

### 令牌环流程

```text
1. Master 1 持有令牌
3. Master 1 发送 Token 到下一个 Master（地址递增）
5. Master 2 收到令牌 → 发送数据帧 / 转发 Token
7. 持续循环
9. Poll For Master：new device 主动发送 → 找下一个 Master
```

### RS485 接线

```text
A+/B- 全双工（少数）
A/B 半双工（主流）

MS/TP 最多 127 节点
波特率：9600 / 19200 / 38400 / 76800 / 115200
终端电阻：120Ω 两端
```

## 调试工具

- Wireshark：BACnet dissector（支持 BVLC / APDU）。
- BACnet 客户端：BACnet Browser（如 YABE）。
- BACnet 模拟：bds / BACnet 设备模拟器。
- 网络扫描：BACnet/IP 设备扫描工具。

## 调试步骤

1. UDP 连接到设备 47808。
2. 发 Who-Is，接收 I-Am。
3. 读 Device 对象的 Object_Name。
4. 读 Device 的 Vendor_Name。
5. 读 AI 1 的 Present_Value。
6. 读 Schedule 1 的属性。
7. 订阅 COV。
9. 写 AO 1 的 Present_Value。
10. 测试 MS/TP（如果使用 RS485）。

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| UDP 无响应 | 端口 / 防火墙 |
| Who-Is 无响应 | 设备不支持 / 网络 |
| I-Am 格式错 | NPDU / APDU |
| ReadProperty 失败 | 对象 ID / 属性 ID |
| COV 不触发 | 订阅失败 / 阈值 |
| MS/TP 不通 | 令牌环 / 波特率 |

## 实战检查清单

- UDP 端口 47808 已开。
- BVLC 编码正确。
- NPDU 编码正确。
- APDU 编码正确。
- Device 对象存在。
- AI/AO/BI/BO 对象存在。
- ReadProperty / ReadPropertyMultiple 支持。
- COV 订阅支持。
- Who-Is / I-Am 支持。
- BBMD 配置（如跨子网）。
- MS/TP 令牌环（RS485 场景）。