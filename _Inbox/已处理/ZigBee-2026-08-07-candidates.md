# ZigBee 候选素材 @ 2026-08-07 00:00

## 协议速览
- 是什么：基于 IEEE 802.15.4 的低功耗 mesh 组网协议（2.4GHz）
- 解决什么：电池供电传感器的多节点可靠组网（智能家居 / 工业抄表 / 楼宇）
- 跟 L4 主题的关联：IoT / 可穿戴核心低功耗协议，产线部署坑点丰富

## 候选文章（5 条）

### 1. Zigbee Debugging VUART — Silicon Labs 培训 Wiki
- 链接：https://github.com/Jim-tech/IoT-Developer-Boot-Camp/wiki/Zigbee-Debugging-VUART
- 来源：GitHub Wiki（Silicon Labs 培训）
- 摘要：EmberZnet UART 被占用时用 VUART+SWO 跑 CLI 调试；硬约束是 Segger RTT Control Block 必须 1KB 对齐。
- 实战点：① CLI 走 SWO 通道跑 info/nwk/ep 诊断；② SEGGER_RTT_ALIGNMENT=1024 是硬性；③ HAL Configurator 启用 VUART via SWO + Serial。
- 推荐动作：扩 deep-dive（EFR32 调试通道 + CLI 抓栈）

### 2. zigbee 编译调试 17 个实战错误汇总
- 链接：https://blog.csdn.net/Stephen_yu/article/details/22048639
- 来源：CSDN（CC2430/CC2530 + Z-Stack 2006 实战 FAQ）
- 摘要：XDATA 溢出、断点失败、Cp001 授权、烧录 hex vs debug 模式冲突等 17 个产线真实错误。
- 实战点：① 数组过大用 `__code` / `code` 搬到 code 段；② 量产 hex 必须 release + .hex 扩展名；③ Fatal #E1 多半是 IAR 和 TI 工具不在同盘。
- 推荐动作：写实战案例（CC2530/CC2652 量产烧录踩坑）

### 3. ZigBee Mesh 模块实测 + 选型（成都亿佰特）
- 链接：https://blog.itpub.net/70016116/viewspace-3116007/
- 来源：ITPUB（国内模块厂商）
- 摘要：E18/E180/Link72 三款模块实测参数：4/20/27dBm 各级通信距离、单跳 10–50ms 延迟、实际 32/80/200 节点上限。
- 实战点：① 4dBm 室内 10–30m、20dBm 50–100m 实测值；② 路由节点每 50–100m 一个是产线密度经验值；③ sleep 终端下行缓存默认 7s 可配。
- 推荐动作：入主题笔记（ZigBee 选型与部署经验值）

### 4. Zigbee 工厂能耗真实部署（安科瑞）
- 链接：https://baike.baidu.com/item/物联网合同能源管理系统/8414732
- 来源：百度百科（厂商方案实录）
- 摘要：江苏工厂 21 个 ZigBee 采集模块 + 82 块 485 电能表；子网 ≤60 节点是产线经验上限；运行于世博 VIP 酒店等。
- 实战点：① 单子网 ≤60 节点（理论 65535 差距巨大）；② 配电室 14 表共用 1 模块走 485；③ 工业以太网上行 + ZigBee 下行两层架构。
- 推荐动作：扩 deep-dive（ZigBee 工业产线部署上限）

### 5. CC debugger 固件升级实战
- 链接：https://www.cnblogs.com/scue/archive/2013/10/29/3394393.html
- 来源：博客园 scue
- 摘要：CC debugger 固件过旧致 IAR 识别不到设备，升级 cebal_fw_srf05dbg.hex 解决。
- 实战点：① 仿真器固件是隐性排障点；② 升级路径 EB apps → 0207 N/A CC debugger。
- 推荐动作：跳过（被 #2 覆盖）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
