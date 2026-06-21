# FPD-Link / GMSL Deep Dive

## 目标

本文深入车载视频 SerDes 链路的工程机制，重点覆盖 FPD-Link/GMSL 分层模型、Serializer/Deserializer 配对、链路锁定、反向控制通道、远端 I2C、同轴供电、线缆和连接器、MIPI CSI/DSI 桥接、多摄像头同步、带宽预算、EMC、诊断寄存器和现场排查。

本文不重复基础调试顺序，而是回答这些问题：

- 为什么 Deserializer I2C 可访问不代表远端摄像头可用。
- 为什么 Link Lock 成功不代表一定有图。
- 为什么远端 I2C、MIPI CSI、视频格式和 SoC Receiver 必须分层验证。
- 为什么多摄像头系统要同时规划 I2C alias、Virtual Channel、同步和带宽。
- 为什么车载环境下线缆、连接器、PoC 和 EMC 会导致偶发掉线。

## 分层模型

FPD-Link/GMSL 链路可按以下层次理解：

```text
Power / Reset / Clock / GPIO
        |
Local Control：SoC I2C -> Deserializer
        |
SerDes Link：Deserializer <-> Serializer
        |
Back Channel：远端 I2C / GPIO / 控制通道
        |
Remote Device：Sensor / Panel / PMIC / EEPROM
        |
Video Bridge：MIPI CSI/DSI / Parallel / RGB
        |
SoC Receiver / Display Controller / ISP
```

关键点：

- 本地 I2C 通只说明 SoC 能访问 Deserializer。
- Link Lock 只说明 SerDes 物理链路建立。
- 远端 I2C 通才说明反向控制链路、地址映射和远端上电基本可用。
- 有 MIPI 输出不代表 SoC CSI Receiver 参数正确。
- 有图但偶发掉线通常要回到线缆、电源、EMC 和链路裕量。

## 典型摄像头系统

摄像头输入链路：

```text
Image Sensor
  -> MIPI CSI-2
  -> Serializer
  -> Coax / STP Cable
  -> Deserializer
  -> MIPI CSI-2
  -> SoC CSI Receiver
  -> ISP
```

控制链路：

```text
SoC I2C
  -> Deserializer local registers
  -> Back Channel
  -> Serializer remote registers
  -> Sensor I2C registers
```

供电链路可能是：

```text
本地电源 -> PoC Network -> 同轴线 -> 远端 PMIC / LDO -> Sensor + Serializer
```

如果使用双绞线或独立供电，则供电路径不同，但排查仍要把电源、控制、视频和高速链路分开。

## Serializer 和 Deserializer 配对

SerDes 不是任意组合都能互通。

必须确认：

- 同一家族或兼容代际。
- 支持的链路速率。
- 支持的线缆类型。
- 是否支持目标视频格式和 Lane 数。
- 是否支持所需反向通道速率。
- 是否支持多路聚合、splitter 或复制输出。
- 寄存器配置脚本是否对应当前芯片版本。

常见问题：

- 原理图型号和软件配置脚本型号不一致。
- Serializer/Deserializer revision 不同，默认寄存器行为变化。
- 评估板脚本直接移植到量产板后，GPIO、电源和地址映射不匹配。
- 摄像头模组更换后，远端上电时序和 sensor 初始化表没有同步更新。

## Link Lock 的含义

Link Lock 表示 Deserializer 和 Serializer 之间的高速串行链路达到某种同步状态。

它通常不代表：

- Sensor 已上电。
- Sensor I2C 已通。
- Sensor 已 streaming。
- MIPI CSI 参数正确。
- SoC 已正确接收图像。

无 Link Lock 时优先检查：

- 远端 Serializer 是否上电。
- 同轴或双绞线是否连接正确。
- 连接器 pinout、屏蔽和接触是否可靠。
- PoC 电感、电容、Bias-T 和滤波网络是否符合参考设计。
- 线缆长度和类型是否超出芯片配置。
- Serializer/Deserializer 模式 strap 是否正确。
- 链路速率、equalizer、pre-emphasis 或 adaptive EQ 是否配置合理。

有 Link Lock 但无图时，优先转向反向 I2C、sensor streaming、MIPI 参数和 SoC CSI Receiver。

## 反向控制通道

FPD-Link/GMSL 的工程价值之一是把控制信号通过同一条链路传到远端。

常见承载：

- I2C。
- GPIO。
- Frame sync。
- Interrupt。
- 远端寄存器访问。

反向通道常见配置项：

- 启用 back channel。
- 设置 back channel 速率。
- 配置 I2C pass-through。
- 配置 I2C alias 或 address translation。
- 配置远端 GPIO 映射。
- 配置 broadcast 或 per-port 控制。

反向 I2C 不通时不要直接判定 sensor 坏。先确认 Deserializer 是否能读到远端 Serializer 状态，再确认 alias、远端上电、reset 和 sensor 地址。

## I2C Alias 和地址规划

多摄像头系统经常出现多个相同 Sensor。

这些 Sensor 原始 I2C 地址相同，需要由 Deserializer 提供地址别名或端口隔离。

典型映射：

```text
Camera 0 Sensor native：0x36 -> SoC sees：0x60
Camera 1 Sensor native：0x36 -> SoC sees：0x62
Camera 2 Sensor native：0x36 -> SoC sees：0x64
Camera 3 Sensor native：0x36 -> SoC sees：0x66
```

还要规划：

- Serializer 远端寄存器地址。
- Sensor 地址。
- PMIC 地址。
- EEPROM 地址。
- Lens 或 actuator 地址。
- 多路端口的 broadcast 行为。

常见故障：

| 现象 | 优先检查 |
| --- | --- |
| 单摄正常，多摄冲突 | alias 是否唯一、端口隔离是否启用 |
| 读到错误 Sensor ID | alias 指向错误端口、broadcast 未关闭 |
| I2C 偶发 NACK | back channel 速率、上拉、电源时序、线缆干扰 |
| 扫描 I2C 导致异常 | 误写敏感寄存器、地址冲突、设备不支持读操作 |

多摄像头量产系统不建议依赖盲扫 I2C 作为主要探测方法，应使用已知地址和明确状态寄存器。

## MIPI CSI 桥接

摄像头 SerDes 系统通常有两段 MIPI：

```text
Sensor -> Serializer：MIPI CSI 输入
Deserializer -> SoC：MIPI CSI 输出
```

两段参数可以不同，但必须被正确桥接。

需要匹配：

- Lane 数。
- Lane rate。
- Data Type。
- Virtual Channel。
- 分辨率。
- 帧率。
- bit depth。
- embedded data。
- 时钟连续或非连续模式。

常见错误：

- Sensor 输出 RAW10，SoC 按 RAW12 或 YUV 接收。
- Deserializer 输出 4 Lane，但 SoC 设备树配置为 2 Lane。
- 多摄聚合后 VC 未区分，SoC 只收到一路或全部丢弃。
- embedded data 使用单独 Data Type，但驱动过滤配置错误。
- Deserializer CSI 输出 Lane 极性或顺序和板级连接不一致。

## 带宽预算

SerDes 链路必须同时满足视频输入、输出和聚合带宽。

摄像头原始带宽粗略估算：

```text
width x height x fps x bits_per_pixel
```

示例：

```text
1920 x 1080 x 30 x 12 bit ~= 746 Mbps
```

还要考虑：

- MIPI CSI-2 packet overhead。
- Blanking。
- Embedded data。
- 多路聚合。
- HDR 多曝光。
- 8b/10b、64b/66b 或厂商链路编码开销，视芯片而定。
- Deserializer 输出 MIPI Lane 总能力。

多摄聚合示例：

```text
4 x 1920x1080@30 RAW12 ~= 2.98 Gbps 原始数据
```

如果链路裕量不足，可能表现为：

- 单摄正常，多摄不稳定。
- 降帧率后正常。
- 低温或高温下更容易丢帧。
- 图像偶发 tearing、CRC error 或 frame sync error。

## 同轴、双绞线和连接器

常见介质：

- Coax，同轴线，便于 PoC 和单连接器摄像头。
- STP，屏蔽双绞线，常见于部分车载和工业场景。
- FAKRA、HSD、Mini FAKRA 或厂商专用连接器。

工程关注：

- 差分或单端通道阻抗。
- 插入损耗。
- 回波损耗。
- 线缆长度。
- 弯折半径。
- 屏蔽接地。
- 连接器接触可靠性。
- 水汽、振动和温度循环。
- ESD 和浪涌防护器件寄生参数。

典型现场现象：

- 短线正常，长线无 lock。
- 静态正常，振动后掉线。
- 实验室正常，整车环境偶发花屏。
- 更换线束供应商后裕量下降。

这类问题通常需要读取 SerDes error counter、观察 lock drop 记录，并做线缆交叉验证。

## PoC 和远端供电

PoC 是 Power over Coax，通过同轴线同时传输电源和高速信号。

简化结构：

```text
本地电源
  -> PoC 注入网络
  -> 同轴线
  -> PoC 提取网络
  -> 远端 DC/DC 或 LDO
  -> Serializer / Sensor
```

PoC 设计关注：

- 电感和磁珠在 SerDes 频段的阻抗。
- 电源纹波对链路的调制。
- 启动浪涌。
- 远端负载瞬态。
- 短路保护。
- 线缆压降。
- EMC 滤波和共模路径。

常见故障：

| 现象 | 优先检查 |
| --- | --- |
| 远端不上电 | PoC 注入、保险丝、线缆、远端 DC/DC EN |
| 冷启动失败 | 浪涌、软启动、reset 延时、电源稳定时间 |
| 图像亮暗变化时掉线 | 远端负载瞬态、电源纹波、PoC 滤波 |
| EMC 测试掉线 | PoC 网络、屏蔽接地、共模滤波、线束布局 |

## 多摄像头同步

环视、ADAS 和机器视觉常需要多摄同步。

同步方式可能包括：

- Deserializer 输出 frame sync 到各 Serializer。
- Serializer 转发 GPIO sync 到 Sensor。
- Sensor 支持外部 FSIN。
- SoC 或 MCU 输出统一触发。
- PTP 或更高层时间同步，视系统架构而定。

同步要同时确认：

- 同步信号电平和极性。
- 周期和脉宽。
- Sensor 寄存器是否启用外同步模式。
- 曝光时间是否超过帧周期。
- 多路 VC 和帧计数是否连续。
- ISP 或应用层是否按同一时间戳处理。

不同步的表现：

- 多摄拼接边界错位。
- 运动物体有撕裂感。
- 某一路固定延迟一帧。
- HDR 或曝光切换时帧序错乱。

## 诊断寄存器和错误计数

SerDes 芯片通常提供丰富状态寄存器。

调试时优先读取：

- Link lock 状态。
- Lock drop counter。
- CRC / packet error counter。
- Cable equalizer 状态。
- Back channel error。
- Remote device present。
- CSI input status。
- CSI output status。
- Line length / frame length 检测。
- 温度和电源状态。
- GPIO 状态。

建议保存两类日志：

- 启动时完整寄存器 dump。
- 故障发生后立即寄存器 dump。

对比两份 dump 往往比只看 dmesg 更快定位问题层级。

## Linux 和驱动入口

Linux 摄像头链路常见组件：

- I2C adapter。
- Deserializer driver。
- Serializer subdevice，视驱动建模方式而定。
- Sensor driver。
- V4L2 subdev。
- Media Controller graph。
- CSI receiver driver。
- ISP driver。
- Regulators / GPIO / Clocks。

常见检查入口：

```text
dmesg
i2cdetect / i2cdump / i2ctransfer
media-ctl -p
v4l2-ctl --list-devices
v4l2-ctl --stream-mmap
debugfs 或 sysfs 中的 CSI/ISP 状态
SerDes 厂商寄存器 dump 工具
示波器 / 频谱仪 / 协议分析仪
```

常见软件问题：

- 设备树 endpoint 连接错。
- data-lanes 顺序错。
- link-frequencies 与 sensor 输出不一致。
- reset GPIO 极性错。
- regulator 名称或 enable 时序错。
- SerDes 初始化脚本运行顺序早于远端供电稳定。
- 多摄 media graph 中 VC 或 port index 描述不一致。

## 初始化顺序

推荐顺序：

1. 打开本地 Deserializer 电源和 reset。
2. 通过本地 I2C 读取 Deserializer ID。
3. 配置 Deserializer 基础模式和端口。
4. 打开 PoC 或远端电源。
5. 等待远端 Serializer 和 Sensor 电源稳定。
6. 确认 SerDes Link Lock。
7. 配置 back channel 和 I2C alias。
8. 读取远端 Serializer ID。
9. 释放 Sensor reset 并读取 Sensor ID。
10. 写 Sensor 初始化表。
11. 配置 Serializer MIPI 输入。
12. 配置 Deserializer MIPI 输出和 VC 映射。
13. 配置 SoC CSI Receiver。
14. 启动 Sensor streaming。
15. 启动采集并检查帧计数、错误计数和图像。

不同芯片可能要求先配 link 再开远端，或先供电再配 link。以芯片手册和参考驱动为准，但分层验证顺序不变。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| Deserializer I2C 不通 | 本地供电、reset、I2C 地址、上拉、电平、pinmux |
| 无 Link Lock | 远端供电、线缆、连接器、PoC、SerDes 配对、速率配置 |
| 有 Lock 但远端 I2C 不通 | back channel、alias、Serializer 状态、Sensor reset、远端电源 |
| 远端 Sensor ID 正确但无图 | Sensor streaming、MIPI 输入、Deserializer CSI 输出、SoC CSI 配置 |
| 有图但花屏 | RAW/YUV 格式、bit depth、Lane rate、VC/DT、信号质量 |
| 单摄正常多摄异常 | 带宽、VC 映射、I2C alias、同步、输出 Lane 能力 |
| 偶发掉线 | 线缆、连接器、PoC 瞬态、EMC、温度、lock drop counter |
| 冷启动失败热启动正常 | 电源时序、reset 延时、远端 PMIC、初始化脚本等待时间 |
| 高温后异常 | 芯片温度、线缆损耗、equalizer 裕量、电源降额 |

## 现场排查流程

推荐流程：

1. 保存硬件版本、线束版本、摄像头模组版本和 SerDes 型号。
2. 读取本地 Deserializer ID 和关键状态。
3. 检查远端供电和 PoC 电压。
4. 确认 Link Lock 和 lock drop counter。
5. 读取远端 Serializer ID。
6. 配置 alias 后读取 Sensor ID。
7. 读取 Sensor 当前模式寄存器和 streaming 状态。
8. 检查 Serializer CSI input 状态。
9. 检查 Deserializer CSI output 状态。
10. 检查 SoC CSI/ISP 错误计数。
11. 降低分辨率、帧率或 Lane rate 做裕量验证。
12. 更换短线、长线、不同线束和不同摄像头做交叉验证。
13. 对比正常样机和故障样机寄存器 dump。

## 深度检查清单

- Serializer/Deserializer 型号、revision 和配置脚本一致。
- 本地 Deserializer I2C、reset 和供电已确认。
- 远端 PoC 或独立供电满足启动和负载瞬态要求。
- Link Lock 稳定，lock drop counter 无异常增长。
- Back channel 已启用，速率和 I2C alias 正确。
- 多摄系统每路 Sensor、Serializer、PMIC 和 EEPROM 地址不冲突。
- Sensor ID、初始化表、MCLK 或参考时钟配置一致。
- Serializer MIPI 输入和 Deserializer MIPI 输出参数匹配。
- SoC CSI Receiver 的 lane、VC、DT、format、link-frequency 与 SerDes 输出一致。
- 多摄聚合带宽、VC 映射和同步信号已验证。
- 线缆、连接器、PoC 网络、ESD/EMC 器件满足目标车载环境。
- 故障现场有启动寄存器 dump 和故障后寄存器 dump 可对比。

## 与 MIPI CSI/DSI 的关系

FPD-Link/GMSL 通常不是替代 MIPI CSI/DSI，而是把短距离 MIPI 链路延伸到车载线束场景。

```text
MIPI CSI/DSI：芯片或板内短距离图像接口
FPD-Link/GMSL：线束上的远距离 SerDes 传输
```

排查时不要把两者混为一层。SerDes Link Lock、远端 I2C、MIPI streaming、SoC CSI 接收和 ISP 输出是连续但不同的层级。

## 延伸阅读

- `bus/fpd-link-gmsl.md`
- `bus/fpd-link-gmsl-practical.md`
- `bus/mipi-csi-dsi-deep-dive.md`
- `bus/display-interfaces.md`
- `basic/lvds.md`
