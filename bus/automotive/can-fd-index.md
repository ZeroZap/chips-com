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
| [[basic/can-fd-and-can-xl\|can-fd-and-can-xl]] | CAN FD / CAN XL 帧格式、位时序、速率切换与 PHY 边界 |
| [[basic/can-deep-dive\|can-deep-dive]] | 位时序、采样点与控制器细节 |
| [[bus/automotive/can-fd-failure-cases\|can-fd-failure-cases]] | 产线故障案例与排查路径 |
| [[bus/automotive/can\|can]] | 经典 CAN 基础概念 |
| [[bus/automotive/can-protocol-family\|can-protocol-family]] | CAN 家族全景 |
| [[bus/automotive/can-standards-map\|can-standards-map]] | 标准号与合规边界 |

## 阅读路径

1. **方案选型**：[[bus/automotive/can-protocol-family|can-protocol-family]] → [[basic/can-fd-and-can-xl|can-fd-and-can-xl]] → [[bus/automotive/can-standards-map|can-standards-map]]。
2. **调试位时序**：[[basic/can-deep-dive|can-deep-dive]] → [[bus/automotive/can-fd-failure-cases|can-fd-failure-cases]]。
3. **产线问题定位**：[[bus/automotive/can-fd-failure-cases|can-fd-failure-cases]] → [[bus/automotive/can-protocol-family|can-protocol-family]]。

## 边界提醒

- CAN FD 与经典 CAN 的帧格式、CRC 和位时序不同，混跑前先确认控制器与收发器能力。
- CAN XL 的规范与兼容性以 [[bus/automotive/can-standards-map|can-standards-map]] 列出的标准版本为准。
