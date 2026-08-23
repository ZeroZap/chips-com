# USB 类驱动专题 (CDC / HID / MSC / DFU)

## 目标

USB 类驱动 (Class Driver) 是 USB 设备功能的核心。本文深入 4 个最常用的类:
- **CDC** (Communication Device Class, 串口)
- **HID** (Human Interface Device, 键鼠/自定义)
- **MSC** (Mass Storage Class, U 盘)
- **DFU** (Device Firmware Upgrade, 升级)

每个类讲清楚: 协议栈、描述符、Class 请求、实战代码。

## CDC (Communication Device Class)

### 协议栈

```text
Application: printf / scanf
  |
CDC ACM (Abstract Control Model):
  - 串口语义 (波特率, 数据位, 停止位, 校验)
  - 流控 (DTR, RTS)
  - 状态通知 (SerialState, Break)
  |
USB Bulk / Interrupt 传输
  |
USB 物理层 (全速 / 高速)
```

### 完整描述符 (标准版)

```c
static const uint8_t cdc_acm_desc[] = {
    /* Configuration Descriptor */
    0x09, 0x02, 0x5C, 0x00, 0x02, 0x01, 0x00, 0xC0, 0x32,
    
    /* IAD */
    0x08, 0x0B, 0x00, 0x02, 0x02, 0x02, 0x01, 0x04,
    
    /* Interface 0: CDC Communication */
    0x09, 0x04, 0x00, 0x00, 0x01, 0x02, 0x02, 0x01, 0x00,
    /* CDC Header */
    0x05, 0x24, 0x00, 0x10, 0x01,
    /* Call Management */
    0x05, 0x24, 0x01, 0x00, 0x01,
    /* ACM */
    0x04, 0x24, 0x02, 0x02,
    /* Union */
    0x05, 0x24, 0x06, 0x00, 0x01,
    /* Notification Endpoint (Interrupt IN) */
    0x07, 0x05, 0x83, 0x03, 0x08, 0x00, 0xFF,
    
    /* Interface 1: CDC Data */
    0x09, 0x04, 0x01, 0x00, 0x02, 0x0A, 0x00, 0x00, 0x00,
    /* Endpoint OUT (Bulk) */
    0x07, 0x05, 0x02, 0x02, 0x40, 0x00, 0x00,
    /* Endpoint IN (Bulk) */
    0x07, 0x05, 0x82, 0x02, 0x40, 0x00, 0x00,
};
```

### 简化描述符 (去中断 IN)

```c
/* 节省 1 个端点, 兼容 Windows 10/11, Linux, macOS */
static const uint8_t cdc_acm_simple_desc[] = {
    0x09, 0x02, 0x4B, 0x00, 0x02, 0x01, 0x00, 0xC0, 0x32,
    
    /* IAD */
    0x08, 0x0B, 0x00, 0x02, 0x02, 0x02, 0x01, 0x04,
    
    /* Interface 0: CDC Communication */
    0x09, 0x04, 0x00, 0x00, 0x00, 0x02, 0x02, 0x01, 0x00,
    0x05, 0x24, 0x00, 0x10, 0x01,
    0x05, 0x24, 0x01, 0x00, 0x01,
    0x04, 0x24, 0x02, 0x02,
    0x05, 0x24, 0x06, 0x00, 0x01,
    /* bNumEndpoints = 0 (去中断 IN) */
    
    /* Interface 1: CDC Data */
    0x09, 0x04, 0x01, 0x00, 0x02, 0x0A, 0x00, 0x00, 0x00,
    /* Endpoint OUT */
    0x07, 0x05, 0x01, 0x02, 0x40, 0x00, 0x00,
    /* Endpoint IN */
    0x07, 0x05, 0x81, 0x02, 0x40, 0x00, 0x00,
};
```

### CDC Class 请求

```c
/* SET_LINE_CODING (0x20) */
typedef struct __attribute__((packed)) {
    uint32_t dwDTERate;      /* 波特率 (e.g. 115200) */
    uint8_t  bCharFormat;    /* 0=1 stop, 1=1.5 stop, 2=2 stop */
    uint8_t  bParityType;    /* 0=None, 1=Odd, 2=Even, 3=Mark, 4=Space */
    uint8_t  bDataBits;      /* 5, 6, 7, 8, 16 */
} cdc_line_coding_t;

/* 处理 SET_LINE_CODING */
void cdc_set_line_coding(cdc_line_coding_t *coding) {
    /* 1. 存配置 */
    g_cdc_coding = *coding;
    /* 2. 重配 UART (如果用 UART 桥接) */
    uart_configure(coding->dwDTERate, coding->bDataBits, 
                   coding->bParityType, coding->bCharFormat);
}

/* GET_LINE_CODING (0x21) - 返回当前配置 */
void cdc_get_line_coding(cdc_line_coding_t *coding) {
    *coding = g_cdc_coding;
}

/* SET_CONTROL_LINE_STATE (0x22) */
void cdc_set_control_line_state(uint16_t state) {
    /* bit 0: DTR */
    /* bit 1: RTS (一般不用, USB 是流控) */
    g_cdc_dtr = (state & 0x01);
    g_cdc_rts = (state & 0x02);
    
    /* 通知应用层 (e.g. DTR 变化时关闭串口) */
    if (!g_cdc_dtr) {
        /* DTR 拉低 = 串口工具关闭了串口 */
    }
}
```

### 实战: CDC ACM 设备端

```c
/* 完整 CDC ACM 设备 */
typedef enum {
    CDC_STATE_IDLE,
    CDC_STATE_LINE_CODING,
    CDC_STATE_CONTROL_LINE,
    CDC_STATE_TX,
    CDC_STATE_RX,
} cdc_state_t;

typedef struct {
    cdc_line_coding_t line_coding;
    uint8_t dtr;
    uint8_t rts;
    uint8_t break_state;
    uint16_t serial_state;  /* 通知 host 的状态 */
    cdc_state_t state;
} cdc_ctx_t;

cdc_ctx_t g_cdc = {
    .line_coding = { 115200, 0, 0, 8 },
};

/* Class 请求处理 */
void cdc_class_request(usb_setup_t *setup) {
    switch (setup->bRequest) {
    case 0x20:  /* SET_LINE_CODING */
        cdc_set_line_coding((cdc_line_coding_t *)ep0_buffer);
        g_cdc.state = CDC_STATE_LINE_CODING;
        break;
    case 0x21:  /* GET_LINE_CODING */
        memcpy(ep0_buffer, &g_cdc.line_coding, sizeof(cdc_line_coding_t));
        /* 在数据阶段发回 */
        break;
    case 0x22:  /* SET_CONTROL_LINE_STATE */
        g_cdc.dtr = setup->wValue & 0x01;
        g_cdc.rts = (setup->wValue >> 1) & 0x01;
        g_cdc.state = CDC_STATE_CONTROL_LINE;
        break;
    }
}

/* Notification 发送 */
void cdc_send_notification(uint16_t state) {
    uint8_t data[10] = {
        0xA1,  /* bmRequestType (Notification) */
        0x20,  /* bNotification (SERIAL_STATE) */
        0x00, 0x00,  /* wValue */
        0x00, 0x00,  /* wIndex (Interface 0) */
        0x02, 0x00,  /* wLength (2 bytes data) */
        state & 0xFF,
        (state >> 8) & 0xFF,
    };
    /* 通过中断 IN 端点发 */
    usb_ep_send(0x83, data, 10);
}
```

### 跨平台兼容性

```text
Windows 10/11:
  - 标准 CDC ACM 完整支持
  - 简化 CDC 也支持
  - 自动装驱动 (usbser.sys)

Linux (3.6+):
  - 标准 CDC ACM 完整支持 (cdc_acm driver)
  - 简化 CDC 也支持
  - /dev/ttyACM0 自动创建

macOS:
  - 标准 CDC ACM 完整支持
  - 简化 CDC 也支持
  - /dev/cu.usbmodem* 自动创建

注意:
  - macOS 对 Notification 端点严格, 必须响应
  - Windows 10/11 对简化 CDC 兼容, 但有 SetLineCoding 等请求时会"不响应"也不报错
```

## HID (Human Interface Device)

### 协议栈

```text
Application: 键鼠 / 触摸 / 自定义设备
  |
HID 协议:
  - Report 描述符 (描述数据格式)
  - Report (具体数据)
  - Boot Report (固定格式, BIOS 用)
  |
USB Interrupt 传输
```

### 描述符 (键盘示例)

```c
/* HID Descriptor */
static const uint8_t hid_desc[] = {
    0x09, 0x21, 0x11, 0x01, 0x00, 0x01, 0x22, 0x3F, 0x00,
};

/* HID Report Descriptor (键盘) */
static const uint8_t hid_keyboard_report[] = {
    0x05, 0x01,       /* Usage Page (Generic Desktop) */
    0x09, 0x06,       /* Usage (Keyboard) */
    0xA1, 0x01,       /* Collection (Application) */
    
    /* Modifier byte */
    0x05, 0x07,       /*   Usage Page (Keyboard) */
    0x19, 0xE0,       /*   Usage Minimum (Left Ctrl = 224) */
    0x29, 0xE7,       /*   Usage Maximum (Right GUI = 231) */
    0x15, 0x00,       /*   Logical Minimum (0) */
    0x25, 0x01,       /*   Logical Maximum (1) */
    0x75, 0x01,       /*   Report Size (1) */
    0x95, 0x08,       /*   Report Count (8) */
    0x81, 0x02,       /*   Input (Data, Var, Abs) - Modifiers */
    
    /* Reserved byte */
    0x95, 0x01,       /*   Report Count (1) */
    0x75, 0x08,       /*   Report Size (8) */
    0x81, 0x03,       /*   Input (Const, Var, Abs) - Reserved */
    
    /* LED output */
    0x95, 0x05,       /*   Report Count (5) */
    0x75, 0x01,       /*   Report Size (1) */
    0x05, 0x08,       /*   Usage Page (LEDs) */
    0x19, 0x01,       /*   Usage Minimum (Num Lock = 1) */
    0x29, 0x05,       /*   Usage Maximum (Kana = 5) */
    0x91, 0x02,       /*   Output (Data, Var, Abs) - LEDs */
    
    /* LED padding */
    0x95, 0x01,       /*   Report Count (1) */
    0x75, 0x03,       /*   Report Size (3) */
    0x91, 0x03,       /*   Output (Const, Var, Abs) - LED Padding */
    
    /* Keycodes (6 keys) */
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

### HID 报告数据结构

```c
/* 键盘报告 (8 字节) */
typedef struct __attribute__((packed)) {
    uint8_t modifier;   /* bit 0: LCtrl, bit 1: LShift, bit 2: LAlt, bit 3: LGUI, bit 4: RCtrl, ... */
    uint8_t reserved;
    uint8_t keycode[6]; /* 最多 6 个键同时按下 */
} hid_keyboard_report_t;

/* 发送键盘报告 */
void hid_send_keyboard(uint8_t modifier, uint8_t *keys, int key_count) {
    hid_keyboard_report_t report = { 0 };
    report.modifier = modifier;
    for (int i = 0; i < key_count && i < 6; i++) {
        report.keycode[i] = keys[i];
    }
    usb_ep_send(0x81, &report, sizeof(report), 100);
}
```

### HID 设备实战

```c
/* HID Class 请求 */
#define HID_GET_REPORT   0x01
#define HID_GET_IDLE     0x02
#define HID_GET_PROTOCOL 0x03
#define HID_SET_REPORT   0x09
#define HID_SET_IDLE     0x0A
#define HID_SET_PROTOCOL 0x0B

void hid_class_request(usb_setup_t *setup) {
    switch (setup->bRequest) {
    case HID_GET_REPORT:
        /* Host 想读 Report (e.g. 键盘 LED 状态) */
        /* 在数据阶段发 */
        break;
    case HID_SET_REPORT:
        /* Host 想写 Report (e.g. 键盘 LED 状态) */
        /* 接收数据, 更新 LED */
        break;
    case HID_GET_IDLE:
        /* 当前 idle 周期 */
        ep0_buffer[0] = g_hid.idle_rate;
        break;
    case HID_SET_IDLE:
        /* 设置 idle 周期 (主机不轮询的容忍时间) */
        g_hid.idle_rate = setup->wValue >> 8;
        break;
    }
}
```

### 跨平台兼容性

```text
Windows 10/11:
  - HID 标准键鼠自动识别
  - 自定义 HID 用 WinUSB / libusb

Linux:
  - HID 标准键鼠自动识别 (/dev/input/event0)
  - 自定义 HID 用 libusb

macOS:
  - HID 标准键鼠自动识别
  - 自定义 HID 用 IOHIDManager

Boot 模式 (BIOS):
  - USB 键盘 / 鼠标支持 (boot subclass 0x01 / protocol 0x01/0x02)
  - 自定义 HID 不支持 boot
```

## MSC (Mass Storage Class)

### 协议栈

```text
Application: 文件读写
  |
File System (FAT / ext4 / ...)
  |
Block Device: 扇区读写
  |
SCSI 命令集: READ(10), WRITE(10), INQUIRY, READ CAPACITY, ...
  |
USB Bulk-Only Transport (BOT): CBW / CSW 协议
  |
USB Bulk 传输
```

### Bulk-Only Transport (BOT) 协议

```text
Command Block Wrapper (CBW): 31 字节
  - dCBWSignature: 0x43425355 (LE)
  - dCBWTag: 唯一 ID
  - dCBWDataTransferLength: 数据传输长度
  - bmCBWFlags: 方向 (bit 7)
  - bCBWLUN: LUN (0)
  - bCBWCBLength: SCSI 命令长度
  - CBWCB: SCSI 命令 (16 字节)

Data: 实际数据 (按 dCBWDataTransferLength)

Command Status Wrapper (CSW): 13 字节
  - dCSWSignature: 0x53425355
  - dCSWTag: 匹配 CBW 的 dCBWTag
  - dCSWDataResidue: 剩余字节
  - bCSWStatus: 0=Success, 1=Fail, 2=Phase Error
```

### SCSI 命令 (常用)

```c
/* INQUIRY (0x12) - 读设备信息 */
typedef struct __attribute__((packed)) {
    uint8_t  opcode;     /* 0x12 */
    uint8_t  evpd;       /* 0 */
    uint8_t  page_code;  /* 0 */
    uint16_t allocation_length;
    uint8_t  control;    /* 0 */
} scsi_inquiry_t;

/* READ CAPACITY (10) (0x25) - 读容量 */
typedef struct __attribute__((packed)) {
    uint8_t  opcode;        /* 0x25 */
    uint8_t  reladdr;       /* 0 */
    uint32_t lba;           /* 0 (读当前) */
    uint16_t reserved;      /* 0 */
    uint8_t  pmi;           /* 0 */
    uint8_t  control;       /* 0 */
} scsi_read_capacity_10_t;

/* READ (10) (0x28) - 读扇区 */
typedef struct __attribute__((packed)) {
    uint8_t  opcode;       /* 0x28 */
    uint8_t  flags;        /* bit 3: DPO, bit 4: FUA */
    uint32_t lba;
    uint8_t  group;
    uint16_t length;       /* 扇区数 */
    uint8_t  control;
} scsi_read_10_t;

/* WRITE (10) (0x2A) - 写扇区 */
typedef struct __attribute__((packed)) {
    uint8_t  opcode;       /* 0x2A */
    uint8_t  flags;
    uint32_t lba;
    uint8_t  group;
    uint16_t length;       /* 扇区数 */
    uint8_t  control;
} scsi_write_10_t;
```

### MSC 描述符

```c
/* MSC 接口: 类 0x08, 子类 0x06, 协议 0x50 (BOT) */
static const uint8_t msc_desc[] = {
    0x09, 0x02, 0x20, 0x00, 0x01, 0x01, 0x00, 0xC0, 0x32,
    /* Interface 0: MSC */
    0x09, 0x04, 0x00, 0x00, 0x02, 0x08, 0x06, 0x50, 0x00,
    /* Endpoint OUT (Bulk) */
    0x07, 0x05, 0x01, 0x02, 0x40, 0x00, 0x00,
    /* Endpoint IN (Bulk) */
    0x07, 0x05, 0x81, 0x02, 0x40, 0x00, 0x00,
};
```

### 实战: USB 读卡器

```c
/* 简化版: 只支持 INQUIRY + READ CAPACITY + READ(10) */
#define MSC_EP_OUT  0x01
#define MSC_EP_IN   0x81

typedef struct {
    uint8_t scsi_cmd[16];
    uint32_t data_residue;
    uint32_t tag;
    uint8_t lun;
    bool phase_error;
} msc_ctx_t;

void msc_handle_cbw(msc_ctx_t *ctx, uint8_t *cbw) {
    /* 1. 解析 CBW */
    if (le32_to_cpu(*(uint32_t *)cbw) != 0x43425355) {
        /* CBW 签名错 */
        ctx->phase_error = true;
        return;
    }
    ctx->tag = le32_to_cpu(*(uint32_t *)(cbw + 4));
    ctx->data_residue = le32_to_cpu(*(uint32_t *)(cbw + 8));
    ctx->lun = cbw[13] & 0x0F;
    
    /* 2. 解析 SCSI 命令 */
    uint8_t opcode = cbw[15];
    switch (opcode) {
    case 0x12:  /* INQUIRY */
        msc_inquiry(ctx);
        break;
    case 0x25:  /* READ CAPACITY (10) */
        msc_read_capacity(ctx);
        break;
    case 0x28:  /* READ (10) */
        msc_read_10(ctx, (scsi_read_10_t *)(cbw + 15));
        break;
    case 0x2A:  /* WRITE (10) */
        msc_write_10(ctx, (scsi_write_10_t *)(cbw + 15));
        break;
    default:
        /* 未知命令, 发送 STALL + CSW (status = fail) */
        usb_ep_stall(MSC_EP_IN);
        msc_send_csw(ctx, 1);  /* fail */
        break;
    }
}
```

## DFU (Device Firmware Upgrade)

### 协议

```text
DFU 类 (0xFE, 子类 0x01):
  - 仅 EP0 (无其他端点)
  - 用于 bootloader 升级

DFU 状态机:
  App Idle
    ↓ DETACH
  App Detach
    ↓ USB Reset
  DFU Idle
    ↓ DNLOAD (下载固件)
  DFU Download Sync
    ↓ (数据 OK)
  DFU Download Busy
    ↓ (写入完成)
  DFU Download Idle
    ↓ 继续 DNLOAD 或 MANIFEST
  Manifest Sync
    ↓ 完整
  Manifest Wait Reset
    ↓ USB Reset
  App Idle (新固件)
```

### DFU 描述符

```c
/* DFU Functional Descriptor */
static const uint8_t dfu_desc[] = {
    0x09, 0x21, 0x0B,
    0xFF, 0x00,  /* wDetachTimeout (ms) = 0xFF00 = 65280 ms */
    0x40, 0x00,  /* wTransferSize = 64 */
    0x10, 0x01,  /* bcdDFUVersion = 0x0110 */
};

/* DFU 接口 (类 0xFE, 子类 0x01, 协议 0x02) */
static const uint8_t dfu_interface_desc[] = {
    0x09, 0x04, 0x00, 0x00, 0x00, 0xFE, 0x01, 0x02, 0x00,
};
```

### DFU Class 请求

```c
#define DFU_DETACH    0x00
#define DFU_DNLOAD    0x01
#define DFU_UPLOAD    0x02
#define DFU_GETSTATUS 0x03
#define DFU_CLRSTATUS 0x04
#define DFU_GETSTATE  0x05
#define DFU_ABORT     0x06

typedef enum {
    DFU_STATE_APP_IDLE = 0,
    DFU_STATE_APP_DETACH,
    DFU_STATE_DFU_IDLE,
    DFU_STATE_DFU_DNLOAD_SYNC,
    DFU_STATE_DFU_DNLOAD_BUSY,
    DFU_STATE_DFU_DNLOAD_IDLE,
    DFU_STATE_DFU_MANIFEST_SYNC,
    DFU_STATE_DFU_MANIFEST,
    DFU_STATE_DFU_MANIFEST_WAIT_RESET,
    DFU_STATE_DFU_UPLOAD_IDLE,
    DFU_STATE_DFU_ERROR,
} dfu_state_t;

void dfu_class_request(usb_setup_t *setup) {
    switch (setup->bRequest) {
    case DFU_DNLOAD:
        /* 接收固件数据, block 编号 = setup->wValue */
        if (setup->wLength > 0) {
            usb_ep0_receive(dfu_buffer, setup->wLength);
            g_dfu_state = DFU_STATE_DFU_DNLOAD_SYNC;
        } else {
            /* wLength = 0 表示结束下载 */
            g_dfu_state = DFU_STATE_DFU_MANIFEST_SYNC;
        }
        break;
    case DFU_GETSTATUS:
        /* 返回状态, poll timeout, state */
        dfu_get_status_response();
        break;
    case DFU_DETACH:
        /* 主机请求进入 DFU 模式 */
        g_dfu_state = DFU_STATE_APP_DETACH;
        break;
    }
}
```

### 实战: 双模式 (App + DFU) 切换

```c
/* Bootloader 启动时检查 */
/* 如果按住按钮, 进入 DFU 模式 */
void bootloader_check_dfu() {
    if (button_pressed()) {
        /* 进入 DFU 模式 */
        dfu_init();
        while (1) {
            dfu_poll();
        }
    } else {
        /* 跳转到 App */
        app_start();
    }
}

/* App 跳到 Bootloader (用于升级) */
void app_jump_to_bootloader() {
    /* 1. 保存标志到 backup register 或 flash */
    *((uint32_t *)BOOT_FLAG_ADDR) = 0xDEADBEEF;
    /* 2. 软复位 */
    NVIC_SystemReset();
}

/* Bootloader 检测到升级标志, 进入 DFU */
void bootloader_init() {
    if (*((uint32_t *)BOOT_FLAG_ADDR) == 0xDEADBEEF) {
        dfu_init();
    }
}
```

## 复合设备示例 (CDC + HID)

```c
/* Configuration Descriptor (CDC + HID 复合设备) */
static const uint8_t composite_desc[] = {
    0x09, 0x02, 0x6F, 0x00, 0x03, 0x01, 0x00, 0xC0, 0x32,
    
    /* IAD for CDC */
    0x08, 0x0B, 0x00, 0x02, 0x02, 0x02, 0x01, 0x04,
    /* CDC Comm + Data + EPs */
    
    /* IAD for HID */
    0x08, 0x0B, 0x02, 0x01, 0x03, 0x03, 0x00, 0x00, 0x05,
    /* HID Interface 2 */
    0x09, 0x04, 0x02, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00,
    /* HID Descriptor */
    0x09, 0x21, 0x11, 0x01, 0x00, 0x01, 0x22, 0x2F, 0x00,
    /* Report Descriptor (32 字节) */
    /* HID Interrupt IN EP */
    0x07, 0x05, 0x83, 0x03, 0x08, 0x00, 0x0A,
};
```

## 7 条类驱动常见错误

| # | 错误 | 后果 |
| --- | --- | --- |
| 1 | CDC 没 IAD | Windows 识别为 2 个设备 |
| 2 | CDC 中断 IN stall | 串口偶尔失败 |
| 3 | HID Report 描述符错 | 设备识别但不响应 |
| 4 | HID 缺 boot subclass | BIOS 不识别 |
| 5 | MSC CBW 签名错 | 主机拒绝 |
| 6 | DFU 状态机错 | 升级失败 |
| 7 | 复合设备 IAD 错 | 部分功能缺失 |

## 关联文档

- `usb-deep-dive.md` 原理
- `usb-practical.md` 速查
- `usb-failure-cases.md` 产线案例
- `usb-enumeration-and-descriptors.md` 枚举详细
- `usb-dma-and-rtos.md` DMA + RTOS
- `usb-vs-other-bus.md` 跨总线对比
- `usb-index.md` 导航
- `usb-dfu-deep-dive.md` DFU 协议 (升级模式)
- `usb-dfu-practical.md` DFU 实战
