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
| 物理层 / 控制器 | 差分电平、终端、位时序、采样点 | [[bus/automotive/can\|can]] · [[basic/can-phy\|can-phy]] · [[basic/can-practical\|can-practical]] |
| 数据链路层 | 帧格式、仲裁、错误处理、CAN FD/XL | [[bus/automotive/can\|can]] · [[basic/can-fd-and-can-xl\|can-fd-and-can-xl]] · [[bus/automotive/can-fd-index\|can-fd-index]] |
| 传输层 | 多帧分包与流控 | [[bus/automotive/iso-tp-index\|iso-tp-index]] |
| 应用层 | 诊断、设备行规、车载网络 | [[bus/automotive/uds-index\|uds-index]] · [[bus/automotive/canopen-index\|canopen-index]] · [[bus/automotive/j1939-index\|j1939-index]] · [[bus/automotive/obd2-index\|obd2-index]] · [[bus/automotive/wwh-obd-index\|wwh-obd-index]] |
| 低速补充总线 | LIN 主从调度 | [[bus/automotive/lin\|lin]] · [[bus/automotive/lin-practical\|lin-practical]] |

## 文档地图

### 全景与标准

- [[bus/automotive/can-protocol-family|can-protocol-family]]：CAN 家族全景、协议矩阵、选型决策与覆盖缺口。
- [[bus/automotive/can-standards-map|can-standards-map]]：按层与按协议汇总 ISO / SAE / CiA 标准号。
- [[basic/can-index|can-index]]：CAN PHY 与控制器层索引。

### 协议族索引

- [[bus/automotive/can-fd-index|can-fd-index]]：CAN FD / CAN XL。
- [[bus/automotive/canopen-index|canopen-index]]：CANopen 与功能安全。
- [[bus/automotive/j1939-index|j1939-index]]：J1939 商用车网络。
- [[bus/automotive/iso-tp-index|iso-tp-index]]：ISO-TP 多帧传输。
- [[bus/automotive/uds-index|uds-index]]：UDS 统一诊断服务。
- [[bus/automotive/obd2-index|obd2-index]]：OBD-II 排放诊断。
- [[bus/automotive/wwh-obd-index|wwh-obd-index]]：WWH-OBD 全球统一诊断。

### 实战与故障

- [[bus/automotive/canopen-failure-cases|canopen-failure-cases]]
- [[bus/automotive/iso-tp-failure-cases|iso-tp-failure-cases]]
- [[bus/automotive/uds-failure-cases|uds-failure-cases]]
- [[bus/automotive/obd2-failure-cases|obd2-failure-cases]]
- [[bus/automotive/wwh-obd-failure-cases|wwh-obd-failure-cases]]
- [[bus/automotive/can-fd-failure-cases|can-fd-failure-cases]]

## 阅读路径

1. **第一次接触 CAN**：[[bus/automotive/can|can]] → [[bus/automotive/can-protocol-family|can-protocol-family]] → [[bus/automotive/can-standards-map|can-standards-map]]。
2. **做 ECU 诊断**：[[bus/automotive/iso-tp-index|iso-tp-index]] → [[bus/automotive/uds-index|uds-index]] → [[bus/automotive/uds-failure-cases|uds-failure-cases]]。
3. **做车载网关**：[[bus/automotive/j1939-index|j1939-index]] → [[bus/automotive/canopen-index|canopen-index]] → [[bus/automotive/can-protocol-family|can-protocol-family]]。
4. **做售后诊断仪**：[[bus/automotive/obd2-index|obd2-index]] → [[bus/automotive/wwh-obd-index|wwh-obd-index]] → [[bus/automotive/can-standards-map|can-standards-map]]。
