# USB 枚举与描述符详解

## 目标

枚举 (Enumeration) 是 USB 设备的核心流程, 描述符是 USB 设备的身份证。本文讲清楚:
- 枚举完整流程 (8 步)
- 描述符结构 (Device / Configuration / Interface / Endpoint)
- 字符串描述符和语言 ID
- 类描述符 (HID / CDC / MSC)
- VID / PID 申请
- 复合设备 (Composite Device) + IAD
- 实战代码骨架

## 枚举完整流程

### 8 步流程

```text
1. 设备插入 (VBUS 检测 + D+/D- 上拉)
   - Device 上拉 D+ (全速) 或 D- (低速) 1.5k ohm
   - Host 感知到设备插入, 监听 SE0 (USB Reset)
   
2. Host 发 USB Reset
   - Host 拉低 D+/D- 保持 10 ms
   - 设备进入 Default 状态 (地址 0)
   - 设备按全速枚举
   
3. Host 发 GET_DESCRIPTOR (Device, wLength=8)
   - Device 返回 Device Descriptor 前 8 字节
   - 主机读 bMaxPacketSize0 (EP0 最大包)
   - 主机读 bcdUSB (USB 版本)
   
4. Host 发 SET_ADDRESS
   - Host 分配地址 (1-127)
   - Device 在 50 ms 内响应
   - Device 进入 Address 状态
   
5. Host 发 GET_DESCRIPTOR (Device, wLength=18)
   - Device 返回完整 Device Descriptor (18 字节)
   - 主机读 VID / PID / 类代码 / 配置数
   
6. Host 发 GET_DESCRIPTOR (Configuration)
   - Device 返回 Configuration + 所有 sub-描述符
   - 主机读 wTotalLength, 决定是否分多次读
   
7. Host 发 GET_DESCRIPTOR (String)
   - Device 返回厂商 / 产品 / 序列号
   - 主机显示在设备管理器
   
8. Host 发 SET_CONFIGURATION
   - Host 选 1 个配置
   - Device 进入 Configured 状态
   - 类驱动加载, 应用层通信开始
```

### 状态转移

```text
Attached (物理插入)
  |   ↓ VBUS 稳定 + D+/D- 上拉
  |   ↓ (Host 拉低 D+/D- 10ms = USB Reset)
  |
Default (Reset 后, 地址 0)
  |   ↓ SET_ADDRESS
  |
Address (已分配地址)
  |   ↓ SET_CONFIGURATION
  |
Configured (已配置)
  |   ↓ 总线空闲 3ms+ (全速/低速) 或 3us (高速)
  |
Suspend (挂起, 低功耗)
  |   ↓ Resume 信号 或 远程唤醒
  |
Configured (恢复)
```

### 关键时间

```text
USB Reset 持续: 10 ms (最少 10 ms, 典型 10-20 ms)
SET_ADDRESS 响应: 50 ms 内
GET_DESCRIPTOR 响应: 500 ms 内
Suspend 触发: 3 ms (全速/低速) / 125 us (高速) 空闲
```

## 描述符结构

### 描述符类型

```text
0x01: Device Descriptor
0x02: Configuration Descriptor
0x03: String Descriptor
0x04: Interface Descriptor
0x05: Endpoint Descriptor
0x06: Device Qualifier
0x07: Other Speed Configuration
0x0B: Interface Association Descriptor (IAD)
0x21: HID Descriptor
0x22: HID Report Descriptor
0x29: Hub Descriptor
0x2A: CDC Header Functional Descriptor
0x2B: CDC Call Management
0x2C: CDC ACM Functional Descriptor
0x2D: CDC Union Functional Descriptor
0x2E: CDC Notification Endpoint
```

### Device Descriptor (18 字节)

```c
typedef struct __attribute__((packed)) {
    uint8_t  bLength;            /* 18 */
    uint8_t  bDescriptorType;    /* 0x01 = DEVICE */
    uint16_t bcdUSB;             /* 0x0200 = USB 2.0, 0x0210 = USB 2.1 */
    uint8_t  bDeviceClass;       /* 0 = 由 Interface 指定 */
    uint8_t  bDeviceSubClass;    /* 通常 0 */
    uint8_t  bDeviceProtocol;    /* 通常 0 */
    uint8_t  bMaxPacketSize0;    /* EP0 大小: 8, 16, 32, 64 */
    uint16_t idVendor;           /* VID */
    uint16_t idProduct;          /* PID */
    uint16_t bcdDevice;          /* 设备版本 */
    uint8_t  iManufacturer;      /* 厂商名 string index */
    uint8_t  iProduct;           /* 产品名 string index */
    uint8_t  iSerialNumber;      /* 序列号 string index */
    uint8_t  bNumConfigurations; /* 配置数 (通常 1) */
} usb_device_desc_t;
```

### Configuration Descriptor (9 字节) + Sub

```c
typedef struct __attribute__((packed)) {
    uint8_t  bLength;              /* 9 */
    uint8_t  bDescriptorType;      /* 0x02 = CONFIGURATION */
    uint16_t wTotalLength;         /* 总长 (本 + 所有 sub) */
    uint8_t  bNumInterfaces;       /* 接口数 */
    uint8_t  bConfigurationValue;  /* 配置值 (SET_CONFIGURATION 用) */
    uint8_t  iConfiguration;       /* 配置描述 string index */
    uint8_t  bmAttributes;         /* bit 7: 保留=1 */
                                 /* bit 6: self-powered */
                                 /* bit 5: remote wakeup */
    uint8_t  bMaxPower;            /* 2 mA 单位, 100 = 200 mA, 250 = 500 mA (最大) */
} usb_config_desc_t;
```

### Interface Descriptor (9 字节)

```c
typedef struct __attribute__((packed)) {
    uint8_t  bLength;            /* 9 */
    uint8_t  bDescriptorType;    /* 0x04 = INTERFACE */
    uint8_t  bInterfaceNumber;   /* 接口号 (从 0 开始) */
    uint8_t  bAlternateSetting;  /* 备用设置 (通常 0) */
    uint8_t  bNumEndpoints;      /* 端点数 (除 EP0) */
    uint8_t  bInterfaceClass;    /* 类 */
    uint8_t  bInterfaceSubClass;
    uint8_t  bInterfaceProtocol;
    uint8_t  iInterface;         /* 接口描述 string index */
} usb_interface_desc_t;
```

### Endpoint Descriptor (7 字节)

```c
typedef struct __attribute__((packed)) {
    uint8_t  bLength;           /* 7 */
    uint8_t  bDescriptorType;   /* 0x05 = ENDPOINT */
    uint8_t  bEndpointAddress;   /* bit 7: 方向 (0=OUT, 1=IN) */
                                /* bit 0-3: 端点号 (1-15) */
    uint8_t  bmAttributes;       /* 传输类型 */
                                /* bit 1-0: 0=Control, 1=Iso, 2=Bulk, 3=Interrupt */
                                /* 其他 bit 含义略 */
    uint16_t wMaxPacketSize;     /* 最大包: 8, 16, 32, 64 (FS), 512 (HS) */
    uint8_t  bInterval;          /* 轮询间隔 (ms 或 125us 单位) */
} usb_endpoint_desc_t;
```

### 字符串描述符

```c
/* 字符串描述符 (Type 3) */
typedef struct __attribute__((packed)) {
    uint8_t  bLength;
    uint8_t  bDescriptorType;  /* 0x03 */
    uint16_t bString[];         /* UTF-16LE, 变长 */
} usb_string_desc_t;

/* 语言 ID 描述符 (索引 0) */
typedef struct __attribute__((packed)) {
    uint8_t  bLength;           /* 4 */
    uint8_t  bDescriptorType;   /* 0x03 */
    uint16_t wLANGID;           /* 0x0409 = en-US, 0x0804 = zh-CN */
} usb_langid_desc_t;
```

### 字符串描述符生成

```c
/* 字符串 "ACME Corp" 转 UTF-16LE */
static uint8_t str_desc[64];

void build_string_desc(const char *s) {
    int len = strlen(s);
    str_desc[0] = 2 + len * 2;       /* 长度 */
    str_desc[1] = 0x03;                /* STRING */
    for (int i = 0; i < len; i++) {
        str_desc[2 + i*2] = s[i];      /* UTF-16LE 低字节 */
        str_desc[3 + i*2] = 0;          /* UTF-16LE 高字节 (ASCII 范围内) */
    }
}
```

## 类描述符 (Class-Specific)

### CDC 类描述符

```c
/* CDC Header Functional Descriptor (0x24, 0x00) */
uint8_t cdc_header_desc[] = {
    0x05, 0x24, 0x00,        /* bFunctionLength, CS_INTERFACE, Header */
    0x10, 0x01,              /* bcdCDC (0x0110 = 1.10) */
};

/* CDC Call Management Functional Descriptor (0x24, 0x01) */
uint8_t cdc_call_mgmt_desc[] = {
    0x05, 0x24, 0x01,        /* bFunctionLength, CS_INTERFACE, CallManagement */
    0x00,                    /* bmCapabilities: 0=不处理 call management */
    0x01,                    /* bDataInterface: Interface 1 (Data interface) */
};

/* CDC Abstract Control Management Functional Descriptor (0x24, 0x02) */
uint8_t cdc_acm_desc[] = {
    0x04, 0x24, 0x02,        /* bFunctionLength, CS_INTERFACE, ACM */
    0x02,                    /* bmCapabilities: bit 1 = Line state + Serial state */
};

/* CDC Union Functional Descriptor (0x24, 0x06) */
uint8_t cdc_union_desc[] = {
    0x05, 0x24, 0x06,        /* bFunctionLength, CS_INTERFACE, Union */
    0x00,                    /* bMasterInterface: Interface 0 (Comm) */
    0x01,                    /* bSlaveInterface0: Interface 1 (Data) */
};

/* CDC Notification Functional Descriptor (0x24, 0x07) - 实际不用, 用 Interrupt Endpoint */
```

### HID 类描述符

```c
/* HID Descriptor (0x21) */
typedef struct __attribute__((packed)) {
    uint8_t  bLength;            /* 9 */
    uint8_t  bDescriptorType;    /* 0x21 = HID */
    uint16_t bcdHID;             /* 0x0111 = HID 1.11 */
    uint8_t  bCountryCode;       /* 0 = none */
    uint8_t  bNumDescriptors;    /* 1 (Report) */
    uint8_t  bReportDescriptorType;  /* 0x22 = Report */
    uint16_t wReportDescriptorLength;  /* Report 描述符长度 */
} usb_hid_desc_t;
```

### MSC 类描述符

MSC 没有专门的类描述符, 只需要 Interface Descriptor 类 = 0x08 即可。

### DFU 类描述符

```c
/* DFU Functional Descriptor (0x21) */
typedef struct __attribute__((packed)) {
    uint8_t  bLength;           /* 9 */
    uint8_t  bDescriptorType;   /* 0x21 = DFU */
    uint8_t  bmAttributes;      /* bit 0: willDetach, bit 1: manifestationTolerant, bit 2: canUpload, bit 3: canDownload */
    uint16_t wDetachTimeout;    /* ms */
    uint16_t wTransferSize;     /* max transfer size */
    uint16_t bcdDFUVersion;     /* 0x0100 = 1.0 */
} usb_dfu_desc_t;
```

## 复合设备 (Composite Device) + IAD

### 复合设备定义

```text
复合设备: 一个 USB 设备有多个功能 (e.g. CDC + MSC)
每个功能用 Interface Association Descriptor (IAD) 分组
```

### IAD 结构

```c
/* Interface Association Descriptor (0x0B) */
typedef struct __attribute__((packed)) {
    uint8_t  bLength;            /* 8 */
    uint8_t  bDescriptorType;    /* 0x0B = IAD */
    uint8_t  bFirstInterface;    /* 第一个接口号 */
    uint8_t  bInterfaceCount;    /* 接口数 */
    uint8_t  bFunctionClass;     /* 类 */
    uint8_t  bFunctionSubClass;  /* 子类 */
    uint8_t  bFunctionProtocol;  /* 协议 */
    uint8_t  iFunction;          /* string index */
} usb_iad_desc_t;
```

### 复合设备示例 (CDC + MSC)

```c
/* Configuration Descriptor 总结构 */
uint8_t config_desc[] = {
    /* Configuration Descriptor */
    0x09, 0x02, ...,
    
    /* IAD for CDC */
    0x08, 0x0B, 0x00, 0x02, 0x02, 0x02, 0x01, 0x00,
    /* Interface 0: CDC Comm */
    0x09, 0x04, 0x00, 0x00, 0x00, 0x02, 0x02, 0x01, 0x00,
    /* CDC Header, CallMgmt, ACM, Union */
    /* Interface 1: CDC Data */
    0x09, 0x04, 0x01, 0x00, 0x02, 0x0A, 0x00, 0x00, 0x00,
    /* EP IN, EP OUT */
    
    /* IAD for MSC */
    0x08, 0x0B, 0x02, 0x01, 0x08, 0x06, 0x50, 0x00,
    /* Interface 2: MSC */
    0x09, 0x04, 0x02, 0x00, 0x02, 0x08, 0x06, 0x50, 0x00,
    /* EP IN, EP OUT */
};
```

## VID / PID 申请

### 申请流程

```text
1. 访问 https://www.usb.org/getting-vendor-id
2. 填写申请表
3. 付费 ($5000 USD, 一次性)
4. 收到 4 位十六进制 VID (e.g. 0x1234)
5. 厂商内部维护 PID 表
```

### PID 分配

```text
每个产品一个唯一 PID
PID 由厂商维护, 不需要申请
建议:
  - PID = 0x0001: 产品 A
  - PID = 0x0002: 产品 A 升级版
  - PID = 0x0010: 产品 B
  - PID = 0x0011: 产品 B 升级版
```

### 临时方案 (开发期间)

```text
如果 VID 申请周期长:
  - 用测试 PID (e.g. 0x0001)
  - 量产前换成正式 VID
  - Windows 每次都重新装驱动 (PID 变 = 设备变)
```

## 标准请求 (Setup) 详解

### Setup 数据格式

```c
typedef struct __attribute__((packed)) {
    uint8_t  bmRequestType;  /* 方向 + 类型 + 接收方 */
    uint8_t  bRequest;
    uint16_t wValue;
    uint16_t wIndex;
    uint16_t wLength;
} usb_setup_t;
```

### bmRequestType 解码

```text
bit 7:   数据方向 (0=Host-to-Device, 1=Device-to-Host)
bit 6-5: 类型
         00 = Standard
         01 = Class
         10 = Vendor
         11 = Reserved
bit 4-0: 接收方
         00000 = Device
         00001 = Interface
         00010 = Endpoint
         00011 = Other
```

### 常见 Standard 请求

```c
/* GET_DESCRIPTOR (0x8006) */
wValue = (DESC_TYPE << 8) | DESC_INDEX
wIndex = 0 (或语言 ID)
wLength = 期望长度

/* SET_ADDRESS (0x0005) */
wValue = 新地址
wIndex = 0
wLength = 0

/* SET_CONFIGURATION (0x0009) */
wValue = 配置值
wIndex = 0
wLength = 0

/* GET_CONFIGURATION (0x8008) */
wValue = 0
wIndex = 0
wLength = 1

/* CLEAR_FEATURE (0x0001) */
wValue = 特性选择子 (e.g. ENDPOINT_HALT = 0)
wIndex = 端点地址 (e.g. 0x81)
wLength = 0

/* SET_FEATURE (0x0003) */
wValue = 特性选择子
wIndex = 端点地址
wLength = 0

/* GET_STATUS (0x8000) */
wValue = 0
wIndex = 设备 / 接口 / 端点
wLength = 2
```

### 常见 Class 请求 (CDC)

```c
/* CDC 通信接口 Class 请求 (0x21) */
SET_LINE_CODING (0x20):
  wValue = 0
  wIndex = Communication Interface
  wLength = 7
  Data: dwDTERate (4 byte), bCharFormat, bParityType, bDataBits

GET_LINE_CODING (0x21):
  wValue = 0
  wIndex = Communication Interface
  wLength = 7

SET_CONTROL_LINE_STATE (0x22):
  wValue = DTR (bit 0) + RTS (bit 1)
  wIndex = Communication Interface
  wLength = 0
```

## 实战: 完整 CDC ACM 描述符

```c
/* 单 CDC ACM 串口, 简化版 (去中断 IN) */
static const uint8_t cdc_acm_full_desc[] = {
    /* Configuration Descriptor */
    0x09, 0x02, 
    0x4B, 0x00,                  /* wTotalLength = 75 字节 */
    0x02,                        /* bNumInterfaces = 2 */
    0x01,                        /* bConfigurationValue */
    0x00,                        /* iConfiguration */
    0xC0,                        /* bmAttributes: self-powered, no remote wakeup */
    0x32,                        /* bMaxPower = 100 (200 mA) */
    
    /* IAD */
    0x08, 0x0B, 0x00, 0x02, 0x02, 0x02, 0x01, 0x04,
    
    /* Interface 0: CDC Comm (类 0x02) */
    0x09, 0x04, 0x00, 0x00, 0x00, 0x02, 0x02, 0x01, 0x00,
    /* CDC Header */
    0x05, 0x24, 0x00, 0x10, 0x01,
    /* Call Management */
    0x05, 0x24, 0x01, 0x00, 0x01,
    /* ACM */
    0x04, 0x24, 0x02, 0x02,
    /* Union */
    0x05, 0x24, 0x06, 0x00, 0x01,
    /* bNumEndpoints = 0 (去中断 IN) */
    
    /* Interface 1: CDC Data (类 0x0A) */
    0x09, 0x04, 0x01, 0x00, 0x02, 0x0A, 0x00, 0x00, 0x00,
    /* Endpoint OUT (Bulk) */
    0x07, 0x05, 0x01, 0x02, 0x40, 0x00, 0x00,
    /* Endpoint IN (Bulk) */
    0x07, 0x05, 0x81, 0x02, 0x40, 0x00, 0x00,
};

/* 验证 wTotalLength */
_Static_assert(sizeof(cdc_acm_full_desc) == 75, "CDC config descriptor size mismatch");
```

## 端点资源管理

### 不同 MCU 端点资源

| MCU | EP0 | 数据端点 | 总端点 |
| --- | --- | --- | --- |
| STM32F103 | 1 | 3 | 4 |
| STM32F407 | 1 | 3 | 4 |
| STM32F723 | 1 | 5 | 6 |
| STM32H743 | 1 | 6 | 7 |
| NXP LPC55 | 1 | 6 | 7 |
| ESP32-S2/S3 | 1 | 6 | 7 |
| 沁恒 CH32V208 | 1 | 7 | 8 |
| 沁恒 CH32V307 | 1 | 15 | 16 |

### 简化 CDC 端点消耗

```text
标准 CDC: EP0 + 中断 IN + Bulk IN + Bulk OUT = 4 端点
简化 CDC (去中断 IN): EP0 + Bulk IN + Bulk OUT = 3 端点
差异: 1 个端点号

适用场景:
  端点紧缺的 MCU (e.g. STM32F103): 用简化 CDC, 留端点给其他功能
  端点充足的 MCU: 用标准 CDC, Notification 能用
```

## 调试枚举

### Windows 工具

```text
设备管理器 -> 看 Unknown Device / 黄色叹号
右键 -> 属性 -> 详细信息 -> 硬件 ID (VID/PID)
右键 -> 属性 -> 事件 -> 看错误码
设备管理器 -> 视图 -> 设备 (按连接) -> 找 USB 树
```

### Linux 工具

```bash
# 列出 USB 设备
lsusb

# 详细描述符
lsusb -v -d VID:PID

# 实时插入/拔插日志
dmesg -w

# USB 抓包 (内核 2.6+)
usbmon

# 卸载 / 重新加载驱动
modprobe -r usbhid
modprobe usbhid
```

### macOS 工具

```bash
# 系统信息 -> USB
system_profiler SPUSBDataType

# 抓包
# macOS 没有原生 USB 抓包, 用 Wireshark + USBPcap (Windows / macOS 不支持)
```

## 7 条枚举常见错误

| # | 错误 | 后果 |
| --- | --- | --- |
| 1 | wTotalLength 算错 | 枚举失败 |
| 2 | 16 bit 字段用 8 bit 接收 | 描述符截断 |
| 3 | bMaxPacketSize0 错 | 高速枚举失败 |
| 4 | 字符串语言 ID 错 | 字符串乱码 |
| 5 | 端点地址冲突 | 数据错乱 |
| 6 | CDC 没 IAD | Windows 识别为 2 个独立设备 |
| 7 | 复合设备 IAD 错 | 部分功能缺失 |

## 关联文档

- `usb-deep-dive.md` 原理
- `usb-practical.md` 速查
- `usb-failure-cases.md` 产线案例
- `usb-class-drivers.md` CDC / HID / MSC / DFU
- `usb-dma-and-rtos.md` DMA + RTOS
- `usb-vs-other-bus.md` 跨总线对比
- `usb-index.md` 导航
- `usb-dfu-deep-dive.md` DFU 协议
- `usb-dfu-practical.md` DFU 实战
