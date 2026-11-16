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
| [canopen.md](canopen.md) | 对象字典、SDO/PDO、NMT、COB-ID 与典型应用 |
| [canopen-practical.md](canopen-practical.md) | 物理层、COB-ID、SDO/PDO、NMT 与电机调试流程 |
| [canopen-deep-dive.md](canopen-deep-dive.md) | 位时序、SDO 命令字、PDO 映射、NMT 状态机与 CiA 402 |
| [canopen-failure-cases.md](canopen-failure-cases.md) | 产线案例：Node ID 冲突、字节序、PDO 映射、心跳过滤 |
| [canopen-safety.md](canopen-safety.md) | SRDO、SCT/SRVT、CRC 配置签名与全局失效安全命令 |

## 阅读路径

1. **入门**：[canopen.md](canopen.md) → [canopen-practical.md](canopen-practical.md)。
2. **协议实现**：[canopen-deep-dive.md](canopen-deep-dive.md) → [canopen.md](canopen.md)。
3. **现场排障**：[canopen-failure-cases.md](canopen-failure-cases.md) → [canopen-practical.md](canopen-practical.md)。
4. **功能安全**：[canopen-safety.md](canopen-safety.md) → [../industrial/README.md](../industrial/README.md)。

## 相关

- CAN 基础：[can.md](can.md) · [../basic/can-index.md](../../basic/can-index.md)
- 家族总览：[can-index.md](can-index.md)
- 标准号：[can-standards-map.md](can-standards-map.md)
