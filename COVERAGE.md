# Coverage Report

## 目标

本文记录当前芯片间通信知识库的覆盖范围和后续可扩展方向。

## 已覆盖主线

基础外设：

- GPIO
- PWM
- ADC/DAC
- UART
- I2C
- SPI
- I2S
- QSPI/OSPI
- JTAG/SWD

基础物理层：

- RS232/RS485
- CAN PHY
- Ethernet PHY
- LVDS

板内和管理总线：

- I3C
- SMBus
- PMBus
- SDIO
- 1-Wire

工业和车载：

- Modbus RTU
- Modbus TCP
- CAN
- CANopen
- LIN
- EtherCAT
- 工业以太网对比

通用外设和高速互联：

- USB
- Ethernet
- PCIe

图像和显示：

- MIPI CSI/DSI
- LVDS
- 显示接口概览

工程方法：

- 学习计划
- 协议选型矩阵
- 分层图谱
- 调试工具指南
- 故障速查
- 实验路线
- 文档模板
- 评审清单
- 场景和设备示例

## 后续可扩展方向

短期补充：

- `bus/usb-deep-dive.md`：更深入的 USB 描述符、复合设备、CDC/HID/MSC 细节。
- `bus/modbus-tcp-deep-dive.md`：Modbus TCP 连接管理、并发客户端、网关转换。
- `bus/ethernet-ip.md`：EtherNet/IP 和 CIP 入门。
- `bus/profinet.md`：PROFINET 入门和工程组态概念。

中期补充：

- `bus/j1939.md`：商用车 CAN 上层协议。
- `bus/uds.md`：车载诊断 UDS。
- `bus/ethernet-tsn.md`：TSN 时间敏感网络。
- `bus/fpd-link-gmsl.md`：车载摄像头高速串行链路。

长期补充：

- 每个协议对应最小实验代码或伪代码。
- 每个协议对应示波器/逻辑分析仪截图说明。
- 典型原理图检查清单。
- 典型驱动状态机模板。

## 当前质量状态

当前知识库已具备：

- 从入门到深入的阅读路径。
- 单协议实战文档。
- 跨协议选型和排障方法。
- 场景化和设备化索引。
- 后续贡献模板。

后续重点应从“覆盖更多协议”转为：

```text
增加实例
增加图示
增加测试方法
增加真实故障案例
```
