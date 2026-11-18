---
tags:
  - layer/bus
  - type/index
  - protocol/iec104
  - topic/power-rtu
---

# IEC 104 主题总览

## 目标

IEC 60870-5-104 是 chips-com 电力 RTU 协议的核心主题之一。本文是**总览导航**，围绕 IEC 104 已经形成 3 篇专题笔记 + 1 篇实战案例，帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/bus/iec104-*.md
│
├── 速查层
│   ├── iec104.md                  1 页概念：APCI、ASDU、COT、CP56
│   └── iec104-practical.md        调试流程速查
│
├── 原理层
│   └── iec104-deep-dive.md        APCI 字节序、k/w/t 状态机、CP56Time2a、命令链
│
└── 实战层
    └── iec104-failure-cases.md    20 个产线死机案例
```

## 5 种读者路径

### 路径 1：刚接触 IEC 104 的工程师（1-2 小时入门）

```text
1. iec104.md            概念 + 帧结构 + 功能码 + 适用场景
2. iec104-practical.md  报文示例 + 调试步骤 + 实战检查清单
3. iec104-failure-cases.md 第 1-5 案例   常见坑点
```

### 路径 2：要做 RTU 上行模块（半天到 1 天）

```text
1. iec104.md            协议定位 + 数据模型
2. iec104-practical.md  TCP 接入 + 启动流程 + 时钟同步 + 总召唤
3. iec104-deep-dive.md  APCI 字节序 + k/w/t 联动 + 命令链
4. iec104-failure-cases.md 第 6-15 案例  突发 / 命令 / 协议层坑
5. 配 iec104-failure-cases 实战代码段
```

### 路径 3：要做一个 IEC 104 测试工具 / 模拟器

```text
1. iec104-practical.md  报文十六进制 + Wireshark 解码
2. iec104-deep-dive.md  ASDU 完整字段 + 通用分类
3. iec104-failure-cases.md 第 11-20 案例 异常路径与边界
```

### 路径 4：写 IEC 104 主站

```text
1. iec104-deep-dive.md  主站实现要点（10 大要点）
2. iec104-failure-cases.md 所有 20 个案例  了解产线常见失败
3. 配 MODBUS / DNP3 主站对比
```

### 路径 5：要对比 IEC 104 与 DNP3 / IEC 101

```text
1. iec104.md            与 IEC 101 / IEC 104 关系
2. bus/dnp3.md          DNP3 三层架构 / Class 报告 / SA v5
3. bus/iec101.md        IEC 101 串行版本
4. rtu-protocols.md     电力 RTU 协议选型矩阵
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| IEC 104 是啥、解决啥 | [[bus/power-rtu/iec104\|iec104]] §定位 |
| TCP 端口 / 启动流程 | [[bus/power-rtu/iec104-practical\|iec104-practical]] §TCP 链路 |
| APCI 4 字节控制域 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §控制域详解 |
| I/S/U 帧格式 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §三种 APDU 格式 |
| 总召唤流程 | [[bus/power-rtu/iec104\|iec104]] §通信流程 + [[bus/power-rtu/iec104-practical\|iec104-practical]] §启动流程 |
| ASDU 类型号表 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §ASDU 字段详解 |
| CP56Time2a 编解码 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §CP56Time2a 详解 |
| k/w/t 参数联动 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §k / w / t 参数联动 |
| 命令选择 / 执行 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §双点命令选择 / 执行 / 撤销 |
| 突发上传策略 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §突发上传 |
| 文件传输 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §文件传输 |
| 通用分类信息（GI） | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §通用分类信息 |
| 主站实现 10 大要点 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §主站实现要点 |
| RTU 实现 10 大要点 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §RTU 实现要点 |
| 16 个常见故障 | [[bus/power-rtu/iec104-deep-dive\|iec104-deep-dive]] §现场常见故障 |
| 20 个产线死机案例 | [[bus/power-rtu/iec104-failure-cases\|iec104-failure-cases]] |
| 选 IEC 104 还是 DNP3 | [[bus/power-rtu/rtu-protocols\|rtu-protocols]] §选型决策速查 |

## 与相邻协议对比

| 维度 | IEC 104 | IEC 101 | DNP3 | Modbus TCP |
| --- | --- | --- | --- | --- |
| 物理 | TCP | 串行 RS485 | TCP / 串行 | TCP |
| 标准 | IEC 60870-5-104 | IEC 60870-5-101 | IEEE 1815 | Modbus |
| 国内使用 | ✅ 主流 | 存量 | 出海 | 工控 |
| 海外使用 | 部分 | 部分 | ✅ 主流 | 通用 |
| 应用层 ASDU | IEC 101 共用 | 101 自有 | DNP3 对象 | 寄存器 |
| 帧定界 | TCP 长度 | FT1.2 静默 | [0x05 0x64] | TCP |
| 校验 | 无（TCP 保证） | CS 字节和 | CRC16 + 校验 | 无 |
| 实时性 | 中 | 中 | 中 | 低 |
| 工业级 | ✅ | ✅ | ✅ | ✅ |

## 选型决策树

```text
电力 RTU 立项
├── 国内变电站 / 配电 / 新能源场站
│   └── ✅ IEC 104（首选）
│       └── 历史兼容 / 串行链路：IEC 101（存量）
├── 出海北美 / 出口项目
│   └── ✅ DNP3（首选）
│       └── 高端变电站：加 IEC 61850 MMS
├── 工业侧通用接口
│   └── ✅ Modbus TCP（首选）
│       └── 协议简单 / 调试方便
└── 楼宇 / 智慧城市
    └── BACnet / OPC UA
```

## 文档关系图

```text
             rtu-protocols.md (战略总览)
                ↓
        ┌───────┼───────┐
        ↓       ↓       ↓
   iec104.md  iec101.md  dnp3.md
   iec61850.md hj212.md  sl651.md
        ↓       ↓       ↓
   iec104-   iec104-   iec104-
   practical  deep-dive  failure-cases
```

## 实战检查清单

```text
- TCP 端口 2404 已开
- STARTDT_ACT / CON 跑通
- 总召唤 C_IC_NA_1 正常返回
- 时钟同步 C_CS_NA_1 周期运行
- k / w / t1 / t2 / t3 与主站一致
- N(S) / N(R) 字节序正确
- 命令选择 → 执行流程跑通
- Wireshark 解码与设计一致
- ASDU 类型与 COT 处理完整
- 突发上传限速策略合理
```

## 延伸阅读

- [[bus/power-rtu/rtu-protocols|rtu-protocols]]：RTU 设备协议全集总览
- [[bus/power-rtu/iec101|iec101]]：IEC 104 串行版本
- [[bus/power-rtu/dnp3|dnp3]]：北美电力 RTU 标配
- [[bus/power-rtu/iec61850|iec61850]]：变电站局域网高端
- [[bus/industrial/modbus|modbus]]：工业通用协议
- [[bus/power-rtu/iec104-failure-cases|iec104-failure-cases]]：20 个产线死机案例库

## 版本演进

```text
IEC 60870-5-104:2000 / 2002 / 2007 / 2010
基本兼容，主要差异在 GI 扩展和文件传输
国内实践以 2002 为主，2010 增补
```