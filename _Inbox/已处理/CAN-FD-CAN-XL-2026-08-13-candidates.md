# CAN FD / CAN XL 候选素材 @ 2026-08-13 22:00

## 协议速览
- 是什么：CAN FD = CAN 2.0 升级（8→64B、BRS 双波特率、5+ Mbps）；CAN XL 是再下一代（10+ Mbps、2048B）
- 解决什么：经典 CAN 1Mbps/8B 在 ADAS/域控/BMS 大数据回传"塞不下、传不快"
- 跟 L4 关联：车载/工控主干网，IoT 边缘网关也常见，采样点/错误帧/物理层是高频踩坑点

## 候选文章（5 条）

### 1. STM32H743 + TJA1145 多节点实车脱网
- 链接：https://blog.csdn.net/weixin_32311823/article/details/156965866
- 来源：CSDN
- 摘要：四节点车载子系统实验室正常实车频繁脱网，Stuff Error + CRC 失败集中在 >2Mbps 段。根因节点位定时因晶振容差累积偏差 >10%，BRS 切换后采样点偏移
- 实战：①位定时名义相同≠实际相同；②BRS 时序失配在高速段放大；③FDCAN_FRAME_FD_BRS 才真提速
- 推荐：实战案例（采样点/晶振）

### 2. TC275 MultiCAN 域控制器
- 链接：https://blog.csdn.net/weixin_42548829/article/details/160491731
- 来源：CSDN
- 摘要：TC275 4 节点 MultiCAN，仲裁 1Mbps 兼容 CAN 2.0，数据段 5Mbps。混合高频小包（电机 8B）和低频大包（日志 64B）
- 实战：①TXD 必须推挽；②RXD 工业环境 20kΩ 上拉；③MultiCAN 17 种中断源可单配
- 推荐：deep-dive（MultiCAN + 混合负载）

### 3. TSMaster 采样点偏移致 ECU 中断（产线故障）
- 链接：https://blog.csdn.net/weixin_29191081/article/details/159074415
- 来源：CSDN
- 摘要：500kbps/16TQ 采样点 80% 标准。新能源车 ECU 误设 60% 致偶发中断；工业节点间采样点差异 >15% 致持续错误帧。主从波特率误差 <1.5%
- 实战：①采样点 = (Sync+Prop+Phase1)/TQ；②节点间差异 >15% 是硬伤；③2Mbps 缩短 Prop 段
- 推荐：实战案例（产线 checklist）

### 4. RA6M5 客户 CANFD 发送异常（产线）
- 链接：https://www.sekorm.com/news/54291101.html
- 来源：世强（瑞萨代理）
- 摘要：客户"CAN 正常、CANFD 异常"，根因 Sample point 和 Manual 未手动配（默认勾选以为自动），结果 Stuff Error
- 实战：①e2 studio CANFD 需 40MHz 时钟；②Normal+FD 双配；③Sample point 漏配直接报 Stuff Error
- 推荐：主题笔记（瑞世工具链）

### 5. RK3576 + ISO 11898-1:2015 C 工具链
- 链接①：https://blog.csdn.net/weixin_49771820/article/details/144259076
- 链接②：https://blog.csdn.net/CodeIsle/article/details/159299205
- 来源：CSDN
- 摘要：①RK3576 `ip link set can0 up` 报 Invalid argument —— CANFD 不能只 set bitrate，须同时配 dbitrate + `fd on`。②C 工具链覆盖 socketcan + TDC + CRC-17（poly 0x1685B）+ BRS 位域映射
- 实战：①`ip link set can0 type can bitrate X dbitrate Y fd on` 三件套；②TDC 必须 fd on 生效；③BRS 位 bit 96（ISO §12.3.2）
- 推荐：deep-dive（SocketCAN + TDC + CRC-17）

## 下一步
等 review。优先级 1=3=5，2=4 次

