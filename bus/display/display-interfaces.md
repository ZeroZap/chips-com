# Display Interfaces Overview

## 目标

本文概览常见显示接口，帮助在 SPI、RGB、LVDS、MIPI DSI、eDP、HDMI 之间建立选型直觉。

## 小屏低成本

常见：

```text
SPI
8080/6800 并口
```

适合：

- 小尺寸 LCD/OLED。
- 低刷新率。
- MCU 项目。

## RGB 并口

特点：

- 数据线多。
- 时序直观。
- 常见于中低分辨率 TFT。

信号：

```text
RGB data
PCLK
HSYNC
VSYNC
DE
```

## LVDS

特点：

- 差分传输。
- 工业屏常见。
- 比 RGB 并口线数少。

适合：

- 工业显示屏。
- 中等分辨率。
- 板间屏线连接。

## MIPI DSI

特点：

- 高速差分 Lane。
- 移动屏常见。
- 需要初始化命令。
- 支持 Video/Command Mode。

适合：

- 手机/平板类屏。
- 嵌入式高清屏。

## eDP

eDP 是 embedded DisplayPort。

常见于：

- 笔记本屏。
- 高分辨率嵌入式显示。

特点：

- 高速 Lane。
- AUX 通道。
- 链路训练。
- 可支持较高分辨率。

## HDMI

HDMI 常用于外部显示连接。

特点：

- 标准显示接口。
- 线缆外接。
- 涉及 EDID、HDCP、TMDS/FRL 等。

适合：

- 外接显示器。
- 消费电子。
- 开发板显示输出。

## 选型直觉

| 场景 | 优先接口 |
| --- | --- |
| MCU 小屏 | SPI |
| 简单 TFT | RGB 并口 |
| 工业屏 | LVDS |
| 移动高清屏 | MIPI DSI |
| 笔记本/高分屏 | eDP |
| 外接显示器 | HDMI |
