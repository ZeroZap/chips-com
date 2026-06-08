# PROFIBUS

## 定位

PROFIBUS 是经典工业现场总线，常见于过程自动化、工厂自动化和西门子生态的早期工业系统。

常见类型：

```text
PROFIBUS DP：分布式 IO，工厂自动化常见
PROFIBUS PA：过程自动化，仪表场景常见
```

## 核心特点

- 主从通信。
- 工业现场使用成熟。
- 设备描述文件支持工程组态。
- PROFIBUS DP 常基于 RS485 物理层。
- PROFIBUS PA 面向过程仪表和本安场景。

## 常见场景

- PLC 与远程 IO。
- 变频器。
- 过程仪表。
- 传统自动化产线。
- 存量工业系统维护。

## 与 PROFINET 的关系

PROFIBUS 是传统现场总线。

PROFINET 是工业以太网体系。

新项目更多会选择 PROFINET，但大量存量设备仍使用 PROFIBUS。

## 工程注意

- 需要专用协议栈或通信模块。
- 需要按拓扑和终端规范布线。
- 设备地址和组态必须一致。
- 存量项目常关注兼容和替换。

## 延伸阅读

- `bus/profinet.md`
- `bus/industrial-ethernet-comparison.md`
