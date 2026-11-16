---
tags:
  - moc
  - navigation
aliases:
  - 知识库首页
  - Dashboard
---

# Chips Communication · 知识库

面向芯片间通信的知识库：从 GPIO / UART / I2C / SPI 等基础接口，到 CAN、Modbus、工业以太网、无线与车载诊断。

> [!tip] 图形导航
> 打开 [[Navigation.canvas|Navigation 画布]] 按分区浏览全部主题。
> 本页是文字版入口，适合移动端、全局搜索和双链跳转。

## 快速入口

| 区域     | 入口                                                                                                                  |
| -------- | --------------------------------------------------------------------------------------------------------------------- |
| 基础接口 | [[basic/README\|基础接口总览]]                                                                                        |
| 总线协议 | [[bus/README\|总线协议总览]]                                                                                          |
| 完整索引 | [[INDEX\|知识库索引]]                                                                                                 |
| 分层图谱 | [[LAYERED_MAP\|分层图谱]]                                                                                             |
| 学习路径 | [[guides/learning/LEARNING_PLAN\|阶段化学习计划]] · [[guides/learning/READING_PATHS\|按目标阅读]]                     |
| 排障     | [[guides/troubleshooting/DEBUG_PLAYBOOK\|跨协议排障]] · [[guides/troubleshooting/TROUBLESHOOTING_QUICKREF\|故障速查]] |
| 选型     | [[guides/learning/PROTOCOL_SELECTION\|选型矩阵]] · [[guides/learning/PROTOCOL_COMPARISON\|协议对照]]                  |

## ① 基础接口 `basic/`

| 主题                 | 入口笔记                                                                                                                                                                               |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 总览                 | [[basic/README\|基础接口总览]]                                                                                                                                                         |
| GPIO / PWM / ADC-DAC | [[basic/gpio\|GPIO]] · [[basic/pwm\|PWM]] · [[basic/adc-dac\|ADC/DAC]]                                                                                                                 |
| UART                 | [[basic/uart-index\|UART 导航]] · [[basic/uart-practical\|实战]] · [[basic/uart-deep-dive\|深入]] · [[basic/uart-failure-cases\|故障案例]]                                             |
| UART 进阶            | [[basic/uart-rs485-and-flow-control\|RS485 与流控]] · [[basic/uart-dma-circular-and-rtos\|DMA 环形缓冲]]                                                                               |
| I2C                  | [[basic/i2c-index\|I2C 导航]] · [[basic/i2c-practical\|实战]] · [[basic/i2c-deep-dive\|深入]] · [[basic/i2c-failure-cases\|故障案例]]                                                  |
| I2C 恢复             | [[basic/i2c-bus-recovery-playbook\|总线恢复手册]] · [[basic/i2c-multimaster\|多主仲裁]] · [[basic/i2c-smbus-timeout\|SMBus 超时]]                                                      |
| SPI                  | [[basic/spi-index\|SPI 导航]] · [[basic/spi-practical\|实战]] · [[basic/spi-deep-dive\|深入]] · [[basic/spi-multislave-and-dma\|多从机与 DMA]] · [[basic/spi-failure-cases\|故障案例]] |
| CAN PHY              | [[basic/can-index\|CAN 导航]] · [[basic/can-phy\|CAN PHY]] · [[basic/can-practical\|实战]] · [[basic/can-fd-and-can-xl\|CAN FD / XL]] · [[basic/can-failure-cases\|故障案例]]          |
| 差分与物理层         | [[basic/rs232-rs485\|RS232/RS485]] · [[basic/can-phy\|CAN PHY]] · [[basic/ethernet-phy\|以太网 PHY]] · [[basic/lvds\|LVDS]]                                                            |
| 高速与调试           | [[basic/qspi-ospi\|QSPI/OSPI]] · [[basic/i2s\|I2S]] · [[basic/jtag-swd\|JTAG/SWD]]                                                                                                     |
| 流式解析             | [[basic/stream-protocol-parser-psm\|流式协议解析器 PSM]]                                                                                                                               |

## ② 总线协议 `bus/`

### 工业与以太网

| 主题                | 入口笔记                                                                                                                                                                   |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Modbus              | [[bus/industrial/modbus\|Modbus]] · [[bus/industrial/rs485-modbus-rtu-practical\|RS485/RTU 实战]] · [[bus/industrial/modbus-tcp-deep-dive\|Modbus TCP 深入]]               |
| PROFIBUS / PROFINET | [[bus/industrial/profibus\|PROFIBUS]] · [[bus/industrial/profinet\|PROFINET]]                                                                                              |
| EtherCAT            | [[bus/industrial/ethercat-deep-dive\|EtherCAT 深入]]                                                                                                                       |
| EtherNet/IP         | [[bus/industrial/ethernet-ip-practical\|EtherNet/IP 实战]] · [[bus/industrial/ethernet-ip-deep-dive\|深入]]                                                                |
| TSN                 | [[bus/industrial/ethernet-tsn\|TSN]] · [[bus/industrial/ethernet-tsn-practical\|TSN 实战]]                                                                                 |
| 工业以太网对比      | [[bus/industrial/industrial-ethernet-comparison\|对比矩阵]]                                                                                                                |
| OPC UA / MQTT       | [[bus/industrial/opcua\|OPC UA]] · [[bus/industrial/mqtt\|MQTT]]                                                                                                           |
| 板内与管理总线      | [[bus/onboard/i3c\|I3C]] · [[bus/onboard/smbus\|SMBus]] · [[bus/onboard/pmbus\|PMBus]] · [[bus/onboard/sdio-practical\|SDIO]] · [[bus/onboard/one-wire-practical\|1-Wire]] |
| 其他                | [[bus/industrial/dmx512\|DMX512]] · [[bus/onboard/pcie-practical\|PCIe]]                                                                                                   |

### 电力 / 水利 / 表计 / 楼宇

| 主题         | 入口笔记                                                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| RTU 协议总览 | [[bus/power-rtu/rtu-protocols\|RTU 协议全集]] · [[bus/power-rtu/rtu-gateway-design\|RTU 网关设计]]                                         |
| IEC 60870    | [[bus/power-rtu/iec104\|IEC 104]] · [[bus/power-rtu/iec101\|IEC 101]]                                                                      |
| DNP3         | [[bus/power-rtu/dnp3\|DNP3]]                                                                                                               |
| IEC 61850    | [[bus/power-rtu/iec61850\|IEC 61850]]                                                                                                      |
| 水利 / 环保  | [[bus/power-rtu/sl651\|SL 651]] · [[bus/power-rtu/szy206\|SZY 206]] · [[bus/power-rtu/slt427\|SL/T 427]] · [[bus/power-rtu/hj212\|HJ 212]] |
| 表计 / 楼宇  | [[bus/power-rtu/dlt645\|DL/T 645]] · [[bus/power-rtu/cjt188\|CJ/T 188]] · [[bus/power-rtu/bacnet\|BACnet]]                                 |

### 车载与诊断

| 主题           | 入口笔记                                                                                                                                                                            |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CAN 家族       | [[bus/automotive/can-protocol-family\|CAN 家族全景]] · [[bus/automotive/can-standards-map\|CAN 标准总表]]                                                                           |
| CAN / CANopen  | [[bus/automotive/can\|CAN]] · [[bus/automotive/canopen\|CANopen]] · [[bus/automotive/canopen-safety\|CANopen Safety]]                                                               |
| J1939          | [[bus/automotive/j1939-index\|J1939 导航]] · [[bus/automotive/j1939-protocol-spec\|J1939 规范]]                                                                                     |
| ISO-TP         | [[bus/automotive/iso-tp\|ISO-TP]] · [[bus/automotive/iso-tp-practical\|实战]] · [[bus/automotive/iso-tp-failure-cases\|故障案例]]                                                   |
| UDS            | [[bus/automotive/uds\|UDS]] · [[bus/automotive/uds-practical\|实战]] · [[bus/automotive/uds-deep-dive\|深入]] · [[bus/automotive/uds-failure-cases\|故障案例]]                      |
| OBD            | [[bus/automotive/obd2\|OBD-II]] · [[bus/automotive/wwh-obd\|WWH-OBD]]                                                                                                               |
| LIN            | [[bus/automotive/lin\|LIN]]                                                                                                                                                         |
| 车载视频与显示 | [[bus/display/fpd-link-gmsl\|FPD-Link/GMSL]] · [[bus/display/hdmi-edp\|HDMI/eDP]] · [[bus/display/display-interfaces\|显示接口]] · [[bus/display/mipi-csi-dsi-debug\|MIPI CSI/DSI]] |

### USB

| 主题       | 入口笔记                                                                                          |
| ---------- | ------------------------------------------------------------------------------------------------- |
| USB 总览   | [[bus/usb/usb-index\|USB 导航]] · [[bus/usb/usb-vs-other-bus\|USB 对比]]                          |
| 协议层     | [[bus/usb/usb-enumeration-and-descriptors\|枚举与描述符]] · [[bus/usb/usb-class-drivers\|类驱动]] |
| 集成与升级 | [[bus/usb/usb-dma-and-rtos\|DMA 与 RTOS]] · [[bus/usb/usb-dfu\|USB DFU]]                          |

## ③ 无线与 IoT

| 主题             | 入口笔记                                                                                                                                                                                         |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| BLE              | [[bus/wireless-iot/ble-index\|BLE 导航]] · [[bus/wireless-iot/ble-practical\|实战]] · [[bus/wireless-iot/ble-deep-dive\|深入]] · [[bus/wireless-iot/ble-failure-cases\|故障案例]]                |
| ZigBee           | [[bus/wireless-iot/zigbee-index\|ZigBee 导航]] · [[bus/wireless-iot/zigbee-practical\|实战]] · [[bus/wireless-iot/zigbee-deep-dive\|深入]] · [[bus/wireless-iot/zigbee-failure-cases\|故障案例]] |
| LoRa             | [[bus/wireless-iot/lora-index\|LoRa 导航]] · [[bus/wireless-iot/lora-practical\|实战]] · [[bus/wireless-iot/lora-deep-dive\|深入]] · [[bus/wireless-iot/lora-failure-cases\|故障案例]]           |
| Matter           | [[bus/wireless-iot/matter-index\|Matter 导航]] · [[bus/wireless-iot/matter-practical\|实战]] · [[bus/wireless-iot/matter-deep-dive\|深入]]                                                       |
| Thread           | [[bus/wireless-iot/thread-index\|Thread 导航]] · [[bus/wireless-iot/thread-practical\|实战]] · [[bus/wireless-iot/thread-deep-dive\|深入]]                                                       |
| 蜂窝 IoT         | [[bus/wireless-iot/lte-iot-index\|LTE IoT 导航]] · [[bus/wireless-iot/lte-iot-practical\|实战]] · [[bus/wireless-iot/lte-iot-deep-dive\|深入]]                                                   |
| 卫星 IoT         | [[bus/wireless-iot/satellite-iot-index\|卫星 IoT 导航]] · [[bus/wireless-iot/satellite-iot-practical\|实战]]                                                                                     |
| 电力线 / 应急    | [[bus/wireless-iot/plb-index\|PLB 导航]] · [[bus/wireless-iot/rescue-comms-index\|应急通信导航]]                                                                                                 |
| 2.4 GHz 私有协议 | [[bus/wireless-iot/nrf2401\|nRF2401 / nRF24L01+]]                                                                                                                                                |

## ④ 学习与选型

| 目标       | 入口笔记                                                                                                |
| ---------- | ------------------------------------------------------------------------------------------------------- |
| 阶段化学习 | [[guides/learning/LEARNING_PLAN\|学习计划]] · [[guides/learning/READING_PATHS\|按目标阅读]]             |
| 动手实验   | [[guides/learning/LABS\|实验路线]] · [[guides/learning/EXPERIMENT_TEMPLATE\|实验记录模板]]              |
| 协议选型   | [[guides/learning/PROTOCOL_SELECTION\|选型矩阵]] · [[guides/learning/PROTOCOL_COMPARISON\|协议对照]]    |
| 场景与器件 | [[guides/learning/APPLICATION_SCENARIOS\|应用场景]] · [[guides/learning/DEVICE_EXAMPLES\|典型设备接口]] |
| 分层与覆盖 | [[LAYERED_MAP\|分层图谱]] · [[TOPIC_MATRIX\|主题完成度]] · [[COVERAGE\|覆盖范围]]                       |
| 参数速查   | [[guides/learning/PARAMETER_CHEATSHEET\|接口参数速查]]                                                  |

## ⑤ 排障与实战

| 场景       | 入口笔记                                                                                                                          |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 系统化排障 | [[guides/troubleshooting/DEBUG_PLAYBOOK\|跨协议排障方法]] · [[guides/troubleshooting/FIELD_DIAGNOSTIC_RUNBOOK\|现场诊断运行手册]] |
| 故障速查   | [[guides/troubleshooting/TROUBLESHOOTING_QUICKREF\|故障速查表]] · [[guides/troubleshooting/FAILURE_CASES\|故障案例库]]            |
| 波形与测量 | [[guides/troubleshooting/WAVEFORM_GUIDE\|波形观察指南]] · [[guides/troubleshooting/MEASUREMENT_EXAMPLES\|测量样例]]               |
| 硬件检查   | [[guides/troubleshooting/SCHEMATIC_CHECKLISTS\|原理图检查清单]]                                                                   |
| 驱动实现   | [[guides/troubleshooting/DRIVER_PATTERNS\|驱动状态机模式]]                                                                        |

## ⑥ 工程与质量

| 主题           | 入口笔记                                                                                                                                |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 量产测试       | [[guides/engineering/PRODUCTION_TEST\|量产测试策略]] · [[guides/engineering/AUTOMATED_TEST_HARNESS\|自动化测试治具]]                    |
| 回归与可靠性   | [[guides/engineering/REGRESSION_TEST_MATRIX\|回归测试矩阵]] · [[guides/engineering/RELIABILITY_GUIDE\|可靠性设计]]                      |
| 质量与追踪     | [[guides/engineering/COMMUNICATION_QUALITY_GATE\|发布质量门禁]] · [[guides/engineering/COMMUNICATION_TRACEABILITY\|通信追踪矩阵]]       |
| 安全与可观测性 | [[guides/engineering/COMMUNICATION_SECURITY_SAFETY\|安全与失效安全]] · [[guides/engineering/COMMUNICATION_OBSERVABILITY\|通信可观测性]] |

## ⑦ 索引与参考

| 主题       | 入口笔记                                                                                                                   |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- |
| 总索引     | [[INDEX\|知识库索引]] · [[COVERAGE\|覆盖范围]] · [[TOPIC_MATRIX\|主题矩阵]]                                                |
| 术语       | [[reference/GLOSSARY\|术语表]] · [[reference/ACRONYMS\|缩写表]]                                                            |
| 工具与模板 | [[reference/TOOLS\|调试工具]] · [[reference/DOC_TEMPLATES\|文档模板]] · [[guides/learning/PARAMETER_CHEATSHEET\|参数速查]] |
| 协作       | [[CONTRIBUTING\|贡献规范]] · [[REVIEW_CHECKLIST\|评审清单]]                                                                |
| 图形导航   | [[Navigation.canvas\|Navigation 画布]]                                                                                     |

## Obsidian 使用说明

- **Vault 根目录**：本仓库根目录即 Vault，直接 `Open folder as vault` 打开。
- **默认链接**：使用 Wikilink（`[[笔记]]`）；移动或重命名文件时会自动更新链接。
- **图形入口**：根目录 `Navigation.canvas` 是分区导航；`Home.md` 是本页。
- **目录约定**：
  - `basic/`：单点通信、时序与物理层接口。
  - `bus/`：按领域分为 `automotive/`、`industrial/`、`power-rtu/`、`wireless-iot/`、`usb/`、`display/`、`onboard/`。
  - `guides/`：`learning/`、`troubleshooting/`、`engineering/`。
  - `reference/`：术语、缩写、工具与模板。
  - `_Inbox/`：待处理候选，`_System/cron-reports/`：自动扫描报告。两者已在 `.obsidian/app.json` 的排除列表中，不进入搜索、图谱和链接建议。
- **标签约定**：入口笔记使用 `#moc`、`#navigation`、`#type/index`；层级标签为 `#layer/basic`、`#layer/bus`。
- **图谱配色**：`basic` 绿色、`bus` 蓝色、`bus/wireless-iot` 橙色，其余根文档保持默认。

### 维护流程

1. 新协议先写入 `basic/` 或 `bus/`，遵循 [[reference/DOC_TEMPLATES|文档模板]]。
2. 在对应目录 `README.md` 与 [[INDEX|索引]] 中登记入口。
3. 在本页对应分区补充链接，必要时更新 [[TOPIC_MATRIX|主题矩阵]] 与 [[COVERAGE|覆盖范围]]。
4. 需要图形化时，在 [[Navigation.canvas|Navigation 画布]] 增加卡片并连线。
5. 每周运行 `python scripts/inbox_status.py`，按 [_Inbox/README.md](_Inbox/README.md) 消化候选，保持 `pending <= 10`。
