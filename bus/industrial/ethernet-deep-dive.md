# Ethernet Deep Dive

## 目标

本文深入 Ethernet 工程细节，重点覆盖 MAC/PHY、MII/RMII/RGMII、MDIO/MDC、以太网帧、MAC 地址、ARP、IP/TCP/UDP、TCP 字节流、嵌入式网口硬件、Wireshark 排障和常见网络问题。

## Ethernet 的分层位置

常见网络通信分层：

```text
应用层：HTTP / MQTT / Modbus TCP / 自定义协议
传输层：TCP / UDP
网络层：IP
链路层：Ethernet
物理层：PHY / 磁性器件 / RJ45 / 网线
```

Ethernet 不是 TCP/IP。

TCP/IP 经常跑在 Ethernet 上。

## MAC 和 PHY

嵌入式 Ethernet 最重要的硬件概念：

```text
MAC
PHY
```

`MAC` 负责：

- 以太网帧收发。
- MAC 地址过滤。
- FCS/CRC 处理。
- DMA 和内存交互。
- 与 TCP/IP 协议栈连接。

`PHY` 负责：

- 物理编码。
- 差分信号驱动。
- 链路检测。
- 自动协商。
- 速率和双工协商。
- 与磁性器件和网线连接。

典型结构：

```text
MCU/SoC MAC <-> PHY <-> Magnetics <-> RJ45 <-> Cable
```

很多 MCU 只有 MAC，没有 PHY。

## MAC-PHY 接口

常见接口：

| 接口 | 常见速率 | 特点 |
| --- | --- | --- |
| MII | 10/100M | 引脚较多 |
| RMII | 10/100M | 引脚较少，常用 50 MHz |
| RGMII | 10/100/1000M | 千兆常见，时序要求高 |
| SGMII | 1G 及以上 | 串行高速接口 |

MCU 常见组合：

```text
STM32 MAC + RMII PHY
```

SoC 千兆网口常见：

```text
MAC + RGMII PHY
```

## RMII 关键点

RMII 常用 50 MHz 参考时钟。

时钟来源可能是：

```text
外部晶振/振荡器同时给 MAC 和 PHY
PHY 输出 50 MHz 给 MAC
MAC 输出 50 MHz 给 PHY
```

必须按芯片手册确认。

RMII 常见问题：

- 50 MHz 时钟方向错。
- 时钟质量差。
- PHY strap 配置和软件不一致。
- CRS_DV/RX/TX 信号复用错误。
- PCB 走线过长或串扰。

## RGMII 关键点

RGMII 用于千兆常见。

它对时序更敏感，涉及：

- TX/RX clock delay。
- PHY internal delay。
- PCB 走线长度。
- 时钟和数据 skew。
- 1.8V/2.5V/3.3V 电平域。

常见坑：

```text
MAC 和 PHY 都开了 delay，导致双重延迟
MAC 和 PHY 都没开 delay，导致采样错位
设备树 phy-mode 配错
```

## MDIO/MDC

MAC 通过 MDIO/MDC 管理 PHY。

```text
MDC：管理时钟
MDIO：双向管理数据
```

可读取或配置：

- PHY ID。
- Link 状态。
- 协商结果。
- 速率。
- 双工模式。
- 自协商控制。
- PHY 复位。

如果 MDIO/MDC 不通，软件通常无法识别 PHY。

排查重点：

- PHY 地址 strap。
- MDIO 上拉。
- MDC 频率。
- 复位时序。
- 驱动指定的 PHY 地址。

## PHY 地址

PHY 地址通常由硬件 strap 引脚决定。

软件可能：

```text
固定指定 PHY address
扫描 MDIO bus
```

常见问题：

```text
硬件 strap 是地址 1
软件驱动找地址 0
结果 MDIO 读不到 PHY
```

调试建议：

```text
扫描全部 PHY 地址
读取 PHY ID 寄存器
确认 strap 与驱动一致
```

## 磁性器件和 RJ45

以太网双绞线接口通常需要磁性器件。

可能形式：

```text
独立网络变压器
集成磁性器件 RJ45 MagJack
```

注意：

- RJ45 不等于 PHY。
- MagJack 也不等于 PHY。
- 中心抽头连接方式要按 PHY 参考设计。
- ESD/浪涌保护要匹配高速信号。

## Ethernet Frame

简化以太网帧结构：

```text
Destination MAC
Source MAC
EtherType / Length
Payload
FCS
```

常见 EtherType：

```text
0x0800：IPv4
0x0806：ARP
0x86DD：IPv6
```

MAC 硬件通常自动处理 FCS，软件抓包一般看不到 FCS。

## MAC 地址

MAC 地址是链路层地址，48-bit。

写法：

```text
00:11:22:33:44:55
```

广播 MAC：

```text
FF:FF:FF:FF:FF:FF
```

正式产品必须保证 MAC 地址唯一。

MAC 地址重复会导致：

- ARP 混乱。
- 交换机学习表错误。
- 数据发错设备。
- 间歇性通信异常。

## ARP

ARP 用于把 IPv4 地址解析成 MAC 地址。

流程：

```text
谁是 192.168.1.20？请告诉 192.168.1.10
目标设备回复自己的 MAC
发送方缓存 IP->MAC 映射
```

如果 ping 不通，先看 ARP：

- 是否发出 ARP Request。
- 目标是否回复 ARP Reply。
- 回复 MAC 是否正确。
- 是否存在 IP 冲突。

## IP、Mask、Gateway

同一网段通信需要：
```text
IP 地址
子网掩码
```

跨网段通信需要：

```text
默认网关
路由
```

常见错误：

- IP 不在同一网段。
- 子网掩码错。
- 网关错。
- 静态 IP 冲突。
- DHCP 未获取地址。

## TCP

TCP 特点：

- 面向连接。
- 可靠传输。
- 有序字节流。
- 拥塞控制。
- 流量控制。

适合：

- HTTP。
- MQTT。
- Modbus TCP。
- 文件传输。
- 可靠命令通道。

关键点：

```text
TCP 是字节流，不保留应用消息边界。
```

一次 `send` 不等于一次 `recv`。

应用层必须设计：

- 长度字段。
- 固定帧长。
- 分隔符。
- 状态机。

## UDP

UDP 特点：

- 无连接。
- 保留数据报边界。
- 不保证到达。
- 不保证顺序。
- 开销小。
- 延迟低。

适合：

- 广播发现。
- 实时状态上报。
- 音视频。
- 简单低延迟控制。

但应用层要处理丢包、乱序和重传需求。

## TCP 粘包和半包

TCP 接收方可能出现：

```text
一次 recv 收到半个应用帧
一次 recv 收到多个应用帧
一次 recv 收到一个半应用帧
```

这不是 TCP 错误。

应用层解析器必须根据协议边界处理。

例如 Modbus TCP 使用 MBAP Header 中的 Length 字段确定帧长度。

## Modbus TCP 与 RTU 区别

Modbus TCP：

```text
MBAP Header + Function + Data
通常 TCP port 502
没有 RTU CRC
```

Modbus RTU：

```text
Address + Function + Data + CRC16
靠静默时间分帧
```

不能简单把 RTU 帧原样塞到 TCP 里当标准 Modbus TCP。

## 嵌入式协议栈

常见嵌入式 TCP/IP 栈：

```text
lwIP
FreeRTOS+TCP
Linux TCP/IP stack
厂商私有协议栈
```

裸机或 RTOS 常见问题：

- pbuf/mbuf 内存不足。
- DMA buffer cache 不一致。
- RX descriptor 不够。
- 链路断开后 socket 未恢复。
- TCP keepalive 未配置。
- 网络任务优先级不合理。

## Cache 和 DMA

带 Cache 的 MCU/SoC 使用 Ethernet DMA 时要特别注意：

- TX 前 clean cache。
- RX 后 invalidate cache。
- DMA buffer 对齐。
- descriptor 放在非缓存区或正确维护。
- 内存屏障。

Cache 问题表现很隐蔽：

- 偶发收不到包。
- 发送旧数据。
- 数据内容随机错误。
- Debug 关闭优化后问题消失。

## Link 状态和自动协商

PHY 会协商：

- 10/100/1000 Mbps。
- Half/Full duplex。

现代交换机通常全双工。

如果双工不匹配，可能出现：

- 丢包。
- 吞吐低。
- CRC 错。
- 重传多。

调试时读取 PHY 状态寄存器，不要只看 Link LED。

## Wireshark 排障顺序

建议按顺序看：

1. 是否有 ARP。
2. ARP 是否有回复。
3. IP 地址和 MAC 是否正确。
4. TCP 三次握手是否完成。
5. 应用层端口是否正确。
6. 是否有 TCP Retransmission。
7. 是否有 Reset。
8. 应用层协议长度是否正确。
9. 是否存在重复 IP 或重复 MAC。

过滤例子：

```text
arp
ip.addr == 192.168.1.50
tcp.port == 502
modbus
```

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| Link 不亮 | PHY 电源、复位、时钟、网线、磁性器件 |
| MDIO 读不到 PHY | PHY 地址、MDC、MDIO 上拉、复位 |
| 有 Link 但 ping 不通 | IP、Mask、ARP、防火墙 |
| ARP 无回复 | 目标 IP、网段、MAC、协议栈收包 |
| TCP 连不上 | 端口监听、防火墙、路由、服务状态 |
| TCP 频繁断开 | keepalive、任务阻塞、内存不足 |
| 数据解析错 | TCP 粘包/半包、字节序、长度字段 |
| 吞吐低 | DMA、Cache、窗口、任务优先级、双工 |

## 深度检查清单

- 确认 MCU/SoC 是否内置 MAC，是否需要外部 PHY。
- MAC-PHY 接口模式正确：MII/RMII/RGMII。
- RMII 50 MHz 时钟方向和质量正确。
- RGMII delay 配置正确。
- MDIO/MDC 能读取 PHY ID。
- PHY 地址 strap 与软件一致。
- PHY 复位时序正确。
- MAC 地址唯一。
- IP/Mask/Gateway 正确。
- ARP 正常。
- TCP 应用有完整分帧状态机。
- DMA 和 Cache 一致性已处理。
- Wireshark 能看到预期协议包。
