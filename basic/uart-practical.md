# UART Practical Guide

## 目标

本文用于把 UART 从概念落到工程实践：如何接线、配置参数、收发数据、定位乱码、区分 TTL/RS232/RS485。

## 最小接线

```text
Device A TX -> Device B RX
Device A RX <- Device B TX
Device A GND -- Device B GND
```

要点：

- `TX` 接对方 `RX`，`RX` 接对方 `TX`。
- TTL UART 必须共地。
- 3.3V 和 5V UART 混接时要确认输入耐压。
- MCU UART 不能直接接 RS232 或 RS485 A/B。

## 常用参数

UART 双方必须配置一致：

```text
baud rate：9600 / 115200 / 1000000
data bits：8
parity：None / Even / Odd
stop bits：1 / 2
flow control：None / RTS/CTS
```

最常见配置：

```text
115200 8N1
```

含义：

```text
115200 baud, 8 data bits, no parity, 1 stop bit
```

## 调试步骤

1. 先用 USB-TTL 工具连接目标板 UART。
2. 确认 GND 共地。
3. 串口工具设置 `115200 8N1` 或设备手册指定参数。
4. 如果无输出，交换 TX/RX。
5. 如果乱码，优先检查波特率和晶振频率。
6. 如果偶发丢字节，检查中断、DMA、FIFO 和接收缓冲区。
7. 如果长线不稳定，改用 RS485/CAN/Ethernet。

## 收发模型

UART 是字节流，不天然保留消息边界。

应用协议应自行定义：

- 固定长度帧。
- 起始符 + 长度 + 数据 + 校验。
- 文本行协议，以 `\r\n` 结尾。
- 超时分帧。

推荐二进制帧：

```text
SOF | LEN | CMD | PAYLOAD | CRC
```

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| 完全没数据 | TX/RX、GND、电源、串口号 |
| 乱码 | 波特率、校验位、晶振误差、电平 |
| 只能收不能发 | TX 接线、方向控制、引脚复用 |
| 偶发丢包 | 缓冲区、DMA、中断优先级、流控 |
| 接上就复位 | 电平冲突、供电、ESD、接错引脚 |

## TTL、RS232、RS485 区分

```text
TTL UART：MCU 引脚电平，0/3.3V 或 0/5V
RS232：正负电压，需要 MAX232/SP3232 等转换芯片
RS485：差分 A/B，需要 RS485 收发器和方向控制
```

不要把这三者都叫“串口”后直接互接。

## 实战检查清单

- 设备手册中的 UART 参数已确认。
- TX/RX 方向已确认。
- GND 已连接。
- 电平兼容或已加电平转换。
- 引脚复用配置正确。
- 接收缓冲区足够。
- 协议有帧边界和校验。
- 长距离通信已改用合适物理层。
