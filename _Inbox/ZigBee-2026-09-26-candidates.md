# ZigBee 候选素材 @ 2026-09-26 12:00

## 协议速览
- 是什么:2.4 GHz IEEE 802.15.4 mesh,AODV 路由 + ZigBee 3.0 统一应用层
- 解决什么:节点数百级低功耗 mesh(智能家居/工业传感/智慧照明)
- 跟 L4 关联:Mesh 自愈 vs 信道干扰 vs 固件三段式 fail,与 BLE 「产线挂」同级别

## 候选文章(4 条)

### 1. Blueprint: Migrating a 70-Device Zigbee Network to a New Coordinator Stack
- 链接:https://casey.berlin/writings/2026/06/zigbee-coordinator-migration-blueprint
- 来源:Casey Berlin(70 节点真迁移 + 4 天 sequel)
- 摘要:MAC_BAD_STATE(0x19) vs MAC_NO_ACK 区分固件 wedge 与空口争用;SLZB-06 自动固件推送 Dev/Beta UART/DMA build 跑生产;pin pan_id+ext_pan_id 后 8 秒恢复 commissioning
- 实战点:①RX 通 TX 全死 = radio 固件 wedge,别再 reset;②`herdsman` 默认不读 coordinator_backup.json,需写死 configuration.yaml
- 推荐:写实战案例(PAN ID pinning 反模式)

### 2. Fixing a Flaky Zigbee Mesh: Coordinator Placement, Routers and Range
- 链接:https://vo.rs/story/fixing-a-flaky-zigbee-mesh-coordinator-placement-routers-and-range
- 来源:vo.rs(4 类 mesh 症状分类)
- 摘要:4 个故障 pattern:单设备随机掉(LQI 看路由)/ 加新设备整网退化(低 quality router 当 parent)/ 数天后整网瞬崩(coordinator USB/驱动/channel 重选)/ 新 router 不中继(必须 mains 稳定 10 分钟再配对)
- 实战点:①Router 是「射频物理维护」,跟 Wi-Fi AP 选址一个思路;②Coordinator channel 切换 mesh 重成形需分钟级,日志按这个时间窗搜
- 推荐:扩 deep-dive(ZigBee mesh 现场排查 SOP)

### 3. Zigbee 网络频繁掉线?从根源解决节点稳定性问题
- 链接:https://www.txrjy.com/forum.php?mod=viewthread&tid=1425671
- 来源:通信人家园(2000 平米仓库 300 节点真 case)
- 摘要:凌晨 3 点批量掉线真凶=清洁工大功率对讲机 450MHz 谐波 + 路由器电源插头松动;在线率 92%→99.8%;5 类根因含父节点失效/信道-WiFi 重叠/路由表老化/电源跌落/NVM 密钥丢失
- 实战点:①工业「非线性干扰源」(对讲机/电焊/变频器谐波)比 Wi-Fi 重叠更难想到;②`zgApsUseParentLqi=TRUE` + `zgApsParentRetryThreshold=3` 是掉线自愈提速关键
- 推荐:扩 deep-dive(ZigBee 工业 EMC + 信道固化)

### 4. Troubleshooting XBee Pro S2B ZigBee Connection Drops
- 链接:https://industrialmonitordirect.com/es/blogs/knowledgebase/troubleshooting-xbee-pro-s2b-zigbee-connection-drops-and-packet
- 来源:Industrial Monitor Direct(XBee 工业 telemetry FAQ)
- 摘要:3 类现场失效(5-65% 间歇丢包 / 断电恢复 / 节点表消失);RSSI<-85dBm 衰减 <-100dBm 链路死;API mode 才能区分「丢包」vs「没发」
- 实战点:①XBee Pro S2B 3.6V 硬上限,5V 直灌永久损坏 → 500mA LDO;②API mode(ATAP=1)产线必备 per-packet RSSI/Tx Status
- 推荐:写实战案例(XBee 工业接入层)

## 下一步
等你 review:激活 / 改写 / 丢弃。优先级 1>3>2>4(按「真实产线故障 + 可复现根因」权重)。
