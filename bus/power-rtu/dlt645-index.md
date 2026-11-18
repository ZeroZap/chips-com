---
tags:
  - layer/bus
  - type/index
  - protocol/dlt645
  - topic/power-rtu
---

# DL/T 645 主题总览

## 目标

DL/T 645 是国内电能表通信规约。本文是**总览导航**，围绕 DL/T 645 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/dlt645-*.md
│
├── 速查层
│   ├── dlt645.md                1 页概念：帧格式、DI、控制码、BCD
│   └── dlt645-practical.md      报文示例 + 调试流程
│
├── 原理层
│   └── dlt645-deep-dive.md      645-1997 vs 645-2007、密码、ESAM
│
└── 实战层
    └── dlt645-failure-cases.md  20 个产线死机案例
```

## 5 种读者路径

### 路径 1：刚接触 DL/T 645

```text
1. dlt645.md            概念 + 帧结构 + DI 编码
2. dlt645-practical.md  报文示例 + 调试步骤
3. dlt645-failure-cases.md 第 1-5 案例  帧定界 / 地址
```

### 路径 2：要做 RTU 接入电表

```text
1. dlt645.md            协议定位
2. dlt645-practical.md  串口参数 + 报文 + 多表轮询
3. dlt645-deep-dive.md  1997 vs 2007、ESAM
4. dlt645-failure-cases.md 第 6-15 案例  数据格式 / 块读
```

### 路径 3：要写电表驱动

```text
1. dlt645-deep-dive.md  BCD 编码 + DI 字典
2. dlt645-practical.md  报文示例
3. dlt645-failure-cases.md 所有案例
```

### 路径 4：要支持 698 / 311 协议

```text
1. dlt645-deep-dive.md  645 → 698 演进
2. dlt645-failure-cases.md 未来兼容性案例
```

### 路径 5：要对比 DL/T 645 与 CJ/T 188

```text
1. dlt645.md            电能表协议
2. bus/cjt188.md        水气热量表协议（结构类似）
```

## 主题速查矩阵

| 你想知道的事            | 文档位置                                                               |
| ----------------------- | ---------------------------------------------------------------------- |
| DL/T 645 是啥           | [[bus/power-rtu/dlt645\|dlt645]] §定位                                 |
| 645-1997 vs 645-2007    | [[bus/power-rtu/dlt645-deep-dive\|dlt645-deep-dive]] §版本对比         |
| 帧格式 68 ... 68 ... 16 | [[bus/power-rtu/dlt645-practical\|dlt645-practical]] §帧格式速记       |
| 表地址 6 字节 BCD       | [[bus/power-rtu/dlt645-deep-dive\|dlt645-deep-dive]] §表地址           |
| DI 4 字节字典           | [[bus/power-rtu/dlt645-deep-dive\|dlt645-deep-dive]] §数据标识（DI）   |
| 控制码 0x01/0x06        | [[bus/power-rtu/dlt645-practical\|dlt645-practical]] §控制码速查       |
| 写数据密码流程          | [[bus/power-rtu/dlt645-deep-dive\|dlt645-deep-dive]] §密码管理         |
| 多帧协议（块读）        | [[bus/power-rtu/dlt645-deep-dive\|dlt645-deep-dive]] §多帧协议（块读） |
| ESAM 安全               | [[bus/power-rtu/dlt645-deep-dive\|dlt645-deep-dive]] §安全合规         |
| BCD 解码                | [[bus/power-rtu/dlt645-deep-dive\|dlt645-deep-dive]] §BCD 解码         |
| 红外手持通信            | [[bus/power-rtu/dlt645-deep-dive\|dlt645-deep-dive]] §红外通信         |
| 16 个常见故障           | [[bus/power-rtu/dlt645-deep-dive\|dlt645-deep-dive]] §现场常见故障     |
| 20 个产线死机案例       | [[bus/power-rtu/dlt645-failure-cases\|dlt645-failure-cases]]           |

## DL/T 645 vs CJ/T 188

| 维度     | DL/T 645         | CJ/T 188         |
| -------- | ---------------- | ---------------- |
| 应用     | 电能表           | 水气热量表       |
| 表地址   | 6 字节 BCD       | 7 字节 BCD       |
| DI 编码  | 4 字节           | 4 字节           |
| 数据格式 | BCD              | BCD              |
| 帧格式   | 68 ... 68 ... 16 | 68 ... 68 ... 16 |
| 控制码   | 0x01/0x06 等     | 0x01/0x06 等     |

两者结构相似，但 DI 字典完全不同。

## 选型决策树

```text
电力 RTU 立项
├── 电能表集抄 / 配电监测
│   └── DL/T 645（首选）
│       └── 阶梯电价 / 远程购电：DL/T 645 + ESAM
├── 下一代（智能电表）
│   └── DL/T 698.45（基于对象）
├── 水气热量表
│   └── CJ/T 188
└── 其他
    └── Modbus RTU（部分电表支持）
```

## 实战检查清单

```text
- RS485 半双工 DE 时序正确
- 串口参数 2400 8E1（默认）
- 表地址 6 字节 BCD（默认 999999999999）
- 帧定界 68 ... 68 ... 16 解析正确
- 控制码主站 / 从站 / 异常三种区分
- DI 4 字节字典正确
- DATA BCD 解码正确
- CS 校验字节计算正确
- 读数据流程
- 写数据密码流程
- 多帧协议（块读）支持
- 异常 ERR 字段处理
```

## 延伸阅读

- [[bus/power-rtu/cjt188|cjt188]]：水气热量表协议（与 DL/T 645 结构类似）
- [[bus/power-rtu/rtu-protocols|rtu-protocols]]：RTU 设备协议全集
- [[bus/industrial/rs485-modbus-rtu-practical|rs485-modbus-rtu-practical]]：RS485 半双工基础
- [[bus/power-rtu/dlt645-failure-cases|dlt645-failure-cases]]：20 个产线死机案例库

## 版本演进

```text
DL/T 645-1997：第一版
DL/T 645-2007：当前主流（DI 4 字节 + 密码 + 块读 + 事件）
DL/T 645-2007Q：2007 修订
DL/T 698.45：下一代（基于对象类）
```
