# Bus And Protocols

`bus` 用于整理建立在基础通信接口之上的成熟总线、协议或网络体系。这里的重点是拓扑结构、寻址、帧格式、协议状态机、错误处理和多设备协作。

## 建议分类

### 基于串口/差分链路的总线

- `modbus.md`：Modbus RTU/TCP、寄存器模型、功能码、主从通信。
- `modbus-tcp-deep-dive.md`：Modbus TCP MBAP、事务 ID、Unit ID、并发连接和 RTU 网关转换。
- `rs485-modbus-rtu-practical.md`：RS485 方向控制、终端/偏置、Modbus RTU 帧、CRC 和调试流程。
- `rs485-modbus-rtu-deep-dive.md`：RS485 半双工、隔离防护、帧间隔、寄存器偏移、主站轮询和现场排障。
- `dmx512.md`：灯光控制总线、帧结构、单向广播。
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
- `ethercat.md`：实时工业以太网、从站级联、分布式时钟。
- `ethercat-deep-dive.md`：EtherCAT 主站/从站、ESC、On-the-fly、过程数据、Mailbox、DC 和 WKC。
- `j1939.md`：商用车 CAN 上层协议、PGN、SPN 和多包传输概览。
- `uds.md`：车载统一诊断服务、DID、安全访问、刷写和 ISO-TP 概览。

### 通用高速总线与网络

- `usb.md`：USB 设备枚举、端点、传输类型、主机控制。
- `usb-practical.md`：USB Host/Device、枚举、描述符、Endpoint、CDC/HID/MSC 和 Type-C 基础。
- `usb-deep-dive.md`：USB 标准请求、描述符层级、复合设备、CDC/HID/MSC 和枚举排障。
- `usb-dfu.md`：USB 固件升级、DFU 模式、分块下载、校验和 bootloader 保护。
- `usb-dfu-practical.md`：USB DFU 工程升级流程、分区、校验、回滚和防变砖策略。
- `ethernet.md`：以太网 MAC/PHY、帧、交换、TCP/IP 入口。
- `ethernet-deep-dive.md`：Ethernet MAC/PHY、RMII/RGMII、MDIO、帧、ARP、TCP/UDP 和 Wireshark 排障。
- `ethernet-modbus-tcp-practical.md`：Ethernet 链路、TCP 字节流、Modbus TCP MBAP 和 Wireshark 调试。
- `industrial-ethernet-comparison.md`：Modbus TCP、PROFINET、EtherNet/IP、EtherCAT 对比和选型。
- `modbus-tcp-deep-dive.md`：Modbus TCP MBAP、事务 ID、Unit ID、并发连接和 RTU 网关转换。
- `profinet.md`：PROFINET 设备发现、组态、周期 IO、诊断和实时通信概览。
- `profinet-practical.md`：PROFINET 设备命名、GSDML、周期 IO、PLC 诊断和 Wireshark 排查。
- `ethernet-ip.md`：EtherNet/IP、CIP 对象模型、显式消息和隐式 IO 概览。
- `ethernet-ip-practical.md`：EtherNet/IP EDS、CIP 对象、Assembly、RPI、显式/隐式消息和抓包调试。
- `ethernet-tsn.md`：TSN 时间敏感网络、时间同步、调度和确定性以太网概览。
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
- `hdmi-edp.md`：HDMI/eDP、EDID、AUX、Link Training、外接和嵌入式显示链路。

## 收录边界

放在 `bus` 的内容通常满足以下条件：

- 已经定义了完整的通信规则，而不只是电气接口。
- 支持多个节点、设备寻址、协议帧、错误处理或标准化设备模型。
- 常用于板间通信、工业控制、车载网络、主机外设连接或系统级互联。

例如：`SPI` 放在 `basic`，但基于 SPI 的 SD 卡协议可放在 `bus`；`CAN PHY` 放在 `basic`，但 `CAN` 和 `CANopen` 放在 `bus`。
