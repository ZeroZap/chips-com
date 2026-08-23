# Satellite-IoT（卫星物联网）

## 定位

Satellite-IoT 是利用 LEO（Low Earth Orbit，低轨）/ MEO（Medium Earth Orbit，中轨）/ GEO（Geostationary Earth Orbit，地球同步轨道）卫星作为通信载体，覆盖地面蜂窝网络盲区（远洋、沙漠、极地、无人区、高山、灾区）的物联网接入技术。典型业务：

```text
远距离（500~3000 km LEO 仰角链路）
超低数据率（短报文 SBD 几十~几百字节）
间歇性连接（卫星过顶窗口期）
覆盖盲区（地面蜂窝不可达）
低功耗（户外设备数月~数年）
```

2024 年后成为 IoT 行业新热点——Starlink Direct to Cell 商用、3GPP NTN（Non-Terrestrial Network，非地面网络）R17 落地、华为 Mate 60 / iPhone 14 直连卫星，国内北斗短报文民用化，是 IoT 出海（航运、矿业、油气、户外追踪）的关键拼图。

## 跟其它无线技术的关系

```text
4G / 5G 蜂窝       → 授权频谱，高速，移动性好，但依赖基站（盲区无效）
NB-IoT / Cat-M     → 蜂窝 IoT，深覆盖 20dB，仍需基站
LoRa / Sigfox      → 免许可 Sub-1GHz，10~15 km 地面，仍需地面网关
BLE / ZigBee       → 短距 10~100 m，本地通信
Satellite-IoT      → 覆盖海洋 / 沙漠 / 极地 / 灾区，地面网络盲区的"最后一公里"
```

互补关系：Satellite-IoT 不替代地面网络，而是"地面网络不可达时的兜底"。典型混合方案：正常用 NB-IoT 蜂窝省流量，紧急情况切到卫星。

## 5 大技术路线对比

| 路线 | 轨道 | 典型业务 | 频段 | 短报文容量 | 终端 | 国内可用 |
| --- | --- | --- | --- | --- | --- | --- |
| **NB-IoT NTN** | LEO + GEO | 物联网直连卫星 | L/S 频段（运营商） | NB-IoT 标准 payload | 蜂窝模组升级 | 2025+ 试商用 |
| **北斗短报文（BDS RDSS）** | GEO + IGSO | 双向短报文 + 定位 | L/S 频段 | 1000 汉字 / 次 | 北斗 RDSS 模组 | 已商用（民用） |
| **Iridium / 铱星 SBD** | LEO 66 颗 | SBD 短数据 + 话音 | L 频段 | 340 B / 消息 | Iridium 模组 | 需卫星电话卡 |
| **Starlink IoT Direct to Cell** | LEO | IoT 直连 + 短信 + 通话 | T-Mobile 1.9 GHz 段 | 未来 NB-IoT 模式 | 改版 LTE 模组 | 暂未覆盖国内 |
| **Garmin inReach / SPOT** | LEO（Iridium / Globalstar） | 户外双向 SOS + 短报文 | L/S 频段 | 160 字符 | 专用终端 | 已商用 |

## 关键技术概念

- **LEO / MEO / GEO**：LEO 500~2000 km（Iridium、Starlink），时延 20~50 ms；MEO 5000~25000 km（北斗 MEO、GPS），时延 100~300 ms；GEO 35786 km（北斗 GEO、Inmarsat），时延 ~600 ms。
- **链路预算（Link Budget）**：卫星到地面 ~600 km 自由空间损耗约 170 dB（400 MHz），地面终端 EIRP 5~10 dBW + 高增益天线（8~12 dBi）勉强够。NTN 链路预算比地面 NB-IoT 差 30+ dB。
- **多普勒（Doppler）**：LEO 高速运动（7.5 km/s），400 MHz 频段多普勒频偏 ~±10 kHz，必须做频率预补偿。
- **时延（Latency）**：LEO 单跳 20~50 ms，GEO 单跳 ~600 ms，IoT 短报文应用对时延不敏感。
- **卫星过顶窗口**：LEO 卫星过顶单颗 ~10 分钟，整组星座（Iridium 66 颗）几乎全时段覆盖。
- **认证 / 激活**：Iridium SBD 必须 IMEI 注册、激活 MO/MT（Mobile Originated / Mobile Terminated，移动发起 / 移动终止）；北斗短报文需入网注册 + 加密卡。

## 关键芯片 / 模组

| 模组 | 厂商 | 路线 | 特点 |
| --- | --- | --- | --- |
| 移远 BG95-M1 / BG95-M3 | 移远 | NB-IoT NTN | 兼容 BG95 平台，R17 NTN 升级 |
| 移远 BG77 | 移远 | NB-IoT NTN | 超小 LCC，卫星物联网卡 |
| 移远 CC200A | 移远 | NB-IoT NTN + LTE | Linux OpenCPU |
| 芯讯通 SIM7000G | 芯讯通 | NB-IoT NTN + GNSS | 多频段 |
| 芯讯通 SIM7080G | 芯讯通 | NB-IoT NTN + GNSS | Cat M1 / NB1/NB2 / GNSS |
| 中斗微星 ZD-V100 | 中斗微星 | 北斗短报文 | 北斗三号 RDSS + RNSS |
| 中电科 CETC-9 | 中电科 | 北斗短报文 | 国产化加固型 |
| 华力创通 HWA-RDSS-101 | 华力创通 | 北斗短报文 | 模块化设计 |
| Iridium 9602 / 9603 | Iridium | SBD | 短数据模组经典款 |
| Iridium 9770 | Iridium | SBD + Edge | 新一代 IoT 优化 |
| Quectel BG95-M3 + NTN firmware | 移远 | NB-IoT NTN | 主流海外方案 |
| Garmin inReach Mini 2 | Garmin | Iridium 双向 | 户外成品（不开放） |
| SPOT X | SPOT | Globalstar | 户外双向（不开放） |
| Nordic nRF9160 + NTN | Nordic | NB-IoT NTN | 集成应用核 |

## 抓包 / 调试工具

| 工具 | 适用路线 | 优势 | 限制 |
| --- | --- | --- | --- |
| QLog / QXDM | NB-IoT NTN | 完整 RRC / NAS 信令 | 仅高通平台 |
| Iridium Analyzer | Iridium SBD | 解析 SBD MT/MO 信令 | 需 Iridium 设备 |
| 北斗短报文 log（RDSS log） | 北斗短报文 | 解析 RDSS 帧格式 | 需北斗模组 |
| 串口 log + AT 回显 | 通用 | 必备、最快 | 浅层 |
| SDR（HackRF / LimeSDR） | L/S 频段 | 看空中 RF | 需射频经验 |
| Wireshark + RDSS dissector | 北斗 | 解析北斗协议 | 需自配 |
| 协议分析仪 CMW500 + NTN 选件 | NB-IoT NTN | 模拟卫星信道 | 贵 |

## 嵌入式产线典型故障

- **NB-IoT NTN 卫星搜不到**：GSE（GNSS Satellite Ephemeris，全球导航卫星系统星历）未下发、星历过期（>3 小时）。
- **北斗短报文发送失败**：入网注册未完成（卡号未授权）、入站频点未对准、电文长度超 1000 汉字。
- **Iridium SBD 拨号失败**：IMEI 未注册、MO/MT 通道关闭、SBD 服务中心不可达。
- **链路预算不足**：天线增益不够（< 5 dBi）、仰角过低（< 15°）、城市峡谷多径。
- **多普勒频偏**：LEO 过顶 400 MHz 多普勒 ~±10 kHz，模组未做预补偿。
- **Starlink IoT 未认证**：T-Mobile 频段协调未完成，模组固件版本不匹配。
- **时延过长**：GEO 卫星 600 ms 单跳 + 二次握手，MQTT keepalive 间隔设置不当。
- **位置漂移**：GNSS 卫星数 < 4 颗，定位误差大。
- **电文丢失**：LEO 过顶窗口期短（< 10 min），数据量超窗口容量。
- **资费卡欠费**：Iridium 短报文按条计费（$0.05~$0.50/条），量产监控务必加计费预警。

## 延伸阅读

- `bus/satellite-iot-practical.md` 调试流程速查 / 5 秒定位 / 错误码表
- `bus/satellite-iot-deep-dive.md` 协议栈 / 卫星注册 / 链路预算 / 多普勒补偿深挖
- `bus/satellite-iot-failure-cases.md` 产线实战案例（NB-IoT NTN / 北斗 / Iridium 等 8-9 例）
- `bus/satellite-iot-index.md` 主题地图 + 读者路径
