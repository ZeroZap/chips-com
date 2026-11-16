---
tags:
  - layer/guides
  - type/failure-cases
  - topic/troubleshooting
---

# Failure Cases

## 目标

本文收集典型通信故障案例，用“现象 -> 排查 -> 根因 -> 修复”的方式沉淀经验。

## I2C 高速偶发 NACK

现象：

```text
100 kHz 稳定，400 kHz 偶发 NACK
```

排查：

- 示波器观察 SCL/SDA 上升沿。
- 检查上拉电阻和挂载设备数量。
- 检查电平转换器型号。

根因：

```text
总线电容较大，上拉过弱，上升沿不满足 Fast-mode 时序。
```

修复：

- 将上拉从 10k 调整到 2.2k/4.7k。
- 降低速率。
- 减少总线电容或分段。

## SPI Flash Fast Read 数据偏移

现象：

```text
0x03 普通读正常，0x0B Fast Read 数据错位
```

排查：

- 逻辑分析仪检查 command/address/dummy。
- 对比 Flash 手册 dummy cycle 要求。

根因：

```text
Fast Read 少发送 8 个 dummy clocks。
```

修复：

- 按手册补足 dummy cycle。
- 不同频率下确认 dummy cycle 配置。

## RS485 最后字节丢失

现象：

```text
Modbus RTU 响应 CRC 偶发错误，最后字节异常
```

排查：

- 逻辑分析仪同时观察 UART TX 和 DE。
- 检查发送完成判断条件。

根因：

```text
软件等待 TXE 后关闭 DE，移位寄存器最后停止位未发完。
```

修复：

- 等待 UART TC 标志后再关闭 DE。

## CAN 单节点一直 ACK Error

现象：

```text
CAN 控制器发送失败，错误计数增加
```

排查：

- 检查总线上是否有其他正常节点。
- 用 CAN 分析仪接入并开启 ACK。

根因：

```text
总线上只有一个发送节点，没有任何节点应答 ACK。
```

修复：

- 接入第二个 CAN 节点或 CAN 分析仪。
- 确认波特率一致。

## USB CDC 枚举成功但无输出

现象：

```text
设备管理器显示虚拟串口，但串口工具无日志
```

排查：

- 检查 Host 是否打开端口。
- 检查 DTR 状态。
- 检查 CDC Bulk IN 是否发送。

根因：

```text
固件等待 DTR 后才输出，串口工具未拉起 DTR。
```

修复：

- 修改串口工具设置。
- 固件区分调试日志和 DTR 控制策略。

## Ethernet ping 不通但 Link 正常

现象：

```text
网口 Link LED 亮，ping 不通
```

排查：

- Wireshark 看 ARP。
- 检查 IP/Mask。
- 检查 MAC 地址是否重复。

根因：

```text
静态 IP 与 PC 不在同一网段。
```

修复：

- 修正 IP 和子网掩码。
- 或配置正确网关。

## MIPI 屏背光亮但黑屏

现象：

```text
背光亮，屏幕无图
```

排查：

- 检查 DSI 初始化命令。
- 检查 Sleep Out 和 Display On。
- 检查 Video Mode 时序。

根因：

```text
只打开了背光，Panel 未完成 DSI 初始化。
```

修复：

- 按屏厂初始化表发送完整命令。
- 确认延时满足手册。

## PCIe 枚举不到设备

现象：

```text
lspci 看不到 Endpoint
```

排查：

- 查看 LTSSM 状态。
- 检查 PERST# 和 REFCLK。
- 检查 Lane TX/RX 方向。

根因：

```text
PERST# 释放过早，Endpoint 电源尚未稳定。
```

修复：

- 调整复位时序。
- 确保 REFCLK 和电源稳定后释放 PERST#。

## FPD-Link/GMSL 多摄偶发掉线

现象：

```text
四路车载摄像头冷启动后都能出图，路试振动或高温一段时间后某一路偶发黑屏。
重新插拔线束或重启后恢复，实验室短线复现概率低。
```

排查：

- 读取 Deserializer 每路 `Link Lock`、`lock drop counter`、CRC/error counter。
- 对比正常样机和故障样机的 SerDes 寄存器 dump。
- 用短同轴线、目标长度线束和另一家线束做交叉验证。
- 测量 PoC 远端电压，重点看摄像头启动和图像亮度变化时的瞬态跌落。
- 将四路聚合临时降为单路或降低分辨率/帧率，观察掉线概率是否下降。
- 检查连接器屏蔽、端子压接、同轴弯折半径和车身接地点。

根因：

```text
目标线束和 PoC 滤波网络组合后链路裕量不足。
振动和温度变化导致连接器接触阻抗上升，远端供电瞬态叠加到高速链路，
Deserializer 记录 lock drop，表现为偶发黑屏。
```

修复：

- 按 SerDes 参考设计重新校核 PoC 电感、磁珠、电容和保护器件选型。
- 改善连接器压接和屏蔽接地，限制线束弯折半径。
- 调整 Deserializer equalizer 或启用自适应均衡，必要时降低链路速率。
- 在驱动中记录 lock drop counter、远端供电状态和 CSI error counter，便于现场闭环。
- 将短线、目标线束、高温、振动和多摄满带宽纳入回归测试。

## Ethernet TSN 延迟偶发尖峰

现象：

```text
Talker -> TSN Switch -> Listener 单跳测试中，实时 UDP 流平均延迟满足要求，
但每隔几十秒出现一次 2 ms 以上尖峰。关闭背景流后尖峰消失。
```

排查：

- 用 `ptp4l` 和 `pmc` 记录 gPTP offset，确认时间同步没有同时跳变。
- 用 Wireshark 抓包确认实时流 VLAN PCP 是否稳定为预期优先级。
- 用交换机统计查看实时队列和普通队列计数。
- 检查 Qbv Gate Control List 的窗口长度、Guard Band 和 Base Time。
- 增加满带宽背景流，比较 Qbv 开启前后的 p99/p999 延迟。
- 用 `ethtool -S` 查看 Talker 网卡队列丢包和硬件 offload 状态。

根因：

```text
实时流 VLAN PCP 正确，但交换机出口队列映射配置错误。
实时流进入了普通队列，Qbv 时间窗口没有保护该队列，背景大帧导致排队等待，
表现为平均延迟正常但尾延迟周期性尖峰。
```

修复：

- 修正交换机 ingress/egress PCP 到队列映射，确保实时流进入 Qbv 保护队列。
- 重新计算 Qbv 窗口、Guard Band 和最大帧长度预算。
- 在测试报告中记录 min、max、p99、p999 和丢包率，不只记录平均值。
- 把背景满载、Grandmaster 切换、链路恢复和配置重启纳入 TSN 回归测试。

## UDS 刷写 Transfer Data 超时

现象：

```text
0x10 会话切换、0x27 安全访问、0x31 擦除例程都正常，
0x34 Request Download 返回正响应，但 0x36 Transfer Data 传输数十个 block 后超时失败。
降低 CAN FD 数据速率或增大工具侧 block 间隔后成功率提高。
```

排查：

- 抓 CAN/ISO-TP 日志，确认 First Frame、Flow Control、Consecutive Frame 序号连续。
- 检查 ECU 返回 Flow Control 的 `BS` 和 `STmin`，确认诊断工具是否严格遵守。
- 区分 ISO-TP 超时、UDS P2/P2* 超时和 Bootloader Flash 写入失败。
- 记录每个 Transfer Data block 的序号、长度、发送时间和 ECU 响应时间。
- 在 Bootloader 中记录 Flash program 耗时、buffer 水位和擦写错误码。
- 临时降低 block 大小或增大 STmin，观察失败点是否后移。

根因：

```text
诊断工具忽略 ECU Flow Control 中的 STmin，连续高速发送 Consecutive Frame。
Bootloader 接收缓冲区被填满，同时 Flash 写入任务占用时间较长，导致 ISO-TP 重组超时。
UDS 层只看到 Transfer Data 超时，误判为刷写服务失败。
```

修复：

- 工具侧严格执行 ECU Flow Control 的 BS/STmin，不用固定高速发送策略覆盖 ECU 参数。
- Bootloader 将 ISO-TP 接收缓冲和 Flash 写入队列解耦，或按实际写入速度调整 Flow Control。
- Request Download 返回的最大块长度要匹配 RAM buffer 和 Flash program 能力。
- 日志中分开记录 ISO-TP 错误、UDS NRC、Flash driver 错误和电压条件。
- 回归测试覆盖不同 CAN/CAN FD 速率、不同 block size、低电压和断电恢复场景。

## PMBus 遥测读数异常误判过流

现象：

```text
BMC 页面显示某路电源输出电流瞬间超过 200 A，触发上层告警。
现场用电流钳和电源模块厂商工具确认实际电流约 18 A，电源未进入保护。
重启 BMC 后告警仍偶发出现。
```

排查：

- 用 SMBus/PMBus 原始读命令记录 `PAGE`、`READ_IOUT`、`STATUS_WORD` 和 `STATUS_IOUT`。
- 确认该设备 `READ_IOUT` 使用 Linear11、Linear16 还是 Direct Format。
- 对比 BMC 驱动换算值、原始 word、厂商工具显示值和外部电流钳读数。
- 检查多路 rail 轮询时是否每次读取前显式写入 `PAGE`。
- 检查 SMBus word 低字节在前是否被驱动误当作高字节在前。
- 读取 `STATUS_CML`，确认是否存在 PEC、非法命令或数据格式错误。

根因：

```text
BMC 驱动把 READ_IOUT 的 Linear11 原始 word 直接当作无符号整数换算，
同时多路轮询依赖全局 PAGE 状态，偶发读到上一轮 rail 的数据。
实际电源没有过流，是数据格式解析和 PAGE 管理错误导致的遥测误报。
```

修复：

- 按设备手册实现 Linear11 有符号 exponent/mantissa 解析。
- 所有 PMBus 通道访问都显式传入并写入 `PAGE`，不要依赖隐藏全局状态。
- 遥测日志同时保存 raw word、converted value、PAGE 和 status bits。
- 告警策略先检查 `STATUS_IOUT` 是否真实置位，再结合换算值和持续时间判断。
- 回归测试覆盖多 rail 轮询、PEC 开关、字节序、Linear11 负指数和厂商工具对比。

## USB DFU 升级后设备不启动

现象：

```text
设备可以进入 DFU 模式，Host 分块下载显示成功，USB 重新枚举后设备无业务功能。
再次上电后既不进入应用，也不自动回到 DFU，只能通过调试器重新烧录恢复。
```

排查：

- 读取 DFU 状态机日志，确认下载、写 Flash、校验和复位各阶段是否完成。
- 用调试器检查 Bootloader 区、Application 起始地址、向量表和栈顶地址。
- 对比镜像 header 中的 load address、image size、hardware version 和 CRC/hash。
- 检查 Host 分块大小是否和设备 Flash page/sector 擦写粒度匹配。
- 检查升级过程中是否错误擦除了 metadata、boot flag 或 Bootloader 保护区域。
- 断电重启后读取 metadata，确认是否处于 `READY_TO_BOOT`、`FAILED` 或未知状态。

根因：

```text
DFU Host 发送的是裸 bin，设备端没有校验镜像 load address 和向量表范围。
新固件按 0x08000000 链接，但 Bootloader 期望应用从 0x08008000 启动。
Bootloader 将错误地址写入 metadata 并直接跳转，导致启动异常且没有回退 DFU。
```

修复：

- 固件镜像必须携带 header，包含 magic、目标地址、长度、硬件版本、CRC/hash 和版本信息。
- Bootloader 校验向量表、栈地址范围、镜像长度和 CRC/hash 后才设置可启动标志。
- Bootloader 区域和恢复入口写保护，普通 DFU 不能擦写。
- 应用首次启动后写入确认标志；未确认时下次启动回退 DFU 或旧镜像。
- 量产日志记录设备序列号、镜像版本、写入地址、校验结果和失败原因。

## BLE 连接周期性断开

现象：

```text
手机与 BLE 设备可以连接，但每隔几十秒到几分钟断开一次。
断开时间不固定，设备日志显示 supervision timeout。
```

排查：

- 记录 connection interval、slave latency、supervision timeout 和 MTU。
- 检查设备是否在连接事件中睡眠过久，错过多个 anchor point。
- 检查 Wi-Fi/2.4 GHz 干扰、天线匹配和 TX power。
- 检查固件是否在长任务中关闭中断或阻塞协议栈。
- 用 BLE sniffer 看是否真的丢失空包，还是主机主动断开。

根因：

```text
设备把 supervision timeout 配得过短，同时在 Flash 擦写时长时间关中断，
连续错过多个连接事件，主机判定链路丢失并发起断开。
```

修复：

- 按应用场景设置 connection interval 和 supervision timeout，留足调度余量。
- Flash 擦写、射频校准等长任务放到连接间隔之外或使用后台任务。
- 监控连接事件丢失计数和 RSSI。
- 多环境测试 Wi-Fi 共存、金属遮挡和远距离。

## LoRaWAN 入网失败

现象：

```text
终端反复发送 Join Request，网关能看到上行，但始终没有 Join Accept。
```

排查：

- 核对 region、frequency plan、sub-band 和网关配置。
- 核对 DevEUI、JoinEUI/AppEUI、AppKey 和设备是否已注册。
- 检查网关是否收到上行、是否转发到 Network Server。
- 检查终端 SF/DR、TX power、天线和晶振频偏。
- 检查 Join Accept 接收窗口和终端收发切换时序。

根因：

```text
终端与网关使用了不同 sub-band，网关能看到部分上行但 Network Server 没有对应频点配置；
同时终端晶振频偏较大，Join Accept 落在接收窗口之外。
```

修复：

- 固定并记录 region/sub-band 配置。
- 校准晶振，验证不同 SF 下的频偏和接收窗口。
- 网关、Network Server、终端三侧日志关联 JoinEUI/DevEUI。
- 入网失败时按退避策略重试，避免占空比违规。

## IEC 60870-5-104 总召超时

现象：

```text
TCP 连接建立成功，主站发送总召，但从站没有返回完整数据或超时断开。
```

排查：

- 用 Wireshark 看 APCI 的 STARTDT、TESTFR、I/S 帧和序号。
- 核对端口 2404、链路地址、公共地址和 ASDU 类型。
- 检查传送原因 COT、信息对象地址和点表数量。
- 检查 K/W 窗口、t1/t2/t3 超时和未确认帧。
- 检查防火墙、NAT、TCP 分片和长连接保持。

根因：

```text
主站和从站的公共地址/点表不一致，从站返回的 ASDU 长度超过主站缓冲区；
主站未及时确认 I 帧，t1 超时后主动断开。
```

修复：

- 统一链路地址、公共地址、点表和 ASDU 类型。
- 核对 K/W 窗口和 t1/t2/t3，保证确认及时。
- 抓包保存 STARTDT、总召、ACT/CON 和断开前的 I 帧序号。
- 对点表规模和单帧长度做边界测试。

## DNP3 事件丢失

现象：

```text
主站轮询遥测正常，但开关变位/告警事件偶发丢失，SOE 时间不连续。
```

排查：

- 检查 outstation 事件缓冲区大小和溢出计数。
- 检查 class 0/1/2/3 轮询和 unsolicited response 配置。
- 检查事件确认（confirm）是否及时，是否重复请求。
- 检查对象 group/variation、点号和事件时间戳。
- 检查链路层重传、TCP 断链和时间同步。

根因：

```text
主站只轮询 class 0，未启用 class 1/2/3 或 unsolicited；
outstation 事件缓冲区满后覆盖最旧事件，导致变位丢失。
```

修复：

- 启用并区分 class 1/2/3，合理配置 unsolicited。
- 扩大事件缓冲区，监控溢出和丢弃计数。
- 保证 confirm 及时，断链后按事件序号补传。
- 统一时间同步和 SOE 时区/闰秒处理。

## CANopen SDO 超时

现象：

```text
CAN 总线上能看到心跳，但主站读写对象字典时 SDO 超时。
```

排查：

- 核对 node ID、SDO 请求/响应 COB-ID（0x600+node / 0x580+node）。
- 检查 index/subindex、数据类型和对象是否支持。
- 检查 SDO 分段传输的 toggle bit、长度和超时。
- 检查心跳、NMT 状态和节点是否处于 Operational。
- 检查波特率、终端和总线错误帧。

根因：

```text
主站使用了错误的 node ID 计算 COB-ID，且对象 index 大小端写反；
从站返回 abort code，但主站只按超时处理，没有解析 SDO abort。
```

修复：

- 统一 node ID 和 COB-ID 计算。
- 解析 SDO abort code 和对象字典类型。
- 对分段传输做 toggle/长度/超时测试。
- 记录 NMT 状态和心跳丢失。

## J1939 地址声明冲突

现象：

```text
J1939 网络偶发节点掉线，地址声明报文重复，部分 PGN 收不到。
```

排查：

- 抓取 Address Claim（PGN 60928）和 NAME。
- 检查源地址是否重复、NAME 优先级和地址仲裁。
- 检查 TP.CM/TP.DT 的 RTS/CTS/BAM 和包序号。
- 检查 250 k/500 k 波特率、终端和总线负载。
- 检查节点是否在地址冲突后重新声明。

根因：

```text
两个节点配置了相同源地址，NAME 优先级较低的一方没有正确让出地址；
同时大包 TP 传输的 CTS 窗口过小，导致多包数据超时。
```

修复：

- 统一地址分配和 NAME 规则，处理地址冲突。
- 调整 TP 窗口、超时和重传。
- 监控地址声明、TP 错误和总线负载。
- 对多节点、长报文和大负载做回归。

## Modbus TCP 寄存器错位

现象：

```text
Modbus TCP 能读到数据，但数值整体偏移或高低字颠倒，部分点位越界。
```

排查：

- 检查 MBAP 长度、transaction ID、unit ID 和 PDU 长度。
- 核对功能码、起始地址、寄存器数量和 0/1-based 地址差异。
- 检查 16/32 位数据的高低字/字节序。
- 检查 TCP 粘包/拆包和一次读取跨多个 PDU。
- 检查网关是否做了地址映射或缩放。

根因：

```text
点表使用 1-based 地址，设备使用 0-based 地址；
32 位浮点由两个寄存器组成，主站按错误字序拼接，导致数值偏移和越界。
```

修复：

- 明确地址基数和点表映射。
- 统一 32/64 位数据的字序和字节序。
- 按 MBAP 长度解析，不假设一次 TCP 包就是一个 PDU。
- 对边界地址、跨页读取和异常码做回归。

## EtherCAT 从站偶发掉线

现象：

```text
EtherCAT 网络运行一段时间后某个从站掉线，WKC 不稳定，主站报 AL Status 错误。
```

排查：

- 检查物理拓扑、网线、连接器和屏蔽。
- 读取从站 AL Status、AL Status Code 和 WKC。
- 检查 DC 同步、主站周期和从站处理时间。
- 检查 PDO 映射、ESI/EEPROM 和从站配置。
- 检查电源、接地和电机干扰。

根因：

```text
从站 DC 同步配置与主站周期不匹配，加上电机启停时地噪声导致偶发丢帧；
WKC 下降后主站未正确处理，从站进入错误状态。
```

修复：

- 统一 DC 模式和同步周期，留足处理余量。
- 改善屏蔽、接地和电源滤波。
- 监控 WKC、AL Status 和丢帧计数。
- 对拓扑变化、热插拔和电机启停做回归。
