# UDS Deep Dive

## 目标

本文深入 UDS 的协议状态机、服务处理框架、诊断权限、负响应策略、刷写事务、DoIP/网关和 ECU 实现边界，适用于诊断工具、ECU Bootloader、T-Box 远程诊断、产线测试和售后诊断系统设计。

本文不重复基础服务号列表，而是回答这些问题：

- UDS 层如何与 CAN、ISO-TP、DoIP 和 ECU 应用解耦。
- 会话、安全等级、Tester Present 和 P2/P2* 如何组成诊断状态机。
- 服务处理时如何决定正响应、负响应和 Response Pending。
- DID、DTC、Routine 和刷写服务如何做权限和条件检查。
- Bootloader 刷写如何保证断电恢复和防变砖。
- 诊断网关和 DoIP 如何改变超时、路由和日志策略。

## 分层模型

UDS 常见分层：

```text
Physical Link：CAN / CAN FD / Ethernet
        |
Transport：ISO-TP / DoIP
        |
UDS Core：SID、SubFunction、DID、Routine、NRC
        |
Diagnostic State：Session、Security、Timing、Tester Present
        |
ECU Services：DID、DTC、Routine、Flash、Configuration
        |
Application / Bootloader：业务数据、故障内存、Flash Driver
```

边界原则：

- CAN 错误和 ISO-TP 重组错误不应伪装成 UDS 业务错误。
- UDS NRC 应反映服务层或业务条件，而不是链路层丢帧。
- Bootloader 和 Application 可以共用 UDS 框架，但服务表、权限和内存访问边界通常不同。

## 诊断状态机

UDS ECU 至少要维护：

- 当前诊断会话。
- 当前安全等级。
- S3 会话保持定时器。
- P2 / P2* 响应时序。
- 当前正在执行的长时间服务。
- 是否处于刷写或例程状态。

典型状态关系：

```text
Default Session
  -> Extended Session
       -> Security Unlocked
       -> Routine / DID Write / DTC Control
  -> Programming Session
       -> Security Unlocked
       -> Download / Transfer / Verify / Reset
```

会话切换时要明确：

- 是否清除安全等级。
- 是否停止正在运行的例程。
- 是否重置 Tester Present 定时器。
- 是否改变可用服务表。
- 是否影响 DTC 记录和通信控制。

## 服务调度框架

ECU 侧服务处理可按以下顺序设计：

```text
接收完整传输层 PDU
解析 SID 和子功能
检查服务是否支持
检查消息长度和格式
检查会话权限
检查安全权限
检查业务条件
执行服务或启动异步任务
返回正响应、负响应或 Response Pending
记录诊断日志
```

推荐将检查拆成统一框架，而不是每个服务重复写散乱逻辑。

好处：

- NRC 决策一致。
- 日志字段一致。
- 会话和安全权限集中配置。
- 便于产线、售后和远程诊断复用。

## NRC 决策顺序

NRC 的顺序会影响工具判断。

推荐优先级：

1. 服务是否支持。
2. 子功能是否支持。
3. 消息长度和格式是否正确。
4. 服务是否支持当前会话。
5. 是否需要安全权限。
6. 请求顺序是否正确。
7. 业务条件是否满足。
8. 参数范围是否有效。
9. 是否需要 Response Pending。

常见 NRC：

| NRC | 定位方向 |
| --- | --- |
| 0x11 | 服务不支持 |
| 0x12 | 子功能不支持 |
| 0x13 | 长度或格式错误 |
| 0x22 | 条件不满足 |
| 0x24 | 请求顺序错误 |
| 0x31 | 请求超出范围 |
| 0x33 | 安全访问拒绝 |
| 0x35 | Key 无效 |
| 0x36 | 尝试次数超限 |
| 0x37 | 延时未结束 |
| 0x78 | Response Pending |

不要把所有业务失败都返回 General Reject。NRC 越具体，现场排查越快。

## P2、P2* 和长时间服务

P2 是普通响应最大时间。

P2* 是 ECU 返回 Response Pending 后的扩展等待时间。

长时间服务包括：

- Flash 擦除。
- Flash 校验。
- 复杂例程。
- 大量 DTC 数据读取。
- 网关跨域路由。

处理策略：

```text
服务能在 P2 内完成 -> 返回最终响应
服务不能在 P2 内完成 -> 返回 7F SID 78
异步任务继续执行
在 P2* 内返回最终响应或继续按规范返回 Pending
```

实现要点：

- 长任务不能阻塞接收 Tester Present 或必要的取消/复位逻辑。
- Pending 频率不能过快导致总线负载过高。
- 工具侧要有最大 Pending 次数或总超时。
- ECU 日志要记录异步任务开始、进度、完成和失败原因。

## 会话管理

常见会话：

- Default Session。
- Extended Session。
- Programming Session。

每个服务要配置可用会话。

示例：

| 服务 | Default | Extended | Programming |
| --- | --- | --- | --- |
| 0x22 读取普通 DID | 可选 | 是 | 可选 |
| 0x2E 写配置 DID | 否 | 是 | 否 |
| 0x27 安全访问 | 否 | 是 | 是 |
| 0x34 Request Download | 否 | 否 | 是 |
| 0x36 Transfer Data | 否 | 否 | 是 |

切换到 Programming Session 前通常要检查：

- 电压范围。
- 点火状态。
- 车速或设备运动状态。
- 当前故障状态。
- 通信网络状态。
- 是否允许进入 Bootloader。

## Tester Present 和 S3

Tester Present 用于保持非默认会话。

S3 定时器超时后 ECU 通常回到默认会话。

工程注意：

- Tester Present 周期应小于 S3 超时。
- 某些服务执行期间是否接受 Tester Present 要明确。
- 刷写期间如果 Tester Present 被长任务阻塞，可能导致会话丢失。
- ECU Reset 后会话和安全状态通常清除。

工具侧不要无脑高频发送 Tester Present，避免占用总线。

## Security Access

Security Access 管理敏感服务权限。

典型状态：

```text
Locked
Seed Issued
Unlocked
Delay Active
Exceeded Attempts
```

实现要点：

- Seed 和 Key 子功能成对。
- 未请求 Seed 直接发 Key 应返回请求顺序错误。
- Key 错误要计数。
- 超过次数要进入延时或锁定。
- 延时状态跨复位或断电是否保持要按安全需求定义。
- 不同安全等级互相影响关系要明确。

安全设计建议：

- 不在日志中明文长期保存 Key。
- Seed 随机性或不可预测性满足项目要求。
- 算法版本可追溯。
- 远程诊断场景要考虑认证、加密和审计。

## DID 体系

DID 设计要明确：

- DID 编号。
- 数据长度。
- 数据类型。
- 字节序。
- 读权限。
- 写权限。
- 所属会话。
- 所需安全等级。
- 生效策略。
- 非易失存储策略。

DID 服务框架：

```text
查 DID 表
检查长度
检查会话
检查安全等级
检查读写方向
调用 DID handler
返回数据或 NRC
```

常见风险：
- 写 DID 后掉电导致配置半写。
- 写入值未做范围检查。
- 多 DID 读取时单个 DID 失败策略不清。
- VIN、序列号、标定数据权限控制不严。
- DID 文档、ODX 和固件实现不一致。

## DTC 和故障内存

DTC 相关服务通常涉及故障存储、快照和扩展数据。

设计要点：

- DTC 编号和状态字。
- 测试失败、当前、确认、历史等状态位。
- 快照数据。
- 扩展数据。
- 清除条件。
- 故障老化策略。
- 故障内存容量和覆盖策略。

读取 DTC 时要区分：

- 当前存在故障。
- 历史故障。
- 已确认故障。
- 本周期测试未完成。

清除 DTC 时要考虑：

- 是否需要会话或安全权限。
- 是否允许车辆运行中清除。
- 当前故障仍存在时是否会立刻重置。
- 清除是否影响快照和扩展数据。

## Routine Control

Routine 用于封装复杂操作。

常见例程：

- 检查编程前条件。
- 擦除内存。
- 校验内存。
- 传感器标定。
- 执行自检。
- 查询异步操作结果。

Routine 设计要明确：

- Routine ID。
- Start/Stop/Result 支持情况。
- 输入参数。
- 输出结果。
- 会话和安全等级。
- 是否异步。
- 执行超时。
- 与刷写状态机的关系。

长时间 Routine 应支持 Response Pending 和结果查询。

## 刷写事务

刷写是 UDS 中最复杂的工程场景。

典型事务：

```text
Extended Session
Check Programming Preconditions
Programming Session
Security Access
Erase Memory Routine
Request Download
Transfer Data block 1..N
Request Transfer Exit
Verify Memory Routine
ECU Reset
Application Valid Check
```

刷写状态机：

```text
IDLE
PRECONDITION_CHECKED
PROGRAMMING_SESSION
SECURITY_UNLOCKED
ERASED
DOWNLOADING
TRANSFER_EXIT
VERIFYING
READY_TO_RESET
FAILED
ROLLBACK / RECOVERY
```

实现要点：

- Request Download 返回最大块长度。
- Transfer Data 序号必须连续。
- 写 Flash 前校验地址范围。
- 擦写时处理电压异常。
- 校验镜像完整性和签名，视安全需求。
- 元数据写入要能断电恢复。
- 应用启动后要有确认机制。
- 失败后能回到 Bootloader 或旧镜像。

不要在未校验完整镜像前覆盖唯一可启动应用。

## 传输层交互

UDS over CAN 常依赖 ISO-TP。

UDS 层关注：

- 完整请求 PDU。
- 完整响应 PDU。
- 服务超时。

ISO-TP 层关注：

- Single Frame。
- First Frame。
- Flow Control。
- Consecutive Frame。
- Block Size。
- STmin。
- 多帧重组和缓冲区。

分层错误要分开记录：

| 层级 | 示例 |
| --- | --- |
| CAN | Bus Off、ACK Error、错误帧 |
| ISO-TP | CF 序号错、FC 超时、缓冲不足 |
| UDS | NRC、会话错误、安全错误、业务条件不满足 |
| Application | Flash 失败、DID 不存在、DTC 存储异常 |

## DoIP 和网关

UDS over DoIP 增加了以太网和路由层。

DoIP 关注：

- Vehicle Identification。
- Routing Activation。
- Logical Address。
- TCP 连接。
- Alive Check。
- DoIP 层错误码。

诊断网关关注：

- Tester 到目标 ECU 的路由。
- 物理寻址和功能寻址。
- 多 ECU 响应聚合。
- 网关自身 NRC 和目标 ECU NRC 区分。
- 网关超时是否覆盖目标 ECU 超时。
- 安全访问是否在目标 ECU 还是网关处理。

日志必须标明错误来自 DoIP、网关、传输层还是目标 ECU。

## ODX 和诊断数据库

UDS 项目常使用 ODX、CDD、Excel 或厂商数据库描述诊断能力。

数据库应包含：

- 服务。
- DID。
- Routine。
- DTC。
- NRC。
- 会话权限。
- 安全等级。
- 数据编码。
- 单位和枚举。
- 刷写流程。

治理重点：

- 数据库版本和 ECU 固件版本绑定。
- 产线、售后和研发工具使用同一来源。
- DID 长度和编码变更有兼容策略。
- 刷写流程变更要同步工具和 Bootloader。

## ECU 实现架构

推荐分层：

```text
Transport Adapter：ISO-TP / DoIP
UDS Core：SID dispatch、NRC、Timing
Session Manager
Security Manager
DID Manager
DTC Manager
Routine Manager
Flash Download Manager
Application Adapter
Diagnostic Logger
```

核心原则：

- 服务表数据驱动。
- 会话和安全权限集中管理。
- 长时间任务异步执行。
- 日志字段统一。
- Bootloader 和 Application 边界清晰。
- 传输层错误不混入 UDS NRC。

## 测试矩阵

UDS 测试不应只测正向流程。

建议覆盖：

- 所有服务正响应。
- 不支持服务和子功能。
- 长度错误。
- 错会话。
- 未解锁安全访问。
- Key 错误和延时。
- 请求顺序错误。
- P2/P2* 超时。
- Response Pending。
- ISO-TP 多帧异常。
- 刷写断电恢复。
- 网关路由错误。
- DoIP 断链恢复。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| ECU 无响应 | CAN/DoIP 链路、寻址、网关路由、会话状态 |
| 单帧服务正常长数据失败 | ISO-TP BS/STmin、缓冲区、CF 序号 |
| 服务返回 0x22 | 车辆状态、电压、点火、业务条件 |
| 服务返回 0x33 | 安全等级、会话、安全访问状态 |
| 一直 0x78 | 长任务卡死、P2* 策略、异步任务状态 |
| 刷写中断 | Transfer Data 序号、Flash 写入、电压、ISO-TP 超时 |
| 清 DTC 后又出现 | 当前故障仍存在、诊断监控重新置位 |
| DoIP 下 CAN 正常但远程失败 | Routing Activation、逻辑地址、网关策略 |

## 深度检查清单

- 传输层和 UDS 层错误分开记录。
- 服务表包含会话、安全和长度规则。
- NRC 决策顺序一致。
- P2/P2* 和 Response Pending 行为明确。
- Tester Present 不被长任务阻塞。
- Security Access 有尝试次数、延时和状态恢复策略。
- DID、DTC、Routine 与诊断数据库一致。
- 刷写有断电恢复、镜像校验和失败回退。
- DoIP 和网关日志能区分错误来源。
- 测试覆盖正向、负向、超时、断电和异常顺序。

## 与 J1939 的区别

J1939 更偏运行数据、参数广播、商用车诊断和多源 PGN/SPN 解析。

UDS 更偏请求响应式诊断、会话权限、DID/DTC、例程控制和 ECU 刷写。

J1939 调试重点是 PGN、SPN、Source Address、NAME 和 TP 重组。

UDS 调试重点是会话、安全等级、NRC、传输层完整性和 ECU 业务状态。

## 延伸阅读

- `bus/uds.md`
- `bus/uds-practical.md`
- `bus/iso-tp-practical.md`
- `bus/iso-tp-deep-dive.md`
- `bus/j1939-deep-dive.md`
- `bus/can.md`
