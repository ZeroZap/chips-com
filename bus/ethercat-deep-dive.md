# EtherCAT Deep Dive

## 目标

本文深入 EtherCAT 工程细节，重点覆盖主站/从站、ESC、On-the-fly、过程数据、Mailbox、CoE、状态机、分布式时钟、WKC、ESI、拓扑和常见调试问题。

## EtherCAT 的定位

EtherCAT 是实时工业以太网协议，常用于：

- 多轴伺服。
- 运动控制。
- 高速 IO。
- 机器人。
- 半导体设备。
- 精密自动化。

它不是普通 TCP/IP 应用协议。

EtherCAT 直接使用以太网帧实现实时过程数据交换。

## On-the-fly

EtherCAT 核心是 On-the-fly 处理。

主站发送一帧，帧经过每个从站时：

```text
从站读取属于自己的输出数据
从站写入自己的输入数据
立即转发给下一个从站
```

优点：

- 高效率。
- 低延迟。
- 多从站一帧交换过程数据。

## 主站和从站

Master 负责：

- 扫描从站。
- 读取 ESI/配置。
- 初始化状态机。
- 配置 PDO 映射。
- 周期发送过程数据帧。
- 分布式时钟同步。
- 错误诊断。

Slave 负责：

- 通过 ESC 处理 EtherCAT 帧。
- 映射输入输出数据。
- 提供 Mailbox。
- 执行业务逻辑。

## ESC

ESC 是 EtherCAT Slave Controller。

从站通常需要 ESC：

```text
EtherCAT PHY/Port <-> ESC <-> MCU/FPGA/Application
```

常见 ESC：

- ET1100。
- LAN9252。
- AX58100。
- MCU/SoC 内置 ESC。

普通 Ethernet MAC + TCP/IP 不能直接作为标准 EtherCAT 从站。

## 状态机

EtherCAT 从站常见状态：

```text
INIT
PRE-OP
SAFE-OP
OP
```

含义：

- INIT：基础初始化。
- PRE-OP：Mailbox 可用，可配置。
- SAFE-OP：输入过程数据可用，输出未完全生效。
- OP：输入输出过程数据正常运行。

设备未进入 OP 时，过程输出通常不会真正生效。

## 过程数据

过程数据用于周期实时交换。

例如伺服：

```text
主站 -> 从站：控制字、目标位置、目标速度
从站 -> 主站：状态字、实际位置、实际速度
```

周期可能是：

```text
1 ms
500 us
250 us
```

过程数据映射错误会导致控制数据错位。

## Mailbox

Mailbox 用于非周期低频通信。

常见协议：

```text
CoE：CANopen over EtherCAT
FoE：File over EtherCAT
EoE：Ethernet over EtherCAT
SoE：Servo over EtherCAT
```

配置对象字典、下载固件、读取诊断通常走 Mailbox。

## CoE

CoE 让 EtherCAT 设备使用类似 CANopen 的对象字典。

常见电机对象：

```text
6040h Controlword
6041h Statusword
6060h Mode of operation
607Ah Target position
6064h Position actual value
```

学过 CANopen 后，理解 EtherCAT 伺服会更容易。

## 分布式时钟 DC

DC 用于多从站高精度同步。

适合：

- 多轴同步控制。
- 同步采样。
- 机器人关节控制。

常见问题：

- DC 未启用。
- 参考时钟选择错误。
- 周期抖动过大。
- 从站同步误差超限。

## WKC

WKC 是 Working Counter。

主站通过 WKC 判断从站是否正确处理了命令。

WKC 不符合预期可能表示：

- 从站掉线。
- 状态不对。
- PDO 映射不匹配。
- 命令未被目标从站处理。
- 拓扑变化。

调试 EtherCAT 时，WKC 是核心指标。

## ESI

ESI 是 EtherCAT Slave Information。

它描述：

- 厂商信息。
- 产品代码。
- 对象字典。
- PDO 映射。
- Mailbox。
- DC 能力。
- 同步管理器。

ESI 与设备固件版本不匹配会导致配置失败或无法进入 OP。

## 调试步骤

1. 主站扫描到所有从站。
2. 确认 ESI 匹配。
3. 从 INIT 进入 PRE-OP。
4. Mailbox 正常。
5. 配置 PDO 映射。
6. 进入 SAFE-OP。
7. 检查输入过程数据。
8. 配置 DC。
9. 进入 OP。
10. 检查 WKC 和周期抖动。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 扫不到从站 | 网线、端口、ESC、供电、拓扑 |
| 进不了 PRE-OP | Mailbox、ESI、从站错误 |
| 进不了 OP | PDO 映射、WKC、DC、应用错误 |
| WKC 不对 | 从站掉线、映射错、状态不对 |
| 伺服不动 | CoE 对象、CiA 402 状态机、PDO |
| 多轴不同步 | DC 配置、主站周期、从站时钟 |

## 实战检查清单

- 不把 EtherCAT 当 TCP/IP socket 协议。
- 从站硬件有 ESC。
- ESI 与固件匹配。
- 从站状态进入 OP。
- PDO 映射与主站一致。
- WKC 符合预期。
- DC 同步误差可接受。
- 周期任务实时性满足控制要求。
