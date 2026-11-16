# LoRa / LoRaWAN 候选素材 @ 2026-10-17 12:00

## 协议速览
- 是什么：1GHz 以下免授权 LPWAN + LoRaWAN MAC
- 解决什么：电池节点公里级通信、私有自建网关
- L4 关联：IoT/可穿戴远距低功耗主力；实战 ≠ 实验室 ≠ 产线 ≠ 量产

## 候选文章（5 条）

### 1. LoRa模块配置到LoRaWAN网关OTAA入网排查实操分享
- 链接：https://www.eefocus.com/article/2103231.html
- 来源：与非网
- 摘要：OTAA 入网 4 类故障域分层定位（密钥/EUI→频段→网关→节点）
- 实战点：密钥+DevEUI+区域频段优先查；"卡网关"=节点日志 OK 但后台无上行；默认信道必须跟现场网关对齐；调试期临时改 Class C
- 推荐：**写实战案例**（4 类故障域可作 L4 排查清单模板）

### 2. 基于LoRaWAN的智能能源系统实践:从选型到踩坑全记录
- 链接：http://www.sheratonhq.com/news/80827
- 来源：sheratonhq
- 摘要：420 节点能源项目 3 个月 P0 全网数据延迟；海量采集+OTA 硬仗
- 实战点：真凶=海量点位+默认频段+ADR 联动吃光容量；关 ADR+固定 SF+错峰；OTA 分组灰度/断点续传/回滚必备；4G 回传隐性瓶颈（UDP vs 服务器收包差定位）
- 推荐：**入主题笔记**（大规模 LoRaWAN + P0 复盘，生产级实战）

### 3. We Deployed IoT Water Sensors on a Kenyan Farm. Here's What Broke.
- 链接：https://dev.to/ascorpi/we-deployed-iot-water-sensors-on-a-kenyan-farm-heres-what-broke-595h
- 来源：dev.to
- 摘要：肯尼亚农场 ESP32 土壤水分传感器实地部署 8 项失效清单
- 实战点：IP65≠防水（温循环+喷淋→密封失效，铠装电缆底线）；太阳能板被鸟粪落叶→4 天电池耗尽；白蚁啃咬普通电缆；2 节点死于物理环境非软件 bug
- 推荐：**写实战案例**（L4 经典"防 IP 等级≠防真实环境"反模式）

### 4. 无线收发芯片选型实战指南:从物理约束到产线鲁棒性
- 链接：http://www.lpqz.cn/news/143532
- 来源：lpqz.cn
- 摘要：Sub-1G 芯片选型+产线鲁棒性+晶振温漂+PA 频谱泄露
- 实战点：SX1262+868MHz+切比雪夫天线 EIRP 15.2→18.7dBm，距离 800m→1.8km；AT 切晶振-40°C 频偏 30ppm→接收频率飘出灵敏度带；CE/FCC 868MHz 二次谐波→SAW 滤波器+BOM 0.8 元；拆解 200+ 终端→稳定 1 年+ 设备都遵循"保守原则"
- 推荐：**入主题笔记**（物理层+产线鲁棒性，跟 IoT/可穿戴硬件选型相关）

### 5. From LoRaWAN Pilot to Production: Why 70% of IoT Projects Never Scale
- 链接：https://lorawan-consulting.com/articles/pilot-to-production
- 来源：lorawan-consulting.com
- 摘要：PoC（10 节点）→ 生产部署 70% 项目卡死 6 个共性根因
- 实战点：PoC 1 网关≠生产多网关负载均衡+去重；ADR 10 节点完美→400 节点容量崩溃；电池"3 年"→"3 月"；设备身份/密钥分发独立子系统；监控升级到 NS 队列深度+重传率+丢包分布
- 推荐：**写实战案例**（70% 量产失败根因，L4 商业反模式彩蛋）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
