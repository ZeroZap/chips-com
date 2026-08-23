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

## 速查要点

### 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 完全没数据 | TX/RX 接反 / 没共地 | 交换 TX/RX, 查 GND |
| 乱码 | 波特率错 / 晶振不准 | 示波器量 baud, 校准 |
| 只能收不能发 | 方向控制 / 模式错 | 查 RS485 收发器 DIR |
| 偶发丢字节 | 缓冲区溢出 / 帧边界丢失 | 开 DMA + 环形缓冲 |
| 高速丢包 | FIFO 不够 / 流控未开 | 开硬件流控或降速 |
| 接上就复位 | 电平不兼容 / ESD | 量两端电平, 加 TVS |
| 串口工具能收, MCU 收不到 | 协议帧边界错 | 加 SOF + LEN + CRC |
| 长线通信失败 | 距离 / EMC 超规格 | 改 RS485 / CAN |

### 常用波特率速查

```text
低俗档 (调试):       9600, 19200
中速档 (多数应用):    115200, 230400
高速档 (下载/固件):  460800, 921600, 1500000
超高速 (特殊):       3000000, 6000000
```

### 帧格式速查

```text
8N1:   1 start + 8 data + 0 parity + 1 stop = 10 bit/byte (最常用)
8E1:   1 start + 8 data + even parity + 1 stop = 10 bit/byte
8O1:   1 start + 8 data + odd parity + 1 stop = 10 bit/byte
8N2:   1 start + 8 data + 0 parity + 2 stop = 11 bit/byte
9N1:   1 start + 9 data + 0 parity + 1 stop = 11 bit/byte
```

### 物理层速查

```text
TTL UART:  MCU 引脚, 0/3.3V 或 0/5V, 距离 < 1m
RS232:     +/-12V 差分 (相对 GND), 需要 MAX232, 距离 < 15m
RS485:     差分 A/B, 半双工 (2 线) 或全双工 (4 线), 距离 < 1200m
RS422:     差分, 全双工, 距离 < 1200m
```

### 错误码速查

```text
framing error:    帧错 (停止位没收到, 波特率/噪声)
parity error:     校验位错 (有干扰)
overrun error:    FIFO 溢出 (CPU 来不及读)
break condition:  长时间低电平 (诊断或异常)
noise error:      噪声干扰
```

### DMA 触发

```text
适合 DMA:
  - 数据长度 > 8 字节
  - 高速 (> 115200) 持续传输
  - 大量日志 / 固件下载
  - 接收多帧连续数据

不适合 DMA:
  - 数据长度 < 4 字节
  - 调试 (printf 阻塞场景)
  - 不确定字节数 (变长协议)
```

### 接收缓冲区大小建议

```text
低速 (< 115200):    256 字节
中速 (115200~1M):   1024 字节
高速 (> 1M):        4096 字节 + DMA 双缓冲
超高速 + 固件下载:   8KB+ 字节
```

### 调试时序

```text
短距离 (< 30cm):    TTL 串口, 3.3V/5V, 不需要转换
中距离 (30cm~15m):  RS232 (MAX232 转换)
长距离 (15m~1200m): RS485 (差分, 抗干扰)
超长距离 / 工业现场:  CAN / RS485 + 光耦隔离
```

## 关联文档

- `uart-deep-dive.md` 原理和体系
- `uart-failure-cases.md` 产线死机案例
- `uart-rs485-and-flow-control.md` RS485 / 流控专题
- `uart-dma-circular-and-rtos.md` DMA + 环形缓冲 + RTOS
- `uart-index.md` 导航
- `rs232-rs485.md` 物理层基础
- `modbus.md` Modbus RTU (UART 上层协议)
- `i2c-practical.md` I2C 速查 (对比)
