---
tags:
  - layer/bus
  - type/index
---
# UDS 主题导航

## 定位

UDS（ISO 14229）是整车与 ECU 诊断的统一服务层，覆盖会话控制、安全访问、DID 读写、例程控制、DTC 与刷写。它依赖 ISO-TP（CAN/DoCAN）或 DoIP 承载。

## 文档地图

| 文档 | 作用 |
| --- | --- |
| [uds.md](uds.md) | 服务分类、会话、安全访问、DID、DTC 与 NRC |
| [uds-practical.md](uds-practical.md) | 请求/响应、常见服务、刷写流程与工具链 |
| [uds-deep-dive.md](uds-deep-dive.md) | 状态机、NRC、S3 会话保持、刷写事务与网关边界 |
| [uds-failure-cases.md](uds-failure-cases.md) | 会话服务表、DID 落盘、种子密钥、刷写变砖、BSC 循环 |

## 阅读路径

1. **做诊断功能**：[uds.md](uds.md) → [uds-practical.md](uds-practical.md)。
2. **做刷写 / Bootloader**：[uds-deep-dive.md](uds-deep-dive.md) → [uds-practical.md](uds-practical.md) → [uds-failure-cases.md](uds-failure-cases.md)。
3. **现场排障**：[uds-failure-cases.md](uds-failure-cases.md) → [iso-tp-failure-cases.md](iso-tp-failure-cases.md)。
4. **乘用车 / 商用车法规诊断**：[obd2-index.md](obd2-index.md) · [wwh-obd-index.md](wwh-obd-index.md)。

## 相关

- 传输层：[iso-tp-index.md](iso-tp-index.md)
- CAN 家族总览：[can-index.md](can-index.md)
- 标准号：[can-standards-map.md](can-standards-map.md)
