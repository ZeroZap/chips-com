# BLE 候选素材 @ 2026-08-23 00:00

L4 关联：HCI 错误码、CI/SL/ST 连接参数、SMP 配对三阶段。本批覆盖产线筛 / 实验室→量产漂移 / 配对状态机 bug 三大坑。

## 候选（5 条）

### 1. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：Dewine Labs
- 摘要：多种 BLE 模块受控 Wi-Fi 干扰实测，**多数产线漂移不是硬件问题，而是标准 BLE 固件面向消费场景设计**。工业/医疗/机器人需"确认连接性"，latency spike / 随机断连 / 吞吐塌方是常态。
- 动作：**扩 deep-dive**（chips-com "协议选型决策"——什么时候不该选 BLE）。

### 2. Fast Production Screening based upon Bluetooth DTM
- 链接：https://devzone.nordicsemi.com/blogs/1049/fast-production-screening-based-upon-bluetooth-dtm/
- 来源：Nordic DevZone
- 摘要：Nordic 产线 RF PHY 筛片——两台 nRF51 DK + 同轴 + 屏蔽盒 + UART 脚本驱动 DTM，4 条命令完成 PER，目标"日 10 万片"，station 须低技能工人复用、便携。
- 动作：**入主题笔记**（产线测试章节真实参数样板）。

### 3. BLE Connection Interval and Battery Life
- 链接：https://punchthrough.com/ble-connection-interval-battery-life
- 来源：Punch Through
- 摘要：拆 CI × SL 对功耗影响。iOS 强约束 15ms / Android 7.5ms；peripheral latency 仅 p→c 单向省电的不对称性；活动/休眠两段应动态切换 CI。默认 CI 100ms/SL 0 **几乎从来不是出货值**。
- 动作：**入主题笔记**（BLE L4 "连接参数工程化"）。

### 4. BLE 连接不稳定以及突然断开（nRF52832 实战）
- 链接：https://blog.csdn.net/cheer_me/article/details/84545359
- 来源：CSDN（咸鱼）
- 摘要：nRF52832 `ble_app_uart` 蓝本。突然断连归 4 类：天线/晶振/芯片兼容/参数/代码。**核心给"发送 flag 模式"**——必须等 `BLE_GATTS_EVT_HVN_TX_COMPLETE` 回调置位后再 `ble_nus_string_send`，否则看门狗复位断开。
- 动作：**写实战案例**（chips-com BLE 笔记"嵌入式 C 代码片段"）。

### 5. Zephyr #61465: pairing_complete vs disconnect_complete 顺序错乱
- 链接：https://github.com/zephyrproject-rtos/zephyr/issues/61465
- 来源：Zephyr GitHub
- 摘要：Zephyr 3.4.0 host bug——配对刚完就断连，host 把 pairing 报 failed，因 `smp_pairing_complete` 检测到 conn 已 `BT_CONN_DISCONNECT_COMPLETE` 就 abort。**空中先 pair 后 disconnect，host 事件顺序颠倒**——不同 controller 表现不同。
- 动作：**入主题笔记**（SMP/事件流章节真实 bug 样本）。

review 后：激活 / 改写 / 丢弃。

<mavis-progress>idle</mavis-progress>
