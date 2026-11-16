---
tags:
  - layer/basic
  - type/overview
  - protocol/ethernet
---

# Ethernet PHY

## 定位

Ethernet PHY 是以太网物理层芯片，负责把 MAC 的数字接口转换为双绞线上的差分信号，并完成链路建立、自协商、编码和部分诊断功能。

典型结构：

```text
MCU/SoC MAC <-> PHY <-> Magnetics <-> RJ45 <-> Cable
```

很多 MCU 只有 MAC，没有内置 PHY；也有 SoC 内置 10/100 PHY，但千兆通常需要外部 PHY。

Ethernet PHY 的工程问题通常不在“ping 通不通”，而在：

- MAC-PHY 接口时序。
- PHY 地址和 MDIO。
- 复位、时钟和电源时序。
- 磁性器件和 RJ45 连接。
- 自协商和链路状态。
- RGMII 延迟和 PCB 信号完整性。
- EMC/ESD 和 PoE。

## MAC-PHY 接口

| 接口  | 数据位宽               | 时钟             | 典型速率    | 特点                |
| ----- | ---------------------- | ---------------- | ----------- | ------------------- |
| MII   | 4 位 TX + 4 位 RX      | 25 MHz / 2.5 MHz | 100/10 Mbps | 引脚多，时序宽松    |
| RMII  | 2 位 TX + 2 位 RX      | 50 MHz REF_CLK   | 100/10 Mbps | 引脚少，时钟要求高  |
| GMII  | 8 位 TX + 8 位 RX      | 125 MHz          | 1000 Mbps   | 引脚多              |
| RGMII | 4 位 TX + 4 位 RX，DDR | 125 MHz          | 1000 Mbps   | 常见千兆，需 delay  |
| SGMII | 串行                   | 1.25 Gbps 等     | 1000 Mbps   | 走线少，常经 SerDes |

### RMII

RMII 常见信号：

```text
REF_CLK   50 MHz 参考时钟
TXD0/TXD1
RXD0/RXD1
TX_EN
CRS_DV
MDIO/MDC
```

注意：

- REF_CLK 可以由 MAC、PHY 或外部时钟源提供。
- 50 MHz 时钟的抖动和走线要控制。
- RMII 只有 2 位数据，时序余量比 MII 小。
- 100M 和 10M 的时钟/采样关系不同。

### RGMII

RGMII 在 125 MHz 时钟的上升沿和下降沿都传数据（DDR），因此对时序非常敏感。

关键点：

- TX/RX 方向可能需要内部或外部 delay。
- delay 配置错误会导致链路不稳定或完全不通。
- PCB 走线长度、阻抗、过孔和串阻影响时序。
- 不同 PHY/MAC 的 delay 默认值不同。
- 1 Gbps 下时序余量最小，10/100 Mbps 可能正常但千兆失败。

## MDIO / MDC

MAC 通过 MDIO/MDC 管理 PHY：

```text
MDC：管理时钟
MDIO：双向管理数据
```

可读取/配置：

- PHY ID。
- Link 状态。
- 自协商结果。
- 速率/双工。
- 寄存器、LED、测试模式。
- 中断/诊断。

常见问题：

- PHY 地址错误。
- MDIO 缺上拉。
- MDC 频率过高/过低。
- 复位未释放。
- MDIO 与 MAC 的时序/驱动配置不匹配。

MDIO 不通时，Linux 通常看不到 PHY，`ethtool` 也无法读取链路信息。

## 复位、时钟与电源

上电顺序通常包括：

1. 电源稳定。
2. 参考时钟稳定。
3. 复位保持足够时间。
4. 释放复位。
5. MDIO 可访问。
6. 自协商/链路建立。

注意：

- 复位脉宽和释放时序按 PHY 手册。
- 有些 PHY 要求复位后等待 PLL 锁定。
- 参考时钟缺失时，MDIO 可能能读但链路不建立。
- 电源纹波会影响眼图和误码。
- 1.2 V/2.5 V/3.3 V 等多电源域的上电顺序要确认。

## 自协商与链路

自协商（Auto-Negotiation）交换：

```text
速率：10/100/1000 Mbps
双工：半双工/全双工
流控：PAUSE
主从：1000BASE-T master/slave
```

常见问题：

- 一端强制、一端自协商，导致速率/双工不匹配。
- 双工不匹配造成碰撞、丢包和性能下降。
- 自协商关闭后，千兆主从配置错误。
- 线缆质量差导致降速或链路抖动。

排查时同时看两端：

```text
ethtool eth0
ethtool -S eth0
dmesg
PHY 寄存器
```

## 磁性器件与 RJ45

RJ45 接口通常需要：

- 网络变压器（隔离变压器）。
- 共模电感。
- 终端/偏置。
- Bob Smith 终端。
- ESD 保护。
- MagJack（集成变压器的 RJ45）。

注意：

```text
RJ45 不是 PHY
MagJack 不是 PHY
变压器不替代 PHY
```

Bob Smith 终端用于共模端接和 EMC，常见 75 Ω 到电容/地。具体按 PHY 和 EMC 设计指南。

## RGMII Delay 与 PCB

RGMII 常见失败模式：

- 千兆不通，10/100 正常。
- 链路时通时断。
- 大流量丢包。
- 温度变化后误码。
- 不同板子表现不一致。

排查方向：

- MAC/PHY 内部 delay 配置。
- TX/RX delay 是否重复叠加。
- 125 MHz 时钟质量。
- 数据/时钟走线长度匹配。
- 阻抗、过孔、串阻。
- 电源和地回流。

## PoE

PoE（Power over Ethernet）通过网线同时传数据和电源：

- 需要 PSE（供电端）和 PD（受电端）。
- 涉及检测、分级、供电和断开。
- 变压器中心抽头、PoE 控制器、隔离和散热。
- 非 PoE 设备接入 PoE 端口时要确认不会损坏。

## 常见故障树

```text
Link 不亮
├── PHY 电源/复位/时钟
├── 磁性器件/RJ45/网线
├── MDIO 不通
├── 自协商失败
└── PHY 损坏/焊接不良

MDIO 读不到
├── PHY 地址错误
├── MDC/MDIO 接反/缺上拉
├── 复位未释放
├── 时钟缺失
└── MAC 引脚复用错误

能 Link 但不通
├── MAC 地址/接口配置
├── 双工/速率不匹配
├── VLAN/IP/路由
├── DMA/驱动问题
└── 丢包/CRC 错误

千兆不稳定
├── RGMII delay
├── 125 MHz 时钟
├── PCB 走线/阻抗
├── 电源/地
└── 线缆/连接器
```

| 现象              | 优先检查                          |
| ----------------- | --------------------------------- |
| Link 不亮         | 电源、复位、时钟、磁性器件、网线  |
| MDIO 读不到       | PHY 地址、MDC、MDIO 上拉、复位    |
| 能 Link 不能 ping | MAC 配置、IP/VLAN、驱动、DMA      |
| 速率异常          | 自协商、线缆、PHY 配置            |
| 千兆不稳定        | RGMII delay、时钟、PCB、电源      |
| 大流量丢包        | DMA/缓冲、流控、双工、CPU 负载    |
| 温度变化后异常    | 时钟/电源余量、焊接、PHY 散热     |
| EMC 超标          | 变压器、Bob Smith、屏蔽、PCB 回流 |

## 测量方法

- 用示波器看参考时钟、复位、MDC/MDIO。
- 用示波器/差分探头看 RGMII 数据和时钟时序。
- 用 `ethtool`、`dmesg`、PHY 寄存器确认链路和错误计数。
- 用网线测试仪/认证仪确认线缆和连接器。
- 用眼图/误码测试评估高速余量。
- EMC 预测试看辐射和传导发射。

## 设计检查清单

- MAC-PHY 接口类型和引脚复用确认。
- PHY 地址、MDIO 上拉、MDC 频率正确。
- 复位、时钟、电源时序满足手册。
- 自协商/强制模式两端一致。
- 磁性器件、Bob Smith、ESD 保护完整。
- RGMII delay 配置唯一且经过验证。
- 差分对阻抗、长度匹配、回流路径合理。
- PoE 场景确认 PSE/PD 兼容和隔离。
- 测试点、LED、调试串口可达。
- 量产测试覆盖 Link、MDIO、吞吐和错误计数。

## 最小实验

1. 上电后读 PHY ID 和 Link 状态。
2. 用 `ethtool` 强制 100M 全双工，再恢复自协商，比较链路。
3. 用示波器测量 RMII/RGMII 时钟和数据时序。
4. 大流量 ping/iperf，观察丢包和错误计数。
5. 更换网线/变压器/delay 配置，记录千兆稳定性。

## 关联文档

- [../bus/industrial/ethernet-deep-dive.md](../bus/industrial/ethernet-deep-dive.md)：Ethernet 分层与调试。
- [../bus/industrial/ethernet-modbus-tcp-practical.md](../bus/industrial/ethernet-modbus-tcp-practical.md)：Modbus TCP 实战。
- [../bus/industrial/ethernet-tsn.md](../bus/industrial/ethernet-tsn.md)：TSN 与确定性网络。
- [../guides/troubleshooting/SCHEMATIC_CHECKLISTS.md](../guides/troubleshooting/SCHEMATIC_CHECKLISTS.md)：原理图检查清单。
