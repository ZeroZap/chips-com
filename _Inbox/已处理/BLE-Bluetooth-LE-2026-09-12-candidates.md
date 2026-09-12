# BLE / Bluetooth LE 候选素材 @ 2026-09-12 00:00

## 协议速览
- 是什么：2.4 GHz 低功耗短距无线协议（GAP/GATT/ATT/L2CAP/Link Layer）
- 解决什么：电池供电 IoT（穿戴/传感器/信标）小数据量间歇通信
- 跟 L4 关联：IoT/可穿戴出货量最大的无线栈，产线最常踩坑

## 候选文章（4 条）

### 1. BLE Data Integrity Failures (Out-of-Order Seggments)
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/125365/ble-data-integrity-failures-out-of-order-segments
- 来源：Nordic Semiconductor 官方 DevZone
- 摘要：BLE-to-WiFi 桥 800 KB GATT notify 传输，BLE+WiFi 同负载触发 CRC fail → SAR out-of-order（A1,A2,A2,A4），三方日志时间戳对齐暴露 RF 共存争抢
- 关键实战点：(1) 同 SoC BLE/WiFi 共存是可量化争抢；(2) 链路层 CRC 漏包 → 应用层重排 buffer 溢出表现"重复包"；(3) 三方日志时间戳对齐是标准定位法
- 推荐动作：**入主题笔记** → BLE 共存章节 + 协议层重传实战

### 2. Why Is Your Bluetooth Remote Control Dropping Connections?
- 链接：https://ebyteiot.com/blogs/ebyte-iot-blog/why-is-your-bluetooth-remote-control-dropping-connections-and-how-can-you-fix-it
- 来源：EBYTE 工业 BLE 模块厂商 blog
- 摘要：遥控器产线断连四大根因：电源纹波致 nRF52 brownout（+4 dBm TX 18 mA 瞬态）/ 2.4 GHz 拥堵 / PCB 天线 VSWR>3.0 失谐 / 连接参数不当；含电源/频谱/示波器四步法
- 关键实战点：(1) 产线 90% 断连根因是硬件+RF 物理层；(2) 跌落 >50 mV 触发 brownout；(3) 表格化诊断矩阵可复用
- 推荐动作：**入主题笔记** → BLE 硬件设计 / 产线可靠性章节

### 3. BLE Is Not Just a Protocol: System-Level Design Mistakes
- 链接：https://www.eurthtech.com/post/ble-is-not-just-a-protocol-system-level-design-mistakes-engineers-make
- 来源：EurthTech 嵌入式产品工程公司 blog
- 摘要：5 大架构盲点：把 BLE 当 pipe / 忽略 central（iOS 后台策略）/ 功耗非免费 / bonding 残键 state 爆炸 / 安全假设老化；含 1 个长寿命产品案例
- 关键实战点：(1) central 视作不可信合作方是硬要求；(2) 残键导致"工厂重置后仍无法配对"；(3) 长期产品 BLE 安全策略需可 OTA 升级
- 推荐动作：**入主题笔记** → BLE 架构 / mobile 后台行为章节

### 4. HCI 硬件错误与 ISR 延迟:STM32 蓝牙开发排查实战
- 链接：http://www.sheratonhq.com/news/85533
- 来源：sheratonhq 技术 blog（中文）
- 摘要：STM32 主机 HCI UART 接蓝牙模块，HCI_HARDWARE_ERROR_EVENT (0x10) + ISR delay 双错根因：ISR 内 HAL_Delay 与 SysTick 优先级倒置 / 关中断超字节间隔致帧错位 / NVIC 分组错 / 阻塞 printf；含 GPIO 测 ISR 延迟 + 速查表
- 关键实战点：(1) 排查序：Hardware Code → ISR 延迟波形 → 硬件信号 → 代码审查；(2) 修 ISR 阻塞 > 改硬件优先级；(3) 覆盖 FreeRTOS 随机死机
- 推荐动作：**入主题笔记** → BLE Host 移植 / MCU+模块集成章节（中文 + 可抄代码）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃

覆盖 4 个独立角度：RF 共存（#1）/ 硬件设计（#2）/ 架构（#3）/ 主机移植（#4）——可分别入 L4 章节或合并为"BLE 产线故障 Top-N"系列。
