# ZigBee 候选素材 @ 2026-09-04 12:00

## 协议速览
- 是什么：基于 IEEE 802.15.4 的低功耗 Mesh 协议，2.4GHz 工业/家居/传感组网
- 解决什么：免布线、低功耗、可自愈的多跳节点通信
- 跟 L4 主题的关联：IoT 实战基础协议，常见 Mesh 路由坍塌、射频干扰、产线工艺 3 类硬坑

## 候选文章（5 条）

### 1. Zigbee 工业组网"自愈"变"自杀"——非线性射频环境协议栈崩溃
- 链接：https://tsight.io/articles/12807223
- 来源：TrueSight 工程分析
- 摘要：化工厂凌晨 3 点掉线，金属多径 → MAC 重传风暴+父节点误判 → 子网雪崩离网。给出抛弃 ZigBee 的工程判断。
- 实战点：① 重传+ED 高 → 父节点误判；② PCB 介电温漂 → 谐振偏移 2MHz+；③ 物理层是协议栈上限。
- 推荐动作：扩 deep-dive（bus/ZigBee.md 加"产线雪崩"段）

### 2. Debugging Zigbee with zigbee2mqtt and Wireshark (90 天实测)
- 链接：https://www.johal.in/debugging-python-zigbee-networks-with-zigbee2mqtt-and-wireshark-3
- 来源：Johal 工程博客
- 摘要：SmartSpace 楼宇 Wireshark 三点抓包+Python 监控，90 天后诊断 4.2h→8min（-96.8%），月停机 47h→3.2h。
- 实战点：① LQI 告警 80/危急 40；② 重传 5%/15%；③ 抓包+桥接 ROI 7.5x。
- 推荐动作：写实战案例（`ZigBee_实战案例_SmartSpace.md`）

### 3. JN5169 ZigBee 模块开发实战：硬件→产线焊接
- 链接：http://www.wmrh.cn/education/21211.html
- 来源：嵌入式工程师博客
- 摘要：JN5169 交钥匙实战：M00/M03/M06 天线、3.3V 去耦、SWD、3D PCB 布局、回流焊温区（≤260°C/TAL 60-90s）、7.1-7.4 故障清单。
- 实战点：① M00 外置天线 vs 金属外壳代价；② 半孔"内切外延"钢网；③ 批量炉温一致性首要。
- 推荐动作：入主题笔记（ZigBee_产线工艺 段）

### 4. 新疆哈密农业 ZigBee 现场故障：天线下垂 1km² 失联
- 链接：https://www.cruciaelectronics.com/info-1960.html
- 来源：智远电子案例库
- 摘要：哈密 4 万亩滴灌 ZigBee，1km² 阀门失联。Analyser 抓包定位 Router 0x0007 方向性异常——吸盘脱落胶带固定，破坏方向图。
- 实战点：① 现场单点检测 OK≠网络 OK；② 天线完整性是最易忽视"软故障"；③ 方向图差异瞬时捕获。
- 推荐动作：扩 deep-dive（bus/ZigBee.md 现场故障段）

### 5. 高雄工厂 ZigBee 监控：酸洗吊挂 20+ 台同轨
- 链接：https://www.asmag.com.tw/showpost/11243.aspx
- 来源：泓格科技案例
- 摘要：20+ 酸洗吊挂设备同轨（移动+金属梁柱），ZT-2570 协调器+ZT-2551 Router，VxCOMM 虚拟串口让主机 0 改代码。
- 实战点：① Router 互转=天然 repeater；② 短帧 PLC 轮询=ZigBee 黄金场景；③ 大封包多包重组防误判。
- 推荐动作：扩 deep-dive（bus/ZigBee.md 工业监控段）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
