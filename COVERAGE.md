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
- PROFIBUS Deep Dive
- DMX512
- DMX512 Practical
- DMX512 Deep Dive
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
- FPD-Link/GMSL Deep Dive
- HDMI/eDP
- HDMI/eDP Practical
- HDMI/eDP Deep Dive
- 显示接口概览

工程方法：

- 学习计划
- 协议选型矩阵
- 分层图谱
- 调试工具指南
- 测量样例
- 故障速查
- 实验路线
- 文档模板
- 评审清单
- 回归测试矩阵
- 自动化测试治具
- 通信可观测性
- 发布质量门禁
- 现场诊断运行手册
- 通信追踪矩阵
- 通信安全与失效安全
- 场景和设备示例

## 后续可扩展方向

短期补充：

- 为高风险协议补充可复查的测量样例、真实故障案例和寄存器/抓包证据。

中期补充：

- 每个高风险现场协议增加真实调试案例。

长期补充：

- 每个协议对应最小实验代码或伪代码。
- 每个协议对应示波器/逻辑分析仪截图说明。
- 每个高风险协议对应自动化回归测试矩阵。
- 每个核心协议对应可执行测试治具 adapter。
- 每个现场协议对应状态、计数器、快照和远程诊断接口。
- 每个高风险发布项对应质量门禁和风险接受记录。
- 每个现场故障对应诊断包、复现用例和关闭标准。
- 每个 R3/R4 风险对应需求、设计、测试、观测和门禁追踪。
- 每个敏感通信链路对应权限、安全日志、回滚和失效安全策略。
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
