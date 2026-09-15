# ZigBee 候选素材 @ 2026-09-14 00:00

## 速览
- 是什么：IEEE 802.15.4 低功耗 Mesh，2.4 GHz
- 解决：智能家居/工业传感节点低功耗自组网
- L4 关联：IoT/可穿戴主攻方向，ZigBee 产线坑是知识库薄弱环节

## 候选（5 条）

### 1. 化工厂凌晨掉线：金属多径触发 MAC 重传雪崩
- 链接：https://tsight.io/articles/12807223
- 来源：tsight.io
- 摘要：化工厂网关凌晨频掉线，频谱抓到金属罐体多径→Jitter→MAC 重传→离网广播雪崩，整网秒级瘫。
- 实战点：①重传+广播放大是工业头号故障 ②>30-50/网关路由表溢出 ③金属/实时>50ms/高密度改 LoRaWAN/TSN
- 推荐：扩 deep-dive（"工业 ZigBee 选型边界"主题）

### 2. 50 设备从混沌到树形：CPU 瓶颈+协调器角落双坑
- 链接：https://sudonull.com/zigbee-network-is-unstable-diagnosing-50-devices
- 来源：sudonull.com
- 摘要：50 设备丢命令/3s 延迟。根因非 RF：Wiren Board CPU 380-400% 过载+协调器角落放置。改树形+Sonoff Dongle E (EFR32MG21)+Pi5+z2m v2.9.2 解决。
- 实战点：①CPU 过载伪装成无线问题 ②树形比纯 Mesh 稳 ③EFR32MG21 比 CC2652P 拥挤 2.4G 稳
- 推荐：写实战案例（"L4 规模天花板"笔记）

### 3. 产线 ionic residue：睡电流 2μA→几十μA
- 链接：https://www.sprintpcbgroup.com/fi/blogs/zigbee-module-pcb-signal-integrity-hdi-stackup-antenna/
- 来源：SprintPCB（真实产线案例）
- 摘要：模块小批量 OK 量产睡电流异常，半月查 HDI 板厂焊后离子残留，湿度一升形成隐性导电通道。
- 实战点：①板厂 cleanliness 比芯片选型更影响睡电流 ②LDO 看 load transient 不看静态 ③晶振 ESR 偏差 1μA 起步
- 推荐：入主题笔记（补"低功耗 IoT 产线"盲区）

### 4. 仓库 30+8 节点"40 跳自愈死结"
- 链接：https://moltbook.com/post/bdb6fd62-6fe5-4617-b3ae-c72cbe66b225
- 来源：moltbook.com
- 摘要：30 end+8 router+1 coord 仓库，部署一周部分节点 3s 延迟。路由基于 LQI 贪心不看跳数；router 太密让算法自优化成 6-hop 荒谬路径。删一半 router 改网格，路径塌回 1-2 跳。
- 实战点：①dense ≠ robust ②ZigBee 路由只看 link cost ③稀疏可推理 > 密集推不出
- 推荐：入主题笔记（"mesh 路由陷阱"小专题）

### 5. Hubitat 反复重启：FF01 cluster 毫秒级同步广播击垮协调器
- 链接：https://community.hubitat.com/t/at-my-wits-end-all-of-my-zigbee-devices-are-constantly-rebooting/164098
- 来源：Hubitat 社区
- 摘要：毫秒级同步多 thermostat/I/O 广播 FF01 私有 cluster→协调器 buffer overflow→radio offline→子节点 panic 重启。修：错峰上报+物理拔插。
- 实战点：①同毫秒同步上报是协调器头号杀手 ②私有 cluster 流量难预测 ③软件重启不复位 radio
- 推荐：入主题笔记（"ZigBee 大规模部署运维"片段）

## 下一步
review 后激活/改写/丢弃；1/2/5 扩 L4 主题，3 补产线盲区，4 独立小专题
