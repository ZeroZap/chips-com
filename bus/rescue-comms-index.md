# Rescue Communications 主题总览

## 目标

救援通讯（Rescue Communications）是 chips-com 知识库的新增主题，围绕"户外 / 海上 / 航空 / 山地紧急救援通讯解决方案"已经形成 5 篇专题笔记。本文档是**总览导航**，帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/rescue-comms-*.md
│
├── 速查层
│   └── rescue-comms-practical.md       调试速查 / 5 秒定位 / 错误码
│
├── 原理层
│   └── rescue-comms-deep-dive.md       卫星链路 / SBD / PLB / 加密深挖
│
├── 实战层
│   └── rescue-comms-failure-cases.md   9 个产线 + 户外实战案例
│
├── 入口
│   └── rescue-comms.md                 主题入口 / 协议族 / 典型产品
│
└── 导航
    └── rescue-comms-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触救援通讯, 想入门" (新人)

按顺序读, 1-2 天能上手:

1. **`rescue-comms.md`** — 主题入口, 5 分钟
2. **`rescue-comms-practical.md`** — 关键参数 / 5 秒定位 / 错误码
3. **`rescue-comms-deep-dive.md`** — 协议栈分层 + 卫星链路

### 路径 B: "我在做救援终端产线失败" (现场救火)

1. **`rescue-comms-practical.md`** "## 5 秒钟定位"
2. **`rescue-comms-failure-cases.md`** — 找类似案例（9 个）
3. **`rescue-comms-deep-dive.md`** "## 错误码速查"

### 路径 C: "我在做卫星模组嵌入式开发" (工程师)

1. **`rescue-comms-deep-dive.md`** "## 卫星 SOS 双向链路深挖"
2. **`rescue-comms-practical.md`** "## 抓包工具"
3. **`rescue-comms-failure-cases.md`** 案例 4（inReach 延迟）

### 路径 D: "我在做海上 / 航空救援" (航海/航空人)

1. **`rescue-comms.md`** "## 实战场景 → 海上 / 航空"
2. **`rescue-comms-deep-dive.md`** "## PLB 406 MHz 协议深挖" + "## 海上 VHF DSC"
3. **`rescue-comms-failure-cases.md`** 案例 7（DSC MMSI 重复）

### 路径 E: "我在做户外登山/应急装备" (户外人)

1. **`rescue-comms.md`** "## 实战场景 → 户外登山"
2. **`rescue-comms-practical.md`** "## PLB 实战注意" + "## Apple Emergency SOS"
3. **`rescue-comms-failure-cases.md`** 案例 1（iPhone 楼内）+ 案例 3（PLB 电池）

### 路径 F: "我在做选型 / 产品规划" (产品经理/架构师)

1. **`rescue-comms.md`** "## 5 大技术路线对比" + "## 典型产品对标"
2. **`rescue-comms-deep-dive.md`** "## 多模融合"
3. **`rescue-comms-failure-cases.md`** 全部案例

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 5 大技术路线 | rescue-comms.md "## 5 大技术路线对比" |
| 典型产品 | rescue-comms.md "## 典型产品对标" |
| Iridium SBD 协议 | rescue-comms-deep-dive.md "## 1.1 Iridium" |
| 北斗 RDSS 协议 | rescue-comms-deep-dive.md "## 1.2 北斗 RDSS" |
| Apple Emergency SOS | rescue-comms-deep-dive.md "## 1.3 Apple Emergency SOS" |
| PLB 406 MHz 协议 | rescue-comms-deep-dive.md "## 3. PLB 406 MHz 协议深挖" |
| VoLTE Emergency | rescue-comms-deep-dive.md "## 4.1 VoLTE Emergency" |
| 卫星 IoT 平台 | rescue-comms-deep-dive.md "## 4.2 卫星 IoT 备份" |
| 海上 VHF DSC | rescue-comms-deep-dive.md "## 5.2 海上 VHF DSC" |
| 业余无线电 | rescue-comms-deep-dive.md "## 5.1 业余无线电 VHF/UHF" |
| 端到端加密 | rescue-comms-deep-dive.md "## 6. 端到端加密" |
| 电池续航设计 | rescue-comms-deep-dive.md "## 7. 电池续航设计" |
| 多模融合架构 | rescue-comms-deep-dive.md "## 8. 多模融合" |
| 抓包工具 | rescue-comms-practical.md "## 抓包 / 抓 log 工具" |
| 5 秒定位 | rescue-comms-practical.md "## 5 秒钟定位" |
| Iridium 错误码 | rescue-comms-practical.md "## 错误码速查（Iridium 9602/9603）" |
| 北斗 RDSS 错误码 | rescue-comms-practical.md "## 错误码速查（北斗 RDSS）" |
| PLB 闪灯编码 | rescue-comms-practical.md "## 错误码速查（PLB 406 MHz）" |
| inReach 实战 | rescue-comms-practical.md "## inReach / Garmin 实战注意" |
| Apple SOS 实战 | rescue-comms-practical.md "## Apple Emergency SOS 实战注意" |
| PLB 实战 | rescue-comms-practical.md "## PLB 实战注意" |
| 北斗短报文实战 | rescue-comms-practical.md "## 北斗短报文实战注意" |
| 户外登山场景 | rescue-comms.md "## 实战场景 → 户外登山" |
| 海上场景 | rescue-comms.md "## 实战场景 → 海上" |
| 航空场景 | rescue-comms.md "## 实战场景 → 航空" |
| 城市应急场景 | rescue-comms.md "## 实战场景 → 城市应急" |
| 产线失败案例 | rescue-comms-failure-cases.md |
| iPhone 楼内 SOS 失败 | rescue-comms-failure-cases.md 案例 1 |
| 华为短报文误发 | rescue-comms-failure-cases.md 案例 2 |
| PLB 电池 3 年失效 | rescue-comms-failure-cases.md 案例 3 |
| inReach 延迟 | rescue-comms-failure-cases.md 案例 4 |
| 北斗入网失败 | rescue-comms-failure-cases.md 案例 5 |
| DJI 4G 备份不工作 | rescue-comms-failure-cases.md 案例 6 |
| DSC MMSI 重复 | rescue-comms-failure-cases.md 案例 7 |
| HAM 中继震中失效 | rescue-comms-failure-cases.md 案例 8 |
| Spot X 低温关机 | rescue-comms-failure-cases.md 案例 9 |

## 关键概念地图

```text
救援通讯（Rescue Communications）
│
├── 5 大技术路线
│   ├── 卫星 SOS 双向
│   │   ├── Apple iPhone 14+ (Globalstar)
│   │   ├── Huawei Mate 60 Pro (北斗 RDSS)
│   │   ├── Garmin inReach (Iridium SBD)
│   │   └── Qualcomm Snapdragon Satellite
│   │
│   ├── 短报文 SBD
│   │   ├── Iridium SBD (9602/9603)
│   │   ├── 北斗短报文 (RDSS)
│   │   └── Inmarsat IsatData Pro
│   │
│   ├── PLB 406 MHz
│   │   ├── COSPAS-SARSAT 系统
│   │   ├── ACR ResQLink
│   │   └── Ocean Signal rescueME
│   │
│   ├── 应急蜂窝
│   │   ├── 4G/5G VoLTE Emergency
│   │   ├── 卫星 IoT 备份 (Astrocast / Swarm / Myriota)
│   │   └── 3GPP NTN (R17+)
│   │
│   └── 户外对讲
│       ├── 业余无线电 VHF/UHF
│       ├── 卫星电话 (Iridium / Thuraya)
│       └── 海上 VHF DSC
│
├── 协议栈
│   ├── 卫星链路 (Iridium / Globalstar / Inmarsat / 北斗)
│   ├── 短报文协议 (SBD / RDSS)
│   ├── PLB 协议 (406 MHz BCH)
│   ├── VoLTE Emergency (3GPP IMS)
│   └── DSC (ITU-R M.493)
│
├── 关键技术
│   ├── 应急链路优先级 / QoS
│   ├── 端到端加密 (AES-256 / SM4)
│   ├── 电池续航 (5-7 年待机 / 24h+ 发射)
│   └── 多模融合 (蜂窝 + 卫星 + 短报文 + PLB)
│
├── 频段
│   ├── L 频段 1.5-1.7 GHz (Iridium / Globalstar / 北斗 / Inmarsat)
│   ├── S 频段 2.4 GHz (Apple Emergency SOS 上行)
│   ├── 406 MHz (PLB / COSPAS-SARSAT)
│   ├── 121.5 MHz (PLB 副载波)
│   ├── 156 MHz (VHF 海上)
│   ├── 144/430 MHz (HAM VHF/UHF)
│   └── 4G/5G (蜂窝应急)
│
└── 实战场景
    ├── 户外登山 (华山 / 珠峰 / K2)
    ├── 海上 (钓鱼船 / 帆船 / 商船)
    ├── 航空 (通用航空 / 滑翔伞)
    └── 城市应急 (地震 / 火灾 / 台风)
```

## 文档关系图

```text
rescue-comms.md (主题入口, 概览)
   ↓ 引用
rescue-comms-practical.md (速查, 调试流程)
   ↓ 引用
rescue-comms-deep-dive.md (原理, 体系)
   ↓ 引用
rescue-comms-failure-cases.md (案例, 实战)
   ↓ 全部引用
rescue-comms-index.md (本文件, 导航)
```

## 学习路径推荐（按角色）

### 嵌入式卫星模组工程师

```text
入口 → 速查 → 原理（Iridium / 北斗）→ 实战案例 4/5
0.5d   0.5d   2d                       1d
```

### 户外 / 应急产品架构师

```text
入口（5 大路线）→ 速查（产品对标）→ 原理（多模融合）→ 实战案例 1/3/6/9
0.5d            0.5d              1d                1d
```

### 海上 / 航空装备工程师

```text
入口（海上/航空场景）→ 原理（PLB / DSC）→ 实战案例 7/8
0.5d                  1d                  1d
```

### 户外救援队员 / 教练

```text
入口 → 速查（PLB / Apple / inReach 实战）→ 实战案例 1/2/3
0.5d   0.5d                              0.5d
```

### 安全 / 应急标准制定者

```text
原理（加密 / 法规）→ 实战案例 8（HAM 失效）→ 入口（场景）
1d                0.5d                       0.5d
```

## 救援通讯主题 vs 其它主题对比

| 主题 | 篇数 | 大小 | 重点 |
| --- | --- | --- | --- |
| BLE | 5 | ~40 KB | 低功耗 + GATT + 配对 + 安全 |
| **Rescue Comms** | **5** | **~70 KB** | **多模链路 + 卫星 + 应急 + 户外** |
| CAN | 8 | 120 KB | 实时多 master + 错误处理 + 演进 |
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

- 救援通讯重点: 多模融合（不是单协议）+ 极端环境（不是常规条件）+ 应急 QoS（不是常规 QoS）
- BLE 重点: 协议栈分层 + GATT 模型
- CAN 重点: 多 master 仲裁 + 错误处理

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| rescue-comms.md | 改版才更新 | 主题入口 |
| rescue-comms-practical.md | 改版才更新 | 速查 / 调试流程 |
| rescue-comms-deep-dive.md | 协议改版 / 新卫星 | 原理体系 |
| rescue-comms-failure-cases.md | **持续更新** | 实战案例 |
| rescue-comms-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题（chips-com 其他目录）

- **`bus/ble-*.md`** — BLE / BLE Mesh（户外手表 / 队友间近距通信）
- **`bus/lorawan-*.md`** — LoRaWAN（户外自建中继）
- **`bus/wifi-*.md`** — Wi-Fi（营地高吞吐）
- **`bus/nb-iot-*.md`** — NB-IoT（蜂窝 IoT 备份）
- **`basic/satellite-comms.md`** — 卫星通讯基础
- **`basic/gnss-positioning.md`** — GPS / 北斗定位原理
- **`basic/emergency-protocols.md`** — 应急协议（行业标准）

## 一句话总结

救援通讯是"人在失联场景下还能把求救信号送出去"的多模融合技术，覆盖卫星 SOS / 短报文 / PLB / 应急蜂窝 / 户外对讲五大路线。强在多链路冗余、极端环境适应、端到端加密、抗误触设计。从原理到产线 + 户外实战案例，5 篇笔记覆盖完整。和 BLE（户外手表）、LoRa（自建中继）、Wi-Fi（营地）、NB-IoT（蜂窝）是**互补**关系。

## 更新记录

- 2026-08-01: 初版, 5 篇笔记全部完成 (L4 闭环)
  - 来源：户外 / 海上 / 航空 / 城市应急四大场景实战
  - 覆盖 Apple Emergency SOS / 华为北斗短报文 / Garmin inReach / Iridium / PLB / DSC / VoLTE Emergency / 业余无线电
  - 9 个实战案例（产线 + 户外）
