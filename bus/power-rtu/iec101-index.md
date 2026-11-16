---
tags:
  - layer/bus
  - type/index
  - protocol/iec101
  - topic/power-rtu
---

# IEC 101 主题总览

## 目标

IEC 60870-5-101 是 IEC 104 的串行版本。本文是**总览导航**，围绕 IEC 101 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/iec101-*.md
│
├── 速查层
│   ├── iec101.md                1 页概念：FT1.2 帧、控制域、ASDU、CS
│   └── iec101-practical.md      报文示例 + 调试流程
│
├── 原理层
│   └── iec101-deep-dive.md      FT1.2 帧、控制字节、FCB/FCV、CS、ASDU
│
└── 实战层
    └── iec101-failure-cases.md  20 个产线死机案例
```

## 5 种读者路径

### 路径 1：刚接触 IEC 101 的工程师

```text
1. iec101.md            概念 + 帧结构 + 控制域
2. iec101-practical.md  报文示例 + 串口调试
3. iec101-failure-cases.md 第 1-5 案例  串口接线 / 控制域
```

### 路径 2：要做 RTU 串行口

```text
1. iec101.md            协议定位
2. iec101-practical.md  串口参数 + 报文示例
3. iec101-deep-dive.md  FT1.2 帧解析 + 控制域编码
4. iec101-failure-cases.md 第 6-15 案例  串行链路 / RS485
```

### 路径 3：要升级 IEC 101 链路到 IEC 104

```text
1. iec104-deep-dive.md  TCP / APCI / 序号
2. iec101-deep-dive.md  串行 / FT1.2 / 控制域
3. 网关设计
```

### 路径 4：写 IEC 101 模拟器 / 测试工具

```text
1. iec101-practical.md  报文十六进制
2. iec101-deep-dive.md  完整字段编码
3. iec101-failure-cases.md 第 11-20 案例
```

### 路径 5：要做 IEC 101 主站

```text
1. iec101-deep-dive.md  主站实现要点
2. iec101-failure-cases.md 所有 20 个案例
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| IEC 101 是啥 | iec101.md §定位 |
| FT1.2 帧格式 | iec101.md §FT1.2 帧结构 |
| 固定长度帧 | iec101-practical.md §帧格式速记 |
| 可变长度帧 | iec101-practical.md §帧格式速记 |
| 控制域 1 字节 | iec101-deep-dive.md §控制域字节编码 |
| DIR / PRM / FCB / FCV | iec101-deep-dive.md §FCB / FCV 翻转机制 |
| 校验字节 CS | iec101-deep-dive.md §FT1.2 帧格式细节 |
| 平衡 / 非平衡传输 | iec101-deep-dive.md §平衡 / 非平衡模式差异 |
| 链路建立流程 | iec101-practical.md §链路建立过程 |
| 主站实现要点 | iec101-deep-dive.md §主站实现要点 |
| RTU 实现要点 | iec101-deep-dive.md §RTU 实现要点 |
| 16 个常见故障 | iec101-deep-dive.md §现场常见故障 |
| 20 个产线死机案例 | iec101-failure-cases.md |
| IEC 101 与 IEC 104 关系 | iec101.md §定位 |

## IEC 101 vs IEC 104 关键差异

| 维度 | IEC 101 | IEC 104 |
| --- | --- | --- |
| 物理 | RS485 / RS232 | TCP |
| 链路层 | FT1.2 帧 | TCP |
| 控制域 | 1 字节（DIR/PRM/FCB/FCV） | 4 字节（I/S/U 格式） |
| 帧定界 | 10 01 / 68 + + 0x16 | TCP 字节流 + 0x68 启动字符 |
| 校验 | CS 字节和 | 无（TCP 保证） |
| 序号 | FCB/FCV 翻转 | N(S)/N(R) |
| 限速 | FCB 状态机 | k/w 限速 |
| 测试帧 | 无 | TESTFR_ACT/CON |
| 应用层 ASDU | 完全共用 | 完全共用 |

## 选型决策树

```text
电力 RTU 立项
├── 国内新建项目
│   └── IEC 104（首选）
├── 兼容存量 / 串行口 / 海外项目
│   └── IEC 101（补充）
├── 厂站 / 电厂（可能用 IEC 101 平衡模式）
│   └── IEC 101
└── 工业侧 RTU
    └── Modbus RTU（更简单）
```

## 实战检查清单

```text
- RS485 半双工 DE 时序正确（等待 UART TC）
- 串口参数与主站一致
- A/B 已通过手册确认
- 总线两端 120Ω 终端
- 帧定界 10 01 / 68 ... 68 解析正确
- 控制域 DIR/PRM/FCB/FCV 解析正确
- 校验字节 CS 计算正确
- 链路建立 F2 流程跑通
- 总召唤正常返回
- 时钟同步周期运行
- 命令选择 → 执行流程跑通
```

## 延伸阅读

- `bus/power-rtu/iec104.md`：IEC 101 的 TCP 升级版
- `bus/power-rtu/rtu-protocols.md`：RTU 设备协议全集
- `bus/industrial/rs485-modbus-rtu-practical.md`：RS485 半双工基础
- `bus/power-rtu/iec101-failure-cases.md`：20 个产线死机案例库

## 版本演进

```text
IEC 60870-5-101:1995 / 2003 / 2006
2003 版引入平衡模式
2006 版细化通用分类（GI）
国内实践以 2003 为主
```