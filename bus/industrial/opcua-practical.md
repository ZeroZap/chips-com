---
tags:
  - layer/bus
  - type/practical
  - protocol/opcua
  - topic/industrial
---

# OPC UA Practical Guide

## 目标

本文用于把 OPC UA 工程链路调通：服务端点发现、会话创建、地址空间浏览、读写、调用方法、订阅和历史访问。

## TCP 接入

```text
Client → TCP:4840 → Server（OPC UA TCP 二进制）
Client → HTTPS:443 → Server（OPC UA HTTPS）
```

## 端点发现

```text
1. Client 连接 Server:4840
3. Client 发 OpenSecureChannelRequest
5. Client 发 GetEndpoints
7. Server 返回端点列表（每个端点一种安全策略 + 加密模式）
9. Client 选择合适的端点
11. Client 创建 SecureChannel
```

## 会话创建

```text
1. Client 发 CreateSessionRequest
3. Server 返回 SessionId + ServerCertificate + Endpoints
5. Client 发 ActivateSessionRequest
7. Server 返回激活结果
9. 进入业务交互
```

实际流程：

```text
OpenSecureChannel → CreateSession → ActivateSession → Browse → Read / Write → CloseSession
```

## 地址空间浏览

Client → Server (BrowseRequest):

```text
Request:
  ViewDescription: (ViewId null = 全地址空间)
  RequestedMaxReferencesPerNode: 100
  NodesToBrowse:
    NodeId: ObjectsFolder (ns=0;i=85)
    BrowseDirection: Forward
    ReferenceTypeId: HierarchicalReferences
    IncludeSubtypes: true
    NodeClassMask: 0
    ResultMask: BrowseName | DisplayName | NodeId
```

Server → Client (BrowseResponse):

```text
Results:
  StatusCode: Good
  ContinuationPoint: null (无后续)
  References:
    ReferenceTypeId: HasChild
    IsForward: true
    TargetNode: ns=0;i=2253 (Server)
    BrowseName: Server
    DisplayName: Server
    NodeClass: Object
```

工程实现：

```text
1. BrowseObjectsFolder
3. BrowseServer.GetChild()
5. BrowseVendor.GetChild()
9. BrowseDevice.GetChild()
```

## 读取节点值

Client → Server (ReadRequest):

```text
Request:
  MaxAge: 0
  TimestampsToReturn: Both
  NodesToRead:
    NodeId: ns=1;s=Device1.Temperature
    AttributeId: Value
    IndexRange: null
    DataEncoding: null
```

Server → Client:

```text
Response:
  Results:
    StatusCode: Good
    Value:
      Type: Double
      Body: 23.5
    ServerTimestamp: ...
    SourceTimestamp: ...
    ServerPicoseconds: 0
    SourcePicoseconds: 0
```

## 写入节点值

Client → Server (WriteRequest):

```text
Request:
  NodesToWrite:
    NodeId: ns=1;s=Device1.SetPoint
    AttributeId: Value
    Value:
      Type: Double
      Body: 75.0
```

Server → Client:

```text
Response:
  Results:
    StatusCode: Good
```

## 方法调用

Client → Server (CallRequest):

```text
Request:
  MethodsToCall:
    ObjectId: ns=1;s=Device1
    MethodId: ns=1;s=Device1.Reset
    InputArguments:
      - Type: Boolean
        Body: true
```

Server → Client:

```text
Response:
  Results:
    StatusCode: Good
    OutputArguments:
      - Type: UInt32
        Body: 0 (success)
    InputArgumentResults: ...
```

## 订阅 + 通知

Client → Server (CreateSubscriptionRequest):

```text
  RequestedPublishingInterval: 1000
  RequestedLifetimeCount: 60
  RequestedMaxKeepAliveCount: 10
  MaxNotificationsPerPublish: 100
  PublishingEnabled: true
  Priority: 0
```

Server → Client:

```text
  SubscriptionId: 1
  RevisedPublishingInterval: 1000
  RevisedLifetimeCount: 60
  RevisedMaxKeepAliveCount: 10
```

### 添加 MonitoredItem

Client → Server (AddMonitoredItemsRequest):

```text
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

### Publish 通知

Server → Client (Publish):

```text
  SubscriptionId: 1
  SequenceNumber
  PublishTime
  NotificationMessage:
    DataChangeNotification:
      MonitoredItems:
        MonitoredItemId: 100
        Value:
          Double = 23.7
        StatusCode: Good
        ServerTimestamp
        SourceTimestamp
```

Client → Server (Publish 后 Acknowledge):

```text
SubscriptionAcknowledgements:
  SubscriptionId: 1
  SequenceNumber
```

## 历史访问

Client → Server (HistoryReadRequest):

```text
  HistoryReadDetails:
    HistoryReadType: ReadRawModifiedDetails
    StartTime: 2026-09-01T00:00:00Z
    EndTime: 2026-09-18T00:00:00Z
    NumValuesPerNode: 100
    ReturnBounds: false
  NodesToRead:
    NodeId: ns=1;s=Device1.Temperature
```

Server → Client:

```text
  Results:
    HistoryData:
      DataValues:
        - Value: 23.5
          ServerTimestamp: 2026-09-01T00:00:00Z
          StatusCode: Good
```

## 安全配置

### 安全策略

```text
None：测试环境
Basic128Rsa15：RSA 15（不推荐）
Basic256：SHA-1（基本）
Basic256Sha256：SHA-256（推荐）
Aes128Sha256RsaOaep
Aes256Sha256RsaPsa
```

### 消息安全模式

```text
None（明文）
Sign（仅签名）
SignAndEncrypt（签名 + 加密）
```

工程实践：

- 生产环境：Basic256Sha256 + SignAndEncrypt。
- 用户认证：UserNamePassword 或 Certificate。

### 用户认证

```text
Anonymous（无认证）
UserNamePassword（用户名密码）
Certificate（X.509 证书）
```

## 客户端调试步骤

1. TCP 连接 Server:4840。
2. OpenSecureChannel。
3. GetEndpoints → 获取安全策略。
4. CreateSession。
5. ActivateSession（用户名密码 / 证书）。
6. Browse Server。
7. Read 节点值。
8. CreateSubscription。
9. AddMonitoredItems。
10. 接收 Publish。
11. Call 方法（可选）。
12. HistoryRead（可选）。
13. CloseSession。

## 服务端调试步骤

1. 监听 TCP:4840。
2. 处理 OpenSecureChannel。
3. 处理 CreateSession。
4. 处理 ActivateSession（认证）。
5. 提供地址空间（Server / ObjectsFolder / ...）。
6. 处理 Read / Write。
7. 处理 Call。
8. 处理 CreateSubscription。
9. 处理 AddMonitoredItems。
10. 检测数据变化 → 发 Publish。
11. 处理 HistoryRead。

## 调试工具

- Wireshark：OPC UA dissector。
- OPC UA 客户端：UA Expert（Unified Automation）、FreeOpcUa。
- OPC UA 服务器：open62541、NodeOPCUA、FreeOpcUa Server。
- 信息建模：Siemens NX / 行业工具。

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| TCP 连接失败 | 端口 / 防火墙 |
| 安全策略协商失败 | Endpoint 配置 |
| 会话创建失败 | 证书 / 认证 |
| 浏览失败 | 地址空间 |
| Read 失败 | NodeId / 权限 |
| Subscribe 不触发 | 监控项配置 |
| Publish 不通 | SubscriptionAck |

## 实战检查清单

- TCP 端口 4840 已开。
- 安全策略协商。
- 会话创建。
- 用户认证。
- 地址空间浏览。
- Read / Write 支持。
- Call 方法调用支持。
- CreateSubscription 支持。
- MonitoredItems 支持。
- Publish 通知支持。
- HistoryRead 历史访问支持。
- 消息安全（Sign / SignAndEncrypt）。
- Companion Specifications 实现。