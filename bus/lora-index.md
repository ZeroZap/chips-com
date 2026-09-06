# LoRa / LoRaWAN 主题总览

## 目标

LoRa / LoRaWAN 是 chips-com 的核心无线协议主题之一，围绕"远距低功耗 IoT（10 km+ 视距、电池寿命 5~10 年）"已经形成 5 篇专题笔记。本文档是**总览导航**，帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/lora-*.md
│
├── 速查层
│   └── lora-practical.md                调试流程速查 / 5 秒定位 / 错误码表
│
├── 原理层
│   └── lora-deep-dive.md                调制 / MAC / Class A/B/C / 配网 / ADR / NS
│
├── 实战层
│   └── lora-failure-cases.md            9 个产线实战案例
│
└── 导航
    └── lora-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 LoRa, 想入门" (新人)

按顺序读, 1-2 天能上手:

1. **`lora.md`** — 主题入口, 5 分钟
2. **`lora-practical.md`** — 频段 / SF/BW / 5 秒定位
3. **`lora-deep-dive.md`** — 物理层调制 + Class 状态机

### 路径 B: "我在做 LoRa 设备产线失败" (现场救火)

1. **`lora-practical.md`** "## 5 秒钟定位"
2. **`lora-failure-cases.md`** — 找类似案例（9 个）
3. **`lora-deep-dive.md`** "## 错误码速查"

### 路径 C: "我在做 LoRa 协议栈移植" (工程师)

1. **`lora-deep-dive.md`** "## 物理层（PHY）" + "## MAC 帧"
2. **`lora-practical.md`** "## 抓包工具"
3. **`lora-deep-dive.md`** "## SX1262 关键 API"

### 路径 D: "我在做 LoRaWAN 安全 / 配网" (安全工程师)

1. **`lora-deep-dive.md`** "## OTAA 配网流程" + "## 安全"
2. **`lora-failure-cases.md`** 案例 1（DevNonce）+ 案例 2（MIC Failure）+ 案例 8（Frame Counter 溢出）
3. **`lora-practical.md`** "## 错误码速查" 的安全相关条目

### 路径 E: "我在做 LoRaWAN 大规模部署" (架构师)

1. **`lora.md`** "## Network Server" + "## 典型芯片"
2. **`lora-deep-dive.md`** "## Network Server 架构" + "## SX1302 关键特性"
3. **`lora-practical.md`** "## 性能数据参考" + `lora-failure-cases.md` 案例 4（GW 容量打满）

### 路径 F: "我在做 LoRa 选型" (架构师 / PM)

1. **`lora.md`** "## 跟其它无线协议的关系" + "## 频段"
2. **`lora-deep-dive.md`** "## 性能数据参考"
3. **`lora-failure-cases.md`** 案例 6（频段错配）

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 频段怎么选 | lora.md "## 频段" |
| 频段错配怎么办 | lora-failure-cases.md 案例 6 / 9 |
| 距离近 | lora-failure-cases.md 案例 7 |
| 怎么选 SF / BW | lora-practical.md "## SF / BW / 速率关系" |
| ADR 怎么开 | lora-deep-dive.md "## ADR" |
| ADR 不收敛 | lora-failure-cases.md 案例 4 |
| OTAA vs ABP | lora.md "## 配网：OTAA vs ABP" |
| AppKey 怎么配 | lora-deep-dive.md "## OTAA 配网流程" |
| Join Fail | lora-failure-cases.md 案例 1 |
| MIC Failure | lora-failure-cases.md 案例 2 |
| Duty Cycle 1% | lora-practical.md "## EU868" + lora-failure-cases.md 案例 3 |
| Class A/B/C 区别 | lora-deep-dive.md "## Class A / B / C 状态机" |
| Class C 资源占用 | lora-failure-cases.md 案例 4 |
| Class B 漂移 | lora-failure-cases.md 案例 5 |
| Frame Counter 溢出 | lora-failure-cases.md 案例 8 |
| NS 怎么选 | lora.md "## Network Server" |
| ChirpStack 部署 | lora-deep-dive.md "## ChirpStack 组件" |
| 抓包工具 | lora-practical.md "## 抓包工具" |
| 错误码 | lora-practical.md "## 错误码速查" |
| SX1262 怎么用 | lora-deep-dive.md "## SX1262 关键 API" |
| LoRaMac-node 移植实战 | lora-deep-dive.md "## LoRaMac-node 协议栈移植实战" |
| SX1302 GW 设计 | lora-deep-dive.md "## SX1302 关键特性" |
| 私有频段 | lora-failure-cases.md 案例 9 |
| LoRa vs NB-IoT | lora.md "## 跟其它无线协议的关系" |
| LoRa CSS 工业抗干扰 | lora-deep-dive.md "### LoRa CSS 工业抗干扰" |
| LoRa 天线设计实战 | lora-deep-dive.md "### LoRa 天线设计实战" |
| Frame Counter MAX_FCNT_GAP | lora-deep-dive.md "### Frame Counter（FCnt）实战" |
| 移动场景 ADR 失效 | lora-failure-cases.md 案例 4 → 移动场景子段 |
| 气体探测器部署 | lora-failure-cases.md 案例 12 |
| 智慧农业部署 | lora-failure-cases.md 案例 13 |
| 智能水表 7 大掉线 | lora-failure-cases.md 案例 14 |
| Join-Storm 5000 节点 | lora-failure-cases.md 案例 15 |
| 14 步 LoRa 调试方法论 | lora-practical.md "## 14 步 LoRa 调试方法论" |
| Dragino 14 步产线 checklist | lora-practical.md "### Dragino Wiki 14 步 checklist" |
| SX1301 网关 5 个长期故障 | lora-failure-cases.md 案例 16 |
| LoRa 低功耗 3 陷阱 + TCXO | lora-failure-cases.md 案例 17 |
| chirp 物理层 + 3 翻车坑 | lora-failure-cases.md 案例 18 |
| CN470 同异频 + 8 子带映射 | lora-failure-cases.md 案例 19 |
| STM32WL LDRO + 32MHz 温漂 | lora-failure-cases.md 案例 20 |
| Daviteq 16 项 LED 状态机 | lora-failure-cases.md 案例 21 |
| 农业 SF7 硬编码 6 周放弃 | lora-failure-cases.md 案例 22 |
| World Bank 城市空气 4 多故障 | lora-failure-cases.md 案例 23 |
| 私网 LoRa 300 节点 99.8% | lora-failure-cases.md 案例 24 |
| LR1120+STM32L433 1/10 join 间歇失败 | lora-failure-cases.md 案例 25 |
| Azure IoT Edge LNS 24h 静默卡死 | lora-failure-cases.md 案例 26 |
| 商业部署 5 坑（ADR + 移动节点） | lora-failure-cases.md 案例 27 |
| SX1278 果园 500 亩 120 节点 1 年稳 | lora-failure-cases.md 案例 28 |
| LoRaWAN 到云端 + DevEUI 大小端 + FCnt | lora-failure-cases.md 案例 29 |

## 关键概念地图

```text
LoRa / LoRaWAN
├── 物理层 (PHY)
│   ├── Chirp Spread Spectrum (啁啾扩频)
│   ├── SF (Spreading Factor) 7~12
│   ├── BW (Bandwidth) 125/250/500 kHz
│   ├── CR (Coding Rate) 4/5~4/8
│   ├── Preamble + Sync + SFD
│   └── Sensitivity -123 ~ -137 dBm
│
├── MAC 层 (LoRaWAN)
│   ├── MHDR (MType / Major)
│   ├── FHDR (DevAddr / FCtrl / FCnt / FOpts)
│   ├── FPort (0=MAC, 1~223=App, 224~255=Reserved)
│   ├── FRMPayload (用户数据 / MAC 命令)
│   └── MIC (4 字节 CMAC/AES-128)
│
├── 设备类型 (Class)
│   ├── Class A (上行后两个短下行窗口, 最低功耗)
│   ├── Class B (同步下行, beacon + ping slot)
│   └── Class C (持续下行接收, 功耗最高)
│
├── 配网
│   ├── OTAA (动态 Join, 每次换 NwkSKey/AppSKey)
│   ├── ABP (烧录固定, 免 Join 但重放风险)
│   ├── DevEUI / AppEUI / DevNonce
│   └── AppKey / NwkSKey / AppSKey
│
├── 安全
│   ├── AppKey (128-bit 根密钥)
│   ├── MIC 校验 (CMAC/AES-128)
│   ├── Frame Counter (16-bit, 防重放)
│   └── AES-128 CTR 加密 payload
│
├── ADR (Adaptive Data Rate)
│   ├── NS 端评估 (20 帧窗口)
│   ├── LinkADRReq 命令
│   └── 收敛到最优 SF/BW
│
├── 频段 (Regional Parameters)
│   ├── CN470 (96 上行 + 48 下行, 国内)
│   ├── EU868 (8 信道, 1% Duty Cycle)
│   ├── US915 (64 上行 + 8 下行, 子带)
│   ├── AS923 (东南亚)
│   ├── AU915 (澳大利亚)
│   └── IN865 (印度)
│
├── 芯片
│   ├── 端点: SX1276/SX1278/SX1262/SX1268/LLCC68/ASR6601
│   ├── 网关: SX1302/SX1303 (8 信道)
│   └── 2.4 GHz: LoRa1280
│
└── Network Server
    ├── TTN (公有云, 免费层 200 节点)
    ├── ChirpStack (开源自建, PG + Redis + MQTT)
    ├── Helium (区块链激励, 衰落)
    ├── AWS IoT Core for LoRaWAN
    └── 自建 (私有部署)
```

## 文档关系图

```text
lora.md (主题入口, 概览)
   ↓ 引用
lora-practical.md (速查, 调试流程)
   ↓ 引用
lora-deep-dive.md (原理, 体系)
   ↓ 引用
lora-failure-cases.md (案例, 实战)
   ↓ 全部引用
lora-index.md (本文件, 导航)
```

## 学习路径推荐（按角色）

### 嵌入式软件工程师（LoRa 协议栈开发）

```text
入口 → 速查 → 原理 → 实战案例
0.5d   0.5d   2d     1d
```

### 物联网 / 可穿戴硬件工程师

```text
入口 → 速查 → 实战案例（天线篇） → 物理层深入
0.5d   0.5d   1d                 1d
```

### Network Server 运维 / 部署

```text
入口（NS 选型） → 原理（GW 协议） → 实战案例（GW 容量 / Class B）
0.5d            1d                 0.5d
```

### 移动 / Web 端开发者（应用层）

```text
速查（应用层 payload） → 实战案例 1（DevNonce） + 案例 8（Frame Counter）
0.5d                0.5d
```

### 安全工程师

```text
原理 (OTAA + 密钥) → 实战案例 1/2/8
1d     1d
```

### 产品架构师（选型 / 商务）

```text
入口（跟其它协议对比 + NS 选型） → 原理（性能数据） → 实战案例 6（频段错配）
0.5d              0.5d                       0.5d
```

## LoRa 主题 vs 其它主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| **LoRa** | **5** | **~62 KB** | **远距 + 低功耗 + Class + 配网 + NS** |
| BLE | 5 | ~49 KB | 短距 + GATT + 配对 + 安全 |
| CAN | 8 | 120 KB | 实时多 master + 错误处理 + 演进 (FD/XL) |
| USB | 9 | ~130 KB | 描述符 + 类驱动 + DMA |
| I2C | 12 | 151 KB | 协议兼容性 + 总线恢复 |
| SPI | 6 | 75 KB | 多从 / 菊花链 / 高速 |
| UART | 6 | 80 KB | RS485 / 流控 / 异步日志 |
| J1939 | 7 | ~95 KB | 商用车协议栈 + 地址声明 |

**共同点**:

- 都有速查 + 原理 + 实战 + 导航 4 层结构
- 都有 failure-cases (产线死机案例)
- 都有 practical 中的"5 秒定位" / 速查表

**差异**:

- LoRa 重点: 远距 + 频段 + Class + OTAA + NS（LoRa 特色）
- BLE 重点: 协议栈分层 + GATT 模型 + 配对安全 (BLE 特色)
- CAN 重点: 多 master 仲裁 + 错误处理 (CAN 特色)
- USB 重点: 描述符体系 + 类驱动 (USB 特色)
- I2C 重点: 总线恢复 (I2C 特色, 因为有 8 步 SOP)

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| lora.md | 改版才更新 | 主题入口 |
| lora-practical.md | 改版才更新 | 速查 / 调试流程 |
| lora-deep-dive.md | 协议改版 / LoRaWAN 1.1 出 | 原理体系 |
| lora-failure-cases.md | **持续更新** | 产线案例 |
| lora-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题（chips-com 其他目录）

- **`bus/ble.md`** — BLE（短距高吞吐，互补关系）
- **`bus/zigbee.md`** — ZigBee（Mesh 短距，互补关系）
- **`bus/thread.md`** — Thread（IPv6 Mesh，互补关系）
- **`bus/matter.md`** — Matter（智能家居统一层）
- **`basic/wireless-phy.md`** — 物理层对比参考（Sub-GHz vs 2.4 GHz）
- **`bus/modbus-practical.md`** — Modbus（远程低速，竞品）

## 一句话总结

LoRa / LoRaWAN 是"远距低功耗 IoT 的事实标准"，强在距离、电池寿命、星型网络、和免许可频段。从原理到产线案例，5 篇笔记覆盖完整。和 BLE / ZigBee / Thread / Wi-Fi 是**互补**关系（远距低速 vs 短距高速），和 NB-IoT 是**直接竞争**（免许可自建 vs 蜂窝流量费）。

## 更新记录

- 2026-08-01: 初版, 5 篇笔记全部完成 (L4 闭环)
  - 来源：_Inbox/LoRa-2026-07-31-candidates.md 9 条候选 + 实战补充
  - 覆盖：物理层调制 / Class A/B/C / OTAA / ADR / 频段 / NS / 9 案例
