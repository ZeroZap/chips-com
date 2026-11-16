---
tags:
  - layer/bus
  - type/failure-cases
  - protocol/iec61850
  - topic/power-rtu
---

# IEC 61850 产线死机案例库

## 目标

把产线常见的 IEC 61850 通信失败、MMS BER 解析错、SCL 配置错、GOOSE/SV 性能问题、命令链错等写成案例库。

## 案例 1：MMS Initiate 失败

### 现象

Client 连接 IED → 无 Initiate Response。

### 排查

```text
Client：Initiate Request（最大 PDU = 65000）
Server：拒绝（仅支持 1500）
```

### 修复

Client Initiate 最大 PDU 改为 1500。

### 复盘

```text
1. MMS Initiate 必须协商最大 PDU
2. IED 端默认 PDU 较小
3. 测试用例必须验证 Initiate
```

## 案例 2：BER 解析错

### 现象

Client Read Response，BER 解析错。

### 排查

```text
Server BER 编码：Tag 0xA4
Client BER 解析：错
```

### 修复

Client BER 解码实现纠正。

### 复盘

```text
1. MMS PDU 使用 ASN.1 BER
2. BER 解析必须按 Tag + Length + Value
3. 测试用例必须验证 BER
```

## 案例 3：SCL 文件解析错

### 现象

IED 端启动失败，找不到 LD。

### 排查

```text
SCL 文件：ICD
解析：未实例化
```

### 修复

IED 解析 CID 文件（实例化）。

### 复盘

```text
1. IED 启动必须解析 CID
2. ICD 是厂家提供，CID 是系统集成商提供
3. 测试用例必须验证 SCL
```

## 案例 4：LN / DO 引用路径错

### 现象

Client Read XCBR1.Pos.stVal 失败。

### 排查

```text
Client：LD0/XCBR1.Pos.stVal
IED：LD1/XCBR1.Pos.stVal
```

### 修复

引用路径纠正。

### 复盘

```text
1. LN / DO 引用路径必须精确
2. 测试用例必须验证引用路径
```

## 案例 5：MMS Read 失败（权限）

### 现象

Client Read 失败，StatusCode = BadAccessDenied。

### 排查

```text
Client：尝试写 Read Only 属性
```

### 修复

Client 改为读可访问属性。

### 复盘

```text
1. MMS 属性有访问权限
2. 测试用例必须验证权限
```

## 案例 6：BRCB 启用失败

### 现象

Client SetBRCBValues 失败。

### 排查

```text
Client：BRCB RptEna = 1
IED：BRCB 已被其他 Client 占用
```

### 修复

禁用其他 Client 的 BRCB。

### 复盘

```text
1. BRCB 是 exclusive 资源
2. 测试用例必须验证 BRCB
```

## 案例 7：InformationReport 不触发

### 现象

Client 订阅 BRCB，IED 变位但不上报。

### 排查

```text
Client：BRCB 配置 OK
IED：BRCB 数据集为空
```

### 修复

IED 配置数据集。

### 复盘

```text
1. BRCB 必须配置数据集
2. 数据集 + 触发选项 + BRCB
3. 测试用例必须验证
```

## 案例 8：命令链 Select 失败

### 现象

Client Select XCBR1.Pos，IED 拒绝。

### 排查

```text
Client：Select + ctlVal = 1
IED：ctlModel = Direct（非 SBO）
```

### 修复

Client 改为 Direct Operate。

### 复盘

```text
1. IED 必须支持 ctlModel 类型
2. Direct / SBO / EnhancedSecurity
3. 测试用例必须验证控制模型
```

## 案例 9：Operate 失败（Select 超时）

### 现象

Client Select → 5 min → IED Select 超时。

### 排查

```text
Client：Select OK 后延迟 5 min 发 Operate
IED：Select 超时 2 min
```

### 修复

Client Select 后立即 Operate。

### 复盘

```text
1. Select 超时通常 2-30 min
2. Client 必须立即 Operate
3. 测试用例必须验证 Select 超时
```

## 案例 10：GOOSE 多播不通

### 现象

保护 Client 收不到 GOOSE 帧。

### 排查

```text
GOOSE 目标 MAC：01-0C-CD-01-00-01
Client：网卡未加入多播组
```

### 修复

Client 网卡加入多播组。

### 复盘

```text
1. GOOSE 是多播
2. Client 必须加入多播组
3. 工程实践：交换机 IGMP Snooping
```

## 案例 11：GOOSE 变位延迟

### 现象

GOOSE 变位 → Client 接收延迟 > 100 ms。

### 排查

```text
IED → 交换机 → Client
交换机配置：阻塞多播
```

### 修复

交换机配置放行 GOOSE 多播。

### 复盘

```text
1. GOOSE 延迟要求 < 4 ms
2. 交换机必须放行多播
3. 测试用例必须验证延迟
```

## 案例 12：SV 不同步

### 现象

MU 发 SV，IED 接收但采样值不同步。

### 排查

```text
MU → IED
未同步（无 PTP）
```

### 修复

启用 PTP 同步。

### 复盘

```text
1. SV 必须同步（IEEE 1588）
2. PTP 精度 1 μs
3. 测试用例必须验证同步
```

## 案例 13：SCL ICD / CID / SCD 混淆

### 现象

系统集成商把 ICD 部署到 IED，IED 启动失败。

### 修复

部署 CID 而非 ICD。

### 复盘

```text
1. ICD 是能力描述，CID 是实例化配置
2. 部署必须用 CID
3. 测试用例必须验证
```

## 案例 14：配置文件版本不匹配

### 现象

IED 配置 confRev = 1，Client 配置 confRev = 2。

### 修复

IED / Client 配置版本一致。

### 复盘

```text
1. confRev 必须一致
2. GOOSE / SV 控制块用 confRev 验证
3. 测试用例必须验证 confRev
```

## 案例 15：性能问题（数据量大）

### 现象

IED 数据集 1000 个 DO，Client Read 延迟 > 10s。

### 修复

拆分数据集 / 使用 Report。

### 复盘

```text
1. 大数据集用 Report 而非 Read
2. Read 适合小数据集
3. 测试用例必须验证性能
```

## 案例 16：Report 不停止

### 现象

Client 取消 BRCB 订阅，IED 仍继续发。

### 排查

```text
Client：DeleteSubscription
IED：未实现
```

### 修复

IED 实现 DeleteSubscription。

### 复盘

```text
1. DeleteSubscription 必须实现
2. 测试用例必须验证清理
```

## 案例 17：File Transfer 失败

### 现象

Client GetFile 失败。

### 排查

```text
Client：File Open + Read
IED：未实现 File Open
```

### 修复

IED 实现文件传输。

### 复盘

```text
1. IEC 61850 文件传输是基础
2. 测试用例必须验证 File
```

## 案例 18：时间同步失败

### 现象

IED 时钟不同步，影响事件记录。

### 修复

启用 IEEE 1588 PTP。

### 复盘

```text
1. IEC 61850 时间同步关键
2. PTP 是首选
3. 测试用例必须验证时间同步
```

## 案例 19：MMS 连接断开

### 现象

Client TCP 连接断开。

### 排查

```text
Client：Initiate → Read → TCP 断
```

### 修复

Client 实现自动重连。

### 复盘

```text
1. MMS TCP 连接必须自动重连
2. 测试用例必须验证断线恢复
```

## 案例 20：一致性测试失败

### 现象

IED 通过 DNV KEMA 测试时某些用例失败。

### 修复

修正 IED 实现，通过所有用例。

### 复盘

```text
1. 一致性测试是项目验收必要
2. 测试报告是 IEC 61850 项目要求
3. 测试用例必须覆盖 PICS / PIXIT
```