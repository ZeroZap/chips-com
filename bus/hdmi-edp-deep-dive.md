# HDMI / eDP Deep Dive

## 目标

本文深入 HDMI 和 eDP 显示链路的工程机制，重点覆盖 EDID、HPD、DDC、AUX、DPCD、Link Training、TMDS、DisplayPort Main Link、Panel 电源时序、背光、HDCP、信号完整性和黑屏/闪屏排查。

本文不重复基础调试顺序，而是回答这些问题：

- HDMI 外接显示为什么要先看 5V、HPD 和 EDID。
- eDP 面板为什么电源时序、AUX 和 Link Training 都必须正确。
- EDID、DPCD、显示模式、Lane 数和 Link Rate 如何共同决定能否出图。
- 背光亮无图和有图无背光为什么是两类问题。
- 高分辨率下为什么线缆、连接器、equalization 和时钟质量会导致闪屏。

## 分层模型

显示链路可按以下层次理解：

```text
Power / Reset / HPD / Backlight
        |
Sideband：HDMI DDC / eDP AUX
        |
Capability：EDID / DPCD / Panel Timing
        |
Link：TMDS / DP Main Link / Lane / Rate / Training
        |
Video Timing：Resolution / Refresh / Pixel Clock / Format
        |
Image Pipeline：Framebuffer / Mixer / Encoder / PHY
        |
Display：Monitor / Panel / TCON / Backlight Driver
```

关键点：

- HDMI 更偏外接显示器和线缆生态。
- eDP 更偏嵌入式面板和固定屏参。
- Sideband 通道不通时，通常还没到高速视频链路问题。
- 背光、电源和视频流要分开排查。

## HDMI 链路组成

HDMI 常见信号：

- TMDS Data Lane。
- TMDS Clock，老版本常见。
- DDC I2C。
- HPD。
- 5V。
- CEC，视产品需要。
- HEAC/ARC/eARC，视产品需要。

调试顺序：

```text
5V 输出
HPD 输入
DDC 读取 EDID
选择显示模式
配置 HDMI PHY / PLL
输出 TMDS / FRL
显示器锁定信号
```

如果 HPD 不高，源端通常不会读取 EDID 或输出视频。

如果 EDID 读不到，通常先查 DDC、上拉、电平、线缆和显示器供电。

## EDID 和显示模式

EDID 描述显示设备能力。

常见内容：

- 厂商和产品信息。
- 支持分辨率。
- 刷新率。
- 时序参数。
- 音频能力。
- 色彩格式。
- 扩展块。
- HDR 或其他能力，视版本而定。

工程注意：

- EDID 能读到不代表所有模式都稳定。
- 选择超出链路能力的模式会无显示或闪屏。
- 有些显示器 EDID 兼容性差，需要 fallback 模式。
- 开发阶段可强制固定模式，排除 EDID 解析问题。

常见 fallback：

```text
1920x1080@60
1280x720@60
1024x768@60
```

## DDC 和 HPD

DDC 是 I2C 通道，用于读取 EDID。

HPD 是热插拔检测。

检查项：

- HDMI 5V 是否存在。
- HPD 是否被显示器拉高。
- DDC SCL/SDA 是否有上拉。
- DDC 电平域是否正确。
- I2C 地址是否应答。
- 是否存在总线被拉低。
- ESD 器件或电平转换是否影响波形。

常见问题：

| 现象 | 优先检查 |
| --- | --- |
| HPD 不高 | 5V、线缆、显示器状态、HPD 引脚复用 |
| EDID 读不到 | DDC 上拉、SCL/SDA 反接、电平、地址、总线被拉低 |
| 热插拔异常 | HPD 中断、防抖、驱动状态机、线缆接触 |

## TMDS 和高速信号

HDMI 老版本常用 TMDS 传输。

高分辨率下要关注：

- Pixel Clock。
- TMDS Clock。
- Lane 速率。
- PHY PLL。
- 线缆质量。
- 连接器阻抗。
- ESD 器件带宽。
- 差分对长度和阻抗。
- 均衡和驱动强度。

典型现象：

- 低分辨率正常，高分辨率闪屏。
- 短线正常，长线闪屏。
- 某些显示器正常，某些显示器无信号。
- 冷机正常，热机闪屏。

这类问题通常不是软件模式表本身，而是链路裕量不足或 PHY/板级设计边界。

## eDP 链路组成

eDP 常见信号：

- Main Link Lane 0..N。
- AUX CH。
- HPD，视平台和面板定义。
- Panel Power。
- Panel Reset。
- Backlight Enable。
- PWM / Backlight Control。

典型启动流程：

```text
打开 Panel 电源
等待电源稳定
释放 Panel Reset
通过 AUX 读取 DPCD
读取 EDID 或面板固定时序
执行 Link Training
配置视频时序
打开 Main Link 视频流
打开背光
```

eDP 黑屏必须分清是面板没上电、AUX 不通、Link Training 失败、视频流异常，还是背光没开。

## AUX 和 DPCD

AUX 是 DisplayPort/eDP 的低速辅助通道。

它用于：

- 读取 DPCD。
- 读取 EDID。
- Link Training 交互。
- 配置面板能力。
- 状态读取。

DPCD 描述链路能力，例如：

- 支持的 Link Rate。
- 支持的 Lane Count。
- Training 状态。
- Downspread。
- eDP 特性。

AUX 不通时，Link Training 通常无法继续。

常见原因：

- AUX P/N 接反。
- 电平或共模不匹配。
- Panel 电源或 reset 时序错误。
- 连接器定义错。
- ESD/共模器件影响信号。

## Link Training

Link Training 用于建立稳定的 DP/eDP Main Link。

它通常包括：

- Clock Recovery。
- Channel Equalization。
- Lane 对齐。
- Link Rate 和 Lane Count 协商。

调试关注：

- 使用几条 Lane。
- 使用哪个 Link Rate。
- Training Pattern 是否完成。
- DPCD 状态位是否达标。
- 是否需要降速或减少 Lane。
- 主控和面板支持能力是否匹配。

常见问题：

| 现象 | 优先检查 |
| --- | --- |
| Link Training 失败 | AUX、Lane 极性、Lane 顺序、速率、信号质量 |
| 低分辨率正常高分失败 | Link Rate、Lane 数、线缆、均衡、时钟 |
| 偶发闪屏 | 链路裕量、屏线、连接器、EMI、热稳定性 |

## Panel 电源和背光

eDP 面板通常需要严格电源时序。

常见控制：

- VDD / Panel Power。
- Reset。
- Backlight Enable。
- PWM。
- Bias Power，视面板类型。

分层排查：

```text
无背光无图：先查电源和 reset
背光亮无图：查 AUX、Link Training、视频流
有图无背光：查背光电源、EN、PWM、驱动
闪屏：查链路裕量、背光供电、EMI、时序
```

背光控制不是视频链路的一部分。背光亮并不代表视频链路正常。

## 视频时序和像素格式

显示模式包含：

- 分辨率。
- 刷新率。
- Pixel Clock。
- Hsync / Vsync。
- Front Porch / Back Porch。
- DE。
- 色彩格式。
- 位深。

常见错误：

- EDID 解析到的模式驱动不支持。
- 面板固定时序和设备树不一致。
- RGB/YUV 格式不匹配。
- 色深超出链路带宽。
- 双通道或多 Lane 配置不一致。

显示异常表现：

- 无图。
- 偏色。
- 花屏。
- 分辨率错。
- 画面偏移。
- 闪烁。

## HDCP 和内容保护

HDCP 视产品需求启用。

注意：

- HDCP 失败可能导致受保护内容黑屏。
- 非受保护测试画面通常不应依赖 HDCP。
- 早期调试显示链路时应先用非 HDCP 内容排除基础链路问题。
- HDCP 涉及密钥、认证和合规，不应与基础链路训练混为一谈。

## 驱动和系统软件

Linux/SoC 显示链路常见组件：

- Display Controller。
- HDMI/eDP Encoder。
- PHY / PLL。
- Bridge Chip。
- Connector。
- Panel Driver。
- Backlight Driver。
- Regulator。
- GPIO reset / enable。
- DRM/KMS Mode Setting。

调试入口：

```text
dmesg
drm.debug
modetest
edid-decode
i2cdetect / i2cdump，视硬件路径
debugfs DRM 状态
示波器 / 协议分析仪
```

常见软件问题：

- 设备树 lane 数或 phy-mode 错。
- regulator 名称或时序错。
- reset GPIO 极性错。
- backlight PWM 极性错。
- bridge chip 初始化顺序错。
- EDID 读取失败后没有 fallback。

## 桥接芯片

很多产品使用桥接：

- MIPI DSI to HDMI。
- MIPI DSI to eDP。
- eDP to LVDS。
- HDMI receiver to RGB/CSI。

桥接调试要分清两侧：

```text
Source -> Bridge 输入侧
Bridge 内部配置
Bridge 输出侧 -> Display
```

常见问题：

- I2C 配置桥失败。
- 输入侧无时钟或格式错。
- 输出侧 Link Training 失败。
- 桥芯片 reset 和电源时序错。
- 固件配置表与屏参不匹配。

## 现场排查流程

HDMI：

1. 确认 5V。
2. 确认 HPD。
3. 读取 EDID。
4. 选择低分辨率安全模式。
5. 输出测试图。
6. 提升到目标分辨率。
7. 更换线缆和显示器做交叉验证。
8. 必要时检查 TMDS 信号质量。

eDP：

1. 确认 Panel 电源。
2. 确认 reset 时序。
3. 确认 AUX 可读 DPCD。
4. 确认 EDID 或固定屏参。
5. 执行 Link Training。
6. 降低 Link Rate 或 Lane 数验证裕量。
7. 输出测试图。
8. 打开背光。
9. 检查闪屏和热稳定性。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| HDMI 无信号 | 5V、HPD、EDID、显示模式、PHY PLL |
| HDMI EDID 读不到 | DDC 上拉、电平、线缆、显示器、HPD |
| HDMI 高分闪屏 | 线缆、ESD 器件、TMDS 裕量、PHY 参数 |
| eDP AUX 不通 | Panel 电源、reset、AUX P/N、连接器、ESD |
| eDP Training 失败 | Lane 顺序、Lane 极性、Link Rate、屏线、DPCD 状态 |
| 背光亮无图 | Main Link、视频时序、Link Training、像素格式 |
| 有图无背光 | Backlight EN、PWM、背光电源、驱动极性 |
| 花屏偏色 | RGB/YUV、bit depth、lane mapping、时序 |

## 深度检查清单

- HDMI 5V、HPD、DDC 和 EDID 已确认。
- HDMI fallback 模式可显示。
- HDMI 高分辨率经过线缆和显示器交叉验证。
- eDP Panel 电源、reset、AUX、DPCD 已确认。
- eDP Link Training 状态位达标。
- Lane 数、Link Rate 和屏参匹配。
- 背光 EN/PWM 与视频链路分开验证。
- Bridge 芯片输入侧、输出侧和配置路径分开排查。
- 设备树、regulator、GPIO、PHY、PLL 和 panel driver 配置一致。
- 黑屏、闪屏、花屏分别按电源/侧带/高速链路/视频时序分层定位。

## 与 MIPI DSI 的区别

MIPI DSI 常见于移动和嵌入式屏，强调 DSI command/video mode、D-PHY Lane 和屏初始化命令。

eDP 强调 AUX、DPCD、Link Training、Lane Rate 和 Panel 电源/背光。

HDMI 强调外接显示、HPD、DDC/EDID、线缆、兼容性和内容保护。

三者都可能黑屏，但排查入口不同。

## 延伸阅读

- `bus/hdmi-edp.md`
- `bus/hdmi-edp-practical.md`
- `bus/display-interfaces.md`
- `basic/lvds.md`
- `bus/mipi-csi-dsi-deep-dive.md`
