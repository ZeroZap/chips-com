# DMX512 Practical Guide

## 目标

本文用于 DMX512 灯光控制调试，重点覆盖 Break、Start Code、通道数据、灯具地址、刷新率、终端和常见闪烁问题。

## 典型连接

```text
Controller -> DMX Transceiver -> DMX+ / DMX- -> Fixtures
```

DMX512 常使用类似 RS485 的差分物理层。

## 帧结构

```text
Break
Mark After Break
Start Code
Channel 1
Channel 2
...
Channel 512
```

`Start Code` 通常为 `0x00` 表示普通调光数据。

## 通道和地址

灯具设置起始地址。

例如某 RGB 灯占 3 通道，起始地址为 10：

```text
Channel 10：R
Channel 11：G
Channel 12：B
```

地址错会导致灯具响应错误通道。

## 调试步骤

1. 确认差分线和方向。
2. 用示波器确认 Break。
3. 确认 Start Code。
4. 发送少量通道数据。
5. 设置灯具起始地址。
6. 逐通道改变数值观察灯具响应。
7. 增加灯具数量并检查终端。

## 常见故障

| 现象 | 优先检查 |
| --- | --- |
| 灯完全不动 | 接线、收发器、Break、地址 |
| 颜色错 | 通道顺序、灯具模式、地址 |
| 闪烁 | 线缆、终端、刷新率、干扰 |
| 多灯异常 | 终端、电缆、地址重叠 |

## 检查清单

- Break 时序正确。
- Start Code 正确。
- 灯具起始地址正确。
- 通道数和灯具模式匹配。
- 长线末端有终端。
