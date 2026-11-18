---
tags:
  - layer/guides
  - type/measurement
  - topic/troubleshooting
---

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

| 字段         | 说明                      |
| ------------ | ------------------------- |
| Bus speed    | 100 kHz / 400 kHz / 1 MHz |
| Pull-up      | 上拉阻值和电压            |
| Devices      | 挂载设备数量和线长        |
| Rise time    | 30% 到 70% 上升时间       |
| Low level    | 低电平是否足够低          |
| NACK address | 出现 NACK 的地址和寄存器  |

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

| 字段          | 说明                       |
| ------------- | -------------------------- |
| Command       | 0x03 / 0x0B / Quad Read 等 |
| Address       | 读取地址                   |
| Dummy clocks  | 实际 dummy clock 数        |
| SPI mode      | CPOL/CPHA                  |
| SCK frequency | 实际时钟频率               |
| First bytes   | 返回前 16 字节             |

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

| 字段        | 说明                       |
| ----------- | -------------------------- |
| Request ID  | Tester 到 ECU CAN ID       |
| Response ID | ECU 到 Tester CAN ID       |
| Addressing  | Normal / Extended / Mixed  |
| BS/STmin    | ECU 返回的流控参数         |
| Block size  | UDS 0x36 每块数据长度      |
| Flash time  | ECU 写 Flash 最大耗时      |
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

| 字段           | 说明                         |
| -------------- | ---------------------------- |
| Command        | PMBus 命令码                 |
| Raw word       | SMBus word 原始值            |
| Format         | Linear11 / Linear16 / Direct |
| PAGE           | 当前 rail                    |
| PEC            | 启用或关闭                   |
| Status bits    | 故障状态位                   |
| External meter | 外部仪表读数                 |

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

| 字段          | 说明              |
| ------------- | ----------------- |
| Image version | 固件版本          |
| Load address  | 镜像目标地址      |
| Image size    | 镜像长度          |
| CRC/hash      | 完整性校验        |
| Flash range   | 实际写入范围      |
| Boot flag     | metadata 启动标志 |
| Confirm flag  | 应用启动确认标志  |

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

| 字段        | 说明                    |
| ----------- | ----------------------- |
| Cable       | 线束型号、长度、供应商  |
| Port        | Deserializer 端口       |
| Link status | lock 和 drop counter    |
| PoC voltage | 启动和满载瞬态          |
| Sensor mode | 分辨率、帧率、bit depth |
| CSI errors  | SoC 接收错误            |
| Temperature | 环境和芯片温度          |

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

## BLE 连接与吞吐测量

目标：区分连接参数、射频干扰、协议栈阻塞和主机行为导致的断连/低吞吐。

工具：

- BLE Sniffer（nRF Sniffer / Ellisys / Ubertooth）。
- nRF Connect。
- 频谱仪/近场探头，视需要。
- 设备日志和连接事件计数。

抓取内容：

- Advertising interval、TX power。
- Connection interval、slave latency、supervision timeout。
- MTU、GATT 读写/通知长度。
- 连接事件丢失、RSSI、重连次数。
- Wi-Fi/2.4 GHz 共存条件。

判定：

- Sniffer 能看到空包但设备没响应，优先查协议栈/中断阻塞。
- 主机主动断开还是 supervision timeout，处理方向不同。
- 吞吐随 connection interval/MTU 变化，说明参数或调度是瓶颈。

## LoRaWAN 入网与链路测量

目标：定位 Join 失败、上行丢失、ADR 不收敛和占空比问题。

工具：

- LoRa 网关日志。
- Network Server 日志。
- 终端串口日志。
- 频谱仪/天线分析仪。

抓取内容：

- region/sub-band、频点和占空比。
- Join Request/Join Accept 时间。
- SF、BW、TX power、ADR。
- RSSI、SNR、CRC 状态。
- 网关/NS/终端三侧 DevEUI/JoinEUI。

判定：

- 网关有上行但 NS 无记录，优先查网关转发和频点配置。
- Join Accept 错过接收窗口，查晶振频偏和收发切换。
- SNR 正常但丢包，查占空比、重试和 NS 策略。

## CAN FD 眼图与错误测量

目标：评估 CAN FD 数据段速率、收发器、终端和拓扑余量。

工具：

- 差分探头/示波器。
- CAN FD 分析仪。
- 眼图/模板分析（如支持）。

抓取内容：

- 仲裁段/数据段波特率、采样点、SJW。
- CANH/CANL 差分摆幅、共模电压。
- 数据段边沿、过冲、振铃和眼图。
- TEC/REC、错误帧、Bus Off。
- 终端电阻和总线长度。

判定：

- 仲裁段正常、数据段误码，优先查收发器环路延迟、采样点和线长。
- 眼图闭合但低速正常，说明高速余量不足。
- 终端/共模异常会同时影响经典 CAN 和 CAN FD。

## Modbus TCP 抓包测量

目标：定位寄存器错位、异常码、粘包/拆包和超时。

工具：

- Wireshark/tshark。
- Modbus Poll/QModMaster。
- 设备应用日志。

抓取内容：

- MBAP transaction ID、length、unit ID。
- Function code、起始地址、数量。
- 异常码和响应时间。
- TCP 重传、断连、并发连接。
- 点表地址基数和字序。

判定：

- 请求/响应长度与 MBAP 不一致，查 PDU 解析。
- 地址整体偏移，查 0/1-based 和网关映射。
- 32 位值异常，查寄存器字序/字节序。

## IEC 60870-5-104 抓包测量

目标：定位链路建立、总召、遥控和超时问题。

工具：

- Wireshark（104 解码）。
- 104 客户端/模拟器。
- 主站/从站日志。

抓取内容：

- TCP 连接、STARTDT/STOPDT/TESTFR。
- I/S/U 帧和发送/接收序号。
- ASDU 类型、COT、公共地址、信息对象地址。
- K/W 窗口、t1/t2/t3。
- 总召/遥控的 ACT/CON/TERM。

判定：

- 连接建立但无数据，先看 STARTDT 和公共地址。
- 总召超时，查点表规模、ASDU 长度和 I 帧确认。
- 遥控失败，查选择/执行、COT 和权限。

## DNP3 事件与时间同步测量

目标：定位事件丢失、确认丢失和时间戳异常。

工具：

- Wireshark（DNP3 解码）。
- DNP3 主站/outstation 日志。
- 点表和事件缓冲统计。

抓取内容：

- Integrity Poll、Class 1/2/3 Poll。
- Unsolicited Response、confirm。
- 对象 group/variation、点号、事件时间。
- 事件缓冲溢出/丢弃计数。
- 链路层重传和时间同步。

判定：

- 只轮询 Class 0 会漏事件。
- confirm 不及时会导致重传/重复事件。
- 时间戳跳变，查对时和时区/闰秒处理。

## EtherCAT WKC 与 DC 测量

目标：定位从站掉线、WKC 异常和 DC 同步问题。

工具：

- TwinCAT/SOEM/IgH Master 日志。
- Wireshark（EtherCAT 解码）。
- 从站 AL Status/EEPROM/ESI。
- 示波器/网线测试仪。

抓取内容：

- 拓扑和端口顺序。
- WKC、AL Status、AL Status Code。
- DC offset、同步周期、主站周期。
- PDO 映射和从站处理时间。
- 网线/连接器/电源/地。

判定：

- WKC 下降但链路在，查从站处理、PDO 和 DC。
- 偶发掉线优先查拓扑、网线、连接器和电机干扰。
- DC offset 收敛差，查主站周期、从站处理和参考时钟。

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

- [[reference/TOOLS|TOOLS]]
- [[guides/troubleshooting/WAVEFORM_GUIDE|WAVEFORM_GUIDE]]
- [[guides/troubleshooting/FAILURE_CASES|FAILURE_CASES]]
- [[guides/troubleshooting/TROUBLESHOOTING_QUICKREF|TROUBLESHOOTING_QUICKREF]]
- [[guides/learning/LABS|LABS]]
- [[guides/learning/EXPERIMENT_TEMPLATE|EXPERIMENT_TEMPLATE]]
