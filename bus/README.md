# Bus And Protocols

`bus` 用于整理建立在基础通信接口之上的成熟总线、协议或网络体系。这里的重点是拓扑结构、寻址、帧格式、协议状态机、错误处理和多设备协作。

## 建议分类

### 基于串口/差分链路的总线

- `modbus.md`：Modbus RTU/TCP、寄存器模型、功能码、主从通信。
- `rs485-modbus-rtu-practical.md`：RS485 方向控制、终端/偏置、Modbus RTU 帧、CRC 和调试流程。
- `rs485-modbus-rtu-deep-dive.md`：RS485 半双工、隔离防护、帧间隔、寄存器偏移、主站轮询和现场排障。
- `dmx512.md`：灯光控制总线、帧结构、单向广播。
- `lin.md`：车身低速网络、主从调度、低成本单线通信。

### 基于 I2C 生态的总线

- `smbus.md`：系统管理总线、电池和主板管理场景。
- `pmbus.md`：电源管理总线、电源模块监控与控制。
- `i3c.md`：I2C 演进总线、动态地址、带内中断、更高速率。
- `i3c-topic.md`：I3C 工程专题、CCC、IBI、动态地址和 I2C 混挂边界。

### 工业与汽车现场总线

- `can.md`：CAN/CAN FD、仲裁、错误处理、车载和工业控制。
- `canopen.md`：CANopen 对象字典、PDO/SDO、设备模型。
- `can-canopen-practical.md`：CAN 物理层、CANopen COB-ID、SDO/PDO/NMT 和电机调试流程。
- `profibus.md`：工业现场总线、主从控制、过程自动化。
- `ethercat.md`：实时工业以太网、从站级联、分布式时钟。

### 通用高速总线与网络

- `usb.md`：USB 设备枚举、端点、传输类型、主机控制。
- `ethernet.md`：以太网 MAC/PHY、帧、交换、TCP/IP 入口。
- `ethernet-modbus-tcp-practical.md`：Ethernet 链路、TCP 字节流、Modbus TCP MBAP 和 Wireshark 调试。
- `pcie.md`：高速点对点总线、Lane、事务层、DMA 场景。

### 简单设备总线

- `one-wire.md`：单线通信、寄生供电、温度传感器等低速设备。
- `sdio.md`：SD 卡和 Wi-Fi 模块常见接口。
- `mipi.md`：显示和摄像头接口，如 DSI、CSI。
- `mipi-csi-dsi-debug.md`：MIPI CSI/DSI 电源时序、I2C 初始化、Lane、像素格式和黑屏/无图定位。

## 收录边界

放在 `bus` 的内容通常满足以下条件：

- 已经定义了完整的通信规则，而不只是电气接口。
- 支持多个节点、设备寻址、协议帧、错误处理或标准化设备模型。
- 常用于板间通信、工业控制、车载网络、主机外设连接或系统级互联。

例如：`SPI` 放在 `basic`，但基于 SPI 的 SD 卡协议可放在 `bus`；`CAN PHY` 放在 `basic`，但 `CAN` 和 `CANopen` 放在 `bus`。
