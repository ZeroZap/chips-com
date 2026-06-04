# Ethernet

## 定位

Ethernet 是现代网络通信的基础链路层技术，常承载 IP、TCP、UDP、HTTP、MQTT、Modbus TCP 和工业以太网协议。

## 分层关系

```text
应用层：HTTP / MQTT / Modbus TCP
传输层：TCP / UDP
网络层：IP
链路层：Ethernet
物理层：PHY / 网线
```

## MAC 和 PHY

`MAC` 负责以太网帧。

`PHY` 负责物理信号。

典型结构：

```text
MCU/SoC MAC <-> PHY <-> RJ45
```

## 常见概念

- MAC 地址。
- Ethernet Frame。
- ARP。
- IP 地址。
- TCP 字节流。
- UDP 数据报。
- 交换机。

## 延伸阅读

- `basic/ethernet-phy.md`
- `bus/ethernet-deep-dive.md`
- `bus/ethernet-modbus-tcp-practical.md`
