# ZigBee 主题总览

## 目标

ZigBee 是 chips-com 的核心无线协议主题之一，围绕"低功耗 mesh 自组网 IoT 通信"已经形成 5 篇专题笔记。本文档是**总览导航**，帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/zigbee-*.md
│
├── 速查层
│   └── zigbee-practical.md              调试流程速查 / 5 秒定位 / 错误码表
│
├── 原理层
│   └── zigbee-deep-dive.md              IEEE 802.15.4 PHY/MAC / NWK / APS / ZDO / ZCL
│
├── 实战层
│   └── zigbee-failure-cases.md          8 个产线实战案例
│
└── 导航
    └── zigbee-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 ZigBee, 想入门" (新人)

按顺序读, 1-2 天能上手:

1. **`zigbee.md`** — 主题入口, 5 分钟
2. **`zigbee-practical.md`** — 关键参数 / 5 秒定位
3. **`zigbee-deep-dive.md`** — 协议栈分层 + ZCL 模型

### 路径 B: "我在做 ZigBee 设备产线失败" (现场救火)

1. **`zigbee-practical.md`** "## 5 秒钟定位"
2. **`zigbee-failure-cases.md`** — 找类似案例（8 个）
3. **`zigbee-deep-dive.md`** "## NWK Status 速查"

### 路径 C: "我在做 ZigBee 协议栈移植" (工程师)

1. **`zigbee-deep-dive.md`** "## IEEE 802.15.4 MAC"
2. **`zigbee-practical.md`** "## 抓包工具"
3. **`zigbee-deep-dive.md`** "## 入网流程"

### 路径 D: "我在做 ZigBee 安全加固" (安全工程师)

1. **`zigbee-deep-dive.md`** "## 安全"
2. **`zigbee-failure-cases.md`** 案例 7（默认 Link Key 量产踩雷）
3. **`zigbee-practical.md`** "## Trust Center 与安全"

### 路径 E: "我在做 ZigBee 选型" (架构师)

1. **`zigbee.md`** "## 典型芯片"
2. **`zigbee-deep-dive.md`** "## 厂商协议栈对比"
3. **`zigbee-practical.md`** "## 性能数据参考"

### 路径 F: "我在做智能家居 zigbee2mqtt 部署" (运维)

1. **`zigbee-failure-cases.md`** 案例 2（zigbee2mqtt 50+ 设备掉线）
2. **`zigbee-practical.md`** "## 抓包工具" 的 zigbee2mqtt 部分
3. **`zigbee-deep-dive.md`** "## ZCL"

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 入网流程 | zigbee-deep-dive.md "## 入网流程" |
| 路由机制 | zigbee-deep-dive.md "## 路由" |
| 信道怎么选 | zigbee-practical.md "## 信道" |
| PAN ID 冲突 | zigbee-failure-cases.md 案例 5 |
| CC2530 ReJoin 失败 | zigbee-failure-cases.md 案例 1 |
| zigbee2mqtt 调优 | zigbee-failure-cases.md 案例 2 |
| EFR32 NCP 调试 | zigbee-failure-cases.md 案例 3 |
| End Device 续航 | zigbee-failure-cases.md 案例 4 |
| ZCL Cluster | zigbee-deep-dive.md "## ZCL" |
| ZCL 错误码 | zigbee-practical.md "## ZCL Status 速查" |
| NWK 错误码 | zigbee-practical.md "## NWK Status 速查" |
| APS 错误码 | zigbee-practical.md "## APS Status 速查" |
| Bind / Group | zigbee-deep-dive.md "## Bind / Group" |
| Trust Center | zigbee-practical.md "## Trust Center 与安全" |
| Install Code | zigbee-failure-cases.md 案例 7 |
| 抓包工具 | zigbee-practical.md "## 抓包工具" |
| Daintree SNA 抓包硬件 | zigbee-practical.md "## 抓包工具"（Daintree SNA 行） |
| 串口电平不匹配（DL-20） | zigbee-practical.md "### USB-TTL 串口电平匹配" |
| CC2530 P0_4 端口 bug | zigbee-practical.md "## 常见问题速查" |
| 改 PANID 后老节点不重连 | zigbee-failure-cases.md 案例 9（参考同类 NV 问题） |
| EFR32MG21 入网卡 association | zigbee-failure-cases.md 案例 9 |
| ZigBee 晶振选型实战 | zigbee-practical.md "### ZigBee 晶振选型实战" |
| CH582 RISC-V 国产 BLE+USB | zigbee-practical.md "### CH582 RISC-V 自定义 BLE Service 实战" |
| 3.3V LDO 浪涌烧毁 | zigbee-failure-cases.md 案例 10 |
| 才茂 CM210 4 类故障 | zigbee-failure-cases.md 案例 11 |
| CC2530 量产烧录 17 错误 | zigbee-failure-cases.md 案例 12 |
| 单子网 ≤60 节点上限 | zigbee-failure-cases.md 案例 13 |
| PAN ID 冲突 63/min 阈值 | zigbee-failure-cases.md 案例 14 |
| 4 万亩滴灌吸盘天线脱落 | zigbee-failure-cases.md 案例 15 |
| 路由风暴 + Neighbor Table 溢出 | zigbee-failure-cases.md 案例 16 |
| 5 大入网失败 + 200 节点 | zigbee-failure-cases.md 案例 17 |
| 涂鸦多网关离线 15-30% | zigbee-failure-cases.md 案例 18 |
| Transport Key 失败 3 根因 | zigbee-failure-cases.md 案例 19 |
| 自愈变自杀 化工厂凌晨雪崩 | zigbee-failure-cases.md 案例 20 |
| 晓网 5 大根因 2000 平米仓库 | zigbee-failure-cases.md 案例 21 |
| BlackHat 2015 + Aviatrix 2024 安全 | zigbee-failure-cases.md 案例 22 |
| Green Power 全栈 + GP 失踪 5 根因 | zigbee-failure-cases.md 案例 23 |
| EFR32 NCP 并发 OTA 0x19 buffer out | zigbee-failure-cases.md 案例 24 |
| Poll Interval | zigbee-practical.md "## End Device 睡眠参数" |
| SoC vs NCP 差异 | zigbee-deep-dive.md "## SoC vs NCP 调试差异" |
| 厂商协议栈对比 | zigbee-deep-dive.md "## 厂商协议栈对比" |
| 协议栈版本兼容 | zigbee-failure-cases.md 案例 8 |

## 关键概念地图

```text
ZigBee 协议栈
├── IEEE 802.15.4 PHY
│   ├── 2.4 GHz ISM（16 信道）
│   ├── 868 / 915 MHz
│   ├── OQPSK + DSSS
│   └── 250 kbps
│
├── IEEE 802.15.4 MAC
│   ├── Beacon / Data / ACK / Command
│   ├── CSMA/CA
│   ├── 超帧结构（CAP + CFP）
│   └── 安全（已弃用）
│
├── ZigBee NWK
│   ├── 设备类型 (Coordinator / Router / End Device)
│   ├── 16-bit NWK 地址
│   ├── 入网（Association / Rejoin / Orphan）
│   ├── 路由（Tree / Table / Source）
│   └── 路由表维护
│
├── ZigBee APS
│   ├── APS Data / Command
│   ├── Bind / Group / Address Table
│   ├── APS 安全（Link Key / Network Key）
│   └── 寻址模式
│
├── ZigBee ZDO
│   ├── Network Address Request
│   ├── IEEE Address Request
│   ├── Active Endpoints Request
│   ├── Simple Descriptor
│   ├── Mgmt 系列（_NWK_Disc, _LQI, _Rtg, _Bind, _Leave）
│   └── Device Announce
│
├── ZCL（ZigBee Cluster Library）
│   ├── Attribute / Command / Report
│   ├── 基础 Cluster (Basic, Identify, On/Off, Level, Color)
│   ├── 测量 Cluster (Illuminance, Temperature, Occupancy)
│   ├── 控制 Cluster (Thermostat, Thermostat UI)
│   └── ZCL Frame
│
├── 安全
│   ├── Trust Center Link Key
│   ├── Network Key + Key Update
│   ├── Install Code 派生 Link Key
│   └── Application / APS Link Key
│
└── 协议版本
    ├── ZigBee 1.x (HA, SE, RS)
    ├── ZigBee 3.0 (统一)
    └── ZigBee 3.0 + Matter 演进
```

## 文档关系图

```text
zigbee.md (主题入口, 概览)
   ↓ 引用
zigbee-practical.md (速查, 调试流程)
   ↓ 引用
zigbee-deep-dive.md (原理, 体系)
   ↓ 引用
zigbee-failure-cases.md (案例, 实战)
   ↓ 全部引用
zigbee-index.md (本文件, 导航)
```

## 学习路径推荐（按角色）

### 嵌入式软件工程师（ZigBee 协议栈开发）

```text
入口 → 速查 → 原理 → 实战案例
0.5d   0.5d   2d     1d
```

### 智能家居 / 楼宇 ZigBee 部署工程师

```text
入口 → 实战案例 2（zigbee2mqtt）→ 原理（ZCL）→ 抓包工具
0.5d   1d                       1d          0.5d
```

### 协议栈移植工程师

```text
原理（IEEE 802.15.4）→ 原理（NWK 入网）→ 实战案例 1（CC2530 BUG）
1d                  1d                     1d
```

### 安全工程师

```text
原理（安全）→ 实战案例 7（默认 Link Key）→ 原理（Install Code）
1d            0.5d                          0.5d
```

### 产品架构师（选型）

```text
入口（芯片清单） → 原理（厂商协议栈对比）→ 速查（性能数据）
0.5d             0.5d                       0.5d
```

## ZigBee 主题 vs 其它主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| **ZigBee** | **5** | **~70 KB** | **Mesh 自组网 + ZCL + Trust Center** |
| BLE | 5 | ~40 KB | 低功耗 + GATT + 配对安全 |
| CAN | 8 | 120 KB | 实时多 master + 错误处理 |
| USB | 9 | ~130 KB | 描述符 + 类驱动 + DMA |
| J1939 | 7 | ~95 KB | 商用车协议栈 + 地址声明 |

**共同点**:

- 都有速查 + 原理 + 实战 + 导航 4 层结构
- 都有 failure-cases (产线死机案例)
- 都有 practical 中的"5 秒定位" / 速查表

**差异**:

- ZigBee 重点: Mesh 路由 + 入网流程 + ZCL 标准化 (ZigBee 特色)
- BLE 重点: GATT 属性 + 配对安全 (BLE 特色)
- CAN 重点: 多 master 仲裁 + 错误处理 (CAN 特色)

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| zigbee.md | 改版才更新 | 主题入口 |
| zigbee-practical.md | 改版才更新 | 速查 / 调试流程 |
| zigbee-deep-dive.md | 协议改版 / ZigBee 4 出 | 原理体系 |
| zigbee-failure-cases.md | **持续更新** | 产线案例 |
| zigbee-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题（chips-com 其他目录）

- **`bus/ble-deep-dive.md`** — BLE（IEEE 802.15.4 同源 PHY，但不同协议栈）
- **`bus/ble-practical.md`** — BLE 实战
- **`bus/ble-failure-cases.md`** — BLE 产线案例
- **`bus/j1939-deep-dive.md`** — J1939（汽车总线，差分 CAN）
- **`bus/can-canopen-deep-dive.md`** — CANopen（CAN 之上应用层）
- **`bus/uds-deep-dive.md`** — 诊断协议（基于 CAN）
- **`bus/ethercat-deep-dive.md`** — 工业 Ethernet

## 一句话总结

ZigBee 是"低功耗 mesh 自组网 IoT 协议的事实标准"，强在 Mesh 自愈、ZCL 标准化、安全配对。从原理到产线案例，5 篇笔记覆盖完整。和 BLE（点对点星型）、Wi-Fi（高速高功耗）、Thread（IPv6 mesh）、LoRa（远距）是**互补**关系。

## 更新记录

- 2026-08-01: 初版, 5 篇笔记全部完成 (L4 闭环)
  - 来源：_Inbox/ZigBee-2026-08-01-candidates.md 3 条候选 + 实战补充
