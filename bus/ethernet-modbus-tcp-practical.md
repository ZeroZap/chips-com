# Ethernet + Modbus TCP Practical Guide

## 目标

本文用于把 Ethernet、TCP/IP 和 Modbus TCP 联合调通，适合网口仪表、PLC、网关、采集设备和嵌入式控制器。

## 分层关系

```text
Modbus TCP：应用层协议
TCP：可靠字节流，常用端口 502
IP：网络寻址
Ethernet：MAC 帧
PHY：网线差分信号
```

Modbus TCP 不是把 Modbus RTU 帧原样放进 TCP。

## 硬件链路

典型 MCU 网口：

```text
MCU MAC -> RMII/MII -> Ethernet PHY -> Magnetics -> RJ45 -> Cable
```

常见检查点：

- PHY 电源和复位。
- 50 MHz RMII 时钟。
- MDIO/MDC 能读 PHY。
- Link LED 正常。
- MAC 地址唯一。

## 网络配置

静态 IP 示例：

```text
IP:      192.168.1.50
Mask:    255.255.255.0
Gateway: 192.168.1.1
Port:    502
```

同网段主机可直接访问：

```text
192.168.1.x
```

跨网段需要网关和路由。

## Modbus TCP 帧结构

Modbus TCP 使用 MBAP Header：

```text
Transaction ID | Protocol ID | Length | Unit ID | Function | Data
```

与 RTU 不同：

```text
没有 RTU CRC
有 MBAP Header
通过 TCP 保证字节可靠传输
```

读保持寄存器请求示例：

```text
00 01 00 00 00 06 01 03 00 00 00 02
```

拆解：

```text
00 01    Transaction ID
00 00    Protocol ID
00 06    Length
01       Unit ID
03       Function
00 00    Start Address
00 02    Quantity
```

## TCP 字节流注意事项

TCP 不保留消息边界。

一次 `recv` 可能收到：

```text
半帧
一帧
多帧
```

必须按 MBAP 中的 `Length` 做状态机解析。

## 调试步骤

1. 确认网口 Link。
2. `ping` 设备 IP。
3. 用 Wireshark 抓 ARP、TCP 三次握手和 Modbus TCP。
4. 用 Modbus Poll 或 pymodbus 读取一个寄存器。
5. 检查 Unit ID、功能码和寄存器地址偏移。
6. 多客户端访问时确认设备是否支持并发连接。
7. 长时间运行测试 TCP 断线重连。

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| 无 Link | PHY、时钟、网线、磁性器件 |
| ping 不通 | IP、网段、ARP、防火墙 |
| TCP 连不上 | 端口 502、服务未监听、防火墙 |
| Modbus 异常 | Unit ID、功能码、地址偏移 |
| 偶发解析错 | TCP 粘包/半包处理 |
| 多客户端异常 | 连接数、资源释放、超时 |

## 实战检查清单

- PHY 已正常 Link。
- MAC 地址唯一。
- IP、Mask、Gateway 正确。
- TCP 断线重连处理完整。
- MBAP Length 解析正确。
- 寄存器地址偏移确认。
- Wireshark 能看到正确 Modbus TCP 报文。
