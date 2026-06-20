# EtherNet/IP Practical Guide

## 目标

本文面向第一次把 EtherNet/IP 设备接入 Rockwell / Allen-Bradley PLC、调试远程 IO、驱动器、传感器或网关设备的工程场景。

重点覆盖：

- 网络和工具准备。
- EDS 设备描述文件。
- CIP 对象、Class、Instance、Attribute。
- 显式消息和隐式 IO 的区别。
- Assembly Object 和周期 IO 映射。
- RPI、连接资源和超时。
- Wireshark 抓包入口。
- 常见 PLC 侧、设备侧和网络侧故障定位。

EtherNet/IP 的难点不是“以太网是否通”，而是 PLC 是否能基于 EDS 和 CIP 对象模型正确建立连接、读写属性并交换周期 IO。

## 最小网络连接

典型调试连接：

```text
Engineering PC / Studio 5000 / BOOTP-DHCP Tool
        |
Industrial Switch
        |
Rockwell PLC ---- EtherNet/IP Device
```

最小检查：

- PLC、工程电脑、设备处于可达网络。
- 设备 LINK/ACT 正常。
- 工程电脑选择正确网卡。
- IP、子网掩码和网关符合现场规划。
- 设备没有被其他控制器占用连接资源。
- 防火墙、VPN、虚拟网卡没有干扰工程工具。

常见端口：

| 端口 | 用途 |
| --- | --- |
| TCP 44818 | EtherNet/IP 显式消息、会话和配置 |
| UDP 2222 | 隐式 IO 周期数据 |
| UDP 44818 | 发现相关流量，视工具和设备实现而定 |

能 ping 通只说明 IP 层可达，不代表 EtherNet/IP 会话、EDS、CIP 路径或 IO 连接正确。

## 工具和文件准备

常见工具：

- Studio 5000 / RSLogix 5000：PLC 工程组态。
- RSLinx / FactoryTalk Linx：设备浏览和通信驱动。
- BOOTP/DHCP Tool：分配或确认设备 IP。
- EDS Hardware Installation Tool：安装 EDS。
- Wireshark：抓包分析显式和隐式通信。
- 厂商配置工具：配置驱动器、IO 模块、传感器或网关参数。

关键文件：

- EDS：Electronic Data Sheet，设备描述文件。
- 固件版本说明：确认 EDS 与设备固件匹配。
- 对象模型文档：说明支持哪些 CIP Class、Instance、Attribute。
- IO 映射表：说明 Input / Output Assembly 的字节含义。

## EDS 文件

EDS 描述设备在工程工具中的身份和能力。

它通常包含：

- Vendor ID。
- Device Type。
- Product Code。
- Revision。
- 设备名称和图标。
- 支持的连接类型。
- Assembly Instance。
- 输入输出数据长度。
- 配置参数。

常见问题：

| 现象 | 优先检查 |
| --- | --- |
| 工具显示 Unknown Device | EDS 未安装或 Vendor/Product 不匹配 |
| 设备能浏览但不能加入工程 | EDS 版本、设备类型、固件版本 |
| IO 长度不匹配 | Assembly Instance、Input/Output Size、模块选择 |
| 下载工程后连接失败 | RPI、连接类型、设备连接资源、设备状态 |

EDS 不只是“显示名称”，它会影响 PLC 如何建立连接和解释设备能力。

## CIP 对象模型

EtherNet/IP 基于 CIP，CIP 用对象模型组织设备能力。

常见表达方式：

```text
Class / Instance / Attribute
```

含义：

- Class：对象类别。
- Instance：对象实例。
- Attribute：实例或类的属性。
- Service：对对象执行的操作，如 Get / Set。

常见对象：

| 对象 | 典型用途 |
| --- | --- |
| Identity Object | 设备身份、厂商、产品、版本、状态 |
| Message Router | 路由显式消息 |
| Assembly Object | 输入输出过程数据集合 |
| Connection Manager | 建立和管理连接 |
| TCP/IP Interface Object | IP、子网、网关等网络参数 |
| Ethernet Link Object | 链路状态、速率、双工、MAC |

调试显式消息时，必须确认：

- Class ID 正确。
- Instance ID 正确。
- Attribute ID 正确。
- Service Code 正确。
- 数据类型和字节序正确。
- 目标对象是否允许写入。

## 显式消息

显式消息用于配置、诊断、参数读写和低频访问。

典型用途：

- 读取设备 Identity。
- 读取或写入参数。
- 读取诊断状态。
- 触发设备命令。
- 配置非周期参数。

常见服务：

| Service | 含义 |
| --- | --- |
| Get Attribute Single | 读取单个属性 |
| Set Attribute Single | 写入单个属性 |
| Reset | 复位对象或设备，视对象支持情况而定 |

显式消息排查顺序：

1. TCP 44818 是否能建立连接。
2. Register Session 是否成功。
3. CIP 路径是否正确。
4. Service 是否被对象支持。
5. 返回状态码是否表示路径、权限或数据错误。
6. 数据类型、长度和字节序是否匹配。

显式消息适合低频配置，不适合作为高速周期控制通道。

## 隐式 IO

隐式 IO 用于周期实时数据交换。

常见数据方向：

```text
Input Assembly：设备 -> PLC
Output Assembly：PLC -> 设备
Configuration Assembly：PLC -> 设备配置，通常在连接建立时使用
```

设备文档一般会给出：

- Input Assembly Instance。
- Output Assembly Instance。
- Configuration Assembly Instance。
- 每个 Assembly 的字节长度。
- 每个字节、位或字的含义。

示例：

```text
Input Assembly 101, 8 bytes
Byte 0..1：Status Word
Byte 2..3：Actual Value
Byte 4..7：Diagnostics Flags

Output Assembly 100, 4 bytes
Byte 0..1：Control Word
Byte 2..3：Setpoint
```

PLC 和设备对 Input / Output 的视角相反，调试时要明确站在哪一侧描述。

## RPI 和连接资源

RPI 是 Requested Packet Interval，即请求的周期数据间隔。

常见问题：

- RPI 设置过小，设备 CPU 或网络负载过高。
- RPI 设置过小，设备协议栈无法接受连接。
- 多个 PLC 或工具同时连接，设备连接资源耗尽。
- 网络抖动导致 IO 超时。

调试建议：

- 首次接入先使用较保守 RPI，例如 20 ms、50 ms 或设备推荐值。
- 稳定后再逐步降低 RPI。
- 记录设备支持的最小 RPI、最大连接数和每类连接数量。
- 区分 Exclusive Owner、Input Only、Listen Only 等连接类型。

## 接入 PLC 的典型流程

1. 确认设备 IP 地址和网络可达。
2. 安装匹配 EDS。
3. 在工程工具中浏览设备。
4. 确认 Vendor ID、Product Code、Revision。
5. 将设备加入 PLC 工程。
6. 选择正确的连接类型和 Assembly。
7. 设置 Input / Output / Configuration 数据长度。
8. 设置 RPI。
9. 下载工程到 PLC。
10. 查看 PLC I/O Tree 和模块状态。
11. 监控输入输出数据是否按预期变化。
12. 用 Wireshark 验证 TCP 44818 和 UDP 2222 流量。

## Wireshark 抓包入口

常用过滤：

```text
enip
cip
tcp.port == 44818
udp.port == 2222
ip.addr == <device-ip>
eth.addr == <device-mac>
```

重点看：

- List Identity：工程工具是否能发现设备。
- Register Session：显式消息会话是否建立。
- Forward Open：PLC 是否请求建立 IO 连接。
- Forward Open Response：设备是否接受连接。
- UDP 2222：隐式 IO 是否周期收发。
- CIP General Status / Extended Status：失败时的状态码。
- TCP Retransmission 或 UDP 丢包：网络质量问题。

抓包判断思路：

| 抓包现象 | 可能方向 |
| --- | --- |
| 无任何 ENIP 报文 | 网卡、网络、工具绑定、防火墙 |
| 有 List Identity 无 Forward Open | PLC 工程未发起 IO 或设备未加入工程 |
| Forward Open 被拒绝 | Assembly、RPI、连接类型、资源或权限 |
| UDP 2222 断续 | 网络抖动、设备负载、RPI 过小 |
| 显式读写返回错误 | CIP 路径、服务、权限、数据类型 |

## 设备侧实现检查

如果你在实现 EtherNet/IP 设备，至少要检查：

- Identity Object 信息与 EDS 一致。
- Product Code、Revision、Device Type 不随意变化。
- Assembly Instance 与 EDS 完全一致。
- Input / Output 字节长度与 EDS 完全一致。
- Connection Manager 正确处理 Forward Open / Forward Close。
- RPI 边界检查明确。
- 连接超时后资源能释放。
- 显式消息错误码可帮助定位问题。
- 设备日志记录连接建立、断开、超时和参数错误。

不要只在自研工具中验证成功，还要用目标 PLC 和目标工程软件验证。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 工具找不到设备 | IP、网卡、防火墙、List Identity、设备协议栈 |
| EDS 安装后仍未知 | Vendor ID、Product Code、Revision、EDS 版本 |
| 显式消息失败 | Class/Instance/Attribute、Service、权限、数据类型 |
| IO 连接不上 | Assembly Instance、数据长度、RPI、连接类型 |
| 连接后马上掉线 | RPI 过小、设备超时、网络抖动、连接资源 |
| 数据错位 | 字节序、结构体对齐、Input/Output 方向理解错误 |
| PLC 显示模块故障 | EDS 不匹配、设备状态、Forward Open 错误码 |
| 多控制器冲突 | Exclusive Owner 连接已被占用、Listen Only 配置错误 |

## 实战检查清单

- EDS 已安装且版本匹配。
- 设备 IP、子网和网关正确。
- 工程工具绑定到正确网卡。
- Identity 信息与 EDS 一致。
- Input / Output / Configuration Assembly Instance 正确。
- IO 数据长度和 PLC 工程一致。
- RPI 在设备支持范围内。
- 连接类型符合应用需求。
- 显式消息读写路径经过验证。
- Wireshark 能看到 Register Session、Forward Open 和 UDP 2222 周期流量。
- PLC 诊断和设备日志能对应同一故障时间点。

## 与 PROFINET 的调试差异

PROFINET 常围绕设备名称、GSDML、DCP、PNIO 和 PLC 组态排查。

EtherNet/IP 更常围绕 EDS、CIP 对象路径、Assembly、Forward Open、RPI 和连接资源排查。

两者都不能只靠 ping 判断通信是否正常。

## 延伸阅读

- `bus/ethernet-ip.md`
- `bus/profinet-practical.md`
- `bus/industrial-ethernet-comparison.md`
- `bus/ethernet-deep-dive.md`
