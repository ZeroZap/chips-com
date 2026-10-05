# Knowledge Base Index

## 核心导航

- `README.md`：项目总览和实战深入路径。
- `LEARNING_PLAN.md`：阶段化学习计划。
- `PROTOCOL_SELECTION.md`：协议选型矩阵。
- `TOPIC_MATRIX.md`：主题完成度矩阵 + 待做主题执行计划（5 分制 L0-L4 评分 + I2C 模式执行模板）。
- `DEBUG_PLAYBOOK.md`：跨协议排障方法。
- `TROUBLESHOOTING_QUICKREF.md`：故障速查表。
- `LABS.md`：实验路线。

## 基础外设

- `basic/gpio.md`
- `basic/pwm.md`
- `basic/adc-dac.md`
- `basic/uart-practical.md`
- `basic/uart-deep-dive.md`
- `basic/i2c-practical.md`
- `basic/i2c-deep-dive.md`
- `basic/spi-practical.md`
- `basic/spi-deep-dive.md`
- `basic/qspi-ospi.md`
- `basic/i2s.md`
- `basic/jtag-swd.md`

## 物理层

- `basic/rs232-rs485.md`
- `basic/can-phy.md`
- `basic/ethernet-phy.md`
- `basic/lvds.md`

## 板内与管理总线

- `bus/i3c.md`
- `bus/i3c-topic.md`
- `bus/i3c-deep-dive.md`
- `bus/smbus.md`
- `bus/pmbus.md`
- `bus/smbus-pmbus-practical.md`
- `bus/sdio-practical.md`
- `bus/one-wire-practical.md`

## 工业与车载

- `bus/modbus.md`
- `bus/modbus-tcp-deep-dive.md`
- `bus/rs485-modbus-rtu-practical.md`
- `bus/rs485-modbus-rtu-deep-dive.md`
- `bus/rtu-protocols.md`：RTU 设备协议全集总览——电力 / 水利 / 表计 / 楼宇 / IoT 协议覆盖矩阵。

### RTU 协议全集（电力 / 水利 / 表计 / 楼宇 / IoT）

每个协议 L4 完整闭环：总览 / 实战 / 深度 / 导航 / 故障案例。

- `bus/iec104.md` / `iec104-practical.md` / `iec104-deep-dive.md` / `iec104-index.md` / `iec104-failure-cases.md`：IEC 60870-5-104。
- `bus/iec101.md` / `iec101-practical.md` / `iec101-deep-dive.md` / `iec101-index.md` / `iec101-failure-cases.md`：IEC 60870-5-101。
- `bus/dnp3.md` / `dnp3-practical.md` / `dnp3-deep-dive.md` / `dnp3-index.md` / `dnp3-failure-cases.md`：DNP3（IEEE 1815）。
- `bus/iec61850.md` / `iec61850-practical.md` / `iec61850-deep-dive.md` / `iec61850-index.md` / `iec61850-failure-cases.md`：IEC 61850 变电站自动化。
- `bus/sl651.md` / `sl651-practical.md` / `sl651-deep-dive.md` / `sl651-index.md` / `sl651-failure-cases.md`：SL 651-2014 水文监测。
- `bus/szy206.md` / `szy206-practical.md` / `szy206-deep-dive.md` / `szy206-index.md` / `szy206-failure-cases.md`：SZY 206-2016 水资源监测。
- `bus/slt427.md` / `slt427-practical.md` / `slt427-deep-dive.md` / `slt427-index.md` / `slt427-failure-cases.md`：SL/T 427 水资源监测补充。
- `bus/hj212.md` / `hj212-practical.md` / `hj212-deep-dive.md` / `hj212-index.md` / `hj212-failure-cases.md`：HJ 212-2017 环保联网。
- `bus/dlt645.md` / `dlt645-practical.md` / `dlt645-deep-dive.md` / `dlt645-index.md` / `dlt645-failure-cases.md`：DL/T 645 电能表。
- `bus/cjt188.md` / `cjt188-practical.md` / `cjt188-deep-dive.md` / `cjt188-index.md` / `cjt188-failure-cases.md`：CJ/T 188 水气热量表。
- `bus/bacnet.md` / `bacnet-practical.md` / `bacnet-deep-dive.md` / `bacnet-index.md` / `bacnet-failure-cases.md`：BACnet 楼宇自动化。
- `bus/opcua.md` / `opcua-practical.md` / `opcua-deep-dive.md` / `opcua-index.md` / `opcua-failure-cases.md`：OPC UA 工业 4.0。

### RTU 跨协议网关设计

- `bus/rtu-gateway-design.md`：RTU 网关总体设计（内部 Point 模型 / 协议转换策略）。
- `bus/modbus-rtu-iec104-gateway.md`：Modbus RTU ↔ IEC 104（电力主站最常见）。
- `bus/dlt645-iec104-gateway.md`：DL/T 645 ↔ IEC 104（电表接入电力主站）。
- `bus/modbus-rtu-mqtt-gateway.md`：Modbus RTU ↔ MQTT（工业 IoT 上云）。
- `bus/hj212-mqtt-gateway.md`：HJ 212 ↔ MQTT（环保 RTU 上云）。
- `bus/dnp3-iec104-gateway.md`：DNP3 ↔ IEC 104（双栈 / 出海 + 国内）。
- `bus/bacnet-opcua-gateway.md`：BACnet ↔ OPC UA（楼宇 + 工业 4.0）。
- `bus/iec61850-iec104-gateway.md`：IEC 61850 ↔ IEC 104（变电站双栈）。
- `bus/can.md`
- `bus/canopen.md`
- `bus/can-canopen-practical.md`
- `bus/can-canopen-deep-dive.md`
- `bus/iso-tp.md`
- `bus/iso-tp-practical.md`
- `bus/iso-tp-deep-dive.md`
- `bus/lin-practical.md`
- `bus/ethercat-deep-dive.md`
- `bus/industrial-ethernet-comparison.md`
- `bus/profinet.md`
- `bus/profinet-practical.md`
- `bus/profinet-deep-dive.md`
- `bus/ethernet-ip.md`
- `bus/ethernet-ip-practical.md`
- `bus/ethernet-ip-deep-dive.md`
- `bus/j1939.md`
- `bus/j1939-practical.md`
- `bus/j1939-deep-dive.md`
- `bus/uds.md`
- `bus/uds-practical.md`
- `bus/uds-deep-dive.md`
- `bus/profibus.md`
- `bus/profibus-practical.md`
- `bus/profibus-deep-dive.md`
- `bus/dmx512.md`
- `bus/dmx512-practical.md`
- `bus/dmx512-deep-dive.md`

## 通用外设与网络

- `bus/usb.md`
- `bus/usb-practical.md`
- `bus/usb-deep-dive.md`
- `bus/usb-failure-cases.md`
- `bus/usb-enumeration-and-descriptors.md`
- `bus/usb-class-drivers.md`
- `bus/usb-dma-and-rtos.md`
- `bus/usb-vs-other-bus.md`
- `bus/usb-index.md`
- `bus/usb-dfu.md`
- `bus/usb-dfu-practical.md`
- `bus/usb-dfu-deep-dive.md`
- `bus/ethernet.md`
- `bus/ethernet-deep-dive.md`
- `bus/ethernet-modbus-tcp-practical.md`
- `bus/modbus-tcp-deep-dive.md`
- `bus/ethernet-tsn.md`
- `bus/ethernet-tsn-practical.md`
- `bus/mqtt.md`
- `bus/mqtt-practical.md`
- `bus/mqtt-deep-dive.md`
- `bus/pcie-practical.md`

## 无线 / 私有 2.4 GHz 协议

- `wireless-2g4/nrf2401.md`：Nordic nRF24L01+ ShockBurst 协议（2.4 GHz 私有轻量收发器，SPI 接口 + 6 pipe + ACK payload）

## 图像与显示

- `bus/mipi-csi-dsi-debug.md`
- `bus/mipi-csi-dsi-deep-dive.md`
- `bus/display-interfaces.md`
- `bus/fpd-link-gmsl.md`
- `bus/fpd-link-gmsl-practical.md`
- `bus/fpd-link-gmsl-deep-dive.md`
- `bus/hdmi-edp.md`
- `bus/hdmi-edp-practical.md`
- `bus/hdmi-edp-deep-dive.md`

## 参考资料

- `GLOSSARY.md`
- `ACRONYMS.md`
- `TOOLS.md`
- `MEASUREMENT_EXAMPLES.md`
- `LAYERED_MAP.md`
- `APPLICATION_SCENARIOS.md`
- `DEVICE_EXAMPLES.md`
- `DOC_TEMPLATES.md`
- `PROTOCOL_COMPARISON.md`
- `REGRESSION_TEST_MATRIX.md`
- `AUTOMATED_TEST_HARNESS.md`
- `COMMUNICATION_OBSERVABILITY.md`
- `COMMUNICATION_QUALITY_GATE.md`
- `FIELD_DIAGNOSTIC_RUNBOOK.md`
- `COMMUNICATION_TRACEABILITY.md`
- `COMMUNICATION_SECURITY_SAFETY.md`

## 知识库里程碑

- **v3.x 沉淀期**（2026-07-29 起）：6 个 L4 闭环主题（I2C / SPI / UART / CAN / J1939 / USB）+ 47 篇 607 KB。暂停主动扩主题，专注实战案例和横向工作。详见 `LEARNING_PLAN.md` 阶段 6。
