# CAN PHY

## 定位

CAN PHY 是 CAN 总线的物理层，负责把控制器的数字信号转换为 `CANH/CANL` 差分信号。

典型结构：

```text
MCU CAN Controller <-> CAN Transceiver <-> CANH/CANL Bus
```

MCU 的 `CAN_TX/CAN_RX` 不能直接接总线。

## CANH / CANL

CAN 使用差分信号。

常见状态：

```text
显性位 dominant：CANH 和 CANL 产生明显差分
隐性位 recessive：CANH 和 CANL 差分较小
```

经典 CAN 中通常可理解为：

```text
dominant = 0
recessive = 1
```

## 终端电阻

总线两端通常各加：

```text
120Ω
```

断电测 `CANH` 和 `CANL` 之间，典型约：

```text
60Ω
```

不要每个节点都加终端。

## 拓扑

推荐总线型拓扑，分支尽量短。

高速 CAN 和 CAN FD 对拓扑更敏感。

## 常见错误

| 现象 | 优先检查 |
| --- | --- |
| 无通信 | 收发器、电源、终端、波特率 |
| Bus Off | CANH/CANL、终端、干扰、ACK |
| 断电测不是 60Ω | 终端缺失或过多 |
| 偶发错误帧 | 拓扑、分支、线缆、采样点 |

## 延伸阅读

- `bus/can-canopen-practical.md`
- `bus/can-canopen-deep-dive.md`
