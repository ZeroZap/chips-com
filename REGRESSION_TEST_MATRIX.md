# Regression Test Matrix

## 目标

本文把通信知识库中的调试经验转成可执行的回归测试矩阵，用于版本发布、硬件改版、协议栈升级、现场故障修复和量产抽测。

核心目标：

- 确认最小通信仍然可用。
- 覆盖参数边界和异常路径。
- 验证错误能被检测、记录和恢复。
- 保留波形、抓包、日志或寄存器 dump 作为证据。
- 避免“实验室通一次”替代系统级可靠性验证。

## 测试分层

每个协议族尽量覆盖以下层级：

| 层级 | 目的 | 证据 |
| --- | --- | --- |
| Bring-up | 验证硬件和最小通信 | ID、枚举、固定帧、Link 状态 |
| Parameter | 验证关键参数边界 | 速率、地址、模式、payload、超时 |
| Negative | 验证错误路径 | NACK、CRC、NRC、Bus Off、枚举失败 |
| Recovery | 验证恢复能力 | 重新初始化、重连、总线恢复、回滚 |
| Stress | 验证长稳和负载 | p99/p999、错误计数、温度、满载 |
| Production | 验证量产可测 | 自动化结果、序列号、治具日志 |

## 测试记录字段

每条回归用例建议记录：

```text
Test ID
Protocol
Topology
Hardware version
Firmware version
Tool version
Precondition
Steps
Expected result
Measured evidence
Pass / Fail
Failure layer
Owner
Regression trigger
```

`Measured evidence` 至少包含一种原始证据：波形、pcap、CAN trace、USB trace、寄存器 dump、系统日志、外部仪表读数或量产治具日志。

## 基础外设矩阵

| 协议 | Bring-up | Parameter | Negative | Recovery | Stress | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| GPIO | 输入输出翻转 | 上拉/下拉/中断边沿 | 悬空输入、抖动 | 去抖和中断清除 | 长时间边沿计数 | 逻辑波形、计数器 |
| UART | 固定字符串收发 | 波特率、8N1、DMA buffer | 错波特率、断线、溢出 | 重新打开串口 | 长时间日志流 | 逻辑分析仪、错误计数 |
| I2C | 扫描地址、读 ID | 100 kHz/400 kHz、Repeated START | NACK、总线被拉低、Clock Stretching | 9 clock 恢复、MUX reset | 多设备轮询 | 示波器上升沿、I2C trace |
| SPI | 读 JEDEC ID | Mode、SCK、dummy cycle | CS 抖动、MISO 延迟 | 重新初始化 Flash | 连续读写擦除 | 逻辑分析仪、示波器 |
| QSPI/OSPI | 读 ID、切换线宽 | dummy、XIP、DTR | 校验失败、模式回退 | 退出 XIP、重新训练 | 大块读写校验 | trace、CRC、性能数据 |

## 工业和车载矩阵

| 协议 | Bring-up | Parameter | Negative | Recovery | Stress | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| RS485/Modbus RTU | 读单寄存器 | 波特率、地址、功能码 | CRC 错、帧间隔错、地址错 | DE/RE 恢复、重试 | 多从站轮询 | UART/DE 波形、Modbus trace |
| CAN | 两节点固定 ID | 波特率、采样点、标准/扩展帧 | ACK Error、Bus Off、错误帧 | 自动恢复或手动恢复 | 高总线负载 | CAN trace、错误计数 |
| CANopen | 读 1000h/1018h | SDO/PDO、Heartbeat、NMT | PDO 映射错、Heartbeat 超时 | NMT reset、重连 | 电机状态机循环 | CANopen trace、对象字典 dump |
| J1939 | 地址声明、PGN 读取 | PGN/SPN、TP、多包 | 地址冲突、TP 超时 | 重新地址声明 | 高负载广播 | CAN trace、DBC 解码 |
| ISO-TP/UDS | 读 DID、安全访问 | BS/STmin、P2/P2*、block size | CF 序号错、NRC、超时 | 会话恢复、刷写回退 | 大镜像刷写 | CAN trace、UDS 日志、Flash 日志 |
| LIN | Break/Sync/ID | 调度表、checksum | 从节点不响应、checksum 错 | 主站重调度 | 长时间车身帧 | LIN trace、时序截图 |

## 工业以太网和网络矩阵

| 协议 | Bring-up | Parameter | Negative | Recovery | Stress | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Ethernet | Link、ARP、ping | MTU、双工、IP、MAC | IP 冲突、丢 ARP、PHY error | 断线重连、DHCP renew | TCP/UDP 长稳 | Wireshark、PHY 统计 |
| Modbus TCP | 读 Holding Register | Unit ID、事务 ID、并发连接 | 长度错、异常码、断连 | TCP 重连 | 多客户端轮询 | pcap、应用日志 |
| PROFINET | DCP 命名、周期 IO | GSDML、模块、诊断 | 名称错、AR/CR 失败 | PLC 重连、设备重启 | 周期 IO 长稳 | Wireshark、PLC 诊断 |
| EtherNet/IP | List Identity、Forward Open | EDS、Assembly、RPI | Assembly 错、连接超时 | 连接重建 | 隐式 IO 长稳 | pcap、PLC/Scanner 日志 |
| EtherCAT | 从站扫描、OP 状态 | PDO、DC、周期 | WKC 错、状态机失败 | 重新扫描、状态切换 | 多轴同步 | Master log、WKC、DC offset |
| TSN | gPTP 同步、单流 | VLAN PCP、Qbv、Qav、Qbu | 队列映射错、GM 切换 | 链路恢复、调度重载 | 背景满载 p99/p999 | pcap、PTP offset、队列统计 |
| MQTT | 连接 broker、发布订阅 | QoS、Keepalive、TLS | 断网、证书错、重复消息 | 自动重连、离线缓存 | 长连接和弱网 | broker log、客户端状态 |

## 主机外设和升级矩阵

| 协议 | Bring-up | Parameter | Negative | Recovery | Stress | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| USB | 枚举、读描述符 | VID/PID、Endpoint、配置 | 描述符错、STALL、断连 | 热插拔重枚举 | 长时间传输 | USB trace、dmesg |
| USB CDC/HID/MSC | 类功能验证 | packet size、polling interval | Host 不拉 DTR、短包 | 重新打开设备 | 大量收发 | USB trace、应用日志 |
| USB DFU | 进入 DFU、分块下载 | block size、manifest、CRC | 错镜像、断电、地址错 | 回退 DFU、A/B rollback | 多次升级 | DFU log、Flash dump、metadata |
| SDIO | 设备枚举、固件加载 | bus-width、clock、IRQ | DAT 线错、固件缺失 | 重新加载固件 | Wi-Fi 吞吐长稳 | dmesg、驱动统计 |
| PCIe | lspci、Link L0 | Gen、Width、BAR、MSI | PERST# 错、LTSSM 卡住 | 重新枚举、热复位 | DMA 长稳 | lspci、AER、DMA CRC |

## 图像和显示矩阵

| 协议 | Bring-up | Parameter | Negative | Recovery | Stress | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| MIPI CSI | 读 Sensor ID、streaming | Lane、VC、DT、RAW/YUV | MCLK 错、format 错、Lane 错 | Sensor reset、pipeline restart | 长时间采集 | CSI error、帧计数、图像 |
| MIPI DSI | 初始化屏、纯色图 | Timing、pixel format、command/video | Sleep Out 缺失、背光误判 | Panel reset、重新初始化 | 高低温闪屏 | DRM log、测试图、波形 |
| FPD-Link/GMSL | Deserializer ID、Link Lock | I2C alias、VC、PoC、线束 | lock drop、远端 I2C 不通 | 端口重连、降速 | 多摄满带宽、高温振动 | SerDes dump、PoC 波形、CSI error |
| HDMI | 5V、HPD、EDID | 分辨率、色深、TMDS/FRL | EDID 读不到、高分闪屏 | 热插拔、fallback mode | 多显示器兼容 | EDID、drm log、示波器 |
| eDP | AUX、DPCD、Link Training | Lane、link rate、panel timing | AUX 不通、training fail | 降速、panel reset | 长稳闪屏 | DPCD、training log、背光波形 |

## 电源管理矩阵

| 协议 | Bring-up | Parameter | Negative | Recovery | Stress | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SMBus | 地址和标准事务 | Read Word、Block Read、PEC | PEC 错、超时、Alert 未清 | 总线恢复、Alert 处理 | 多设备轮询 | SMBus trace、PEC 计算 |
| PMBus | STATUS_WORD、READ_VOUT/IOUT | PAGE、Linear11/16、Direct | PAGE 错、写保护、状态锁存 | CLEAR_FAULTS、重新读状态 | 多 rail 遥测长稳 | raw word、换算值、外部仪表 |

## 异常注入建议

异常注入要可控、可复现、可恢复。

| 注入类型 | 方法 | 目标 |
| --- | --- | --- |
| 断线 | 拔线、继电器、交换机端口 down | 验证断线检测和恢复 |
| 降压 | 可编程电源降低输入 | 验证电源边界和故障记录 |
| 错帧 | 工具发送 CRC/长度/序号错误 | 验证协议错误路径 |
| 高负载 | 背景流、总线负载、满帧发送 | 验证尾延迟和缓冲区 |
| 温度 | 高低温箱或热风枪 | 验证边界和漂移 |
| 重启 | MCU/SoC/交换机/PLC 重启 | 验证重连和状态恢复 |
| 断电 | 下载或写 Flash 中断电 | 验证回滚和防变砖 |

## 发布前最小门禁

每个版本发布前建议至少满足：

- 所有外部通信接口通过 Bring-up 测试。
- 高风险接口至少有一个 Negative 和 Recovery 用例。
- 固件升级链路完成断电恢复或失败回退验证。
- 网络和现场总线完成断线重连验证。
- 高速图像/显示链路完成长稳和高低温抽测。
- 所有新增故障修复都有对应回归用例。
- 所有失败用例能定位到明确层级，而不是只记录“通信失败”。

## 与其他文档的关系

- `MEASUREMENT_EXAMPLES.md`：说明如何采集证据。
- `FAILURE_CASES.md`：记录典型故障闭环。
- `TROUBLESHOOTING_QUICKREF.md`：给现场快速定位方向。
- `PRODUCTION_TEST.md`：定义量产工位测试策略。
- `RELIABILITY_GUIDE.md`：定义长期可靠性和恢复策略。
- `REVIEW_CHECKLIST.md`：定义设计评审入口。
- `LABS.md`：把矩阵拆成可学习的实验路线。
