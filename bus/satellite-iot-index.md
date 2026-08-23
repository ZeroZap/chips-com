# Satellite-IoT 主题总览

## 目标

Satellite-IoT（卫星物联网）是 chips-com 覆盖地面蜂窝盲区的关键无线技术，围绕"远洋 / 沙漠 / 极地 / 无人区 / 灾区"等无地面网络场景的物联网接入，已形成 5 篇专题笔记。本文档是**总览导航**，帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/satellite-iot-*.md
│
├── 速查层
│   └── satellite-iot-practical.md         调试流程速查 / 5 秒定位 / 错误码表
│
├── 原理层
│   └── satellite-iot-deep-dive.md         轨道 / 链路预算 / 多普勒 / 3GPP NTN / 北斗 RDSS / Iridium SBD 深挖
│
├── 实战层
│   └── satellite-iot-failure-cases.md     9 个产线实战案例（5 大路线全覆盖）
│
└── 导航
    └── satellite-iot-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 Satellite-IoT, 想入门" (新人)

按顺序读, 1-2 天能上手:

1. **`satellite-iot.md`** — 主题入口, 5 大技术路线, 10 分钟
2. **`satellite-iot-practical.md`** — 关键参数 / 5 秒定位 / 错误码
3. **`satellite-iot-deep-dive.md`** — 协议栈 + 链路预算 + 多普勒

### 路径 B: "我在做卫星 IoT 设备产线失败" (现场救火)

1. **`satellite-iot-practical.md`** "## 5 秒钟定位"
2. **`satellite-iot-failure-cases.md`** — 找类似案例（9 个）
3. **`satellite-iot-deep-dive.md`** "## 错误码速查" 章节

### 路径 C: "我在做卫星 IoT 协议栈移植" (工程师)

1. **`satellite-iot-deep-dive.md`** "## 3GPP NTN 协议栈" / "## Iridium SBD 协议栈"
2. **`satellite-iot-practical.md`** "## 抓包工具"
3. **`satellite-iot-failure-cases.md`** 案例 1 / 4（Doppler 补偿）

### 路径 D: "我在做户外定位 / 救援设备" (产品经理)

1. **`satellite-iot.md`** "## 5 大技术路线"
2. **`satellite-iot-deep-dive.md`** "## Garmin inReach" / "## 北斗短报文"
3. **`satellite-iot-practical.md`** "## 资费" / "## 户外测试"

### 路径 E: "我在做卫星 IoT 芯片选型" (架构师)

1. **`satellite-iot.md`** "## 关键芯片 / 模组"
2. **`satellite-iot-deep-dive.md`** "## 关键芯片 / 模组深挖"
3. **`satellite-iot-practical.md`** "## 检查清单"

### 路径 F: "我在做海外项目（美国 / 欧洲）" (海外)

1. **`satellite-iot.md`** "## Starlink IoT" / "## Iridium"
2. **`satellite-iot-failure-cases.md`** 案例 3 / 7（Iridium / Starlink）
3. **`satellite-iot-deep-dive.md`** "## Iridium SBD"

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 5 大路线选哪个 | satellite-iot.md "## 5 大技术路线对比" |
| 卫星搜不到 | satellite-iot-failure-cases.md 案例 1 |
| 频度超限 | satellite-iot-failure-cases.md 案例 2 |
| Iridium +SBDI 错误 | satellite-iot-failure-cases.md 案例 3 |
| NB-IoT NTN PRACH 失败 | satellite-iot-failure-cases.md 案例 4 |
| MOMSN 溢出 | satellite-iot-failure-cases.md 案例 5 |
| 北斗卡未激活 | satellite-iot-failure-cases.md 案例 6 |
| Starlink 无信号 | satellite-iot-failure-cases.md 案例 7 |
| 电文超长 | satellite-iot-failure-cases.md 案例 8 |
| 极地丢包 | satellite-iot-failure-cases.md 案例 9 |
| 链路预算 | satellite-iot-deep-dive.md "## 链路预算实战" |
| 多普勒补偿 | satellite-iot-deep-dive.md "## Doppler / RTD 补偿" |
| 3GPP NTN 协议栈 | satellite-iot-deep-dive.md "## 3GPP NTN" |
| 北斗 RDSS 协议 | satellite-iot-deep-dive.md "## 北斗短报文（RDSS）协议" |
| Iridium SBD 协议 | satellite-iot-deep-dive.md "## Iridium SBD 协议" |
| 5 秒定位 | satellite-iot-practical.md "## 5 秒钟定位" |
| +CME ERROR 错误码 | satellite-iot-practical.md "## NB-IoT NTN 错误码" |
| +SBDI 错误码 | satellite-iot-practical.md "## Iridium SBD 错误码" |
| 北斗错误码 | satellite-iot-practical.md "## 北斗短报文错误" |
| 抓包工具 | satellite-iot-practical.md "## 抓包工具" |
| 关键芯片 | satellite-iot.md "## 关键芯片 / 模组" |
| 户外测试 | satellite-iot-practical.md "## 调试步骤" |
| 资费 | satellite-iot-practical.md "## Iridium SBD 关键参数" |

## 关键概念地图

```text
Satellite-IoT 协议栈
│
├── 卫星轨道物理层
│   ├── LEO（500~2000 km）：Iridium / Starlink
│   │   ├── 路径损耗：~138 dB @ 400 MHz, ~154 dB @ 2 GHz
│   │   ├── 多普勒：±10 kHz @ 400 MHz
│   │   └── 过顶窗口：~10 min / 颗
│   ├── MEO（5000~25000 km）：GPS / 北斗 MEO
│   └── GEO（35786 km）：北斗 GEO / Inmarsat
│       ├── 路径损耗：~188 dB @ 1.5 GHz
│       ├── 时延：~600 ms 单跳
│       └── 覆盖：3 颗覆盖全球
│
├── 5 大技术路线
│   ├── NB-IoT NTN（3GPP R17+）
│   │   ├── 频段：L/S 频段（n254/n255/n256）
│   │   ├── 终端：蜂窝模组（移远 BG95-M3 / Nordic nRF9160）
│   │   ├── 接入：SIB-NTN + GSE + Doppler pre-compensation
│   │   └── 国内：2025+ 试商用
│   ├── 北斗短报文（RDSS）
│   │   ├── 频段：L 频段入站 + S 频段出站
│   │   ├── 容量：1000 汉字（普通）/ 1680（升级）
│   │   ├── 终端：中斗微星 / 华力创通 / 中电科
│   │   └── 国内：已商用（民用）
│   ├── Iridium / 铱星（SBD）
│   │   ├── 频段：L 频段（1616~1626.5 MHz）
│   │   ├── 容量：MO 340 B / MT 270 B
│   │   ├── 终端：Iridium 9602/9603/9770
│   │   └── 全球：已商用
│   ├── Starlink IoT（Direct to Cell）
│   │   ├── 频段：1.9 GHz（T-Mobile 美国段）
│   │   ├── 时延：20~40 ms
│   │   ├── 终端：Starlink 认证 LTE 模组
│   │   └── 国内：暂未覆盖
│   └── Garmin inReach / SPOT
│       ├── 网络：Iridium / Globalstar
│       ├── 业务：户外双向 SOS + 短报文
│       └── 形态：成品终端
│
├── 链路预算
│   ├── 自由空间损耗（FSPL）
│   ├── 多普勒频偏
│   ├── 多普勒变化率
│   ├── 卫星仰角（20°+ 最佳）
│   ├── 大气衰减 / 雨衰
│   └── 极化 / 指向损耗
│
├── 多普勒补偿（NTN 关键）
│   ├── Doppler pre-compensation
│   ├── RTD (Round Trip Delay) pre-compensation
│   └── GSE (GNSS Satellite Ephemeris)
│
├── 协议栈
│   ├── 3GPP NTN（NB-IoT / LTE-M）
│   │   ├── R17：NTN SI/WI
│   │   ├── R18：增强
│   │   └── R19：NR NTN
│   ├── 北斗 RDSS
│   │   ├── 入站帧（用户→卫星）
│   │   ├── 出站帧（卫星→用户）
│   │   └── 加密（AES-128 / SM4）
│   ├── Iridium SBD
│   │   ├── MO（Mobile Originated）
│   │   ├── MT（Mobile Terminated）
│   │   ├── MOMSN 16-bit 计数器
│   │   └── SBD DirectIP / Email Gateway
│   └── Starlink Direct to Cell
│       └── LTE 简化协议（私有）
│
├── 关键技术
│   ├── PRACH pre-compensation
│   ├── HARQ 时序调整
│   ├── eDRX / PSM
│   ├── 卫星过顶预测
│   └── 频度限制
│
└── 错误码
    ├── +CME ERROR（蜂窝）
    ├── +CEREG 状态
    ├── +SBDI 返回（Iridium）
    └── RDSS 错误码（北斗）
```

## 5 大技术路线对比

| 维度 | NB-IoT NTN | 北斗短报文 | Iridium SBD | Starlink IoT | Garmin inReach |
| --- | --- | --- | --- | --- | --- |
| 标准化 | 3GPP R17 | 国内军用 / 民用 | Iridium 私有 | SpaceX 私有 | Iridium / Globalstar |
| 轨道 | LEO + GEO | GEO + IGSO | LEO 66 颗 | LEO | LEO |
| 频段 | L/S 频段 | L 频段入站 + S 频段出站 | L 频段 | 1.9 GHz | L 频段 |
| 容量 | 26 / 127 kbps | 1000 汉字 | 340 B/条 | 数十 kbps | 160 字符 |
| 时延 | 5~15 s | 1~5 s | 5~30 s | 5~15 s | 5~30 s |
| 国内可用 | 2025+ | 已商用 | 需卫星卡 | 否 | 已商用 |
| 终端 | 蜂窝模组 | 北斗 RDSS 模组 | Iridium 模组 | LTE 模组 | 成品 |
| 资费 | 运营商流量 | 北斗卡 | $0.05/条 | T-Mobile 套餐 | $14.95/月起 |
| 典型场景 | 蜂窝盲区 IoT | 国内户外救援 | 全球资产追踪 | 美国户外 | 户外运动 |

## 文档关系图

```text
satellite-iot.md (主题入口, 概览)
   ↓ 引用
satellite-iot-practical.md (速查, 调试流程)
   ↓ 引用
satellite-iot-deep-dive.md (原理, 体系)
   ↓ 引用
satellite-iot-failure-cases.md (案例, 实战)
   ↓ 全部引用
satellite-iot-index.md (本文件, 导航)
```

## 学习路径推荐（按角色）

### 嵌入式软件工程师（卫星 IoT 协议栈开发）

```text
入口 → 速查 → 原理 → 实战案例
0.5d   0.5d   2d     1d
```

### 户外救援 / 测绘设备硬件工程师

```text
入口（5 大路线） → 速查（关键参数） → 原理（北斗 RDSS） → 实战案例 2/6
0.5d              0.5d                       1d                  1d
```

### 海外项目架构师

```text
入口（5 大路线 + 选型） → 实战案例 3/7（Iridium/Starlink） → 原理（链路预算）
0.5d                                  1d                                1d
```

### 卫星通信协议栈移植工程师

```text
原理（3GPP NTN / Iridium SBD / 北斗 RDSS） → 实战案例 4（Doppler） → 速查（AT 命令）
2d                                          1d                       0.5d
```

### 产品经理（卫星 IoT 选型）

```text
入口（5 大路线） → 速查（资费 + 关键参数） → 实战案例（哪些坑）
0.5d              0.5d                          1d
```

## Satellite-IoT 主题 vs 其它主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| **Satellite-IoT** | **5** | **~85 KB** | **远距覆盖 / 5 大路线 / 链路预算 / 户外实战** |
| LTE-IoT | 5 | ~75 KB | 蜂窝 IoT（NB-IoT / Cat-M / Cat 1）|
| LoRa | 5 | ~70 KB | 远距免许可（Sub-GHz）|
| BLE | 5 | ~40 KB | 低功耗短距（2.4 GHz）|
| Matter | 5 | ~60 KB | 智能家居协议（IP）|
| Thread | 5 | ~50 KB | 低功耗 Mesh（IEEE 802.15.4）|
| ZigBee | 5 | ~60 KB | 智能家居 Mesh（IEEE 802.15.4）|

**共同点**:

- 都有速查 + 原理 + 实战 + 导航 4 层结构
- 都有 failure-cases（产线死机案例）
- 都有 practical 中的"5 秒定位" / 速查表

**差异**:

- Satellite-IoT 重点: 5 大路线（蜂窝 / 北斗 / Iridium / Starlink / Garmin）+ 链路预算 + 多普勒（卫星 IoT 特色）
- LTE-IoT 重点: 蜂窝接入（Cat 1 / M1 / NB1/NB2）（蜂窝特色）
- LoRa 重点: 免许可频段 + LoRaWAN NS（远距免许可特色）
- BLE 重点: GATT 模型 + 配对安全（短距特色）

**互补关系**:

```text
Satellite-IoT  → 全球 / 远洋 / 沙漠 / 极地（地面不可达）
LTE-IoT        → 城市 / 蜂窝覆盖区（高数据量）
LoRa / Sigfox  → 城郊 / 工业（中等距离 + 自建网）
BLE / ZigBee   → 短距（10~100 m）
```

实战典型方案：

```text
户外追踪器：
  - 正常区域：LTE-IoT（NB-IoT 省流量）
  - 盲区：Satellite-IoT（北斗 + Iridium 双模）
  - 短距：BLE（手机 App 配置）

智慧农业：
  - 田地：LoRa（自建网关）
  - 远田：NB-IoT
  - 极端偏远：Satellite-IoT（北斗短报文）

智慧物流（集装箱 / 货车）：
  - 城市道路：LTE Cat 1
  - 跨境 / 海上：Satellite-IoT（Iridium SBD）
```

## 关键芯片 / 模组速查

| 模组 | 路线 | 平台 | 特点 |
| --- | --- | --- | --- |
| 移远 BG95-M3 / BG77 | NB-IoT NTN | Qualcomm MDM9205 | 主流海外方案 |
| 移远 CC200A | NB-IoT NTN + LTE | Linux OpenCPU | 高端 IoT 网关 |
| 芯讯通 SIM7080G | NB-IoT NTN + GNSS | Qualcomm | 多频段 |
| Nordic nRF9160 + NTN | NB-IoT NTN | Nordic SiP | 集成 M33 应用核 |
| 中斗微星 ZD-V100 | 北斗短报文 | RDSS + RNSS | 国产化 |
| 中电科 CETC-9 | 北斗短报文 | 加固型 | 国产化 |
| 华力创通 HWA-RDSS-101 | 北斗短报文 | 模块化 | 国产化 |
| Iridium 9602 | Iridium SBD | Iridium 经典 | 短数据 |
| Iridium 9603 | Iridium SBD | Iridium 新 | 短数据 |
| Iridium 9770 | Iridium SBD + Edge | Iridium | 新一代 IoT |
| Quectel BG95-M3 NTN fw | NB-IoT NTN | Qualcomm | 海外主流 |
| Garmin inReach Mini 2 | Iridium 双向 | Garmin 成品 | 户外运动 |
| SPOT X | Globalstar | SPOT 成品 | 户外单向 |

## 关键错误码速查

| 错误码 | 路线 | 含义 |
| --- | --- | --- |
| `+CME ERROR: 30` | NB-IoT NTN | NO NETWORK 搜不到网络 |
| `+CME ERROR: 514` | NB-IoT NTN | BUSY 并发 AT 命令阻塞 |
| `+CME ERROR: 100` | NB-IoT NTN | INVALID SIM USIM 卡无效 |
| `+CME ERROR: 133` | NB-IoT NTN | SERVICE NOT SUBSCRIBED 业务未订 |
| `+SBDI: 0` | Iridium SBD | Success |
| `+SBDI: 1` | Iridium SBD | Timeout |
| `+SBDI: 3` | Iridium SBD | MO too many bytes > 340 B |
| `+SBDI: 4` | Iridium SBD | Gateway not available |
| `+SBDI: 7` | Iridium SBD | MOMSN out of range |
| `+SBDI: 12` | Iridium SBD | IMEI not provisioned |
| `RDSS_AUTH_FAIL` | 北斗 | 入网 / 认证失败 |
| `RDSS_TX_FREQ_LIMIT` | 北斗 | 频度超限（1 min/1 条）|
| `RDSS_LEN_EXCEED` | 北斗 | 电文超长（> 1000 汉字）|
| `+CEREG: 0` | NB-IoT NTN | NOT REGISTERED |
| `+CEREG: 1` | NB-IoT NTN | REGISTERED HOME |
| `+CEREG: 5` | NB-IoT NTN | REGISTERED ROAMING |

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| satellite-iot.md | 改版才更新 | 主题入口 |
| satellite-iot-practical.md | 改版才更新 | 速查 / 调试流程 |
| satellite-iot-deep-dive.md | 协议改版 / 3GPP R18+ | 原理体系 |
| satellite-iot-failure-cases.md | **持续更新** | 产线案例 |
| satellite-iot-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题（chips-com 其他目录）

- **`bus/lte-iot-*.md`** — 蜂窝 IoT（NB-IoT / Cat-M / Cat 1 地面方案）
- **`bus/lora-*.md`** — LoRa 远距免许可（地面自建网）
- **`bus/ble-*.md`** — BLE 短距（手机 App 配置通道）
- **`bus/can-*.md`** — CAN 总线（车载诊断）
- **`bus/thread-*.md`** — Thread Mesh（智能家居）
- **`bus/matter-*.md`** — Matter 协议（智能家居）
- **`basic/can-phy.md`** — 物理层对比参考

## 一句话总结

Satellite-IoT 是"地面网络不可达时的兜底"，强在覆盖（远洋 / 沙漠 / 极地 / 灾区）、卫星注册（Doppler / RTD 补偿）、短报文容量。**5 大路线各有定位**：

- **NB-IoT NTN**：3GPP 标准 + 蜂窝融合（2025+ 主流）
- **北斗短报文**：国内独有能力（民用 + 救援）
- **Iridium SBD**：全球资产追踪（66 颗 LEO）
- **Starlink IoT**：美国主导（IoT 模式 2025+）
- **Garmin inReach**：户外运动双向

从原理到产线案例，5 篇笔记覆盖完整。和 LTE-IoT（地面蜂窝）、LoRa（地面自建）、BLE（短距）是**互补**关系。

## 更新记录

- 2026-08-01: 初版, 5 篇笔记全部完成 (L4 闭环)
  - 来源：_Inbox/Satellite-IoT-2026-08-01-candidates.md 9 条候选 + 实战补充
  - 覆盖：NB-IoT NTN / 北斗短报文 / Iridium SBD / Starlink IoT / Garmin inReach 5 大路线
  - 案例：9 个产线实战（频度超限 / IMEI 未注册 / Doppler 补偿 / MOMSN 溢出 / 卡未激活 / 极地丢包等）
