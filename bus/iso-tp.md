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

## 延伸阅读

- `bus/uds.md`
- `bus/can.md`
- `bus/can-canopen-deep-dive.md`
