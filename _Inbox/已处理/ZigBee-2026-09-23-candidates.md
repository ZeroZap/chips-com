# ZigBee 候选素材 @ 2026-09-23 00:00

## 协议速览
- 是什么：基于 IEEE 802.15.4 的低功耗 mesh 协议，ZigBee 3.0/PRO 主流
- 解决什么：智能家居/楼宇/工业传感的低速率网状自组网
- 跟 L4 关联：IoT/可穿戴核心协议；本批 5 篇全产线/固件层实战

## 候选文章（5 条）

### 1. Troubleshooting a ZigBee PAN ID Conflict
- 链接：https://dev.to/justinethier/troubleshooting-a-zigbee-pan-id-conflict-pfb
- 来源：dev.to 工程 blog（SiLabs EmberZNet 背景）
- 摘要：建筑部署后整网反复重建分裂。根因是部分设备 EPID 字节序反转，SiLabs 协调器 63/min 阈值触发整网换 PAN ID 把设备拆两半。
- 关键实战点：EPID 反转 lab 几十台测不出；阈值 63/min 可调；抓包对比 beacon EPID 与 NV
- 推荐动作：写实战案例

### 2. Z-Stack 20240710 BUFFER_FULL 网络崩溃
- 链接：https://blog.gitcode.com/3f1089ec9a65cfe3818fcdd6c0d274ca.html
- 来源：GitCode 博客（Zigbee2MQTT 社区，ZBDongle-P 用户群）
- 摘要：60-120 设备网络数小时后 0x11 BUFFER_FULL，需物理拔插协调器恢复。降级 20221226 稳定。
- 关键实战点：大网缓冲区管理是真实痛点；保留已知工作版本；网络分段缓解过载
- 推荐动作：入主题笔记

### 3. 70-Device Zigbee Coordinator Migration + 固件伏击
- 链接：https://casey.berlin/writings/2026/06/zigbee-coordinator-migration-blueprint
- 来源：Casey Berlin 独立工程 blog
- 摘要：不停网迁移 70 设备协调器蓝图。续篇揭露 SLZB-06 auto-update beta 固件触发 MAC_BAD_STATE（0x19，TX 死 RX 活）。修复：关 auto-update + 手动稳定版 + pin pan_id/ext_pan_id。
- 关键实战点：RX 通 TX 死=固件 wedge；协调器基础设施别 auto-update；Z2M 必须 pin 网络身份
- 推荐动作：扩 deep-dive

### 4. SonoffLAN Zigbee Pro Bridge 411 错误
- 链接：https://blog.gitcode.com/1e5ddb64bba951d6824f4426f3510a03.html
- 来源：GitCode 博客（SonoffLAN 用户+官方沟通）
- 摘要：ZBMINIL2 偶发 411（设备不可达，eWeLink 自定义码）。RSSI -60~-70dBm 良好，实为 2.4GHz 信道冲突。手动指定信道 15/20 稳定 72h+。
- 关键实战点：RSSI 良好 ≠ 链路可靠；Zigbee 与 WiFi 隔离选 15/20/25/26；debug 日志+信道扫描定位
- 推荐动作：写实战案例

### 5. Zigbee 自组网工业现场拓扑崩塌
- 链接：https://tsight.io/articles/10805159
- 来源：tsight.io 工业 IoT 分析
- 摘要：化工园区 Zigbee 传感网案例。关键路由节点重启后 RREQ 风暴+丢包+跳数抖→死锁。链路状态表开销随节点数平方增长，路由表溢出。
- 关键实战点："自愈"掩盖拓扑不可控；LQI 波动+路由震荡是灾难源；工业务实选静态拓扑
- 推荐动作：入主题笔记

## 下一步
等你 review：激活 / 改写 / 丢弃