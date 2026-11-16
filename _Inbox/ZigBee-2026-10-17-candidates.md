# ZigBee 候选素材 @ 2026-10-17 00:00

## 协议速览
IEEE 802.15.4 低功耗 Mesh(2.4GHz/DSSS/250kbps),多节点自组网+弱信号自愈路由;实验室 OK 产线挂典型协议,抗干扰/Mesh/大规模组网是 L4 高频考点

## 候选文章（4 条,与 10-14 错开）

### 1. Zigbee randomly broken for months. Fix took 5 seconds
- 链接：https://engineering.zooz.com/@nicolas.azrak/my-zigbee-devices-were-randomly-broken-for-months-the-fix-took-5-seconds-fa46a1105ec6
- 来源：ZOOZ Engineering (Nicolas Azrak)
- 摘要：家中 Zigbee 随机掉线数月。真因:USB 3.0 噪声污染协调器 2.4GHz。修复:USB 棒远离 USB 3.0 + `/dev/serial/by-id/` + 开 `last_seen`。
- 实战点：① USB 3.0 隐形 2.4GHz 干扰源 ② 物理位置>软件参数 ③ `last_seen` 是调试基本功
- 推荐动作：**扩 deep-dive**(USB 3.0 干扰机制)

### 2. Zigbee子设备数据丢失排查
- 链接：https://juejin.cn/post/7675288419880878131
- 来源：稀土掘金 (JVS-IOT 实战)
- 摘要：制造业 Zigbee"数据丢失"真因不是网络协议,是 JVS-IOT 平台缺失子设备注册+Topic 绑定,消息因无业务 Topic 被过滤。
- 实战点：① 丢失≠丢包,先查平台 ② 注册+Topic 绑定是平台层盲点 ③ 影子+未知 Topic 日志告警
- 推荐动作：**写实战案例**(产线数据丢失 SOP)

### 3. Zigbee网络频繁掉线?从根源解决
- 链接：http://www.cells-net.com/news/Zigbee%E7%BD%91%E7%BB%9C%E9%A2%91%E7%B9%81%E6%8E%89%E7%BA%BF%EF%BC%9F%E4%BB%8E%E6%A0%B9%E6%BA%90%E8%A7%A3%E5%86%B3%E8%8A%82%E7%82%B9%E7%A8%B3%E5%AE%9A%E6%80%A7%E9%97%AE%E9%A2%98.html
- 来源：晓网电子 (ZigBee 模组厂)
- 摘要：掉线真因:电源余量不足,发射瞬间电压跌落致射频模组复位。改进:大电容+宽压 2.0~5.5V+电源监测。实测 200 节点/10 级路由/7 天丢包率 3.6%,零掉线。
- 实战点：① 示波器抓发射电压定位 ② 模组硬件抗扰基线 ③ 路由按需建立避路由表老化
- 推荐动作：**入主题笔记**(ZigBee 模组选型+电源设计)

### 4. Zigbee自组网拓扑崩塌:链路状态表看工业真相
- 链接：https://tsight.io/articles/10805159
- 来源：TrueSight (工业 IoT)
- 摘要：化工园区 Zigbee"掉线"真因不是设备损坏。链路状态表在金属屏蔽+高密度部署下性能骤降,路由震荡+自愈代价让大规模场景 Zigbee 成稳定性灾难源。
- 实战点：① 链路状态表条目有限是隐性故障源 ② 自愈逻辑可放大故障 ③ 金属反射+多径=链路抖动
- 推荐动作：**扩 deep-dive**(链路状态表条目数+路由震荡触发)

## 下一步
等你 review 后决定:激活 / 改写 / 丢弃