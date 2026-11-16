---
tags:
  - layer/bus
  - type/deep-dive
  - protocol/obd2
  - topic/automotive
---

# OBD-II Deep Dive

## 目标

本文深入 OBD-II 的 PID 空间、Mode 语义、I/M 监测模型、故障码体系、CAN 标识符分配和与 UDS 的边界，回答这些问题：

- 支持哪些 PID 是怎么表达和协商的。
- I/M 就绪状态（Readiness）和监测项（Monitor）的状态机是什么。
- 故障码有哪几类，pending / confirmed / permanent 怎么区分。
- OBD-II 和 UDS 在同一辆车上如何共存、职责如何划分。
- 法规约束下哪些行为是强制性的、哪些是可选项。

## 目标受众

- 做 OBD-II 读取设备（ELM327 类、OBD 盒子、车队诊断终端）的人。
- 做 ECU 侧 OBD 响应实现（发动机 EMS 移植、第三方 ECU）的人。
- 做售后诊断工具和排放检测对接的人。

## PID 支持协商

PID 空间是**分层块状**的，每个 PID 块的第 0 号 PID 是"支持位图"。

### 三层结构

```text
PID 0x00  ->  bit31..bit0 映射 PID 0x01..0x20 的支持情况
PID 0x20  ->  bit31..bit0 映射 PID 0x21..0x40 的支持情况
PID 0x40  ->  bit31..bit0 映射 PID 0x41..0x60 的支持情况
PID 0x60  ->  bit31..bit0 映射 PID 0x61..0x80 的支持情况
```

例：读 PID 0x00 返回 `BF 3F B9 00 00 00 00 00`

```text
0xBF 0x3F 0xB9 0x00  ->  支持 PID 0x01..0x1A, 0x21..0x3F, 0x41..0x49 等
bit = 1 表示该 PID 支持
```

**关键**：不要假设某个 PID 一定存在。必须先读 0x00 / 0x20 / 0x40 / 0x60 拿到支持位图，再决定读哪些。

### PID 0x01 详解码

```text
bit0     MIL (Malfunction Indicator Lamp) 故障灯
bit1     动力系统故障 (DTC 涉及动力总成)
bit2     动力系统故障 (仅排放相关)
bit3     底盘系统故障
bit4     车身系统故障
bit5-6   保留
bit7-15  DTC 数量 (3 bit, 与 bit16-23 组成 4 bit)
```

DTC 数量是 4 bit（bit7-15 + bit16-23），所以完整读取是：

```text
响应: 84 41 01 <8 bytes>
byte1 = 0x84 (bit7 = DTC count MSB)
byte3 = bit0=MIL, bit1-4 = 各系统故障, bit5-6 = 保留, bit7 = DTC count LSB
```

### 扩展 PID（新一代）

2020 年后法规增加了 OBD Monitor 相关 PID：

```text
PID 0x1D  Mode 01 支持的 Mode 列表 (09 00 04)
PID 0x1E  OBD Monitor ID
PID 0x1F  发动机运行时间
PID 0xA6  OBD Monitor ID (与 1E 并存)
PID 0xA7  OBD Monitor 支持状态
PID 0xA8  OBD Monitor 结果
PID 0xA9  OBD Monitor 车辆信息
```

这一块各 OEM 实现差异较大，**读之前先查支持位图**。

## Mode 01: 实时数据

请求：`01 <PID>`，响应：`41 <PID> <data...>`。

### 典型多字节编码

**发动机转速**（PID 0x0C）：

```text
响应: 41 0C 1A 00
value = (0x1A << 8) | 0x00 = 6656
rpm = value * 2 / 4 = 3328
```

**冷却液温度**（PID 0x04）：

```text
响应: 41 04 5A
temp = 0x5A - 40 = 90 - 40 = 50 摄氏度
```

**车速**（PID 0x0D）：

```text
响应: 41 0D 32
speed = 0x32 = 50 km/h
```

**节气门位置**（PID 0x11）：

```text
响应: 41 11 19
position = 0x19 * 100 / 255 = 9.8 %
```

**模块电压**（PID 0x42）：

```text
响应: 41 42 8C 3D
voltage = ((0x8C << 8) | 0x3D) / 1000 = 1.655 V
```

**通用解码公式**：

```text
物理值 = (A * 256 + B) * 系数 + 偏移
```

常见系数表：

| 类型 | 公式 |
| --- | --- |
| 温度 | value - 40 |
| 转速 | value * 2 / 4 |
| 百分比 | value * 100 / 255 |
| 电压 | value / 1000 |
| 原始值 | value 直出 |

### Mode 01 的多 ECU 特性

OBD-II 请求是**广播**（0x7DF），所以总线上多个 ECU 都会响应。

```text
请求: 02 41 0C 00 00 00 00 00  (0x7DF)
响应: 03 41 0C 1A 00 00 00 00  (0x7E8, ECM)
```

不同 PID 由不同 ECU 负责：

```text
0x7E8 ECM  -> 转速, 水温, 负荷, 燃油
0x7E9 TCM  -> 变速箱信息
0x7EA ABS  -> 车速(部分车型)
0x7EB 其他 -> 车身信息
```

**工具必须能区分不同源 ID 的响应**，不能假设"第 N 个响应就是第 N 个 ECU"。

## Mode 02: 冻结帧

Mode 02 的 PID 空间与 Mode 01 **完全相同**，但返回的是**故障发生瞬间**的数据快照。

```text
请求: 02 04 ...   (Mode 02 + PID 0x04 冷却液温度)
响应: 42 04 5A
```

冻结帧是**排放相关故障触发时**自动保存的，通常只保存一组。

工程注意：

- 冻结帧的 PID 支持情况**与 Mode 01 不同**，要单独读 Mode 02 的 0x00 支持位图。
- 多个 DTC 可能对应多个冻结帧组（Frame 1 / Frame 2）。
- 清除故障码（Mode 04）会**同时清掉冻结帧**，读取要先于清除。

## Mode 03: 排放相关故障码

请求 `03`，响应格式：

```text
byte0: DTC 数量 (n)
byte1: 0x43
byte2..: 每个 DTC 2 字节, 大端
```

例：

```text
04 43 01 40 03 01 00 00
     │  └──┬─┘ └──┬──┘
     │     │      └── DTC 2: 0x0301 (P0301)
     │     └───────── DTC 1: 0x0140 (P0140)
     └─────────────── 0x43 = 0x40 + Mode 03
DTC 数量 = 0x04
```

Mode 03 只返回**排放相关**故障码（P0xxx 和 P2xxx 为主），不返回车身/通信类。

## Mode 04: 清除故障码

```text
请求: 04 00 00 00 00 00 00 00
响应: 04 44 00 00 00 00 00 00
```

Mode 04 会清除：

- 故障码（Mode 03 / 07 的可见码）
- 冻结帧（Mode 02）
- MIL 状态
- I/M 就绪状态（部分实现）

**关键工程约束**：

- 很多 ECU 要求清除前满足条件（车速 = 0，点火 ON，电压正常）。
- 清除后 **I/M 就绪状态会重置**，尾气检测前必须重新跑完监测循环。
- 清除**不能**消除故障本身，故障条件还在就会立刻重新报码。

## Mode 05 / 06 / 08: I/M 就绪与监测

### 两个不同概念

```text
Readiness (I/M Readiness)  监测项是否已跑完 -> 能否做尾气检测
Monitor Result             单个监测项的具体结果 -> 哪个系统没通过
```

### Mode 05: 就绪状态位图

```text
响应: 04 41 <bit7..bit0> <bit15..bit8> <bit23..bit16> <bit31..bit24>
```

标准定义的 readiness bit：

| Bit | 监测项 |
| --- | --- |
| 0 | Misfire (失火) |
| 1 | Fuel System (燃油系统) |
| 2 | Comprehensive (综合) |
| 3 | Catalyst (催化器) |
| 4 | EVAP (蒸发排放) |
| 5 | O2 Sensor (氧传感器) |
| 6 | O2 Heater (氧传感器加热) |
| 7 | EGR (废气再循环) |
| 8 | AIR (二次空气) |
| 9 | EVAP Monitor (蒸发监测) |
| 10 | 冷启动催化器 |
| 11 | 混合气 |
| 12 | 二次空气监测 |
| 13 | 冷启动排气 |
| 14 | 催化剂加热器 |
| 15 | 热保护 |

每个 bit：

```text
0 = 该监测项未完成
1 = 该监测项已完成
```

**典型故障**：读到的 readiness 全是 1（全部就绪），但 MIL 亮着 —— 说明**监控模式（Monitor）**有问题，Mode 05 不反映这个。

### Mode 06: 监测结果

```text
响应: 08 46 00 81 00 65 00 00 00
     │  │  └──┬──┘ └──┬──┘
     │  │     │       └── 监测项 3 结果
     │  │     └────────── 监测项 2 结果
     │  └──────────────── 0x46 = 0x40 + Mode 06
     └─────────────────── 监测项数量 = 8
```

单个监测项结果字节：

| 值 | 含义 |
| --- | --- |
| 0x00 | 完成且通过 |
| 0x01–0x7F | 未完成 / 失败（含具体故障信息） |
| 0x80 | 该监测项不支持 |
| 0xFF | 不适用（该车辆配置无此监测项） |

这是 Mode 05 的补充：**Mode 05 告诉你"没完成"，Mode 06 告诉你"哪个没完成、为什么"**。

### Mode 08: 指定监测项

```text
请求: 08 <monitor_id>
响应: 48 <monitor_id> <AVD> <status>
```

可以定向读某个监测项的状态和故障信息，用于精确定位。

## Mode 07: 待定故障码

```text
请求: 07
响应: 04 47 01 20 03 03 00 00
```

Pending DTC 是**还没到确认条件**的故障码。

分类体系：

```text
Confirmed (已确认)  Mode 03  -- 排放相关, 故障已复现足够次数
Pending (待定)      Mode 07  -- 故障出现过但未达确认门限
Permanent (永久)    需 UDS 0x19 -- 需外部清除, 通常伴随 MIL 闪烁
```

工程意义：Pending 码能捕捉**间歇性故障**，是修车时最有价值的线索之一。

## Mode 09: 车辆信息

```text
请求: 09 02
响应: 06 49 02 56 49 4E ...        (VIN)

请求: 09 04
响应: 04 49 04 43 41 4C ...        (标定 ID)

请求: 09 06
响应: 04 49 06 41 42 43 ...        (VIN 的第三部分)
```

Mode 09 的 PID 是**两字节**（PID + 子 PID），这和 Mode 01/02 的单字节 PID 不同。

支持的子 PID：

```text
0x02  VIN
0x03  标定 ID
0x04  标定 ID (另一种编码)
0x05  ECU 校准号
0x06  VIN 第三段
0x07  ECU 软件号
0x08  ECU 标定零件号
0x09  ECU 硬件零件号
0x0A  系统标识符
0x0B  制造日期
0x0C  序列号
0x0D  支撑的 OBD 监测项
0x0E  OBD Monitor ID
```

Mode 09 通常需要**扩展寻址**（29 位帧），因为 VIN 有 17 字节，单帧装不下：

```text
请求 (11 位): 03 49 02 00 00 00 00 00
响应 (扩展帧或多帧): VIN 分多帧返回
```

## OBD-II 与 UDS 的边界

同一辆车上两者共存，职责划分：

```text
OBD-II                          UDS
------------------------------  -------------------------------
法规强制                        整车厂定义
只读为主 (除 Mode 04)           完整读写
无会话                          有会话状态机
无权限                          有安全等级
PID 固定编号                    DID 自由定义
覆盖排放相关                    覆盖整车
任何 OBD 扫描器都能用             需要 OEM 诊断规范
```

**实现上的共存方式**：现代 ECU 内部通常有两套诊断处理：

```text
OBD 处理路径:
  识别 0x7DF 功能寻址 + 排放相关 Mode -> OBD 响应 (强制实现)

UDS 处理路径:
  识别 OEM 诊断 ID + UDS SID -> UDS 响应
```

在 OEM 诊断 ID 上收到的 Mode 01 请求，很多 OEM 会**转发或合并**到 OBD 数据源，这样 UDS 工具也能读到实时数据。

**关键区别**：OBD-II 请求用的是**功能寻址广播**，UDS 用的是**物理寻址单播**。同一个 ECU 可以同时支持两套，但响应 ID 不同。

## 法规强制性要点

### 必须实现

- Mode 01 的核心 PID（转速、水温、车速、负荷、燃油、氧传感器等）
- Mode 03 / 04 / 05 / 06 / 07
- 标准诊断连接器（OBD-II 16 针 J1962）
- MIL 指示（可以是仪表灯，也可以是闪烁代码）

### 常见地区差异

| 地区 | 额外要求 |
| --- | --- |
| 中国 | GB 18352 / GB 3847，OBD + 环保监控（HJ 相关） |
| 欧盟 | Euro 6/6b 增加 OBD 监测项和 OBM (On-Board Monitoring) |
| 美国 | EPA OBD-II，CARB 对某些州额外要求 |

### 典型失效判据

法规对"诊断功能失效"（Incomplete/Not Ready）的判定：

```text
- 关键 PID 读不到
- 故障码读不到
- 清除功能无效
- I/M 就绪状态无法正确置位
- 同一请求连续两次返回不同结果（数据不可信）
```

## 实现要点

### ECU 侧 OBD 响应

```c
/* OBD 响应: 只在功能寻址且是支持的 Mode 时响应 */
int obd_handle_request(const can_frame_t *f, can_frame_t *resp) {
    uint8_t mode = f->data[1] & 0xBF;   /* 去掉 0x40 位 */
    uint8_t pid  = f->data[2];

    switch (mode) {
        case 0x01: return obd_mode01(pid, resp);
        case 0x03: return obd_mode03(resp);
        case 0x04: return obd_mode04(resp);
        case 0x05: return obd_mode05(resp);
        case 0x06: return obd_mode06(resp);
        case 0x07: return obd_mode07(resp);
        default:   return -1;   /* 不支持的 Mode 不响应 */
    }
}
```

**要点**：不支持的 Mode **不应该响应**（不是回错误码）。这是 OBD-II 与 UDS 的显著差异 —— UDS 会回 `0x7F 11`（服务不支持），OBD-II 通常直接静默。

### 数据一致性

法规要求同一 PID 连续读取结果必须稳定：

```c
/* 转速计算要避免抖动 */
uint16_t obd_get_rpm(void) {
    static uint16_t last = 0;
    uint16_t rpm = engine_rpm_calculated();   /* 不是原始捕获值 */
    /* 低通滤波, 避免 PID 读数抖动导致检测不通过 */
    rpm = (last * 3 + rpm) / 4;
    last = rpm;
    return rpm;
}
```

这是 OBD-II 独有的工程要求：**数据稳定性本身是被检测的指标**。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 扫描器连不上 | 协议选择、波特率、CAN ID、ELM327 兼容性 |
| 能读转速但读不到水温 | 支持位图、PID 是否属于别的 ECU |
| 故障码读不全 | Mode 03 与 Mode 07 区别、是否只读了排放相关 |
| 清码后 MIL 还亮 | 故障条件未消除、I/M 就绪被重置 |
| Readiness 全 0 | 监测循环未跑完（需一个完整驾驶循环） |
| 同一 PID 两次读数不同 | 数据稳定性（法规检测项）、滤波缺失 |
| Mode 06 读不到 | 是否需要扩展寻址、29 位帧支持 |
| VIN 读不全 | ISO-TP 多帧、扩展寻址 |

## 相关规范详解

OBD-II 的标准体系比想象的宽，容易漏掉：

| 标准 | 覆盖 | 关键点 |
| --- | --- | --- |
| **SAE J1979 / ISO 15031-5** | 应用层 | Mode 01-09 命令、PID 编号、故障码格式、I/M 监测项。两者**技术等同、平行出版**（现行 ISO 15031-5:2015 / SAE J1979_202505） |
| **SAE J1979-DA** | 数据附录 | **PID / MID / TID / INFOTYPE 的实际定义在这里，不在 ISO 正文**。持续修订（现行 2024 版） |
| **SAE J1979-2 / J1979-3** | UDS 承载 | **OBDonUDS**（燃烧车）/ **ZEVonUDS**（零排放）。同一批 OBD 数据改用 SID + DID 承载 |
| SAE J2012-DA | 故障码附录 | DTC 与 FTB 的实际定义 |
| ISO 15031-6 | 故障码定义 | DTC 格式定义规则（引用 SAE J2012-DA） |
| ISO 15031-1 | 总则 | 一般信息与用例定义 |
| ISO 15031-2 | 术语 | 术语与缩写指南（对应 SAE J1930） |
| ISO 15031-3 | 连接器 | 诊断连接器及相关电路（对应 SAE J1962），16 针定义 |
| ISO 15031-4 | 测试设备 | 外部测试设备规范 |
| ISO 15031-7 | 安全 | 数据链路安全性 |
| **ISO 15765-2 / ISO 15765-4** | **DoCAN 承载** | ISO-TP 传输网络层 + 排放相关系统要求（同时规定 CAN ID 格式与诊断针脚/波特率）。**MY2008 起美国强制** |
| **ISO 14230-1 / -2 / -4** | **DoK-Line 承载** | KWP2000：物理层 / 数据链路层 / 排放相关要求。5-baud 或 fast init |
| **ISO 9141-2、SAE J1850** | **遗留串行承载** | 老式单线 K 线 / 单线总线，5-baud 初始化 |
| ISO 14229-2 | 会话层 | 借用于 DoCAN 与 DoK-Line；**不适用于 J1850 与 ISO 9141-2**（那两种协议无会话层） |
| ISO 11898-1 / -2 | 物理/链路 | CAN 数据链路与物理层（被 ISO 15765-4 引用） |
| ISO 27145-1 ~ -4, -6 | 商用车 | **WWH-OBD**，另一套体系（见下） |

### OBD-II 与 WWH-OBD 的规范关系

```text
法规层
├── 乘用车    SAE J1979 / ISO 15031-5   (OBD-II)
└── 商用车    ISO 27145-3               (WWH-OBD)
              ├── ISO 27145-2  通用数据字典（表示层）
              ├── ISO 27145-1  一般信息
              ├── ISO 27145-4  连接器
              ├── ISO 27145-6  外部测试设备
              ├── ISO 14229-2  会话层
              └── ISO 13400-2  传输层 (DoIP) / ISO 15765-2 (CAN)
```

WWH-OBD 的应用层 **ISO 27145-3 定义的是 UDS 服务的子集**，会话层直接引用 ISO 14229-2 —— 也就是说，商用车 OBD 是站在 UDS 体系上的，而不是另起炉灶。

> ⚠️ **ISO 27145-5 不存在**，系列为 1 / 2 / 3 / 4 / 6，跳过 5。完整分工见 `bus/automotive/wwh-obd.md`。

### Mode 与 UDS 服务的对应

OBD-II 的 Mode 是**固定编号**，与 UDS 的 SID 没有一一对应关系：

```text
OBD-II Mode 01  ≈  UDS 0x22 (ReadDataByIdentifier) —— 但 PID 空间固定
OBD-II Mode 03  ≈  UDS 0x19 (ReadDTCInformation) —— 但 DTC 是 2 字节排放码
OBD-II Mode 04  ≈  UDS 0x14 (ClearDiagnosticInformation)
OBD-II Mode 09  ≈  UDS 0x22 —— 但走扩展寻址多帧
```

**不能把 OBD-II 的 PID 当 DID 用**，反之亦然。两者编号空间独立。

### 各地区法规对应

| 地区 | 法规 | 备注 |
| --- | --- | --- |
| 美国 | EPA 40 CFR Part 85 | 联邦 OBD-II 要求 |
| 美国加州 | CARB Title 1 Section 1968 | 在联邦基础上追加 |
| 欧盟 | Euro 5 / 6 / 7 | 通过 UNECE R83 / R115 落地 |
| 中国 | GB 18352（汽油）、GB 3847（柴油） | OBD 覆盖要求 |
| 商用车通用 | UNECE R49 / R84 / R85 | 重型车 OBD |

### 环境与硬件规范（做 ECU 侧实现时）

| 标准 | 作用 |
| --- | --- |
| ISO 16750-2 | 电气负荷：过压、抛负载、反接、短路 |
| ISO 7637-2 | 电源线瞬态干扰 |
| ISO 10605 | 静电放电 |
| CISPR 25 | 车载发射限值 |
| ISO 11452 | 辐射抗扰度 |
| ISO 26262 | 功能安全（诊断覆盖率） |
| ISO/SAE 21434 | 网络安全（CAN 注入防护） |

**OBD-II 的法规检测项**中，有一条容易被忽略：**同一 PID 连续读取结果必须一致**。这要求 ECU 侧对 PID 数据做滤波和量化，不能直接返回原始捕获值。



- 先读 PID 0x00 / 0x20 / 0x40 / 0x60 确认支持范围。
- 区分 11 位标准帧寻址和 29 位扩展帧寻址。
- 响应 ID 区分 0x7E8 / 0x7E9 / 0x7EA / 0x7EB。
- Mode 01 与 Mode 02 的支持集**分别**读取。
- Mode 03 / 07 / 19 三类故障码分开处理。
- Mode 05 与 Mode 06 配合使用。
- 温标、转速、百分比的解码公式逐个核对。
- 读冻结帧要在清码之前。
- 清码前后的 readiness 变化要记录。
- 数据稳定性（滤波）不能省。

## 延伸阅读

- `bus/automotive/obd2.md` — OBD-II 概览、九个 Mode、PID 速查
- `bus/automotive/obd2-practical.md` — 工具链、调试流程、检查清单
- `bus/automotive/obd2-failure-cases.md` — 故障案例
- `bus/automotive/uds.md` — UDS 入口
- `bus/automotive/uds-deep-dive.md` — UDS 深度（与本文对照）
- `bus/automotive/wwh-obd.md` — WWH-OBD（ISO 27145）商用车体系
- `bus/automotive/iso-tp.md` — ISO-TP 入口
- `bus/automotive/can-standards-map.md` — CAN 家族标准规范总表
- `bus/automotive/can-protocol-family.md` — CAN 家族全景
