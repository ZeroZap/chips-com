# LTE-IoT Deep Dive

## 目标

深入 LTE-IoT 协议栈：PHY / MAC / RLC / PDCP / RRC / NAS / EPS 承载。覆盖蜂窝注册流程、APN 配置、PSM/eDRX、AT 命令与 QMI/RmNet 接口、信令流程、Qos。目标读者：模组驱动移植、协议分析、深度故障定位、功耗优化的工程师。

## 协议栈分层

```text
┌─────────────────────────────────────────────────────┐
│ 应用层 (User Plane)                                 │
│  TCP/UDP + MQTT/CoAP + TLS/DTLS                    │
├─────────────────────────────────────────────────────┤
│ NAS (Non-Access Stratum)                            │
│  EMM (EPS Mobility Management)                     │
│  ESM (EPS Session Management)                       │
│  附着 / 鉴权 / 鉴权 / 默认承载建立                  │
├─────────────────────────────────────────────────────┤
│ AS (Access Stratum)                                 │
│  RRC (Radio Resource Control)                      │
│  PDCP (Packet Data Convergence Protocol)            │
│  RLC (Radio Link Control)                           │
│  MAC (Medium Access Control)                        │
├─────────────────────────────────────────────────────┤
│ PHY (Physical Layer)                                │
│  OFDMA (DL) / SC-FDMA (UL)                         │
│  Cat 1 20 MHz / Cat M1 1.4 MHz / NB-IoT 200 kHz    │
├─────────────────────────────────────────────────────┤
│ RF 前端                                              │
│  功率放大器 / 滤波器 / 天线                          │
└─────────────────────────────────────────────────────┘
```

**两种实现形态**：

- **Modem + 主机**：蜂窝模组作为独立模组，外部 MCU 通过 UART（AT）/ USB（QMI / RmNet / NCM）/ SPI 通信
- **SoC 集成**：nRF9160 模式，蜂窝核与应用核集成在同一 SoC

**实战选型**：

```text
Modem + 主机：灵活，模组选型自由，主机可换 RTOS / Linux
SoC 集成：体积小，功耗低，但仅限特定 SoC（nRF9160 / 高通部分）
QMI / RmNet：Linux 下走 USB 虚拟网卡，性能优于 AT
```

## 物理层（PHY）

### 频段与双工

```text
FDD（Frequency Division Duplex）：
  DL（下行）和 UL（上行）走不同频率，同时收发
  典型：B1/B3/B5/B7/B8/B20/B28

TDD（Time Division Duplex）：
  DL/UL 走同频率，不同时隙
  典型：B34/B38/B39/B40/B41

HD-FDD（Half-Duplex FDD）：
  同一时间只能收或发
  Cat M1 / NB-IoT 标配，省电
```

### 带宽与子载波

| 类 | 带宽 | 子载波间隔 | RB 数 | FFT |
| --- | --- | --- | --- | --- |
| Cat 1 | 20 MHz | 15 kHz | 100 | 2048 |
| Cat M1 | 1.4 MHz | 15 kHz | 6 | 128 |
| NB-IoT (in-band) | 180 kHz | 15 kHz | 1 | 128 |
| NB-IoT (standalone) | 200 kHz | 15 kHz | 1 | 128 |
| NB-IoT (guard-band) | 180 kHz | 15 kHz | 1 | 128 |

**NB-IoT 部署模式**：

```text
In-band：     在 LTE 载波内的 PRB（Physical Resource Block）
Standalone：  独立 200 kHz 频谱（GSM 退网后常用）
Guard-band：  LTE 载波保护带（边缘未用频谱）
```

### 覆盖增强（CE Level）

```text
CE Level 0：正常覆盖（无重复）
CE Level 1：中等增强（重复 8~16 次）
CE Level 2：深度覆盖（重复 32~128 次）
NB-IoT 可达 CE Level 2，Cat M1 可达 CE Level 1
```

**MCL (Maximum Coupling Loss)**：

```text
普通 LTE：  142.7 dB MCL
Cat M1：    155.7 dB MCL（+15 dB）
NB-IoT：    164 dB MCL（+20 dB，对应地下室场景）
```

### 调制与编码

| 链路 | 调制 | 编码率 | 峰值速率（NB-IoT 例子） |
| --- | --- | --- | --- |
| DL | QPSK / 16QAM | 1/3 ~ 1 | 26 kbps（NB1 单 tone） |
| UL | BPSK / QPSK | 1/3 ~ 1 | multi-tone 62 kbps |

NB-IoT 提升速率手段：

```text
多载波（NB2 支持）
高阶调制（NB2 16QAM DL）
HARQ 重传
```

## MAC 层

### HARQ（Hybrid ARQ）

```text
下行异步 HARQ：
  上行同步 HARQ
  最多 8 个并行进程
NB-IoT：最多 2 个下行 + 1 个上行 HARQ 进程（资源受限）
```

### 调度

```text
下行：eNodeB 调度，UE 听 PDCCH（物理下行控制信道）
上行：UE 申请 SR（Scheduling Request），eNodeB 分配
NB-IoT：NPUSCH（窄带物理上行共享信道）
```

### RACH（随机接入）

```text
4 步 RACH（Cat 1 / Cat M1）：
  MSG1：UE → eNodeB，Preamble
  MSG2：eNodeB → UE，RAR（Random Access Response）
  MSG3：UE → eNodeB，RRC Connection Request
  MSG4：eNodeB → UE，RRC Connection Setup

NB-IoT：可走 4 步 RACH 或 2 步 RACH（NB2 优化，省时）
```

## RLC（Radio Link Control）

### 三种模式

```text
TM (Transparent Mode)：透传，无分段 / 重传（如 BCCH）
UM (Unacknowledged Mode)：无应答重传（如 VoLTE 语音）
AM (Acknowledged Mode)：应答 + ARQ（如数据业务）
```

### 功能

```text
分段与重组（Segmentation / Reassembly）
ARQ：AM 模式下 NACK + 重传
轮询（Polling）：eNodeB 轮询 UE 状态
```

## PDCP（Packet Data Convergence Protocol）

```text
头压缩：ROHC（Robust Header Compression），IPv4/IPv6/TCP/UDP
加密：EEA1 (SNOW 3G) / EEA2 (AES) / EEA3 (ZUC)
完整性保护：EIA1 / EIA2 / EIA3
重排序：乱序检测
复制检测：避免重复 PDU
```

## RRC（Radio Resource Control）

### 状态

```text
RRC_IDLE：
  UE 监听寻呼（paging）
  测量小区重选
  eNodeB 不分配 DRX 周期
  可启用 PSM / eDRX

RRC_CONNECTED：
  UE 有专属 SRB + DRB
  eNodeB 知道 UE 精确位置（serving cell）
  可快速传输数据
  Cat M1 / NB-IoT 可长时间停留 RRC_IDLE 节省电

RRC_IDLE 状态细分：
  - IDLE normal paging
  - IDLE with PSM（关闭收发）
  - IDLE with eDRX（长周期监听）
```

### 关键 RRC 消息

```text
RRC Connection Setup
RRC Connection Reconfiguration（含默认承载建立）
RRC Connection Reestablishment
RRC Connection Release（带 releaseCause）
RRC Connection Suspend / Resume（NB-IoT 优化）
```

## NAS（Non-Access Stratum）

### EMM（EPS Mobility Management）

#### 状态

```text
EMM-DEREGISTERED：未附着
  ↕ Attach / Detach
EMM-REGISTERED：已附着

EMM-REGISTERED 子状态：
  EMM-REGISTERED.NORMAL-SERVICE
  EMM-REGISTERED.LIMITED-SERVICE
  EMM-REGISTERED.ATTEMPTING-TO-UPDATE
  EMM-REGISTERED.NO-CELL-AVAILABLE
  EMM-REGISTERED.PLMN-SEARCH
  EMM-REGISTERED.UPDATE-NEEDED
```

#### 关键流程

```text
附着流程（Attach）：
  UE → MME: Attach Request (IMSI, last visited TAI, UE capability, ...)
  MME → UE: Identity Request (IMSI 获取)
  UE → MME: Identity Response
  MME ↔ HSS: Authentication (AKA)
  UE ↔ MME: Security Mode Command/Complete
  MME → UE: Attach Accept (GUTI, TAI list, EPS bearer, ...)

  Attach Accept 内嵌：
    +EPS network feature support
    +T3412 周期（隐式注册定时器）
    +T3324（PSM active timer）
    +T3402（去附着 retry 定时器）
    +eDRX parameters
    +Default APN
    +PDN type (IPv4 / IPv6 / IPv4v6)

TAU（Tracking Area Update）：
  UE 移出原 TA → TAU Request
  MME → UE: TAU Accept
  跨 MME 时 Context Transfer

去附着（Detach）：
  UE 主动：Detach Request (power off / detach only)
  网络主动：Detach Request
```

#### 关键定时器

| 定时器 | 含义 | 典型值 |
| --- | --- | --- |
| T3412 | 周期性 TAU 定时器（隐式注册） | 54 min ~ 310 h（可配） |
| T3413 | 寻呼响应定时器 | 5 ~ 15s |
| T3324 | PSM active timer（激活态） | 0 ~ 186 min（可配） |
| T3402 | 去附着 retry 定时器 | 默认 12 min |
| T3346 | 抑制定时器（PSM） | 0 ~ 2550s |

### ESM（EPS Session Management）

#### 默认承载建立

```text
Attach Accept 中内嵌：
  Activate Default EPS Bearer Context Request
    - EPS Bearer ID
    - APN
    - PDN type
    - IP address（V4/V6/V4V6）
    - QoS (QCI, ARP, MBR, GBR)

UE → MME: Activate Default EPS Bearer Context Accept
UE 获得 IP 地址
```

#### 专用承载

```text
用于特定业务的 QoS（如 VoLTE）
UE / 网络可发起
```

## 蜂窝注册流程（端到端）

```text
1. 上电
   UE 加载 firmware
   USIM 初始化
   IMEI 读取

2. PLMN 选择
   优先级：
     RPLMN (Registered PLMN)
     HPLMN (Home PLMN) / EHPLMN
     UPLMN (User-controlled PLMN list)
     OPLMN (Operator-controlled PLMN list)
     其他 PLMN

3. 频段扫描
   按支持频段逐个扫 RSSI
   找最强 4G 小区（中心频率 + EARFCN）
   找 SIB（System Information Block）

4. 小区同步
   PSS（Primary Synchronization Signal）
   SSS（Secondary Synchronization Signal）
   PBCH（Physical Broadcast Channel）
   解析 MIB / SIB1 / SIB2

5. RACH 随机接入
   Preamble（4 步 RACH）
   RAR（Random Access Response）
   RRC Connection Request
   RRC Connection Setup

6. 附着
   Attach Request
   鉴权（AKA）
   Security Mode
   Attach Accept
   Activate Default EPS Bearer Context

7. PDN 连接
   IP 地址获取
   DNS 配置

8. 数据传输
   TCP/UDP
   TLS/DTLS
   应用协议（MQTT/CoAP/HTTP）
```

## 关键概念深挖

### PLMN 选择

```text
PLMN 编码：
  MCC（移动国家码）+ MNC（移动网络码）
  中国移动：460 + 00 / 02 / 04 / 07
  中国联通：460 + 01 / 06 / 09
  中国电信：460 + 03 / 05 / 11
  中国广电：  460 + 15

选网策略：
  自动：按上述优先级
  手动：`AT+COPS=1,2,"46000"` 强制选中国移动
```

### 小区重选

```text
RRC_IDLE 时：
  UE 测量邻区
  S 准则（小区是否可驻留）
  R 准则（同频 / 异频重选）
  触发小区重选

NB-IoT：
  仅重选，不切换（no handover）
  重选失败 → RRC_IDLE 继续搜网
```

### 切换（仅 Cat 1 / Cat M1 支持）

```text
RRC_CONNECTED 时：
  测量报告 → eNodeB 决策
  X2 / S1 接口切换准备
  RRC Connection Reconfiguration（含 mobilityControlInfo）
  UE 在新小区随机接入
  完成切换

NB-IoT：
  无切换，仅小区重选（节省信令）
```

### 鉴权（AKA）

```text
MME → HSS：Authentication Data Request (IMSI)
HSS → MME：Authentication Data Response (RAND, AUTN, XRES, KASME)
MME → UE：Authentication Request (RAND, AUTN)
UE：验证 AUTN（防伪）
UE → MME：Authentication Response (RES)
MME：XRES 与 RES 比对
```

### 加密与完整性

```text
安全算法（3GPP TS 33.401）：
  EEA1: SNOW 3G（机密性）
  EEA2: AES-CTR
  EEA3: ZUC
  EIA1: SNOW 3G（完整性）
  EIA2: AES-CMAC
  EIA3: ZUC

UE 能力上报：UE Network Capability IE
MME 选算法：Security Mode Command
```

## APN 详解

### APN 结构

```text
APN = <APN NI>.<APN OI>
  APN NI：APN Network Identifier（公网 / 专网标识）
  APN OI：APN Operator Identifier（运营商域名，可选）

例：
  cmnet            → 中国移动公网
  ctnet            → 中国电信公网
  uninet           → 中国联通公网
  abc.example.com  → 专网（需要运营商侧 MME 配置）
```

### APN 类型

| 类型 | 用途 | 鉴权 |
| --- | --- | --- |
| Default APN | 附着时自动建立默认承载 | 无 / PAP / CHAP |
| Dedicated APN | 专网 / 私网 | 通常 PAP / CHAP |

### APN 限制

```text
公网 APN（cmnet/ctnet/uninet）：
  走运营商骨干网 + 互联网
  限制：可能封 80/443 等端口

专网 APN：
  走运营商 APN 专网
  优势：端到端、安全、QoS
  限制：需运营商侧配置

NB-IoT APN：
  走 IoT 核心网
  限速（NB-IoT 本身速率低）
  限制：常需用专网 APN
```

## PSM（Power Save Mode）

### 原理

```text
UE 跟网络协商 T3412（TAU 周期）+ T3324（PSM active timer）

正常流程：
  1. UE 接入网络
  2. 数据传输完
  3. 启动 T3324（active timer）
  4. T3324 到期 → 进入 PSM
  5. PSM 状态：收发全关，仅 RTC
  6. 等 T3412 到期 → 自动醒来 TAU
  7. 寻呼不可达

功耗节省：
  RRC_IDLE ~ mA 级
  PSM ~ µA 级
```

### 启用

```text
AT 命令：
  AT+CPSMS=1,,,"<T3412>","<T3324>"
  T3412 = 01000110 (binary) = 6 min
  T3324 = 00100001 (binary) = 1 min

  GPRS Timer 3 编码：
  unit: 0~7 (10 min / 1 hour / 10 hour / 2 sec / 30 sec / 1 min / 320 hour / ...)
  value: 0~31

实操：
  T3412 = "10100101" → 4 hour（10 hour * 5 = 50 hour?）
  T3324 = "00100001" → 1 min

参考：3GPP TS 24.008 §10.5.7.4a GPRS Timer 3
```

### 注意点

```text
1. PSM 期间不可达（不发下行数据）
2. 主动发数据要先退出 PSM（30 秒级延迟）
3. T3412 不能太短（避免频繁 TAU 耗电）
4. T3324 决定 active 窗口（够发上行就行）
5. 运营商必须支持 PSM 业务（默认都支持）
6. NB-IoT + PSM 是抄表首选方案
```

## eDRX（extended DRX）

### 原理

```text
传统 DRX：1.28s ~ 2.56s
eDRX（NB-IoT）：最长达 174.4 min（2.91 hour）
eDRX（Cat M1）：最长达 ~44 min

UE 协商 eDRX 周期 + PTW（Paging Time Window）

流程：
  1. UE 跟网络协商 eDRX
  2. UE 在每个 eDRX 周期内的 PTW 时间窗监听寻呼
  3. PTW 之外，UE 关闭收发
  4. 寻呼被推迟到下一个 PTW
```

### 启用

```text
AT 命令：
  AT+CEDRXS=1,5,"0101"  // 开启 eDRX，模式 5（NB-IoT），周期 0101

  eDRX 周期（NB-IoT）：
  0101 = 20.48 s
  0010 = 40.96 s
  0011 = 81.92 s
  ...
  1001 = 174.4 min

参考：3GPP TS 24.008 §10.5.5.32
```

### PSM vs eDRX

| 维度 | PSM | eDRX |
| --- | --- | --- |
| 可达性 | 不可达 | 周期可达（PTW） |
| 省电 | 极致（µA） | 中（百 µA） |
| 下行延迟 | 60 min+ | 周期内可达（min 级） |
| 适合 | 抄表（仅上行） | 远程控制（需下行） |

## AT 命令与 QMI 接口

### AT 命令

```text
3GPP TS 27.007：通用（语音 / SMS / 数据）
3GPP TS 27.005：SMS 扩展
3GPP TS 27.010：串口多路复用
厂商扩展：
  移远 AT 手册（Quectel_xxx_AT_Commands_Manual）
  芯讯通 SIMCom AT 手册
  广和通 Fibocom AT 手册
```

### QMI / RmNet（高通平台）

```text
QMI（Qualcomm MSM Interface）：
  主机通过 USB / SDIO / PCIe 走 QMI 协议
  比 AT 命令更高效（结构化消息）

RmNet：
  Linux 走 USB 虚拟网卡
  qmi_wwan / qmi_netdev 驱动
  IP 包直接通过 USB 传

RNDIS / NCM：
  类似 RmNet，但走 USB 网络标准
  Windows 兼容 RNDIS，Linux 兼容 NCM
```

### 串口多路复用

```text
场景：1 个 UART 同时用 AT + 数据 + log
方案：3GPP TS 27.010 multiplexer
  - 通道 1：AT 命令
  - 通道 2：数据
  - 通道 3：log
  - 通道 4：调试

启动：AT+CMUX=0  (默认)
```

## 功耗优化实战

### 模组选型

```text
低功耗档（NB-IoT 抄表）：
  模组：NB-IoT（BG77 / SIM7080）
  协议：NB-IoT + PSM
  电池：锂亚硫酰氯 8500 mAh
  寿命：> 10 年（每天 1 次上报）

平衡档（资产追踪）：
  模组：Cat M1（BG95）
  协议：Cat M1 + eDRX
  电池：锂离子 1000 mAh
  寿命：> 6 个月（每小时 1 次）

高速档（POS）：
  模组：Cat 1（EC200N）
  协议：Cat 1 + DRX
  电池：市电 + 备份
  寿命：永久
```

### 功耗数据参考

```text
移远 EC200N (Cat 1)：
  关机：        10 µA
  PSM：        3 µA
  空闲：       20 mA
  注册：       200 mA（瞬态）
  传输峰值：   2 A（瞬态）

移远 BG95 (Cat M1/NB-IoT)：
  关机：        5 µA
  PSM：        1 µA
  空闲：       10 mA
  注册：       150 mA
  传输峰值：   500 mA

Nordic nRF9160 (Cat M1/NB-IoT + GPS)：
  关机：        1.5 µA
  PSM：        2 µA
  空闲：       5 mA
  GPS 跟踪：   50 mA
```

## 实战经验

- **APN 错是最常见的搜网失败原因**：NB-IoT 卡配 cmnet 完全搜不到，电信 NB-IoT 必须 ctnb
- **PSM 启用后下行不可达**：主动呼叫下行前要先 `AT+CFUN=0/1` 退出 PSM
- **eDRX 需运营商业务开通**：基础 eDRX 普遍支持，长 eDRX（>10 min）需申请
- **PDP 激活失败原因 80% 是 APN / 用户名密码错**
- **Cat 1 模组瞬态电流大**：电源设计要留 50% 余量（2A → 选 3A 电源）
- **多模组同区域干扰**：频段相同 + 小区同步 → 错峰注册
- **NB-IoT 模组兼容 2G / 4G**：但移动 NB-IoT 卡不能上 4G，电信 NB-IoT 卡也只能 NB-IoT

## 关联文档

- `bus/lte-iot.md` 主题入口
- `bus/lte-iot-practical.md` 调试流程速查
- `bus/lte-iot-failure-cases.md` 产线实战案例
- `bus/lte-iot-index.md` 主题地图 + 导航
