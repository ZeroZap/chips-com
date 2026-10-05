# Bus And Protocols

`bus` 用于整理建立在基础通信接口之上的成熟总线、协议或网络体系。这里的重点是拓扑结构、寻址、帧格式、协议状态机、错误处理和多设备协作。

## 建议分类

### 基于串口/差分链路的总线

- `modbus.md`：Modbus RTU/TCP、寄存器模型、功能码、主从通信。
- `modbus-tcp-deep-dive.md`：Modbus TCP MBAP、事务 ID、Unit ID、并发连接和 RTU 网关转换。
- `rs485-modbus-rtu-practical.md`：RS485 方向控制、终端/偏置、Modbus RTU 帧、CRC 和调试流程。
- `rs485-modbus-rtu-deep-dive.md`：RS485 半双工、隔离防护、帧间隔、寄存器偏移、主站轮询和现场排障。

### RTU 设备协议全集（远动终端）

- `rtu-protocols.md`：RTU 设备协议支持矩阵——电力（IEC 101/104、DNP3、IEC 61850）、水利/环保（SL651、SZY206、HJ212）、表计/楼宇/IoT（DL/T 645、CJ/T 188、BACnet、MQTT、OPC UA），含典型场景协议组合和 chips-com 补齐路线图。
- `rtu-gateway-design.md`：RTU 网关总体设计——内部 Point 模型、协议转换策略、数据流。

#### 电力调度协议

- `iec104.md` / `iec104-practical.md` / `iec104-deep-dive.md` / `iec104-index.md` / `iec104-failure-cases.md`：IEC 60870-5-104，国内 RTU 上行标配（L4 完整闭环）。
- `iec101.md` / `iec101-practical.md` / `iec101-deep-dive.md` / `iec101-index.md` / `iec101-failure-cases.md`：IEC 60870-5-101，IEC 104 的串行版本。
- `dnp3.md` / `dnp3-practical.md` / `dnp3-deep-dive.md` / `dnp3-index.md` / `dnp3-failure-cases.md`：DNP3，北美电力 SCADA / 出海电力标配。
- `iec61850.md` / `iec61850-practical.md` / `iec61850-deep-dive.md` / `iec61850-index.md` / `iec61850-failure-cases.md`：IEC 61850，变电站自动化高端。

#### 水利 / 环保监测协议

- `sl651.md` / `sl651-practical.md` / `sl651-deep-dive.md` / `sl651-index.md` / `sl651-failure-cases.md`：SL 651-2014，水文监测国标。
- `szy206.md` / `szy206-practical.md` / `szy206-deep-dive.md` / `szy206-index.md` / `szy206-failure-cases.md`：SZY 206-2016，水资源监测。
- `slt427.md` / `slt427-practical.md` / `slt427-deep-dive.md` / `slt427-index.md` / `slt427-failure-cases.md`：SL/T 427，水资源监测补充。
- `hj212.md` / `hj212-practical.md` / `hj212-deep-dive.md` / `hj212-index.md` / `hj212-failure-cases.md`：HJ 212-2017，环保联网。

#### 表计 / 楼宇 / IoT 协议

- `dlt645.md` / `dlt645-practical.md` / `dlt645-deep-dive.md` / `dlt645-index.md` / `dlt645-failure-cases.md`：DL/T 645，国内电表协议。
- `cjt188.md` / `cjt188-practical.md` / `cjt188-deep-dive.md` / `cjt188-index.md` / `cjt188-failure-cases.md`：CJ/T 188，水气热量表协议。
- `bacnet.md` / `bacnet-practical.md` / `bacnet-deep-dive.md` / `bacnet-index.md` / `bacnet-failure-cases.md`：BACnet，楼宇自动化国际标准。
- `opcua.md` / `opcua-practical.md` / `opcua-deep-dive.md` / `opcua-index.md` / `opcua-failure-cases.md`：OPC UA，工业 4.0 信息建模。

#### RTU 跨协议网关设计

- `modbus-rtu-iec104-gateway.md`：Modbus RTU ↔ IEC 104（电力主站最常见）。
- `dlt645-iec104-gateway.md`：DL/T 645 ↔ IEC 104（电表接入电力主站）。
- `modbus-rtu-mqtt-gateway.md`：Modbus RTU ↔ MQTT（工业 IoT 上云）。
- `hj212-mqtt-gateway.md`：HJ 212 ↔ MQTT（环保 RTU 上云）。
- `dnp3-iec104-gateway.md`：DNP3 ↔ IEC 104（双栈 / 出海 + 国内）。
- `bacnet-opcua-gateway.md`：BACnet ↔ OPC UA（楼宇 + 工业 4.0）。
- `iec61850-iec104-gateway.md`：IEC 61850 ↔ IEC 104（变电站双栈）。

#### RTU 协议厂商对标

- `iec104-vendor-bench.md`：IEC 104 厂商对标（南瑞 / 四方 / ABB / Siemens / SEL）。
- `iec101-vendor-bench.md`：IEC 101 厂商对标。
- `dlt645-vendor-bench.md`：DL/T 645 厂商对标（三星 / 宁波水表 / 海兴 / 威胜）。
- `hj212-vendor-bench.md`：HJ 212 厂商对标（聚光 / 先河 / 雪迪龙）。
- `sl651-vendor-bench.md`：SL 651 厂商对标（四创 / 国睿）。
- `dnp3-vendor-bench.md`：DNP3 厂商对标（ABB / Siemens / SEL / GE）。
- `iec61850-vendor-bench.md`：IEC 61850 厂商对标。
- `szy206-vendor-bench.md`：SZY 206 厂商对标。
- `slt427-vendor-bench.md`：SL/T 427 厂商对标。
- `bacnet-vendor-bench.md`：BACnet 厂商对标（Honeywell / JCI / Siemens / Schneider）。
- `opcua-vendor-bench.md`：OPC UA 厂商对标（Siemens / Beckhoff / Rockwell）。
- `cjt188-vendor-bench.md`：CJ/T 188 厂商对标（宁波水表 / 新天科技）。
- `mqtt-vendor-bench.md`：MQTT 厂商对标（AWS IoT / Azure / 阿里云 / 华为云 / EMQX）。

- `dmx512.md`：灯光控制总线、帧结构、单向广播。
- `dmx512-practical.md`：DMX512 Break、Start Code、通道地址、灯具模式、刷新率和终端调试。
- `dmx512-deep-dive.md`：DMX512 时序、通道模型、RDM、多 Universe、抗干扰和灯光系统排查。
- `lin.md`：车身低速网络、主从调度、低成本单线通信。
- `lin-practical.md`：LIN 主从调度、Break/Sync/Identifier、Checksum、LDF 和车身节点调试。

### 基于 I2C 生态的总线

- `smbus.md`：系统管理总线、电池和主板管理场景。
- `pmbus.md`：电源管理总线、电源模块监控与控制。
- `smbus-pmbus-practical.md`：SMBus 事务、PEC、Alert、PMBus 命令、Linear 格式、PAGE 和故障状态。
- `i3c.md`：I2C 演进总线、动态地址、带内中断、更高速率。
- `i3c-topic.md`：I3C 工程专题、CCC、IBI、动态地址和 I2C 混挂边界。
- `i3c-deep-dive.md`：I3C 动态地址、CCC、IBI、Hot-Join、SDR/HDR、混合总线和驱动模型。

### 工业与汽车现场总线

- `can.md`：CAN/CAN FD、仲裁、错误处理、车载和工业控制。
- `canopen.md`：CANopen 对象字典、PDO/SDO、设备模型。
- `can-canopen-practical.md`：CAN 物理层、CANopen COB-ID、SDO/PDO/NMT 和电机调试流程。
- `can-canopen-deep-dive.md`：CAN 位时序、仲裁、错误状态、CANopen PDO/SDO/NMT 和 CiA 402。
- `iso-tp.md`：CAN 多帧传输、Single/First/Consecutive/Flow Control 帧和 UDS 承载。
- `iso-tp-practical.md`：ISO-TP 多帧调试、Flow Control、Block Size、STmin 和 UDS 验证。
- `profibus.md`：工业现场总线、主从控制、过程自动化。
- `profibus-practical.md`：PROFIBUS DP/PA 区分、地址、终端、GSD、主站组态和从站诊断。
- `profibus-deep-dive.md`：PROFIBUS DP/PA、主从周期通信、GSD、诊断、总线段和存量系统排查。
- `ethercat.md`：实时工业以太网、从站级联、分布式时钟。
- `ethercat-deep-dive.md`：EtherCAT 主站/从站、ESC、On-the-fly、过程数据、Mailbox、DC 和 WKC。
- `j1939.md`：商用车 CAN 上层协议、PGN、SPN 和多包传输概览。
- `j1939-practical.md`：J1939 29-bit ID、PGN/SPN、地址声明、多包传输、DBC 和网关调试。
- `j1939-deep-dive.md`：J1939 29-bit ID、NAME、地址声明、PGN/SPN、多包、DM 诊断和网关治理。
- `j1939-network-management.md`：NAME 64 bit 字段详细编码、Address Claimed 协议、Commanded Address、心跳监控、多 ECU 协同、Linux 内核 J1939 支持。
- `j1939-transport-protocol.md`：J1939-21 传输协议——BAM 广播协议 + RTS/CTS 点对点协议完整流程 + 超时/重传 + 实战代码。
- `j1939-failure-cases.md`：20 个产线 J1939 死机案例（地址声明冲突 / DM 格式错 / TP 丢包 / NAME 配置错 / 一致性测试等）。
- `j1939-index.md`：J1939 主题总览导航——5 种读者路径、主题速查矩阵、J1939 vs CAN FD 决策。
- `uds.md`：车载统一诊断服务、DID、安全访问、刷写和 ISO-TP 概览。
- `uds-practical.md`：UDS 会话、DID、DTC、安全访问、NRC、刷写流程和诊断日志调试。
- `uds-deep-dive.md`：UDS 诊断状态机、NRC、会话、安全访问、刷写事务、DoIP/网关和实现边界。

### 通用高速总线与网络

- `usb.md`：USB 设备枚举、端点、传输类型、主机控制。
- `usb-practical.md`：USB Host/Device、枚举、描述符、Endpoint、CDC/HID/MSC 和 Type-C 基础（扩）。
- `usb-deep-dive.md`：USB 标准请求、描述符层级、复合设备、CDC/HID/MSC 和枚举排障（扩）。
- `usb-failure-cases.md`：20 个产线 USB 死机案例（描述符 / VBUS / 类驱动 / 高速 / 信号完整性 / VID 等）。
- `usb-enumeration-and-descriptors.md`：枚举 8 步流程、Device/Configuration/Interface/Endpoint 描述符、字符串描述符、IAD 复合设备、VID/PID 申请。
- `usb-class-drivers.md`：CDC (串口) / HID (键鼠) / MSC (U 盘) / DFU (升级) 4 大类驱动完整协议栈和实战代码。
- `usb-dma-and-rtos.md`：USB DMA 模式 (单次 / 双缓冲 / 循环)、FreeRTOS / Zephyr / RT-Thread 三平台集成、缓存一致性 (Cortex-M7)。
- `usb-vs-other-bus.md`：USB vs CAN / I2C / SPI / UART / Ethernet / 无线协议 12 维度对比 + 选型决策树。
- `usb-index.md`：USB 主题总览导航——5 种读者路径、主题速查矩阵、USB vs 其他主题对比。
- `usb-dfu.md`：USB 固件升级、DFU 模式、分块下载、校验和 bootloader 保护。
- `usb-dfu-practical.md`：USB DFU 工程升级流程、分区、校验、回滚和防变砖策略。
- `ethernet.md`：以太网 MAC/PHY、帧、交换、TCP/IP 入口。
- `ethernet-deep-dive.md`：Ethernet MAC/PHY、RMII/RGMII、MDIO、帧、ARP、TCP/UDP 和 Wireshark 排障。
- `ethernet-modbus-tcp-practical.md`：Ethernet 链路、TCP 字节流、Modbus TCP MBAP 和 Wireshark 调试。
- `industrial-ethernet-comparison.md`：Modbus TCP、PROFINET、EtherNet/IP、EtherCAT 对比和选型。
- `modbus-tcp-deep-dive.md`：Modbus TCP MBAP、事务 ID、Unit ID、并发连接和 RTU 网关转换。
- `profinet.md`：PROFINET 设备发现、组态、周期 IO、诊断和实时通信概览。
- `profinet-practical.md`：PROFINET 设备命名、GSDML、周期 IO、PLC 诊断和 Wireshark 排查。
- `profinet-deep-dive.md`：PROFINET DCP、GSDML、AR/CR、周期 IO、诊断、RT/IRT 和协议栈实现边界。
- `ethernet-ip.md`：EtherNet/IP、CIP 对象模型、显式消息和隐式 IO 概览。
- `ethernet-ip-practical.md`：EtherNet/IP EDS、CIP 对象、Assembly、RPI、显式/隐式消息和抓包调试。
- `ethernet-ip-deep-dive.md`：EtherNet/IP CIP 对象、Encapsulation、Forward Open、Assembly、RPI 和实现边界。
- `ethernet-tsn.md`：TSN 时间敏感网络、时间同步、调度和确定性以太网概览。
- `ethernet-tsn-practical.md`：TSN 时间同步、队列调度、Qbv/Qav/Qbu、交换机配置和延迟测量实践。
- `mqtt.md`：MQTT 发布订阅、Topic、QoS、Keepalive 和 IoT 上云场景。
- `mqtt-practical.md`：MQTT Topic 设计、QoS、Keepalive、断线重连、TLS 和网关上云实践。
- `pcie.md`：高速点对点总线、Lane、事务层、DMA 场景。
- `pcie-practical.md`：PCIe Root Complex/Endpoint、Lane、配置空间、BAR、MSI/MSI-X、DMA 和 LTSSM。

### 简单设备总线

- `one-wire.md`：单线通信、寄生供电、温度传感器等低速设备。
- `one-wire-practical.md`：1-Wire 上拉、GPIO 时序、ROM ID、DS18B20、寄生供电和多设备搜索。
- `sdio.md`：SD 卡和 Wi-Fi 模块常见接口。
- `sdio-practical.md`：SDIO CLK/CMD/DAT、1-bit/4-bit、Wi-Fi 模块、固件和设备树调试。
- `mipi.md`：显示和摄像头接口，如 DSI、CSI。
- `mipi-csi-dsi-debug.md`：MIPI CSI/DSI 电源时序、I2C 初始化、Lane、像素格式和黑屏/无图定位。
- `mipi-csi-dsi-deep-dive.md`：MIPI D-PHY、CSI/DSI 初始化、RAW/YUV/RGB、显示时序和图像链路排障。
- `display-interfaces.md`：SPI、RGB、LVDS、MIPI DSI、eDP、HDMI 显示接口选型概览。
- `fpd-link-gmsl.md`：车载视频 SerDes、FPD-Link、GMSL 和远距离摄像头/显示链路。
- `fpd-link-gmsl-practical.md`：车载 SerDes 链路锁定、远端 I2C、MIPI 桥接和多摄像头调试。
- `fpd-link-gmsl-deep-dive.md`：车载 SerDes 分层模型、反向通道、链路预算、PoC、多摄同步和现场排查。
- `hdmi-edp.md`：HDMI/eDP、EDID、AUX、Link Training、外接和嵌入式显示链路。
- `hdmi-edp-practical.md`：HDMI/eDP EDID、HPD、DDC、AUX、Link Training、Panel 电源和背光调试。
- `hdmi-edp-deep-dive.md`：HDMI/eDP EDID、DPCD、TMDS/Main Link、Link Training、背光和黑屏排查。

## 收录边界

放在 `bus` 的内容通常满足以下条件：

- 已经定义了完整的通信规则，而不只是电气接口。
- 支持多个节点、设备寻址、协议帧、错误处理或标准化设备模型。
- 常用于板间通信、工业控制、车载网络、主机外设连接或系统级互联。

例如：`SPI` 放在 `basic`，但基于 SPI 的 SD 卡协议可放在 `bus`；`CAN PHY` 放在 `basic`，但 `CAN` 和 `CANopen` 放在 `bus`。
