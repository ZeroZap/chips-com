# Chips Communication Knowledge Base

这是一个面向芯片间通信的知识库，用于整理从基础外设接口到成熟总线协议的通信体系。

## 分类原则

通信内容按抽象层级划分：

1. `basic/`：基础通信接口与电气/时序机制。
2. `bus/`：建立在基础接口之上的成熟总线、协议或网络体系。

`basic` 关注“芯片如何通过某种外设接口收发数据”，`bus` 关注“多个设备如何通过协议规则组织通信”。

## 推荐目录结构

```text
chips-com/
├── basic/
│   ├── README.md
│   ├── uart.md
│   ├── i2c.md
│   ├── spi.md
│   ├── gpio.md
│   ├── pwm.md
│   ├── adc-dac.md
│   ├── can-phy.md
│   └── ethernet-phy.md
├── bus/
│   ├── README.md
│   ├── modbus.md
│   ├── can.md
│   ├── i3c.md
│   ├── smbus.md
│   ├── pmbus.md
│   ├── one-wire.md
│   ├── usb.md
│   ├── ethernet.md
│   └── fieldbus.md
└── README.md
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

完整的阶段化学习安排见 `LEARNING_PLAN.md`。

跨协议排障方法见 `DEBUG_PLAYBOOK.md`。

协议选型矩阵见 `PROTOCOL_SELECTION.md`。

术语表见 `GLOSSARY.md`，缩写表见 `ACRONYMS.md`，调试工具指南见 `TOOLS.md`，分层图谱见 `LAYERED_MAP.md`。

应用场景选型见 `APPLICATION_SCENARIOS.md`，典型设备接口参考见 `DEVICE_EXAMPLES.md`。

文档模板见 `DOC_TEMPLATES.md`，协议对照表见 `PROTOCOL_COMPARISON.md`，故障速查见 `TROUBLESHOOTING_QUICKREF.md`，实验路线见 `LABS.md`。

完整索引见 `INDEX.md`，按目标阅读见 `READING_PATHS.md`，新增内容评审见 `REVIEW_CHECKLIST.md`，贡献规范见 `CONTRIBUTING.md`。

当前覆盖范围和后续扩展方向见 `COVERAGE.md`。

原理图检查见 `SCHEMATIC_CHECKLISTS.md`，驱动状态机模式见 `DRIVER_PATTERNS.md`，故障案例见 `FAILURE_CASES.md`，波形观察见 `WAVEFORM_GUIDE.md`。

实验记录模板见 `EXPERIMENT_TEMPLATE.md`，接口参数速查见 `PARAMETER_CHEATSHEET.md`，量产测试策略见 `PRODUCTION_TEST.md`，可靠性设计见 `RELIABILITY_GUIDE.md`。

## 实战深入路径

完成基础概念后，按以下顺序进入工程调试文档：

1. `basic/uart-practical.md`：UART 接线、参数、乱码和字节流分帧。
2. `basic/uart-deep-dive.md`：UART 波特率误差、过采样、DMA、硬件流控和量产排障。
3. `basic/i2c-practical.md`：I2C 上拉、地址扫描、寄存器读写和总线恢复。
4. `basic/i2c-deep-dive.md`：I2C 上拉/电容、地址、Clock Stretching、总线恢复、MUX 和器件特性。
5. `basic/spi-practical.md`：SPI Mode、片选、dummy byte 和多设备共享。
6. `basic/spi-deep-dive.md`：SPI 采样模式、CS 边界、dummy cycle、Flash 命令、高速信号和 QSPI/OSPI。
7. `bus/rs485-modbus-rtu-practical.md`：RS485 方向控制、终端电阻、Modbus RTU 帧和 CRC。
8. `bus/rs485-modbus-rtu-deep-dive.md`：RS485 半双工、隔离防护、帧间隔、寄存器偏移、主站轮询和现场排障。
9. `bus/can-canopen-practical.md`：CAN 物理层、CANopen SDO/PDO/NMT 和电机调试入口。
10. `bus/can-canopen-deep-dive.md`：CAN 位时序、仲裁、错误状态、CANopen PDO/SDO/NMT 和 CiA 402。
11. `bus/i3c-topic.md`：I3C 动态地址、CCC、IBI 和 I2C 混挂边界。
12. `bus/i3c-deep-dive.md`：I3C 动态地址、CCC、IBI、Hot-Join、SDR/HDR、混合总线和驱动模型。
13. `bus/smbus-pmbus-practical.md`：SMBus 事务、PEC、Alert、PMBus 命令、Linear 格式、PAGE 和故障状态。
14. `bus/usb-practical.md`：USB Host/Device、枚举、描述符、Endpoint、CDC/HID/MSC 和 Type-C 基础。
15. `bus/ethernet-deep-dive.md`：Ethernet MAC/PHY、RMII/RGMII、MDIO、帧、ARP、TCP/UDP 和 Wireshark 排障。
16. `bus/ethernet-modbus-tcp-practical.md`：Ethernet 链路、TCP 字节流和 Modbus TCP MBAP。
17. `bus/mipi-csi-dsi-debug.md`：MIPI CSI/DSI 电源、I2C 初始化、Lane、像素格式和黑屏/无图定位。
18. `bus/mipi-csi-dsi-deep-dive.md`：MIPI D-PHY、CSI/DSI 初始化、RAW/YUV/RGB、显示时序和图像链路排障。
19. `bus/pcie-practical.md`：PCIe Root Complex/Endpoint、Lane、配置空间、BAR、MSI 和 DMA。
20. `bus/sdio-practical.md`：SDIO CLK/CMD/DAT、Wi-Fi 模块、固件、设备树和枚举排障。
21. `bus/one-wire-practical.md`：1-Wire 上拉、时序、ROM ID、DS18B20 和寄生供电。
22. `bus/lin-practical.md`：LIN 主从调度、Break/Sync/ID/Checksum 和车身低速节点。
23. `bus/ethercat-deep-dive.md`：EtherCAT 主从、ESC、On-the-fly、PDO、Mailbox、DC 和 WKC。
24. `bus/industrial-ethernet-comparison.md`：Modbus TCP、PROFINET、EtherNet/IP 和 EtherCAT 选型对比。
25. `bus/usb-deep-dive.md`：USB 标准请求、描述符层级、复合设备、类协议和枚举排障。
26. `bus/modbus-tcp-deep-dive.md`：Modbus TCP MBAP、事务 ID、Unit ID、并发连接和网关转换。
27. `bus/profinet.md`：PROFINET 设备发现、组态、周期 IO、诊断和实时通信概览。
28. `bus/profinet-practical.md`：PROFINET 设备命名、GSDML、周期 IO、PLC 诊断和 Wireshark 排查。
29. `bus/profinet-deep-dive.md`：PROFINET DCP、GSDML、AR/CR、周期 IO、诊断、RT/IRT 和协议栈实现边界。
30. `bus/ethernet-ip.md`：EtherNet/IP、CIP 对象模型、显式消息和隐式 IO 概览。
31. `bus/ethernet-ip-practical.md`：EtherNet/IP EDS、CIP 对象、Assembly、RPI、显式/隐式消息和抓包调试。
32. `bus/ethernet-ip-deep-dive.md`：EtherNet/IP CIP 对象、Encapsulation、Forward Open、Assembly、RPI 和实现边界。
33. `bus/j1939.md`：J1939、PGN、SPN、商用车 CAN 通信概览。
34. `bus/j1939-practical.md`：J1939 29-bit ID、PGN/SPN、地址声明、多包传输、DBC 和网关调试。
35. `bus/uds.md`：UDS 诊断服务、DID、安全访问、刷写和 ISO-TP 概览。
36. `bus/uds-practical.md`：UDS 会话、DID、DTC、安全访问、NRC、刷写流程和诊断日志调试。
37. `bus/ethernet-tsn.md`：TSN 时间敏感网络、同步、调度和确定性以太网概览。
38. `bus/fpd-link-gmsl.md`：车载视频 SerDes、FPD-Link、GMSL 和远距离摄像头链路。
39. `bus/profibus.md`：PROFIBUS DP/PA、传统现场总线和西门子存量生态概览。
40. `bus/dmx512.md`：DMX512 灯光控制、Break、通道数据和舞台灯光场景。
41. `bus/hdmi-edp.md`：HDMI/eDP 外接和嵌入式显示链路概览。
42. `bus/usb-dfu.md`：USB DFU 固件升级、bootloader、分块下载和防变砖策略。
43. `bus/iso-tp.md`：ISO-TP CAN 多帧传输、Flow Control 和 UDS 承载。
44. `bus/mqtt.md`：MQTT 发布订阅、Topic、QoS 和 IoT 上云场景。
45. `bus/iso-tp-practical.md`：ISO-TP CAN 多帧调试、Flow Control、STmin、Block Size 和 UDS 验证。
46. `bus/usb-dfu-practical.md`：USB DFU 升级流程、分区、校验、回滚和防变砖工程实践。
47. `bus/mqtt-practical.md`：MQTT Topic、QoS、Keepalive、断线重连、TLS 和网关上云实践。
48. `bus/fpd-link-gmsl-practical.md`：车载 SerDes 链路锁定、远端 I2C、MIPI 桥接和多摄像头调试。

## 基础外设补充

基础外设文档用于补齐通信前置能力：

1. `basic/gpio.md`：GPIO 输入输出、上拉下拉、推挽开漏和中断。
2. `basic/pwm.md`：PWM 频率、占空比、分辨率和典型控制场景。
3. `basic/adc-dac.md`：ADC/DAC 分辨率、参考电压、采样和模拟输出。
4. `basic/i2s.md`：I2S 音频时钟、采样率、位深和 Codec 连接。
5. `basic/qspi-ospi.md`：QSPI/OSPI 线宽、dummy cycle、Flash 和 XIP。
6. `basic/jtag-swd.md`：JTAG/SWD 下载调试接口、VTref、复位和量产烧录。
7. `basic/lvds.md`：LVDS 差分信号、工业屏连接和显示链路调试。
