# IEC 61850 主流厂商 / 产品对标

## 定位

IEC 61850 是变电站自动化国际标准。本文梳理 IEC 61850 在电力保护 / 智能变电站行业的典型厂商和产品。

> 说明：本文档基于公开资料整理，**具体型号 / 规格请以厂商官网为准**。

## 海外厂商（IEC 61850 主场）

| 厂商 | 典型产品 | IEC 61850 能力 |
| --- | --- | --- |
| **ABB** | REL 670 / REF 615 / RTU 540 | ✅ MMS + GOOSE + SV、一致性测试 |
| **Siemens** | SIPROTEC 5 / 7SA86 / SICAM RTU | ✅ MMS + GOOSE + SV、SCL |
| **Schweitzer (SEL)** | SEL-487B / SEL-451 | ✅ MMS + GOOSE + SV、SCL |
| **GE / Hitachi** | UR / B30 / T60 | ✅ MMS + GOOSE + SV |
| **Schneider** | MiCOM P5 / P7 | ✅ MMS + GOOSE |
| **Toshiba** | GR-200 | ✅ MMS + GOOSE + SV |

## 国内厂商

| 厂商 | 典型产品 | IEC 61850 能力 |
| --- | --- | --- |
| **南瑞继保** | PCS-9000 / RCS-9000 | ✅ MMS + GOOSE + SV、SCL |
| **北京四方** | CFR-2000 / CSC-300 | ✅ MMS + GOOSE + SV |
| **长园深瑞** | PRS-3000 / 7000 | ✅ MMS + GOOSE |
| **国电南自** | PSL600 / 690 | ✅ MMS + GOOSE |
| **积成电子** | iES-G200 | ✅ MMS |
| **许继电气** | WXH-801 系列 | ✅ MMS + GOOSE |

## 关键能力矩阵

| 能力 | ABB | Siemens | SEL | 南瑞 | 四方 |
| --- | --- | --- | --- | --- | --- |
| MMS Client/Server | ✅ | ✅ | ✅ | ✅ | ✅ |
| GOOSE Publisher/Subscriber | ✅ | ✅ | ✅ | ✅ | ✅ |
| SV Publisher/Subscriber | ✅ | ✅ | ✅ | ✅ | ✅ |
| SCL (ICD/SSD/IID/CID/SCD) | ✅ | ✅ | ✅ | ✅ | ✅ |
| IEEE 1588 时间同步 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 一致性测试（DNV KEMA） | ✅ | ✅ | ✅ | ⚠️ 部分 | ⚠️ 部分 |
| IEC 61850 Edition 2 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 网络安全（PRP/HSR） | ✅ | ✅ | ✅ | ✅ | ✅ |
| 数据集（DataSet） | ✅ | ✅ | ✅ | ✅ | ✅ |
| BRCB/URCB | ✅ | ✅ | ✅ | ✅ | ✅ |
| 命令 SBO / Direct / Enhanced | ✅ | ✅ | ✅ | ✅ | ✅ |
| 文件传输 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 通用分类（GI） | ✅ | ✅ | ✅ | ✅ | ✅ |

## 一致性测试

| 厂商 | 测试机构 | 测试级别 |
| --- | --- | --- |
| ABB | DNV KEMA | A / B / C |
| Siemens | DNV KEMA | A / B / C |
| SEL | DNV KEMA | A / B / C |
| GE | DNV KEMA | A / B / C |
| 南瑞继保 | 中国电科院 | 国内 |
| 北京四方 | 中国电科院 | 国内 |

国际项目要求 KEMA 一致性测试报告。

## 数字化变电站产品架构

```text
站控层（IEC 61850 MMS）：
  - 后台监控
  - 远动机（IEC 104 上行）

间隔层（IEC 61850 MMS + GOOSE）：
  - 保护装置
  - 测控装置
  - 智能终端
  - 合并单元（MU）

过程层（IEC 61850 SV + GOOSE）：
  - 互感器（ECT / EVT）
  - 一次设备（断路器 / 隔离开关）
```

## 选型决策

```text
IEC 61850 应用场景
├── 数字化变电站
│   ├── 国内智能变电站
│   │   └── 南瑞 / 四方 / ABB / Siemens
│   ├── 海外变电站
│   │   └── ABB / Siemens / SEL
│   └── 高端变电站
│           └── ABB / Siemens + Edition 2
├── 配电站自动化
│   └── 长园深瑞 / 国电南自
├── 新能源场站
│   └── ABB / Siemens / 南瑞
└── 工厂自动化（高端）
    └── Siemens / ABB / Beckhoff
```

## 选型要点

```text
1. 一致性测试（DNV KEMA 报告）
3. SCL 工具链（厂家提供）
5. 网络安全（PRP/HSR / VLAN / 加密）
7. GOOSE 延迟 < 4 ms
9. Edition 版本（Edition 2 推荐）
```

## 延伸阅读

- `bus/power-rtu/iec61850.md`：IEC 61850 协议
- `bus/power-rtu/iec104-vendor-bench.md`：IEC 104 对标
- `bus/power-rtu/dnp3-vendor-bench.md`：DNP3 对标