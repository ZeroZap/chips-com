# DNP3 主题总览

## 目标

DNP3（IEEE 1815）是北美电力 SCADA / 出海 RTU 协议。本文是**总览导航**，围绕 DNP3 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/dnp3-*.md
│
├── 速查层
│   ├── dnp3.md                  1 页概念：三层架构、对象变体、Class
│   └── dnp3-practical.md        报文示例 + 调试步骤
│
├── 原理层
│   └── dnp3-deep-dive.md        链路层 / 传输层 / 应用层 / SA v5/v6
│
└── 实战层
    └── dnp3-failure-cases.md    20 个产线死机案例
```

## 5 种读者路径

### 路径 1：刚接触 DNP3

```text
1. dnp3.md            概念 + 三层架构 + 对象变体
2. dnp3-practical.md  报文示例 + 调试步骤
3. dnp3-failure-cases.md 第 1-5 案例  链路 / 应用层
```

### 路径 2：要做 RTU 出海北美

```text
1. dnp3.md            协议定位
2. dnp3-practical.md  TCP 接入 + Class 报告
3. dnp3-deep-dive.md  对象变体 + 命令链 + SA v5
4. dnp3-failure-cases.md 第 6-15 案例  突发 / 命令 / Class
```

### 路径 3：要做 DNP3 SA v5/v6

```text
1. dnp3-deep-dive.md  SA v5/v6 认证
2. dnp3-practical.md  SA 调试
3. dnp3-failure-cases.md SA 相关案例
```

### 路径 4：要做 DNP3 主站

```text
1. dnp3-deep-dive.md  主站实现要点
2. dnp3-failure-cases.md 所有 20 案例
```

### 路径 5：要做 DNP3 一致性测试

```text
1. dnp3-deep-dive.md  一致性测试
2. dnp3-practical.md  测试工具
3. dnp3-failure-cases.md 测试用例
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| DNP3 是啥 | dnp3.md §定位 |
| 三层架构 | dnp3.md §三层架构 |
| 链路层帧 | dnp3-deep-dive.md §帧格式详解 |
| 传输层 | dnp3-deep-dive.md §传输层 |
| 应用层 | dnp3-deep-dive.md §应用层详解 |
| 对象变体 | dnp3-deep-dive.md §数据对象完整列表 |
| Class 报告 | dnp3-deep-dive.md §Class 报告策略 |
| 命令链 | dnp3-deep-dive.md §命令详解 |
| 时间 | dnp3-deep-dive.md §时间 |
| SA v5/v6 | dnp3-deep-dive.md §Secure Authentication (SA) v5 |
| 一致性测试 | dnp3-deep-dive.md §一致性测试 |
| 16 个常见故障 | dnp3-deep-dive.md §现场常见故障 |
| 20 个产线死机案例 | dnp3-failure-cases.md |

## DNP3 vs IEC 104

| 维度 | DNP3 | IEC 104 |
| --- | --- | --- |
| 标准 | IEEE 1815 | IEC 60870-5-104 |
| 物理 | TCP / 串行 | TCP |
| 体系 | 三层架构（链路 / 传输 / 应用） | 二层（APCI + ASDU） |
| 数据模型 | 对象组 / 变体 | ASDU 类型 |
| 报告模式 | Class 0/1/2/3 | 总召唤 / 时钟同步 / 突发 |
| 安全 | SA v5/v6（HMAC） | 无（依赖网络层） |
| 国内使用 | 出海 | 主流 |

## 选型决策树

```text
电力 RTU 立项
├── 国内新建项目
│   └── IEC 104（首选）
├── 北美 / 出海项目
│   └── DNP3（首选）
│       └── 高端变电站：加 IEC 61850
├── 关键基础设施（北美）
│   └── DNP3 + SA v5/v6
└── 工业侧通用
    └── Modbus RTU / TCP
```

## 实战检查清单

```text
- TCP 端口 20000 已开
- 链路层 [0x05 0x64] 启动符解析正确
- CRC16 计算正确（多项式 0xA6BC）
- 控制字节 DIR/PRM/FCB/FCV 解析正确
- 传输层分片重组
- 应用层对象 / 变体字典
- Class 0/1/2/3 报告模式
- 完整性轮询调度
- 事件轮询调度
- 未确认报告启用
- 命令 Select → Operate 流程
- 时间同步（g50v1 / g50v4）
- SA v5 认证（关键基础设施）
- SA v6 认证（最新）
- VPN / 专网配置
```

## 延伸阅读

- `bus/power-rtu/rtu-protocols.md`：RTU 设备协议全集
- `bus/power-rtu/iec104.md`：国内电力 RTU 标配
- `bus/power-rtu/iec61850.md`：变电站局域网高端
- `bus/power-rtu/dnp3-failure-cases.md`：20 个产线死机案例库

## 版本演进

```text
DNP3 v1：早期
DNP3 v2：当前主流
DNP3 v3：2007 后更新
IEEE 1815-2010：标准化为 IEEE 1815
IEEE 1815-2012：SA v5
IEEE 1815-2023：SA v6
```