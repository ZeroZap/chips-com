# LoRa 候选素材 @ 2026-10-04 12:00

## 协议速览
- 是什么：Semtech CSS 扩频 + LoRaWAN MAC，Sub-GHz（410-493/868/915 MHz），SF7-SF12 抗干扰。
- 解决什么：电池节点 km 级远距离 + 数年寿命，典型水务/农业/工业监测。
- L4 关联：「实验室 OK 产线挂」重灾区——ALOHA 拥堵 + VFD 干扰 + SiP 漏电 4 大雷区齐活。

## 候选文章（4 条）

### 1. moltbook - LoRa node hit 12km LOS, failed at 400m in warehouse
- 链接：https://moltbook.com/post/3c844e60-953e-490f-8c64-2e86c79948ff
- 来源：moltbook 工程博客
- 摘要：SX1276 SF9 +14dBm 山谷 12 km 干净；仓库同层 400 m 一半上行失踪。根因：传送带 VFD 在 868 MHz 灌宽带噪声，RSSI 还行但 SNR -3 到 -8 dB 击穿 SF9 解调门限。修法：网关天线抬 3 m + 远离变频器 + LNA 前置腔体滤波器，SNR→+7。
- 实战点：①「RSSI 能活≠SNR 能活」必记 SNR；② VFD = 868 MHz 隐蔽噪声源；③ SF12/提功率治标，挪天线+腔体滤波治本；④ 部署前频谱分析仪扫一遍。
- 推荐：扩 deep-dive ⭐⭐⭐⭐⭐（L4 工业 VFD 干扰专题）

### 2. CSDN - LoRa SiP 低功耗节点:从选型到现场排查完整指南
- 链接：https://blog.csdn.net/weixin_29168813/article/details/164110346
- 来源：CSDN 实战长文
- 摘要：园区 2000 节点 + 3 网关 + HTTP 平台，上线 1 月后早 8-9 点失败率 40%、部分节点需断电重启。根因：整点定时上报拥堵 + 默认重传随机窗口 5 s 过小。修法：全节点开 ADR（近节点 SF10→SF7/8）+ 上报时间按节点 ID 加随机偏移到 30 min 窗口 + 重传窗口扩到 60 s，失败率 40%→<0.5%。
- 实战点：① 扩频 ≠ 无限并发，>SF9 空口容量是硬上限；② ALOHA + 整点定时 = 必然拥堵，必强制错峰；③ 重传窗口 ≥ 60 s 才能撕开拥塞；④ ADR 是「城市级 LoRa」必选项。
- 推荐：扩 deep-dive ⭐⭐⭐⭐⭐（L4 MAC 接入策略专题）

### 3. LinkedIn - LoRa Network Failure Story (Mashuk E Lahi)
- 链接：https://www.linkedin.com/posts/mashuk-e-lahi_iot-embeddedsystems-fieldengineering-activity-7471360772607021057-nVoH
- 来源：LinkedIn / World Bank 城市空气质量项目
- 摘要：城市传感网 Day 1 全 40 节点在线，Day 2 剩 16 节点。两周排查发现 4 类根因叠加：城市 RF 干扰让 LoRa 距离缩 60%、GSM 同楼地面/楼顶差 3 格、传感器运输温冲击校准漂移、PCB 冷焊点振动失效。
- 实战点：①「多根因叠加」是产线常态，单一调试不可能全覆盖；② 城市 RF 干扰是 LoRa 距离杀手；③ 冷焊点 + 运输温冲击 = 部署一周内集中爆发；④ 现场调试 = 万用表+示波器+耐心。
- 推荐：写实战案例 ⭐⭐⭐⭐（L4 多根因叠加案例）

### 4. 腾讯搜一搜 - 踩过 LoRaWAN 坑后,工厂把园区换成私网 LoRa
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_3356a8e8e0413252
- 来源：腾讯搜一搜 / 工厂设备主管自述
- 摘要：精密制造厂老周第一版 LoRaWAN 翻车 3 次：凌晨看板联动空压机房被第三方网络服务器抖动卡 10+ min；网络服务器升级要开工单等半天；两车间节点要为「跨网络接入」持续付费。改私网 LoRa（网关本地解析+边缘盒子）后联动秒级、运维自掌。
- 实战点：①「标准协议 ≠ 适用场景」——小园区不需要公共 LoRaWAN；② 第三方网络服务器 = 单点故障 + 失运维控制；③ 私网 LoRa 边缘盒子 = 数据不出厂 + 秒级联动；④ 决策第 1 问永远「数据去哪 / 谁运维 / 规模多大」再选标准。
- 推荐：入主题笔记 ⭐⭐⭐（LoRaWAN vs 私网选型专题）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
