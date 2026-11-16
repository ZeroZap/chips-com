# IEC 61850 Deep Dive

## 目标

本文深入 IEC 61850 协议栈细节，重点解决 MMS 编码、LN/DO/DA 建模、BRCB/URCB 报告机制、命令传递链、GOOSE/SV 性能约束、SCL 工程化、时间同步和一致性测试。

## 协议栈分层

```text
物理层：以太网 100BASE-TX / 1000BASE-T / 光纤
链路层：以太网 MAC（支持多播）
网络层：IPv4 / IPv6
传输层：TCP（MMS）/ 直接映射（GOOSE / SV）
表示层：ASN.1 BER
应用层：MMS / GOOSE / SV
```

IEC 61850 复杂在建模（MMS + SCL）和多种传输（TCP / 多播）。

## MMS PDU 编码

MMS PDU 使用 ASN.1 BER（Basic Encoding Rules）：

```text
结构：
  Tag（1 字节）
  Length（1-N 字节）
  Value

Example:
  0xA2 (Context, Constructed, Tag 2)
  Length
  Value...
```

工程实现：

```text
BER 解析：基于 TLV 递归
BER 编码：树状构造 → 字节流
```

常用 BER 库：

```text
libiec61850（Linux）
asn1c（开源）
pyasn1（Python）
```

## MMS 服务完整列表

基本服务：

```text
Initiate
Conclude
Abort
Reject
Status
UnsolicitedStatus
```

变量访问：

```text
GetNameList
Read
Write
InformationReport
GetVariableAccessAttributes
GetDataDirectory
GetDataDefinition
GetDataSetValues
SetDataSetValues
CreateDataSet
DeleteDataSet
GetDataSetDirectory
```

报告 / 日志：

```text
Report（Buffered / Unbuffered）
GetBRCBValues / SetBRCBValues
GetURCBValues / SetURCBValues
GetLCBValues / SetLCBValues
ReadLog / GetLogStatus
```

命令：

```text
Select
SelectWithValue
Cancel
Operate
CommandTermination
TimeActivatedOperate
TimeActivatedOperateTermination
```

文件：

```text
FileOpen
FileRead
FileClose
FileDelete
FileRename
ObtainFile
```

GOOSE / SV：

```text
SendGOOSEMessage
SendSVMessage
GetGoCBValues
SetGoCBValues
GetSvCBValues
SetSvCBValues
```

## 命名空间（Object Name）

MMS 对象命名：

```text
Domain：逻辑设备 LD
Named Variable：数据对象 DO + 数据属性 DA
Named Variable List：数据集 DataSet
```

引用格式：

```text
Domain:
  "LD0"

Named Variable:
  "LD0/XCBR1.Pos.stVal"
  LD 名称 / LN 名称 / DO 名称 / DA 名称

Named Variable List:
  "LD0/LLN0.dsAin1"
```

## 报告控制块（BRCB / URCB）

### BRCB（Buffered Report Control Block）

```text
BRCB reference：命名空间路径
RptEna：1 = 启用
DatSet：数据集引用
ConfRev：配置版本
OptFlds：选项字段
  - sequence-number
  - report-time-stamp
  - reason-for-inclusion
  - data-reference
  - buffer-overflow
  - entryID
TrgOps：触发选项
  - dchg（data change）
  - qchg（quality change）
  - dupd（data update）
IntgPd：完整性周期（ms）
BufTm（包含与 time）
ResvTms：保留时间
SqNum：序列号（递增）
GI=0
PurgeBuf：清空缓冲
EntryID：入口 ID
```

### URCB（Unbuffered Report Control Block）

类似 BRCB 但无缓冲：

```text
适用于：
  高实时性数据（如保护事件）
  变位立即上报
```

## 报告触发流程

```text
1. 数据变化 → 触发 dchg
3. 质量变化 → 触发 qchg
5. 完整性周期到 → 触发 integrity
7. Server 检查 BRCB 条件
9. 数据集成员变化 → 发送 InformationReport
11. 报告含：
    sqNum（递增）
    timestamp
    数据
```

## 命令模型

### Direct-with-Normal-Security

```text
1. Select（client 发送）
3. Server 返回 Select Response（OK / Not Authorized / Locked）
5. Operate（client 发送）
7. Server 执行命令
9. Operate Response（result = OK / Failed）
```

### SBO（Select-Before-Operate）

```text
1. Select
3. 收到 Operate → 执行
5. 或收到 Cancel → 取消
```

### TimeActivatedOperate

```text
带时间戳的操作：
  OperateAt + time
  Server 等待到时间执行
```

## 控制对象属性

```text
Pos：
  ctlVal：控制值
  origin：来源（or / 操作员）
  ctlTest：测试标志
  OperTim：操作时间
  Terminal：终端
  ...
```

控制服务：

```text
Direct（直接执行）
SBO（选择后执行）
SBOw（选择带值后执行）
EnhancedSecurity（增强安全）
```

## 数据对象（DO）常用

每个 LN 有 DO。常用 LN/DO：

```text
XCBR（断路器）：
  Pos：位置（分合 = 中间）
  OpCnt：操作计数

XSWI（隔离开关）：
  Pos：位置

CSWI（开关控制器）：
  Mod：模式
  Loc：就地 / 远方
  Pos：位置

MMXU（三相测量）：
  TotW：总有功
  TotVAr：总无功
  TotPF：总功率因数
  TotVA：总视在功率
  PhV：相电压
  A：相电流
  W：有功
  VAr：无功
  PF：功率因数

PIOC（瞬时过流保护）：
  Str：启动（保护启动）
  Op：动作（保护动作）
  TmASt：定时器状态

TCTR（电流互感器）：
  Amp：电流瞬时值（CT 一次侧）
  ARtg：额定电流
```

## 数据属性（DA）层次

```text
DO（数据对象）：
  Functional Constraint（功能约束）
  Presence（必须 / 可选 / 条件）
  Sub Data Attributes（子数据属性）
```

功能约束（FC）：

```text
ST    状态（status）
MX    测量（measurement）
CO    控制（control）
SP    设点（setpoint）
CF    配置（configuration）
EX    描述（description）
DC    描述（description）
SE    可设置带约束（setpoint, constrained）
SG    设置组（setting group）
BR    Buffered Report
RP    Unbuffered Report
GO    GOOSE Control
SV    SV Control
```

例：

```text
XCBR1.Pos.stVal（FC=ST, 当前状态）
MMXU1.TotW.mag.f（FFC=MX, 测量幅值）
CSWI1.Pos.ctlVal（FC=CO, 控制值）
```

## GOOSE 详解

GOOSE PDU 结构：

```text
gMMS PDU：
  goCBRef      GOOSE 控制块引用
  datSet       数据集引用
  goID         GOOSE ID
  t            时间戳
  stNum        状态序号（变位时增）
  sqNum        序列号（每帧增）
  test         测试标志
  confRev      配置版本
  ndsCom       需要重传
  numDatSetEntries 数据集条目数
  data         数据（g1v1 / g2v1 / ...）
```

GOOSE 传输机制：

```text
变位时：
  立即发送（高优先级）
  stNum + 1

后续重传：
  4ms, 8ms, 16ms, 32ms, 64ms, ... 退避
  sqNum 每帧增
  直到接收确认或超时

GoCBEna=1 时启用 GOOSE
```

性能要求：

```text
变位 → 接收：< 4 ms
重传：8 ms, 16 ms, 32 ms
GOOSE 帧最大：1500 bytes（MAC 单包）
```

## SV 详解

SV PDU 结构：

```text
svMMS PDU：
  svCBRef       SV 控制块引用
  smvID         SV ID
  smpCnt        采样计数（递增）
  confRev       配置版本
  smpSynch      同步状态
  smpRate       采样率
  numDatSetEntries 数据集条目数
  data         数据（采样值）
```

SV 性能：

```text
采样率：
  IEC 61850-9-2 LE：4.8 kHz（80 samples/cycle, 50 Hz 系统）
  IEC 61850-9-2：4 kHz 或 80 samples/cycle

帧间隔：
  250 μs @ 4.8 kHz
  312.5 μs @ 3.2 kHz

同步要求：1 μs
```

## SCL 配置详解

### ICD（IED Capability Description）

```text
厂家提供
IED 能力描述：
  LD 列表
  LN 类列表
  DO 类型
  Report Control Block
  GOOSE Control Block
  SV Control Block
  DataSet 引用（但不实际）
```

### SCD（Substation Configuration Description）

```text
系统集成商提供
整个变电站配置：
  Substation
    VoltageLevel
      Bay
        ConductingEquipment
        ConnectivityNode
  Communication
    Subnetwork
      ConnectedAP
        GSE / SMV
  IED（每个 IED 的 CID）
```

### CID（Configured IED Description）

```text
每个 IED 实例化
  IED 名称 / 网络地址
  LD 实例化
  Report Control Block 配置
  GOOSE / SV 控制块配置
  DataSet 实际定义
```

### 配置流程

```text
1. 厂家提供 ICD（每个 IED）
3. 系统集成商导入 ICD
5. 配置 Substation 拓扑
7. 实例化 IED
9. 配置 Report Control Block
10. 配置 GOOSE / SV 控制块
11. 生成 SCD
12. 将 IED 相关 CID 下载到 IED
```

## SCL XML 详解

```xml
<SCL xmlns="http://www.iec.ch/61850/2003/SCL">
  <Header id="SCD_Project1" version="1.0"/>
  <Substation name="SUB1">
    <VoltageLevel name="VL1">
      <Bay name="Bay1">
        <ConductingEquipment name="Breaker1" type="CBR"/>
      </Bay>
    </VoltageLevel>
  </Substation>
  <Communication>
    <Subnetwork name="Subnet1">
      <ConnectedAP apName="AP1" iedName="IED1">
        <GSE apName="AP1_GSE1" ldInst="LD0">
          <Address>
              <MAC>01-0C-CD-01-00-01</MAC>
              <APPID>0001</APPID>
            </Address>
            <GSEControl datSet="dsTrip" appID="GSE1" confRev="1"/>
          </GSE>
        </ConnectedAP>
      </Subnetwork>
  </Communication>
  <IED name="IED1">
    <AccessPoint name="AP1">
      <Server>
        <Authentication/>
        <LDevice inst="LD0">
          <LNode lnClass="LLN0" inst=""/>
          <LNode lnClass="XCBR" inst="1">
            <DOI name="Pos">
              <DAI name="ctlModel">
                <Val>sbo-with-normal</Val>
              </DAI>
            </DOI>
          </LNode>
          <DataSet name="dsTrip">
            <FCDA ldInst="LD0" lnClass="XCBR" inst="1" doName="Pos" daName="stVal" fc="ST"/>
          </DataSet>
          <GSEControl datSet="dsTrip" appID="GSE1" confRev="1"/>
          <ReportControl datSet="dsAin" rptID="brcbAin" confRev="1" buffered="true" bufTm="100" intgPd="1000"/>
        </LDevice>
      </Server>
    </AccessPoint>
  </IED>
  <DataTypeTemplates>
    <LNodeType id="LTC_XBR_1" lnClass="XCBR">
      <DO name="Pos" type="DPC"/>
    </LNodeType>
</SCL>
```

## MMS BER 编码示例

Read Request：

```text
Read Request PDU:
  0xA4 (Context [4] IMPLICIT ReadRequest, Constructed)
  Length
    VariableAccessSpecification:
      0x20 (ObjectName)
      Length
        DomainName:
          0x81 (Visible String)
          Length
            "LD0"
        ItemName:
          0x80 (Visible String)
          Length
            "XCBR1.Pos.stVal"
```

工程实现：

```text
BER 编码：递归编码 TLV
BER 解码：递归解析 TLV
```

## 一致性测试

IEC 61850-10 一致性测试：

```text
测试层级：
  A 级：基本 MMS 服务
  B 级：报告 + 日志 + 控制
  C 级：GOOSE + SV

测试项：
  Initiate
  GetNameList
  Read / Write
  Report（Buffer / Unbuffer）
  Control（Direct / SBO）
  GOOSE（Pub / Sub）
  SV（Pub / Sub）
  时间同步

测试工具：
  KEMA（DNV）一致性测试工具
  IEC 61850 测试仪
```

工程实践：

- 国内：电力科学研究院测试。
- 海外：DNV（KEMA）/TUV 测试。
- 测试报告是项目验收必要。

## Client / Server 性能

```text
Read 性能：10-100 ms（取决于数据集大小）
Report 性能：10-100 ms（变位触发）
Control 性能：< 100 ms（Select → Operate）
GOOSE 性能：< 4 ms（变位 → 接收）
SV 性能：250 μs / 帧（4.8 kHz）
```

## 主站（Client / SCADA / RTU）实现要点

```text
1. MMS Initiate
3. GetNameList（树遍历）
5. Read（单 DO / DataSet）
7. Write（配置参数）
9. InformationReport（订阅）
10. 报告控制块配置
11. Select / Operate / Cancel
12. 文件传输
13. SCL 解析（CID 下载 / 校验）
14. GOOSE 监听（如保护 IED）
15. SV 订阅（如合并单元）
16. 时间同步（IEEE 1588）
```

## IED（Server / RTU）实现要点

```text
1. SCL 解析（ICD / CID）
3. 构建 LD / LN / DO 树
5. MMS Initiate 服务
7. GetNameList 服务
9. Read / Write 服务
12. InformationReport 服务
13. 报告控制块 BRCB / URCB 实现
14. Select / Operate 处理
15. GOOSE 发布（如保护 IED）
16. SV 发布（如合并单元）
17. 时间同步（IEEE 1588）
18. 数据采集 → 上报
19. 一致性测试支持
```

## 抓包排障

Wireshark IEC 61850 dissector：

```text
1. TCP MMS 流量（MMS 端口 102）
3. BER 解码
5. Initiate / Read / Write / InformationReport
7. GOOSE 帧（多播，0x88B8）
9. SV 帧（多播，0x88BA）
```

工程排障清单：

```text
1. MMS Initiate 失败
3. GetNameList 无响应
5. Read 失败（引用路径错）
7. Write 失败（权限 / 保护）
9. InformationReport 不触发
11. 控制链失败
13. GOOSE 不通
15. SV 不通
17. 时间不同步
19. 一致性测试失败
```

## 现场常见故障

| 现象 | 优先检查 |
| --- | --- |
| MMS Initiate 失败 | TCP / Initiate 参数 |
| GetNameList 无响应 | Domain / Object class |
| Read 失败 | 引用路径 |
| Write 失败 | 权限 |
| InformationReport 不触发 | BRCB / URCB 配置 |
| Select 失败 | 控制模型 |
| Operate 失败 | Select 超时 |
| GOOSE 不通 | 多播 / APPID |
| SV 不通 | 多播 / 同步 |
| 时间不同步 | IEEE 1588 |

## 深度检查清单

- MMS TCP 端口 102 已开。
- MMS Initiate 服务已实现。
- GetNameList / Read / Write 已支持。
- InformationReport 订阅支持。
- 命令 Select / Operate 流程完整。
- 报告控制块 BRCB / URCB 配置。
- 数据集 DataSet 定义。
- 触发选项支持（dchg / qchg / integrity）。
- GOOSE 多播发布 / 订阅。
- SV 多播发布 / 订阅。
- SCL 文件解析（ICD / CID / SCD）。
- 时间同步（IEEE 1588 PTP）。
- 一致性测试（A / B / C 级）。
- 多 IED 管理。
- 网络冗余（PRP / HSR）。
- 网络安全（防火墙 / VLAN）。
- 多客户端支持（如 SCADA + 监控）。
- 性能优化（变位 → 接收 < 4 ms）。