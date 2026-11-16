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
8. PMBus 读取 STATUS_WORD、READ_VOUT/IOUT，记录 raw word 和 Linear 换算值。

## 工业总线实验

1. USB-RS485 工具读取 Modbus 从站。
2. MCU 实现 Modbus RTU 主站。
3. MCU 实现 Modbus RTU 从站。
4. CAN 两节点互发标准帧。
5. CANopen 读取对象字典。
6. CANopen 控制电机进入 Operation Enabled。
7. LIN Master 发送调度帧。
8. UDS over ISO-TP 读取 DID、执行安全访问并模拟 Transfer Data 分块传输。

## 网络和主机外设实验

1. USB CDC 虚拟串口。
2. USB HID 键盘或自定义 HID。
3. Ethernet ping。
4. TCP echo server。
5. Modbus TCP server。
6. SDIO Wi-Fi 模块枚举。
7. PCIe Endpoint 枚举。
8. TSN 单跳测试 gPTP offset、VLAN PCP、Qbv 开关和 p99/p999 延迟。
9. USB DFU 分块下载测试镜像，验证 CRC、metadata 和失败回退。

## 图像显示实验

1. SPI 小屏显示纯色。
2. MIPI DSI 屏初始化和纯色测试。
3. I2C 读取摄像头 Sensor ID。
4. MIPI CSI 输出 RAW 图。
5. ISP 转换显示图像。
6. FPD-Link/GMSL 读取 Deserializer ID、Link Lock 和远端 Sensor ID。
7. FPD-Link/GMSL 对比短线、目标线束和降带宽时的 lock drop counter。

## 工具实验

1. 示波器测 I2C 上升沿。
2. 逻辑分析仪解码 SPI。
3. CAN 分析仪观察错误帧。
4. Wireshark 抓 ARP 和 Modbus TCP。
5. USB 日志观察枚举。
6. 示波器测 SerDes PoC 远端电压启动和负载瞬态。
7. Wireshark 抓 PTP、VLAN PCP 和 TSN 实时流周期。
8. CAN 分析仪记录 ISO-TP FF/FC/CF、BS、STmin 和 UDS P2/P2*。
9. USB 抓包或 DFU 工具日志记录 download、getstatus、manifest 和 reset 流程。

## 进阶目标

- 为每个协议保留一套最小可复现实验。
- 每个实验记录接线、参数、波形、日志和故障现象。
- 把实验结果反向补充到对应协议文档。
