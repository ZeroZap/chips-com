# J1939 主题总览

## 目标

J1939 是 chips-com 汽车 / 工规核心主题之一, 围绕"商用车网络协议"已经形成 8 篇专题笔记。本文档是**总览导航**, 帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/j1939-*.md
│
├── 简介层
│   ├── j1939.md                         1 页概念
│   └── j1939-practical.md               调试流程速查 + 实战
│
├── 规范层
│   └── j1939-protocol-spec.md           协议层分解 / 标准号 / 报文类型 / J1939-DA
│
├── 原理层
│   ├── j1939-deep-dive.md               PGN / CAN ID / NAME / DM / 优先级
│   └── j1939-network-management.md      NAME 字段 / 地址声明 / 命令地址 / 心跳
│
├── 实战层
│   ├── j1939-failure-cases.md           21 个产线死机案例
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

1. **`j1939-protocol-spec.md`** — 协议层分解与标准号选型
2. **`j1939-network-management.md`** — NAME / 地址分配
3. **`j1939-practical.md`** "## CAN ID 与 PGN"
4. **`j1939-deep-dive.md`** "## J1939 协议分层"

### 路径 F: "我要写规范文档 / 引用 SAE 标准号" (系统/标准工程师)

1. **`j1939-protocol-spec.md`** — J1939 全系列标准号按层分解、5 种报文类型、PGN 分类
2. **`j1939-protocol-spec.md`** "## 九、J1939 DA 与 DBC" — 参数定义来源
3. **`bus/can-standards-map.md`** — CAN 家族标准总表（含 J1939 反查索引）

### 路径 E: "我在做诊断 (DM1/DM14/UDS)" (诊断)

1. **`j1939-failure-cases.md`** 案例 2 / 9 / 14 — DM 错误
2. **`j1939-deep-dive.md`** "## 诊断报文 (DM)"
3. **`bus/uds-deep-dive.md`** — UDS 协议 (在 CAN 上的诊断)

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| J1939 是什么 | j1939.md |
| **J1939 分几个协议层 / 标准号** | **j1939-protocol-spec.md** "## 一、协议层分解" |
| **报文有哪几种类型** | **j1939-protocol-spec.md** "## 五、五种报文类型" |
| **参数定义从哪来 (DBC?)** | **j1939-protocol-spec.md** "## 九、J1939 DA 与 DBC" |
| **DTC 的 SPN/FMI/OC/CM 含义** | **j1939-protocol-spec.md** "## 八、诊断：DTC 与 DM 报文" |
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
│   ├── J1939-14: 500 kbaud, 每个 ECU 终端电阻
│   ├── J1939-15: 简化物理层 (轻型车)
│   └── J1939-17: CAN FD 物理层
│
├── 数据链路层
│   ├── CAN ID 编码 (PF, PS, SA, PRIO)
│   ├── PGN (Parameter Group Number)
│   ├── J1939-21 (含 TP 多包传输)
│   ├── J1939-22 (over CAN FD)
│   └── J1939-84 (越野 OBD 合规)
│
├── 传输层 (J1939-21 内含)
│   ├── TP.CM / TP.DT
│   ├── BAM (1 对多, 广播)
│   └── RTS/CTS (1 对 1, 重传)
│
├── 网络层
│   └── J1939-31 (布局与路由)
│
├── 网络管理
│   ├── J1939-81: NAME 字段 / 地址声明 / 命令地址
│   └── 心跳 (PGN 65260)
│
├── 应用层
│   ├── J1939-71: 车辆应用层 (PGN / SPN 定义)
│   ├── J1939-73: 诊断 (DM1, DM2, DM14, DM15)
│   └── J1939-DA: 参数数据库 (Excel, 非 DBC)
│
└── 工具
    ├── DBC 文件 (由 J1939-DA 生成)
    ├── J1939 合规性测试 (Vector / Softing)
    └── Linux SocketCAN J1939 内核模块
```

## 文档关系图

```text
j1939.md (简介)
   ↓ 引用
j1939-protocol-spec.md (规范层: 标准号 / 报文类型 / DA)
j1939-practical.md (速查)
   ↓ 引用
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
速查 → 产线案例 → J1939 合规性测试 → 故障注入
  0.5d   1d          0.5d                  0.5d
```

## 相关规范

J1939 全部由 **SAE** 发布，标准号按"层-序号"编号：

| 层 | 标准 | 作用 |
| --- | --- | --- |
| 数据链路 | **SAE J1939-21** | 核心标准。29-bit ID、PGN 构成、TP 多包传输（BAM / RTS-CTS） |
| CAN FD | SAE J1939-22 | J1939 跑在 CAN FD 上的数据链路层 |
| CAN FD | SAE J1939-17 | J1939 的 CAN FD 物理层 |
| 网络层 | SAE J1939-31 | 网络布局与路由 |
| 网络管理 | SAE J1939-81 | NAME 字段、地址声明、Commanded Address |
| 应用层 | SAE J1939-71 | 车辆应用层（PGN / SPN 定义） |
| 诊断 | SAE J1939-73 | DM1 / DM2 等诊断报文 |
| 合规 | SAE J1939-84 | 越野重型车 OBD 合规（Tier 4 final） |
| 合规 | SAE J1939-01 / -02 | J1939 体系总则 / 卡车客车合规性 |
| 物理 | SAE J1939-11 | 250 kbit/s 物理层（双绞 120Ω） |
| 物理 | SAE J1939-14 | 500 kbit/s 物理层（部分工程机械） |
| 物理 | SAE J1939-15 | 简化物理层（轻型车 / 乘用车） |
| 物理 | SAE J2284-1 ~ -4 | 北美 CAN 物理层 |
| 连接器 | SAE J1939-13 | 车载诊断连接器（DB9 / 13 针） |
| 安全 | SAE J1939-91A | 车载网络接口安全建议 |

**注意**：J1939-84 是**越野重型车 OBD 合规**标准，**不是**一致性测试规范。一致性测试由 SAE 组织的合规性测试流程（Vector / Softing 提供）执行。

**下层依赖**：

```text
J1939 应用层 (J1939-71 / -73)
└── J1939 数据链路 (J1939-21)
    └── CAN 物理层 (J1939-11 / -14 / -15, SAE J2284-x)
```

**相关法规**：EPA / CARB 重型车 OBD 法规；商用车环境看 SAE J1455。

**桥接**：CiA 510 定义了 CANopen（SDO / EMCY）到 J1939 PGN 的映射，可在同一网络上叠加。

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
| j1939-protocol-spec.md | SAE 改版才更新 | 规范 |
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
- **`bus/can-standards-map.md`** — CAN 家族标准规范总表

## 一句话总结

J1939 是商用车领域的"CAN 之上的标准化协议", 解决了"多厂商 ECU 互通"问题。从 NAME 字段到地址声明到 TP 多帧到 DM 诊断, 8 篇笔记覆盖完整。

## 更新记录

- 2026-07-28: 初版, 7 篇笔记全部完成 (L4 闭环升级)
- 2026-10-31: 新增「相关规范」节, 补齐 SAE J1939 全系列标准号; 修正 J1939-84 的定位 (越野 OBD 合规, 非一致性测试)。
- 2026-11-16: 新增 `j1939-protocol-spec.md` (规范层, 8 篇), 主题地图加「规范层」分支, 读者路径加路径 F (写规范/引用标准号), 速查矩阵加 4 条规范类入口, 概念地图重画为含物理/链路/传输/网络/管理/应用 6 层的完整分解。
