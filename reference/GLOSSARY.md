---
tags:
  - layer/reference
  - type/reference
---

# Communication Glossary

## 目标

本文整理芯片间通信常见术语，作为阅读各协议文档时的统一参考。

## 基础信号

| 术语       | 含义                                         |
| ---------- | -------------------------------------------- |
| High       | 高电平，通常表示逻辑 1，具体电压取决于电平域 |
| Low        | 低电平，通常表示逻辑 0                       |
| Floating   | 浮空，输入没有确定电平，容易乱跳             |
| Pull-up    | 上拉，让信号默认变高                         |
| Pull-down  | 下拉，让信号默认变低                         |
| Push-pull  | 推挽输出，可主动拉高和拉低                   |
| Open-drain | 开漏输出，只能主动拉低，高电平靠上拉         |
| Tri-state  | 三态/高阻，设备不驱动信号线                  |

## 时序

| 术语           | 含义                                         |
| -------------- | -------------------------------------------- |
| Clock          | 时钟，控制同步通信节奏                       |
| Setup Time     | 建立时间，数据在采样边沿前需要稳定的时间     |
| Hold Time      | 保持时间，数据在采样边沿后需要继续稳定的时间 |
| Rise Time      | 上升沿时间                                   |
| Fall Time      | 下降沿时间                                   |
| Jitter         | 抖动，边沿或时钟周期的不稳定变化             |
| Duty Cycle     | 占空比，高电平时间占周期比例                 |
| Sampling Point | 采样点，接收端读取信号的位置                 |

## 串行通信

| 术语        | 含义                       |
| ----------- | -------------------------- |
| Baud Rate   | 波特率，串行符号速率       |
| Start Bit   | 起始位，UART 帧开始标记    |
| Stop Bit    | 停止位，UART 帧结束标记    |
| Parity      | 校验位，用于简单错误检测   |
| Full-duplex | 全双工，可同时收发         |
| Half-duplex | 半双工，同一时间只能发或收 |
| Simplex     | 单工，只能单向通信         |
| LSB First   | 低位先发                   |
| MSB First   | 高位先发                   |

## 总线和协议

| 术语     | 含义                                 |
| -------- | ------------------------------------ |
| Bus      | 总线，多设备共享的通信介质或协议体系 |
| Address  | 地址，用于选择设备或寄存器           |
| Frame    | 帧，一次完整协议数据单元             |
| Packet   | 包，某些协议中的传输单元             |
| Payload  | 有效载荷，协议头尾之外的业务数据     |
| CRC      | 循环冗余校验，用于错误检测           |
| Checksum | 校验和，较简单的错误检测             |
| ACK      | 应答，表示接收方确认                 |
| NACK     | 不应答，表示未确认或拒绝             |
| Timeout  | 超时，等待事件未在规定时间发生       |
| Retry    | 重试，失败后再次尝试通信             |

## 差分信号

| 术语                  | 含义                                 |
| --------------------- | ------------------------------------ |
| Differential Pair     | 差分对，用两根线之间的电压差表示信号 |
| Common Mode           | 共模，两根差分线共同相对地的电压     |
| Termination           | 终端匹配，用于减少反射               |
| Bias                  | 偏置，让空闲总线保持确定状态         |
| Shielded Twisted Pair | 屏蔽双绞线，提升抗干扰能力           |
| Isolation             | 隔离，用于处理地电位差和安全问题     |

## 网络

| 术语        | 含义                       |
| ----------- | -------------------------- |
| MAC Address | 以太网链路层地址           |
| IP Address  | 网络层地址                 |
| ARP         | IP 地址到 MAC 地址解析协议 |
| TCP         | 可靠字节流传输协议         |
| UDP         | 无连接数据报协议           |
| Port        | 传输层端口号               |
| Socket      | 网络通信端点抽象           |
| MTU         | 最大传输单元               |

## 高速接口

| 术语          | 含义                                        |
| ------------- | ------------------------------------------- |
| Lane          | 高速接口中的一条数据通道                    |
| PHY           | 物理层收发器                                |
| Link Training | 链路训练，高速链路建立过程                  |
| Equalization  | 均衡，补偿高速信号损耗                      |
| Eye Diagram   | 眼图，用于评估高速信号质量                  |
| XIP           | Execute In Place，从外部 Flash 直接执行代码 |

## 调试

| 术语              | 含义                                 |
| ----------------- | ------------------------------------ |
| Logic Analyzer    | 逻辑分析仪，用于数字协议解码         |
| Oscilloscope      | 示波器，用于观察电气波形             |
| Protocol Analyzer | 协议分析仪，用于抓取复杂协议         |
| Sniffer           | 监听器，旁路抓取通信数据             |
| Loopback          | 回环测试，发送端和接收端直接闭环验证 |

## 协议机制

| 术语                   | 含义                                               |
| ---------------------- | -------------------------------------------------- |
| Wired-AND              | 线与逻辑，任一设备拉低则整条线为低                 |
| Arbitration            | 仲裁，多主设备竞争总线时决定优先级                 |
| Clock Stretching       | 时钟拉伸，从设备拉低 SCL 延长事务                  |
| Repeated START         | 重复起始，在不释放总线的情况下开始新事务           |
| ACK / NACK             | 应答 / 非应答，接收方确认或拒绝数据                |
| Bus Recovery           | 总线恢复，通过时钟脉冲和 STOP 条件释放被拉死的总线 |
| 7-bit / 10-bit Address | I2C 的 7 位 / 10 位从设备地址                      |
| CPOL / CPHA            | SPI 时钟极性与时钟相位                             |
| Chip Select            | 片选，选中某个 SPI 从设备                          |
| Dummy Cycle            | 空周期，等待器件输出有效数据所需的额外时钟         |
| Daisy Chain            | 菊花链，多个器件串行连接                           |
| Multi-drop             | 多点共享，多设备挂接在同一条总线上                 |
| Baud Rate Error        | 波特率误差，收发双方速率偏差                       |
| Oversampling           | 过采样，在一个位时间内多次采样                     |
| Framing Error          | 帧错误，起始位、停止位或帧结构不合法               |
| Overrun                | 溢出，接收缓冲未及时读取导致数据丢失               |
| Flow Control           | 流控，通过硬件或软件信号控制发送节奏               |
| Inter-frame Gap        | 帧间隔，两帧之间必须保持的空闲时间                 |
| Dominant / Recessive   | 显性 / 隐性，CAN 差分总线上的两种逻辑状态          |
| Bit Stuffing           | 位填充，连续同电平位后插入反相位                   |
| Bit Timing             | 位时序，CAN 一个位时间内的分段与采样安排           |
| SJW                    | 同步跳转宽度，用于吸收时钟偏差                     |
| TEC / REC              | 发送 / 接收错误计数器                              |
| Bus Off                | 总线关闭，节点错误计数超限后退出总线               |
| Error Frame            | 错误帧，节点检测到错误时发出的特殊帧               |
| Remote Frame           | 远程帧，请求其他节点发送指定标识符的数据           |
| DLC                    | 数据长度码，表示 CAN 帧数据段长度                  |
| BRS                    | 位速率切换，CAN FD 数据段切换到更高速率            |
| PGN / SPN              | J1939 参数组编号 / 可疑参数编号                    |
| DTC                    | 诊断故障码                                         |
| PDO / SDO              | CANopen 过程数据对象 / 服务数据对象                |
| NMT                    | CANopen 网络管理                                   |
| EMCY                   | CANopen 紧急报文                                   |
| Object Dictionary      | 对象字典，CANopen 设备参数和数据的统一索引         |
| COB-ID                 | 通信对象标识符，CANopen 报文标识符                 |
| Heartbeat              | 心跳，节点周期性上报存活状态                       |
| SYNC                   | CANopen 同步对象，用于周期同步                     |

## 工业与电力

| 术语              | 含义                                                     |
| ----------------- | -------------------------------------------------------- |
| Master / Slave    | 主站 / 从站，主站发起事务，从站响应                      |
| Polling           | 轮询，主站按顺序逐个访问从站                             |
| Function Code     | 功能码，Modbus 中定义操作类型                            |
| Register          | 寄存器，Modbus 数据的基本寻址单位                        |
| Coil              | 线圈，Modbus 可读写布尔量                                |
| Discrete Input    | 离散输入，Modbus 只读布尔量                              |
| Holding Register  | 保持寄存器，Modbus 可读写 16 位寄存器                    |
| Input Register    | 输入寄存器，Modbus 只读 16 位寄存器                      |
| MBAP              | Modbus TCP 应用协议报文头                                |
| ASDU              | 应用服务数据单元，IEC 60870 / IEC 61850 中的业务数据单元 |
| APDU              | 应用协议数据单元                                         |
| Telemetry         | 遥测，采集并上传模拟量或状态量                           |
| Teleindication    | 遥信，上传开关量状态                                     |
| Telecontrol       | 遥控，下发开关控制命令                                   |
| Setpoint          | 遥调，下发设定值                                         |
| IED               | 智能电子设备，变电站自动化中的保护、测控装置             |
| GOOSE             | 面向通用对象的变电站事件，用于快速状态传递               |
| SV                | 采样值，用于传输电流、电压采样数据                       |
| MMS               | 制造报文规范，IEC 61850 的客户端/服务器通信              |
| RTU               | 远程终端单元，现场数据采集与控制设备                     |
| PLC               | 可编程逻辑控制器                                         |
| SCADA             | 数据采集与监视控制系统                                   |
| HMI               | 人机界面                                                 |
| Gateway           | 网关，完成协议转换、点位映射和链路隔离                   |
| Point Table       | 点表，描述设备点位、地址、类型和缩放关系                 |
| Deadband          | 死区，变化量未超过阈值时不上报                           |
| Time Sync         | 对时，统一现场设备的时间基准                             |
| SOE               | 事件顺序记录，按毫秒级时间戳记录状态变化                 |
| Store-and-forward | 存储转发，先完整接收再转发                               |
| Polling Cycle     | 轮询周期，主站完成一轮从站访问的时间                     |

## 无线与 IoT

| 术语             | 含义                                              |
| ---------------- | ------------------------------------------------- |
| Advertising      | 广播，设备主动发送可被发现的数据包                |
| Scanning         | 扫描，监听周围广播或信标                          |
| Connection       | 连接，主从设备建立会话后的数据通道                |
| GATT             | 通用属性配置文件，BLE 服务与特征的数据模型        |
| ATT              | 属性协议，BLE 客户端/服务器读写属性的基础协议     |
| Service          | 服务，BLE 中一组相关特征的集合                    |
| Characteristic   | 特征，BLE 中可读写的值与描述符集合                |
| Descriptor       | 描述符，描述特征值的附加信息                      |
| Beacon           | 信标，周期性广播固定信息的低功耗设备              |
| PAN              | 个人区域网络                                      |
| Coordinator      | 协调器，ZigBee 网络中负责建网和管理的节点         |
| Router           | 路由器，ZigBee 网络中转发数据的节点               |
| End Device       | 终端设备，ZigBee 网络中低功耗叶子节点             |
| Border Router    | 边界路由器，连接 Thread 网络与外部 IP 网络        |
| Commissioner     | 调试器，负责将设备加入 Matter/Thread 网络         |
| Fabric           | Matter 网络织物，一组受同一信任根管理的设备集合   |
| Spreading Factor | 扩频因子，LoRa 中决定速率、距离和抗干扰能力的参数 |
| Coding Rate      | 编码率，LoRa 前向纠错编码比例                     |
| ADR              | 自适应数据速率，网络根据链路质量调整终端速率      |
| OTAA             | 空中激活，LoRaWAN 设备通过入网流程获取会话密钥    |
| ABP              | 个性化激活，LoRaWAN 设备预置密钥直接入网          |
| Duty Cycle Limit | 占空比限制，无线法规对发射占空比的约束            |
| RSSI             | 接收信号强度指示                                  |
| SNR              | 信噪比                                            |
| LQI              | 链路质量指示                                      |
| PSM              | 省电模式，蜂窝 IoT 终端长时间休眠                 |
| eDRX             | 扩展非连续接收，降低蜂窝 IoT 终端监听功耗         |
| NTN              | 非地面网络，卫星或高空平台参与的 3GPP 网络        |
| LEO              | 低地球轨道                                        |
| GEO              | 地球静止轨道                                      |
| Short Message    | 短报文，北斗等卫星系统的简短消息业务              |
| PLB              | 个人定位信标                                      |
| EPIRB            | 应急无线电示位标                                  |
| AIS              | 船舶自动识别系统                                  |
| GNSS             | 全球导航卫星系统                                  |
| Ephemeris        | 星历，卫星轨道与时钟参数                          |
| Fix              | 定位解，接收机计算出的位置、速度和时间            |
| TTFF             | 首次定位时间，Time To First Fix                   |

## 时间同步与网络

| 术语              | 含义                                   |
| ----------------- | -------------------------------------- |
| Deterministic     | 确定性，最坏情况延迟和抖动有上界       |
| Best Effort       | 尽力而为，不保证带宽、延迟和丢包       |
| gPTP              | 通用精确时间协议，IEEE 802.1AS         |
| PTP               | 精确时间协议，IEEE 1588                |
| Grandmaster       | 主时钟，时间同步域的根时钟             |
| Boundary Clock    | 边界时钟，逐跳终结并重新生成同步时间   |
| Transparent Clock | 透明时钟，测量并补偿报文驻留时间       |
| VLAN              | 虚拟局域网，按逻辑划分广播域           |
| PCP               | 优先级代码点，VLAN 标签中的 3 位优先级 |
| Qbv               | 时间感知整形，按时间门控队列发送       |
| Qav               | 基于信用的整形，为音视频流提供带宽保障 |
| Frame Preemption  | 帧抢占，高优先级帧中断低优先级帧传输   |
| Redundancy        | 冗余，链路或设备故障时仍可通信         |
| MRP               | 介质冗余协议，工业环网冗余             |
| RSTP              | 快速生成树协议，以太网环路防环         |
| QoS               | 服务质量，按优先级调度和保障网络流     |
| Latency           | 延迟，数据从发送到接收的时间           |
| P99 / P999        | 99% / 99.9% 分位延迟，用于衡量尾延迟   |
| Fragmentation     | 分片，将超过 MTU 的报文拆分传输        |
| Firewall          | 防火墙，按规则过滤网络流量             |

## 显示与高速链路

| 术语            | 含义                                            |
| --------------- | ----------------------------------------------- |
| D-PHY / C-PHY   | MIPI 的两种物理层                               |
| CSI / DSI       | MIPI 摄像头串行接口 / 显示串行接口              |
| Virtual Channel | 虚拟通道，在同一条链路上复用多路数据            |
| Data Type       | 数据类型，MIPI 包中标识像素格式或命令           |
| Blanking        | 消隐，有效像素之外的水平和垂直空闲区            |
| Pixel Clock     | 像素时钟，显示控制器输出像素的节拍              |
| EDID            | 扩展显示标识数据，显示器能力描述                |
| DDC             | 显示数据通道，读取 EDID 和控制显示器的低速总线  |
| HDCP            | 高带宽数字内容保护                              |
| PoC             | Power over Coax，同轴电缆同时传输电源和高速信号 |
| Link Lock       | 链路锁定，SerDes 接收端完成时钟和数据对齐       |
| SerDes          | 串行器 / 解串器                                 |
| Pre-emphasis    | 预加重，发送端增强高频分量补偿损耗              |
| Insertion Loss  | 插入损耗，信号经过信道后的幅度衰减              |
| Return Loss     | 回波损耗，阻抗不匹配导致的反射程度              |
| TDR             | 时域反射，用于定位阻抗不连续点和线缆故障        |
| Eye Mask        | 眼图模板，判定信号质量是否满足规范的区域        |
| BER             | 误码率，错误比特数与总比特数之比                |
| PRBS            | 伪随机二进制序列，用于高速链路压力测试          |

## 安全与测试

| 术语                   | 含义                                                                         |
| ---------------------- | ---------------------------------------------------------------------------- |
| Secure Boot            | 安全启动，逐级校验固件签名后执行                                             |
| Secure Access          | 安全访问，通过 Seed/Key 或证书获得诊断权限                                   |
| Seed / Key             | 种子 / 密钥，诊断安全访问的挑战响应机制                                      |
| Replay                 | 重放攻击，重复发送截获的合法报文                                             |
| Rollback               | 回滚，将固件恢复到旧版本                                                     |
| Anti-rollback          | 防回滚，阻止降级到存在漏洞的旧版本                                           |
| Message Authentication | 消息认证，验证报文来源和完整性                                               |
| MAC                    | Message Authentication Code，消息认证码；网络语境下也指 Media Access Control |
| Nonce                  | 随机数，防止重放和保证新鲜性                                                 |
| Fail-safe              | 失效安全，故障时进入安全状态                                                 |
| Watchdog               | 看门狗，监测程序或通信是否卡死                                               |
| Fault Injection        | 故障注入，主动制造错误验证系统恢复能力                                       |
| FMEA                   | 失效模式与影响分析                                                           |
| FTA                    | 故障树分析                                                                   |
| MTBF                   | 平均无故障时间                                                               |
| FIT                    | 每十亿小时的失效次数                                                         |
| HALT / HASS            | 高加速寿命试验 / 高加速应力筛选                                              |
| DUT / UUT              | 被测设备 / 被测单元                                                          |
| Test Fixture           | 测试治具，用于固定、供电和自动测量的装置                                     |
| Golden Sample          | 黄金样本，作为比对基准的已知良好样机                                         |
| Soak Test              | 浸泡测试，长时间持续运行以暴露累积问题                                       |
| Regression             | 回归测试，验证修改未破坏既有功能                                             |

## 关联文档

- [ACRONYMS](ACRONYMS.md)：缩写与标准编号速查。
- [STANDARDS](STANDARDS.md)：标准编号、范围与对应文档。
- [TOOLS](TOOLS.md)：测量、抓包和自动化工具。
- [DOC_TEMPLATES](DOC_TEMPLATES.md)：文档结构模板。
- [知识库索引](../INDEX.md)：按协议查找正文。
