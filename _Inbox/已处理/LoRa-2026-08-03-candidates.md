# LoRa / LoRaWAN 候选素材 @ 2026-08-03 12:00

## 协议速览
- 是什么：基于 CSS 扩频的 Sub-GHz LPWAN + LoRa Alliance 标准化协议栈。
- 解决什么：电池设备公里级、海量节点、私有部署免流量费的远距离组网。
- 跟 L4 关联：IoT/可穿戴 ✅ 优先——能源/路灯/农业/资产追踪直接对应 ZeroZap 连接器。

## 候选文章（4 条）

### 1. Dragino LC01 LoRaWAN 智能路灯控制实战
- 链接：https://blog.csdn.net/weixin_33675507/article/details/85487534
- 来源：CSDN / Dragino 工程实战
- 摘要：LC01 继电器 + Class C 模式 + OTAA + The Things Stack + ThingsBoard 全链路，含 220V 接线、Payload Formatter 解码、Node-RED 自动化。
- 实战点：① 零线双线共接 IN N（最高发故障）；② FPort 1/2 + `06 01`/`06 00` 指令；③ 7 步故障排查表。
- 推荐动作：**扩 deep-dive**——Class C 继电器 + 220V 浪涌是高产线场景。

### 2. 工业排水 6km 远距离监测（ATMEGA328P + 太阳能）
- 链接：https://blog.csdn.net/weixin_33690367/article/details/92027406
- 来源：CSDN 工厂项目复盘
- 摘要：化工厂"零排放"合规，6 公里外 6+ 排水口水位 7x24 监测回控制室大屏。ATMEGA328P + 超声波 + GPS + LoRa，单点 < 100 美元，太阳能供电。
- 实战点：① 选型——为啥 LoRaWAN 不是 NB-IoT/GPRS/Zigbee；② 非视距抗树枝遮挡链路预算实测；③ 笔记本当简易网关的过渡方案。
- 推荐动作：**写实战案例**——拆 3 篇（选型/硬件/部署）。

### 3. 映翰通 EC312-LoRaWAN 工厂一站式方案
- 链接：https://blog.csdn.net/chshang1992/article/details/160875115
- 来源：CSDN / 映翰通工业级
- 摘要：一网关接电表 + 温湿度/漏水/烟感/门磁 + 电机震动；4G/Wi-Fi 多链路 + 双 SIM 冗余；边缘本地联动（风机/照明）。
- 实战点：① 零停产改造 + 远程运维；② 硬件+传输双加密；③ 数据驱动绿色工厂认证。
- 推荐动作：**入主题笔记**——"工厂 IoT 私有 LoRa"可复用到仓储/园区。

### 4. LoRaMac-node 源码深度解析（Semtech 协议栈）
- 链接：https://blog.csdn.net/weixin_29092787/article/details/155143786
- 来源：CSDN / LoRaMac-node
- 摘要：CSS 150dB 链路预算；MAC/PHY/Region/Utils 四层；`LoRaMacSend()` 加 MIC 加密 + RX1/RX2 定时；PAL 移植 SX1276↔SX1262；ADR 自适应。
- 实战点：① `LoRaMacRegionNvmUpdate(CN470)` 错频段违法；② NV 持久化用 EEPROM/SE 芯片；③ 移动设备关 ADR 锁 DR_5。
- 推荐动作：**扩 deep-dive**——写《LoRaMac-node STM32 移植实战》。

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃

**优先级**：A 必扩 → #1 + #4；B 入笔记 → #2 + #3。