---
tags:
  - layer/basic
  - type/overview
  - protocol/lvds
---

# LVDS

## 定位

LVDS（Low-Voltage Differential Signaling，低压差分信号）是一种低摆幅差分信号方式，广泛用于：

- 显示屏接口（工业屏、车载屏）。
- 板间高速连接。
- ADC/DAC 数据输出。
- FPGA/SoC 间连接。
- 摄像头/图像链路（部分场景）。
- 需要低 EMI、较高速度、较短距离的差分传输。

LVDS 本身是物理层信号方式，不定义完整协议。显示 LVDS 只是 LVDS 的一种典型应用。

## 电气特点

| 项目     | 典型值/关注点                   |
| -------- | ------------------------------- |
| 差分摆幅 | 约 250~450 mV                   |
| 共模电压 | 约 1.0~1.4 V（具体按标准/器件） |
| 差分阻抗 | 约 100 Ω                        |
| 终端     | 接收端通常 100 Ω                |
| 信号方式 | 电流驱动/差分                   |
| 距离     | 板内到数米，取决于速率和线缆    |
| EMI      | 低摆幅、差分，辐射较低          |

LVDS 的“低摆幅”带来低功耗和低 EMI，但也意味着：

- 接收器需要合适的共模和终端。
- 噪声余量比 RS485 小。
- PCB 阻抗和端接非常重要。
- 长线/劣质线缆容易导致误码。

## 显示 LVDS

很多工业屏使用 LVDS 接口。常见结构：

```text
SoC/桥片 LVDS TX <-> 屏线 <-> LVDS RX（屏内）
```

信号包括：

```text
Clock Pair
Data Pair 0
Data Pair 1
Data Pair 2
Data Pair 3（可选）
Data Pair 4（可选）
```

常见通道：

| 类型          | 数据对       | 典型位宽    | 说明            |
| ------------- | ------------ | ----------- | --------------- |
| 单通道 18-bit | 3 对 + 时钟  | 6 bit/颜色  | 低成本屏        |
| 单通道 24-bit | 4 对 + 时钟  | 8 bit/颜色  | 常见            |
| 双通道 24-bit | 8 对 + 时钟  | 8 bit/颜色  | 高分辨率/高刷新 |
| 双通道 30-bit | 10 对 + 时钟 | 10 bit/颜色 | 高色深          |

具体 Lane 数、位宽和映射以屏/桥片手册为准。

## VESA / JEIDA 映射

同样 24-bit LVDS，常见两种数据映射：

```text
VESA
JEIDA
```

两者对颜色位到 Lane 的排列不同。映射不匹配会出现：

- 偏色。
- 颜色通道错位。
- 灰阶异常。
- 图像花屏但时序看似正常。

排查时先确认：

- 屏手册要求 VESA 还是 JEIDA。
- SoC/桥片输出配置。
- 屏线是否交叉/转接。
- 是否使用了双通道且通道顺序错误。

## 时序与像素格式

显示 LVDS 需要匹配：

```text
Pixel Clock
Hsync / Vsync / DE
Horizontal/Vertical front porch/back porch
Active width/height
Pixel format：RGB565/RGB666/RGB888
Color depth：18/24/30 bit
Refresh rate
```

常见问题：

- 分辨率/时序不匹配导致黑屏或滚动。
- Pixel Clock 偏差导致画面抖动/撕裂。
- RGB 顺序错误导致偏色。
- 18/24 bit 配置不匹配导致颜色压缩或错位。
- 双通道 Lane 顺序错误导致半屏/花屏。

## 扩频与 EMI

LVDS 常使用扩频（Spread Spectrum）降低 EMI：

- 对像素时钟进行小幅频率调制。
- 降低窄带辐射峰值。
- 可能影响接收端 PLL 锁定和时序余量。

开启扩频后要验证：

- 屏是否稳定锁定。
- 长时间运行是否闪屏。
- 不同温度/批次是否一致。
- EMC 测试是否真正改善。

## PCB 与线缆

设计要点：

- 差分阻抗约 100 Ω。
- 差分对内长度匹配。
- 差分对间 skew 满足时序要求。
- 时钟对优先布线，远离噪声源。
- 减少过孔、分支和跨分割。
- 终端电阻靠近接收端。
- 屏线连接器定义和屏蔽可靠。
- 长线/转接板要重新评估眼图。

## 常见故障树

```text
屏幕无图
├── 屏电源/背光
├── Pixel Clock 缺失
├── LVDS 时钟对/数据对
├── 屏初始化/使能
├── 时序/分辨率不匹配
└── 屏线接触/断线

花屏
├── Lane 顺序错误
├── VESA/JEIDA 映射错误
├── 双通道顺序错误
├── 时序/Pixel Clock 偏差
├── 线缆/连接器质量
└── 信号完整性

偏色
├── RGB 映射错误
├── 位宽/颜色深度不匹配
├── VESA/JEIDA 配置
└── 屏参数错误

闪烁/抖动
├── 时钟质量/扩频
├── 电源纹波
├── 地回流/EMI
├── 线缆/连接器
└── 温度/批次差异
```

| 现象            | 优先检查                          |
| --------------- | --------------------------------- |
| 屏幕无图        | 电源、背光、时钟对、数据对、时序  |
| 花屏            | Lane 顺序、映射、像素格式、线缆   |
| 偏色            | bit mapping、RGB 顺序、VESA/JEIDA |
| 闪烁            | 时钟质量、电源、接地、EMI         |
| 半屏/分区异常   | 双通道 Lane 顺序、通道使能        |
| 高温/长时间异常 | 时序余量、扩频、电源、连接器      |

## 测量方法

- 示波器/差分探头看 LVDS 差分摆幅、共模和眼图。
- 测量 Pixel Clock 频率和抖动。
- 逻辑分析仪/协议分析仪解码 Lane 数据（如支持）。
- 用测试图案检查颜色、灰阶、边界和闪烁。
- 高低温、长线、不同屏批次做余量测试。

## 设计检查清单

- 屏型号、分辨率、位宽、通道数确认。
- VESA/JEIDA 映射配置正确。
- Pixel Clock 和时序参数匹配。
- 差分阻抗、对内/对间长度匹配满足要求。
- 终端电阻和共模设计正确。
- 屏线连接器定义、屏蔽和固定可靠。
- 扩频设置经过稳定性验证。
- 电源/背光/复位时序满足屏手册。
- 测试图案和 EMC 预测试完成。
- 量产测试覆盖纯色、灰阶、闪烁和长时间运行。

## 最小实验

1. 输出纯色/灰阶测试图案，检查颜色和边界。
2. 切换 VESA/JEIDA，观察偏色和映射变化。
3. 用示波器测量 Pixel Clock 和一对数据的眼图。
4. 更换不同长度/质量的屏线，记录花屏边界。
5. 开启/关闭扩频，比较 EMI 和稳定性。

## 关联文档

- [../bus/display/display-interfaces.md](../bus/display/display-interfaces.md)：显示接口概览。
- [../bus/display/mipi-csi-dsi-deep-dive.md](../bus/display/mipi-csi-dsi-deep-dive.md)：MIPI DSI 对比。
- [../bus/display/fpd-link-gmsl-deep-dive.md](../bus/display/fpd-link-gmsl-deep-dive.md)：远端显示链路。
- [../guides/troubleshooting/MEASUREMENT_EXAMPLES.md](../guides/troubleshooting/MEASUREMENT_EXAMPLES.md)：显示测量样例。
