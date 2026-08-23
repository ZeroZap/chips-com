# Thread 主题总览

## 目标

Thread 是 chips-com 的核心无线协议主题之一，围绕"低功耗 mesh IPv6 网络"已经形成 5 篇专题笔记。本文档是**总览导航**，帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/thread-*.md
│
├── 速查层
│   └── thread-practical.md              调试流程速查 / 5 秒定位 / 错误码表
│
├── 原理层
│   └── thread-deep-dive.md              6LoWPAN / MLE / RPL / Border Router 深挖
│
├── 实战层
│   └── thread-failure-cases.md          9 个产线实战案例
│
└── 导航
    └── thread-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 Thread, 想入门" (新人)

按顺序读, 1-2 天能上手:

1. **`thread.md`** — 主题入口, 5 分钟
2. **`thread-practical.md`** — 关键参数 / 抓包工具
3. **`thread-deep-dive.md`** — 协议栈 / 路由 / 配网

### 路径 B: "我在做 Thread 设备产线失败" (现场救火)

1. **`thread-practical.md`** "## 5 秒钟定位"
2. **`thread-failure-cases.md`** — 找类似案例（9 个）
3. **`thread-deep-dive.md`** "## 错误码速查"

### 路径 C: "我在做 Thread 协议栈移植" (工程师)

1. **`thread-deep-dive.md`** "## 协议栈分层"
2. **`thread-practical.md`** "## OT CLI 常用命令"
3. **`thread-deep-dive.md`** "## MLE / RPL"

### 路径 D: "我在做 Thread + Matter 集成" (Matter 工程师)

1. **`thread.md`** "## Matter over Thread"
2. **`thread-deep-dive.md`** "## Commissioning"
3. **`bus/matter-practical.md`** "## Matter over Thread"

### 路径 E: "我在做 Border Router 部署" (运维)

1. **`thread-practical.md`** "## Border Router 配置"
2. **`thread-failure-cases.md`** 案例 6（BR 切换）
3. **`thread-deep-dive.md`** "## Border Router"

### 路径 F: "我在做 Thread 大规模部署" (架构师)

1. **`thread-failure-cases.md`** 案例 4（Router 子节点限制）
2. **`thread-practical.md`** "## 关键参数"
3. **`thread-deep-dive.md`** "## 性能数据"

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 入网流程 | thread-practical.md "## 调试步骤" |
| PSKc 派生 | thread-deep-dive.md "## PSKc / Joiner Key 派生" |
| Channel 怎么选 | thread-practical.md "## Channel" |
| Channel Mask | thread-practical.md "## Channel Mask 实战" |
| Border Router 配置 | thread-practical.md "## Border Router 配置" |
| 抓包工具 | thread-practical.md "## 抓包工具" |
| 5 秒定位 | thread-practical.md "## 5 秒钟定位" |
| 错误码 | thread-practical.md "## 错误码速查" |
| RPL 路由 | thread-deep-dive.md "## RPL" |
| MLE 链路 | thread-deep-dive.md "## MLE" |
| 6LoWPAN | thread-deep-dive.md "## 6LoWPAN" |
| 配网（Commissioning） | thread-deep-dive.md "## Commissioning" |
| 设备类型 | thread.md "## 设备类型" |
| 地址类型 | thread-deep-dive.md "## 地址" |
| Network Data | thread-deep-dive.md "## Network Data" |
| Sleepy End Device | thread-practical.md "## Sleepy End Device 配置" |
| Joiner 找不到 Commissioner | thread-failure-cases.md 案例 1 |
| Channel Mask 0 | thread-failure-cases.md 案例 2 |
| 多网络共信道 | thread-failure-cases.md 案例 3 |
| REED 升级 Router 失败 | thread-failure-cases.md 案例 4 |
| RPL 路由震荡 | thread-failure-cases.md 案例 5 |
| Border Router 切换 | thread-failure-cases.md 案例 6 |
| SED 频繁唤醒 | thread-failure-cases.md 案例 7 |
| Network Key 不匹配 | thread-failure-cases.md 案例 8 |
| IPv6 通信断 | thread-failure-cases.md 案例 9 |

## 关键概念地图

```text
Thread 协议栈
├── IEEE 802.15.4 PHY
│   ├── 2.4 GHz OQPSK, 250 kbps
│   ├── 信道 11-26
│   └── DSSS
│
├── IEEE 802.15.4 MAC
│   ├── CSMA/CA
│   └── ACK
│
├── 6LoWPAN
│   ├── IPHC 头压缩
│   ├── 分片 / 重组
│   └── Mesh 转发
│
├── IPv6
│   ├── ML-EID
│   ├── RLOC
│   ├── ALOC
│   └── Link-Local / ULA / GUA
│
├── MLE（Mesh Link Establishment）
│   ├── Link Request / Accept / Update
│   ├── Parent Selection
│   ├── Child Update
│   └── MLE Security（Network Key）
│
├── RPL（路由）
│   ├── DODAG 拓扑
│   ├── DIO / DAO / DIS / CC
│   ├── OF0 / MRHOF
│   └── Local / Global Repair
│
├── Network Data
│   ├── Prefix TLV
│   ├── Route TLV
│   └── Service TLV
│
├── CoAP（Constrained Application Protocol）
│   ├── UDP 61631
│   ├── /c/cs /c/cl /c/ca
│   └── 用于 Commissioning + Matter
│
├── DTLS 1.2 / TLS 1.3
│   ├── Joiner ↔ Commissioner
│   ├── Matter
│   └── Group Cast
│
├── UDP
│   ├── Commissioning 端口
│   ├── Matter 端口
│   └── 应用端口
│
├── 配网 (Commissioning)
│   ├── Commissioner
│   ├── Joiner
│   ├── PSKc / PSKd
│   └── DTLS 握手
│
├── 安全
│   ├── Master Key
│   ├── Network Key
│   ├── PSKc / Joiner Key
│   ├── MLE Security
│   └── DTLS
│
└── 设备类型
    ├── Router (FTD)
    ├── REED
    ├── End Device (MED)
    └── Sleepy End Device (SED)
```

## 文档关系图

```text
thread.md (主题入口, 概览)
   ↓ 引用
thread-practical.md (速查, 调试流程)
   ↓ 引用
thread-deep-dive.md (原理, 体系)
   ↓ 引用
thread-failure-cases.md (案例, 实战)
   ↓ 全部引用
thread-index.md (本文件, 导航)
```

## 学习路径推荐（按角色）

### 嵌入式软件工程师（Thread 协议栈开发）

```text
入口 → 速查 → 原理 → 实战案例
0.5d   0.5d   2d     1d
```

### Matter 集成工程师

```text
入口（Matter 关系）→ 速查（配网）→ 原理（Commissioning）→ 实战案例
0.5d                  0.5d                0.5d                  0.5d
```

### 协议栈移植工程师

```text
原理（协议栈）→ 原理（MLE / RPL）→ 实战案例 4-9
1d              1d                0.5d
```

### Border Router 运维

```text
速查（BR 配置）→ 实战案例 6（BR 切换）→ 原理（Border Router）
0.5d              0.5d                  0.5d
```

### 产品架构师（选型）

```text
入口（芯片清单）→ 原理（性能数据）→ 速查（典型参数）
0.5d             0.5d              0.5d
```

## Thread 主题 vs 其它主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| **Thread** | **5** | **~55 KB** | **IPv6 mesh / MLE / RPL / 配网 / BR** |
| Matter | 5 | ~60 KB | 应用层互操作 / 跨生态 / 配网 / 安全 |
| BLE | 5 | ~50 KB | 低功耗 + GATT + 配对安全 |
| ZigBee | 5 | ~70 KB | Mesh 自组网 + ZCL + Trust Center |
| CAN | 8 | 120 KB | 实时多 master + 错误处理 |

**Thread 与 Matter / ZigBee 关系**：

```text
Matter:    应用层（智能家居互操作）
Thread:    mesh 网络层（IPv6）
ZigBee:    mesh 网络层（私有 IPv4 风格协议）
BLE:       配网通道

Matter over Thread：Matter 应用跑在 Thread mesh 上
Matter over Wi-Fi：Matter 应用跑在 Wi-Fi 上
ZigBee Cluster Library → Matter Cluster Library
```

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| thread.md | 改版才更新 | 主题入口 |
| thread-practical.md | 改版才更新 | 速查 / 调试流程 |
| thread-deep-dive.md | Thread 版本更新 | 原理体系 |
| thread-failure-cases.md | **持续更新** | 产线案例 |
| thread-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题（chips-com 其他目录）

- **`bus/matter-*.md`** — Matter over Thread（最常见部署）
- **`bus/zigbee-*.md`** — 同源 PHY 对比（ZigBee 不走 IPv6）
- **`bus/ble-*.md`** — BLE 配网通道
- **`bus/ethernet-*.md`** — Matter over Ethernet
- **`bus/wi-fi-*.md`** — Wi-Fi IoT 协议（待建）

## 一句话总结

Thread 是"低功耗 mesh IPv6 网络协议"，强在 mesh 自愈、IPv6 端到端、Matter 集成。从配网到产线案例，5 篇笔记覆盖完整。和 Matter（应用层）、BLE（配网通道）、ZigBee（同源 PHY）是**分层协作 / 互补**关系。

## 更新记录

- 2026-08-01: 初版, 5 篇笔记全部完成 (L4 闭环)
  - 来源：Thread 1.3 规范 + OpenThread 实战 + 实战复盘
