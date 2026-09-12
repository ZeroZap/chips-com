# CAN FD / CAN XL 候选素材 @ 2026-09-11 17:03

## 协议速览
- 是什么：CAN 演进版（FD 扩带宽/数据，XL 再上一档）
- 解决什么：8B/1Mbps 经典 CAN 数据量翻倍时带宽不足
- 跟 L4 关联：同源总线族补 deep-dive；9-2 中国产线视角，9-11 切到「欧美工厂 / TI 论坛 / 整车级召回」

## 候选文章（4 条）

### 1. 400ns 边沿率缺陷 = 1.5 万美元幻影 ECU 保修
- 链接：https://obd-cable.com?p=4510/
- 来源：obd-cable.com（OBD 线缆工厂）
- 摘要：Stuttgart 实验室，欧洲 Tier 1 telematics 6 周 63 件幻影保修件累计 $15K，8 天定位：OBD-II 至 Molex 12-pin 诊断线束 65℃ 介电常数漂移，3m 线缆叠加 12pF/m 寄生电容，CAN FD 5Mbps 边沿率 400ns 超规格，采样窗口落在不确定区。
- 实战点：①幻影保修 forensic ②温度敏感介电常数 ③200ns bit time 被 400ns 边沿吃掉 ④产线测试未覆盖「满容性负载+真实收发器」

### 2. 工业现场总线 4 大 killer：lab 能用到产线就崩
- 链接：https://www.eurthtech.com/post/why-your-can-bus-works-in-the-lab-and-fails-in-the-machine
- 来源：Eurth Tech（工业现场总线供应商）
- 摘要：4 大 killer：①地电位差（GND 偏移 1-10V 推出共模）②stub 长度违反（1Mbps 限 30cm）③终端电阻错（>2/缺一/错位 → 100% 反射）④屏蔽层断路成天线。fix：每节点隔离收发器（ISO1050/ADM3053）+ repeater + 按速率算 stub 上限。
- 实战点：①地电位差 vs 电机/VFD 注入电流 ②星形拓扑隐性违标 ③隔离 vs 普通收发器选择+commissioning 实测 stub

### 3. Ford 438 万辆 ITRM 召回 = CAN race 跨层教训
- 链接：https://blog.logcat.ai/2026/03/12/4.3-million-vehicles-one-race-condition-what-the-ford-itrm-recall-teaches-us-about-cross-layer-debugging
- 来源：logcat.ai（Android Automotive 调试博客，2026-03）
- 摘要：2026-02-20 Ford 提交 NHTSA 26V104000 召回 4,380,609 辆（F-150/F-250/Expedition/Maverick/E-Transit MY2021-2027），根因：ITRM 与 CAN Standby Control bit (STBCC) 启动时 race；预计 1% 显形 = 43,000+ 辆 trailer brake 失效。2025-10 内部发现，5 月起 OTA 修复。
- 实战点：①STBCC race 9,999 次启动 0 显形第 10,000 次温漂/中断触发——non-deterministic 量产最难抓 ②OEM/supplier 黑盒+cross-layer observability 鸿沟 ③软件召回年比 3.3M→13.4M 翻 4 倍

### 4. SN65HVD234 量产 4% 失效率：TI E2E 40kV 探针
- 链接：https://e2e.ti.com/support/processors-group/processors/f/processors-forum/1314245/unable-to-boot-from-tftp---am335x-starter-kit
- 来源：TI E2E 论坛（Mike Page 求助原帖，2 供应商+2 MCU 都中招）
- 摘要：高压击穿检测仪（手持 40kV）+ 基站，4 芯螺旋线。T24CAN TVS 完好无 PCB 缺陷，4% 出货失效：R pin 卡高/偶有 MCU D pin 损坏/多颗 IC 烧穿。加 4V7 齐纳无效。已排除电源 latch-up/短路/32V PSU/40kV 瞬态。
- 实战点：①4% 失效率=良率灾难 ②两供应商+两 MCU 复现排除单器件 ③RS pin 隐性 silent mode（>0.75*VCC → 不发只收）易忽略

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
