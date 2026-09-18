# ZigBee 候选素材 @ 2026-08-25 00:00

上轮(08-23)已覆盖掉线/路由/入网/RF/工厂；本轮**新角度**：协议栈迁移/安全实战/2.4GHz 规划/OTA 陷阱/配网远程运维。

## 协议速览
- 是什么：IEEE 802.15.4 / 2.4 GHz 低功耗 Mesh，2026 L4 IoT 出货主力
- 解决什么：低功耗+多节点+自组网；产线易掉、入网易挂、密钥易泄
- L4 关联：IoT/可穿戴量产避坑 + 工控 2024 攻击 + 协议演进

## 候选文章（5 条）

### 1. ZigBee Exploited (BlackHat 2015)
- 链接：https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2015/11/20081735/us-15-Zillner-ZigBee-Exploited-The-Good-The-Bad-And-The-Ugly-wp.pdf
- 来源：BlackHat 2015 / Cognosec
- 摘要：审计 Hue/SmartThings/门锁 3 类。默认 TC key + 入网降级；ZLL Touchlink 几米外劫持；11 月**无 key rotation**。
- 关键点：① ZLL master key reddit 泄露；② ZigBeeAlliance09 默认 key 可嗅探网络密钥
- 推荐：实战案例笔记（L4 出厂安全基线）

### 2. How Zigbee Flaws Exposed Industrial IoT in 2024
- 链接：https://aviatrix.ai/threat-research-center/zigbee-industrial-2024-protocol-exposure
- 来源：Aviatrix threat-research（2024）
- 摘要：2024 真实工控 ZigBee 渗透 + 3 CVE。链：嗅探→弱 key→协调器仿冒→端点重绑→继电器劫持。完整 MITRE ATT&CK 映射。
- 关键点：① 工业 ZigBee 仍大量默认 key；② rejoin 窗口持续抓网络 key
- 推荐：入主题笔记（2024 OT 攻击 + 零信任部署）

### 3. Zigbee 与 Wi-Fi 同频段干扰（亿佰特）
- 链接：https://www.ebyte.com/news/4616.html
- 来源：成都亿佰特（国产模组厂）
- 摘要：2.4GHz 频谱图解 WiFi 1/6/11 与 ZigBee 11-26 重叠。4 策略：信道规划、5GHz 分流、Mesh 自愈、部署天线。
- 关键点：① WiFi 1 覆盖 ZigBee 11-15，6 覆盖 17-21；② 路由器"自动信道"是干扰主因
- 推荐：扩 deep-dive（2.4GHz 信道规划速查表）

### 4. ZigBee OTAU 实战：BitCloud 协议栈
- 链接：https://blog.csdn.net/weixin_29796279/article/details/162241446
- 来源：CSDN 实战博客（SAMR21 / BitCloud）
- 摘要：BitCloud OTAU 全栈：3 角色 + Header + SAMR21 256KB 分区 + 4 阶段测试 + 5 故障表 + Ubiqua 嗅探。
- 关键点：① Flash 擦写前必须解写保护；② >150 节点 OTA 已知 lpsw7828；③ 断点续传 = 每块更新 NVM
- 推荐：入主题笔记（L4 设备端 OTA 防变砖）

### 5. ZigBee 配网集群实战：Commissioning Cluster
- 链接：https://bbs.csdn.net/weixin_33217202/article/details/100160463
- 来源：CSDN 实战博客（NXP）
- 摘要：Commissioning Cluster 解产线千节点运维。4 属性集 + 远程 RestartDevice（delay+jitter）+ 4 场景配置表。
- 关键点：① u8ScanAttempts×信道×单次时长=总扫描；② u16RejoinInterval 60s→3600s 退避避风暴
- 推荐：扩 deep-dive（产线千节点参数调优表）

## 下一步
review 后：激活（挑 1-2 篇扩 deep-dive 或实战笔记）/ 改写 / 丢弃。
