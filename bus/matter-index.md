# Matter 主题总览

## 目标

Matter 是 chips-com 的核心无线协议主题之一，围绕"智能家居 / IoT 应用层互操作标准"已经形成 5 篇专题笔记。本文档是**总览导航**，帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/matter-*.md
│
├── 速查层
│   └── matter-practical.md              配网 / 5 秒定位 / 错误码表
│
├── 原理层
│   └── matter-deep-dive.md              数据模型 / IM / 配网 / 安全深挖
│
├── 实战层
│   └── matter-failure-cases.md          8 个产线实战案例
│
└── 导航
    └── matter-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 Matter, 想入门" (新人)

按顺序读, 1-2 天能上手:

1. **`matter.md`** — 主题入口, 5 分钟
2. **`matter-practical.md`** — 配网流程 / 关键参数
3. **`matter-deep-dive.md`** — 数据模型 / Interaction Model

### 路径 B: "我在做 Matter 设备产线失败" (现场救火)

1. **`matter-practical.md`** "## 5 秒钟定位"
2. **`matter-failure-cases.md`** — 找类似案例（8 个）
3. **`matter-deep-dive.md`** "## 错误码速查"

### 路径 C: "我在做 Matter 协议栈移植" (工程师)

1. **`matter-deep-dive.md`** "## 协议栈分层"
2. **`matter-practical.md`** "## chip-tool 常用命令"
3. **`matter-failure-cases.md`** 案例 1 / 2（配网 / CASE）

### 路径 D: "我在做 Matter 安全加固" (安全工程师)

1. **`matter-deep-dive.md`** "## 安全模型"
2. **`matter-deep-dive.md`** "## 证书链"
3. **`matter-failure-cases.md`** 案例 5（OTA 签名）

### 路径 E: "我在做 Matter 选型" (架构师)

1. **`matter.md`** "## 典型芯片"
2. **`matter-deep-dive.md`** "## Matter over Thread / Wi-Fi / Ethernet"
3. **`matter-practical.md`** "## 性能数据"

### 路径 F: "我在准备 Matter 认证" (CSA 认证工程师)

1. **`matter-failure-cases.md`** 案例 7（Cluster 顺序）
2. **`matter-deep-dive.md`** "## Matter 设备类型（Device Type Library）"
3. **`matter-practical.md`** "## Matter 认证测试"

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 配网流程 | matter-practical.md "## 配网流程" |
| Setup Payload 怎么生成 | matter-practical.md "## Setup Payload" |
| BLE 0xFEAF 抓包 | matter-practical.md "## Commissionable Discovery 抓包" |
| 5 秒定位 | matter-practical.md "## 5 秒钟定位" |
| 数据模型 | matter-deep-dive.md "## 数据模型" |
| Interaction Model | matter-deep-dive.md "## Interaction Model" |
| PASE 协议 | matter-deep-dive.md "## PASE" |
| CASE 协议 | matter-deep-dive.md "## CASE" |
| Attestation | matter-deep-dive.md "## Attestation" |
| ACL | matter-deep-dive.md "## Access Control" |
| 跨 Fabric | matter-deep-dive.md "## 多 Fabric" |
| Binding | matter-deep-dive.md "## Subscription / Binding" |
| OTA 升级 | matter-deep-dive.md "## OTA 升级" |
| Matter over Thread | matter-deep-dive.md "## Matter over Thread / Wi-Fi / Ethernet" |
| Device Type | matter-deep-dive.md "## Matter 设备类型" |
| Cluster 顺序 | matter-failure-cases.md 案例 7 |
| 跨生态测试 | matter-practical.md "## 跨生态测试" |
| IM 错误码 | matter-practical.md "## Matter IM 错误" |
| 性能数据 | matter-practical.md "## 性能数据" |

## 关键概念地图

```text
Matter 协议栈
├── 应用层
│   ├── 智能家居 / 智能灯 / 智能门锁 / ...
│   └── 厂商特定应用
│
├── Interaction Model
│   ├── Read / Write / Subscribe / Invoke / Report
│   ├── Timed Interaction
│   └── Status Response
│
├── Data Model
│   ├── Node（节点）
│   ├── Endpoint（端点 0x0001 ~ 0xFFFE）
│   ├── Cluster（簇）
│   │   ├── Attribute（属性）
│   │   ├── Command（命令）
│   │   └── Event（事件）
│   └── Device Type
│
├── 配网 (Commissioning)
│   ├── Commissionable Discovery
│   ├── CommissioningWindow
│   ├── PASE（SPAKE2+）
│   ├── Attestation（DAC / PAI / PAA / CD）
│   ├── Operational Discovery
│   ├── CSR / NOC
│   ├── CASE（sigma 协议）
│   └── ACL 配置
│
├── 安全
│   ├── 证书链（PAA → PAI → DAC → NOC → ICAC）
│   ├── Attestation 流程
│   ├── Access Control
│   ├── 跨 fabric 隔离
│   └── OTA 签名验证
│
├── 消息层
│   ├── Reliable / Unreliable
│   ├── MRP（Message Reliability Protocol）
│   ├── MRP Standalone Acknowledgement
│   └── Group Cast
│
├── 传输层
│   ├── UDP 5540
│   ├── TCP 5540
│   ├── DTLS（UDP 加密）
│   └── TLS 1.3（TCP 加密）
│
├── 网络层
│   ├── IPv6（必）
│   ├── 6LoWPAN（Thread）
│   ├── IP multicast
│   └── SLAAC 地址分配
│
└── 物理层
    ├── Wi-Fi (802.11)
    ├── Ethernet (802.3)
    └── Thread (802.15.4)
```

## 文档关系图

```text
matter.md (主题入口, 概览)
   ↓ 引用
matter-practical.md (速查, 调试流程)
   ↓ 引用
matter-deep-dive.md (原理, 体系)
   ↓ 引用
matter-failure-cases.md (案例, 实战)
   ↓ 全部引用
matter-index.md (本文件, 导航)
```

## 学习路径推荐（按角色）

### 嵌入式软件工程师（Matter 协议栈开发）

```text
入口 → 速查 → 原理 → 实战案例
0.5d   0.5d   2d     1d
```

### 智能家居 App 开发者

```text
速查（配网） → 原理（IM / Subscription） → 实战案例 3（跨生态同步）
0.5d            1d                          0.5d
```

### 协议栈移植工程师

```text
原理（协议栈） → 原理（数据模型） → 原理（配网） → 实战案例 1+2
1d              0.5d                0.5d          0.5d
```

### 安全工程师

```text
原理（证书链） → 原理（Attestation） → 实战案例 5（OTA 签名）
0.5d             0.5d                    0.5d
```

### 产品架构师（选型）

```text
入口（芯片清单） → 原理（Thread / Wi-Fi / Ethernet 对比）→ 速查（性能数据）
0.5d             0.5d                                  0.5d
```

### Matter 认证工程师

```text
实战案例 7（Cluster 顺序）→ 原理（Device Type） → 速查（认证测试）
0.5d                       0.5d                  0.5d
```

## Matter 主题 vs 其它主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| **Matter** | **5** | **~60 KB** | **应用层互操作 / 跨生态 / 配网 / 安全** |
| Thread | 5 | ~50 KB | mesh / 6LoWPAN / IPv6 / Border Router |
| BLE | 5 | ~50 KB | 低功耗 + GATT + 配对安全 |
| ZigBee | 5 | ~70 KB | Mesh 自组网 + ZCL + Trust Center |
| CAN | 8 | 120 KB | 实时多 master + 错误处理 |

**Matter 与 Thread / ZigBee / BLE 关系**：

```text
Matter:    应用层（智能家居互操作）
Thread:    mesh 网络层（Matter over Thread）
ZigBee:    mesh 网络层（Matter 受 ZigBee Cluster Library 影响）
BLE:       配网通道（仅用于 Matter Commissioning）

Matter ≠ Thread（Matter 是应用层，Thread 是网络层）
Matter 复用 ZCL Cluster
Matter 配网用 BLE
Matter 也跑在 Wi-Fi / Ethernet
```

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| matter.md | 改版才更新 | 主题入口 |
| matter-practical.md | 改版才更新 | 速查 / 调试流程 |
| matter-deep-dive.md | Matter 版本更新 | 原理体系 |
| matter-failure-cases.md | **持续更新** | 产线案例 |
| matter-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题（chips-com 其他目录）

- **`bus/thread-*.md`** — Matter over Thread（Matter 最常见部署）
- **`bus/ble-*.md`** — BLE 配网通道
- **`bus/zigbee-*.md`** — Cluster 沿用参考
- **`bus/uds-*.md`** — 诊断协议（不同领域）
- **`bus/ethernet-*.md`** — Matter over Ethernet

## 一句话总结

Matter 是"智能家居应用层互操作标准"，强在跨厂商 / 跨生态互通、本地优先、IP 化。从配网到产线案例，5 篇笔记覆盖完整。和 Thread（mesh 底层）、Wi-Fi / Ethernet（IP 接入）、BLE（配网通道）是**分层协作**关系，不是竞争。

## 更新记录

- 2026-08-01: 初版, 5 篇笔记全部完成 (L4 闭环)
  - 来源：Matter 1.4 规范 + 实战复盘
