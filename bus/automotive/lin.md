---
tags:
  - layer/bus
  - type/overview
  - protocol/lin
  - topic/automotive
---

# LIN

## 定位

LIN（Local Interconnect Network）是**低成本车载局部互联总线**，由 ISO 17987 标准化。

它的设计目标很明确：用最便宜的硬件实现车身低速设备的通信，让车窗、座椅、雨刮这类简单执行器不必占用 CAN 节点。

```text
CAN  →  多 master、实时性强、贵
LIN  →  单 master、成本低、够用
```

**LIN 不是 CAN 家族的成员**，两者是互补关系：CAN 负责整车主干通信，LIN 负责车门/座椅等局部低速网络。

## 与 CAN 的核心差异

| 维度 | CAN | LIN |
| --- | --- | --- |
| 拓扑 | 多节点共享总线 | 单 master + 多 slave |
| 信号 | 差分 CAN_H / CAN_L | **单线** |
| 速率 | 500 kbps ~ 5 Mbps | 10 / 20 kbps |
| 仲裁 | 硬件非破坏性仲裁 | 无仲裁，靠调度表 |
| 寻址 | CAN ID 广播 | 帧 ID 在 Header 里，由 Master 指定 |
| 数据 | 8 字节（FD 64） | 1-8 字节 |
| 校验 | CRC + 错误计数 | Checksum（Classic / Enhanced） |
| 错误处理 | Error Passive / Bus Off | 简单重试 |
| 成本 | 高 | 低 |
| 典型设备 | 整车 ECU、动力域 | 车窗、座椅、雨刮、门锁 |

## 物理层

三根线：

```text
LIN      单线信号
VBAT     12V 供电
GND      地
```

LIN 空闲电平是 **1（ recessive）**，逻辑 0 是**低电平（dominant）**。

关键点：

- 必须通过 **LIN 收发器**接入，MCU 的 UART TX/RX 不能直接接总线。
- 总线两端各一个上拉电阻（典型 1 kΩ 到 VBAT），加上收发器内部上拉，总阻值约 500 Ω ~ 1 kΩ。
- 12V 车载环境必须考虑 **ESD、负载突降、EMC**。
- 有睡眠/唤醒机制，靠主机发 Wakeup 脉冲或从机发 Wakeup Request。

## 帧结构

```text
Break | Sync | Protected ID | Data (1-8) | Checksum
```

### Break

主节点发送的**长低电平**（典型 500 µs ~ 2 ms），标志帧开始，同时用于同步从节点。

### Sync

固定 `0x55`，从节点用它来测量波特率并锁定。

### Protected Identifier

2 字节：

```text
byte0: ID[1:0] | ID[5:4] | Parity
byte1: ID[7:2]
```

`Protected` 的含义是：**ID 的两个奇偶校验位让从节点能在不接收完整个 ID 的情况下就判断"这个帧是不是给我的"**，从而提前准备响应。

奇偶校验：

```text
P1 = ID0 ⊕ ID1 ⊕ ID2 ⊕ ID4
P0 = ID1 ⊕ ID3 ⊕ ID4 ⊕ ID5
```

ID 范围 `0x00 ~ 0x3F`（6 bit，共 64 个）。

### Data

1-8 字节，含义由 LDF 定义。

### Checksum

```text
Classic Checksum:   仅覆盖 Data
Enhanced Checksum:  覆盖 Protected ID + Data
```

用哪种**取决于具体帧的定义**，Master 和 Slave 必须一致 —— 这是最常见的配置错误来源。

## 调度机制

LIN 是**纯时间触发**的，Master 持有调度表决定"什么时候发哪个 Header"。

```text
调度表示例:
  0x11  10ms   -> Door_Light
  0x12  20ms   -> Window_Up
  0x13  100ms  -> Seat_Position
  0x14  200ms  -> Diagnostic_Master
```

帧内还分两种槽：

```text
Header Slot:  Master 发 Header, Slave 准备响应
Response Slot: Slave 发 Data
```

即使 Master 只是查询状态，也要占用 Header + Response 两段时间。

### 诊断

LIN 有专门的诊断帧（0x3C Master Request / 0x3D Slave Response），用于：

- 节点地址分配（Initial Assign / Conditional Assign）。
- 读取/修改节点配置。
- 读取状态。

## LDF

LIN Description File（`.ldf`）描述整个网络：

```text
节点定义  Node_Com_positions
帧定义    Frame: ID, Publisher, Subscribers, Length
信号定义  Signal: Name, Size, Init_value, Publisher, Subscribers
调度表    Schedule_table
编码      Logical_value, Physical_value, Scale, Offset, Unit
```

**工程铁律**：主从双方的信号解析必须来自**同一份 LDF**，不要各自手写偏移量。

## 睡眠与唤醒

```text
Wakeup: 主机发 dominant 脉冲 (> 50ms)
Wakeup Request: 从机发 13 位 0x3C + 0x00 + pulse
Sleep: 主机发送 0x3C + 0x01 + 0x00 + pulse
```

节能是 LIN 的重要卖点（车身静态电流要求很严）。

## 与 CAN 的工程选型

```text
需要 CAN:
  - 多节点都要主动发数据
  - 高实时性 (ms 级硬约束)
  - 故障安全要求高
  - 需要错误状态机和 Bus Off
  - 刷写 / 大数据量传输

需要 LIN:
  - 一个中心节点控制若干简单从设备
  - 数据量小 (1-8 字节)
  - 成本敏感
  - 低速场景 (车窗、座椅)
  - 需要低静态电流
```

## 延伸阅读

- [[bus/automotive/lin-practical|lin-practical]] — LIN 实战：调试步骤、故障定位、检查清单
- [[bus/automotive/can-protocol-family|can-protocol-family]] — CAN 家族全景（LIN 与 CAN 的对比）
- [[basic/can-vs-other-bus|can-vs-other-bus]] — CAN 与其他总线横向对比
- [[basic/uart-deep-dive|uart-deep-dive]] — LIN 数据格式与 UART 的关系
- [[LAYERED_MAP|LAYERED_MAP]] — 全库分层地图

## 更新记录

- 2026-10-31: 初版。补齐 LIN 概念页，闭合 CAN 家族覆盖表中的最后一项可补缺口。
