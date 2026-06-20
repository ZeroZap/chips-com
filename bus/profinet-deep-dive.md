# PROFINET Deep Dive

## 目标

本文深入 PROFINET 的工程架构和实现边界，重点覆盖 DCP、GSDML、AR/CR、周期 IO、诊断模型、RT/IRT、网络拓扑、协议栈集成、认证和量产排查。

本文不重复基础接线步骤，而是回答这些问题：

- 为什么 ping 通不代表 PROFINET 通。
- 为什么 Device Name 比 IP 更关键。
- GSDML 如何影响 PLC 组态和 IO 长度。
- PLC 与设备如何建立应用关系和周期通信。
- RT/IRT 的能力边界在哪里。
- 实现 PROFINET 设备时哪些内容不能靠普通 TCP/IP 代码拼出来。

## 分层模型

PROFINET 不是单一 TCP 应用协议。

工程上可按以下层次理解：

```text
Ethernet PHY/MAC
        |
二层发现和链路信息：DCP / LLDP
        |
IP 配置和普通网络服务：IP / ARP / TCP / UDP
        |
PROFINET 应用关系：AR / CR / IO / Alarm / Record
        |
PLC 工程组态：GSDML / Module / Submodule / Slot / Subslot
        |
设备应用：输入输出、诊断、参数、状态机
```

关键点：

- 设备发现和命名依赖二层机制。
- 周期 IO 不是普通 socket 收发。
- 工程组态决定 PLC 对设备结构和数据长度的理解。
- 设备实现要同时满足协议栈、应用映射和认证要求。

## 设备身份

PROFINET 设备需要稳定、一致的身份信息。

常见身份字段：

- Vendor ID。
- Device ID。
- Device Type。
- Order Number。
- Serial Number。
- Hardware Revision。
- Software Revision。
- Station Name，也就是 Device Name。

身份信息至少要满足：

- 与 GSDML 一致。
- 与固件版本策略一致。
- 可被工程工具识别。
- 现场换件后有明确命名和恢复策略。

不要随意改变 Vendor ID、Device ID 或模块结构，否则旧 PLC 工程可能无法继续识别设备。

## DCP

DCP 是 Discovery and Configuration Protocol。

常见用途：

- Identify：发现在线设备。
- Set：设置 Device Name 或 IP 参数。
- Get：读取设备标识和配置。
- Reset：恢复出厂或重置通信参数，取决于设备支持。

DCP 的工程意义：

```text
PLC 或工程工具先按二层扫描设备
再根据 MAC 和设备类型确认目标
然后写入 Device Name 和 IP 参数
最后 PLC 按组态中的 Device Name 找到设备
```

常见问题：

| 现象 | 根因方向 |
| --- | --- |
| 扫不到设备 | 二层不通、网卡绑定错、防火墙、协议栈未启动 |
| 能扫到但不能命名 | 设备写保护、名称格式、DCP Set 被拒绝 |
| 命名成功但 PLC 不连 | PLC 组态名称不一致、GSDML 不匹配、模块不匹配 |
| 换设备后异常 | 新设备 MAC 变化、旧名称未写入、现场工具未重新分配 |

Device Name 是 PLC 绑定设备的重要依据。IP 地址正确但 Device Name 不匹配，周期 IO 仍可能无法建立。

## GSDML

GSDML 是 PROFINET 设备描述文件。

它通常描述：

- 厂商和设备标识。
- 模块和子模块。
- Slot 和 Subslot 结构。
- 输入输出数据长度。
- 参数数据。
- 诊断项。
- 支持的通信能力。
- 版本和兼容性信息。

GSDML 与设备固件必须一致。

典型映射关系：

```text
GSDML Module/Submodule
        |
PLC 工程中的 Slot/Subslot
        |
PROFINET IO 数据偏移和长度
        |
设备应用输入输出缓冲区
```

常见错误：

- GSDML 中 IO 长度和固件实际实现不一致。
- 工程选择的模块不是设备当前固件支持的模块。
- Submodule 诊断能力声明和实际告警不一致。
- 固件升级后 GSDML 版本未同步。
- 复制旧项目时保留了不兼容设备描述。

## 模块、子模块和数据映射

PROFINET 设备常用模块化结构描述能力。

概念：

- Device：整机设备。
- Module：功能模块或插槽模块。
- Submodule：更细粒度的输入输出或接口单元。
- Slot：模块位置。
- Subslot：子模块位置。

远程 IO 示例：

```text
Slot 1：Digital Input Module
  Subslot 1：16-bit DI Input

Slot 2：Digital Output Module
  Subslot 1：16-bit DO Output
```

设备侧实现要明确：

- 每个 Submodule 的输入长度。
- 每个 Submodule 的输出长度。
- 数据偏移。
- 字节序和位定义。
- 模块插拔或配置变化策略。
- 默认安全输出状态。

## AR 和 CR

AR 是 Application Relation。

CR 是 Communication Relation。

简化理解：

```text
AR：PLC 和设备之间的一组应用关系
CR：AR 内部不同通信通道，如 IO、Record、Alarm
```

典型关系：

- IO CR：周期输入输出数据。
- Record Data CR：参数、记录读写。
- Alarm CR：诊断和告警。

调试时看到 PLC 已发现设备，不代表 AR 已建立。看到 AR 建立，也不代表 IO CR 数据长度、周期和应用状态都正确。

常见 AR/CR 失败方向：

- GSDML 与设备标识不一致。
- Module/Submodule 不一致。
- IO 长度不一致。
- 设备应用未准备好。
- 实时能力或周期参数不支持。
- 设备资源不足。

## 周期 IO

周期 IO 是 PROFINET 工程的核心。

方向定义：

```text
Input：Device -> PLC
Output：PLC -> Device
```

设备侧需要定义：

- 输入数据什么时候采样。
- 输出数据什么时候生效。
- 通信断开后输出保持、清零还是进入安全值。
- 数据有效位和诊断位如何表达。
- 周期抖动和应用任务优先级。

PLC 侧需要确认：

- IO 地址映射正确。
- 变量类型和长度正确。
- 数据更新周期满足控制需求。
- 设备诊断不影响控制逻辑误判。

周期 IO 不适合传输大量低频配置数据。参数和记录更适合通过 Record Data 机制或厂商工具处理。

## Record Data

Record Data 常用于参数读写和非周期数据访问。

典型用途：

- 读取设备参数。
- 写入配置。
- 读取模块信息。
- 厂商私有扩展。

设计注意：

- 参数 ID 和数据结构要稳定。
- 写参数要有权限和范围检查。
- 长时间写入要给出明确错误或状态。
- 参数生效策略要清楚，是立即生效、重启生效还是重新建立 AR 生效。

## Alarm 和诊断

PROFINET 的诊断能力是其区别于简单寄存器协议的重要部分。

常见诊断：

- 模块故障。
- 子模块故障。
- 通道故障。
- 参数错误。
- 外部电源错误。
- 通信错误。
- 维护需求。

诊断设计要考虑：

- 诊断项是否在 GSDML 中声明。
- 诊断触发和清除条件。
- 是否支持通道级诊断。
- PLC 诊断缓冲区显示是否可读。
- 设备日志和 PLC 诊断是否能对应。

不要只在设备串口日志里报错，PLC 工程侧也应能看到合理诊断。

## LLDP 和拓扑

LLDP 用于链路层邻居发现。

PROFINET 工程中常用于：

- 识别设备端口连接关系。
- 拓扑诊断。
- 设备替换和端口定位。
- 工程工具显示网络结构。

常见问题：

- 交换机或设备不透传/不支持相关链路信息。
- 设备多端口信息错误。
- 端口命名和实际接线不一致。
- 现场换线后拓扑诊断异常。

## RT 和 IRT

PROFINET 常见实时等级：

```text
NRT：普通非实时通信，基于标准 TCP/IP 等
RT：实时周期 IO，常见自动化 IO 场景
IRT：同步实时，面向高同步运动控制
```

RT 工程关注：

- 周期时间。
- 网络负载。
- 交换机和设备处理能力。
- PLC 和设备任务调度。

IRT 工程额外关注：

- 时间同步。
- 计划通信窗口。
- 支持 IRT 的硬件。
- 支持 IRT 的交换网络和设备。
- 工程工具中的同步域配置。

不能假设普通 Ethernet MAC 加软件协议栈就能实现 IRT。IRT 对硬件、交换和协议栈能力都有要求。

## 网络设计

PROFINET 网络设计要考虑：

- 工业交换机能力。
- 线缆和接地。
- 环网或冗余需求。
- 广播和组播流量。
- 与普通 IT 网络隔离。
- 端口镜像和抓包能力。
- EMI 和现场接地。

调试建议：

- 首次接入用简单拓扑，减少变量。
- 先单设备跑通，再增加设备数量。
- 使用支持端口镜像的交换机抓包。
- 控制广播风暴和无关网络流量。
- 记录 PLC、设备、交换机端口和线缆编号。

## 协议栈集成

实现 PROFINET 设备通常需要成熟协议栈。

原因：

- DCP、LLDP、AR/CR、Alarm、Record、实时 IO 都需要完整状态机。
- GSDML 和固件实现必须一致。
- 认证要求严格。
- PLC 生态兼容性不能只靠自测工具验证。

设备软件分层建议：

```text
Ethernet Driver
PROFINET Stack
Device Model / GSDML Mapping
Application IO Buffer
Diagnostics / Alarm Manager
Parameter / Record Manager
Nonvolatile Config
Factory Test / Logging
```

关键边界：

- 协议栈负责通信状态机。
- 应用负责真实 IO 数据和设备状态。
- GSDML 映射层负责保证工程描述与固件一致。
- 日志系统负责把 PLC 诊断和设备内部事件关联起来。

## 状态机和异常处理

设备应明确处理：

- 上电初始化。
- 未命名状态。
- 已命名但未组态。
- AR 建立中。
- 周期 IO 正常。
- PLC 停止或断开。
- 网络断开。
- 设备应用故障。
- 恢复出厂。

异常输出策略必须明确：

- 通信断开时输出保持还是清零。
- PLC 停止时输出如何处理。
- 设备内部故障时是否继续上传输入。
- 安全相关输出是否需要独立安全机制。

## 认证和一致性

PROFINET 产品通常涉及一致性测试和认证。

认证关注：

- 协议行为。
- GSDML 合规性。
- 诊断行为。
- 实时能力。
- 设备标识。
- 网络行为。
- 压力和异常场景。

工程上应保留：

- 协议栈版本。
- GSDML 版本。
- 固件版本。
- 测试报告。
- 已验证 PLC 和工程工具版本。
- 已知兼容性限制。

不要在认证后随意改变设备模型、GSDML、IO 长度或协议栈配置。

## Wireshark 分析路径

常用过滤：

```text
pn_dcp
pn_io
lldp
arp
eth.addr == <device-mac>
ip.addr == <device-ip>
```

分析顺序：

1. 看 LLDP 是否能识别邻居和端口。
2. 看 DCP Identify 是否发现设备。
3. 看 DCP Set 是否写入 Device Name 或 IP。
4. 看 AR 建立过程是否出现错误。
5. 看周期 PNIO 是否稳定。
6. 看 Alarm 或诊断是否与 PLC 诊断一致。
7. 看断开和恢复过程是否符合预期。

抓包注意：

- 尽量使用交换机端口镜像。
- 工程电脑抓包可能只能看到工具与设备的发现/命名流量。
- PLC 与设备之间的周期 IO 需要在合适位置镜像。
- 记录抓包点，避免误判“没有报文”。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 工具扫不到设备 | 网卡绑定、DCP、二层网络、设备协议栈、LINK |
| 能命名但 PLC 不连 | Device Name、GSDML、Device ID、模块/子模块 |
| AR 建立失败 | IO 长度、Slot/Subslot、实时参数、设备资源 |
| 周期 IO 不更新 | PLC 运行状态、IO CR、应用缓冲区、周期任务 |
| PLC 诊断显示模块不匹配 | GSDML 版本、固件模型、工程选择模块 |
| 运行中掉线 | 网络质量、交换机、EMI、设备负载、看门狗 |
| 换设备后不恢复 | 名称未写入、设备型号不一致、GSDML 不匹配 |
| IRT 达不到同步要求 | 硬件能力、同步域、交换设备、工程配置 |

## 深度检查清单

- Device Name、IP、MAC、Vendor ID、Device ID 记录完整。
- GSDML 与固件版本绑定清晰。
- Module/Submodule、Slot/Subslot 和 IO 长度一致。
- DCP Identify / Set / Get 行为正常。
- LLDP 端口和拓扑信息正确。
- AR/CR 建立和断开状态机明确。
- 周期 IO 数据方向、长度、偏移和安全状态明确。
- Record Data 参数读写有边界检查。
- Alarm 和诊断项能被 PLC 工具识别。
- RT/IRT 能力声明和硬件能力一致。
- 协议栈、GSDML、固件和认证版本可追溯。
- Wireshark 抓包点和 PLC 诊断时间点可对应。

## 与 EtherNet/IP 的差异

PROFINET 常围绕 Device Name、GSDML、DCP、AR/CR、PNIO 和 PLC 诊断调试。

EtherNet/IP 常围绕 EDS、CIP 对象、Assembly、Forward Open、RPI 和连接资源调试。

二者都基于以太网，但工程模型、设备描述文件、周期 IO 建立方式和生态工具完全不同。

## 延伸阅读

- `bus/profinet.md`
- `bus/profinet-practical.md`
- `bus/industrial-ethernet-comparison.md`
- `bus/ethernet-deep-dive.md`
- `bus/ethernet-ip-practical.md`
