# BLE / Bluetooth LE 候选素材 @ 2026-08-25 21:38

## 候选文章（4 条）

### 1. My BLE peripheral dropped connection every 30s — bug was mDNS
- 链接：https://moltbook.com/post/9ab7ff6d-7e73-4f5e-b65d-e891a0f23edf
- 来源：moltbook 开发者真实调试日志
- 摘要：ESP32-C3 + NimBLE，连接稳定 30 秒后必掉，disconnect 0x08。凶手是同片 WiFi 的 mDNS announce 跟 BLE 连接事件抢 2.4G 共存时隙。
- 实战点：① 2.4G 单射频 coex 是隐性炸弹；② BLE 日志不指向 WiFi；③ 修 coex 优先级比改协议参数管用
- 推荐：**写实战案例**（最贴 L4「真实故障」）

### 2. BLE 30s 掉线：iPhone 挂，Android 稳
- 链接：https://moltbook.com/post/03115e3c-f56c-4983-ad65-e2bfa4791902
- 来源：moltbook（nRF52840）
- 摘要：nRF52840 推流传感器，Android 几小时不连，iPhone 准时 30 秒断。根因：iOS 对 connection param 有硬规则（间隔 15ms 倍数、latency ≤30、timeout ≥2s）静默拒绝 update，固件却按错误间隔跑 housekeeping 阻塞 radio。
- 实战点：① param 是 request 不是 set，central 说了算；② 固件必须 read-back actual params；③ 规则在 iOS Accessory Design Guidelines
- 推荐：**写实战案例**（跟 #1 配套，双平台覆盖）

### 3. BLE 频繁断连全解 + 量产验收 checklist
- 链接：https://ask.csdn.net/questions/9376158
- 来源：CSDN 高赞答
- 摘要：分层拆解：信号层（Wi-Fi/微波炉共存、RSSI<LQI）、协议层（Supervision Timeout ≥ (1+Latency)×Interval×2）、固件层（HCI 缓冲、ISR 耗时）、电源层（DC-DC 纹波 > 30mV 让 RF 灵敏度掉 8-12dB）、OS 层。附 10 项量产验收 checklist。
- 实战点：① 错误码速查（0x05/0x06/0x07/0x08/0x3B）；② 三参数合规公式 + 误配示例；③ 10 项必检
- 推荐：**入主题笔记**（L4 标准的"BLE 量产验收清单"）

### 4. 智能硬件产测踩坑：样机 OK 量产掉线
- 链接：https://www.sohu.com/a/1062723094_122726091
- 来源：搜狐产测行业自媒体
- 摘要：智能门锁打样七八版客户说好，首批 3000 台出货一月退 200+。原因：Wi-Fi 模组不稳、电池异常、北方低温死机。智能秤案例：产测只校重量，蓝牙天线虚焊震动后断连；增加"多工位联测"才暴露。智能锁案例：几十万条产测数据只看漏检率，海外死机回查才发现某批次 RAM 读写慢 20% 早就预警。
- 实战点：① 产测 = 数据采集+趋势，不是 PASS/FAIL；② 隐藏场景（干扰/震动/温变）必须进工位；③ 数据闭环：采集→监控→预警→根因→修正
- 推荐：**写实战案例**（跟 #1 #2 形成"协议层 + 产线层"完整覆盖）

## 下一步
- 优先 #1 + #2 + #4 → chips-com BLE L4 实战案例集
- #3 → 主题笔记《BLE 量产验收 checklist》
