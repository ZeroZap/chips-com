# HJ 212 主题总览

## 目标

HJ 212-2017 是环保联网规约。本文是**总览导航**，围绕 HJ 212 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/hj212-*.md
│
├── 速查层
│   ├── hj212.md                1 页概念：帧格式、QN、CN、MN 字段
│   └── hj212-practical.md      报文示例 + 调试步骤
│
├── 原理层
│   └── hj212-deep-dive.md      Header / Data 段解析、因子字典、省级差异
│
└── 实战层
    └── hj212-failure-cases.md  20 个产线死机案例
```

## 5 种读者路径

### 路径 1：刚接触 HJ 212

```text
1. hj212.md            概念 + 帧格式 + 因子字典
2. hj212-practical.md  报文示例 + 调试步骤
3. hj212-failure-cases.md 第 1-5 案例  端口 / MN / PW
```

### 路径 2：要做 RTU 接入环保平台

```text
1. hj212.md            协议定位
2. hj212-practical.md  TCP 接入 + 心跳 + 数据上报
3. hj212-deep-dive.md  Header / Data 段 + 因子字典
4. hj212-failure-cases.md 第 6-15 案例  数据格式 / 命令
```

### 路径 3：要做对接省级多平台

```text
1. hj212-deep-dive.md  省级平台差异
2. hj212-practical.md  调试步骤
3. hj212-failure-cases.md 第 16-20 案例  省级对接
```

### 路径 4：要做 HJ 212 因子字典扩展

```text
1. hj212-deep-dive.md  因子字典
2. hj212-practical.md  报文示例
3. hj212-failure-cases.md 第 11-15 案例  因子字典
```

### 路径 5：要做 HJ 212 中心站模拟

```text
1. hj212-deep-dive.md  完整 Header / Data 段
2. hj212-practical.md  心跳 / 数据 / 命令
3. hj212-failure-cases.md 所有 20 案例
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| HJ 212 是啥 | hj212.md §定位 |
| 应用领域 | hj212.md §应用领域 |
| Header 字段 | hj212-deep-dive.md §Header 字段详解 |
| Data 段 | hj212-deep-dive.md §Data 段详解 |
| QN 请求编号 | hj212-deep-dive.md §QN（请求编号） |
| CN 命令码 | hj212-deep-dive.md §CN（命令编号） |
| ST 系统编号 | hj212-deep-dive.md §ST（系统编号） |
| MN 设备编号 | hj212-deep-dive.md §MN（设备唯一编号） |
| 因子字典 | hj212-deep-dive.md §因子字典 |
| 心跳策略 | hj212-deep-dive.md §心跳 |
| CRC 校验 | hj212-deep-dive.md §CRC 校验 |
| 省级平台差异 | hj212-deep-dive.md §省级平台差异 |
| 主站实现要点 | hj212-deep-dive.md §主站实现要点 |
| 中心站实现要点 | hj212-deep-dive.md §中心站实现要点 |
| 16 个常见故障 | hj212-deep-dive.md §现场常见故障 |
| 20 个产线死机案例 | hj212-failure-cases.md |

## HJ 212 vs SL 651 vs IEC 104

| 维度 | HJ 212 | SL 651 | IEC 104 |
| --- | --- | --- | --- |
| 应用 | 环保 | 水文 | 电力 |
| 字符集 | ASCII | 二进制 + BCD | 二进制 |
| 协议格式 | 文本 | 字节 | 字节 |
| TCP | 端口 47808 | TCP / 串行 | 端口 2404 |
| 报文长度 | 较长 | 短 | 中 |
| 调试 | 简单 | 中 | 中 |
| 应用领域 | 排污口 / 空气 | 河道 / 水库 | 变电站 |

## 选型决策树

```text
环保 RTU 立项
├── 排污口在线监测
│   └── HJ 212（首选）
├── 空气站联网
│   └── HJ 212
├── 地表水
│   └── HJ 212（ST=21）
└── 噪声
    └── HJ 212（ST=24）
```

## 实战检查清单

```text
- TCP 端口与省级一致
- MN（13 位）已注册到省级平台
- PW（6 位）密码与省级一致
- 心跳周期符合省级要求
- 心跳应答正常
- 实时 / 分钟 / 小时 / 日数据按周期上报
- 超标数据标识正确
- 命令请求能正确应答
- 设置参数生效
- 因子编码与省级平台字典一致
- 数据状态 Flag-N 字段正确
- TCP 长连接保活
- 异常断开重连
- 离线数据补传机制
```

## 延伸阅读

- `bus/rtu-protocols.md`：RTU 设备协议全集
- `bus/sl651.md`：SL 651（结构相似）
- `bus/mqtt.md`：与 MQTT 互通
- `bus/hj212-failure-cases.md`：20 个产线死机案例库

## 版本演进

```text
HJ 212-2005：第一版
HJ 212-2017：当前主流（扩展 TCP / 命令码 / CRC）
HJ 212-2025：下一代更新中
```