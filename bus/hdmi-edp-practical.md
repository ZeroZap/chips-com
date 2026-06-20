# HDMI / eDP Practical Guide

## 目标

本文用于 HDMI/eDP 显示链路调试，重点覆盖 EDID、HPD、DDC、AUX、Link Training、Panel 电源时序、背光和常见无显示问题。

## HDMI 调试顺序

1. 确认 5V 输出。
2. 确认 HPD 状态。
3. 通过 DDC 读取 EDID。
4. 选择显示模式。
5. 输出 TMDS 信号。
6. 检查显示器是否锁定信号。

如果 EDID 读不到，优先检查 DDC I2C 和 HPD。

## eDP 调试顺序

1. 打开 Panel 电源。
2. 等待电源稳定。
3. 释放 Panel reset。
4. 通过 AUX 读取 DPCD/EDID。
5. 执行 Link Training。
6. 输出视频流。
7. 打开背光。

## HDMI 关键点

- HPD 表示显示器连接状态。
- DDC 是 I2C，用于读取 EDID。
- 分辨率和刷新率由 EDID 决定。
- 线缆质量影响高分辨率稳定性。

## eDP 关键点

- AUX 通道用于配置和状态读取。
- Link Training 决定 Lane 数和速率。
- Panel 电源时序和背光时序重要。
- 高分屏对信号质量要求高。

## 常见故障

| 现象 | 优先检查 |
| --- | --- |
| HDMI 无显示 | 5V、HPD、EDID、分辨率 |
| HDMI 闪屏 | 线缆、信号质量、分辨率过高 |
| eDP 黑屏 | Panel 电源、AUX、Link Training、背光 |
| 背光亮无图 | 视频流、时序、Link 状态 |

## 检查清单

- HDMI HPD 和 EDID 正常。
- eDP AUX 可通信。
- Link Training 成功。
- 显示模式与屏幕支持匹配。
- 背光和视频链路分开排查。
