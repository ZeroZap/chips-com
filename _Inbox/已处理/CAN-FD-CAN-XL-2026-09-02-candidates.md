# CAN FD / CAN XL 候选素材 @ 2026-09-02 12:00

## 协议速览
- 是什么：CAN 演进版（FD 扩带宽/数据，XL 再上一档）
- 解决什么：8B/1Mbps 经典 CAN 在数据量翻倍场景带宽不足
- 跟 L4 关联：同源总线族，补 deep-dive 故障库

## 候选文章（5 条）

### 1. CAN FD 与 CAN XL 长距离性能与局限
- 链接：https://blog.csdn.net/2401_88858637/article/details/161546981
- 来源：CSDN（重卡 BMS）
- 摘要：40m 线缆跑 1Mbps CAN FD 误码率 10⁻³ 频繁 Bus-Off；换 CAN XL 终端电阻折腾两周。50m 非屏蔽线实测：CAN FD 2Mbps 采样点 70%→85% 误码率 10⁻⁵→10⁻⁷，再调 90% 反恶化。
- 实战点：①40m/8Mbps 位时间 125ns vs 50m 延迟 400ns ②采样点 vs 反射波 ③XL 对线缆更严
- 推荐：扩 deep-dive（长距离极限 + 采样点）

### 2. CAN 调试实战干货指南
- 链接：http://www.mzlw.cn/news/122325
- 来源：尧图网络（量产工程师）
- 摘要：四层定位（物理 80% / 链路 15% / 协议 4% / 业务 1%）。万用表 55-65Ω 判终端；TEC/REC 96/128/256 + 自愈；CANoe 三套参数；附 STM32F4 CAN_Error_Process + CRC8 源码。
- 实战点：①80% 物理层 ②FD/2.0 混用降级 BRS+15bit CRC ③Reset+Stop+Start 自愈
- 推荐：写实战案例入主题笔记（CAN 量产故障库骨架）

### 3. CAN 总线故障排雷手册
- 链接：https://www.eet-china.com/mp/a468630.html
- 来源：电子工程专辑
- 摘要：四大门派（物理 60%+ / 协议 / 软件 / 系统）。产线故事：0Ω=短路找剐蹭；∞=总线断；CANoe Bit Timing Detection 查"波特率一致但采样点 75% vs 90%"隐性不一致。
- 实战点：①隔离法断节点定位 ②采样点差异放大成 CRC 错误 ③负载 >70% 雪崩丢帧
- 推荐：扩 deep-dive（采样点 + Bit Timing Detection）

### 4. CAN 错误状态机 + STM32 诊断实践
- 链接：https://blog.csdn.net/gan8painter/article/details/155736121
- 来源：CSDN（车载网关）
- 摘要：网关装车后每 2-3h 某 ECU 间歇失联，发全 0x00 后 TEC 飙 256 入 Bus Off。软件/拓扑均正常，长时监测发现 SN65HVD230 VCC 在空调吸合时数十 ms × 1.5V 跌落。修复：VCC 加 100μF 低 ESR 钽电容 + 优化电源走线。
- 实战点：①TEC/REC 三态 96/128/256 ②REC 缓升=接收 EMC，TEC 急升=发送硬件 ③Bus Off 冷静期 2.8ms
- 推荐：入主题笔记（CAN 状态机 + 电源完整性配对）

### 5. CAN FD 实战：MCP2517FD 双板对接
- 链接：https://makeronsite.com/blog/2026/07/055-canfd-vehicle-communication
- 来源：创客出手（2026-07）
- 摘要：STM32F103C8T6×2 + MCP2517FD×2 + TJA1050 + 120Ω 物料 + 接线。SPI Mode 0 强制；仲裁 500kbps / 数据 2Mbps；TDC 自动 TDCMOD=0x02。误码→降 1Mbps + 启 TDC + 换屏蔽双绞线 ≤40m。
- 实战点：①SPI ≤10MHz ②TDC 根治相位错位 ③FD 混入经典网触发格式错误
- 推荐：跳过（成熟工具链）/ 仅参考附录

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
