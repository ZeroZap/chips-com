# LVDS

## 定位

LVDS 是 Low Voltage Differential Signaling，低压差分信号。

它是一种物理层信号方式，常用于：

- 显示屏接口。
- 板间高速连接。
- ADC 数据输出。
- FPGA/SoC 间连接。

## 特点

- 差分传输。
- 电压摆幅小。
- EMI 较低。
- 速度较高。
- 适合短到中距离板间连接。

## 显示 LVDS

很多工业屏使用 LVDS。

常见包括：

```text
Clock Pair
Data Pair 0
Data Pair 1
Data Pair 2
Data Pair 3，可选
```

显示屏还需要：

- 电源。
- 背光。
- EDID 或配置引脚，视屏幕而定。

## 硬件注意

- 差分阻抗。
- P/N 极性。
- Pair 内长度匹配。
- Pair 间时序关系。
- 连接器定义。
- 终端匹配。
- 屏线质量。

## 常见错误

| 现象 | 优先检查 |
| --- | --- |
| 屏幕无图 | 电源、背光、时钟对、数据对 |
| 花屏 | Lane 顺序、像素格式、时序、线缆 |
| 偏色 | bit mapping、RGB 顺序 |
| 闪烁 | 时钟质量、线缆、接地、EMI |

## 与 MIPI DSI 对比

LVDS 在工业屏中常见，接口相对传统。

MIPI DSI 在移动和嵌入式高清屏中常见，协议更复杂，引脚更少。
