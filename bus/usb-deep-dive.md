# USB Deep Dive

## 目标

本文深入 USB 工程细节，重点覆盖标准请求、描述符层级、复合设备、CDC/HID/MSC、Endpoint 0、设备状态、Remote Wakeup、Type-C/PD 边界和枚举失败定位。

## USB 设备状态

USB Device 常见状态：

```text
Attached
Powered
Default
Addressed
Configured
Suspended
```

设备只有进入 Configured 后，非 EP0 的业务 Endpoint 才能正常工作。

## Endpoint 0

Endpoint 0 是默认控制端点。

负责：

- 读取描述符。
- 设置地址。
- 设置配置。
- 标准请求。
- 类请求。
- 厂商请求。

EP0 实现不稳定会导致所有 USB 类都不可靠。

## 标准请求

常见标准请求：

| 请求 | 含义 |
| --- | --- |
| GET_DESCRIPTOR | 读取描述符 |
| SET_ADDRESS | 设置设备地址 |
| SET_CONFIGURATION | 设置配置 |
| GET_CONFIGURATION | 获取配置 |
| GET_STATUS | 获取状态 |
| CLEAR_FEATURE | 清除特性 |
| SET_FEATURE | 设置特性 |

枚举抓包时重点看这些请求是否正确响应。

## 描述符层级

典型结构：

```text
Device Descriptor
Configuration Descriptor
  Interface Descriptor
    Endpoint Descriptor
    Class-specific Descriptor
```

复合设备会有多个 Interface。

Configuration 的总长度必须覆盖所有下级描述符。

## 复合设备

复合设备例如：

```text
CDC + HID
CDC + MSC
Audio + HID
```

要点：

- Interface 编号不能冲突。
- Endpoint 地址不能冲突。
- 类描述符要放在正确 Interface 下。
- Windows 可能需要 IAD 描述符识别 CDC 复合设备。

## CDC 深入注意

CDC ACM 常见接口：

```text
Communication Interface
Data Interface
Interrupt IN Endpoint
Bulk IN Endpoint
Bulk OUT Endpoint
```

常见问题：

- Host 未设置 DTR，设备不输出。
- Line Coding 请求未处理。
- Bulk 包长和缓冲区不匹配。
- 断开重连后状态未清理。

## HID 深入注意

HID 的核心是 Report Descriptor。

常见问题：

- Report 长度和 Endpoint 包长不匹配。
- Usage Page/Usage 写错。
- Input/Output/Feature 报告方向混乱。
- Host 轮询周期不符合预期。

## MSC 深入注意

MSC 常见协议栈：

```text
Bulk-Only Transport
SCSI 命令集
Block device
File system
```

常见风险：

- Host 缓存导致拔出前数据未写完。
- MCU 和 Host 同时改文件系统。
- 扇区读写没有对齐。
- 存储介质擦写寿命。

## Suspend 和 Remote Wakeup

USB Host 可让设备进入 suspend。

设备要注意：

- 降低功耗。
- 保持必要唤醒状态。
- Remote Wakeup 需要 Host 授权。
- resume 时恢复时钟和 Endpoint 状态。

## Type-C 和 PD 边界

Type-C 是连接器和角色检测体系。

USB PD 是电源协商协议。

普通 USB 2.0 Device 使用 Type-C 时也要正确处理 CC：

```text
Sink 侧 Rd 下拉
Source 侧 Rp 上拉
```

不要把 Type-C 当成只换了连接器。

## 枚举失败定位

| 阶段 | 可能问题 |
| --- | --- |
| 插入无反应 | VBUS、D+/D-、CC、上拉、时钟 |
| Default 失败 | Bus reset、EP0、时钟 |
| 读描述符失败 | 描述符长度、EP0 buffer |
| 设置地址失败 | USB 栈状态机 |
| 设置配置失败 | 配置总长度、Endpoint 冲突 |
| 类驱动失败 | 类描述符、VID/PID、驱动匹配 |

## 深度检查清单

- EP0 标准请求完整。
- 描述符长度和层级正确。
- Endpoint 地址唯一。
- 复合设备 IAD 处理正确。
- 类请求已实现。
- Suspend/Resume 状态正确。
- Type-C CC 角色正确。
- 枚举失败时有抓包或系统日志。

## USB 协议的本质

USB (Universal Serial Bus) 是 1996 年由 Compaq / Intel / Microsoft 等联合推出的串行总线标准。

**适用场景**:
- PC 外设 (键鼠, U 盘, 打印机)
- 嵌入式设备 (调试口, 数据采集, 固件升级)
- 充电 (Type-C 普及)
- 视频 / 音频 (UVC, UAC)
- 工业 / 医疗 / 车载

**不适用**:
- 长距离 (> 5m 用 USB Hub 或光纤)
- 实时工业控制 (用 CAN, EtherCAT)
- 板内通信 (用 SPI/I2C)
- 极低功耗传感器

工程直觉:
```text
USB 是"PC 时代的标准接口", 强在通用性和生态
USB 不是"工业实时总线", 强在兼容性
```

## USB 物理层

### 信号

```text
USB 1.x / 2.0 (低速 / 全速 / 高速):
  - D+ 和 D- 差分信号
  - 电压: 3.3V 单端
  - 全速: 12 Mbaud, NRZI 编码
  - 高速: 480 Mbaud, 仍 NRZI, 加 bit stuffing
  - 上拉电阻决定速度:
    - D+ 上拉 1.5k ohm 到 3.3V = 全速
    - D- 上拉 1.5k ohm 到 3.3V = 低速
    - 高速协商后切换到 45 ohm 终端

USB 3.0 / 3.1 (SuperSpeed):
  - 新增 TX+/TX-, RX+/RX- 差分对
  - 与 USB 2.0 兼容 (D+/D-)
  - 5 Gbps / 10 Gbps
```

### NRZI 编码

```text
NRZI (Non Return to Zero Inverted):
  - 0 -> 电平翻转
  - 1 -> 电平保持
  - 保证时钟信息

bit stuffing:
  - 6 个连续 1 后插入 1 个 0
  - 接收方去填充
```

### 包结构 (USB 1.x / 2.0)

```text
所有 USB 包:
  - SYNC 字段 (8 bit, 同步)
  - PID  (8 bit, 包类型)
  - 数据 (变长)
  - CRC (16 bit, 校验)
  - EOP  (End of Packet)

包类型:
  - Token: SETUP, IN, OUT, SOF (Start of Frame)
  - Data: DATA0, DATA1
  - Handshake: ACK, NAK, STALL, NYET
  - Special: PRE (低速前导), ERR (高速错误)
```

### 事务 (Transaction)

```text
USB 事务 = Token + Data + Handshake

IN 事务 (Device -> Host):
  Host  -> Device: IN Token
  Device -> Host: DATA (或 NAK / STALL)
  Host  -> Device: ACK (如果收到 DATA)

OUT 事务 (Host -> Device):
  Host  -> Device: OUT Token + DATA
  Device -> Host: ACK (或 NAK / STALL)

SETUP 事务:
  Host  -> Device: SETUP Token + 8 byte SETUP 数据
  Device -> Host: ACK
```

### 帧 / 微帧

```text
全速: 1 ms 帧
  - 每帧 1500 字节 (max)
  - 1 个 SOF (Start of Frame)

高速: 125 us 微帧
  - 8 个微帧 = 1 帧
  - 1 ms 帧 = 8 微帧
```

## USB 枚举 (Enumeration)

### 完整流程

```text
1. 设备插入 (VBUS 检测)
2. 设备 D+ / D- 上拉 1.5k ohm 到 3.3V (Host 感知)
3. Host 发出 USB Reset (保持 D+/D- 低 10 ms)
4. 设备进入 Default 状态
5. Host 发 GET_DESCRIPTOR (Device), 读取 8 字节
   - 读 bMaxPacketSize0 (EP0 最大包)
6. Host 发 SET_ADDRESS (分配地址, 默认 0)
7. 设备进入 Address 状态
8. Host 发 GET_DESCRIPTOR (Device, 18 字节)
9. Host 发 GET_DESCRIPTOR (Configuration)
10. Host 发 SET_CONFIGURATION (选 1 个配置)
11. 设备进入 Configured 状态
12. 类驱动加载, 应用层通信开始
```

### 设备状态机

```text
Attached       刚插入
Powered        VBUS 供电
Default        Reset 后, 地址 0
Address        分配了地址
Configured     配置完成
Suspend        总线空闲 3 ms (低速 / 全速) 或 3 us (高速)
```

### 关键请求

```text
GET_DESCRIPTOR (0x8006):
  - wValue 高 8 bit: 描述符类型
    1 = Device
    2 = Configuration
    3 = String
    4 = Interface
    5 = Endpoint
    6 = Device Qualifier
    7 = Other Speed Configuration
    11 = Interface Association
    0x21 = HID
    0x22 = HID Report
    0x2B = CDC 类特定
  - wValue 低 8 bit: 描述符索引
  - wIndex: 语言 ID (字符串) 或 0
  - wLength: 期望长度

SET_ADDRESS (0x0005):
  - wValue: 新地址 (1-127)
  - Device 必须在 50 ms 内响应

SET_CONFIGURATION (0x0009):
  - wValue: 配置值 (1-N) 或 0 (去配置)
  - Device 必须响应

CLEAR_FEATURE (0x0001):
  - 清 HALT 端点 (wValue = 0, wIndex = 端点)
  - 清 DEVICE_REMOTE_WAKEUP (wValue = 1)
  - 清 TEST_MODE (wValue = 2)
```

## 描述符详解

### Device Descriptor (18 字节)

```c
typedef struct __attribute__((packed)) {
    uint8_t  bLength;            /* 18 */
    uint8_t  bDescriptorType;    /* 1 = DEVICE */
    uint16_t bcdUSB;             /* USB 版本, 0x0200 = USB 2.0 */
    uint8_t  bDeviceClass;       /* 类代码 (0 = 由 Interface 指定) */
    uint8_t  bDeviceSubClass;
    uint8_t  bDeviceProtocol;
    uint8_t  bMaxPacketSize0;    /* EP0 最大包: 8, 16, 32, 64 */
    uint16_t idVendor;           /* VID, 必须向 USB-IF 申请 */
    uint16_t idProduct;          /* PID, 自己定 */
    uint16_t bcdDevice;          /* 设备版本 */
    uint8_t  iManufacturer;      /* 厂商字符串索引 */
    uint8_t  iProduct;           /* 产品字符串索引 */
    uint8_t  iSerialNumber;      /* 序列号字符串索引 */
    uint8_t  bNumConfigurations; /* 配置数量 */
} usb_device_desc_t;
```

### Configuration Descriptor (9 字节) + 子描述符

```c
typedef struct __attribute__((packed)) {
    uint8_t  bLength;              /* 9 */
    uint8_t  bDescriptorType;      /* 2 = CONFIGURATION */
    uint16_t wTotalLength;         /* 总长度 (本 + 所有 sub) */
    uint8_t  bNumInterfaces;       /* 接口数量 */
    uint8_t  bConfigurationValue;  /* 配置值 */
    uint8_t  iConfiguration;       /* 字符串索引 */
    uint8_t  bmAttributes;         /* bit 6: self-powered, bit 5: remote wakeup */
    uint8_t  bMaxPower;            /* 2 mA 单位, 100 = 200 mA */
} usb_config_desc_t;
```

### Interface Descriptor (9 字节)

```c
typedef struct __attribute__((packed)) {
    uint8_t  bLength;            /* 9 */
    uint8_t  bDescriptorType;    /* 4 = INTERFACE */
    uint8_t  bInterfaceNumber;   /* 接口号 */
    uint8_t  bAlternateSetting;  /* 备用设置 */
    uint8_t  bNumEndpoints;      /* 端点数 (除 EP0) */
    uint8_t  bInterfaceClass;    /* 类 */
    uint8_t  bInterfaceSubClass;
    uint8_t  bInterfaceProtocol;
    uint8_t  iInterface;         /* 字符串索引 */
} usb_interface_desc_t;
```

### Endpoint Descriptor (7 字节)

```c
typedef struct __attribute__((packed)) {
    uint8_t  bLength;           /* 7 */
    uint8_t  bDescriptorType;   /* 5 = ENDPOINT */
    uint8_t  bEndpointAddress;   /* bit 7: 方向 (0=OUT, 1=IN) */
                                /* bit 0-3: 端点号 (1-15) */
    uint8_t  bmAttributes;       /* 传输类型 */
                                /* 0=Control, 1=Iso, 2=Bulk, 3=Interrupt */
    uint16_t wMaxPacketSize;     /* 最大包大小 (8, 16, 32, 64, 512) */
    uint8_t  bInterval;          /* 轮询间隔 (1-255 ms) */
} usb_endpoint_desc_t;
```

### 字符串描述符

```text
字符串描述符 (Type 3):
  字节 0: bLength
  字节 1: 0x03 (STRING)
  字节 2+: UTF-16LE 字符串

字符串索引 0 = 语言 ID 描述符:
  字节 0: 4
  字节 1: 0x03
  字节 2-3: 语言 ID (e.g. 0x0409 = en-US)
  字节 4-5: 子语言 ID
```

### HID 报告描述符

```c
/* HID Report Descriptor */
/* 复杂, 描述报告的格式 (usage page, usage, logical min/max, etc.) */
uint8_t hid_report_desc[] = {
    0x05, 0x01,       /* Usage Page (Generic Desktop) */
    0x09, 0x06,       /* Usage (Keyboard) */
    0xA1, 0x01,       /* Collection (Application) */
    0x05, 0x07,       /*   Usage Page (Keyboard) */
    0x19, 0xE0,       /*   Usage Minimum (224) */
    0x29, 0xE7,       /*   Usage Maximum (231) */
    0x15, 0x00,       /*   Logical Minimum (0) */
    0x25, 0x01,       /*   Logical Maximum (1) */
    0x75, 0x01,       /*   Report Size (1) */
    0x95, 0x08,       /*   Report Count (8) */
    0x81, 0x02,       /*   Input (Data, Var, Abs) - Modifiers */
    0x95, 0x01,       /*   Report Count (1) */
    0x75, 0x08,       /*   Report Size (8) */
    0x81, 0x03,       /*   Input (Const, Var, Abs) - Reserved */
    0x95, 0x05,       /*   Report Count (5) */
    0x75, 0x01,       /*   Report Size (1) */
    0x05, 0x08,       /*   Usage Page (LEDs) */
    0x19, 0x01,       /*   Usage Minimum (1) */
    0x29, 0x05,       /*   Usage Maximum (5) */
    0x91, 0x02,       /*   Output (Data, Var, Abs) - LEDs */
    0x95, 0x01,       /*   Report Count (1) */
    0x75, 0x03,       /*   Report Size (3) */
    0x91, 0x03,       /*   Output (Const, Var, Abs) - LED Padding */
    0x95, 0x06,       /*   Report Count (6) */
    0x75, 0x08,       /*   Report Size (8) */
    0x15, 0x00,       /*   Logical Minimum (0) */
    0x26, 0xFF, 0x00, /*   Logical Maximum (255) */
    0x05, 0x07,       /*   Usage Page (Keyboard) */
    0x19, 0x00,       /*   Usage Minimum (0) */
    0x2A, 0xFF, 0x00, /*   Usage Maximum (255) */
    0x81, 0x00,       /*   Input (Data, Array) - Keycodes */
    0xC0              /* End Collection */
};
```

## USB 故障树

```text
现象: USB 设备不被 PC 识别
  |
  +-- 完全没有反应
  |     -> VBUS 检测 / 供电 / 时钟
  |     -> 验证: 量 VBUS (5V), 量 1.5k 上拉
  |
  +-- 看到 Unknown Device
  |     -> 描述符错 / 设备类请求失败
  |     -> 验证: 抓包 GET_DESCRIPTOR, 看返回数据
  |
  +-- 看到但有黄色叹号
  |     -> Windows 错误码 (Code 10 / 28 / 43 等)
  |     -> 验证: 设备管理器看错误码, 查驱动
  |
  +-- 枚举成功但传输错
  |     -> 端点错 / 数据错 / 协议错
  |     -> 验证: Wireshark 抓包, 看端点状态
  |
  +-- 频繁断连
  |     -> VBUS 跌落 / 信号完整性 / Hub 问题
  |     -> 验证: 量 VBUS 波形, 换 Hub
  |
  +-- 高速 (480M) 跑不通
        -> 物理层 / Hub 不支持 / 信号完整性
        -> 验证: 用 2.0 端口测试, 检查 Hub
```

### 故障树对应快速判定

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 完全没反应 | VBUS / 供电 / 时钟 | 量 VBUS, 查时钟 |
| Unknown Device | 描述符错 | 抓包 GET_DESCRIPTOR |
| 黄色叹号 Code 10 | 启动失败 | 设备管理器看错误 |
| 黄色叹号 Code 28 | 驱动没装 | 装 WinUSB / libusb 驱动 |
| 黄色叹号 Code 43 | 描述符错 | 抓包分析 |
| 枚举后断连 | VBUS 跌落 | 量 VBUS 波形 |
| 高速跑不通 | 物理层 | 用 2.0 Hub 测试 |
| CDC 串口打不开 | CDC 描述符错 | 查 CDC ACM 描述符 |

## 端点详解

### 端点号 (bEndpointAddress)

```text
端点地址 = 端点号 + 方向

端点号 (1-15): Device 内唯一
方向 (bit 7): 0 = OUT, 1 = IN

例:
  0x81 = IN 端点 1
  0x01 = OUT 端点 1
  0x82 = IN 端点 2
```

### 端点类型 (bmAttributes)

```text
bit 1-0:
  00 = Control
  01 = Isochronous
  10 = Bulk
  11 = Interrupt

bit 3-2 (同步类型, 用于 Iso):
  00 = No Synchronization
  01 = Asynchronous
  10 = Adaptive
  11 = Synchronous

bit 5-4 (使用类型, 用于 Iso):
  00 = Data endpoint
  01 = Feedback endpoint
  10 = Implicit feedback data endpoint

Control: EP0 固定, 其他端点可选
Bulk / Interrupt: 每个接口 N 个
Iso: 固定带宽
```

### 最大包大小

```text
全速:
  - EP0: 8, 16, 32, 64
  - Bulk: 8, 16, 32, 64
  - Interrupt: <= 64
  - Iso: <= 1023

高速:
  - EP0: 64
  - Bulk: 512
  - Interrupt: <= 1024
  - Iso: <= 1024
```

### 轮询间隔 (bInterval)

```text
全速: 1-255 ms
高速: 1-16 (125 us - 2 ms, 1 单位 = 125 us)

Interrupt 端点必须有 bInterval:
  - HID 键盘: 10 ms (全速), 1 (高速 125 us)
  - CDC 中断: 255 ms (全速)
```

## 控制传输 (Control Transfer)

### 3 阶段

```text
SETUP 阶段:
  Host -> Device: SETUP Token + 8 字节 setup 数据
  Device -> Host: ACK

数据阶段 (如果有):
  IN:  Device -> Host: DATA
  OUT: Host -> Device: DATA
  (用 DATA0/DATA1 切换)
  
状态阶段:
  方向与数据阶段相反
  接收方: ACK
  发送方: 收到 ACK 表示完成
```

### Setup 数据 (8 字节)

```c
typedef struct __attribute__((packed)) {
    uint8_t  bmRequestType;   /* 方向 + 类型 + 接收方 */
    uint8_t  bRequest;        /* 请求 */
    uint16_t wValue;          /* 值 */
    uint16_t wIndex;          /* 索引 */
    uint16_t wLength;         /* 数据阶段长度 */
} usb_setup_t;

/* bmRequestType:
   bit 7:   数据方向 (0=Host->Device, 1=Device->Host)
   bit 6-5: 类型 (0=Standard, 1=Class, 2=Vendor, 3=Reserved)
   bit 4-0: 接收方 (0=Device, 1=Interface, 2=Endpoint, 3=Other)
*/
```

## USB 类驱动

### CDC (Communication Device Class)

```text
最常见: CDC ACM (Abstract Control Model)
用于 USB 转串口

接口:
  Interface 0: Communication (类 0x02)
    - Header, Call Management, ACM, Union 类描述符
    - 中断 IN 端点 (通知 host)
  Interface 1: Data (类 0x0A)
    - Bulk IN 端点
    - Bulk OUT 端点

简化版 (去中断 IN):
  - bNumEndpoints = 0
  - 兼容 Windows 10/11
  - 节省 1 个端点
```

### HID (Human Interface Device)

```text
用于键鼠 / 触摸 / 自定义设备

接口:
  Interface 0: HID (类 0x03)
    - HID 描述符
    - Report 描述符
    - 中断 IN 端点 (设备 -> host)
    - 可选中断 OUT 端点 (host -> 设备)

Report 描述符是核心, 定义数据格式
```

### MSC (Mass Storage Class)

```text
用于 U 盘 / SD 卡读卡器

接口:
  Interface 0: MSC (类 0x08)
    - Bulk IN 端点
    - Bulk OUT 端点
    - Bulk-Only Transport (BOT) 协议
    - SCSI 命令集 (READ, WRITE, INQUIRY 等)
```

### DFU (Device Firmware Upgrade)

```text
用于固件升级

接口:
  Interface 0: DFU (类 0xFE, 子类 0x01)
    - 仅 EP0 (无其他端点)
    - DFU 协议 (detach, download, upload, manifest)
    - 用于 bootloader 升级
```

## USB 速度协商

### 协商流程 (全速 -> 高速)

```text
1. 设备以全速枚举 (D+ 上拉 1.5k)
2. Host 发 USB Test Packet (高速 chirp)
3. 设备如果支持高速, 反射 K chirp
4. Host 看到 chirp, 切到高速信号电平 (45 ohm 终端)
5. 设备切到高速, 发高速 SOF
6. Host 重新发 USB Reset
7. 设备高速枚举
```

### 高速协商失败

```text
原因:
  - Hub 不支持高速
  - 高速信号完整性差
  - 设备实际只有全速能力

回退:
  - 设备自动回全速
  - 但有些 Host 看到高速失败会停枚举
```

## USB 状态机

```text
Attached (刚插入)
  |   ↓ VBUS 稳定
  |   ↓ D+/D- 上拉
  |
Powered (供电)
  |   ↓ Host 检测 + Reset
  |
Default (Reset 后, 地址 0)
  |   ↓ SET_ADDRESS
  |
Address (已分配地址)
  |   ↓ SET_CONFIGURATION
  |
Configured (已配置)
  |   ↓ 总线空闲 3 ms+
  |
Suspend (挂起, 低功耗)
  |   ↓ Resume 信号
  |
Configured (恢复)
```

## 7 条 USB 常见错误

| # | 错误 | 后果 |
| --- | --- | --- |
| 1 | VID 未申请 | 驱动加载失败 |
| 2 | 描述符 wTotalLength 算错 | 枚举失败 |
| 3 | EP0 大小用 8 错配 | 全速 OK, 高速失败 |
| 4 | CDC 没有中断 IN | 某些 OS 兼容性差 |
| 5 | HID Report 描述符错 | 设备被识别但不响应 |
| 6 | 高速协商失败 | 始终全速 |
| 7 | 字符串描述符语言 ID 错 | 字符串乱码 |

## 关联文档

- `usb-practical.md` 速查
- `usb-failure-cases.md` 产线案例
- `usb-enumeration-and-descriptors.md` 枚举详细
- `usb-class-drivers.md` CDC / HID / MSC / DFU
- `usb-dma-and-rtos.md` DMA + RTOS
- `usb-vs-other-bus.md` 跨总线对比
- `usb-index.md` 导航
- `usb-dfu-deep-dive.md` DFU 协议
- `usb-dfu-practical.md` DFU 实战

- 枚举失败有抓包或系统日志。
