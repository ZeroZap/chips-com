# J1939 Deep Dive

## 目标

本文深入 J1939 的协议结构、网络管理、参数数据库和网关实现，重点覆盖 29-bit ID、PGN 计算、PDU1/PDU2、NAME、Address Claim、Request、Transport Protocol、DM 诊断、SPN 编码、DBC 治理和现场深度排查。

本文不重复基础抓包步骤，而是回答这些问题：

- 为什么 J1939 不能只按 CAN ID 理解。
- PGN 为什么在 PDU1 和 PDU2 中计算方式不同。
- Source Address、Destination Address 和 NAME 分别解决什么问题。
- Address Claim 如何影响设备上线和地址冲突处理。
- BAM 和 RTS/CTS 多包传输如何组织长数据。
- DBC / 参数数据库如何决定 SPN 工程值。
- 网关实现为什么必须保留 Source Address 和时间戳语义。

## 分层模型

J1939 可以按以下层次理解：

```text
CAN PHY：CANH/CANL、终端、线缆、隔离
        |
CAN 2.0B：29-bit 扩展帧、仲裁、错误处理
        |
J1939 Network Management：地址、NAME、Address Claim
        |
J1939 Parameter Groups：PGN、PDU1/PDU2、Request
        |
J1939 Transport Protocol：BAM、RTS/CTS、TP.DT
        |
Application / Diagnostics：SPN、DM 报文、厂商参数
        |
Gateway / Cloud / HMI：DBC 解码、上报、存储、告警
```

关键点：

- CAN 层只负责帧传输和仲裁。
- J1939 层定义 29-bit ID 字段含义和参数组。
- 应用层通过 PGN/SPN 表达车辆或设备状态。
- 网关层必须维护来源、时间和数据库版本。

## 29-bit ID 字段

J1939 使用 CAN 扩展帧。

29-bit ID 字段通常拆分为：

```text
Priority | R | DP | PF | PS | SA
```

字段含义：

| 字段 | 位宽 | 作用 |
| --- | --- | --- |
| Priority | 3 | 仲裁优先级，数值越小优先级越高 |
| R | 1 | Reserved |
| DP | 1 | Data Page，参与 PGN 计算 |
| PF | 8 | PDU Format，决定 PDU1/PDU2 |
| PS | 8 | PDU Specific，目标地址或 Group Extension |
| SA | 8 | Source Address，发送节点地址 |

工程上常犯的错误：

- 只按完整 29-bit ID 过滤，忽略 Source Address。
- PDU1 中错误地把 PS 算入 PGN。
- 把 Priority 改动当成不同业务报文。
- 同一 PGN 多个 Source Address 混在一起解码。

## PGN 计算

PGN 是 Parameter Group Number。

PGN 由 R、DP、PF、PS 部分计算，但要区分 PDU 类型。

PDU1：

```text
PF < 240
PS = Destination Address
PGN = R | DP | PF | 00
```

PDU2：

```text
PF >= 240
PS = Group Extension
PGN = R | DP | PF | PS
```

因此，同样的 PF 在不同目标地址下，PDU1 的 PGN 不变，只是目标地址不同。

过滤建议：

- 先按 PGN 分组。
- 再按 Source Address 区分来源。
- PDU1 还要按 Destination Address 判断点对点目标。
- 对多包传输再关联 TP 会话。

## Priority 和仲裁

Priority 影响 CAN 仲裁。

数值越小，优先级越高。

设计注意：

- 控制和安全相关报文优先级通常更高。
- 低优先级大流量报文不能挤占关键状态报文。
- 周期过密的非关键 PGN 会增加总线负载。
- 网关转发时不要随意改变 Priority。

现场排查时，如果总线负载高，低优先级报文可能出现明显延迟或丢失。

## Source Address

Source Address 是节点在 J1939 网络中的 8-bit 地址。

它用于区分同一 PGN 的不同发送者。

示例：

```text
PGN X from SA 0x00：发动机控制器
PGN X from SA 0x03：变速箱控制器
```

网关解析时必须保留 Source Address。

如果只上报 PGN 和 SPN，不上报 Source Address，多 ECU 系统中会产生数据覆盖和误判。

## NAME

NAME 是 J1939 设备的全局身份字段。

它通常包含：

- Identity Number。
- Manufacturer Code。
- ECU Instance。
- Function Instance。
- Function。
- Vehicle System。
- Industry Group。
- Arbitrary Address Capable。

NAME 用于：

- 地址声明时比较优先级。
- 识别设备类型和厂商。
- 地址冲突时决定谁保留地址。

工程建议：

- 量产设备 NAME 要唯一或按规范配置。
- 同型号多个节点要正确设置实例字段。
- 网关日志要记录 Source Address 和 NAME 的映射。
- 现场换件后要重新确认 NAME 和地址是否符合预期。

## Address Claim

Address Claim 用于节点声明 Source Address。

核心流程：

```text
节点上电
发送 Address Claim，声明 SA 和 NAME
监听是否有其他节点声明同一 SA
若冲突，按 NAME 优先级仲裁
失败节点选择新地址或停止通信
```

调试重点：

- 上电后是否发送 Address Claim。
- Source Address 是否唯一。
- NAME 是否符合设备配置。
- 地址冲突时是否重新声明。
- 固定地址设备和任意地址设备策略是否兼容。

常见问题：

| 现象 | 根因方向 |
| --- | --- |
| 设备不上报业务 PGN | Address Claim 未完成、地址冲突、应用未启动 |
| 同一地址两个设备 | 实例配置重复、NAME 配置错误、固定地址冲突 |
| 网关识别错设备 | SA 与 NAME 映射缓存未更新 |
| 换件后异常 | 新设备 NAME/SA 不同，平台绑定旧映射 |

## Request PGN

Request PGN 用于请求目标节点发送指定 PGN。

常见用途：

- 请求 Address Claim。
- 请求软件标识。
- 请求组件标识。
- 请求诊断信息。
- 请求厂商自定义数据。

工程注意：

- 请求本身是一个 PGN。
- 请求数据中携带被请求 PGN。
- PDU1 请求需要目标地址。
- 目标设备可以不支持被请求 PGN。
- 响应可能是单帧或多包。

请求无响应时，不要立刻判断设备掉线，应检查目标地址、被请求 PGN、权限、应用状态和总线负载。

## SPN 编码

SPN 是参数或信号。

每个 SPN 至少需要定义：

- 所属 PGN。
- 起始位。
- 长度。
- 字节序。
- Resolution。
- Offset。
- 单位。
- 无效值。
- 错误或不可用状态。

工程值计算通常类似：

```text
Physical Value = Raw Value * Resolution + Offset
```

常见错误：

- 把无效值当真实值。
- Resolution 或 Offset 使用错版本。
- 大小端理解错误。
- 多字节信号跨字节解析错误。
- 枚举值未按规范映射。

数据库版本必须和目标车型、ECU 固件和客户规范一致。

## Transport Protocol

J1939 TP 用于传输超过 8 字节的数据。

核心报文：

- TP.CM：Connection Management。
- TP.DT：Data Transfer。

常见模式：

```text
BAM：广播长消息
RTS/CTS：点对点流控长消息
```

BAM 流程：

```text
Sender -> BAM，声明总长度、包数、目标 PGN
Sender -> TP.DT #1
Sender -> TP.DT #2
...
Sender -> TP.DT #N
```

RTS/CTS 流程：

```text
Sender -> RTS，声明总长度、包数、目标 PGN
Receiver -> CTS，允许发送若干包
Sender -> TP.DT #1..#K
Receiver -> CTS，继续允许
Sender -> TP.DT ...
Receiver -> EndOfMsgAck
```

调试重点：

- 总长度是否正确。
- 包数是否正确。
- Sequence Number 是否连续。
- TP.CM 中目标 PGN 是否正确。
- BAM 间隔是否符合设备能力。
- RTS/CTS 是否出现 Abort。
- 多个 TP 会话是否冲突。

## 多包重组策略

网关或分析软件需要维护 TP 会话状态。

状态至少包括：

- 发送 Source Address。
- 目标地址，广播或点对点。
- 目标 PGN。
- 总长度。
- 总包数。
- 当前序号。
- 接收缓冲。
- 超时。

异常处理：

- 序号跳变。
- 超时。
- 长度超限。
- 新会话覆盖旧会话。
- Abort。
- 缓冲区不足。

不要把未完整重组的数据交给上层 SPN 解码。

## DM 诊断报文

J1939 定义了诊断相关 DM 报文。

常见方向：

- 当前故障。
- 历史故障。
- 清除故障。
- 指示灯状态。
- 诊断准备状态。

DTC 通常涉及：

- SPN。
- FMI。
- OC。
- CM，视格式而定。

含义：

- SPN：哪个参数或部件相关。
- FMI：故障模式，如超范围、短路、数据异常。
- OC：发生次数。

诊断解析要点：

- DTC 字节布局和格式版本。
- 多个 DTC 的循环解析。
- 指示灯状态。
- 清除故障请求是否被允许。
- 当前故障是否会清除后立即重现。

## 周期、负载和带宽

J1939 常见于 250 kbps 或 500 kbps CAN 网络。

总线负载设计要考虑：

- 周期 PGN 数量。
- 每个 PGN 周期。
- 多包报文频率。
- 诊断请求流量。
- 网关主动请求频率。
- 错误重发。

网关不要无节制轮询大量 PGN。

建议：

- 区分高频控制数据和低频状态数据。
- 对软件版本、组件标识等低频信息缓存。
- 对多包响应限速。
- 总线负载高时降低非关键请求频率。

## 网关实现

J1939 网关常将数据转为 MQTT、HTTP、Modbus、CANopen 或私有协议。

核心设计：

- 保留 Source Address。
- 保留 PGN。
- 保留 SPN。
- 保留原始值和工程值。
- 保留时间戳。
- 保留数据库版本。
- 区分无效值、超时值和真实值。
- 支持多包重组。
- 控制主动请求频率。

上云数据建议包含：

```text
vehicle_id
source_address
pgn
spn
raw_value
physical_value
unit
timestamp
db_version
quality
```

如果只上传物理值，不上传来源和质量标记，后续排障会很困难。

## 数据库治理

J1939 数据库可能来自标准、客户规范、DBC、Excel 或厂商私有协议文档。

治理重点：

- 数据库版本号。
- 适用车型或设备型号。
- ECU 固件版本。
- PGN/SPN 来源。
- 私有 PGN 标注。
- 单位和无效值。
- 变更记录。

常见风险：

- 同一 SPN 在不同客户项目中定义不同。
- 厂商私有 PGN 与标准 PGN 混用。
- DBC 更新后网关固件未同步。
- 云端解析版本和车端采集版本不一致。

## 安全和只监听策略

很多 J1939 采集设备应优先只监听。

主动发送请求或控制报文前，要评估：

- 是否影响 ECU 行为。
- 是否增加总线负载。
- 是否违反客户安全要求。
- 是否需要认证或授权。
- 是否会触发故障记录。

控制类报文必须有明确安全机制和失效策略。

## 现场深度排查流程

建议顺序：

1. 确认 CAN 物理层、终端和错误计数。
2. 确认扩展帧和波特率。
3. 统计 Source Address 和 Address Claim。
4. 建立 SA -> NAME 映射。
5. 按 PGN 统计周期、抖动和丢失。
6. 加载正确数据库解析 SPN。
7. 检查无效值和质量标记。
8. 对长报文检查 TP 重组。
9. 对诊断报文检查 SPN/FMI/OC。
10. 对网关上报检查时间戳、来源和数据库版本。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 扩展帧全无 | CAN 波特率、分析仪设置、总线接线、设备上电 |
| PGN 解析错 | PDU1/PDU2、DP、PF/PS、数据库版本 |
| 同一信号跳变 | Source Address 混淆、多 ECU 同 PGN、网关覆盖 |
| 多包解析失败 | TP.CM、TP.DT 序号、超时、目标 PGN、缓冲区 |
| DTC 解析异常 | SPN/FMI 格式、DM 类型、字节序、数据库版本 |
| 上云数据不可信 | 时间戳、质量标记、无效值、数据库版本缺失 |
| 接入采集器后车辆异常 | 主动请求过多、发送控制报文、总线负载升高 |

## 深度检查清单

- CAN 扩展帧、波特率、终端和错误计数正常。
- 29-bit ID 字段拆解正确。
- PGN 计算区分 PDU1/PDU2。
- Source Address 和 NAME 映射已记录。
- Address Claim 冲突策略明确。
- Request PGN 目标地址和响应策略正确。
- BAM 和 RTS/CTS 多包重组有超时和异常处理。
- SPN 缩放、偏移、单位和无效值来自正确数据库版本。
- DM 诊断报文可解析 SPN/FMI/OC。
- 网关保留来源、时间戳、质量标记和数据库版本。
- 主动发送报文前已评估安全和总线负载影响。

## 与 UDS 的区别

J1939 主要用于商用车和重型设备的运行数据、状态和诊断参数广播，强调 PGN/SPN、地址声明和多源数据解析。

UDS 主要用于诊断会话、DID、DTC、例程、安全访问和刷写，强调请求响应、权限和诊断状态机。

二者都可运行在 CAN 生态中，但工程目标和状态机完全不同。

## 延伸阅读

- `bus/j1939.md`
- `bus/j1939-practical.md`
- `bus/can.md`
- `basic/can-phy.md`
- `bus/uds-practical.md`
- `bus/iso-tp-deep-dive.md`
