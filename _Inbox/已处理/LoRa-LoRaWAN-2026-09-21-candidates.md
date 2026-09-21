# LoRa / LoRaWAN 候选素材 @ 2026-09-21 00:00

## 协议速览
- 是什么：Semtech Sub-GHz CSS 扩频物理层 + LoRaWAN MAC，组 LPWAN。
- 解决什么：电池供电、km 级远距、几十 B / 几天一发的 IoT。
- 跟 L4 主题关联：典型 IoT / 可穿戴边缘链路，跟「IOT 🥇」对齐，与 BLE/ZigBee 形成低功耗远距对照。

## 候选文章（4 条）

### 1. LoRa 技术详解：从扩频原理到 LoRaWAN 组网实战（CSDN）
- 链接：https://blog.csdn.net/weixin_29188043/article/details/165678387
- 来源：CSDN 实战博客
- 摘要：「几百亩农田 40+ 土壤节点、基站架管理房顶、最远 2.8 km」；SF/BW/CR 搭配、Class A/B/C 选型、ADR 启用后电池寿命翻倍；末尾 6 条「现场踩坑速查表」。
- 实战点：40+ 节点 / 2.8 km；链路预算 + Okumura-Hata（理想值 ×1/10~1/30）。
- 推荐动作：扩 deep-dive（「LoRaWAN 部署 7 条铁律」主题笔记）。

### 2. LoRa 模块通信丢包怎么办（亿佰特）
- 链接：https://www.ebyte.com/news/4903.html
- 来源：成都亿佰特官网（LoRa 模块厂商，E22 内置 FEC + LBT）
- 摘要：SF/功率对照（SF +1 → 灵敏度 +3 dB、距离 +20%、时间 ×2；22→33 dBm 功耗 1×→12×）；5 个 AT 指令优化。案例：「某工厂车间初始丢包 15%，天线引出 + LBT + 降速 + FEC + 2 次重传后降到 0.5% 以下」。
- 实战点：15% → 0.5% 工厂案例；「天线 > 速率 > LBT/FEC > 功率 > 重传」排查优先级。
- 推荐动作：写实战案例（「LoRa 工业丢包排查清单」L4 工具）。

### 3. LoRa 现场排雷：别让「远距离低功耗」成为丢包借口（TrueSight）
- 链接：https://tsight.io/articles/10718540
- 来源：TrueSight（工业 IoT 技术博客，针对矿井/变频器车间）
- 摘要：打脸「工业级模块」营销——80% 集成商在金属厂房连 500 m 都稳不住。4 件套：VNA 校准驻波比 < 1.5（距离 +30%）、TDMA 切断射频、Hopping Table 跳频、磁珠/LDO 抑制变频器纹波。
- 实战点：VNA + TDMA + Hopping + LDO「拒绝虚假开发」4 件套。
- 推荐动作：扩 deep-dive（「LoRa 工业部署 4 件套」主题笔记）。

### 4. LoRa 抗干扰性能怎么样（技象科技）
- 链接：https://www.techphant.cn/blog/107781.html
- 来源：技象科技（TPUNB 通信模块厂商）
- 摘要：CSS「低于噪声」解码（噪声 +20 dB 仍可解调，对比 FSK -8 dB）、FEC、SF 7~12。实测：硅谷 50 km 城市穿透；变频器车间 LoRa 稳而 Wi-Fi 失效。四大缓解：频谱感知 / 自适应 / 跳频 / Mesh。
- 实战点：LoRa vs FSK 抗噪 +20 dB vs -8 dB 极限。
- 推荐动作：入主题笔记（chips-com LoRa「原理 + 抗干扰」章节素材）。

## 下一步
等你 review：建议 1+2+3 → 「L4 实战」主题骨架；候选 4 作原理补强。