# LoRa / LoRaWAN 候选素材 @ 2026-08-15 00:00

## 协议速览
- 是什么：Sub-GHz LPWAN，物理层 Semtech 专利 LoRa 扩频 + LoRaWAN MAC；Class A/B/C 三模式
- 解决什么：km 级远距离 + μA 级休眠，填 Wi-Fi（短距）和蜂窝（高功耗）之间的空档
- 跟 L4 关联：IoT/可穿戴优先方向；典型：表计/环境监测/资产追踪/智慧路灯/油田水利

## 候选文章（5 条）

### 1. LoRaWAN 低功耗优化与通信调试（4 维度量产实战）
- 链接：https://blog.csdn.net/lin280340404/article/details/160683338
- 来源：CSDN（嵌入式深耕 24，15 年经验）
- 摘要：野外 LoRaWAN 量产 4 维优化（硬件/软件/参数/通信），续航 6-12 月→3-5 年，15km+ 开阔地、丢包<1%
- 实战点：① LDO Iq<1μA（XC6206=0.7μA）② ADR 4 坑：开启时机/移动禁用/ACK 10:1/回退 ③ SF 黄金选择：近 SF7-9/中 SF9-10/远 SF11-12
- 推荐：**扩 deep-dive**（功耗建模+Class 实测，并入《L4 协议对比表》）

### 2. LoRaWAN 智能路灯：Dragino LC01 到云端（端到端）
- 链接：https://blog.csdn.net/weixin_33675507/article/details/85487534
- 来源：CSDN（项目复盘+工程化部署）
- 摘要：220V 硬件→TTS OTAA→Class C 远程→ThingsBoard 仪表盘→量产全链路，4 类故障
- 实战点：① 零交叉触发专利解决 SSR 电弧 ② 零线虚接是 220V 输出失效最高发故障 ③ 工业规划：RSSI/SNR 勘测/SPO 防雷/IP65 接线盒
- 推荐：**入主题笔记**（《LoRaWAN 部署工程化》专题）

### 3. LoRaWAN stack 移植笔记（STM32 踩坑）
- 链接：https://www.cnblogs.com/answerinthewind/p/6272349.html
- 来源：博客园（AnswerInTheWind LoRaMac-node 移植系列）
- 摘要：L151CBT6 移植 L051C8T6 的 4 个真实坑（JLink/BOOT0/RTC/中断）
- 实战点：① BOOT0 悬空→一行不跑，飞线 GND 即解 ② RTC 不进中断：局部改全局无理由解决 ③ P2P 3 参数配对：iqInverted/preambleLen/SYNCWORD，接收 preamble 必须 > 发射
- 推荐：**写实战案例**（冷启动排查，入《L4 调试模式》案例库）

### 4. LORA 通信距离实测（华东 433MHz 徒步）
- 链接：https://blog.csdn.net/ydgd118/article/details/107731225
- 来源：CSDN（实地徒步）
- 摘要：433MHz/125kHz/SF11/CR4-5，3.5dB 弹簧 vs 15dB 船桨，徒步 2.9km，货车 2m 阻挡衰 0.1km+
- 实战点：① 433MHz 实测 ≈3km（乡镇/SF11）② 临时障碍 2m 即衰 0.1km+ ③ 手持 vs 架设 RSSI 差异显著（人体吸收）
- 推荐：**入主题笔记**（真实距离补《L4 协议对比》频段覆盖表）

### 5. 浅谈 lorawan 调试心得（多频段多基站）
- 链接：https://blog.csdn.net/zhufeng88/article/details/76651858
- 来源：CSDN（CLAA 中兴 + 433/868/915 多厂家）
- 摘要：横跨 470/433/868/915 四频段，3 个真实坑，含 0.1MHz 频偏诊断
- 实战点：① 晶振电容不匹配→频偏 0.1MHz，频谱有信号但基站收不到（查 0x06/0x07）② 915 上行正常下行失败：官方 DR4+ 强改 BW=500K 但基站只支持 125K ③ 单包 ≈200 字节，按 datarate 分包
- 推荐：**写实战案例**（频偏诊断+官方代码兼容陷阱，入《L4 典型 Bug 库》）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
