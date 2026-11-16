---
tags:
  - layer/bus
  - type/index
---

# Bus And Protocols

`bus` 用于整理建立在基础通信接口之上的成熟总线、协议或网络体系。这里的重点是拓扑结构、寻址、帧格式、协议状态机、错误处理和多设备协作。

## 分目录导航

| 领域                      | 入口                                             | 内容                                                                |
| ------------------------- | ------------------------------------------------ | ------------------------------------------------------------------- |
| 车载与诊断                | [automotive/README.md](automotive/README.md)     | CAN 家族、CANopen、J1939、ISO-TP、UDS、OBD、LIN                     |
| 工业与工业以太网          | [industrial/README.md](industrial/README.md)     | Modbus、PROFI*、EtherCAT、EtherNet/IP、TSN、OPC UA、MQTT、DMX512    |
| 电力 / 水利 / 表计 / 楼宇 | [power-rtu/README.md](power-rtu/README.md)       | IEC 101/104、DNP3、IEC 61850、SL/SZY/HJ、DL/T 645、CJ/T 188、BACnet |
| 无线与物联网              | [wireless-iot/README.md](wireless-iot/README.md) | BLE、ZigBee、LoRa、Matter、Thread、LTE IoT、卫星、PLB、应急通信     |
| USB                       | [usb/README.md](usb/README.md)                   | USB 枚举、类驱动、DFU、DMA/RTOS                                     |
| 显示与视频链路            | [display/README.md](display/README.md)           | HDMI/eDP、FPD-Link/GMSL、MIPI CSI/DSI                               |
| 板内与管理总线            | [onboard/README.md](onboard/README.md)           | I3C、SMBus/PMBus、SDIO、1-Wire、PCIe                                |

## 建议分类

### 基于串口/差分链路的总线

- [industrial/modbus.md](industrial/modbus.md)：Modbus RTU/TCP、寄存器模型、功能码、主从通信。
- [industrial/modbus-tcp-deep-dive.md](industrial/modbus-tcp-deep-dive.md)：Modbus TCP MBAP、事务 ID、Unit ID、并发连接和 RTU 网关转换。
- [industrial/rs485-modbus-rtu-practical.md](industrial/rs485-modbus-rtu-practical.md)：RS485 方向控制、终端/偏置、Modbus RTU 帧、CRC 和调试流程。
- [industrial/rs485-modbus-rtu-deep-dive.md](industrial/rs485-modbus-rtu-deep-dive.md)：RS485 半双工、隔离防护、帧间隔、寄存器偏移、主站轮询和现场排障。

### RTU 设备协议全集（远动终端）

- [power-rtu/rtu-protocols.md](power-rtu/rtu-protocols.md)：RTU 设备协议支持矩阵——电力（IEC 101/104、DNP3、IEC 61850）、水利/环保（SL651、SZY206、HJ212）、表计/楼宇/IoT（DL/T 645、CJ/T 188、BACnet、MQTT、OPC UA），含典型场景协议组合和 chips-com 补齐路线图。
- [power-rtu/rtu-gateway-design.md](power-rtu/rtu-gateway-design.md)：RTU 网关总体设计——内部 Point 模型、协议转换策略、数据流。

#### 电力调度协议

- [power-rtu/iec104.md](power-rtu/iec104.md) / [power-rtu/iec104-practical.md](power-rtu/iec104-practical.md) / [power-rtu/iec104-deep-dive.md](power-rtu/iec104-deep-dive.md) / [power-rtu/iec104-index.md](power-rtu/iec104-index.md) / [power-rtu/iec104-failure-cases.md](power-rtu/iec104-failure-cases.md)：IEC 60870-5-104，国内 RTU 上行标配（L4 完整闭环）。
- [power-rtu/iec101.md](power-rtu/iec101.md) / [power-rtu/iec101-practical.md](power-rtu/iec101-practical.md) / [power-rtu/iec101-deep-dive.md](power-rtu/iec101-deep-dive.md) / [power-rtu/iec101-index.md](power-rtu/iec101-index.md) / [power-rtu/iec101-failure-cases.md](power-rtu/iec101-failure-cases.md)：IEC 60870-5-101，IEC 104 的串行版本。
- [power-rtu/dnp3.md](power-rtu/dnp3.md) / [power-rtu/dnp3-practical.md](power-rtu/dnp3-practical.md) / [power-rtu/dnp3-deep-dive.md](power-rtu/dnp3-deep-dive.md) / [power-rtu/dnp3-index.md](power-rtu/dnp3-index.md) / [power-rtu/dnp3-failure-cases.md](power-rtu/dnp3-failure-cases.md)：DNP3，北美电力 SCADA / 出海电力标配。
- [power-rtu/iec61850.md](power-rtu/iec61850.md) / [power-rtu/iec61850-practical.md](power-rtu/iec61850-practical.md) / [power-rtu/iec61850-deep-dive.md](power-rtu/iec61850-deep-dive.md) / [power-rtu/iec61850-index.md](power-rtu/iec61850-index.md) / [power-rtu/iec61850-failure-cases.md](power-rtu/iec61850-failure-cases.md)：IEC 61850，变电站自动化高端。

#### 水利 / 环保监测协议

- [power-rtu/sl651.md](power-rtu/sl651.md) / [power-rtu/sl651-practical.md](power-rtu/sl651-practical.md) / [power-rtu/sl651-deep-dive.md](power-rtu/sl651-deep-dive.md) / [power-rtu/sl651-index.md](power-rtu/sl651-index.md) / [power-rtu/sl651-failure-cases.md](power-rtu/sl651-failure-cases.md)：SL 651-2014，水文监测国标。
- [power-rtu/szy206.md](power-rtu/szy206.md) / [power-rtu/szy206-practical.md](power-rtu/szy206-practical.md) / [power-rtu/szy206-deep-dive.md](power-rtu/szy206-deep-dive.md) / [power-rtu/szy206-index.md](power-rtu/szy206-index.md) / [power-rtu/szy206-failure-cases.md](power-rtu/szy206-failure-cases.md)：SZY 206-2016，水资源监测。
- [power-rtu/slt427.md](power-rtu/slt427.md) / [power-rtu/slt427-practical.md](power-rtu/slt427-practical.md) / [power-rtu/slt427-deep-dive.md](power-rtu/slt427-deep-dive.md) / [power-rtu/slt427-index.md](power-rtu/slt427-index.md) / [power-rtu/slt427-failure-cases.md](power-rtu/slt427-failure-cases.md)：SL/T 427，水资源监测补充。
- [power-rtu/hj212.md](power-rtu/hj212.md) / [power-rtu/hj212-practical.md](power-rtu/hj212-practical.md) / [power-rtu/hj212-deep-dive.md](power-rtu/hj212-deep-dive.md) / [power-rtu/hj212-index.md](power-rtu/hj212-index.md) / [power-rtu/hj212-failure-cases.md](power-rtu/hj212-failure-cases.md)：HJ 212-2017，环保联网。

#### 表计 / 楼宇 / IoT 协议

- [power-rtu/dlt645.md](power-rtu/dlt645.md) / [power-rtu/dlt645-practical.md](power-rtu/dlt645-practical.md) / [power-rtu/dlt645-deep-dive.md](power-rtu/dlt645-deep-dive.md) / [power-rtu/dlt645-index.md](power-rtu/dlt645-index.md) / [power-rtu/dlt645-failure-cases.md](power-rtu/dlt645-failure-cases.md)：DL/T 645，国内电表协议。
- [power-rtu/cjt188.md](power-rtu/cjt188.md) / [power-rtu/cjt188-practical.md](power-rtu/cjt188-practical.md) / [power-rtu/cjt188-deep-dive.md](power-rtu/cjt188-deep-dive.md) / [power-rtu/cjt188-index.md](power-rtu/cjt188-index.md) / [power-rtu/cjt188-failure-cases.md](power-rtu/cjt188-failure-cases.md)：CJ/T 188，水气热量表协议。
- [power-rtu/bacnet.md](power-rtu/bacnet.md) / [power-rtu/bacnet-practical.md](power-rtu/bacnet-practical.md) / [power-rtu/bacnet-deep-dive.md](power-rtu/bacnet-deep-dive.md) / [power-rtu/bacnet-index.md](power-rtu/bacnet-index.md) / [power-rtu/bacnet-failure-cases.md](power-rtu/bacnet-failure-cases.md)：BACnet，楼宇自动化国际标准。
- [industrial/opcua.md](industrial/opcua.md) / [industrial/opcua-practical.md](industrial/opcua-practical.md) / [industrial/opcua-deep-dive.md](industrial/opcua-deep-dive.md) / [industrial/opcua-index.md](industrial/opcua-index.md) / [industrial/opcua-failure-cases.md](industrial/opcua-failure-cases.md)：OPC UA，工业 4.0 信息建模。

#### RTU 跨协议网关设计

- [industrial/modbus-rtu-iec104-gateway.md](industrial/modbus-rtu-iec104-gateway.md)：Modbus RTU ↔ IEC 104（电力主站最常见）。
- [power-rtu/dlt645-iec104-gateway.md](power-rtu/dlt645-iec104-gateway.md)：DL/T 645 ↔ IEC 104（电表接入电力主站）。
- [industrial/modbus-rtu-mqtt-gateway.md](industrial/modbus-rtu-mqtt-gateway.md)：Modbus RTU ↔ MQTT（工业 IoT 上云）。
- [power-rtu/hj212-mqtt-gateway.md](power-rtu/hj212-mqtt-gateway.md)：HJ 212 ↔ MQTT（环保 RTU 上云）。
- [power-rtu/dnp3-iec104-gateway.md](power-rtu/dnp3-iec104-gateway.md)：DNP3 ↔ IEC 104（双栈 / 出海 + 国内）。
- [power-rtu/bacnet-opcua-gateway.md](power-rtu/bacnet-opcua-gateway.md)：BACnet ↔ OPC UA（楼宇 + 工业 4.0）。
- [power-rtu/iec61850-iec104-gateway.md](power-rtu/iec61850-iec104-gateway.md)：IEC 61850 ↔ IEC 104（变电站双栈）。

#### RTU 协议厂商对标

- [power-rtu/iec104-vendor-bench.md](power-rtu/iec104-vendor-bench.md)：IEC 104 厂商对标（南瑞 / 四方 / ABB / Siemens / SEL）。
- [power-rtu/iec101-vendor-bench.md](power-rtu/iec101-vendor-bench.md)：IEC 101 厂商对标。
- [power-rtu/dlt645-vendor-bench.md](power-rtu/dlt645-vendor-bench.md)：DL/T 645 厂商对标（三星 / 宁波水表 / 海兴 / 威胜）。
- [power-rtu/hj212-vendor-bench.md](power-rtu/hj212-vendor-bench.md)：HJ 212 厂商对标（聚光 / 先河 / 雪迪龙）。
- [power-rtu/sl651-vendor-bench.md](power-rtu/sl651-vendor-bench.md)：SL 651 厂商对标（四创 / 国睿）。
- [power-rtu/dnp3-vendor-bench.md](power-rtu/dnp3-vendor-bench.md)：DNP3 厂商对标（ABB / Siemens / SEL / GE）。
- [power-rtu/iec61850-vendor-bench.md](power-rtu/iec61850-vendor-bench.md)：IEC 61850 厂商对标。
- [power-rtu/szy206-vendor-bench.md](power-rtu/szy206-vendor-bench.md)：SZY 206 厂商对标。
- [power-rtu/slt427-vendor-bench.md](power-rtu/slt427-vendor-bench.md)：SL/T 427 厂商对标。
- [power-rtu/bacnet-vendor-bench.md](power-rtu/bacnet-vendor-bench.md)：BACnet 厂商对标（Honeywell / JCI / Siemens / Schneider）。
- [industrial/opcua-vendor-bench.md](industrial/opcua-vendor-bench.md)：OPC UA 厂商对标（Siemens / Beckhoff / Rockwell）。
- [power-rtu/cjt188-vendor-bench.md](power-rtu/cjt188-vendor-bench.md)：CJ/T 188 厂商对标（宁波水表 / 新天科技）。
- [industrial/mqtt-vendor-bench.md](industrial/mqtt-vendor-bench.md)：MQTT 厂商对标（AWS IoT / Azure / 阿里云 / 华为云 / EMQX）。

- [industrial/dmx512.md](industrial/dmx512.md)：灯光控制总线、帧结构、单向广播。
- [industrial/dmx512-practical.md](industrial/dmx512-practical.md)：DMX512 Break、Start Code、通道地址、灯具模式、刷新率和终端调试。
- [industrial/dmx512-deep-dive.md](industrial/dmx512-deep-dive.md)：DMX512 时序、通道模型、RDM、多 Universe、抗干扰和灯光系统排查。
- [automotive/lin.md](automotive/lin.md)：LIN 车载低速总线概念、与 CAN 的核心差异、帧结构、调度机制、LDF 和睡眠唤醒。
- [automotive/lin-practical.md](automotive/lin-practical.md)：LIN 主从调度、Break/Sync/Identifier、Checksum、LDF 和车身节点调试。

### 基于 I2C 生态的总线

- [onboard/smbus.md](onboard/smbus.md)：系统管理总线、电池和主板管理场景。
- [onboard/pmbus.md](onboard/pmbus.md)：电源管理总线、电源模块监控与控制。
- [onboard/smbus-pmbus-practical.md](onboard/smbus-pmbus-practical.md)：SMBus 事务、PEC、Alert、PMBus 命令、Linear 格式、PAGE 和故障状态。
- [onboard/i3c.md](onboard/i3c.md)：I2C 演进总线、动态地址、带内中断、更高速率。
- [onboard/i3c-topic.md](onboard/i3c-topic.md)：I3C 工程专题、CCC、IBI、动态地址和 I2C 混挂边界。
- [onboard/i3c-deep-dive.md](onboard/i3c-deep-dive.md)：I3C 动态地址、CCC、IBI、Hot-Join、SDR/HDR、混合总线和驱动模型。

### 工业与汽车现场总线

- [automotive/can-protocol-family.md](automotive/can-protocol-family.md)：CAN 家族全景——分层结构、协议矩阵、选型决策、文档索引与覆盖缺口。
- [automotive/can-standards-map.md](automotive/can-standards-map.md)：CAN 家族标准规范总表——按层（连接器/物理/链路/传输/网络/应用/测试/环境/安全/法规）与按协议两张维度汇总标准号，含 OBD-II vs WWH-OBD vs UDS 对比与物理层收发器选型。
- [automotive/can.md](automotive/can.md)：CAN/CAN FD、仲裁、错误处理、车载和工业控制。
- [automotive/canopen.md](automotive/canopen.md)：CANopen 对象字典、PDO/SDO、设备模型。
- [automotive/canopen-practical.md](automotive/canopen-practical.md)：CAN 物理层、CANopen COB-ID、SDO/PDO/NMT 和电机调试流程。
- [automotive/canopen-deep-dive.md](automotive/canopen-deep-dive.md)：CAN 位时序、仲裁、错误状态、CANopen PDO/SDO/NMT 和 CiA 402。
- [automotive/canopen-failure-cases.md](automotive/canopen-failure-cases.md)：CANopen 产线案例（Node ID 冲突 / SDO 字节序 / PDO 映射 / NMT 状态机 / Heartbeat 过滤 / EMCY 编码 / 总线负载饿死）。
- [automotive/canopen-safety.md](automotive/canopen-safety.md)：CANopen Safety（CiA 304 / EN 50325-5）——SRDO 1-out-of-2 取反冗余、SCT/SRVT 双超时、CRC-16-CCITT 配置签名、GFC 全局失效安全命令。
- [automotive/iso-tp.md](automotive/iso-tp.md)：CAN 多帧传输、Single/First/Consecutive/Flow Control 帧和 UDS 承载。
- [automotive/iso-tp-practical.md](automotive/iso-tp-practical.md)：ISO-TP 多帧调试、Flow Control、Block Size、STmin 和 UDS 验证。
- [automotive/iso-tp-deep-dive.md](automotive/iso-tp-deep-dive.md)：ISO-TP 寻址方式、PCI 编码、流控参数、超时和缓冲区。
- [automotive/iso-tp-failure-cases.md](automotive/iso-tp-failure-cases.md)：ISO-TP 产线案例（SF 7 字节边界 / TX-RX ID 方向 / 寻址方式 / BS 语义 / STmin 编码 / SN 4bit 环绕 / 缓冲区越界 / CAN FD DLC 编码）。
- [automotive/uds.md](automotive/uds.md)：车载统一诊断服务、DID、安全访问、刷写和 ISO-TP 概览。
- [automotive/uds-practical.md](automotive/uds-practical.md)：UDS 会话、DID、DTC、安全访问、NRC、刷写流程和诊断日志调试。
- [automotive/uds-deep-dive.md](automotive/uds-deep-dive.md)：UDS 诊断状态机、NRC、会话、安全访问、刷写事务、DoIP/网关和实现边界。
- [automotive/uds-failure-cases.md](automotive/uds-failure-cases.md)：UDS 产线案例（会话服务表 / DID 落盘 / 种子密钥 / 安全延时 / 刷写变砖 / BSC 4bit 循环 / Response Pending 死锁 / S3 会话保持 / 功能寻址冲突）。
- [automotive/obd2.md](automotive/obd2.md)：OBD-II 车载排放诊断概览、九个 Mode、PID 速查和 DTC 格式。
- [automotive/obd2-deep-dive.md](automotive/obd2-deep-dive.md)：OBD-II PID 支持协商、I/M 就绪与监测模型、Mode 详解、OBD-II 与 UDS 的边界。
- [automotive/obd2-practical.md](automotive/obd2-practical.md)：ELM327 / SocketCAN 工具链、抓包分析、调试流程和检查清单。
- [automotive/obd2-failure-cases.md](automotive/obd2-failure-cases.md)：OBD-II 案例（适配器能力 / PID 解码 / 多 ECU 响应源 / 清码复现 / readiness 诊断 / VIN 多帧 / 数据一致性 / 自回显）。
- [automotive/wwh-obd.md](automotive/wwh-obd.md)：WWH-OBD（ISO 27145）——商用车全球统一车载诊断；27145-1/2/3/4/6 分工、DoCAN + DoIP 双链路、PID/MID/ITID 到 DID/RID/DTC 映射、GTR No. 5 法规定位。
- [industrial/profibus.md](industrial/profibus.md)：工业现场总线、主从控制、过程自动化。
- [industrial/profibus-practical.md](industrial/profibus-practical.md)：PROFIBUS DP/PA 区分、地址、终端、GSD、主站组态和从站诊断。
- [industrial/profibus-deep-dive.md](industrial/profibus-deep-dive.md)：PROFIBUS DP/PA、主从周期通信、GSD、诊断、总线段和存量系统排查。

- [industrial/ethercat-deep-dive.md](industrial/ethercat-deep-dive.md)：EtherCAT 主站/从站、ESC、On-the-fly、过程数据、Mailbox、DC 和 WKC。
- [automotive/j1939.md](automotive/j1939.md)：商用车 CAN 上层协议、PGN、SPN 和多包传输概览。
- [automotive/j1939-practical.md](automotive/j1939-practical.md)：J1939 29-bit ID、PGN/SPN、地址声明、多包传输、DBC 和网关调试。
- [automotive/j1939-deep-dive.md](automotive/j1939-deep-dive.md)：J1939 29-bit ID、NAME、地址声明、PGN/SPN、多包、DM 诊断和网关治理。
- [automotive/j1939-network-management.md](automotive/j1939-network-management.md)：NAME 64 bit 字段详细编码、Address Claimed 协议、Commanded Address、心跳监控、多 ECU 协同、Linux 内核 J1939 支持。
- [automotive/j1939-transport-protocol.md](automotive/j1939-transport-protocol.md)：J1939-21 传输协议——BAM 广播协议 + RTS/CTS 点对点协议完整流程 + 超时/重传 + 实战代码。
- [automotive/j1939-failure-cases.md](automotive/j1939-failure-cases.md)：21 个产线 J1939 死机案例（地址声明冲突 / DM 格式错 / TP 丢包 / NAME 配置错 / 一致性测试等）。
- [automotive/j1939-index.md](automotive/j1939-index.md)：J1939 主题总览导航——5 种读者路径、主题速查矩阵、J1939 vs CAN FD 决策。

### 通用高速总线与网络

- [usb/usb.md](usb/usb.md)：USB 设备枚举、端点、传输类型、主机控制。
- [usb/usb-practical.md](usb/usb-practical.md)：USB Host/Device、枚举、描述符、Endpoint、CDC/HID/MSC 和 Type-C 基础（扩）。
- [usb/usb-deep-dive.md](usb/usb-deep-dive.md)：USB 标准请求、描述符层级、复合设备、CDC/HID/MSC 和枚举排障（扩）。
- [usb/usb-failure-cases.md](usb/usb-failure-cases.md)：21 个产线 USB 死机案例（描述符 / VBUS / 类驱动 / 高速 / 信号完整性 / VID 等）。
- [usb/usb-enumeration-and-descriptors.md](usb/usb-enumeration-and-descriptors.md)：枚举 8 步流程、Device/Configuration/Interface/Endpoint 描述符、字符串描述符、IAD 复合设备、VID/PID 申请。
- [usb/usb-class-drivers.md](usb/usb-class-drivers.md)：CDC (串口) / HID (键鼠) / MSC (U 盘) / DFU (升级) 4 大类驱动完整协议栈和实战代码。
- [usb/usb-dma-and-rtos.md](usb/usb-dma-and-rtos.md)：USB DMA 模式 (单次 / 双缓冲 / 循环)、FreeRTOS / Zephyr / RT-Thread 三平台集成、缓存一致性 (Cortex-M7)。
- [usb/usb-vs-other-bus.md](usb/usb-vs-other-bus.md)：USB vs CAN / I2C / SPI / UART / Ethernet / 无线协议 12 维度对比 + 选型决策树。
- [usb/usb-index.md](usb/usb-index.md)：USB 主题总览导航——5 种读者路径、主题速查矩阵、USB vs 其他主题对比。
- [usb/usb-dfu.md](usb/usb-dfu.md)：USB 固件升级、DFU 模式、分块下载、校验和 bootloader 保护。
- [usb/usb-dfu-practical.md](usb/usb-dfu-practical.md)：USB DFU 工程升级流程、分区、校验、回滚和防变砖策略。
- [industrial/ethernet.md](industrial/ethernet.md)：以太网 MAC/PHY、帧、交换、TCP/IP 入口。
- [industrial/ethernet-deep-dive.md](industrial/ethernet-deep-dive.md)：Ethernet MAC/PHY、RMII/RGMII、MDIO、帧、ARP、TCP/UDP 和 Wireshark 排障。
- [industrial/ethernet-modbus-tcp-practical.md](industrial/ethernet-modbus-tcp-practical.md)：Ethernet 链路、TCP 字节流、Modbus TCP MBAP 和 Wireshark 调试。
- [industrial/industrial-ethernet-comparison.md](industrial/industrial-ethernet-comparison.md)：Modbus TCP、PROFINET、EtherNet/IP、EtherCAT 对比和选型。
- [industrial/modbus-tcp-deep-dive.md](industrial/modbus-tcp-deep-dive.md)：Modbus TCP MBAP、事务 ID、Unit ID、并发连接和 RTU 网关转换。
- [industrial/profinet.md](industrial/profinet.md)：PROFINET 设备发现、组态、周期 IO、诊断和实时通信概览。
- [industrial/profinet-practical.md](industrial/profinet-practical.md)：PROFINET 设备命名、GSDML、周期 IO、PLC 诊断和 Wireshark 排查。
- [industrial/profinet-deep-dive.md](industrial/profinet-deep-dive.md)：PROFINET DCP、GSDML、AR/CR、周期 IO、诊断、RT/IRT 和协议栈实现边界。
- [industrial/ethernet-ip.md](industrial/ethernet-ip.md)：EtherNet/IP、CIP 对象模型、显式消息和隐式 IO 概览。
- [industrial/ethernet-ip-practical.md](industrial/ethernet-ip-practical.md)：EtherNet/IP EDS、CIP 对象、Assembly、RPI、显式/隐式消息和抓包调试。
- [industrial/ethernet-ip-deep-dive.md](industrial/ethernet-ip-deep-dive.md)：EtherNet/IP CIP 对象、Encapsulation、Forward Open、Assembly、RPI 和实现边界。
- [industrial/ethernet-tsn.md](industrial/ethernet-tsn.md)：TSN 时间敏感网络、时间同步、调度和确定性以太网概览。
- [industrial/ethernet-tsn-practical.md](industrial/ethernet-tsn-practical.md)：TSN 时间同步、队列调度、Qbv/Qav/Qbu、交换机配置和延迟测量实践。
- [industrial/mqtt.md](industrial/mqtt.md)：MQTT 发布订阅、Topic、QoS、Keepalive 和 IoT 上云场景。
- [industrial/mqtt-practical.md](industrial/mqtt-practical.md)：MQTT Topic 设计、QoS、Keepalive、断线重连、TLS 和网关上云实践。

- [onboard/pcie-practical.md](onboard/pcie-practical.md)：PCIe Root Complex/Endpoint、Lane、配置空间、BAR、MSI/MSI-X、DMA 和 LTSSM。

### 简单设备总线

- [onboard/one-wire-practical.md](onboard/one-wire-practical.md)：1-Wire 上拉、GPIO 时序、ROM ID、DS18B20、寄生供电和多设备搜索。

- [onboard/sdio-practical.md](onboard/sdio-practical.md)：SDIO CLK/CMD/DAT、1-bit/4-bit、Wi-Fi 模块、固件和设备树调试。

- [display/mipi-csi-dsi-debug.md](display/mipi-csi-dsi-debug.md)：MIPI CSI/DSI 电源时序、I2C 初始化、Lane、像素格式和黑屏/无图定位。
- [display/mipi-csi-dsi-deep-dive.md](display/mipi-csi-dsi-deep-dive.md)：MIPI D-PHY、CSI/DSI 初始化、RAW/YUV/RGB、显示时序和图像链路排障。
- [display/display-interfaces.md](display/display-interfaces.md)：SPI、RGB、LVDS、MIPI DSI、eDP、HDMI 显示接口选型概览。
- [display/fpd-link-gmsl.md](display/fpd-link-gmsl.md)：车载视频 SerDes、FPD-Link、GMSL 和远距离摄像头/显示链路。
- [display/fpd-link-gmsl-practical.md](display/fpd-link-gmsl-practical.md)：车载 SerDes 链路锁定、远端 I2C、MIPI 桥接和多摄像头调试。
- [display/fpd-link-gmsl-deep-dive.md](display/fpd-link-gmsl-deep-dive.md)：车载 SerDes 分层模型、反向通道、链路预算、PoC、多摄同步和现场排查。
- [display/hdmi-edp.md](display/hdmi-edp.md)：HDMI/eDP、EDID、AUX、Link Training、外接和嵌入式显示链路。
- [display/hdmi-edp-practical.md](display/hdmi-edp-practical.md)：HDMI/eDP EDID、HPD、DDC、AUX、Link Training、Panel 电源和背光调试。
- [display/hdmi-edp-deep-dive.md](display/hdmi-edp-deep-dive.md)：HDMI/eDP EDID、DPCD、TMDS/Main Link、Link Training、背光和黑屏排查。

## 收录边界

放在 `bus` 的内容通常满足以下条件：

- 已经定义了完整的通信规则，而不只是电气接口。
- 支持多个节点、设备寻址、协议帧、错误处理或标准化设备模型。
- 常用于板间通信、工业控制、车载网络、主机外设连接或系统级互联。

例如：`SPI` 放在 `basic`，但基于 SPI 的 SD 卡协议可放在 `bus`；`CAN PHY` 放在 `basic`，但 `CAN` 和 `CANopen` 放在 `bus`。
