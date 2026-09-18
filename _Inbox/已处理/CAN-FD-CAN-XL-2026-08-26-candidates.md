# CAN FD / CAN XL 候选素材 @ 2026-08-26 12:00

CAN FD（2-8 Mbps / 64B）；CAN XL 第三代（10-20 Mbps / 2048B）。填补 CAN FD 与汽车以太网的中速空白。TDC/SSP/BRS/采样点是硬件硬约束，**和 L4「不在 demo 跑通就完事」直接冲突**。

## 候选（4 条）

### 1. CAN FD 错误帧排查指南（TDC 实战）
- 链接：https://www.eet-china.com/mp/a321786.html
- 来源：电子工程专辑，**汽车电子工程师窦明佳**
- 摘要：台架单测全过，装车后整网狂报错；拔节点后正常。Stuff Error 全在 bit 24/28。示波器抓 TX-RX 环路延迟 + 调 TDCV+TDCO 解决。
- 实战点：
  - 「台架通 ≠ 装车通」—— 线束/分支长度改变环路延迟
  - 采样点 75%-82% 是 ISO11898 硬性范围；TDCO = (PROP+TSEG1)*DBRP，2Mbps 80% = **400ns**
- 推荐：**扩 deep-dive**

### 2. CANFD TDC/SSP Bit Stuff Error 诊断实战
- 链接：https://blog.csdn.net/weixin_29195615/article/details/158202762
- 来源：CSDN，汽车电子 10+ 年工程师
- 摘要：示波器量 TX→RX 延迟 150ns，2Mbps 占位宽 30%，主采样点 80% 错位。NXP S32K：TDCEN=1 + TDCO=25 消除。
- 实战点：
  - 环路延迟测量：TX 边沿触发 → RX 边沿光标；TDCO = 期望 SSP - TDCV
  - 4 陷阱：单测思维 / 忽略 Loop Delay / TDCO 拍脑袋 / SSP 落下一位
- 推荐：**写实战案例**

### 3. Advanced CAN-FD Debugging: Transceiver Mysteries
- 链接：https://tech.hoomanely.com/advanced-can-fd-debugging-solving-transceiver-mysteries
- 来源：Hoomanely Tech（STM32H562 实战）
- 摘要：STM32H5 + CAN FD @ 1M/5M 间歇性丢帧 + Bus-Off。根因 = 5M 信号反射 + 收发器状态机错位。降到 73% 采样点 + 严格模式切换时序。
- 实战点：
  - 收发器模式切换：datasheet 强制 delay，SLEEP→NORMAL 必须 atomic GPIO
  - TxDelayCompensationOffset = 0x40 = 64 tq（实测延迟）；高负载 >2000 msg/s + 反射叠加触发 Bus-Off
- 推荐：**入主题笔记**（STM32H5 收发器模式机单独一节）

### 4. CAN XL 真实车装：Daimler Buses 铰接巴士
- 链接：https://can-cia.org/s/2OCes
- 来源：CiA + Daimler Truck 联合报道
- 摘要：2022 夏 Daimler + Bosch + NXP + R&S + Vector 联合，CAN FD 换 CAN XL。铰接巴士载客演示，500kbps 仲裁 / 14.5Mbps 数据段 / 60+ 米拓扑。**总线 99% 仍稳定**。
- 实战点：
  - 真实车规级负载极限 —— 99% bus load 仍可通信
  - 桥接：DLC 1:1 映射，CAN FD 接口 + CAN XL bridge
- 推荐：**入主题笔记**（CAN XL 商用里程碑 + 拓扑模板）

<mavis-progress>idle</mavis-progress>
