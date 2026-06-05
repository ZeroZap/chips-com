# Troubleshooting Quick Reference

## 目标

本文提供快速故障速查表，适合现场或调试时快速定位方向。

## 无响应

| 协议 | 优先检查 |
| --- | --- |
| UART | TX/RX、GND、波特率、电平 |
| I2C | 电源、RESET、上拉、地址、SCL/SDA 空闲高 |
| SPI | CS、Mode、MOSI/MISO、供电 |
| RS485 | A/B、DE/RE、地址、串口参数 |
| CAN | 收发器、终端、波特率、ACK |
| USB | VBUS、D+/D-、描述符、时钟 |
| Ethernet | PHY Link、MDIO、IP、ARP |
| MIPI | 电源时序、I2C ID、MCLK、RESET |

## 偶发错误

| 方向 | 可能原因 |
| --- | --- |
| 电气 | 噪声、线太长、阻抗不匹配、上拉不足 |
| 时序 | 采样点、波特率误差、clock stretching、dummy cycle |
| 软件 | 缓冲区溢出、DMA/cache、任务阻塞、超时过短 |
| 协议 | CRC、长度、状态机、重试策略 |

## 低速正常，高速失败

| 协议 | 优先检查 |
| --- | --- |
| I2C | 上拉、电容、电平转换器 |
| SPI | Mode、MISO 延迟、线长、振铃 |
| CAN | 采样点、终端、拓扑 |
| Ethernet | PHY、双工、RGMII delay、线缆 |
| SDIO | DAT 线、上拉、bus-width、时钟 |
| MIPI | Lane rate、走线、ESD 电容 |

## 数据值不对

| 类型 | 优先检查 |
| --- | --- |
| 寄存器 | 地址偏移、字节序、PAGE、权限 |
| 传感器 | 转换时间、data ready、单位换算 |
| Modbus | 40001 偏移、word swap、scale |
| PMBus | Linear11/Linear16、Direct 格式、PAGE |
| CANopen | 对象字典、PDO 映射、单位缩放 |
| 图像 | RAW/YUV/RGB、Bayer order、stride |

## 枚举失败

| 协议 | 优先检查 |
| --- | --- |
| USB | 描述符、Endpoint、VID/PID、VBUS |
| PCIe | LTSSM、PERST#、REFCLK、Lane、BAR |
| SDIO | CLK/CMD/DAT、firmware、设备树 |
| I3C | DAA、动态地址、CCC、混挂 I2C |

## 推荐最小验证

| 协议 | 最小验证 |
| --- | --- |
| UART | 回环或打印固定字符串 |
| I2C | 扫描地址 + 读 ID |
| SPI | 读 JEDEC ID |
| RS485/Modbus | 上位机读单寄存器 |
| CAN | 两节点互发固定 ID |
| CANopen | 读 1000h 或 1018h |
| Ethernet | Link + ARP + ping |
| USB | 枚举 + 读描述符 |
| MIPI CSI | 读 Sensor ID + streaming |
| MIPI DSI | 初始化 + 纯色测试图 |
