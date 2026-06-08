# PROFINET

## 定位

PROFINET 是工业以太网协议，常见于西门子 PLC 和自动化系统生态。

它不是简单 TCP 应用协议，而是面向工业设备发现、组态、周期 IO、诊断和实时通信的完整体系。

## 常见场景

- PLC 与远程 IO。
- 变频器。
- 伺服驱动。
- 工业机器人。
- 产线自动化。

## 核心概念

- 设备发现。
- 设备命名。
- 工程组态。
- 周期 IO 数据。
- 诊断。
- 实时通信。
- GSDML 设备描述文件。

## 实时等级

PROFINET 有不同实时能力，普通入门先理解：

```text
普通 TCP/IP 通信
RT 实时通信
IRT 高同步实时通信
```

具体能力取决于设备和协议栈。

## 与 Modbus TCP 对比

Modbus TCP 更简单，像寄存器读写。

PROFINET 更像自动化设备体系，包含设备模型、组态和诊断。

## 工程注意

- 通常需要协议栈和认证。
- 需要 GSDML。
- 需要配合 PLC 工程工具。
- 实时能力依赖硬件和栈支持。

## 延伸阅读

- `bus/industrial-ethernet-comparison.md`
- `bus/ethernet-deep-dive.md`
