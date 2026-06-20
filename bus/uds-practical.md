# UDS Practical Guide

## 目标

本文面向汽车 ECU 诊断、产线测试、售后诊断、Bootloader 刷写、T-Box 远程诊断和诊断网关调试场景。

重点覆盖：

- UDS over CAN / CAN FD / DoIP 的调试入口。
- ISO-TP 请求响应和多帧承载。
- 诊断会话和 Tester Present。
- DID 读写。
- DTC 读取和清除。
- Security Access 种子密钥流程。
- Routine Control。
- Request Download / Transfer Data / Transfer Exit 刷写流程。
- NRC 负响应定位。
- P2 / P2* 超时。
- 诊断日志和抓包分析。

UDS 调试的关键不是记住所有 SID，而是把会话状态、权限状态、传输层状态和 ECU 内部业务状态分开看。

## 分层关系

常见 UDS over CAN 分层：

```text
CAN PHY：CANH/CANL、波特率、终端
CAN：标准帧/扩展帧、ID、仲裁、错误计数
ISO-TP：Single/First/Consecutive/Flow Control、多帧重组
UDS：服务、会话、权限、DID、DTC、刷写
ECU Application：诊断数据、Flash、例程、故障内存
```

排查时不要把所有问题都归到 UDS 层。单帧不通先查 CAN，长数据不通先查 ISO-TP，服务返回 NRC 再查 UDS 状态和业务条件。

## 最小调试准备

典型连接：

```text
Tester / Diagnostic Tool / PCAN / CANoe / CANalyzer
        |
CAN / CAN FD / DoIP
        |
ECU / Gateway / Vehicle Network
```

最小检查：

- CAN 或 DoIP 物理链路正常。
- 请求 ID 和响应 ID 明确。
- 标准帧/扩展帧类型明确。
- ISO-TP 寻址方式明确，如 Normal / Extended / Mixed。
- 诊断会话入口明确。
- DID、Routine、DTC 和安全等级来自正确诊断规范。
- 工具超时参数和 ECU 规范一致。

不要假设所有 ECU 都使用相同 CAN ID、相同 DID 或相同安全等级。

## 常用服务速查

| SID | 服务 | 常见用途 |
| --- | --- | --- |
| 0x10 | Diagnostic Session Control | 进入默认、扩展、编程会话 |
| 0x11 | ECU Reset | 软复位、硬复位、应用重启 |
| 0x14 | Clear Diagnostic Information | 清除 DTC |
| 0x19 | Read DTC Information | 读取故障码和状态 |
| 0x22 | Read Data By Identifier | 读取 DID，如 VIN、版本、传感器值 |
| 0x27 | Security Access | 种子密钥解锁权限 |
| 0x28 | Communication Control | 控制 ECU 通信行为 |
| 0x2E | Write Data By Identifier | 写入 DID，如配置或标定数据 |
| 0x31 | Routine Control | 启动、停止、查询例程 |
| 0x34 | Request Download | 请求下载固件数据 |
| 0x36 | Transfer Data | 传输刷写数据块 |
| 0x37 | Request Transfer Exit | 结束数据传输 |
| 0x3E | Tester Present | 保持诊断会话 |
| 0x85 | Control DTC Setting | 控制 DTC 记录开关 |

正响应 SID 通常为：

```text
Response SID = Request SID + 0x40
```

例如：

```text
0x22 -> 0x62
0x10 -> 0x50
0x27 -> 0x67
```

负响应格式：

```text
0x7F | Original SID | NRC
```

## 诊断会话

常见会话：

```text
Default Session
Extended Session
Programming Session
```

典型流程：

```text
Tester -> ECU：10 03    进入 Extended Session
ECU -> Tester：50 03 ...
Tester -> ECU：3E 00    周期 Tester Present
```

工程注意：

- 某些 DID 只能在扩展会话读取。
- 刷写通常需要编程会话。
- 会话会超时回到默认会话。
- Tester Present 周期要小于 ECU 会话超时。
- 切会话可能影响通信、DTC 记录或应用状态。

常见错误：

| 现象 | 优先检查 |
| --- | --- |
| 服务在默认会话返回 NRC | 是否需要 Extended 或 Programming Session |
| 会话进入后过一会失效 | Tester Present 周期、工具超时、ECU S3 定时器 |
| 进编程会话失败 | 电压、车速、点火状态、诊断权限、网关路由 |

## DID 读取和写入

读取 DID 使用 `0x22`。

示例：读取 DID `F190`，常用于 VIN：

```text
Request:  22 F1 90
Response: 62 F1 90 <data...>
```

写 DID 使用 `0x2E`。

示例：

```text
Request:  2E F1 99 <data...>
Response: 6E F1 99
```

DID 调试要点：

- DID 是否存在。
- DID 是否允许当前会话访问。
- 写 DID 是否需要 Security Access。
- 数据长度是否严格匹配。
- 编码格式是否明确，如 ASCII、BCD、小端整数、大端整数。
- 写入后是否需要复位或例程生效。

常见 NRC：

| NRC | 方向 |
| --- | --- |
| 0x13 | 请求长度或格式错误 |
| 0x22 | 条件不满足 |
| 0x31 | 请求超出范围，DID 不支持或数据不合法 |
| 0x33 | 安全访问拒绝 |

## DTC 读取和清除

DTC 读取使用 `0x19`。

常见子功能：

- 按状态掩码读取 DTC。
- 读取 DTC 快照。
- 读取扩展数据。
- 读取支持的 DTC。

清除 DTC 使用 `0x14`。

工程注意：

- 清 DTC 可能需要扩展会话或安全权限。
- 清 DTC 可能要求点火、电压、车速等条件满足。
- DTC 状态字比 DTC 编号更重要，能反映当前、历史、确认、测试失败等状态。
- 清除后要重新读取确认是否真的清掉。
- 有些当前故障仍存在，清除后会立刻重新置位。

调试顺序：

1. 读取当前 DTC 和状态。
2. 记录快照和扩展数据。
3. 修复故障或断开触发条件。
4. 执行 Clear Diagnostic Information。
5. 重新读取 DTC。
6. 跑一轮诊断条件确认是否复现。

## Security Access

Security Access 使用 `0x27`。

典型 Seed / Key 流程：

```text
Tester -> ECU：27 01          请求 Level 1 Seed
ECU -> Tester：67 01 <seed>
Tester -> ECU：27 02 <key>    发送 Level 1 Key
ECU -> Tester：67 02
```

注意：

- Seed 子功能通常是奇数。
- Key 子功能通常是对应偶数。
- 不同安全等级算法不同。
- 错误次数可能触发延时或锁定。
- 断电、复位或切会话可能清除解锁状态。

常见 NRC：

| NRC | 方向 |
| --- | --- |
| 0x24 | 请求顺序错误，如没请求 seed 就发 key |
| 0x35 | Key 无效 |
| 0x36 | 超过尝试次数 |
| 0x37 | 需要等待延时 |

工程建议：

- 日志中记录安全等级、seed 长度、key 长度和 NRC。
- 工具不要在失败后无限重试。
- 算法、端序和数据拼接必须和 ECU 规范一致。

## Routine Control

Routine Control 使用 `0x31`。

常见用途：

- 擦除 Flash。
- 校验固件。
- 检查编程条件。
- 执行传感器校准。
- 查询例程结果。

常见子功能：

```text
01：Start Routine
02：Stop Routine
03：Request Routine Results
```

调试重点：

- Routine ID 是否正确。
- 例程是否需要会话或安全权限。
- 例程参数长度和格式是否正确。
- 长时间例程是否返回 Response Pending。
- 例程结果是否需要单独查询。

## 刷写流程

典型 UDS 刷写流程：

```text
进入 Extended Session
检查编程条件
进入 Programming Session
Security Access 解锁
Routine Control 擦除 Flash
Request Download
Transfer Data block 1..N
Request Transfer Exit
Routine Control 校验固件
ECU Reset
应用启动确认
```

关键服务：

| 服务 | 作用 |
| --- | --- |
| 0x10 | 进入编程会话 |
| 0x27 | 解锁刷写权限 |
| 0x31 | 擦除、校验、检查条件 |
| 0x34 | 声明下载地址、大小和格式 |
| 0x36 | 发送数据块 |
| 0x37 | 结束传输 |
| 0x11 | 复位 ECU |

刷写调试要点：

- Flash 地址和大小是否和 bootloader 分区匹配。
- Transfer Data block sequence counter 是否连续。
- ISO-TP Block Size 和 STmin 是否适配 ECU Flash 写入速度。
- 每个下载块的最大长度是否来自 Request Download 响应。
- 擦除和校验可能耗时，需要正确处理 `0x78 Response Pending`。
- 断电恢复和失败回滚策略必须明确。

## P2 / P2* 和 Response Pending

UDS 响应时间常见参数：

```text
P2：正常响应最大等待时间
P2*：ECU 返回 Response Pending 后的扩展等待时间
```

Response Pending：

```text
7F <SID> 78
```

表示 ECU 已收到请求，但处理时间较长。

工具处理原则：

- 收到 `0x78` 后不要立即判失败。
- 按 P2* 继续等待最终响应。
- 对擦除、校验、例程和刷写尤其常见。
- 限制最大等待次数，避免工具无限挂起。

## NRC 定位方法

常见 NRC：

| NRC | 含义方向 | 常见原因 |
| --- | --- | --- |
| 0x10 | General Reject | ECU 拒绝但原因不细 |
| 0x11 | Service Not Supported | 服务不支持 |
| 0x12 | SubFunction Not Supported | 子功能不支持 |
| 0x13 | Incorrect Message Length Or Invalid Format | 长度或格式错 |
| 0x22 | Conditions Not Correct | 条件不满足 |
| 0x24 | Request Sequence Error | 请求顺序错 |
| 0x31 | Request Out Of Range | DID/Routine/参数越界 |
| 0x33 | Security Access Denied | 安全权限不足 |
| 0x35 | Invalid Key | Key 错误 |
| 0x36 | Exceed Number Of Attempts | 安全访问尝试次数超限 |
| 0x37 | Required Time Delay Not Expired | 安全延时未结束 |
| 0x78 | Response Pending | ECU 处理中 |

定位顺序：

1. 确认 SID 和子功能是否支持。
2. 确认请求长度和数据格式。
3. 确认当前会话。
4. 确认安全等级。
5. 确认 ECU 运行条件，如电压、点火、车速、DTC 状态。
6. 确认请求顺序。
7. 对 `0x78` 按 P2* 等待最终响应。

## 抓包和日志

诊断日志至少记录：

- 时间戳。
- 请求 CAN ID / 响应 CAN ID。
- ISO-TP 帧类型和重组结果。
- UDS SID、子功能、DID、Routine ID。
- NRC。
- 会话状态。
- 安全等级。
- P2 / P2* 超时。
- 刷写块序号和长度。

抓包排查入口：

```text
先看 CAN 错误和帧类型
再看 ISO-TP 单帧/多帧是否完整
再看 UDS 正响应或负响应
最后看 ECU 业务条件
```

常见日志判断：

| 现象 | 优先检查 |
| --- | --- |
| 无响应 | CAN ID、寻址方式、ECU 在线、网关路由 |
| 单帧服务正常，长 DID 失败 | ISO-TP Flow Control、STmin、Block Size、缓冲区 |
| 进入会话后又失败 | Tester Present、S3 超时、会话被复位 |
| 写 DID 失败 | 会话、安全访问、长度、数据范围 |
| 刷写中断 | Transfer Data 序号、ISO-TP 超时、Flash 写入、供电 |

## 网关和 DoIP 注意

UDS 可以通过诊断网关访问多个 ECU。

网关场景要确认：

- 目标 ECU 地址或逻辑地址。
- 物理寻址和功能寻址区别。
- 网关是否允许该服务路由。
- 网关是否改写超时行为。
- 多 ECU 响应是否可能冲突。

DoIP 场景要额外检查：

- IP 地址和端口。
- Vehicle Identification。
- Routing Activation。
- TCP 连接状态。
- DoIP 逻辑地址。
- UDS 负响应和 DoIP 层错误要分开记录。

## 实战检查清单

- 裸 CAN / CAN FD / DoIP 链路已确认。
- 请求 ID、响应 ID 和寻址方式明确。
- Single Frame 和 Multi Frame 都验证过。
- 会话切换和 Tester Present 正常。
- DID 读写格式和权限明确。
- DTC 读取、清除和状态字解释正确。
- Security Access 顺序、算法、端序和错误次数处理正确。
- Routine Control 支持长时间处理和结果查询。
- 刷写流程能处理 `0x78`、超时、断电和回滚。
- 诊断工具日志能区分 CAN、ISO-TP、UDS 和 ECU 业务错误。
- 所有服务行为以 ECU 诊断规范为准，不使用默认假设。

## 与 ISO-TP 的关系

ISO-TP 负责把超过单帧的数据可靠分片和重组。

UDS 负责定义诊断服务、会话、权限、DID、DTC 和刷写语义。

调试原则：

```text
没有完整 ISO-TP 数据，就不要分析 UDS 负响应
UDS 返回 NRC 时，再进入会话、权限和业务条件排查
```

## 延伸阅读

- `bus/uds.md`
- `bus/iso-tp-practical.md`
- `bus/iso-tp-deep-dive.md`
- `bus/can.md`
- `basic/can-phy.md`
