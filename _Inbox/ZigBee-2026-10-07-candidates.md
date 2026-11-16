# ZigBee 候选素材 @ 2026-10-07 00:00

## 协议速览
- 是什么：基于 IEEE 802.15.4 的低功耗 mesh 协议，250 kbps @ 2.4 GHz。
- 解决什么：电池传感网自组网与路由，工业/智能家居低功耗场景。
- 跟 L4 主题的关联：「实验室 OK 产线挂」L4 高频翻车协议。本轮抓**官方 bug tracker + 固件版本战 + 路由表维护 + 工程化排障**，与上次 RF/退避/PAN ID/HA 互补。

## 候选文章（4 条）

### 1. Nordic Semiconductor - nRF Connect SDK Known Issues
- 链接：https://docs.nordicsemi.com/bundle/ncs-2.0.1/page/nrf/known_issues.html
- 来源：Nordic 官方 docs
- 摘要：nRF Connect SDK Zigbee 已知问题。KRKNWK-11826（满员 + 1 个离开后 beacon flags 不更新 → 永远拒绝新设备）和 KRKNWK-12017（Device Announcement 未被 parent ACK → joiner 停止）。两条都有 workaround。
- 实战点：KRKNWK-11826 fix 调 `bdb_start_top_level_commissioning(ZB_BDB_NETWORK_STEERING)`；KRKNWK-12017 fix 监听 `ZB_NLME_STATUS_INDICATION` + `ZB_NWK_COMMAND_STATUS_PARENT_LINK_FAILURE` 后软件复位。
- 推荐动作：入主题笔记（⭐⭐⭐⭐⭐）

### 2. GitCode - Z-Stack 固件网络稳定性问题分析
- 链接：https://blog.gitcode.com/3f1089ec9a65cfe3818fcdd6c0d274ca.html
- 来源：GitCode 博客
- 摘要：Z-Stack 20240710 新固件崩溃实战。`0x11: BUFFER_FULL` 崩溃，物理重新插拔协调器才能恢复。60-120 设备/mesh 规模。降级到 20221226 后正常。
- 实战点：60+ 设备是高负载警戒值；0x11 = 缓冲池耗尽 + 调度队列满；新固件规模适配前不能上关键业务。
- 推荐动作：扩 deep-dive（⭐⭐⭐⭐）

### 3. tsight.io - Zigbee 自组网的拓扑崩塌
- 链接：https://tsight.io/articles/10805159
- 来源：tsight.io 技术博客
- 摘要：化工厂 Zigbee 传感网路由抖动 → 广播风暴 → 网络死锁。链路状态表 3 大代价：开销爆炸（带宽 × 节点数²）、路由震荡（LQI 跳变切父节点）、路由表溢出（终端失联）。教科书"自愈"实为"瘫痪"。
- 实战点：广播开销 N² 增长，高密度硬约束；"频繁切父节点"根因 LQI 跳变；路由表 12-20 条，超即剔旧路径。
- 推荐动作：写实战案例（⭐⭐⭐⭐）

### 4. zigbeeguru.com - Why Zigbee Devices Lose Connection (Real Fixes)
- 链接：https://zigbeeguru.com/?p=75/
- 来源：Zigbee Guru（欧洲住宅/酒店调试实战）
- 摘要：欧洲住宅 + 酒店工程化排障清单。7 步诊断：协调器位置 → Wi-Fi 干扰 → 路由器密度 → 终端休眠 → 固件/网关 → 楼宇材料 → LQI/拓扑图。协调器藏金属机柜 = 衰减 10-20 dB = "随机"掉线。
- 实战点：协调器藏金属机柜 = 10-20 dB 衰减（RF 头号翻车）；Wi-Fi 高占空比饱和 → 信道不重叠仍挣扎；1 router / 5-10 end device = 骨架稳态比。
- 推荐动作：入主题笔记（⭐⭐⭐）