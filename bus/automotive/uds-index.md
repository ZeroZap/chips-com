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
| [[bus/automotive/uds\|uds]] | 服务分类、会话、安全访问、DID、DTC 与 NRC |
| [[bus/automotive/uds-practical\|uds-practical]] | 请求/响应、常见服务、刷写流程与工具链 |
| [[bus/automotive/uds-deep-dive\|uds-deep-dive]] | 状态机、NRC、S3 会话保持、刷写事务与网关边界 |
| [[bus/automotive/uds-failure-cases\|uds-failure-cases]] | 会话服务表、DID 落盘、种子密钥、刷写变砖、BSC 循环 |

## 阅读路径

1. **做诊断功能**：[[bus/automotive/uds|uds]] → [[bus/automotive/uds-practical|uds-practical]]。
2. **做刷写 / Bootloader**：[[bus/automotive/uds-deep-dive|uds-deep-dive]] → [[bus/automotive/uds-practical|uds-practical]] → [[bus/automotive/uds-failure-cases|uds-failure-cases]]。
3. **现场排障**：[[bus/automotive/uds-failure-cases|uds-failure-cases]] → [[bus/automotive/iso-tp-failure-cases|iso-tp-failure-cases]]。
4. **乘用车 / 商用车法规诊断**：[[bus/automotive/obd2-index|obd2-index]] · [[bus/automotive/wwh-obd-index|wwh-obd-index]]。

## 相关

- 传输层：[[bus/automotive/iso-tp-index|iso-tp-index]]
- CAN 家族总览：[[bus/automotive/can-index|can-index]]
- 标准号：[[bus/automotive/can-standards-map|can-standards-map]]
