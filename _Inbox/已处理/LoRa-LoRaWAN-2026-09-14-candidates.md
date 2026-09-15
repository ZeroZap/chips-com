# LoRa / LoRaWAN 候选素材 @ 2026-09-14 12:00
是什么：基于 LoRa 调制的 LPWAN，sub-GHz，Class A/B/C 三类终端。解决电池场景小包（几十~200B）公里级广域上行。跟 L4 主题关联：IoT/可穿戴关键 LPWAN 候选，与 BLE/ZigBee 互补。
### 1. 基于 LoRaWAN 的智能能源系统实践：从选型到踩坑全记录
- 链接/来源：https://www.sheratonhq.com/news/80827 ｜ 技术博客（中文）
- 摘要：350→420 点位智能能源全链路。3 月后 P0 事故三因素叠加：半信道网关瓶颈 + ChirpStack 连接池打满 + ADR 全网 SF7 扎堆。FUOTA 升级 Class A/C 切换；STM32L0+SX1262 节点 50uA 均流。P0 三步修法吞吐×4，jitter 削高峰 60%，470MHz 频谱扫干扰避广电共存。
- 推荐：**扩 deep-dive**（P0 + 电源树 + FUOTA 灰度入主题笔记）

### 2. Why Industrial Predictive Maintenance Deployments Fail in Year Two
- 链接/来源：https://techeasily.co.uk/?p=10793/ ｜ techeasily IIoT 博客
- 摘要：欧洲制造/物流/能源 3 个真实失败案例。核心论断：失败不在 AI/传感器，而在网关 12 小时上行断链污染 AI baseline → 14-22 月信任崩溃死亡。汽车厂 VFD 干扰试点未暴露；冷库 18 AP 改 2 网关；双 SIM failover + buffer 保 sequence。
- 推荐：**写实战案例**（"断链 → baseline 漂移 → 死亡"失败模式笔记）

### 3. LoRaWAN in the wild: notes from a few real deployments
- 链接/来源：http://echolo.io/journal/lorawan-in-the-wild ｜ echolo.io 一线部署商
- 摘要：水产/农业/工业 4 年部署笔记。直白说营销文不靠谱：spec 10mi/10y/多并发只实验室成立。真实距离 农场 6-8mi / 林地 1-3mi / 工业 200-600m；电池 2-3y 不是 10y；不再做的设计：WiFi-LoRa 桥、sub-minute 采样、单网关。
- 推荐：**入主题笔记**（"LoRa spec vs reality"参考表）

### 4. Troubleshooting LoRaWAN Downlinks Scheduled But Not Sent
- 链接/来源：https://industrialmonitordirect.com/ar/blogs/knowledgebase/troubleshooting-lorawan-downlinks-scheduled-but-not-sent ｜ Industrial Monitor Direct
- 摘要：NS 显示"scheduled"但设备没收到的故障排查，4 Fault Domain 矩阵（应用/NS/网关/边缘）。Domain A encoder 异常 try/catch；Domain B ChirpStack device lock 改 replace 模式；Domain D Class A 必须等上行才有 RX 窗口。
- 推荐：**扩 deep-dive**（ChirpStack/TTN/AWS IoT Wireless 三平台 + MQTT 订阅定位法）

### 5. LoRaWAN Gateway Troubleshooting: RSSI, SNR & Packet Loss
- 链接/来源：https://www.robustel.store/blogs/industrial-iot-blog/lorawan-gateway-troubleshooting-rssi-snr-packet-loss ｜ Robustel 工程级博客
- 摘要：从 Wi-Fi/Cellular 转 LoRaWAN 的 SNR 阈值差异 + 3 种丢包 pattern 根因 + 4 类隐性硬件故障。SF7 需 SNR≥-7.5dB / SF12 需 -20dB；3 pattern 随机/周期/沉默；隐性故障 电缆进水、pigtail 折断、天线 2.4G/915G 错接。
- 推荐：**入主题笔记**（RSSI/SNR 阈值速查 + 丢包诊断流程 + 硬件 checklist）
