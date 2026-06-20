# EtherNet/IP Deep Dive

## 目标

本文深入 EtherNet/IP 的协议结构和设备实现边界，重点覆盖 CIP 对象模型、Encapsulation、显式消息、隐式 IO、Connection Manager、Forward Open、Assembly、RPI、EDS、一致性测试和现场深度排查。

本文不重复基础接入步骤，而是回答这些问题：

- EtherNet/IP 为什么不是简单 TCP 私有协议。
- CIP 对象模型如何组织设备能力。
- TCP 44818、UDP 2222 和 Encapsulation 分别承担什么。
- Forward Open 为什么决定 IO 连接能否建立。
- Assembly 和 EDS 如何共同决定 PLC 的 IO 数据长度。
- RPI、连接资源和超时如何影响稳定性。
- 实现设备时哪些内容必须和 EDS、固件、协议栈一致。

## 分层模型

EtherNet/IP 可按以下层次理解：

```text
Ethernet PHY/MAC
        |
IP / ARP / TCP / UDP
        |
EtherNet/IP Encapsulation
        |
CIP Message Router / Connection Manager
        |
CIP Objects：Identity / Assembly / TCP-IP / Ethernet Link / Vendor Objects
        |
Device Application：IO、参数、诊断、控制逻辑
```

关键点：

- EtherNet/IP 使用标准以太网和 TCP/UDP/IP。
- 工业语义来自 CIP，不来自普通 IP 层。
- 周期 IO 依赖连接管理和 Assembly 映射。
- 显式消息和隐式消息使用不同通信模型。

## EtherNet/IP Encapsulation

EtherNet/IP Encapsulation 是运行在 TCP/UDP 之上的封装层。

常见用途：

- 注册和管理会话。
- 发送 CIP 显式消息。
- 发现设备身份。
- 承载连接建立请求。

常见命令：

| 命令 | 用途 |
| --- | --- |
| ListIdentity | 发现设备身份 |
| RegisterSession | 建立显式消息会话 |
| UnRegisterSession | 注销会话 |
| SendRRData | 发送未连接显式消息 |
| SendUnitData | 发送连接相关数据 |
| ListServices | 查询服务能力 |

工程意义：

```text
TCP 连上 44818
不代表 CIP 消息已经可用
必须 Register Session 成功
再看 CIP 路径、服务和对象响应
```

常见问题：

| 现象 | 根因方向 |
| --- | --- |
| TCP 44818 能连但无响应 | Encapsulation Header、Session、命令格式 |
| Register Session 失败 | 协议版本、资源、协议栈状态 |
| List Identity 不出现 | UDP/TCP 发现路径、网段、防火墙、设备栈未启动 |

## CIP 对象模型

CIP 用对象模型表达设备能力。

基本路径：

```text
Class -> Instance -> Attribute
```

常见操作：

```text
Service -> Object Path -> Request Data -> Response Data
```

常用对象：

| 对象 | 作用 |
| --- | --- |
| Identity Object | 厂商、设备类型、产品代码、版本、状态 |
| Message Router | 路由显式消息到目标对象 |
| Assembly Object | 输入、输出、配置数据集合 |
| Connection Manager | 建立、关闭和管理连接 |
| TCP/IP Interface Object | IP、子网、网关、地址配置方式 |
| Ethernet Link Object | MAC、链路状态、速率、双工、接口计数 |

对象模型设计要稳定。工程工具、EDS、PLC 工程和上位机脚本都可能依赖这些 Class、Instance、Attribute。

## Identity Object

Identity Object 是设备识别基础。

常见属性：

- Vendor ID。
- Device Type。
- Product Code。
- Revision。
- Status。
- Serial Number。
- Product Name。

工程要求：

- 与 EDS 中声明一致。
- 固件升级时 Revision 策略明确。
- Product Code 不随意改变。
- Status 能反映主要设备状态。

如果 Identity 与 EDS 不一致，工程工具可能显示 Unknown Device 或拒绝建立正确 IO 连接。

## EDS 和设备模型

EDS 是 Electronic Data Sheet。

它描述：

- 设备身份。
- 支持的连接。
- Assembly Instance。
- IO 数据大小。
- 参数。
- 配置项。
- 图标和显示信息。

EDS 与固件之间的关键一致性：

```text
EDS Identity == Identity Object
EDS Assembly Instance == 固件 Assembly Object
EDS IO Size == 固件实际输入输出长度
EDS Connection Parameters == Connection Manager 支持能力
```

常见错误：

- EDS 更新了，但固件 Assembly 没更新。
- 固件新增字段，但 EDS IO Size 没改。
- Product Revision 不匹配。
- 参数枚举值和设备实际实现不一致。
- 工程项目缓存了旧 EDS。

## 显式消息

显式消息用于低频配置、诊断和参数访问。

典型路径：

```text
Register Session
SendRRData
CIP Service
Message Router
Target Object
Response Status
```

常见服务：

| Service | 作用 |
| --- | --- |
| Get Attribute Single | 读取属性 |
| Set Attribute Single | 写入属性 |
| Get Attribute All | 读取多个属性，视对象支持 |
| Reset | 复位对象或设备 |

显式消息错误定位：

- Encapsulation 是否成功。
- Session Handle 是否有效。
- CIP Path 是否正确。
- Service 是否支持。
- Attribute 是否存在。
- 当前状态是否允许写入。
- Request Data 长度和类型是否正确。

显式消息不适合高频控制。如果需要周期控制，应使用隐式 IO。

## 隐式 IO

隐式 IO 用于周期实时数据交换。

典型特征：

- 基于连接。
- 周期发送。
- 数据含义由 Assembly 和 EDS 定义。
- 常通过 UDP 2222 承载。
- 对 RPI、超时和连接资源敏感。

数据方向要站在 PLC 视角确认：

```text
Input：Device -> PLC
Output：PLC -> Device
Configuration：PLC -> Device，连接建立或配置时使用
```

设备侧要明确：

- Output 到达后何时生效。
- Input 何时采样和更新。
- 通信断开后输出策略。
- 数据有效位和故障位如何表达。
- 多连接场景是否允许。

## Assembly Object

Assembly Object 是周期 IO 的数据集合。

常见实例：

```text
Input Assembly Instance
Output Assembly Instance
Configuration Assembly Instance
```

设计 Assembly 时要注意：

- 字节长度稳定。
- 字段偏移明确。
- 字节序明确。
- 保留字段预留。
- 状态字和控制字定义清晰。
- 版本演进有兼容策略。

示例：

```text
Input Assembly 101, 12 bytes
0..1：Status Word
2..3：Actual Speed
4..7：Actual Position
8..11：Fault Flags

Output Assembly 100, 8 bytes
0..1：Control Word
2..3：Target Speed
4..7：Target Position
```

常见问题：

| 现象 | 根因方向 |
| --- | --- |
| PLC 显示 IO 长度不匹配 | EDS Size、Assembly Instance、固件长度 |
| 数据错位 | 字节序、结构体对齐、保留字段、PLC 数据类型 |
| 输出无效 | 连接未建立、Run/Idle 状态、设备状态机未使能 |

## Connection Manager

Connection Manager 负责连接建立和管理。

关键能力：

- Forward Open。
- Large Forward Open，适用于更大连接参数场景。
- Forward Close。
- 连接超时。
- 连接资源管理。

PLC 建立 IO 通信时，通常会发起 Forward Open。

Forward Open 关注：

- O->T 和 T->O 数据大小。
- RPI。
- 连接类型。
- Transport Class。
- Connection Path。
- Assembly Instance。
- Timeout 参数。

失败时优先看：

- General Status。
- Extended Status。
- Requested Packet Interval 是否支持。
- 数据大小是否和 Assembly 匹配。
- 连接路径是否指向正确对象。
- 设备连接资源是否耗尽。

## RPI、超时和资源

RPI 是 Requested Packet Interval。

RPI 不是越小越好。

影响因素：

- 设备 CPU 负载。
- 协议栈处理能力。
- 网络负载。
- PLC 扫描周期。
- 输出控制实时性要求。
- 设备允许的最小周期。

工程策略：

- 首次调试使用保守 RPI。
- 稳定后逐步降低。
- 记录最小支持 RPI 和推荐值。
- 多连接场景评估总负载。
- 超时后必须释放连接资源。

常见连接类型：

- Exclusive Owner：控制输出，通常只允许一个控制器。
- Input Only：只接收设备输入。
- Listen Only：监听已有连接数据，依赖 owner 存在。

多控制器冲突经常来自连接类型和资源策略不清。

## Run/Idle 和输出安全

EtherNet/IP IO 数据常涉及 Run/Idle 状态。

设备要明确：

- PLC Run 时输出是否生效。
- PLC Idle / Program 时输出如何处理。
- 连接断开时输出保持、清零还是进入安全值。
- 设备内部故障时是否忽略输出。
- 是否需要独立安全功能，不能只靠通信协议保证。

输出策略应写入设备手册、EDS 说明和测试用例。

## TCP/IP Interface 和 Ethernet Link

网络相关对象用于配置和诊断链路。

TCP/IP Interface 关注：

- IP 地址。
- 子网掩码。
- 网关。
- DHCP / BOOTP / 静态配置。
- 主机名，视实现而定。

Ethernet Link 关注：

- MAC 地址。
- 链路状态。
- 速率。
- 双工模式。
- 接口计数。
- 物理错误统计。

现场问题中，链路正常但 IO 不正常很常见；也可能 IO 抖动根因来自链路错误计数或半双工配置问题。

## 诊断和状态码

CIP 响应包含 General Status 和可能的 Extended Status。

定位思路：

- General Status 看大类错误。
- Extended Status 看连接、路径或资源细节。
- 同时对照 PLC 诊断、设备日志和抓包。

常见方向：

| 现象 | 优先检查 |
| --- | --- |
| Path Segment Error | CIP 路径、Class/Instance/Attribute |
| Service Not Supported | 目标对象是否支持该服务 |
| Attribute Not Supported | Attribute ID 是否存在 |
| Invalid Attribute Value | 写入值范围或数据类型 |
| Connection Failure | Assembly、RPI、资源、连接类型 |
| Resource Unavailable | 连接数、内存、协议栈资源 |

不要只看 PLC UI 的简短错误，应抓包查看 CIP 状态码和 Extended Status。

## EDS 版本和兼容性

产品发布后，EDS 和固件需要版本策略。

建议：

- EDS 文件名包含产品和版本。
- 固件 Release Note 说明对应 EDS。
- IO 数据长度变化视为兼容性风险。
- Product Code 和 Major Revision 改动要谨慎。
- 新增可选参数优先保持旧工程可用。
- 工程工具缓存旧 EDS 时要给出清理指导。

如果必须破坏兼容性，应明确迁移路径和升级步骤。

## 设备实现架构

典型设备软件分层：

```text
Ethernet Driver
TCP/IP Stack
EtherNet/IP Adapter Stack
CIP Object Model
Assembly Mapping
Application IO Buffer
Parameter / Diagnostics Manager
Nonvolatile Configuration
Logging / Factory Test
```

关键边界：
- 协议栈处理 Encapsulation、CIP、连接和超时。
- 对象模型提供稳定的 Class/Instance/Attribute。
- Assembly Mapping 保证 EDS 与应用数据一致。
- 应用层负责真实 IO、状态机和故障策略。
- 日志系统负责关联 PLC 错误、CIP 错误和内部状态。

## 一致性和认证

EtherNet/IP 产品通常需要关注 ODVA 一致性要求和生态兼容性。

测试关注：

- Encapsulation 行为。
- CIP 对象实现。
- Identity 信息。
- EDS 一致性。
- 连接建立和释放。
- RPI 和超时。
- 异常报文处理。
- 多控制器和资源限制。
- 长时间稳定性。

工程上应保存：

- 协议栈版本。
- EDS 版本。
- 固件版本。
- 已验证 PLC 和工具版本。
- 测试报告。
- 已知限制。

不要在认证或客户验证后随意改变 Assembly、连接参数或 Identity。

## Wireshark 深度分析

常用过滤：

```text
enip
cip
tcp.port == 44818
udp.port == 2222
ip.addr == <device-ip>
eth.addr == <device-mac>
```

分析顺序：

1. List Identity 是否能发现设备。
2. TCP 44818 是否建立。
3. Register Session 是否成功。
4. 显式消息 CIP Path 和 Service 是否正确。
5. Forward Open 是否发出。
6. Forward Open 响应状态码是什么。
7. UDP 2222 是否周期收发。
8. IO 周期是否稳定，是否出现丢包或抖动。
9. 连接关闭、超时和恢复是否符合预期。

抓包技巧：

- 保存 PLC 下载工程前后的完整抓包。
- 把 PLC 诊断时间点和抓包时间对齐。
- 对比成功设备和失败设备的 Forward Open 参数。
- 对比 EDS 中的 Assembly 与抓包中的连接参数。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 工具找不到设备 | List Identity、网卡、防火墙、IP、协议栈状态 |
| EDS 安装后仍未知 | Identity、Vendor ID、Product Code、Revision |
| 显式读写失败 | CIP Path、Service、Attribute、权限、数据长度 |
| IO 连接失败 | Forward Open、Assembly、RPI、连接类型、资源 |
| IO 运行中掉线 | RPI 过小、网络抖动、设备负载、超时策略 |
| 数据错位 | Assembly 映射、字节序、结构体对齐、EDS Size |
| 多控制器冲突 | Exclusive Owner、Input Only、Listen Only、资源限制 |
| 修改 IP 后异常 | TCP/IP Interface、BOOTP/DHCP、工具缓存、网段规划 |

## 深度检查清单

- Identity Object 与 EDS 一致。
- EDS Assembly Instance 和固件一致。
- Input / Output / Configuration 长度一致。
- Forward Open 支持的连接类型明确。
- RPI 最小值、推荐值和拒绝策略明确。
- 连接超时后资源释放正确。
- Run/Idle 和通信断开输出策略明确。
- CIP 错误码和设备日志可对应。
- TCP/IP Interface 和 Ethernet Link 对象可用于现场诊断。
- 协议栈、EDS、固件和认证版本可追溯。
- Wireshark 能看到 Register Session、Forward Open 和 UDP 2222 周期流量。

## 与 PROFINET 的差异

EtherNet/IP 以 CIP 对象模型为核心，工程调试围绕 EDS、Assembly、Forward Open、RPI 和连接资源展开。

PROFINET 以 GSDML、Device Name、DCP、AR/CR、PNIO 和 PLC 诊断为核心。

二者都不是“能 ping 通就算通”，也都需要设备描述文件与固件实现严格一致。

## 延伸阅读

- `bus/ethernet-ip.md`
- `bus/ethernet-ip-practical.md`
- `bus/profinet-deep-dive.md`
- `bus/industrial-ethernet-comparison.md`
- `bus/ethernet-deep-dive.md`
