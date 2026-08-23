# PLB 主题总览

## 目标

PLB（Personal Locator Beacon）是 chips-com 的户外紧急救援信标主题，围绕"COSPAS-SARSAT 国际救援卫星系统、406 MHz 数字求救信号、121.5 MHz 近场测向、GNSS 定位集成"形成 5 篇专题笔记。本文档是**总览导航**，帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/plb-*.md
│
├── 速查层
│   └── plb-practical.md                调试流程速查 / 5 秒定位 / 错误码表 / 烧录脚本
│
├── 原理层
│   └── plb-deep-dive.md                COSPAS-SARSAT / 406 MHz 编码 / BCH / UIN / GNSS
│
├── 实战层
│   └── plb-failure-cases.md            9 个产线实战案例（UIN 重复 / BCH 错 / 电池 / 防水）
│
├── 入口
│   └── plb.md (主题入口, 概览)
│
└── 导航
    └── plb-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 PLB, 想入门" (新人)

按顺序读, 1-2 天能上手:

1. **`plb.md`** — 主题入口, 5 分钟
2. **`plb-practical.md`** — 关键参数 / 5 秒定位 / 烧录脚本
3. **`plb-deep-dive.md`** — COSPAS-SARSAT 系统 + 406 MHz 编码

### 路径 B: "我在做 PLB 产线失败" (现场救火)

1. **`plb-practical.md`** "## 5 秒钟定位"
2. **`plb-failure-cases.md`** — 找类似案例（9 个）
3. **`plb-deep-dive.md`** "## 关键芯片深度" 章节

### 路径 C: "我在做 PLB 固件 / 协议栈" (工程师)

1. **`plb-deep-dive.md`** "## 406 MHz 物理层" + "## BCH 纠错"
2. **`plb-practical.md`** "## 烧录 UIN 实战"
3. **`plb-failure-cases.md`** 案例 2 (BCH 错) + 案例 8 (协议码错)

### 路径 D: "我在做 PLB 认证 (COSPAS-SARSAT T.007)" (认证工程师)

1. **`plb-deep-dive.md`** "## 认证深挖"
2. **`plb-practical.md`** "## 认证检查清单"
3. **`plb-failure-cases.md`** 案例 2 / 3 (BCH + 121.5 频偏)

### 路径 E: "我在做 PLB 选型" (架构师 / 采购)

1. **`plb.md`** "## 关键芯片 / 模块"
2. **`plb-deep-dive.md`** "## 关键芯片深度" (Microsemi / 海积 / LKT4211 / u-blox)
3. **`plb-practical.md`** "## 性能数据参考"

### 路径 F: "我在做 PLB 应急救援 / 户外产品" (产品经理)

1. **`plb.md`** 主题入口
2. **`plb.md`** "## 跟卫星通讯 / Garmin inReach 的关系"
3. **`plb-failure-cases.md`** 案例 5 (误触) + 案例 9 (电池低温)

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 什么是 PLB | plb.md "## 定位" |
| 跟 EPIRB / ELT 区别 | plb.md "## 跟 EPIRB / ELT 的关系" |
| 跟 inReach 区别 | plb.md "## 跟卫星通讯 / Garmin inReach 的关系" |
| COSPAS-SARSAT 系统架构 | plb-deep-dive.md "## COSPAS-SARSAT 系统架构" |
| 406 MHz 物理层 | plb-deep-dive.md "## 406 MHz 物理层" |
| BCH 纠错 | plb-deep-dive.md "## 406 MHz 物理层" "## 协议解析实战" |
| UIN 编码规则 | plb-deep-dive.md "## UIN 编码" |
| MID 国家码表 | plb-deep-dive.md "## MID 分配" |
| 121.5 MHz 测向 | plb-deep-dive.md "## 121.5 MHz 测向原理" |
| GNSS 集成 | plb-deep-dive.md "## GNSS 集成" |
| 多普勒定位原理 | plb-deep-dive.md "## 多普勒定位原理" |
| 整机硬件 | plb-deep-dive.md "## 整机架构" |
| Microsemi Syracuse 4 | plb-deep-dive.md "## Microsemi（Microchip）Syracuse 4 系列" |
| 国产海积 HZB406 | plb-deep-dive.md "## 国产海积 HZB406" |
| LKT4211 模组 | plb-deep-dive.md "## LKT4211（121.5 MHz 模组）" |
| 5 秒定位 | plb-practical.md "## 5 秒钟定位" |
| 抓包工具 | plb-practical.md "## 抓包工具" |
| 烧录 UIN 脚本 | plb-practical.md "## 烧录 UIN 实战" |
| 电池测试 | plb-practical.md "## 触发测试" |
| 认证检查清单 | plb-practical.md "## 认证检查清单" |
| 注册 UIN | plb-practical.md "## 配网流程" |
| UIN 重复问题 | plb-failure-cases.md 案例 1 |
| BCH 编码错 | plb-failure-cases.md 案例 2 |
| 121.5 MHz 频偏 | plb-failure-cases.md 案例 3 |
| 电池续航短 | plb-failure-cases.md 案例 4 |
| 防误触设计 | plb-failure-cases.md 案例 5 |
| 浸水失效 | plb-failure-cases.md 案例 6 |
| GNSS 拉低频慢 | plb-failure-cases.md 案例 7 |
| 协议码错 | plb-failure-cases.md 案例 8 |
| 电池低温跌容 | plb-failure-cases.md 案例 9 |

## 关键概念地图

```text
COSPAS-SARSAT 国际救援系统
├── Space Segment 卫星段
│   ├── LEOSAR 低轨道 (SARR 仪器)
│   │   ├── 6 颗现役 (NOAA / MetOp / Elektro)
│   │   ├── 850~1000 km 极轨道
│   │   ├── 多普勒定位能力
│   │   └── 1544.5 MHz 转发到 LUT
│   │
│   ├── GEOSAR 静轨道 (SARR 仪器)
│   │   ├── 8 颗现役 (GOES / MSG / Elektro)
│   │   ├── 35786 km 赤道静轨
│   │   ├── 即时接收 (无多普勒)
│   │   └── 极地盲区
│   │
│   └── MEOSAR 中轨道 (Galileo / GLONASS / GPS)
│       ├── 2024+ 全覆盖
│       ├── LEO + GEO 优势合并
│       └── 全球无缝 + 多普勒定位
│
├── Ground Segment 地面段
│   ├── LEOLUT (LEO Local User Terminal)
│   │   ├── 接收 SARR 1544.5 MHz
│   │   ├── 多普勒频移 → 位置 (±5 km)
│   │   └── 全球 50+ 节点
│   │
│   ├── GEOLUT (GEO Local User Terminal)
│   │   ├── 接收 GEO SARR 1544.5 MHz
│   │   ├── 解析 PLB 报文 + GNSS 位置
│   │   └── 全球 30+ 节点
│   │
│   ├── MCC (Mission Control Center)
│   │   ├── 任务控制中心
│   │   ├── 全球 30+ 节点互联
│   │   └── 根据 UIN 查注册国
│   │
│   └── RCC (Rescue Coordination Center)
│       ├── 救援协调中心
│       ├── 1 国家 1 个 (中国: 南海救助局)
│       └── 协调 SAR 队伍出动
│
└── Beacon 406 MHz 信标
    ├── PLB (个人)
    │   ├── 手动触发
    │   ├── MID 412 (中国)
    │   └── 户外 / 登山 / 远洋
    │
    ├── EPIRB (船用)
    │   ├── 自动 / 手动触发
    │   ├── 水压释放
    │   └── 海洋救生
    │
    └── ELT (航空)
        ├── G 触发器 + 手动
        ├── 24-bit ICAO 地址
        └── 飞机坠落

PLB 整机体系
├── 物理层
│   ├── 406 MHz 数字信号 (5W, BPSK 400 bps)
│   ├── 121.5 MHz 模拟信号 (50~100 mW, AM)
│   └── GNSS 信号 (L1, 多模)
│
├── 协议层
│   ├── BCH(202, 112) 短消息
│   ├── BCH(250, 144) 长消息 (含位置)
│   ├── UIN 60 bit 编码 (MID + Protocol + ID)
│   ├── Preamble + Sync + BCH
│   └── 0.5 s 发射 / 50 s 周期
│
├── 频率
│   ├── 406.0 ~ 406.1 MHz 数字 (上行)
│   ├── 121.5 MHz 模拟 (近场测向)
│   ├── 1544.5 MHz LEOSAR 转发
│   └── 1575.42 / 1561 / 1602 MHz GNSS
│
├── 编码
│   ├── BPSK 400 bps
│   ├── BCH 多项式 (T.001 标准)
│   ├── 短消息 112 bit → 202 bit BCH
│   ├── 长消息 144 bit → 250 bit BCH
│   └── 突发错 40 / 60 bit 可纠
│
├── 定位
│   ├── GNSS (优选) ±50 m
│   ├── 多普勒 (LEO) ±5 km
│   ├── 121.5 MHz 测向 (近场 5~10 km)
│   └── 时延 < 1 h (LEO+GEO 合并)
│
└── 关键芯片
    ├── 406 MHz 发射: Microsemi Syracuse 4 / 海积 HZB406
    ├── 121.5 MHz: LKT4211 / Si4063
    ├── GNSS: u-blox MAX-M10 / 中科微 AT6558R
    └── MCU: STM32L073 / 国产 GD32L233
```

## 文档关系图

```text
plb.md (主题入口, 概览)
   ↓ 引用
plb-practical.md (速查, 调试流程)
   ↓ 引用
plb-deep-dive.md (原理, 体系)
   ↓ 引用
plb-failure-cases.md (案例, 实战)
   ↓ 全部引用
plb-index.md (本文件, 导航)
```

## 学习路径推荐（按角色）

### 嵌入式软件工程师（PLB 固件 / 协议栈开发）

```text
入口 → 速查 → 原理 (BCH 章节) → 实战案例 (案例 2 BCH 错)
0.5d   0.5d   2d                     1d
```

### 嵌入式硬件工程师（PLB RF 电路 / 整机）

```text
入口 → 速查 → 原理 (整机架构) → 实战案例 (案例 6 防水 + 7 GNSS 天线)
0.5d   0.5d   2d                   1d
```

### 卫星通讯 / 应急救援设备认证工程师

```text
入口 → 原理 (COSPAS-SARSAT 架构) → 速查 (认证检查清单) → 实战 (案例 2/3)
0.5d   2d                              0.5d                       1d
```

### 户外 / 应急救援产品经理

```text
入口 → 原理 (PLB 跟 inReach 区别) → 实战 (案例 5 误触 + 9 电池低温)
0.5d   1d                              0.5d
```

### 产品架构师 / 采购（PLB 选型）

```text
入口（芯片清单） → 原理（关键芯片深度） → 速查（性能数据参考）
0.5d              1d                        0.5d
```

## PLB 主题 vs 其它主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| **PLB** | **5** | **~75 KB** | **国际救援卫星系统 + 应急通讯 + 防水 + 低温** |
| BLE | 5 | ~40 KB | 低功耗 + GATT + 配对 + 安全 |
| LoRa | 5 | ~75 KB | 远距 + LoRaWAN + 低功耗 |
| Matter | 5 | ~60 KB | 智能家居 + Thread/Wi-Fi 桥接 |
| Thread | 5 | ~50 KB | 802.15.4 + IPv6 + Mesh |
| LTE-IoT | 5 | ~75 KB | NB-IoT / Cat-M + 蜂窝 |
| USB | 9 | ~130 KB | 描述符 + 类驱动 + DMA |
| CAN | 8 | 120 KB | 实时多 master + 错误处理 |

**PLB 主题特色**：

- **国际标准体系**：COSPAS-SARSAT 强标准（BCH / UID / 频段 / 周期都强制）
- **认证驱动**：T.007 认证是生死线（不通过不能上市）
- **人命关天**：误触发成本 5 万 + 救援出动，错报 / 漏报都不可接受
- **5 年电池**：长期待机 + 触发后 24+ h 持续发射
- **多模融合**：406 MHz + 121.5 MHz + GNSS 三个独立子系统

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| plb.md | 改版才更新 | 主题入口 |
| plb-practical.md | 改版才更新 | 速查 / 调试流程 |
| plb-deep-dive.md | COSPAS-SARSAT 标准改版 | 原理体系 |
| plb-failure-cases.md | **持续更新** | 产线案例 |
| plb-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题（chips-com 其他目录）

PLB 是户外 / 应急救援主题，跟以下主题有交集：

- **`basic/gnss.md`**（如果有）— GNSS 协议族（GPS / GLONASS / 北斗）
- **`basic/lora-deep-dive.md`** — LoRa 长距（户外场景有部分替代关系）
- **`bus/matter-deep-dive.md`** — Matter 智能家居（户外场景少）
- **`bus/thread-deep-dive.md`** — Thread 802.15.4（Mesh 户外传感）
- **`bus/ble-deep-dive.md`** — BLE 近场（户外穿戴）
- **`bus/can-canopen-deep-dive.md`** — 工业控制（户外基站）
- **`basic/embedded-power.md`**（如果有）— 嵌入式低功耗（PLB 5 年电池设计）

## 一句话总结

PLB 是"国际救援卫星系统的个人分支"，强在 COSPAS-SARSAT 全球无缝覆盖、5 年电池、24 小时持续求救、防水防误触。从协议（BCH / UIN / 编码）到产线案例（UIN 重复 / 频偏 / 防水失效），5 篇笔记覆盖完整。跟 EPIRB（船用）/ ELT（航空）同协议不同形态，跟 Garmin inReach 互补不互替。

## 更新记录

- 2026-08-01: 初版, 5 篇笔记全部完成 (L4 闭环)
  - 来源：_Inbox/PLB-2026-08-01-candidates.md 9 条候选 + COSPAS-SARSAT T.001/T.007 实战补充
  - 总规模：~75 KB（含 9 个产线实战案例）
