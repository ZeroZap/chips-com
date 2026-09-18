# LoRa / LoRaWAN 候选素材 @ 2026-08-31 12:00

## 协议速览
- 是什么：sub-GHz CSS + LoRaWAN MAC，km 级低功耗 IoT LPWAN
- 解决什么：电池设备 km 级小包上报，免蜂窝月费
- 跟 L4 关联：IoT/可穿戴/产线监控主线

## 候选文章（5 条）

### 1. LoRaWAN Class C not working on Heltec
- 链接：https://github.com/jgromes/RadioLib/issues/1638
- 来源：GitHub RadioLib
- 摘要：2 层混凝土墙 Heltec Class C，地下室 RSSI -44/SNR -7.25，1 楼 -73/+12.5。RA08H 同条件正常。
- 实战：①RSSI/SNR 分层定位 RF 路径 ②关 CRC 逐包 log 区分 RF vs MAC ③排查必先 baseline 已知正常硬件
- 推荐：**扩 deep-dive**（RF 调试方法论+阈值表，入 L4）

### 2. the LoRa packet that arrived 45 minutes late
- 链接：https://moltbook.com/post/5e59d97b-36ba-456e-bb53-43c48e2a77bf
- 来源：Moltbook
- 摘要：SX1276 SF12 农场 bench OK，field 收 45 分钟前数据。追一天发现 RFM95W 因邻居同频冲突反复重传老包。
- 实战：①duty cycle + confirmed + 重试 → 诡异"陈旧数据" ②现场必问同频设备 ③bench/field RF 隔离需同频扫
- 推荐：**写实战案例**（紧凑，转 L4 案例笔记）

### 3. LoRa Network Failure Story: Debugging in the Field
- 链接：https://www.linkedin.com/posts/mashuk-e-lahi_iot-embeddedsystems-fieldengineering-activity-7471360772607021057-nVoH
- 来源：LinkedIn（WB IoT 复盘）
- 摘要：城市 40 节点空气监测 day 1 全在线 day 2 剩 24。4 个独立根因：城市 RF -60%、GSM 地面/楼顶差 3 格、2 颗传感器温度冲击校准漂移、1 块 PCB 冷焊点振动失效。
- 实战：①**多故障叠加**比单点常见 ②现场调试 = 万用表+硬件+经验 ③设计考虑运输/振动/温度对校准影响
- 推荐：**入主题笔记**（"多故障叠加"，入 L4 调试方法论）

### 4. IoT Failure Post-Mortems — Smart Farm Case
- 链接：https://iotclass.org/testing-validation/iot-deployment-failure-case-studies.html
- 来源：iotclass.org
- 摘要：$15万/8月/200 土壤湿度 500 acres，W3 60% 离线 W6 废弃。根因：丘陵 RF 阴影+玉米 8ft 吸 RF+单网关无冗余+SF7 硬编码无 ADR。
- 实战：①vegetation/季节动态影响链路预算 ②ADR 必须开（硬编码 SF 是最大反模式）③单网关 = 单点故障搬到现场
- 推荐：**扩 deep-dive**（农业/林业 LoRa checklist + 修复代码，入 L4 案例）

### 5. LoRa Reliability Improvement MDPI §6.2
- 链接：https://www.mdpi.com/2079-8954/14/5/515
- 来源：MDPI Systems
- 摘要：SME 工厂 LoRaWAN 接收率 33%。pipeline 分段发现 98-99% 失败在 parser 之前 = confirmed 依赖 ACK + 信道有限 + rejoin 异常。修后 33%→95%。
- 实战：①**pipeline 分段差异**比端到端 metrics 易定位 ②confirmed + 有限信道 → 自我恶化 ③修套餐 = 减 confirmed + 扩信道 + rejoin + 调参
- 推荐：**入主题笔记**（LoRaWAN 数据可靠性方法论，入 L4）
