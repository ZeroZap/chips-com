---
tags:
  - layer/bus
  - type/index
---
# ISO-TP 主题导航

## 定位

ISO-TP（ISO 15765-2）解决 CAN 帧 8 字节 payload 与上层长报文之间的矛盾，提供单帧、首帧、连续帧与流控帧机制，是 UDS、OBD 等诊断协议的传输层。

## 文档地图

| 文档 | 作用 |
| --- | --- |
| [iso-tp.md](iso-tp.md) | 帧类型、PCI 字段、SF/FF/CF/FC 与寻址方式 |
| [iso-tp-practical.md](iso-tp-practical.md) | 多帧调试、BS、STmin、流控与 UDS 验证 |
| [iso-tp-deep-dive.md](iso-tp-deep-dive.md) | 序列号、超时、异常流控与实现边界 |
| [iso-tp-failure-cases.md](iso-tp-failure-cases.md) | 7 字节边界、TX/RX ID 方向、BS/STmin、SN 环绕等案例 |

## 阅读路径

1. **实现 ISO-TP 收发**：[iso-tp.md](iso-tp.md) → [iso-tp-deep-dive.md](iso-tp-deep-dive.md)。
2. **联调 UDS**：[iso-tp-practical.md](iso-tp-practical.md) → [uds-index.md](uds-index.md)。
3. **抓包排障**：[iso-tp-failure-cases.md](iso-tp-failure-cases.md) → [iso-tp-practical.md](iso-tp-practical.md)。

## 关键边界

- CAN FD 下 payload 更大，但仍需确认双方对 ISO-TP 扩展与填充策略的支持。
- 流控参数（BS、STmin）必须与接收端能力匹配，否则表现为多帧中途停住或丢帧。

## 相关

- [can-index.md](can-index.md) · [uds-index.md](uds-index.md) · [obd2-index.md](obd2-index.md)
