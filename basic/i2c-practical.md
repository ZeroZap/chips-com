# I2C Practical Guide

## 目标

本文用于 I2C 工程调试：接线、上拉、电平、地址扫描、寄存器读写和总线恢复。

## 最小接线

```text
Controller SCL -> Target SCL
Controller SDA -> Target SDA
Controller GND -- Target GND
```

I2C 是开漏总线，`SCL` 和 `SDA` 通常都需要上拉电阻。

```text
VCC
 |
 R
 |
SDA/SCL ---- Controller
        ---- Target A
        ---- Target B
```

## 上拉电阻

常见取值：

```text
10k：低速、短线、设备少
4.7k：常用默认选择
2.2k：较高速或总线电容较大
```

选择依据：

- 速度越高，上拉通常要更强。
- 线越长、设备越多，总线电容越大。
- 电阻太小会增加拉低电流。

## 地址确认

I2C 常见 7-bit 地址，例如：

```text
0x68
```

协议线上会发送：

```text
写：0xD0
读：0xD1
```

因为：

```text
0x68 << 1 = 0xD0
```

调试时要确认手册写的是 7-bit 地址还是 8-bit 地址。

## 典型寄存器写

```text
START
Address + Write
Register Address
Data
STOP
```

抽象 API：

```c
i2c_write_reg(0x68, 0x10, 0x55);
```

## 典型寄存器读

```text
START
Address + Write
Register Address
REPEATED START
Address + Read
Read Data
NACK
STOP
```

很多设备要求 `Repeated START`，不要随意改成 `STOP + START`。

## 调试步骤

1. 确认目标设备供电、电压域和复位脚。
2. 用示波器或逻辑分析仪确认 `SCL/SDA` 空闲为高。
3. 先用 100 kHz 扫描地址。
4. 找到地址后读取固定 ID 寄存器。
5. 再切到 400 kHz 或更高速度。
6. 如果出现 NACK，回到 100 kHz 并检查上拉。
7. 如果 SDA 被拉低，执行总线恢复。

## 总线恢复

当从设备异常导致 `SDA` 被拉低时，可尝试：

```text
把 SCL/SDA 临时配置为 GPIO
发送 9 个 SCL 脉冲
生成 STOP 条件
重新初始化 I2C 控制器
```

如果仍无法恢复，复位或断电目标设备。

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| 扫不到地址 | 电源、复位、上拉、地址、电平 |
| 偶发 NACK | 上拉、电容、线长、速度 |
| 读值全 0xFF | 设备未响应、地址错、SDA 上拉 |
| 读值全 0x00 | SDA 被拉低、寄存器地址错 |
| 高速不稳定 | 上升沿太慢、走线太长 |

## 实战检查清单

- 上拉电阻已安装到正确电压域。
- 设备地址按 7-bit/8-bit 规则确认。
- 读寄存器流程使用 Repeated START。
- 多设备地址无冲突。
- 不同电压域已做 I2C 电平转换。
- 总线恢复机制已实现。
