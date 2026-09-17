# CAN FD / CAN XL 候选素材 @ 2026-09-17 12:00

## 协议速览
- 是什么：CAN FD = Flexible Data-Rate，仲裁段 ≤1Mbps + 数据段 ≤8Mbps + 64B 数据；CAN XL 进一步 20Mbps + 2048B 数据 + 去位填充
- 解决什么：经典 CAN 1Mbps / 8B 带宽不足；CAN XL 解决大包传输与位填充开销瓶颈
- 跟 L4 主题的关联：🟡 **次优主题**（user profile 已标 CAN/UDS 不优先，但 cron 轮询机械跑）

## 候选文章（5 条）

### 1. CAN FD 总线错误帧排查指南（21ic / 样车调试真实案例）
- 链接：https://blog.csdn.net/jluliuchao/article/details/140293232
- 来源：21ic 电子技术论坛（转载至 CSDN）
- 摘要：单节点测试通过，装车后总线大量错误帧（Stuff Error Bit Pos=24/28），3 周才定位到 TDCO（发送延迟补偿偏移）未按 ISO 11898 配置。
- 关键实战点：
  - 排查顺序：线束 → 接口电路 → 采样点 → TDC（最终真因）
  - 错误位位置规律性 = 位错误的指纹（区别 EMC 干扰）
  - TDCO 标准公式 = (PROP+TSEG1) × DBRP
- 推荐动作：✅ 扩 deep-dive（"CAN FD SSP/TDC 排查手册"是 L4 闭环缺失的一环）

### 2. Advanced CAN-FD Debugging: Solving Transceiver Mysteries（Hoomanely Tech）
- 链接：https://tech.hoomanely.com/advanced-can-fd-debugging-solving-transceiver-mysteries
- 来源：Hoomanely Tech Blog（STM32H562 多传感器边缘平台）
- 摘要：1Mbps 仲裁 + 5Mbps 数据阶段产线出货后帧丢失，2000 msg/s 触发 Bus-off，根因是 5Mbps 信号反射 + 收发器模式机时序违例。
- 关键实战点：
  - STM32H5 FDCAN 寄存器配置（Prescaler=16 / SP=87.5% / TDC enable）
  - 收发器 4 种模式（SLEEP/STANDBY/LISTEN/NORMAL）原子切换 + 10ms 稳定延迟
  - 5Mbps 反射问题 → 降到保守时序 + SP 余量
- 推荐动作：✅ 写实战案例（STM32H5 FDCAN 寄存器模板 + 收发器状态机）

### 3. How a 400-Nanosecond Edge Rate Defect Creates a $15K Phantom ECU Warranty（obd-cable.com）
- 链接：https://obd-cable.com/?p=4510/
- 来源：OBD Cables 工程博客（Tier 1 线束厂实战）
- 摘要：3 米 CAN FD 5Mbps 线束 65℃ 下介电常数漂移 → 上升沿退化 400ns → 采样点落入不确定区 → J1939 节点 Bus-off，$15K phantom warranty。
- 关键实战点：
  - 标准 QC（continuity / 绝缘电阻 / 拉力）**全过**但 AC 行为不符
  - DC 电阻 60Ω ≠ AC 阻抗 60Ω
  - 眼图闭合的根因：收发器 35mA 驱动 vs 总电容负载
- 推荐动作：✅ 写实战案例（"线束 QC vs 信号完整性 gap"——非常实战角度）

### 4. CAN 错误状态机原理与 STM32 工程诊断实践（CSDN 真实项目案例）
- 链接：https://blog.csdn.net/gan8painter/article/details/155736121
- 来源：CSDN 原创（汽车电子项目）
- 摘要：车载网关装车后每 2-3 小时某 ECU Bus-off，根因是 SN65HVD230 VCC 在空调/ABS 启动时跌落 1.5V，加 100μF 钽电容修复。
- 关键实战点：
  - TEC/REC 阈值（96 警告 / 128 被动 / 256 Bus-off）
  - **REC↑ = EMC 问题**；**TEC↑ = 发送端硬件缺陷**（实战经验总结）
  - FreeRTOS 监控任务模板（100ms 检查 TEC/REC + 5s 节流报警）
- 推荐动作：✅ 写实战案例（CAN 错误状态机监控 + FreeRTOS 任务模板）

### 5. STM32 FDCAN 车载诊断实战：UDS 栈集成中的时序坑与 CRC 校验反例
- 链接：https://aiot.csdn.net/6a1d267310ee7a33f2769f50.html
- 来源：CSDN（STM32H7 车载网关量产经验）
- 摘要：OEM 工厂 Vector CANoe v11 CheckCRC() 报 CRC 错误，研发环境 100% 通过，根因是 STM32 硬件 CRC 含位填充而软件算法不含，2Mbps 下才出现。
- 关键实战点：
  - FDCAN_CCCR.RETRAN 关闭 + 软件重传 + TIM16 超时控制
  - FDCAN_TXBC.TFQS ≥ 16 + 优先处理流控帧（避免 BRS 切换丢帧）
  - 量产 SOP 验证清单：电气特性 + 协议一致性 + 环境适应性 + 产线专用
- 推荐动作：✅ 写实战案例（量产 SOP 4 类验证清单 + CRC 一致性 hack）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃。
注意：user profile 已标 CAN/UDS 🟡**次优主题**，但 cron 机械轮询；review 时可考虑是否要把 CAN 类合并到"汽车总线 L4"主题做总览而非单篇 deep-dive。