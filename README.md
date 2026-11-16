# Chips Communication Knowledge Base

这是一个面向芯片间通信的知识库，用于整理从基础外设接口到成熟总线协议的通信体系。

## Obsidian 知识库

本仓库根目录可直接作为 [Obsidian](https://obsidian.md/) Vault 打开（`Open folder as vault` → 选择仓库根目录）。

- 图形导航：[Navigation.canvas](Navigation.canvas)
- 文字仪表盘：[Home.md](Home.md)
- 完整索引：[INDEX.md](INDEX.md)

`.obsidian/` 已包含推荐配置：默认使用 Wikilink、启用 Canvas / 图谱 / 大纲等核心插件，并在搜索与图谱中排除 `_Inbox/` 与 `_System/`。

`_Inbox/` 是候选素材队列，处理流程见 `_Inbox/README.md`，可用 `python scripts/inbox_status.py` 查看积压。`_System/` 是本地自动化运行日志，已加入 `.gitignore`，不再入库。

## 分类原则

通信内容按抽象层级划分：

1. `basic/`：基础通信接口与电气/时序机制。
2. `bus/`：建立在基础接口之上的成熟总线、协议或网络体系，按领域分目录。
3. `guides/`：学习路径、选型、排障与工程质量等跨协议指南。
4. `reference/`：术语、缩写、工具与文档模板。

`basic` 关注“芯片如何通过某种外设接口收发数据”，`bus` 关注“多个设备如何通过协议规则组织通信”。

## 目录结构

```text
chips-com/
├── Home.md                     # Obsidian 仪表盘
├── Navigation.canvas           # Obsidian 图形导航
├── README.md
├── INDEX.md
├── basic/                      # 基础接口（扁平）
│   ├── README.md
│   ├── uart-*.md
│   ├── i2c-*.md
│   ├── spi-*.md
│   └── can-*.md
├── bus/
│   ├── README.md
│   ├── automotive/             # CAN 家族、J1939、ISO-TP、UDS、OBD、LIN
│   ├── industrial/             # Modbus、PROFI*、EtherCAT、EtherNet/IP、TSN、OPC UA、MQTT
│   ├── power-rtu/              # IEC 101/104、DNP3、IEC 61850、SL/SZY/HJ、DL/T 645、CJ/T 188、BACnet
│   ├── wireless-iot/           # BLE、ZigBee、LoRa、Matter、Thread、LTE IoT、卫星、PLB、应急
│   ├── usb/
│   ├── display/                # HDMI/eDP、FPD-Link/GMSL、MIPI
│   └── onboard/                # I3C、SMBus/PMBus、SDIO、1-Wire、PCIe
├── guides/
│   ├── learning/               # 学习路径、选型、场景与实验
│   ├── troubleshooting/        # 排障、波形、测量与故障案例
│   └── engineering/            # 量产、回归、可靠性与通信治理
├── reference/                  # 术语、缩写、工具与模板
├── _Inbox/                     # 待处理候选（Obsidian 排除）
└── _System/                    # 自动扫描报告（Obsidian 排除）
```

## 文档模板

每个协议或接口文档建议包含以下部分：

```markdown
# 名称

## 定位

说明它解决什么通信问题，常见于哪些芯片或系统。

## 基本概念

说明主从关系、拓扑、信号线、时钟、帧结构、地址、仲裁等核心概念。

## 硬件连接

说明引脚、上拉/下拉、终端电阻、电平转换、隔离、线缆长度等硬件注意点。

## 通信流程

说明初始化、发送、接收、应答、错误处理等典型流程。

## 优点与限制

说明速度、距离、成本、复杂度、实时性、抗干扰等取舍。

## 典型应用

列出传感器、存储器、电机控制、工业采集、板间通信等应用场景。

## 与相关协议对比

说明它和相近接口或总线的区别，例如 SPI vs I2C、UART vs RS485、CAN vs Modbus。
```

## 学习路径

建议从基础接口开始，再进入总线协议：

1. `GPIO`：理解数字电平、输入输出、边沿、中断。
2. `UART`：理解异步串口、波特率、帧格式。
3. `I2C`：理解同步串行、地址、开漏、上拉、多设备挂载。
4. `SPI`：理解高速同步串行、片选、模式、全双工。
5. `RS485/CAN PHY`：理解差分信号、终端匹配、长距离抗干扰。
6. `Modbus/CAN/USB/Ethernet`：理解成熟协议如何定义设备、帧、错误处理和网络行为。

完整的阶段化学习安排见 [guides/learning/LEARNING_PLAN.md](guides/learning/LEARNING_PLAN.md)。

跨协议排障方法见 [guides/troubleshooting/DEBUG_PLAYBOOK.md](guides/troubleshooting/DEBUG_PLAYBOOK.md)。

协议选型矩阵见 [guides/learning/PROTOCOL_SELECTION.md](guides/learning/PROTOCOL_SELECTION.md)。

术语表见 [reference/GLOSSARY.md](reference/GLOSSARY.md)，缩写表见 [reference/ACRONYMS.md](reference/ACRONYMS.md)，调试工具指南见 [reference/TOOLS.md](reference/TOOLS.md)，分层图谱见 [LAYERED_MAP.md](LAYERED_MAP.md)。

应用场景选型见 [guides/learning/APPLICATION_SCENARIOS.md](guides/learning/APPLICATION_SCENARIOS.md)，典型设备接口参考见 [guides/learning/DEVICE_EXAMPLES.md](guides/learning/DEVICE_EXAMPLES.md)。

文档模板见 [reference/DOC_TEMPLATES.md](reference/DOC_TEMPLATES.md)，协议对照表见 [guides/learning/PROTOCOL_COMPARISON.md](guides/learning/PROTOCOL_COMPARISON.md)，故障速查见 [guides/troubleshooting/TROUBLESHOOTING_QUICKREF.md](guides/troubleshooting/TROUBLESHOOTING_QUICKREF.md)，实验路线见 [guides/learning/LABS.md](guides/learning/LABS.md)。

完整索引见 [INDEX.md](INDEX.md)，按目标阅读见 [guides/learning/READING_PATHS.md](guides/learning/READING_PATHS.md)，新增内容评审见 [REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md)，贡献规范见 [CONTRIBUTING.md](CONTRIBUTING.md)。

当前覆盖范围和后续扩展方向见 [COVERAGE.md](COVERAGE.md)。

原理图检查见 [guides/troubleshooting/SCHEMATIC_CHECKLISTS.md](guides/troubleshooting/SCHEMATIC_CHECKLISTS.md)，驱动状态机模式见 [guides/troubleshooting/DRIVER_PATTERNS.md](guides/troubleshooting/DRIVER_PATTERNS.md)，故障案例见 [guides/troubleshooting/FAILURE_CASES.md](guides/troubleshooting/FAILURE_CASES.md)，波形观察见 [guides/troubleshooting/WAVEFORM_GUIDE.md](guides/troubleshooting/WAVEFORM_GUIDE.md)，测量样例见 [guides/troubleshooting/MEASUREMENT_EXAMPLES.md](guides/troubleshooting/MEASUREMENT_EXAMPLES.md)。

实验记录模板见 [guides/learning/EXPERIMENT_TEMPLATE.md](guides/learning/EXPERIMENT_TEMPLATE.md)，接口参数速查见 [guides/learning/PARAMETER_CHEATSHEET.md](guides/learning/PARAMETER_CHEATSHEET.md)，量产测试策略见 [guides/engineering/PRODUCTION_TEST.md](guides/engineering/PRODUCTION_TEST.md)，可靠性设计见 [guides/engineering/RELIABILITY_GUIDE.md](guides/engineering/RELIABILITY_GUIDE.md)，回归测试矩阵见 [guides/engineering/REGRESSION_TEST_MATRIX.md](guides/engineering/REGRESSION_TEST_MATRIX.md)，自动化测试治具见 [guides/engineering/AUTOMATED_TEST_HARNESS.md](guides/engineering/AUTOMATED_TEST_HARNESS.md)，通信可观测性见 [guides/engineering/COMMUNICATION_OBSERVABILITY.md](guides/engineering/COMMUNICATION_OBSERVABILITY.md)，发布质量门禁见 [guides/engineering/COMMUNICATION_QUALITY_GATE.md](guides/engineering/COMMUNICATION_QUALITY_GATE.md)，现场诊断运行手册见 [guides/troubleshooting/FIELD_DIAGNOSTIC_RUNBOOK.md](guides/troubleshooting/FIELD_DIAGNOSTIC_RUNBOOK.md)，通信追踪矩阵见 [guides/engineering/COMMUNICATION_TRACEABILITY.md](guides/engineering/COMMUNICATION_TRACEABILITY.md)，通信安全与失效安全见 [guides/engineering/COMMUNICATION_SECURITY_SAFETY.md](guides/engineering/COMMUNICATION_SECURITY_SAFETY.md)。

## 实战深入路径

完成基础概念后，按以下顺序进入工程调试文档：

1. [basic/uart-practical.md](basic/uart-practical.md)：UART 接线、参数、乱码和字节流分帧。
2. [basic/uart-deep-dive.md](basic/uart-deep-dive.md)：UART 波特率误差、过采样、DMA、硬件流控和量产排障。
3. [basic/i2c-practical.md](basic/i2c-practical.md)：I2C 上拉、地址扫描、寄存器读写和总线恢复。
4. [basic/i2c-deep-dive.md](basic/i2c-deep-dive.md)：I2C 上拉/电容、地址、Clock Stretching、总线恢复、MUX 和器件特性。
5. [basic/spi-practical.md](basic/spi-practical.md)：SPI Mode、片选、dummy byte 和多设备共享。
6. [basic/spi-deep-dive.md](basic/spi-deep-dive.md)：SPI 采样模式、CS 边界、dummy cycle、Flash 命令、高速信号和 QSPI/OSPI。
7. [bus/industrial/rs485-modbus-rtu-practical.md](bus/industrial/rs485-modbus-rtu-practical.md)：RS485 方向控制、终端电阻、Modbus RTU 帧和 CRC。
8. [bus/industrial/rs485-modbus-rtu-deep-dive.md](bus/industrial/rs485-modbus-rtu-deep-dive.md)：RS485 半双工、隔离防护、帧间隔、寄存器偏移、主站轮询和现场排障。
9. [bus/automotive/canopen-practical.md](bus/automotive/canopen-practical.md)：CAN 物理层、CANopen SDO/PDO/NMT 和电机调试入口。
10. [bus/automotive/canopen-deep-dive.md](bus/automotive/canopen-deep-dive.md)：CAN 位时序、仲裁、错误状态、CANopen PDO/SDO/NMT 和 CiA 402。
11. [bus/onboard/i3c-topic.md](bus/onboard/i3c-topic.md)：I3C 动态地址、CCC、IBI 和 I2C 混挂边界。
12. [bus/onboard/i3c-deep-dive.md](bus/onboard/i3c-deep-dive.md)：I3C 动态地址、CCC、IBI、Hot-Join、SDR/HDR、混合总线和驱动模型。
13. [bus/onboard/smbus-pmbus-practical.md](bus/onboard/smbus-pmbus-practical.md)：SMBus 事务、PEC、Alert、PMBus 命令、Linear 格式、PAGE 和故障状态。
14. [bus/usb/usb-practical.md](bus/usb/usb-practical.md)：USB Host/Device、枚举、描述符、Endpoint、CDC/HID/MSC 和 Type-C 基础。
15. [bus/industrial/ethernet-deep-dive.md](bus/industrial/ethernet-deep-dive.md)：Ethernet MAC/PHY、RMII/RGMII、MDIO、帧、ARP、TCP/UDP 和 Wireshark 排障。
16. [bus/industrial/ethernet-modbus-tcp-practical.md](bus/industrial/ethernet-modbus-tcp-practical.md)：Ethernet 链路、TCP 字节流和 Modbus TCP MBAP。
17. [bus/display/mipi-csi-dsi-debug.md](bus/display/mipi-csi-dsi-debug.md)：MIPI CSI/DSI 电源、I2C 初始化、Lane、像素格式和黑屏/无图定位。
18. [bus/display/mipi-csi-dsi-deep-dive.md](bus/display/mipi-csi-dsi-deep-dive.md)：MIPI D-PHY、CSI/DSI 初始化、RAW/YUV/RGB、显示时序和图像链路排障。
19. [bus/onboard/pcie-practical.md](bus/onboard/pcie-practical.md)：PCIe Root Complex/Endpoint、Lane、配置空间、BAR、MSI 和 DMA。
20. [bus/onboard/sdio-practical.md](bus/onboard/sdio-practical.md)：SDIO CLK/CMD/DAT、Wi-Fi 模块、固件、设备树和枚举排障。
21. [bus/onboard/one-wire-practical.md](bus/onboard/one-wire-practical.md)：1-Wire 上拉、时序、ROM ID、DS18B20 和寄生供电。
22. [bus/automotive/lin-practical.md](bus/automotive/lin-practical.md)：LIN 主从调度、Break/Sync/ID/Checksum 和车身低速节点。
23. [bus/industrial/ethercat-deep-dive.md](bus/industrial/ethercat-deep-dive.md)：EtherCAT 主从、ESC、On-the-fly、PDO、Mailbox、DC 和 WKC。
24. [bus/industrial/industrial-ethernet-comparison.md](bus/industrial/industrial-ethernet-comparison.md)：Modbus TCP、PROFINET、EtherNet/IP 和 EtherCAT 选型对比。
25. [bus/usb/usb-deep-dive.md](bus/usb/usb-deep-dive.md)：USB 标准请求、描述符层级、复合设备、类协议和枚举排障。
26. [bus/industrial/modbus-tcp-deep-dive.md](bus/industrial/modbus-tcp-deep-dive.md)：Modbus TCP MBAP、事务 ID、Unit ID、并发连接和网关转换。
27. [bus/industrial/profinet.md](bus/industrial/profinet.md)：PROFINET 设备发现、组态、周期 IO、诊断和实时通信概览。
28. [bus/industrial/profinet-practical.md](bus/industrial/profinet-practical.md)：PROFINET 设备命名、GSDML、周期 IO、PLC 诊断和 Wireshark 排查。
29. [bus/industrial/profinet-deep-dive.md](bus/industrial/profinet-deep-dive.md)：PROFINET DCP、GSDML、AR/CR、周期 IO、诊断、RT/IRT 和协议栈实现边界。
30. [bus/industrial/ethernet-ip.md](bus/industrial/ethernet-ip.md)：EtherNet/IP、CIP 对象模型、显式消息和隐式 IO 概览。
31. [bus/industrial/ethernet-ip-practical.md](bus/industrial/ethernet-ip-practical.md)：EtherNet/IP EDS、CIP 对象、Assembly、RPI、显式/隐式消息和抓包调试。
32. [bus/industrial/ethernet-ip-deep-dive.md](bus/industrial/ethernet-ip-deep-dive.md)：EtherNet/IP CIP 对象、Encapsulation、Forward Open、Assembly、RPI 和实现边界。
33. [bus/automotive/j1939.md](bus/automotive/j1939.md)：J1939、PGN、SPN、商用车 CAN 通信概览。
34. [bus/automotive/j1939-practical.md](bus/automotive/j1939-practical.md)：J1939 29-bit ID、PGN/SPN、地址声明、多包传输、DBC 和网关调试。
35. [bus/automotive/j1939-deep-dive.md](bus/automotive/j1939-deep-dive.md)：J1939 29-bit ID、NAME、地址声明、PGN/SPN、多包、DM 诊断和网关治理。
36. [bus/automotive/uds.md](bus/automotive/uds.md)：UDS 诊断服务、DID、安全访问、刷写和 ISO-TP 概览。
37. [bus/automotive/uds-practical.md](bus/automotive/uds-practical.md)：UDS 会话、DID、DTC、安全访问、NRC、刷写流程和诊断日志调试。
38. [bus/automotive/uds-deep-dive.md](bus/automotive/uds-deep-dive.md)：UDS 诊断状态机、NRC、会话、安全访问、刷写事务、DoIP/网关和实现边界。
39. [bus/industrial/ethernet-tsn.md](bus/industrial/ethernet-tsn.md)：TSN 时间敏感网络、同步、调度和确定性以太网概览。
40. [bus/industrial/ethernet-tsn-practical.md](bus/industrial/ethernet-tsn-practical.md)：TSN 时间同步、队列调度、Qbv/Qav/Qbu、交换机配置和延迟测量实践。
41. [bus/display/fpd-link-gmsl.md](bus/display/fpd-link-gmsl.md)：车载视频 SerDes、FPD-Link、GMSL 和远距离摄像头链路。
42. [bus/industrial/profibus.md](bus/industrial/profibus.md)：PROFIBUS DP/PA、传统现场总线和西门子存量生态概览。
43. [bus/industrial/profibus-deep-dive.md](bus/industrial/profibus-deep-dive.md)：PROFIBUS DP/PA、主从周期通信、GSD、诊断、总线段和存量系统排查。
44. [bus/industrial/dmx512.md](bus/industrial/dmx512.md)：DMX512 灯光控制、Break、通道数据和舞台灯光场景。
45. [bus/industrial/dmx512-practical.md](bus/industrial/dmx512-practical.md)：DMX512 Break、Start Code、通道地址、灯具模式、刷新率和终端调试。
46. [bus/industrial/dmx512-deep-dive.md](bus/industrial/dmx512-deep-dive.md)：DMX512 时序、通道模型、RDM、多 Universe、抗干扰和灯光系统排查。
47. [bus/display/hdmi-edp.md](bus/display/hdmi-edp.md)：HDMI/eDP 外接和嵌入式显示链路概览。
48. [bus/display/hdmi-edp-practical.md](bus/display/hdmi-edp-practical.md)：HDMI/eDP EDID、HPD、DDC、AUX、Link Training、Panel 电源和背光调试。
49. [bus/display/hdmi-edp-deep-dive.md](bus/display/hdmi-edp-deep-dive.md)：HDMI/eDP EDID、DPCD、TMDS/Main Link、Link Training、背光和黑屏排查。
50. [bus/usb/usb-dfu.md](bus/usb/usb-dfu.md)：USB DFU 固件升级、bootloader、分块下载和防变砖策略。
51. [bus/automotive/iso-tp.md](bus/automotive/iso-tp.md)：ISO-TP CAN 多帧传输、Flow Control 和 UDS 承载。
52. [bus/industrial/mqtt.md](bus/industrial/mqtt.md)：MQTT 发布订阅、Topic、QoS 和 IoT 上云场景。
53. [bus/automotive/iso-tp-practical.md](bus/automotive/iso-tp-practical.md)：ISO-TP CAN 多帧调试、Flow Control、STmin、Block Size 和 UDS 验证。
54. [bus/usb/usb-dfu-practical.md](bus/usb/usb-dfu-practical.md)：USB DFU 升级流程、分区、校验、回滚和防变砖工程实践。
55. [bus/industrial/mqtt-practical.md](bus/industrial/mqtt-practical.md)：MQTT Topic、QoS、Keepalive、断线重连、TLS 和网关上云实践。
56. [bus/display/fpd-link-gmsl-practical.md](bus/display/fpd-link-gmsl-practical.md)：车载 SerDes 链路锁定、远端 I2C、MIPI 桥接和多摄像头调试。
57. [bus/display/fpd-link-gmsl-deep-dive.md](bus/display/fpd-link-gmsl-deep-dive.md)：车载 SerDes 分层模型、反向通道、链路预算、PoC、多摄同步和现场排查。

### CAN 家族专题（2026-10-31 补齐，2026-11-02 续）

CAN 家族全景、四个协议的 failure-cases、OBD-II 车载诊断，以及功能安全 / 商用车诊断两个专篇：

58. [bus/automotive/can-protocol-family.md](bus/automotive/can-protocol-family.md)：CAN 家族全景——分层结构、协议矩阵、选型决策、文档索引与覆盖缺口。
59. [bus/automotive/can-standards-map.md](bus/automotive/can-standards-map.md)：CAN 家族标准规范总表——按层（连接器/物理/链路/传输/网络/应用/测试/环境/安全/法规）与按协议汇总标准号。
60. [bus/automotive/iso-tp-failure-cases.md](bus/automotive/iso-tp-failure-cases.md)：ISO-TP 产线案例——SF 7 字节边界、TX/RX ID 方向、BS 语义、STmin 编码、SN 4bit 环绕。
61. [bus/automotive/uds-failure-cases.md](bus/automotive/uds-failure-cases.md)：UDS 产线案例——会话服务表、DID 落盘、种子密钥、刷写变砖、BSC 循环、S3 会话保持。
62. [bus/automotive/canopen-failure-cases.md](bus/automotive/canopen-failure-cases.md)：CANopen 产线案例——Node ID 冲突、SDO 字节序、PDO 映射、NMT 状态机、Heartbeat 过滤。
63. [bus/automotive/obd2.md](bus/automotive/obd2.md)：OBD-II 车载排放诊断概览、九个 Mode、PID 速查和 DTC 格式。
64. [bus/automotive/obd2-deep-dive.md](bus/automotive/obd2-deep-dive.md)：OBD-II PID 支持协商、I/M 就绪与监测模型、Mode 详解、OBD-II 与 UDS 的边界。
65. [bus/automotive/obd2-practical.md](bus/automotive/obd2-practical.md)：ELM327 / SocketCAN 工具链、抓包分析、调试流程和检查清单。
66. [bus/automotive/obd2-failure-cases.md](bus/automotive/obd2-failure-cases.md)：OBD-II 案例——适配器能力、PID 解码、多 ECU 响应源、readiness 诊断、VIN 多帧。
67. [bus/automotive/lin.md](bus/automotive/lin.md)：LIN 车载低速总线概念、与 CAN 的核心差异、帧结构、调度机制和 LDF。
68. [bus/automotive/canopen-safety.md](bus/automotive/canopen-safety.md)：CANopen Safety（CiA 304 / EN 50325-5）——SRDO 取反冗余、SCT/SRVT 双超时、CRC 配置签名、GFC 全局失效安全命令。
69. [bus/automotive/wwh-obd.md](bus/automotive/wwh-obd.md)：WWH-OBD（ISO 27145）——商用车全球统一车载诊断，分部分工、DoCAN + DoIP 双链路、PID/MID/ITID 映射。
70. [bus/automotive/wwh-obd-deep-dive.md](bus/automotive/wwh-obd-deep-dive.md)：WWH-OBD 深度——各部分确切边界、PID/MID/ITID→DID/RID 映射、24 位 DTC 格式与 SPN/FMI 对齐、ISO 27145-4 初始化与 11/29 位寻址验证、DoCAN/DoIP 双链路。
71. [bus/automotive/wwh-obd-practical.md](bus/automotive/wwh-obd-practical.md)：WWH-OBD 实战——双链路选型、初始化序列、11/29 位验证脚本、DoIP 路由激活与抓包、24 位 DTC 解析、商用车产线与检测站场景。
72. [bus/automotive/wwh-obd-failure-cases.md](bus/automotive/wwh-obd-failure-cases.md)：WWH-OBD 案例——DoIP 链路识别、长寻址车型、DTC 格式错乱、路由激活 0x03、网关路由、P2\* 超时、产线检测时机。

## 基础外设补充

基础外设文档用于补齐通信前置能力：

1. [basic/gpio.md](basic/gpio.md)：GPIO 输入输出、上拉下拉、推挽开漏和中断。
2. [basic/pwm.md](basic/pwm.md)：PWM 频率、占空比、分辨率和典型控制场景。
3. [basic/adc-dac.md](basic/adc-dac.md)：ADC/DAC 分辨率、参考电压、采样和模拟输出。
4. [basic/i2s.md](basic/i2s.md)：I2S 音频时钟、采样率、位深和 Codec 连接。
5. [basic/qspi-ospi.md](basic/qspi-ospi.md)：QSPI/OSPI 线宽、dummy cycle、Flash 和 XIP。
6. [basic/jtag-swd.md](basic/jtag-swd.md)：JTAG/SWD 下载调试接口、VTref、复位和量产烧录。
7. [basic/lvds.md](basic/lvds.md)：LVDS 差分信号、工业屏连接和显示链路调试。
