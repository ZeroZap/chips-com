# Coverage Report

## 目标

本文记录当前芯片间通信知识库的覆盖范围和后续可扩展方向。

## 已覆盖主线

基础外设：

- GPIO
- PWM
- ADC/DAC
- Comparator
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
- CAN 协议全景汇总
- CAN 标准规范总表
- CANopen
- CANopen Failure Cases
- CANopen Safety
- J1939
- J1939 Practical
- J1939 Deep Dive
- UDS
- UDS Practical
- UDS Deep Dive
- UDS Failure Cases
- ISO-TP
- ISO-TP Practical
- ISO-TP Deep Dive
- ISO-TP Failure Cases
- OBD-II
- OBD-II Deep Dive
- OBD-II Practical
- OBD-II Failure Cases
- WWH-OBD
- WWH-OBD Deep Dive
- WWH-OBD Practical
- WWH-OBD Failure Cases
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

电力 / 水务 / 表计 / 楼宇：

- IEC 60870-5-104
- IEC 60870-5-101
- IEC 61850
- DNP3
- SL 651-2014
- SZY 206-2016
- SL/T 427
- HJ 212-2017
- DL/T 645
- CJ/T 188
- BACnet
- OPC UA
- RTU 网关设计
- RTU 协议厂商对标

无线 / IoT / 卫星：

- BLE
- ZigBee
- Matter
- Thread
- LoRa / LoRaWAN
- LTE-IoT / NB-IoT
- Satellite-IoT
- PLB
- Rescue-Communications
- nRF2401

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
- 标准与规范索引
- 缩写表与术语表
- 工具与测量指南
- 文档模板与评审清单

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

当前知识库规模：

```text
知识库文档：313 篇（basic 44 + bus 234 + guides 29 + reference 6）
总体量：约 3.3 MB
索引主题：34 个
5 分主题：31 个（19 个核心 L4 + 12 个行业闭环）
```

当前知识库已具备：

- 从入门到深入的阅读路径。
- 单协议实战文档和故障案例。
- 跨协议选型、排障和工程治理方法。
- 电力、水务、表计、楼宇和无线 IoT 的协议闭环。
- 场景化、设备化和主题化索引。
- 参考层：缩写、术语、标准、工具和文档模板。

## 当前主要缺口

- `basic/` 的 10 个基础主题已升级到 L2，仍需补真实案例、波形和量产数据。
- 比较器已补独立文档，后续补阈值精度与响应案例。
- `guides/learning/` 已补汽车诊断、电力 RTU、无线 IoT、工业以太网与 TSN 的对比/选型/场景/设备/参数表；实验卡仍需细化。
- `guides/troubleshooting/` 已补 BLE、LoRaWAN、IEC 104、DNP3、CANopen、J1939、Modbus TCP、EtherCAT 案例；仍需更多现场证据。
- 图片和真实测量截图仍偏少；新增文档时需要同步维护 frontmatter / tags。

后续重点应从“覆盖更多协议”转为：

```text
增加实例
增加图示
增加测试方法
增加真实故障案例
统一元数据与互链
```
