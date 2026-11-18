---
tags:
  - layer/basic
  - type/index
  - protocol/can
---

# CAN 主题总览

## 目标

CAN 是 chips-com 的核心主题之一, 围绕"汽车/工规多 master 实时总线"已经形成 9 篇专题笔记（含索引）。本文档是 **PHY / 控制器层索引**, 聚焦位时序、差分物理层、仲裁与 Bus Off；协议栈与诊断族请从 [[bus/automotive/can-index|can-index]] 进入。

## 主题地图

```text
chips-com/basic/can-*.md
│
├── 速查层
│   └── can-practical.md                 调试流程速查
│
├── 原理层
│   ├── can-phy.md                       物理层 / 收发器 / 终端电阻
│   ├── can-deep-dive.md                 物理层 / 帧格式 / 仲裁 / 错误处理 / 故障树
│   └── can-multimaster-and-bus-off.md   多 master 仲裁 + 错误状态机 + Bus Off
│
├── 实战层
│   ├── can-failure-cases.md             21 个产线死机案例
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

1. **[[basic/can-practical|can-practical]]** — 调试流程速查, 10 分钟
2. **[[basic/can-deep-dive|can-deep-dive]]** — 原理, 重点:
   - "## CAN 物理层"
   - "## CAN 帧格式 (经典 CAN)"
   - "## CAN 仲裁机制"
   - "## CAN 错误处理"
3. **[[basic/can-multimaster-and-bus-off|can-multimaster-and-bus-off]]** — 多 master + 错误状态机

### 路径 B: "我在做产线 CAN 通信失败" (现场救火)

1. **[[basic/can-practical|can-practical]]** "## 5 秒钟定位"
2. **[[basic/can-deep-dive|can-deep-dive]]** "## CAN 故障树"
3. **[[basic/can-failure-cases|can-failure-cases]]** — 找类似案例 (21 个)
4. **[[basic/can-multimaster-and-bus-off|can-multimaster-and-bus-off]]** — 节点状态机

### 路径 C: "我在做 CAN FD 升级" (工程实现)

1. **[[basic/can-fd-and-can-xl|can-fd-and-can-xl]]** — 演进
2. **[[basic/can-deep-dive|can-deep-dive]]** "## CAN FD 简介"
3. **[[basic/can-rtos-integration|can-rtos-integration]]** — 配置代码

### 路径 D: "我在做汽车 ECU 选型" (架构师)

1. **[[basic/can-vs-other-bus|can-vs-other-bus]]** — 横向对比
2. **[[basic/can-practical|can-practical]]** "## 关键参数"
3. **[[basic/can-deep-dive|can-deep-dive]]** "## CAN 收发器选型"
4. **[[basic/can-multimaster-and-bus-off|can-multimaster-and-bus-off]]** — 调度策略

### 路径 E: "我在 Linux 上做 CAN 开发"

1. **[[basic/can-rtos-integration|can-rtos-integration]]** "## Linux SocketCAN"
2. **[[basic/can-practical|can-practical]]** Linux 工具 (can-utils)
3. **[[basic/can-failure-cases|can-failure-cases]]** — Linux 场景

## 主题速查矩阵

按问题找文档:

| 我想知道                  | 看哪里                                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------- |
| 终端电阻怎么接, 阻值多少  | [[basic/can-practical\|can-practical]] "## 终端电阻详解"                                          |
| 波特率怎么算              | [[basic/can-deep-dive\|can-deep-dive]] "## 波特率计算"                                            |
| 仲裁机制                  | [[basic/can-deep-dive\|can-deep-dive]] "## CAN 仲裁机制"                                          |
| 错误计数器 (TEC/REC) 规则 | [[basic/can-multimaster-and-bus-off\|can-multimaster-and-bus-off]] "## 错误计数器 (TEC/REC) 规则" |
| Bus Off 怎么恢复          | [[basic/can-multimaster-and-bus-off\|can-multimaster-and-bus-off]] "## Bus Off 恢复机制"          |
| 节点状态机                | [[basic/can-multimaster-and-bus-off\|can-multimaster-and-bus-off]] "## 节点状态机"                |
| CAN FD 和经典 CAN 区别    | [[basic/can-fd-and-can-xl\|can-fd-and-can-xl]] "## CAN FD 关键改进"                               |
| CAN FD 收发器选型         | [[basic/can-fd-and-can-xl\|can-fd-and-can-xl]] "## CAN FD 物理层"                                 |
| 过滤器怎么配              | [[basic/can-deep-dive\|can-deep-dive]] "## CAN 过滤器"                                            |
| ID 怎么分配               | [[basic/can-multimaster-and-bus-off\|can-multimaster-and-bus-off]] "## 应用层优先级分配"          |
| 多 master 调度            | [[basic/can-multimaster-and-bus-off\|can-multimaster-and-bus-off]] "## 多 Master 调度的工程问题"  |
| SocketCAN 编程            | [[basic/can-rtos-integration\|can-rtos-integration]] "## Linux SocketCAN"                         |
| RTOS 集成模式             | [[basic/can-rtos-integration\|can-rtos-integration]] "## 三个 RTOS 的 CAN 抽象"                   |
| 产线死机案例              | [[basic/can-failure-cases\|can-failure-cases]]                                                    |
| 和 I2C 区别               | [[basic/can-vs-other-bus\|can-vs-other-bus]] "## CAN vs I2C"                                      |
| 和 SPI 区别               | [[basic/can-vs-other-bus\|can-vs-other-bus]] "## CAN vs SPI"                                      |
| 和 RS485 区别             | [[basic/can-vs-other-bus\|can-vs-other-bus]] "## CAN vs UART/RS485"                               |
| 和 Ethernet 区别          | [[basic/can-vs-other-bus\|can-vs-other-bus]] "## CAN vs Ethernet"                                 |
| CAN FD vs CAN XL 选型     | [[basic/can-fd-and-can-xl\|can-fd-and-can-xl]] "## CAN FD 选型决策"                               |

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

| 主题    | 篇数  | 大小       | 重点                                        |
| ------- | ----- | ---------- | ------------------------------------------- |
| **CAN** | **9** | **113 KB** | **实时多 master + 错误处理 + 演进 (FD/XL)** |
| I2C     | 11    | 151 KB     | 协议兼容性 + 总线恢复 (Recovery)            |
| SPI     | 6     | 75 KB      | 多从 / 菊花链 / 高速                        |
| UART    | 6     | 80 KB      | RS485 / 流控 / 异步日志                     |

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

| 文档                                                               | 更新频率          | 维护者          |
| ------------------------------------------------------------------ | ----------------- | --------------- |
| [[basic/can-practical\|can-practical]]                             | 改版才更新        | 速查 / 调试流程 |
| [[basic/can-deep-dive\|can-deep-dive]]                             | 改版才更新        | 原理体系        |
| [[basic/can-failure-cases\|can-failure-cases]]                     | **持续更新**      | 产线案例        |
| [[basic/can-multimaster-and-bus-off\|can-multimaster-and-bus-off]] | 改版才更新        | 仲裁 / 错误     |
| [[basic/can-fd-and-can-xl\|can-fd-and-can-xl]]                     | CAN XL 量产时     | 演进            |
| [[basic/can-rtos-integration\|can-rtos-integration]]               | RTOS 改版时       | RTOS 集成       |
| [[basic/can-vs-other-bus\|can-vs-other-bus]]                       | 新总线出现时      | 跨总线对比      |
| [[basic/can-index\|can-index.md]]                                  | 新增 / 删除文档时 | 导航            |

## 相关标准规范

CAN 涉及的标准横跨物理层到法规，完整总表见 **[[bus/automotive/can-standards-map|can-standards-map]]**。核心几项：

| 层       | 标准                                          | 作用                                            |
| -------- | --------------------------------------------- | ----------------------------------------------- |
| 数据链路 | **ISO 11898-1**                               | 核心标准，经典 CAN / CAN FD / CAN XL 三代帧格式 |
| 物理     | **ISO 11898-2**                               | 高速差分物理层、终端电阻、位时序电气特性        |
| 物理     | ISO 11898-6 / ISO 11898-3 / ISO 14950-2       | 低功耗 / 低速容错 / 单线变体                    |
| 一致性   | ISO 16845-1 / -2                              | 一致性测试方法学与测试计划                      |
| 传输     | ISO 15765-2                                   | ISO-TP（UDS 与 OBD 的公共底座）                 |
| 应用     | ISO 14229-1 ~ -7                              | UDS 总纲与各承载变体                            |
| 应用     | SAE J1979 / ISO 15031-5                       | OBD-II 排放诊断（乘用车）                       |
| 应用     | ISO 27145-1 ~ -4, -6                          | WWH-OBD（商用车全球统一诊断）                   |
| 应用     | CiA 301 / CiA 402 / CiA 1301                  | CANopen / 驱动 Profile / CANopen FD             |
| 应用     | SAE J1939-21 / -71 / -73 / -81                | J1939 数据链路 / 应用层 / 诊断 / 网络管理       |
| 环境     | ISO 16750-1 ~ -5                              | 环境条件与试验（电气/机械/气候/化学）           |
| EMC      | ISO 7637-2 / ISO 10605 / CISPR 25 / ISO 11452 | 瞬态 / ESD / 发射 / 辐射抗扰度                  |
| 安全     | ISO 26262 / ISO 21434 / UNECE R155-R156       | 功能安全 / 网络安全 / 软件更新合规              |

## 关联主题 (chips-com 其他目录)

- **[[bus/automotive/can-protocol-family|can-protocol-family]]** — CAN 家族协议全景（CAN/FD/XL/ISO-TP/CANopen/J1939/UDS/OBD-II）
- **[[bus/automotive/can-standards-map|can-standards-map]]** — CAN 家族标准规范总表（按层 + 按协议）
- **[[bus/automotive/canopen-deep-dive|canopen-deep-dive]]** — CANopen (CAN 之上的应用层协议)
- **[[bus/automotive/canopen-practical|canopen-practical]]** — CANopen 实战
- **[[bus/automotive/canopen-failure-cases|canopen-failure-cases]]** — CANopen 产线案例
- **[[bus/automotive/j1939-deep-dive|j1939-deep-dive]]** — J1939 (商用车, 基于 CAN)
- **[[bus/automotive/j1939-practical|j1939-practical]]** — J1939 实战
- **[[bus/automotive/uds-deep-dive|uds-deep-dive]]** — UDS (诊断, 基于 CAN)
- **[[bus/automotive/uds-practical|uds-practical]]** — UDS 实战
- **[[bus/automotive/uds-failure-cases|uds-failure-cases]]** — UDS 产线案例
- **[[bus/automotive/iso-tp-practical|iso-tp-practical]]** — ISO-TP (CAN 之上多帧传输)
- **[[bus/automotive/iso-tp-failure-cases|iso-tp-failure-cases]]** — ISO-TP 产线案例
- **[[bus/automotive/obd2|obd2]]** — OBD-II 排放诊断概览
- **[[bus/automotive/obd2-failure-cases|obd2-failure-cases]]** — OBD-II 案例
- **[[bus/industrial/rs485-modbus-rtu-deep-dive|rs485-modbus-rtu-deep-dive]]** — Modbus RTU (RS485)
- **[[bus/industrial/ethernet-ip-deep-dive|ethernet-ip-deep-dive]]** — EtherNet/IP (工业 Ethernet)
- **[[basic/can-phy|can-phy]]** — CAN 物理层基础
- **[[basic/i2c-vs-smbus-recovery|i2c-vs-smbus-recovery]]** — 跨协议对比参考
- **[[basic/i2c-bus-recovery-playbook|i2c-bus-recovery-playbook]]** — 总线恢复对比
- **[[basic/spi-failure-cases|spi-failure-cases]]** — 产线死机案例对比

## 一句话总结

CAN 是"可靠的实时多 master 现场总线", 强在错误检测、仲裁和实时性。从原理到产线案例, 9 篇笔记（含索引）覆盖完整。和 I2C / SPI / UART 的关系是"互补"而非"竞争"。

## 更新记录

- 2026-07-26: 初版, 8 篇笔记全部完成 (L4 闭环)
- 2026-10-31: 新增「相关标准规范」节; 修正 ISO-TP 实战文档坏链; 补充 CANopen / UDS / ISO-TP / OBD-II 的案例库链接。
- 2026-11-16: 统一计数口径, 修正为 9 篇（含索引）/ 113 KB, 并在主题地图补入 [[basic/can-phy|can-phy]]。
