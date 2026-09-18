# LoRa / LoRaWAN 候选素材 @ 2026-08-28 00:00

实战坑集中在入网流程、空中资源挤兑、RX 时序三类隐藏细节

## 候选文章（5 条）

### 1. LoRa Network Failure Story: Debugging in the Field (LinkedIn · World Bank IoT post-mortem)
- 链接：https://www.linkedin.com/posts/mashuk-e-lahi_iot-embeddedsystems-fieldengineering-activity-7471360772607021057-nVoH
- 摘要：城市空气监测 Day1 40 节点在线，Day2 16 节点掉线。两周排查 4 个并发根因：城市 RF 干扰削 LoRa 距离 60%、GSM 信号楼内 3 满格差、传感器运输温度冲击致校准漂移、PCB 冷焊点振动失效。实战点：现场 debug 须"症状→物理→链路→应用"逐级。
- 推荐：入 deep-dive（真实故障链，跟 user 的 IoT/可穿戴方向高度匹配）

### 2. LoRaWAN downlink never arrived — RX2 datarate mismatch (Moltbook)
- 链接：https://moltbook.com/post/29806580-2904-41f4-96dc-3f8281314757
- 摘要：节点 join+uplink 全 OK，2 天收不到下行。根因：节点 RX2 硬编码 DR0(SF12)，NS 配 RX2=DR3(SF9)；cheap crystal 致 RX1 漂移使下行全落 RX2，SF12 解调器对 SF9 完全失聪。修复 1 行：join-accept 解析 DLSettings.RX2DataRate。实战点：DLSettings byte 必须从 join-accept 解析。
- 推荐：扩 deep-dive（"LoRaWAN 协议栈 silent failure 系列"开篇）

### 3. LoRaWAN 大规模部署隐形瓶颈：空中资源挤兑 (腾讯云)
- 链接：https://cloud.tencent.com.cn/developer/article/2637228
- 摘要：网关 8 收/16 解调 vs 单一发射通道，下行是 1/N 瓶颈。优化：①按需入网（避免 join storm）；②慎用 confirmed；③本地 ADR（设备按 RSSI/SNR 选 SF7/8，不依赖 NS 下行）。实战点：服务器 ADR 在下行拥堵时永远到不了 → 本地 ADR 是唯一可靠路径。
- 推荐：写实战案例（user 产线必踩 join storm + 本地 ADR 两坑）

### 4. STM32WL LoRa 节点入网失败问题分析 (EET China · ST 官方)
- 链接：https://www.eet-china.com/mp/a255088.html
- 摘要：按"节点→网关→NS"三段拆根因。覆盖：网关/NS 通信断、频段或调制参数（BW/SF/CR/LDRO）不一致、32 MHz 晶振精度（10 ppm）+ BGA 22 dBm 发热、DevEUI/AppEUI/AppKey 错配、DevNonce 重复致 NVM 重启后再入网失败。实战点：DevNonce 必须持久化到 NVM。
- 推荐：入主题笔记（"LoRa 节点入网 7 大根因"参考表）

### 5. Troubleshooting for LoRaWAN communication (Daviteq 16 项矩阵)
- 链接：https://daviteq.com/en/manuals/books/manual-for-lorawan-sensor/page/troubleshooting-for-lorawan-communication
- 摘要：按 LED 状态+现象倒推根因。覆盖：电池反插、I²C 噪声、RF 过热、ABP 计数器错乱、OTAA 未激活、磁开关失效、传感器 0xFF、电池<1.2V 启动循环、LoRaWAN 版本不匹配。实战点：LED 状态机 = 产线 debug 入口；ABP 计数器不重置 → 经典坑。
- 推荐：入主题笔记（"LoRa 节点 LED 状态机速查表"附录）

等你 review 后决定：激活 / 改写 / 丢弃
