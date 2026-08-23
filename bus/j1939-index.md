# J1939 主题总览

## 目标

J1939 是 chips-com 汽车 / 工规核心主题之一, 围绕"商用车网络协议"已经形成 7 篇专题笔记。本文档是**总览导航**, 帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/j1939-*.md
│
├── 简介层
│   ├── j1939.md                         1 页概念
│   └── j1939-practical.md               调试流程速查 + 实战
│
├── 原理层
│   ├── j1939-deep-dive.md               PGN / CAN ID / NAME / DM / 优先级
│   └── j1939-network-management.md      NAME 字段 / 地址声明 / 命令地址 / 心跳
│
├── 实战层
│   ├── j1939-failure-cases.md           20 个产线死机案例
│   └── j1939-transport-protocol.md      BAM / RTS/CTS 多帧传输
│
└── 导航
    └── j1939-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 J1939, 想入门" (新人)

1. **`j1939.md`** — 1 页概念, 5 分钟
2. **`j1939-practical.md`** — 调试流程速查
3. **`j1939-deep-dive.md`** — 原理, 重点:
   - "## J1939 与 CAN 的关系"
   - "## PGN 和 SPN"
   - "## CAN ID 编码"
   - "## NAME 字段"
4. **`j1939-network-management.md`** — 地址声明

### 路径 B: "我在做产线 J1939 通信失败" (现场救火)

1. **`j1939-failure-cases.md`** — 找类似案例
2. **`j1939-practical.md`** "## 调试步骤"
3. **`j1939-deep-dive.md`** "## 错误处理"

### 路径 C: "我在做 ECU 固件下载 / 大数据传输" (工程实现)

1. **`j1939-transport-protocol.md`** — BAM / RTS/CTS
2. **`j1939-failure-cases.md`** 案例 3 / 6 / 19 — TP 错误案例
3. **`j1939-deep-dive.md`** "## J1939-21 传输协议"

### 路径 D: "我在做商用车 ECU 选型 / 集成" (架构师)

1. **`j1939-network-management.md`** — NAME / 地址分配
2. **`j1939-practical.md`** "## CAN ID 与 PGN"
3. **`j1939-deep-dive.md`** "## J1939 协议分层"

### 路径 E: "我在做诊断 (DM1/DM14/UDS)" (诊断)

1. **`j1939-failure-cases.md`** 案例 2 / 9 / 14 — DM 错误
2. **`j1939-deep-dive.md`** "## 诊断报文 (DM)"
3. **`bus/uds-deep-dive.md`** — UDS 协议 (在 CAN 上的诊断)

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| J1939 是什么 | j1939.md |
| CAN ID 怎么编码 | j1939-deep-dive.md "## CAN ID 编码" |
| PGN / SPN 是什么 | j1939-deep-dive.md "## PGN 和 SPN" |
| NAME 字段结构 | j1939-network-management.md "## NAME 字段" |
| 地址声明协议 | j1939-network-management.md "## 地址声明" |
| 命令地址协议 | j1939-network-management.md "## 命令地址" |
| 心跳机制 | j1939-network-management.md "## 心跳" |
| BAM 协议 | j1939-transport-protocol.md "## BAM" |
| RTS/CTS 协议 | j1939-transport-protocol.md "## RTS/CTS" |
| DM1 格式 | j1939-deep-dive.md "## 诊断报文 (DM)" |
| 多帧 DTC 传输 | j1939-transport-protocol.md |
| 优先级 (PRIO) 怎么设 | j1939-failure-cases.md 案例 13 |
| 地址冲突怎么解决 | j1939-network-management.md "## 实战代码" |
| 产线死机案例 | j1939-failure-cases.md |
| J1939-84 一致性测试 | j1939-failure-cases.md 案例 20 |
| J1939 vs CAN | can-vs-other-bus.md "## CAN vs LIN" / j1939-deep-dive.md |
| Linux J1939 内核 | j1939-network-management.md "## Linux 内核 J1939 支持" |

## 关键概念地图

```text
J1939 协议族
├── 物理层
│   ├── CAN 2.0B (29 bit ID)
│   ├── J1939-11: 250 kbaud, 屏蔽双绞, 终端电阻在 OBD
│   └── J1939-14: 500 kbaud, 每个 ECU 终端电阻
│
├── 数据链路层
│   ├── CAN ID 编码 (PF, PS, SA, PRIO)
│   ├── PGN (Parameter Group Number)
│   └── 多 master 仲裁
│
├── 应用层
│   ├── NAME 字段 (64 bit)
│   ├── 地址声明 (PGN 60928)
│   ├── 命令地址 (PGN 65240)
│   ├── 心跳 (PGN 65260)
│   └── DM 诊断报文 (DM1, DM2, DM14, DM15)
│
├── 传输协议
│   ├── BAM (1 对多, 广播)
│   └── RTS/CTS (1 对 1, 重传)
│
├── 协议分层
│   ├── J1939-21: 传输层
│   ├── J1939-71: 车辆应用层
│   ├── J1939-73: 诊断
│   ├── J1939-81: 网络管理
│   └── J1939-84: 一致性测试
│
└── 工具
    ├── DBC 文件 (CANdb++ / Vector)
    ├── J1939-84 一致性测试 (Vector / Softing)
    └── Linux SocketCAN J1939 内核模块
```

## 文档关系图

```text
j1939.md (简介)
   ↓ 引用
j1939-practical.md (速查)
j1939-deep-dive.md (原理)
   ↓ 引用
j1939-network-management.md (网络管理)
j1939-transport-protocol.md (TP 协议)
j1939-failure-cases.md (产线案例)
   ↓ 全部引用
j1939-index.md (本文件, 导航)
```

## 学习路径推荐 (按角色)

### 汽车 ECU 软件工程师
```text
速查 → 原理 → 网络管理 → TP 协议 → 产线案例
  0.5d   1d      1d          1d       1d
```

### 汽车 ECU 硬件工程师
```text
简介 → 速查 → 物理层 (J1939-11/14) → 收发器
  0.5d   0.5d      0.5d                0.5d
```

### 商用车诊断工程师
```text
速查 → 原理 (DM 部分) → TP → 产线 DM 案例 → UDS
  0.5d   1d              1d    0.5d          1d
```

### 车载网络架构师
```text
网络管理 → 跨总线对比 → J1939 vs CAN FD vs Ethernet
  1d          0.5d              0.5d
```

### 产线测试工程师
```text
速查 → 产线案例 → J1939-84 一致性测试 → 故障注入
  0.5d   1d          0.5d                  0.5d
```

## J1939 vs CAN FD 决策

| 场景 | 推荐 |
| --- | --- |
| 现有 J1939 网络 | 保持 J1939 (经典 CAN) |
| 新设计, 高速需求 | J1939 + CAN FD |
| 跨厂商 (Tier 1) 集成 | J1939 (标准 PGN) |
| 域控制器 (ADAS) | Ethernet (J1939 不够) |
| 整车主干网 | CAN FD + Ethernet |
| 卡车 / 客车 / 工程机械 | J1939 主流 |

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| j1939.md | 改版才更新 | 简介 |
| j1939-practical.md | 改版才更新 | 速查 |
| j1939-deep-dive.md | 改版才更新 | 原理 |
| j1939-network-management.md | 改版才更新 | 网络管理 |
| j1939-transport-protocol.md | 改版才更新 | TP 协议 |
| j1939-failure-cases.md | **持续更新** | 产线案例 |
| j1939-index.md | 新增 / 删除时 | 导航 |

## 关联主题 (chips-com 其他目录)

- **`basic/can-*.md`** — CAN 基础 (J1939 的物理层)
- **`bus/can-canopen-deep-dive.md`** — CANopen (CAN 之上, 工业)
- **`bus/uds-*.md`** — UDS (ISO 14229, J1939 诊断之上)
- **`bus/iso-tp-*.md`** — ISO-TP (UDS 多帧传输, 类似 J1939 TP)
- **`bus/uds-deep-dive.md`** — UDS 详细
- **`basic/can-vs-other-bus.md`** — CAN vs I2C / SPI / UART / RS485
- **`can-multimaster-and-bus-off.md`** — CAN 多 master (J1939 用)

## 一句话总结

J1939 是商用车领域的"CAN 之上的标准化协议", 解决了"多厂商 ECU 互通"问题。从 NAME 字段到地址声明到 TP 多帧到 DM 诊断, 7 篇笔记覆盖完整。

## 更新记录

- 2026-07-28: 初版, 7 篇笔记全部完成 (L4 闭环升级)
