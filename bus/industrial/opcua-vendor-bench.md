---
tags:
  - layer/bus
  - type/vendor-bench
  - protocol/opcua
  - topic/industrial
---

# OPC UA 主流厂商 / 产品对标

## 定位

OPC UA（IEC 62541）是工业 4.0 / 数字孪生 / MES 集成的国际标准。本文梳理 OPC UA 在 PLC / 工控 / 数字孪生行业的典型厂商和产品。

> 说明：本文档基于公开资料整理，**具体型号 / 规格请以厂商官网为准**。

## 海外厂商（OPC UA 主场）

| 厂商 | 典型产品 | OPC UA 能力 |
| --- | --- | --- |
| **Siemens** | SIMATIC S7-1500 / ET 200 / MindSphere | ✅ Server + Client、Companion Specs |
| **Beckhoff** | TwinCAT / CX 系列 | ✅ Server + Client |
| **Schneider** | M580 / EcoStruxure | ✅ Server |
| **ABB** | AC500 / Ability | ✅ Server |
| **Rockwell** | ControlLogix / FactoryTalk | ✅ Server + Client |
| **B&R** | X20 系列 / Automation Studio | ✅ Server |
| **Bosch Rexroth** | IndraLogic / ctrlX | ✅ Server |

## 国内厂商

| 厂商 | 典型产品 | OPC UA 能力 |
| --- | --- | --- |
| **和利时** | LK 系列 PLC / DCS | ✅ Server |
| **浙大中控** | DCS / XP 系列 | ✅ Server |
| **南大傲拓** | NA-PLC | ⚠️ 部分 |
| **汇川技术** | H5U / AM 系列 | ⚠️ 部分 |
| **信捷电气** | XG 系列 | ⚠️ 部分 |
| **英威腾** | AX 系列 | ⚠️ 部分 |

国内 PLC 厂商 OPC UA 支持较弱，主要靠 SIEMENS / ABB / Schneider 支撑工厂市场。

## 关键能力矩阵

| 厂商 | OPC UA Server | OPC UA Client | 安全策略 | Companion Specs |
| --- | --- | --- | --- | --- |
| Siemens | ✅ | ✅ | Basic256Sha256 + SignAndEncrypt | ✅ 完整 |
| Beckhoff | ✅ | ✅ | Basic256Sha256 | ✅ |
| Schneider | ✅ | ⚠️ 部分 | Basic256Sha256 | ⚠️ 部分 |
| ABB | ✅ | ⚠️ 部分 | Basic256Sha256 | ⚠️ 部分 |
| Rockwell | ✅ | ✅ | Basic256Sha256 | ⚠️ 部分 |
| 和利时 | ✅ | ⚠️ 部分 | Basic256 | ⚠️ 部分 |
| 浙大中控 | ✅ | ⚠️ 部分 | Basic256 | ⚠️ 部分 |
| 汇川 | ⚠️部分 | ⚠️部分 | ⚠️ 部分 | ⚠️ 部分 |

## Companion Specifications（行业信息模型）

```text
OPC UA 联盟定义的行业 Companion Specifications：
- Machinery（机械）
- Robotics（机器人）
- Plastics EUROMAP 77/82（塑料机械）
- Machine Tools（机床）
- Process Automation（过程自动化）
- ISA-95（制造业）
- BACnet（楼宇集成）
- ADI（分析仪器）
- Field Level Communications
- IIoT
- OpenSCS（安全）

主流厂商支持：
- Siemens：完整支持多个 Companion
- Beckhoff：完整支持
- Schneider：部分支持
- Rockwell：部分支持
- 和利时 / 浙大中控：部分支持
```

## 选型决策

```text
OPC UA 应用场景
├── 工厂数字化
│   ├── 高端 (Industry 4.0)
│   │   └── Siemens / Beckhoff / ABB
│   ├── 国产 MES 集成
│   │   └── 和利时 / 浙大中控
│   ├── 数字孪生
│   │   └── Siemens MindSphere
│   │   └── Beckhoff + TwinCAT Analytics
│   └── MES / ERP 集成
│           └── Siemens / Schneider / Rockwell
├── 工业云平台
│   ├── AWS IoT
│   ├── Azure IoT
│   ├── Siemens MindSphere
│   └── Schneider EcoStruxure
├── 工业 4.0 标杆工厂
│   └── Siemens / Beckhoff + Companion Specs
└── 中小型工业 IoT
    └── Beckhoff / Schneider
```

## 选型要点

```text
1. OPC UA Server + Client 双支持
3. 安全策略（Basic256Sha256 推荐）
5. Companion Specifications 行业支持
7. 信息建模工具
9. 一致性测试（OPC Foundation 认证）
11. 数字证书管理
```

## OPC Foundation 认证

```text
OPC UA 一致性认证：
- OPC Foundation 测试
- Server / Client 标识
- 通信栈测试
- 信息建模测试
- 安全策略测试

主流厂商均通过认证：
- Siemens / Beckhoff / Schneider / ABB / Rockwell
- 和利时 / 浙大中控：部分通过
```

## 行业大厂关键产品

```text
Siemens MindSphere：
- 工业云平台
- OPC UA 作为数据传输标准

Beckhoff TwinCAT：
- PC 控制 + OPC UA
- 信息建模工具

Schneider EcoStruxure：
- 物联网平台
- OPC UA 集成
```

## 延伸阅读

- [[bus/industrial/opcua|opcua]]：OPC UA 协议
- [[bus/power-rtu/bacnet-vendor-bench|bacnet-vendor-bench]]：BACnet 对标（楼宇 + 工业 4.0）
- [[bus/industrial/modbus-rtu-mqtt-gateway|modbus-rtu-mqtt-gateway]]：Modbus ↔ MQTT 网关