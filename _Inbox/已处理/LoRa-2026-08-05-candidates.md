# LoRa / LoRaWAN 候选素材 @ 2026-08-05 00:00

## 协议速览
- 是什么：Sub-GHz CSS 物理层（LoRa）+ MAC 层协议（LoRaWAN），星型拓扑+多信道网关
- 解决什么：电池供电设备公里级低速率通信（电池 5-10 年），水表/农业/工业监控
- L4 关联：IoT/可穿戴方向核心 LPWAN，ADR/干扰/移动性是高频坑点

## 候选文章（5 条）

### 1. 工业物联网 LoRaWAN 控制终端应用与配置指南
- 链接：https://blog.csdn.net/weixin_42608299/article/details/160723371
- 来源：CSDN / DFRobot DFR1120 工业终端实战
- 摘要：DIN 导轨式终端（89×53×24mm），EU868/US915 双版，OTAA/ABP+Class A/C 完整协议栈，视距 4km；SX1276 + 光耦隔离 5-24V 数字输入 + 0-10V/15bit 模拟输入
- 实战点：工业 EMC 设计；频段双版法规风险；模拟精度+抗扰要求
- 推荐：写实战案例（智慧工厂/工业监控产品形态）

### 2. LoRaWAN 终端源码深度解析（LoRaMac-node）
- 链接：https://blog.csdn.net/weixin_29092787/article/details/155143786
- 来源：CSDN 深度技术博客
- 摘要：拆解 Semtech 官方 LoRaMac-node 协议栈（STM32/ESP32 移植），MAC/PHY/Region/Utils 四层；详解帧组装、Class A 节能、Class B Beacon 时隙、AdrLinkComputeNextDataRate() 调速
- 实战点：AES-CBC+CMAC-MIC 安全链路；Class A/B/C 功耗-时延权衡；PAL 抽象跨 STM32/ESP32/nRF52；移动场景关 ADR
- 推荐：扩 deep-dive（LoRaMac-node 移植、ADR 工程参数）

### 3. 工业 4.0 通信利器：LoRa 扩频技术适配复杂工业场景
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_2206a10030807952
- 来源：腾讯企鹅号
- 摘要：对比 Wi-Fi/ZigBee 在金属密集+强电磁环境的劣势；LoRa CSS 170dB 链路预算（SF12 时 -19.5dB 仍可解调），啁啾占满信道对频率选择性衰落天然免疫
- 实战点：金属多径（啁啾跨短时脉冲干扰）；CSS 宽带分散+匹配滤波抑窄带；普通晶振也稳
- 推荐：入主题笔记（LoRa 抗干扰物理层 + 工业场景适配）

### 4. LoRaWAN 核心特点之 ADR 机制详解
- 链接：https://zhuanlan.zhihu.com/p/113746989
- 来源：知乎专栏
- 摘要：详解 ADR——NS 提速（基于 RSSI/SNR 缓存 LinkADRReq 逐级下发）+ 节点降速（Confirm 帧 2 包无 ACK 自动降一档，Unconfirm 帧靠 ADRACKReq 轮询）
- 实战点：NS 提速 vs 节点降速双向机制；Power/DR/Channel mask ACK 任一为 0 即拒绝；静态 vs 移动节点 ADR 差异
- 推荐：写实战案例（NS 侧 ADR 调参、移动场景降速踩坑）

### 5. LoRaWAN ADR 算法简介及最新研究方向
- 链接：https://blog.csdn.net/HowieXue/article/details/127832765
- 来源：CSDN 综述
- 摘要：综述 ADR 演进——基础 NS vs 商业（利尔达 Unicore 3.0）实现差异；研究热点 4 方向：算法优化/评估/数据分析/其他
- 实战点：Semtech 官方仅给 EU868 简单建议；商业 NS（TTN/Helium/ChirpStack）实现差异巨大
- 推荐：跳过（综述性强深度不够；除非做 ADR 算法对比主题）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
<mavis-progress>idle</mavis-progress>
