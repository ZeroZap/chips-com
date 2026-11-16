# ZigBee 候选素材 @ 2026-11-07 12:04

## 协议速览
- 是什么：IEEE 802.15.4 低功耗 Mesh，协调器/路由/终端三角色自组网。
- 解决什么：多节点组网 + 链路自愈，不依赖 Wi-Fi AP。
- L4 关联：与 Thread/Matter 同属 2.4GHz 家庭栈，补协调器迁移、RF 一致性、路由。

## 候选文章（5 条）

### 1. 70 设备原地换协调器栈（ember→zstack）
- 链接：https://casey.berlin/writings/2026/06/zigbee-coordinator-migration-blueprint
- 来源：独立工程师实机 runbook
- 摘要：不重配对换栈，一周挖出三层叠加故障，72h 老化 92 次探测零失败。
- 实战点：① 刷错板型固件→PA 接错 GPIO，LQI 腰斩且日志无提示；② Wi-Fi AP 挪到信道 11，Zigbee ch23/24 扫描 226/255 饱和，屏蔽后 0/1
- 动作：写实战案例（LQI 213/148/76 三代对照）

### 2. Zigbee 模组量产射频自动化测试与一致性管控
- 链接：https://www.21ic.com/a/1013725.html
- 来源：21ic 产线方案（STM32H7 + 8 通道射频切换）
- 摘要：实验室频谱仪调好的 RF 一上产线就崩，给三层架构秒级测试。
- 实战点：① 人工逐点单台 >30s 有人为误差，撑不住年产数十万级；② 三层=主控/射频切换/工位，16 路光耦隔离 IO 防误触
- 动作：扩 deep-dive（治批次离散度：功率/灵敏度超标）

### 3. STM32WB ZigBee 配网：从按键入网到安全运营
- 链接：https://shequ.stmicroelectronics.cn/thread-869208-1-4.html
- 来源：ST 官方社区（拆 AN5627）
- 摘要：把 R22 规范 600 页配网章节压成产线 30 秒流程。
- 实战点：① 6 条入网路径耗时：集中式 3-8s、Touchlink 1-3s、Find&Bind 5-15s、ZCL 10-30s；② 密钥归属：安装码/TCLK/Global Key 谁能进二维码
- 动作：入主题笔记（配网路径表可抄速查表）

### 4. Zigbee Source Routing：关掉反而治好掉线
- 链接：https://futurion.blog/zigbee-source-routing-when-turning-it-off-fixes-weird-dropouts
- 来源：独立博客方法论
- 摘要：源路由预设整条跳数路径，混牌消费网路径一变整条僵死。
- 实战点：① 症状=挪动关键插排后整组电池传感器集体掉线、纸面 LQI 好行为差；② A/B 纪律=基线快照→低峰只改一个变量→等收敛→变差立即回滚
- 动作：写实战案例（物理层优先：协调器别塞金属背板/USB 噪声口）

### 5. ESP32+CC2652P 开源 Zigbee 网关硬件
- 链接：https://damodev.csdn.net/6a4357ee10ee7a33f2848671.html
- 来源：CSDN 技术文（开源网关全栈）
- 摘要：ESP32 跑 TCP/MQTT/Web/OTA，CC2652P 跑 Z-Stack，含产线烧录路径切换。
- 实战点：① DIP 拨码在 PCB 层切串口：WiFi 模式级联烧录、USB 模式直连变 CDC，产线免跳线；② 20dBm 比 CC2652R 高 6dB→同天线距离 ×2.5，代价是弃陶瓷天线改微带（-3dB）
- 动作：入主题笔记（BAL-SM-0012 巴伦 + BPF-2400M，板 41×44×5mm）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
