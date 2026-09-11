# LoRa / LoRaWAN 候选素材 @ 2026-09-11 00:00

## 协议速览
- 是什么：基于 Chirp 扩频的 LPWAN 协议，sub-GHz 非授权频段，星型 + IP 回传
- 解决什么：电池终端 2-5 km 范围、每小时几十字节的 IoT 场景
- 跟 L4 主题的关联：IoT/可穿戴"低功耗广域"代表，跟 BLE/Zigbee 短距/远距互补

## 候选文章（5 条）

### 1. 基于 LoRaWAN 的智能能源系统实践（拓冰网络）
- 链接：http://www.kwkd.cn/news/79492
- 实战点：①P0 事故 = 半信道网关瓶颈 + PG 连接池打满 + ADR SF7 扎堆三联 ②470 MHz 频谱仪前置扫频 ③FUOTA 时电池节点平时 Class A 收指令才切 Class C
- 推荐：**扩 deep-dive**（大规模组网必踩坑）

### 2. Why Industrial Predictive Maintenance Fail in Year Two（EasyNet）
- 链接：https://techeasily.co.uk/?p=10793/
- 实战点：①VFD 干扰 CNC 区 LoRa，pilot 通过 rollout 失败 ②双 SIM failover + 本地缓冲保时序无 gap ③同款传感装 27 种机器未调采样率，6 台"产生无效数据"
- 推荐：**写实战案例**（Year-2 失效独立笔记）

### 3. LoRaWAN 智能能源 300 节点从翻车到稳定（尧图网络）
- 链接：http://www.wmrh.cn/news/1191354
- 实战点：①NS 与业务平台解耦，改 payload 不牵连密钥/ADR ②应用层去重键 = "设备 ID + 设备本地时间戳"，服务器时间会"倒序电量" ③FUOTA 100KB 实际分多段 + 灰度推送
- 推荐：**入主题笔记**（产线规模化 checklist）

### 4. Troubleshooting LoRaWAN Downlinks Scheduled But Not Sent
- 链接：https://industrialmonitordirect.com/pt/blogs/knowledgebase/troubleshooting-lorawan-downlinks-scheduled-but-not-sent
- 实战点：①最常见隐性失败：encoder 异步抛错 UI 仍显 "scheduled"，需订阅 MQTT `+/devices/+/events/#` 抓 as.up.errors ②单信道 forwarder（ESP32 单信道 sketch）下行不可靠，TTN 不支持 ③RX2 区域 mismatch：RX1 OK RX2 永不到
- 推荐：**入主题笔记**（下行诊断矩阵必备工具表）

### 5. ESP32 LoRaWAN Troubleshooting: Fix Join & TX Errors
- 链接：https://electricalflux.com/mcu-general/esp32-lorawan-troubleshooting-join-errors
- 实战点：①TTN 密钥：DevEUI/JoinEUI MSB，AppKey LSB，LMIC 需手动 reverse ②Heltec V3 SX1262 初始化序列与 SX1276 不同，标准 LMIC V3 上 SPI timeout ③US915 网关多听 Subband 2 (8-15)，其他信道永远 EV_JOIN_FAILED
- 推荐：**扩 deep-dive**（板级 SPI/DIO 端序硬件细节）

## 下一步
等你 review：激活 / 改写 / 丢弃
