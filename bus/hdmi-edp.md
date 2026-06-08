# HDMI / eDP

## 定位

HDMI 和 eDP 都是常见显示链路。

```text
HDMI：外接显示器、电视、采集设备
eDP：嵌入式 DisplayPort，常见于笔记本和高分屏
```

## HDMI

HDMI 常用于外部显示连接。

涉及：

- 视频数据。
- 音频。
- EDID。
- 热插拔检测 HPD。
- DDC/I2C。
- HDCP，视产品需求。

常见问题：

- 显示器无信号。
- EDID 读取失败。
- 分辨率不匹配。
- 线缆质量导致闪屏。

## eDP

eDP 是嵌入式 DisplayPort。

常见于：

- 笔记本屏。
- 平板屏。
- 高分辨率嵌入式显示。

涉及：

- Main Link Lane。
- AUX 通道。
- Link Training。
- Panel 电源时序。
- 背光控制。

## 与 MIPI DSI 对比

MIPI DSI 常见于移动/嵌入式屏。

eDP 常见于高分辨率计算平台屏幕。

HDMI 常见于外接显示。

## 工程注意

- 显示接口不仅是数据线，还包括 EDID/AUX、HPD、背光和电源时序。
- 高速线缆和连接器质量非常关键。
- 屏参和时序必须匹配。

## 延伸阅读

- `bus/display-interfaces.md`
- `bus/mipi-csi-dsi-deep-dive.md`
