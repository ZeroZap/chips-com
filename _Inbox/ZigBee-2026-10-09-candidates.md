# ZigBee 候选素材 @ 2026-10-09 22:33

## 协议速览
- 是什么：IEEE 802.15.4 低功耗 mesh 协议，250 kbps @ 2.4 GHz。
- 解决什么：电池传感网自组网与路由。
- L4 关联：实验室 OK 产线挂的高频翻车协议。本轮抓 Green Power 失效 + 产线批量入网 + GP commissioning 卡死 + Install Code leave 循环，与上轮互补。

## 候选文章（4 条）

### 1. futurion.blog - Zigbee Green Power: Why Energy-Harvesting Sensors Still Vanish From Your Mesh
- 链接：https://futurion.blog/zigbee-green-power-why-energy-harvesting-sensors-still-vanish-from-your-mesh/
- 来源：futurion 实战 blog（2026-04）
- 摘要：自供电传感器在真实 mesh 消失的 4 大根因——proxy 部署差、协调器备份恢复后设备在线但 state 不更新、proxy 间 key 不一致、Matter/Thread 迁移时 GP 最后一英里困境。
- 实战点：备份恢复后 secured 错位；proxy 必须靠近 GP 端点；拓扑变后触发设备 20 次看延迟
- 推荐：入主题笔记（⭐⭐⭐⭐⭐）

### 2. 通信人家园 - Zigbee 开发避坑指南：设备无法入网？90% 是这 5 个原因
- 链接：https://www.txrjy.com/thread-1425706-1-2.html
- 来源：通信人家园 cellsnet（2026-03-06）
- 摘要：工业项目 200 节点入网 85% → 99.5% 案例。批量 20 台 3 台 IC CRC 错入网失败；volatile 误用触发路由重发 beacon；TRACE 风暴致堆栈溢出；金属货架盲区 RSSI -82dBm 临界。
- 实战点：IC CRC 是产线硬指标；-82dBm 是工业部署临界值
- 推荐：写实战案例（⭐⭐⭐⭐⭐）

### 3. NXP Community - About Green Power bi-directional commissioning
- 链接：https://community.nxp.com/t5/forums/forumtopicprintpage/board-id/wireless-connectivity/message-id/3018/print-single-message/true/page/1
- 来源：NXP 论坛（2017-07）
- 摘要：JN-SW-4170 occupancy sensor 卡在 bi-directional GP commissioning。Sensor 发 channel request → bulb 应答 → sensor 发 GP commissioning 命令 → bulb 只 broadcast notification，从未发出 GP commissioning reply (GPDF) → sensor 持续重发。
- 实战点：GP commissioning reply = GPDF 不是 ZCL；需 proxy 30s 内回 GPDF；sniffer 定位唯一手段
- 推荐：入主题笔记（⭐⭐⭐⭐）

### 4. Nordic DevZone - ZigBee install code Network left (leave type: 0)
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/84728/zigbee-install-code-network-left-leave-type-0
- 来源：Nordic DevZone 实战回帖
- 摘要：nRF sensor 反复 leave/rejoin 循环调试。`zb_set_installcode_policy(ZB_TRUE)` = 0x02（强制）非 0x01；必须 `zigbee_enable()` 前 set IC；coordinator 装对 EUI64+extpanid。根因：coordinator 加 sensor 时填错长地址。
- 实战点：IC Policy 三态 0x00/0x01/0x02；CRC16-CCITT 自算；EUI64 大小端字节序反转
- 推荐：扩 deep-dive（⭐⭐⭐⭐）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
<mavis-progress>idle</mavis-progress>