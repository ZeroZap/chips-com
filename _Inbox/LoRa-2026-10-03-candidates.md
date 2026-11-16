# LoRa 候选素材 @ 2026-10-03 00:00

## 协议速览
- 是什么：基于 Chirp 扩频的 LPWAN，LoRaWAN 是其 MAC 协议
- 解决什么：公里级覆盖 + 电池级功耗 + 免 SIM 的"小数据长距离"
- L4 关联：IoT/可穿戴接入层；"实验室 OK、产线翻车"是核心

## 候选文章（5 条）

### 1. 基于 LoRaWAN 的智能能源系统实践
- 链接：https://www.sheratonhq.com/news/80827
- 来源：行业 blog（中文长文）
- 摘要：350→420 点抄表实战：选型 + ChirpStack + 上线 3 月 P0（半信道网关打满 + DB 池耗尽 + ADR 全 SF7 撞车）+ FUOTA 升级坑。
- 实战点：①ADR 节点密集压 SF7 撞车须强制最小 SF；②FUOTA 须 Class C 收包电池风险高；③半信道/全信道是 500 节点分水岭。
- 推荐：**扩 deep-dive**

### 2. LoRaWAN 网关容量估算：从 8 路解调到实战
- 链接：https://blog.csdn.net/weixin_29168153/article/details/165503419
- 来源：CSDN 工程师实战长文
- 摘要：拆 SX1301/1302 8 路解调本质 + 0.3 效率系数公式 + 3 案例：3000 井盖丢包 15%（4 频点+默认 SF12）、养老院 SOS 卡顿（ACK 挤占）、2000 农业远端 SF12 拖垮。
- 实战点：①8 路解调≠同时 8 包看空中时间；②多网关去重放大 5~10×；③频谱仪扫底噪 > 理论计算。
- 推荐：**扩 deep-dive**

### 3. 深夜排障：工业 LoRaWAN 链路失效物理诱因
- 链接：https://tsight.io/articles/13242120?lang=zh
- 来源：TrueSight 技术 blog
- 摘要：冷库 EM300-TH 掉线：开阔正常、挂墙 RSSI 跌 -120dBm，多径相消；"加功率=抬底噪=恶化"反直觉；给天线极化 45°、SF 下调、磁环隔离 3 加固。
- 实战点：①多径 RSSI 尚可 SNR 低=停调功率转极化；②睡眠周期与 RX1 漂移致盲听；③电池内阻老化发送瞬间跌穿。
- 推荐：**写实战案例**

### 4. Hot Take: LoRaWAN Is Overkill for Factory IoT
- 链接：https://johal.in/hot-take-lorawan-is-overkill-factory-iot-use
- 来源：Johal.in（含代码）
- 摘要：12 工厂 + 500+ 节点实测：ADR 在 RSSI 抖动 20dB 场景 30 天内 34% 节点锁死 SF12，电池 -22%、延迟 +10×；给 disable_adr() 代码。
- 实战点：①ADR 是工厂负债须禁；②固定 SF7/8+预勘测才正解；③Sigfox free keep-alive 比 LoRaWAN 心跳便宜。
- 推荐：**写实战案例**

### 5. LoRaWAN Downlinks Always in RX2
- 链接：https://industrialmonitordirect.com/es/blogs/knowledgebase/lorawan-downlinks-always-in-rx2-diagnosing-rx1-loss
- 来源：Industrial Monitor Direct KB
- 摘要：诊断 Class A 下行总落 RX2 不进 RX1。"故意调度"vs"时序缺陷"：SF12 上行强制 SF12 下行（1.16s vs SF9 的 0.165s，7× 网关占用）。含 T_sym/T_payload 公式。
- 实战点：①SF12 上行=下行 1.16s + 115s 黑窗；②RX1DROffset 是排查起点；③别"修"它，把上行 SF 降下来。
- 推荐：**入主题笔记**

## 下一步
等你 review：激活 / 改写 / 丢弃
