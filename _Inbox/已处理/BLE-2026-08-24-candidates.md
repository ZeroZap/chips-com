# BLE / Bluetooth LE 候选素材 @ 2026-08-24 12:00

## 协议速览
低功耗短距射频 (2.4 GHz)，GATT 服务-特征值模型；BLE 5.x 加 2M PHY / Coded PHY。解决可穿戴 / IoT 终端"手机直连 + 纽扣电池 1 年续航"硬需求。L4 关联：IoT/可穿戴 优先。

## 候选文章 (5 条)

### 1. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：dewinelabs
- 摘要+实战：实测多 BLE 模块在 Wi-Fi 干扰下延迟/吞吐，挑战"换硬件"误区。工业三大杀手 = Wi-Fi 同频 / 金属反射 / 移动体；标准 BLE 固件为消费场景设计。
- 扩 deep-dive：产线环境分类 + BLE 鲁棒性矩阵

### 2. ESP32-C3 BLE dropped every 30s — bug was mDNS
- 链接：https://moltbook.com/post/9ab7ff6d-7e73-4f5e-b65d-e891a0f23edf
- 摘要+实战：ESP32-C3 + NimBLE 30s 必断。查 2 天协议栈才发现 mDNS + WiFi beacon 挤掉 6 个连接事件。单 2.4 GHz 射频共存隐形雷；0x08 错误码不指明共存争用。修复：supervision 4s + interval 50ms + `esp_coex_preference_set(ESP_COEX_PREFER_BT)`
- 入主题笔记：单芯片共存坑 + ESP_COEX 配置

### 3. nRF52840 dropped every 30s on iPhone, worked on Android
- 链接：https://moltbook.com/post/03115e3c-f56c-4983-ad65-e2bfa4791902
- 摘要+实战：nRF52840 自定义 GATT，Android 跑通，iPhone 30s 断。申请 7.5ms interval + 0 latency + 400ms supervision，**iOS 静默拒绝** (要求 interval 15ms 倍数 / timeout ≥ 2s / `timeout > (1+latency)*interval*2`)。iOS Accessory Design Guidelines 参数表必读。
- 扩 deep-dive：iOS/Android 蓝牙栈参数兼容矩阵

### 4. BLE 断连原因分析 (GR55xx 基带诊断 + 错误码)
- 链接：https://developers.goodix.com/zh/bbs/detail/c649c96ac97a4959a855b326b9b11f8b
- 来源：Goodix (GR55xx 国产 BLE SoC)
- 摘要+实战：汇顶 FAE 笔记，GR551x/5525/5526/5331 基带诊断 GPIO + 钩子函数 (`diag_evt_start_cbk_start_func`)，逻辑分析仪打 Radio Event→App Callback 时差。错误码：0x98=超时/调度、0xB8=指令错过、0xB2=响应超时、0xCE=建连失败、0xA3=远端主动、0xCD=加密相关。国产 SDK 调试不输 Nordic。
- 入主题笔记：0x08/0x28/0x3B/0x3E/0x98 跨芯片错误码映射

### 5. STM32+nRF52840 SPI/BLE 功耗异常实战
- 链接：https://blog.csdn.net/open4/article/details/155453744
- 摘要+实战：手环 3.2mA vs 目标 8μA (差 400 倍)。定位：① ISR 阻塞 ("假休眠")；② SPI 频繁小包 (合并 burst 减 55%)；③ 协议栈重传 (中断响应 > 1ms)。方案 = 轻量 ISR + 任务通知 + 环形缓冲 + 动态连接参数三档，实测降耗 35%。ISR "三不原则" (不打印/不访问 SPI/不阻塞)。
- 写实战案例：外置 BLE + 主控 MCU 电源/性能权衡模板
## 下一步
等你 review：激活 / 改写 / 丢弃
- 激活：#1 + #4 (内容稀缺)
- 改写：#2 + #3 (moltbook 社区帖可改写"国产芯片视角")
- 跳过：无