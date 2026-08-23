# Measurement Examples

## 目标

本文把通信调试中的“测量样例”标准化，帮助把现象、工具、观测点、阈值、日志和结论记录成可复查的证据链。

适用场景：

- 现场故障复现。
- 新板 bring-up。
- 协议栈联调。
- 量产测试边界确认。
- 回归测试用例沉淀。

## 通用记录模板

每次测量至少记录：

```text
目标：验证什么假设
拓扑：设备、线缆、供电、版本
工具：示波器、逻辑分析仪、CAN 分析仪、Wireshark、系统日志
触发：上电、发包、插拔、降压、满载、温度、振动
采样：采样率、带宽、探头、抓包点、时间窗口
原始数据：波形截图、pcap、trace、寄存器 dump、日志
判定：正常范围、异常条件、对比样机
结论：根因、修复、待验证项
```

不要只保存结论。没有原始波形、抓包或日志的结论很难复查。

## 示波器测 I2C 上升沿

目标：验证 I2C Fast-mode 偶发 NACK 是否由上升沿过慢导致。

拓扑：

```text
MCU I2C Master -> Sensor / EEPROM / MUX
```

测量点：

- SCL。
- SDA。
- 目标器件 VCC。
- GND 参考点尽量靠近目标器件。

触发建议：

- 触发在 START 条件。
- 或触发在 NACK 后的 SDA 高电平。

记录字段：

| 字段 | 说明 |
| --- | --- |
| Bus speed | 100 kHz / 400 kHz / 1 MHz |
| Pull-up | 上拉阻值和电压 |
| Devices | 挂载设备数量和线长 |
| Rise time | 30% 到 70% 上升时间 |
| Low level | 低电平是否足够低 |
| NACK address | 出现 NACK 的地址和寄存器 |

判定：

- 上升沿慢时，先降低速率或减小上拉验证方向。
- 逻辑分析仪能解码不代表边沿满足时序。
- 如果 SCL/SDA 空闲不是高电平，优先查短路、设备挂死或电平域。

## 逻辑分析仪测 SPI Flash Fast Read

目标：验证 Fast Read 数据错位是否由 dummy cycle 或 SPI Mode 错误导致。

测量点：

- CS。
- SCK。
- MOSI。
- MISO。
- WP/HOLD，视封装和模式而定。

触发建议：

```text
CS falling edge
```

记录字段：

| 字段 | 说明 |
| --- | --- |
| Command | 0x03 / 0x0B / Quad Read 等 |
| Address | 读取地址 |
| Dummy clocks | 实际 dummy clock 数 |
| SPI mode | CPOL/CPHA |
| SCK frequency | 实际时钟频率 |
| First bytes | 返回前 16 字节 |

判定：

- 普通读正常、Fast Read 错位时优先查 dummy cycle。
- 低速正常、高速失败时要用示波器确认 MISO 延迟和振铃。
- CS 中途抖动会破坏事务边界。

## CAN / ISO-TP / UDS 刷写测量

目标：定位 UDS Transfer Data 超时是 CAN、ISO-TP、UDS 还是 Bootloader Flash 写入问题。

工具：

- CAN 分析仪。
- 诊断工具日志。
- ECU Bootloader 日志。
- 电源记录，视故障是否和电压相关。

抓取内容：

- CAN ID。
- DLC。
- Single Frame / First Frame / Flow Control / Consecutive Frame。
- Flow Control `BS` 和 `STmin`。
- Consecutive Frame sequence number。
- UDS SID、NRC、P2/P2*。
- Transfer Data block sequence counter。

记录字段：

| 字段 | 说明 |
| --- | --- |
| Request ID | Tester 到 ECU CAN ID |
| Response ID | ECU 到 Tester CAN ID |
| Addressing | Normal / Extended / Mixed |
| BS/STmin | ECU 返回的流控参数 |
| Block size | UDS 0x36 每块数据长度 |
| Flash time | ECU 写 Flash 最大耗时 |
| Error layer | CAN / ISO-TP / UDS / Flash |

判定：

- FF 后无 CF，先查 Flow Control 和 ID。
- CF 序号跳变，先查丢帧、工具发送节奏和总线负载。
- UDS 0x78 不是错误本身，而是长任务仍在进行。
- Flash 写入慢时，应通过 Flow Control 限速或分块队列解耦。

## PMBus 遥测测量

目标：确认电源遥测异常是硬件真实故障，还是数据格式、PAGE、PEC 或字节序错误。

工具：

- BMC 日志。
- SMBus/PMBus 原始读写工具。
- 厂商 GUI 或评估板工具。
- 万用表、电流钳或电子负载。

抓取内容：

- `PAGE`。
- `STATUS_BYTE`。
- `STATUS_WORD`。
- `READ_VIN`。
- `READ_VOUT`。
- `READ_IOUT`。
- `STATUS_CML`。
- raw word 和换算值。

记录字段：

| 字段 | 说明 |
| --- | --- |
| Command | PMBus 命令码 |
| Raw word | SMBus word 原始值 |
| Format | Linear11 / Linear16 / Direct |
| PAGE | 当前 rail |
| PEC | 启用或关闭 |
| Status bits | 故障状态位 |
| External meter | 外部仪表读数 |

判定：

- `READ_IOUT` 异常但 `STATUS_IOUT` 未置位，优先查换算和 PAGE。
- Linear11 exponent 和 mantissa 都可能是有符号数。
- 多 rail 轮询不能依赖隐藏的全局 PAGE 状态。
- 清除状态前先保存状态寄存器，否则会丢失根因证据。

## Ethernet / TSN 延迟测量

目标：验证实时流延迟尖峰是否由时间同步、队列映射、Qbv 调度或背景流分类导致。

工具：

- Wireshark。
- `ptp4l`。
- `pmc`。
- `ethtool -S`。
- 交换机统计和配置导出。
- 硬件时间戳，优先使用。

抓取内容：

- PTP / gPTP 报文。
- VLAN tag 和 PCP。
- 实时流周期。
- 背景流吞吐。
- 队列计数。
- Qbv Gate Control List。
- min、max、p99、p999 和丢包率。

Wireshark 过滤示例：

```text
ptp || eth.type == 0x88f7
vlan && udp.port == <real-time-port>
eth.addr == <talker-mac>
```

判定：

- 平均延迟合格不代表 TSN 合格。
- gPTP offset 不稳时不要先调 Qbv。
- PCP 正确不代表交换机队列映射正确。
- 背景流满载是必要测试条件，不是额外压力测试。

## USB DFU 升级测量

目标：确认 DFU 下载成功后无法启动是 USB 传输、Flash 写入、镜像格式、metadata 还是 Bootloader 跳转问题。

工具：

- DFU Host 工具日志。
- USB 抓包。
- 设备串口或 RTT 日志。
- 调试器。
- Flash dump。

抓取内容：

- DFU descriptor。
- download block number。
- getstatus 返回状态。
- manifestation 阶段。
- reset 原因。
- 镜像 header。
- metadata。
- 应用向量表。

记录字段：

| 字段 | 说明 |
| --- | --- |
| Image version | 固件版本 |
| Load address | 镜像目标地址 |
| Image size | 镜像长度 |
| CRC/hash | 完整性校验 |
| Flash range | 实际写入范围 |
| Boot flag | metadata 启动标志 |
| Confirm flag | 应用启动确认标志 |

判定：

- USB 下载成功不代表镜像可启动。
- 裸 bin 缺少 load address 和硬件版本信息时风险高。
- Bootloader 必须先校验向量表和镜像完整性再跳转。
- 没有应用确认和失败回退时，升级风险不可控。

## FPD-Link / GMSL 链路测量

目标：定位车载 SerDes 偶发黑屏是链路、PoC、远端 I2C、MIPI 桥接还是 SoC CSI 接收问题。

工具：

- SerDes 寄存器 dump 工具。
- 示波器。
- 电源记录仪。
- SoC CSI 错误计数。
- 图像采集日志。

抓取内容：

- Link Lock。
- Lock drop counter。
- CRC/error counter。
- Back channel error。
- 远端 Serializer ID。
- Sensor ID。
- PoC 远端电压。
- CSI input/output status。
- VC/DT 映射。

记录字段：

| 字段 | 说明 |
| --- | --- |
| Cable | 线束型号、长度、供应商 |
| Port | Deserializer 端口 |
| Link status | lock 和 drop counter |
| PoC voltage | 启动和满载瞬态 |
| Sensor mode | 分辨率、帧率、bit depth |
| CSI errors | SoC 接收错误 |
| Temperature | 环境和芯片温度 |

判定：

- Deserializer 可访问不代表远端链路正常。
- Link Lock 不代表 Sensor streaming 正常。
- 短线正常、长线异常时要看线束损耗、连接器和 equalizer。
- 多摄异常要同时检查带宽、VC、I2C alias 和同步。

## HDMI / eDP 显示测量

目标：定位黑屏、闪屏、花屏是电源、侧带通道、高速链路、显示时序还是背光问题。

工具：

- 示波器。
- `edid-decode`。
- DRM/KMS debugfs。
- `modetest`。
- 显示测试图。
- 协议分析仪，视项目需要。

抓取内容：

- HDMI 5V、HPD、DDC。
- EDID。
- eDP AUX。
- DPCD。
- Link Training 状态。
- Lane count 和 link rate。
- Panel power、reset、backlight EN/PWM。
- 显示时序和像素格式。

判定：

- 背光亮不代表视频链路正常。
- EDID 能读到不代表高分辨率模式稳定。
- eDP AUX 不通时不要先调 Main Link。
- 低分辨率正常、高分辨率闪屏通常是链路裕量或 PHY 参数问题。

## 测量报告最小结构

建议每个案例最终沉淀为：

```markdown
## 案例标题

现象：

复现条件：

拓扑和版本：

测量工具：

关键证据：

对比实验：

根因：

修复：

回归测试：
```

关键证据至少包含一个原始数据来源，例如波形、pcap、trace、寄存器 dump、系统日志或外部仪表读数。

## 延伸阅读

- `TOOLS.md`
- `WAVEFORM_GUIDE.md`
- `FAILURE_CASES.md`
- `TROUBLESHOOTING_QUICKREF.md`
- `LABS.md`
- `EXPERIMENT_TEMPLATE.md`
