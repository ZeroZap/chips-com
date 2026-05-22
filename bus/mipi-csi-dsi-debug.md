# MIPI CSI/DSI Debug Guide

## 目标

本文用于 MIPI 摄像头和显示屏调试，重点覆盖电源时序、I2C 初始化、Lane 参数、像素格式和常见黑屏/无图问题。

## 分层关系

摄像头常见链路：

```text
Power/GPIO/MCLK -> Sensor 初始化
I2C -> Sensor 寄存器配置
MIPI CSI -> 图像数据
CSI Receiver/ISP -> 图像处理
```

屏幕常见链路：

```text
Power/GPIO -> Panel 初始化
MIPI DSI -> 显示命令和像素数据
PWM/Enable -> 背光
I2C/SPI -> 触摸控制器
```

## CSI 摄像头调试顺序

1. 确认 AVDD、DVDD、IOVDD 电源时序。
2. 确认 RESET/PWDN GPIO 状态。
3. 确认 MCLK 频率，例如 24 MHz。
4. 用 I2C 读取 Sensor ID。
5. 写入厂商初始化寄存器表。
6. 配置分辨率、帧率、像素格式和 Lane 数。
7. 启动 streaming。
8. 配置 SoC CSI Receiver 参数匹配。
9. 配置 ISP 或采集链路。
10. 观察帧同步、错误计数和图像输出。

## CSI 关键参数

```text
Lane count
Lane rate
MCLK
Resolution
Frame rate
Pixel format
RAW bit depth
Virtual Channel
Data Type
```

Sensor 输出和 SoC 接收端必须一致。

## DSI 屏幕调试顺序

1. 确认屏幕电源时序。
2. 确认 RESET 时序。
3. 发送 DSI 初始化命令表。
4. 设置像素格式。
5. 发送 Sleep Out，例如 `0x11`。
6. 延时满足手册要求。
7. 发送 Display On，例如 `0x29`。
8. 配置 Video Mode 或 Command Mode。
9. 打开背光。
10. 输出测试图案。

## DSI 关键参数

```text
Lane count
Lane rate
Video/Command mode
Pixel format
Hactive/Vactive
HSA/HBP/HFP
VSA/VBP/VFP
DSI command sequence
Backlight enable/PWM
```

## 常见现象定位

| 现象 | 优先检查 |
| --- | --- |
| 摄像头 I2C 扫不到 | 电源、RESET、MCLK、地址、电平 |
| I2C 正常但无图 | streaming、CSI 参数、Lane 数 |
| 图像花屏 | 像素格式、Lane 速率、RAW/YUV 解析 |
| 图像颜色异常 | Bayer 顺序、RAW bit depth、ISP 配置 |
| 屏幕背光亮无图 | DSI 初始化、显示时序、像素格式 |
| 屏幕完全黑 | 电源、RESET、背光、Sleep Out |
| 触摸不通 | 触摸 I2C/SPI 独立排查 |

## 硬件检查

- 差分阻抗符合设计要求。
- P/N 极性正确。
- Lane 顺序正确。
- FPC 引脚定义匹配。
- ESD 器件电容适合高速 MIPI。
- 参考平面连续。
- 电源噪声满足 sensor/panel 要求。

## 软件检查

- 设备树或板级配置中 Lane 数一致。
- MCLK 频率与寄存器表匹配。
- Sensor 初始化表对应当前分辨率和帧率。
- DSI 初始化命令对应当前 panel 型号。
- ISP 配置匹配 RAW 格式和 Bayer 顺序。
- 背光和触摸不是同一链路问题。

## 实战检查清单

- 先确认低速控制链路，再看高速 MIPI。
- 摄像头先读 ID，再启动 streaming。
- 屏幕先发初始化命令，再开背光。
- 两端 Lane、格式、时序完全一致。
- 用测试图案和固定曝光降低变量。
