# DNP3 主流厂商 / 产品对标

## 定位

DNP3（IEEE 1815）是北美电力 SCADA 标准。本文梳理 DNP3 在出海电力 / 北美电力行业的典型厂商和产品。

> 说明：本文档基于公开资料整理，**具体型号 / 规格请以厂商官网为准**。

## 海外厂商（DNP3 主场）

| 厂商 | 典型产品 | DNP3 能力 |
| --- | --- | --- |
| **ABB** | RTU 540 / RTU 560 | ✅ 完整：SA v5/v6、Class 报告、文件操作 |
| **Siemens** | SICAM RTU / SIPROTEC 5 | ✅ 完整：SA v5 |
| **Schweitzer (SEL)** | SEL-2240 / SEL-2440 | ✅ 完整：SA v5、Class 报告、文件操作 |
| **GE / Hitachi Energy** | RTU 100/200/300 | ✅ 完整：SA v5 |
| **Schneider** | PowerLogic | ✅ 完整 |
| **Rockwell Automation** | Allen-Bradley RTU | ✅ 完整 |
| **Eaton** | Cooper RTU | ✅ 完整 |
| **Moxa** | UC-5100 / RTU 模块 | ✅ 完整：TCP / Serial |

## 国内厂商（DNP3 出海）

| 厂商 | 典型产品 | DNP3 能力 |
| --- | --- | --- |
| **南瑞继保** | PCS-9000 / RCS-9000 | ⚠️ 部分（需特别配置） |
| **北京四方** | CFR-2000 | ⚠️ 部分 |
| **南京南自** | NAS 系列 | ⚠️ 部分 |
| **积成电子** | iES 系列 | ⚠️ 部分 |
| **长园深瑞** | PRS 系列 | ⚠️ 部分 |

国内厂商 DNP3 较弱，主要客户为北美出海项目。

## 关键能力矩阵

| 能力 | ABB | Siemens | SEL | GE | Moxa |
| --- | --- | --- | --- | --- | --- |
| DNP3 TCP | ✅ | ✅ | ✅ | ✅ | ✅ |
| DNP3 Serial | ✅ | ✅ | ✅ | ✅ | ✅ |
| 三层架构（链路 / 传输 / 应用） | ✅ | ✅ | ✅ | ✅ | ✅ |
| CRC16 (0xA6BC) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Class 0 完整性轮询 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Class 1/2/3 事件报告 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 未确认报告（Unsolicited） | ✅ | ✅ | ✅ | ✅ | ✅ |
| 对象 g1v1/v2 / g4v1/v2 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 命令 Select+Operate | ✅ | ✅ | ✅ | ✅ | ✅ |
| Direct Operate | ✅ | ✅ | ✅ | ✅ | ✅ |
| 文件操作 | ✅ | ✅ | ✅ | ✅ | ✅ |
| SA v5 | ✅ | ✅ | ✅ | ✅ | ✅ |
| SA v6 | ✅ | ⚠️ 部分 | ✅ | ⚠️ 部分 | ⚠️ 部分 |
| 多主站 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 一致性测试 | DNV | DNV | DNV | DNV | DNV |

## SA v5 / v6 加密

| 厂商 | SA v5 | SA v6 |
| --- | --- | --- |
| ABB | ✅ | ✅ |
| Siemens | ✅ | ⚠️ 部分 |
| SEL | ✅ | ✅ |
| GE | ✅ | ⚠️ 部分 |
| Moxa | ✅ | ✅ |

北美关键基础设施（北美电力 / 油气）强制要求 SA。

## 与 IEC 104 / IEC 61850 双栈

| 厂商 | DNP3 | IEC 104 | IEC 61850 |
| --- | --- | --- | --- |
| ABB | ✅ | ✅ | ✅ |
| Siemens | ✅ | ✅ | ✅ |
| SEL | ✅ | ⚠️ 部分 | ✅ |
| GE | ✅ | ✅ | ✅ |
| 南瑞 | ⚠️ 部分 | ✅ | ✅ |
| 四方 | ⚠️ 部分 | ✅ | ✅ |

## 选型决策

```text
DNP3 应用场景
├── 北美电力 SCADA
│   └── SEL / ABB / Siemens / GE
├── 出海电力项目
│   └── SEL / ABB + IEC 61850 高端
├── 北美关键基础设施（油气）
│   └── SEL + SA v5/v6（强制）
├── 工业控制（北美）
│   └── SEL / Rockwell / Schneider
└── 国内项目
    └── IEC 104 / IEC 61850 (DNP3 不适用)
```

## 选型要点

```text
1. SA v5 是否强制（北美关键基础设施）
2. SA v6 是否支持（最新版本）
3. 多主站支持（部分厂商限制）
4. 文件操作支持（高端项目）
5. 一致性测试报告（DNV / TUV）
6. TCP / Serial 双支持
```

## 延伸阅读

- `bus/dnp3.md`：DNP3 协议
- `bus/iec61850-vendor-bench.md`：IEC 61850 对标