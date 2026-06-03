# Communication Learning Plan

## 目标

本计划用于有序深入芯片间通信知识库。学习路径从基础外设接口开始，逐步进入工业总线、网络通信、高速接口和专题调试。

## 阶段 1：基础接口打牢

目标：掌握板内常见低速/中速通信接口，能够独立完成接线、初始化、抓波形和基础故障定位。

1. `UART`

   已完成文档：

   - `basic/uart-practical.md`
   - `basic/uart-deep-dive.md`

   重点能力：

   - TX/RX/GND 接线。
   - 波特率和 8N1。
   - 字节流分帧。
   - DMA + IDLE 接收。
   - 波特率误差和现场排障。

2. `I2C`

   已完成文档：

   - `basic/i2c-practical.md`
   - `basic/i2c-deep-dive.md`

   重点能力：

   - 上拉电阻和总线电容。
   - 7-bit/8-bit 地址。
   - Repeated START。
   - Clock Stretching。
   - 总线恢复和 MUX。

3. `SPI`

   已完成文档：

   - `basic/spi-practical.md`
   - `basic/spi-deep-dive.md`

   重点能力：

   - CPOL/CPHA。
   - CS 事务边界。
   - dummy cycle。
   - SPI Flash 命令。
   - QSPI/OSPI 基础。

## 阶段 2：工业串行与现场总线

目标：理解长距离、抗干扰、多设备总线设计，能够调试工业仪表、采集模块、电机驱动和现场设备。

1. `RS485 + Modbus RTU`

   已完成文档：

   - `bus/rs485-modbus-rtu-practical.md`
   - `bus/rs485-modbus-rtu-deep-dive.md`

   重点能力：

   - DE/RE 方向控制。
   - 终端电阻和偏置。
   - 隔离与浪涌防护。
   - Modbus RTU 帧间隔和 CRC。
   - 寄存器地址偏移和主站轮询。

2. `CAN + CANopen`

   已完成文档：

   - `bus/can-canopen-practical.md`
   - `bus/can-canopen-deep-dive.md`

   重点能力：

   - CANH/CANL 和终端。
   - 仲裁和错误状态。
   - 标准帧/扩展帧/CAN FD。
   - CANopen 对象字典。
   - SDO/PDO/NMT/Heartbeat。
   - CiA 402 电机状态机。

3. `LIN`

   后续建议文档：

   - `bus/lin.md`

   重点能力：

   - 单线车身总线。
   - 主从调度。
   - Break/Sync/Identifier/Data/Checksum。

## 阶段 3：I2C 生态扩展与电源管理

目标：理解系统管理、电源管理和下一代双线总线。

1. `I3C`

   已完成文档：

   - `bus/i3c.md`
   - `bus/i3c-topic.md`
   - `bus/i3c-deep-dive.md`

   重点能力：

   - 动态地址分配。
   - CCC。
   - IBI。
   - Hot-Join。
   - I2C 混挂限制。

2. `SMBus / PMBus`

   已完成文档：

   - `bus/smbus-pmbus-practical.md`

   重点能力：

   - SMBus 事务。
   - PEC。
   - SMBALERT。
   - PMBus 命令。
   - Linear 数据格式。
   - PAGE 和电源故障状态。

## 阶段 4：通用主机外设与网络

目标：理解主机枚举、协议栈、网络分层和嵌入式联网。

1. `USB`

   已完成文档：

   - `bus/usb-practical.md`

   重点能力：

   - Host/Device/OTG。
   - 枚举和描述符。
   - Endpoint。
   - Control/Bulk/Interrupt/Isochronous。
   - CDC/HID/MSC。

2. `Ethernet + Modbus TCP`

   已完成文档：

   - `bus/ethernet-modbus-tcp-practical.md`

   后续建议深化：

   - `bus/ethernet-deep-dive.md`
   - `bus/modbus-tcp-deep-dive.md`

   重点能力：

   - MAC/PHY。
   - RMII/MII/RGMII。
   - ARP/IP/TCP/UDP。
   - TCP 字节流。
   - Modbus TCP MBAP。
   - Wireshark 排障。

## 阶段 5：高速接口与图像显示

目标：理解高速差分链路、显示和摄像头调试、高性能系统互联。

1. `MIPI CSI/DSI`

   已完成文档：

   - `bus/mipi-csi-dsi-debug.md`

   后续建议深化：

   - `bus/mipi-csi-deep-dive.md`
   - `bus/mipi-dsi-deep-dive.md`

   重点能力：

   - D-PHY Lane。
   - 摄像头 I2C 初始化。
   - MCLK/RESET/电源时序。
   - RAW/YUV 像素格式。
   - DSI command/video mode。
   - 黑屏、花屏、无图排查。

2. `PCIe`

   后续建议文档：

   - `bus/pcie.md`
   - `bus/pcie-practical.md`

   重点能力：

   - Root Complex 和 Endpoint。
   - Lane 和 Gen。
   - 配置空间。
   - BAR。
   - DMA。
   - 链路训练和信号完整性。

3. `SDIO`

   后续建议文档：

   - `bus/sdio.md`
   - `bus/sdio-practical.md`

   重点能力：

   - CLK/CMD/DAT0~3。
   - 1-bit/4-bit 模式。
   - Wi-Fi 模块驱动。
   - 固件、设备树和中断。

## 推荐下一步

优先继续：

```text
Ethernet Deep Dive
```

原因：

- 已经完成 USB Host/Device 体系。
- Ethernet 是网络通信和工业以太网的基础。
- 后续 Modbus TCP、EtherCAT、PROFINET 都依赖 Ethernet 分层理解。

建议下一篇文档：

```text
bus/ethernet-deep-dive.md
```

建议覆盖：

- MAC/PHY。
- MII/RMII/RGMII。
- MDIO/MDC。
- Ethernet Frame。
- ARP/IP/TCP/UDP。
- TCP 字节流。
- Wireshark 排障。
