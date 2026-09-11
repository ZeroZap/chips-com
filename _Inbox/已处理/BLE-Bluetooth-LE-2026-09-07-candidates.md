# BLE / Bluetooth LE 候选素材 @ 2026-09-07 00:00

## 协议速览
- 是什么：低功耗短距无线协议（2.4 GHz，GAP/GATT，PHY 1M/2M/Coded）
- 解决什么：手机-外设/IoT 节点的低功耗数据通路
- L4 关联：可穿戴/IoT 产线良率 + 现场连接稳定性，跟出货 IoT 固件高耦合

## 候选文章（5 条）

### 1. Debugging nRF BLE Connection Issues With Zephyr RTOS
- 链接：https://mab-labs.com/blog/debugging-nrf-ble-connection-issues-with-zephyr-rtos
- 来源：MAB Labs 客户真实案例
- 摘要：nRF52840 + Zephyr 在 dev kit 正常、自有产板频繁掉线。根因 Laird BL654 没贴 32.768kHz 晶振（PPM ±500），Zephyr 默认按 dev kit 走 ±50 PPM → 链路层 SCA 协商被手机拒。`CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC` 切到 500 PPM 修复。
- 实战点：BOM 漂移影响 BLE 行为；Zephyr Kconfig 7 档 PPM 必须跟硬件匹配
- 推荐：扩 deep-dive

### 2. A Memory Leak in the Linux Kernel Bluetooth Stack
- 链接：http://www.mind.be/blog/a-memory-leak-in-the-linux-kernel-bluetooth-stack/
- 来源：Mind 嵌入式团队 bug hunt 复盘
- 摘要：嵌入式 Linux 跑 4 天后崩溃，BLE L2CAP 内存泄漏。复现条件"BLE 启但 peer 不存在"——`kmalloc-1k/-192` 持续涨。v5.13/5.15/6.5 复现，patch series + STM32 DK2 + QEMU 复现步骤。
- 实战点：BLE 启不用 = 内存炸弹；`/proc/slabinfo | grep kmalloc` 速定位；syzbot 2023 已报但无人修
- 推荐：写实战案例

### 3. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：Dewine Labs 工业级 BLE 工程咨询
- 摘要：工业/医疗/机器人现场 BLE 延迟波动、莫名断连。根因"标准 BLE 栈为消费设备设计（容忍偶尔延迟），非为工业实时设计"。Wi-Fi 同频干扰下重传窗口让确定性丢失。团队通常先怀疑硬件，但栈层面才是关键。
- 实战点：lab ≠ 产线 RF；工业级 BLE = 重传管理 + 共存策略 + 时序确定性
- 推荐：入主题笔记

### 4. BLE 4.0 协议栈的内存崩坏：从中断饥饿到任务调度死锁
- 链接：https://tsight.io/articles/11664458
- 来源：TrueSight 技术博客
- 摘要：CC254x（8KB RAM）跑 BLE 4.0，连接间隔 7.5ms 时 OSAL 单线程调度撞"死亡临界点"。应用层耗时过长 → LL 层 ACK 超时断连。调试技巧：GPIO 翻转 + 逻辑分析仪看 `osal_run_system` 入口/出口跟 LL ISR 重叠。极端资源下应禁自动连接参数更新、绕 GATT 直接 LL 透传。
- 实战点：8KB RAM BLE 7.5ms 间隔 = 性能死亡区；串口打印加剧崩溃；标准实现可放弃
- 推荐：扩 deep-dive

### 5. Why Wearable IoT Sensor Electronics Fail at Battery Life
- 链接：https://promwad.com/news/smart-textile-electronics-iot-sensors
- 来源：Promwad 硬件/固件外包团队
- 摘要：可穿戴 200mAh lab 跑 72h，field（15°C 温差 + 真实 BLE）只跑 31h。固件无 bug，但**为 lab 设计**。3 件事叠加：手机把连接间隔 200ms→100ms（radio-on 翻倍）；-85dBm 下 PER 8-15%（重传能量翻倍）；低温晶振漂移致 sensor/BLE 事件碰撞，MCU 进不了 deep sleep。
- 实战点：手机会**主动**重协商连接间隔；field 续航只有 lab 40-50% 是常态
- 推荐：入主题笔记

## 下一步
- **1+2+4** 扩 deep-dive（不同平台不同根因，凑"出货 IoT BLE 故障"系列）
- **3+5** 入主题笔记（工业 BLE 可靠性 + 产线续航 vs lab）
- 等 review 决定激活/改写/丢弃
