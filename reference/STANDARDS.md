---
tags:
  - layer/reference
  - type/reference
---

# Standards

> 本文按领域汇总知识库涉及的标准与规范，作为选型、评审和合规检查的统一入口。
> 标准版本会持续更新，具体条款以官方发布文本为准。
> 最后更新：2026-11-16

## 使用方式

- 先按领域找到标准编号，再进入对应协议文档。
- “范围”列只描述标准覆盖的核心内容，不替代标准原文。
- 涉及认证、法规或安全等级时，必须核对最新版本和适用地区。

## 汽车 / CAN / 诊断

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| ISO 11898-1 | CAN 数据链路层与帧格式，含经典 CAN、CAN FD | `basic/can-deep-dive.md`、`basic/can-fd-and-can-xl.md` |
| ISO 11898-2 | 高速 CAN 物理层、差分电平、终端与位时序 | `basic/can-phy.md`、`basic/can-practical.md` |
| ISO 11898-3 | 低速容错 CAN 物理层 | `basic/can-phy.md` |
| ISO 16845-1 / -2 | CAN 一致性测试方法 | `basic/can-deep-dive.md` |
| ISO 15765-2 | CAN 上的诊断传输协议（ISO-TP） | `bus/automotive/iso-tp-index.md` |
| ISO 14229-1 ~ -7 | 统一诊断服务（UDS） | `bus/automotive/uds-index.md` |
| SAE J1939-21 | J1939 数据链路层与传输协议 | `bus/automotive/j1939-index.md` |
| SAE J1939-71 | J1939 车辆应用层 | `bus/automotive/j1939-protocol-spec.md` |
| SAE J1939-73 | J1939 诊断应用层 | `bus/automotive/j1939-index.md` |
| SAE J1939-81 | J1939 网络管理与地址声明 | `bus/automotive/j1939-network-management.md` |
| SAE J1979 / ISO 15031-5 | OBD-II 诊断测试模式 | `bus/automotive/obd2-index.md` |
| ISO 27145-1 ~ -4, -6 | WWH-OBD 全球统一车载诊断 | `bus/automotive/wwh-obd-index.md` |
| CiA 301 | CANopen 应用层与通信规范 | `bus/automotive/canopen-index.md` |
| CiA 402 | CANopen 驱动与运动控制行规 | `bus/automotive/canopen-safety.md` |
| CiA 1301 | CANopen FD 规范 | `bus/automotive/canopen-index.md` |
| ISO 26262 | 汽车功能安全 | `guides/engineering/COMMUNICATION_SECURITY_SAFETY.md` |
| ISO 21434 | 汽车网络安全工程 | `guides/engineering/COMMUNICATION_SECURITY_SAFETY.md` |
| UNECE R155 / R156 | 车辆网络安全与软件更新法规 | `guides/engineering/COMMUNICATION_SECURITY_SAFETY.md` |
| ISO 16750-1 ~ -5 | 汽车电子环境条件与试验 | `guides/engineering/RELIABILITY_GUIDE.md` |
| ISO 7637-2 | 汽车电源线瞬态传导抗扰度 | `guides/engineering/RELIABILITY_GUIDE.md` |
| ISO 10605 | 汽车电子静电放电试验 | `guides/engineering/RELIABILITY_GUIDE.md` |
| CISPR 25 | 车辆电子部件辐射发射 | `guides/engineering/RELIABILITY_GUIDE.md` |
| ISO 11452 | 车辆电子部件辐射抗扰度 | `guides/engineering/RELIABILITY_GUIDE.md` |

## 工业自动化 / 工业以太网

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| IEC 61158 | 工业通信网络现场总线规范 | `bus/industrial/industrial-ethernet-comparison.md` |
| IEC 61784 | 现场总线通信行规 | `bus/industrial/industrial-ethernet-comparison.md` |
| IEC 62443 | 工业自动化与控制系统网络安全 | `guides/engineering/COMMUNICATION_SECURITY_SAFETY.md` |
| IEC 61131 | 可编程控制器编程与系统 | `bus/industrial/modbus.md` |
| Modbus Application Protocol | Modbus 应用层与功能码 | `bus/industrial/modbus.md` |
| Modbus over Serial Line | Modbus RTU / ASCII 串行链路 | `bus/industrial/rs485-modbus-rtu-deep-dive.md` |
| Modbus Messaging on TCP/IP | Modbus TCP 与 MBAP | `bus/industrial/ethernet-modbus-tcp-practical.md` |
| EtherCAT ETG Specification | EtherCAT 主从站、状态机与 PDO | `bus/industrial/ethercat-deep-dive.md` |
| PROFINET IEC 61158 / 61784 | PROFINET IO、RT/IRT、GSDML | `bus/industrial/profinet-deep-dive.md` |
| PROFIBUS IEC 61158 / 61784 | PROFIBUS DP 与 GSD | `bus/industrial/profibus-deep-dive.md` |
| EtherNet/IP ODVA | EtherNet/IP、CIP、EDS | `bus/industrial/ethernet-ip-deep-dive.md` |
| IEC 62541 | OPC UA 信息模型、服务与安全 | `bus/industrial/opcua-index.md` |
| ASHRAE 135 / ISO 16484-5 | BACnet 楼宇自动控制网络 | `bus/power-rtu/bacnet-index.md` |
| IEEE 1815 | DNP3 分布式网络协议 | `bus/power-rtu/dnp3-index.md` |

## 电力 / 水务 / 表计 / 楼宇

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| IEC 60870-5-101 | 串行远动通信传输规约 | `bus/power-rtu/iec101-index.md` |
| IEC 60870-5-104 | 以太网远动通信传输规约 | `bus/power-rtu/iec104-index.md` |
| IEC 61850 | 变电站自动化通信网络与系统 | `bus/power-rtu/iec61850-index.md` |
| DL/T 645-2007 | 多功能电能表通信规约 | `bus/power-rtu/dlt645-index.md` |
| DL/T 698.45 | 电能信息采集与管理系统通信 | `bus/power-rtu/dlt645-index.md` |
| CJ/T 188-2018 | 户用计量仪表数据传输技术条件 | `bus/power-rtu/cjt188-index.md` |
| HJ 212-2017 | 污染物在线监控系统数据传输标准 | `bus/power-rtu/hj212-index.md` |
| SL 651-2014 | 水文监测数据通信规约 | `bus/power-rtu/sl651-index.md` |
| SZY 206-2016 | 水资源监测数据传输规约 | `bus/power-rtu/szy206-index.md` |
| SL/T 427-2014 | 水资源监测数据传输补充规定 | `bus/power-rtu/slt427-index.md` |

## 网络 / TSN / IoT

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| IEEE 802.3 | Ethernet 物理层与 MAC | `bus/industrial/ethernet-deep-dive.md` |
| IEEE 802.1Q | VLAN、优先级与服务质量管理 | `bus/industrial/ethernet-tsn-practical.md` |
| IEEE 802.1AS | gPTP 时间同步 | `bus/industrial/ethernet-tsn-practical.md` |
| IEEE 802.1Qbv | 时间感知整形 | `bus/industrial/ethernet-tsn-practical.md` |
| IEEE 802.1Qav | 基于信用的整形 | `bus/industrial/ethernet-tsn-practical.md` |
| IEEE 802.1CB | 帧复制与消除 | `bus/industrial/ethernet-tsn.md` |
| IEEE 802.11 | 无线局域网 | `bus/wireless-iot/` |
| IEEE 802.15.1 | 无线个人区域网络 / 蓝牙 | `bus/wireless-iot/ble-index.md` |
| IEEE 802.15.4 | 低速率无线个人区域网络 | `bus/wireless-iot/zigbee-index.md` |
| RFC 791 / 793 / 768 | IPv4、TCP、UDP | `bus/industrial/ethernet-deep-dive.md` |
| RFC 7252 | CoAP | `bus/industrial/mqtt.md` |
| MQTT 3.1.1 / 5.0 | MQTT 消息传输协议 | `bus/industrial/mqtt.md` |

## USB / PCIe / 显示 / MIPI

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| USB 2.0 | 低速、全速、高速 USB | `bus/usb/usb-index.md` |
| USB 3.2 | SuperSpeed USB 及速率扩展 | `bus/usb/usb-index.md` |
| USB4 | 高速隧道、供电与显示复用 | `bus/usb/usb-index.md` |
| USB Device Class Specifications | CDC、HID、MSC、UVC、UAC 等类规范 | `bus/usb/usb-class-drivers.md` |
| USB DFU 1.1 | 设备固件升级 | `bus/usb/usb-dfu.md` |
| PCI Express Base Specification | PCIe 物理层、链路层、事务层 | `bus/onboard/pcie-practical.md` |
| PCI Express CEM Specification | PCIe 连接器、供电与机械 | `bus/onboard/pcie-practical.md` |
| MIPI CSI-2 | 摄像头串行接口 | `bus/display/mipi-csi-dsi-deep-dive.md` |
| MIPI DSI | 显示串行接口 | `bus/display/mipi-csi-dsi-deep-dive.md` |
| MIPI D-PHY / C-PHY | MIPI 物理层 | `bus/display/mipi-csi-dsi-deep-dive.md` |
| HDMI 2.1 | 高清多媒体接口 | `bus/display/hdmi-edp-deep-dive.md` |
| eDP 1.4 / 1.5 | 嵌入式 DisplayPort | `bus/display/hdmi-edp-deep-dive.md` |
| DisplayPort 2.0 | 高速显示接口 | `bus/display/hdmi-edp-deep-dive.md` |
| HDCP 2.3 | 高带宽数字内容保护 | `bus/display/hdmi-edp-deep-dive.md` |
| E-EDID | 显示器能力描述 | `bus/display/hdmi-edp-practical.md` |

## 无线 / 卫星

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| Bluetooth Core Specification | BLE 广播、连接、GATT、ATT、HCI | `bus/wireless-iot/ble-index.md` |
| ZigBee 3.0 | ZigBee 网络层、ZCL、设备对象 | `bus/wireless-iot/zigbee-index.md` |
| Thread 1.3 | 基于 IPv6 的低功耗网状网络 | `bus/wireless-iot/thread-index.md` |
| Matter 1.x | 跨生态智能家居应用层 | `bus/wireless-iot/matter-index.md` |
| LoRaWAN 1.0.4 | LoRa 广域网入网、ADR、MAC 层 | `bus/wireless-iot/lora-index.md` |
| 3GPP LTE / NB-IoT | 蜂窝 IoT 接入、PSM、eDRX | `bus/wireless-iot/lte-iot-index.md` |
| Iridium SBD | 铱星短突发数据 | `bus/wireless-iot/satellite-iot-index.md` |
| Cospas-Sarsat | 卫星搜救与 406 MHz 信标 | `bus/wireless-iot/plb-index.md` |
| 北斗短报文 | 北斗卫星短报文通信 | `bus/wireless-iot/satellite-iot-index.md` |

## 功能安全 / 网络安全 / EMC

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| IEC 61508 | 功能安全通用标准 | `guides/engineering/COMMUNICATION_SECURITY_SAFETY.md` |
| ISO 26262 | 汽车功能安全 | `guides/engineering/COMMUNICATION_SECURITY_SAFETY.md` |
| IEC 62443 | 工业控制系统网络安全 | `guides/engineering/COMMUNICATION_SECURITY_SAFETY.md` |
| ISO 21434 | 汽车网络安全工程 | `guides/engineering/COMMUNICATION_SECURITY_SAFETY.md` |
| IEC 61000-4-2 | 静电放电抗扰度 | `guides/engineering/RELIABILITY_GUIDE.md` |
| IEC 61000-4-4 | 电快速瞬变脉冲群抗扰度 | `guides/engineering/RELIABILITY_GUIDE.md` |
| IEC 61000-4-5 | 浪涌抗扰度 | `guides/engineering/RELIABILITY_GUIDE.md` |
| CISPR 25 | 车辆部件辐射发射 | `guides/engineering/RELIABILITY_GUIDE.md` |
| ISO 11452 | 车辆部件辐射抗扰度 | `guides/engineering/RELIABILITY_GUIDE.md` |

## 关联文档

- [ACRONYMS](ACRONYMS.md)：缩写与标准编号速查。
- [GLOSSARY](GLOSSARY.md)：协议术语与工程概念。
- [TOOLS](TOOLS.md)：测量、抓包和自动化工具。
- [DOC_TEMPLATES](DOC_TEMPLATES.md)：标准文档结构模板。
- [知识库索引](../INDEX.md)：按协议查找正文。
