---
tags:
  - layer/bus
  - type/index
---
# OBD-II 主题导航

## 定位

OBD-II 是乘用车排放与车载诊断的法规接口（SAE J1979 / ISO 15031 系列），通过标准 Mode、PID 与 DTC 提供只读诊断能力。它和 OEM 的 UDS 服务集、商用车的 WWH-OBD 属于不同法规体系。

## 文档地图

| 文档 | 作用 |
| --- | --- |
| [[bus/automotive/obd2\|obd2]] | 九个 Mode、PID 速查、DTC 格式与接口概览 |
| [[bus/automotive/obd2-practical\|obd2-practical]] | ELM327 / SocketCAN 工具链、抓包与检查清单 |
| [[bus/automotive/obd2-deep-dive\|obd2-deep-dive]] | PID 支持协商、I/M 就绪、监测模型、与 UDS 的边界 |
| [[bus/automotive/obd2-failure-cases\|obd2-failure-cases]] | 适配器能力、PID 解码、多 ECU 响应源、VIN 多帧等案例 |

## 阅读路径

1. **做读取工具**：[[bus/automotive/obd2|obd2]] → [[bus/automotive/obd2-practical|obd2-practical]]。
2. **做深度诊断**：[[bus/automotive/obd2-deep-dive|obd2-deep-dive]] → [[bus/automotive/obd2-failure-cases|obd2-failure-cases]]。
3. **区分法规体系**：[[bus/automotive/obd2|obd2]] → [[bus/automotive/wwh-obd-index|wwh-obd-index]] → [[bus/automotive/uds-index|uds-index]]。

## 相关

- 传输层：[[bus/automotive/iso-tp-index|iso-tp-index]]
- 整车诊断：[[bus/automotive/uds-index|uds-index]]
- 商用车法规诊断：[[bus/automotive/wwh-obd-index|wwh-obd-index]]
- CAN 家族总览：[[bus/automotive/can-index|can-index]]
