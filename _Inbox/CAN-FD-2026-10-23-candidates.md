# CAN FD / CAN XL 候选素材 @ 2026-10-23 12:00

## 协议速览
- 是什么：ISO 11898-1:2015，仲裁段 500k、数据段最高 8M（BRS），单帧 64B
- 解决什么：CAN 2.0 单帧 8B 在诊断/雷达/以太网 offload 场景带宽不够
- 跟 L4 主题的关联：已有 `bus/can-fd-failure-cases.md`（133 例）；本批补的是**温度-电容-边沿速率**与**混合总线兼容性**两条现有笔记未见根因

## 候选文章（3 条）

### 1. 400 纳秒边沿速率缺陷如何造成 1.5 万美元的幽灵 ECU 索赔
- 链接：https://obd-cable.com/?p=4510/
- 来源：OBD 线缆厂技术博客（含实测数据）
- 摘要：6 周 63 起车队索赔，返厂件全过室温台架测试。根因是 OBD 线缆让差分上升沿慢 400ns；5Mbps 位周期仅 200ns，65℃ 舱温时总线电容超收发器额定 18%，采样窗口塌陷 → 位错。
- 关键实战点：
  1. 边沿速率 = 收发器驱动能力 vs 寄生电容，跟线缆 DC 特性无关；直通/绝缘测试全过
  2. 三相失效：23℃ 眼图干净 → 15-20min 介电常数漂移 → 65℃ 越阈值，错误计数器先归零后爆发
  3. 产线对策：全温域眼图 + 统计抽样 QC；投入 $40k vs 三年索赔敞口 $250k
- 推荐动作：**写实战案例**（可直接扩一条 FC：温度-边沿速率-幽灵索赔）

### 2. CAN FD Tq 采样点时序稳定性与物理层失效分析指南
- 链接：https://tsight.io/articles/20435950
- 来源：TrueSight 技术文
- 摘要：采样点配 80% 偏早，信号未稳定即采样，连续 CRC error；解法是加长 Prop_Seg 把采样点后移到 75%。强调软件填的百分比只是理论值，真实位置还取决于 fosc、分频比、阻抗匹配。
- 关键实战点：给出分速率推荐区间（500k 仲裁 80-87.5% / 2M 数据段 70-80% / 5M 数据段 60-70%）；RC 振荡器 ±0.5% 才够 1Mbps；MCAN 数据段 SJW 可到 128 TQ
- 推荐动作：扩 deep-dive（采样点速查表 + STM32 FDCAN NBTP 算例）

### 3. 别把 CAN FD 当成"加了油的 CAN 2.0"：量产项目避坑指南
- 链接：https://tsight.io/articles/20271656
- 来源：TrueSight 技术文
- 摘要：BRS 切换后高温下采样点落进跳变区触发 Error Frame；64B payload 靠轮询/高频中断会在 70% 负载下打爆 CPU；混合总线开 BRS 等于对 CAN 2.0 节点发格式错误。
- 关键实战点：混合总线必须提速只能走 Gateway 协议转换，禁止物理并联；DMA + 环形缓冲是量产硬门槛
- 推荐动作：写实战案例（兼容性反模式）

## 备选（偏教程向，未展开）
- CAN FD 物理层陷阱与实时性崩塌（TEC/REC>127 失总线控制权）— https://tsight.io/articles/19672646
- Baud Mismatch 未必 Bus Off — https://industrialmonitordirect.com/pl/blogs/knowledgebase/can-fd-baud-mismatch-error-passive-not-always-bus-off/
- CAN XL 选型（补 CAN FD 与以太网空白）— https://www.icanic.cn/news/10267.html

## 下一步
等你 review：激活 / 改写 / 丢弃。建议优先 #1（唯一带完整数据链的量产根因）。