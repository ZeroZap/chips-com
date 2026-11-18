---
tags:
  - layer/bus
  - type/overview
  - protocol/iso-tp
  - topic/automotive
---

# ISO-TP

## 定位

ISO-TP 是 ISO 15765-2，常用于在 CAN 上传输超过单帧长度的数据。

UDS over CAN 通常使用 ISO-TP。

## 为什么需要 ISO-TP

经典 CAN 单帧最多 8 字节。

诊断、刷写、读取长数据时需要分包。

ISO-TP 定义了：

- 单帧。
- 首帧。
- 连续帧。
- 流控帧。

## 帧类型

```text
SF：Single Frame
FF：First Frame
CF：Consecutive Frame
FC：Flow Control
```

发送长数据时：

```text
发送 FF
等待 FC
按 BS/STmin 发送 CF
```

## 关键参数

- Block Size。
- STmin。
- 超时。
- 寻址方式。
- 标准帧或扩展帧。

## 常见错误

| 现象 | 优先检查 |
| --- | --- |
| 多帧中断 | Flow Control、超时、Block Size |
| 数据错位 | Sequence Number、长度、缓冲区 |
| UDS 无响应 | CAN ID、寻址方式、会话状态 |

## 相关规范

| 标准 | 作用 |
| --- | --- |
| **ISO 15765-2** | 核心标准。传输协议与网络层服务：SF/FF/CF/FC、Block Size、STmin、寻址方式 |
| ISO 15765-1 | DoCAN 一般信息与用例定义（体系总览） |
| ISO 15765-3 | DoCAN 网络层服务（网络管理） |
| ISO 15765-4 | DoCAN 网络集成与路由（网关、多 ECU） |
| ISO 11898-1 | 下层 CAN 数据链路 |
| ISO 11898-2 | 下层 CAN 物理层 |

**承载关系**：

```text
ISO-TP (ISO 15765-2)
├── UDS        (ISO 14229-3)      汽车诊断 / 刷写
├── OBD-II     (SAE J1979)        乘用车排放
├── WWH-OBD    (ISO 27145-3)      商用车排放
└── KWP2000    (历史标准, 同源)
```

**注意**：ISO 15765-2 明确适用于法规 OBD 用途，但**不允许用 CAN FD**。CAN FD 场景要用 ISO-TP 的 CAN FD 变体（CAN FD escape sequence），这是 SAE J1939-22 和 CiA 1301 各自定义的方式。

## 延伸阅读

- [[bus/automotive/uds|uds]]
- [[bus/automotive/can|can]]
- [[bus/automotive/canopen-deep-dive|canopen-deep-dive]]
- [[bus/automotive/iso-tp-deep-dive|iso-tp-deep-dive]]
- [[bus/automotive/iso-tp-practical|iso-tp-practical]]
- [[bus/automotive/iso-tp-failure-cases|iso-tp-failure-cases]]
- [[bus/automotive/can-standards-map|can-standards-map]] — CAN 家族标准规范总表
