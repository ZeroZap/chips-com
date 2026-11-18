---
tags:
  - layer/bus
  - type/overview
  - protocol/obd2
  - topic/automotive
---

# OBD-II 车载排放诊断协议

## 定位

OBD-II（On-Board Diagnostics, Second Generation）是全球统一的车辆排放检测标准。

它的特点是**强制性 + 最小化**：法规只规定"必须能读哪些数据"，不规定"怎么实现"。这和 CANopen / UDS 的自由度完全不同。

## 分层关系

```text
OBD-II (Mode 01-09, PID 空间)
        |
        +-- 通常承载于 ISO-TP (多帧时)
        |
CAN 2.0A / CAN FD 帧
        |
CAN PHY
```

OBD-II 和 UDS 的关系：

| 维度 | OBD-II | UDS |
| --- | --- | --- |
| 标准 | SAE J1979 / ISO 15031-5 | ISO 14229 |
| 目的 | 排放检测、强制法规 | 整车厂诊断、售后 |
| 适用 | 所有量产车，全球统一 | OEM 自定义 |
| 数据模型 | 固定 PID 编号 | DID 自由定义 |
| 会话/权限 | 无 | 有 |
| 传输 | ISO-TP | ISO-TP / DoIP |
| 谁定义 | 法规 | 整车厂 |

关键区别：**OBD-II 是"只读为主"的最小诊断集**，不需要进会话、不需要种子密钥。UDS 才是完整诊断体系。

### 为什么写作 "SAE J1979 / ISO 15031-5"

这一行看着像"两个标准并列"，其实是**同一份技术内容的两种发布形态**。

**SAE 的官方表述**（SAE J1979_200705 引言）：

> *"The prior version of SAE J1979 was technically equivalent to a draft version of ISO 15031-5. The ISO document was subsequently edited and published as an International Standard, including minor editorial changes. This version of SAE J1979 includes all of the editorial changes that were included in the published version of the ISO document."*

翻译成工程语言：

```text
1. 先有 ISO 15031-5 的草案（DIS）
2. SAE 把同一份技术内容作为美国标准 J1979 发布，标题写明
   "Equivalent to ISO/DIS 15031-5"
3. ISO 定稿后只做编辑性修改，SAE 再版一次，把编辑改动吸收进来
4. 之后两者平行维护，内容"技术上等同"
```

所以两个编号指向**同一套 Mode 01-09 服务定义**，区别只在发布机构、读者和法规引用场合：

| | SAE J1979 | ISO 15031-5 |
| --- | --- | --- |
| 发布方 | SAE International（美国） | ISO（国际） |
| 引用场合 | EPA / CARB 法规文件、SAE 体系 | 欧盟 / 中国 / 其他地区法规 |
| 同步方式 | SAE 与 ISO 联合出版（WG 平行），内容同步 | 同左 |

> **工程含义**：实现 OBD-II 时，**照哪本做都行**，但要意识到它们是同步维护的同一份规范；遇到细节差异时，回到本地区法规引用的那一份。

### ISO 15031 系列的分工

OBD-II 不是一个标准，是一整族。**核心是 Part 5**：

| Part | 标题 | 作用 |
| --- | --- | --- |
| ISO 15031-1 | General information and use case definition | 总则与用例 |
| ISO 15031-2 | Terms, definitions, abbreviations and acronyms | 术语（对应 SAE J1930-DA） |
| ISO 15031-3 | Diagnostic connector and related electrical circuits | 16 针 J1962 连接器（对应 SAE J1962） |
| ISO 15031-4 | External test equipment | 外部测试设备（扫描仪）规范 |
| **ISO 15031-5** | **Emissions-related diagnostic services** | **核心：Mode 01-09、PID 空间、服务定义** |
| ISO 15031-6 | Emissions-related diagnostic trouble code definitions | 故障码定义（引用 SAE J2012-DA） |
| ISO 15031-7 | Data link security | 数据链路安全 |

现行版：**ISO 15031-5:2015**（第 3 版，2026-10 复审确认仍现行）。

> **中国对应**：GB/T 42193 系列（等同采用 ISO 15031），如 GB/T 42193.5-2026 ≡ ISO 15031-5:2015。

### 与 ISO 15765-4 / ISO 9141-2 / ISO 14230-4 的关系：应用层 vs 承载

这三者不是同一层的竞争标准，而是**「同一套 OBD 服务，跑在不同承载上」**。

**先看 SAE J1979_202505 / ISO 15031-5 的 Table 1**（OSI 七层映射）——这是标准自己画的图：

| OSI 层 | DoCAN 路径 | DoK-Line 路径 | 遗留串行路径 |
| --- | --- | --- | --- |
| **7 应用层** | ISO 15031-5 / SAE J1979 | ISO 15031-5 / SAE J1979 | ISO 15031-5 / SAE J1979 |
| **6 表示层** | ISO 15031-2、ISO 15031-5、ISO 15031-6 + SAE J1930-DA / J1979-DA / J2012-DA | 同左 | 同左 |
| **5 会话层** | **ISO 14229-2**（支持 DoCAN） | **ISO 14229-2**（支持 DoK-Line） | **不适用** |
| **4 传输层** | ISO 15765-2 | ISO 14230-4 + ISO 15031-5 | ISO 15031-5 / SAE J1979 |
| **3 网络层** | ISO 15765-2 | ISO 14230-4 + ISO 15031-5 | ISO 15031-5 / SAE J1979 |
| **2 数据链路层** | ISO 15765-4、ISO 11898-1/-2 | ISO 14230-2 | SAE J1850 / ISO 9141-2 |
| **1 物理层** | ISO 15765-4、ISO 11898-1/-2 | ISO 14230-1 | SAE J1850 / ISO 9141-2 |

**一句话概括**：

```text
ISO 15031-5 / SAE J1979  =  应用层（Mode 01-09 的服务定义）
ISO 15765-4              =  DoCAN 承载（CAN 上的 ISO-TP + 诊断要求）
ISO 14230-4              =  DoK-Line 承载（KWP2000 在 K 线上的排放相关要求）
ISO 9141-2               =  遗留 K 线承载（老式单线串行）

关系: 同一套 OBD 服务  ×  四种可选承载
```

> **不是「OBD-II 建立在 CAN 上」**，而是「OBD-II **可以**跑在 CAN 上」。ISO 15031-5 是**独立于物理层的服务定义**，这是它能把同一套 Mode 01-09 铺到五种物理协议上的前提。

### 关键规则：ISO 15031-5 覆盖并取代承载标准的部分条款

ISO 15031-5 的范围声明里有一句关键的话：

> *"Each clause in ISO 15031-5 which specifies additional details to existing clauses of **ISO 9141-2, ISO 14230-4, SAE J1850, and ISO 15765-4 supersede those specifications**."*

中文标准 GB/T 42193.5-2026 的对应表述：

> *"本文件规定了 **ISO 9141-2、ISO 14230-4、SAE J1850 和 ISO 15765-4 现行条款的额外要求，并替代现行条款**。"*

**工程含义**：做 OBD-II 时，**同一层出现冲突，以 ISO 15031-5 为准**。

```text
ISO 15765-4  说 CAN 上怎么做 OBD          ┐
ISO 14230-4  说 K 线上怎么做 OBD          ├─→ 冲突时 ISO 15031-5 优先
ISO 9141-2   说老式 K 线怎么做 OBD         ┘
```

这也是为什么**读 ISO 15031-5 正文 + 对应承载标准**才能完整实现，而不能只读其中一本。

### 会话层为什么只有 CAN 和 K 线有

上表第 5 层有个容易漏的细节：

```text
ISO 14229-2 支持 ISO 15765-4 DoCAN 和 ISO 14230-4 DoK-Line
ISO 14229-2 不适用于 SAE J1850 和 ISO 9141-2
```

原因：OBD-II 本身**没有会话概念**（不需要 0x10 诊断会话切换）。ISO 14229-2 是 UDS 的会话层，被**借用**到 DoCAN 和 DoK-Line 上（因为这两条承载本身是 UDS 家族的一部分，ECU 侧已经实现了会话层），但 **J1850 和 ISO 9141-2 上没有会话层可用**——它们是纯问答应答式的遗留协议。

> **工程含义**：在 CAN / KWP2000 上做 OBD，请求前**不需要**发 0x10 切换会话；但如果 ECU 实现了会话状态机，工具侧最好先切到 default session 兜底。在 J1850 / 9141-2 上则连会话这个概念都不存在。

### 五种物理承载对照

| 承载 | 标准 | 速率 | J1962 针脚 | 初始化 | 美国 MY |
| --- | --- | --- | --- | --- | --- |
| SAE J1850 PWM | SAE J1850 | 41.6 kbit/s | 2, 10 | 无 | 1996-2007 |
| SAE J1850 VPW | SAE J1850 | 10.4 kbit/s | 2 | 无 | 1996-2007 |
| **ISO 9141-2** | ISO 9141-2 | 10.4 kbit/s | 7（+15 L 线） | **5-baud 初始化** | 1996-2007 |
| **ISO 14230-4**（KWP2000） | ISO 14230-1/-2/-4 | 10.4 kbit/s | 7（+15） | 5-baud 或 fast init | 1996-2007 |
| **ISO 15765-4**（CAN） | ISO 15765-2/-4 | 250 / 500 kbit/s | 6, 14 | 无（11/29 位 ID） | 2003 起允许，**2008 起强制** |

> **中国对应**：GB/T 39851 系列（DoCAN，≡ ISO 15765-4）、GB/T 41590 系列（DoK-Line，≡ ISO 14230-4）。

**关键差别**：

- **ISO 9141-2** 是**老式单线串行**，只有 5-baud 初始化，功能寻址靠固定请求 ID。
- **ISO 14230-4（KWP2000）** 物理层与 9141-2 同源（K 线），但**应用层是 Keyword 编码**（如 `09` 读车速、`03` 读码、`0100` 读支持位图），比 9141-2 的 0x40|Service 编码更接近 OBD-II 的 Mode 风格。
- **ISO 15765-4（CAN）** 是唯一还在用的——**MY2008 起美国强制 500 kbit/s CAN**（13 CCR 1968.2(g)(3.4)）。

### 编码风格随承载而变（最容易踩的坑）

**同一套 OBD 数据，在不同承载上的请求/响应字节格式不一样**：

```text
ISO 9141-2 (老式 K 线):
  请求:  0x40 | Service | ...        (Service 用 0x01/0x03/0x05...)
  响应:  0x40 | Service | data...
  否定:  0x7F | Service | ...

ISO 14230-4 (KWP2000):
  请求:  0x09 0x01                   (Keyword + 子功能, 0x09=读实时数据 0x01=转速)
  响应:  0x41 0x01 <A> <B> ...        (0x41 = Keyword + 0x01 的肯定响应)
  否定:  0x7F 0x09 <NRCI> ...

ISO 15765-4 (CAN):
  请求:  0x02 0x41 0x0C 0x00 ...      (第0字节=长度, 第1字节=0x40|Service)
  响应:  0x03 0x41 0x0C 0x1A 0x00 ...
```

> **注意**：KWP2000 的 `09 01` 和 OBD-II 的 `Mode 09` **不是一回事**——KWP2000 的 0x09 是 Keyword 编码的「当前动力总成诊断数据」，语义上接近 OBD-II 的 Mode 01/02，但 PID 编号体系**不是** SAE J1979-DA 那套。**两者不能混用解码表。**

### 数据链路层与物理层的归属

上表里 **ISO 15765-4 同时出现在第 2 层和第 1 层**，这不是重复，是标准分工：

```text
ISO 15765-4 = DoCAN 的 "排放相关系统要求"
  ├─ 第 2 层: 数据链路层接口 (诊断请求/响应的 CAN ID 格式、寻址规则)
  └─ 第 1 层: 物理层 (诊断连接器针脚、波特率、位定时)

ISO 11898-1 = CAN 数据链路层
ISO 11898-2 = CAN 物理层 (收发器)
```

DoK-Line 同理拆成三个部分：

```text
ISO 14230-1 = 物理层 (K 线电气)
ISO 14230-2 = 数据链路层 (报文格式、校验和)
ISO 14230-4 = 排放相关系统要求 (OBD 用的那部分)
```

> **工程含义**：读 ISO 15765-4 时要分清哪部分讲 CAN ID 规则、哪部分讲针脚和波特率——这俩混在同一标准里，是它被当成「CAN 的一部分」来理解的主要原因。

### 数据不在标准正文里 —— 在 SAE 数字附录里

这是 OBD-II 最容易被误解的一点。**ISO 15031-5 只定义"服务格式"，不定义"每个 PID 的具体数值和换算"**。

真正的数据内容在 **SAE 数字附录（Digital Annex）** 里：

```text
ISO 15031-2  ←→  SAE J1930-DA   术语、缩写
ISO 15031-5  ←→  SAE J1979-DA   PID / MID / TID / INFOTYPE 定义 ★
ISO 15031-6  ←→  SAE J2012-DA   DTC 与 FTB 定义
```

| SAE 文档 | 内容 |
| --- | --- |
| **SAE J1979-DA** | 全部标准化数据项：**PID、Monitor ID、Test ID、InfoType ID** |
| **SAE J2012-DA** | 全部标准化 **DTC 与 FTB（故障类型字节）** |
| **SAE J1930-DA** | 全部标准化命名对象、术语与缩写 |

> **工程含义**：查"PID 0x0C 的换算公式"要去 **J1979-DA**，不是 ISO 15031-5 正文。工具链里那份 OBD-II PID 表，数据源是 J1979-DA。SAE J1979-DA 是**持续修订**的（现行 2024 版），ISO 15031-5 正文则多年不动——**数据更新走附录，服务定义走正文**，这是两条独立的更新线。

### 2026 年的新变化：J1979 正在拆成多部分

这是写 OBD-II 时最容易过时的点。**SAE J1979 正在从单一文档演变成一个系列**：

| 编号 | 标题 | 年份 | 内容 |
| --- | --- | --- | --- |
| **SAE J1979** | E/E Diagnostic Test Modes | 现行 2025-05 | 传统 Mode 01-09（燃烧发动机） |
| **SAE J1979-2** | E/E Diagnostic Test Modes | 2021-04 | **OBDonUDS** —— 同样的 OBD 数据，改用 UDS 承载 |
| **SAE J1979-3** | E/E Diagnostic Test Modes: Zero Emission Vehicle Propulsion Systems on UDS (**ZEVonUDS**) | 2022 / 2023-10 | 零排放与插电混动车型的 UDS 版 OBD |
| **SAE J1979-DA** | Digital Annex of E/E Diagnostic Test Modes | 持续修订（现行 2024） | 数字附录 |

**为什么要拆**：传统 OBD-II 围绕内燃机尾气设计，纯电车没有发动机、没有排气系统、连催化器和氧传感器都没有，原有定义无法覆盖。同时传统 PID 编号空间在若干处**已用尽**（比如故障码长度受限）。

**J1979-2 / J1979-3 的技术含义**：把 OBD 数据**从 Mode + PID 搬到 SID + DID**：

```text
传统 OBD-II (SAE J1979 / ISO 15031-5)     OBDonUDS / ZEVonUDS
──────────────────────────────          ──────────────────────
Mode 01 + PID 0x0C  读转速        →      SID 0x22 + DID 读转速
Mode 03      读排放故障码           →      SID 0x19 + DTC 格式标识
Mode 04      清码                   →      SID 0x14 清码
响应 41 0C xx                          响应 62 <DID> xx
否定响应: 静默不响应                     否定响应: 7F <SID> <NRC>
```

> **这正是 OBD-II 与 UDS "分层但不重叠"的最终形态**：OBD 的**法规数据内容**（哪些数据必须可读）不变，但**承载方式**可以换成 UDS。J1979-2 是燃烧发动机的 OBDonUDS，J1979-3 是 J1979-2 的子集，专注零排放动力系统。

**法规落地时间线**（美国市场）：

```text
J1979-2 OBDonUDS:  自 MY2023 起在美国实施
J1979-3 ZEVonUDS: MY2026 起 40% 的 ZEV/PHEV 需支持
                   MY2027 起 100%
                   MY2028 起所有 ZEV 必须支持
                   (CARB CCR 1962.5 另有替代时间表)
```

> **工程含义**：做 2026 年后的工具链，**不能只支持传统 Mode 01-09**。新车型（尤其纯电/插混）读 OBD 数据要按 UDS 走：J1979-2 走 DID 读数据 + 0x19/0x14 读清故障码。**"读不到数据"在新车上往往不是工具坏了，是工具只会 Mode。**

## 法规约束（为什么不能改）

OBD-II 由各国排放法规强制：

- 中国：GB 18352（汽油）、GB 3847（柴油）
- 欧盟：Euro 5/6，对应 UN ECE R83 / R115
- 美国：EPA / CARB OBD-II

这意味着：

- PID 编号和数据含义**不能随意改**。
- 支持的 PID 集合由法规规定，缺失即不合规。
- 必须能读故障码、清除故障码、读 I/M 就绪状态。
- 必须有标准诊断连接器（OBD-II 16 针 J1962）。

## 九个 Mode

| Mode | 名称 | 作用 | 常见用途 |
| --- | --- | --- | --- |
| 0x01 | Request Current Powertrain Diagnostic Data | 读实时数据 | 转速、水温、车速、负荷 |
| 0x02 | Request Powertrain Freeze Frame Data | 读故障冻结帧 | 事故瞬间的快照数据 |
| 0x03 | Request Emission-Related DTC | 读排放相关故障码 | 发动机/变速箱故障码 |
| 0x04 | Clear/Reset OBD Information | 清故障码和复位 | 修车后清码 |
| 0x05 | Request I/M Readiness Status | 读 I/M 就绪状态 | 判断能否做尾气检测 |
| 0x06 | Request I/M Readiness (Monitor) | 读各监测项结果 | 年检前自检 |
| 0x07 | Request Pending DTCs | 读待定故障码 | 间歇性故障捕捉 |
| 0x08 | Read I/M Readiness Status | 读指定监测项 | 定向诊断 |
| 0x09 | Request Vehicle Information | 读车辆信息 | VIN、标定 ID |

诊断请求格式：

```text
CAN 帧 (8 bytes, 单帧):
  byte0: 数据长度 (不含自身)
  byte1: 0x40 | Mode
  byte2+: 参数 (PID 等)

例: 读转速 (Mode 01, PID 0C)
  02 41 0C 00 00 00 00 00
```

响应格式：

```text
  byte0: 数据长度
  byte1: 0x40 | Mode
  byte2: PID
  byte3+: 数据
```

## CAN 标识符

请求（11 位标准帧，广播）：

```text
0x7DF  请求发给所有 ECU
```

响应（各 ECU 用自己的 ID）：

```text
0x7E8  发动机 / ECM
0x7E9  变速箱 / TCM
0x7EA  制动 / ABS / ESC
0x7EB  其他模块
```

29 位扩展帧（部分车型 / 重卡）：

```text
0x18DAF110  请求
0x18DAF110 + n  各 ECU 响应
```

**注意**：OBD-II 的功能寻址请求意味着总线上多个 ECU 都会收到。响应可能来自多个 ECU（不同 PID 由不同 ECU 响应），这和 UDS 的"一次请求一个目标"完全不同。

## 常用 PID 速查

| PID | 名称 | 单位 / 编码 |
| --- | --- | --- |
| 0x00 | PIDs 01-20 支持位图 | 位掩码 |
| 0x01 | MIL 状态 + DTC 数量 | bit0=MIL, bit7-15=DTC 数 |
| 0x03 | 发动机负荷 | 0-100 % |
| 0x04 | 冷却液温度 | A-40 |
| 0x05 | 发动机转速 | (rpm×4)/2 |
| 0x0B | 进气歧管压力 | kPa |
| 0x0C | 发动机转速 | rpm×4/2 |
| 0x0D | 车辆速度 | km/h |
| 0x0F | 进气温度 | A-40 |
| 0x10 | 空气流量 | (g/s)×100 |
| 0x11 | 节气门位置 | 0-100 % |
| 0x1F | 发动机运行时间 | 秒 |
| 0x21 | MIL 亮起后行驶距离 | km |
| 0x2F | 油箱液位 | 0-100 % |
| 0x31 | 故障码清除后行驶距离 | km |
| 0x42 | 模块电压 | mV/1000 |
| 0x46 | 环境温度 | A-40 |
| 0x49 | 加速踏板位置 | 0-100 % |
| 0x4C | 指令扭矩 | -100~99.8 % |
| 0x67 | 机油温度 | A-40 |

**温标约定**：温度 = A - 40。读到 `0x5A`（90）→ 90 - 40 = 50 ℃。

**转速编码**：多数 PID 用 `(rpm × 4) / 2`，即 `rpm = value × 2 / 4`。例：值 `0x1A00` = 6656 → 6656×2/4 = 3328 rpm。

## 故障码格式

2 字节 DTC，高位在前：

```text
bit15-14: 首字符类型
  00 = P (Powertrain 动力系统)
  01 = C (Chassis 底盘)
  10 = B (Body 车身)
  11 = U (Network 通信)

bit13-8:  第二字符 (字母或数字)
bit7-0:   第三字符 (十六进制)

例:
P0100  00 01 00 → 0x0100 → P0100  进气歧管压力电路
P0301  00 03 01 → 0x0301 → P0301  点火线圈 1 失火
U0100  11 01 00 → 0xC100 → U0100  与 ECM 的通信丢失
```

## 相关规范

OBD-II 不止一个标准，涉及三层：

| 层 | 标准 | 作用 |
| --- | --- | --- |
| 应用层 | **SAE J1979 / ISO 15031-5** | 核心标准。定义 Mode 01-09、PID 空间、I/M 监测项、故障码格式。两者技术等同，平行出版（现行 ISO 15031-5:2015 / SAE J1979_202505） |
| 数据附录 | **SAE J1979-DA / J2012-DA / J1930-DA** | PID / MID / TID / INFOTYPE、DTC 与 FTB、术语的实际定义。**内容在这里，不在 ISO 正文** |
| 合规 | ISO 15031-6 | 诊断故障码定义（DTC 格式规则，引用 SAE J2012-DA） |
| 外围 | ISO 15031-1 / -2 / -3 / -4 / -7 | 一般信息、术语、连接器（= SAE J1962）、测试设备、数据链路安全性 |
| UDS 承载 | **SAE J1979-2（OBDonUDS）/ J1979-3（ZEVonUDS）** | 2021 起把同一批 OBD 数据改用 UDS（SID + DID）承载，覆盖燃烧车与零排放车型 |
| **承载 · DoCAN** | **ISO 15765-2 / ISO 15765-4** + ISO 11898-1/-2 | CAN 上的 ISO-TP 传输网络层 + 排放相关系统要求。**MY2008 起美国强制** |
| **承载 · DoK-Line** | **ISO 14230-1 / -2 / -4** | KWP2000：物理层 / 数据链路层 / 排放相关要求 |
| **承载 · 遗留串行** | **ISO 9141-2**、SAE J1850 | 老式单线 K 线与单线总线，5-baud 初始化 |
| 会话层 | ISO 14229-2 | 借用于 DoCAN / DoK-Line；**不适用于 J1850 与 ISO 9141-2** |
| 法规 | EPA 40 CFR Part 85、CARB Title 1 §1968、Euro 5/6、GB 18352 / GB 3847 | 各地区排放法规与 OBD 覆盖要求 |

> 中国对应：GB/T 42193 系列（≡ ISO 15031）、GB/T 39851 系列（DoCAN）、GB/T 41590 系列（DoK-Line）。

### 与 WWH-OBD 的区别（最容易混淆）

```text
OBD-II   (SAE J1979)  ──┐
                        ├── 法规诊断，乘用车
WWH-OBD  (ISO 27145)  ──┘   商用车

UDS      (ISO 14229)  ───── OEM 诊断，全车系
```

三者**不是版本升级关系**，而是并列体系。WWH-OBD 是商用车版 OBD，其应用层 ISO 27145-3 定义的是 **UDS 服务的子集**，会话层直接用 ISO 14229-2。

### 与 UDS 的规范边界

| 维度 | OBD-II | UDS |
| --- | --- | --- |
| 标准 | SAE J1979 / ISO 15031-5 | ISO 14229 |
| 性质 | 法规强制 | OEM 规范 |
| 会话/权限 | 无 | 有 |
| 数据模型 | PID 固定编号 | DID 自由定义 |
| 谁能用 | 任何 OBD 扫描器 | 需 OEM 诊断规范 |

> **但边界正在移动**：SAE J1979-2（OBDonUDS）与 J1979-3（ZEVonUDS）把 OBD 的法规数据**放到了 UDS 的承载上**——法规要求「哪些数据必须可读」不变，承载方式从 Mode+PID 换成 SID+DID。所以「OBD 用 Mode、UDS 用 DID」不再是绝对的二分，而是**同一套数据有两种承载形态**。

---

## 更新记录

- 2026-11-16: 补充「为什么写作 SAE J1979 / ISO 15031-5」。依据 SAE J1979_200705 引言原文（*"technically equivalent to a draft version of ISO 15031-5 ... This version of SAE J1979 includes all of the editorial changes that were included in the published version of the ISO document"*），说明二者是**同一份技术内容的两种发布形态**、平行出版，而非两个并列标准。同时补充三项此前缺失的关键事实：① **ISO 15031-5 正文只定义服务格式，PID/MID/TID/INFOTYPE 与 DTC/FTB 的实际数据在 SAE 数字附录**（J1979-DA / J2012-DA / J1930-DA，数据更新走附录、服务定义走正文，两条独立更新线）；② **SAE J1979 正在拆分为系列**——J1979-2（OBDonUDS，2021-04，燃烧车）与 J1979-3（ZEVonUDS，2022/2023-10，零排放），把 OBD 数据改用 UDS 承载，法规时间线 MY2026 起 40% / MY2027 起 100% / MY2028 起全部 ZEV 必须支持（CARB CCR 1962.5 另有替代时间表）；③ 补入现行版本号 ISO 15031-5:2015（第 3 版，2026-10 复审确认）与 SAE J1979_202505，以及中国对应 GB/T 42193 系列（GB/T 42193.5-2026 ≡ ISO 15031-5:2015）。同步更新 [[bus/automotive/obd2-deep-dive|obd2-deep-dive]] 与 [[bus/automotive/can-standards-map|can-standards-map]] 的标准表。

---

## 扩展阅读

- [[bus/automotive/obd2-deep-dive|obd2-deep-dive]] — PID 空间、监测项状态、I/M 就绪、Mode 详解
- [[bus/automotive/obd2-practical|obd2-practical]] — ELM327、candump、调试流程、检查清单
- [[bus/automotive/obd2-failure-cases|obd2-failure-cases]] — 产线与售后故障案例
- [[bus/automotive/uds|uds]] — UDS 入口（与 OBD-II 的对照）
- [[bus/automotive/wwh-obd|wwh-obd]] — WWH-OBD（ISO 27145）——商用车版 OBD，与本文是**并列体系**不是升级
- [[bus/automotive/iso-tp|iso-tp]] — ISO-TP 入口（OBD-II 的传输底座）
- [[bus/automotive/can-standards-map|can-standards-map]] — CAN 家族标准规范总表
- [[bus/automotive/can-protocol-family|can-protocol-family]] — CAN 家族全景
