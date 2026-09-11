# LoRa / LoRaWAN 候选素材 @ 2026-09-06 12:00

## 协议速览
- 是什么：sub-GHz 免授权 LPWAN（Semtech 调制 + LoRa Alliance MAC）
- 解决什么：电池供电、km 级覆盖、星型（终端→GW→NS→App）
- L4 关联：智能农业 / 工业监测 / 楼宇 IoT 第一选项

## 候选文章（5 条）

### 1. 如何解决 LoRaWAN 空中资源挤兑问题（腾讯云）
- 链接：https://developer.cloud.tencent.com/article/2584909
- 来源：腾讯云开发者社区
- 摘要：分析 GW 8 上行 / 1 下行"挤兑"瓶颈，三大策略。
- 实战点：① 大规模同时上电→Join Storm 阻塞下行；② Unconfirmed+应用 ACK 释放下行；③ 本地 ADR 在网络 ADR 失效时仍能调 SF。
- 动作：**写实战案例**（国内大规模 LPWAN 容量工程模板）

### 2. LoRa SX1278 传输距离不足:实战排查（华为云）
- 链接：https://bbs.huaweicloud.com/blogs/469043
- 来源：华为云博主
- 摘要：理论 2km 实际 300m，链路预算缺口 ≥30dB，五步排查。
- 实战点：① 默认 17dBm 不是 20dBm（3dB=距离 1.4×）；② 发射瞬间 VCC 跌落≥0.3V；③ 天线 1m→2m 可让 300m→600-900m。
- 动作：**入主题笔记**（链路预算+电源滤波做"选型避坑"独立章节）

### 3. Why Industrial PdM Fails in Year Two（TechEasily / EasyNet）
- 链接：https://techeasily.co.uk/?p=10793/
- 来源：欧洲 IIoT 团队博客
- 摘要：汽车/食品/物流多案例——Pilot 通过但主车间月内丢 3/8 集群；12h 上行断网损坏 AI 时序基线，月 14-22 部署"安静死亡"。
- 实战点：① VFD 干扰 Pilot 未暴露；② 鹿特丹冷库 18 WiFi AP 不敌 2 LoRaGW；③ 双 SIM + 本地缓冲防时序断点。
- 动作：**扩 deep-dive**（L4 闭环+网关可靠性，工业 IoT 案例集）

### 4. ESP32 LoRaWAN Troubleshooting: Join & TX（electricalflux）
- 链接：https://electricalflux.com/mcu-general/esp32-lorawan-troubleshooting-join-errors
- 来源：英文硬件博客
- 摘要：90% EV_JOIN_FAILED = 密钥字节序 + US915 subband；MCCI LMIC 与 SX1262 不兼容（DIO 路径不同）。
- 实战点：① DevEUI 用 MSB、AppKey 用 LSB；② US915 64 信道只 8 subband 监听；③ Heltec V3 需 `LMIC_selectSubBand(1)`。
- 动作：**入主题笔记**（嵌入式工程师最常踩两坑清单）

### 5. SX1262 vs SX1278 实战选型（CSDN 8 年 IIoT）
- 链接：https://blog.csdn.net/weixin_30430169/article/details/97980463
- 来源：CSDN
- 摘要：智慧水表实测 SX1262 通信 4→8 次/日、整体功耗 -23%；山区气象站多径下 SX1278 反而更稳。
- 实战点：① DC-DC 模式需 47nH 外部电感，错配就 brownout 0mA；② 决策树：>3 年电池+>20 次/日+尺寸受限→SX1262。
- 动作：**写实战案例**（决策树进 L4 笔记"LoRa 选型"模块）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
