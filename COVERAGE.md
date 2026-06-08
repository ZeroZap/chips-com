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
- J1939
- UDS
- ISO-TP
- LIN
- EtherCAT
- PROFIBUS
- DMX512
- PROFINET
- EtherNet/IP
- 工业以太网对比

通用外设和高速互联：

- USB
- USB Deep Dive
- USB DFU
- Ethernet
- Ethernet TSN
- MQTT
- PCIe

图像和显示：

- MIPI CSI/DSI
- LVDS
- FPD-Link/GMSL
- HDMI/eDP
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

- 为 `PROFINET`、`EtherNet/IP`、`J1939`、`UDS` 增加 practical/deep-dive 文档。
- 为 `FPD-Link/GMSL` 增加调试案例和链路预算说明。

中期补充：

- 为 `PROFIBUS`、`DMX512`、`HDMI/eDP` 增加 practical 文档和调试案例。
- 为 `USB DFU`、`ISO-TP`、`MQTT` 增加 deep-dive 文档。

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
