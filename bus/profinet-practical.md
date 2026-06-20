# PROFINET Practical Guide

## 目标

本文面向第一次把 PROFINET 设备接入 PLC 或调试现场问题的工程场景，重点覆盖网络接线、设备命名、GSDML、周期 IO、诊断和抓包排查。

PROFINET 调试的关键不是只看 TCP/IP 是否通，而是确认设备是否被 PLC 正确发现、命名、组态并进入周期 IO 数据交换。

## 最小网络连接

典型调试连接：

```text
Engineering PC / PLC Tool
        |
Industrial Switch
        |
PLC Controller ---- PROFINET Device
```

最小检查：

- PLC、工程电脑、设备处于同一二层网络。
- 网线、交换机端口、设备 LINK/ACT 正常。
- 工程电脑网卡选择正确。
- 禁用不相关网卡或确认工具绑定到正确网卡。
- 设备电源、复位、固件和协议栈已启动。

PROFINET 发现和设备命名依赖二层以太网，不能只按普通 IP 路由思路排查。

## 关键工程文件

GSDML 是 PROFINET 设备描述文件。

它描述：

- Vendor ID 和 Device ID。
- 设备名称、模块、子模块。
- 输入输出数据长度。
- 诊断能力。
- 支持的实时能力。
- 图标和工程工具显示信息。

常见问题：

| 现象 | 优先检查 |
| --- | --- |
| 工具能扫到但不能组态 | GSDML 版本、设备型号、固件版本 |
| IO 长度不匹配 | 模块/子模块选择、输入输出字节数 |
| 下载组态失败 | 设备名称、IP、设备 ID、协议栈状态 |

## 设备发现和命名

PROFINET 设备通常需要先被工程工具发现，再分配设备名称和 IP。

典型流程：

```text
扫描在线设备
确认 MAC 地址和设备类型
分配 Device Name
分配 IP 参数
下载 PLC 组态
PLC 建立周期 IO 通信
```

注意：

- Device Name 必须和 PLC 组态一致。
- IP 地址不等于设备名称，二者都要检查。
- 现场换设备后，MAC 变了，名称可能需要重新分配。
- 多个同型号设备接入时，先逐个上电命名更安全。

## 周期 IO 数据

PROFINET 的核心工程目标通常是周期 IO 数据交换。

PLC 侧关注：

```text
Input：设备 -> PLC
Output：PLC -> 设备
```

设备侧关注：

- 输入输出缓冲区长度。
- 字节序和位定义。
- 模块槽位和子槽位映射。
- 周期更新是否超时。
- 安全状态或故障状态下输出如何处理。

不要只验证“能 ping 通”。设备能 ping 通不代表 PROFINET 周期 IO 已建立。

## Wireshark 抓包入口

常用观察点：

```text
eth.addr == <device-mac>
pn_dcp
pn_io
lldp
arp
```

重点看：

- DCP Identify：工程工具是否能发现设备。
- DCP Set：设备名称和 IP 是否被设置。
- LLDP：设备邻居和端口信息是否正常。
- ARP：IP 冲突或地址解析问题。
- PNIO：PLC 是否尝试建立 IO 通信。

如果普通交换机不支持端口镜像，可把工程电脑、PLC 和设备接到支持镜像的交换机，或临时只抓工程电脑与设备之间的发现和命名过程。

## 调试步骤

1. 确认 LINK/ACT、电源、复位和设备固件状态。
2. 工程电脑选择正确网卡，关闭无关 VPN 或虚拟网卡干扰。
3. 用工程工具扫描在线 PROFINET 设备。
4. 根据 MAC 地址确认目标设备。
5. 导入匹配的 GSDML。
6. 在 PLC 工程中选择正确设备、模块和 IO 长度。
7. 分配 Device Name 和 IP。
8. 下载 PLC 组态。
9. 查看 PLC 诊断缓冲区和设备诊断。
10. 用 Wireshark 确认 DCP、LLDP、PNIO 过程。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 扫不到设备 | 二层网络、网卡选择、防火墙、设备协议栈、LINK |
| 能扫到但不能命名 | 设备写保护、协议栈状态、名称格式、工具权限 |
| 名称后仍连不上 | PLC 组态名称、IP、设备 ID、GSDML 版本 |
| 周期 IO 不起来 | 模块/子模块、IO 长度、实时能力、PLC 诊断 |
| 运行一段时间掉线 | 网线、交换机、EMI、设备看门狗、周期超时 |
| 换设备后异常 | MAC 变化、旧名称残留、设备型号或固件不一致 |

## 工程注意

- PROFINET 产品通常涉及协议栈授权和一致性测试。
- 不同 PLC 工程工具对诊断信息的展示方式不同，但核心仍是名称、GSDML、模块和周期 IO。
- IRT 或高同步场景依赖交换机、设备硬件和协议栈能力，不能只靠软件配置补齐。
- 现场问题要同时看 PLC 诊断、设备日志和网络抓包。

## 实战检查清单

- GSDML 与设备固件和型号匹配。
- Device Name 与 PLC 组态完全一致。
- IP 地址无冲突，网段符合现场规划。
- PLC 选择的模块和 IO 长度与设备实现一致。
- 设备能被 DCP Identify 发现。
- PLC 诊断缓冲区无设备不匹配或组态错误。
- Wireshark 能看到 DCP、LLDP 和 PNIO 相关报文。
- 现场交换机、线缆和接地满足工业环境要求。

## 延伸阅读

- `bus/profinet.md`
- `bus/industrial-ethernet-comparison.md`
- `bus/ethernet-deep-dive.md`
