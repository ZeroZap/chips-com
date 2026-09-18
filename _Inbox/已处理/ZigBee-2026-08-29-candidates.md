# ZigBee 候选素材 @ 2026-08-29 12:00

## 协议速览
- 是什么：基于 IEEE 802.15.4 的低功耗 Mesh（2.4GHz，16 信道，250kbps）
- 解决什么：智能家居/工业传感"电池用几年+几百节点稳定组网"
- L4 关联：IoT 主力；覆盖产线掉线/工业干扰/安全渗透/芯片选型

## 候选文章（5 条）

### 1. Zigbee 工业组网:当"自愈"变成"自杀"
- 链接：https://tsight.io/articles/12807223
- 来源：TrueSight
- 摘要：化工厂凌晨 3 点无线网关频繁掉线真案。金属罐体多径效应触发 MAC 重传风暴，父节点广播离网，雪崩式瘫痪。
- 实战点：(1) Dk 温漂 2MHz→VSWR→PA 发热闭环；(2) 50ms 控制+30+ 节点=Zigbee 边界；(3) 替代：LoRaWAN/TSN
- 推荐：扩 deep-dive（MAC 重传+雪崩模型）→ 入主题笔记

### 2. Zigbee assessment in industrial environments
- 链接：https://mgicomputers.com/tech-news/turn-me-on-turn-me-off-zigbee-assessment-in-industrial-environments
- 来源：MGI Computers
- 摘要：工业 ZigBee 安全+调试。nRF52840 刷 Zephyr 协调器做 stack profile 差异测试，Python+Scapy 重组 APS。
- 实战点：(1) 同一 EPID 高 Update ID beacon 攻击；(2) Python 协调器 ACKs 太慢掉线；(3) 私用 profile 改不动只能换固件
- 推荐：扩 deep-dive（Zigbee 安全攻防+抓包工具链）

### 3. IIoT ZigBee-Based WSN in Solar Protection Curtains Workshop
- 链接：https://www.mdpi.com/1424-8220/24/2/712/html
- 来源：MDPI Sensors（西班牙 Galeo 工厂真部署）
- 摘要：5 工位+ERP ZigBee WSN。每节点 10000 包/2h，活动+休息 PER 0.00%；48h 实测含 worker ID / 工单 / heat-welding 时长。
- 实战点：(1) 工业 ZigBee PER 0% 真部署；(2) 加密按公司策略可切；(3) 工位×产品×员工三角分析
- 推荐：写实战案例笔记（产线 WSN 部署 checklist）

### 4. ZigBee PRO 通信控制器芯片：选型、协议栈与实战指南
- 链接：http://www.hqwc.cn/news/1369328.html
- 来源：hqwc.cn 实战长文
- 摘要：CC2652R vs EFR32MG21 vs JN5189 横评。Z-Stack vs ZBOSS 移植、UART/SPI 外接 NCP、install code 入网。
- 实战点：(1) flip chip 封装对 PCB 层数强制；(2) End Device timeout > poll 周期才不掉线；(3) PHY 250kbps vs 应用层 30-60kbps
- 推荐：入主题笔记（芯片选型+协议栈对比表）

### 5. SmartSpace: Debugging Python ZigBee Networks with zigbee2mqtt
- 链接：https://www.johal.in/debugging-python-zigbee-networks-with-zigbee2mqtt-and-wireshark-3
- 来源：johal.in（SmartSpace 三层楼 90 天实测）
- 摘要：3 楼 Wireshark 抓包+Python 监控。LQI 阈值 80/40、Retrans 5%/15% 报警。90 天：诊断 4.2h→8min（-96.8%）、月停机 47h→3.2h（-93.2%）。
- 实战点：(1) LQI<80 重传率指数上升；(2) 100ms vs 10s 误配致拥塞；(3) $2400+80h 集成→年省 $18k（7.5x ROI）
- 推荐：扩 deep-dive（zigbee2mqtt+Wireshark 阈值表）→ 入笔记

## 下一步
等你 review：激活/改写/丢弃
<mavis-progress>idle</mavis-progress>
