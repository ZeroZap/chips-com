# Chips Communication Knowledge Base

这是一个面向芯片间通信的知识库，用于整理从基础外设接口到成熟总线协议的通信体系。

## 分类原则

通信内容按抽象层级划分：

1. `basic/`：基础通信接口与电气/时序机制。
2. `bus/`：建立在基础接口之上的成熟总线、协议或网络体系。

`basic` 关注“芯片如何通过某种外设接口收发数据”，`bus` 关注“多个设备如何通过协议规则组织通信”。

## 推荐目录结构

```text
chips-com/
├── basic/
│   ├── README.md
│   ├── uart.md
│   ├── i2c.md
│   ├── spi.md
│   ├── gpio.md
│   ├── pwm.md
│   ├── adc-dac.md
│   ├── can-phy.md
│   └── ethernet-phy.md
├── bus/
│   ├── README.md
│   ├── modbus.md
│   ├── can.md
│   ├── i3c.md
│   ├── smbus.md
│   ├── pmbus.md
│   ├── one-wire.md
│   ├── usb.md
│   ├── ethernet.md
│   └── fieldbus.md
└── README.md
```

## 文档模板

每个协议或接口文档建议包含以下部分：

```markdown
# 名称

## 定位

说明它解决什么通信问题，常见于哪些芯片或系统。

## 基本概念

说明主从关系、拓扑、信号线、时钟、帧结构、地址、仲裁等核心概念。

## 硬件连接

说明引脚、上拉/下拉、终端电阻、电平转换、隔离、线缆长度等硬件注意点。

## 通信流程

说明初始化、发送、接收、应答、错误处理等典型流程。

## 优点与限制

说明速度、距离、成本、复杂度、实时性、抗干扰等取舍。

## 典型应用

列出传感器、存储器、电机控制、工业采集、板间通信等应用场景。

## 与相关协议对比

说明它和相近接口或总线的区别，例如 SPI vs I2C、UART vs RS485、CAN vs Modbus。
```

## 学习路径

建议从基础接口开始，再进入总线协议：

1. `GPIO`：理解数字电平、输入输出、边沿、中断。
2. `UART`：理解异步串口、波特率、帧格式。
3. `I2C`：理解同步串行、地址、开漏、上拉、多设备挂载。
4. `SPI`：理解高速同步串行、片选、模式、全双工。
5. `RS485/CAN PHY`：理解差分信号、终端匹配、长距离抗干扰。
6. `Modbus/CAN/USB/Ethernet`：理解成熟协议如何定义设备、帧、错误处理和网络行为。

完整的阶段化学习安排见 `LEARNING_PLAN.md`。

跨协议排障方法见 `DEBUG_PLAYBOOK.md`。

协议选型矩阵见 `PROTOCOL_SELECTION.md`。

## 实战深入路径

完成基础概念后，按以下顺序进入工程调试文档：

1. `basic/uart-practical.md`：UART 接线、参数、乱码和字节流分帧。
2. `basic/uart-deep-dive.md`：UART 波特率误差、过采样、DMA、硬件流控和量产排障。
3. `basic/i2c-practical.md`：I2C 上拉、地址扫描、寄存器读写和总线恢复。
4. `basic/i2c-deep-dive.md`：I2C 上拉/电容、地址、Clock Stretching、总线恢复、MUX 和器件特性。
5. `basic/spi-practical.md`：SPI Mode、片选、dummy byte 和多设备共享。
6. `basic/spi-deep-dive.md`：SPI 采样模式、CS 边界、dummy cycle、Flash 命令、高速信号和 QSPI/OSPI。
7. `bus/rs485-modbus-rtu-practical.md`：RS485 方向控制、终端电阻、Modbus RTU 帧和 CRC。
8. `bus/rs485-modbus-rtu-deep-dive.md`：RS485 半双工、隔离防护、帧间隔、寄存器偏移、主站轮询和现场排障。
9. `bus/can-canopen-practical.md`：CAN 物理层、CANopen SDO/PDO/NMT 和电机调试入口。
10. `bus/can-canopen-deep-dive.md`：CAN 位时序、仲裁、错误状态、CANopen PDO/SDO/NMT 和 CiA 402。
11. `bus/i3c-topic.md`：I3C 动态地址、CCC、IBI 和 I2C 混挂边界。
12. `bus/i3c-deep-dive.md`：I3C 动态地址、CCC、IBI、Hot-Join、SDR/HDR、混合总线和驱动模型。
13. `bus/smbus-pmbus-practical.md`：SMBus 事务、PEC、Alert、PMBus 命令、Linear 格式、PAGE 和故障状态。
14. `bus/usb-practical.md`：USB Host/Device、枚举、描述符、Endpoint、CDC/HID/MSC 和 Type-C 基础。
15. `bus/ethernet-deep-dive.md`：Ethernet MAC/PHY、RMII/RGMII、MDIO、帧、ARP、TCP/UDP 和 Wireshark 排障。
16. `bus/ethernet-modbus-tcp-practical.md`：Ethernet 链路、TCP 字节流和 Modbus TCP MBAP。
17. `bus/mipi-csi-dsi-debug.md`：MIPI CSI/DSI 电源、I2C 初始化、Lane、像素格式和黑屏/无图定位。
18. `bus/mipi-csi-dsi-deep-dive.md`：MIPI D-PHY、CSI/DSI 初始化、RAW/YUV/RGB、显示时序和图像链路排障。
19. `bus/pcie-practical.md`：PCIe Root Complex/Endpoint、Lane、配置空间、BAR、MSI 和 DMA。
20. `bus/sdio-practical.md`：SDIO CLK/CMD/DAT、Wi-Fi 模块、固件、设备树和枚举排障。
21. `bus/one-wire-practical.md`：1-Wire 上拉、时序、ROM ID、DS18B20 和寄生供电。
22. `bus/lin-practical.md`：LIN 主从调度、Break/Sync/ID/Checksum 和车身低速节点。
23. `bus/ethercat-deep-dive.md`：EtherCAT 主从、ESC、On-the-fly、PDO、Mailbox、DC 和 WKC。
24. `bus/industrial-ethernet-comparison.md`：Modbus TCP、PROFINET、EtherNet/IP 和 EtherCAT 选型对比。
