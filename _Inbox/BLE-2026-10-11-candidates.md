# BLE 候选素材 @ 2026-10-11 12:00

## 协议速览
- 是什么：低功耗短距无线，2.4 GHz ISM，广播+连接+GATT
- 解决什么：手机-外设可发现/可连接/可加密通道，IoT/可穿戴事实标配
- 跟 L4 关联："实验室 OK 产线挂"高发——多模共存/屏蔽/批次漂移全是 L4 坑

## 候选文章（5 条）

### 1. 智能电瓶车蓝牙硬件连通性测试方案全复盘
- 链接：http://www.bryh.cn/news/237000
- 来源：尧图网络
- 摘要：电瓶车一车多蓝牙模组（仪表/BMS/中控/锁）产线验收，4 层分层法+屏蔽箱+衰减器
- 实战点：① 扫描不到=射频层，配对秒掉=链路层，已连无反应=应用层；② 屏蔽箱+0~60dB 衰减器复现远距；③ 抽检只留核心用例控节拍
- 推荐：写实战案例（一车多模+屏蔽箱方法论补硬件测试视角）

### 2. Fixing Zephyr Bluetooth LE Connection Timeout Issues
- 链接：https://www.embeddedsoft.net/fixing-zephyr-bluetooth-le-connection-timeout-issues
- 来源：EmbeddedSoft.net
- 摘要：Zephyr supervision timeout 根因分析，medical/IIoT/consumer 影响，从 reason 0x08 反推
- 实战点：① Supervision × (1+Slave Latency) > 真实睡眠累计；② Pairing 后丢 = bond storage 丢/IRK 错；③ reset reason 分 POR/PIN/WDT
- 推荐：扩 deep-dive（Zephyr/RTOS 视角补 Hubble 协议栈空缺）

### 3. 嵌入式 WiFi 与蓝牙调试实战
- 链接：http://www.mhpq.cn/news/1086633
- 来源：尧图网络（嵌入式分享 #21）
- 摘要：12 年 WiFi/BT 调试经验，5 问预检清单 + HCI 层分界法则
- 实战点：① 真案：隔墙连不上 = SDK 国家码 TX power 被压低几 dBm；② TX 峰值 300mA 纹波 = 概率连不上；③ 晶振 ±20ppm 是底线
- 推荐：入主题笔记（5 问+HCI 分界法则作 BLE 调试骨架）

### 4. 嵌入式偶发 Bug 排查实战：蓝牙断开取证与批次对照
- 链接：http://www.tzjp.cn/news/396310
- 来源：尧图网络（拖半年真案）
- 摘要：换机/录屏/批次对照三阶法定位 BLE 偶发断开，真凶是新批次天线匹配电容 10pF→12pF
- 实战点：① 录屏+日志时间轴对齐 = 偶发→必现；② 批次对照定位器件漂移最强；③ HC05 排查配 JFlash 烧录对照表
- 推荐：写实战案例（电容批次错配是 IoT 产线头号 L4 杀手）

### 5. BLE L2CAP 详解：MTU、ECN 流控与丢包
- 链接：见 web_search 缓存
- 来源：尧图网络（L2CAP 实战长文）
- 摘要：3 真项目卡点：nRF52840 工业 72h 零丢包、DA1469x 医疗 ECG、ESP32-S3 OBD-II AT 透传
- 实战点：① PHY 251B 扣 LL 头 = L2CAP 必须分片；② ECN 信用算错 = notify 失败；③ Bluedroid L2CAP 比 NimBLE 更稳
- 推荐：扩 deep-dive（L2CAP 是 BLE 笔记常被忽略的"承重墙"）

## 下一步
等 review：激活 / 改写 / 丢弃
下次 ~24h 后按轮询表，下个非 BLE 协议（CAN-FD）