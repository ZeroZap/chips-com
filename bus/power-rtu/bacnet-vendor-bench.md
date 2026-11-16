---
tags:
  - layer/bus
  - type/vendor-bench
  - protocol/bacnet
  - topic/power-rtu
---

# BACnet 主流厂商 / 产品对标

## 定位

BACnet 是楼宇自动化国际标准。本文梳理 BACnet 在楼宇 / 暖通空调 / 智能建筑行业的典型厂商和产品。

> 说明：本文档基于公开资料整理，**具体型号 / 规格请以厂商官网为准**。

## 海外厂商（BACnet 主场）

| 厂商 | 典型产品 | BACnet 能力 |
| --- | --- | --- |
| **Honeywell** | Niagara / Spyder / TDC | ✅ BACnet/IP、MS/TP、COV、BACnet/SC |
| **Johnson Controls** | Metasys / Facility Explorer | ✅ BACnet/IP、MS/TP、COV、BACnet/SC |
| **Siemens** | Desigo CC / APOGEE | ✅ BACnet/IP、MS/TP、COV |
| **Schneider** | EcoStruxure / StruxureWare | ✅ BACnet/IP、MS/TP、COV |
| **Delta** | ORCAview / BMS | ✅ BACnet/IP、MS/TP |
| **Trane** | Tracer / Ensemble | ✅ BACnet/IP、MS/TP |
| **Carrier** | i-Vu | ✅ BACnet/IP |
| **Automated Logic** | WebCTRL | ✅ BACnet/IP |
| **Distech** | EC-Net | ✅ BACnet/IP、MS/TP |

## 国内厂商

| 厂商 | 典型产品 | BACnet 能力 |
| --- | --- | --- |
| **海林节能** | HBS / HL-BMS | ✅ BACnet/IP、MS/TP |
| **同方泰德** | Techcon | ✅ BACnet/IP |
| **江森自控（合资）** | Metasys | ✅ BACnet/IP、MS/TP |
| **施耐德电气（合资）** | EcoStruxure | ✅ BACnet/IP、MS/TP |
| **杭州源牌** | 中央空调群控 | ⚠️ Modbus |
| **深圳达实** | 中央空调群控 | ⚠️ Modbus |

国内厂商对 BACnet 支持较少，主要靠合资厂商支撑楼宇市场。

## 关键能力矩阵

| 能力 | Honeywell | JCI | Siemens | Schneider | Delta |
| --- | --- | --- | --- | --- | --- |
| BACnet/IP | ✅ | ✅ | ✅ | ✅ | ✅ |
| BACnet MS/TP | ✅ | ✅ | ✅ | ✅ | ✅ |
| BACnet Ethernet | ⚠️ 部分 | ⚠️部分 | ✅ | ⚠️部分 | ⚠️部分 |
| Object 标准支持 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Device Object | ✅ | ✅ | ✅ | ✅ | ✅ |
| AI/AO/BI/BO/AV/BV | ✅ | ✅ | ✅ | ✅ | ✅ |
| Schedule | ✅ | ✅ | ✅ | ✅ | ✅ |
| Trend Log | ✅ | ✅ | ✅ | ✅ | ✅ |
| Calendar | ✅ | ✅ | ✅ | ✅ | ✅ |
| Loop | ✅ | ✅ | ✅ | ✅ | ✅ |
| Notification Class | ✅ | ✅ | ✅ | ✅ | ✅ |
| ReadProperty / ReadPropertyMultiple | ✅ | ✅ | ✅ | ✅ | ✅ |
| SubscribeCOV | ✅ | ✅ | ✅ | ✅ | ✅ |
| Confirmed COV | ✅ | ✅ | ✅ | ✅ | ✅ |
| BBMD | ✅ | ✅ | ✅ | ✅ | ✅ |
| Foreign Device | ✅ | ✅ | ✅ | ✅ | ✅ |
| BACnet/SC (TLS) | ✅ | ✅ | ⚠️ 部分 | ⚠️ 部分 | ✅ |
| 一致性测试 | BTL | BTL | BTL | BTL | BTL |

## BACnet Testing Laboratories (BTL)

```text
BACnet 一致性认证：
- BTL Listing（认证机构 BACnet Testing Laboratories）
- 测试 BACnet/IP / MS/TP 标准符合
- 标志：DDC 设备是否通过认证

主流厂商均通过 BTL：
- Honeywell / JCI / Siemens / Schneider / Delta / Trane / Carrier

国内厂商：
- 海林节能：通过 BTL
- 同方泰德：通过 BTL
```

## 选型决策

```text
BACnet 应用场景
├── 大型楼宇（写字楼 / 商场）
│   ├── 综合 BMS
│   │   └── Honeywell / JCI / Siemens / Schneider
│   ├── 数据中心
│   │   └── Schneider / Vertiv / Delta
│   └── 医院 / 学校
│           └── Honeywell / JCI / Delta
├── 中小型楼宇
│   └── Honeywell / Delta / Distech
├── 工业 HVAC
│   └── Trane / Carrier
├── 智慧城市
│   └── Honeywell / Siemens / Schneider（云集成）
└── 国内项目
        └── 海林 / 同方泰德 / 江森自控（合资）
```

## 选型要点

```text
1. BTL 一致性认证（项目要求）
3. BACnet/IP + MS/TP 双支持
5. BBMD 跨子网支持
7. BACnet/SC TLS 加密（关键基础设施）
9. Companion Specifications 支持
```

## 行业大厂关键产品

```text
Honeywell Niagara：
- Niagara Framework
- 楼宇一体化平台

JCI Metasys：
- 综合 BMS
- 业界市占率第一

Siemens Desigo CC：
- 综合楼宇平台
- 与 Desigo 控制器集成

Schneider EcoStruxure：
- 物联网平台
- 楼宇 + 能源 + 数据中心
```

## 延伸阅读

- `bus/power-rtu/bacnet.md`：BACnet 协议
- `bus/industrial/opcua-vendor-bench.md`：OPC UA 对标（楼宇 + 工业 4.0 集成）