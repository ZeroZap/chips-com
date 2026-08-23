# USB Practical Guide

## 目标

本文用于 USB 工程入门和调试，重点覆盖 Host/Device/OTG、枚举流程、描述符、Endpoint、传输类型、CDC/HID/MSC、VBUS、D+/D-、Type-C 基础和常见枚举失败排查。

## USB 不是 UART

USB CDC 虚拟串口在电脑上看起来像串口，但底层不是 UART。

UART：

```text
双方配置波特率后直接收发字节
```

USB：

```text
Host 检测设备
复位设备
读取描述符
分配地址
选择配置
加载驱动
通过端点传输数据
```

所以 USB 的关键不是“TX/RX 接线”，而是：

```text
枚举 + 描述符 + 端点 + 类驱动
```

## Host、Device、OTG

USB 角色非常重要。

`Host` 负责：

- 提供 VBUS。
- 检测设备连接。
- 枚举设备。
- 分配地址。
- 调度所有传输。
- 加载驱动。

`Device` 负责：

- 上报描述符。
- 响应 Host 请求。
- 通过 Endpoint 收发数据。

`OTG` 表示设备可在不同场景下切换 Host 或 Device 角色。

两个普通 USB Device 不能直接通信，例如：

```text
U 盘 <-> 鼠标
```

必须有 Host：

```text
PC Host <-> U 盘 Device
```

## USB 2.0 基本线缆

常见 USB 2.0 信号：

```text
VBUS：5V
D+：差分数据线
D-：差分数据线
GND：地
```

Device 侧通常通过 D+/D- 上拉让 Host 检测速度类型。

硬件设计要注意：

- D+/D- 不要接反。
- ESD 器件电容要适合 USB。
- 差分线走线要短且成对。
- VBUS 检测和供电路径要符合角色。
- Device 不应随意向 VBUS 反灌电。

## USB 速度等级

常见速度：

| 名称 | 速度 |
| --- | --- |
| Low Speed | 1.5 Mbps |
| Full Speed | 12 Mbps |
| High Speed | 480 Mbps |
| SuperSpeed | 5 Gbps 起 |

很多 MCU 只支持：

```text
USB Full Speed 12 Mbps
```

如果要 High Speed，通常需要：

- 内置 HS PHY。
- 外部 ULPI PHY。
- 更严格的 PCB 设计。

不要看到芯片写 USB 就默认是 480 Mbps。

## 枚举流程

USB Device 插入 Host 后，典型流程：

```text
连接检测
Bus Reset
读取 Device Descriptor 前 8 字节
分配 USB Address
读取完整 Device Descriptor
读取 Configuration Descriptor
读取 Interface 和 Endpoint 信息
选择 Configuration
加载类驱动或厂商驱动
开始正常传输
```

枚举失败常见原因：

- D+/D- 接反。
- 设备描述符错误。
- Endpoint 配置不匹配。
- VBUS 检测错误。
- 时钟不准。
- USB 栈未正确响应标准请求。

## 描述符

USB Device 通过描述符告诉 Host 自己是什么。

常见描述符：

```text
Device Descriptor
Configuration Descriptor
Interface Descriptor
Endpoint Descriptor
String Descriptor
Class-specific Descriptor
```

描述符决定：

- VID/PID。
- 设备类。
- 接口数量。
- Endpoint 数量。
- 包大小。
- 供电需求。
- 字符串信息。

描述符长度或层级错误会导致 Host 枚举失败。

## VID 和 PID

USB 设备通常有：

```text
VID：Vendor ID
PID：Product ID
```

实验阶段可以使用芯片厂商示例 VID/PID。

正式产品必须处理 VID/PID 合规问题，不应随意使用别人的 VID。

## Configuration、Interface、Endpoint

USB 结构可以理解为：

```text
Device
  Configuration
    Interface
      Endpoint
```

一个设备可以是复合设备，例如：

```text
CDC 虚拟串口 + HID 控制接口
```

这时会有多个 Interface。

## Endpoint 方向

Endpoint 方向从 Host 视角定义：

```text
IN：Device -> Host
OUT：Host -> Device
```

这点非常容易看反。

例如：

```text
Bulk IN：设备发数据给主机
Bulk OUT：主机发数据给设备
```

Endpoint 0 是默认控制端点，每个 USB Device 都必须有。

## 传输类型

USB 主要传输类型：

| 类型 | 特点 | 常见用途 |
| --- | --- | --- |
| Control | 管理请求，Endpoint 0 必用 | 枚举、配置、控制命令 |
| Bulk | 可靠，大数据，不保证延迟 | U 盘、CDC 数据 |
| Interrupt | 小数据，周期轮询，延迟可控 | 键盘、鼠标、HID、CDC 通知 |
| Isochronous | 保证带宽，不重传 | 音频、视频 |

选择传输类型要看数据特性。

不要把所有数据都塞进 Control 传输。

## USB CDC

CDC ACM 常用于虚拟串口。

典型 Endpoint：

```text
Control Endpoint 0
Interrupt IN：通知
Bulk IN：Device -> Host 数据
Bulk OUT：Host -> Device 数据
```

注意：

- CDC 波特率设置很多时候只是兼容串口 API。
- 底层传输不等于 UART 起始位/停止位。
- Host 打开串口前，Device 侧发送数据可能无人读取。
- DTR/RTS 状态可能影响固件是否开始输出。

## USB HID

HID 常用于：

- 键盘。
- 鼠标。
- 游戏手柄。
- 简单控制设备。

优点：

```text
系统原生驱动支持好
通常免自定义驱动
```

限制：

- 报告描述符复杂。
- 数据包大小和轮询周期有限制。
- 不适合大吞吐数据。

## USB MSC

MSC 是 Mass Storage Class。

常见用途：

- U 盘。
- 读卡器。
- MCU 模拟 U 盘。
- 拖拽升级。
- 日志导出。

注意：

```text
文件系统一致性非常重要
```

Host 和 MCU 不应同时随意修改同一存储区域，否则可能损坏文件系统。

## USB Device 调试步骤

1. 确认 VBUS、D+、D-、GND 接线。
2. 确认 USB 时钟精度。
3. 确认 Device 栈启动。
4. 插入 Host，观察是否有连接事件。
5. 用系统日志查看枚举信息。
6. 检查 VID/PID 和描述符。
7. 确认 Endpoint 数量和最大包大小。
8. 使用类驱动工具测试 CDC/HID/MSC。
9. 用 USB 抓包工具分析标准请求。

## USB Host 调试步骤

1. 确认 Host 能提供 VBUS。
2. 确认过流保护和电源开关。
3. 检测 Device 连接。
4. 执行枚举。
5. 读取描述符。
6. 匹配类驱动。
7. 分配 Endpoint 传输资源。
8. 处理断开、重连和错误恢复。

Host 开发通常比 Device 更复杂，因为 Host 要识别和驱动别人。

## Type-C 基础

USB Type-C 是连接器和相关生态，不等于固定速度。

Type-C 可能承载：

- USB 2.0。
- USB 3.x。
- DisplayPort Alt Mode。
- USB PD。

Type-C 关键引脚：

```text
CC1 / CC2
```

CC 用于：

- 插入检测。
- 方向识别。
- Source/Sink 角色判断。
- 默认电流能力声明。
- PD 协商入口。

只做 USB 2.0 Type-C Device 时，也必须正确处理 CC 下拉。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 插入无反应 | VBUS、D+/D-、CC、上拉/下拉、时钟 |
| 未知 USB 设备 | 描述符、标准请求响应、时钟 |
| 枚举到一半失败 | 配置描述符长度、Endpoint 参数 |
| CDC 无数据 | Host 是否打开端口、DTR、Bulk Endpoint |
| HID 不工作 | Report Descriptor、轮询间隔、报告长度 |
| MSC 文件损坏 | 文件系统一致性、缓存、拔出流程 |
| 高速不稳定 | PCB、线缆、ESD 电容、PHY、阻抗 |

## 抓包和工具

常用工具：

- Windows 设备管理器。
- Linux `dmesg`、`lsusb`、`usbmon`。
- Wireshark USB capture。
- USB 协议分析仪。
- 芯片厂商 USB debug log。

Linux 常用命令：

```text
lsusb
lsusb -v
```

## 实战检查清单

- Host/Device/OTG 角色已明确。
- VBUS 方向和检测正确。
- D+/D- 没接反。
- USB 时钟满足精度要求。
- 描述符长度和层级正确。
- Endpoint 方向按 Host 视角定义。
- Control/Bulk/Interrupt/Isochronous 类型选择合理。
- CDC/HID/MSC 类描述符与 Endpoint 匹配。
- Type-C CC 处理正确。
- 枚举失败时有抓包或系统日志。

## 速查要点

### 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| PC 完全看不到设备 | VBUS / 描述符 / 时钟 | 查 VBUS, 查时钟, USB 树查看 |
| 看到设备但有黄色叹号 | 描述符错 / 驱动不匹配 | 设备管理器看错误码 |
| 枚举后立即断开 | 电源 / 描述符 / 信号完整性 | 量 VBUS 跌落, 查描述符 |
| 枚举成功但传输错 | 端点 / 数据错 | Wireshark 抓 USB 流量 |
| 高速 (480M) 跑不通 | 物理层 / Hub / 阻抗 | 用 2.0 端口重试, 查 Hub |
| CDC 串口打开失败 | CDC 类描述符错 | 查 CDC ACM 描述符, 串口工具日志 |
| HID 设备不被识别 | HID 报告描述符错 | USBlyzer / Wireshark 分析 |
| 传输大文件失败 | 端点 stall / 超时 | 抓包看 stall, 查 USB 错误码 |
| 断电后无法重新枚举 | VBUS 时序 / 控制器状态 | 查上电时序, 控制器 reset |

### USB 速度档

```text
低速 (Low Speed, 1.5M):    HID 鼠标 / 键盘 / 部分嵌入式
全速 (Full Speed, 12M):   多数嵌入式 / USB 1.1 标准
高速 (High Speed, 480M):  USB 2.0, 视频 / 存储
超速 (Super Speed, 5G):   USB 3.0, 视频 / 高速存储
超速+ (Super Speed+, 10G): USB 3.1 / 3.2

实际工程: 大多数嵌入式 USB 是全速, 偶尔高速
```

### 端点类型

```text
Control (控制):
  - 端点 0 固定
  - 用于枚举 / 配置 / 类请求
  - 双向, 消息式

Bulk (批量):
  - 用于数据量大, 实时性不高的场景
  - 例: U盘读文件, 串口大数据
  - 保证送达, 不保证带宽

Interrupt (中断):
  - 周期性小数据 (1-1024 字节)
  - 例: HID 键盘 / 鼠标
  - 有轮询周期保证

Isochronous (等时):
  - 实时性高, 不保证送达
  - 例: USB 音频 / 视频
  - 固定带宽, 无重传
```

### 描述符层级

```text
Device Descriptor (设备描述符, 1 个)
  |
  +-- Configuration Descriptor (配置描述符, N 个)
       |
       +-- Interface Descriptor (接口描述符, N 个)
            |
            +-- Endpoint Descriptor (端点描述符, N 个)
            +-- Class-specific Descriptor (类特定描述符)
       |
       +-- Interface Association Descriptor (IAD, 复合设备)
```

### 关键描述符字段

```text
Device Descriptor:
  bLength, bDescriptorType, bcdUSB, bDeviceClass,
  bDeviceSubClass, bDeviceProtocol,
  idVendor (VID, 16 bit), idProduct (PID, 16 bit),
  bcdDevice, iManufacturer, iProduct, iSerialNumber,
  bNumConfigurations

Configuration Descriptor:
  bLength, bDescriptorType, wTotalLength, bNumInterfaces,
  bConfigurationValue, iConfiguration,
  bmAttributes (self-powered / bus-powered / remote-wakeup),
  bMaxPower (2 mA 单位)

Interface Descriptor:
  bLength, bDescriptorType, bInterfaceNumber,
  bAlternateSetting, bNumEndpoints,
  bInterfaceClass, bInterfaceSubClass, bInterfaceProtocol,
  iInterface
```

### 常见类代码

```text
0x00: Use class info in interface descriptor
0x01: Audio
0x02: CDC (Communication Device Class, 串口)
0x03: HID (Human Interface Device, 键鼠)
0x05: Physical
0x06: Image
0x07: Printer
0x08: Mass Storage (U 盘)
0x09: Hub
0x0B: Smart Card
0x0D: Content Security
0x0E: Video
0x0F: Personal Healthcare
0x10: Audio/Video
0xE0: Wireless (Bluetooth)
0xFF: Vendor Specific
```

### USB 请求 (Setup 请求)

```text
GET_DESCRIPTOR        0x8006  获取描述符
SET_ADDRESS          0x0005  设置地址
SET_CONFIGURATION    0x0009  设置配置
GET_CONFIGURATION    0x8008  获取配置
SET_INTERFACE        0x000B  设置接口
CLEAR_FEATURE        0x0001  清除特性 (e.g. HALT 端点)
SET_FEATURE          0x0003  设置特性
GET_STATUS           0x8000  获取状态
SET_DESCRIPTOR       0x0007  设置描述符 (可选)
SYNCH_FRAME          0x800C  同步帧 (Iso)
```

### CDC 串口实战

```text
CDC ACM (Abstract Control Model) 是最常用的 USB 串口

接口布局:
  - Interface 0: Communication (CDC Control)
    - 中断 IN 端点 (通知 host)
  - Interface 1: Data
    - Bulk IN 端点 (device -> host)
    - Bulk OUT 端点 (host -> device)

类描述符:
  - Header
  - Call Management
  - Abstract Control Management
  - Union (CDC 类)

简化版 (省中断 IN):
  - 兼容 Windows 10/11, Linux, macOS
  - 节省 1 个端点
```

### 调试工具

```text
USB 抓包:
  - Wireshark (USBPcap, USB 流量分析)
  - USBlyzer (Windows, 描述符查看)
  - Ellisys USB Explorer (硬件抓包)
  - Total Phase Beagle (硬件抓包)

USB 描述符查看:
  - Windows: 设备管理器 -> 设备属性 -> 详细信息 -> 硬件 ID
  - Linux: lsusb -v
  - macOS: 系统信息 -> USB

USB 调试日志:
  - Linux: dmesg | grep usb
  - Windows: 设备管理器日志
  - 抓包工具
```

### 常见错误码

```text
USBD_OK              0  成功
USBD_BUSY           1  忙
USBD_FAIL           2  失败
USBD_TIMEOUT        3  超时
USBD_ERR_STALL      4  端点 stall
USBD_ERR_MEM        5  内存错
USBD_ERR_PARAM      6  参数错
```

### 端点状态

```text
Idle:    空闲
Busy:    正在传输
Halt:    停止 (host 发 CLEAR_FEATURE 才恢复)
Setup:   接收 setup 包
Stall:   错误, 端点不能工作
NAK:     Not Acknowledge, 暂时不接受 (流控)
NYET:    Not Yet (高速, 流量控制)
```

### VBUS 检测

```text
Device 必须检测 VBUS:
  - 知道插入事件, 开始枚举
  - 知道拔出事件, 复位状态

检测方式:
  - 专用 VBUS 引脚 (e.g. PA9 on STM32)
  - 通过电阻分压
  - 集成在 USB PHY 里

VBUS 检测失败 = 永远不枚举
```

### USB 时钟

```text
USB 时钟精度要求:
  - 全速: 1.5% (e.g. 48 MHz +/- 720 kHz)
  - 高速: 0.05% (e.g. 480 MHz +/- 240 kHz)
  - 通常: HSE 12 MHz / 24 MHz / 48 MHz 晶振
  - 内部 RC 不行 (精度不够)
```

### DMA 触发

```text
适合 DMA:
  - Bulk 端点大数据
  - 等时端点音频/视频
  - 高速传输 (USB 高速模式)

不适合 DMA:
  - 中断端点小数据
  - 控制端点
```

### 描述符长度检查

```text
描述符常见错误:
  - bLength 错 (每种描述符有固定长度)
  - wTotalLength 算错 (Configuration 描述符总长, 含所有 sub)
  - 16 bit 字段用 8 bit 接收 (wTotalLength, wMaxPacketSize)
  - 字符串描述符语言 ID 错

防御: 编译期 sizeof() 断言
```

## 关联文档

- `usb-deep-dive.md` 原理和体系
- `usb-failure-cases.md` 产线死机案例
- `usb-enumeration-and-descriptors.md` 枚举 + 描述符
- `usb-class-drivers.md` CDC / HID / MSC / DFU
- `usb-dma-and-rtos.md` DMA + RTOS 集成
- `usb-vs-other-bus.md` 跨总线对比
- `usb-index.md` 导航
- `usb-dfu-deep-dive.md` DFU 协议 (升级模式)
- `usb-dfu-practical.md` DFU 实战
- `basic/spi-*.md` SPI 类比 (差分信号)
- `can-vs-other-bus.md` 跨总线对比参考

