# SDIO Practical Guide

## 目标

本文用于 SDIO 工程调试，重点覆盖 SDIO 与 SD 卡关系、CLK/CMD/DAT0~3、1-bit/4-bit 模式、Wi-Fi 模块、电源时序、固件、设备树、驱动和常见枚举失败排查。

## SDIO 的定位

SDIO 是 SD 总线生态下的 I/O 外设接口。

常见设备：

- Wi-Fi 模块。
- Wi-Fi/BT Combo 模块。
- SDIO 网卡。
- 部分嵌入式无线模块。

它比 UART 更适合较高吞吐无线数据，比 PCIe/USB 简化一些，但驱动栈仍然复杂。

## 信号线

常见 SDIO 信号：

```text
CLK
CMD
DAT0
DAT1
DAT2
DAT3
VCC
GND
```

1-bit 模式：

```text
CLK + CMD + DAT0
```

4-bit 模式：

```text
CLK + CMD + DAT0~DAT3
```

很多 Wi-Fi 模块使用 4-bit 模式以获得更高吞吐。

## 上拉和电压

SDIO 通常需要 CMD/DAT 线上拉。

要确认：

- I/O 电压是 1.8V 还是 3.3V。
- Host 和模块电压一致。
- 是否支持 UHS 或 1.8V 切换。
- 上拉位置和阻值符合参考设计。

电压域错误可能导致枚举失败或损坏模块。

## SDIO Wi-Fi 模块常见额外信号

除 SDIO 总线外，Wi-Fi 模块通常还需要：

```text
WL_REG_ON / CHIP_EN
HOST_WAKE / WLAN_IRQ
32.768 kHz sleep clock
主晶振或参考时钟
电源 rail
BT UART/PCM，Combo 模块常见
```

只接 CLK/CMD/DAT 不一定能工作。

## 枚举流程概念

Host 会通过 SDIO 命令识别设备。

大致流程：

```text
上电
低速初始化
发送 SDIO 初始化命令
读取 CCCR/FBR
识别 Function
切换总线宽度
提高时钟频率
加载功能驱动
下载固件
启动设备
```

Wi-Fi 模块通常枚举成功后还要加载 firmware。

## 固件和驱动

SDIO Wi-Fi 常见软件组成：

```text
SDIO host controller driver
MMC/SDIO core
Wi-Fi chip driver
firmware binary
NVRAM/校准配置
设备树或板级数据
```

常见问题：

- 固件文件缺失。
- 固件版本和驱动不匹配。
- NVRAM 配置不匹配。
- 设备树 GPIO/IRQ 配错。
- 电源时序不满足。

## 设备树常见配置

Linux 下常见需要描述：
```text
SDIO host controller
bus-width = <4>
non-removable
cap-sdio-irq
keep-power-in-suspend
vmmc-supply
vqmmc-supply
wl-reg-on GPIO
host-wake IRQ
```

不同平台和驱动命名不同，以厂商 BSP 为准。

## 调试步骤

1. 确认模块供电和 enable 引脚。
2. 确认 CLK 输出。
3. 先低速枚举。
4. 确认 CMD/DAT 上拉和电压。
5. 查看内核日志是否识别 SDIO function。
6. 确认 Wi-Fi 驱动匹配芯片 ID。
7. 确认 firmware/NVRAM 文件路径。
8. 确认 HOST_WAKE 中断。
9. 再提高 SDIO 时钟和启用 4-bit 模式。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 完全不枚举 | 供电、enable、CLK、CMD/DAT 上拉 |
| 只低速可用 | 信号完整性、上拉、线长、频率 |
| 4-bit 失败 | DAT1~DAT3 接线、上拉、设备树 bus-width |
| 驱动加载失败 | chip ID、驱动版本、firmware |
| Wi-Fi 起不来 | NVRAM、校准、REG_ON、firmware |
| suspend 后失败 | keep-power、唤醒 IRQ、电源时序 |

## 实战检查清单

- Host 支持 SDIO，不只是 SD Memory。
- CMD/DAT 上拉正确。
- I/O 电压匹配。
- 1-bit 模式先跑通，再切 4-bit。
- Wi-Fi 模块 enable 和 wake 信号正确。
- firmware/NVRAM 与驱动匹配。
- 设备树 bus-width、IRQ、电源配置正确。
