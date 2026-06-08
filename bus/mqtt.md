# MQTT

## 定位

MQTT 是轻量级发布/订阅消息协议，常用于 IoT 设备和云平台通信。

它通常运行在 TCP 之上，也可配合 TLS。

## 核心概念

- Broker。
- Client。
- Topic。
- Publish。
- Subscribe。
- QoS。
- Retained Message。
- Last Will。

## QoS

```text
QoS 0：最多一次
QoS 1：至少一次
QoS 2：只有一次
```

嵌入式设备常用 QoS 0 或 QoS 1。

## 常见场景

- 设备遥测。
- 状态上报。
- 云端命令下发。
- 网关汇聚数据。
- 远程配置。

## 工程注意

- 断线重连。
- 心跳 keepalive。
- Topic 设计。
- QoS 和缓存策略。
- TLS 证书和时间同步。
- 网络不稳定下的数据补发。

## 与 Modbus TCP 对比

Modbus TCP 偏工业寄存器读写。

MQTT 偏云端消息发布/订阅。

二者可在网关中共存：

```text
现场 Modbus -> 网关 -> MQTT 上云
```

## 延伸阅读

- `bus/ethernet-deep-dive.md`
- `APPLICATION_SCENARIOS.md`
