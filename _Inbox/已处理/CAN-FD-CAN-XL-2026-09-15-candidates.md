# CAN FD / CAN XL 候选素材 @ 2026-09-15 00:00

## 协议速览
经典 CAN 升级版：数据段 5Mbps（FD）/ 10Mbps+（XL），BRS 双波特率 + 21bit CRC + 64B DLC。带宽救星但物理层 + 位定时 + 收发器管理更严苛。

## 候选文章（5 条）

### 1. CAN FD 错误帧排查指南（CSDN 窦明佳）
- 链接：https://blog.csdn.net/jluliuchao/article/details/140293232
- 摘要：OEM 样车装车后 CAN FD 大量错误帧，位错误规律出现在数据段 bit 24/28。线束+终端+接口+采样点全无效，最终是 TDCO 配错。
- 实战点：①Stuff Error bit 24/28 + 数据段 = TDCO 指纹；②单节点 OK / 入网挂掉 = 物理层耦合。
- 推荐：入 deep-dive（TDCO + SSP 可独立笔记）。

### 2. CAN 错误状态机与 STM32 诊断（CSDN gan8painter）
- 链接：https://blog.csdn.net/gan8painter/article/details/155736121
- 摘要：TEC/REC → Active/Passive/Bus-Off 三态 + FreeRTOS 监控骨架。真实车载案例：装车 2-3h ECU 间歇失联→TEC=256 Bus-Off；根因 ABS/空调启动时 SN65HVD230 VCC 跌落 1.5V，加 100μF 钽电容修复。
- 实战点：①REC↑ = 接收端 EMC，TEC↑ = 发送端硬件；②Bus-Off 恢复 ≈ 2.8ms@500kbps。
- 推荐：扩 deep-dive + 入主题笔记。

### 3. Why CAN Bus Works in Lab and Fails in Machine（EURTH Tech）
- 链接：https://www.eurthtech.com/post/why-your-can-bus-works-in-the-lab-and-fails-in-the-machine
- 摘要：现场"实验室复现不了"根因 = 地电位差（plant 接地各点 1-10V）+ 拓扑错（星型违反 30cm stub）+ 终端位置错。修复：每节点隔离收发器（ISO1050/ADM3053）+ 拓扑硬约束。
- 实战点：①工业 80% 通信故障 = 物理层 / 接地；②共模超 ±2V/+7V 收发器非线性；③终端 = 两端各 120Ω 实测 ≈ 60Ω。
- 推荐：入主题笔记（工业现场排错 SOP），与 basic/can-*.md 对照。

### 4. Debugging CAN Bus with Multimeter Over Software（LinkedIn）
- 链接：https://www.linkedin.com/posts/kumar-swamy-naik-o_debugdiaries-embeddedsystems-firmware-activity-7487695849905594370-wd8T
- 摘要：模块化机箱背板（多插卡 MCAN），少量卡正常→插满后总线瘫痪。资深工程师直接万用表量 CAN_H↔CAN_L，发现每张卡自带 120Ω 并联 → 总阻远低于 60Ω 匹配点。拆掉中间终端后恢复稳定。
- 实战点：①任何总线"上电测电阻"应排第一；②插卡 / 模块化设计自带终端 = 量产隐患。
- 推荐：写实战案例笔记（L4 系列实战模板）。

### 5. CAN 调试实战干货指南（mzlw.cn）
- 链接：http://www.mzlw.cn/news/122325
- 摘要：物理 80% / 链路 15% / 协议 4% / 业务 1% 四层定位；CANoe 三场景模板；六大故障根因+修复；附 STM32F4 自愈 + CRC8 代码。
- 实战点：①先物理后软件；②混合组网降级 15bit CRC + 关 BRS；③自愈需 100ms 巡检 + 自动复位。
- 推荐：跳过（同质化多，作参考索引）。

## 下一步
等你 review：激活 / 改写 / 丢弃。
推荐度：2≈1>3>4>5