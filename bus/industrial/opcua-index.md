---
tags:
  - layer/bus
  - type/index
  - protocol/opcua
  - topic/industrial
---

# OPC UA 主题总览

## 目标

OPC UA 是工业 4.0 / 数字孪生 / MES 集成的国际标准。本文是**总览导航**，围绕 OPC UA 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/opcua-*.md
│
├── 速查层
│   ├── opcua.md                1 页概念：地址空间、服务、安全
│   └── opcua-practical.md      报文示例 + 调试步骤
│
├── 原理层
│   └── opcua-deep-dive.md      NodeId 编码、订阅、安全、Companion
│
└── 实战层
    └── opcua-failure-cases.md  20 个产线死机案例
```

## 5 种读者路径

```text
1. opcua.md            概念 + 地址空间 + 服务
2. opcua-practical.md  GetEndpoints / Read / Subscribe
3. opcua-deep-dive.md  NodeId 编码 + 订阅 + 安全
4. opcua-failure-cases.md 20 案例
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| OPC UA 是啥 | [[bus/industrial/opcua\|opcua]] §定位 |
| 信息建模 | [[bus/industrial/opcua\|opcua]] §信息建模 |
| 节点类型 | [[bus/industrial/opcua\|opcua]] §信息建模 |
| 服务 | [[bus/industrial/opcua\|opcua]] §服务 |
| 安全策略 | [[bus/industrial/opcua\|opcua]] §安全 |
| 编码 | [[bus/industrial/opcua-deep-dive\|opcua-deep-dive]] §编码 |
| NodeId 编码 | [[bus/industrial/opcua-deep-dive\|opcua-deep-dive]] §节点 ID（NodeId） |
| 地址空间浏览 | [[bus/industrial/opcua-deep-dive\|opcua-deep-dive]] §地址空间建模 |
| 订阅 / 通知 | [[bus/industrial/opcua-deep-dive\|opcua-deep-dive]] §订阅 / 通知 |
| 历史访问 | [[bus/industrial/opcua-deep-dive\|opcua-deep-dive]] §历史访问 |
| 证书管理 | [[bus/industrial/opcua-deep-dive\|opcua-deep-dive]] §安全机制 |
| Companion Specifications | [[bus/industrial/opcua-deep-dive\|opcua-deep-dive]] §Companion Specifications |
| 16 个常见故障 | [[bus/industrial/opcua-deep-dive\|opcua-deep-dive]] §现场常见故障 |
| 20 个产线死机案例 | [[bus/industrial/opcua-failure-cases\|opcua-failure-cases]] |

## OPC UA vs BACnet vs MQTT

| 维度 | OPC UA | BACnet | MQTT |
| --- | --- | --- | --- |
| 应用 | 工业 4.0 | 楼宇 | IoT |
| 物理 | TCP / HTTPS | UDP / RS485 | TCP |
| 数据模型 | 地址空间 | 对象 | Topic |
| 信息建模 | 行业 Companion | LN | 无 |
| 安全 | Sign + Encrypt | BACnet/SC | TLS |
| 工业级 | 高 | 中 | 中 |

## 选型决策树

```text
工业 IoT / 数字孪生
├── 工厂 MES / ERP 集成
│   └── OPC UA（首选）
├── 跨厂区数据汇聚
│   └── OPC UA / MQTT
├── 楼宇 HVAC
│   └── BACnet
└── 云平台轻量对接
    └── MQTT
```

## 实战检查清单

```text
- TCP 端口 4840 已开
- HTTPS 端口 443 已开（如使用 HTTPS）
- 安全策略协商
- 会话创建
- 用户认证
- 地址空间浏览
- Read / Write 支持
- Call 方法调用支持
- CreateSubscription 支持
- MonitoredItems 支持
- Publish 通知支持
- HistoryRead 历史访问支持
- 消息安全（Sign / SignAndEncrypt）
- 客户端证书 / 服务器证书
- Companion Specifications 实现
- 信息建模（行业标准）
- 重连机制
```

## 延伸阅读

- [[bus/power-rtu/rtu-protocols|rtu-protocols]]：RTU 设备协议全集
- [[bus/power-rtu/bacnet|bacnet]]：与 BACnet 对比
- [[bus/industrial/mqtt|mqtt]]：与 MQTT 对比
- [[bus/industrial/opcua-failure-cases|opcua-failure-cases]]：20 个产线死机案例库

## 版本演进

```text
OPC UA 1.0: 2008
OPC UA 1.04: 当前主流
IEC 62541: 国际标准
```