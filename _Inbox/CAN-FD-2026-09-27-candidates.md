# CAN FD 候选素材 @ 2026-09-27 12:00

## 协议速览
- 是什么：CAN Flexible Data Rate（ISO 11898-1:2015），兼容经典 CAN，数据段 64B + 可选 BRS
- 解决什么：经典 CAN 8B/1Mbps 撑不住 ADAS/OTA/大负载诊断帧；DLC 查表+BRS 提吞吐 ~5x
- 跟 L4 关联：与"产线挂/实验室 OK"反差模式匹配；汽车总线 IoT 弱相关，DLC 查表/TEC 监控可迁移工业 CANopen

## 候选文章（4 条）

### 1. CAN Bus Physical Layer Autopsy（5 类现场故障）
- 链接：https://obd-cable.com/can-bus-physical-layer-testing-guide/
- 来源：OBD Cables 工程博客
- 摘要：维修厂 5 类真实 CAN 故障：stub 过长、屏蔽层双端接地(+22dB)、穿刺探针腐蚀(0.1→11Ω/8月)、未端接反射(2.1V)、CAN_H/L 反接(11 款车踩坑)
- 关键实战点：60Ω 验收；PicoScope6 persistence 捕 micro-crack；10k 帧 Loopback；24h soak
- 推荐动作：**扩 deep-dive** → `can-fd-signal-integrity.md`

### 2. CAN 错误状态机与 STM32 诊断实践
- 链接：https://blog.csdn.net/gan8painter/article/details/155736121
- 来源：CSDN 汽车电子工程师原创
- 摘要：错误状态机 + TEC/REC 阈值（96/127/255/256）+ FreeRTOS 监控；真实案例 —— 网关装车后每 2-3h 某 ECU 间歇失联，发 0x00 非法帧后 BusOff，根因 SN65HVD230 VCC 跌落 1.5V，加 100μF 钽电容修复
- 关键实战点：HAL_GetState 二元陷阱；REC↑=接收端 EMC；TEC↑=发送端硬件；CAN_L 与电机线平行 10cm 致 REC=130
- 推荐动作：**扩 deep-dive** → `can-fd-error-state-machine.md`

### 3. 400ns Edge Rate: $15K Phantom ECU Warranty
- 链接：https://obd-cable.com/400-nanosecond-edge-rate-phantom-ecu-warranty/
- 来源：OBD Cables 续篇（热致边沿退化）
- 摘要：6 阶段失效 —— 冷启 OK → 15min 升温 → 65°C 介质常数漂移 → 边沿 400ns 退化 → 偶发位错 → TEC 过 96 → 误诊"ECU 模块坏"重复保修；根因线缆规范缺高频 dielectric 表征
- 关键实战点：热致寄生电容；DTC 指向模块非线缆；telematics 每 6-8 周误换
- 推荐动作：**入主题笔记** → `can-fd-thermal-aging.md`

### 4. CAN FD DLC 配置错误致 ECU OTA 失败（AUTOSAR BSW）
- 链接：https://www.lpnh.cn/news/84.html
- 来源：尧图网（车规开发者内部稿）
- 摘要：DLC 0xE 应映射 64B 而非 48B（ISO 11898-1:2015 Table 12）；整车厂 OTA 因 LUT 错失败 100%、127s/车；修复后 39s/车；DLC72 vs DLC64 仲裁失败率 18.7%→0.02%；含 S32K3xx 寄存器级 + ASIL-B FMEDA + Cppcheck AST 规则
- 关键实战点：TXFIFO DLC_MASK 必须 0xF；BL/AP TDCO 不一致致 RX FIFO 溢出；AST 捕 CanIfDlc>8 非法
- 推荐动作：**扩 deep-dive** → `can-fd-dlc-mapping.md`（CANopen 也用同一套 DLC 表）

## 下一步
- 1/2/4 实战密度高可直接入 `_basic/`
- 3 偏汽车 IoT 弱相关，仅作 L4 实战案例归档
- Ford ITRM 4.3M 召回(logcat.ai)弱相关已剔
- review：激活→落_basic/；改写→调范围；丢弃→下协议