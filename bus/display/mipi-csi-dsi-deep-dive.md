# MIPI CSI/DSI Deep Dive

## 目标

本文深入 MIPI CSI/DSI 工程细节，重点覆盖 D-PHY Lane、摄像头初始化、显示屏初始化、RAW/YUV/RGB 格式、CSI Receiver、ISP、DSI Video/Command Mode、电源时序、MCLK、RESET、黑屏、花屏和无图排查。

## MIPI 不是单一接口

MIPI 是一组移动和嵌入式接口标准。

本文聚焦：

```text
MIPI CSI：Camera Serial Interface，摄像头输入
MIPI DSI：Display Serial Interface，显示输出
```

简化理解：

```text
CSI：Sensor -> SoC
DSI：SoC -> Panel
```

## CSI/DSI 与低速控制接口

MIPI 高速 Lane 通常只传输图像或显示数据。

设备初始化还需要其他信号。

摄像头常见：

```text
MIPI CSI Data/Clock Lane
I2C 控制接口
MCLK
RESET
PWDN
AVDD/DVDD/IOVDD
```

屏幕常见：

```text
MIPI DSI Data/Clock Lane
RESET
电源 rail
背光 EN/PWM
触摸 I2C/SPI
触摸 INT
```

工程直觉：

```text
MIPI 负责高速数据
I2C/GPIO/Clock/Power 负责让设备进入正确状态
```

## D-PHY Lane

CSI/DSI 常见物理层是 D-PHY。

常见信号：

```text
Clock Lane：CLK+ / CLK-
Data Lane 0：D0+ / D0-
Data Lane 1：D1+ / D1-
Data Lane 2：D2+ / D2-
Data Lane 3：D3+ / D3-
```

常见 Lane 数：

```text
1 Lane
2 Lane
4 Lane
```

Lane 数越多，总带宽越高。

## Lane 速率估算

摄像头带宽粗略估算：

```text
width × height × fps × bits_per_pixel
```

例如：

```text
1920 × 1080 × 30 × 10 bit ≈ 622 Mbps 原始数据
```

再考虑协议开销和 blanking，需要更高 Lane 总带宽。

如果 2 Lane 不够，就需要提高 Lane rate 或增加 Lane 数。

## CSI 摄像头初始化流程

典型流程：

```text
打开电源 rail
等待电源稳定
提供 MCLK
释放 PWDN
释放 RESET
通过 I2C 读取 Sensor ID
写初始化寄存器表
配置分辨率、帧率、曝光、增益
配置像素格式和 MIPI Lane
配置 SoC CSI Receiver
启动 Sensor streaming
启动 ISP 或采集链路
```

顺序错误可能导致：

- I2C 扫不到。
- Sensor ID 读错。
- 有 MIPI 波形但无图。
- 偶发启动失败。

## MCLK

很多 Sensor 需要外部参考时钟。

常见频率：

```text
19.2 MHz
24 MHz
26 MHz
27 MHz
```

MCLK 错误会导致：

- I2C 能通但不出图。
- 帧率不对。
- PLL 配置失败。
- MIPI Lane rate 不匹配。

初始化寄存器表通常和 MCLK 频率绑定。

不要随意换 MCLK 而不改寄存器表。

## CSI Receiver 配置

SoC 端 CSI Receiver 必须匹配 Sensor 输出：

- Lane 数。
- Lane 速率。
- 数据类型。
- Virtual Channel。
- 像素格式。
- 分辨率。
- 时钟连续或非连续模式。

Sensor 配 2 Lane，SoC 配 4 Lane，通常无法正常接收。

Sensor 输出 RAW10，SoC 按 YUV422 解析，会出现异常。

## RAW、YUV、RGB

摄像头常见输出：

```text
RAW8 / RAW10 / RAW12
YUV422
RGB
```

多数图像传感器原始输出是 Bayer RAW。

RAW 数据不是最终 RGB 图片，需要 ISP 处理。

ISP 处理包括：

- 黑电平校正。
- 去马赛克。
- 白平衡。
- 色彩校正。
- 降噪。
- Gamma。
- 格式转换。

如果把 RAW 当 RGB 看，图像会花、偏色或像马赛克。

## Bayer 顺序

常见 Bayer 排列：

```text
RGGB
GRBG
GBRG
BGGR
```

Bayer 顺序配置错误会导致：

- 偏绿。
- 偏紫。
- 颜色严重错误。
- 细节异常。

调试图像颜色时，除了曝光和白平衡，也要检查 Bayer order。

## Virtual Channel 和 Data Type

MIPI CSI-2 使用：

```text
VC：Virtual Channel
DT：Data Type
```

常见用途：

- 多路图像复用。
- 图像数据和嵌入式 metadata 区分。
- HDR 多曝光数据。

如果 VC 或 DT 过滤配置不对，SoC 可能丢弃有效数据。

## Embedded Data

有些 Sensor 会输出 embedded data，例如：

- 曝光信息。
- 增益信息。
- 帧计数。
- 统计信息。

这些数据可能使用不同 Data Type。

驱动要决定：

- 是否接收。
- 是否丢弃。
- 是否传给 ISP。
- 是否用于 3A 算法。

## DSI 屏幕初始化流程

典型流程：

```text
打开 panel 电源
等待电源稳定
执行 RESET 时序
初始化 DSI Host
发送厂商初始化命令表
设置像素格式
Sleep Out，通常 0x11
等待规定延时
Display On，通常 0x29
启动 Video/Command 传输
打开背光
```

注意：

```text
背光亮不代表 DSI 显示链路正常
```

背光只是照明，图像数据和屏幕初始化是另一条链路。

## DCS 命令

常见 DSI DCS 命令：

```text
0x11：Sleep Out
0x29：Display On
0x28：Display Off
0x10：Enter Sleep Mode
0x3A：Set Pixel Format
0x36：Memory Access Control
```

很多屏幕还需要大量厂商私有命令。

这些命令通常来自：

- 屏厂初始化表。
- 原厂驱动。
- BSP。
- Android/Linux panel driver。

## DSI Video Mode 和 Command Mode

`Video Mode`：

```text
SoC 按显示时序持续推送整帧数据
类似传统 RGB/LVDS 显示流
```

`Command Mode`：

```text
通过命令和数据包更新屏幕
适合带显存或低功耗局部刷新
```

屏幕支持哪种模式取决于 panel 控制器。

驱动配置必须匹配屏幕手册。

## 显示时序

Video Mode 需要配置：

```text
Hactive
HSA
HBP
HFP
Vactive
VSA
VBP
VFP
Pixel clock
Lane rate
```

这些参数不匹配会导致：

- 黑屏。
- 花屏。
- 图像偏移。
- 抖动。
- 屏幕偶发闪烁。

## 像素格式

DSI 常见像素格式：

```text
RGB565
RGB666
RGB888
```

SoC 输出格式、DSI Host 格式、Panel 接收格式必须一致。

格式不匹配可能导致：

- 颜色异常。
- 图像错位。
- 一行数据长度不对。
- 花屏。

## 触摸和显示分离

带触摸屏常见结构：

```text
显示：MIPI DSI
触摸：I2C 或 SPI
触摸中断：GPIO
触摸复位：GPIO
```

触摸不通不要直接归因于 DSI。

显示不亮也不代表触摸控制器有问题。

两条链路要分开排查。

## 硬件设计注意

MIPI 是高速差分接口。

重点：

- 差分阻抗。
- P/N 极性。
- Lane 顺序。
- 走线长度匹配。
- 参考平面连续。
- 过孔数量。
- FPC 连接器定义。
- ESD 器件寄生电容。
- 电源噪声。
- MCLK 质量。

MIPI 不适合飞线调试。

## Lane Swap 和 Polarity Swap

有些 SoC 支持：

```text
Lane swap
Polarity swap
```

有些不支持。

如果硬件 Lane 顺序或 P/N 接反，是否能软件修正要提前确认。

不能修正时只能改硬件。

## Linux 设备树常见配置

Linux 下常见需要描述：

- Sensor I2C 地址。
- Clocks。
- Regulators。
- Reset/PWDN GPIO。
- MIPI endpoint。
- Data lanes。
- Link frequency。
- Pixel format。
- Panel timing。
- Backlight。

设备树和驱动不匹配时，硬件正常也可能不出图。

## CSI 调试顺序

推荐顺序：

1. 确认电源时序。
2. 确认 MCLK。
3. 确认 RESET/PWDN。
4. I2C 读取 Sensor ID。
5. 写入初始化表。
6. 用示波器或 SoC 状态确认 MIPI 有活动。
7. 确认 Lane 数和 link frequency。
8. 确认 RAW/YUV 格式。
9. 确认 ISP pipeline。
10. 输出测试帧或固定曝光图像。

## DSI 调试顺序

推荐顺序：

1. 确认 panel 电源。
2. 确认 RESET 时序。
3. 确认 DSI Host 初始化。
4. 发送 panel 初始化命令。
5. 发送 Sleep Out 和 Display On。
6. 配置显示时序和像素格式。
7. 输出纯色测试图。
8. 打开背光。
9. 检查是否有花屏、偏色、偏移。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| Sensor I2C 不通 | 电源、MCLK、RESET、地址、电平 |
| I2C 通但无图 | streaming、Lane、CSI Receiver、格式 |
| 图像花屏 | Lane rate、格式、Bayer、信号完整性 |
| 图像偏色 | Bayer order、白平衡、RAW bit depth |
| 屏幕背光亮无图 | DSI 初始化、Sleep Out、Display On、时序 |
| 屏幕花屏 | Lane、pixel format、timing、初始化表 |
| 触摸无响应 | 触摸 I2C/SPI、INT、RESET，独立排查 |
| 偶发启动失败 | 电源时序、RESET 延时、MCLK 稳定时间 |

## 深度检查清单

- 摄像头和屏幕电源 rail 顺序正确。
- MCLK 频率与寄存器表匹配。
- RESET/PWDN 时序满足手册。
- I2C 初始化表对应当前硬件版本。
- Lane 数、Lane 顺序、P/N 极性正确。
- CSI Receiver 和 Sensor 输出参数一致。
- RAW/YUV/RGB 格式一致。
- Bayer order 配置正确。
- DSI Video/Command Mode 与 panel 匹配。
- Panel 初始化命令完整。
- 背光和显示链路分开排查。
- Linux 设备树 endpoint 和 data-lanes 正确。
