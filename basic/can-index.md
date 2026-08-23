# CAN 主题总览

## 目标

CAN 是 chips-com 的核心主题之一, 围绕"汽车/工规多 master 实时总线"已经形成 8 篇专题笔记。本文档是**总览导航**, 帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/basic/can-*.md
│
├── 速查层
│   └── can-practical.md                 调试流程速查
│
├── 原理层
│   ├── can-deep-dive.md                 物理层 / 帧格式 / 仲裁 / 错误处理 / 故障树
│   └── can-multimaster-and-bus-off.md   多 master 仲裁 + 错误状态机 + Bus Off
│
├── 实战层
│   ├── can-failure-cases.md             20 个产线死机案例
│   ├── can-fd-and-can-xl.md             演进: CAN FD 数据段加速 + CAN XL
│   ├── can-rtos-integration.md          RTOS 集成 + Linux SocketCAN
│   └── can-vs-other-bus.md              与 I2C/SPI/UART/RS485/Ethernet 对比
│
└── 导航
    └── can-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 CAN, 想入门" (新人)

按顺序读, 1-2 天能上手:

1. **`can-practical.md`** — 调试流程速查, 10 分钟
2. **`can-deep-dive.md`** — 原理, 重点:
   - "## CAN 物理层"
   - "## CAN 帧格式 (经典 CAN)"
   - "## CAN 仲裁机制"
   - "## CAN 错误处理"
3. **`can-multimaster-and-bus-off.md`** — 多 master + 错误状态机

### 路径 B: "我在做产线 CAN 通信失败" (现场救火)

1. **`can-practical.md`** "## 5 秒钟定位"
2. **`can-deep-dive.md`** "## CAN 故障树"
3. **`can-failure-cases.md`** — 找类似案例 (20 个)
4. **`can-multimaster-and-bus-off.md`** — 节点状态机

### 路径 C: "我在做 CAN FD 升级" (工程实现)

1. **`can-fd-and-can-xl.md`** — 演进
2. **`can-deep-dive.md`** "## CAN FD 简介"
3. **`can-rtos-integration.md`** — 配置代码

### 路径 D: "我在做汽车 ECU 选型" (架构师)

1. **`can-vs-other-bus.md`** — 横向对比
2. **`can-practical.md`** "## 关键参数"
3. **`can-deep-dive.md`** "## CAN 收发器选型"
4. **`can-multimaster-and-bus-off.md`** — 调度策略

### 路径 E: "我在 Linux 上做 CAN 开发"

1. **`can-rtos-integration.md`** "## Linux SocketCAN"
2. **`can-practical.md`** Linux 工具 (can-utils)
3. **`can-failure-cases.md`** — Linux 场景

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 终端电阻怎么接, 阻值多少 | can-practical.md "## 终端电阻详解" |
| 波特率怎么算 | can-deep-dive.md "## 波特率计算" |
| 仲裁机制 | can-deep-dive.md "## CAN 仲裁机制" |
| 错误计数器 (TEC/REC) 规则 | can-multimaster-and-bus-off.md "## 错误计数器 (TEC/REC) 规则" |
| Bus Off 怎么恢复 | can-multimaster-and-bus-off.md "## Bus Off 恢复机制" |
| 节点状态机 | can-multimaster-and-bus-off.md "## 节点状态机" |
| CAN FD 和经典 CAN 区别 | can-fd-and-can-xl.md "## CAN FD 关键改进" |
| CAN FD 收发器选型 | can-fd-and-can-xl.md "## CAN FD 物理层" |
| 过滤器怎么配 | can-deep-dive.md "## CAN 过滤器" |
| ID 怎么分配 | can-multimaster-and-bus-off.md "## 应用层优先级分配" |
| 多 master 调度 | can-multimaster-and-bus-off.md "## 多 Master 调度的工程问题" |
| SocketCAN 编程 | can-rtos-integration.md "## Linux SocketCAN" |
| RTOS 集成模式 | can-rtos-integration.md "## 三个 RTOS 的 CAN 抽象" |
| 产线死机案例 | can-failure-cases.md |
| 和 I2C 区别 | can-vs-other-bus.md "## CAN vs I2C" |
| 和 SPI 区别 | can-vs-other-bus.md "## CAN vs SPI" |
| 和 RS485 区别 | can-vs-other-bus.md "## CAN vs UART/RS485" |
| 和 Ethernet 区别 | can-vs-other-bus.md "## CAN vs Ethernet" |
| CAN FD vs CAN XL 选型 | can-fd-and-can-xl.md "## CAN FD 选型决策" |

## 关键概念地图

```text
CAN 总线
├── 物理层
│   ├── 差分 CAN_H / CAN_L
│   ├── 收发器 (TJA1050, TJA1443, SN65HVD257)
│   ├── 终端电阻 120 ohm
│   └── 隔离收发器 (工业)
│
├── 协议层
│   ├── 帧格式 (标准/扩展/FD)
│   ├── 位填充
│   ├── CRC 校验
│   ├── 仲裁 (显性优先)
│   └── ACK 机制
│
├── 错误处理
│   ├── 5 类错误 (位 / 填充 / CRC / 形式 / 应答)
│   ├── 错误计数器 (TEC / REC)
│   ├── 节点状态 (Active / Passive / Bus Off)
│   └── 自动恢复 (AutoBusOff)
│
├── 工程
│   ├── ID 分配 (DBC 文件)
│   ├── 报文优先级
│   ├── 报文聚合
│   ├── 总线利用率
│   ├── 过滤器配置
│   └── 多 master 调度
│
└── 演进
    ├── CAN FD (数据段加速, 64 字节)
    ├── CAN FD ISO 标准
    └── CAN XL (高速, 2048 字节, TSN 融合)
```

## 文档关系图

```text
can-practical.md (速查, 入门)
   ↓ 引用
can-deep-dive.md (原理, 体系)
   ↓ 引用
can-failure-cases.md (案例, 实战)
can-multimaster-and-bus-off.md (仲裁, 错误)
can-fd-and-can-xl.md (演进)
can-rtos-integration.md (RTOS, Linux)
can-vs-other-bus.md (跨总线对比)
   ↓ 全部引用
can-index.md (本文件, 导航)
```

## 学习路径推荐 (按角色)

### 嵌入式软件工程师
```text
速查 → 原理 → 多 master / 错误处理 → RTOS / Linux
  0.5d   1d      1d                  1d
```

### 汽车 ECU 工程师
```text
速查 → 原理 → 多 master → CAN FD → UDS / 诊断
  0.5d   1d      1d         0.5d      1d
```

### 工业 / 自动化工程师
```text
速查 → 原理 → CANopen / Modbus → 跨总线对比
  0.5d   1d       1d              0.5d
```

### 嵌入式硬件工程师
```text
速查 → 物理层 (deep-dive) → 收发器选型 → 信号完整性
  0.5d   1d                    0.5d          1d
```

### 产品架构师
```text
跨总线对比 → 选型决策树 → CANopen / J1939 / UDS 应用
  0.5d          0.5d                1d
```

## CAN 主题 vs I2C/SPI/UART 主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| **CAN** | **8** | **120 KB** | **实时多 master + 错误处理 + 演进 (FD/XL)** |
| I2C | 12 | 151 KB | 协议兼容性 + 总线恢复 (Recovery) |
| SPI | 6 | 75 KB | 多从 / 菊花链 / 高速 |
| UART | 6 | 80 KB | RS485 / 流控 / 异步日志 |

**共同点**:
- 都有速查 + 原理 + 实战 + 专题 + 导航 5 层结构
- 都有 failure-cases (产线死机案例)
- 都有 RTOS 集成
- 都有跨总线对比

**差异**:
- CAN 重点: 多 master 仲裁 + 错误处理 (CAN 特色)
- I2C 重点: 总线恢复 (I2C 特色, 因为有 8 步 SOP)
- SPI 重点: 多从 / 菊花链 (SPI 特色)
- UART 重点: RS485 / 流控 (UART 特色)

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| can-practical.md | 改版才更新 | 速查 / 调试流程 |
| can-deep-dive.md | 改版才更新 | 原理体系 |
| can-failure-cases.md | **持续更新** | 产线案例 |
| can-multimaster-and-bus-off.md | 改版才更新 | 仲裁 / 错误 |
| can-fd-and-can-xl.md | CAN XL 量产时 | 演进 |
| can-rtos-integration.md | RTOS 改版时 | RTOS 集成 |
| can-vs-other-bus.md | 新总线出现时 | 跨总线对比 |
| can-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题 (chips-com 其他目录)

- **`bus/can-canopen-deep-dive.md`** — CANopen (CAN 之上的应用层协议)
- **`bus/can-canopen-practical.md`** — CANopen 实战
- **`bus/j1939-deep-dive.md`** — J1939 (商用车, 基于 CAN)
- **`bus/j1939-practical.md`** — J1939 实战
- **`bus/uds-deep-dive.md`** — UDS (诊断, 基于 CAN)
- **`bus/uds-practical.md`** — UDS 实战
- **`bus/iso-tcp-practical.md`** — ISO-TP (CAN 之上多帧传输)
- **`bus/rs485-modbus-rtu-deep-dive.md`** — Modbus RTU (RS485)
- **`bus/ethernet-ip-deep-dive.md`** — EtherNet/IP (工业 Ethernet)
- **`basic/can-phy.md`** — CAN 物理层基础
- **`i2c-vs-smbus-recovery.md`** — 跨协议对比参考
- **`i2c-bus-recovery-playbook.md`** — 总线恢复对比
- **`spi-failure-cases.md`** — 产线死机案例对比

## 一句话总结

CAN 是"可靠的实时多 master 现场总线", 强在错误检测、仲裁和实时性。从原理到产线案例, 8 篇笔记覆盖完整。和 I2C / SPI / UART 的关系是"互补"而非"竞争"。

## 更新记录

- 2026-07-26: 初版, 8 篇笔记全部完成 (L4 闭环)
