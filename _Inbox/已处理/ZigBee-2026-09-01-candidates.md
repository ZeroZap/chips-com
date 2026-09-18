# ZigBee 候选素材 @ 2026-09-01 12:00

## 协议速览
- 是什么：基于 IEEE 802.15.4 的低功耗 Mesh（2.4 GHz，250 kbps）
- 解决什么：智能家居/工业传感大量电池节点的低功耗+多跳覆盖
- L4 关联：上轮覆盖 Mesh 雪崩/入网/干扰；本轮聚焦 **3.0 安全 + Green Power 能量收集 + EFR32 量产 OTA** 三块 L4 实战短板

## 候选文章（5 条）

### 1. Touchlink 100m 远距离劫持（FAU）
- 链接：https://www.tf.fau.eu/2017/08/research/when-strangers-can-control-our-lights/
- 来源：FAU IT Security Infrastructures（学界+厂商复现）
- 摘要：单条命令 100m 外劫持 GE/IKEA/Philips/Osram 灯。Touchlink inter-PAN 帧明文无认证+2015 泄露的全局 master key。设计 2m，实测 36m。
- 实战点：(1) master key 因 ZLL 兼容**不可轮换**；(2) 建议禁用 3.0 产品的 Touchlink（Philips 已 OTA 修）；(3) 替代：EZ-mode + install code
- 推荐：扩 deep-dive（配网机制安全对比表）

### 2. Green Power 3.0 协议栈实战（CSDN）
- 链接：https://blog.csdn.net/weixin_33582311/article/details/162064872
- 来源：CSDN（基于 NXP JN516x SDK，CC BY-SA）
- 摘要：GP 3.0 全栈：源/代理/汇聚/Combo 四角色+隧道传输+去重表+三层地址+三种配网模式。含 NXP 初始化代码+翻译表+6 类故障表。
- 实战点：(1) 去重表**本地**，汇聚节点须再过一遍；(2) GP 地址冲突优先级高于 ZigBee；(3) 双向"二次握手"省 GP 接收能量；(4) 家庭 SIZE 5-10/工业 15-20/TIMEOUT 2-3s
- 推荐：写实战案例（"超低功耗协议栈"NXP 模板）

### 3. EFR32 NCP 并发 OTA 阻塞（Silicon Labs 社区）
- 链接：https://community.silabs.com/s/question/0D5Vm00000jv87CKAQ/blocking-issue-during-multiple-zigbee-ota-updates
- 来源：Silicon Labs 工程师社区（员工 Jesse 给出根因）
- 摘要：HOST+EFR32 NCP+0~5 终端并发起 OTA，NCP 偶发阻塞 50ms+ 触发 host assert。Log `NCP has run out of buffers, error 0x19`。EFR32MG21+SiSDK 2024.06。
- 实战点：(1) OTA 70min+0.5s polling+主机小时级属性读三重打爆 NCP 缓冲区；(2) 官方修：`EZSP_CONFIG_PACKET_BUFFER_COUNT=0xFF` + 检查 OTA Bootload Cluster + **禁用 Packet Handoff plugin**；(3) 50ms 周期任务是隐性观察窗
- 推荐：入主题笔记（"EFR32 NCP 量产 OTA 三板斧"+必禁 plugin 清单）

### 4. ZigBee 3.0 安全演进（Silicon Labs 官方）
- 链接：https://github.com/SiliconLabs/zigbee_applications/blob/master/zigbee_concepts/Zigbee-Networking-Concepts/Networking%20Concepts%20-%20Zigbee%20Security.md
- 来源：Silicon Labs 官方 GitHub
- 摘要：HA 1.2 → Black Hat 2015 Cognosec → 3.0 修复时间线。`ZigbeeAlliance09` 默认 key 被"jamming 逼降级到 insecure rejoin"破解，3.0 用 **install code** 解决。
- 实战点：(1) Secure Rejoin→Trust Center Rejoin 降级是漏洞利用关键；(2) 3.0 三件套：默认 key 限缩+强制轮换+Install Code 单次 join key；(3) 配网窗口几百 ms，但 2015 jamming+sniffing 做成确定性攻击
- 推荐：扩 deep-dive（"安全层演进"章节，2015 BH→3.0→PRO 2023 时间线）

### 5. Green Power 设备"失踪"5 根因（futurion）
- 链接：https://futurion.blog/zigbee-green-power-why-energy-harvesting-sensors-still-vanish-from-your-mesh/
- 来源：futurion 实战博客
- 摘要：能量收集设备"ghost"——配对成功后掉线、加路由器更糟。5 根因：缺 GP Proxy/加路由器改 link cost/协调器固件差异/能量不足/配网漏。
- 实战点：(1) "**更多路由器≠更好**"——GP 依赖特定 proxy 转发，路由 churn 撞微焦耳；(2) 协调器 OTA 改变 GP sink；(3) ZigBee 仅 1 broadcast/s，多 GP 广播必丢（必须 unicast）；(4) playbook：固件锁版/代理近端/20 次触发回归
- 推荐：写实战案例（GP"代理近端"部署方法论）

## 下一步
等你 review：激活/改写/丢弃
<mavis-progress>idle</mavis-progress>
