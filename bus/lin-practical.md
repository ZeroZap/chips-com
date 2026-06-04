# LIN Practical Guide

## 目标

本文用于 LIN 工程入门和调试，重点覆盖 LIN 与 UART 的关系、单线物理层、主从调度、帧结构、Break、Sync、Identifier、Checksum 和车身控制场景。

## LIN 的定位

LIN 是低成本车载局部互联总线。

常见场景：

- 车窗。
- 座椅。
- 后视镜。
- 空调风门。
- 雨刮。
- 门锁。
- 氛围灯。
- 简单传感器。

它通常作为 CAN 的低成本补充。

## LIN 不是普通 UART

LIN 数据格式和 UART 类似，但它是完整车载总线。

需要：

```text
MCU UART/LIN Controller <-> LIN Transceiver <-> LIN Bus
```

不能把 MCU UART TX/RX 直接接 LIN 总线。

## 物理层

LIN 是单线总线。

常见信号：

```text
LIN
VBAT
GND
```

通常需要 LIN 收发器连接到汽车电源环境。

设计要考虑：

- 12V 电源。
- 负载突降。
- ESD。
- EMC。
- 睡眠和唤醒。

## 主从调度

LIN 通常一个 Master，多个 Slave。

Master 负责调度：

```text
按调度表发送 Header
指定哪个帧在什么时候出现
```

Slave 根据 Identifier 判断：

- 是否接收数据。
- 是否需要响应数据。

这种模型简单、低成本，但实时性和灵活性不如 CAN。

## 帧结构

典型 LIN 帧：

```text
Break
Sync
Protected Identifier
Data
Checksum
```

`Break`：

```text
主节点发送的长低电平，用于标识帧开始
```

`Sync`：

```text
通常为 0x55，用于同步波特率
```

`Identifier`：

```text
包含帧 ID 和奇偶校验位
```

## Checksum

LIN 有两类校验：

```text
Classic Checksum
Enhanced Checksum
```

Classic 通常只覆盖 Data。

Enhanced 覆盖 Protected Identifier 和 Data。

使用哪种取决于 LIN 版本和帧定义。

Checksum 配错会导致 Slave 丢帧或报错。

## LDF

LIN Description File 描述网络：

- 节点。
- 帧。
- 信号。
- 调度表。
- 波特率。
- 诊断信息。

工程中应以 LDF 为准生成或配置主从节点通信。

## 调试步骤

1. 确认 LIN 收发器供电。
2. 确认 Master 发送 Break。
3. 确认 Sync 为 0x55。
4. 确认 Identifier 和 parity。
5. 确认 Slave 是否按 ID 响应。
6. 检查 Checksum 类型。
7. 对照 LDF 检查信号编码。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 总线无波形 | 收发器、电源、Master 调度 |
| Slave 不响应 | ID、波特率、Break、Sync、唤醒 |
| Checksum 错 | Classic/Enhanced、数据长度、ID |
| 偶发失败 | EMC、电源、睡眠唤醒、时钟误差 |
| 信号值不对 | LDF、bit offset、scale、endian |

## 实战检查清单

- 使用 LIN 收发器。
- Master 调度表正确。
- Break 长度满足规范。
- Sync 为 0x55。
- Protected Identifier parity 正确。
- Checksum 类型匹配。
- 信号解析按 LDF。
- 车载电源和 EMC 防护已考虑。
