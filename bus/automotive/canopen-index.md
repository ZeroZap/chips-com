---
tags:
  - layer/bus
  - type/index
---
# CANopen 主题导航

## 定位

CANopen 是建立在 CAN 之上的应用层协议，核心对象是对象字典、SDO、PDO、NMT 与心跳/节点保护。功能安全场景使用 CANopen Safety（CiA 304 / EN 50325-5）。

## 文档地图

| 文档 | 作用 |
| --- | --- |
| [[bus/automotive/canopen\|canopen]] | 对象字典、SDO/PDO、NMT、COB-ID 与典型应用 |
| [[bus/automotive/canopen-practical\|canopen-practical]] | 物理层、COB-ID、SDO/PDO、NMT 与电机调试流程 |
| [[bus/automotive/canopen-deep-dive\|canopen-deep-dive]] | 位时序、SDO 命令字、PDO 映射、NMT 状态机与 CiA 402 |
| [[bus/automotive/canopen-failure-cases\|canopen-failure-cases]] | 产线案例：Node ID 冲突、字节序、PDO 映射、心跳过滤 |
| [[bus/automotive/canopen-safety\|canopen-safety]] | SRDO、SCT/SRVT、CRC 配置签名与全局失效安全命令 |

## 阅读路径

1. **入门**：[[bus/automotive/canopen|canopen]] → [[bus/automotive/canopen-practical|canopen-practical]]。
2. **协议实现**：[[bus/automotive/canopen-deep-dive|canopen-deep-dive]] → [[bus/automotive/canopen|canopen]]。
3. **现场排障**：[[bus/automotive/canopen-failure-cases|canopen-failure-cases]] → [[bus/automotive/canopen-practical|canopen-practical]]。
4. **功能安全**：[[bus/automotive/canopen-safety|canopen-safety]] → [[bus/industrial/README|README]]。

## 相关

- CAN 基础：[[bus/automotive/can|can]] · [[basic/can-index|can-index]]
- 家族总览：[[bus/automotive/can-index|can-index]]
- 标准号：[[bus/automotive/can-standards-map|can-standards-map]]
