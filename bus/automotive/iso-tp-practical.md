# ISO-TP Practical Guide

## 目标

本文用于 ISO-TP 工程调试，重点覆盖 CAN ID、寻址、单帧/多帧、Flow Control、Block Size、STmin、超时和 UDS 承载。

## 最小前提

先确认裸 CAN 正常：

- CANH/CANL 接线正确。
- 波特率一致。
- 两节点可互发帧。
- 标准帧/扩展帧类型确认。

ISO-TP 是 CAN 之上的传输层，不解决物理层问题。

## 帧类型

ISO-TP 常见 PCI 类型：

```text
Single Frame
First Frame
Consecutive Frame
Flow Control
```

短数据用 Single Frame。

长数据流程：

```text
Sender -> First Frame
Receiver -> Flow Control
Sender -> Consecutive Frame 1..N
```

## Flow Control

Flow Control 控制发送节奏。

关键字段：

```text
Flow Status
Block Size
STmin
```

`Block Size` 表示连续发送多少个 CF 后需要再等 FC。

`STmin` 表示连续帧之间最小间隔。

## UDS 常见 ID

UDS over CAN 常见一对 ID：

```text
Tester -> ECU
ECU -> Tester
```

具体 ID 由整车或 ECU 规范定义。

不要假设所有 ECU 都用同一组 ID。

## 调试步骤

1. 裸 CAN 通信确认。
2. 确认请求 ID 和响应 ID。
3. 先发送短 UDS 请求，验证 Single Frame。
4. 再读取长 DID，验证 First/Flow/Consecutive。
5. 调整 Block Size 和 STmin。
6. 检查超时和序号。
7. 再做刷写或大数据传输。

## 常见故障

| 现象 | 优先检查 |
| --- | --- |
| 单帧正常多帧失败 | Flow Control、STmin、Block Size |
| 连续帧中断 | 超时、序号、接收缓冲区 |
| ECU 无响应 | CAN ID、会话、安全访问、寻址方式 |
| 数据长度错误 | First Frame length、重组缓冲区 |

## 检查清单

- CAN 帧类型和 ID 确认。
- Single Frame 已验证。
- Flow Control 正确发送。
- CF 序号连续。
- STmin 和 Block Size 被遵守。
- 超时参数合理。
- 上层 UDS 状态机正确。
