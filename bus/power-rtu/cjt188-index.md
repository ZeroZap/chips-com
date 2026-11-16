# CJ/T 188 主题总览

## 目标

CJ/T 188 是水气热量表通信规约。本文是**总览导航**，围绕 CJ/T 188 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/cjt188-*.md
│
├── 速查层
│   ├── cjt188.md                1 页概念：帧格式、DI、控制码
│   └── cjt188-practical.md      报文示例 + 调试步骤
│
├── 原理层
│   └── cjt188-deep-dive.md      表地址、BCD、密码、ESAM
│
└── 实战层
    └── cjt188-failure-cases.md  20 个产线死机案例
```

## 5 种读者路径

```text
1. cjt188.md            概念 + 帧结构 + DI
2. cjt188-practical.md  报文示例 + 调试
3. cjt188-deep-dive.md  表地址 + BCD + 密码 + ESAM
4. cjt188-failure-cases.md 20 案例
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| CJ/T 188 是啥 | cjt188.md §定位 |
| 与 DL/T 645 关系 | cjt188.md §与 DL/T 645 的关系 |
| 帧格式 | cjt188-practical.md §帧格式速记 |
| 表地址 7 字节 | cjt188-deep-dive.md §表地址 |
| DI 字典 | cjt188-deep-dive.md §数据标识（DI）详解 |
| 密码管理 | cjt188-deep-dive.md §密码管理 |
| 多帧协议 | cjt188-deep-dive.md §多帧协议（块读） |
| ESAM 安全 | cjt188-deep-dive.md §安全合规 |
| 红外手持 | cjt188-deep-dive.md §红外通信 |
| 16 个常见故障 | cjt188-deep-dive.md §现场常见故障 |
| 20 个产线死机案例 | cjt188-failure-cases.md |

## CJ/T 188 vs DL/T 645

| 维度 | CJ/T 188 | DL/T 645 |
| --- | --- | --- |
| 应用 | 水气热量表 | 电能表 |
| 表地址 | 7 字节 BCD | 6 字节 BCD |
| DI 编码 | 4 字节 | 4 字节 |
| 数据格式 | BCD | BCD |
| 帧格式 | 68 ... 68 ... 16 | 68 ... 68 ... 16 |
| 控制码 | 0x01/0x06 等 | 0x01/0x06 等 |

两者结构相似，但 DI 字典完全不同。

## 选型决策树

```text
水气热量表集抄立项
├── 冷水表 / 热水表
│   └── CJ/T 188（首选）
├── 热量表（北方供暖）
│   └── CJ/T 188
├── 燃气表
│   └── CJ/T 188
├── 电能表
│   └── DL/T 645
└── 其他
    └── Modbus RTU（部分支持）
```

## 实战检查清单

```text
- RS485 半双工 DE 时序正确
- 串口参数 2400 8E1（默认）
- 表地址 7 字节 BCD（默认 9999999999999）
- 帧定界 68 ... 68 ... 16 解析正确
- 控制码主站 / 从站 / 异常三种区分
- DI 4 字节字典正确
- DATA BCD 解码正确
- CS 校验字节正确
- 读流程正常
- 写流程密码验证正确
- 多帧协议支持
- 异常 ERR 字段处理
- 多表分时访问避免总线冲突
```

## 延伸阅读

- `bus/power-rtu/rtu-protocols.md`：RTU 设备协议全集
- `bus/power-rtu/dlt645.md`：DL/T 645（结构类似）
- `bus/industrial/rs485-modbus-rtu-practical.md`：RS485 半双工基础
- `bus/power-rtu/cjt188-failure-cases.md`：20 个产线死机案例库

## 版本演进

```text
CJ/T 188-2002：第一版（DI 2 字节）
CJ/T 188-2018：当前主流（DI 4 字节 + 密码 + 块读）
```