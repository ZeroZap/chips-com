# EtherNet/IP

## 定位

EtherNet/IP 是工业以太网协议，常见于 Rockwell / Allen-Bradley 生态。

这里的 IP 是 Industrial Protocol，不是 Internet Protocol 的缩写。

EtherNet/IP 基于 CIP，Common Industrial Protocol。

## 常见场景

- PLC 与远程 IO。
- 变频器。
- 执行器。
- 传感器。
- 工业控制器。

## 核心概念

- CIP 对象模型。
- 显式消息 Explicit Messaging。
- 隐式 IO Implicit Messaging。
- TCP/UDP/IP。
- EDS 设备描述文件。

## 显式和隐式消息

显式消息：

```text
配置、诊断、低频访问
```

隐式 IO：

```text
周期实时 IO 数据
```

## 与 Modbus TCP 对比

Modbus TCP：

```text
寄存器模型，简单直接
```

EtherNet/IP：

```text
CIP 对象模型，生态和设备模型更复杂
```

## 工程注意

- 通常需要协议栈。
- 需要 EDS 文件。
- 要考虑连接资源和 RPI。
- 工业项目常涉及一致性和认证。

## 延伸阅读

- `bus/industrial-ethernet-comparison.md`
- `bus/ethernet-deep-dive.md`
