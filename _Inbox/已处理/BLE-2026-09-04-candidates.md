# BLE / Bluetooth LE 候选素材 @ 2026-09-04 00:00

## 协议速览
- 是什么：低功耗短距无线，2.4 GHz ISM 跳频，GATT 服务/特征抽象
- 解决什么：IoT / 可穿戴 / 工业外设的「手机直连 + 长电池寿命」链路
- 跟 L4 主题的关联：IoT/可穿戴首选协议，晶振/天线/MTU/PHY 是高频踩坑点

## 候选文章（5 条）

### 1. Debugging nRF BLE Connection Issues With Zephyr RTOS
- 链接：https://mab-labs.com/blog/debugging-nrf-ble-connection-issues-with-zephyr-rtoss
- 来源：MAB Labs（嵌入式咨询公司，真实客户案例）
- 摘要：客户产品用 Laird BL654（nRF52840 SOM）跑 Zephyr，开发板没事，自制板 BLE 连接反复掉。根因：32.768 kHz 晶振未贴，时钟精度 ±500 ppm；Zephyr 默认 50 ppm 配置导致 BLE 链路层连接参数违规。改 `CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC` 后稳定。
- 关键实战点：
  - 「开发板没事 / 自制板频繁掉」= 99% 是 BOM/晶振/天线差异
  - 32.768 kHz 晶振精度 → 直接进 BLE SCA（睡眠时钟精度）参数
  - Zephyr `CLOCK_CONTROL_NRF_K32SRC_ACCURACY` 7 档映射，ppm 越大连接越容易掉
- 推荐动作：扩 deep-dive（BLE 链路层 SCA 参数 + 时钟源选型矩阵）

### 2. ESP32 Bluetooth Connection Drops: Error Diagnosis & Fixes
- 链接：https://electricalflux.com/mcu-general/esp32-bluetooth-connection-error-diagnosis
- 来源：Electrical Flux（工程师博客，含真实错误码表）
- 摘要：Bluedroid 占 110-140 KB SRAM，与 WiFi/音频 buffer 抢内存会 `ESP_ERR_NO_MEM`。NimBLE 只占 30 KB，是 BLE-only 项目首选。错误码表实战：0x103=NO_MEM / 0x106=INVALID_STATE / 0x3008=GATT_INSUF_RESOURCE / 0x2002=LINK_LAYER_NO_MEM。
- 关键实战点：
  - Bluedroid vs NimBLE 内存对比表（110-140 KB vs 30 KB）
  - `esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT)` 释放 30 KB
  - MTU 协商时未实现 `onMtuChanged` 回调 → Guru Meditation / buffer overflow
  - ESP-IDF 错误码表（hex → 宏名 → 失效域 → 修复动作）
- 推荐动作：写实战案例（ESP32 BLE 内存踩坑手册）

### 3. 蓝牙无法连接外设：工业场景排查方案
- 链接：https://gutab.cn/news_industrial/899.html
- 来源：合亿 Gutab（工业平板厂商技术博客）
- 摘要：工业 4 维排查框架——①射频物理层（VSWR、AFH 信道表、LOS）②协议栈参数（广播间隔 vs 扫描窗口、连接参数协商、安全/白名单）③电源管理（瞬时电流跌落、USB Selective Suspend、接地环路）④固件逻辑（业务状态机挂起协议栈、SPP-over-BLE MTU 协商）。每维都给具体测量点和系统日志关键词。
- 关键实战点：
  - 工业外壳金属屏蔽 → 天线 VSWR 检测是必查项
  - 「外设极长广播间隔 + 主机短扫描窗口」= 经典「设备找不到」
  - HCI 日志抓 `Send HCI Command Failed` / `Event Queue Full` → 驱动层 buffer 溢出
  - 工业 OS 的 USB Selective Suspend 会偷偷断蓝牙供电
- 推荐动作：扩 deep-dive（工业 BLE 4 维排查决策树，可入 basic/）

### 4. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：DEWINE Labs（北欧工业 BLE 工程公司，专注实时无线）
- 摘要：4 款 Nordic 系 BLE 模块（nRF52840 HCI / BL654 / Proteus-III / NINA-B112 + LinkBlu RT）在 1 m / 100 B / 100 ms / ≤30 ms 延迟约束下的对比。干净 RF 环境下都过；Wi-Fi 干扰下标准 BLE 全部超 30 ms。LinkBlu RT 因双通道隔离 + 自适应干扰处理仍稳定。
- 关键实战点：
  - 「lab 过 ≠ 产线过」= RF 复杂度（金属反射、运动设备、2.4 GHz 拥挤）差异
  - 30 ms 实时阈值下标准 BLE 表现（具体延迟分布图）
  - LinkBlu RT 设计原则：bounded latency + dual-channel isolation + adaptive interference handling
  - 「吞吐量能过 / 实时性不过」= 工业 BLE 真实门槛
- 推荐动作：写实战案例（实时 BLE 系统选型对比，IoT/工业可参考）

### 5. TI CC23xx Debugging Runtime Issues（broken_basic_ble 实战 lab）
- 链接：https://dev.ti.com/tirex/content/simplelink_academy_for_cc23xx_8_40_00_00/_build_simplelink_academy_for_cc23xx_8_40_00_00/source/cc23xx_debugging_runtime_issues.html
- 来源：Texas Instruments 官方 SimpleLink Academy
- 摘要：故意留 bug 的 `broken_basic_ble` 工程做 debug 教学。症状：手机能扫到但「Peripheral Connection Timeout」。Debug 流程：①硬件 sanity（供电/RF 路径/SmartRF Studio 双向打流）②抓 sniffer log 看 LL 报文。预编译 hex file 可用作对照。
- 关键实战点：
  - 「能扫到不能连」= 经典 LL 层问题，先用 SmartRF Studio 隔离 RF 路径
  - Sniffer 抓包比看 log 高效得多（看 LL 控制报文）
  - TI 的 hex files 在 `\examples\rtos\\ble5stack\\hexfiles`（自研硬件不要用）
- 推荐动作：跳过（教学 lab 价值一般；上面 4 条实战更重）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
