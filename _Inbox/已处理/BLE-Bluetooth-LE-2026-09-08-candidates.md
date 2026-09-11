# BLE / Bluetooth LE 候选素材 @ 2026-09-08 20:24

## 协议速览
- 是什么：低功耗短距无线（2.4 GHz），手机/IoT 主流接入
- 解决什么：替换线缆 + 电池长寿命设备联网
- 跟 L4 主题的关联：IoT/可穿戴首选；lab vs production 失效是 L4 实战热话题

## 候选文章（5 条）

### 1. BLE Firmware for IoT（医疗 6 个月实战）
- 链接：https://qapl.net/blog/ble-firmware-iot-what-to-know
- 来源：QA Platform 工程 blog
- 摘要：医疗血压计 BLE 适配器部署后 30% 测量丢失；拉一周 470K 行 journal 定位 62 个失败（33 freeze + 8 安全 bug + 21 设备不在场）。MCU 256KB RAM，8s watchdog 自愈。
- 实战点：Central ≠ Peripheral（复杂度差一量级）；bonding key 必持久化；8s watchdog 是商业可靠线
- 推荐动作：扩 deep-dive

### 2. nRF52 GATT 通知丢包——根因连接间隔
- 链接：https://moltbook.com/post/f2c80403-2bc3-4ddc-80ee-2992ac71ae99
- 来源：moltbook 工程师复盘
- 摘要：5ms 推 notify 但 central 谈成 30ms 连接间隔，每 event 只发 1 个，tx queue 静默溢出。修复：请求更短 CI + NRF_ERROR_RESOURCES backoff + 等 TX_COMPLETE。
- 实战点：BLE 吞吐 = central 协商窗口；hvx 失败必 backoff；iOS 最短 15ms
- 推荐动作：写实战案例

### 3. Nano 33 BLE 掉线——brownout + 天线失谐
- 链接：https://electricalflux.com/mcu-general/fix-ble-arduino-nano33-connection-dropouts
- 来源：electricalflux 故障排查手册
- 摘要：nRF52840 TX 突发 18mA → 3.3V 跌破 2.7V brownout → MCU 复位断连；面包板寄生电容使 2.4G 天线失谐（10m→30cm）。100µF Ta + 100nF MLCC、15mm RF keep-out、地铜距天线 ≥5mm。
- 实战点：电源去耦不够 = 95% 不明复位；天线 keep-out 是硬约束
- 推荐动作：入主题笔记（BLE 硬件设计硬约束清单）

### 4. 4 款 BLE 模块在 Wi-Fi 干扰下实测
- 链接：https://dewinelabs.com/we-tested-4-popular-ble-modules-under-real-wi-fi-interference-and-heres-what-we-found/
- 来源：DEWINE Labs 实测
- 摘要：100B/100ms 控制回路 + 30ms 时延硬门槛。Wi-Fi 干扰下 Nordic nRF52840 / Ezurio BL654 / Würth Proteus-III / u-blox NINA-B112 全部排队超阈。标准 BLE 是 best-effort，real-time 需双通道隔离 + 自适应干扰响应。
- 实战点：晚到的数据 = 无效数据；单队列混 control/log 是根因
- 推荐动作：扩 deep-dive

### 5. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：DEWINE Labs 系统分析
- 摘要：生产环境 Wi-Fi/金属/多径反射 lab 复刻不出。系统级失败 ≠ 硬件失败；标准 BLE 固件为消费设计，工业/医疗不容。调硬件只是临时缓解，根因在调度。
- 实战点：lab 验证 ≠ 量产可靠；30ms 是工业分水岭
- 推荐动作：跳过（已被 #4 覆盖）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
