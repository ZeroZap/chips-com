# LoRa/LoRaWAN 候选素材 @ 2026-09-30 00:00

## 协议速览
- 是什么：Semtech CSS 扩频（LoRa 物理层）+ LoRaWAN MAC
- 解决什么：免许可 ISM、uA 休眠、km~10km、低速率 LPWAN
- 跟 L4 关联：L4 实战坑经典场——实验室 OK 产线挂；SF/BW/CR + 天线/频点取舍必修课

## 候选文章（5 条）

### 1. 复杂工厂 LoRa 模块抗干扰实测与部署指南
- 链接：http://www.wmrh.cn/news/15487
- 来源：尧图网络
- 摘要：CNC+变频器+焊机车间三组 SF 实测——SF7 变频器旁丢包 35%、SF12 三点 <0.5%；三步干扰定位+4 工程坑。
- 实战点：①变频器 IGBT 抬 470-510MHz 底噪 20dB；②SF12 占空长挤并发；③金属柜放网关=屏蔽死
- 动作：扩 deep-dive（SF/BW/CR 取舍 + 工业干扰源）

### 2. The Real Challenges of Deploying a LoRaWAN Network
- 链接：https://www.macnman.com/success-stories/blogs/lorawan-deployment-challenges
- 来源：Macnman
- 摘要：万级扩容 6 挑战——Provisioning、FUOTA、监控/backhaul、干扰、ADR、Class A/B/C。
- 实战点：①FUOTA 受 1% duty cycle 限，10k 节点更新拖几周；②RSSI 够+SNR 差=干扰；③Class A 下行窗口="不能做控制"根因；④实测 460 节点×10 包/天=单网关容量。
- 动作：写实战案例（FUOTA + 大规模 onboarding）

### 3. 踩过 LoRaWAN 坑后,工厂换成私网 LoRa
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_3356a8e8e0413252
- 来源：腾讯搜一搜/DreamLNK
- 摘要：精密厂老周 3 翻车——看板卡死、工单卡壳、跨网持续付费；改私网 LoRa，秒级联动+数据不出厂。
- 实战点：①"标准≠适合"——小范围园区 LoRaWAN 不如私网；②NS 运维锁三方；③决策三问=数据去哪/谁运维/规模多大。
- 动作：入主题笔记（公网 vs 私网决策树）

### 4. LoRa Network Planning and RF Site Surveys
- 链接：http://rfengineer.net/rf-engineering/lora-network-planning-rf-site-surveys
- 来源：RF Engineer Network
- 摘要：3 真实部署——12 km² 智慧城市（4 网关避 902MHz FSK）、15000 英亩农业（ADR 关换静态 SF9 PDR 99.2%）、180km 油气管道（10dBi Yagi 30km 间隔）。
- 实战点：①902MHz SCADA FSK 干扰→切 915-928MHz；②ADR pilot 收敛不稳→关掉；③近-远靠 ADR+功率控制。
- 动作：扩 deep-dive（频谱规划 + ADR 取舍 + case 数据集）

### 5. Monitoring Compressed Air with LoRaWAN Solution
- 链接：https://www.advantech.com/zh-tw/resources/case-study/monitoring-compressed-air-with-lorawan-monitoring-solution
- 来源：Advantech 研华
- 摘要：钢铁厂 3 空压站——SUTO+Modbus/RTU→WISE-2200→WISE-6610→Node-RED→S4M；金属密集 300-400m 稳定，单网关 500 点。
- 实战点：①Modbus/RTU+LoRaWAN 串接架构；②Node-RED 边缘预处理；③金属密集厂区 300-400m 是实际部署上限。
- 动作：写实战案例（钢铁/化工工业级参考架构）

下次：CAN FD/XL（24h 三协议已占）。等 review：激活/改写/丢弃