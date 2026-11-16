# FlexRay 候选素材 @ 2026-11-10 00:05

## 协议速览
- 是什么：时间触发(TDMA)+双通道冗余的车载总线，10 Mbps/通道。
- 解决什么：给 x-by-wire 底盘微秒级确定性，替代 CAN 事件触发的不可预测仲裁延迟。
- 跟 L4 主题的关联：库内 0 篇 FlexRay 正式笔记（仅 _Inbox 候选），本轮 4 条均为板级/产线/车间级，可直接开题。

## 候选文章（4 条）

### 1. 基于 MC9S12XF512MLM 的 FlexRay 总线调试记录
- 链接：https://blog.csdn.net/xushengliang12/article/details/135448903
- 来源：CSDN · 自研板 + TJA1080A 收发器（原创调试日志）
- 摘要：两块开发板一收一发烧官方例程仍不通，回退烧一次 CAN 再切回 FlexRay 才恢复；自研板最终定位到两颗贴片电容。
- 关键实战点：① 卡片板"RX/TX/TXE 三根线即可正常收发"，自研板逐项排查隔离器、TJA1080A、共模滤波器；② 电容取值过大导致通信失败，取下 C29/C35 后与开发板例程互通。
- 推荐动作：写实战案例（板级从零复现，本轮最硬）

### 2. FlexRay is faster than CAN and you need to adapt
- 链接：https://www.autobiz.ie/home/flexray-is-faster-than-can-and-you-need-to-adapt
- 来源：Autobiz（爱尔兰汽车维修培训）
- 摘要：车间端物理层量测与示波器判据，整体替代 CAN 时代的 60Ω 量测惯例。
- 关键实战点：① 终端节点 94Ω、中间节点 2.6kΩ，2/3/4 节点网络整网等效 47/46/45Ω；② 1 bit 仅 100ns，普通探头带宽不够，需 10:1 衰减高频探头（如 PicoScope 4425A）。
- 推荐动作：入主题笔记（物理层量测判据小节）

### 3. FlexRay 总线系统的常见故障与诊断方法
- 链接：https://bbs.plcjs.com/forum.php?mod=viewthread&tid=644568
- 来源：PLC 技术网（整理自大众系维修培训资料）
- 摘要：J533 诊断接口三类故障判别 + 线束维修工艺 + 两种拓扑下的终端电阻设置。
- 关键实战点：① 绞距 A=30mm、压接区绞合段≤30mm、剥线≤100mm、0.35mm² 双芯护套，维修须保持双绞；② 终端电阻分"终止节点终端"（驱动+ECU 各一个）与"环路两端各组件各一个"。
- 推荐动作：入主题笔记（产线工艺 + 诊断接口）

### 4. TC387 中 FlexRay 通信（英飞凌 AURIX 社区）
- 链接：https://community.infineon.com/t5/AURIX-MCU/TC387%E4%B8%ADflexray%E9%80%9A%E4%BF%A1/m-p/1191551
- 来源：Infineon Community · 官方工程师答复
- 摘要：与 CANoe 联调报 Missing offset correction / Clock Corr. Failed，官方定位为 SYNC 帧数量不足。
- 关键实战点：① 日志 A/B 偶周期 SYNC 帧 1/0、奇周期 0/0 → 偏移校正与速率校正双双失败，须偶/奇周期成对 SYNC；② 至少 2 个同步节点，双通道集群须 A/B 两通道都发 SYNC，AURIX 单节点时 CANoe 要补足同步节点。
- 推荐动作：写实战案例（同步失败根因链）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
