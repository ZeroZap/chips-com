# Satellite-IoT 深度技术解析

## 目标

本文从卫星轨道物理层、链路预算、多普勒补偿、3GPP NTN 协议栈、北斗 RDSS 协议、Iridium SBD 协议、Starlink Direct to Cell 七个维度深入解析卫星 IoT 技术，适合做卫星 IoT 协议栈移植、芯片选型、链路预算工程师阅读。

## 一、卫星轨道与物理层

### 1.1 轨道类型对比

```text
LEO（低轨）
  高度:     500 ~ 2000 km
  周期:     90 ~ 120 min
  时延:     单跳 20 ~ 50 ms
  路径损耗: 400 MHz ~ 138 dB（距离 600 km）
            2 GHz    ~ 154 dB
  覆盖:     单颗 ~10 min / 圈
            整组（66 颗 Iridium）~ 近乎全时
  特点:     时延低、损耗小、卫星数量多、需多普勒补偿

MEO（中轨）
  高度:     5000 ~ 25000 km
  周期:     6 ~ 12 h
  时延:     单跳 100 ~ 300 ms
  路径损耗: 1.5 GHz ~ 182 dB
  覆盖:     几颗即可全球（GPS 24 颗）
  特点:     GPS / 北斗 MEO 用，IoT 不主流

GEO（地球同步轨道）
  高度:     35786 km
  周期:     24 h（与地球同步）
  时延:     单跳 ~600 ms
  路径损耗: 1.5 GHz ~ 188 dB
  覆盖:     3 颗覆盖全球（除极地）
  特点:     北斗 GEO、Inmarsat 用，链路预算极紧
```

### 1.2 自由空间路径损耗

公式（dB）：

```text
FSPL (dB) = 20 × log10(d) + 20 × log10(f) + 32.44
           d = 距离 (km)
           f = 频率 (MHz)
```

| 频段 | 频率 | 距离 600 km（LEO） | 距离 36000 km（GEO） |
| --- | --- | --- | --- |
| UHF（400 MHz） | 400 | 139.0 dB | 174.5 dB |
| L 频段 | 1500 | 151.4 dB | 186.9 dB |
| S 频段 | 2500 | 155.9 dB | 191.4 dB |
| C 频段 | 4000 | 160.0 dB | 195.5 dB |
| Ku 频段 | 12000 | 169.5 dB | 205.0 dB |

LEO 比 GEO 路径损耗低 35~40 dB，这是 LEO 成为 IoT 主战场的主要原因。

### 1.3 多普勒效应

LEO 卫星相对地面速度 ~7.5 km/s，多普勒频偏：

```text
Δf = f0 × v / c
    f0 = 载波频率
    v  = 相对速度（7.5 km/s max）
    c  = 光速

400 MHz → Δf max = 10 kHz
1.5 GHz → Δf max = 37.5 kHz
2.5 GHz → Δf max = 62.5 kHz
```

LEO 多普勒变化率 ~ ±0.5 Hz/s（400 MHz），IoT 短报文应用（持续时间 < 1 s）可视为准静态。

### 1.4 链路预算

NB-IoT NTN 链路预算（参考）：

```text
EIRP（地面终端）            =  +7 dBW (5W + 10 dBi 高增益)
FSPL（600 km, 1.5 GHz）     =  -151 dB
大气衰减 / 雨衰             =  -3 dB
极化损耗                   =  -3 dB
指向损耗（仰角 20°）        =  -2 dB
G/T（卫星接收）              =  +5 dB/K
Boltzmann                   =  -228.6 dBW/K/HZ
C/N0                        =  81.4 dBHz
BW（180 kHz NB-IoT）        =  52.6 dBHz (10×log10(180000))
SNR                         =  28.8 dB
```

NB-IoT NTN 终端最大允许路径损耗（MCL）= 164 dB。

对比地面 NB-IoT：MCL 164 dB vs 164 dB（持平），但地面 NB-IoT 有 15 dB 覆盖增强，NTN 链路预算实际更紧。

### 1.5 卫星过顶窗口

LEO 卫星过顶单颗窗口：

```text
仰角 0°   →  ~12 min（赤道）
仰角 8°   →  ~10 min
仰角 20°  →  ~7 min
仰角 45°  →  ~4 min
仰角 90°  →  ~0 min（天顶）
```

IoT 短报文（< 1 s 发射）完全可以在过顶窗口内完成，但需在窗口前完成 GSE 接收 + 频率同步。

## 二、3GPP NTN（NB-IoT / LTE-M）协议栈

### 2.1 3GPP R17 关键增强

3GPP 在 R17（2022 冻结）首次完整定义 NTN：

```text
3GPP R15（2018）: 卫星 IoT 研究（SI），R15 不含 NTN
3GPP R16（2020）: 4G 卫星研究，NCC（Network Controlled Cell，地面 + 卫星协同）
3GPP R17（2022）: 5G NTN SI/WI（Study Item / Work Item）
                   - FR1（Frequency Range 1，410 MHz ~ 7.125 GHz）NTN 频段定义（n254/n255/n256）
                   - LEO / GEO 场景支持
                   - Doppler / Timing pre-compensation
                   - GSE（GNSS Satellite Ephemeris）下发
                   - HARQ（Hybrid Automatic Repeat Request，混合自动重传请求）时序调整（RTD，Round Trip Delay，往返时延）
3GPP R18（2024）: NTN 增强
                   - NB-IoT / LTE-M NTN 完整支持
                   - Store-and-forward（存储转发）支持（卫星上 IoT 数据暂存）
3GPP R19（2025+）: NR NTN（5G NR 卫星接入）
                   - 高速率卫星（数百 Mbps）
```

### 2.2 NTN 信令流程

```text
1. 终端开机，搜星
2. 接收 SIB-NTN（NTN 广播）：
   - 服务卫星星历（GSE）
   - 频点信息
   - 当前 Doppler / Timing offset
3. 终端计算 pre-compensation（自己需要补偿的频率和时间偏移）
4. PRACH 接入：
   - 频率已 pre-compensation
   - Timing 按 RTD 提前发射
5. RRC Connection Setup
6. Attach 流程（含 NTN-Specific IE）
7. PDU Session Establishment
8. 数据传输
```

### 2.3 NTN 关键 IE（Information Element，信息元素）

```text
NTN-Config-r17:
  - referenceLocation        // 参考位置（用于卫星对准）
  - ephemerisInfo            // 星历信息
  - ephemerisValidity        // 星历有效期
  - ntniab-Indication        // IAB（Integrated Access and Backhaul，集成接入回传）支持
  - cellSpecificKoffset-r17  // RTD 补偿
  - ta-Report-r17            // TA（Timing Advance，定时提前）报告
```

### 2.4 Doppler / RTD 补偿

终端在 PRACH 前必须做的补偿：

```text
Doppler pre-compensation:
  Δf_tx = -Δf_observed × (f_ul / f_dl)  // 反向 + 按上/下行频比
  
RTD pre-compensation:
  Δt_tx = -RTD / 2  // 提前发射

例：
  LEO 600 km，RTD = 8 ms
  Δt_tx = -4 ms（提前 4 ms 发射）
  400 MHz，Doppler = +10 kHz
  Δf_tx = -10 kHz（反相补偿）
```

### 2.5 eDRX / PSM 在 NTN

```text
PSM（Power Saving Mode，省电模式）:
  - T3324 (Active Timer)        = 0 ~ 186 min
  - T3412 (TAU/Periodic-RAU)    = 0 ~ 413 天
  - 退出 PSM 后才可收发

eDRX（Extended Discontinuous Reception，扩展非连续接收）:
  - 地面 NB-IoT:  2.91 s ~ ~44 min
  - NTN NB-IoT:   10.24 s ~ ~41 min（更宽松）
  - PTW（Paging Time Window，寻呼时间窗口）= 1 ~ 60 s
  - 终端只在 PTW 监听寻呼
```

NTN 终端功耗对比：

```text
地面 NB-IoT PSM 待机:  3 ~ 5 µA
NTN NB-IoT PSM 待机:   10 ~ 20 µA（更频繁的星历更新）
NTN NB-IoT eDRX:       50 ~ 100 µA
```

## 三、北斗短报文（RDSS）协议

### 3.1 北斗系统组成

```text
北斗三号（BDS-3，2020 全球组网完成）：
  - 3 颗 GEO（地球同步轨道，定点于 80°E / 110.5°E / 140°E）
  - 3 颗 IGSO（Inclined Geo-Synchronous Orbit，倾斜地球同步轨道）
  - 24 颗 MEO（中等地球轨道，Walker 24/3/1 星座）

RDSS（Radio Determination Satellite Service，卫星无线电测定业务）:
  - 入站（L 频段，1610 ~ 1626.5 MHz）：用户 → 卫星
  - 出站（S 频段，2483.5 ~ 2500 MHz）：卫星 → 用户
  - 业务：定位 + 短报文 + 位置报告

RNSS（Radio Navigation Satellite Service，卫星无线电导航业务）:
  - B1I（1561.098 MHz）/ B3I（1268.52 MHz）
  - 业务：导航 / 定位
```

### 3.2 RDSS 帧格式

入站帧：

```text
| 前导码 | 用户地址 | 电文内容 | 校验 | 长度 |
| 32 bit | 24 bit  | N × 8 bit | CRC | ~ 200 ~ 1000 bit |
```

出站帧：

```text
| 前导码 | 帧类型 | 中心站地址 | 用户地址 | 电文内容 | 校验 |
| 32 bit | 8 bit  | 24 bit     | 24 bit  | N × 8 bit | CRC |
```

### 3.3 短报文通信流程

```text
用户 A → 北斗 GEO → 地面中心站 → 北斗 GEO → 用户 B
                                    ↓
                              业务处理 / 转发

定位：
  1. 用户 A 发 RDSS 信号（含用户地址）
  2. 北斗 GEO 转发到地面中心站
  3. 中心站解算位置（通过两颗卫星的时差 + 高程库）
  4. 出站信号返回位置结果

短报文：
  1. 用户 A 编码短报文（含收信人地址）
  2. 入站发射（RDSS 频段）
  3. GEO 卫星转发到中心站
  4. 中心站解调 + 加密验证
  5. 出站广播到目标用户 B
  6. 用户 B 接收出站帧
  7. ACK 回执（用户 A 收到）

时延：
  入站 + 出站 + 中心站处理 ≈ 1 ~ 5 s
```

### 3.4 加密与认证

```text
入网注册：
  - 用户提交 ID + 加密因子（AES-128 / SM4）
  - 中心站分配卡号
  - 卡号 + 密钥写入 RDSS 卡

电文加密：
  - AES-128 / SM4（国产化必 SM4）
  - 每用户独立密钥
  - 中心站解密后再加密转发

防重放：
  - 时间戳 + 序列号
  - 中心站校验时效
```

## 四、Iridium SBD 协议

### 4.1 Iridium 星座

```text
66 颗 LEO 卫星（+ 12 颗备份）
6 个极地轨道面
高度 780 km
周期 100 min

每颗卫星 48 个波束（L 频段）
每颗卫星 4 个 Ka 频段星间链路
```

### 4.2 SBD 协议栈

```text
L 频段 (1616 ~ 1626.5 MHz)
  ↓
物理层：QPSK（Burst），突发式发射
  ↓
MAC 层：SDMA / TDMA / FDMA 混合
  - 4 帧 / 90 ms（每帧 240 个时隙）
  - 4 波束 / 帧 / 卫星
  ↓
逻辑信道：
  - BCCH（Broadcast Control Channel，广播控制信道）
  - RACH（Random Access Channel，随机接入信道）
  - SDCCH（Stand-alone Dedicated Control Channel，独立专用控制信道）
  - SACCH（Slow Associated Control Channel，慢速随路控制信道）
  - TCH（Traffic Channel，业务信道）
  ↓
SBD 协议：
  - MO（Mobile Originated，移动发起）：用户 → Iridium → SBD 服务中心
  - MT（Mobile Terminated，移动终止）：SBD 服务中心 → Iridium → 用户
```

### 4.3 SBD 数据格式

MO 帧：

```text
| IMEI (15B) | MOMSN (2B) | MTMSN (2B) | Payload (≤ 340 B) |
```

MT 帧：

```text
| IMEI (15B) | MOMSN (2B) | MTMSN (2B) | Payload (≤ 270 B) |
```

### 4.4 SBD 服务中心

```text
DirectIP (SBD DirectIP):
  - 通过 TCP/IP 直接连接 SBD 服务中心
  - 端口：10800（生产环境）
  - 格式：二进制帧 + CRC16

Email Gateway:
  - <imei>@sbd.iridium.com
  - 自动转 SBD 短报文

HTTP POST:
  - 某些场景下用 HTTP 转发
```

### 4.5 SBD 关键 AT 命令

```text
AT+CIER=1,1,1,1              // 启用错误回显
AT+CSQ                       // 信号强度
AT+SBDDET                    // 检测 SBD 模组
AT+SBDREG?                   // 查询注册状态
AT+SBDMTA=0                  // 关闭 MT（节省流量）
AT+SBDWB=<length>            // 写 MO buffer
AT+SBDI                      // 触发 MO 发送
AT+SBDRT                     // 读 MT buffer
AT+SBDD                      // 清理 buffer
AT+SBDTC                     // 触发 MT 同步（拉取）
```

## 五、Starlink Direct to Cell

### 5.1 技术路线

```text
SpaceX + T-Mobile（美国）
2024 Q1 商用：短信 + 通话（限定机型）
2024 Q3：IoT 模式试商用
2025+：完整 LTE / 5G 直连卫星

频段：
  - 1.9 GHz PCS 段（T-Mobile 持有）
  - 卫星下行 + 上行到地面 LTE 终端
  - 部分频谱共享（动态）

技术特点：
  - 大卫星 + 大波束（覆盖大）
  - Doppler 预补偿
  - 卫星间激光链路（减少地面站依赖）
```

### 5.2 与 NB-IoT NTN 对比

```text
                    Starlink IoT           NB-IoT NTN (3GPP)
频段                1.9 GHz PCS            n255 (1525-1660 MHz)
覆盖                美国 + 部分海外         全球（依运营商部署）
速率                数十 kbps (初期)       26 / 127 kbps
时延                20 ~ 40 ms             20 ~ 50 ms
标准                私有（Starlink + T-Mobile）3GPP R17 标准
IoT 模式            2025+                  已商用（部分运营商）
终端认证            Starlink 认证          运营商 + 3GPP 认证
国内可用            否                     2025+ 试商用
```

## 六、Garmin inReach / SPOT 户外双向

### 6.1 体系结构

```text
Garmin inReach：
  - 终端（inReach Mini 2 / Mini 3）
  - Iridium 模组（嵌入）
  - 双向报文（inReach 用户可发可收）
  - 配套 Garmin Explore App
  - 地图 + 路径规划
  - 紧急 SOS（一键）

SPOT：
  - SPOT X / SPOT 5
  - Globalstar 卫星网络
  - 跟踪 + 报文 + SOS
  - 跟踪频率可设（5/10/30/60 min）
  - 平台：SPOT My Globalstar
```

### 6.2 通信流程

```text
inReach:
  1. 用户编报文（按键 / 手机 App）
  2. Iridium 模组附网（自动）
  3. 卫星过顶窗口发送
  4. Iridium 转发到服务中心
  5. 服务中心分发：
     - 其他 inReach 设备（双向）
     - 预设邮箱 / 手机（单向）
     - MapShare 平台（公开）
  6. 收信人回信（inReach 设备端）
  7. 反向链路 + 模组接收

SPOT:
  1. 用户按键 / 编报文
  2. Globalstar 模组附网
  3. 卫星转发
  4. SPOT 平台分发
  5. SOS 走专业搜救通道（IERCC，International Emergency Response Coordination Center，国际应急响应协调中心）
  6. 单向（不可回复）
```

## 七、链路预算实战

### 7.1 NB-IoT NTN 链路预算（终端侧）

```text
上行（终端 → 卫星）:
  终端 TX power            =  +23 dBm (200 mW)
  终端天线增益              =  +10 dBi（高增益定向）
  EIRP                      =  +33 dBm

  FSPL（600 km, 1.5 GHz）   =  -151 dB
  大气衰减                  =   -3 dB
  极化损耗                  =   -3 dB
  指向损耗                  =   -2 dB
  卫星 G/T                  =   +3 dB/K
  Boltzmann                  =  -228.6 dBW/K/Hz
  C/N0                      =   105.6 dBHz

  BW (180 kHz)              =   52.6 dBHz
  SNR                       =   53 dB （链路极好）
```

### 7.2 Iridium SBD 链路预算

```text
上行（终端 → Iridium）:
  TX power                  =  +27 dBm (0.5 W)
  天线增益（全向）          =   +3 dBi
  EIRP                      =  +30 dBm

  FSPL (780 km, 1.6 GHz)    =  -153 dB
  大气衰减                  =   -2 dB
  指向损耗                  =   -3 dB
  卫星 G/T                  =   -1 dB/K
  Boltzmann                  =  -228.6 dBW/K/Hz
  C/N0                      =   99.6 dBHz

  BW (50 kHz burst)         =   47 dBHz
  SNR                       =   52.6 dB
```

### 7.3 北斗短报文链路预算

```text
上行（用户 → GEO）:
  TX power                  =  +30 dBm (1 W)
  天线增益                  =   +4 dBi（小型螺旋）
  EIRP                      =  +34 dBm

  FSPL (36000 km, 1.6 GHz)  =  -188 dB
  大气衰减                  =   -3 dB
  极化损耗                  =   -3 dB
  指向损耗                  =   -2 dB
  卫星 G/T                  =   -5 dB/K
  Boltzmann                  =  -228.6 dBW/K/Hz
  C/N0                      =   61.6 dBHz

  BW (8 kHz burst)          =   39 dBHz
  SNR                       =   22.6 dB （极紧）
```

北斗 GEO 链路预算比 LEO 紧 40 dB！实际产品必须用功率放大器（PA）+ 高增益天线。

## 八、产线链路预算核查

```text
核查项（产线必做）：
  □ 终端 TX power 实测（功率计）
  □ 天线 VSWR（VNA 扫）
  □ EIRP（频谱仪 + 测试天线）
  □ 卫星过顶时段实测（C/N0 记录）
  □ 不同时段 / 不同仰角的丢包率
  □ 多普勒跟踪曲线
  □ 频度限制测试（北斗 1 min 限制）
  □ 电文长度边界测试（1000 汉字）
  □ IMEI / 卡号注册完整性
  □ 资费告警触发
```

## 九、协议栈对比

| 维度 | NB-IoT NTN | 北斗短报文 | Iridium SBD | Starlink IoT |
| --- | --- | --- | --- | --- |
| 标准化 | 3GPP R17 | 国内军用 / 民用 | Iridium 私有 | SpaceX 私有 |
| 协议栈深度 | 完整蜂窝 | 简化 MAC | 简化 SBD | LTE 简化 |
| 业务类型 | 数据 + 短报文 | 短报文 + 定位 | 短数据 | 短信 + 数据 |
| 容量 | 26 / 127 kbps | 1 k 汉字/次 | 340 B/条 | 数十 kbps |
| 时延 | 5~15 s | 1~5 s | 5~30 s | 5~15 s |
| 终端 | 蜂窝模组 | 北斗 RDSS 模组 | SBD 模组 | LTE 模组 |
| 国内 | 2025+ | 已商用 | 需卫星卡 | 不可用 |

## 十、关键芯片 / 模组深挖

### 10.1 移远 BG95-M3

```text
平台:      Qualcomm MDM9205
类:        Cat M1 / Cat NB1 / Cat NB2 / NTN
频段:      B1/B2/B3/B4/B5/B8/B12/B13/B18/B19/B20/B25/B26/B27/B28/B66/B85
           + NTN n255 (L 频段)
GNSS:      GPS / GLONASS / BeiDou / Galileo / QZSS
电源:      3.3V ~ 4.3V
峰值电流:  ~500 mA
封装:      LCC 94 pin
尺寸:      23.6 × 19.9 × 2.2 mm
AT 命令:   3GPP TS 27.007 + Quectel 扩展
```

### 10.2 中斗微星 ZD-V100

```text
类:        北斗三号 RDSS + RNSS
频段:      RDSS L 频段入站 + S 频段出站
           RNSS B1I / B3I
电文长度:  1000 汉字（普通卡）
定位精度:  10 m
电源:      3.3V ~ 5V
封装:      24 pin 邮票孔
尺寸:      20 × 16 × 2.5 mm
接口:      UART + SPI
```

### 10.3 Iridium 9602 / 9603

```text
类:        SBD 短数据
频段:      1616 ~ 1626.5 MHz
电源:      3.0V ~ 5.5V
峰值电流:  ~1.5 A（发射）
封装:      25 pin
尺寸:      41 × 24 × 4 mm
接口:      UART
认证:      FCC / IC / CE / Iridium 认证
```

### 10.4 Nordic nRF9160 + NTN

```text
平台:      Nordic nRF9160 SiP（System in Package，系统级封装）
类:        Cat M1 / Cat NB1 / NB2 / NTN / GPS
频段:      全 LTE 频段 + NTN
GNSS:      GPS
应用核:    Cortex-M33 (64 MHz, 1 MB Flash, 256 KB RAM)
电源:      3.0V ~ 5.5V
封装:      7 × 7 mm LGA
```

## 十一、产线常见技术难题

### 11.1 GSE 过期

```text
现象: NTN 搜星失败 / 附着失败
原因: 模组长时间无服务，下载的 SIB-NTN 星历 > 3 小时
解决:
  - 模组重新搜星，强制下载 SIB-NTN
  - 应用层加 watchdog，超时重试
  - eDRX 不要设太长（影响星历更新）
```

### 11.2 多普勒未补偿

```text
现象: PRACH 接入失败 +CEREG: 0
原因: 终端未做 Doppler pre-compensation
解决:
  - 升级模组固件（必须支持 NTN Doppler pre-compensation）
  - 确认 SIB-NTN 中 ephemeris 完整
  - 测试时记录 Doppler 值（频谱仪）
```

### 11.3 北斗频度超限

```text
现象: 入站失败 / ACK 收不到
原因: 普通卡 1 min 内重复发
解决:
  - 应用层加 1 min 间隔
  - 加 ACK 等待 30 s
  - 紧急电文走专用卡（频度更宽松）
```

### 11.4 Iridium MOMSN 越界

```text
现象: +SBDI: 7, x, ...
原因: MOMSN（2 B）65535 后溢出 / 复位
解决:
  - 应用层 MOMSN 持久化（fds）
  - 定期重启
  - 避免复位后从 0 开始
```

### 11.5 户外卫星过顶窗口短

```text
现象: 短报文丢失 / 超时
原因: 数据量 > 窗口容量 / 多普勒未同步
解决:
  - 应用层分包
  - 监控卫星过顶时间（预测软件）
  - 高仰角优先
```

## 关联文档

- `bus/satellite-iot.md` 主题入口
- `bus/satellite-iot-practical.md` 调试流程速查
- `bus/satellite-iot-failure-cases.md` 产线实战案例
- `bus/satellite-iot-index.md` 主题地图 + 导航

## 参考文献

- 3GPP TS 36.101 (NTN bands)
- 3GPP TS 38.101-1 (FR1 NTN)
- 3GPP TR 38.811 (NTN SI)
- 北斗 RDSS ICD（公开）
- Iridium SBD Developer Guide
- SpaceX/T-Mobile Direct to Cell 公告
