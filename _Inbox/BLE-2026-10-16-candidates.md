# BLE 候选素材 @ 2026-10-16 12:00

24h 去重通过（_Inbox 空）。轮询第 1 项。无 reviewed-。

## 协议速览
2.4 GHz 低功耗短距无线，IoT 标配通道；Mesh/Audio/Beacon/配网 4 类 L4 实战是产线翻车重灾区。

## 候选（5 条）

### 1. ESP32 双模量产：5 万片被海关扣留
- https://blog.csdn.net/weixin_42552315/article/details/165448346
- CSDN，17 个量产项目作者
- 摘要：跳过 EMC 预扫致 5 万片 Wi-Fi 辐射超标被海关扣，整改 +0.32 元/片 总损 16 万；多项目对比 ESP32 vs nRF52840+ESP8266 双芯。
- 实战：①共享 RF→BLE 连接 800→3200ms / 失败率 0.3→12.7% ②OTA 抢占 BLE 广播致配网无响应 ③模组 vs 开发板 ≥8dB SNR 差，量产必三批次
- 动作：扩 deep-dive（"ESP32 产线翻车档"主题笔记）

### 2. b-parasite：nRF52840 土壤传感器 PCBWay 10 块量产
- https://smarthome-aber-sicher.de/en/blog/2026/09/24/b-parasite-bodenfeuchtesensor
- smarthome-aber-sicher.de，独立博主
- 摘要：PCBWay Turnkey 拼装 10 块 nRF52840+E73 模组开源传感，BTHome 配网；ESP32 充当 SWD 烧录器免 J-Link。
- 实战：①HASL 焊盘残留致 CR2032 不导电，砂纸打磨修 ②ESP32_nRF52_SWD 把 ESP32 变 SWD flasher ③HEX→BIN：HEX 烧 10 块几分钟，BIN 几十秒（量产关键）
- 动作：写实战案例（"小批量 BLE 节点 DIY 量产"）

### 3. BWG840x BLE→MQTT 双芯片网关 30 min
- https://docs.adsumnetworks.com/ble-wifi-gateway
- Adsum Networks（IoT 工具厂商 blog）
- 摘要：Fanstel BWG840 上 nRF52840 全 adv 扫描 + ESP32 UART 上 MQTT + Dashboard；成品走 CRA（欧盟网络弹性法案）SBOM/CVE 扫描。
- 实战：①5cm 内 36 adv 包 0 接收→3 层 debug 定位 ②Wi-Fi 凭据错 fallback AP 不变砖 ③UART 帧+CRC+状态帧对齐双芯 LED
- 动作：写实战案例（"双芯片网关 L4 排查"）

### 4. nRF52840+Zephyr IEC 62304 CGM：FDA 0 整改
- https://www.ankhinnovations.com/services/firmware-development
- Ankh Innovations，认证外包案例库
- 摘要：医疗 BLE CGM nRF52840+Zephyr+MPU，400 项 HIL 覆盖 BLE/ADC/加密，FDA 0 整改；同年 1.2 万工业节点 ECDSA P-256 双 bank OTA 0 砖机。
- 实战：①47 build / 6 月 / 1% canary 灰度 ②ECDSA P-256 bootloader 装入 32KB + bsdiff 差分 70% payload ③10000 次中断 OTA soaks 验回滚
- 动作：扩 deep-dive（"高可靠 BLE OTA 设计"主题）

### 5. BLE Mesh 节点配网失败：8 层排查表
- https://ask.csdn.net/questions/9114652
- CSDN 问答，采纳答案
- 摘要：Provisioning 失败 7 大根因 + 物理/链路/网络/应用/安全/环境/固件/协议栈 8 层排查表 + Mermaid 流程。
- 实战：①37/38/39 与 Wi-Fi 1/6/11 撞 → 30%+ 丢包 ②未 Factory Reset 拒二次配网 ③IV Index 不同步 / NetKey 错绑是隐形地雷
- 动作：入主题笔记（"BLE Mesh L4 排查 checklist"）

## 下一步
review 后：激活 / 改写 / 丢弃

<mavis-progress>idle</mavis-progress>
