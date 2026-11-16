# SL 651 主题总览

## 目标

SL 651-2014 是水文监测规约。本文是**总览导航**，围绕 SL 651 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/sl651-*.md
│
├── 速查层
│   ├── sl651.md                1 页概念：链路帧、信息帧、要素编码
│   └── sl651-practical.md      报文示例 + 调试步骤
│
├── 原理层
│   └── sl651-deep-dive.md      链路状态机、要素字典、多信道
│
└── 实战层
    └── sl651-failure-cases.md  20 个产线死机案例
```

## 5 种读者路径

### 路径 1：刚接触 SL 651

```text
1. sl651.md            概念 + 帧格式 + 要素字典
2. sl651-practical.md  报文示例 + 调试步骤
3. sl651-failure-cases.md 第 1-5 案例  端口 / 地址 / 链路
```

### 路径 2：要做 RTU 接入水文站

```text
1. sl651.md            协议定位
2. sl651-practical.md  TCP 接入 + 链路状态机
3. sl651-deep-dive.md  要素编码 + BCD 格式
4. sl651-failure-cases.md 第 6-15 案例  数据格式 / 命令
```

### 路径 3：要做水文多信道备份

```text
1. sl651-deep-dive.md  多信道备份
2. sl651-practical.md  GSM 短信备份
3. sl651-failure-cases.md 第 16-20 案例  信道切换
```

### 路径 4：要做加报策略

```text
1. sl651-deep-dive.md  加报触发
2. sl651-practical.md  自报 + 加报
3. sl651-failure-cases.md 第 11-15 案例  加报
```

### 路径 5：要做 SL 651 加密信道

```text
1. sl651-deep-dive.md  加密扩展
2. sl651-practical.md  加密信道
3. sl651-failure-cases.md 加密相关案例
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| SL 651 是啥 | sl651.md §定位 |
| 协议分层 | sl651.md §协议分层 |
| 网络结构 | sl651.md §网络结构 |
| 链路帧 | sl651-deep-dive.md §链路帧 |
| 信息帧 | sl651-deep-dive.md §信息帧 |
| 链路建立流程 | sl651-practical.md §链路建立 |
| 自报 | sl651-deep-dive.md §自报策略 |
| 加报触发 | sl651-deep-dive.md §加报触发 |
| GSM 短信备份 | sl651-deep-dive.md §GSM 短信备份 |
| 北斗短报文 | sl651-deep-dive.md §北斗短报文 |
| 加密扩展 | sl651-deep-dive.md §链路密码 |
| 主站实现要点 | sl651-deep-dive.md §主站（测站）实现要点 |
| 中心站实现要点 | sl651-deep-dive.md §中心站实现要点 |
| 16 个常见故障 | sl651-deep-dive.md §现场常见故障 |
| 20 个产线死机案例 | sl651-failure-cases.md |

## SL 651 vs SZY 206 vs IEC 104

| 维度 | SL 651 | SZY 206 | IEC 104 |
| --- | --- | --- | --- |
| 应用 | 水文 | 水资源 | 电力 |
| 字符集 | 二进制 + BCD | 二进制 + BCD | 二进制 |
| 协议格式 | 字节 | 字节 | 字节 |
| 链路帧 | F1/F2/F3/F4 | F1/F2/F3/F4 | 无 |
| 信息帧 | STX + LEN + ... | 同 SL 651 | APCI + ASDU |
| 要素编码 | 4 字节 | 4 字节 | ASDU Type |
| 多信道 | TCP/GSM/北斗 | TCP/GSM/北斗 | TCP |

## 选型决策树

```text
水文 / 水资源 RTU 立项
├── 河道 / 水库 / 水文站
│   └── SL 651（首选）
├── 取水口 / 地下水
│   └── SZY 206（首选）
├── 水资源监测补充
│   └── SL/T 427
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
- 北斗短报文备份（可选）
- 多信道切换状态机
- CRC 计算正确
- 要素编码正确
- BCD 编码正确
- 加密扩展（省级要求）
```

## 延伸阅读

- `bus/power-rtu/rtu-protocols.md`：RTU 设备协议全集
- `bus/power-rtu/szy206.md`：SZY 206（与 SL 651 配套）
- `bus/power-rtu/slt427.md`：SL/T 427（补充）
- `bus/power-rtu/hj212.md`：HJ 212（环保）
- `bus/power-rtu/sl651-failure-cases.md`：20 个产线死机案例库

## 版本演进

```text
SL 651-1998：第一版
SL 651-2014：当前主流
省份扩展：广东、湖南、河南等
```