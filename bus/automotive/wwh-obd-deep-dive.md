---
tags:
  - layer/bus
  - type/deep-dive
  - protocol/wwh-obd
  - topic/automotive
---

# WWH-OBD Deep Dive

## 目标

本文深入 WWH-OBD（ISO 27145）的数据模型、初始化流程、寻址体系、24 位 DTC 格式和 DoCAN / DoIP 双链路，回答这些问题：

- ISO 27145 各部分到底各自定义了什么，边界在哪。
- PID / MID / ITID 到 DID / RID 的映射为什么必须存在，怎么用。
- WWH-OBD 的 24 位 DTC 格式怎么来的，和 SAE J2012-DA、J1939 SPN/FMI 怎么对齐。
- ISO 27145-4 的初始化序列为什么要区分 11 位和 29 位 CAN ID。
- DoCAN 和 DoIP 两条链路怎么选、各自的报文长什么样。
- WWH-OBD 和 OBD-II 在同一辆商用车上怎么区分。

## 目标受众

- 做商用车（重卡、客车、工程机械）诊断设备、车队终端、检测线设备的人。
- 做 ECU 侧 WWH-OBD 服务实现（EMS / 后处理 / 变速箱）的人。
- 做排放检测站、年检站设备对接的人。
- 做商用车诊断工具链、DoIP 网关的人。

## ISO 27145 各部分的确切边界

这是最容易搞错的地方。先看权威标题和范围：

| Part | 权威标题 | 年份 / 状态 | 定义什么 |
| --- | --- | --- | --- |
| **ISO 27145-1** | General information and use case definition | 2012（2024 复审确认） | 系列结构、用例场景、术语 |
| **ISO 27145-2** | **Common data dictionary** | 2012（Amd 1:2023） | **所有法规数据元素**：DTC / DID / RID + PID/MID/ITID 映射 |
| **ISO 27145-3** | **Common message dictionary** | 2012（2024 复审确认） | **UDS 服务子集**（来自 ISO 14229-1）+ 公共消息集 |
| **ISO 27145-4** | Connection between vehicle and test equipment | 2016 | **协议初始化入口** + 全部 OSI 层要求 |
| **ISO 27145-6** | External test equipment | 2015 | 外部测试设备规范 |

> ⚠️ **ISO 27145-5 不存在**，系列是 1/2/3/4/6，跳过 5。

> ⚠️ 早期版本是 **ISO/PAS 27145-x:2006**，且 -2 的标题是 *"Common emissions-related data dictionary"*，-3 是 *"Common message dictionary"*。现行版把 -2 的 "emissions-related" 去掉，改成更通用的 "Common data dictionary"。

### 关键澄清：-2 管数据，-3 管服务，-4 管连接

这是三个最容易混淆的边界：

```text
ISO 27145-2  "Common data dictionary"
    → 定义「有哪些数据」：DTC / DID / RID
    → 定义「怎么映射」：PID / MID / ITID → DID / RID
    → 与传输层无关，纯数据字典

ISO 27145-3  "Common message dictionary"
    → 定义「怎么传」：ISO 14229-1 中 UDS 服务的子集
    → 公共消息集独立于 transport / network / data link / physical 层
    → 不规定车载网络架构

ISO 27145-4  "Connection between vehicle and test equipment"
    → 定义「怎么连」：初始化序列、寻址、时序、各 OSI 层要求
    → 是「协议初始化入口点」
```

一句话：**-2 是名词表，-3 是动词表，-4 是接头规程。**

### ISO 27145-2 的附录结构（做实现的必读）

ISO 27145-2 的附录本身就说明了工作量的分布：

| 附录 | 性质 | 内容 |
| --- | --- | --- |
| **Annex A** | 规范性 | DID（PID, MID, ITID）和 RID 支持定义 |
| **Annex B** | 规范性 | **WWH-OBD server/ECU 必须支持的 DID** |
| **Annex C** | 资料性 | GTR WWH-OBD 排放系统参数 |
| **Annex D** | 规范性 | GTR WWH-OBD **DTCExtendedDataRecord** 内容 |
| **Annex E** | 资料性 | 新 DID（PID, MID, ITID）**分配指南** |

> **工程含义**：Annex A 是**映射表本体**（PID→DID），Annex B 是**强制实现清单**。做 ECU 侧实现时，Annex B 决定了「至少必须支持哪些 DID」；Annex E 决定了「想新增一个自定义 DID 该怎么申请编号」。

## 数据模型：PID / MID / ITID → DID / RID

### 为什么需要映射

OBD-II 的 PID 是**面向参数**的（读 0x0C 就给转速），UDS 的 DID 是**面向数据字典**的（一个 DID 对应一个具名数据项，可能带子字节）。

商用车法规数据用 PID/MID/ITID 组织（继承 OBD-II 传统），但通过 UDS 服务传输，所以必须有映射表：

```text
法规视角（面向对象）              传输视角（面向服务）
─────────────────────         ─────────────────────
PID  0x0C  发动机转速    ──→   DID  0xF190  发动机转速
MID  0x65  O2 监测器    ──→   DID  0xF18x  监测器状态
ITID 0x01  标定 ID      ──→   RID  0x0201  执行标定例程
```

### 三个标识符族

| 标识符 | 全称 | 来源体系 | 读法 | 承载服务 |
| --- | --- | --- | --- | --- |
| **PID** | Parameter Identifier | OBD-II 传统 | 单字节，读实时参数 | ReadDataByIdentifier (0x22) |
| **MID** | Monitor Identifier | OBD-II 传统 | 单字节，读监测器状态 | ReadDataByIdentifier (0x22) |
| **ITID** | Information Type Identifier | OBD-II 传统 | 单字节，读信息类型 | ReadDataByIdentifier (0x22) |
| **DID** | Data Identifier | UDS (ISO 14229-1) | 双字节，读数据 | ReadDataByIdentifier (0x22) |
| **RID** | Routine Identifier | UDS (ISO 14229-1) | 双字节，跑例程 | RoutineControl (0x31) |

> **实现要点**：PID/MID/ITID 走的是 **0x22 ReadDataByIdentifier**，和 DID 共用同一个服务；RID 走 **0x31 RoutineControl**。所以「PID/MID/ITID → DID/RID」的映射实际上是「同一个 UDS 服务下的不同编号空间」，而不是两套协议。

### 映射查询的实际做法

映射表（Annex A）不在工具里时，实践中的三条路：

```text
1. 查 SAE 数字附录
   - SAE J1979-DA  → OBD 服务与 PID 定义
   - SAE J2012-DA  → DTC 定义
   - SAE J1939-DA  → J1939 的 SPN / PGN / DTC 定义

2. 反查车辆实际支持集
   - 读 Annex B 要求的「强制 DID 支持位图」
   - 工具侧维护 PID→DID 映射表文件（ODX / CDD 格式）

3. 从 OEM 的诊断数据库取
   - 量产工具链用 ODX（ISO 22901）/ CDD（ISO 22900）
```

### 强制 DID 支持集（Annex B）

Annex B 规定了 **WWH-OBD server/ECU 必须支持的 DID**。这是**合规基线**，与 OEM 自定义 DID 无关。

工程上意味着：**一台合规的商用车，不管什么品牌，都必须能回答 Annex B 列出的那批 DID**。工具侧应把这批 DID 硬编码为「必测项」。

## 24 位 DTC 格式（ISO 27145-2 §8）

这是 WWH-OBD 与乘用车 OBD-II 最实质的差别。OBD-II 是 2 字节 DTC，WWH-OBD 是 **3 字节**。

### 格式定义

ISO 27145-2 定义了 3 字节 DTC 格式，目的是向后兼容两套既有体系：

- **SAE J2012-DA** 定义的 DTC 格式
- **SAE J1939** Companion Spreadsheet 的 **SPN** 与 **SAE J1939-73:2010 Appendix A** 的 **FMI**

```text
ISO 27145-2 WWH-OBD DTC 格式（24 bit）

  bit23................bit16 | bit15................bit8 | bit7..........bit0
  ┌───────────────────────────┬────────────────────────┬───────────────┐
  │  BaseDTC number (16 bit)  │ FTB (8 bit)            │ 空闲/格式位   │
  └───────────────────────────┴────────────────────────┴───────────────┘
          高 16 位                    低 8 位
```

### 与 SAE J2012-DA 的映射

```text
SAE J2012-DA 定义 3 字节 DTC = 2 字节 BaseDTC + 1 字节 FTB
                     │
                     └──→ 直接落在 ISO 27145-2 的 24 bit 格式里
```

### 与 J1939 SPN / FMI 的映射

这是最巧妙的设计——J1939 的 SPN（Suspect Parameter Number）和 FMI（Failure Mode Identifier）加起来正好是 19 bit，能塞进 24 bit 格式：

```text
ISO 27145-2 24 bit DTC:
  ┌───────────────────────────────────────┬──────────────────────────┐
  │                                       │                          │
  │                                       │  SPN (19 bit)            │
  │                                       │  ├─ 高 8 位              │
  │                                       │  └─ 低 8 位              │
  │                                       │         ┌──────────────┐ │
  │                                       │         │ FMI (5 bit)  │ │
  │                                       │         └──────────────┘ │
  └───────────────────────────────────────┴──────────────────────────┘
```

**结果**：商用车诊断工具读到的同一个 DTC，可以**无损地**翻译回 J1939 的 SPN/FMI 或 SAE J2012-DA 的 BaseDTC/FTB。

> **这是 WWH-OBD 设计上最重要的一点**：它把「乘用车式 2 字节排放码」和「重卡式 SPN/FMI」统一到一个 24 bit 容器里，所以商用车诊断工具不需要为 OBD-II 和 J1939 写两套 DTC 解析器。

### DTCFormatIdentifier

DTC 格式由 **DTCFormatIdentifier**（在 ReadDTCInformation / ClearDiagnosticInformation 服务里指定）来标识。同一套 UDS 服务可以按不同格式读出不同编码的 DTC。

工程含义：**工具必须先协商 DTC 格式，再解析 DTC**，否则读到的是字节流而不是故障码。

### DTCExtendedDataRecord（Annex D）

规范性附录 D 定义了 **GTR WWH-OBD 的 DTCExtendedDataRecord 内容**——即 DTC 后面跟的扩展数据记录（快照、发生次数、状态字节等）。

```
DTC 响应结构:
  [DTC 格式标识] [DTC 数量] [DTC1 (3 byte)] [DTC1 的扩展数据记录] [DTC2 (3 byte)] ...
```

> 扩展数据记录的内容和长度**按 DTC 格式标识变化**，解析器必须按格式分支，不能硬编码长度。

## ISO 27145-4：初始化序列与寻址

### 初始化是「插件即用」的核心

ISO 27145-4 的核心诉求是 **plug and play**：测试设备插上就能识别车辆支持哪条链路、哪个协议、哪些服务。标准原文的表述是：基于初始化结果，测试设备判定车辆的排放相关系统支持哪种协议和诊断服务——

```text
- legislated OBD:      ISO 15031 (all parts)
- legislated WWH-OBD:  ISO 27145 (all parts)
```

**这一点极其重要**：同一条商用车诊断线，可能同时挂着 OBD-II 设备和 WWH-OBD 设备，工具必须能区分。

### 11 位与 29 位 CAN ID 验证程序

ISO 27145-4 §7.1 的结构：

```text
7  CAN based wired connection
  7.1 Initialization sequence
      7.1.1 External test equipment error detection provisions
      7.1.2 11 bit CAN identifier verification procedure
      7.1.3 29 bit CAN identifier verification procedure
```

这两个验证程序是**标准明确规定的初始化步骤**，不是可选优化。

### 为什么必须区分 11 位 / 29 位

商用车诊断的两种寻址：

| 维度 | 11 位标准帧 | 29 位扩展帧 |
| --- | --- | --- |
| CAN ID 范围 | 0x000 - 0x7FF | 0x80000000+ |
| 寻址方式 | 功能寻址（广播）+ 物理寻址 | 物理寻址为主 |
| 典型场景 | 短寻址、简单请求 | 长寻址、多 ECU、大数据量 |
| 覆盖 ECU 数 | 较少 | **7.5.3 规定最大 WWH-OBD ECU 数量** |

**验证程序的工程逻辑**：工具在初始化阶段逐个测试 11 位和 29 位寻址是否有效，据此决定后续用哪种帧格式。这不是「都试一遍哪个通用哪个」，而是**按标准流程走，判断车支持哪种**。

### 网络层参数（7.5）

```text
7.5 Network layer
    7.5.1 Addressing formats
    7.5.2 Data link layer interface
    7.5.3 Maximum number of WWH-OBD ECUs
    7.5.4 Functional addressing
    7.5.5 Physical addressing
    7.5.6 Network layer timing parameter values
    7.5.7 Definition of network layer parameter values
```

> **7.5.3 的「最大 WWH-OBD ECU 数量」是采购与测试设备容量规划的依据** —— 一个测试设备要支持多少个 ECU 节点，取决于标准允许的上限和目标车型的实际 ECU 布局。

### 时序参数

ISO 15765-4:2021（第 4 版）的重大技术变更之一是**统一所有时间参数为 `t_ParameterName` 格式**，并把 `P2_CAN_max` 更正为 `Δt_P2_CAN_Client_Max`。

已知的关键约束（来自 DoCAN 排放相关系统要求）：

```text
P2 (Server 首次响应)          ≈ 50 ms
P2* (需要 NRC 0x78 延长时)     ≈ 5000 ms
P2_CAN_Client_Max             客户端最大等待
```

> **工程含义**：客户端超时必须留出 `P2*` 的余量。工具若用 100 ms 超时，遇到需要 NRC 0x78 response pending 的 ECU 就会误判超时——这在商用车重负载 ECU 上很常见。

## 两条数据链路

### DoCAN

| 项 | 内容 |
| --- | --- |
| 标准 | ISO 15765-2（传输 / 网络层服务）+ ISO 15765-4（排放相关系统要求） |
| 版本 | ISO 15765-4:2021 为现行第 4 版 |
| 定位 | 从现有 CAN 诊断**平滑迁移**的入口 |
| 中国对应 | GB/T 39851 系列（GB/T 39851.3-2021 ≡ ISO 15765-4:2016, MOD） |

### DoIP

| 项 | 内容 |
| --- | --- |
| 标准 | ISO 13400（全部部分） |
| 版本 | ISO 13400-2:2019 现行；含 TLS 变体（独立端口） |
| 定位 | 以太网诊断，面向未来 |
| 端口 | UDP 13400（车辆识别 / 公告）+ TCP 13400（诊断消息） |

### DoIP 报文结构

所有 DoIP 消息共用 8 字节通用头：

```text
byte0: protocol version (0x02)
byte1: inverse protocol version (0xFD)
byte2-3: payload type
byte4-7: payload length
```

关键 payload type：

| Payload Type | 名称 | 方向 |
| --- | --- | --- |
| 0x0001 | Vehicle identification request | 测 → 车（UDP） |
| 0x0004 | Vehicle announcement | 车 → 测（UDP，广播） |
| 0x0005 | Routing activation request | 测 → 车 |
| 0x0006 | Routing activation response | 车 → 测 |
| 0x8001 | Diagnostic message | 测 → 车 |
| 0x8002 | Diagnostic message positive acknowledge | 车 → 测 |
| 0x8003 | Diagnostic message negative acknowledge | 车 → 测 |

路由激活请求示例：

```text
02 FD 00 05 00 00 00 07 0E 00 00 00 00 00 00
│  │  │     │     └──┬─┘
│  │  │     │        └─ 源地址 0x0E00
│  │  │     └────────── 长度 7
│  │  └──────────────── payload type 0x0005
│  └─────────────────── 反向版本 0xFD
└────────────────────── 版本 0x02
```

路由激活成功（响应码 0x10）后，才能发诊断消息：

```text
02 FD 80 01 00 00 00 07 0E 00 10 01 22 F1 90
                              └──┬─┘
                                 └─ 0x22 ReadDataByIdentifier, DID 0xF190 (VIN)
```

### DoIP 与 DoCAN 的对比

| 维度 | DoCAN | DoIP |
| --- | --- | --- |
| 物理层 | CAN（ISO 11898-1/-2） | 100BASE-TX 以太网（ISO 13400-4） |
| 传输 | CAN + ISO-TP 分帧 | TCP（自带分帧/排序） |
| 寻址 | CAN ID | **逻辑地址**（0x1001 等） |
| 发现机制 | 无（固定 ID） | UDP 广播车辆识别 |
| 连接建立 | 无连接 | 需 **routing activation** |
| 带宽 | 500 kbps | 100 Mbit/s |
| 安全 | 无内建 | 无内建（TLS 变体在额外端口） |

> **安全提醒**：DoIP 默认**没有**认证和加密。路由激活成功不等于认证通过，除非 OEM 额外实现 activation type 0xE0 检查或启用 TLS。同时保护 CAN 上的 ECU 并不能防止 DoIP 网关把它转发出去。

## 与 OBD-II 的关系

**并列体系，不是升级关系**。同一辆商用车上可以并存。

| 维度 | OBD-II | WWH-OBD |
| --- | --- | --- |
| 标准 | SAE J1979 / ISO 15031-5 | ISO 27145 系列 |
| 法规 | 各地排放法规 | GTR No. 5 |
| 适用 | 乘用车 | 商用车 / 中重型车 |
| 服务模型 | Mode 01-09（固定模式） | UDS 子集 |
| DTC | 2 字节 | **3 字节（24 bit）** |
| 标识 | PID / MID / ITID | DID / RID + PID/MID/ITID 映射 |
| 承载 | ISO 15765-4 | DoCAN + DoIP |
| 寻址 | 11 位为主 | 11 位 + 29 位，标准定义验证程序 |

### 如何判断一辆车走哪套体系

初始化阶段按 ISO 27145-4 判定：

```text
1. 尝试 11 位 CAN ID 验证程序
2. 尝试 29 位 CAN ID 验证程序
3. 尝试 DoIP 车辆识别（UDP 13400）
4. 依据结果判定:
     - 支持 ISO 15031 的 Mode 服务  → OBD-II
     - 支持 ISO 27145 的 UDS 子集   → WWH-OBD
```

> **注意**：ISO 27145-3 的公共消息集「包含支持 SAE J1979-DA 和 SAE J2012-DA WWH-OBD 数据集的规定」——意味着 WWH-OBD 体系本身就能承载 OBD-II 的数据集，这是标准层面「全球统一」的设计意图。

## 与 J1939 的关系

WWH-OBD **大量引用 SAE J1939**：

| 引用 | 用途 |
| --- | --- |
| **SAE J1939** | 重型车网络顶层文档 |
| **SAE J1939-73** | 应用层——诊断（DM / DM1 / DM2） |
| **SAE J1939-03** | OBD 实施指南 |
| **SAE J1939-DA** | J1939 数字附录 |
| **SAE J1930-DA** | 诊断术语与缩写 |

具体的映射已经在 24 位 DTC 格式里体现：**SPN + FMI → WWH-OBD 24 bit DTC**。

```text
J1939 侧                          WWH-OBD 侧
─────────────────────          ─────────────────────
SPN (19 bit) + FMI (5 bit)  →  DTC (24 bit)
PGN                     →  寻址 / 网络层
DM1 / DM2               →  DTC 状态（pending / confirmed / permanent）
```

> **工程判断**：做商用车 OBD，**J1939 是绕不开的地基**。WWH-OBD 负责「法规诊断怎么走」，J1939 负责「车上的数据怎么组织」。

## 实现要点

### ECU 侧：UDS 服务子集

WWH-OBD ECU 实现的是 UDS 服务子集，而不是自定义协议：

```c
/* WWH-OBD ECU 侧：按 ISO 27145-3 支持的 UDS 服务分派 */
int wwh_handle(const uint8_t *req, uint8_t *resp, size_t *len)
{
    uint8_t sid = req[0];

    switch (sid) {
        /* --- ISO 27145-3 的公共消息集 --- */
        case 0x10: return uds_diagnostic_session_control(req, resp, len);
        case 0x14: return uds_clear_diagnostic_information(req, resp, len);
        case 0x19: return uds_read_dtc_information(req, resp, len);
        case 0x22: return uds_read_data_by_identifier(req, resp, len);
        case 0x31: return uds_routine_control(req, resp, len);

        /* --- 不支持的 SID：必须回 NRC 0x11 --- */
        default:
            resp[0] = 0x7F;
            resp[1] = sid;
            resp[2] = 0x11;   /* serviceNotSupported */
            *len = 3;
            return 0;
    }
}
```

> **与 OBD-II 的显著差异**：OBD-II 对不支持的 Mode 通常**静默不响应**；UDS（含 WWH-OBD）必须回 **NRC 0x11**。这个差别在做工具时经常被搞反。

### 强制 DID 的实现

Annex B 列出的 DID 是**合规基线**：

```c
/* 合规基线: 这些 DID 必须支持, 缺一个即不合规 */
static const uint16_t wwh_mandatory_dids[] = {
    /* Annex B 具体清单以 ISO 27145-2:2012 表 B.1 为准 */
    0xF190,  /* VIN */
    0xF18A,  /* 标定软件 ID */
    0xF18B,  /* 标定零件号 */
    0xF18C,  /* ECU 硬件零件号 */
    0xF18D,  /* ECU 软件零件号 */
    /* ... 以标准表为准 */
};

/* 支持位图: 用于 Annex A 的 DID 支持声明 */
static uint8_t wwh_did_support_bitmap[32];
```

### 24 位 DTC 存储与输出

```c
/* WWH-OBD 内部存 24 bit DTC */
typedef uint32_t wwh_dtc_t;

/* SPN(19) + FMI(5) → 24 bit DTC */
static inline wwh_dtc_t dtc_from_spn_fmi(uint32_t spn, uint8_t fmi)
{
    /* SPN 低 8 位 | FMI 5 位 | SPN 高 11 位 */
    return (spn & 0xFFu)
         | ((uint32_t)(fmi & 0x1Fu) << 8)
         | ((spn >> 8) << 13);
}

/* 反解, 供 J1939 工具使用 */
static inline void dtc_to_spn_fmi(wwh_dtc_t dtc, uint32_t *spn, uint8_t *fmi)
{
    *spn = (dtc & 0xFFu) | ((dtc >> 13) << 8);
    *fmi = (dtc >> 8) & 0x1Fu;
}
```

> 编码是**格式约定**，落地前必须用标准 Figure 5 的位域对照表复核——本例仅表达「SPN/FMI 能无损装进 24 bit」这一事实。

### 法规数据元素可扩展性

标准明确：若新增 WWH-OBD GTR 模块，ISO 27145 适用性可**带扩展地实现**，扩展可以：

- 写进 **ISO 27145-2** 本身
- 作为 **SAE Digital Annex** 的增强
- 或作为其他引用文档的一部分

> **工程含义**：GTR No. 5 会持续增补模块。实现时应把「GTR 模块」与「通信栈」解耦——通信栈按 ISO 27145-3/-4 做，数据字典按 SAE 数字附录版本走。Annex E 给出了新 DID（PID/MID/ITID）的分配指南，是提请编号申请的依据。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 初始化阶段就没响应 | 11/29 位验证程序走没走、波特率、ECU 上电条件 |
| 只支持 29 位，11 位不通 | 车型要求长寻址；工具寻址格式配置 |
| DoIP 路由激活失败（响应码 0x03） | OEM activation type 未使能 |
| 读 DTC 拿到 3 字节但解不出 SPN | DTCFormatIdentifier 没协商，或按 2 字节 OBD-II 格式解析 |
| PID 读不到但 DID 能读 | 映射表没做，或 DID 命名空间不对 |
| P2 超时误判 | 客户端超时没留 NRC 0x78 的 P2* 余量 |
| DoCAN 通 DoIP 不通 | 车辆无以太网诊断口 / 网关未开 DoIP / UDP 13400 被防火墙拦 |
| 同一车两种工具读出不同 DTC | 一套按 2 字节、一套按 3 字节解析；或 DTC 格式标识不同 |

## 相关规范详解

| 标准 | 覆盖 | 关键点 |
| --- | --- | --- |
| **ISO 27145-1** | 总则 | 系列结构、用例定义、术语 |
| **ISO 27145-2** | 数据 | **DTC/DID/RID 定义 + PID/MID/ITID 映射 + 24 bit DTC 格式 + Annex A-E**。实现时的数据字典主要看这本 |
| **ISO 27145-3** | 消息 | **UDS 服务子集**（ISO 14229-1）+ 公共消息集。与传输层无关 |
| **ISO 27145-4** | 连接 | **初始化入口**：11/29 位验证、寻址、时序、最大 ECU 数、各 OSI 层 |
| **ISO 27145-6** | 测试设备 | 外部测试设备规范 |
| **ISO 14229-1 / -2** | UDS | 应用层 / 会话层。-3 的服务来源，-2 的会话层被直接引用 |
| **ISO 15765-2 / -4** | DoCAN | 传输网络层 / 排放相关系统要求（2021 第 4 版） |
| **ISO 13400-2 / -3 / -4** | DoIP | 传输网络层 / 激活线 / 硬件（100BASE-TX） |
| **ISO 11898-1 / -2** | CAN | 数据链路 / 物理 |
| **SAE J1979-DA** | OBD 数据集 | OBD 服务与 PID 定义，被 -3 引用 |
| **SAE J2012-DA** | DTC 定义 | DTC 格式规则，被 -2 引用 |
| **SAE J1939 / -73 / -03 / -DA** | J1939 | 商用车网络与诊断 |
| **ISO 22900 / ISO 22901** | 数据交换 | MVCI / ODX，工具与 ECU 数据库 |
| **ISO 16750-2 / -3 / -4** | 环境 | 电气负荷 / 机械负荷 / 气候 |
| **ISO 7637-2 / ISO 10605 / CISPR 25** | 环境 | 瞬态干扰 / ESD / 车载发射 |
| **ISO 21434 / ISO 26262** | 安全 | 网络安全 / 功能安全（诊断覆盖率） |

> **版本提示**：本文以 ISO 官网与各标准销售页当前版本为准（ISO 27145-1/-2/-3 为 2012 版、2024 复审确认；-4 为 2016；-6 为 2015；ISO 15765-4 为 2021 第 4 版；ISO 13400-2 为 2019）。落地前请核对最新版本号与年份。

## 延伸阅读

- `bus/automotive/wwh-obd.md` — WWH-OBD 专篇（标准分工 / 分层结构 / 三方对比）
- `bus/automotive/wwh-obd-practical.md` — 工具链、初始化流程、DoIP 实操、检查清单
- `bus/automotive/wwh-obd-failure-cases.md` — 故障案例
- `bus/automotive/obd2.md` — 乘用车 OBD-II 概览（对照）
- `bus/automotive/uds.md` / `bus/automotive/uds-deep-dive.md` — UDS 服务与会话（WWH-OBD 的服务底座）
- `bus/automotive/iso-tp.md` — ISO-TP（DoCAN 的传输层）
- `bus/automotive/j1939-index.md` — J1939 导航（商用车网络地基）
- `bus/automotive/j1939-protocol-spec.md` — J1939 协议规范层（PGN/SPN/DTC 字段）
- `bus/automotive/can-standards-map.md` — CAN 家族标准规范总表
- `bus/automotive/can-protocol-family.md` — CAN 家族全景
