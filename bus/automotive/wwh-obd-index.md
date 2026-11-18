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
| [[bus/automotive/wwh-obd\|wwh-obd]] | 各部分分工、DoCAN + DoIP 双链路、PID/MID/ITID 映射 |
| [[bus/automotive/wwh-obd-practical\|wwh-obd-practical]] | 双链路选型、初始化序列、11/29 位验证、DoIP 路由与 DTC 解析 |
| [[bus/automotive/wwh-obd-deep-dive\|wwh-obd-deep-dive]] | 各部分边界、DID/RID 映射、24 位 DTC 与 SPN/FMI 对齐 |
| [[bus/automotive/wwh-obd-failure-cases\|wwh-obd-failure-cases]] | DoIP 链路识别、长寻址、DTC 格式、路由激活、P2 超时等案例 |

## 阅读路径

1. **理解法规链路**：[[bus/automotive/wwh-obd|wwh-obd]] → [[bus/automotive/wwh-obd-deep-dive|wwh-obd-deep-dive]]。
2. **上真车联调**：[[bus/automotive/wwh-obd-practical|wwh-obd-practical]] → [[bus/automotive/wwh-obd-failure-cases|wwh-obd-failure-cases]]。
3. **与乘用车 OBD 对照**：[[bus/automotive/obd2-index|obd2-index]] → [[bus/automotive/wwh-obd|wwh-obd]]。

## 相关

- 服务层：[[bus/automotive/uds-index|uds-index]]
- 传输层：[[bus/automotive/iso-tp-index|iso-tp-index]]
- DoIP / 车载以太网：见 [[bus/industrial/README|README]] 中的以太网与网关资料
- CAN 家族总览：[[bus/automotive/can-index|can-index]]
