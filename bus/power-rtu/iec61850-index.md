---
tags:
  - layer/bus
  - type/index
  - protocol/iec61850
  - topic/power-rtu
---

# IEC 61850 主题总览

## 目标

IEC 61850 是变电站自动化国际标准。本文是**总览导航**，围绕 IEC 61850 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/iec61850-*.md
│
├── 速查层
│   ├── iec61850.md                1 页概念：MMS、GOOSE、SV、SCL
│   └── iec61850-practical.md      报文示例 + 调试步骤
│
├── 原理层
│   └── iec61850-deep-dive.md      MMS BER、LN/DO/DA、SCL、一致性
│
└── 实战层
    └── iec61850-failure-cases.md  20 个产线死机案例
```

## 5 种读者路径

### 路径 1：刚接触 IEC 61850

```text
1. iec61850.md            概念 + 通信模型 + 建模
2. iec61850-practical.md  MMS 接入 + 服务示例
3. iec61850-failure-cases.md 第 1-5 案例  MMS / SCL
```

### 路径 2：要做 RTU 接入 IED

```text
1. iec61850.md            协议定位
2. iec61850-practical.md  MMS Initiate + Read + Write
3. iec61850-deep-dive.md  BER 编码 + LN/DO/DA + BRCB/URCB
4. iec61850-failure-cases.md 第 6-15 案例  GOOSE / SV / 命令
```

### 路径 3：要做 GOOSE / SV 集成

```text
1. iec61850-deep-dive.md  GOOSE/SV 详解
2. iec61850-practical.md  GOOSE/SV 调试
3. iec61850-failure-cases.md GOOSE/SV 案例
```

### 路径 4：要做 IEC 61850 一致性测试

```text
1. iec61850-deep-dive.md  一致性测试
2. iec61850-practical.md  测试工具
3. iec61850-failure-cases.md 测试用例
```

### 路径 5：要做 IEC 61850 IED 端

```text
1. iec61850-deep-dive.md  SCL 解析 + Server 实现
2. iec61850-practical.md  IED 实现步骤
3. iec61850-failure-cases.md IED 实现案例
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| IEC 61850 是啥 | iec61850.md §定位 |
| 通信模型 | iec61850.md §通信模型 |
| MMS | iec61850.md §MMS（Client/Server） |
| GOOSE | iec61850.md §GOOSE |
| SV | iec61850.md §SV |
| 建模 | iec61850.md §建模层次 |
| LN 类 | iec61850.md §逻辑节点（LN）类 |
| ACSI 服务 | iec61850-deep-dive.md §ACSI 服务 |
| BRCB / URCB | iec61850-deep-dive.md §报告控制块（BRCB / URCB） |
| 命令模型 | iec61850-deep-dive.md §命令模型 |
| MMS BER | iec61850-deep-dive.md §MMS PDU 编码 |
| SCL XML | iec61850-deep-dive.md §SCL XML 详解 |
| 一致性测试 | iec61850-deep-dive.md §一致性测试 |
| 16 个常见故障 | iec61850-deep-dive.md §现场常见故障 |
| 20 个产线死机案例 | iec61850-failure-cases.md |

## IEC 61850 vs IEC 104 vs DNP3

| 维度 | IEC 61850 | IEC 104 | DNP3 |
| --- | --- | --- | --- |
| 标准 | IEC 61850 | IEC 60870-5-104 | IEEE 1815 |
| 物理 | Ethernet | TCP | TCP / 串行 |
| 应用场景 | 站内 IED 互联 | 站控上行 | SCADA |
| 实时性 | 高（GOOSE） | 中 | 中 |
| 复杂度 | 高 | 中 | 中 |
| 国内 | 高端 | 主流 | 出海 |

## 选型决策树

```text
变电站自动化
├── 站内 IED 互联
│   └── IEC 61850（首选）
│       ├── 保护跳闸：GOOSE
│       └── 采样值：SV
├── 站控上行
│   └── IEC 104（首选）
├── 高端 / 综合自动化
│   └── IEC 61850 + IEC 104（双栈）
└── 海外 / 北美
    └── DNP3
```

## 实战检查清单

```text
- TCP 端口 102 已开
- MMS Initiate 服务已实现
- GetNameList / Read / Write 支持
- InformationReport 订阅支持
- 命令 Select / Operate 流程完整
- 报告控制块 BRCB / URCB 配置
- 数据集 DataSet 定义
- 触发选项支持
- GOOSE 多播接收（如保护 IED）
- SV 多播订阅（如合并单元）
- SCL 文件解析（ICD / CID / SCD）
- 时间同步（IEEE 1588）
- 一致性测试（A / B / C 级）
```

## 延伸阅读

- `bus/power-rtu/rtu-protocols.md`：RTU 设备协议全集
- `bus/power-rtu/iec104.md`：与 IEC 104 对比（站控上行）
- `bus/power-rtu/dnp3.md`：与 DNP3 对比（北美）
- `bus/power-rtu/iec61850-failure-cases.md`：20 个产线死机案例库

## 版本演进

```text
IEC 61850-1: 总览
IEC 61850-2: 术语
IEC 61850-3: 一般要求
IEC 61850-4: 系统项目管理
IEC 61850-5: 通信要求
IEC 61850-6: SCL 配置语言
IEC 61850-7: ACSI
IEC 61850-8: MMS 映射
IEC 61850-9: SV 采样值
IEC 61850-10: 一致性测试
Edition 1: 2003-2005
Edition 2: 2009-2014
Edition 3: 2020+
```