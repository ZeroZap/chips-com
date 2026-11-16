# Acronyms

> 按领域分组整理。含有多种含义的缩写会在“含义”列标注上下文。
> 最后更新：2026-11-16

## 通用与调试

| 缩写 | 全称                         | 含义                        |
| ---- | ---------------------------- | --------------------------- |
| GPIO | General Purpose Input/Output | 通用输入输出                |
| PWM  | Pulse Width Modulation       | 脉宽调制                    |
| ADC  | Analog-to-Digital Converter  | 模数转换                    |
| DAC  | Digital-to-Analog Converter  | 数模转换                    |
| DMA  | Direct Memory Access         | 直接内存访问                |
| CRC  | Cyclic Redundancy Check      | 循环冗余校验                |
| EMI  | Electromagnetic Interference | 电磁干扰                    |
| ESD  | Electrostatic Discharge      | 静电放电                    |
| EFT  | Electrical Fast Transient    | 电快速瞬变脉冲群            |
| ACK  | Acknowledgement              | 确认应答                    |
| NACK | Negative Acknowledgement     | 否定应答                    |
| ISR  | Interrupt Service Routine    | 中断服务程序                |
| RTOS | Real-Time Operating System   | 实时操作系统                |
| MCU  | Microcontroller Unit         | 微控制器                    |
| SoC  | System on Chip               | 片上系统                    |
| PCB  | Printed Circuit Board        | 印制电路板                  |
| PMIC | Power Management IC          | 电源管理芯片                |
| TVS  | Transient Voltage Suppressor | 瞬态电压抑制器              |
| FIFO | First In First Out           | 先进先出缓冲                |
| LSB  | Least Significant Bit        | 最低有效位                  |
| MSB  | Most Significant Bit         | 最高有效位                  |
| XIP  | Execute In Place             | 原地执行                    |
| PEC  | Packet Error Checking        | 包错误校验（SMBus / PMBus） |
| IO   | Input/Output                 | 输入输出                    |
| DI   | Digital Input                | 数字输入                    |
| DO   | Digital Output               | 数字输出                    |
| AI   | Analog Input                 | 模拟输入                    |
| AO   | Analog Output                | 模拟输出                    |

## 基础总线与物理层

| 缩写   | 全称                                                    | 含义                                                                    |
| ------ | ------------------------------------------------------- | ----------------------------------------------------------------------- |
| UART   | Universal Asynchronous Receiver/Transmitter             | 通用异步收发器                                                          |
| USART  | Universal Synchronous/Asynchronous Receiver/Transmitter | 通用同步/异步收发器                                                     |
| I2C    | Inter-Integrated Circuit                                | 双线串行总线                                                            |
| SCL    | Serial Clock                                            | 串行时钟（I2C；IEC 61850 语境下也指 Substation Configuration Language） |
| SDA    | Serial Data                                             | 串行数据                                                                |
| SMBus  | System Management Bus                                   | 系统管理总线                                                            |
| PMBus  | Power Management Bus                                    | 电源管理总线                                                            |
| SPI    | Serial Peripheral Interface                             | 串行外设接口                                                            |
| SCLK   | Serial Clock                                            | 串行时钟（SPI）                                                         |
| MOSI   | Master Out Slave In                                     | 主出从入                                                                |
| MISO   | Master In Slave Out                                     | 主入从出                                                                |
| CS     | Chip Select                                             | 片选                                                                    |
| SS     | Slave Select                                            | 从设备选择                                                              |
| NSS    | Negative Slave Select                                   | 低有效片选（STM32 常见命名）                                            |
| CPOL   | Clock Polarity                                          | 时钟极性                                                                |
| CPHA   | Clock Phase                                             | 时钟相位                                                                |
| I2S    | Inter-IC Sound                                          | 音频串行接口                                                            |
| PCM    | Pulse-Code Modulation                                   | 脉冲编码调制                                                            |
| TDM    | Time-Division Multiplexing                              | 时分复用                                                                |
| PDM    | Pulse-Density Modulation                                | 脉冲密度调制                                                            |
| S/PDIF | Sony/Philips Digital Interface                          | 索尼/飞利浦数字音频接口                                                 |
| I3C    | Improved Inter Integrated Circuit                       | I2C 演进总线                                                            |
| SDIO   | Secure Digital Input Output                             | SD I/O 总线                                                             |
| SD     | Secure Digital                                          | 安全数字存储卡                                                          |
| eMMC   | embedded MultiMediaCard                                 | 嵌入式多媒体卡                                                          |
| QSPI   | Quad SPI                                                | 四线 SPI                                                                |
| OSPI   | Octal SPI                                               | 八线 SPI                                                                |
| JTAG   | Joint Test Action Group                                 | 联合测试工作组（调试接口）                                              |
| SWD    | Serial Wire Debug                                       | 串行线调试                                                              |
| SWO    | Serial Wire Output                                      | 串行线输出                                                              |
| RS232  | Recommended Standard 232                                | 串行通信标准                                                            |
| RS485  | Recommended Standard 485                                | 差分串行通信标准                                                        |
| RS422  | Recommended Standard 422                                | 差分串行通信标准                                                        |
| TTL    | Transistor-Transistor Logic                             | 晶体管-晶体管逻辑电平                                                   |
| CMOS   | Complementary Metal-Oxide-Semiconductor                 | 互补金属氧化物半导体电平                                                |
| DE     | Driver Enable                                           | 驱动器使能                                                              |
| RE     | Receiver Enable                                         | 接收器使能                                                              |
| LVDS   | Low-Voltage Differential Signaling                      | 低压差分信号                                                            |

## 汽车 / CAN / 诊断

| 缩写    | 全称                                               | 含义                                                             |
| ------- | -------------------------------------------------- | ---------------------------------------------------------------- |
| CAN     | Controller Area Network                            | 控制器局域网                                                     |
| CAN FD  | CAN Flexible Data-rate                             | 可变数据速率 CAN                                                 |
| CAN XL  | CAN Extra Long                                     | 超长帧 CAN                                                       |
| ECU     | Electronic Control Unit                            | 电子控制单元                                                     |
| ID      | Identifier                                         | 标识符                                                           |
| DLC     | Data Length Code                                   | 数据长度码                                                       |
| RTR     | Remote Transmission Request                        | 远程发送请求                                                     |
| IDE     | Identifier Extension                               | 标识符扩展                                                       |
| BRS     | Bit Rate Switch                                    | 位速率切换                                                       |
| ESI     | Error State Indicator / EtherCAT Slave Information | 错误状态指示（CAN FD）/ EtherCAT 从站描述文件                    |
| FDF     | FD Format Indicator                                | FD 格式指示                                                      |
| TEC     | Transmit Error Counter                             | 发送错误计数器                                                   |
| REC     | Receive Error Counter                              | 接收错误计数器                                                   |
| SJW     | Synchronization Jump Width                         | 同步跳转宽度                                                     |
| DBC     | Database CAN                                       | CAN 数据库文件                                                   |
| PGN     | Parameter Group Number                             | 参数组编号                                                       |
| SPN     | Suspect Parameter Number                           | 可疑参数编号                                                     |
| BAM     | Broadcast Announce Message                         | 广播宣告报文                                                     |
| RTS     | Request To Send                                    | 请求发送                                                         |
| CTS     | Clear To Send                                      | 允许发送                                                         |
| TP      | Transport Protocol                                 | 传输协议                                                         |
| ISO-TP  | ISO Transport Protocol                             | ISO 传输协议                                                     |
| UDS     | Unified Diagnostic Services                        | 统一诊断服务                                                     |
| OBD     | On-Board Diagnostics                               | 车载诊断                                                         |
| WWH-OBD | World-Wide Harmonized OBD                          | 全球统一车载诊断                                                 |
| DTC     | Diagnostic Trouble Code                            | 诊断故障码                                                       |
| DID     | Data Identifier                                    | 数据标识符                                                       |
| NRC     | Negative Response Code                             | 否定响应码                                                       |
| PID     | Parameter Identifier                               | 参数标识符（OBD；控制领域也指 Proportional-Integral-Derivative） |
| OEM     | Original Equipment Manufacturer                    | 原始设备制造商                                                   |
| VIN     | Vehicle Identification Number                      | 车辆识别代号                                                     |
| COB-ID  | Communication Object Identifier                    | 通信对象标识符                                                   |
| EDS     | Electronic Data Sheet                              | 电子数据表（CANopen；EtherCAT 从站描述文件为 ESI）               |
| DCF     | Device Configuration File                          | 设备配置文件                                                     |
| LSS     | Layer Setting Services                             | 层设置服务                                                       |
| CiA     | CAN in Automation                                  | CAN 国际用户与制造商组织                                         |
| LIN     | Local Interconnect Network                         | 本地互联网络                                                     |
| SENT    | Single Edge Nibble Transmission                    | 单边沿半字节传输                                                 |
| PSI5    | Peripheral Sensor Interface 5                      | 外设传感器接口 5                                                 |
| NMT     | Network Management                                 | CANopen 网络管理                                                 |
| EMCY    | Emergency                                          | CANopen 紧急报文                                                 |
| PDO     | Process Data Object                                | CANopen 过程数据对象                                             |
| SDO     | Service Data Object                                | CANopen 服务数据对象                                             |
| WKC     | Working Counter                                    | EtherCAT 工作计数器                                              |

## 工业自动化 / 电力 / 水务 / 楼宇

| 缩写        | 全称                                              | 含义                                                            |
| ----------- | ------------------------------------------------- | --------------------------------------------------------------- |
| RTU         | Remote Terminal Unit                              | 远程终端单元                                                    |
| PLC         | Programmable Logic Controller                     | 可编程逻辑控制器                                                |
| DCS         | Distributed Control System                        | 分布式控制系统                                                  |
| SCADA       | Supervisory Control and Data Acquisition          | 数据采集与监视控制                                              |
| HMI         | Human-Machine Interface                           | 人机界面                                                        |
| IED         | Intelligent Electronic Device                     | 智能电子设备                                                    |
| VFD         | Variable Frequency Drive                          | 变频器                                                          |
| BMS         | Battery Management System                         | 电池管理系统                                                    |
| PDU         | Protocol Data Unit                                | 协议数据单元（电力/工业语境下也可能是 Power Distribution Unit） |
| ASDU        | Application Service Data Unit                     | 应用服务数据单元                                                |
| APCI        | Application Protocol Control Information          | 应用协议控制信息                                                |
| APDU        | Application Protocol Data Unit                    | 应用协议数据单元                                                |
| GOOSE       | Generic Object Oriented Substation Event          | 面向通用对象的变电站事件                                        |
| SV          | Sampled Values                                    | 采样值                                                          |
| MMS         | Manufacturing Message Specification               | 制造报文规范                                                    |
| SCL         | Substation Configuration Language                 | 变电站配置语言（IEC 61850；I2C 语境下为 Serial Clock）          |
| CID         | Configured IED Description                        | 配置后的 IED 描述                                               |
| ICD         | IED Capability Description                        | IED 能力描述                                                    |
| SCD         | Substation Configuration Description              | 变电站配置描述                                                  |
| DNP3        | Distributed Network Protocol version 3            | 分布式网络协议第 3 版                                           |
| IEC         | International Electrotechnical Commission         | 国际电工委员会                                                  |
| MBAP        | Modbus Application Protocol                       | Modbus 应用协议报文头                                           |
| FC          | Function Code                                     | 功能码（Modbus）                                                |
| BACnet      | Building Automation and Control Networks          | 楼宇自动控制网络                                                |
| OPC UA      | Open Platform Communications Unified Architecture | 开放平台通信统一架构                                            |
| CIP         | Common Industrial Protocol                        | 通用工业协议                                                    |
| GSDML       | General Station Description Markup Language       | 通用站描述标记语言                                              |
| PROFINET    | Process Field Network                             | 过程现场网络                                                    |
| PROFIBUS    | Process Field Bus                                 | 过程现场总线                                                    |
| EtherCAT    | Ethernet for Control Automation Technology        | 用于控制自动化技术的以太网                                      |
| EtherNet/IP | Ethernet Industrial Protocol                      | 工业以太网协议                                                  |
| HART        | Highway Addressable Remote Transducer             | 可寻址远程传感器高速通道                                        |
| IRT         | Isochronous Real Time                             | 等时实时                                                        |
| MRP         | Media Redundancy Protocol                         | 介质冗余协议                                                    |
| RT          | Real-Time                                         | 实时                                                            |

## 网络 / 工业以太网 / TSN

| 缩写  | 全称                                        | 含义                              |
| ----- | ------------------------------------------- | --------------------------------- |
| MAC   | Media Access Control                        | 介质访问控制                      |
| PHY   | Physical Layer                              | 物理层                            |
| MII   | Media Independent Interface                 | 媒体独立接口                      |
| RMII  | Reduced Media Independent Interface         | 精简媒体独立接口                  |
| RGMII | Reduced Gigabit Media Independent Interface | 精简千兆媒体独立接口              |
| GMII  | Gigabit Media Independent Interface         | 千兆媒体独立接口                  |
| SGMII | Serial Gigabit Media Independent Interface  | 串行千兆媒体独立接口              |
| MDIO  | Management Data Input/Output                | PHY 管理数据接口                  |
| ARP   | Address Resolution Protocol                 | 地址解析协议                      |
| IP    | Internet Protocol                           | 网络层协议                        |
| TCP   | Transmission Control Protocol               | 可靠传输协议                      |
| UDP   | User Datagram Protocol                      | 用户数据报协议                    |
| HTTP  | Hypertext Transfer Protocol                 | 超文本传输协议                    |
| MQTT  | Message Queuing Telemetry Transport         | 消息队列遥测传输                  |
| CoAP  | Constrained Application Protocol            | 受限应用协议                      |
| QoS   | Quality of Service                          | 服务质量                          |
| VLAN  | Virtual Local Area Network                  | 虚拟局域网                        |
| PCP   | Priority Code Point                         | 优先级代码点                      |
| TSN   | Time-Sensitive Networking                   | 时间敏感网络                      |
| gPTP  | generalized Precision Time Protocol         | 通用精确时间协议（IEEE 802.1AS）  |
| PTP   | Precision Time Protocol                     | 精确时间协议                      |
| Qbv   | Time-Aware Shaper                           | 时间感知整形器（IEEE 802.1Qbv）   |
| Qav   | Credit-Based Shaper                         | 基于信用的整形器（IEEE 802.1Qav） |
| MTU   | Maximum Transmission Unit                   | 最大传输单元                      |
| DHCP  | Dynamic Host Configuration Protocol         | 动态主机配置协议                  |
| DNS   | Domain Name System                          | 域名系统                          |
| NAT   | Network Address Translation                 | 网络地址转换                      |
| ICMP  | Internet Control Message Protocol           | 互联网控制消息协议                |
| PoE   | Power over Ethernet                         | 以太网供电                        |
| AP    | Access Point                                | 无线接入点                        |

## USB / PCIe / 显示

| 缩写     | 全称                                      | 含义                |
| -------- | ----------------------------------------- | ------------------- |
| USB      | Universal Serial Bus                      | 通用串行总线        |
| CDC      | Communications Device Class               | USB 通信设备类      |
| HID      | Human Interface Device                    | USB 人机接口设备    |
| MSC      | Mass Storage Class                        | USB 大容量存储类    |
| OTG      | On-The-Go                                 | USB 角色切换能力    |
| DFU      | Device Firmware Upgrade                   | 设备固件升级        |
| UVC      | USB Video Class                           | USB 视频类          |
| UAC      | USB Audio Class                           | USB 音频类          |
| PCIe     | PCI Express                               | 高速系统互联        |
| RC       | Root Complex                              | PCIe 主机侧         |
| EP       | Endpoint                                  | PCIe 设备侧         |
| BAR      | Base Address Register                     | PCIe 基地址寄存器   |
| MSI      | Message Signaled Interrupt                | PCIe 消息中断       |
| MSI-X    | MSI Extended                              | 扩展消息中断        |
| LTSSM    | Link Training and Status State Machine    | PCIe 链路训练状态机 |
| TLP      | Transaction Layer Packet                  | 事务层数据包        |
| DLLP     | Data Link Layer Packet                    | 数据链路层数据包    |
| AER      | Advanced Error Reporting                  | 高级错误报告        |
| REFCLK   | Reference Clock                           | 参考时钟            |
| PERST#   | PCI Express Reset                         | PCIe 复位信号       |
| MIPI     | Mobile Industry Processor Interface       | 移动产业处理器接口  |
| CSI      | Camera Serial Interface                   | 摄像头串行接口      |
| DSI      | Display Serial Interface                  | 显示串行接口        |
| D-PHY    | MIPI D-PHY                                | MIPI 常见物理层     |
| C-PHY    | MIPI C-PHY                                | MIPI 高速物理层     |
| VC       | Virtual Channel                           | 虚拟通道            |
| DT       | Data Type                                 | 数据类型            |
| ISP      | Image Signal Processor                    | 图像信号处理器      |
| V4L2     | Video for Linux 2                         | Linux 视频子系统    |
| HDMI     | High-Definition Multimedia Interface      | 高清多媒体接口      |
| eDP      | Embedded DisplayPort                      | 嵌入式显示端口      |
| DP       | DisplayPort                               | 显示端口            |
| EDID     | Extended Display Identification Data      | 扩展显示标识数据    |
| HDCP     | High-bandwidth Digital Content Protection | 高带宽数字内容保护  |
| DDC      | Display Data Channel                      | 显示数据通道        |
| FPD-Link | Flat Panel Display Link                   | 平板显示链路        |
| GMSL     | Gigabit Multimedia Serial Link            | 千兆多媒体串行链路  |
| RGB      | Red Green Blue                            | 红绿蓝              |
| TFT      | Thin Film Transistor                      | 薄膜晶体管          |
| OLED     | Organic Light-Emitting Diode              | 有机发光二极管      |
| HDR      | High Dynamic Range                        | 高动态范围          |

## 无线 / IoT / 卫星

| 缩写    | 全称                                          | 含义                                                            |
| ------- | --------------------------------------------- | --------------------------------------------------------------- |
| BLE     | Bluetooth Low Energy                          | 低功耗蓝牙                                                      |
| BR/EDR  | Basic Rate/Enhanced Data Rate                 | 基本速率/增强数据速率                                           |
| GAP     | Generic Access Profile                        | 通用访问配置文件                                                |
| GATT    | Generic Attribute Profile                     | 通用属性配置文件                                                |
| ATT     | Attribute Protocol                            | 属性协议                                                        |
| L2CAP   | Logical Link Control and Adaptation Protocol  | 逻辑链路控制与适配协议                                          |
| HCI     | Host Controller Interface                     | 主机控制器接口                                                  |
| SIG     | Bluetooth Special Interest Group              | 蓝牙技术联盟                                                    |
| ZCL     | ZigBee Cluster Library                        | ZigBee 簇库                                                     |
| ZDO     | ZigBee Device Object                          | ZigBee 设备对象                                                 |
| PAN     | Personal Area Network                         | 个人区域网络                                                    |
| LoRa    | Long Range                                    | 远距离无线调制                                                  |
| LoRaWAN | LoRa Wide Area Network                        | LoRa 广域网                                                     |
| SF      | Spreading Factor                              | 扩频因子                                                        |
| ADR     | Adaptive Data Rate                            | 自适应数据速率                                                  |
| OTAA    | Over-The-Air Activation                       | 空中激活                                                        |
| ABP     | Activation By Personalization                 | 个性化激活                                                      |
| EUI     | Extended Unique Identifier                    | 扩展唯一标识符                                                  |
| RSSI    | Received Signal Strength Indicator            | 接收信号强度指示                                                |
| SNR     | Signal-to-Noise Ratio                         | 信噪比                                                          |
| LQI     | Link Quality Indicator                        | 链路质量指示                                                    |
| LTE     | Long Term Evolution                           | 长期演进（4G）                                                  |
| NB-IoT  | Narrowband Internet of Things                 | 窄带物联网                                                      |
| Cat-M1  | LTE Category M1                               | LTE M1 类别                                                     |
| Cat-1   | LTE Category 1                                | LTE 1 类别                                                      |
| eMTC    | enhanced Machine-Type Communication           | 增强型机器通信                                                  |
| PSM     | Power Saving Mode                             | 省电模式（蜂窝 IoT；协议解析语境下也指 Protocol State Machine） |
| eDRX    | extended Discontinuous Reception              | 扩展非连续接收                                                  |
| APN     | Access Point Name                             | 接入点名称                                                      |
| SIM     | Subscriber Identity Module                    | 用户识别模块                                                    |
| GNSS    | Global Navigation Satellite System            | 全球导航卫星系统                                                |
| GPS     | Global Positioning System                     | 全球定位系统                                                    |
| NTN     | Non-Terrestrial Network                       | 非地面网络                                                      |
| LEO     | Low Earth Orbit                               | 低地球轨道                                                      |
| GEO     | Geostationary Earth Orbit                     | 地球静止轨道                                                    |
| RDSS    | Radio Determination Satellite Service         | 卫星无线电测定业务（北斗短报文）                                |
| PLB     | Personal Locator Beacon                       | 个人定位信标                                                    |
| EPIRB   | Emergency Position Indicating Radio Beacon    | 应急无线电示位标                                                |
| SARSAT  | Search and Rescue Satellite-Aided Tracking    | 搜索救援卫星辅助跟踪                                            |
| COSPAS  | Cosmicheskaya Sistema Poiska Avariynykh Sudov | 空间救援遇险船只搜索系统                                        |
| SBD     | Short Burst Data                              | 短突发数据（Iridium）                                           |
| SOS     | Save Our Souls                                | 国际求救信号（非严格缩写）                                      |
| AIS     | Automatic Identification System               | 船舶自动识别系统                                                |
| NFC     | Near Field Communication                      | 近场通信                                                        |
| RFID    | Radio Frequency Identification                | 射频识别                                                        |
| UWB     | Ultra-Wideband                                | 超宽带                                                          |

## 标准与组织

| 缩写  | 全称                                                  | 含义                       |
| ----- | ----------------------------------------------------- | -------------------------- |
| ISO   | International Organization for Standardization        | 国际标准化组织             |
| SAE   | Society of Automotive Engineers                       | 国际自动机工程师学会       |
| IEEE  | Institute of Electrical and Electronics Engineers     | 电气与电子工程师协会       |
| 3GPP  | 3rd Generation Partnership Project                    | 第三代合作伙伴计划         |
| ITU   | International Telecommunication Union                 | 国际电信联盟               |
| IETF  | Internet Engineering Task Force                       | 互联网工程任务组           |
| CISPR | International Special Committee on Radio Interference | 国际无线电干扰特别委员会   |
| UNECE | United Nations Economic Commission for Europe         | 联合国欧洲经济委员会       |
| DL/T  | 电力行业标准                                          | 中国电力行业推荐性标准     |
| CJ/T  | 城镇建设行业标准                                      | 中国城镇建设行业推荐性标准 |
| HJ    | 环境保护行业标准                                      | 中国环境保护行业标准       |
| SL    | 水利行业标准                                          | 中国水利行业标准           |

## 常见标准编号

| 编号            | 名称                                                            | 适用领域               |
| --------------- | --------------------------------------------------------------- | ---------------------- |
| ISO 11898       | Road vehicles — Controller area network (CAN)                   | CAN 物理层与数据链路层 |
| ISO 14229       | Road vehicles — Unified diagnostic services (UDS)               | 统一诊断服务           |
| ISO 15765       | Road vehicles — Diagnostic communication over CAN (DoCAN)       | CAN 上的诊断传输       |
| ISO 26262       | Road vehicles — Functional safety                               | 汽车功能安全           |
| ISO 21434       | Road vehicles — Cybersecurity engineering                       | 汽车网络安全           |
| SAE J1939       | Serial Control and Communications Heavy Duty Vehicle Network    | 商用车 CAN 应用层      |
| SAE J1979       | E/E Diagnostic Test Modes                                       | OBD-II 诊断服务        |
| IEC 60870-5-101 | Telecontrol equipment and systems — Transmission protocols      | 串行远动通信           |
| IEC 60870-5-104 | Telecontrol equipment and systems — Network access              | 以太网远动通信         |
| IEC 61850       | Communication networks and systems for power utility automation | 变电站自动化           |
| IEEE 802.1AS    | Timing and Synchronization                                      | gPTP 时间同步          |
| IEEE 802.1Q     | Bridges and Bridged Networks                                    | VLAN、QoS、TSN         |
| IEEE 802.3      | Ethernet                                                        | 以太网                 |
| IEEE 802.15.4   | Low-Rate Wireless Networks                                      | ZigBee、Thread 等底层  |
