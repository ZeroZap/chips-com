# ZigBee 候选素材 @ 2026-09-20 00:00

## 协议速览
- 是什么：IEEE 802.15.4 低功耗 Mesh（2.4GHz，250kbps，65000+ 节点）。
- 解决什么：低功耗+自组网+网状冗余的传感/控制（家居/路灯/工业）。
- 跟 L4 关联：Mesh 拓扑+工业协议栈可靠性边界，basic/ 排错章节优选素材。

## 候选文章（5 条）

### 1. Zigbee 工业组网："自愈"变"自杀"
- 链接：https://tsight.io/articles/12807223
- 来源：tsight.io
- 摘要：化工厂网关凌晨 3 点频掉，频谱仪抓金属罐体多径→MAC 重传风暴+父节点离网广播雪崩，几秒子网全崩。
- 实战点：①多径→ED 偏高→CSMA/CA 死等→离网广播 ②单网关>50 节点路由表溢出阈值
- 动作：扩 deep-dive（Mesh 自愈边界 / 选型决策树）

### 2. Zigbee2MQTT 容器化部署与故障自愈实践
- 链接：https://blog.gitcode.com/c129385b9423a3e42675310b0d25e46e.html
- 来源：GitCode 博客
- 摘要：汽车车间协调器 USB 松动致温控中断 2h，Docker `--restart=always` 让 10s 自愈。
- 实战点：①USB dongle 物理松脱是产线最大隐患 ②`--memory=512m --cpus=0.5` 资源限制 ③多实例 vs 主备切换
- 动作：写实战案例（容器化产线部署配方）

### 3. Z-Stack 固件网络稳定性问题分析
- 链接：https://blog.gitcode.com/3f1089ec9a65cfe3818fcdd6c0d274ca.html
- 来源：GitCode 博客（社区实测）
- 摘要：ZBDongle-P+20240710 固件+60-120 设备数小时后协调器吐 `0x11 BUFFER_FULL` 崩溃，必须物理拔插，回退 20221226 稳定。
- 实战点：①缓冲区缺陷+内存泄漏在高密度显形 ②大网络升级先跑模拟生产 ③保留已知工作版本作"金标"
- 动作：入主题笔记（Z-Stack 固件选型 / 升级守则）

### 4. Troubleshooting a ZigBee PAN ID Conflict
- 链接：https://dev.to/justinethier/troubleshooting-a-zigbee-pan-id-conflict-pfb
- 来源：dev.to（SiLabs EmberZNet 实战）
- 摘要：商用楼宇网关 PAN ID 冲突→重选 PAN→网络撕裂。Simplicity Studio 抓包发现部分设备 EPID 字节反转，触发 63/min 阈值。
- 实战点：①Beacon EPID 翻转=经典生产 bug ②协调器 63/min 阈值工程权衡 ③EPID 字节序反转要肉眼对比两台 Beacon
- 动作：扩 deep-dive（ZigBee 抓包 / 协调器阈值调优）

### 5. 70-Device Zigbee 迁移 + 4 天后固件伏击
- 链接：https://casey.berlin/writings/2026/06/zigbee-coordinator-migration-blueprint
- 来源：Casey Berlin 工程师博客
- 摘要：SLZB-06 自动更新刷入 dev/beta 固件，生产 mesh 现 `MAC_BAD_STATE(0x19)`：RX 正常、TX 全死。`advanced: pan_id/ext_pan_id` 锁定身份+`herdsman` 备份恢复。
- 实战点：①MAC_BAD_STATE ≠ MAC_NO_ACK，TX 全死=固件卡死 ②Dev/Beta 细标藏在 picker 三层菜单 ③`database.db.backup` 是 re-pair 救命稻草 ④PAN ID 显式写入 yaml 必备
- 动作：写实战案例（产线协调器迁移配方 / 固件自动更新治理）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃