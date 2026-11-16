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
| [obd2.md](obd2.md) | 九个 Mode、PID 速查、DTC 格式与接口概览 |
| [obd2-practical.md](obd2-practical.md) | ELM327 / SocketCAN 工具链、抓包与检查清单 |
| [obd2-deep-dive.md](obd2-deep-dive.md) | PID 支持协商、I/M 就绪、监测模型、与 UDS 的边界 |
| [obd2-failure-cases.md](obd2-failure-cases.md) | 适配器能力、PID 解码、多 ECU 响应源、VIN 多帧等案例 |

## 阅读路径

1. **做读取工具**：[obd2.md](obd2.md) → [obd2-practical.md](obd2-practical.md)。
2. **做深度诊断**：[obd2-deep-dive.md](obd2-deep-dive.md) → [obd2-failure-cases.md](obd2-failure-cases.md)。
3. **区分法规体系**：[obd2.md](obd2.md) → [wwh-obd-index.md](wwh-obd-index.md) → [uds-index.md](uds-index.md)。

## 相关

- 传输层：[iso-tp-index.md](iso-tp-index.md)
- 整车诊断：[uds-index.md](uds-index.md)
- 商用车法规诊断：[wwh-obd-index.md](wwh-obd-index.md)
- CAN 家族总览：[can-index.md](can-index.md)
