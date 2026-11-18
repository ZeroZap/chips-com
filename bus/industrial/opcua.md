---
tags:
  - layer/bus
  - type/overview
  - protocol/opcua
  - topic/industrial
---

# OPC UA

## 定位

OPC UA（OPC Unified Architecture）是 OPC 基金会新一代工业通信标准，用于工业 4.0、数字孪生、MES 集成、设备互操作。

```text
OPC Classic：DA / HDA / AE（基于 COM/DCOM，已淘汰）
OPC UA：IEC 62541 标准（替代 OPC Classic）
```

## 应用领域

- 工业 4.0 制造。
- 工厂数字化。
- MES / ERP 集成。
- 数字孪生。
- 设备互操作。
- 工业云平台对接。
- 楼宇 / 能源 / 流程行业。

## 协议分层

```text
物理层：以太网
链路层：以太网
传输层：TCP（端口 4840）/ HTTPS / WebSocket
编码层：二进制 / XML / JSON
应用层：OPC UA 服务
```

## 通信模型

```text
Client（MES / SCADA / 数字孪生平台）
  → CreateSession / ActivateSession
  → Browse（地址空间发现）
  → Read / Write
  → Call（方法调用）
  → CreateSubscription（订阅）

Server（PLC / RTU / 控制器）
  → 服务响应
  → Publish（推送通知）
```

## 端口

```text
OPC UA TCP 二进制：4840
OPC UA HTTPS：443
WebSocket：4840 + 升级
```

## 信息建模

OPC UA 核心是地址空间（AddressSpace）：

```text
地址空间 = 节点树
节点之间通过引用（Reference）连接
节点类型：
  Object      实体
  Variable    变量
  Method      方法
  ObjectType  对象类型
  VariableType 变量类型
  ReferenceType 引用类型
  DataType    数据类型
  View        视图
```

### 节点属性

每个节点有标准属性：

```text
NodeId
BrowseName
DisplayName
Description
WriteMask
UserWriteMask
References
```

Variable 节点额外属性：

```text
Value
DataType
ValueRank
ArrayDimensions
AccessLevel
UserAccessLevel
MinimumSamplingInterval
Historizing
```

## 节点 ID（NodeId）

```text
NodeId = NamespaceIndex:Identifier
NamespaceIndex：0..65535
Identifier：可数字或字符串

例：
  ns=0;i=85  默认命名空间，ID 85
  ns=1;s=Device1.Temperature  命名空间 1，字符串 ID
```

NodeId 编码：

```text
FourByteNodeId：0, 1 字节命名空间 + 1 字节 ID（ns 0..255, id 0..255）
NumericNodeId：0, 2 字节命名空间 + 4 字节 ID
StringNodeId：1, 2 字节命名空间 + N 字节字符串
GuidNodeId：2, 2 字节命名空间 + 16 字节 GUID
ByteStringNodeId：3, 2 字节命名空间 + N 字节字符串
```

## 命名空间

OPC UA 命名空间：

```text
Namespace 0：OPC UA 内置（BaseNodeClass 等）
Namespace 1：服务器默认（服务器地址空间）
Namespace 2..N：自定义（用户定义）
```

## 服务

OPC UA 服务分为多个族：

### 通用服务

```text
FindServers
GetEndpoints
CreateSession
ActivateSession
CloseSession
```

### 地址空间服务

```text
Browse
BrowseNext
Read
Write
TranslateBrowsePathsToNodeIds
RegisterNodes
UnregisterNodes
```

### 方法调用

```text
Call
```

### 订阅 / 通知

```text
CreateSubscription
AddMonitoredItems
ModifyMonitoredItems
RemoveMonitoredItems
DeleteSubscription
SetPublishingMode
Publish
SetMonitoringMode
Republish
```

### 历史访问

```text
HistoryRead
HistoryUpdate
```

## 订阅 / 通知

```text
1. 客户端创建 Subscription
3. 客户端添加 MonitoredItem（指定 NodeId / SamplingInterval / 触发方式）
5. 服务器检测数据变化
7. 服务器发 Publish（Notification）
9. 客户端接收并 Acknowledge
```

MonitoredItem 触发方式：

```text
StatusValue（值变化）
StatusValueTimestamp（值 + 时间戳）
StatusValueTimestampStatus
```

工程实现：

```text
1. 订阅一个或多个 MonitoredItem
3. 接收 Publish
5. 处理数据
7. Acknowledge
```

## 历史访问

```text
HistoryRead：
  - 按时间范围读取历史数据
  - 聚合（平均 / 最大 / 最小）

HistoryUpdate：
  - 插入 / 删除 / 替换历史数据
```

工程实践：

- 工厂历史数据查询。
- 趋势曲线分析。
- 性能报告。

## 安全

### 安全策略

```text
None（无安全）
Basic128Rsa15（RSA 15）
Basic256（SHA-1）
Basic256Sha256（SHA-256，推荐）
Aes128Sha256RsaOaep
Aes256Sha256RsaPsa
```

### 消息安全

```text
None（明文）
Sign（签名）
SignAndEncrypt（签名+加密）
```

### 用户认证

```text
Anonymous（匿名）
UserNamePassword（用户名密码）
Certificate（证书）
IssuedToken（JWT / SAML）
```

## 编码

### 二进制编码

```text
类型 ID + 长度 + 数据
高效，适合 OPC UA TCP
```

### XML 编码

```text
文本格式，适合 OPC UA HTTPS
```

### JSON 编码

```text
云原生友好
适合工业云
```

## Companion Specifications

OPC UA 联盟定义行业信息模型：

```text
OPC UA for Machinery
OPC UA for Robotics
OPC UA for Plastics (EUROMAP)
OPC UA for Machine Tools
OPC UA for Process Automation
OPC UA for ISA-95
OPC UA for BACnet（与 BACnet 集成）
```

工程实践：

- 采用行业 Companion Specifications。
- 与特定行业客户匹配。

## 报文示例

### GetEndpoints

```text
Client → Server:
  Message Type: MSG (0x4D 0x53 0x47 = "MSG")
  Message Size: ...
  SecureChannelId: 1
  SecurityTokenId: 1
  Sequence Number: 1
  Request Id: 1
  Encoded Type: GetEndpointsRequest
```

Server → Client:

```text
  Encoded Type: GetEndpointsResponse
  Endpoints:
    EndpointUrl
    SecurityPolicyUri
    SecurityMode
    ServerCertificate
    TransportProfileUri
    ServerSecurityPolicy (每种安全策略)
```

### Read

```text
Client → Server (ReadRequest):
  NodesToRead:
    NodeId: ns=1;s=Device1.Temperature
    AttributeId: Value (13)
```

Server → Client (ReadResponse):

```text
  Results:
    StatusCode: Good
    Value: Double = 23.5
```

### Subscribe

```text
Client → Server (CreateSubscriptionRequest):
  RequestedPublishingInterval: 1000
  RequestedLifetimeCount: 60
  RequestedMaxKeepAliveCount: 10
  MaxNotificationsPerPublish: 100
  PublishingEnabled: true
```

Server → Client:

```text
  SubscriptionId: 1
  RevisedPublishingInterval: 1000
  RevisedLifetimeCount: 60
  RevisedMaxKeepAliveCount: 10
```

### AddMonitoredItems

```text
Client → Server (AddMonitoredItemsRequest):
  SubscriptionId: 1
  ItemsToCreate:
    ItemToCreate:
      ItemToMonitor:
        NodeId: ns=1;s=Device1.Temperature
        AttributeId: Value
      MonitoringMode: Reporting
      SamplingInterval: 500
      Filter: None
      QueueSize: 1
      DiscardOldest: true
```

Server → Client:

```text
  Results:
    MonitoredItemId: 100
    StatusCode: Good
    RevisedSamplingInterval: 500
```

### Publish

```text
Server → Client (PublishRequest 服务端推送):
  SubscriptionId: 1
  NotificationMessage:
    SequenceNumber
    PublishTime
    Notification:
        DataChangeNotification:
          MonitoredItems:
            MonitoredItemId: 100
            Value: Double = 23.7
            StatusCode: Good
            ServerTimestamp
```

## 适用场景

- 工厂数字化（Industry 4.0）。
- MES / ERP 集成。
- 数字孪生。
- 设备互操作。
- 工业云平台。
- 跨厂区数据汇聚。

## 延伸阅读

- [[bus/power-rtu/rtu-protocols|rtu-protocols]]：RTU 设备协议全集。
- [[bus/power-rtu/bacnet|bacnet]]：与 BACnet 对比（楼宇场景）。
- [[bus/industrial/mqtt|mqtt]]：与 MQTT 对比（云场景）。

## 检查清单

- TCP 端口 4840 已开（OPC UA TCP）。
- HTTPS 端口 443 已开（OPC UA HTTPS）。
- 安全策略协商（GetEndpoints）。
- 会话创建（CreateSession + ActivateSession）。
- 用户认证（Anonymous / UserNamePassword / Certificate）。
- 地址空间 Browse 完整。
- Read / Write 支持。
- Call 方法调用支持。
- CreateSubscription + MonitoredItems 支持。
- HistoryRead 历史访问支持。
- 消息安全（Sign / SignAndEncrypt）。
- Companion Specifications 实现。