---
tags:
  - layer/bus
  - type/failure-cases
  - protocol/bacnet
  - topic/power-rtu
---

# BACnet 产线死机案例库

## 目标

把产线常见的 BACnet 楼宇通信失败、UDP / MS/TP、COV、BBMD 等写成案例库。

## 案例 1：UDP 端口未开

### 现象

BACS 完全连不上 IED。

### 修复

防火墙放行 UDP 47808。

## 案例 2：BVLC 编码错

### 修复

BVLC Type / Function 编码纠正。

## 案例 3：NPDU 编码错

### 修复

NPDU Version / Control 编码纠正。

## 案例 4：APDU 编码错

### 修复

APDU PDU Type / Invoke ID 编码纠正。

## 案例 5：Object Identifier 编码错

### 现象

BACS Read AI 1 失败。

### 修复

Object Identifier Tag + Length + Value 编码纠正。

## 案例 6：Property Identifier 错

### 修复

Property Identifier 编码纠正。

## 案例 7：COV 不触发

### 现象

订阅 COV 但变位不通知。

### 修复

COV_Increment / 触发条件检查。

## 案例 8：COV 订阅超时

### 现象

COV Lifetime 超时。

### 修复

定期续订。

## 案例 9：ReadPropertyMultiple 错

### 修复

ReadPropertyMultiple 编码纠正。

## 案例 10：WriteProperty 权限失败

### 修复

权限 / 写保护检查。

## 案例 11：MS/TP 令牌环冲突

### 修复

令牌环节点地址 / 波特率纠正。

## 案例 12：MS/TP CRC8 错

### 修复

CRC8 计算纠正。

## 案例 13：BBMD 注册失败

### 修复

Foreign Device 注册 TTL 调整。

## 案例 14：BBMD BDT 配置错

### 修复

Broadcast Distribution Table 配置纠正。

## 案例 15：Who-Is 无响应

### 修复

设备支持 / 网络检查。

## 案例 16：Schedule 不触发

### 修复

Schedule 配置纠正。

## 案例 17：Trend Log 不记录

### 修复

Trend Log Buffer / Stop_When_Full 配置。

## 案例 18：Device Object 不完整

### 修复

Device Object 属性完整化。

## 案例 19：跨子网不通

### 修复

BBMD / 二层网络配置。

## 案例 20：性能问题

### 现象

数据量大时延迟高。

### 修复

COV 订阅 + 分页读取。