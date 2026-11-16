# 1-Wire Practical Guide

## 目标

本文用于 1-Wire 工程调试，重点覆盖单线开漏、上拉、时序、ROM ID、DS18B20、寄生供电、多设备搜索和常见故障定位。

## 1-Wire 的定位

1-Wire 是极简低速总线。

典型用途：

- DS18B20 温度传感器。
- 唯一 ID 芯片。
- 小容量 EEPROM。
- 设备身份识别。
- 电池包识别。

它适合低速、低成本、少线场景，不适合高速数据通信。

## 接线

常见三线接法：

```text
VDD
DQ
GND
```

DQ 需要上拉：

```text
VDD
 |
 R 4.7k 常见
 |
DQ ---- MCU GPIO
   ---- 1-Wire Device
```

寄生供电只用：

```text
DQ
GND
```

但工程稳定性通常不如三线供电。

## GPIO 配置

1-Wire 通常使用开漏或模拟开漏：

```text
输出 0：拉低 DQ
输出 1：释放 DQ，靠上拉变高
```

如果 MCU 没有开漏输出，可通过切换方向实现：

```text
拉低：GPIO output low
释放：GPIO input
```

## 时序

1-Wire 依赖严格时序。

主机通过拉低和释放 DQ 的时间表示：

- Reset。
- Presence。
- Write 0。
- Write 1。
- Read bit。

软件 bit-bang 时要注意：

- 关闭或控制中断影响。
- 延时函数精度。
- 编译优化。
- RTOS 调度。
- GPIO 翻转速度。

## ROM ID

每个 1-Wire 设备通常有 64-bit ROM ID。

组成：

```text
Family Code
Serial Number
CRC
```

常用命令：

```text
Read ROM：单设备读取 ROM
Match ROM：选择指定设备
Skip ROM：跳过选择，适合单设备
Search ROM：搜索总线所有设备
```

多设备总线必须使用 Search ROM 或已知 ROM ID 管理。

## DS18B20 流程

单设备读取温度典型流程：

```text
Reset
Presence
Skip ROM
Convert T
等待转换完成
Reset
Presence
Skip ROM
Read Scratchpad
校验 CRC
换算温度
```

多设备时用：

```text
Match ROM
```

选择具体传感器。

## 寄生供电注意

寄生供电优点：

```text
少一根电源线
```

缺点：

- 转换期间电流不足。
- 长线更不稳定。
- 多设备更复杂。
- 可能需要 strong pull-up。

如果条件允许，优先三线供电。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 无 Presence | 接线、上拉、GPIO 方向、供电 |
| 温度固定 85°C | 转换未完成或上电默认值 |
| CRC 错 | 时序、中断、线长、上拉 |
| 多设备丢失 | Search ROM、线缆、电源、寄生供电 |
| 长线不稳定 | 降速、加强上拉、三线供电、屏蔽线 |

## 实战检查清单

- DQ 有合适上拉。
- GPIO 释放时确实为高阻或开漏释放。
- Reset 和 Presence 时序正确。
- 单设备先用 Skip ROM 跑通。
- 多设备使用 Search/Match ROM。
- Scratchpad CRC 已校验。
- DS18B20 转换时间已等待。
- 寄生供电场景有 strong pull-up 或改三线供电。
