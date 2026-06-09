# MQTT Practical Guide

## 目标

本文用于 MQTT 嵌入式工程实践，重点覆盖 Broker、Topic、QoS、Keepalive、断线重连、TLS、离线缓存和网关场景。

## 基本结构

```text
Device Client <-> Broker <-> Cloud/Application Client
```

设备发布数据到 Topic，也可订阅命令 Topic。

## Topic 设计

建议包含层级：

```text
product/{product_id}/device/{device_id}/telemetry
product/{product_id}/device/{device_id}/command
product/{product_id}/device/{device_id}/status
```

Topic 要避免过度随意，否则后期难以维护权限和路由。

## QoS 选择

```text
QoS 0：低延迟，允许丢
QoS 1：至少一次，可能重复
QoS 2：只有一次，开销最大
```

嵌入式常用 QoS 0 或 QoS 1。

QoS 1 业务层要能处理重复消息。

## Keepalive

Keepalive 用于检测连接是否存活。

要考虑：

- 蜂窝网络延迟。
- NAT 超时。
- 低功耗睡眠。
- Broker 配置。

## 断线重连

推荐策略：

- 指数退避。
- 最大重连间隔。
- 网络恢复后重新订阅。
- 清理旧 session。
- 记录断线原因。

## TLS

使用 TLS 时注意：

- 证书存储。
- 设备时间同步。
- 根证书更新。
- RAM 占用。
- 握手耗时。

## 网关场景

常见：

```text
Modbus/CAN/RS485 现场设备 -> 网关 -> MQTT 上云
```

网关要处理：

- 本地轮询。
- 数据缓存。
- 云端断线。
- 命令下发映射。
- 设备影子或状态同步。

## 常见故障

| 现象 | 优先检查 |
| --- | --- |
| 连不上 Broker | DNS、端口、认证、TLS、网络 |
| 频繁掉线 | Keepalive、NAT、信号、Broker 限制 |
| 命令收不到 | Topic、订阅、权限、session |
| 数据重复 | QoS 1、重传、业务去重 |
| TLS 失败 | 时间、证书、SNI、CA |

## 检查清单

- Client ID 唯一。
- Topic 命名规范。
- QoS 与业务匹配。
- Keepalive 合理。
- 断线重连和重新订阅完整。
- TLS 证书和时间同步正确。
- 离线缓存策略明确。
