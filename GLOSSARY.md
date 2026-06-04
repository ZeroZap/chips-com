# Communication Glossary

## 目标

本文整理芯片间通信常见术语，作为阅读各协议文档时的统一参考。

## 基础信号

| 术语 | 含义 |
| --- | --- |
| High | 高电平，通常表示逻辑 1，具体电压取决于电平域 |
| Low | 低电平，通常表示逻辑 0 |
| Floating | 浮空，输入没有确定电平，容易乱跳 |
| Pull-up | 上拉，让信号默认变高 |
| Pull-down | 下拉，让信号默认变低 |
| Push-pull | 推挽输出，可主动拉高和拉低 |
| Open-drain | 开漏输出，只能主动拉低，高电平靠上拉 |
| Tri-state | 三态/高阻，设备不驱动信号线 |

## 时序

| 术语 | 含义 |
| --- | --- |
| Clock | 时钟，控制同步通信节奏 |
| Setup Time | 建立时间，数据在采样边沿前需要稳定的时间 |
| Hold Time | 保持时间，数据在采样边沿后需要继续稳定的时间 |
| Rise Time | 上升沿时间 |
| Fall Time | 下降沿时间 |
| Jitter | 抖动，边沿或时钟周期的不稳定变化 |
| Duty Cycle | 占空比，高电平时间占周期比例 |
| Sampling Point | 采样点，接收端读取信号的位置 |

## 串行通信

| 术语 | 含义 |
| --- | --- |
| Baud Rate | 波特率，串行符号速率 |
| Start Bit | 起始位，UART 帧开始标记 |
| Stop Bit | 停止位，UART 帧结束标记 |
| Parity | 校验位，用于简单错误检测 |
| Full-duplex | 全双工，可同时收发 |
| Half-duplex | 半双工，同一时间只能发或收 |
| Simplex | 单工，只能单向通信 |
| LSB First | 低位先发 |
| MSB First | 高位先发 |

## 总线和协议

| 术语 | 含义 |
| --- | --- |
| Bus | 总线，多设备共享的通信介质或协议体系 |
| Address | 地址，用于选择设备或寄存器 |
| Frame | 帧，一次完整协议数据单元 |
| Packet | 包，某些协议中的传输单元 |
| Payload | 有效载荷，协议头尾之外的业务数据 |
| CRC | 循环冗余校验，用于错误检测 |
| Checksum | 校验和，较简单的错误检测 |
| ACK | 应答，表示接收方确认 |
| NACK | 不应答，表示未确认或拒绝 |
| Timeout | 超时，等待事件未在规定时间发生 |
| Retry | 重试，失败后再次尝试通信 |

## 差分信号

| 术语 | 含义 |
| --- | --- |
| Differential Pair | 差分对，用两根线之间的电压差表示信号 |
| Common Mode | 共模，两根差分线共同相对地的电压 |
| Termination | 终端匹配，用于减少反射 |
| Bias | 偏置，让空闲总线保持确定状态 |
| Shielded Twisted Pair | 屏蔽双绞线，提升抗干扰能力 |
| Isolation | 隔离，用于处理地电位差和安全问题 |

## 网络

| 术语 | 含义 |
| --- | --- |
| MAC Address | 以太网链路层地址 |
| IP Address | 网络层地址 |
| ARP | IP 地址到 MAC 地址解析协议 |
| TCP | 可靠字节流传输协议 |
| UDP | 无连接数据报协议 |
| Port | 传输层端口号 |
| Socket | 网络通信端点抽象 |
| MTU | 最大传输单元 |

## 高速接口

| 术语 | 含义 |
| --- | --- |
| Lane | 高速接口中的一条数据通道 |
| PHY | 物理层收发器 |
| Link Training | 链路训练，高速链路建立过程 |
| Equalization | 均衡，补偿高速信号损耗 |
| Eye Diagram | 眼图，用于评估高速信号质量 |
| XIP | Execute In Place，从外部 Flash 直接执行代码 |

## 调试

| 术语 | 含义 |
| --- | --- |
| Logic Analyzer | 逻辑分析仪，用于数字协议解码 |
| Oscilloscope | 示波器，用于观察电气波形 |
| Protocol Analyzer | 协议分析仪，用于抓取复杂协议 |
| Sniffer | 监听器，旁路抓取通信数据 |
| Loopback | 回环测试，发送端和接收端直接闭环验证 |
