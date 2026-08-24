# BLE 候选素材 @ 2026-08-22 12:00

低功耗短距无线（2.4 GHz），IoT/可穿戴主力；出货链路核心，掉线/配对失败/电池 brown-out 是线上高频事故。候选 5 条：

### 1. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：DEWINE Labs（Nordic 平台工业 BLE 咨询）
- 摘要：实测多款 BLE 模块在 Wi-Fi 干扰下的延迟/吞吐，挑战"硬件是瓶颈"假设；BLE 消费级偶发延迟可接受，工业控制环下时序敏感崩。
- 实战点：(a) 实验室干净 RF≠产线稳定 (b) best-effort 调度负载下失效 (c) 确定性调度方案 LinkBlu RT
- 推荐：**扩 deep-dive**（L4 工业部署章节核心案例）

### 2. BLE Is Not Just a Protocol: System-Level Design Mistakes
- 链接：https://www.eurthtech.com/post/ble-is-not-just-a-protocol-system-level-design-mistakes-engineers-make
- 来源：EurthTech blog
- 摘要：5 类架构性错误：透明管道化/忽视中心设备/功耗后置/状态机爆炸/安全假设不演进；附多年出货产品真实案例。
- 实战点：(a) 5 误区结构化清单 (b) bonding/密钥/隐私要随部署期演进 (c) 设计期建模恢复路径
- 推荐：**入主题笔记**（L4"系统级设计"骨架）

### 3. Why Battery Percentage Can't Predict a Bluetooth LE Brown-Out
- 链接：https://novelbits.io/battery-percentage-bluetooth-le-brownout
- 来源：Novel Bits（Nordic 周边 BLE 培训站）
- 摘要：纽扣电池 BLE 发射瞬间电流尖峰触发 brown-out，bonding 键损坏、supervision timeout；电池百分比采静止电压不预测 loaded 跌落。TI：22~50 μF 储能电容可恢复 40%+ 容量。
- 实战点：(a) POF 才是低电量正确信号 (b) 22~50 μF 电容单点最大杠杆 (c) 复位循环加速电芯高内阻末段
- 推荐：**写实战案例**（brown-out SOP,穿戴向）

### 4. BLE 连接问题排查指南
- 链接：https://www.tuyaos.com/viewtopic.php?t=3989
- 来源：Tuya 开发者论坛（IoT 官方）
- 摘要：FAE 视角排查手册：设备/手机/配网/广播/工具五步；7 个高频 HCI 错误码（0x08/0x13/0x16/0x1F/0x22/0x28/0x3D）及解法。
- 实战点：(a) 错误码速查表 (b) Android 默认 7 GATT 上限（SDK 设备 4）(c) 涂鸦配网 30s 超时硬约束
- 推荐：**入主题笔记**（L4"错误码速查"小节）

### 5. BLE 连接异常断开原因深度解析与重连策略实战
- 链接：https://blog.csdn.net/pytorch8learner/article/details/155528816
- 来源：CSDN 工程师博客
- 摘要：拆 0x3E 错误底层（6 广播事件内未建链）；办公 2.4 GHz 噪声比郊区高 20 dB；iOS 7.5ms vs 国产锁 15ms 触发 0x3B。
- 实战点：(a) PCB 天线净空距离 +30% (b) 工业 IoT 自定义信道算法稳定性 +50% (c) CONN_INTERVAL>112.5ms 时 Android 13 弱信号重连失败率 68%
- 推荐：**入主题笔记**（L4 中文实战，与 #4 中西对照）

## 下一步
等你 review。优先级：1>2>3>4≈5。
