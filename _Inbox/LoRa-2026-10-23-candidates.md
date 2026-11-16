# LoRa 候选素材 @ 2026-10-23 00:00

## 协议速览
- 是什么：Sub-GHz Chirp 扩频 + LoRaWAN MAC，SX12xx 为射频主力
- 解决什么：电池供电、上报稀疏、弱覆盖（表井 / 金属箱）下的远距离遥测
- 跟 L4 主题的关联：ALOHA 无仲裁上行 + CAD 退避，根因就是"碰撞—重试"，与总线仲裁失败同构

## 候选文章（4 条）

### 1. LoRa智能计量实战：从芯片选型到现场部署的完整指南
- 链接：http://www.hqwc.cn/news/1395233.html
- 来源：技术社区长文（智能计量方向）
- 摘要：以电/水/气表实战口吻讲 LoRa 选型、协议栈移植与现场坑点，重心在碰撞治理。
- 关键实战点：
  - CAD 会增功耗，只在入网时开，平时靠随机退避降碰撞
  - 上行周期各节点随机加 0–60s 偏移，显著提升整体网络容量
  - 外壳必须 IP67 带天线孔，换壳成本远高于一次选对
- 推荐动作：扩 deep-dive

### 2. 工业物联网网关子设备数据通信盲区：成因、排查与根治
- 链接：https://blog.csdn.net/weixin_29188997/article/details/164451879
- 来源：CSDN（现场实施视角）
- 摘要：把现场"曲线断段"拆成时间 / 空间 / 逻辑三类盲区，给四步排查法与根治方案。
- 关键实战点：
  - 算例：12 台设备各响应 80ms + 间隔 50ms ≈ 1.5s/轮，单台超时就拖垮整轮
  - 补传数据时间戳对不上真实采集时刻，曲线"看着完整"但无精度
  - 均值插值 / 跳点连接掩盖缺失，仅完整率对工况时暴露
- 推荐动作：写实战案例

### 3. LPWAN 节点设计实战：从 LoRa 选型到低功耗部署
- 链接：https://blog.csdn.net/weixin_29164497/article/details/164110572
- 来源：CSDN
- 摘要：硬件选型 → 功耗建模 → ADR / Duty Cycle / OTAA 重试 → 现场排查，含入网失败实战。
- 关键实战点：
  - Join 重试用指数退避 + 抖动：30s 起翻倍、上限 1h、叠加 10–30s 随机；否则一台节点失败就变相 DDoS 整个网关接收通道
  - 铁皮柜 / 地下管廊内安装导致入网困难，点位须现场实测而非照图纸定
  - 做 OTA 前必须确认 Flash 容得下 Bootloader + A/B 两份镜像
- 推荐动作：扩 deep-dive

### 4. 21 IoT Deployment Failures: Connectivity
- 链接：https://iotclass.org/testing-validation/iot-deployment-failure-case-studies.html
- 来源：IoT Class 案例库
- 摘要：把连通性故障当"证据包"读；LoRaWAN 章节点名 link budget、SF、ADR、duty-cycle、网关位置。
- 关键实战点：
  - 每个失败案例须落成可执行前置控制项：现场测试 / 负载测试 / 凭证检查 / 灰度门禁 / 回滚预案
  - 明确点名 duty-cycle 限流与 downlink 稀缺两类被低估的坑
- 推荐动作：入主题笔记

## 备选（偏教程向，未展开）
- STM32WL LoRaWAN 入网调试（21IC）https://bbs.21ic.com/icview-3520439-1-1.html — CN470 需改 RX2 频率

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃