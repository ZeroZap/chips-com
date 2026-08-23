# LTE-IoT 主题总览

## 目标

LTE-IoT（蜂窝物联网）是 chips-com 核心无线协议主题之一，围绕"中低速 IoT / 移动资产追踪 / 远程抄表 / POS 终端 / 车载设备"已经形成 5 篇专题笔记。本文档是**总览导航**，帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/lte-iot*.md
│
├── 速查层
│   └── lte-iot-practical.md                调试流程速查 / 5 秒定位 / 错误码表
│
├── 原理层
│   └── lte-iot-deep-dive.md                PHY / NAS / RRC / EPS / PSM / eDRX
│
├── 实战层
│   └── lte-iot-failure-cases.md            9 个产线实战案例
│
└── 导航
    └── lte-iot-index.md (本文件)
```

## 读者路径

### 路径 A："我刚接触 LTE-IoT，想入门"（新人）

按顺序读，1-2 天能上手：

1. **`lte-iot.md`** — 主题入口，5 分钟
2. **`lte-iot-practical.md`** — APN / 蜂窝注册 / 5 秒定位
3. **`lte-iot-deep-dive.md`** — 协议栈分层 + NAS 流程

### 路径 B："我在做 LTE-IoT 设备产线失败"（现场救火）

1. **`lte-iot-practical.md`** "## 5 秒钟定位"
2. **`lte-iot-failure-cases.md`** — 找类似案例（9 个）
3. **`lte-iot-practical.md`** "## 错误码速查"

### 路径 C："我在做 LTE-IoT 模组驱动移植"（工程师）

1. **`lte-iot-deep-dive.md`** "## 蜂窝注册流程"
2. **`lte-iot-practical.md`** "## AT 命令 / QMI / RmNet"
3. **`lte-iot-deep-dive.md`** "## 协议栈分层"

### 路径 D："我在做低功耗 IoT 选型"（架构师）

1. **`lte-iot.md`** "## 三大类对比"
2. **`lte-iot-deep-dive.md`** "## PSM / eDRX"
3. **`lte-iot-practical.md`** "## 功耗数据"

### 路径 E："我在做蜂窝协议安全"（安全工程师）

1. **`lte-iot-deep-dive.md`** "## NAS / 鉴权 / 加密"
2. **`lte-iot-failure-cases.md`** 案例 2 / 7（APN 错 / SIM 不识别）
3. **`lte-iot-practical.md`** "## NAS EMM 拒绝原因"

## 主题速查矩阵

按问题找文档：

| 我想知道 | 看哪里 |
| --- | --- |
| 三大类（Cat 1 / M1 / NB-IoT）怎么选 | lte-iot.md "## 三大类对比" |
| 国内频段是哪些 | lte-iot.md "## 国内频段" |
| APN 怎么配 | lte-iot-practical.md "## APN 配置" |
| 搜不到网 | lte-iot-failure-cases.md 案例 1 |
| PDP 激活失败 | lte-iot-failure-cases.md 案例 2 |
| PSM 启用后下行丢 | lte-iot-failure-cases.md 案例 3 |
| DNS 解析失败 | lte-iot-failure-cases.md 案例 4 |
| 模组过温 | lte-iot-failure-cases.md 案例 5 |
| 模组重启（电流塌陷） | lte-iot-failure-cases.md 案例 6 |
| SIM 不识别 | lte-iot-failure-cases.md 案例 7 |
| NB-IoT 卡插 4G 设备 | lte-iot-failure-cases.md 案例 8 |
| 地下停车场注册不上 | lte-iot-failure-cases.md 案例 9 |
| CME ERROR 码 | lte-iot-practical.md "## +CME ERROR" |
| CMS ERROR 码 | lte-iot-practical.md "## +CMS ERROR" |
| TCP 错误码 | lte-iot-practical.md "## TCP / IP 错误" |
| NAS EMM 拒绝原因 | lte-iot-practical.md "## NAS EMM 拒绝原因" |
| 蜂窝注册流程 | lte-iot-deep-dive.md "## 蜂窝注册流程" |
| PSM 怎么配 | lte-iot-deep-dive.md "## PSM" |
| eDRX 怎么配 | lte-iot-deep-dive.md "## eDRX" |
| 协议栈分层 | lte-iot-deep-dive.md "## 协议栈分层" |
| NAS 状态机 | lte-iot-deep-dive.md "## NAS" |
| 鉴权 AKA | lte-iot-deep-dive.md "## 鉴权（AKA）" |
| 抓包工具 | lte-iot.md "## 抓包工具" |
| 模组选型 | lte-iot.md "## 典型芯片 / 模组" |
| 移动 vs 电信 vs 联通 | lte-iot.md "## 国内频段" |
| 与 5G RedCap 关系 | lte-iot.md "## 跟其它无线技术的关系" |
| 功耗数据 | lte-iot-deep-dive.md "## 功耗数据参考" |
| 产线测试清单 | lte-iot-practical.md "## 检查清单" |

## 关键概念地图

```text
LTE-IoT 协议栈
├── PHY 层
│   ├── 频段：FDD (B1/B3/B5/B8/B28) + TDD (B34/B38/B39/B40/B41)
│   ├── 带宽：Cat 1 20 MHz / Cat M1 1.4 MHz / NB-IoT 200 kHz
│   ├── 调制：QPSK / 16QAM
│   └── 覆盖增强：CE Level 0/1/2（重复 1/8/32~128 次）
│
├── MAC 层
│   ├── HARQ（4-8 进程）
│   ├── 调度（PDCCH / NPUSCH）
│   └── RACH（4 步 / 2 步）
│
├── RLC 层
│   ├── TM / UM / AM 三种模式
│   ├── 分段 / 重组
│   └── ARQ
│
├── PDCP 层
│   ├── 头压缩（ROHC）
│   ├── 加密（EEA1/2/3）
│   └── 完整性（EIA1/2/3）
│
├── RRC 层
│   ├── 状态：RRC_IDLE / RRC_CONNECTED
│   ├── 状态机：Setup / Reconfiguration / Release
│   └── PSM / eDRX
│
├── NAS 层
│   ├── EMM（移动性管理）
│   │   ├── 状态：EMM-DEREGISTERED / EMM-REGISTERED
│   │   ├── 附着 / 去附着 / TAU
│   │   ├── 鉴权（AKA）
│   │   └── 安全模式（Security Mode）
│   │
│   └── ESM（会话管理）
│       ├── 默认承载建立
│       ├── 专用承载
│       └── APN / IP 分配
│
└── EPS 端到端
    ├── E-UTRAN（基站）
    ├── EPC（核心网：MME + SGW + PGW）
    ├── PLMN（MCC + MNC）
    ├── Bearer（默认 + 专用）
    ├── QoS（QCI / ARP / MBR / GBR）
    └── 关键定时器
        ├── T3412（TAU 周期）
        ├── T3324（PSM active）
        ├── T3402（去附着 retry）
        └── T3346（PSM 抑制定时器）
```

## 文档关系图

```text
lte-iot.md (主题入口，概览)
   ↓ 引用
lte-iot-practical.md (速查，调试流程)
   ↓ 引用
lte-iot-deep-dive.md (原理，体系)
   ↓ 引用
lte-iot-failure-cases.md (案例，实战)
   ↓ 全部引用
lte-iot-index.md (本文件，导航)
```

## 学习路径推荐（按角色）

### 嵌入式软件工程师（LTE-IoT 模组驱动）

```text
入口 → 速查 → 原理 → 实战案例
0.5d   1d     2d     1d
```

### 物联网 / 移动资产硬件工程师

```text
入口 → 速查（电源 / 模组选型） → 实战案例 5 / 6 / 7
0.5d   0.5d                    0.5d
```

### 物联网解决方案架构师

```text
入口（三类对比） → 原理（PSM / eDRX） → 实战案例 9（覆盖）
0.5d            0.5d                  0.5d
```

### 测试工程师

```text
速查（错误码 / 5 秒定位） → 实战案例 → 入口（频段）
1d                       1d          0.5d
```

### 售前 / 产品经理

```text
入口（三大类对比 + 频段） → 实战案例（客户教育）
0.5d                      0.5d
```

## LTE-IoT 主题 vs 其它主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| **LTE-IoT** | **5** | **~60 KB** | **蜂窝 IoT + APN + PSM/eDRX + 移动性** |
| BLE | 5 | ~40 KB | 低功耗 + GATT + 配对 + 安全 |
| ZigBee | 5 | ~58 KB | Mesh + ZDO + ZCL + 安全 |
| Thread | 5 | ~55 KB | IPv6 + RPL + Border Router + 边界 |
| Matter | 5 | ~60 KB | 应用层 + 跨协议 + 调试 + 资源 |
| CAN | 8 | 120 KB | 实时多 master + 错误处理 + 演进 (FD/XL) |
| USB | 9 | ~130 KB | 描述符 + 类驱动 + DMA |
| I3C | 3 | ~17 KB | 协议兼容 + 总线恢复 |

**共同点**：

- 都有速查 + 原理 + 实战 + 导航 4 层结构
- 都有 failure-cases（产线死机案例）
- 都有 practical 中的"5 秒定位" / 速查表

**差异**：

- **LTE-IoT 重点**：蜂窝接入 + 移动性 + 授权频谱 + 网络协商（PSM/eDRX 跟运营商相关）
- **BLE 重点**：协议栈分层 + GATT 模型 + 配对安全
- **ZigBee 重点**：Mesh + ZDO 状态机
- **Thread 重点**：IPv6 + RPL 路由
- **Matter 重点**：应用层 + 跨协议整合

## 蜂窝 IoT 三大类选型决策

```text
按场景选：

速率需求 > 1 Mbps → Cat 1（POS / 车载 / 监控）
移动性要求高       → Cat 1 / Cat M1（车队 / 可穿戴）
覆盖要求极强       → NB-IoT（抄表 / 烟感 / 停车）
功耗要求极致       → NB-IoT + PSM（10 年电池）
成本敏感          → NB-IoT（模组 ~30 元）/ Cat 1 bis（~40 元）
语音需求          → Cat 1 / Cat M1（VoLTE）
```

**蜂窝 vs 非蜂窝**：

```text
短距（< 100m）+ 局域网 → BLE / ZigBee / Thread / Matter
中距（< 10km）+ 移动   → LTE-IoT (Cat 1 / Cat M1)
远距（< 50km）+ 静态   → LoRa / Sigfox
授权频谱要求           → LTE-IoT (Cat 1 / Cat M1 / NB-IoT)
非授权频谱             → BLE / ZigBee / LoRa / Wi-Fi
5G 过渡               → 5G RedCap (R17/R18)
```

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| lte-iot.md | 改版才更新 | 主题入口 |
| lte-iot-practical.md | 改版才更新 | 速查 / 调试流程 |
| lte-iot-deep-dive.md | 协议改版 / 5G 演进 | 原理体系 |
| lte-iot-failure-cases.md | **持续更新** | 产线案例 |
| lte-iot-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题（chips-com 其他目录）

- **`bus/ble.md`** — BLE（短距 IoT，与 LTE-IoT 互补）
- **`bus/zigbee.md`** — ZigBee（Mesh 局域网）
- **`bus/thread.md`** — Thread（IPv6 局域网）
- **`bus/matter.md`** — Matter（应用层跨协议）
- **`bus/mqtt-deep-dive.md`** — MQTT（常用于 LTE-IoT 业务层）
- **`bus/can-canopen.md`** — 车载 CAN（车机 / TBOX 与 Cat 1 集成）
- **`basic/can-phy.md`** — 物理层对比参考

## 一句话总结

LTE-IoT 是"中低速蜂窝 IoT 的事实标准"，强在覆盖（NB-IoT 164 dB MCL）、移动性（Cat 1 / Cat M1）、授权频谱、全国漫游。从原理到产线案例，5 篇笔记覆盖完整。和 BLE（短距）、LoRa（远距非授权）、5G RedCap（5G 过渡）是**互补**关系。

## 更新记录

- 2026-08-01: 初版，5 篇笔记全部完成（L4 闭环）
  - 三大类（Cat 1 / Cat M1 / NB-IoT）+ 9 个产线实战案例
  - 覆盖 PHY / MAC / RLC / PDCP / RRC / NAS / EPS 全栈
  - 包含 PSM / eDRX / DRX 三大省电机制
  - 包含 APN / 鉴权 / 安全 / QoS 关键流程
