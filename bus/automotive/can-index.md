---
tags:
  - layer/bus
  - type/index
---
# CAN 家族导航

## 定位

CAN 家族覆盖从物理层到应用层的完整链路：经典 CAN、CAN FD、CAN XL、CANopen、J1939、ISO-TP、UDS、OBD-II、WWH-OBD 与 LIN。本页是 family 级总入口，负责回答“某个问题应该看哪一层、哪篇笔记”。

## 分层边界

| 层 | 关注点 | 主要文档 |
| --- | --- | --- |
| 物理层 / 控制器 | 差分电平、终端、位时序、采样点 | [can.md](can.md) · [../../basic/can-phy.md](../../basic/can-phy.md) · [../../basic/can-practical.md](../../basic/can-practical.md) |
| 数据链路层 | 帧格式、仲裁、错误处理、CAN FD/XL | [can.md](can.md) · [../../basic/can-fd-and-can-xl.md](../../basic/can-fd-and-can-xl.md) · [can-fd-index.md](can-fd-index.md) |
| 传输层 | 多帧分包与流控 | [iso-tp-index.md](iso-tp-index.md) |
| 应用层 | 诊断、设备行规、车载网络 | [uds-index.md](uds-index.md) · [canopen-index.md](canopen-index.md) · [j1939-index.md](j1939-index.md) · [obd2-index.md](obd2-index.md) · [wwh-obd-index.md](wwh-obd-index.md) |
| 低速补充总线 | LIN 主从调度 | [lin.md](lin.md) · [lin-practical.md](lin-practical.md) |

## 文档地图

### 全景与标准

- [can-protocol-family.md](can-protocol-family.md)：CAN 家族全景、协议矩阵、选型决策与覆盖缺口。
- [can-standards-map.md](can-standards-map.md)：按层与按协议汇总 ISO / SAE / CiA 标准号。
- [../../basic/can-index.md](../../basic/can-index.md)：CAN PHY 与控制器层索引。

### 协议族索引

- [can-fd-index.md](can-fd-index.md)：CAN FD / CAN XL。
- [canopen-index.md](canopen-index.md)：CANopen 与功能安全。
- [j1939-index.md](j1939-index.md)：J1939 商用车网络。
- [iso-tp-index.md](iso-tp-index.md)：ISO-TP 多帧传输。
- [uds-index.md](uds-index.md)：UDS 统一诊断服务。
- [obd2-index.md](obd2-index.md)：OBD-II 排放诊断。
- [wwh-obd-index.md](wwh-obd-index.md)：WWH-OBD 全球统一诊断。

### 实战与故障

- [canopen-failure-cases.md](canopen-failure-cases.md)
- [iso-tp-failure-cases.md](iso-tp-failure-cases.md)
- [uds-failure-cases.md](uds-failure-cases.md)
- [obd2-failure-cases.md](obd2-failure-cases.md)
- [wwh-obd-failure-cases.md](wwh-obd-failure-cases.md)
- [can-fd-failure-cases.md](can-fd-failure-cases.md)

## 阅读路径

1. **第一次接触 CAN**：[can.md](can.md) → [can-protocol-family.md](can-protocol-family.md) → [can-standards-map.md](can-standards-map.md)。
2. **做 ECU 诊断**：[iso-tp-index.md](iso-tp-index.md) → [uds-index.md](uds-index.md) → [uds-failure-cases.md](uds-failure-cases.md)。
3. **做车载网关**：[j1939-index.md](j1939-index.md) → [canopen-index.md](canopen-index.md) → [can-protocol-family.md](can-protocol-family.md)。
4. **做售后诊断仪**：[obd2-index.md](obd2-index.md) → [wwh-obd-index.md](wwh-obd-index.md) → [can-standards-map.md](can-standards-map.md)。
