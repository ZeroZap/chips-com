# Industrial Ethernet Comparison

## 目标

本文对比常见工业以太网和工业网络协议：Modbus TCP、PROFINET、EtherNet/IP、EtherCAT，并给出选型直觉。

## 一句话理解

```text
Modbus TCP：简单寄存器读写，适合监控和通用仪表
PROFINET：西门子生态常见，面向自动化系统
EtherNet/IP：Rockwell/AB 生态常见，基于 CIP 对象模型
EtherCAT：强实时运动控制，On-the-fly 处理
```

## 对比表

| 协议 | 常见承载 | 实时性 | 复杂度 | 典型场景 |
| --- | --- | --- | --- | --- |
| Modbus TCP | TCP/IP | 一般 | 低 | 仪表、网关、简单 PLC 通信 |
| PROFINET | Ethernet/IP 体系与实时机制 | 中到高 | 高 | 西门子 PLC、远程 IO、自动化 |
| EtherNet/IP | TCP/UDP/IP + CIP | 中 | 高 | Rockwell/AB、工业控制 |
| EtherCAT | Ethernet 帧 | 高 | 高 | 伺服、多轴、高速 IO |

## Modbus TCP

优点：

- 简单。
- 易实现。
- 资料多。
- 普通 socket 可开发。

限制：

- 实时性一般。
- 数据模型简单。
- 不适合强实时多轴控制。

适合：

- 采集仪表。
- 网关。
- 上位机监控。
- 简单参数读写。

## PROFINET

PROFINET 常见于西门子生态。

特点：

- 工程组态能力强。
- 设备命名和发现。
- 周期 IO。
- 诊断体系。
- 实时等级可扩展。

适合：

- 西门子 PLC 项目。
- 远程 IO。
- 变频器和驱动。
- 自动化产线。

## EtherNet/IP

EtherNet/IP 中的 IP 是 Industrial Protocol。

它基于 CIP 对象模型。

特点：

- 对象模型。
- 显式消息和隐式 IO。
- Rockwell/AB 生态常见。
- 使用 TCP/UDP/IP。

适合：

- Rockwell PLC 系统。
- 工业 IO。
- 驱动和执行器。

## EtherCAT

EtherCAT 重点：

- 实时。
- 高同步。
- 多从站过程数据。
- On-the-fly。
- 分布式时钟。

适合：

- 多轴伺服。
- 机器人。
- 高速 IO。
- 半导体设备。

## 选型直觉

如果客户要简单读写寄存器：

```text
Modbus TCP
```

如果客户是西门子生态：

```text
PROFINET
```

如果客户是 Rockwell/AB 生态：

```text
EtherNet/IP
```

如果项目是高速多轴运动控制：

```text
EtherCAT
```

如果只是设备配置网页或云连接：

```text
HTTP / MQTT / REST / 自定义 TCP/UDP
```

## 实战检查清单

- 客户 PLC 生态是什么。
- 是否需要认证。
- 是否需要强实时。
- 是否需要标准设备模型。
- 是否已有协议栈。
- MCU/SoC 性能是否足够。
- 调试工具和主站软件是否可用。
- 是否需要和现有产线兼容。
