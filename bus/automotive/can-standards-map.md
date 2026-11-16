---
tags:
  - layer/bus
  - type/overview
  - protocol/can
  - topic/automotive
---

# CAN 家族标准规范总表

## 目标

CAN 相关的标准**不止协议本身**。一个上车的 CAN 节点要过认证，牵涉物理层、数据链路层、诊断、排放法规、功能安全、网络安全、环境可靠性等十几个系列。

本文是 **CAN 家族标准号总索引**，提供两张主表：

- [## 按层总表](#按层总表) —— 每一层有哪些标准，各管什么
- [## 按协议总表](#按协议总表) —— 每个协议涉及哪些标准

配套阅读：

- `bus/automotive/can-protocol-family.md` —— CAN 家族协议全景与覆盖状态
- `basic/can-failure-cases.md` / `bus/automotive/can-fd-failure-cases.md` —— 物理层与链路层案例

## 使用方式

1. **做新项目** → 从「按协议总表」找到你的协议，横向看它涉及的所有层。
2. **过认证 / 送检** → 从「按层总表」按测试项目反查标准号。
3. **排查现场问题** → 先确认是协议层还是电气/环境层，再查对应标准。

> ⚠️ **标准版本会更新**。本文记录的是各系列的标准号与分工关系，不锁定小版本号。实际项目请以官网当前版本为准，并确认是否被新版替代。

---

## 按层总表

### L0 — 连接器与线束

| 标准 | 名称 | 管什么 |
| --- | --- | --- |
| ISO 15031-3 / SAE J1962 | 诊断连接器及相关电路 | OBD-II 16 针诊断口（D 型 / J 型）的针脚定义、电气要求 |
| SAE J1939-13 | 车载诊断连接器 | 卡车 / 工程机械的诊断口（DB9 / J1939 13 针） |

### L1 — 物理层（电气）

| 标准 | 名称 | 管什么 |
| --- | --- | --- |
| ISO 11898-2 | 高速 CAN 物理介质接入层 | 差分 CAN_H/CAN_L、终端电阻、位时序电气特性、唤醒 |
| ISO 11898-3 | 低速容错单线 CAN | LSFT CAN，线断也能继续通信（≤125 kbit/s） |
| ISO 11898-6 | 高速低功耗 CAN | 降低静态电流的收发器规范 |
| ISO 14950-2 | 单线 CAN 兼容物理层 | TJA1050 这类单线收发器规范 |
| ISO 11519 | 低速容错 CAN | 容错 CAN 的低速变体 |
| SAE J1939-11 | 250 kbit/s 物理层 | J1939 车载线束布线规则、双绞 120Ω |
| SAE J1939-14 | 500 kbit/s 物理层 | 部分工程机械使用的 500k 变体 |
| SAE J1939-15 | 简化物理层 | 轻型车/乘用车适用的低配布线 |
| CiA 601-4 | CAN SIC 收发器 | Signal Improvement Capability，抑制振铃，让 CAN FD/XL 能在非优化拓扑跑 |
| CiA 604-x | CAN FD Light | commander/responder 模式，成本敏感的传感器/执行器网络 |
| CiA 610-3 | CAN SIC XL 收发器 | CAN XL 用，支持 PWM 编码，10 Mbit/s+ |
| SAE J2284-1/-2/-3/-4 | CAN 物理层 | 北美体系下的 CAN 物理层规范 |
| ISO 17987 | LIN | 车载低速单线总线（与 CAN 互补） |

### L2 — 数据链路层

| 标准 | 名称 | 管什么 |
| --- | --- | --- |
| ISO 11898-1 | CAN 数据链路层与物理信号 | **核心标准**。经典 CAN / CAN FD / CAN XL 三代帧格式、仲裁、错误处理、CRC |
| Bosch CAN Spec 2.0 (1991) | 原始 CAN 规范 | ISO 11898-1 的前身，业界通用引用基准 |
| SAE J1939-21 | J1939 数据链路层 | 29-bit ID 编码、PGN 构成、TP 多包传输（BAM / RTS-CTS） |
| SAE J1939-22 | J1939 CAN FD 数据链路层 | J1939 跑在 CAN FD 上的变体 |
| SAE J1939-17 | CAN FD 物理层 | J1939 的 CAN FD 物理层扩展 |

### L3 — 传输层 / 网络层

| 标准 | 名称 | 管什么 |
| --- | --- | --- |
| ISO 15765-2 | DoCAN 传输协议与网络层服务 | **ISO-TP 本体**。SF/FF/CF/FC、BS、STmin、寻址方式 |
| ISO 15765-3 | DoCAN 网络层服务 | 网络管理、节点状态 |
| ISO 15765-4 | DoCAN 排放相关系统要求 | **OBD 用的 DoCAN**。诊断 CAN ID 格式与寻址规则（数据链路层）+ 诊断连接器针脚、波特率、位定时（物理层）。与 ISO 15031-5 冲突时**以 15031-5 为准** |
| ISO 20794-3 | 以太网上的传输与网络层 | UDS over Ethernet / DoIP 的传输层 |

### L4 — 网络管理

| 标准 | 名称 | 管什么 |
| --- | --- | --- |
| SAE J1939-81 | J1939 网络管理与地址声明 | NAME 字段、Address Claimed 协议、Commanded Address |
| SAE J1939-31 | J1939 网络层 | 网络布局与路由 |

### L5 — 应用层（诊断与设备模型）

| 标准 | 名称 | 管什么 |
| --- | --- | --- |
| ISO 14229-1 | UDS 应用层 | **UDS 规范与要求总纲**。SID 集、NRC、DID、DTC、Routine、刷写 |
| ISO 14229-2 | UDS 会话层服务 | 会话层接口，与传输层解耦 |
| ISO 14229-3 | UDS on CAN | UDS 在 CAN 上的实施约束 |
| ISO 14229-4 | UDS on FlexRay | FlexRay 承载 |
| ISO 14229-5 | UDS on IP | 以太网承载（与 DoIP 配套） |
| ISO 14229-6 | UDS on K-Line | K 线承载（老平台） |
| ISO 14229-7 | UDS on LIN | LIN 承载 |
| SAE J1979 / ISO 15031-5 | 排放相关诊断服务 | **OBD-II 本体**。Mode 01-09、PID 空间、I/M 监测。两者技术等同、平行出版 |
| SAE J1979-DA / J2012-DA / J1930-DA | SAE 数字附录 | **PID/MID/TID/INFOTYPE、DTC/FTB、术语的实际定义**，持续修订 |
| SAE J1979-2 / J1979-3 | OBDonUDS / ZEVonUDS | 2021 起把 OBD 数据改用 UDS（SID+DID）承载；-3 专为零排放动力系统 |
| ISO 15031-6 | 诊断故障码定义 | DTC 格式定义规则（引用 SAE J2012-DA） |
| ISO 15031-1 / -2 / -3 / -4 | OBD 通用信息、术语、连接器、测试设备 | OBD 体系的外围部分 |
| ISO 15031-7 | 数据链路安全性 | 数据链路层安全要求 |
| ISO 27145-1/-2/-3/-4/-6 | WWH-OBD | **全球统一车载诊断**，商用车 OBD 体系（见下方对比） |
| CiA 301 | CANopen 应用层与通信 Profile | **CANopen 本体**。对象字典、NMT、SDO/PDO、SYNC、EMCY、Heartbeat |
| CiA 1301 | CANopen FD 应用层 | CANopen 跑在 CAN FD 上（USDO 替代 SDO） |
| CiA 1302 | CANopen FD 附加应用层 | CiA 1302-1/-2 已定稿（2026-08 CiA 公告） |
| CiA 402 | 驱动与运动控制设备 Profile | CiA 402 电机状态机（Switch On Disabled → Operation Enabled） |
| CiA 304 / CiA 305 | CANopen Safety / LSS | 安全相关扩展 / 层设置服务 |
| CiA 306 | CANopen 电子数据表（EDS） | EDS 文件格式定义 |
| CiA 510 | CANopen ↔ J1939 映射 | 把 CANopen 的 SDO/EMCY 映射到 J1939 PGN |
| ISO 13400-2 / -3 / -4 | DoIP | 以太网上的诊断（传输层 / 数据链路层 / 连接器） |

### L6 — 一致性与互操作性测试

| 标准 | 名称 | 管什么 |
| --- | --- | --- |
| ISO 16845-1 | CAN 一致性测试方法学 | 检查 CAN 是否符合 ISO 11898-1 的方法与抽象测试套件 |
| ISO 16845-2 | 高速 MAU 一致性测试计划 | 具体的测试用例集（2018 版为现行） |

### L7 — 环境、可靠性与 EMC

| 标准 | 名称 | 管什么 |
| --- | --- | --- |
| ISO 16750-1 ~ -5 | 车载电气电子设备环境条件与试验 | 总则 / 电气负荷 / 机械负荷 / 气候负荷 / 化学负荷 |
| ISO 16750-2 | 电气负荷 | 过压、抛负载（load dump）、反接、短路、供电中断 |
| ISO 16750-3 | 机械负荷 | 振动、冲击、跌落 |
| ISO 16750-4 | 气候负荷 | 温度循环、湿热、太阳辐射 |
| ISO 16750-5 | 化学负荷 | 燃油、机油、清洗剂耐受 |
| ISO 7637-2 | 传导与耦合引起的电骚扰 | 电源线瞬态干扰（抛负载等），12V 系统最常引用的电气标准 |
| ISO 10605 | 静电放电 | 车规 ESD 试验方法 |
| CISPR 25 | 保护车载接收机的无线电骚扰特性 | 车载电子**发射**限值 |
| ISO 11452 | 辐射电磁能产生的骚扰（部件试验方法） | 车载电子**抗扰度** |
| ISO 11451 | 辐射电磁能产生的骚扰（整车试验方法） | 整车级抗扰度 |
| SAE J1455 | 重型车电子设备环境实践 | 商用车环境条件 |
| SAE J1113 | 电磁兼容试验方法 | 北美体系 |
| IEC 60068 系列 | 环境试验 | 通用环境试验基础 |
| AEC-Q100 / Q101 / Q200 | 车载级元器件认证 | IC / 分立器件 / 被动元件 |

### L8 — 功能安全与网络安全

| 标准 | 名称 | 管什么 |
| --- | --- | --- |
| ISO 26262 | 道路车辆功能安全 | ASIL 等级、HARA、FMEA/FMEDA、诊断覆盖率、安全机制 |
| ISO/SAE 21434 | 道路车辆网络安全工程 | TARA、威胁建模、CAN 注入攻击防护、SecOC |
| UNECE R155 | 网络安全管理法规 | 要求整车厂建立网络安全管理体系（CSMS） |
| UNECE R156 | 软件更新管理体系法规 | SUMS、OTA 合规 |
| ISO 24089 | 车载软件更新工程 | 软件更新流程与安全 |
| SAE J1939-91A | 车载网络接口安全建议 | J1939 侧的安全指引 |
| AUTOSAR | 汽车开放系统架构 | CanIf / CanTp / CanNm / PduR / Dcm / SecOC 等模块规范 |

### L9 — 排放法规与型式认证

| 法规 / 标准 | 地区 | 管什么 |
| --- | --- | --- |
| UNECE R10 | 欧洲/全球 | EMC 型式认证，含零部件 |
| EPA 40 CFR Part 85 | 美国 | OBD-II 法规要求 |
| CARB Title 1 Section 1968 | 美国加州 | 加州 OBD 附加要求 |
| Euro 5 / Euro 6 / Euro 7 | 欧盟 | 排放限值与 OBD 覆盖要求 |
| GB 18352 / GB 3847 | 中国 | 汽油车 / 柴油车排放限值与 OBD 要求 |
| GB/T 28046 | 中国 | 等同采用 ISO 16750 |
| GB/T 18655 | 中国 | 等同采用 CISPR 25 |
| GB/T 21437 | 中国 | 等同采用 ISO 7637 |
| GB/T 33014 | 中国 | 等同采用 ISO 11452 |

---

## 按协议总表

### CAN（经典）

| 层 | 标准 |
| --- | --- |
| 物理 | ISO 11898-2、ISO 11898-6、ISO 14950-2、ISO 11519、ISO 11898-3、SAE J2284-x |
| 数据链路 | **ISO 11898-1**、Bosch CAN Spec 2.0 |
| 一致性 | ISO 16845-1、ISO 16845-2 |
| 环境 | ISO 16750-1~5、ISO 7637-2、ISO 10605、CISPR 25、ISO 11452 |
| 安全 | ISO 26262、ISO/SAE 21434、UNECE R155/R156 |

### CAN FD

| 层 | 标准 |
| --- | --- |
| 数据链路 | ISO 11898-1（:2015 起含 CAN FD）、CI_A 604-x（CAN FD Light）、CiA 601-x（节点与系统设计） |
| 物理 | ISO 11898-2（高速数据段）、CiA 601-4（SIC 收发器） |
| 一致性 | ISO 16845-2（涵盖 CAN FD） |
| 备注 | CAN FD 节点可作为经典 CAN 节点工作；反向不成立（经典节点会破坏 FD 帧） |

### CAN XL

| 层 | 标准 |
| --- | --- |
| 数据链路 | **ISO 11898-1:2024**（第 3 版，整合原 CiA 610-1） |
| 物理 | **ISO 11898-2:2024**（第 4 版，整合原 CiA 610-3 SIC XL） |
| 特征 | 1–2048 字节数据场、>10 Mbit/s、分离仲裁 ID（11 bit）与接受场（32 bit）、SDT 字段标识上层协议 |
| 状态 | 2024 年正式进入 ISO；CiA 正推进 CAN XL 生态与 Webinar |
| 注意 | CAN XL 硬件可承载 TCP/UDP 与传统上层协议 |

### ISO-TP

| 层 | 标准 |
| --- | --- |
| 传输 | **ISO 15765-2**（核心） |
| 网络 | ISO 15765-3、ISO 15765-4 |
| 物理/链路 | ISO 11898-1、ISO 11898-2 |
| 承载 | UDS（ISO 14229-3）、OBD-II（ISO 15031-5 / SAE J1979）、WWH-OBD（ISO 27145） |

### UDS

| 层 | 标准 |
| --- | --- |
| 应用 | **ISO 14229-1**（总纲）、ISO 14229-2（会话层） |
| 承载变体 | ISO 14229-3（CAN）、ISO 14229-4（FlexRay）、ISO 14229-5（IP）、ISO 14229-6（K-Line）、ISO 14229-7（LIN） |
| 传输 | ISO 15765-2（CAN/DoCAN）、ISO 20794-3（以太网） |
| 以太网 | ISO 13400-2/-3/-4（DoIP） |
| 数据字典 | ODX / CDD（OEM 自定义格式） |
| 安全 | ISO 26262、ISO/SAE 21434、ISO 24089、UNECE R155/R156 |

### OBD-II（乘用车排放诊断）

| 层 | 标准 |
| --- | --- |
| 应用 | **SAE J1979 / ISO 15031-5**（核心，Mode 01-09、PID 空间。两者技术等同、平行出版） |
| 数据附录 | **SAE J1979-DA / J2012-DA / J1930-DA**（PID/MID/TID/INFOTYPE、DTC/FTB、术语的实际定义） |
| UDS 承载 | **SAE J1979-2**（OBDonUDS，燃烧车）/ **SAE J1979-3**（ZEVonUDS，零排放） |
| **承载 · DoCAN** | **ISO 15765-2 / ISO 15765-4** + ISO 11898-1/-2（MY2008 起美国强制） |
| **承载 · DoK-Line** | **ISO 14230-1 / -2 / -4**（KWP2000，5-baud 或 fast init） |
| **承载 · 遗留串行** | **ISO 9141-2**、SAE J1850（PWM 41.6 / VPW 10.4 kbit/s） |
| 会话层 | ISO 14229-2（借用于 DoCAN 与 DoK-Line；**不适用于 J1850 与 ISO 9141-2**） |
| 故障码 | ISO 15031-6（DTC 格式定义，引用 SAE J2012-DA） |
| 外围 | ISO 15031-1（信息）、-2（术语）、-3（连接器 = SAE J1962）、-4（测试设备） |
| 安全 | ISO 15031-7（数据链路安全性） |
| 传输 | ISO 15765-2、ISO 15765-4 |
| 物理/链路 | ISO 11898-1、ISO 11898-2 |
| 法规 | EPA 40 CFR Part 85、CARB Title 1 §1968、Euro 5/6、GB 18352 |
| 中国对应 | GB/T 42193 系列（如 GB/T 42193.5-2026 ≡ ISO 15031-5:2015） |
| 体系 | **仅乘用车**；商用车看 ISO 27145 |

### WWH-OBD（商用车全球统一诊断）

| 层 | 标准 |
| --- | --- |
| 应用 | **ISO 27145-3**（Common message dictionary，通用消息字典；内容为 UDS 服务子集） |
| 数据字典 | ISO 27145-2（Common data dictionary，通用数据字典，DTC/DID/RID 定义与 PID/MID/ITID 映射） |
| 框架 | ISO 27145-1（General information and use case definition） |
| 连接器 | ISO 27145-4（Connection between vehicle and test equipment，体系入口点） |
| 测试设备 | ISO 27145-6（External test equipment） |
| 会话层 | ISO 14229-2 |
| 传输 | ISO 13400-2（DoIP）、ISO 15765-2 + ISO 15765-4（DoCAN，2021 第 4 版） |
| 链路 | ISO 13400-3、ISO 11898-1 |
| 物理 | ISO 11898-2 |
| 法规 | GTR No. 5（全球重型车 OBD 技术法规） |
| 商用车网络 | SAE J1939、SAE J1939-73（诊断应用层）、SAE J1939-DA |
| 数字附录 | SAE J1979-DA、SAE J2012-DA（DTC 定义） |

> ⚠️ **ISO 27145-5 不存在**，系列为 1/2/3/4/6。

### CANopen

| 层 | 标准 |
| --- | --- |
| 应用 | **CiA 301**（核心，EN 50325-4 对应） |
| CANopen FD | CiA 1301、CiA 1302-1/-2 |
| 设备 Profile | CiA 402（驱动）、CiA 401（I/O）、CiA 404~434（各类设备接口） |
| 安全 | CiA 304（CANopen Safety，SRDO 冗余传输 → EN 50325-5）、CiA 305（LSS） |
| 描述文件 | CiA 306（EDS）、CiA 1311（XDD） |
| 桥接 | CiA 302（附加应用层）、CiA 510（→ J1939 PGN 映射） |
| 环境/安全 | ISO 16750、ISO 26262（按工业或车载场景选） |

### J1939

| 层 | 标准 |
| --- | --- |
| 数据链路 | **SAE J1939-21**（29-bit ID、PGN、TP） |
| CAN FD | SAE J1939-22（数据链路）、SAE J1939-17（物理） |
| 网络层 | SAE J1939-31 |
| 网络管理 | SAE J1939-81（NAME、地址声明） |
| 应用层 | SAE J1939-71（车辆应用层）、SAE J1939-73（诊断 DM1/DM2）、SAE J1939-84（越野 OBD 合规） |
| 物理 | SAE J1939-11（250k）、-14（500k）、-15（简化）、SAE J2284-x |
| 连接器 | SAE J1939-13 |
| 安全 | SAE J1939-91A |
| 合规 | SAE J1939-01/02（合规性）、EPA/CARB 重型车法规 |

### LIN

| 层 | 标准 |
| --- | --- |
| 全部 | **ISO 17987**（物理 + 数据链路 + 应用层一体化） |
| 诊断 | ISO 14229-7（UDS on LIN） |
| 环境 | ISO 16750、ISO 7637-2 |

---

## OBD-II vs WWH-OBD vs UDS：最容易搞混的一组

这是车载诊断里最常见的混淆。三者**不是版本升级关系，而是并列体系**：

| 维度 | OBD-II | WWH-OBD | UDS |
| --- | --- | --- | --- |
| 标准 | SAE J1979 / ISO 15031-5 | ISO 27145 | ISO 14229 |
| 适用 | 乘用车 | 商用车 | 全车系（OEM 诊断） |
| 性质 | **法规强制** | **法规强制** | OEM 规范 |
| 内容 | Mode 01-09 固定 PID | UDS 服务子集 | 完整服务集 |
| DTC | 2 字节 | **3 字节（24 bit）** | 2 字节 / 3 字节 |
| 会话/权限 | 无 | 有（ISO 14229-2 会话层） | 有 |
| 读数据 | PID 固定编号 | WWH-OBD 通用数据字典 | DID 自由定义 |
| 谁能用 | 任何 OBD 扫描器 | 商用车专用 | 需 OEM 诊断规范 |

关键关系：

```text
OBD-II (SAE J1979)  ──┐
                      ├── 法规诊断，面向用户和年检
WWH-OBD (ISO 27145) ──┘

UDS (ISO 14229) ──── OEM 诊断，面向售后、产线、OTA
```

WWH-OBD 在表示层和应用层借用了 UDS 的机制（ISO 27145-3 定义的是 **UDS 服务的子集**），会话层直接用 ISO 14229-2，传输层用 ISO 13400-2（DoIP）或 ISO 15765-2（CAN）。

---

## 物理层选型速查

| 需求 | 物理层标准 | 典型收发器 | 说明 |
| --- | --- | --- | --- |
| 经典高速 CAN | ISO 11898-2 | TJA1050、SN65HVD230、TCAN1042 | 最通用 |
| 低功耗经典 CAN | ISO 11898-6 | TJA1051/T/3、TJA1041/T/3 | 静态电流低 |
| 5V 供电经典 CAN | ISO 11898-2 | TJA1443 | 收发器直接用 5V |
| CAN FD | ISO 11898-2 | TJA1044、TCAN1044/1042 | 需 FD 认证 |
| CAN FD + 振铃抑制 | ISO 11898-2 + CiA 601-4 | SIC 收发器 | 非优化拓扑跑 FD |
| CAN XL | ISO 11898-2:2024 | SIC XL | 10 Mbit/s+ |
| 低速容错 | ISO 11898-3 / ISO 11519 | TJA1021/T/3 | 线断可继续通信 |
| 单线 CAN | ISO 14950-2 | TJA1050 | 成本极低 |

**终端电阻**：高速 CAN 总线两端各一个 120Ω，断电测 CANH-CANL 约 60Ω。ISO 11898-2 规定的是 120Ω ±5%（部分 OEM 规范放宽到 ±1%）。

---

## 工程上"标准管不到"的部分

标准只规定"必须做什么"，不规定"怎么排障"。以下内容属于工程实践，不在任何标准覆盖范围内：

- 终端电阻的**实际安装工艺**（压接、阻值一致性、位置）。
- 走线拓扑与**分支长度**的现场约束。
- 采样点与 SJW 的**具体取值**（标准只给范围）。
- CAN ID / PGN / COB-ID 的**分配策略**。
- 对象字典与诊断数据库的**版本治理**。
- 跨 OEM 的**协议差异适配**。
- 抓包日志的**字段规范**与可观测性建设。

这些在 `basic/can-failure-cases.md`、`bus/automotive/can-fd-failure-cases.md`、`bus/automotive/canopen-failure-cases.md` 等案例库里体现。

---

## 标准号反查索引

| 标准号 | 属于 | 管什么 |
| --- | --- | --- |
| Bosch CAN Spec 2.0 | CAN | 原始 CAN 规范 |
| ISO 11519 | CAN | 低速容错 CAN |
| ISO 11898-1 | CAN/FD/XL | 数据链路层核心 |
| ISO 11898-2 | CAN/FD/XL | 物理层 |
| ISO 11898-3 | CAN | 低速容错单线 |
| ISO 11898-6 | CAN | 高速低功耗 |
| ISO 14950-2 | CAN | 单线 CAN 物理层 |
| ISO 15765-1 | ISO-TP | 总览与用例 |
| ISO 15765-2 | ISO-TP | 传输协议 |
| ISO 15765-3 | ISO-TP | 网络层服务 |
| ISO 15765-4 | ISO-TP | DoCAN 排放相关系统要求（诊断 CAN ID / 针脚 / 波特率） |
| ISO 14230-1 / -2 / -4 | KWP2000 / DoK-Line | 物理层 / 数据链路层 / 排放相关系统要求。**OBD 的 K 线承载** |
| ISO 9141-2 | 遗留 K 线 | 老式单线串行诊断，5-baud 初始化。**OBD 的早期 K 线承载** |
| SAE J1850 | 遗留单线总线 | J1850 PWM (41.6 kbit/s) / VPW (10.4 kbit/s)。OBD 的美系承载 |
| ISO 14229-1 ~ -7 | UDS | UDS 各承载变体 |
| ISO 15031-1 ~ -7 | OBD-II | 乘用车排放诊断 |
| ISO 27145-1 ~ -4, -6 | WWH-OBD | 商用车全球统一诊断（-5 不存在） |
| ISO 16845-1/-2 | CAN | 一致性测试 |
| ISO 16750-1 ~ -5 | 通用 | 环境条件与试验 |
| ISO 7637-2 | 通用 | 传导电骚扰 |
| ISO 10605 | 通用 | 静电放电 |
| ISO 11452 | 通用 | 辐射抗扰度（部件） |
| ISO 11451 | 通用 | 辐射抗扰度（整车） |
| CISPR 25 | 通用 | 车载发射限值 |
| ISO 26262 | 通用 | 功能安全 |
| ISO/SAE 21434 | 通用 | 网络安全 |
| ISO 24089 | 通用 | 软件更新工程 |
| ISO 17987 | LIN | LIN 全栈 |
| ISO 13400-2/-3/-4 | DoIP | 以太网诊断 |
| ISO 20794-3 | DoIP | 以太网传输与网络层 |
| SAE J1939-01/02 | J1939 | 合规性 |
| SAE J1939-11/14/15/17 | J1939 | 物理层各变体 |
| SAE J1939-13 | J1939 | 诊断连接器 |
| SAE J1939-21/22 | J1939 | 数据链路层 |
| SAE J1939-31 | J1939 | 网络层 |
| SAE J1939-71 | J1939 | 车辆应用层 |
| SAE J1939-73 | J1939 | 诊断 |
| SAE J1939-81 | J1939 | 网络管理 |
| SAE J1939-84 | J1939 | 越野 OBD 合规 |
| SAE J1939-91A | J1939 | 网络安全 |
| SAE J1962 / ISO 15031-3 | OBD-II | 诊断连接器 |
| SAE J1979 | OBD-II | 排放诊断服务 |
| SAE J1979-2 | OBD-II | OBDonUDS（UDS 承载的 OBD，燃烧车） |
| SAE J1979-3 | OBD-II | ZEVonUDS（零排放动力系统 on UDS） |
| SAE J1979-DA / J2012-DA / J1930-DA | OBD-II | SAE 数字附录（PID/DTC/术语数据定义） |
| SAE J2284-1 ~ -4 | CAN | 北美物理层 |
| SAE J1455 / J1113 | 通用 | 商用车环境 / EMC 方法 |
| CiA 301 | CANopen | 应用层核心 |
| CiA 302/304/305/306 | CANopen | 附加功能 / 安全 / LSS / EDS |
| CiA 401 ~ 434 | CANopen | 设备 Profile |
| CiA 402 | CANopen | 驱动与运动控制 |
| CiA 510 | CANopen | 到 J1939 的映射 |
| CiA 601-x | CAN FD | 节点系统设计 / SIC 收发器 |
| CiA 604-x | CAN FD | CAN FD Light |
| CiA 610-1/-3 | CAN XL | 数据链路 / 物理层（已并入 ISO 11898） |
| CiA 1301 / 1302 | CANopen FD | 应用层 |
| CiA 1311 | CANopen | XDD 描述文件 |
| EN 50325-4 | CANopen | CANopen 通信协议（欧洲 EN 对应件，对应 CiA 301） |
| EN 50325-5 | CANopen | CANopen 安全（对应 CiA 304） |
| SAE J2012-DA | OBD-II | 诊断故障码定义（被 ISO 15031-6 引用） |
| GTR No. 5 | WWH-OBD | 全球重型车 OBD 技术法规（WWH-OBD 的法规落地） |
| UNECE R10 | 通用 | EMC 型式认证（含零部件） |
| UNECE R155 | 通用 | 网络安全管理法规（CSMS） |
| UNECE R156 | 通用 | 软件更新管理体系法规（SUMS / OTA） |

---

## 关联主题

- `bus/automotive/can-protocol-family.md` —— CAN 家族协议全景与 L0-L4 覆盖状态
- `bus/automotive/can-fd-failure-cases.md` —— CAN FD 产线案例
- `basic/can-failure-cases.md` —— CAN 物理层 / 链路层案例
- `basic/can-index.md` —— CAN 主题导航
- `bus/automotive/obd2.md` —— OBD-II 概览
- `bus/automotive/wwh-obd.md` —— WWH-OBD（ISO 27145）商用车全球统一诊断
- `bus/automotive/wwh-obd-deep-dive.md` —— WWH-OBD 深度（24 位 DTC / PID→DID 映射 / 初始化 / DoIP）
- `bus/automotive/uds.md` —— UDS 概览
- `bus/automotive/canopen.md` —— CANopen 概览
- `bus/automotive/canopen-safety.md` —— CANopen Safety（CiA 304 / EN 50325-5）
- `bus/automotive/iso-tp.md` —— ISO-TP 概览
- `bus/automotive/j1939-index.md` —— J1939 导航
- `bus/automotive/lin.md` —— LIN 概念
- `LAYERED_MAP.md` —— 全库分层地图
- `reference/ACRONYMS.md` / `reference/GLOSSARY.md` —— 术语表

## 更新记录

- 2026-10-31: 初版。按层（连接器/物理/链路/传输/网络/应用/测试/环境/安全/法规）和按协议（CAN/FD/XL/ISO-TP/UDS/OBD-II/WWH-OBD/CANopen/J1939/LIN）两张维度汇总标准号，附 OBD-II vs WWH-OBD vs UDS 对比、物理层收发器选型、标准号反查索引。
