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

## 实战深入路径

完成基础概念后，按以下顺序进入工程调试文档：

1. `basic/uart-practical.md`：UART 接线、参数、乱码和字节流分帧。
2. `basic/i2c-practical.md`：I2C 上拉、地址扫描、寄存器读写和总线恢复。
3. `basic/spi-practical.md`：SPI Mode、片选、dummy byte 和多设备共享。
4. `bus/rs485-modbus-rtu-practical.md`：RS485 方向控制、终端电阻、Modbus RTU 帧和 CRC。
5. `bus/can-canopen-practical.md`：CAN 物理层、CANopen SDO/PDO/NMT 和电机调试入口。
6. `bus/i3c-topic.md`：I3C 动态地址、CCC、IBI 和 I2C 混挂边界。
7. `bus/ethernet-modbus-tcp-practical.md`：Ethernet 链路、TCP 字节流和 Modbus TCP MBAP。
8. `bus/mipi-csi-dsi-debug.md`：MIPI CSI/DSI 电源、I2C 初始化、Lane、像素格式和黑屏/无图定位。
