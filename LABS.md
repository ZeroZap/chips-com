# Labs Roadmap

## 目标

本文给出从入门到进阶的实验路线，帮助把文档知识变成可操作经验。

## 基础实验

1. GPIO 控制 LED。
2. GPIO 读取按键并去抖。
3. PWM 调光 LED。
4. ADC 读取电位器。
5. UART 打印日志。
6. UART 实现简单命令行。

## 板内总线实验

1. I2C 扫描设备地址。
2. I2C 读取传感器 ID。
3. I2C EEPROM 页写和 ACK polling。
4. SPI 读取 Flash JEDEC ID。
5. SPI Flash 读写擦除。
6. QSPI memory-mapped 读取。
7. I2S 播放固定音频数据。

## 工业总线实验

1. USB-RS485 工具读取 Modbus 从站。
2. MCU 实现 Modbus RTU 主站。
3. MCU 实现 Modbus RTU 从站。
4. CAN 两节点互发标准帧。
5. CANopen 读取对象字典。
6. CANopen 控制电机进入 Operation Enabled。
7. LIN Master 发送调度帧。

## 网络和主机外设实验

1. USB CDC 虚拟串口。
2. USB HID 键盘或自定义 HID。
3. Ethernet ping。
4. TCP echo server。
5. Modbus TCP server。
6. SDIO Wi-Fi 模块枚举。
7. PCIe Endpoint 枚举。

## 图像显示实验

1. SPI 小屏显示纯色。
2. MIPI DSI 屏初始化和纯色测试。
3. I2C 读取摄像头 Sensor ID。
4. MIPI CSI 输出 RAW 图。
5. ISP 转换显示图像。

## 工具实验

1. 示波器测 I2C 上升沿。
2. 逻辑分析仪解码 SPI。
3. CAN 分析仪观察错误帧。
4. Wireshark 抓 ARP 和 Modbus TCP。
5. USB 日志观察枚举。

## 进阶目标

- 为每个协议保留一套最小可复现实验。
- 每个实验记录接线、参数、波形、日志和故障现象。
- 把实验结果反向补充到对应协议文档。
