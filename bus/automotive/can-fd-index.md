---
tags:
  - layer/bus
  - type/index
---
# CAN FD / CAN XL 主题导航

## 定位

CAN FD 在经典 CAN 基础上引入可变数据速率与更大 payload；CAN XL 进一步扩展 payload 与网络能力。本索引把控制器/物理层资料与产线故障案例放在同一入口。

## 文档地图

| 文档 | 作用 |
| --- | --- |
| [../../basic/can-fd-and-can-xl.md](../../basic/can-fd-and-can-xl.md) | CAN FD / CAN XL 帧格式、位时序、速率切换与 PHY 边界 |
| [../../basic/can-deep-dive.md](../../basic/can-deep-dive.md) | 位时序、采样点与控制器细节 |
| [can-fd-failure-cases.md](can-fd-failure-cases.md) | 产线故障案例与排查路径 |
| [can.md](can.md) | 经典 CAN 基础概念 |
| [can-protocol-family.md](can-protocol-family.md) | CAN 家族全景 |
| [can-standards-map.md](can-standards-map.md) | 标准号与合规边界 |

## 阅读路径

1. **方案选型**：[can-protocol-family.md](can-protocol-family.md) → [../../basic/can-fd-and-can-xl.md](../../basic/can-fd-and-can-xl.md) → [can-standards-map.md](can-standards-map.md)。
2. **调试位时序**：[../../basic/can-deep-dive.md](../../basic/can-deep-dive.md) → [can-fd-failure-cases.md](can-fd-failure-cases.md)。
3. **产线问题定位**：[can-fd-failure-cases.md](can-fd-failure-cases.md) → [can-protocol-family.md](can-protocol-family.md)。

## 边界提醒

- CAN FD 与经典 CAN 的帧格式、CRC 和位时序不同，混跑前先确认控制器与收发器能力。
- CAN XL 的规范与兼容性以 [can-standards-map.md](can-standards-map.md) 列出的标准版本为准。
