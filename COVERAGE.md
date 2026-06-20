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
- J1939 Practical
- J1939 Deep Dive
- UDS
- UDS Practical
- UDS Deep Dive
- ISO-TP
- ISO-TP Practical
- ISO-TP Deep Dive
- LIN
- EtherCAT
- PROFIBUS
- PROFIBUS Practical
- DMX512
- DMX512 Practical
- PROFINET
- PROFINET Practical
- PROFINET Deep Dive
- EtherNet/IP
- EtherNet/IP Practical
- EtherNet/IP Deep Dive
- 工业以太网对比

通用外设和高速互联：

- USB
- USB Deep Dive
- USB DFU
- USB DFU Practical
- USB DFU Deep Dive
- Ethernet
- Ethernet TSN
- Ethernet TSN Practical
- MQTT
- MQTT Practical
- MQTT Deep Dive
- PCIe

图像和显示：

- MIPI CSI/DSI
- LVDS
- FPD-Link/GMSL
- FPD-Link/GMSL Practical
- HDMI/eDP
- HDMI/eDP Practical
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

- 为 `PROFIBUS`、`DMX512`、`HDMI/eDP` 增加 deep-dive 文档和真实调试案例。

中期补充：

- 为 `FPD-Link/GMSL` 增加更完整的链路预算、同轴/双绞线选型和多摄同步案例。

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
