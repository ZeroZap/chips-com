# LoRa / LoRaWAN 候选素材 @ 2026-08-24 00:00

## 协议速览
- 是什么：LoRa（CSS 物理层）+ LoRaWAN（MAC/网络层），sub-GHz ISM（EU868/US915/CN470/AS923）LPWAN
- 解决什么：电池传感器数 km 距离、低速率（0.3-50 kbps）周期上传少量遥测
- 跟 L4 主题的关联：IoT/工业传感主流远距低功耗链路；regional profile + 频段子带 + DevNonce/DevEUI 派发是高频实战坑

## 候选文章（3 条）

### 1. Resolving LoRaWAN Join-Storms — 真实故障排查
- 链接：https://www.concept13.co.uk/news/lorawan-join-storm/
- 来源/摘要：Concept13 英文 case study。欧洲物管公司数千 LoRaWAN 传感器密集部署，shared AppKey + 每网关自跑 LNS island + 繁重 Node Red 叠加，**packet loss 飙到 80%**，系统"自激振荡"
- 关键实战点：① 单项小问题叠加触发 Join Storm 雪崩 ② 集中式云端 LNS 单点最大改进（恢复 >80%） ③ 25 项颜色编码改进清单可作部署 checklist
- 推荐动作：**扩 deep-dive**（密集部署"自激振荡"模型教学价值高）

### 2. Why IIoT PdM Fails in Year Two — 多真实工厂反思
- 链接：https://techeasily.co.uk?p=10793/
- 来源/摘要：EasyNet 工程团队博客。反驳"AI 不行"——**真问题是网关上行断电致 AI baseline 漂移**。3 真实工厂：West Midlands 汽车件（VFD 干扰）、Rotterdam 冷库（夹芯板无覆盖）、Birmingham 食品加工（9h 断网 → 2 周 false positive 激增 → 团队失信）
- 关键实战点：① Pilot 与产线环境差异（VFD EMI/冷库/高度差）是部署杀手 ② 12h 断网 = 时序断裂 = AI baseline 漂移 = 信任崩塌 ③ 双 SIM 故障转移 + 本地缓冲保 sequence 连续
- 推荐动作：**入主题笔记**（IIoT 长期部署"非技术性失败"维度）

### 3. STM32WL LoRa 节点入网失败问题分析 — 中文实战
- 链接：https://www.eet-china.com/mp/a255088.html
- 来源/摘要：电子工程专辑 ST 中文应用笔记。STM32WL + RAK2287 + Loriot 下 OTAA 入网失败 4 大根因：① 网关-NET 通信 ② 节点-网关 RF（频段/BW/SF/LDRO/RF 性能） ③ 参数不匹配 ④ DevNonce 重复
- 关键实战点：① SF=11/12 时 STM32WL 例程默认开 LDRO，**网关不开 LDRO 必失败** ② BGA 22 dBm Tx 持续工作 PCB 发热 → 32 MHz 晶振温漂 → 灵敏度劣化 ③ DevNonce 与 AppEUI 绑定，**重复 = 永远被 NS 忽略**
- 推荐动作：**入主题笔记 + 实战案例**（中文工程语境，CN470 子带配置直接可用）

## 下一步
等你 review。建议激活优先级 #1（Join Storm 雪崩）+ #2（Year Two 失败反思）+ #3（中文 STM32WL）
