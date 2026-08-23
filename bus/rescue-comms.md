# 救援通讯（Rescue Communications）

## 定位

救援通讯是"人在失联场景下还能把求救信号送出去"的一类通信技术总称，覆盖户外登山、海上船舶、航空、火灾地震、极地探险等常规蜂窝网（Cellular Network）覆盖缺失或拥塞的场景。跟 BLE/Wi-Fi 这种局域网无线不同，救援通讯的关键指标不是带宽，而是"**链路能不能在最差的射频环境（无基站、暴雨、雷击、海上、低温）下建立起来**"。

技术核心：

- 链路冗余：蜂窝 / 卫星 / 短报文 / PLB（Personal Locator Beacon，个人定位信标）/ 业余无线电（Amateur Radio）多备份
- 极端环境适应：低温 -40°C、高湿、海水、9 级阵风、机身震动
- 电池续航：5~7 年待机，紧急发射 24+ 小时
- 端到端加密：不依赖地面网络也能加密（抗截获、抗胁迫）
- 5 秒定位：救援黄金窗口期，设备从开机到送出位置必须 < 5 s

## 协议族总览

```text
救援通讯（Rescue Communications）
├── 卫星 SOS 双向
│   ├── Apple Emergency SOS（iPhone 14+，2022 推出，Globalstar 卫星）
│   ├── Huawei Mate 60 Pro 北斗短报文（Beidou-3 RDSS，国产）
│   ├── Garmin inReach Mini 2 / Messenger（Iridium 卫星）
│   └── Qualcomm Snapdragon Satellite（Iridium，IoT 平台）
│
├── 短报文（Short Burst Data, SBD）
│   ├── 北斗短报文（BDS RDSS / RSMC）
│   ├── Iridium SBD（9602 / 9603 模组）
│   └── Inmarsat IsatData Pro
│
├── PLB 单向求救援
│   ├── COSPAS-SARSAT 406 MHz（国际标准）
│   ├── ACR ResQLink View / RLink
│   └── Ocean Signal rescueME
│
├── 应急蜂窝
│   ├── 4G/5G VoLTE Emergency（运营商紧急呼叫优先级）
│   ├── 卫星 IoT 备份（Astrocast / Swarm / Myriota）
│   └── 3GPP NTN（Non-Terrestrial Network，非地面网络）
│
└── 户外对讲
    ├── 业余无线电 VHF/UHF（144/430 MHz，HAM）
    ├── 卫星电话 Iridium 9555 / 9575 Extreme
    ├── 卫星电话 Thuraya XT-LITE
    └── 海上 VHF DSC（Digital Selective Calling，156 MHz）
```

## 跟其他总线/无线协议的关系

```text
IoT 总线      │ 救援通讯用到什么
──────────────┼─────────────────────────────
BLE / BLE Mesh│ 队友间近距短报文（< 100 m），户外手表组网
LoRa          │ 自建野外中继，5~10 km 低功耗
Wi-Fi 6E      │ 营地高吞吐（地图/影像），不是救援链路
NB-IoT / LTE-M│ 蜂窝 IoT 备份（运营商有覆盖时）
卫星 IoT      │ 蜂窝无覆盖时的主链路
PLB 406 MHz   │ 救命用，单向求救援
```

救援通讯**不是替代**常规无线，而是蜂窝失能后的兜底链路。一个典型的户外 / 海上终端会有 BLE（手表/手机近场）、Wi-Fi（营地）、蜂窝（4G/5G）、卫星（NB-IoT / 短报文 / 双向 SOS）、PLB（最后一根稻草）五路并行。

## 5 大技术路线对比

| 路线 | 链路 | 数据方向 | 典型带宽/速率 | 终端成本 | 适用场景 |
| --- | --- | --- | --- | --- | --- |
| 卫星 SOS 双向 | L 频段 / S 频段 | 双向（语音/简讯） | 短信 1.2 kbps | 手机 / 模组 0~500 USD | 户外 / 山区 / 海外 |
| 短报文 SBD | UHF / L | 单向/双向 | 几十~几百字节 | 模组 100~500 USD | 应急简讯 / IoT |
| PLB 406 MHz | 406 MHz | 单向求救援 | 5 W 短脉冲 | 200~500 USD | 户外 / 海上最后兜底 |
| 应急蜂窝 | 4G/5G VoLTE | 双向 | 数十 kbps | 手机 0 增量 | 城市应急 / 弱信号 |
| 户外对讲 VHF/UHF | 144/430 MHz | 半双工 | 语音 25 kHz | 对讲机 50~300 USD | 业余无线电 / 户外队内 |

## 关键概念

- **PLB (Personal Locator Beacon)**：单向 406 MHz 信标，被 COSPAS-SARSAT（国际卫星辅助搜救系统）卫星接收，全球 6 颗低轨卫星 + 5 颗静地卫星覆盖，定位精度 5 km。仅发射，不确认。
- **SBD (Short Burst Data)**：铱星（Iridium）定义的短报文协议，单条消息几十~几百字节，延迟 5~30 s。适合位置/状态上传，不适合语音。
- **RDSS (Radio Determination Satellite Service)**：北斗特有的有源定位 + 短报文合一服务，双向 1000 个汉字以内。
- **COSPAS-SARSAT**：国际搜救卫星系统，406 MHz 频段，40+ 国家参与，免费服务（中国由交通运输部救援中心负责）。
- **VoLTE Emergency**：运营商定义的紧急呼叫优先 QoS（Quality of Service，服务质量），即使网络拥塞也会接通。
- **3GPP NTN**：3GPP Release 17 起把卫星接入纳入 5G 体系，未来手机直连卫星是趋势。
- **DSC (Digital Selective Calling)**：海上 VHF 频段（156 MHz）的数字选呼，按 MMSI（Maritime Mobile Service Identity，海上移动业务识别码）寻址。

## 典型产品对标

| 类别 | 产品 | 关键链路 | 续航 | 备注 |
| --- | --- | --- | --- | --- |
| 卫星 SOS 手机 | Apple iPhone 14+ | Globalstar 卫星（2022+） | 5 年待命 | 中国/印度未开通 |
| 卫星 SOS 手机 | Huawei Mate 60 Pro | 北斗-3 RDSS | 待命 5+ 年 | 中国独有 |
| 双向卫星终端 | Garmin inReach Mini 2 | Iridium SBD 双向 | 14 天（10 min 跟踪） | 全球覆盖 |
| 双向卫星终端 | Garmin inReach Messenger | Iridium SBD | 28 天 | 手机伴侣 |
| 卫星电话 | Iridium Extreme 9575 | Iridium 语音/SBD | 30 小时通话 | 真正全球通 |
| 卫星电话 | Thuraya XT-LITE | Thuraya L 频段 | 6 小时通话 | 覆盖亚非欧 |
| PLB 单向 | ACR ResQLink View | 406 MHz + 121.5 MHz | 5 年待命 + 24h 发射 | 海上必备 |
| 短报文模组 | Iridium 9602/9603 | Iridium SBD | - | 嵌入式 IoT |
| 短报文模组 | 北斗 RDSS 模组（HX-DU1616D 等） | 北斗-3 RDSS | - | 国产 |
| 户外无人机控制 | DJI RC Plus | OcuSync + 4G 蜂窝备份 | 6 小时 | 救援无人机 |

## 实战场景

### 户外登山

- 蜂窝：山峰 3000 m+ 通常无信号
- 卫星：北斗短报文 / Iridium SBD / Globalstar 兜底
- PLB：海拔高/温度低/单人登山必带
- 关键装备：户外手表（Fenix / Suunto）+ inReach + PLB

### 海上

- VHF DSC：船-船 / 船-岸 AIS（Automatic Identification System，自动识别系统）
- 卫星：Iridium / Inmarsat / 北斗 RDSS
- PLB：船-船 + 救生衣 PLB（ACR / Ocean Signal）
- EPIRB（Emergency Position Indicating Radio Beacon，紧急位置指示无线电信标）：406 MHz 船用版，5 W，自释放

### 航空

- VHF 121.5 MHz：应急频率，耳机通话
- ELT (Emergency Locator Transmitter)：406 MHz 机载版，撞击自动启动
- ADS-B Out：广播位置给附近飞机/地面
- 通用航空（小飞机 / 滑翔伞）通常仅 ELT 兜底

### 城市应急

- 蜂窝：4G/5G VoLTE Emergency
- 短报文：北斗 RDSS（地震后基站瘫痪）
- 卫星 IoT：应急车 / 现场指挥所
- 业余无线电：HAM 应急中继（ARES / RACES）

## 嵌入式产线典型故障

- **PLB 5 年待机实测不到 3 年**：电池自放电率高，量产测试必须按 5 年等效
- **短报文发送失败率 > 30%**：天线仰角不足 / 卫星覆盖边缘
- **卫星模组入网慢（> 5 min）**：冷启动/热启动/温启动没分档
- **DSC 误触发**：MMSI 写入错或测试模式未关
- **北斗 RDSS 模组无定位**：用户卡（SIM-like）未激活 / 卡槽接触不良
- **iPhone 14 Emergency SOS 在国内不生效**：Globalstar 卫星不在中国境内
- **inReach 双向消息延迟 > 5 min**：Iridium 拥塞 / 遮挡

## 延伸阅读

- `bus/rescue-comms-practical.md` 调试速查 / 5 秒定位 / 错误码
- `bus/rescue-comms-deep-dive.md` 卫星链路 / SBD / PLB / 加密深挖
- `bus/rescue-comms-failure-cases.md` 产线 + 户外实战案例（8-9 个）
- `bus/rescue-comms-index.md` 主题地图 + 读者路径
