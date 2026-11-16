# SZY 206 主题总览

## 目标

SZY 206-2016 是水资源监测规约。本文是**总览导航**，围绕 SZY 206 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/szy206-*.md
│
├── 速查层
│   ├── szy206.md                1 页概念：取水要素、累计流量
│   └── szy206-practical.md      报文示例 + 调试步骤
│
├── 原理层
│   └── szy206-deep-dive.md      水资源要素字典、多信道
│
└── 实战层
    └── szy206-failure-cases.md  20 个产线死机案例
```

## 5 种读者路径

### 路径 1：刚接触 SZY 206

```text
1. szy206.md            概念 + 取水要素 + 协议分层
2. szy206-practical.md  报文示例 + 调试步骤
3. szy206-failure-cases.md 第 1-5 案例  端口 / 地址
```

### 路径 2：要做取水口监测 RTU

```text
1. szy206.md            协议定位
2. szy206-practical.md  TCP 接入 + 要素编码
3. szy206-deep-dive.md  BCD 解码 + 多信道
4. szy206-failure-cases.md 第 6-15 案例
```

### 路径 3：要做地下水监测

```text
1. szy206-deep-dive.md  地下水要素
2. szy206-practical.md  地下水报文
3. szy206-failure-cases.md 地下水案例
```

### 路径 4：要做 SZY 206 加密

```text
1. szy206-deep-dive.md  加密扩展
2. szy206-practical.md  加密信道
3. szy206-failure-cases.md 加密案例
```

### 路径 5：要做多中心站切换

```text
1. szy206-deep-dive.md  多中心站
2. szy206-practical.md  切换流程
3. szy206-failure-cases.md 多中心站案例
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| SZY 206 是啥 | szy206.md §定位 |
| 取水要素 | szy206.md §水资源要素编码 |
| 与 SL 651 区别 | szy206-deep-dive.md §与 SL 651 的差异 |
| 报文示例 | szy206-practical.md §报文示例 |
| 自报策略 | szy206-deep-dive.md §自报策略 |
| 加报触发 | szy206-deep-dive.md §加报策略 |
| GSM 短信备份 | szy206-deep-dive.md §GSM 短信备份 |
| 多信道备份 | szy206-deep-dive.md §多信道备份策略 |
| 加密扩展 | szy206-deep-dive.md §链路密码 |
| 16 个常见故障 | szy206-deep-dive.md §现场常见故障 |
| 20 个产线死机案例 | szy206-failure-cases.md |

## SZY 206 vs SL 651

| 维度 | SZY 206 | SL 651 |
| --- | --- | --- |
| 应用 | 水资源 | 水文 |
| 重点要素 | 取水流量、累计 | 雨量、水位、流量 |
| 设备类型 | 取水口、地下水 | 水文站、雨量站 |
| 中心站 | 水资源 | 水文 |
| 编码体系 | 4 字节要素 | 4 字节要素 |

## 选型决策树

```text
水资源 RTU 立项
├── 取水口在线监测
│   └── SZY 206（首选）
├── 地下水监测
│   └── SZY 206
├── 灌区用水
│   └── SL/T 427
├── 河道 / 水库 / 水文
│   └── SL 651
└── 电力 RTU
    └── IEC 104
```

## 实战检查清单

```text
- TCP 端口与省级一致
- 测站地址 / 中心站地址 BCD 编码正确
- 链路建立 F2 流程跑通
- 链路维持 F1 心跳正常
- 自报周期符合省级要求
- 加报触发逻辑正常
- 召测应答能正常返回
- 控制命令能正确应答
- 时间校准能正常执行
- 设置参数能生效
- GSM 短信备份信道正常
- 多信道切换状态机
- CRC 计算正确
- 要素编码正确
- BCD 编码正确
- 加密扩展（省级要求）
- 取水许可精细化
```

## 延伸阅读

- `bus/power-rtu/rtu-protocols.md`：RTU 设备协议全集
- `bus/power-rtu/sl651.md`：SL 651（结构相似）
- `bus/power-rtu/slt427.md`：SL/T 427（补充）
- `bus/power-rtu/szy206-failure-cases.md`：20 个产线死机案例库

## 版本演进

```text
SZY 206-2016：当前主流
省份扩展：广东、湖南、河南等
```