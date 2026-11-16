# PCIe Practical Guide

## 目标

本文用于 PCIe 工程入门和调试，重点覆盖 Root Complex、Endpoint、Lane、Gen、配置空间、BAR、MSI/MSI-X、DMA、链路训练、LTSSM 和常见枚举失败排查。

## PCIe 的定位

PCIe 是高速点对点系统互联接口，常见于：

- NVMe SSD。
- 网卡。
- Wi-Fi 模块。
- FPGA。
- GPU。
- AI 加速器。
- 视频采集卡。

工程直觉：

```text
I2C/SPI 是外设小路
USB 是通用外设总线
Ethernet 是网络
PCIe 是主机内部高速扩展通道
```

## Root Complex 和 Endpoint

PCIe 链路两端角色不同：

```text
Root Complex：主机侧，通常在 CPU/SoC
Endpoint：设备侧，如 SSD、网卡、FPGA
```

两个 Endpoint 不能直接普通互连。

多个设备通常通过 PCIe Switch 扩展。

## Lane 和 Gen

一个 Lane 包含：

```text
TX+ / TX-
RX+ / RX-
```

常见宽度：

```text
x1 / x2 / x4 / x8 / x16
```

常见代际：

```text
Gen1 / Gen2 / Gen3 / Gen4 / Gen5
```

带宽由 Gen 和 Lane 数共同决定。

例如：

```text
Gen3 x4 常见于 NVMe SSD
Gen2 x1 常见于嵌入式 Wi-Fi/扩展设备
```

## 链路训练和 LTSSM

PCIe 上电后会进行链路训练。

LTSSM 是 Link Training and Status State Machine。

常见阶段概念：

```text
Detect
Polling
Configuration
L0
Recovery
Disabled
Hot Reset
```

正常工作状态通常是：

```text
L0
```

如果链路停在 Detect/Polling，优先检查：

- PERST#。
- REFCLK。
- Lane 连接。
- 供电。
- AC 耦合电容。
- RC/EP 角色。

## REFCLK 和 PERST#

PCIe 常见关键控制：

```text
REFCLK：参考时钟
PERST#：PCIe 复位
```

注意：

- Endpoint 供电稳定后才能释放 PERST#。
- REFCLK 必须满足频率和抖动要求。
- 有些平台支持 SSC，有些组合不兼容。
- M.2/miniPCIe 模块还可能使用 CLKREQ#。

## AC 耦合电容

PCIe 高速差分线通常需要 AC 耦合电容。

位置和取值要按平台规范。

常见错误：

- 漏放 AC 耦合电容。
- 放在错误方向或错误位置。
- 封装和布局不适合高速。
- Lane 极性和方向搞错。

## 配置空间

PCIe 设备有配置空间。

主机枚举时读取：

```text
Vendor ID
Device ID
Class Code
Revision
BAR
Capability List
Interrupt Capability
```

如果 Vendor ID 读到 `0xFFFF`，通常表示设备未响应。

优先检查链路是否训练成功。

## BAR

BAR 是 Base Address Register。

它告诉主机设备需要哪些地址空间。

常见类型：

```text
MMIO BAR
I/O BAR，较少见
64-bit BAR
```

主机给 BAR 分配地址后，驱动可以通过内存映射访问设备寄存器。

## MSI 和 MSI-X

PCIe 常用消息中断：

```text
MSI
MSI-X
```

相比传统 INTx，MSI/MSI-X 更适合现代系统。

调试中断问题时检查：

- 设备是否支持 MSI/MSI-X。
- 驱动是否启用。
- 中断向量是否分配成功。
- IOMMU/中断控制器配置。
- 设备是否真正写中断消息。

## DMA

PCIe 高性能依赖 DMA。

典型流程：

```text
驱动分配 DMA buffer
配置设备 DMA 地址和长度
设备通过 PCIe 读写主机内存
设备触发 MSI/MSI-X 中断
驱动处理完成数据
```

注意：

- DMA 地址不是普通虚拟地址。
- 需要 DMA mapping API。
- Cache 一致性必须处理。
- IOMMU 可能限制访问。
- 设备不能越界访问内存。

## M.2 接口注意

M.2 插槽不等于一定支持所有协议。

可能承载：

```text
PCIe
SATA
USB
SDIO
I2C/SMBus
```

要确认：

- Key 类型。
- 实际连接了几条 PCIe Lane。
- 是否有 REFCLK。
- 是否有 PERST#。
- 电源电压和电流是否满足。
- 模块需要的 sideband 信号。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 枚举不到设备 | 供电、PERST#、REFCLK、Lane、RC/EP 角色 |
| LTSSM 不到 L0 | Lane 信号、AC 电容、时钟、复位时序 |
| Vendor ID 0xFFFF | 链路未通、配置访问失败 |
| 速率降级 | 信号完整性、线长、均衡、设备能力 |
| Lane 数降级 | 某些 Lane 断路、极性、连接器问题 |
| 驱动加载失败 | VID/PID、Class Code、BAR、中断 |
| DMA 数据错 | Cache、IOMMU、地址映射、buffer 对齐 |

## 实战检查清单

- RC/EP 角色正确。
- REFCLK 满足设备要求。
- PERST# 时序正确。
- Lane TX/RX 方向正确。
- AC 耦合电容位置正确。
- LTSSM 能进入 L0。
- 配置空间能读到 Vendor ID。
- BAR 分配成功。
- MSI/MSI-X 或 INTx 可用。
- DMA buffer 映射和 Cache 一致性正确。
