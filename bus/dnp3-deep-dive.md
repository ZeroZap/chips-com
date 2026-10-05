# DNP3 Deep Dive

## 目标

本文深入 DNP3 协议栈细节，重点解决链路层 CRC、传输层分片、应用层对象变体、Class 报告调度、命令选择执行链、SA v5/v6 认证和现场排障。

## 协议栈分层

```text
物理层：RS485 / 以太网 / 光纤 / 4G
链路层：DNP3 链路层（IEEE 1815）
传输层：DNP3 传输层
应用层：DNP3 应用层
```

DNP3 三层架构清晰，每层都有 CRC/序列号等可靠性机制。

## 帧格式详解

### 链路层帧

```text
[0x05 0x64] [Length] [Control] [Dest] [Source] [CRC16]
```

Length 字节：

```text
Length = 控制 + 目的 + 源 + CRC = 1 + 2 + 2 + 2 = 7 字节
```

如果应用层数据大于 255 - 5 = 250 字节，则需要分片。链路层支持多个连续帧（Each frame = max 250 bytes payload）。

### CRC 计算

DNP3 链路层 CRC 是 16 位 CRC，多项式 0xA6BC（不同于 Modbus）：

```text
uint16_t crc = 0;
for (i = 0; i < len; i++) {
    crc ^= data[i] << 8;
    for (j = 0; j < 8; j++) {
        if (crc & 0x8000) {
            crc = (crc << 1) ^ 0xA6BC;
        } else {
            crc <<= 1;
        }
    }
}
```

CRC 范围：从 Length 字节开始到 Source 末尾。

## 控制字节详解

```text
bit 7：DIR（0 = 主站→从站，1 = 从站→主站）
bit 6：PRM（启动方）
bit 5：FCB（帧计数位，主站侧翻转）
bit 4：FCV（帧计数有效）
bit 3：DFC（数据流控制）
bit 2..0：功能码
```

主站启动（PRM=1）功能码：

```text
0 = Reset
1 = ACK
2 = NACK
3 = Confirmed User Data
4 = Unconfirmed User Data
5 = Request Link Status
```

从站响应（PRM=0）功能码：

```text
0 = ACK
1 = NACK
11 = Link Status
```

## 传输层

传输层用于分段长帧：

```text
[TH1] [First segment payload]
[TH2] [Second segment payload]
[TH3] [Final segment payload]
```

TH（传输头部）1 字节：

```text
bit 7：FIR（First = 1 表示第一段）
bit 6：FIN（Final = 1 表示最后段）
bit 5..0：SEQ（0..63 序列号）
```

应用层数据 = 多个 TH + 后续 payload 直到 FIN=1。

工程实现：

```text
发送：
  payload 大于 249 字节 → 分段
  第一段 FIR=1 SEQ=N
  中间段 FIN=N
  最后段 FIR=1 FIN=1

接收：
  按 SEQ 重组
  累积到 FIR=1 + FIN=1 → 完整 ASDU
```

## 应用层详解

### 应用控制字节

```text
bit 7：FIR（First）
bit 6：FIN（Final）
bit 5：CON（Need confirmation）
bit 4：UNS（Unsolicited）
bit 3..0：SEQ
```

应用 SEQ：

```text
0..15 循环
主站侧每次发送 SEQ += 1
从站响应复制 SEQ
```

### 应用功能码

请求类（主站 → RTU）：

```text
0x00 Confirm（应答）
0x01 Read
0x02 Write
0x03 Select
0x04 Operate
0x05 Direct Operate
0x06 Direct Operate No Ack
0x07 Freeze
0x08 Freeze No Ack
0x09 Freeze Clear
0x0A Freeze Clear No Ack
0x0B Enable Unsolicited
0x0C Disable Unsolicited
0x0D Assign Class
0x0E Delay Measure
0x0F Record Current Time
0x10 Open File
0x11 Close File
0x12 Delete File
0x13 Get File Info
0x14 Authenticate File
0x15 Abort File
0x16 Authenticate User (v6)
0x17 Unsolicited Auth Challenge (v6)
0x18 Request Challenge (v6)
0x19 Save Configuration (v6)
0x1D Cold Restart
0x1E Warm Restart
0x1F Return File Info
0x20 Initialize Application
0x21 Start Application
0x22 Stop Application
```

响应类（RTU → 主站）：

```text
0x81 Response
0x82 Unsolicited Response
```

### 对象头

每个对象请求 / 响应包含 Object Header：

```text
Group（1 字节）
Variation（1 字节）
Qualifier（1 字节）
Range / Count / Index（0-N 字节）
```

Qualifier 码：

```text
0x00 = No Range / Count = 0
0x01 = 1-byte Index Prefix
0x02 = 2-byte Index Prefix
0x03 = 4-byte Index Prefix
0x04 = 1-byte Count + 8-bit Index
0x05 = 2-byte Count + 16-bit Index
0x06 = 4-byte Count + 32-bit Index
0x07 = 1-byte Reserved Index
0x08 = 2-byte Reserved Index
0x09 = 4-byte Reserved Index
0x0B = 1-byte Free Format
0x0C = 2-byte Free Format
0x0D = 4-byte Free Format
0x10 = 1-byte Index Range
0x11 = 2-byte Index Range
0x12 = 4-byte Index Range
```

## 数据对象完整列表

| Group | 名称 | Variation | 含义 |
| --- | --- | --- | --- |
| g1 | Binary Input | v1 | Static |
| g1 | | v2 | Event |
| g2 | Binary Output | v1 | Static |
| g2 | | v2 | Event |
| g2 | | v3 | command+status |
| g3 | Counter | v1 | 32-bit Static |
| g3 | | v2 | 16-bit Static |
| g3 | | v3 | 32-bit Event |
| g4 | Analog Input | v1 | 32-bit Static |
| g4 | | v2 | 16-bit Static |
| g4 | | v3 | 32-bit Event |
| g10 | Binary Output | v1 | Binary Output |
| g10 | | v2 | Binary Output Event |
| g11 | Binary Output Command | v1 | Command |
| g11 | | v2 | Command Event |
| g20 | Counter | v1 | Static |
| g20 | | v2 | Event |
| g30 | Analog Input | v1 | Static |
| g30 | | v2 | Event |
| g40 | Analog Output Status | v1 | 16-bit Static |
| g40 | | v2 | 32-bit Static |
| g40 | | v3 | Event |
| g41 | Analog Output Command | v1 | 16-bit Command |
| g41 | | v2 | 32-bit Command |
| g41 | | v3 | Event |
| g50 | Time | v1 | 6-byte Time |
| g50 | | v2 | 4-byte Time |
| g50 | | v3 | 4-byte Time + Date |
| g50 | | v4 | 10-byte Time |
| g60 | Class | v1 | Static Class |
| g60 | | v2 | Event Class |
| g60 | | v3 | Static + Event |

## Class 报告策略

### 完整性轮询

```text
主站发：Read + g60v2 Range=0x00（Class 0）
RTU 回：所有 g1v1（Binary Input Static）+ g4v1（Analog Input Static）+ ...

工程实践：
  启动后立即执行
  周期性（如每 1 小时）
  数据完整性保证
```

### 事件轮询

```text
主站发：Read + g60v2 Range=0x01（Class 1）
       Read + g60v2 Range=0x02（Class 2）
       Read + g60v2 Range=0x03（Class 3）

RTU 回：Class 1/2/3 事件数据（如 Binary Input Event, Analog Input Event）

工程实践：
  周期短（1-10 秒）
  Class 1 优先级最高
  Class 3 优先级最低
```

### 未确认报告

```text
主站发：Enable Unsolicited
RTU 启用后主动上报事件

RTU 上报：
  App Control UNS=1
  FuncCode 0x82 Unsolicited Response
  Object：g1v2 / g4v3 等 Event 类型
```

## 数据格式详解

### Binary Input（g1）

g1v1（1 字节）：

```text
bit 7：状态（0/1）
bit 6..0：Flags
  bit 6：Online
  bit 5：Restart
  bit 4：Comm Lost
  bit 3：Remote Force
  bit 2：Local Force
  bit 1：Chatter Filter
  bit 0：State（实际值）
```

注意：Flags 中 bit 0 = State，实际状态位是 bit 7。

g1v2（1 字节状态 + 6 字节时间）：

```text
1 字节状态 + 6 字节时间（g50v1）
```

### Analog Input（g4v1）

```text
4 字节模拟量值（int32）
1 字节 Flags
  bit 7：Online
  bit 6：Restart
  bit 5：Comm Lost
  bit 4：Remote Force
  bit 3：Local Force
  bit 2：Over Range
  bit 1：Reference Err
  bit 0：Under Range
```

实际值：

```text
工程值 = DNP3 值 × scale
```

### Counter（g3v1）

```text
4 字节计数器（uint32）
2 字节 Flags
```

Flags 类似 Analog Input。

## 命令详解

### Select

```text
主站发：
  FuncCode 0x03
  Object: g10v1 + Point + Data

RTU 响应：
  FuncCode 0x83 Response
  Object: g10v1 + Point + Status（OK / Not authorized / Select timeout）
```

### Operate

```text
主站发：
  FuncCode 0x04
  Object: g10v1 + Point + Data（与 Select 同）

RTU 响应：
  FuncCode 0x83 Response
  Status: Success / Failure
```

### Direct Operate（无 Select）

```text
主站发：
  FuncCode 0x05
  Object: g10v1 + Point + Data
```

Single 流程快，无 Select → Operate 两步。

## 时间

g50v1（6 字节时间）：

```text
字节 0-1：毫秒（16 bit 低字节在前）
字节 2：日（低字节）
字节 3：日（高字节，含百年）
字节 4：时
字节 5：分
```

g50v4（10 字节时间）：

```text
g50v1 6 字节 +
秒（8 bit） +
LQF + 时区偏移（16 bit）
```

工程实现：

```text
RTU 收到 Record Current Time → 更新本地 RTC
后续上报带时间戳（g1v2 / g4v3）
```

## Secure Authentication (SA) v5

DNP3 SA v5 用于关键基础设施：

```text
挑战应答（Challenge-Response）：
  1. 主站发 Request Challenge
  3. RTU 回 Challenge（含 nonce）
  5. 主站用预共享密钥计算 HMAC
  7. 主站发 HMAC + 命令
  9. RTU 验证 HMAC + 执行
```

SA v5 模式：

```text
Aggressive Mode：
  主站发命令 + HMAC
  RTU 直接验证并执行
  单向认证

Normal Mode：
  主站发 Request Challenge
  RTU 回 Challenge
  主站发 HMAC
  RTU 验证后执行
  双向认证（防重放）
```

## Secure Authentication v6

IEEE 1815-2023 引入 v6：

```text
改进：
  HMAC-SHA256（替代 SHA-1）
  多密钥支持（key update）
  增强随机数
  Session-based 认证
```

## 文件操作

DNP3 文件操作：

```text
Open File (0x19)：
  打开文件用于读

Close File (0x1A)：
  关闭文件

Read File (0x1B)：
  读文件内容

Get File Info (0x1C)：
  获取文件信息（如配置、固件）
```

工程实践：

- 用于配置文件下载。
- 用于固件升级。

## 设备重启

```text
Cold Restart (0x1D)：
  设备冷重启（断电重启）
Warm Restart (0x1E)：
  设备热重启（软重启）
```

## 主站实现要点

```text
1. TCP 长连接
3. 链路层帧收发
4. CRC16 计算
5. 控制字节解析
6. 传输层分片重组
7. 应用层对象字典
8. Class 0/1/2/3 报告调度
9. 完整性轮询调度
10. 事件轮询调度
11. 未确认报告启用
12. 命令 Select → Operate
13. 时间同步
14. SA v5/v6 认证
15. 文件操作
```

## RTU 实现要点

```text
1. TCP server
3. 链路层帧收发
4. CRC16 计算
5. 控制字节处理
6. 传输层分片重组
7. 应用层对象映射到测点
8. Class 分配
9. 完整性轮询响应
10. 事件轮询响应
11. 未确认报告主动上报
12. 命令执行
13. 时间同步
14. SA v5/v6 认证
15. 文件操作
```

## 抓包排障

Wireshark DNP3 dissector：

```text
1. TCP 连接
3. 链路层 [0x05 0x64]
5. CRC16 验证
7. 控制字节
9. 传输层 TH
11. 应用层 FuncCode + Object
```

工程排障清单：

```text
1. TCP 异常
3. 链路层 CRC 错
5. 控制字节错
7. 传输层分片错
9. 应用层 Object 错
11. Class 分配错
13. 命令未执行
15. 未确认报告不触发
17. 时间戳错
19. SA 认证失败
```

## 现场常见故障

| 现象 | 优先检查 |
| --- | --- |
| TCP 连接失败 | IP / 端口 / 防火墙 |
| 链路状态无响应 | 控制字节错 |
| 完整性轮询无响应 | Object 错 |
| Class 报告混乱 | Class 分配错 |
| 命令未执行 | Select → Operate 顺序 |
| 未确认报告不触发 | Enable Unsolicited 未发 |
| 时间错 | 时钟不同步 |
| SA 认证失败 | 密钥 / 模式错 |

## 深度检查清单

- TCP 端口 20000 已开。
- 链路层 [0x05 0x64] 启动符解析正确。
- CRC16 计算正确（多项式 0xA6BC）。
- 控制字节 DIR/PRM/FCB/FCV/DFC 解析正确。
- 传输层分片重组。
- 应用层 Object / Variation / Qualifier 字典完整。
- Class 0/1/2/3 报告模式正确。
- 完整性轮询调度。
- 事件轮询调度。
- 未确认报告启用。
- 命令 Select → Operate 流程。
- Direct Operate 无 Select（如适用）。
- 时间同步（g50v1 / g50v4）。
- 计数器 32-bit / 16-bit。
- 模拟量 32-bit / 16-bit。
- Binary Input 标志位正确。
- 设备重启命令支持。
- 文件操作（可选）。
- SA v5 认证（关键基础设施）。
- SA v6 认证（最新关键基础设施）。
- 多主站支持（RTU 侧）。
- VPN / 专网配置（关键基础设施）。