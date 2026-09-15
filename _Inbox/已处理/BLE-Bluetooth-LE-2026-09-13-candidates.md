# BLE / Bluetooth LE 候选素材 @ 2026-09-13 12:00

## 协议速览
- 是什么：2.4 GHz 跳频 + GATT 服务的低功耗短距无线协议，IoT/可穿戴/工业传感主力
- 解决什么：电池供电设备（年续航级）间歇性小包上报 + 配置下行
- L4 关联：产线 Fail 闭环 / 工业抗干扰 / GATT 状态机是 L4 实战池最大单一来源

## 候选文章（5 条）

### 1. BLE Data Integrity Failures (Out-of-Order Segments) — Nordic DevZone
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/125365/ble-data-integrity-failures-out-of-order-segments/565935
- 来源：Nordic 官方 Q&A 论坛
- 摘要：BLE→Wi-Fi 网关做 800 KB 大文件传输（GATT notify + 应用层 SAR），高负载下包乱序。Gateway/Node/Wi-Fi TCP 三方日志时间戳对齐，定位 Wi-Fi 抢占中断致 `sfp_crc_fail`，SAR 重组失败、A2 重复。
- 实战点：三方日志时间戳相关法定位跨协议竞争；SAR 必须把"包乱序"当正常态；BLE+Wi-Fi 共存是同 MCU 硬坑
- 推荐：扩 deep-dive 进 BLE/Wi-Fi 共存主题笔记

### 2. 蓝牙产线测试 Fail 的产品怎么处理 — 华汉仪器
- 链接：https://www.hhins.cn/xingyedongtai/12-392.html
- 来源：华汉仪器（产线测试方案商）博客
- 摘要：把产线 Fail 拆三类（误测/参数偏移/硬故障），三站式闭环：复测验证站→维修与修复验证站→报废与统计分析，SN 全程追溯 + MES Fail 跟踪模块。
- 实战点：误测站必须换机型复测（屏蔽箱门/线缆/夹具是产线最大噪声源）；维修后跑完整测试序列；复测通过率/维修成功率/报废率是产线 3 指标
- 推荐：写实战案例（"产线 BLE 测试三站闭环"），L4 通用测试方法学可复用

### 3. [PATCH v3] Increase LE connection timeout for industrial sensors — linux-bluetooth
- 链接：https://marc.info/?m=177211875328431
- 来源：linux-bluetooth 邮件列表（Volvo Group Dajid Morel 提交）
- 摘要：TE Connectivity BLE 压力传感器在工厂 RF 噪声下手握手需 12.5s，Linux kernel `hci_conn.c` 硬编码 2s timeout 必失败。empirical 证明 userspace socket 不覆盖 HCI 内核中止。patch 把 `conn_timeout` 提到 20s。
- 实战点：工业传感器握手 latency 远超 2s 默认值；userspace 与 kernel HCI timeout 是两套；BlueZ + Ubuntu Core 22 真实工业部署
- 推荐：扩 deep-dive BLE 连接 timeout 选型（仓库缺），入主题笔记

### 4. 从信号完整性视角重构蓝牙连接逻辑 — tsight.io
- 链接：https://tsight.io/articles/15176126?lang=zh
- 来源：tsight.io（工业 BLE 协议分析博客）
- 摘要：Ellisys 抓包看工业现场真实断连：满屏 `LL_CONNECTION_UPDATE_IND` 超时 + MIC Failure，物理层 ACK 优先级被数据处理抢占致断链。给信道图谱避让 + T_IFS 时序偏差 + 天线去耦 4 条工程建议。
- 实战点：跳频+信道图谱动态剔除是被忽视的生存机制；ACK 优先级 > 数据处理；Channel Map 屏蔽 10–20 个拥堵信道换鲁棒性
- 推荐：入主题笔记（信号完整性/跳频序列/T_IFS 时序），L4 进阶深挖

### 5. SweynTooth — 12 vulnerabilities impact millions of BLE devices
- 链接：https://breachspot.com/news/vulnerabilities/twelve-vulnerabilities-impact-millions-of-bluetooth-le-devices/
- 来源：Breach Spot / 新加坡科技与设计大学披露
- 摘要：12 个 BLE SoC SDK 漏洞，影响 480+ 产品（Samsung/Fitbit/Xiaomi/Medtronic 起搏器/VivaCheck 血糖仪等）。TI/NXP/Cypress/Dialog/Microchip/ST/Telink SDK 在 LL 帧处理/配对/加密上实现缺陷。Dialog/Microchip/STM 仍有未修补。
- 实战点：BLE SoC 选型不能只看 spec，要查 CVE 历史与补丁节奏；医疗/工业/可穿戴被点名；物理近距+协议层=攻击面
- 推荐：写实战案例（"BLE SoC 选型必查 CVE"），L4 安全章节素材

## 下一步
等你 review 后决定：激活（≥3 篇扩 deep-dive）/ 改写（只留 1-2 篇）/ 丢弃（本轮跳过）
