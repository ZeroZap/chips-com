# ZigBee 候选素材 @ 2026-09-13 00:00

## 协议速览
- 是什么：IEEE 802.15.4 低功耗 mesh，2.4 GHz / 250 kbps
- 解决什么：IoT 自组网、低功耗传感，成本低续航长
- 跟 L4 关联：智能家居/工业传感/智能照明主流，ZigBee 3.0 仍是嵌入式组网主力

## 候选文章（5 条）

### 1. Zigbee 工业组网：当"自愈"变成"自杀"
- 链接：https://tsight.io/articles/12807223
- 来源：tsight.io（工业 IoT 工程博客）
- 摘要：化工厂传感网关凌晨 3 点频掉，频谱仪抓金属罐体多径致 MAC 重传风暴，触发"鬼影"离网广播雪崩
- 实战点：①多径→重传→父节点判丢失→雪崩 ②工业高温 PCB Dk 漂移致天线谐振偏移 2 MHz+ ③节点 >30-50 触发路由表溢出
- 推荐：扩 deep-dive（ZigBee 工业 vs LoRa 选型对比）

### 2. Zigbee assessment in industrial environments
- 链接：https://cubexgroup.com/?p=8606/
- 来源：Cubex Group（工业安全研究博客）
- 摘要：工业 ZigBee 渗透——Python high-level + Zephyr C 固件跑 MAC ACK 解时序；私人 profile (0x00) vs ZigBee Pro (0x02) 不兼容致加入失败
- 实战点：①Python 协议栈慢到 ACK 超时 ②Update ID 跨厂商行为未定义 ③nRF52840+Zephyr 跑 MAC 才是工业可行解
- 推荐：入主题笔记（IoT 协议栈 C/Python 混合调试架构）

### 3. My Zigbee mesh healed itself into a 40-hop loop
- 链接：https://moltbook.com/post/bdb6fd62-6fe5-4617-b3ae-c72cbe66b225
- 来源：moltbook 工程师实战帖
- 摘要：仓库 30 端点+8 router，测试完美，一周后现场 3 秒延迟。路由贪 LQI 不贪跳数，6 跳"便宜"但物理荒谬；减 router+网格化回 1-2 跳
- 实战点：①"dense ≠ robust" ②LQI 路由的诡异均衡 ③稀疏可推理拓扑 vs 密集但不可预测
- 推荐：写实战案例（mesh 选型反直觉教训）

### 4. Zigbee Module PCB Signal Problems: Stop Blaming the RF Chip First
- 链接：https://www.sprintpcbgroup.com/fi/blogs/zigbee-module-pcb-signal-integrity-hdi-stackup-antenna/
- 来源：SprintpcbGroup（PCB 厂博客）
- 摘要：HDI 板厂焊后离子残留→湿度下 PCB 漏电→ZigBee 休眠 2μA 飙 20μA+；换可信赖板厂后 72h 湿度箱稳；LDO 瞬态+32.768kHz 晶振 ESR 都偷 1μA
- 实战点：①离子残留是隐形寄生电阻 ②LDO 动态响应 > 静态电流 ③晶振负载电容失配延长启动功耗
- 推荐：扩 deep-dive（嵌入式低功耗 PCB 制造 Checklist）

### 5. JN5169 ZigBee 模块开发实战：从硬件设计到协议栈应用
- 链接：http://www.wmrh.cn/education/21211.html
- 来源：wmrh.cn（无线模组技术博客）
- 摘要：NXP JN5169 选型（M00/M03/M06 天线）+ PCB 布局+回流焊工艺+批量产线踩坑
- 实战点：①M00 外置天线 vs 金属外壳 ②邮票孔半孔钢网"内切外延" ③回流焊峰值/TAL 严格符合规格
- 推荐：入主题笔记（NXP ZigBee 量产经验合集）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
