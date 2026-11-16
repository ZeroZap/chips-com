# DNP3

## 定位

DNP3（Distributed Network Protocol version 3）是北美电力 SCADA 标准，IEEE 1815 标准。用于电力主站（Master）和远动终端（Outstation / RTU）之间通信。

```text
DNP3 v1: 早期版本（部分遗留）
DNP3 v2: 当前主流
DNP3 v3: 2007 后更新
IEEE 1815: 2010 / 2012 / 2023
```

## 应用领域

- 北美电力 SCADA。
- 海外电力项目（北美、南美、欧洲）。
- 出海 RTU 产品标配。
- 关键基础设施（北美电力、油气）。

## 协议分层

```text
物理层：RS485 / 以太网 / 光纤 / 4G
链路层：DNP3 链路层
传输层：DNP3 传输层
应用层：DNP3 应用层
```

## 三层架构

```text
应用层：功能码（Read/Write/Select/Operate）+ 数据对象 + 标志
传输层：分段/重组 + 序列号
链路层：寻址 + 帧定界 + CRC
```

## 链路层帧

```text
[0x05 0x64] [Length] [Control] [Destination] [Source] [CRC] [CRCB]
```

字段：

```text
0x05 0x64  启动字符（2 字节）
Length     = 控制 + 目的 + 源 + CRC 字节数（1 字节）
Control    = 控制字节（1 字节）
Destination = 目的地址（2 字节低字节在前）
Source   = 源地址（2 字节低字节在前）
CRC     = 16 位 CRC
```

注意长度字段：表示控制 + 目的 + 源 + CRC = 1 + 2 + 2 + 2 = 7 字节（不含启动字符 + 长度本身）。

如果长度超过 255，链路层自动分段。

## 控制字节

```text
bit 7：DIR（1 = 主站→从站，0 = 从站→主站）
bit 6：PRM（启动方）
bit 5：FCB（帧计数位）
bit 4：FCV（帧计数有效）
bit 3：DFC（数据流控制）
bit 2..0：功能码
```

链路功能码：

```text
0 = ACK
1 = NACK
2 = Test Link States
3 = Test Link States Reply
4 = Unconfirmed User Data
5 = Confirmed User Data
6 = Request Link Status
7 = Link Status
```

## 传输层

传输层用于分片重组。传输层头部 1 字节：

```text
bit 7：FIR（Final = 1 表示最后一个片段）
bit 6：FIN（First = 1 表示第一个片段）
bit 5..0：SEQ（序列号）
```

## 应用层

应用层头部：

```text
[Control] [FuncCode] [ObjectHeader...] [Data...]
```

应用层控制字节：

```text
bit 7：FIR（First fragment）
bit 6：FIN（Final fragment）
bit 5：CON（Control flag）
bit 4：UNS（Unsolicited）
bit 3..0：SEQ（序列号）
```

应用功能码：

| FuncCode | 含义 | 方向 |
| --- | --- | --- |
| 0x00 | Confirm | 应答 |
| 0x01 | Read | 主站读 |
| 0x02 | Write | 主站写 |
| 0x03 | Select | 选择（命令） |
| 0x04 | Operate | 执行（命令） |
| 0x05 | Direct Operate | 直接执行（无连选） |
| 0x06 | Direct Operate No Ack | 直接执行不确认 |
| 0x07 | Freeze | 累积量冻结 |
| 0x0D | Assign Class | 分配 Class |
| 0x0E | Delay Measure | 延迟测量 |
| 0x14 | Record Current Time | 记录时间 |
| 0x18 | File Read | 文件读 |
| 0x1D | Cold Restart | 冷重启 |
| 0x1E | Warm Restart | 热重启 |
| 0x80 | Response | 应答响应 |

## 数据对象（Object）

DNP3 用对象组和变体标识数据：

```text
Group: 数据类型（如 g1 = Binary Input, g2 = Binary Output, g4 = Analog Input）
Variation: 数据格式/时序
Point Index: 测点号
```

常用对象：

| Group | 名称 | 说明 |
| --- | --- | --- |
| g1 | Binary Input | 数字量输入 |
| g2 | Binary Output | 数字量输出 |
| g3 | Counter | 累积量 |
| g4 | Analog Input | 模拟量输入 |
| g10 | Binary Output | 输出命令 |
| g13 | Binary Output Command Event | |
| g20 | Counter | |
| g30 | Analog Input | |
| g40 | Analog Output Status | 模拟量输出 |
| g41 | Analog Output Command | 模拟量输出命令 |
| g50 | Time and Date | 时间日期 |
| g60 | Class | Class 数据 |

常用变体：

| Variant | 含义 |
| --- | --- |
| g1v1 | Binary Input Static（无时序） |
| g1v2 | Binary Input Event（含时序） |
| g2v1 | Binary Output Status |
| g2v2 | Binary Output Event |
| g3v1 | Counter Static |
| g3v2 | Counter Event |
| g4v1 | 32-bit Analog Input Static + Flag |
| g4v2 | 16-bit Analog Input Static + Flag |
| g4v3 | 32-bit Analog Input Event |
| g10v1 | Binary Output |
| g10v2 | Binary Output Event |
| g50v1 | Time and Date (6 字节) |
| g50v4 | Time and Date (10 字节含秒分数) |

## Class 报告

DNP3 把数据分为 4 个 Class：

```text
Class 0：所有静态数据（Integrity Poll 全部读）
Class 1：高优先级（如报警）
Class 2：中优先级（事件）
Class 3：低优先级（一般事件）
```

工程实践：

```text
完整性轮询（Integrity Poll）：
  读 Class 0 所有数据
  通常在链路建立后 / 周期性（如每 1 小时）
  
事件轮询（Event Poll）：
  读 Class 1 / 2 / 3 事件数据
  通常周期性（如每 1-10 秒）

未确认报告（Unsolicited Report）：
  RTU 主动上报，无需主站询问
  通过 Enable Unsolicited 启用
```

## 报文示例

### 完整性轮询（读 Class 0）

主站 → RTU：

```text
链路层：[0x05 0x64] [Length=7] [Control] [Dest=RTU] [Source=Master] [CRC]
传输层：FIR/FIN + SEQ
应用层：
  Control: FIR=1, FIN=1, CON=0
  FuncCode: 0x01 Read
  Object: g60v1 + Qualifier 0x06 + Range（Class 0）
    Object: 60
    Variation: 1
    Qualifier: 6
    Range: 0x00（Class 0）
```

RTU → 主站：

```text
应用层：
  Control: FIR=1, FIN=1, CON=0, UNS=0
  FuncCode: 0x81 Response
  Object: g1v1（Binary Input Static）+ 测点数据
        g4v1（Analog Input Static）+ 测点数据
        ...
```

### 选择 → 执行（命令下行）

主站 → RTU（Select）：

```text
FuncCode: 0x03 Select
Object: g10v1 + Point 5
Value: 01（合）
```

RTU → 主站（响应）：

```text
FuncCode: 0x83 Response
```

主站 → RTU（Operate）：

```text
FuncCode: 0x04 Operate
Object: g10v1 + Point 5
Value: 01
```

### 未确认报告

RTU → 主站：

```text
FuncCode: 0x02 Write（实际是响应）
Object: g2v2 Binary Output Event
```

## 时间

DNP3 用 6 字节 BCD 时间戳（g50v1）：

```text
字节 0-1：ms（16 bit）
字节 2-3：日（hundreds + days）
字节 4：时
字节 5：分
```

g50v4 增加秒分数（10 字节）。

## 累积量（Counter）

g3v1 32-bit Counter Static：

```text
字节 0-3：32-bit 计数器值（BCD 或 uint32）
字节 4-5：flags
```

## Secure Authentication (SA)

DNP3 SA v5 / v6 用于安全关键基础设施：

```text
v5 (IEEE 1815-2010)：
  HMAC-SHA1 + 挑战应答
  Aggressive Mode（高效）
  Normal Mode（标准）

v6 (IEEE 1815-2023)：
  HMAC-SHA256
  增强密钥管理
  多密钥支持
```

工程实践：

- 关键基础设施必须支持 SA。
- 加密密钥每台设备独立。
- 双向认证。

## TCP/IP 传输

DNP3 over TCP（IEEE 754 系列）：

```text
TCP 端口：20000（DNP3 默认）
```

链路层首部 [0x05 0x64] 标识 DNP3 数据流。

工程实践：

```text
1. 主站连接 RTU:20000
3. 主站发完整性轮询
5. RTU 回响应
7. 周期性事件轮询
9. 突发 / 未确认报告
```

## 适用场景

- 北美电力 SCADA。
- 海外电力出海项目。
- 油气 SCADA。
- 关键基础设施。
- 出海 RTU 必备。

## 延伸阅读

- `bus/rtu-protocols.md`：RTU 设备协议全集。
- `bus/iec104.md`：与 IEC 104 对比（国内 vs 海外）。
- `bus/dnp3-deep-dive.md`：DNP3 三层结构（应用 / 链路 / 物理）细节。
- IEEE 1815 标准细节：本库暂无专篇，需查 IEEE 官方标准原文。

## 检查清单

- TCP 端口 20000 已开。
- 链路层 [0x05 0x64] 启动符解析正确。
- 控制字节 DIR/PRM/FCB/FCV/DFC 解析正确。
- 传输层分片重组实现。
- 应用层对象/变体字典实现。
- Class 0/1/2/3 报告模式。
- 完整性轮询 + 事件轮询调度。
- 未确认报告启用。
- 命令选择 → 执行流程。
- SA v5/v6 加密（关键基础设施）。