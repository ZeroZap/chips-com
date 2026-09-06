# BLE 主题总览

## 目标

BLE 是 chips-com 的核心无线协议主题之一，围绕"低功耗 IoT / 可穿戴 / 资产追踪的短距无线通信"已经形成 5 篇专题笔记。本文档是**总览导航**，帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/ble-*.md
│
├── 速查层
│   └── ble-practical.md                 调试流程速查 / 5 秒定位 / 错误码表
│
├── 原理层
│   └── ble-deep-dive.md                 PHY / LL / HCI / L2CAP / ATT / GATT / GAP / SMP
│
├── 实战层
│   └── ble-failure-cases.md             8 个产线实战案例
│
└── 导航
    └── ble-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 BLE, 想入门" (新人)

按顺序读, 1-2 天能上手:

1. **`ble.md`** — 主题入口, 5 分钟
2. **`ble-practical.md`** — 关键参数 / 5 秒定位
3. **`ble-deep-dive.md`** — 协议栈分层 + GATT 模型

### 路径 B: "我在做 BLE 设备产线失败" (现场救火)

1. **`ble-practical.md`** "## 5 秒钟定位"
2. **`ble-failure-cases.md`** — 找类似案例（8 个）
3. **`ble-deep-dive.md`** "## HCI STATUS 错误码速查"

### 路径 C: "我在做 BLE 协议栈移植" (工程师)

1. **`ble-deep-dive.md`** "## SoC vs NCP 调试差异"
2. **`ble-practical.md`** "## 抓包工具"
3. **`ble-deep-dive.md`** "## HCI" 章节

### 路径 D: "我在做 BLE 安全加固" (安全工程师)

1. **`ble-deep-dive.md`** "## SMP（Security Manager Protocol）"
2. **`ble-failure-cases.md`** 案例 1（RTL8762E DoS 漏洞）
3. **`ble-practical.md`** "## 5 秒钟定位" 的安全相关条目

### 路径 E: "我在做 BLE 选型" (架构师)

1. **`ble.md`** "## 典型芯片"
2. **`ble-deep-dive.md`** "## PHY 档位" + "## BLE 5.x 扩展"
3. **`ble-practical.md`** "## 性能数据参考"

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 连接参数怎么配 | ble-practical.md "## 连接参数三件套" |
| 连接参数协商失败（0x3B/0x08/0x05） | ble-practical.md "## 连接参数协商 SOP" |
| 加密源码级细节（Cordio 视角） | ble-deep-dive.md "## SMP（Security Manager Protocol）" → 加密源码级要点 |
| 配对攻击防御（Just Works / MitM） | ble-failure-cases.md 案例 1.5 |
| PHY 选哪个 | ble-deep-dive.md "## BLE 5.x PHY 档位" |
| 广播参数怎么设 | ble-practical.md "## 广播参数" |
| MTU 怎么协商 | ble-practical.md "## MTU" |
| GATT Service 怎么定义 | ble-deep-dive.md "## GATT（Generic Attribute Profile）" |
| 配对失败 | ble-failure-cases.md 案例 1 / 4 / 5 |
| 0x3E 断开 | ble-failure-cases.md 案例 2 |
| 0x3D MIC 失败 | ble-failure-cases.md 案例 7 |
| 距离近 | ble-failure-cases.md 案例 8 |
| 功耗高 | ble-failure-cases.md 案例 6 |
| ADC 影响 BLE | ble-failure-cases.md 案例 3 |
| HCI 错误码 | ble-practical.md "## HCI STATUS 错误码速查" |
| ATT 错误码 | ble-practical.md "## ATT Error 速查" |
| nRF52832 实战 | ble-practical.md "## nRF52832 实战注意" |
| 抓包工具 | ble-practical.md "## 抓包工具" |
| Windows 端 BLE 调试 | ble-practical.md "## 抓包工具"（BLEDebug + CH9143 行） |
| 配对方式 | ble-deep-dive.md "## GAP" / "## SMP" |
| 加密流程 | ble-deep-dive.md "## SMP（Security Manager Protocol）" |
| LE 2M / Coded | ble-deep-dive.md "## BLE 5.x 扩展" |
| Privacy / RPA | ble-deep-dive.md "## Privacy 与地址轮换" |
| SoC vs NCP 差异 | ble-deep-dive.md "## SoC vs NCP 调试差异" |
| LE Audio / CIS / BIS | ble-deep-dive.md "## Connected Isochronous Stream" |
| Android BLE MTU 20 字节硬限 | ble-practical.md "### Android BLE MTU 实战（20 字节硬限）" |
| nRF52832 高数据率（HVN_TX_COMPLETE） | ble-practical.md "### nRF52832 高数据率发送实战" |
| Windows Host 电源管理影响 | ble-practical.md "### Host 电源管理影响 BLE 链路（隐性坑）" |
| 跨平台协议栈差异（SM/L2CAP/Flags） | ble-failure-cases.md 案例 10 |
| Zephyr 绑定被静默覆盖 | ble-failure-cases.md 案例 11 |
| RTL8762 配对诊断 SM 7 错误 | ble-failure-cases.md 案例 12 |
| CC2340R5 换芯片变体 ICall abort | ble-failure-cases.md 案例 13 |
| 工业 BLE 现场 P99 抖动 | ble-failure-cases.md 案例 14 |
| Nordic DTM 产线筛片 | ble-failure-cases.md 案例 15 |
| Goodix 私有错误码 + GPIO 诊断 | ble-failure-cases.md 案例 16 |
| nRF52832 sd_power_system_off 间歇性 | ble-failure-cases.md 案例 17 |
| Nordic OTA 工具链实战 | ble-failure-cases.md 案例 18 |
| LightBlue 6 项产前 checklist | ble-practical.md "### LightBlue 6 项外设产前 checklist" |
| Ellisys 抓包 + 错误码 133/257 | ble-failure-cases.md 案例 19 |
| SAMD21 小内存 + BLE 预算 | ble-failure-cases.md 案例 20 |
| L2CAP ECFC + EATT（SPSM=0x0027） | ble-deep-dive.md "### L2CAP 进阶：ECFC + EATT" |
| Android requestMtu 断连 | ble-failure-cases.md 案例 22 |
| 华为 / 小米 / OPPO GATT 碎片化 | ble-failure-cases.md 案例 23 |
| 实时日志压到 10 分钟 | ble-failure-cases.md 案例 24 |
| ESP32-C3 mDNS + WiFi coex | ble-failure-cases.md 案例 25 |
| STM32+nRF52840 外挂 ISR 假休眠 | ble-failure-cases.md 案例 26 |
| CH582 国产 RISC-V 漏电 3 坑 | ble-failure-cases.md 案例 27 |
| STM32WB 0x02 BlueCore 升级 fix | ble-failure-cases.md 案例 28 |
| Abbott Libre 3 FDA 召回 + iCGM | ble-failure-cases.md 案例 29 |
| NVIDIA Tegra SE ECDH 0x05 silent fail | ble-failure-cases.md 案例 30 |
| Arduino Nano 33 18mA brownout + BareOS | ble-failure-cases.md 案例 31 |
| 零售 IoT overnight degradation | ble-failure-cases.md 案例 32 |
| BLE sensor 60s 能量账本 | ble-failure-cases.md 案例 33 |
| Ellisys PHY + Nordic Out-of-Order + NCP OTA 0x19 | ble-failure-cases.md 案例 34 |
| BLE 5 大系统级错误 | ble-failure-cases.md 案例 35 |
| 40 万台安全产品 BLE 重设计 | ble-failure-cases.md 案例 36 |
| Zephyr 32.768kHz 晶振 ±500ppm SCA | ble-failure-cases.md 案例 37 |
| ESP32 Bluedroid 110KB vs NimBLE 30KB | ble-failure-cases.md 案例 38 |
| 工业 4 维排查 + USB Selective Suspend | ble-failure-cases.md 案例 39 |
| 4 款 BLE 模块 Wi-Fi 干扰 30ms 对比 | ble-failure-cases.md 案例 40 |
| CC254x 8KB RAM 7.5ms OSAL 死锁 | ble-failure-cases.md 案例 41 |
| T20i A2 线 19.2% 不良 + KT6368A DMA | ble-failure-cases.md 案例 42 |
| 仓库 RTL8852BU 0xfcf0 -16 $47k 损失 | ble-failure-cases.md 案例 43 |

## 关键概念地图

```text
BLE 协议栈
├── PHY 层
│   ├── 2.4 GHz ISM 频段
│   ├── 40 信道（37, 38, 39 = 广播）
│   ├── GFSK 调制
│   └── LE 1M / 2M / Coded (S2/S8)
│
├── LL 层（Link Layer）
│   ├── 设备地址 (Public / Random / RPA)
│   ├── 广播 PDU (ADV_IND / SCAN_REQ / CONNECT_REQ)
│   ├── 连接 PDU (LL Data / LL Control)
│   ├── 跳频 (AFH, Channel Map)
│   ├── 加密启动 (LL_START_ENC_REQ)
│   └── CRC-24 / MIC-32
│
├── HCI
│   ├── Command / Event / Data
│   ├── UART (H4/H5) / SPI / USB (H2)
│   └── 关键命令与事件清单
│
├── L2CAP
│   ├── 信道 (LE-U / LE-C / 动态)
│   ├── MTU 协商 (默认 23, 最大 247)
│   └── 分片 / 重组
│
├── ATT（属性协议）
│   ├── Attribute 模型
│   ├── Read / Write / Notify / Indicate
│   └── Error Response
│
├── GATT（通用属性配置）
│   ├── Service / Characteristic / Descriptor
│   ├── CCCD (0x2902)
│   ├── 预定义 Service
│   └── Discovery 流程
│
├── GAP（通用访问配置）
│   ├── 角色 (Broadcaster/Observer/Peripheral/Central)
│   ├── 状态机
│   └── 配对方式
│
├── SMP（安全管理器协议）
│   ├── LE Legacy Pairing
│   ├── LE Secure Connections (ECDH P-256)
│   ├── AuthReq (Bonding/MITM/SC/Keypress)
│   └── IRK / LTK / CSRK
│
└── BLE 5.x 扩展
    ├── LE 2M PHY
    ├── LE Coded PHY (S2/S8)
    ├── Extended Advertising
    ├── Periodic Advertising
    └── Connected Isochronous Stream (CIS/BIS)
```

## 文档关系图

```text
ble.md (主题入口, 概览)
   ↓ 引用
ble-practical.md (速查, 调试流程)
   ↓ 引用
ble-deep-dive.md (原理, 体系)
   ↓ 引用
ble-failure-cases.md (案例, 实战)
   ↓ 全部引用
ble-index.md (本文件, 导航)
```

## 学习路径推荐（按角色）

### 嵌入式软件工程师（BLE 协议栈开发）

```text
入口 → 速查 → 原理 → 实战案例
0.5d   0.5d   2d     1d
```

### 物联网 / 可穿戴硬件工程师

```text
入口 → 速查 → 实战案例（天线篇） → PHY 深入
0.5d   0.5d   1d                 1d
```

### 移动 App 开发者

```text
速查（GATT/CCCD/MTU） → 实战案例 5
0.5d                0.5d
```

### 安全工程师

```text
原理 (SMP) → 实战案例 1 → 原理 (Privacy)
1d     0.5d     1d
```

### 产品架构师（选型）

```text
入口（芯片清单） → 原理（PHY/SoC vs NCP） → 速查（性能数据）
0.5d              0.5d                          0.5d
```

## BLE 主题 vs 其它主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| **BLE** | **5** | **~40 KB** | **低功耗 + GATT + 配对 + 安全** |
| CAN | 8 | 120 KB | 实时多 master + 错误处理 + 演进 (FD/XL) |
| USB | 9 | ~130 KB | 描述符 + 类驱动 + DMA |
| I2C | 12 | 151 KB | 协议兼容性 + 总线恢复 |
| SPI | 6 | 75 KB | 多从 / 菊花链 / 高速 |
| UART | 6 | 80 KB | RS485 / 流控 / 异步日志 |
| J1939 | 7 | ~95 KB | 商用车协议栈 + 地址声明 |

**共同点**:

- 都有速查 + 原理 + 实战 + 导航 4 层结构
- 都有 failure-cases (产线死机案例)
- 都有 practical 中的"5 秒定位" / 速查表

**差异**:

- BLE 重点: 协议栈分层 + GATT 模型 + 配对安全 (BLE 特色)
- CAN 重点: 多 master 仲裁 + 错误处理 (CAN 特色)
- USB 重点: 描述符体系 + 类驱动 (USB 特色)
- I2C 重点: 总线恢复 (I2C 特色, 因为有 8 步 SOP)

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| ble.md | 改版才更新 | 主题入口 |
| ble-practical.md | 改版才更新 | 速查 / 调试流程 |
| ble-deep-dive.md | 协议改版 / BLE 6 出 | 原理体系 |
| ble-failure-cases.md | **持续更新** | 产线案例 |
| ble-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题（chips-com 其他目录）

- **`bus/zigbee-deep-dive.md`** — ZigBee（IEEE 802.15.4 同源 PHY）
- **`bus/zigbee-practical.md`** — ZigBee 实战
- **`bus/zigbee-failure-cases.md`** — ZigBee 产线案例
- **`basic/can-phy.md`** — 物理层对比参考
- **`bus/j1939-deep-dive.md`** — 商用车协议栈（不同物理层）
- **`bus/uds-deep-dive.md`** — 诊断协议（基于 CAN）
- **`bus/ethercat-deep-dive.md`** — 工业 Ethernet（不同物理层）

## 一句话总结

BLE 是"低功耗短距无线的事实标准"，强在功耗、GATT 属性模型、安全配对。从原理到产线案例，5 篇笔记覆盖完整。和 ZigBee（IEEE 802.15.4 同源）、Wi-Fi（更高速高功耗）、LoRa（远距）是**互补**关系。

## 更新记录

- 2026-08-01: 初版, 5 篇笔记全部完成 (L4 闭环)
  - 来源：_Inbox/BLE-2026-07-31-candidates.md 5 条候选 + 实战补充
