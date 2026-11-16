---
tags:
  - layer/bus
  - type/index
  - protocol/slt427
  - topic/power-rtu
---

# SL/T 427 主题总览

## 目标

SL/T 427 是水资源监测补充规约。本文是**总览导航**，围绕 SL/T 427 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/slt427-*.md
│
├── 速查层
│   ├── slt427.md                1 页概念：水质扩展、多中心站
│   └── slt427-practical.md      报文示例 + 调试步骤
│
├── 原理层
│   └── slt427-deep-dive.md      水质 / 灌区 / 加密 / 多中心站
│
└── 实战层
    └── slt427-failure-cases.md  20 个产线死机案例
```

## 5 种读者路径

```text
1. slt427.md            概念 + 与 SZY 206 区别
2. slt427-practical.md  水质数据上报
3. slt427-deep-dive.md  水质 / 灌区 / 加密 / 多中心站
4. slt427-failure-cases.md 20 案例
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| SL/T 427 是啥 | slt427.md §定位 |
| 与 SZY 206 关系 | slt427.md §与 SZY 206 关系 |
| 水质要素 | slt427.md §要素编码扩展 |
| 灌区要素 | slt427.md §要素编码扩展 |
| 历史数据回传 | slt427-deep-dive.md §历史数据回传（FC=0x35） |
| 多中心站切换 | slt427-deep-dive.md §多中心站切换 |
| 加密信道 | slt427-deep-dive.md §加密信道 |
| 设备状态 | slt427-deep-dive.md §设备状态扩展 |
| GSM 短信备份 | slt427-deep-dive.md §GSM 短信备份 |
| 16 个常见故障 | slt427-deep-dive.md §现场常见故障 |
| 20 个产线死机案例 | slt427-failure-cases.md |

## SL/T 427 vs SZY 206

| 维度 | SL/T 427 | SZY 206 |
| --- | --- | --- |
| 应用 | 水资源扩展 | 基础水资源 |
| 重点 | 水质 + 灌区 | 取水流量 |
| 编码 | 扩展要素 | 基础要素 |
| 中心站 | 多中心站 | 单 / 双中心站 |
| 加密 | 部分省份强制 | 可选 |
| 历史数据 | 完整回传 | 简单 |

## 选型决策树

```text
水资源 RTU 立项
├── 水质监测数据传输
│   └── SL/T 427（首选）
├── 灌区用水监测
│   └── SL/T 427
├── 取水口流量
│   └── SZY 206
├── 多中心站 / 加密要求
│   └── SL/T 427
└── 基础水资源
    └── SZY 206
```

## 实战检查清单

```text
- TCP 端口与省级一致
- 测站地址 / 中心站地址 BCD 编码正确
- 链路建立 F2 流程跑通
- 链路维持 F1 心跳正常
- 自报周期符合省级要求
- 水质数据上报正常
- 灌区数据上报正常（如需要）
- 历史数据回传支持
- 多中心站切换支持
- 加密信道（如省级要求）
- CRC 计算正确
- 要素编码正确
- BCD 编码正确
- VPN / 专网配置
```

## 延伸阅读

- `bus/power-rtu/rtu-protocols.md`：RTU 设备协议全集
- `bus/power-rtu/szy206.md`：SZY 206（配套）
- `bus/power-rtu/sl651.md`：SL 651（水文）
- `bus/power-rtu/slt427-failure-cases.md`：20 个产线死机案例库

## 版本演进

```text
SL/T 427-2014：当前主流
省份扩展：广东、湖南、河南等
```