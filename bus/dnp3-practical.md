# DNP3 Practical Guide

## 目标

本文用于把 DNP3 工程链路调通：TCP 接入、链路层帧解析、传输层分片、应用层对象、Class 报告、命令流程和 SA 认证。

## TCP 接入

```text
主站（client）→ TCP:20000 → RTU（server）
```

默认端口：20000

工程注意：

- 关键基础设施用 VPN / 专网。
- 双向连通性。
- 长连接保活。

## 链路层帧格式

```text
[0x05 0x64] [Length] [Control] [Dest] [Source] [CRC16]
```

字段：

```text
0x05 0x64：启动字符
Length：控制 + 目的 + 源 + CRC 字节数
Control：控制字节 1 字节
Dest：目的地址 2 字节低字节在前
Source：源地址 2 字节低字节在前
CRC16：16-bit CRC
```

## 控制字节速记

主站启动（DIR=0, PRM=1）：

```text
bit 7 = 0
bit 6 = 1
bit 5 = FCB
bit 4 = FCV
bit 3..0 = 功能码
```

从站响应（DIR=1, PRM=0）：

```text
bit 7 = 1
bit 6 = 0
bit 5 = DFC
bit 4 = RES
bit 3..0 = 功能码
```

## 报文示例

### 链路层 ACK

```text
05 64 05 40 02 00 02 00 87 9E 05 64
```

字段：

```text
05 64 启动
05 Length
40 控制字节（DIR=0, PRM=1, FCB=0, FCV=0, 功能码 0）
02 00 目的地址 = 2
02 00 源地址 = 2
87 9E CRC16
```

实际：CRC16 是 16 位（无后续字节），但 DNP3 用 16 位 + 加 16 位反转校验。

### 链路状态请求

主站 → RTU：

```text
05 64 05 C9 02 00 02 00 CRC1 CRC2
```

控制字节 0xC9：

```text
DIR=0, PRM=1, FCB=0, FCV=0, FC=9 (请求链路状态)
```

RTU → 主站响应：

```text
05 64 05 0B 02 00 02 00 CRC1 CRC2
```

控制字节 0x0B：

```text
DIR=1, PRM=0, FC=11 (链路状态响应)
```

## 传输层

应用层数据大时（>249 字节），传输层分片：

```text
[TH1] [First segment]
[TH2] [Second segment]
...
```

传输层头部 1 字节：

```text
FIR（bit 7）：First = 1
FIN（bit 6）：Final = 1
SEQ（bit 5..0）：0..63 序列号
```

工程实现：

```text
接收：按 SEQ 重组 → 直到 FIR=1 + FIN=1
发送：按 249 字节切片 → 序列号递增
```

## 应用层对象

应用层典型请求：

```text
FUNC = 0x01 Read
Object Header:
  Group = 60 (Class)
  Variation = 1
  Qualifier = 6
  Range = 0x00 (Class 0)
```

应用层响应：

```text
FUNC = 0x81 Response
Object Data:
  Group + Variation + Points
```

### 读完整性数据（Integrity Poll）

主站 → RTU：

```text
App Control: FIR=1 FIN=1 CON=0
FuncCode: 0x01 Read
Objects:
  g60v1 Class 0
  g60v2 Class 1
  g60v3 Class 2
  g60v4 Class 3
```

注意：实际常用一个 Object 读所有 Class 0：

```text
g60v2 Qualifier=6 Range=0x00 → Class 0
```

RTU 响应：

```text
FUNC = 0x81
Objects:
  g1v1 Binary Input Static
  g4v1 Analog Input Static
  ...
```

### 读 Class 0（实际请求）

主站 → RTU：

```text
App Control: FIR=1 FIN=1 CON=0
FuncCode: 0x01
Object:
  Group: 60
  Variation: 2
  Qualifier: 6
  Range: 0x00（=Class 0）
```

### 读 Class 1/2/3（事件）

```text
Group: 60, Variation: 3, Range: 0x01 (Class 1)
Group: 60, Variation: 4, Range: 0x02 (Class 2)
Group: 60, Variation: 1, Range: 0x03 (Class 3)
```

## 启用未确认报告

主站 → RTU：

```text
FuncCode: 0x14 Enable Unsolicited
Object:
  Group: 60
  Variation: 2
  Range: 0x00..0x03（启用所有 Class）
```

RTU 启用后主动上报事件。

## 命令流程（Select → Operate）

### 选择

主站 → RTU：

```text
FuncCode: 0x03 Select
Object:
  Group: 10（Binary Output）
  Variation: 1
  Qualifier: 17（Point + 8 bytes per index）
  Point: 5
  Data:
    01（合）
    00 00 00 00 00 00 00（控制码 + 标志）
```

### Operate

主站 → RTU：

```text
FuncCode: 0x04 Operate
Object: 同 Select
```

### Direct Operate（无选择）

主站 → RTU：

```text
FuncCode: 0x05 Direct Operate
Object: 同 Select
```

## 时间

DNP3 时间 g50v1（6 字节）：

```text
字节 0-1：毫秒（16 bit 低字节在前）
字节 2：日（低字节）
字节 3：日（高字节，百位）
字节 4：时
字节 5：分
```

g50v4（10 字节）扩展：

```text
g50v1 6 字节 + 秒（bit 0..7） + 时区（8 bit） + 时区偏移（16 bit）
```

## Counter (g3v1)

```text
Group: 3
Variation: 1
Data:
  32-bit 计数器（4 字节）
  Flag 16-bit（2 字节）
```

## Analog Input (g4v1)

```text
Group: 4
Variation: 1
Data:
  32-bit 模拟量（4 字节）
  Flag 8-bit（1 字节）
```

Flag 字节：

```text
bit 7：Online
bit 6：Restart
bit 5：Comm Lost
bit 4：Remote Force
bit 3：Local Force
bit 2：Over
bit 1：Under
bit 0：Ref Err
```

## 调试工具

- Wireshark：DNP3 dissector。
- DNP3 主站模拟：OpenDNP3、libdnp3。
- DNP3 RTU 模拟：DNP3 设备模拟器。
- socat：TCP 端口转发。

## 调试步骤

1. TCP 连接到 RTU:20000。
2. 发请求链路状态，确认链路。
3. 发完整性轮询（读 Class 0），确认所有数据。
4. 发事件轮询（读 Class 1/2/3），确认事件。
5. 启用未确认报告。
6. 发选择 + 操作命令。
7. 验证 SA v5/v6 认证（如启用）。

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| TCP 连接失败 | IP / 端口 / 防火墙 |
| 链路状态无响应 | 控制字节 DIR/PRM 错 |
| 完整性轮询无响应 | 测点组变体错 |
| Class 报告混乱 | Class 分配错 |
| 命令未执行 | Select → Operate 顺序错 |
| 未确认报告不触发 | Enable Unsolicited 未发 |
| 时间错 | 时钟不同步 |
| SA 认证失败 | 密钥 / 模式错 |

## 实战检查清单

- TCP 端口 20000 已开。
- 链路层 [0x05 0x64] 启动符解析正确。
- 控制字节解析正确。
- 传输层分片重组。
- 应用层对象 / 变体字典。
- Class 0/1/2/3 报告模式。
- 完整性轮询调度。
- 事件轮询调度。
- 未确认报告启用。
- 命令 Select → Operate 流程。
- 时间同步。
- SA v5/v6（关键基础设施）。
- 多主站（RTU 支持时）。