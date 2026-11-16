---
tags:
  - layer/bus
  - type/failure-cases
  - protocol/opcua
  - topic/industrial
---

# OPC UA 产线死机案例库

## 目标

把产线常见的 OPC UA 工业通信失败、安全策略、订阅机制、信息建模等写成案例库。

## 案例 1：TCP 端口未开

### 修复

防火墙放行 4840。

## 案例 2：安全策略协商失败

### 修复

GetEndpoints 选择合适策略。

## 案例 3：证书无效

### 修复

证书更新 / CA 信任链。

## 案例 4：用户认证失败

### 修复

认证方式（Anonymous / UsernamePassword / Certificate）纠正。

## 案例 5：地址空间浏览失败

### 修复

Browse 引用 / NodeClassMask 调整。

## 案例 6：Read 失败（权限）

### 修复

权限检查。

## 案例 7：Write 失败

### 修复

写权限检查。

## 案例 8：Call 方法失败

### 修复

方法调用参数纠正。

## 案例 9：CreateSubscription 失败

### 修复

Subscription 参数协商。

## 案例 10：AddMonitoredItems 失败

### 修复

SamplingInterval / QueueSize 调整。

## 案例 11：Publish 不通

### 修复

SubscriptionAck 处理。

## 案例 12：HistoryRead 失败

### 修复

节点历史支持检查。

## 案例 13：NodeId 编码错

### 修复

NodeId 编码纠正。

## 案例 14：Variant 解码错

### 修复

Variant 编码纠正。

## 案例 15：时间同步错

### 修复

UTC 时间统一。

## 案例 16：反向 OPC UA Server 失败

### 修复

反向连接状态管理。

## 案例 17：证书过期

### 修复

证书定期更新。

## 案例 18：性能问题

### 修复

MonitoredItems + Publish 频率优化。

## 案例 19：Companion Specs 缺失

### 修复

行业 Companion Specifications 实现。

## 案例 20：跨平台兼容性

### 修复

多种二进制 / JSON 编码兼容。