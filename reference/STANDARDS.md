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
| ISO 11898-1 | CAN 数据链路层与帧格式，含经典 CAN、CAN FD | [[basic/can-deep-dive\|can-deep-dive]]、[[basic/can-fd-and-can-xl\|can-fd-and-can-xl]] |
| ISO 11898-2 | 高速 CAN 物理层、差分电平、终端与位时序 | [[basic/can-phy\|can-phy]]、[[basic/can-practical\|can-practical]] |
| ISO 11898-3 | 低速容错 CAN 物理层 | [[basic/can-phy\|can-phy]] |
| ISO 16845-1 / -2 | CAN 一致性测试方法 | [[basic/can-deep-dive\|can-deep-dive]] |
| ISO 15765-2 | CAN 上的诊断传输协议（ISO-TP） | [[bus/automotive/iso-tp-index\|iso-tp-index]] |
| ISO 14229-1 ~ -7 | 统一诊断服务（UDS） | [[bus/automotive/uds-index\|uds-index]] |
| SAE J1939-21 | J1939 数据链路层与传输协议 | [[bus/automotive/j1939-index\|j1939-index]] |
| SAE J1939-71 | J1939 车辆应用层 | [[bus/automotive/j1939-protocol-spec\|j1939-protocol-spec]] |
| SAE J1939-73 | J1939 诊断应用层 | [[bus/automotive/j1939-index\|j1939-index]] |
| SAE J1939-81 | J1939 网络管理与地址声明 | [[bus/automotive/j1939-network-management\|j1939-network-management]] |
| SAE J1979 / ISO 15031-5 | OBD-II 诊断测试模式 | [[bus/automotive/obd2-index\|obd2-index]] |
| ISO 27145-1 ~ -4, -6 | WWH-OBD 全球统一车载诊断 | [[bus/automotive/wwh-obd-index\|wwh-obd-index]] |
| CiA 301 | CANopen 应用层与通信规范 | [[bus/automotive/canopen-index\|canopen-index]] |
| CiA 402 | CANopen 驱动与运动控制行规 | [[bus/automotive/canopen-safety\|canopen-safety]] |
| CiA 1301 | CANopen FD 规范 | [[bus/automotive/canopen-index\|canopen-index]] |
| ISO 26262 | 汽车功能安全 | [[guides/engineering/COMMUNICATION_SECURITY_SAFETY\|COMMUNICATION_SECURITY_SAFETY]] |
| ISO 21434 | 汽车网络安全工程 | [[guides/engineering/COMMUNICATION_SECURITY_SAFETY\|COMMUNICATION_SECURITY_SAFETY]] |
| UNECE R155 / R156 | 车辆网络安全与软件更新法规 | [[guides/engineering/COMMUNICATION_SECURITY_SAFETY\|COMMUNICATION_SECURITY_SAFETY]] |
| ISO 16750-1 ~ -5 | 汽车电子环境条件与试验 | [[guides/engineering/RELIABILITY_GUIDE\|RELIABILITY_GUIDE]] |
| ISO 7637-2 | 汽车电源线瞬态传导抗扰度 | [[guides/engineering/RELIABILITY_GUIDE\|RELIABILITY_GUIDE]] |
| ISO 10605 | 汽车电子静电放电试验 | [[guides/engineering/RELIABILITY_GUIDE\|RELIABILITY_GUIDE]] |
| CISPR 25 | 车辆电子部件辐射发射 | [[guides/engineering/RELIABILITY_GUIDE\|RELIABILITY_GUIDE]] |
| ISO 11452 | 车辆电子部件辐射抗扰度 | [[guides/engineering/RELIABILITY_GUIDE\|RELIABILITY_GUIDE]] |

## 工业自动化 / 工业以太网

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| IEC 61158 | 工业通信网络现场总线规范 | [[bus/industrial/industrial-ethernet-comparison\|industrial-ethernet-comparison]] |
| IEC 61784 | 现场总线通信行规 | [[bus/industrial/industrial-ethernet-comparison\|industrial-ethernet-comparison]] |
| IEC 62443 | 工业自动化与控制系统网络安全 | [[guides/engineering/COMMUNICATION_SECURITY_SAFETY\|COMMUNICATION_SECURITY_SAFETY]] |
| IEC 61131 | 可编程控制器编程与系统 | [[bus/industrial/modbus\|modbus]] |
| Modbus Application Protocol | Modbus 应用层与功能码 | [[bus/industrial/modbus\|modbus]] |
| Modbus over Serial Line | Modbus RTU / ASCII 串行链路 | [[bus/industrial/rs485-modbus-rtu-deep-dive\|rs485-modbus-rtu-deep-dive]] |
| Modbus Messaging on TCP/IP | Modbus TCP 与 MBAP | [[bus/industrial/ethernet-modbus-tcp-practical\|ethernet-modbus-tcp-practical]] |
| EtherCAT ETG Specification | EtherCAT 主从站、状态机与 PDO | [[bus/industrial/ethercat-deep-dive\|ethercat-deep-dive]] |
| PROFINET IEC 61158 / 61784 | PROFINET IO、RT/IRT、GSDML | [[bus/industrial/profinet-deep-dive\|profinet-deep-dive]] |
| PROFIBUS IEC 61158 / 61784 | PROFIBUS DP 与 GSD | [[bus/industrial/profibus-deep-dive\|profibus-deep-dive]] |
| EtherNet/IP ODVA | EtherNet/IP、CIP、EDS | [[bus/industrial/ethernet-ip-deep-dive\|ethernet-ip-deep-dive]] |
| IEC 62541 | OPC UA 信息模型、服务与安全 | [[bus/industrial/opcua-index\|opcua-index]] |
| ASHRAE 135 / ISO 16484-5 | BACnet 楼宇自动控制网络 | [[bus/power-rtu/bacnet-index\|bacnet-index]] |
| IEEE 1815 | DNP3 分布式网络协议 | [[bus/power-rtu/dnp3-index\|dnp3-index]] |

## 电力 / 水务 / 表计 / 楼宇

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| IEC 60870-5-101 | 串行远动通信传输规约 | [[bus/power-rtu/iec101-index\|iec101-index]] |
| IEC 60870-5-104 | 以太网远动通信传输规约 | [[bus/power-rtu/iec104-index\|iec104-index]] |
| IEC 61850 | 变电站自动化通信网络与系统 | [[bus/power-rtu/iec61850-index\|iec61850-index]] |
| DL/T 645-2007 | 多功能电能表通信规约 | [[bus/power-rtu/dlt645-index\|dlt645-index]] |
| DL/T 698.45 | 电能信息采集与管理系统通信 | [[bus/power-rtu/dlt645-index\|dlt645-index]] |
| CJ/T 188-2018 | 户用计量仪表数据传输技术条件 | [[bus/power-rtu/cjt188-index\|cjt188-index]] |
| HJ 212-2017 | 污染物在线监控系统数据传输标准 | [[bus/power-rtu/hj212-index\|hj212-index]] |
| SL 651-2014 | 水文监测数据通信规约 | [[bus/power-rtu/sl651-index\|sl651-index]] |
| SZY 206-2016 | 水资源监测数据传输规约 | [[bus/power-rtu/szy206-index\|szy206-index]] |
| SL/T 427-2014 | 水资源监测数据传输补充规定 | [[bus/power-rtu/slt427-index\|slt427-index]] |

## 网络 / TSN / IoT

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| IEEE 802.3 | Ethernet 物理层与 MAC | [[bus/industrial/ethernet-deep-dive\|ethernet-deep-dive]] |
| IEEE 802.1Q | VLAN、优先级与服务质量管理 | [[bus/industrial/ethernet-tsn-practical\|ethernet-tsn-practical]] |
| IEEE 802.1AS | gPTP 时间同步 | [[bus/industrial/ethernet-tsn-practical\|ethernet-tsn-practical]] |
| IEEE 802.1Qbv | 时间感知整形 | [[bus/industrial/ethernet-tsn-practical\|ethernet-tsn-practical]] |
| IEEE 802.1Qav | 基于信用的整形 | [[bus/industrial/ethernet-tsn-practical\|ethernet-tsn-practical]] |
| IEEE 802.1CB | 帧复制与消除 | [[bus/industrial/ethernet-tsn\|ethernet-tsn]] |
| IEEE 802.11 | 无线局域网 | `bus/wireless-iot/` |
| IEEE 802.15.1 | 无线个人区域网络 / 蓝牙 | [[bus/wireless-iot/ble-index\|ble-index]] |
| IEEE 802.15.4 | 低速率无线个人区域网络 | [[bus/wireless-iot/zigbee-index\|zigbee-index]] |
| RFC 791 / 793 / 768 | IPv4、TCP、UDP | [[bus/industrial/ethernet-deep-dive\|ethernet-deep-dive]] |
| RFC 7252 | CoAP | [[bus/industrial/mqtt\|mqtt]] |
| MQTT 3.1.1 / 5.0 | MQTT 消息传输协议 | [[bus/industrial/mqtt\|mqtt]] |

## USB / PCIe / 显示 / MIPI

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| USB 2.0 | 低速、全速、高速 USB | [[bus/usb/usb-index\|usb-index]] |
| USB 3.2 | SuperSpeed USB 及速率扩展 | [[bus/usb/usb-index\|usb-index]] |
| USB4 | 高速隧道、供电与显示复用 | [[bus/usb/usb-index\|usb-index]] |
| USB Device Class Specifications | CDC、HID、MSC、UVC、UAC 等类规范 | [[bus/usb/usb-class-drivers\|usb-class-drivers]] |
| USB DFU 1.1 | 设备固件升级 | [[bus/usb/usb-dfu\|usb-dfu]] |
| PCI Express Base Specification | PCIe 物理层、链路层、事务层 | [[bus/onboard/pcie-practical\|pcie-practical]] |
| PCI Express CEM Specification | PCIe 连接器、供电与机械 | [[bus/onboard/pcie-practical\|pcie-practical]] |
| MIPI CSI-2 | 摄像头串行接口 | [[bus/display/mipi-csi-dsi-deep-dive\|mipi-csi-dsi-deep-dive]] |
| MIPI DSI | 显示串行接口 | [[bus/display/mipi-csi-dsi-deep-dive\|mipi-csi-dsi-deep-dive]] |
| MIPI D-PHY / C-PHY | MIPI 物理层 | [[bus/display/mipi-csi-dsi-deep-dive\|mipi-csi-dsi-deep-dive]] |
| HDMI 2.1 | 高清多媒体接口 | [[bus/display/hdmi-edp-deep-dive\|hdmi-edp-deep-dive]] |
| eDP 1.4 / 1.5 | 嵌入式 DisplayPort | [[bus/display/hdmi-edp-deep-dive\|hdmi-edp-deep-dive]] |
| DisplayPort 2.0 | 高速显示接口 | [[bus/display/hdmi-edp-deep-dive\|hdmi-edp-deep-dive]] |
| HDCP 2.3 | 高带宽数字内容保护 | [[bus/display/hdmi-edp-deep-dive\|hdmi-edp-deep-dive]] |
| E-EDID | 显示器能力描述 | [[bus/display/hdmi-edp-practical\|hdmi-edp-practical]] |

## 无线 / 卫星

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| Bluetooth Core Specification | BLE 广播、连接、GATT、ATT、HCI | [[bus/wireless-iot/ble-index\|ble-index]] |
| ZigBee 3.0 | ZigBee 网络层、ZCL、设备对象 | [[bus/wireless-iot/zigbee-index\|zigbee-index]] |
| Thread 1.3 | 基于 IPv6 的低功耗网状网络 | [[bus/wireless-iot/thread-index\|thread-index]] |
| Matter 1.x | 跨生态智能家居应用层 | [[bus/wireless-iot/matter-index\|matter-index]] |
| LoRaWAN 1.0.4 | LoRa 广域网入网、ADR、MAC 层 | [[bus/wireless-iot/lora-index\|lora-index]] |
| 3GPP LTE / NB-IoT | 蜂窝 IoT 接入、PSM、eDRX | [[bus/wireless-iot/lte-iot-index\|lte-iot-index]] |
| Iridium SBD | 铱星短突发数据 | [[bus/wireless-iot/satellite-iot-index\|satellite-iot-index]] |
| Cospas-Sarsat | 卫星搜救与 406 MHz 信标 | [[bus/wireless-iot/plb-index\|plb-index]] |
| 北斗短报文 | 北斗卫星短报文通信 | [[bus/wireless-iot/satellite-iot-index\|satellite-iot-index]] |

## 功能安全 / 网络安全 / EMC

| 标准 / 规范 | 范围 | 对应文档 |
| --- | --- | --- |
| IEC 61508 | 功能安全通用标准 | [[guides/engineering/COMMUNICATION_SECURITY_SAFETY\|COMMUNICATION_SECURITY_SAFETY]] |
| ISO 26262 | 汽车功能安全 | [[guides/engineering/COMMUNICATION_SECURITY_SAFETY\|COMMUNICATION_SECURITY_SAFETY]] |
| IEC 62443 | 工业控制系统网络安全 | [[guides/engineering/COMMUNICATION_SECURITY_SAFETY\|COMMUNICATION_SECURITY_SAFETY]] |
| ISO 21434 | 汽车网络安全工程 | [[guides/engineering/COMMUNICATION_SECURITY_SAFETY\|COMMUNICATION_SECURITY_SAFETY]] |
| IEC 61000-4-2 | 静电放电抗扰度 | [[guides/engineering/RELIABILITY_GUIDE\|RELIABILITY_GUIDE]] |
| IEC 61000-4-4 | 电快速瞬变脉冲群抗扰度 | [[guides/engineering/RELIABILITY_GUIDE\|RELIABILITY_GUIDE]] |
| IEC 61000-4-5 | 浪涌抗扰度 | [[guides/engineering/RELIABILITY_GUIDE\|RELIABILITY_GUIDE]] |
| CISPR 25 | 车辆部件辐射发射 | [[guides/engineering/RELIABILITY_GUIDE\|RELIABILITY_GUIDE]] |
| ISO 11452 | 车辆部件辐射抗扰度 | [[guides/engineering/RELIABILITY_GUIDE\|RELIABILITY_GUIDE]] |

## 关联文档

- [[reference/ACRONYMS|ACRONYMS]]：缩写与标准编号速查。
- [[reference/GLOSSARY|GLOSSARY]]：协议术语与工程概念。
- [[reference/TOOLS|TOOLS]]：测量、抓包和自动化工具。
- [[reference/DOC_TEMPLATES|DOC_TEMPLATES]]：标准文档结构模板。
- [[INDEX|知识库索引]]：按协议查找正文。
