# CAN + CANopen Deep Dive

## 目标

本文深入 CAN 与 CANopen 工程细节，重点覆盖 CAN 位时序、采样点、仲裁、错误状态、Bus Off、CAN FD、CANopen COB-ID、SDO/PDO、NMT、Heartbeat、Emergency 和 CiA 402 电机控制状态机。

## 分层模型

先把层级分清：

```text
CAN PHY：CANH/CANL 差分物理层
CAN：帧、ID、仲裁、ACK、CRC、错误处理
CANopen：对象字典、SDO、PDO、NMT、Heartbeat、EMCY
CiA 402：CANopen 上的电机驱动设备状态机
```

典型链路：

```text
MCU CAN Controller <-> CAN Transceiver <-> CANH/CANL Bus
```

MCU 的 `CAN_TX/CAN_RX` 不能直接接 `CANH/CANL`，必须经过 CAN 收发器。

## CAN 和 RS485 的核心差异

`RS485 + Modbus RTU`：

```text
主站轮询
从站响应
上层协议避免冲突
```

`CAN`：

```text
多节点都可以主动发送
通过 ID 仲裁决定谁先发
硬件内建错误检测和重发
```

这就是 CAN 适合车载、BMS、电机和分布式控制的原因。

## CAN 终端和拓扑

CAN 总线两端通常各加：

```text
120Ω
```

断电测 `CANH` 和 `CANL` 之间通常约：

```text
60Ω
```

推荐拓扑：

```text
Node1 ---- Node2 ---- Node3 ---- Node4
```

避免长星型和长分支。

分支越长，高速下反射越明显。

## 位时序基础

CAN 一位时间由多个时间段组成：

```text
Sync Segment
Propagation Segment
Phase Segment 1
Phase Segment 2
```

工程上常见配置参数：

```text
prescaler
time quanta
BS1 / TSEG1
BS2 / TSEG2
SJW
sample point
```

不同 MCU 命名略有差异。

## 采样点

采样点是 CAN 位时间中读取总线电平的位置。

常见经验：

```text
500 kbps / 1 Mbps 常见采样点约 75%~87.5%
长线或传播延迟大时采样点可能需要后移
```

如果波特率一样但采样点差异过大，仍可能通信不稳定。

现场问题表现：

- 偶发错误帧。
- 高速不稳定。
- 节点多后不稳定。
- 线长增加后不稳定。

## SJW

`SJW` 是 Synchronization Jump Width。

它决定 CAN 控制器重新同步时可以调整的时间宽度。

作用：

```text
补偿节点时钟误差和边沿相位偏差
```

SJW 不是越大越好，要结合位时序配置和控制器限制。

## 仲裁机制

CAN 使用显性位和隐性位仲裁。

经典理解：

```text
显性位 = 0
隐性位 = 1
```

总线规则：

```text
只要有节点发送 0，总线就是 0
所有节点发送 1，总线才是 1
```

节点一边发送一边监听。

如果自己发送 1，却读到 0，说明输了仲裁。

输掉的节点停止发送，胜出的节点继续发送。

这叫：

```text
非破坏性仲裁
```

胜出消息不会被破坏。

## ID 优先级

CAN ID 越小，优先级通常越高。

例如：

```text
0x100 优先级高于 0x200
```

设计 ID 时应考虑：

- 紧急故障消息使用更高优先级。
- 控制命令优先于普通状态。
- 高频消息不要全部使用最高优先级。
- 避免低优先级消息长期饥饿。

## ID 不是设备地址

CAN ID 通常表示消息含义，而不是目标设备地址。

例如：

```text
0x100：电机控制命令
0x180：电机状态反馈
0x200：BMS 电压信息
0x300：故障事件
```

所有节点都能收到帧，再根据 ID 过滤。

上层协议可以把节点号编码进 ID，例如 CANopen。

## 标准帧和扩展帧

标准帧：

```text
11-bit ID
范围 0x000 ~ 0x7FF
```

扩展帧：

```text
29-bit ID
范围 0x00000000 ~ 0x1FFFFFFF
```

选择建议：

- 简单自定义协议优先标准帧。
- J1939 等协议使用扩展帧。
- 混用标准帧和扩展帧时要明确过滤规则。

## ACK 机制

发送节点发送一帧后，需要至少一个接收节点在 ACK 位应答。

ACK 表示：

```text
至少有一个节点正确收到该 CAN 帧
```

不表示：

```text
业务处理成功
目标设备执行命令
所有节点都收到
```

如果总线上只有一个节点，它通常会一直 ACK Error。

调试时至少要有另一个正常节点或分析仪应答。

## 错误类型

CAN 控制器能检测多种错误：

- Bit Error。
- Stuff Error。
- CRC Error。
- Form Error。
- ACK Error。

错误会影响发送错误计数和接收错误计数。

不同控制器提供的寄存器和状态不同，但都应关注错误计数。

## Error Active、Error Passive、Bus Off

CAN 节点有错误状态：

```text
Error Active
Error Passive
Bus Off
```

`Error Active`：

```text
正常参与通信，能主动发送错误帧
```

`Error Passive`：

```text
错误较多，通信能力受限，错误影响降低
```

`Bus Off`：

```text
错误过多，节点退出总线，避免持续干扰
```

Bus Off 常见原因：

- 波特率不一致。
- CANH/CANL 接反。
- 没有终端。
- 总线上没有其他节点 ACK。
- 收发器供电异常。
- 强干扰或短路。

## Bus Off 恢复策略

Bus Off 后不要只盲目重启控制器。

推荐策略：

```text
记录错误状态
停止发送应用报文
等待一段恢复时间
重新初始化 CAN 控制器
恢复前先确认总线物理状态
恢复后低频发送测试帧
```

如果物理问题未解决，自动恢复会反复 Bus Off。

## CAN FD

CAN FD 相比经典 CAN：

```text
单帧数据可到 64 字节
数据段可使用更高速率
```

需要注意：

- 控制器必须支持 CAN FD。
- 收发器要支持目标速率。
- 总线所有相关节点要兼容。
- 仲裁段仍受传统 CAN 规则约束。
- 数据段高速对线缆和拓扑更敏感。

不要把经典 CAN 网络直接改配置当 CAN FD 使用。

## CAN 过滤器

CAN 是广播总线。

控制器过滤器用于减少 CPU 负担。

过滤方式常见：

```text
ID list
ID mask
FIFO routing
standard/extended frame filter
```

常见问题：

- ID mask 配错导致收不到帧。
- 标准帧/扩展帧类型不匹配。
- FIFO 满导致丢帧。
- 过滤器顺序影响匹配。

## 裸 CAN 协议设计建议

自定义 CAN 协议建议定义：

- ID 分配表。
- 周期帧。
- 事件帧。
- 命令帧。
- 心跳帧。
- 数据字节序。
- 缩放系数和单位。
- 超时策略。
- 版本号。
- 故障码。

不要只在代码里隐式定义 ID 含义。

## CANopen 核心对象

CANopen 建立在 CAN 之上。

核心概念：

```text
Node ID
Object Dictionary
COB-ID
SDO
PDO
NMT
Heartbeat
Emergency
EDS
```

对象字典使用：

```text
Index + Sub-index
```

例如：

```text
6040:00 Controlword
6041:00 Statusword
6060:00 Modes of operation
607A:00 Target position
6064:00 Position actual value
```

## COB-ID 默认规则

CANopen 默认常用：

| 通信对象 | COB-ID |
| --- | --- |
| NMT | 0x000 |
| SYNC | 0x080 |
| EMCY | 0x080 + Node ID |
| TPDO1 | 0x180 + Node ID |
| RPDO1 | 0x200 + Node ID |
| TPDO2 | 0x280 + Node ID |
| RPDO2 | 0x300 + Node ID |
| SDO Tx | 0x580 + Node ID |
| SDO Rx | 0x600 + Node ID |
| Heartbeat | 0x700 + Node ID |

Node ID 为 `2` 时：

```text
SDO Rx = 0x602
SDO Tx = 0x582
TPDO1  = 0x182
RPDO1  = 0x202
```

## SDO

SDO 用于读写对象字典，适合配置和诊断。

特点：

```text
一问一答
可靠确认
适合低频访问
不适合高频实时控制
```

读取 `6041:00`：

```text
CAN ID: 0x600 + Node ID
Data:   40 41 60 00 00 00 00 00
```

注意小端：

```text
6041h -> 41 60
```

## SDO 命令字

常见 expedited SDO 命令字：

| 命令字 | 含义 |
| --- | --- |
| 40 | 读请求 |
| 2F | 写 1 字节 |
| 2B | 写 2 字节 |
| 23 | 写 4 字节 |
| 4F | 返回 1 字节 |
| 4B | 返回 2 字节 |
| 43 | 返回 4 字节 |
| 60 | 写成功响应 |
| 80 | SDO Abort |

SDO Abort 不应忽略，它会给出失败原因。

常见原因：

- 对象不存在。
- 子索引不存在。
- 只读对象被写。
- 数据长度不匹配。
- 当前状态不允许访问。

## PDO

PDO 用于实时过程数据。

特点：

```text
无一问一答
无单帧确认
传输效率高
需要预先映射
```

典型电机：

```text
RPDO：主控 -> 驱动器，控制字、目标位置、目标速度
TPDO：驱动器 -> 主控，状态字、实际位置、实际速度
```

PDO 映射决定每一帧的字节含义。

## PDO 映射注意

配置 PDO 映射时通常要：

```text
禁用 PDO
清空映射数量
写入映射对象
写入映射数量
配置 COB-ID 和传输类型
重新启用 PDO
```

常见对象：

```text
1600h：RPDO1 Mapping
1A00h：TPDO1 Mapping
1400h：RPDO1 Communication Parameter
1800h：TPDO1 Communication Parameter
```

不同设备可能限制哪些对象可映射。

## PDO 传输类型

PDO 可能按不同方式发送：

- 同步发送，跟随 SYNC。
- 异步事件触发。
- 周期定时。
- 远程请求，较少用。

调试时要确认：

```text
是否需要 SYNC
事件定时器是否配置
抑制时间是否配置
设备是否已 Operational
```

## NMT 状态机

CANopen NMT 常见状态：

```text
Initialization
Pre-operational
Operational
Stopped
```

典型流程：

```text
上电 Boot-up
进入 Pre-operational
SDO 配置参数
NMT Start
进入 Operational
PDO 开始工作
```

启动节点 2：

```text
CAN ID: 0x000
Data:   01 02
```

## Heartbeat

Heartbeat 用于在线监测。

节点发送：

```text
CAN ID: 0x700 + Node ID
Data:   NMT state
```

常见状态值：

| 值 | 状态 |
| --- | --- |
| 0x00 | Boot-up |
| 0x04 | Stopped |
| 0x05 | Operational |
| 0x7F | Pre-operational |

主控应监测 Heartbeat 超时，不能只假设节点一直在线。

## Emergency

Emergency 报文用于故障主动上报。

默认 COB-ID：

```text
0x080 + Node ID
```

常见内容：

- Emergency Error Code。
- Error Register。
- 厂商自定义错误字段。

适合报告：

- 过压。
- 欠压。
- 过流。
- 过温。
- 编码器错误。
- 通信错误。

## CiA 402 电机状态机

很多 CANopen 电机驱动遵循 CiA 402。

核心对象：

```text
6040h Controlword
6041h Statusword
6060h Modes of operation
6061h Modes of operation display
607Ah Target position
6064h Position actual value
60FFh Target velocity
6077h Torque actual value
```

常见状态：

```text
Switch On Disabled
Ready to Switch On
Switched On
Operation Enabled
Fault
```

典型使能序列：

```text
6040 = 0x0006
6040 = 0x0007
6040 = 0x000F
```

实际状态跳转必须根据 `6041h` 判断，不要盲目延时后认为成功。

## 电机不动的常见原因

CANopen 电机不动时，优先检查：

- 节点是否进入 Operational。
- 驱动是否 Fault。
- `6041h` 是否 Operation Enabled。
- `6060h` 操作模式是否正确。
- 目标值单位和缩放是否正确。
- 控制字是否触发新目标。
- PDO 映射是否与主控一致。
- 限位、急停、使能输入是否满足。
- 电机功率电源是否正常。

## CANopen 调试顺序

推荐步骤：

1. 裸 CAN 通信正常。
2. 收到 Boot-up。
3. 读取 `1000h` 设备类型。
4. 读取 `1018h` Identity Object。
5. 配置 Heartbeat。
6. 用 SDO 读取关键对象。
7. 配置 PDO 映射。
8. NMT Start。
9. 观察 TPDO。
10. 下发 RPDO。
11. 处理 EMCY 和 Heartbeat 超时。

## 工具建议

常用工具：

- CAN 分析仪。
- CANopen 主站工具。
- 厂商调试软件。
- PCAN/CANable/CANcase 等适配器。
- 示波器。

调试时建议保存：

- DBC 或 ID 表。
- EDS 文件。
- 对象字典文档。
- CAN 抓包。
- 错误计数。
- Bus Off 记录。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 无帧 | 收发器、电源、波特率、终端 |
| ACK Error | 总线上无其他节点、波特率不一致 |
| Bus Off | CANH/CANL、终端、波特率、干扰 |
| 只能发不能收 | 过滤器、接线、收发器 RXD |
| SDO Abort | 对象不存在、权限、状态、长度 |
| PDO 不发 | 未 Operational、传输类型、映射 |
| Heartbeat 超时 | 节点掉线、总线错误、Node ID 错 |
| 电机不使能 | CiA 402 状态机、Fault、硬件使能 |

## 深度检查清单

- CANH/CANL 和终端电阻正确。
- 断电测总线约 60Ω。
- 波特率、采样点和 SJW 合理。
- 至少有一个节点 ACK。
- 错误计数和 Bus Off 有日志。
- CAN ID 优先级设计合理。
- 过滤器不会误丢目标帧。
- CANopen Node ID 唯一。
- SDO 小端字节序正确。
- NMT 已进入 Operational。
- PDO 映射和主控解析一致。
- Heartbeat 和 EMCY 已处理。
- CiA 402 状态机按 Statusword 判断。
