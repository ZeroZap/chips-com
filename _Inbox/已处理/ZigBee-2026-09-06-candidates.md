# ZigBee 候选素材 @ 2026-09-06 00:00

## 协议速览
- 是什么：IEEE 802.15.4 低功耗 2.4GHz Mesh，250kbps，CSMA-CA
- 解决什么：电池节点自组网 + Mesh 自愈 + 大规模组网
- 跟 L4 的关联：IoT 产线故障高发（重传风暴、路由表溢出、Wi-Fi 共存），实战素材密度高于 BLE/LoRa

## 候选文章（5 条）

### 1. Zigbee 工业组网：当"自愈"变成"自杀"
- 链接：https://tsight.io/articles/12807223
- 来源：tsight.io
- 摘要：化工厂凌晨 3 点网关频繁掉线。金属罐体多径 Jitter 触发 MAC 重传 + ED 持续偏高 → 父节点误判离网 → 瞬间广播风暴致雪崩式离网
- 关键点：① 802.15.4 IFS 对抖动极敏感 ② 单网关承载 30-50 节点 ③ 强金属+实时>50ms 应弃用
- 推荐：**扩 deep-dive**（协议栈死循环案例，L4 必收）

### 2. Debugging Zigbee with zigbee2mqtt and wireshark
- 链接：https://www.johal.in/debugging-python-zigbee-networks-with-zigbee2mqtt-and-wireshark-3
- 来源：johal.in
- 摘要：SmartSpace 3 楼层抓包+Python 监控 90 天，诊断时间 4.2h→8min(-96.8%)，非计划停机 47h→3.2h(-93.2%)
- 关键点：① Wi-Fi 信道 11 与 ZigBee 15 重叠→改 25 ② 故障路由器致 47 终端失联，LQI 拓扑秒定位 ③ 人体传感器错配 100ms 上报（应 10s）致消息风暴
- 推荐：**写实战案例**（量化数据全，适合 L4 性能优化章节）

### 3. ZigBee Mesh 路由坍塌与抗干扰边界
- 链接：https://tsight.io/articles/10687747
- 来源：tsight.io
- 摘要：金属车间 5m 丢包 40%，50+ 节点 Route Discovery 指数级广播风暴，Neighbor/Routing Table 溢出致网络瘫
- 关键点：① 协调器不放中心，放密度最高+射频最复杂区 ② 固件层关键控制帧做优先级隔离 ③ 与候选 1 互补
- 推荐：**入主题笔记**（路由坍塌+自愈边界双视角）

### 4. JN5169 ZigBee 量产踩坑：从硬件到协议栈
- 链接：http://www.wmrh.cn/education/21211.html
- 来源：wmrh.cn
- 摘要：NXP JN5169 量产踩坑大全：模块不启动/调试器不连/距离短/无法入网/批次性问题，带完整排查步骤
- 关键点：① 回流焊峰值>260°C 或 TAL 超时→模块时好时坏 ② 半孔焊盘"内切外延"钢网 ③ 终端深睡前未用 GPIO 改输入态防漏电
- 推荐：**写实战案例**（硬件+焊接+量产，IoT 方向强相关）

### 5. Building a Budget Zigbee Mesh That Doesn't Drop
- 链接：https://futurion.blog/building-a-budget-zigbee-mesh-that-doesnt-drop-constantly
- 来源：futurion.blog
- 摘要：智能家居 Mesh 5 条军规：协调器放中心+USB 延长线；先买常供电路由器再买电池传感器；路由器放"强弱交界"中点
- 关键点：① 电池设备不能当 Mesh backbone ② 路由器先到位→传感器后入网→自动化最后上 ③ 与 1/3 互补：工业+消费级双视角
- 推荐：**入主题笔记**

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
