---
tags:
  - layer/bus
  - protocol/can
aliases:
  - CAN 家族全景
  - CAN 协议家族
description: CAN 家族的分层地图：PHY / CAN FD / CAN XL / ISO-TP / CANopen / J1939 / UDS / OBD-II / WWH-OBD，含协议矩阵、选型决策、文档索引与覆盖缺口。
---

# CAN 协议全景汇总

## 定位

CAN 不是单一协议，而是覆盖物理层、数据链路、传输层与应用层的协议家族。本文是 **CAN 家族的统一入口**，只做跨协议导航与边界说明；单协议的帧格式、调试步骤和案例请进入对应入口页。

| 你想解决的问题               | 入口                                          |
| ---------------------------- | --------------------------------------------- |
| CAN 之上还有哪些协议？       | [分层结构](#分层结构)                         |
| 我的场景该选哪个协议？       | [协议矩阵](#协议矩阵) · [选型决策](#选型决策) |
| 每个协议读到哪一步？         | [文档索引](#文档索引)                         |
| 库内还缺什么？               | [覆盖缺口](#覆盖缺口)                         |
| 标准号、电器规范与法规边界？ | [can-standards-map.md](can-standards-map.md)  |

## 分层结构

```text
┌─────────────────────────────────────────────────────────────┐
│  L4 应用层     CANopen    J1939    UDS    OBD-II              │
│  (设备模型 /   对象字典  PGN/SPN  诊断服务  排放检测          │
│   报文语义)   PDO/SDO   DM/TP    会话/DID  Mode 01-09         │
│                CiA 402   NAME/地址                         │
├─────────────────────────────────────────────────────────────┤
│  L3 传输层     ISO-TP (ISO 15765-2)                          │
│  (分包/流控)   SF/FF/CF/FC · BS · STmin                     │
├─────────────────────────────────────────────────────────────┤
│  L2 数据链路   CAN 2.0A (经典 CAN, 11/29-bit, 8B)           │
│                CAN FD  (64B payload, 高速数据段)             │
│                CAN XL  (2048B, TSN 融合)                    │
│                仲裁 · 错误处理 · TEC/REC · Bus Off           │
├─────────────────────────────────────────────────────────────┤
│  L1 物理层     CAN PHY (差分 CAN_H/CAN_L, 120Ω 终端电阻)     │
│                收发器 TJA1050 / TJA1443 / SN65HVD257         │
└─────────────────────────────────────────────────────────────┘
```

**关键理解**：ISO-TP 是传输层（解决单帧 8 字节不够），UDS 和 OBD 都跑在 ISO-TP 之上；CANopen 和 J1939 自带传输机制（BAM / NMT），通常**不**依赖 ISO-TP。

上图只列主干；WWH-OBD、CANopen Safety、LIN 等分支见下方清单。

### 完整分层清单

| 层  | 协议           | 标准号                         | 定位                                           |
| --- | -------------- | ------------------------------ | ---------------------------------------------- |
| L1  | CAN PHY        | ISO 11898                      | 差分物理层、终端电阻、收发器                   |
| L2  | Classic CAN    | ISO 11898-1 / CAN 2.0A         | 11/29-bit ID，8 字节载荷                       |
| L2  | CAN FD         | ISO 11898-1:2015               | 数据段 64 字节，多速率                         |
| L2  | CAN XL         | **ISO 11898-1:2024**           | 1–2048 字节，>10 Mbit/s（2024 年正式进入 ISO） |
| L2  | LIN            | ISO 17987                      | 车身低速单线总线（**非 CAN 家族，但常并列**）  |
| L3  | ISO-TP         | ISO 15765-2                    | 多帧传输 + 流控                                |
| L4  | CANopen        | CiA 301 / CiA 402              | 工业设备模型、对象字典、PDO/SDO                |
| L4  | CANopen FD     | CiA 1301 / CiA 1302            | CANopen 跑在 CAN FD 上，USDO 替代 SDO          |
| L4  | J1939          | SAE J1939-21 / -71 / -73 / -81 | 商用车网络，PGN/SPN、地址声明                  |
| L4  | UDS            | ISO 14229-1 ~ -7               | 统一诊断服务，读 DTC、刷写                     |
| L4  | OBD-II         | **SAE J1979 / ISO 15031-5**    | 乘用车排放检测，Mode 01-09                     |
| L4  | WWH-OBD        | **ISO 27145-1 ~ -4, -6**       | 商用车全球统一车载诊断（GTR No. 5 法规）       |
| L4  | CANopen-Safety | CiA 304 / EN 50325-5           | 安全功能认证扩展                               |

> **OBD-II 已于 2026-10-31 补齐**：`bus/automotive/obd2.md` / `bus/automotive/obd2-deep-dive.md` / `bus/automotive/obd2-practical.md` / `bus/automotive/obd2-failure-cases.md` 四篇。
>
> **各协议的标准号、电器规范与环境/安全规范的完整总表见 `bus/automotive/can-standards-map.md`**。

## 协议矩阵

### 按应用领域

| 协议        | 领域              | 是否跑在 CAN 上 | 库内覆盖                   | 关键特性                           |
| ----------- | ----------------- | --------------- | -------------------------- | ---------------------------------- |
| **CANopen** | 工业 / 运动控制   | 是              | **L4**（5 篇 + 12 例）     | 对象字典 + SDO/PDO + NMT + CiA 402 |
| **J1939**   | 商用车 / 工程机械 | 是              | **L4**（8 篇 + 21 例）     | PGN/SPN + 地址声明 + BAM/TP + DM   |
| **UDS**     | 汽车诊断 / 刷写   | 是（也可 DoIP） | **L4**（5 篇 + 12 例）     | 会话 / DID / 安全访问 / 刷写 + NRC |
| **ISO-TP**  | 通用多帧传输      | 是              | **L4**（5 篇 + 12 例）     | SF/FF/CF/FC + BS/STmin             |
| **OBD-II**  | 乘用车排放检测    | 是              | **L4**（5 篇 + 12 例）     | Mode 01-09 + PID + readiness       |
| **WWH-OBD** | 商用车法规诊断    | 是              | **L4**（5 篇 + 12 例）     | ISO 27145 + DoCAN/DoIP + 24 位 DTC |
| **CAN FD**  | 高带宽车载        | 是（独立 L2）   | **L4**（3 篇 + 21 例）     | 64 B payload + 可变数据速率        |
| **CAN XL**  | 车载以太网融合    | 是（独立 L2）   | **L2**（并入 CAN FD 笔记） | 2048 B + TSN                       |

### 按协议角色

```text
CAN (L2)
├── 传输层
│   └── ISO-TP  ──┬── UDS      (诊断服务)
│                 ├── OBD-II   (排放检测)
│                 └── DoIP     (以太网诊断，非 CAN 但同一 UDS 语义)
├── 自带传输机制
│   ├── CANopen  ─── 对象字典 / PDO / SDO / NMT / CiA 402
│   └── J1939    ─── PGN / SPN / NAME / BAM / RTS-CTS / DM
└── 变体 L2
    ├── CAN FD   ─── 64B 载荷，CANopen over FD / J1939 over FD
    └── CAN XL   ─── 2048B，TSN 融合
```

### 关键差异速查

| 维度          | CANopen                  | J1939                      | UDS                 | OBD-II                     |
| ------------- | ------------------------ | -------------------------- | ------------------- | -------------------------- |
| 寻址方式      | Node ID (1-127) + COB-ID | PGN (29-bit ID 内嵌)       | 物理寻址 / 功能寻址 | 功能寻址广播 0x7DF         |
| 周期性数据    | PDO (预映射, 无请求)     | PGN 周期广播               | 无（请求-响应）     | Mode 01 请求-响应          |
| 配置/参数     | SDO (一问一答)           | DM / 配置消息              | DID 读写            | Mode 04 清除               |
| 心跳/节点管理 | NMT + Heartbeat          | 地址声明 (Address Claimed) | Tester Present      | 无                         |
| 错误报告      | Emergency (0x80)         | DM1/DM2 (灯码)             | NRC (负响应码)      | Mode 03/07 故障码          |
| 多帧传输      | 通常单帧                 | 自带 BAM / TP              | ISO-TP              | ISO-TP（Mode 09 需扩展帧） |
| 会话/权限     | 无                       | 无                         | 有                  | 无                         |
| 典型设备      | 电机 / IO 模块 / 编码器  | 卡车 ECU / 发动机 / ABS    | 诊断仪 / OTA        | OBD-II 读取器              |
| 库内状态      | **L4 完整**              | **L4 完整**                | **L4 完整**         | **L4 完整**                |

> **OBD-II vs UDS 的关键区别**：OBD-II 是法规强制的只读最小集，不需要会话和种子密钥；UDS 是 OEM 定义的完整诊断体系。同一辆车上两者共存，OBD-II 走 0x7DF 功能寻址，UDS 走 OEM 物理寻址。

## 选型决策

```text
需要 CAN 之上选协议
│
├─ 工业设备互联 / 电机控制？
│   └─ CANopen（对象字典 + CiA 402）
│
├─ 商用车 / 工程机械网络？
│   └─ J1939（PGN/SPN + 地址声明）
│
├─ 读取故障码 / 刷写 ECU？
│   └─ UDS（ISO-TP 承载）
│
├─ 排放检测 / 二代诊断？
│   └─ OBD-II（Mode 01-09）—— 注意与 UDS 是两套体系，不是升级关系
│
└─ 单帧装不下数据？
    └─ ISO-TP（多帧 + 流控）—— UDS 和 OBD-II 的公共底座
```

## 文档索引

### basic/ — CAN 物理层与协议本体（9 篇）

| 文档                                   | 定位                                            |
| -------------------------------------- | ----------------------------------------------- |
| `basic/can-index.md`                   | CAN PHY / 控制器层导航                          |
| `basic/can-practical.md`               | 调试速查：终端电阻、can-utils、常见错误         |
| `basic/can-deep-dive.md`               | 帧格式、仲裁、错误处理、波特率与过滤器          |
| `basic/can-multimaster-and-bus-off.md` | 多主仲裁、TEC/REC、节点状态机与 Bus Off 恢复    |
| `basic/can-failure-cases.md`           | 21 个产线案例（详见文档）                       |
| `basic/can-fd-and-can-xl.md`           | CAN FD 关键改进、选型决策与 CAN XL              |
| `basic/can-rtos-integration.md`        | RTOS 集成与 Linux SocketCAN                     |
| `basic/can-vs-other-bus.md`            | CAN 与 I2C / SPI / UART / RS485 / Ethernet 对比 |
| `basic/can-phy.md`                     | 差分物理层与收发器基础                          |

### bus/automotive/ — CAN FD 与应用层协议

| 文档                                         | 定位                                          | 案例 |
| -------------------------------------------- | --------------------------------------------- | ---- |
| `bus/automotive/can.md`                      | CAN / CAN FD 概览入口                         | —    |
| `bus/automotive/can-fd-failure-cases.md`     | CAN FD 产线案例与排查（全库最大 CAN 文档）    | 21   |
| `bus/automotive/canopen.md`                  | CANopen 定位、对象字典、SDO/PDO               | —    |
| `bus/automotive/canopen-index.md`            | CANopen 主题导航                              | —    |
| `bus/automotive/canopen-practical.md`        | COB-ID、SDO/PDO/NMT 与电机调试                | —    |
| `bus/automotive/canopen-deep-dive.md`        | 位时序、PDO 映射、NMT 状态机与 CiA 402        | —    |
| `bus/automotive/canopen-failure-cases.md`    | Node ID 冲突 / 字节序 / PDO 映射 / NMT        | 12   |
| `bus/automotive/canopen-safety.md`           | CiA 304 / EN 50325-5：SRDO、SCT/SRVT、GFC     | —    |
| `bus/automotive/iso-tp.md`                   | ISO-TP 定位、帧类型与关键参数                 | —    |
| `bus/automotive/iso-tp-index.md`             | ISO-TP 主题导航                               | —    |
| `bus/automotive/iso-tp-practical.md`         | 多帧调试、流控、BS/STmin                      | —    |
| `bus/automotive/iso-tp-deep-dive.md`         | 序列号、超时与异常流控                        | —    |
| `bus/automotive/iso-tp-failure-cases.md`     | SF 边界 / BS 语义 / STmin / SN 环绕           | 12   |
| `bus/automotive/j1939.md`                    | J1939 概念入口                                | —    |
| `bus/automotive/j1939-index.md`              | J1939 主题导航                                | —    |
| `bus/automotive/j1939-protocol-spec.md`      | 标准号分层、报文类型、PGN/SPN 与 J1939-DA     | —    |
| `bus/automotive/j1939-practical.md`          | 29-bit ID、地址声明、DBC 与网关调试           | —    |
| `bus/automotive/j1939-deep-dive.md`          | NAME、PGN/SPN、多包与 DM 诊断                 | —    |
| `bus/automotive/j1939-network-management.md` | NAME 编码、Address Claimed、Commanded Address | —    |
| `bus/automotive/j1939-transport-protocol.md` | J1939-21：BAM 与 RTS/CTS                      | —    |
| `bus/automotive/j1939-failure-cases.md`      | 地址冲突 / DM 格式 / TP 丢包                  | 21   |
| `bus/automotive/uds.md`                      | UDS 定位、SID 服务表与 ISO-TP 关系            | —    |
| `bus/automotive/uds-index.md`                | UDS 主题导航                                  | —    |
| `bus/automotive/uds-practical.md`            | 会话、DID、DTC、安全访问与刷写                | —    |
| `bus/automotive/uds-deep-dive.md`            | 诊断状态机、刷写事务与 DoIP/网关边界          | —    |
| `bus/automotive/uds-failure-cases.md`        | 会话 / 种子密钥 / 刷写变砖 / BSC 循环         | 12   |
| `bus/automotive/obd2.md`                     | OBD-II 概览、Mode、PID 与 DTC                 | —    |
| `bus/automotive/obd2-index.md`               | OBD-II 主题导航                               | —    |
| `bus/automotive/obd2-deep-dive.md`           | PID 协商、I/M 模型、与 UDS 的边界             | —    |
| `bus/automotive/obd2-practical.md`           | ELM327 / SocketCAN 工具链与调试流程           | —    |
| `bus/automotive/obd2-failure-cases.md`       | 适配器 / 解码 / 多 ECU 响应 / readiness       | 12   |
| `bus/automotive/wwh-obd.md`                  | ISO 27145 分部分工、双链路与数据映射          | —    |
| `bus/automotive/wwh-obd-index.md`            | WWH-OBD 主题导航                              | —    |
| `bus/automotive/wwh-obd-deep-dive.md`        | 部分边界、24 位 DTC、初始化与 DoIP            | —    |
| `bus/automotive/wwh-obd-practical.md`        | 双链路选型、路由激活与 DTC 解析               | —    |
| `bus/automotive/wwh-obd-failure-cases.md`    | 链路识别 / 长寻址 / DTC 格式 / P2 超时        | 12   |
| `bus/automotive/lin.md`                      | LIN 概念、帧结构、调度与 LDF                  | —    |
| `bus/automotive/lin-practical.md`            | 主从调度、Break/Sync、Checksum                | —    |

### _Inbox/ — 待处理候选

6 份 CAN FD 候选待处理（流程见 [_Inbox/README.md](../../_Inbox/README.md)）：

| 文件                              | 日期       |
| --------------------------------- | ---------- |
| `CAN-FD-2026-09-27-candidates.md` | 2026-09-27 |
| `CAN-FD-2026-10-05-candidates.md` | 2026-10-05 |
| `CAN-FD-2026-10-08-candidates.md` | 2026-10-08 |
| `CAN-FD-2026-10-18-candidates.md` | 2026-10-18 |
| `CAN-FD-2026-10-23-candidates.md` | 2026-10-23 |
| `CAN-FD-2026-11-09-candidates.md` | 2026-11-09 |

`已处理/` 内另有 6 份历史候选（2026-08-13 至 2026-09-17）。

## 覆盖缺口

按 L0-L4 分级（L4 = 总览 + 实战 + 深度 + 故障案例 齐备；导航页可选）：

| 协议               | 现状 | 篇数   | 案例 | 判定      | 剩余缺口                                                                         |
| ------------------ | ---- | ------ | ---- | --------- | -------------------------------------------------------------------------------- |
| **CAN / CAN FD**   | L4   | 12     | 42   | ✅ 完整   | —                                                                                |
| **J1939**          | L4   | 8      | 21   | ✅ 完整   | —                                                                                |
| **CANopen**        | L4   | 5      | 12   | ✅ 完整   | —                                                                                |
| **UDS**            | L4   | 5      | 12   | ✅ 完整   | —                                                                                |
| **ISO-TP**         | L4   | 5      | 12   | ✅ 完整   | —                                                                                |
| **OBD-II**         | L4   | 5      | 12   | ✅ 完整   | —                                                                                |
| **WWH-OBD**        | L4   | 5      | 12   | ✅ 完整   | —                                                                                |
| **CAN XL**         | L2   | 0 独立 | 0    | 🟡 合并中 | 仅在 `basic/can-fd-and-can-xl.md` 内                                             |
| **CANopen-Safety** | L3   | 1      | 0    | 🟡 有专篇 | 有 `bus/automotive/canopen-safety.md`（SRDO / CRC / GFC），缺 failure-cases      |
| **LIN**            | L2   | 2      | 0    | 🟡 缺 FC  | 有 `bus/automotive/lin.md` + `bus/automotive/lin-practical.md`，缺 failure-cases |

> **案例数口径**：统一按 `^## 案例` 统计**真实实战案例数**。
>
> 早期报告用的 `^### ` 是**子小节数**（现象/抓包/定位/修复/复盘），会虚报 4.6 倍 —— 例如 `basic/can-failure-cases.md` 真实 21 例但 h3 有 100 个。本文所有数字已统一为 `^## 案例` 口径。

### 剩余建议补齐顺序

1. **CAN XL 独立笔记** — 等 CAN XL 量产落地再做，现在并入 `basic/can-fd-and-can-xl.md` 够用。
2. **CANopen-Safety failure-cases** — 专篇已有（`bus/automotive/canopen-safety.md`），下一步补 SRDO 配置 CRC 不符 / SRVT 超时 / 取反帧失配的产线案例。
3. **LIN failure-cases** — LIN 属车载低速分支，与 CAN 主线关联度低，按需补。

> 各协议独立 index 已于 2026-11-16 补齐：`can-index` / `can-fd-index` / `canopen-index` / `iso-tp-index` / `uds-index` / `obd2-index` / `wwh-obd-index`。

> 2026-10-31 已完成：ISO-TP / UDS / CANopen / OBD-II 四个协议的 failure-cases 全部补齐（各 12 例），OBD-II 从 L0 直接建到 L4；补齐 LIN 概念页；新增 `bus/automotive/can-standards-map.md` 标准规范总表。
>
> 2026-11-16 已完成：WWH-OBD 从 L3 升至 L4（新增 deep-dive / practical / failure-cases 各一篇，12 例）。

## 关联主题

- `basic/i2c-index.md` / `basic/spi-index.md` / `basic/uart-index.md` — 其他总线主题（结构对齐，见各 index 的对比表）
- `basic/can-vs-other-bus.md` — CAN 与其他总线的横向对比
- `bus/automotive/can-standards-map.md` — **CAN 家族标准规范总表**（按层 + 按协议 + 反查索引）
- `bus/automotive/iso-tp.md` — ISO-TP 入口
- `bus/automotive/uds.md` — UDS 入口
- `bus/automotive/obd2.md` — OBD-II 入口
- `bus/automotive/wwh-obd.md` — WWH-OBD 专篇（ISO 27145，商用车全球统一诊断）
- `bus/automotive/wwh-obd-deep-dive.md` — WWH-OBD 深度（数据模型 / 24 位 DTC / 初始化 / DoIP）
- `bus/automotive/wwh-obd-practical.md` — WWH-OBD 实战（初始化 / 路由激活 / DTC 解析）
- `bus/automotive/wwh-obd-failure-cases.md` — WWH-OBD 案例库（12 例）
- `bus/automotive/canopen-safety.md` — CANopen Safety 专篇（CiA 304 / EN 50325-5，SRDO）
- `bus/automotive/j1939-index.md` — J1939 导航
- `bus/automotive/j1939-protocol-spec.md` — J1939 协议规范层（标准号按层分解、报文类型、J1939-DA）
- `bus/automotive/lin.md` — LIN 概念页（车身低速，与 CAN 互补）
- `bus/automotive/lin-practical.md` — LIN 实战（主从调度、Break/Sync、Checksum、LDF）
- `LAYERED_MAP.md` — 全库分层地图
- `guides/learning/PROTOCOL_SELECTION.md` — 协议选型矩阵

## 一句话总结

CAN 家族分四层：物理层 CAN PHY、数据链路 CAN / CAN FD / CAN XL、传输层 ISO-TP、应用层 CANopen / J1939 / UDS / OBD-II / WWH-OBD。**截至 2026-11-16，七个主协议全部 L4 闭环**，failure-cases 实测共 123 例；剩余 3 项低优先级缺口：CAN XL 独立笔记、CANopen-Safety failure-cases、LIN failure-cases。

## 更新记录

- 2026-10-31: 初版。汇总 CAN 家族全部分层协议，标注各协议 L0-L4 覆盖状态，识别 4 个缺口（ISO-TP FC / UDS FC / CANopen FC / OBD-II 空白）。
- 2026-10-31: 补齐。新增 ISO-TP / UDS / CANopen 三个 failure-cases（各 12 例）与 OBD-II 四篇（概览 + 深度 + 实战 + 12 例），四个协议全部升至 L4；补齐 LIN 概念页。缺口表重算为 3 项低优先级待补。
- 2026-10-31: 规范与口径。新增 `bus/automotive/can-standards-map.md` 标准规范总表（按层 L0-L9 + 按协议，含 ISO 61 / SAE 21 / CiA 18 个标准号与 61 行反查索引）；修正 CAN XL（ISO 11898-1:2024）、OBD-II（SAE J1979）、J1939-84、J1939-81 四处标准号错误；**案例数口径统一为 `^## 案例`**（原 100/133 为 h3 子小节数，虚报 4.6 倍），实测 111 例；缺口表扩为 5 项（新增 CANopen-Safety / WWH-OBD 专篇）。
- 2026-11-02: 补齐两个专篇。新增 `bus/automotive/canopen-safety.md`（CiA 304 / EN 50325-5：SRDO 1-out-of-2 取反冗余、SCT/SRVT 双超时、CRC-16-CCITT 小端配置签名、GFC）与 `bus/automotive/wwh-obd.md`（ISO 27145-1/2/3/4/6 分工，DoCAN + DoIP 双链路，PID/MID/ITID → DID/RID/DTC 映射）；两项从 🔴 真空白升到 L3 有专篇。**修正 standards-map 的 ISO 27145-3 描述**（原写「UDS 服务子集」，实为标题是 Common message dictionary，UDS 子集只是其内容范围）并补入 **ISO 27145-6:2015 External test equipment**（原标准表完全漏了 Part 6）；注明 **ISO 27145-5 不存在**。剩余缺口 5 → 3 项。
- 2026-11-16: J1939 补规范层。新增 `bus/automotive/j1939-protocol-spec.md`，J1939 从 7 篇增至 **8 篇**，覆盖度仍为 L4（案例数不变）。补齐库内缺失的**协议规范层视角**：J1939 全系列标准号按物理/链路/传输/网络/管理/应用六层分解、5 种报文类型、PGN 全局/特定分类、EDP-DP 数据页对照表、8672 个 PGN 的容量计算、J1939-DA（Excel 而非 DBC）的来源、SPN 19 bit 范围与 SLOT 定义、DTC 的 SPN/FMI/OC/CM 字段、BAM 与 CM 的时序差异（50-200 ms vs 无限时）。
- 2026-11-16: WWH-OBD 补齐至 L4。新增 `bus/automotive/wwh-obd-deep-dive.md`（ISO 27145 各部分确切边界：-2 管数据 / -3 管服务 / -4 管连接；Annex A-E 结构；PID·MID·ITID→DID·RID 映射；**24 位 DTC 格式**与 SAE J2012-DA BaseDTC/FTB 及 J1939 SPN/FMI 的对齐；ISO 27145-4 §7.1.2/7.1.3 的 11 位与 29 位 CAN ID 验证程序；DoCAN/DoIP 双链路与 DoIP payload type 集）、`bus/automotive/wwh-obd-practical.md`（双链路选型、初始化脚本、DoIP 路由激活、24 位 DTC 解析、商用车产线与检测站场景）、`bus/automotive/wwh-obd-failure-cases.md`（12 例）。WWH-OBD 从 L3 升至 L4，failure-cases 实测总数 111 → **123 例**，缺口表剩余 3 项 → **2 项**。**核对 ISO 27145-2/-3/-4 与 ISO 13400-2 官方范围声明**，确认 -3 标题为 "Common message dictionary" 且其范围确为「ISO 14229-1 中 UDS 服务的子集实现」（原表述正确，无需修正）；补入 **ISO 15765-4:2021** 为现行第 4 版（时间参数统一为 `t_ParameterName`、`P2_CAN_max` 更正为 `Δt_P2_CAN_Client_Max`）与 **GB/T 39851.3-2021** 中国对应标准。

- 2026-11-16: 描述与索引整理。补齐 CAN 家族 7 个索引页，关闭“独立 index”缺口；精简协议矩阵、文档索引与覆盖表描述；候选数量按 `_Inbox` 实况更新（6 待处理 + 6 历史）；目录迁移至 `bus/automotive/`。
