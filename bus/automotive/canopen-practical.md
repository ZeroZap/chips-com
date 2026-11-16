# CAN + CANopen Practical Guide

## 目标

本文用于把 CAN 物理层、CAN 帧和 CANopen 设备模型联合调通，适合电机驱动、IO 模块、工业设备和 BMS。

## 分层关系

```text
CAN PHY：CANH/CANL 差分信号
CAN：帧、ID、仲裁、ACK、错误处理
CANopen：Node ID、对象字典、SDO、PDO、NMT、Heartbeat
```

## 硬件接线

```text
MCU CAN_TX -> CAN Transceiver TXD
MCU CAN_RX <- CAN Transceiver RXD
CANH/CANL  -> CAN 总线
GND        -> 参考地或隔离参考
```

MCU 的 `CAN_TX/CAN_RX` 不能直接接 `CANH/CANL`。

## 终端电阻

总线两端各加：

```text
120Ω
```

断电后测 `CANH` 和 `CANL` 之间，典型约：

```text
60Ω
```

## CAN 基础调通

1. 确认所有节点波特率一致，例如 500 kbps。
2. 确认 CANH/CANL 没接反。
3. 用 CAN 分析仪发送固定 ID 帧。
4. 检查 ACK、错误计数和 Bus Off 状态。
5. 先用标准帧，再按需要启用扩展帧。
6. 裸 CAN 跑通后再上 CANopen。

## CANopen 默认 COB-ID

节点 `Node ID = 2` 时：

```text
TPDO1     = 0x182
RPDO1     = 0x202
SDO Tx    = 0x582
SDO Rx    = 0x602
Heartbeat = 0x702
```

记住：

```text
Node ID 不是 CAN ID
COB-ID 才是实际发送的 CAN ID
```

## SDO 读取对象

读取节点 2 的 `6041:00` 状态字：

```text
CAN ID: 0x602
Data:   40 41 60 00 00 00 00 00
```

响应示例：

```text
CAN ID: 0x582
Data:   4B 41 60 00 27 02 00 00
```

`Index` 使用小端：

```text
6041h -> 41 60
```

## NMT 启动节点

启动节点 2：

```text
CAN ID: 0x000
Data:   01 02
```

启动所有节点：

```text
CAN ID: 0x000
Data:   01 00
```

## 电机驱动简化流程

1. 等待 `0x700 + Node ID` Boot-up。
2. 用 SDO 设置模式，例如 `6060:00`。
3. 配置 PDO 映射和通信参数。
4. NMT Start 进入 Operational。
5. 按 CiA 402 状态机写 `6040h` 控制字。
6. 通过 `6041h` 状态字确认 Operation Enabled。
7. 运行中用 PDO 周期交换目标值和反馈值。

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| 无任何帧 | 收发器、电源、终端、波特率 |
| ACK Error | 总线上无其他正常节点、波特率错 |
| Bus Off | CANH/CANL、终端、波特率、干扰 |
| SDO 无响应 | COB-ID、Node ID、状态、对象权限 |
| PDO 不工作 | 未 Operational、映射错误、COB-ID 冲突 |
| 电机不动 | CiA 402 状态机、使能、故障、控制字 |

## 实战检查清单

- CAN PHY 和终端电阻正确。
- 波特率和采样点匹配。
- Node ID 唯一。
- Heartbeat 正常。
- SDO 字节序正确。
- NMT 已进入 Operational。
- PDO 映射与主站解析一致。
