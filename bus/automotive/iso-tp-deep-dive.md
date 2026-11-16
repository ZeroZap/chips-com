# ISO-TP Deep Dive

## 目标

本文深入 ISO-TP 多帧传输机制，重点覆盖寻址方式、PCI 编码、流控参数、超时、缓冲区、UDS 集成和刷写场景。

## 寻址方式

常见：

```text
Normal Addressing
Extended Addressing
Mixed Addressing
```

工程中必须确认诊断规范要求的寻址方式，否则 CAN ID 正确也可能无响应。

## PCI 编码

ISO-TP 在数据首字节或前几个字节中编码传输控制信息。

常见：

- Single Frame：携带短数据长度。
- First Frame：携带总长度高低位。
- Consecutive Frame：携带序号。
- Flow Control：携带流控状态、BS、STmin。

## 超时

需要处理：

- 等待 Flow Control 超时。
- 等待 Consecutive Frame 超时。
- 发送间隔超时。
- UDS P2/P2* 应用层超时。

ISO-TP 超时和 UDS 超时要区分。

## 缓冲区

多帧接收需要预分配或动态管理缓冲区。

注意：

- First Frame 声明长度不能超过最大缓冲。
- Consecutive Frame 序号要连续。
- 接收完成后再交给 UDS 层。
- 异常中断时释放状态。

## 刷写场景

UDS 刷写常用 ISO-TP 传输大块数据。

要关注：

- Block Size。
- STmin。
- Flash 写入速度。
- Tester Present。
- Transfer Data 序号。
- 断电恢复。

## 常见问题

| 现象 | 根因方向 |
| --- | --- |
| FF 后无 CF | Flow Control 未发或 ID 错 |
| CF 中断 | STmin/BS/超时/缓冲区 |
| 数据重组错 | SN 丢失、长度计算错 |
| 刷写失败 | UDS 状态、Flash 写入、传输块序号 |

## 检查清单

- 寻址方式明确。
- 请求/响应 CAN ID 正确。
- PCI 类型解析正确。
- Flow Control 参数生效。
- 超时分层处理。
- 缓冲区大小足够。
- UDS 层和 ISO-TP 层错误可区分。
