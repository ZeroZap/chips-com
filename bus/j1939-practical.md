# J1939 Practical Guide

## 目标

本文面向商用车、工程机械、农机、发动机 ECU、仪表、车队监控终端和网关设备的 J1939 调试场景。

重点覆盖：

- 物理层和 CAN 扩展帧准备。
- 29-bit ID 拆解。
- PGN、SPN 和源地址。
- PDU1 / PDU2 的区别。
- 地址声明 Address Claim。
- 请求报文 Request PGN。
- BAM、RTS/CTS 多包传输。
- DBC / 参数数据库解析。
- CAN 分析仪和日志排查方法。
- 现场常见故障定位。

J1939 调试的关键是把 CAN ID、PGN、源地址、目标地址、SPN 缩放和多包状态机统一起来看，不能只按裸 CAN ID 过滤。

## 最小硬件准备

典型连接：

```text
J1939 Device / ECU
        |
CANH / CANL
        |
CAN Analyzer / Gateway / Vehicle Bus
```

最小检查：

- 使用 CAN 扩展帧，29-bit ID。
- 常见波特率为 250 kbps，具体以车辆或设备平台为准。
- CANH/CANL 没有接反。
- 总线两端有 120 ohm 终端，断电测 CANH-CANL 约 60 ohm。
- 分析仪、设备和总线参考地或隔离参考合理。
- 分析仪软件启用 Extended Frame 解码。

如果分析仪只显示 11-bit 标准帧或大量错误帧，先不要看 J1939 层，优先修 CAN 物理层和位时序。

## 29-bit ID 拆解

J1939 使用 CAN 29-bit 扩展 ID。

常见字段：

```text
Priority | Reserved | Data Page | PDU Format | PDU Specific | Source Address
```

简化理解：

| 字段 | 作用 |
| --- | --- |
| Priority | 仲裁优先级，数值越小优先级越高 |
| DP | Data Page，参与 PGN 计算 |
| PF | PDU Format，决定 PDU1 / PDU2 |
| PS | PDU Specific，可能是目标地址或 Group Extension |
| SA | Source Address，发送节点地址 |

调试时至少要能从 29-bit ID 中拆出：

- PGN。
- Source Address。
- Destination Address，如果是 PDU1。
- Priority。

## PDU1 和 PDU2

J1939 的 PGN 解析要区分 PF。

PDU1：

```text
PF < 240
PS = Destination Address
PGN 低 8 bit 置 0
用于点对点或目标地址相关通信
```

PDU2：

```text
PF >= 240
PS = Group Extension
PGN 包含 PS
多用于广播参数组
```

常见错误是把 PDU1 的 PS 也算进 PGN，导致过滤和 DBC 匹配失败。

## PGN 和 SPN

PGN 是 Parameter Group Number，表示一组参数。

SPN 是 Suspect Parameter Number，表示具体信号或参数。

示例关系：

```text
PGN：某一类报文，如发动机转速相关报文
SPN：报文内部某个信号，如 Engine Speed
```

每个 SPN 通常需要：

- 起始字节和位。
- 长度。
- 字节序。
- 分辨率 Resolution。
- 偏移 Offset。
- 单位。
- 无效值或错误值定义。

原始字节不能直接当工程值使用，必须按 SPN 定义换算。

## 地址和 Address Claim

J1939 节点使用 8-bit Source Address。

同一总线上地址应唯一。

地址声明用于节点上线时声明自己的地址和 NAME。

调试要点：

- 上电后观察 Address Claim 报文。
- 确认设备是否拿到预期地址。
- 检查是否有地址冲突。
- 同型号多个设备同时上电时尤其要注意地址分配策略。

常见现象：

| 现象 | 可能方向 |
| --- | --- |
| 设备上线后不发业务报文 | 地址声明失败、地址冲突、应用未启动 |
| 两个设备地址相同 | 配置重复、NAME 仲裁、固定地址冲突 |
| 网关解析错设备 | 只看 PGN 没看 Source Address |

## 请求 PGN

J1939 支持请求某个 PGN。

典型用途：

- 请求地址声明。
- 请求软件版本。
- 请求诊断信息。
- 请求非周期参数。

调试时注意：

- 请求报文目标地址是否正确。
- 被请求 PGN 是否支持请求。
- 目标设备是否处于可响应状态。
- 响应可能是单帧，也可能触发多包传输。

如果请求后无响应，不能只判断设备离线，还要检查目标地址、PGN 字节序、权限和设备状态。

## 多包传输

经典 CAN 单帧最多 8 字节，J1939 用 Transport Protocol 传输超过 8 字节的数据。

常见方式：

```text
BAM：Broadcast Announce Message，广播多包
RTS/CTS：点对点流控多包
```

BAM 特点：

- 广播发送。
- 接收方不逐包确认。
- 适合广播长数据。
- 丢包后通常只能等下一次发送。

RTS/CTS 特点：

- 点对点。
- 接收方通过 CTS 控制发送节奏。
- 适合更可靠的长数据传输。

多包调试重点：

- 总长度是否正确。
- 包数量是否正确。
- Sequence Number 是否连续。
- TP.CM 和 TP.DT 是否匹配。
- 目标 PGN 是否正确。
- 超时和 Abort 原因。

## DBC 和参数数据库

J1939 调试强依赖数据库。

数据库通常描述：

- PGN。
- SPN。
- 信号名称。
- 起始位和长度。
- 缩放和偏移。
- 单位。
- 枚举值。
- 无效值。

常见问题：

| 现象 | 优先检查 |
| --- | --- |
| 原始帧有但无解码 | PGN 计算、PDU1/PDU2、DBC 版本 |
| 数值明显不对 | 字节序、缩放、偏移、单位 |
| 某些信号一直无效 | 无效值定义、设备未使能、信号条件不满足 |
| 同一 PGN 多源冲突 | Source Address 没过滤、多个 ECU 同时发送 |

DBC 只能保证解析规则，不保证现场设备一定按同一版本实现。

## 抓包和过滤方法

CAN 分析仪或日志工具应优先支持：

- 扩展帧显示。
- J1939 PGN 解码。
- Source Address 过滤。
- DBC 加载。
- 多包重组。
- 时间戳和周期统计。

常用观察维度：

```text
按 Source Address 看节点
按 PGN 看参数组
按周期看丢帧或抖动
按多包会话看 BAM/RTS/CTS
按诊断 PGN 看故障码
```

现场排查建议：

1. 先确认总线无 Error Frame、Bus Off 和错误计数异常。
2. 确认所有目标设备有 Address Claim。
3. 按 Source Address 列出在线节点。
4. 按 PGN 过滤核心业务报文。
5. 加载 DBC 或协议数据库解析 SPN。
6. 检查周期和超时。
7. 对长报文检查多包重组。
8. 对网关场景检查源地址、目标地址和 PGN 映射。

## 网关和终端设备注意

车队监控、T-Box、边缘网关常见需求是把 J1939 数据转成 MQTT、HTTP、Modbus 或私有协议。

网关设计要明确：

- 采集哪些 PGN 和 SPN。
- 每个 SPN 的上报周期。
- 无效值是否上报。
- 断线缓存策略。
- 多源同 PGN 如何区分。
- 是否主动请求非周期 PGN。
- 是否参与地址声明。
- 是否只监听，还是会主动发送请求或控制报文。

只监听设备通常风险较低；主动发送请求或控制报文时，要确认不会影响车辆或设备控制安全。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 完全无帧 | CANH/CANL、电源、终端、波特率、分析仪扩展帧设置 |
| 有错误帧 | 波特率、采样点、接线、终端、干扰 |
| 有帧但解析不到 PGN | 29-bit 扩展帧、PDU1/PDU2、DBC 版本 |
| 只有部分设备在线 | 地址声明、设备供电、地址冲突、网段分支 |
| SPN 数值不对 | 缩放、偏移、字节序、单位、无效值 |
| 多包数据不完整 | BAM/RTS/CTS、序号、超时、丢帧 |
| 网关上传数据混乱 | Source Address、PGN 过滤、DBC 映射、时间戳 |
| 请求无响应 | 目标地址、请求 PGN、设备状态、权限、是否支持请求 |

## 实战检查清单

- CAN 扩展帧已启用。
- 波特率和采样点与车辆或设备总线一致。
- CANH/CANL、终端和参考地正确。
- 能看到 Address Claim。
- 每个节点 Source Address 唯一。
- PGN 解析区分 PDU1 和 PDU2。
- DBC 或参数数据库版本明确。
- SPN 缩放、偏移、单位和无效值处理正确。
- 多包传输能重组并处理超时。
- 网关按 Source Address 区分同 PGN 多来源。
- 主动请求或发送报文前已评估现场安全影响。

## 与 CANopen 的区别

CANopen 常围绕 Node ID、对象字典、SDO、PDO、NMT 和 Heartbeat 调试。

J1939 常围绕 Source Address、PGN、SPN、Address Claim、Request、BAM/RTS/CTS 和 DBC 调试。

二者都基于 CAN，但上层模型完全不同，不能把 CANopen 的 COB-ID 思路直接套到 J1939。

## 延伸阅读

- `bus/j1939.md`
- `bus/can.md`
- `basic/can-phy.md`
- `bus/can-canopen-practical.md`
- `bus/can-canopen-deep-dive.md`
