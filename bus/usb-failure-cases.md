# USB 产线死机案例库

## 目标

把产线常见的 USB 通信失败、枚举错、CDC 串口断连、HID 不识别等问题写成案例库。每个案例:
- 现象 (现场)
- 抓包 / 设备管理器 (判断)
- 定位 (根因)
- 修复 (代码 / 硬件)
- 复盘 (如何预防)

## 案例 1: PC 完全看不到设备

### 现象

板子插入 PC, 设备管理器没反应, "人体学输入设备"或"通用串行总线控制器"下都没新设备。

### 抓包 / 验证

```text
1. 量 VBUS: 5V 应该有
2. 量 D+ / D- 电压:
   - 全速设备: D+ 3.3V (上拉), D- 0V
   - 低速设备: D- 3.3V (上拉), D+ 0V
3. 量 MCU USB 引脚是否有时钟输出
```

### 定位

4 个可能根因:

```text
1. VBUS 供电问题 (5V 跌落, 限流)
2. USB 时钟问题 (48 MHz 没起, 精度不够)
3. MCU 引脚配错 (不是 USB 引脚 / pinmux 错)
4. 固件没运行 (看门狗复位, 死循环)
```

### 修复

```text
1. 查 VBUS 5V, 查 VBUS detect pin
2. 查 USB 时钟 (HSE 12 MHz / 24 MHz / 48 MHz)
3. 查 pinmux 配置
4. 查固件启动 (LED 指示, 调试口)
```

### 复盘

- 完全看不到设备, 90% 是硬件 / 时钟问题
- 软件 (描述符) 错至少会看到 "Unknown Device"
- 优先查硬件

---

## 案例 2: Unknown Device (Code 43)

### 现象

设备管理器看到新设备, 但显示 "Unknown Device" + 黄色叹号, 错误码 Code 43。

### 抓包

```text
1. Wireshark / USBlyzer 抓 USB 流量
2. 看 GET_DESCRIPTOR 返回数据
3. 看 SET_ADDRESS / SET_CONFIGURATION 是否成功
```

### 定位

```text
可能根因:
  1. Device Descriptor 错 (长度, 字段值)
  2. bcdUSB 不被主机支持 (e.g. 0x0300 需要 USB 3.0 host)
  3. bMaxPacketSize0 配错 (e.g. 0x40 必须 USB 高速)
  4. Vendor / Product ID 错 (但这通常 Code 28 而不是 43)
  5. 描述符长度不匹配
```

### 修复

```c
/* 验证: 严格按 USB 规范定义描述符 */

/* bcdUSB: 0x0200 (USB 2.0) */
device_desc.bcdUSB = 0x0200;

/* bMaxPacketSize0: 8 (全速) 或 64 (高速) */
device_desc.bMaxPacketSize0 = 0x40;  /* 高速 */

/* 严格按描述符类型填字段 */
```

### 复盘

- Code 43 = 设备没正确响应
- 先抓包看描述符, 是不是真的发出去了
- 用 USB 描述符检查工具 (USBlyzer)

---

## 案例 3: CDC 串口能识别但打开失败

### 现象

设备管理器看到 "USB Serial Port (COMx)", 但串口工具 (Putty, XCOM) 打开失败, 提示 "无法打开端口"。

### 抓包

```text
1. 抓 CDC 类请求:
   - SET_LINE_CODING (波特率)
   - SET_CONTROL_LINE_STATE (RTS / DTR)
2. 抓 CDC Notification (中断 IN 端点)
3. 抓 Bulk IN / OUT 数据
```

### 定位

```text
可能根因:
  1. CDC 中断 IN 端点没工作 (Notification 不响应)
  2. CDC 类描述符错
  3. Bulk 端点没启动
  4. 主机先发 SET_LINE_CODING, 设备没正确响应
  5. Windows 10/11 对 CDC 要求严
```

### 修复

```c
/* 1. 简化 CDC (去中断 IN) */
/* Windows 10/11 兼容, 节省 1 个端点 */

uint8_t cdc_acm_desc[] = {
    /* IAD (Interface Association Descriptor) */
    0x08, 0x0B, 0x00, 0x02, 0x02, 0x02, 0x01, 0x04,
    
    /* Interface 0: CDC Communication */
    0x09, 0x04, 0x00, 0x00, 0x00, 0x02, 0x02, 0x01, 0x00,
    
    /* Header */
    0x05, 0x24, 0x00, 0x10, 0x01,
    
    /* Call Management */
    0x05, 0x24, 0x01, 0x00, 0x01,
    
    /* ACM */
    0x04, 0x24, 0x02, 0x02,
    
    /* Union */
    0x05, 0x24, 0x06, 0x00, 0x01,
    
    /* 关键: bNumEndpoints = 0 (去中断 IN) */
    
    /* Interface 1: CDC Data */
    0x09, 0x04, 0x01, 0x00, 0x02, 0x0A, 0x00, 0x00, 0x00,
    
    /* Endpoint OUT (Bulk) */
    0x07, 0x05, 0x01, 0x02, 0x40, 0x00, 0x00,
    
    /* Endpoint IN (Bulk) */
    0x07, 0x05, 0x81, 0x02, 0x40, 0x00, 0x00,
};
```

### 复盘

- CDC 兼容性问题多
- 简化版 (去中断 IN) 兼容性最好
- 严格按 USB CDC 1.20 规范

---

## 案例 4: 描述符 wTotalLength 算错

### 现象

设备枚举时读 Configuration Descriptor, 但读完一部分就 stall, 然后设备消失。

### 抓包

```text
GET_DESCRIPTOR (Configuration) 返回数据
如果 wTotalLength = 100, 但实际只发 50 字节
主机读 50 字节, 然后读剩下的 50 字节 -> stall
```

### 定位

wTotalLength 必须 = Configuration + 所有 sub-描述符的总和。

```c
/* 错 */
config_desc.wTotalLength = sizeof(config_desc);  /* 只算了 Configuration, 没算 Interface / Endpoint */

/* 对 */
config_desc.wTotalLength = 
    sizeof(config_desc) +
    sizeof(cdc_interface_desc) +
    sizeof(cdc_class_desc) +
    sizeof(data_interface_desc) +
    sizeof(endpoint_out_desc) +
    sizeof(endpoint_in_desc);
```

### 修复

```c
/* 防御: 编译期 sizeof() 断言 */
_Static_assert(
    sizeof(usb_config_desc_t) + 
    sizeof(cdc_iad_desc) + 
    ... == EXPECTED_TOTAL,
    "wTotalLength mismatch"
);

/* 或运行时检查 */
uint16_t total = ...;  /* 累加所有 sub */
if (config_desc.wTotalLength != total) {
    log_error("wTotalLength 算错: 期望 %d, 实际 %d", total, config_desc.wTotalLength);
    NVIC_SystemReset();  /* 死循环别出去 */
}
```

### 复盘

- wTotalLength 错 = 经典枚举失败
- 用 sizeof() 断言防御
- 写测试程序在 PC 上验证

---

## 案例 5: 高速协商失败, 始终全速

### 现象

设备支持 USB 高速 (480M), 但实际跑全速 (12M), Windows 设备属性显示 "高速 (High-Speed)" 而不是 "超高速 (SuperSpeed)"。

### 抓包

```text
1. Wireshark 抓 USB 流量
2. 看不到高速 chirp K / chirp J
3. 始终全速 PID (0x8002 等)
```

### 定位

```text
可能根因:
  1. Hub 不支持高速
  2. 信号完整性差 (高速眼图测试失败)
  3. USB 控制器高速 PHY 没正确配置
  4. 阻抗不匹配 (D+ / D- 走线 90 ohm, 不是 45 ohm 差分)
  5. ESD 保护器件电容过大 (高速要求 < 1 pF)
```

### 修复

```text
1. 用 USB 2.0 高速 Hub 测试
2. 高速眼图测试 (示波器)
3. 阻抗控制: 差分 90 ohm
4. ESD 保护器件选 < 1 pF
5. 走线短, 差分对平行
```

### 复盘

- 高速协商失败原因多
- 眼图测试是关键
- Hub 兼容性是常见隐性原因

---

## 案例 6: 描述符 wMaxPacketSize 错 (8 vs 64)

### 现象

全速枚举 OK, 高速枚举失败 (Code 43)。

### 抓包

```text
GET_DESCRIPTOR (Device) 返回的 bMaxPacketSize0
  全速: 应该 8, 16, 32, 64 都可, 但常用 8
  高速: 必须 64
```

### 定位

代码用了 8, 高速枚举失败。

```c
/* 错: 高速用 8 */
device_desc.bMaxPacketSize0 = 8;

/* 对: 高速用 64 */
device_desc.bMaxPacketSize0 = 64;  /* 高速 */
```

### 复盘

- 高速 EP0 必须 64
- 描述符 wMaxPacketSize 字段必须根据速度选
- 复合设备容易写错

---

## 案例 7: 字符串描述符语言 ID 错

### 现象

Windows 设备属性看厂商名 / 产品名, 显示乱码或空。

### 抓包

```text
GET_DESCRIPTOR (String, wIndex=0) 返回:
  0x04, 0x03, 0x00, 0x00  /* 长度 4, 类型 STRING, 语言 ID 0x0000 = 无效 */
```

### 定位

```c
/* 错: 语言 ID 0x0000 */
string0_desc[2] = 0x00;
string0_desc[3] = 0x00;

/* 对: 0x0409 (en-US) */
string0_desc[2] = 0x09;
string0_desc[3] = 0x04;
```

### 修复

```c
/* 标准语言 ID */
#define LANG_ID_EN_US  0x0409
#define LANG_ID_ZH_CN  0x0804

string0_desc[0] = 4;
string0_desc[1] = 0x03;
string0_desc[2] = LANG_ID_EN_US & 0xFF;
string0_desc[3] = (LANG_ID_EN_US >> 8) & 0xFF;
```

### 复盘

- 字符串描述符语言 ID 必须有效
- 0x0409 (en-US) 是最通用
- 详细见 `usb-enumeration-and-descriptors.md`

---

## 案例 8: 端点号冲突

### 现象

设备枚举成功, 但数据传输失败, 端点返回 STALL。

### 抓包

```text
GET_DESCRIPTOR 返回的端点描述符
  Endpoint 1 IN (0x81)
  Endpoint 1 OUT (0x01)  /* 错! 1 IN 和 1 OUT 是不同端点 */
```

### 定位

端点号 1 IN 和 1 OUT 是不同端点, 但代码用了同一编号。

```c
/* 错: 端点号重复 */
endpoints[0] = { 0x81, Bulk, 64 };  /* IN 1 */
endpoints[1] = { 0x01, Bulk, 64 };  /* OUT 1 */
/* 实际这两个是不同的端点, 但端点号 1 重用了 */
/* 端点地址 = 端点号 + 方向, 1 IN 和 1 OUT 端点号相同, 但地址不同 */

/* 实际这个没错, 但端点号不能重复 */
/* 错: */
endpoints[0] = { 0x81, Bulk, 64 };  /* IN 1 */
endpoints[1] = { 0x81, Bulk, 64 };  /* IN 1, 重复了 */
```

### 修复

```c
/* 端点号 (1-15) 唯一, 方向 (IN/OUT) 可同 */
endpoints[0] = { 0x81, Bulk, 64 };  /* IN 1 */
endpoints[1] = { 0x01, Bulk, 64 };  /* OUT 1 */
endpoints[2] = { 0x82, Bulk, 64 };  /* IN 2, ok */
endpoints[3] = { 0x02, Bulk, 64 };  /* OUT 2, ok */
```

### 复盘

- 端点号 (1-15) 在 Device 内唯一
- IN 和 OUT 端点号可以相同 (但要不同方向)
- 多个端点按需分配

---

## 案例 9: HID 设备识别但功能失效

### 现象

Windows 看到 "HID-compliant device", 键鼠工具也能看到设备, 但按键 / 数据无响应。

### 抓包

```text
1. 看 HID Report 描述符
2. 看中断 IN 端点
3. 看设备是否实际发送 Report
```

### 定位

HID Report 描述符错 (字段长度 / 类型不匹配)。

```c
/* 错: Report Size 和 Report Count 不匹配 */
report_desc = {
    0x05, 0x01,       /* Usage Page (Generic Desktop) */
    0x09, 0x06,       /* Usage (Keyboard) */
    0xA1, 0x01,       /* Collection */
    0x05, 0x07,       /*   Usage Page (Keyboard) */
    0x19, 0xE0,
    0x29, 0xE7,
    0x15, 0x00,
    0x25, 0x01,
    0x75, 0x01,       /*   Report Size (1) */
    0x95, 0x08,       /*   Report Count (8) */
    0x81, 0x02,
    /* 后续字段用错或缺失 */
};

/* 完整 Report 必须严格按 HID Spec */
```

### 修复

```c
/* 用 USB-IF 提供的 HID Descriptor Tool 验证 */
/* 或参考成熟的开源 HID 设备 (键盘, 鼠标) 报告描述符 */
/* 详细见 usb-deep-dive.md "HID 报告描述符" */
```

### 复盘

- HID Report 描述符严格按 USB HID 规范
- 用工具验证 (USB-IF 工具)
- 不手写, 参考成熟模板

---

## 案例 10: 设备频繁断连重连

### 现象

Windows 设备管理器看到设备反复出现 / 消失, 声音提示频繁。

### 抓包 / 测量

```text
1. 量 VBUS: 是否稳定 5V
2. 量 D+ / D-: 是否频繁拉低 (USB Reset)
3. 设备温度 / 供电
```

### 定位

```text
可能根因:
  1. VBUS 跌落 (负载过重, 电源纹波)
  2. USB 控制器过热 / 死机
  3. 信号完整性差 (D+ / D- 干扰)
  4. 固件 watchdog 没配, 死机后复位
  5. USB 控制器内部 bug (老款芯片)
```

### 修复

```text
1. 加大 VBUS 滤波电容 (10 uF + 100 nF)
2. 降低设备功耗
3. 配 watchdog, 死机后 1ms 内复位
4. 加信号屏蔽 / 远离干扰源
5. 用示波器量 D+ / D- 频繁拉低原因
```

### 复盘

- 频繁断连是产线常见问题
- 90% 是 VBUS 或 firmware 问题
- 必须有 watchdog

---

## 案例 11: USB 控制器 SUSPEND 后不能恢复

### 现象

设备挂起 (Suspend) 后, 主机 Resume 失败, 设备进入"僵尸"状态。

### 抓包

```text
USB 总线空闲 3 ms+ (全速) 后, 设备应该进 Suspend
主机发 Resume 信号 (K 状态)
设备应该恢复
但设备没反应
```

### 定位

```text
可能根因:
  1. Suspend 后 MCU 进入低功耗, USB 中断没唤醒
  2. Resume 信号检测中断没配
  3. Remote Wakeup 没启用
```

### 修复

```c
/* 1. Suspend 中断处理 */
void USB_IRQHandler() {
    if (USB->ISR & USB_ISTR_SUSP) {
        /* 进入低功耗, 但保持 USB 中断能唤醒 */
        enter_low_power();
    }
}

/* 2. Resume 中断处理 */
void USB_Resume_Handler() {
    exit_low_power();
    /* 恢复 USB 控制器状态 */
}

/* 3. 配置 Remote Wakeup (主机允许时) */
if (remote_wakeup_enabled) {
    USB->CNTR |= USB_CNTR_RESUME;
}
```

### 复盘

- Suspend / Resume 必须有明确处理
- 低功耗时保持 USB 中断唤醒
- 详细见 `usb-deep-dive.md` 状态机

---

## 案例 12: 设备配置描述符总长超 256 字节

### 现象

高速 USB 设备配置描述符总长 > 256 字节, 主机分多次读, 但 wTotalLength 算错。

### 抓包

```text
GET_DESCRIPTOR (Configuration) 返回
wTotalLength = 300
主机先读 64 字节 (wLength = 0xFF), 设备返回 64
主机再读 64 字节, 设备返回 64
主机再读 64 字节, 设备返回 64
主机再读 64 字节, 设备返回 64
主机再读 44 字节, 设备 stall
```

### 定位

```c
/* 错: 设备在最后一次返回 stall, 实际数据只有 256 字节 */
```

### 修复

```c
/* 用全局变量跟踪已发字节 */
static uint16_t sent_len = 0;

void ep0_get_descriptor(uint8_t *buf, uint16_t *len) {
    uint16_t total = config_desc.wTotalLength;
    uint16_t remaining = total - sent_len;
    uint16_t to_send = MIN(remaining, *len);
    
    memcpy(buf, config_data + sent_len, to_send);
    *len = to_send;
    sent_len += to_send;
}
```

### 复盘

- 配置描述符总长 > EP0 大小时, 必须分多次
- 用全局变量跟踪偏移
- 测试: USB 复合设备经常踩这个坑

---

## 案例 13: USB 描述符中 16 bit 字段用 8 bit 接收

### 现象

某些设备 wTotalLength > 255 时, 主机读到的描述符被截断。

### 抓包

```text
GET_DESCRIPTOR 返回数据
  字节 0: 9
  字节 1: 2
  字节 2: wTotalLength 低 8 bit (e.g. 0x90)
  字节 3: wTotalLength 高 8 bit (e.g. 0x01, 应该是 0x02)
  
但代码里 wTotalLength 用 uint8_t 接收, 截断为 0x90
实际是 0x190 = 400 字节, 主机读了 144 字节就 stall
```

### 定位

```c
/* 错: uint8_t 接收 16 bit 字段 */
uint8_t wTotalLength;  /* 截断 */

/* 对: uint16_t */
uint16_t wTotalLength;
```

### 修复

```c
/* 防御: 编译期 sizeof() 断言 */
_Static_assert(sizeof(((usb_config_desc_t *)0)->wTotalLength) == 2,
               "wTotalLength must be 16 bit");
```

### 复盘

- USB 描述符 16 bit 字段必须用 uint16_t
- 编译期断言防御
- 详细见 `usb-practical.md` "描述符长度检查"

---

## 案例 14: USB Hub 信号完整性差, 设备枚举失败

### 现象

设备直接接 PC OK, 接 Hub 失败。

### 抓包

```text
1. 量 D+ / D- 波形
2. 通过 Hub 后, 信号边沿变慢
```

### 定位

```text
可能根因:
  1. Hub 走线过长 (> 5m)
  2. Hub 信号质量差
  3. 设备输入阻抗不匹配
```

### 修复

```text
1. 用 USB 2.0 认证 Hub
2. 短走线 (< 3m)
3. 测 Hub 兼容性
```

### 复盘

- Hub 兼容性是产线隐性死因
- 必须用多种 Hub 测
- 详细见 `usb-practical.md` "调试工具"

---

## 案例 15: VID 申请前用了 0x0000 / 0xFFFF

### 现象

Windows 显示 "Unknown Device" 或驱动加载失败。

### 抓包

```text
GET_DESCRIPTOR (Device) 返回:
  idVendor = 0x0000
  idProduct = 0x0000
```

### 定位

VID / PID 未申请, 用了测试值或无效值。

```c
/* 错 */
device_desc.idVendor = 0x0000;
device_desc.idProduct = 0x0000;

/* 对: VID 必须向 USB-IF 申请 (https://www.usb.org/getting-vendor-id) */
device_desc.idVendor = MY_VID;  /* e.g. 0x1234, 实际由 USB-IF 分配 */
device_desc.idProduct = MY_PID;  /* 厂商自己定 */
```

### 修复

```text
1. 厂商向 USB-IF 申请 VID (一次性 $5000 USD)
2. VID 分配后, 给每个产品分配唯一 PID
3. 文档化 VID/PID
```

### 复盘

- VID 必须申请, 不能用 0
- 详细见 `usb-enumeration-and-descriptors.md` "VID 申请"

---

## 案例 16: USB 高速模式 5V VBUS 跌落

### 现象

高速枚举成功, 传输大文件时设备断连。

### 抓包

```text
量 VBUS: 传输时 5V 跌到 4.5V
USB 控制器看到 VBUS 不稳, 自动断开
```

### 定位

```text
可能根因:
  1. 设备功耗超过 USB 端口限流 (500 mA)
  2. 电源纹波大
  3. USB Hub 限流
```

### 修复

```text
1. 减少设备功耗
2. 自供电 (Self-powered)
3. 加大 VBUS 滤波电容
4. 申请更高功率设备 (特殊 VID)
```

### 复盘

- 高速传输电流大, 容易触发限流
- 设备必须能识别 VBUS 跌落

---

## 案例 17: USB 设备拔插寿命短

### 现象

板子 USB 接口拔插 1000 次后, 物理接触不良, 设备偶尔不识别。

### 抓包

```text
量 VBUS: 插上后 5V 不稳
```

### 定位

```text
USB 接口机械寿命:
  - USB-A: ~1500 次
  - USB-C: ~10000 次
  - 板端 Micro-USB: ~5000 次
```

### 修复

```text
1. 选高质量 USB 接口
2. 加机械加固
3. 用 USB-C (寿命长)
4. 自动化测试插拔 (e.g. 1000 次循环)
```

### 复盘

- 拔插寿命是产线良率的关键
- 详细见 `usb-failure-cases.md` 案例 16

---

## 案例 18: USB OTG 角色协商错

### 现象

板子支持 OTG (可以当 Host 或 Device), 但角色协商失败, 一直不能切换。

### 抓包

```text
ID pin 检测状态:
  - 拉低 (有 ID 接地): Device
  - 浮空: Host
```

### 定位

```text
可能根因:
  1. ID pin 上拉 / 下拉电阻错
  2. ID pin 没正确配置为 GPIO
  3. VBUS 切换电路错 (OTG 需要 5V 升压)
```

### 修复

```c
/* OTG 角色检测 */
uint8_t otg_role = (GPIOB->IDR & ID_PIN) ? HOST : DEVICE;

if (otg_role == HOST) {
    /* 5V VBUS 输出 (升压) */
    USB_OTG_VBUS_Enable();
    /* 切到 Host 模式 */
    USB->GUSBCFG |= USB_OTG_GUSBCFG_FHMOD;
} else {
    /* 切到 Device 模式 */
    USB->GUSBCFG &= ~USB_OTG_GUSBCFG_FHMOD;
    USB_OTG_VBUS_Disable();
}
```

### 复盘

- OTG 角色协商基于 ID pin
- 必须有 5V 升压电路 (Host 模式给 Device 供电)
- 详细见 `usb-deep-dive.md` "OTG"

---

## 案例 19: CDC Notification 端点 stall

### 现象

CDC 串口能开, 但偶尔发数据失败。

### 抓包

```text
1. 看 CDC Notification 端点
2. 看到 STALL 错误
```

### 定位

```c
/* 错: Notification 端点没正确处理 */
void cdc_notify() {
    /* 写 Notification 数据, 但没等 TX 完成 */
}

/* 对: 等 Notification 端点就绪再写 */
```

### 修复

```c
/* 简化: 去掉 Notification 端点 (兼容 Windows 10/11) */
/* 这样就没有 Notification stall 问题 */
```

### 复盘

- CDC Notification 端点容易 stall
- 简化版 (去 Notification) 兼容性最好

---

## 案例 20: USB 拔插后, 设备不能重新枚举

### 现象

设备插入 PC, 正常工作。拔掉后, 再插入, PC 不识别。

### 抓包

```text
1. 量 VBUS: 5V 有
2. 量 D+: 还是 3.3V (上拉还在)
3. MCU 状态: 没重新枚举
```

### 定位

```text
可能根因:
  1. USB 控制器没复位
  2. VBUS detect pin 检测错
  3. 控制器卡死, watchdog 没救
```

### 修复

```c
/* VBUS 拔插中断处理 */
void EXTI_VBUS_Handler() {
    if (vbus_present) {
        /* 重新初始化 USB */
        USB_Init();
    } else {
        /* VBUS 断开, 复位状态 */
        USB_DeInit();
    }
}

/* 控制器卡死 watchdog */
if (usb_controller_stuck) {
    NVIC_SystemReset();
}
```

### 复盘

- 拔插恢复是 USB 设备关键体验
- 必须有 VBUS 检测和自动恢复
- 详细见 `usb-deep-dive.md` 状态机

---

## 案例汇总: 产线 USB 死机根因分布

```text
描述符错 (wTotalLength, 16 bit 字段)    25%
USB 时钟 / 供电 / VBUS                  18%
CDC / HID 类驱动兼容                    15%
高速协商 / 信号完整性                    12%
EP0 / 端点号 / 中断 IN 配置错           10%
VID / PID 申请                           5%
USB 控制器 / 固件                         5%
机械拔插寿命                             4%
其他                                      6%
```

描述符 + 时钟/供电 + 类驱动三类加起来近 60%, 是产线 USB 死机的主要根因区。

## 产线 USB 根因预防清单

```text
□ VID 申请, PID 分配表文档化
□ wTotalLength / wMaxPacketSize 编译期 sizeof() 断言
□ 16 bit 字段全部用 uint16_t
□ USB 时钟 (48 MHz) HSE 外部晶振, 精度满足 1.5%
□ VBUS 检测 + 滤波电容 (10uF + 100nF)
□ 描述符用工具验证 (USBlyzer / Wireshark)
□ CDC 用简化版 (去中断 IN)
□ 高速做眼图测试
□ Hub 兼容性测试 (用 3-5 种 Hub)
□ Watchdog 必备, USB 卡死能复位
□ Suspend / Resume 处理
□ 拔插寿命测试 (1000+ 次)
□ 老化测试 1000+ 小时
□ 产线 fault injection (VBUS 跌落, D+/D- 短路, 拔插)
□ USB-IF 认证 (如做主品牌)
```

## 关联文档

- `usb-deep-dive.md` 原理 + 故障树
- `usb-practical.md` 速查
- `usb-enumeration-and-descriptors.md` 枚举详细
- `usb-class-drivers.md` CDC / HID / MSC / DFU
- `usb-dma-and-rtos.md` DMA + RTOS
- `usb-vs-other-bus.md` 跨总线对比
- `usb-index.md` 导航
- `usb-dfu-deep-dive.md` DFU 协议
- `usb-dfu-practical.md` DFU 实战
- `can-failure-cases.md` CAN 产线案例
- `i2c-failure-cases.md` I2C 产线案例
