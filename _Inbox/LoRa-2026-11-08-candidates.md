# LoRa 候选素材 @ 2026-11-08 12:03

## 协议速览
- 是什么：Sub-GHz Chirp 扩频(CSS) 物理层 + LoRaWAN MAC，SX126x 射频、SX1302 网关基带
- 解决什么：电池供电、上报稀疏、弱覆盖（井下/金属箱/洞窟/牧场）下的远距离遥测
- 跟 L4 主题的关联：ALOHA 无仲裁上行 + CAD 退避，根因是「碰撞—重试—丢包」，与总线仲裁失败同构

## 候选文章（4 条）

### 1. 石窟微环境监测实战：LoRaWAN 双模协同系统
- 链接：https://blog.csdn.net/weixin_28718793/article/details/166154113
- 来源：CSDN 文保现场（建设 7 个月，运行 1 年多）
- 摘要：470MHz 比 2.4GHz 少衰减 15-25dB，一年 120 万条记录。
- 关键实战点：
  - SX1262 @SF12 灵敏度 -137dBm，比 ZigBee/WiFi 高 20dB；拐角点 -117dBm 投递率仅 95%
  - 调网关天线方向靠多径反射提到 98%；STM32L412 停机 1.1uA + RAK7289 八通道
- 推荐动作：扩 deep-dive

### 2. Elecrow：LoRa 模组高精度测试与质量保证体系
- 链接：https://www.elecrow.com/blog/testing-quality-assurance-system-for-lora-modules.html
- 来源：Elecrow 代工产线量产 QC
- 摘要：模组量产全流程 QC，DFM、拼板、专用夹具 + 测试固件、整机老化。
- 关键实战点：
  - 频谱仪测 Tx 功率/Rx 灵敏度/SNR/杂散，信号发生器 + 万用表配合
  - 3D-SPI、AOI、X-ray（查 BGA/QFN 空洞短路）、ICT 四层检测；功能测试 <1 min/台
- 推荐动作：入主题笔记

### 3. LoRaWAN Link Check：内置 RF 自测替代人工勘场
- 链接：https://www.macnman.com/success-stories/blogs/built-in-lorawan-rf-testing-sensor-installation
- 来源：Macnman 安装现场实战
- 摘要：人头高度勘场器测 ≠ 安装点真值，金属柜/冷库可再吃 10-20dB。
- 关键实战点：
  - RSSI/SNR 说下行，link margin + 网关数说上行；弱下行是入网失败与 ADR 异常根因
  - SF12 小包空口时长约为 SF7 的 25 倍，位置选错直接吃电池
- 推荐动作：扩 deep-dive

### 4. UND-1101 网关 + LPMDL-1103 记录仪现场实测（保加利亚）
- 链接：https://thingslog.com/blog/2019/05/09/thingslog-und1101-and-lpmdl-1103-lora-field-test-in-flat-rural-terrain-around-the-area-of-elin-pelin
- 来源：ThingsLog 厂商实测（ttnmapper 数据）
- 摘要：功率档 1、SF11、9dBd 天线，覆盖 1 镇 + 10 村。
- 关键实战点：
  - 内置 2dBi 与外置 2dBi 天线 SNR 差 2-4dB；「锅盖住」两种天线都掉 5dB
  - 无直视 6-7km，有直视 10-20km；井下/金属箱至少额外留 5dB 链路预算
- 推荐动作：写实战案例

## 备选（未展开）
- 哥伦比亚草原牛项圈 LoRaWAN 实地试验（13 万+ 上行，RAK WisBlock+太阳能）https://bioengineer.org/?p=462122
- 路灯改造 LoRaWAN 监测（MDPI 2024，德国 Ilmenau 52 盏灯试点）https://www.mdpi.com/2673-4117/5/1/28/html
- 本轮排除黑名单域名 hqwc.cn、kwkr.cn（同文多域名洗稿，命中 2 条）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
