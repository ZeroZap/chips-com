# Matter Deep Dive

## 目标

深入 Matter 协议栈各层：Application / Interaction Model / Data Model / Message Layer / Security / Transport (UDP/TCP) / Network (IPv6/Thread/Wi-Fi/Ethernet)。覆盖数据模型、Interaction Model、配网（PASE / CASE / NOC）、安全（Attestation / DAC / PAI / NOC / Access Control）、多 Fabric、Binding、Subscription、OTA。目标读者：协议栈移植、产线深度故障定位、Matter 认证准备工程师。

## 协议栈分层

```text
┌─────────────────────────────────────────────────────┐
│ Application Layer                                  │
│  应用 Profile（智能家居 / 智能灯 / 智能门锁）       │
├─────────────────────────────────────────────────────┤
│ Interaction Model (IM)                             │
│  Read / Write / Subscribe / Invoke / Report        │
├─────────────────────────────────────────────────────┤
│ Data Model                                         │
│  Node / Endpoint / Cluster / Attribute / Command   │
├─────────────────────────────────────────────────────┤
│ Message Layer                                      │
│  Reliable / Unreliable 消息                         │
├─────────────────────────────────────────────────────┤
│ Security                                           │
│  CASE / PASE / Group Cast / IPsec / TLS            │
├─────────────────────────────────────────────────────┤
│ Transport                                          │
│  UDP / TCP / DTLS / TLS 1.3                        │
├─────────────────────────────────────────────────────┤
│ Network                                            │
│  IPv6 / 6LoWPAN (Thread) / Wi-Fi / Ethernet         │
├─────────────────────────────────────────────────────┤
│ Physical                                           │
│  802.15.4 (Thread) / 802.11 (Wi-Fi) / 802.3 (ETH)  │
└─────────────────────────────────────────────────────┘
```

**端口**：

- UDP 5540：Matter 通用（commissioning + operational）
- UDP 5550：commissioning 备用
- TCP 5540：ble-wifi 切换

## 数据模型

### Node

```text
Node:
  - 1 个 Fabric
  - 1+ Endpoint
  - Node ID (64-bit, 派生自 Fabric ID)
  - Vendor ID
  - Product ID
  - DAC（Device Attestation Certificate）
  - PAI（Product Attestation Intermediate）
  - CD（Certification Declaration）
  - NOC（Node Operational Certificate）
```

### Endpoint

```text
Endpoint:
  - 编号 0 ~ 0xFFFE
  - 0x0000 = Network Commissioning（Root Node 必备）
  - 0x0001 ~ 0xFFFE = 应用功能端点
  - 0xFFFF = reserved
  - 1 个 Device Type
  - 1+ Cluster
  - 数量限制：255（实务上 20 以下）
```

### Cluster

```text
Cluster:
  - 32-bit Cluster ID
  - 0x0000 ~ 0x001F = ZDO 风格（Fixed Clusters）
  - 0x0006 = On/Off
  - 0x0008 = Level
  - 0x001D = Descriptor
  - 0x001E = Binding
  - 0x001F = Access Control
  - 0x0200 ~ 0x02FF = 测量 / 传感器
  - 0x0300 ~ 0x03FF = 照明
  - 0x0400 ~ 0x04FF = HVAC
  - 0xFC00 ~ 0xFFFE = Vendor Specific
  - 1+ Attribute
  - 0+ Command
  - 0+ Event
```

### Attribute

```text
Attribute:
  - 16-bit 或 32-bit ID
  - 类型（DataType）：bool / uint8 / int8 / uint16 / ...
  - 访问：R / W / RW / Read-only / Write-only
  - Quality 标志：nullable / non-volatile / ...
  - 范围：min / max
```

**Matter 复用 ZigBee Cluster Library 的数据类型**：

| 类型 | 字节 | 范围 |
| --- | --- | --- |
| boolean | 1 | true / false |
| uint8 | 1 | 0 ~ 255 |
| uint16 | 2 | 0 ~ 65535 |
| uint32 | 4 | 0 ~ 2^32-1 |
| int8 | 1 | -128 ~ 127 |
| int16 | 2 | -2^15 ~ 2^15-1 |
| int32 | 4 | -2^31 ~ 2^31-1 |
| float | 4 | IEEE 754 |
| octet string | N | 字节数组 |
| char string | N | UTF-8 字符串 |
| enum | 1/2/4 | 枚举值 |

### Command

```text
Command:
  - 8-bit Command ID（Cluster 范围内）
  - 0x00 = 保留
  - 0x01 ~ 0xFE = 标准命令
  - 0xFF = 厂商特定
  - 0x00 = 响应（Response）
  - 0x01 = Custom Response
```

### Event

```text
Event:
  - 8-bit Event ID
  - 优先级：Critical / Error / Info / Debug
  - 状态：保留 / 上报 / 已处理
  - 事件数据：octet string

Event Cluster:
  - 通用：StartUp / Shutdown / Reachable / State Change
```

## Interaction Model (IM)

### 5 种 Action

```text
1. Read (Subscribe Read)
   - 读 Attribute / Event
   - Client → Server

2. Write
   - 写 Attribute
   - Client → Server

3. Subscribe
   - 订阅 Attribute / Event
   - 订阅参数：MinIntervalFloor / MaxIntervalCeiling
   - Server 主动发 Report

4. Invoke
   - 调 Command
   - Client → Server
   - Response / Status Report

5. Report
   - Server 主动上报
   - 触发：Attribute 变化 / 定时 / Event
```

### IM 消息

```text
Read Request/Response
Write Request/Response
Subscribe Request/Response
Invoke Command Request/Response
Report Data
Status Response
Timed Request（限时命令）
```

### Interaction Mode

```text
Timed Interaction：限时（默认 10s）
非 Timed：立即
非阻塞：异步
```

## 配网（Commissioning）

### 完整流程

```text
Step 1: Commissionable Discovery
  - 设备 BLE 广播 0xFEAF Service Data
  - 包含 Discriminator + Vendor ID + Product ID

Step 2: CommissioningWindow 开启
  - 设备等待配网（默认 15 分钟）

Step 3: PASE 握手
  - SPAKE2+ 协议
  - 基于 Setup Passcode
  - 加密通道建立

Step 4: Attestation
  - 设备发 DAC（Device Attestation Certificate）
  - Commissioner 验证证书链（PAI → PAA）
  - 验证 CD（Certification Declaration）

Step 5: Commissioning Flows
  - Network Commissioning
    - Wi-Fi: SSID + 密码
    - Thread: Network Master Key + PAN ID + Channel
  - Operational Discovery
  - Time Sync

Step 6: CSR + NOC 签发
  - 设备生成 CSR（Key Pair + Subject）
  - Commissioner 用 Fabric CA 签发 NOC
  - NOC + ICAC 写入设备

Step 7: CASE 握手
  - 设备 + Commissioner 用 NOC 互相验证
  - 建立 CASE session

Step 8: ACL 配置
  - 设备接受 fabric 内的节点
  - Access Control List

Step 9: 加 fabric
  - 设备进入 Operational 状态
  - 接受 fabric 内其他节点的 IM 操作
```

### PASE（Password-Authenticated Session Establishment）

```text
基于 SPAKE2+ 协议
  - Passcode (4 字节)
  - Discriminator (12 bits)

SPAKE2+ 流程：
  1. 双方共享 Passcode
  2. 双方生成临时密钥
  3. 互相验证临时密钥
  4. 派生 shared secret
  5. 建立加密 session

优势：
  - 防中间人（MITM）
  - 防离线暴力破解（Passcode 强）
  - 无需证书
```

### CASE（Certificate Authenticated Session Establishment）

```text
基于 sigma 协议（IKEv2-like）
  - 双方用 NOC 互相验证
  - 派生 shared secret
  - 建立加密 session

CASE 流程：
  1. 双方交换 NOC
  2. 验证证书链（NOC → ICAC → Fabric Root）
  3. 双方生成临时密钥
  4. Diffie-Hellman 密钥交换
  5. 派生 shared secret
  6. 建立 CASE session

Session Key:
  - 用于 IM 消息加密
  - 8 小时生命周期（可更新）
  - 256-bit AES-CCM
```

## 安全模型

### 证书链

```text
PAA (Product Attestation Authority)  ← CSA 根证书
  └─ PAI (Product Attestation Intermediate)  ← 厂商产品级
        └─ DAC (Device Attestation Certificate)  ← 单设备
              └─ NOC (Node Operational Certificate)  ← Fabric 内
                    └─ ICAC (Intermediate Certificate, 可选)
```

**证书字段**：

```text
PAA / PAI / DAC：用于 Attestation，证明设备真伪
NOC / ICAC：用于 CASE，证明设备在合法 fabric 内
```

### Attestation

```text
Attestation 流程：
  1. 设备发 DAC + PAI（链上发）
  2. Commissioner 验证证书链
    - DAC 签 PAI 签 PAA（锚定 CSA 根）
  3. 验证 CD（Certification Declaration）
    - 包含 VID / PID / Certification ID
  4. 验证设备 NOC
    - 设备唯一
    - Fabric 内

PAA 来源：
  - DCL (Distributed Compliance Ledger) 公开
  - 厂商在 CSA 申请 PAI
  - 工厂批量签发 DAC
```

### Access Control（ACL）

```text
ACL Entry:
  - Fabric Index
  - Privilege: View / Operate / Manage / Admin
  - Auth Mode: PASE / CASE / Group
  - Subjects: Node ID / Group ID / All

Privileges:
  View (1): 读
  Operate (2): 写 / 调
  Manage (3): 加 / 删 ACL
  Admin (4): fabric 级别管理
```

## Matter over Thread / Wi-Fi / Ethernet

| 维度 | Thread | Wi-Fi | Ethernet |
| --- | --- | --- | --- |
| 物理层 | 802.15.4 | 802.11 | 802.3 |
| IPv6 适配 | 6LoWPAN | Native | Native |
| Mesh | Yes | No | No |
| 路由 | RPL | Wi-Fi Mesh (extender) | 静态 |
| Border Router | 必 | 不需 | 不需 |
| 带宽 | 250 kbps | 11+ Mbps | 100+ Mbps |
| 功耗 | 低 | 中 | 高 |
| 适合 | 电池设备 | 供电设备 | 固定设备 |
| Border Router | EFR32 / nRF / ESP | N/A | N/A |

**Matter over Thread 部署结构**：

```text
Thread Border Router (TBR) ←→ Wi-Fi / Ethernet
       │
       ├── Thread Node 1 (Sensor)
       ├── Thread Node 2 (Light)
       ├── Thread Node 3 (Lock)
       └── Thread Sleepy End Device (Button)

Matter 控制器（手机 / Hub）通过 TBR 访问 Thread 设备
```

## Cluster Library

### 沿用 ZigBee Cluster Library

Matter 沿用 ZigBee Cluster Library 的 Cluster 定义，**ZCL 1.0 → Matter 1.0 → Matter 1.4** 一脉相承。

**已变化**：

- Cluster ID 重新定义（部分变化）
- Attribute 数据类型扩展
- Command ID 重新编号
- 新增 Cluster: Window Covering / Door Lock / Electrical Measurement / ...

**重要 Cluster**：

| Cluster | ID | 主要 Attribute | 主要 Command |
| --- | --- | --- | --- |
| On/Off | 0x0006 | OnOff | On, Off, Toggle |
| Level | 0x0008 | CurrentLevel | MoveToLevel, Move, Step |
| Color | 0x0300 | CurrentX, CurrentY, CurrentHue, CurrentSaturation | MoveToColor, MoveToHue, StepColor |
| Thermostat | 0x0201 | LocalTemperature, OccupiedHeatingSetpoint | SetpointRaiseLower |
| Window Covering | 0x0102 | CurrentPositionLiftPercent100 | UpOrOpen, DownOrClose, StopMotion |
| Door Lock | 0x0101 | LockState, LockType | LockDoor, UnlockDoor |

## 多 Fabric / 多 Admin

### Multi-Fabric

```text
Matter 设备支持同时加入多个 Fabric：
  - Fabric 1: Apple Home
  - Fabric 2: Google Home
  - Fabric 3: Amazon Alexa
  - Fabric 4: 米家

每个 Fabric:
  - 独立 NOC
  - 独立 Fabric ID
  - 独立 Admin Node
  - 独立 ACL

实务：
  - 设备保存 1+ Fabric 状态
  - KVS / NVM 需独立分区
  - 推荐 5+ Fabric 支持
```

### Multi-Admin

```text
Multi-Admin 流程：
  1. 设备在 Fabric 1 (Apple Home)
  2. 设备在 Fabric 2 (Google Home)
  3. Fabric 1 Admin 通知 Fabric 2 Admin
     - 用 Commissioning Discovery 找 Fabric 2
     - 设备重新走 Commissioning Flow
  4. 设备同时在两个 Fabric

简化版：
  - Apple Home → Google Home 一键迁移（用户授权）
```

## Subscription / Binding

### Subscription

```text
Client 订阅 Server 的 Attribute：
  SubscribeRequest:
    - AttributePath
    - MinIntervalFloor (ms)
    - MaxIntervalCeiling (ms)

Server 响应：
  - SubscribeResponse
  - 初始 ReportData

Server 定时 / 变化时：
  - ReportData (含 Attribute)

Cancel:
  - 客户端断开 → 自动取消
```

### Binding

```text
Binding 跨设备 Cluster 关联：
  - 开关 (EP 1 On/Off Cluster) → 灯 (EP 1 On/Off Cluster)
  - 按钮按 → 灯开关

Binding 存储：
  - 本地绑定（开关端）
  - 全局绑定（fabric 共享）

创建：
  - 由 Admin Node 写 Binding Cluster
  - 或通过 Subscription / Group 间接实现
```

## OTA 升级

```text
OTA 升级流程：
  1. OTA Provider 准备镜像
  2. OTA Requestor（设备）通过 fabric 找 OTA Provider
  3. Provider 发送镜像（分片）
  4. Requestor 校验签名（CSA 签名）
  5. 校验通过 → 应用镜像
  6. 重启

OTA Cluster (0x001A):
  - OTA Provider Attribute
  - ImageNotify
  - QueryImage
  - ApplyUpdate
  - UpdateCompleted

安全：
  - 镜像签名（CSA Root + 厂商 Intermediate）
  - 设备必须验证签名
  - 防回滚保护
```

## Matter 设备类型（Device Type Library）

| Device Type | ID | Cluster 强制 | 备注 |
| --- | --- | --- | --- |
| On/Off Light | 0x0001 | On/Off | 基础灯 |
| Dimmable Light | 0x0101 | On/Off + Level | 调光灯 |
| Color Dimmable Light | 0x0100 | On/Off + Level + Color Control | 调色灯 |
| On/Off Light Switch | 0x0103 | Identify + On/Off (client) | 开关 |
| On/Off Plug-in Unit | 0x010A | On/Off | 智能插座 |
| Thermostat | 0x0301 | Thermostat + Thermostat UI | 恒温器 |
| Temperature Sensor | 0x0302 | Temperature Measurement | 温度传感器 |
| Humidity Sensor | 0x0307 | Humidity Measurement | 湿度传感器 |
| Occupancy Sensor | 0x0107 | Occupancy Sensing | 占用传感器 |
| Door Lock | 0x000A | Door Lock | 智能门锁 |
| Window Covering | 0x0202 | Window Covering | 窗帘 |
| Generic Switch | 0x000F | Identify + Switch | 通用开关 |
| Speaker | 0x0022 | Audio + Speaker | 智能音箱 |
| Video Player | 0x0023 | Content Launcher | 视频播放 |

**强制 Cluster 检查**：

```text
认证测试时 CSA Test Harness 检查：
  1. Device Type 注册的 Cluster 是否全部实现
  2. Mandatory Attribute 是否实现
  3. Mandatory Command 是否实现
  4. Attribute 顺序（按 Device Type Library 顺序）
  5. DataModelRevision 是否最新
```

## Commissionable Discovery 抓包

```text
nRF Connect / LightBlue 扫描：
  - Service 0xFEAF
  - Service Data:
    - Length (1B)
    - Vendor ID (2B, LE)
    - Product ID (2B, LE)
    - Discriminator (2B, LE 12 bits)
    - DiscriminatorBit (1 bit)
    - Version (4 bits)
    - Additional Data (1B)

如没看到：
  - 设备没启 Commissionable Mode
  - 长按重置键未生效
  - BLE 广播没启
```

## 性能数据

```text
Commissioning 时间：
  PASE: ~500 ms
  Attestation: ~200 ms
  CASE: ~500 ms
  NOC 写入: ~100 ms
  总: ~2-3 s

Read Attribute 延迟:
  Wi-Fi: ~30-50 ms
  Thread: ~100-200 ms (1 跳)
  Thread 多跳: ~300-500 ms

Invoke Command 延迟:
  同 Read，但 +50ms

Report 周期:
  默认 MinIntervalFloor: 0 ms
  默认 MaxIntervalCeiling: 60 s
  实际: 属性变化 1s 内上报
```

## 实战经验

- **CommissioningWindow 超时**：默认 15 分钟，用户扫码慢就过期。改用更长窗口（1 小时）
- **多 Fabric 持久化失败**：KVS 没分独立区，fabric 互相覆盖
- **跨生态不通用 Attribute**：iOS 读 / Android 写的差异（CASE 流程一）
- **认证测试 Cluster 顺序**：必须按 Matter Device Library 顺序
- **OTA 镜像签名**：必须用厂商私钥签，设备用厂商公钥验
- **Thread Border Router 切换**：不同生态（Apple/Google）共用 TBR
- **Wi-Fi 切换 fabric 掉线**：Wi-Fi 切换触发 IP 变更，fabric 路由表失效

## 关联文档

- `bus/matter.md` 主题入口
- `bus/matter-practical.md` 调试流程速查
- `bus/matter-failure-cases.md` 产线实战案例
- `bus/matter-index.md` 主题地图 + 导航
- `bus/thread-*.md` Matter over Thread
- `bus/ble-deep-dive.md` BLE 配网通道
- `bus/zigbee-*.md` Cluster 沿用参考
