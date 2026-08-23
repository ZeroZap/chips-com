# Basic Communication Interfaces

`basic` 用于整理芯片和外设之间的基础通信接口。这里的重点是硬件连接、信号时序、寄存器配置和单点通信机制。

## 建议分类

### 通用数字接口

- `gpio.md`：通用输入输出、上下拉、中断、开漏/推挽。
- `pwm.md`：占空比、频率、定时器、调光和电机控制。
- `jtag-swd.md`：芯片下载调试接口、JTAG、SWD、VTref 和量产烧录注意事项。

### 串行通信接口

- `uart.md`：异步串口、波特率、起始位/停止位、校验位。
- `uart-practical.md`：UART 接线、参数、乱码、分帧和 TTL/RS232/RS485 区分（扩）。
- `uart-deep-dive.md`：UART 波特率误差、过采样、DMA、流控、分帧和量产排障（扩）。
- `uart-failure-cases.md`：20 个产线 UART 死机案例（baud 错、RS485 方向、协议分帧、DMA 丢包、ESD 等）。
- `uart-rs485-and-flow-control.md`：RS485 物理层、收发器选型、方向控制时序、硬件流控 RTS/CTS、软件流控 XON/XOFF、实战代码骨架。
- `uart-dma-circular-and-rtos.md`：DMA 接收 + 环形缓冲 + idle 不定长接收 + FreeRTOS/Zephyr/RT-Thread 三平台集成 + 完整代码骨架。
- `uart-index.md`：UART 主题总览导航——5 种读者路径、主题速查矩阵、UART vs SPI vs I2C 选型速查。
- `i2c.md`：双线同步总线、地址、ACK/NACK、上拉电阻。
- `i2c-practical.md`：I2C 上拉、地址扫描、寄存器读写、Repeated START 和总线恢复。
- `i2c-deep-dive.md`：I2C 上拉/电容、地址、Clock Stretching、总线恢复、MUX 和器件特性。
- `i2c-bus-recovery-playbook.md`：I2C 总线被拉低死锁的实战手册——8 步恢复 SOP、STM32 HAL 平台适配、可移植 C 代码骨架、产线故障注入测试方案、面试回答模板。
- `i2c-rtos-integration.md`：RT-Thread / Zephyr / FreeRTOS 三平台集成 bus recovery 的代码模式与对比。
- `i2c-multimaster.md`：多主机仲裁物理原理、隐藏多 master 场景、bus recovery 风险与工程方案。
- `i2c-smbus-timeout.md`：SMBus 三大 timeout 精确数值、与 bus recovery 的关系、常见错误。
- `i2c-linux-fault-injection.md`：Linux i2c-stub / i2c-gpio fault injection / bus_recovery_info 实操与回归测试脚本。
- `i2c-state-machine.md`：I2C 状态机 + DMA + 中断并发模型，常见死锁和竞态解决方案。
- `i2c-failure-cases.md`：20 个产线死机案例，案例驱动的实战参考。
- `i2c-vs-smbus-recovery.md`：I2C vs SMBus bus recovery 行为对比——一句话核心差异、完整对比表、4 种场景行为差异、timeout 数值精确对比、混用策略、选型决策树。
- `i2c-index.md`：I2C 主题总览导航——四种读者路径、主题速查矩阵、学习路径推荐。
- `spi.md`：四线同步总线、片选、CPOL/CPHA、全双工通信。
- `spi-practical.md`：SPI Mode、片选时序、dummy byte、多设备共享和故障定位。
- `spi-deep-dive.md`：SPI 采样模式、CS 边界、dummy cycle、Flash 命令、高速信号和 QSPI/OSPI。
- `spi-practical.md`：SPI Mode、片选时序、dummy byte、多设备共享和故障定位（扩）。
- `spi-failure-cases.md`：20 个产线 SPI 死机案例（Mode 错、CS 时序、Flash 时序、DMA race、信号完整性等）。
- `spi-multislave-and-dma.md`：多从设备共享、菊花链、DMA 模式、中断协作、4 类 race condition 解决方案。
- `spi-rtos-integration.md`：RT-Thread / Zephyr / FreeRTOS 三平台集成模式、mutex 与 reconfig 优化、双缓冲、实战代码骨架。
- `spi-index.md`：SPI 主题总览导航——5 种读者路径、主题速查矩阵、SPI vs I2C 选型速查。
- `qspi-ospi.md`：SPI Flash 高速扩展、Quad/Octal 数据线、dummy cycle、XIP。
- `i2s.md`：音频串行接口、采样率、左右声道时钟、位时钟。

### 模拟与混合信号接口

- `adc-dac.md`：模数/数模转换、采样率、分辨率、参考电压。
- `comparator.md`：比较器、阈值、电平检测。

### 物理层相关

- `rs232-rs485.md`：串口电平转换、差分传输、半双工通信。
- `can-phy.md`：CAN 物理层、差分信号、终端电阻。
- `can-practical.md`：CAN 调试流程速查、终端电阻详解、收发器选型、Linux SocketCAN 工具。
- `can-deep-dive.md`：CAN 物理层 / 帧格式 / 仲裁 / 错误处理 / 故障树（完整原理体系）。
- `can-multimaster-and-bus-off.md`：多 master 仲裁、节点状态机（Active / Passive / Bus Off）、错误计数器规则、Bus Off 恢复。
- `can-failure-cases.md`：20 个产线 CAN 死机案例（终端 / 波特率 / bus off / EMC 等）。
- `can-fd-and-can-xl.md`：CAN FD 数据段加速 + CAN XL 演进、双波特率配置、收发器选型。
- `can-rtos-integration.md`：RT-Thread / Zephyr / FreeRTOS 三平台集成 + Linux SocketCAN 完整实战。
- `can-vs-other-bus.md`：CAN vs I2C / SPI / UART / RS485 / Ethernet / LIN / FlexRay 12 维度对比。
- `can-index.md`：CAN 主题总览导航——5 种读者路径、主题速查矩阵、CAN vs I2C/SPI/UART 主题对比。
- `ethernet-phy.md`：以太网 PHY、MII/RMII/RGMII、磁性器件。
- `lvds.md`：低压差分信号、显示 LVDS、差分阻抗和屏线调试。

## 收录边界

放在 `basic` 的内容通常满足以下条件：

- 主要描述芯片外设本身，而不是完整应用层协议。
- 重点是信号线、时序、收发机制、硬件连接。
- 可以作为多个上层总线或协议的基础。

例如：`UART` 放在 `basic`，但 `Modbus RTU` 放在 `bus`；`RS485` 作为物理层可放在 `basic`，但基于 RS485 的完整协议应放在 `bus`。
