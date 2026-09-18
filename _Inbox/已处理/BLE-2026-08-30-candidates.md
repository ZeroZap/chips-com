# BLE 候选素材 @ 2026-08-30 12:00

## 速览
- BLE：2.4 GHz 跳频 + GATT 服务发现 + 加密配对，IoT / 可穿戴 / 手机外设事实标准
- 解决：低功耗（µA 级睡眠 + mA 级瞬时脉冲）下做几十 kbps 短距双向数传
- 跟 L4 关联：跟 LoRa / ZigBee / Thread 同台竞争"短距低功耗"赛道；实战失败模式密度 ≥ LoRa（连接参数 + RF 共存 + 电源 + 主机后台策略四重坑）

## 候选

### 1. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：dewinelabs.com（BLE 测试厂商，做控制 Wi-Fi 干扰下的对比实测）
- 摘要：硬件多半不是元凶。真实场景 BLE 间歇延迟 / 莫名断连 / Wi-Fi 密集时吞吐掉，是 lab 没复现的工厂 / 仓库 / 医院 / 机器人 RF 复杂度。作者团队用受控 Wi-Fi 干扰对比多款主流 BLE 模块，结果推翻几条"常见假设"。
- 实战点：**lab-vs-field 落差根因** = 验证环境不反映现场（金属、多径、Wi-Fi 拥塞、流动设备反射面）；**症状不灾难化** = 延迟突刺 / 间歇断开 / 吞吐随日变化，无法复现；**架构级问题** = 团队先换硬件再换技术，浪费月级
- 推荐：**入 deep-dive** → 跟 #2 spörk 零售案例合成「BLE lab→field 必备自检表」

### 2. BLE retail IoT "overnight degradation" 案例（spörk LinkedIn）
- 链接：https://www.linkedin.com/posts/michael-spoerk_a-ble-system-that-cannot-diagnose-its-own-activity-7467506046744465410-uOwC
- 来源：LinkedIn / Michael Spörk（嵌入式无线从业者）
- 摘要：零售 IoT 部署一夜之间全面劣化。无硬件 / 无固件 / 无安装改动。现场勘察后定位：同频段另一 IoT 网 OTA 升级后占用更多共享频谱（含合规上限）。自家设备没坏，是 RF 环境变了。
- 实战点：**"可自诊断"是部署级硬需求**（不然每次派人上站）；**远程诊断 = 收集 RSSI / 动态协商 TX / 噪声底**；**共享 ISM 频段无法独占** = 邻居 OTA 直接拖垮你
- 推荐：**入实战案例** → 跟 #1 lab→field 互为正反：#1 讲"为啥上站"，#2 讲"上站后发现啥"

### 3. BLE Arduino Nano 33 BLE 断连硬件层排雷（nRF52840）
- 链接：https://electricalflux.com/mcu-general/fix-ble-arduino-nano33-connection-dropouts
- 来源：electricalflux.com
- 摘要：nRF52840 TX 突发 18 mA / +4 dBm 触发 3.3V 跌穿 2.7V brownout → MCU 重置 → 掉链。面包板金属弹簧引脚引入寄生电容把 chip antenna 调偏，10 m 距离直接掉到 30 cm。给出 100 µF 钽 + 100 nF 陶瓷去耦 + 15 mm RF keep-out + PCB 接地铜皮距天线 ≥ 5 mm 的硬规范。
- 实战点：**TX 突发电流预算 = 板级设计必做项**（不是芯片 spec 兜底）；**chip antenna 调偏比选错芯片更要命**；**MTU / connection interval 不匹配 = 移动端静默断开**
- 推荐：**入 deep-dive** → BareOS 这类 128KB RAM / 512KB ROM 板做 BLE 评估时直接当 checklist；可拆出「N32L40X 雷达」 类比

### 4. 工业场景蓝牙"无法连接"4 维排查方案
- 链接：https://gutab.cn/news_industrial/899.html
- 来源：gutab.cn（工业平板 / 嵌入式工控机厂商）
- 摘要：工业现场金属屏蔽 / 多径 / 高频干扰 / 温湿度严苛，家用"重启-重配"逻辑不奏效。给出 4 维分层排查：① 射频物理层（VSWR、AFH 信道图、LOS）+ ② 协议栈 GAP/GATT（广播间隔 vs 扫描窗口、连接参数交集、配对 MAC 白名单）+ ③ 电源管理（瞬时跌落、USB Selective Suspend、ACPI 策略）+ ④ 固件驱动（HCI 队列溢出、MTU 协商、状态机占线）。
- 实战点：**分层定位法** = 从物理层到应用层逐级验；**HCI 错误码比应用错误码值钱 10 倍**（"Send HCI Command Failed" / "Event Queue Full"）；**ACPI 切蓝牙电源** = 工业 OS 隐藏地雷
- 推荐：**入 L4 主题笔记** → 跟 #1 / #2 合成「BLE 工业故障定位 SOP」；可跟 BareOS / XinYi AT 自检思路对位

### 5. 低功耗 BLE 传感器节点实战全攻略（硬件→固件→现场）
- 链接：http://www.wmrh.cn/news/1170933
- 来源：wmrh.cn（IoT 实战 blog）
- 摘要：从 nRF52 / STM32WB / ESP32-C3 选型开始，覆盖外围 LDO 静态电流 / I2C 上下拉 / 状态 LED / 大电容漏电的"隐形 µA"，给出 PPK2 / Joulescope / Otii Arc 测试方案，**48 小时连续录波才暴露的隐藏定时器**真实案例。完整 60s 上报周期算账：睡眠 2 µA + 读传感 5 mA × 15 ms + BLE 广播 11 mA × 8 ms = 3.47 µA 平均 → CR2032 理论 7.2 年，折扣后 3-4 年。
- 实战点：**能量账本精确到 µA**（70 µA 睡眠漏电 = 130 天 vs 预期 2 年）；**法拉第笼隔离法**判内 / 外因；**连接参数保守区间**（iPhone + 三星 + 小米 + 华为真机验证）；**2.4 GHz 共存现场定位** = 金属线槽 / 排烟管反射
- 推荐：**扩 deep-dive** → 跟 user 工作方向「IoT / 可穿戴」强匹配，可拆出「BLE sensor node 量产前 7 项必查」

## 下一步
等 review。优先级 #1 + #2 + #4 走「BLE lab→field 定位法」聚合，#3 跟 BareOS 板级清单合成，#5 单独走 IoT 节点 deep-dive。
