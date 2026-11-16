# LIN 候选素材 @ 2026-11-04 00:00

## 速览
- 是什么：ISO 17987 单线车载低速总线，10/20 kbps，单主多从。
- 解决什么：最低成本把车窗/座椅/雨刮挂上车身网络，替代 CAN。
- L4 关联：非 IoT 主线，但为轮转表最后一个未服务协议，补完即 12 协议全覆盖。

## 候选（5 条）

### 1. Pico 实测：2015 极光发电机 LIN 故障
- 链接：https://hongtronics.com/en?p=69023
- 来源：虹科 / Pico Auto
- 摘要：Pico 序列解码见 ID=11 只有帧头无应答、ID=E9 齐全，GWM 存 P0A1A-87。
- 实战点：拆发电机 C1DC14C 波形不变 → 从机节点本体坏，非线束；换件后 ID=11 恢复应答。
- 动作：写实战案例（failure-cases 首条）

### 2. 三菱 U1570/U1515 LIN 无总线活动诊断流程
- 链接：http://mitsubishi.automotive-manuals.com/imiev-2011/M154510540023300ENG.html
- 来源：三菱原厂维修手册
- 摘要：故障树＝ETACS 坏/从机坏/LIN 对电源短路/对地短路，6 步量测。
- 实战点：拆连接器测对地电压，表针不动正常、恒定值＝对电源短路；对地电阻 ≥1 kΩ 判正常；断从机后改报 U1500 属正常。
- 动作：写实战案例（物理层量测 SOP）

### 3. 车载 LIN 主从通信代码设计与量产踩坑
- 链接：https://blog.csdn.net/weixin_29192211/article/details/164740668
- 来源：CSDN（量产项目）
- 摘要：主机 1/10 ms 定时中断推进调度表，三层架构。翻车点＝调度表、唤醒条件、校验和类型混用。
- 实战点：通信矩阵是地基，用 DBC/LDF 生成调度表；低优先帧留空闲槽，防超时拖垮整表；从机可用内部 RC 振荡器。
- 动作：扩 deep-dive（新建 lin-deep-dive.md）

### 4. LIN 休眠唤醒测试避坑：主节点丢失 / 预休眠
- 链接：https://blog.csdn.net/weixin_29663861/article/details/161988086
- 来源：CSDN（台架测试）
- 摘要：某 OEM 统计 42% 的 LIN 节点测试异常源于非标休眠实现，此两类占 68%。
- 实战点：供应商私加"1 s 无主节点通信即休眠"→ 测试假故障；规范休眠仅显式 Go-To-Sleep 与总线空闲 4-10 s。
- 动作：写实战案例（休眠唤醒独立成节）

### 5. 示波器抓取并解析 LIN 数据帧
- 链接：https://blog.csdn.net/weixin_33691817/article/details/91996732
- 来源：CSDN（实操）
- 摘要：车窗不升降时示波器最直接；≥100 MHz，DC 耦合，降沿触发于静态电压 60%。
- 实战点：空闲隐性 ~12 V/显性 ~0 V，先用万用表确认静态电压再设触发；波特率须实测计算，不能填 19200。
- 动作：入主题笔记（补 lin-practical.md 量测段）

## 排除
hqwc.cn（AI 农场，含规范错误）、tsight.io（农场）、mzlw.cn/wmzlw.cn（洗稿）、bodocs.net（泛案例）、mbb.eet-china.com（讲 CAN 非 LIN）。

## 下一步
等你 review：激活 / 改写 / 丢弃
库现状：lin.md 4.8 KB + lin-practical.md 2.8 KB，无 deep-dive / failure-cases；候选 1/2/4 可支撑新建 failure-cases。
