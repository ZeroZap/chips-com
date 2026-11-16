---
tags:
  - layer/bus
  - type/index
---
# WWH-OBD 主题导航

## 定位

WWH-OBD（World-Wide Harmonized OBD，ISO 27145 系列）面向商用车，把法规诊断映射到 UDS 服务与 24 位 DTC，并支持 DoCAN 与 DoIP 两种链路。

## 文档地图

| 文档 | 作用 |
| --- | --- |
| [wwh-obd.md](wwh-obd.md) | 各部分分工、DoCAN + DoIP 双链路、PID/MID/ITID 映射 |
| [wwh-obd-practical.md](wwh-obd-practical.md) | 双链路选型、初始化序列、11/29 位验证、DoIP 路由与 DTC 解析 |
| [wwh-obd-deep-dive.md](wwh-obd-deep-dive.md) | 各部分边界、DID/RID 映射、24 位 DTC 与 SPN/FMI 对齐 |
| [wwh-obd-failure-cases.md](wwh-obd-failure-cases.md) | DoIP 链路识别、长寻址、DTC 格式、路由激活、P2 超时等案例 |

## 阅读路径

1. **理解法规链路**：[wwh-obd.md](wwh-obd.md) → [wwh-obd-deep-dive.md](wwh-obd-deep-dive.md)。
2. **上真车联调**：[wwh-obd-practical.md](wwh-obd-practical.md) → [wwh-obd-failure-cases.md](wwh-obd-failure-cases.md)。
3. **与乘用车 OBD 对照**：[obd2-index.md](obd2-index.md) → [wwh-obd.md](wwh-obd.md)。

## 相关

- 服务层：[uds-index.md](uds-index.md)
- 传输层：[iso-tp-index.md](iso-tp-index.md)
- DoIP / 车载以太网：见 `../industrial/README.md` 中的以太网与网关资料
- CAN 家族总览：[can-index.md](can-index.md)
