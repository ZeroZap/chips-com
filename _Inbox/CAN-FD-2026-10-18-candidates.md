# CAN FD / CAN XL 候选素材 @ 2026-10-18 12:00

## 协议速览
- 是什么：经典 CAN 的演进：CAN FD（仲裁段 1Mbps + 数据段 ≤8Mbps / 64B payload）；CAN XL（PWM 编码 ≤20Mbps / 2048B + VCID 逻辑隔离）
- 解决什么：车内 ECU 带宽焦虑 + 网关大帧搬运；工业网关多协议桥接
- L4 关联：**非主方向**（user profile "❌ 不优先：汽车总线"），但工控楼宇次优有交集（CANopen 主站/Modbus-CAN 网关）；本期偏车规实战，作 L4 反模式参考

## 候选文章（4 条）

### 1. CAN FD 网关 ECU 集成：CRC 错误从偶发到定位的实战
- 链接：https://www.embedcrest.com/blog/can-bus-protocol-automotive
- 来源：embedcrest.com
- 摘要：5Mbps 数据段网关接 legacy 500kbps 网；高负载 >60% 才出 CRC 间歇错
- 实战点：真凶 = 桩线 45mm（>30mm 推荐值）→ 反射落在位采样点；修复 = 缩短桩线 + 100Ω 端接；TEC/REC >96 要在 Bus Off 之前抓早期信号
- 推荐：**写实战案例**（"软件 OK ≠ 总线 OK，物理层优先"反模式）

### 2. CAN 总线为什么不会撞车：仲裁 / 采样点 / 错误恢复边界
- 链接：https://blog.51cto.com/u_14903315/14970583
- 来源：51CTO
- 摘要：两节点 500kbps 标称但分段参数差几个百分点；热车 / 长线缆下偶发 → Error Passive
- 实战点：采样点 87.5% 全网统一；SJW 决定漂移容忍；5 步排查 = 终端电阻→共地→位定时→TEC/REC→总线负载；SocketCAN 用 `ip -details link show can0`+`candump -e`
- 推荐：**入主题笔记**（L4 排查清单模板 + Linux 命令）

### 3. AURIX Bit0 错误进 Bus-Off 的两段式排错
- 链接：https://community.infineon.com/t5/AURIX/Unable-to-transmit-CANFD-messages-onto-the-CAN-bus/td-p/1193765
- 来源：Infineon 官方社区（FAE 真人回复）
- 摘要：CAN FD 报文发不出，LEC=Bit0，TEC 暴增→Bus-Off→立即恢复→循环
- 实战点：根因=RX 引脚卡隐性 1，跟 SOF 显性 0 冲突触发位错；分步排错=①Loopback 排除软件 ②TX/RX 引脚复用确认 ③电源域隔离（INH 不能吃掉调试供电）
- 推荐：**写实战案例**（L4"故障循环掩盖根因"反模式 + Loopback 自检模板）

### 4. CAN XL 网关升级：从 8 字节到 2048 字节的落地实操
- 链接：https://blog.csdn.net/weixin_26873711/article/details/166348595
- 来源：CSDN
- 摘要：网关升级到 CAN XL 工作量拆解 + 4 类典型问题排查（XL/2.0 混网、位错、DMA、VCID 串扰）
- 实战点：换收发器 ≠ 升级；CAN_XL+CAN2.0 同总线=双方格式错→Bus Off；老线缆必须换 120Ω 屏蔽双绞+支线≤0.3m；大帧瓶颈=软件逐帧中断+内存拷贝，开 DMA+零拷贝+环形描述符能翻几倍吞吐
- 推荐：**入主题笔记**（CAN XL 实战标本，跟边缘网关/MCU+MPU 异构架构交集）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃

---
- 跳过：copperhilltech 产业分析；motodemy 工具栈介绍（非实战）
