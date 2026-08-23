# ZigBee Deep Dive

## 目标

深入 ZigBee 协议栈各层：IEEE 802.15.4 PHY/MAC / NWK / APS / ZDO / ZCL。覆盖入网流程（Association / Rejoin / Orphan）、路由（树状 + 路由表 + 源路由）、安全（Trust Center / Link Key / Install Code）、ZigBee 3.0 / ZCL 标准化。目标读者：协议栈移植、产线深度故障定位、安全加固工程师。

## 协议栈分层

```text
┌─────────────────────────────────────────────────────┐
│ 应用层                                              │
│  ZigBee 3.0 / Home Automation / Light Link / 私有  │
├─────────────────────────────────────────────────────┤
│ ZCL    标准化 Cluster + Attribute + Command        │
│ ZDO    设备管理（入网 / 离开 / Bind / Descriptor）  │
├─────────────────────────────────────────────────────┤
│ APS    应用支持子层（Bind / Group / ACK / 安全）    │
├─────────────────────────────────────────────────────┤
│ NWK    网络层（路由 / 地址分配 / 入网）             │
├─────────────────────────────────────────────────────┤
│ MAC    IEEE 802.15.4（CSMA/CA / ACK / 信标）       │
├─────────────────────────────────────────────────────┤
│ PHY    IEEE 802.15.4（2.4GHz OQPSK, 250 kbps）     │
└─────────────────────────────────────────────────────┘
```

**两种实现形态**：

- **SoC**：协议栈 + 应用都在 MCU 跑（CC2652 + Z-Stack / EFR32MG + EmberZNet）
- **NCP**：协议栈在独立芯片，主机通过 EZSP / CPC 通信（EFR32 常用）

## IEEE 802.15.4 物理层

### 频段与信道

| 频段 | 频段范围 | 信道数 | 比特率 |
| --- | --- | --- | --- |
| 2.4 GHz | 2.400~2.4835 GHz | 16 | 250 kbps |
| 915 MHz | 902~928 MHz | 10 | 250 kbps |
| 868 MHz | 868~868.6 MHz | 1 | 250 kbps（欧洲） |

**2.4 GHz 信道**（最常用）：

```text
Channel 11: 2405 MHz
Channel 12: 2410 MHz
...
Channel 26: 2480 MHz
间隔 5 MHz
```

### 调制

```text
OQPSK（Offset Quadrature Phase Shift Keying）
  4 bit 符号 → 16-ary 准正交调制
  32-chip PN 序列 DSSS
  250 kbps PHY = 62.5 ksymbol/s
```

### 帧结构

```text
PHY Frame:
  ┌─────┬──────────────────────────┬──┐
  │Preamble│ SFD │ Length │ PSDU   │ FCS│
  │4 byte │1B │  1B   │ <=127B │2B │
  └─────┴──────────────────────────┴──┘
PSDU 即 MAC 帧
```

## IEEE 802.15.4 MAC

### 帧类型

```text
Beacon                     → 协调器广播（信标模式）
Data                       → 数据帧
ACK                        → 确认帧
MAC Command                → MAC 层命令
```

### 数据帧格式

```text
┌────┬─────┬──────┬────┬─────┬─────┬──────┬────┬─────┐
│ FC │Seq │DstPAN│Dst │SrcPAN│Src │Payload│FCS │
│2B │1B │  2B  │2B/8│ 2B  │2B/8│ <= 102B│ 2B│
└────┴─────┴──────┴────┴─────┴─────┴──────┴────┴─────┘
```

### CSMA/CA

```text
发送前先 Backoff:
  Backoff exponent (BE) 起始 3
  选 0 ~ 2^BE - 1 之间的随机数 R
  等待 R × aUnitBackoffPeriod (20 symbol = 320 µs)
  再次 CCA（Clear Channel Assessment）
  信道忙 → BE++, 重试
  BE > macMaxBE → 失败
```

### ACK

```text
数据帧 FC.Ack Request = 1
接收方 macAckWaitDuration (864 µs) 内 ACK
没收到 ACK → 重传，最多 aMaxFrameRetries (3) 次
```

### 信标使能模式（Beacon-enabled）

```text
Superframe 结构（ZigBee 较少用）：
  Beacon Interval  | Active Portion                | Inactive Portion
  BO/SO 配置       | CAP (CSMA/CA) + CFP (GTS)     | 节能

  CAP：Contention Access Period，普通设备用 CSMA/CA
  CFP：Contention-Free Period，Guaranteed Time Slot
```

**ZigBee 实务**：基本不用 Beacon-enabled 模式，靠 Beacons 做网络发现。End Device 唤醒后主动 Poll Parent。

## ZigBee 网络层（NWK）

### 设备类型

```text
Coordinator (FFD)
  - 启动 PAN，分配 16-bit NWK 地址
  - 唯一 1 个（0x0000）

Router (FFD)
  - 转发、路由
  - 永不上电睡眠
  - 允许新节点关联

End Device (RFD)
  - 不转发
  - 可睡眠
  - 仅与父节点（Router / Coordinator）通信
```

### 网络地址

```text
16-bit NWK 地址（短地址）：
  Coordinator: 0x0000
  Router / End Device: 父节点分配
  0xFFFC = 路由器广播（Router Broadcast）
  0xFFFD = 终端广播（End Device Broadcast）
  0xFFFE = 全节点广播
  0xFFFF = reserved

地址分配（树状路由算法）：
  Cskip(d) = (1 - Rm - h × Rm^(Lm - d)) / (1 - Rm)   (Rm != 1)
  父节点按 Cskip 公式把地址段分给子节点
```

### 入网流程

**Association（首次入网）**：

```text
1. End Device: Beacon Request
   Coordinator / Router: Beacon（带 PAN ID + 路由容量 + Permit Join）
2. End Device 选择父节点
3. End Device → 父节点: Association Request（Command Frame, 含 IEEE 地址）
4. 父节点 → Coordinator: 分配 16-bit NWK 地址
5. 父节点 → End Device: Association Response
6. End Device: Transport Key Request → Trust Center: Transport Key
7. Trust Center → End Device: APS Transport Key（含 Network Key）
8. End Device 入网完成
```

**Rejoin（已知网络，重连）**：

```text
1. End Device Beacon Request
2. 父节点 Beacon
3. End Device: Rejoin Request（含 16-bit NWK + IEEE + TC Address）
4. 父节点验证（TC + Trust Center）
5. 父节点: Rejoin Response（含新 Network Key）
6. End Device 用 Network Key 加密通讯
```

**Orphan（父节点丢失）**：

```text
1. End Device Poll → 父节点没响应
2. End Device: Orphan Notification（广播）
3. 父节点（如果存在）: Coordinator Realignment
4. End Device 重新加入
5. 如无父节点响应 → 走 Rejoin / Discovery
```

**实战关联**：

- Rejoin 失败 → End Device 反复 Orphan → 最终掉网
- ReJoinRequest 状态机 BUG（CC2530）→ 必须兜底 ZDO_MultipleJoinReq

### 路由

**树状路由（Tree Routing）**：

```text
按地址段推算下一跳：
  dst_addr vs 本节点地址
  Cskip 公式算层级
 优点：无路由表
 缺点：路径非最优
```

**路由表路由（Table Routing）**：

```text
Router 维护路由表：
  目标地址 → 下一跳 + 成本
 路由发现：Route Request → Route Reply
 路由记录：Route Record
```

**源路由（Source Route）**：

```text
源节点记录完整路径：
  源 → A → B → C → 目标
 应用：协调器向 End Device 发数据（不知道 End Device 当前父节点）
 路径由 End Device 父节点提供
```

**路由发现触发**：

```text
NWK 层发数据时无路由
 → Route Request（mesh 内广播）
 → 目标节点 / 中间节点发 Route Reply
 → 源节点记录路由
```

### 路由表维护

```text
NIB（Network Information Base）属性：
  nwkRouteTable（路由表）
  nwkRREQRetries（Route Request 重试次数）
  nwkRREPWaitTime（Route Reply 等待时间）
  nwkMaxHops（最大跳数，默认 30）
  nwkRouteDiscoveryTime（路由发现超时）
```

## ZigBee APS 层

### 数据帧

```text
APS Data Frame:
  ┌──────┬─────┬─────┬──────┬──────┬─────┬─────┐
  │FC(1B)│DstEP│ClusterID│ProfileID│Counter│Payload│
  └──────┴─────┴─────┴──────┴──────┴─────┴─────┘
```

### 寻址模式

```text
0x00 = 64-bit IEEE 地址
0x01 = Group 地址
0x02 = 16-bit NWK 地址（节点）
0x03 = 16-bit NWK + End Point
0x04 = Source Binding（按 Bind 表）
```

### Bind / Group

```text
Bind：
  源 Cluster (EP, ClusterID) → 目标 (地址, EP, ClusterID)
  写在源节点的 Bind Table
  触发后，源 Cluster 的命令自动发到所有 Bind 目标

Group：
  EP 加入 Group ID (0x0001 ~ 0xFFEF)
  Cluster 命令发到 Group ID 时，所有成员 EP 都收
```

**Bind vs Group 选型**：

| 场景 | 推荐 |
| --- | --- |
| 1 对多控制（场景模式） | Group |
| 跨厂商设备（同 Group） | Group |
| 复杂数据流（带确认） | Bind |
| 一对多持续同步 | Bind + Report |

### APS 安全

```text
APS Security:
  Link Key（128-bit）→ 节点对节点加密
  Network Key（128-bit）→ 网络广播加密
APS Frame Control.Security = 1 → 加密
```

## ZDO（ZigBee Device Object）

### ZDO Cluster（固定 0x0000 ~ 0x001F）

| Cluster | 用途 |
| --- | --- |
| 0x0000 Network Address Request | 查 IEEE → 16-bit NWK |
| 0x0001 IEEE Address Request | 查 16-bit NWK → IEEE |
| 0x0002 Node Descriptor Request | 节点能力（FFD/RFD） |
| 0x0003 Power Descriptor Request | 电源能力 |
| 0x0004 Simple Descriptor Request | EP / ProfileID / Cluster |
| 0x0005 Active Endpoints Request | 节点的 EP 列表 |
| 0x0006 Match Descriptor Request | 按 ProfileID + ClusterID 查 |
| 0x0006 Match Descriptor Response | 命中列表 |
| 0x0010 Device Announce | 入网后通知 |
| 0x0019 Mgmt_NWK_Disc_req | 邻居 PAN ID 扫描 |
| 0x0020 Mgmt_LQI_req | 邻居 LQI 表查询 |
| 0x0021 Mgmt_Rtg_req | 路由表查询 |
| 0x0022 Mgmt_Bind_req | Bind 表查询 |
| 0x0023 Mgmt_Leave_req | 强制设备离开 |
| 0x0014 Permit Join Request | 父节点允许入网 |
| 0x8017 Mgmt_NWK_Update_req | 改 Channel / Channel Mask |

## ZCL（ZigBee Cluster Library）

### 概念

```text
Cluster = 一组相关属性 + 命令
  Attribute: 状态/配置 (e.g. OnOff)
  Command: 动作 (e.g. On, Off, Toggle)
  Report: 属性变化主动上报

Endpoint 上有 1+ Cluster
  Endpoint 1 (Switch): [OnOff Cluster, Level Cluster]
  Endpoint 2 (Light):  [OnOff Cluster, Level Cluster, Color Cluster]
```

### ZCL 帧结构

```text
ZCL Header:
  Frame Control (1B) | Manuf Code (0/2B) | Transaction Seq | Command ID
Payload:
  Command Specific
```

### 标准 Cluster（部分）

| Cluster ID | 名称 | 属性 | 命令 |
| --- | --- | --- | --- |
| 0x0000 | Basic | ZCLVersion, ManufacturerName, ModelIdentifier | ResetToFactoryDefaults |
| 0x0003 | Identify | IdentifyTime | Identify, IdentifyQuery, IdentifyTriggerEffect |
| 0x0004 | Groups | NameSupport | AddGroup, ViewGroup, RemoveGroup, RemoveAllGroups |
| 0x0006 | On/Off | OnOff | On, Off, Toggle, OffWithEffect, OnWithRecallGlobalScene |
| 0x0008 | Level | CurrentLevel, MinLevel, MaxLevel | MoveToLevel, Move, Step, Stop |
| 0x0300 | Color Control | CurrentHue, CurrentSaturation, CurrentX/Y | MoveToHue, MoveToColor, StepColor |
| 0x0400 | Illuminance | MeasuredValue, Min/Max | — |
| 0x0402 | Temperature | MeasuredValue, Min/Max | — |
| 0x0406 | Occupancy | Occupancy | — |
| 0x0204 | Thermostat | LocalTemperature, OccupiedCoolingSetpoint | Setpoint Raise/Lower |
| 0x0201 | Thermostat UI | KeypadLockout | — |

### ZCL 报告机制

```text
服务端：
  配置 Reporting (AttributeId, MinInterval, MaxInterval, Change)
客户端：
  配置 Reporting Response
服务端：
  定时 (MaxInterval) 或 变化超过 Change → Report Attributes
客户端：
  Report Attributes → 处理
```

**实战**：

```c
// 报告配置（On/Off Cluster 状态变化上报）
configure_reporting_req_t cfg = {
    .direction = 0,  // Server -> Client
    .attribute_id = 0x0000,  // OnOff
    .data_type = ZCL_BOOLEAN,
    .min_interval = 0,        // 立即
    .max_interval = 30,       // 30s
    .reportable_change = NULL,  // Boolean 不需要
};
```

## 安全

### 密钥类型

```text
Trust Center Link Key（Default Well-Known）：
  5A 69 67 42 65 65 41 6C 6C 69 61 6E 63 65 30 39
  "ZigBeeAlliance09"（16 字节 ASCII）
  仅生产阶段用，量产前必须改

Network Key（128-bit）：
  整个网络共享
  节点入网时由 Trust Center 传输
  周期更新（Key Switch）

Application / APS Link Key（128-bit）：
  点对点（Bind / Report）
  Install Code 派生
```

### Trust Center 角色

```text
1. 验证入网请求
   - Trust Center Link Key 或 Install Code
   - 验证 IEEE 地址
2. 分配 Network Key
   - 加密传输（用 Trust Center Link Key）
3. 监控网络
   - 接收 Transport Key 命令
   - 处理 NWK Key Update
   - 强制 Leave（Mgmt_Leave_req）
```

### Install Code 派生 Link Key

```text
Install Code:
  16 字节 unique data + 2 字节 CRC16
  印在产品标签 / 工程文档
  Trust Center:
    HMAC_SHA_256(InstallCode + 0x5A6967426565416C6C69616E63653039)
    → 16 字节 Link Key
  设备入网时：
    用 Install Code 派生 Link Key
    验证 Trust Center
```

### Key Switch

```text
NWK Key Update:
  1. Trust Center 广播 NWK Key Update (新 Key)
  2. 节点收到 → 切换新 Key
  3. 旧 Key 仍可解密（限过期时间）
  4. 过期后只用新 Key

APS Encrypted APS Transport Key:
  1. Trust Center → 设备: APS Transport Key (新 NWK Key, 加密)
  2. 设备用 Trust Center Link Key 解密
  3. 切换
```

## ZigBee 3.0 vs 经典 ZigBee

| 维度 | ZigBee 3.0 | 经典 ZigBee（如 HA） |
| --- | --- | --- |
| 启动 | 0xFFFE（Coordinator 选） | 固定 PAN ID |
| 安全 | 强制 Install Code | Trust Center Link Key 可选 |
| Cluster | 统一 ZCL 库 | 各自 Profile |
| 互操作 | 跨厂商 | 同 Profile 厂商 |
| 入网 | Network Steering + Finding & Binding | 手动安装 |

**Network Steering 流程**：

```text
1. 设备扫描 Beacon → 找 0xFFFE 网络
2. 加入
3. Trust Center 验证
4. 设备主动找 Binding 目标（Finding & Binding）
5. 通过 Identify 触发，匹配后 Bind
```

## 厂商协议栈对比

| 维度 | Z-Stack (TI) | EmberZNet (Silicon Labs) | nRF Connect ZB (Nordic) | ZBOSS (ZBOSS / Espressif) |
| --- | --- | --- | --- | --- |
| 厂商 | TI | Silicon Labs | Nordic | DSR / Espressif |
| 协议 | ZigBee 3.0 | ZigBee 3.0 / Matter | Thread / Zigbee | ZigBee 3.0 |
| SoC | CC2652 / CC1352 | EFR32MG | nRF52840 | ESP32-H2 / C5 |
| NCP | 支持 | 支持（EZSP / CPC） | 不支持 | 计划 |
| 调试 | TI Packet Sniffer / Ubiqua | Ember Desktop | nRF Sniffer | 自研 |
| 文档 | 详尽 | 详尽（带 AN/UG/KBA） | 较新 | 中文 |
| 易上手 | 中 | 中 | 易 | 易 |

## SoC vs NCP 调试差异

| 维度 | SoC | NCP |
| --- | --- | --- |
| 协议栈调试 | 用厂商 IDE（Simplicity Studio / CCS） | 通过 EZSP / CPC 命令 |
| Crash 抓取 | IDE 内置 backtrace | NCP assert 通常只能断电重启，需 SWO 抓 |
| 内存占用 | 协议栈 + 应用共 RAM | 主机只跑应用，RAM 充足 |
| 实时性 | 协议栈中断与应用耦合 | 主机可独立优化 |
| 升级 | OTA 协议栈 + 应用双区 | 协议栈固化在模块，只升级主机 |

**EFR32 NCP 调试**：

- 留出 10-pin Simplicity Connector（至少 SWO/SWDIO/SWCLK/GND）
- 启用 ncp-debug-print 插件（依赖 emberMinimal + printf + serial）
- 崩启用看门狗：assert/CRS/SW 重启靠 SWO 抓 log

## 性能数据参考

```text
入网时间：
  Association: ~2-5 s（首次）
  Rejoin: ~1-2 s（已知网络）

最大吞吐：
  APS Data 帧 payload：~80 字节
  应用层吞吐：~30 kbps
  端到端延迟：~50-300 ms（单跳）
  Mesh 多跳延迟：~10-30 ms/跳

功耗（End Device）：
  睡眠：~1.5 µA
  唤醒 30ms：~8 mA
  Poll Interval 3s：平均 ~30 µA
  CR2032 撑 1 年
```

## 实战经验

- **ReJoinRequest 失败**：CC2530 NLME 状态机 BUG，Orphan 后需兜底 ZDO_MultipleJoinReq
- **NV 残留致误关联邻居网关**：flash PAN ID 限定回原网络
- **EFR32 NCP crash**：SWO 抓 log + emberMinimal/printf/serial 插件链
- **End Device 不睡眠**：Poll Control 错配 + Keepalive 漏配
- **多 Coordinator 冲突**：Channel Mask 没限 + 邻居 PAN 干扰
- **zigbee2mqtt 50+ 设备掉线**：USB 适配器固件 / MQTT 队列积压

## 关联文档

- `bus/zigbee.md` 主题入口
- `bus/zigbee-practical.md` 调试流程速查
- `bus/zigbee-failure-cases.md` 产线实战案例
- `bus/zigbee-index.md` 主题地图 + 导航
