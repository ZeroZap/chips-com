# ZigBee 候选素材 @ 2026-10-01 00:00

## 协议速览
- 是什么：IEEE 802.15.4 低功耗 mesh，2.4 GHz 16 信道，16 位 PAN ID + 64 位 Extended PAN ID。
- 解决什么：智能家居 / 工业传感的低功耗自组网。
- 跟 L4 关联：典型"实验室 OK、产线挂"——mesh 自愈反致广播风暴、PAN ID 冲突、450MHz 谐波、协调器 auto-update 推 beta 致 MAC 死锁。

## 候选文章（3 条）

### 1. Blueprint: Migrating a 70-Device Zigbee Network to a New Coordinator Stack — Without Re-Pairing
- 链接：https://casey.berlin/writings/2026/06/zigbee-coordinator-migration-blueprint
- 来源：Casey Berlin（独立技术 blog）
- 摘要：70 节点迁移 ~30 分钟不停机；4 天后遭 firmware ambush——SLZB-06 自动更新推 Dev/Beta，致 MAC_BAD_STATE（0x19，RX 通 TX 全失败）。所有 reset 无效，唯一解 = 刷 stable + pin pan_id / ext_pan_id。
- 实战点：MAC_BAD_STATE ≠ 干扰，MAC_NO_ACK 才需处理——错误码语义是 L4 排障核心；auto-update 会偷偷推 beta。
- 推荐：**扩 deep-dive**（错误码速查 + auto-update 防呆流程，独立笔记）。

### 2. Zigbee 网络频繁掉线：从根源解决节点稳定性问题（2000㎡仓库 300 节点）
- 链接：https://www.txrjy.com/thread-1425671-1-1.html
- 来源：通信人家园（老牌通信工程师论坛）
- 摘要：大型结霜仓库 300 个 ZigBee 温湿度传感器，1 个月后每天凌晨 3 点批量掉线。抓包定位：清洁工大功率对讲机 450MHz 谐波 + 路由器供电接头松动瞬断。信道锁 25 + 备用路由后，在线率 92% → 99.8%，自愈 5min → 30s。
- 实战点：凌晨 3 点批量 = 人类活动时序——工业 IoT 排障必查人；KPI 模板：在线率 92→99.8% + 自愈 5min→30s。
- 推荐：**写实战案例**（IoT/可穿戴方向——"产线外部干扰"+"KPI 量化"齐全）。

### 3. Zigbee 组网：在射频黑洞中重建秩序
- 链接：https://tsight.io/articles/11938041
- 来源：TrueSight（工业无线 blog，强观点）
- 摘要：硬刚"ZigBee 自动组网是工业现场元凶"。金属屏蔽工厂路由震荡 → 协调器 CPU 90% → 全网瘫；PAN ID 冲突致设备跨网加入。提出"静态路由绑定 + 多网关物理隔离 + 调大信标间隔"三板斧。
- 实战点：自愈在工业高干扰下是反向放大器——L4 反模式案例；产线确定性感 > 弹性。
- 推荐：**入主题笔记**（L4 "工业 mesh 反模式"，跟 BLE / Thread 横向对照）。

### 4. WLT2422Z‑S 工业 ZigBee 模块：工控避坑
- 链接：https://m.eechina.com/view.php?id=911176
- 来源：电子工程网（eechina）
- 实战点：选型 checklist = 发射功率 + 灵敏度（-106dBm）+ 链路预算 128dBm；单包 ≤ 60B。
- 推荐：**入主题笔记**（L4 "工业模块选型"，跟 BLE / LoRa 横向对照）。

## 下一步
等你 review：激活 / 改写 / 丢弃
- 优先级：1（错误码 + auto-update）> 2（2000㎡仓库 + KPI）> 4（选型 checklist）> 3（mesh 反模式横向）