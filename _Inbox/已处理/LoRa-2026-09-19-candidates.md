# LoRa / LoRaWAN 候选素材 @ 2026-09-19 12:00

## 协议速览
- Sub-GHz 扩频（CSS）低功耗广域网，物理层 LoRa + MAC 层 LoRaWAN
- 电池节点数公里级、低速率（0.3-50kbps）回传，省 SIM 月费
- L4 关联：IoT 户外传感主力；坑集中在 SF/BW/CR + 同频互扰 + Aloha 容量

## 候选文章（5 条）

### 1. LoRa 项目翻车实录：SF/带宽/编码率配置不当，电池续航"雪崩"
- https://blog.csdn.net/weixin_30443813/article/details/97916213（CSDN）
- 摘要：万亩农田承诺 3 年续航 4 月失联；根因 SF 盲调 12，100B 帧 6554ms。气象站 SF7→SF10，AA 电池 18→5 月；智慧水务 SF10→SF8+自适应，6000 水表 9→48 月。
- 实战点：SF 每+1 传输时间翻倍（SF12=32.77ms/符号@125kHz）。
- **入主题笔记 → LoRa 功耗铁三角**

### 2. 车间无线通信总断连？LoRa 工业终端（JYLN061）抗干扰实战
- https://blog.csdn.net/weixin_29190651/article/details/165370174（CSDN）
- 摘要：三大杀手——变频器（IGBT 2-16kHz 谐波漂移）/ 电焊机（拉弧宽带脉冲）/ 多径驻波（移动 30cm 差 20dB）。200×80m 汽车车间 SF10+BW125+CR4/5+27dBm，1h 0 丢包。
- 实战点：灵敏度每+3dB≈距离×1.14；天线高于金属 30cm；RS485 隔离+单点接地。
- **写实战案例 → 车间部署 SOP**

### 3. LoRa 12km line-of-sight but failed at 400m in a warehouse
- https://moltbook.com/post/3c844e60-953e-490f-8c64-2e86c79948ff（moltbook）
- 摘要：SX1276 SF9 +14dBm 户外 12km；仓库 400m 丢一半。**真凶 VFD 变频器把 868MHz 噪声底拉满**——RSSI 还能看，SNR -3~-8dB 过不了 SF9 解调门限。修法：天线升 3m + LNA 前 cavity filter，SNR → +7。
- 实战点：必须 RSSI+SNR 双轨记录。
- **入主题笔记 → 站点勘测 SOP**

### 4. LoRa 12km line-of-sight but failed at 400m in a parking garage
- https://moltbook.com/post/9796be07-afe5-4bb7-91ed-83fb81c99732（moltbook）
- 摘要：SX1276 SF7 户外 12km；停车场 400m 混凝土几乎 0 包。**真凶不是 RF——40 节点同 RTC 边界唤醒，2 秒窗口同频碰撞，capture effect 只剩最强**。修法：chip unique ID 随机 0-45s 偏移写 flash，丢包 95% → <3%。
- 实战点：ALOHA 数学早算过但实战没人算；capture effect = 强包吃弱包。
- **入主题笔记 → LoRa 密集部署 ALOHA 容量模型**

### 5. My LoRa SF5 Realistic Range Journey — 6 月 147 测试复盘
- https://dredyson.com/my-lora-sf5-realistic-range-journey-what-i-learned-after-6-months-of-testing-a-complete-case-study-on-sx1262-modules-antenna-selection-and-why-your-range-might-be-10x-lower-than-expected
- 摘要：定位 4 隐形坑——RadioLib bug 锁 TX +11dBm 丢 19% 距离；sync word 默认 0x34 收邻居包→CRC 错；SX1262 boosted RX 未开白丢 3dB；配置顺序错位引发 CRC。
- 实战点：SF5→SF12 = 26dB 增益 ≈ 距离×40。
- **扩 deep-dive → LoRa 选型 + RadioLib 坑清单**

## 下一步
review 后决定激活/改写/丢弃。下次轮询 **CAN FD / CAN XL**。
