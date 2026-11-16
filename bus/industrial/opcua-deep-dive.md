---
tags:
  - layer/bus
  - type/deep-dive
  - protocol/opcua
  - topic/industrial
---

# OPC UA Deep Dive

## 目标

本文深入 OPC UA 协议栈细节，重点解决地址空间建模、NodeId 编码、服务调用、订阅通知机制、安全策略与证书管理、信息建模标准和现场排障。

## 协议栈分层

```text
物理层：以太网
链路层：以太网
传输层：TCP（端口 4840）/ HTTPS / WebSocket
编码层：二进制 / XML / JSON
应用层：OPC UA 服务
```

OPC UA 复杂在信息建模和订阅机制。

## 传输方式

### OPC UA TCP

```text
TCP 4840
二进制编码（高效）
底层消息：MSG / OPN / HEL / ACK / ERR / CLO
```

底层消息：

```text
HEL：Hello（客户端 → 服务端）
ACK：ACK（服务端 → 客户端）
OPN：OpenSecureChannel
MSG：消息（携带应用层服务）
ERR：错误
CLO：CloseSecureChannel
```

### OPC UA HTTPS

```text
HTTPS 443
XML / 二进制 / JSON 编码
SOAP 风格
```

### OPC UA WebSocket

```text
TCP 4840 + WebSocket 升级
二进制编码
适合实时
```

## 消息格式

### Hello (HEL)

```text
[H] [EL] [Length] [Version] [RecvBufferSize] [SendBufferSize] [MaxMessageSize] [MaxChunkCount] [EndpointUrl]
```

### Acknowledge (ACK)

```text
[A] [CK] [Length] [Version] [RecvBufferSize] [SendBufferSize] [MaxMessageSize] [MaxChunkCount]
```

### OpenSecureChannel (OPN)

```text
[O] [PN] [Length] [SecureChannelId] [SecurityPolicyUri] [SenderCertificate] [ReceiverCertificateThumbprint] [SequenceNumber] [RequestId] [ServiceRequest]
```

请求列表：

```text
OpenSecureChannelRequest
  ClientProtocolVersion
  RequestType: Issue / Renew
  SecurityMode: None / Sign / SignAndEncrypt
  ClientNonce
  RequestedLifetime
```

### Message (MSG)

```text
[M] [SG] [Length] [SecureChannelId] [TokenId] [SequenceNumber] [RequestId] [ServiceRequest]
```

### Error (ERR)

```text
[E] [RR] [Length] [SecureChannelId] [TokenId] [ErrorCode] [Reason]
```

### CloseSecureChannel (CLO)

```text
[C] [LO] [Length] [SecureChannelId] [TokenId]
```

## 编码

### 二进制编码

```text
Type ID（1-N 字节）
Length（1-N 字节）
Value（变长）

Tag 规则：
  0x00-0x1F：Application types
  0x20-0x3F：DataTypes
  0x40-0x5F：Server Diagnostics
  0x60-0x7F：Reserved
```

### XML / JSON 编码

文本格式，适合跨平台调试。

## 地址空间建模

### 节点类型

```text
Object：
  实体，例：MyDevice
  默认引用：HasComponent / HasProperty

Variable：
  变量，例：MyDevice.Temperature
  Value（值）
  DataType（类型）
  AccessLevel（读写权限）

Method：
  方法，例：MyDevice.Reset
  InputArguments + OutputArguments

ObjectType：
  对象类型，例：DeviceType
  描述对象的元数据

VariableType：
  变量类型，例：AnalogItemType

ReferenceType：
  引用类型，例：HasComponent
  Symmetric（双向）

DataType：
  数据类型，例：Double / String

View：
  视图，限制浏览
```

### 标准地址空间结构

```text
Root
  └─ Objects (i=85)
      └─ Server (i=2253)
          ├─ ServerArray
          ├─ NamespaceArray
          └─ ...
      └─ Device (用户定义)
          ├─ Variable: Temperature
          ├─ Variable: Pressure
          ├─ Method: Reset
          └─ Method: Calibrate
  └─ Types (i=86)
      └─ ObjectTypes
          └─ DeviceType
      └─ VariableTypes
          └─ AnalogItemType
      └─ ReferenceTypes
          └─ HasComponent
  └─ Views (i=87)
```

### 节点 ID 完整说明

```text
NodeId = NamespaceIndex:Identifier

Namespace：
  0：内置
  1：服务器默认
  2..N：自定义

Identifier：
  Numeric（数字）
  String（字符串）
  Guid（GUID）
  ByteString（字节串）

编码：
  FourByteNodeId：标识符 0（ns 0..255, id 0..255）
  NumericNodeId：标识符 0（ns 0..65535, id uint32）
  StringNodeId：标识符 1（ns 0..65535, string）
  GuidNodeId：标识符 2（ns 0..65535, GUID 16 字节）
  ByteStringNodeId：标识符 3（ns 0..65535, byte[]）
```

## 服务详解

### CreateSession

```text
Request:
  ClientDescription:
    ApplicationUri
    ProductUri
    ApplicationName
    ApplicationType
    GatewayServerUri
    DiscoveryProfileUri
    DiscoveryUrls
  ServerUri
    EndpointUrl
  SessionName
  ClientNonce
  ClientCertificate
  RequestedSessionTimeout
  MaxResponseMessageSize
```

Response:

```text
  SessionId
  AuthenticationToken
  RevisedSessionTimeout
  ServerNonce
  ServerCertificate
  ServerEndpoints (可选)
  ServerSoftwareCertificates
```

### ActivateSession

```text
Request:
  ClientSignature
    Algorithm
    Signature
  ClientSoftwareCertificates
  LocaleIds
  UserIdentityToken
    AnonymousIdentityToken / UsernameIdentityToken / X509IdentityToken
  UserTokenSignature
```

### Browse

```text
Request:
  ViewDescription
  RequestedMaxReferencesPerNode
  NodesToBrowse
    NodeId
    BrowseDirection (Forward / Backward / Both)
    ReferenceTypeId
    IncludeSubtypes
    NodeClassMask
    ResultMask
```

Response:

```text
  Results
    StatusCode
    ContinuationPoint
    References
      ReferenceTypeId
      IsForward
      TargetNodeId
      TargetNodeClass
      BrowseName
      DisplayName
      TypeDefinition
```

### Read

```text
Request:
  MaxAge
  TimestampsToReturn
  NodesToRead
    NodeId
    AttributeId
    IndexRange
    DataEncoding
```

Response:

```text
  Results
    StatusCode
    Value (Variant)
    ServerTimestamp
    SourceTimestamp
    ServerPicoseconds
    SourcePicoseconds
```

### Write

```text
Request:
  NodesToWrite
    NodeId
    AttributeId
    IndexRange
    Value
```

Response:

```text
  Results
    StatusCode
```

### Call

```text
Request:
  MethodsToCall
    ObjectId
    MethodId
    InputArguments
```

Response:

```text
  Results
    StatusCode
    OutputArguments
    InputArgumentResults
```

### CreateSubscription

```text
Request:
  RequestedPublishingInterval
  RequestedLifetimeCount
  RequestedMaxKeepAliveCount
  MaxNotificationsPerPublish
  PublishingEnabled
  Priority
```

Response:

```text
  SubscriptionId
  RevisedPublishingInterval
  RevisedLifetimeCount
  RevisedMaxKeepAliveCount
```

### AddMonitoredItems

```text
Request:
  SubscriptionId
  ItemsToCreate
    ItemToCreate
      ItemToMonitor
        NodeId
        AttributeId
        IndexRange
        DataEncoding
      MonitoringMode (Disabled / Sampling / Reporting)
      SamplingInterval
      Filter (DataChangeFilter / AggregateFilter)
      QueueSize
      DiscardOldest
```

Response:

```text
  Results
    MonitoredItemId
    StatusCode
    RevisedSamplingInterval
    RevisedQueueSize
```

### Publish

```text
Request:
  SubscriptionAcknowledgements
```

Response:

```text
  SubscriptionId
  AvailableSequenceNumbers
  MoreNotifications
  NotificationMessage
    SequenceNumber
    PublishTime
    Notification
      DataChangeNotification
        MonitoredItems
          ClientHandle
          MonitoredItemValue
            Value
            StatusCode
            ServerTimestamp
            SourceTimestamp
```

## 安全机制

### 安全策略

```text
None
Basic128Rsa15
Basic256
Basic256Sha256
Aes128Sha256RsaOaep
Aes256Sha256RsaPsa
```

### 消息安全

```text
None
Sign
SignAndEncrypt
```

### 加密算法

```text
HMAC-SHA1
HMAC-SHA256
AES-128-CBC
AES-256-CBC
RSA-OAEP
RSA-PSS
```

### 证书

```text
应用实例证书（X.509 v3）
服务器证书
客户端证书
CA 证书
```

工程实践：

- 生产环境必须使用证书。
- 自签名证书（测试）/ CA 签发证书（生产）。

### 用户认证

```text
AnonymousIdentityToken：
  PolicyId: "Anonymous"

UsernameIdentityToken：
  PolicyId: "Username_Basic256Sha256"
  UserName
  Password

X509IdentityToken：
  CertificateData
  PolicyId: "Certificate_X509"
```

## Companion Specifications

OPC UA 联盟定义行业信息模型：

```text
OPC UA for Machinery（机械）
OPC UA for Plastics (EUROMAP 77/82)
OPC UA for Machine Tools
OPC UA for Robotics
OPC UA for Process Automation
OPC UA for ISA-95
OPC UA for BACnet（与 BACnet 集成）
OPC UA for ADI（分析）
OPC UA for Field Level Communications
OPC UA for IIoT
```

每个 Companion Specification 定义：

```text
对象类型（ObjectType）
变量类型（VariableType）
引用类型（ReferenceType）
数据类型（DataType）
```

工程实践：

- 采用行业标准信息模型。
- 与客户具体业务匹配。

## 客户端实现要点

```text
1. OPC UA 客户端 SDK
3. 反向地址空间（Browse）
5. 安全策略配置
6. 会话管理
7. Read / Write 缓存
8. Subscribe / MonitoredItem 管理
9. Call 方法缓存
10. HistoryRead / HistoryUpdate
11. 服务端证书验证
12. 客户端证书
13. 重连机制
14. 反向 OPC UA Server
```

## 服务端实现要点

```text
1. OPC UA 服务器 SDK（open62541 / NodeOPCUA）
3. 地址空间构建
4. 服务器端点配置
5. 安全策略支持
6. 会话管理
7. Read / Write 实现
9. Call 方法实现
10. CreateSubscription 实现
11. MonitoredItem 检测
12. Publish 调度
13. HistoryRead 实现
14. 用户认证（Anonymous / Username / Certificate）
15. 服务器证书
16. Companion Specifications
```

## 抓包排障

Wireshark OPC UA dissector：

```text
1. TCP 4840
3. HEL / ACK / OPN / MSG / ERR / CLO 消息
5. 安全策略
7. 请求 / 响应服务
9. NodeId / 值
11. 订阅 / 通知
```

工程排障清单：

```text
1. TCP 端口未开
3. 安全策略不匹配
7. 证书无效
9. 用户认证失败
11. 地址空间节点不兼容
13. Read / Write 权限
15. 订阅不触发
17. Publish 不通
19. HistoryRead 失败
21. 方法调用失败
```

## 现场常见故障

| 现象 | 优先检查 |
| --- | --- |
| TCP 连接失败 | 端口 / 防火墙 |
| 安全策略协商失败 | 端点配置 |
| 会话创建失败 | 证书 / 认证 |
| 浏览失败 | 地址空间 |
| Read 失败 | NodeId / 权限 |
| Subscribe 不触发 | 监控项配置 |
| Publish 不通 | SubscriptionAck |
| HistoryRead 失败 | 节点历史支持 |

## 深度检查清单

- TCP 端口 4840 已开。
- HTTPS 端口 443 已开（如使用 HTTPS）。
- 安全策略协商。
- 会话创建。
- 用户认证（Anonymous / UsernamePassword / Certificate）。
- 地址空间浏览。
- Read / Write 支持。
- Call 方法调用支持。
- CreateSubscription 支持。
- MonitoredItems 支持。
- Publish 通知支持。
- HistoryRead 历史访问支持。
- 消息安全（Sign / SignAndEncrypt）。
- 客户端证书 / 服务器证书。
- Companion Specifications 实现。
- 信息建模（行业标准）。
- 重连机制。
- 反向 OPC UA Server（如支持）。
- 性能监控（MonitoredItems 数量 / Publish 频率）。