# LoRa 候选素材 @ 2026-08-30 00:00

## 速览
- Sub-GHz Chirp Spread Spectrum + LoRaWAN MAC，免许可 ISM 频段
- 解决：电池终端数公里级低速率回传（农业 / 抄表 / 资产追踪 / 工业 sensor）
- 跟 L4 关联：边缘 sensor 链路兄弟层；实战失败模式密度最高

## 候选

### 1. 22 IoT Deployment Failure Post-Mortems（Case 1 农业）
- 链接：https://iotclass.org/testing-validation/iot-deployment-failure-case-studies.html
- 来源：iotclass.org
- 摘要：200 土壤湿度 sensor 6 周放弃。Root：平地藏 RF 路径、玉米 8 英尺吃 20dB、单 gateway 无冗余、SF7 硬编码丢 ADR
- 实战点：lab 跟 field RF 差（地形+季节）；真 ADR retry [7,9,11,12]；单 gateway=SPOF
- 推荐：**入 L4 deep-dive** → 扩成「LoRaWAN 部署前必查清单」

### 2. 工厂从 LoRaWAN 换私网 LoRa（踩坑三连）
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_3356a8e8e0413252
- 来源：企鹅号 / DreamLNK
- 摘要：精密制造厂三次翻车：凌晨看板卡十几分钟（数据绕公网）、NS 升级开工单等半天、跨网接入持续付费 → 换私网 LoRa + 边缘盒子秒级
- 实战点：LoRaWAN 配 public NS 隐形成本；NS 升级锁死运维
- 推荐：**入主题笔记** → 跟工控/楼宇对位，作 L4 选型决策树分叉

### 3. the LoRa packet that arrived 45 minutes late
- 链接：https://moltbook.com/post/5e59d97b-36ba-456e-bb53-43c48e2a77bf
- 来源：moltbook.com
- 摘要：SX1276+SF12 bench 全过；现场数据晚 45 分钟。真相：邻居气象站 800m 同频，gateway ACK 延迟 → node retry 把旧包按原时间戳重传
- 实战点：bench 跟 field 差在 RF 隔离；ACK 依赖型 confirmed uplink=数据新鲜度错位（非丢包）
- 推荐：**入 deep-dive** → 跟 #1 合成「LoRaWAN 现场调试两个必查表」

### 4. LoRaWAN in the wild
- 链接：http://echolo.io/journal/lorawan-in-the-wild
- 来源：echolo.io
- 摘要：水产/远程农业/钢混 yard 实战数字：开放农田 6-8 mi、林地 1-3 mi、钢混 200-600m；2×AA 锂电实测 2-3 年（非 spec 10 年）；DO<3mg/L 鱼几分钟内死
- 实战点：gateway 数=worst-case terrain 决定；电池瓶颈是 sample interval+payload
- 推荐：**扩实战案例集** → 作 chips-com 实战层引用基线

### 5. LoRa Reliability Improvement 33%→95%（MDPI §6.2）
- 链接：https://www.mdpi.com/2079-8954/14/5/515
- 来源：MDPI
- 摘要：工厂周期采集接收率掉 33%。分段定位（gateway 可见 vs parser 持久化）→ ACK 依赖型 confirmed uplink + 活跃信道不足 + stale device state。修后 95%
- 实战点：**分段定位法**=端到端症状拆相邻段差异；confirmed-mode 在周期上报是反向债务
- 推荐：**入 deep-dive** → 升华为「LoRaWAN 生产故障定位 SOP」，跟 BareOS AT 自检同思路

## 下一步
等 review。优先 #1+#3+#5 入 deep-dive，#2+#4 中文旁证。
