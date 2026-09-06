# LoRa / LoRaWAN 候选素材 @ 2026-09-05 00:00

## 协议速览
- 是什么：Semtech 扩频 + LoRaWAN MAC，sub-GHz LPWAN 主流
- 解决什么：电池节点 1-15km、~10 年寿命、少量遥测
- L4 关联：IoT/可穿戴核心；解"低功耗+远距离+占空比"三难

## 候选（5 条）

### 1. LR1120+STM32L433 自研板入网间歇失败（1/10 join）
- 链接：https://github.com/Lora-net/SWL2001/issues/52
- 来源：GitHub（Semtech 官方，EddieCarrera 实战）
- 摘要：STM32L433+LR1120 PCBA 接私有 LoRaWAN，join 10 次成 1 次。换 NUCLEO 跳线复现 → 锁定 LR1120 侧。维护者答：US915 64+8 信道需网关支持；HP/LP 走 `ral_lr11xx_bsp.c` BSP。
- 实战点：①间歇失败=网关信道数 vs 节点跳频列表；②HP/LP 是 BSP 层不是 AT
- 推荐动作：扩 deep-dive

### 2. Azure IoT Edge LoRaWAN 设备 24h 周期性掉线
- 链接：https://github.com/Azure/iotedge-lorawan-starterkit/issues/292
- 来源：GitHub（Azure 官方，1.0.5→1.0.5.1 修复）
- 摘要：LNS 端生产部署所有设备 ±24h 断连，根因 `ENABLE_GATEWAY` 环境变量缺失致 LNS 静默卡死。PR #294 修复。LNS"沉默失败"经典案例。
- 实战点：①24h 周期=内部定时器/证书续期；②docker inspect→env→版本三步走
- 推荐动作：写实战案例

### 3. Mastering Your LoRaWAN Rollout: 5 Common Pitfalls
- 链接：https://www.iox-connect.com/journal/mastering-your-lorawan-rollout5-common-pitfalls-and-how-to-avoid-them
- 来源：ioX-Connect 行业 blog（LoRaWAN 网络运营商）
- 摘要：商业部署 5 坑——(1)网关位置+RF 噪声（Wi-Fi/VFD）；(2)ADR 配错"卡一档"全网拖慢；(3)移动节点 ADR 失效需关改固定；(4)弱安全（ABP vs OTAA）；(5)"Set & Forget" 致 RF 退化。
- 实战点：①RF 噪声=Wi-Fi/中继器/VFD；②移动节点=关 ADR+固定保守；③半年重做 site survey
- 推荐动作：入主题笔记

### 4. LoRa 远距离通信实战：SX1278 模块组网（果园项目）
- 链接：https://makeronsite.com/blog/2026/03/lora-sx1278-practice-guide/
- 来源：MakerOnSite（中文实战博客，农业 IoT 真实项目）
- 摘要：SX1278+Arduino Nano 果园土壤湿度监测，8 网关 500 亩 120 节点跑 1 年稳。市区/郊区/室内三套 SF/BW/CR/功率经验+星型完整代码+RSSI 实测。
- 实战点：①市区 SF9/BW125/CR5/17dBm；②郊区 SF11/BW125/CR7/17dBm；③室内 SF7/BW500/CR5/10dBm
- 推荐动作：扩 deep-dive

### 5. LoRaWAN 实战：传感器到云端（MachineQ 案例）
- 链接：http://www.nxbn.cn/news/9347
- 来源：尧图网（中文，5 篇系列完结篇+真实 MachineQ 接入）
- 摘要：Heltec LoRa 32 V3（SX1262）+BME280+MachineQ US915 全链路（Cayenne LPP→MQTT→InfluxDB→Grafana）。重点：DevEUI 大小端坑、看门狗复位、FCnt 持久化。
- 实战点：①DevEUI 大端 vs 小端=入网失败 #1；②FCnt 必须持久化 EEPROM；③复位原因码 1B 极有价值
- 推荐动作：入主题笔记

## 下一步
review 后决定: 激活/改写/丢弃
