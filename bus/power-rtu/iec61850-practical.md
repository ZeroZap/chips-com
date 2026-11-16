---
tags:
  - layer/bus
  - type/practical
  - protocol/iec61850
  - topic/power-rtu
---

# IEC 61850 Practical Guide

## 目标

本文用于把 IEC 61850 工程链路调通：MMS Initiate、GetNameList、Read/Write、InformationReport、命令流程、GOOSE/SV 集成、SCL 配置解析和一致性测试。

## MMS TCP 连接

```text
Client（SCADA / RTU）→ TCP:102 → Server（IED）
```

工程注意：

- MMS TCP 端口固定 102。
- Initiate 服务建立 MMS 会话。
- Initiate 协商参数：max PDU size、services supported。

## MMS Initiate

Client → Server：

```text
MMS PDU: Initiate Request
  proposedMaxServOutstandingCalling
  proposedMaxServOutstandingCalled
  proposedDataStructureNestingLevel
  proposedVersion
```

Server → Client：

```text
MMS PDU: Initiate Response
  negotiatedMaxServOutstandingCalling
  negotiatedMaxServOutstandingCalled
  negotiatedDataStructureNestingLevel
  negotiatedVersion
```

工程实践：

```text
1. MMS Initiate Request
3. MMS Initiate Response
5. 协商成功 → 进入业务交互
```

## GetNameList

Client → Server：

```text
MMS PDU: GetNameList Request
  objectClass = Domain
  objectName = ""  根
  continueAfter = ""
```

Server → Client：

```text
MMS PDU: GetNameList Response
  listOfNames = ["LD0", "LD1", ...]
```

工程实现：

```text
1. 列出 IED 内的所有 LD
3. 对每个 LD 列 LN
5. 对每个 LN 列 DO
7. 对每个 DO 列 DA
```

## Read 数据

Client → Server（读单个 DO）：

```text
MMS PDU: Read Request
  variableAccessSpecification = (name: ["LD0/XCBR1/Pos.stVal"])
```

Server → Client：

```text
MMS PDU: Read Response
  value = (boolean: 1)  分位
```

## Read 数据集

Client → Server（读 DataSet）：

```text
MMS PDU: Read Request
  variableAccessSpecification = (name: ["LD0/LLN0.dsAin1"])
  ds = DataSet reference
```

Server → Client：

```text
MMS PDU: Read Response
  value = 数据集所有成员的当前值
```

## Write 数据

Client → Server（写单个 DO）：

```text
MMS PDU: Write Request
  variableAccessSpecification = name
  value = new value
```

工程实践：

```text
1. 用于配置参数（如 Mod、Beh）
3. 用于控制模式切换
5. 不能写入被保护数据
```

## 信息报告（InformationReport）

Client → Server（订阅）：

```text
MMS PDU: SetBRCBValues（配置报告控制块）
  BRCB reference
  RptEna = true
  DatSet = 数据集引用
  TrgOps = data-change | quality-change | integrity
  OptFlds = sequence-number | report-time-stamp
  IntgPd = 1000（完整性周期）
```

Server → Client（主动）：

```text
MMS PDU: InformationReport
  BRCB reference
  data = 数据集当前值
```

工程实践：

```text
1. SetBRCBValues 配置报告
3. SetURCBValues 配置非缓冲报告
5. 启动报告
7. 接收 InformationReport 报文
```

## 命令（Select → Operate）

Client → Server（选择）：

```text
MMS PDU: SelectWithValue（推荐）或 Select
  objectName = XCBR1.Pos
  value = (boolean: 1)  合位
```

Server → Client（响应）：

```text
MMS PDU: Select Response
  result = OK
```

Client → Server（操作）：

```text
MMS PDU: Operate
  objectName = XCBR1.Pos
  value = (boolean: 1)
```

Server → Client（操作结果）：

```text
MMS PDU: Operate Response
  result = OK
```

控制模型：

```text
Direct-with-normal-security（标准）：
  Select → Operate → CommandTermination

SBO（Select-Before-Operate）：
  Select → 收到 Cancel 或 Operate

Direct：
  直接 Operate
```

## GOOSE 多播接收

GOOSE 帧：

```text
目标 MAC：01-0C-CD-01-xx-xx
Ethertype：0x88B8
APPID：1-65535
PDU：gMMS PDU
```

工程实现：

```text
1. 打开多播接收（绑定到 01-0C-CD-01-xx-xx）
3. 接收 GOOSE 帧
5. 解析 goCBRef / stNum / sqNum / data
7. 提取跳闸 / 告警信息
```

GOOSE 重传机制：

```text
变位时立即发送
4ms, 8ms, 16ms, 32ms, ... 退避重发
直到 stNum 变化被接收方确认
```

## SV 多播订阅

SV 帧：

```text
目标 MAC：01-0C-CD-04-xx-xx（保护）
Ethertype 0x88BA
APPID：1-65535
PDU：sv PDU
```

工程实现：

```text
1. 绑定到 01-0C-CD-04-xx-xx
3. 接收 SV 帧
5. 解析采样数据
7. 同步（基于 IEEE 1588）
```

## SCL 配置解析

SCL 文件示例（ICD）：

```xml
<SCL xmlns="http://www.iec.ch/61850/2003/SCL">
  <IED name="IED1">
    <AccessPoint name="AP1">
      <Server>
        <LDevice inst="LD0">
          <LNode inst="1" lnClass="XCBR">
            <DO name="Pos" type="DPC"/>
            <DO name="Loc" type="SPS"/>
          </LNode>
          <LNode inst="2" lnClass="CSWI">
            <DO name="Mod" type="ENC"/>
          </LNode>
        </LDevice>
      </Server>
    </AccessPoint>
  </IED>
</SCL>
```

工程实现：

```text
1. 解析 XML
3. 提取 IED / LD / LN / DO 树
5. 映射到 MMS 命名空间
7. 启动 MMS 服务
```

工具：

```text
SCL 解析：libiec61850 / pyiec61850
SCL 校验：SCL Validator
SCL 编辑：Siemens DIGSI / ABB PCM600 / 第三方
```

## 时间同步

IEC 61850 时间同步：

```text
IEEE 1588 PTP（首选）：
  主时钟 GPS / 北斗 / 铷钟
  从时钟 IED
  精度 < 1 μs

NTP：
  精度 < 10 ms（不适合 SV）

1PPS：
  精度 < 100 ns（适合 SV）
```

工程实现：

```text
1. PTP 模式（Best Master Clock 算法）
3. PTP 同步后驱动本地 RTC
5. SV 采样基于本地 RTC
7. MMS 报告带时间戳
```

## GOOSE / SV 配置

GOOSE / SV 需要编目协议（gcbRef / svCBRef）：

```text
GOOSE 控制块：
  goCBRef = "IED1LD0/LLN0.gcbTrip1"
  datSet = "IED1LD0/LLN0.dsTrip"
  APPID = 1

SV 控制块：
  svCBRef = "IED1LD0/LLN0.svcbMU1"
  smvID = "MU1"
  confRev = 1
  smpRate = 4800
```

## Client 调试步骤

1. TCP 连接 IED:102。
2. 发 MMS Initiate Request。
3. 收 MMS Initiate Response。
4. 发 GetNameList Request（Domain）。
6. 发 Read Request（读 XCBR1.Pos.stVal）。
7. 收 Read Response。
8. 发 SetBRCBValues（订阅报告）。
9. 接收 InformationReport。
10. 发 Select → Operate（命令）。
11. 接收 Operate Response。

## RTU Server 调试步骤

1. 解析 ICD / CID SCL 文件。
2. 构建 LD / LN / DO 树。
3. 启动 MMS server（TCP:102）。
4. 接收 Initiate Request → 回 Initiate Response。
5. 接收 GetNameList → 回 Domain/LN/DO 列表。
6. 接收 Read → 回值。
7. 接收 SetBRCBValues → 配置 BRCB。
8. 接收 Select/Operate → 执行。
9. 定时器触发 InformationReport。

## 调试工具

- Wireshark：IEC 61850 / MMS dissector。
- MMS 主站模拟：libiec61850 / pyiec61850 / openMUC。
- SCL 工具：Siemens DIGSI / ABB PCM600。
- GOOSE / SV 模拟：libiec61850。
- 一致性测试：KEMA（DNV）测试工具。

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| MMS Initiate 失败 | TCP 端口 / Initiate 参数 |
| GetNameList 无响应 | Domain / Object class |
| Read 失败 | 引用路径错 |
| Write 失败 | 权限 / 写保护 |
| InformationReport 不触发 | 数据集 / 触发选项 / RptEna |
| Select 失败 | 控制模型 |
| Operate 失败 | Select 超时 |
| GOOSE 不通 | 多播 / APPID / 数据集 |
| SV 不通 | 多播 / APPID / 同步 |
| 时间不同步 | PTP / NTP |

## 实战检查清单

- TCP 端口 102 已开。
- MMS Initiate 服务已实现。
- GetNameList / Read / Write 已支持。
- InformationReport 订阅支持。
- 命令 Select / Operate 流程完整。
- 报告控制块 BRCB / URCB 配置。
- 数据集 DataSet 定义。
- 触发选项支持。
- GOOSE 多播接收（如保护 IED）。
- SV 多播订阅（如合并单元）。
- SCL 文件解析（ICD / CID / SCD）。
- 时间同步（IEEE 1588 / NTP）。
- 一致性测试报告。