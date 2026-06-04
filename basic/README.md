# Basic Communication Interfaces

`basic` 用于整理芯片和外设之间的基础通信接口。这里的重点是硬件连接、信号时序、寄存器配置和单点通信机制。

## 建议分类

### 通用数字接口

- `gpio.md`：通用输入输出、上下拉、中断、开漏/推挽。
- `pwm.md`：占空比、频率、定时器、调光和电机控制。
- `jtag-swd.md`：芯片下载调试接口、JTAG、SWD、VTref 和量产烧录注意事项。

### 串行通信接口

- `uart.md`：异步串口、波特率、起始位/停止位、校验位。
- `uart-practical.md`：UART 接线、参数、乱码、分帧和 TTL/RS232/RS485 区分。
- `uart-deep-dive.md`：UART 波特率误差、过采样、DMA、流控、分帧和量产排障。
- `i2c.md`：双线同步总线、地址、ACK/NACK、上拉电阻。
- `i2c-practical.md`：I2C 上拉、地址扫描、寄存器读写、Repeated START 和总线恢复。
- `i2c-deep-dive.md`：I2C 上拉/电容、地址、Clock Stretching、总线恢复、MUX 和器件特性。
- `spi.md`：四线同步总线、片选、CPOL/CPHA、全双工通信。
- `spi-practical.md`：SPI Mode、片选时序、dummy byte、多设备共享和故障定位。
- `spi-deep-dive.md`：SPI 采样模式、CS 边界、dummy cycle、Flash 命令、高速信号和 QSPI/OSPI。
- `qspi-ospi.md`：SPI Flash 高速扩展、Quad/Octal 数据线、dummy cycle、XIP。
- `i2s.md`：音频串行接口、采样率、左右声道时钟、位时钟。

### 模拟与混合信号接口

- `adc-dac.md`：模数/数模转换、采样率、分辨率、参考电压。
- `comparator.md`：比较器、阈值、电平检测。

### 物理层相关

- `rs232-rs485.md`：串口电平转换、差分传输、半双工通信。
- `can-phy.md`：CAN 物理层、差分信号、终端电阻。
- `ethernet-phy.md`：以太网 PHY、MII/RMII/RGMII、磁性器件。
- `lvds.md`：低压差分信号、显示 LVDS、差分阻抗和屏线调试。

## 收录边界

放在 `basic` 的内容通常满足以下条件：

- 主要描述芯片外设本身，而不是完整应用层协议。
- 重点是信号线、时序、收发机制、硬件连接。
- 可以作为多个上层总线或协议的基础。

例如：`UART` 放在 `basic`，但 `Modbus RTU` 放在 `bus`；`RS485` 作为物理层可放在 `basic`，但基于 RS485 的完整协议应放在 `bus`。
