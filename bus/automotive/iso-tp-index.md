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
| [[bus/automotive/iso-tp\|iso-tp]] | 帧类型、PCI 字段、SF/FF/CF/FC 与寻址方式 |
| [[bus/automotive/iso-tp-practical\|iso-tp-practical]] | 多帧调试、BS、STmin、流控与 UDS 验证 |
| [[bus/automotive/iso-tp-deep-dive\|iso-tp-deep-dive]] | 序列号、超时、异常流控与实现边界 |
| [[bus/automotive/iso-tp-failure-cases\|iso-tp-failure-cases]] | 7 字节边界、TX/RX ID 方向、BS/STmin、SN 环绕等案例 |

## 阅读路径

1. **实现 ISO-TP 收发**：[[bus/automotive/iso-tp|iso-tp]] → [[bus/automotive/iso-tp-deep-dive|iso-tp-deep-dive]]。
2. **联调 UDS**：[[bus/automotive/iso-tp-practical|iso-tp-practical]] → [[bus/automotive/uds-index|uds-index]]。
3. **抓包排障**：[[bus/automotive/iso-tp-failure-cases|iso-tp-failure-cases]] → [[bus/automotive/iso-tp-practical|iso-tp-practical]]。

## 关键边界

- CAN FD 下 payload 更大，但仍需确认双方对 ISO-TP 扩展与填充策略的支持。
- 流控参数（BS、STmin）必须与接收端能力匹配，否则表现为多帧中途停住或丢帧。

## 相关

- [[bus/automotive/can-index|can-index]] · [[bus/automotive/uds-index|uds-index]] · [[bus/automotive/obd2-index|obd2-index]]
