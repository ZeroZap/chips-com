# USB 主题总览

## 目标

USB 是 chips-com 的核心主题之一, 围绕"PC 外设 / 调试接口"已经形成 8 篇专题笔记 + 3 篇 DFU 子专题。本文档是**总览导航**, 帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/usb-*.md
│
├── 速查层
│   ├── usb.md                          1 页概念
│   └── usb-practical.md                调试流程速查
│
├── 原理层
│   ├── usb-deep-dive.md                物理层 / 协议 / 帧 / 状态机 / 故障树
│   └── usb-enumeration-and-descriptors.md  枚举 / 描述符 / IAD / VID
│
├── 实战层
│   ├── usb-failure-cases.md            20 个产线死机案例
│   ├── usb-class-drivers.md            CDC / HID / MSC / DFU
│   ├── usb-dma-and-rtos.md             DMA + FreeRTOS / Zephyr / RT-Thread
│   └── usb-vs-other-bus.md             vs CAN / I2C / SPI / UART / Ethernet
│
├── DFU 子主题
│   ├── usb-dfu.md                      1 页概念
│   ├── usb-dfu-practical.md            DFU 实战
│   └── usb-dfu-deep-dive.md            DFU 协议
│
└── 导航
    └── usb-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 USB, 想入门" (新人)

1. **`usb.md`** — 1 页概念, 5 分钟
2. **`usb-practical.md`** — 调试流程速查
3. **`usb-deep-dive.md`** — 原理, 重点:
   - "## USB 协议的本质"
   - "## USB 物理层"
   - "## USB 枚举"
   - "## 描述符结构"
4. **`usb-enumeration-and-descriptors.md`** — 描述符详细

### 路径 B: "我在做产线 USB 通信失败" (现场救火)

1. **`usb-practical.md`** "## 5 秒钟定位"
2. **`usb-deep-dive.md`** "## USB 故障树"
3. **`usb-failure-cases.md`** — 找类似案例 (20 个)
4. **`usb-enumeration-and-descriptors.md`** — 描述符检查

### 路径 C: "我在做 CDC 串口 (USB 转 UART)" (工程实现)

1. **`usb-class-drivers.md`** "## CDC" 部分
2. **`usb-enumeration-and-descriptors.md`** CDC 描述符
3. **`usb-dma-and-rtos.md`** 实战代码
4. **`usb-failure-cases.md`** 案例 3 (CDC 串口打不开)

### 路径 D: "我在做 HID 设备 (键鼠 / 触摸 / 自定义)" (工程实现)

1. **`usb-class-drivers.md`** "## HID" 部分
2. **`usb-deep-dive.md`** "## HID 报告描述符"
3. **`usb-failure-cases.md`** 案例 9 (HID 失效)

### 路径 E: "我在做固件升级 DFU" (工程实现)

1. **`usb-class-drivers.md`** "## DFU" 部分
2. **`usb-dfu-deep-dive.md`** 协议
3. **`usb-dfu-practical.md`** 实战
4. **`usb-failure-cases.md`** DFU 相关

### 路径 F: "我在做 USB + RTOS 集成"

1. **`usb-dma-and-rtos.md`** — 完整模式
2. **`usb-practical.md`** "## 调试工具"
3. **`usb-failure-cases.md`** "## 案例 11" 之后的 RTOS 案例

### 路径 G: "我在做 USB 跨协议桥接"

1. **`usb-vs-other-bus.md`** — 跨总线对比
2. **`usb-class-drivers.md`** CDC / HID 用作桥接
3. 相关协议笔记 (CAN / I2C / SPI / UART)

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 设备管理器看到 Unknown Device | usb-practical.md "## 5 秒钟定位" + usb-failure-cases.md 案例 2 |
| CDC 串口打不开 | usb-failure-cases.md 案例 3 + usb-class-drivers.md CDC |
| HID 设备识别但不响应 | usb-failure-cases.md 案例 9 + usb-class-drivers.md HID |
| wTotalLength 算错 | usb-failure-cases.md 案例 4 + usb-enumeration-and-descriptors.md |
| 16 bit 字段用 8 bit 接收 | usb-failure-cases.md 案例 13 + usb-enumeration-and-descriptors.md |
| 高速协商失败 | usb-failure-cases.md 案例 5 + usb-deep-dive.md |
| 端点地址冲突 | usb-failure-cases.md 案例 8 + usb-deep-dive.md |
| VID 申请 | usb-enumeration-and-descriptors.md "VID 申请" |
| 字符串乱码 | usb-failure-cases.md 案例 7 + usb-enumeration-and-descriptors.md |
| CDC 是否省中断 IN | usb-class-drivers.md CDC 简化版 |
| 复合设备 IAD 写法 | usb-enumeration-and-descriptors.md IAD |
| USB DFU 实现 | usb-dfu-deep-dive.md + usb-dfu-practical.md |
| USB + RTOS | usb-dma-and-rtos.md |
| USB 中断优先级 | usb-dma-and-rtos.md |
| USB DMA 双缓冲 | usb-dma-and-rtos.md "## USB DMA 模式" |
| USB 缓存一致 (Cortex-M7) | usb-dma-and-rtos.md "## 缓存一致性" |
| USB vs CAN 选哪个 | usb-vs-other-bus.md "## USB vs CAN" |
| USB 在汽车的应用 | usb-vs-other-bus.md "## USB 在汽车中的应用" |
| 产线死机案例 | usb-failure-cases.md |
| Linux USB 调试 | usb-practical.md "## 调试工具" |

## 关键概念地图

```text
USB 协议
├── 物理层
│   ├── 低速 1.5M, 全速 12M, 高速 480M, SuperSpeed 5G
│   ├── D+/D- 差分
│   ├── 1.5k 上拉 (决定速度)
│   ├── NRZI 编码 + bit stuffing
│   └── 45 ohm 终端 (高速)
│
├── 协议层
│   ├── 包结构 (SYNC / PID / DATA / CRC / EOP)
│   ├── 事务 (Token + Data + Handshake)
│   ├── 帧 (1ms 全速, 125us 高速)
│   └── 控制 / Bulk / Interrupt / Iso 传输
│
├── 描述符
│   ├── Device (18 byte, 唯一)
│   ├── Configuration (9 byte + sub)
│   ├── Interface (9 byte)
│   ├── Endpoint (7 byte)
│   ├── String (UTF-16LE)
│   ├── IAD (复合设备)
│   └── 类描述符 (CDC / HID / MSC / DFU)
│
├── 枚举流程
│   ├── Attached -> Powered -> Default -> Address -> Configured
│   ├── 8 步流程 (GET_DESCRIPTOR, SET_ADDRESS, ...)
│   └── Suspend / Resume
│
├── 类驱动
│   ├── CDC (串口)
│   ├── HID (键鼠)
│   ├── MSC (U 盘 / SD)
│   ├── DFU (固件升级)
│   └── Vendor (自定义)
│
├── 工程
│   ├── DMA + RTOS
│   ├── 高速信号完整性
│   ├── Hub 兼容性
│   ├── 拔插寿命
│   └── 产线 fault injection
│
└── 演进
    ├── USB 3.0 / 3.1 / 3.2 (5G / 10G)
    ├── USB Type-C (24 pin, 双向)
    └── USB4 (40G, 基于 Thunderbolt)
```

## 文档关系图

```text
usb.md (简介)
   ↓ 引用
usb-practical.md (速查)
   ↓ 引用
usb-deep-dive.md (原理, 体系)
   ↓ 引用
usb-enumeration-and-descriptors.md (枚举, 描述符)
usb-failure-cases.md (案例, 实战)
usb-class-drivers.md (CDC / HID / MSC / DFU)
usb-dma-and-rtos.md (DMA + RTOS)
usb-vs-other-bus.md (跨总线对比)
   ↓ 引用
usb-dfu-*.md (DFU 子主题)
   ↓ 全部引用
usb-index.md (本文件, 导航)
```

## 学习路径推荐 (按角色)

### 嵌入式软件工程师
```text
速查 → 原理 → 枚举 → 类驱动 → DMA/RTOS
  0.5d   1d      1d      1d        1d
```

### USB 类驱动工程师 (CDC / HID / MSC)
```text
枚举 → 类驱动 → DMA/RTOS → 产线案例
  0.5d   2d        1d          0.5d
```

### USB 设备硬件工程师
```text
简介 → 速查 → 物理层 (deep-dive) → 高速信号完整性
  0.5d   0.5d      1d                    1d
```

### 固件升级工程师
```text
DFU 简介 → DFU 实战 → DFU 协议 → 复合设备 (DFU + APP)
  0.5d       1d         1d              1d
```

### 跨协议工程师
```text
USB 速查 → 跨总线对比 → USB 桥接 (USB <-> CAN / SPI / UART)
  0.5d       0.5d              1d
```

## USB 主题 vs 其他主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| **USB** | **8 + 3 (DFU)** | **~130 KB** | **PC 外设 / 类驱动 / 枚举 / VID-PID** |
| I2C | 12 | 151 KB | 协议兼容性 + 总线恢复 (Recovery) |
| SPI | 6 | 75 KB | 多从 / 菊花链 / 高速 |
| UART | 6 | 80 KB | RS485 / 流控 / 异步日志 |
| CAN | 9 | 107 KB | 实时多 master + 错误处理 + 演进 |
| J1939 | 7 | 77 KB | 商用车网络协议 (NAME / TP) |

**共同点**:
- 都有速查 + 原理 + 实战 + 专题 + 导航 5 层结构
- 都有 failure-cases (产线死机案例)
- 都有 RTOS 集成
- 都有跨总线对比

**差异**:
- USB 重点: 类驱动生态 (CDC / HID / MSC / DFU) + 枚举 + VID/PID
- I2C 重点: 总线恢复 (I2C 特色, 因为有 8 步 SOP)
- SPI 重点: 多从 / 菊花链 (SPI 特色)
- UART 重点: RS485 / 流控 (UART 特色)
- CAN 重点: 多 master 仲裁 + 错误处理 (CAN 特色)
- J1939 重点: NAME / 地址声明 / TP (J1939 特色)

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| usb.md | 改版才更新 | 简介 |
| usb-practical.md | 改版才更新 | 速查 |
| usb-deep-dive.md | 改版才更新 | 原理 |
| usb-enumeration-and-descriptors.md | 改版才更新 | 枚举 |
| usb-failure-cases.md | **持续更新** | 产线案例 |
| usb-class-drivers.md | 类驱动改版时 | 类驱动 |
| usb-dma-and-rtos.md | RTOS 改版时 | DMA + RTOS |
| usb-vs-other-bus.md | 新总线出现时 | 跨总线 |
| usb-dfu-*.md | 改版才更新 | DFU 子主题 |
| usb-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题 (chips-com 其他目录)

- **`basic/can-*.md`** — CAN 基础 (USB 桥接用)
- **`basic/i2c-*.md`** — I2C 基础 (USB 桥接用)
- **`basic/spi-*.md`** — SPI 基础 (USB 桥接用)
- **`basic/uart-*.md`** — UART 基础 (USB CDC 桥接)
- **`bus/can-canopen-deep-dive.md`** — CANopen (USB <-> CAN 桥接)
- **`bus/uds-*.md`** — UDS (USB 诊断之上)
- **`can-vs-other-bus.md`** — CAN vs 其他总线 (对比参考)
- **`i2c-vs-smbus-recovery.md`** — 跨协议对比参考

## 一句话总结

USB 是"PC 时代的标准接口", 强在通用性、类驱动生态和即插即用。CDC (串口) / HID (键鼠) / MSC (U盘) / DFU (升级) 是 4 大主流类驱动, 8 篇笔记覆盖原理 / 实战 / 专题 / 跨总线对比全维度。

## 更新记录

- 2026-07-28: 初版, 8 篇主线 + 3 篇 DFU 子主题全部完成 (L4 闭环)
