# ZigBee 候选素材 @ 2026-09-10 14:04

## 协议速览
- 是什么：基于 IEEE 802.15.4 的低功耗 Mesh（2.4GHz/250kbps/16 信道）
- 解决什么：电池节点星/树/Mesh 组网 + AES-128 加密
- 跟 L4 关联：与 BLE/Thread/Matter 同列 IoT 短距无线栈

## 候选文章（5 条）

### 1. The Week the Sniffer Earned Its Keep
- 链接：https://hackaday.io/project/206190/log/249349
- 来源：Hackaday.io 项目日志
- 摘要：自研 ESP32-C6 sniffer 一周撞 3 故障：车库 Tuya -96dBm 直连无 router 备援；整网 NWK_NO_ROUTE 实为 Hue 桥前级 desense（空间近非信道冲突）；配对停滞。RSSI histogram 面板定位 loud-neighbor。
- 实战点：① 强信号 desense 在空间不在频段 ② 高帧率+RSSI 集中=物理近
- 推荐动作：扩 deep-dive（sniffer + RSSI histogram 算法）

### 2. ZigBee 工业组网"自愈"变"自杀"
- 链接：https://tsight.io/articles/12807223
- 来源：TrueSight 工业 IoT 分析
- 摘要：化工厂 380 节点凌晨 3 点掉线，实为金属罐体多径抖动→MAC 重传→ED 偏高→子节点判丢失→离网广播风暴→雪崩。弃用三判据：强金属+移动遮挡/实时<50ms/密度>30-50。
- 实战点：① PCB Dk 温漂 2MHz→PA VSWR 恶化 ② CSMA/CA 过度谦让
- 推荐动作：写实战案例（金属产线 ZigBee vs LoRa vs TSN 决策树）

### 3. ESP32-C6 Zigbee Remote Failure（4 层叠加故障）
- 链接：https://dredyson.com/why-zigbee-remote-failure-matters-more-than-you-think-...
- 来源：dredyson.com 工程复盘
- 摘要：3 周调 C6 遥控器：setReporting 缺配/C6 SDK 跨芯片 bug（time cluster 缺实现→null crash）/Z2M converter 编码须与固件一致/GPIO0 浮空需 5MΩ 下拉/NVS 双阶段重配。
- 实战点：① 5MΩ 兼顾防浮空+键盘弱电压触发 ② NVS 双阶段
- 推荐动作：入主题笔记（C6 end device 实战清单 + 跨芯片 SDK 雷区）

### 4. SNZB-02DR2 OTA 解析失败：Telink SDK 加密格式变更
- 链接：https://sonoff.tech/en-us/blogs/news/fixing-the-snzb-02dr2-ota-issue-improving-home-assistant-support-for-telink-ota
- 来源：SONOFF 官方博客
- 摘要：2025-09 SNZB-02DR2 在 SONOFF 网关 OK，HA（Z2M+ZHA）三症：check fail/100% 卡住/推送缺失。根因=Telink 0xf000 sub-element 插 Tag Info 致标准 ZCL OTA offset 错位。#9963+#9984 修复。
- 实战点：① OTA 三类失败：传输/解析/版本 ② 厂商私货 sub-element 突破 length 语义
- 推荐动作：扩 deep-dive（OTA 失败判定流程 + 私货 sub-element 适配 checklist）

### 5. 破解 ZigBee 三大工程难题｜晓网 WLT 工业模组
- 链接：https://m.eechina.com/view.php?id=906446
- 来源：电子工程网（晓网科技）
- 摘要：传统 ZigBee 160 节点离线 9.1%/延迟 600ms+；WLT 380 节点 72h 满载=99.6% 在线/<10ms。AT 无返回 6 大原因+6 对策。WLT2430Z 视距 3km，休眠<4μA。
- 实战点：① 上电 3s 内发指令必丢 ② 信道 25 抗 450MHz 谐波
- 推荐动作：入主题笔记（产线选型 checklist + 工业模组 4 硬指标）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
