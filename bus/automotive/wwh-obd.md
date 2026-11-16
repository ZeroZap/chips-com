# WWH-OBD（ISO 27145 商用车全球统一车载诊断）

> **W**orld-**W**ide **H**armonized **O**n-**B**oard Diagnostics —— 商用车（重型车 / 中重型车）的全球统一车载诊断体系，由 **GTR No. 5**（全球技术法规第 5 号）驱动，通信规范落在 **ISO 27145** 系列。
>
> 与乘用车 OBD-II（SAE J1979 / ISO 15031）是**并列体系**，不是升级关系。

## 标准定位

| 项 | 内容 |
| --- | --- |
| 系列总称 | **ISO 27145** — *Road vehicles — Implementation of World-Wide Harmonized On-Board Diagnostics (WWH-OBD) communication requirements* |
| 法规驱动 | **GTR No. 5**（Global technical regulation No. 5），WWH-OBD 全球技术法规 |
| 主管委员会 | ISO/TC 22（道路车辆）/ SC 31 |
| 适用范围 | 商用车（货车、客车、牵引车、工程机械等），**乘用车用 OBD-II** |
| 目标 | 成为访问 VOBD（Vehicle On-Board Diagnostics）信息的**单一通信标准** |

### 各部分标题（权威版本）

| Part | 标题 | 年份 |
| --- | --- | --- |
| **ISO 27145-1** | General information and use case definition | 2012 |
| **ISO 27145-2** | **Common data dictionary** | 2012（Amd 1:2023） |
| **ISO 27145-3** | **Common message dictionary** | 2012（2024 复审确认仍现行） |
| **ISO 27145-4** | Connection between vehicle and test equipment | 2016 |
| **ISO 27145-6** | **External test equipment** | 2015 |

> ⚠️ **常见错误**：**ISO 27145-5 不存在**。系列是 1/2/3/4/6，**跳过 5**。
>
> ⚠️ 早期版本（ISO/PAS 27145-x:2006）用的是 *"Common emissions-related data dictionary"*（-2）和 *"Common message dictionary"*（-3），现行版把 -2 的 "emissions-related" 去掉了，改成更通用的 "Common data dictionary"。

## 分层结构与承载

WWH-OBD **不是独立协议**，而是站在 UDS + ISO-TP 之上的一层「法规数据字典 + 服务子集」。

```
┌──────────────────────────────────────────────┐
│  GTR No. 5（全球技术法规）                     │  ← 规定「要测什么」
├──────────────────────────────────────────────┤
│  ISO 27145-2  通用数据字典                     │  ← DTC / DID / RID 定义
│               PID / MID / ITID 映射            │
├──────────────────────────────────────────────┤
│  ISO 27145-3  通用消息字典                     │  ← UDS 服务子集
├──────────────────────────────────────────────┤
│  ISO 27145-4  车辆↔测试设备连接（协议入口）      │  ← 初始化序列 / OSI 各层
├──────────────────────────────────────────────┤
│  ISO 14229-2  UDS 会话层                       │
├──────────────────────────────────────────────┤
│  两条数据链路（并列）：                          │
│   ① DoCAN   ISO 15765-2（传输/网络）+ ISO 15765-4 │
│   ② DoIP    ISO 13400（全部部分）                │
├──────────────────────────────────────────────┤
│  ISO 11898-1 / -2   CAN 数据链路 / 物理          │
└──────────────────────────────────────────────┘
```

### 两条数据链路

| 链路 | 标准 | 说明 |
| --- | --- | --- |
| **DoCAN** | ISO 15765-2（传输/网络层）+ **ISO 15765-4**（排放相关系统要求） | 现有 CAN 诊断，迁移入口 |
| **DoIP** | ISO 13400（全部部分） | 以太网诊断，面向未来 |

> **关键点**：ISO 27145-4 定义的通信概念**同时基于这两条链路**。测试设备需要「即插即用」（plug and play）地识别车辆支持哪条链路。

### 迁移路径（标准原文表述）

```
现状（乘用车）                  目标（全球统一）
─────────────────────────────────────────────────
ISO 15031 系列（法定 OBD）  →   ISO 27145 系列（法定 WWH-OBD）
  基于 DoCAN                    基于 DoCAN + DoIP
```

标准明确指出：为了从现有通信标准**平滑迁移**到未来全球统一标准，初始通信概念基于 **ISO 15765 系列（DoCAN）**；未来将基于 **ISO 13400 系列（DoIP）**。

> 因为用了标准网络层协议，**未来可以扩展到可选物理层（如无线）** —— 这是标准预留的扩展点。

## 各部分职责

| Part | 管什么 | 对应 OSI 层 |
| --- | --- | --- |
| **-1** | 系列结构与分区、各部分关系、用例场景、通用术语 | — |
| **-2** | 所有**法规数据元素**：DTC / DID / RID 定义；**PID / MID / ITID 映射** | 表示层 |
| **-3** | **统一诊断服务（UDS）子集**（来自 ISO 14229-1）；公共消息集 | 应用层 |
| **-4** | 协议**初始化入口**：建立/维持/终止通信；所有 OSI 层要求 | 全 OSI 层 |
| **-6** | **外部测试设备**规范 | — |

### ISO 27145-4 的章节结构（来自标准目录）

```
6  Vehicle and external test equipment connection requirements
7  CAN based wired connection
   7.1 Initialization sequence
       7.1.1 External test equipment error detection provisions
       7.1.2 11 bit CAN identifier verification procedure
       7.1.3 29 bit CAN identifier verification procedure
   7.2 Application layer
       7.2.1 Diagnostic protocol communication types
       7.2.2 Diagnostic protocol timing parameters
       7.2.3 Timing performance requirements
   7.3 Presentation layer
   7.4 Session layer
   7.5 Network layer
       7.5.1 Addressing formats
       7.5.2 Data link layer interface
       7.5.3 Maximum number of WWH-OBD ECUs
       7.5.4 Functional addressing
       7.5.5 Physical addressing
       7.5.6 Network layer timing parameter values
       7.5.7 Definition of network layer parameter values
   7.6 Data link layer
   7.7 Physical layer
       7.7.1 Diagnostic connector
       7.7.2 External test equipment baud-rates
       7.7.3 External test equipment CAN bit timing
```

> **工程价值**：7.1.2 / 7.1.3 的 **11 bit / 29 bit CAN ID 验证流程**是标准明确规定的初始化步骤 —— 很多自制扫描工具栽在这。7.5.3 规定了**最大 WWH-OBD ECU 数量**，7.5.4/7.5.5 定义了功能寻址与物理寻址格式。

## 关键标识符体系

WWH-OBD 有一套**独立的标识符空间**，与乘用车 OBD-II 的 PID 空间不是一回事。

| 标识符 | 全称 | 含义 |
| --- | --- | --- |
| **DID** | Data Identifier | 数据标识符（ISO 14229-1 体系） |
| **RID** | Routine Identifier | 例程标识符（ISO 14229-1 体系） |
| **DTC** | Diagnostic Trouble Code | 诊断故障码（引用 **SAE J2012-DA**） |
| **PID** | Parameter Identifier | 参数标识符（**乘用车 OBD-II 概念**） |
| **MID** | Monitor Identifier | 监测器标识符（OBD-II 概念） |
| **ITID** | Information Type Identifier | 信息类型标识符（OBD-II 概念） |

**ISO 27145-2 的核心工作**就是做 **PID / MID / ITID → DID / RID / DTC** 的映射表。

> **为什么要映射**：OBD-II 的 PID 是「面向参数」的（读 0x0C 就给转速），UDS 的 DID 是「面向数据字典」的。商用车法规数据用 PID/MID/ITID 组织（继承 OBD-II 传统），但通过 UDS 服务传输，所以必须有映射表。

## 与 J1939 的关系

WWH-OBD 体系**大量引用 SAE J1939**：

| 引用 | 用途 |
| --- | --- |
| **SAE J1939** | 重型车网络顶层文档（SG / BO / SP / PG / BAM 等基础概念） |
| **SAE J1939-73** | 应用层——诊断（DM / DM1 / DM2） |
| **SAE J1939-03** | OBD 实施指南 |
| **SAE J1939-DA** | J1939 数字附录（Digital Annex） |
| **SAE J1930-DA** | 电气/电子系统诊断术语与缩写 |

> **工程判断**：做商用车 OBD，**J1939 是绕不开的地基**——WWH-OBD 的数据模型大量复用 J1939 的 PGN/SPN 体系。ISO 27145-4 和 -2 的交叉引用里，J1939-DA 和 J1979-DA 并列出现。
>
> 本库已有 J1939 完整主题（7 篇 / 21 例），配合本文使用。

## 三方对比：OBD-II / WWH-OBD / UDS

| 维度 | OBD-II（乘用车） | WWH-OBD（商用车） | UDS（通用诊断） |
| --- | --- | --- | --- |
| 标准 | SAE J1979 / ISO 15031-5 | ISO 27145 系列 | ISO 14229-1~-7 |
| 法规 | 各地排放法规 | **GTR No. 5** | 无（行业通用） |
| 适用 | 乘用车（≤3.5t） | 商用车 / 中重型车 | 所有车型 OEM 售后 |
| 服务模型 | Mode 01-09（固定模式） | UDS **子集** | 完整 SID 集合 |
| 数据标识 | PID / MID | DID / RID / DTC + PID/MID/ITID 映射 | DID / RID |
| 承载 | ISO 15765-4 | DoCAN（ISO 15765-4）+ DoIP（ISO 13400） | DoCAN / DoIP / DoK-Line / DoFR |
| 传输层 | 已内含 | ISO 15765-2 | 由承载决定 |

**关系要点**：

- **OBD-II 与 WWH-OBD 是并列的法规体系**，不是代际关系
- **UDS 是基础协议**，OBD-II 和 WWH-OBD 都在其上（OBD-II 用固定的 Mode 映射，WWH-OBD 用 UDS 子集）
- **WWH-OBD 的数据模型大量复用 J1939**（PGN/SPN/DM）

```
        SAE J1979 / ISO 15031-5        ISO 27145 系列
              OBD-II                       WWH-OBD
                │                             │
         固定 Mode 服务                  UDS 服务子集
                │                             │
                └──────────┬──────────────────┘
                           │
                    ISO 14229-1 (UDS)
                           │
              ┌────────────┼────────────┐
          ISO 15765-4   ISO 13400    ISO 14229-4
             (DoCAN)      (DoIP)       (DoFR)
```

## 实现要点

### 法规数据元素可扩展性

标准明确：若新增 WWH-OBD GTR 模块，ISO 27145 适用性可**带扩展地实现**，扩展可以：
- 写进 ISO 27145-2 本身
- 作为 **SAE Digital Annex**（数字附录）的增强
- 或作为其他引用文档的一部分

> **工程含义**：GTR No. 5 会持续增补模块。实现时应把「GTR 模块」与「通信栈」解耦——通信栈按 ISO 27145-3/-4 做，数据字典按 SAE 数字附录版本走。

### 测试设备侧

- ISO 27145-6 单独规范**外部测试设备**
- 初始化流程需支持 **11 bit 与 29 bit CAN ID 两种**的验证程序
- 需实现**即插即用**的链路协商（DoCAN 还是 DoIP）

## 与库内已有内容的衔接

| 本库文档 | 关系 |
| --- | --- |
| `bus/automotive/obd2.md` | 乘用车 OBD-II 概览（九 Mode / PID 速查 / DTC 格式） |
| `bus/automotive/obd2-deep-dive.md` | OBD-II 深入（PID 协商 / I-M 监测模型） |
| `bus/automotive/obd2-practical.md` | ELM327 / SocketCAN 实操 |
| `bus/automotive/obd2-failure-cases.md` | OBD-II 产线案例（12 例） |
| `bus/automotive/wwh-obd-deep-dive.md` | WWH-OBD 深入（各部分边界 / PID→DID 映射 / 24 位 DTC / 初始化 / DoIP 协议） |
| `bus/automotive/wwh-obd-practical.md` | WWH-OBD 实战（初始化脚本 / 路由激活 / 24 位 DTC 解析） |
| `bus/automotive/wwh-obd-failure-cases.md` | WWH-OBD 案例（12 例） |
| `bus/automotive/uds.md` / `bus/automotive/uds-practical.md` | UDS 会话 / DID / 安全访问 / 刷写 |
| `bus/automotive/iso-tp.md` | DoCAN 的传输层（ISO 15765-2） |
| `bus/automotive/j1939-index.md` | 商用车网络地基（PGN/SPN / DM） |
| `bus/automotive/can-standards-map.md` | ISO 27145 系列在标准总表中的位置 |

## 相关标准

| 标准 | 关系 |
| --- | --- |
| **GTR No. 5** | WWH-OBD 全球技术法规（上位） |
| **ISO 27145-1~-4, -6** | 本标准系列 |
| **ISO 14229-1 / -2** | UDS 应用层 / 会话层 |
| **ISO 15765-2 / -4** | DoCAN 传输网络层 / 排放相关系统 |
| **ISO 13400-1~-4** | DoIP |
| **ISO 11898-1 / -2** | CAN 数据链路 / 物理 |
| **SAE J1939 / -73 / -03 / -DA** | 商用车网络与诊断 |
| **SAE J1979-DA / J2012-DA** | 数字附录（OBD 服务 / DTC 定义） |
| **SAE J1930-DA** | 诊断术语 |
| **ISO 22900 / ISO 22901** | MVCI / ODX 数据交换格式 |

> **标准版本提示**：标准版本会持续更新与修订，本文以 ISO 官网与各标准销售页当前版本为准；落地前请核对最新版本号与年份。
