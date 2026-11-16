# ZigBee 候选素材 @ 2026-10-02 12:00

## 协议速览
- IEEE 802.15.4 + ZigBee PRO/ZigBee 3.0，2.4 GHz Mesh
- 低功耗室内/园区 Mesh 自组网（照明/温湿度/传感/抄表）
- L4 关联：实验室 OK 产线挂典型协议

## 候选文章（5 条）

### 1. 70 节点 Zigbee 迁移 + firmware ambush
- https://casey.berlin/writings/2026/06/zigbee-coordinator-migration-blueprint
- casey.berlin（HA/Z2M 实战派）
- 70 节点无重配迁协调器，4 天后灯全断、传感器正常。TX `MAC_BAD_STATE (0x19)` RX 正常 = 射频 firmware 死锁
- 实战：`MAC_BAD_STATE` ≠ `MAC_NO_ACK`，MAC 层拒发必 reflash；SLZB-06 自动 OTA 推 Dev/Beta **Day1 必关**；`pan_id` + `ext_pan_id` 必显式钉，NV 擦除后 DB 全丢
- 动作：**扩 deep-dive + 实战案例**（出货 checklist 两条铁律）

### 2. 4 类 mesh 故障 pattern
- https://vo.rs/story/fixing-a-flaky-zigbee-mesh-coordinator-placement-routers-and-range
- vo.rs
- 单设备掉/加设备后全网退化/全网同时掉/新路由不工作，每种给 LQI/日志定位
- 实战：**先 LQI 非 RSSI**；廉价 smart plug 路由实现差被优选后塌方；Coordinator USB 供电/驱动崩溃比设备故障更常见
- 动作：**入主题笔记**（流程图可入 L4 排错指南）

### 3. 2000 平米仓库 300 节点凌晨 3 点掉线
- https://www.txrjy.com//thread-1425671-1-1.html
- 通信人家园（中文工控论坛实战帖）
- 300 节点温湿度，1 月后每晚 3 点批量掉。根因 = 450MHz 对讲机谐波 + 路由电源松动；改造后在线率 92%→99.8%
- 实战：**450MHz 对讲机三次谐波进 2.4G**，必抓包 ED 定位；Z-Stack `ParentRetryThreshold=3`，自愈 5min→30s；路由电源余量 ≥200mA；`emberSaveNetworkToNv()` 重启不丢密钥
- 动作：**入主题笔记**（中文圈最完整「产线 100+ 节点批量掉线」根因清单）

### 4. 户外 mesh 灯控 pier 雷达谐波
- https://telectronichub.com/electronics/wireless-mesh-networks-for-outdoor-light-control-do-they-deliver-reliability
- telectronichub
- 港口 ZigBee 户外灯控，pier 当天偶天线反辐射 2.4G 雷达谐波击穿 CSMA/CA；铁氧体磁环 + repeater 移混凝土灯杆 = 99.95% uptime
- 实战：**金属结构当天偶天线效应**；CSMA/CA 被压制 = 物理层非协议 bug；户外必工业级芯片（CC2652R -40~+125°C）
- 动作：**入主题笔记**（金属环境/温控 L4 模板）

### 5. XBee Pro S2B 三类失效 + AT 调试
- https://industrialmonitordirect.com/tr/blogs/knowledgebase/troubleshooting-xbee-pro-s2b-zigbee-connection-drops-and-packet
- Industrial Monitor Direct
- XBee Pro S2B 工业 telemetry 三类失效：5-65% packet loss / 断电才恢复 / 节点失踪
- 实战：**生产必 API mode**，transparent 无法区分「丢 vs 没发」；ATAI=0x00 才健康；3.3V LDO ≥500mA peak；U.FL 松动 = 间歇丢包头号嫌疑
- 动作：**扩 deep-dive**（AT 命令体系对所有 ZigBee 派生调试有借鉴）

## 下一步
review 后决定激活/改写/丢弃。下一轮 = CAN FD