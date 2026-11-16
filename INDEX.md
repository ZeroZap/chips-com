---
tags:
  - type/index
---

# Knowledge Base Index

## 核心导航

- [Home.md](Home.md)：Obsidian 仪表盘——按主题和角色组织的双链入口。
- `Navigation.canvas`：根目录 Canvas 图形导航——分区浏览基础、总线、无线、排障与索引。
- [README.md](README.md)：项目总览和实战深入路径。
- [guides/learning/LEARNING_PLAN.md](guides/learning/LEARNING_PLAN.md)：阶段化学习计划。
- [guides/learning/PROTOCOL_SELECTION.md](guides/learning/PROTOCOL_SELECTION.md)：协议选型矩阵。
- [TOPIC_MATRIX.md](TOPIC_MATRIX.md)：主题完成度矩阵 + 待做主题执行计划（5 分制 L0-L4 评分 + I2C 模式执行模板）。
- [guides/troubleshooting/DEBUG_PLAYBOOK.md](guides/troubleshooting/DEBUG_PLAYBOOK.md)：跨协议排障方法。
- [guides/troubleshooting/TROUBLESHOOTING_QUICKREF.md](guides/troubleshooting/TROUBLESHOOTING_QUICKREF.md)：故障速查表。
- [guides/learning/LABS.md](guides/learning/LABS.md)：实验路线。

## 总线协议分目录

- [bus/automotive/README.md](bus/automotive/README.md)：车载与诊断——CAN 家族、CANopen、J1939、ISO-TP、UDS、OBD、LIN。
- [bus/industrial/README.md](bus/industrial/README.md)：工业与工业以太网——Modbus、PROFI*、EtherCAT、EtherNet/IP、TSN、OPC UA、MQTT、DMX512。
- [bus/power-rtu/README.md](bus/power-rtu/README.md)：电力 / 水利 / 表计 / 楼宇——IEC 101/104、DNP3、IEC 61850、SL/SZY/HJ、DL/T 645、CJ/T 188、BACnet。
- [bus/wireless-iot/README.md](bus/wireless-iot/README.md)：无线与物联网——BLE、ZigBee、LoRa、Matter、Thread、LTE IoT、卫星、PLB、应急通信。
- [bus/usb/README.md](bus/usb/README.md)：USB 枚举、类驱动、DFU、DMA/RTOS。
- [bus/display/README.md](bus/display/README.md)：显示与视频链路——HDMI/eDP、FPD-Link/GMSL、MIPI CSI/DSI。
- [bus/onboard/README.md](bus/onboard/README.md)：板内与管理总线——I3C、SMBus/PMBus、SDIO、1-Wire、PCIe。

## 基础外设

- [basic/gpio.md](basic/gpio.md)
- [basic/pwm.md](basic/pwm.md)
- [basic/adc-dac.md](basic/adc-dac.md)
- [basic/uart-practical.md](basic/uart-practical.md)
- [basic/uart-deep-dive.md](basic/uart-deep-dive.md)
- [basic/i2c-practical.md](basic/i2c-practical.md)
- [basic/i2c-deep-dive.md](basic/i2c-deep-dive.md)
- [basic/spi-practical.md](basic/spi-practical.md)
- [basic/spi-deep-dive.md](basic/spi-deep-dive.md)
- [basic/qspi-ospi.md](basic/qspi-ospi.md)
- [basic/i2s.md](basic/i2s.md)
- [basic/jtag-swd.md](basic/jtag-swd.md)

## 物理层

- [basic/rs232-rs485.md](basic/rs232-rs485.md)
- [basic/can-phy.md](basic/can-phy.md)
- [basic/ethernet-phy.md](basic/ethernet-phy.md)
- [basic/lvds.md](basic/lvds.md)

## 板内与管理总线

- [bus/onboard/i3c.md](bus/onboard/i3c.md)
- [bus/onboard/i3c-topic.md](bus/onboard/i3c-topic.md)
- [bus/onboard/i3c-deep-dive.md](bus/onboard/i3c-deep-dive.md)
- [bus/onboard/smbus.md](bus/onboard/smbus.md)
- [bus/onboard/pmbus.md](bus/onboard/pmbus.md)
- [bus/onboard/smbus-pmbus-practical.md](bus/onboard/smbus-pmbus-practical.md)
- [bus/onboard/sdio-practical.md](bus/onboard/sdio-practical.md)
- [bus/onboard/one-wire-practical.md](bus/onboard/one-wire-practical.md)

## 工业与车载

- [bus/industrial/modbus.md](bus/industrial/modbus.md)
- [bus/industrial/modbus-tcp-deep-dive.md](bus/industrial/modbus-tcp-deep-dive.md)
- [bus/industrial/rs485-modbus-rtu-practical.md](bus/industrial/rs485-modbus-rtu-practical.md)
- [bus/industrial/rs485-modbus-rtu-deep-dive.md](bus/industrial/rs485-modbus-rtu-deep-dive.md)
- [bus/power-rtu/rtu-protocols.md](bus/power-rtu/rtu-protocols.md)：RTU 设备协议全集总览——电力 / 水利 / 表计 / 楼宇 / IoT 协议覆盖矩阵。

### RTU 协议全集（电力 / 水利 / 表计 / 楼宇 / IoT）

每个协议 L4 完整闭环：总览 / 实战 / 深度 / 导航 / 故障案例。

- [bus/power-rtu/iec104.md](bus/power-rtu/iec104.md) / [iec104-practical.md](bus/power-rtu/iec104-practical.md) / [iec104-deep-dive.md](bus/power-rtu/iec104-deep-dive.md) / [iec104-index.md](bus/power-rtu/iec104-index.md) / [iec104-failure-cases.md](bus/power-rtu/iec104-failure-cases.md)：IEC 60870-5-104。
- [bus/power-rtu/iec101.md](bus/power-rtu/iec101.md) / [iec101-practical.md](bus/power-rtu/iec101-practical.md) / [iec101-deep-dive.md](bus/power-rtu/iec101-deep-dive.md) / [iec101-index.md](bus/power-rtu/iec101-index.md) / [iec101-failure-cases.md](bus/power-rtu/iec101-failure-cases.md)：IEC 60870-5-101。
- [bus/power-rtu/dnp3.md](bus/power-rtu/dnp3.md) / [dnp3-practical.md](bus/power-rtu/dnp3-practical.md) / [dnp3-deep-dive.md](bus/power-rtu/dnp3-deep-dive.md) / [dnp3-index.md](bus/power-rtu/dnp3-index.md) / [dnp3-failure-cases.md](bus/power-rtu/dnp3-failure-cases.md)：DNP3（IEEE 1815）。
- [bus/power-rtu/iec61850.md](bus/power-rtu/iec61850.md) / [iec61850-practical.md](bus/power-rtu/iec61850-practical.md) / [iec61850-deep-dive.md](bus/power-rtu/iec61850-deep-dive.md) / [iec61850-index.md](bus/power-rtu/iec61850-index.md) / [iec61850-failure-cases.md](bus/power-rtu/iec61850-failure-cases.md)：IEC 61850 变电站自动化。
- [bus/power-rtu/sl651.md](bus/power-rtu/sl651.md) / [sl651-practical.md](bus/power-rtu/sl651-practical.md) / [sl651-deep-dive.md](bus/power-rtu/sl651-deep-dive.md) / [sl651-index.md](bus/power-rtu/sl651-index.md) / [sl651-failure-cases.md](bus/power-rtu/sl651-failure-cases.md)：SL 651-2014 水文监测。
- [bus/power-rtu/szy206.md](bus/power-rtu/szy206.md) / [szy206-practical.md](bus/power-rtu/szy206-practical.md) / [szy206-deep-dive.md](bus/power-rtu/szy206-deep-dive.md) / [szy206-index.md](bus/power-rtu/szy206-index.md) / [szy206-failure-cases.md](bus/power-rtu/szy206-failure-cases.md)：SZY 206-2016 水资源监测。
- [bus/power-rtu/slt427.md](bus/power-rtu/slt427.md) / [slt427-practical.md](bus/power-rtu/slt427-practical.md) / [slt427-deep-dive.md](bus/power-rtu/slt427-deep-dive.md) / [slt427-index.md](bus/power-rtu/slt427-index.md) / [slt427-failure-cases.md](bus/power-rtu/slt427-failure-cases.md)：SL/T 427 水资源监测补充。
- [bus/power-rtu/hj212.md](bus/power-rtu/hj212.md) / [hj212-practical.md](bus/power-rtu/hj212-practical.md) / [hj212-deep-dive.md](bus/power-rtu/hj212-deep-dive.md) / [hj212-index.md](bus/power-rtu/hj212-index.md) / [hj212-failure-cases.md](bus/power-rtu/hj212-failure-cases.md)：HJ 212-2017 环保联网。
- [bus/power-rtu/dlt645.md](bus/power-rtu/dlt645.md) / [dlt645-practical.md](bus/power-rtu/dlt645-practical.md) / [dlt645-deep-dive.md](bus/power-rtu/dlt645-deep-dive.md) / [dlt645-index.md](bus/power-rtu/dlt645-index.md) / [dlt645-failure-cases.md](bus/power-rtu/dlt645-failure-cases.md)：DL/T 645 电能表。
- [bus/power-rtu/cjt188.md](bus/power-rtu/cjt188.md) / [cjt188-practical.md](bus/power-rtu/cjt188-practical.md) / [cjt188-deep-dive.md](bus/power-rtu/cjt188-deep-dive.md) / [cjt188-index.md](bus/power-rtu/cjt188-index.md) / [cjt188-failure-cases.md](bus/power-rtu/cjt188-failure-cases.md)：CJ/T 188 水气热量表。
- [bus/power-rtu/bacnet.md](bus/power-rtu/bacnet.md) / [bacnet-practical.md](bus/power-rtu/bacnet-practical.md) / [bacnet-deep-dive.md](bus/power-rtu/bacnet-deep-dive.md) / [bacnet-index.md](bus/power-rtu/bacnet-index.md) / [bacnet-failure-cases.md](bus/power-rtu/bacnet-failure-cases.md)：BACnet 楼宇自动化。
- [bus/industrial/opcua.md](bus/industrial/opcua.md) / [opcua-practical.md](bus/industrial/opcua-practical.md) / [opcua-deep-dive.md](bus/industrial/opcua-deep-dive.md) / [opcua-index.md](bus/industrial/opcua-index.md) / [opcua-failure-cases.md](bus/industrial/opcua-failure-cases.md)：OPC UA 工业 4.0。

### RTU 跨协议网关设计

- [bus/power-rtu/rtu-gateway-design.md](bus/power-rtu/rtu-gateway-design.md)：RTU 网关总体设计（内部 Point 模型 / 协议转换策略）。
- [bus/industrial/modbus-rtu-iec104-gateway.md](bus/industrial/modbus-rtu-iec104-gateway.md)：Modbus RTU ↔ IEC 104（电力主站最常见）。
- [bus/power-rtu/dlt645-iec104-gateway.md](bus/power-rtu/dlt645-iec104-gateway.md)：DL/T 645 ↔ IEC 104（电表接入电力主站）。
- [bus/industrial/modbus-rtu-mqtt-gateway.md](bus/industrial/modbus-rtu-mqtt-gateway.md)：Modbus RTU ↔ MQTT（工业 IoT 上云）。
- [bus/power-rtu/hj212-mqtt-gateway.md](bus/power-rtu/hj212-mqtt-gateway.md)：HJ 212 ↔ MQTT（环保 RTU 上云）。
- [bus/power-rtu/dnp3-iec104-gateway.md](bus/power-rtu/dnp3-iec104-gateway.md)：DNP3 ↔ IEC 104（双栈 / 出海 + 国内）。
- [bus/power-rtu/bacnet-opcua-gateway.md](bus/power-rtu/bacnet-opcua-gateway.md)：BACnet ↔ OPC UA（楼宇 + 工业 4.0）。
- [bus/power-rtu/iec61850-iec104-gateway.md](bus/power-rtu/iec61850-iec104-gateway.md)：IEC 61850 ↔ IEC 104（变电站双栈）。

### RTU 协议厂商对标

- [bus/power-rtu/iec104-vendor-bench.md](bus/power-rtu/iec104-vendor-bench.md)：IEC 104 厂商对标（南瑞 / 四方 / ABB / Siemens / SEL）。
- [bus/power-rtu/iec101-vendor-bench.md](bus/power-rtu/iec101-vendor-bench.md)：IEC 101 厂商对标。
- [bus/power-rtu/dlt645-vendor-bench.md](bus/power-rtu/dlt645-vendor-bench.md)：DL/T 645 厂商对标（三星 / 宁波水表 / 海兴 / 威胜）。
- [bus/power-rtu/hj212-vendor-bench.md](bus/power-rtu/hj212-vendor-bench.md)：HJ 212 厂商对标（聚光 / 先河 / 雪迪龙）。
- [bus/power-rtu/sl651-vendor-bench.md](bus/power-rtu/sl651-vendor-bench.md)：SL 651 厂商对标（四创 / 国睿）。
- [bus/power-rtu/dnp3-vendor-bench.md](bus/power-rtu/dnp3-vendor-bench.md)：DNP3 厂商对标（ABB / Siemens / SEL / GE）。
- [bus/power-rtu/iec61850-vendor-bench.md](bus/power-rtu/iec61850-vendor-bench.md)：IEC 61850 厂商对标。
- [bus/power-rtu/szy206-vendor-bench.md](bus/power-rtu/szy206-vendor-bench.md)：SZY 206 厂商对标。
- [bus/power-rtu/slt427-vendor-bench.md](bus/power-rtu/slt427-vendor-bench.md)：SL/T 427 厂商对标。
- [bus/power-rtu/bacnet-vendor-bench.md](bus/power-rtu/bacnet-vendor-bench.md)：BACnet 厂商对标（Honeywell / JCI / Siemens / Schneider）。
- [bus/industrial/opcua-vendor-bench.md](bus/industrial/opcua-vendor-bench.md)：OPC UA 厂商对标（Siemens / Beckhoff / Rockwell）。
- [bus/power-rtu/cjt188-vendor-bench.md](bus/power-rtu/cjt188-vendor-bench.md)：CJ/T 188 厂商对标（宁波水表 / 新天科技）。
- [bus/industrial/mqtt-vendor-bench.md](bus/industrial/mqtt-vendor-bench.md)：MQTT 厂商对标（AWS IoT / Azure / 阿里云 / 华为云 / EMQX）。
- [bus/automotive/can-protocol-family.md](bus/automotive/can-protocol-family.md)：CAN 家族全景——分层结构、协议矩阵、选型决策、文档索引与覆盖缺口。
- [bus/automotive/can-standards-map.md](bus/automotive/can-standards-map.md)：CAN 家族标准规范总表——按层与按协议汇总 ISO/SAE/CiA 标准号，含电器规范、环境/安全/法规层。
- [bus/automotive/can-index.md](bus/automotive/can-index.md)：CAN 家族分层导航——物理层、传输层与应用层边界。
- [bus/automotive/can-fd-index.md](bus/automotive/can-fd-index.md)：CAN FD / CAN XL 导航。
- [bus/automotive/canopen-index.md](bus/automotive/canopen-index.md)：CANopen 导航。
- [bus/automotive/iso-tp-index.md](bus/automotive/iso-tp-index.md)：ISO-TP 导航。
- [bus/automotive/uds-index.md](bus/automotive/uds-index.md)：UDS 导航。
- [bus/automotive/obd2-index.md](bus/automotive/obd2-index.md)：OBD-II 导航。
- [bus/automotive/wwh-obd-index.md](bus/automotive/wwh-obd-index.md)：WWH-OBD 导航。
- [bus/automotive/can.md](bus/automotive/can.md)
- [bus/automotive/canopen.md](bus/automotive/canopen.md)
- [bus/automotive/canopen-practical.md](bus/automotive/canopen-practical.md)
- [bus/automotive/canopen-deep-dive.md](bus/automotive/canopen-deep-dive.md)
- [bus/automotive/canopen-failure-cases.md](bus/automotive/canopen-failure-cases.md)
- [bus/automotive/canopen-safety.md](bus/automotive/canopen-safety.md)
- [bus/automotive/iso-tp.md](bus/automotive/iso-tp.md)
- [bus/automotive/iso-tp-practical.md](bus/automotive/iso-tp-practical.md)
- [bus/automotive/iso-tp-deep-dive.md](bus/automotive/iso-tp-deep-dive.md)
- [bus/automotive/iso-tp-failure-cases.md](bus/automotive/iso-tp-failure-cases.md)
- [bus/automotive/obd2.md](bus/automotive/obd2.md)
- [bus/automotive/obd2-deep-dive.md](bus/automotive/obd2-deep-dive.md)
- [bus/automotive/obd2-practical.md](bus/automotive/obd2-practical.md)
- [bus/automotive/obd2-failure-cases.md](bus/automotive/obd2-failure-cases.md)
- [bus/automotive/wwh-obd.md](bus/automotive/wwh-obd.md)
- [bus/automotive/wwh-obd-deep-dive.md](bus/automotive/wwh-obd-deep-dive.md)
- [bus/automotive/wwh-obd-practical.md](bus/automotive/wwh-obd-practical.md)
- [bus/automotive/wwh-obd-failure-cases.md](bus/automotive/wwh-obd-failure-cases.md)
- [bus/automotive/lin.md](bus/automotive/lin.md)
- [bus/automotive/lin-practical.md](bus/automotive/lin-practical.md)
- [bus/industrial/ethercat-deep-dive.md](bus/industrial/ethercat-deep-dive.md)
- [bus/industrial/industrial-ethernet-comparison.md](bus/industrial/industrial-ethernet-comparison.md)
- [bus/industrial/profinet.md](bus/industrial/profinet.md)
- [bus/industrial/profinet-practical.md](bus/industrial/profinet-practical.md)
- [bus/industrial/profinet-deep-dive.md](bus/industrial/profinet-deep-dive.md)
- [bus/industrial/ethernet-ip.md](bus/industrial/ethernet-ip.md)
- [bus/industrial/ethernet-ip-practical.md](bus/industrial/ethernet-ip-practical.md)
- [bus/industrial/ethernet-ip-deep-dive.md](bus/industrial/ethernet-ip-deep-dive.md)
- [bus/automotive/j1939.md](bus/automotive/j1939.md)
- [bus/automotive/j1939-practical.md](bus/automotive/j1939-practical.md)
- [bus/automotive/j1939-deep-dive.md](bus/automotive/j1939-deep-dive.md)
- [bus/automotive/uds.md](bus/automotive/uds.md)
- [bus/automotive/uds-practical.md](bus/automotive/uds-practical.md)
- [bus/automotive/uds-deep-dive.md](bus/automotive/uds-deep-dive.md)
- [bus/automotive/uds-failure-cases.md](bus/automotive/uds-failure-cases.md)
- [bus/industrial/profibus.md](bus/industrial/profibus.md)
- [bus/industrial/profibus-practical.md](bus/industrial/profibus-practical.md)
- [bus/industrial/profibus-deep-dive.md](bus/industrial/profibus-deep-dive.md)
- [bus/industrial/dmx512.md](bus/industrial/dmx512.md)
- [bus/industrial/dmx512-practical.md](bus/industrial/dmx512-practical.md)
- [bus/industrial/dmx512-deep-dive.md](bus/industrial/dmx512-deep-dive.md)

## 通用外设与网络

- [bus/usb/usb.md](bus/usb/usb.md)
- [bus/usb/usb-practical.md](bus/usb/usb-practical.md)
- [bus/usb/usb-deep-dive.md](bus/usb/usb-deep-dive.md)
- [bus/usb/usb-failure-cases.md](bus/usb/usb-failure-cases.md)
- [bus/usb/usb-enumeration-and-descriptors.md](bus/usb/usb-enumeration-and-descriptors.md)
- [bus/usb/usb-class-drivers.md](bus/usb/usb-class-drivers.md)
- [bus/usb/usb-dma-and-rtos.md](bus/usb/usb-dma-and-rtos.md)
- [bus/usb/usb-vs-other-bus.md](bus/usb/usb-vs-other-bus.md)
- [bus/usb/usb-index.md](bus/usb/usb-index.md)
- [bus/usb/usb-dfu.md](bus/usb/usb-dfu.md)
- [bus/usb/usb-dfu-practical.md](bus/usb/usb-dfu-practical.md)
- [bus/usb/usb-dfu-deep-dive.md](bus/usb/usb-dfu-deep-dive.md)
- [bus/industrial/ethernet.md](bus/industrial/ethernet.md)
- [bus/industrial/ethernet-deep-dive.md](bus/industrial/ethernet-deep-dive.md)
- [bus/industrial/ethernet-modbus-tcp-practical.md](bus/industrial/ethernet-modbus-tcp-practical.md)
- [bus/industrial/modbus-tcp-deep-dive.md](bus/industrial/modbus-tcp-deep-dive.md)
- [bus/industrial/ethernet-tsn.md](bus/industrial/ethernet-tsn.md)
- [bus/industrial/ethernet-tsn-practical.md](bus/industrial/ethernet-tsn-practical.md)
- [bus/industrial/mqtt.md](bus/industrial/mqtt.md)
- [bus/industrial/mqtt-practical.md](bus/industrial/mqtt-practical.md)
- [bus/industrial/mqtt-deep-dive.md](bus/industrial/mqtt-deep-dive.md)
- [bus/onboard/pcie-practical.md](bus/onboard/pcie-practical.md)

## 无线 / 私有 2.4 GHz 协议

- [bus/wireless-iot/nrf2401.md](bus/wireless-iot/nrf2401.md)：Nordic nRF24L01+ ShockBurst 协议（2.4 GHz 私有轻量收发器，SPI 接口 + 6 pipe + ACK payload）

## 图像与显示

- [bus/display/mipi-csi-dsi-debug.md](bus/display/mipi-csi-dsi-debug.md)
- [bus/display/mipi-csi-dsi-deep-dive.md](bus/display/mipi-csi-dsi-deep-dive.md)
- [bus/display/display-interfaces.md](bus/display/display-interfaces.md)
- [bus/display/fpd-link-gmsl.md](bus/display/fpd-link-gmsl.md)
- [bus/display/fpd-link-gmsl-practical.md](bus/display/fpd-link-gmsl-practical.md)
- [bus/display/fpd-link-gmsl-deep-dive.md](bus/display/fpd-link-gmsl-deep-dive.md)
- [bus/display/hdmi-edp.md](bus/display/hdmi-edp.md)
- [bus/display/hdmi-edp-practical.md](bus/display/hdmi-edp-practical.md)
- [bus/display/hdmi-edp-deep-dive.md](bus/display/hdmi-edp-deep-dive.md)

## 参考资料

- [reference/GLOSSARY.md](reference/GLOSSARY.md)
- [reference/ACRONYMS.md](reference/ACRONYMS.md)
- [reference/STANDARDS.md](reference/STANDARDS.md)
- [reference/TOOLS.md](reference/TOOLS.md)
- [guides/troubleshooting/MEASUREMENT_EXAMPLES.md](guides/troubleshooting/MEASUREMENT_EXAMPLES.md)
- [LAYERED_MAP.md](LAYERED_MAP.md)
- [guides/learning/APPLICATION_SCENARIOS.md](guides/learning/APPLICATION_SCENARIOS.md)
- [guides/learning/DEVICE_EXAMPLES.md](guides/learning/DEVICE_EXAMPLES.md)
- [reference/DOC_TEMPLATES.md](reference/DOC_TEMPLATES.md)
- [guides/learning/PROTOCOL_COMPARISON.md](guides/learning/PROTOCOL_COMPARISON.md)
- [guides/engineering/REGRESSION_TEST_MATRIX.md](guides/engineering/REGRESSION_TEST_MATRIX.md)
- [guides/engineering/AUTOMATED_TEST_HARNESS.md](guides/engineering/AUTOMATED_TEST_HARNESS.md)
- [guides/engineering/COMMUNICATION_OBSERVABILITY.md](guides/engineering/COMMUNICATION_OBSERVABILITY.md)
- [guides/engineering/COMMUNICATION_QUALITY_GATE.md](guides/engineering/COMMUNICATION_QUALITY_GATE.md)
- [guides/troubleshooting/FIELD_DIAGNOSTIC_RUNBOOK.md](guides/troubleshooting/FIELD_DIAGNOSTIC_RUNBOOK.md)
- [guides/engineering/COMMUNICATION_TRACEABILITY.md](guides/engineering/COMMUNICATION_TRACEABILITY.md)
- [guides/engineering/COMMUNICATION_SECURITY_SAFETY.md](guides/engineering/COMMUNICATION_SECURITY_SAFETY.md)

## 知识库里程碑

- **v3.x 沉淀期**（2026-07-29 起）：31 个 5 分主题（19 个核心 L4 + 12 个行业闭环）+ 312 篇知识库文档（含索引与模板）/ 约 3.2 MB。暂停主动扩主题，专注实战案例和横向工作。详见 [guides/learning/LEARNING_PLAN.md](guides/learning/LEARNING_PLAN.md) 阶段 6。
