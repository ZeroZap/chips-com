---
tags:
  - layer/basic
  - type/index
---

# Basic Communication Interfaces

`basic` 用于整理芯片和外设之间的基础通信接口。这里的重点是硬件连接、信号时序、寄存器配置和单点通信机制。

## 建议分类

### 通用数字接口

- [gpio.md](gpio.md)：电气边界、输入/输出模式、中断、去抖状态机、寄存器流程、故障树、测量与最小实验。
- [pwm.md](pwm.md)：定时器频率/分辨率计算、占空比边界、互补死区、舵机/LED/滤波 DAC、故障树与测量。
- [jtag-swd.md](jtag-swd.md)：JTAG/SWD 信号与协议、VTref、复位、低功耗/安全锁定、量产烧录与夹具设计。

### 串行通信接口

- [uart-practical.md](uart-practical.md)：UART 接线、参数、乱码、分帧和 TTL/RS232/RS485 区分（扩）。
- [uart-deep-dive.md](uart-deep-dive.md)：UART 波特率误差、过采样、DMA、流控、分帧和量产排障（扩）。
- [uart-failure-cases.md](uart-failure-cases.md)：21 个产线 UART 死机案例（baud 错、RS485 方向、协议分帧、DMA 丢包、ESD 等）。
- [uart-rs485-and-flow-control.md](uart-rs485-and-flow-control.md)：RS485 物理层、收发器选型、方向控制时序、硬件流控 RTS/CTS、软件流控 XON/XOFF、实战代码骨架。
- [uart-dma-circular-and-rtos.md](uart-dma-circular-and-rtos.md)：DMA 接收 + 环形缓冲 + idle 不定长接收 + FreeRTOS/Zephyr/RT-Thread 三平台集成 + 完整代码骨架。
- [uart-index.md](uart-index.md)：UART 主题总览导航——5 种读者路径、主题速查矩阵、UART vs SPI vs I2C 选型速查。
- [stream-protocol-parser-psm.md](stream-protocol-parser-psm.md)：流式协议解析器 PSM 模式库——L1 UART 5 状态机 / L2 TCP MBAP 状态机 / L3 J1939 TP 二级 PSM 的统一参考。

- [i2c-practical.md](i2c-practical.md)：I2C 上拉、地址扫描、寄存器读写、Repeated START 和总线恢复。
- [i2c-deep-dive.md](i2c-deep-dive.md)：I2C 上拉/电容、地址、Clock Stretching、总线恢复、MUX 和器件特性。
- [i2c-bus-recovery-playbook.md](i2c-bus-recovery-playbook.md)：I2C 总线被拉低死锁的实战手册——8 步恢复 SOP、STM32 HAL 平台适配、可移植 C 代码骨架、产线故障注入测试方案、面试回答模板。
- [i2c-rtos-integration.md](i2c-rtos-integration.md)：RT-Thread / Zephyr / FreeRTOS 三平台集成 bus recovery 的代码模式与对比。
- [i2c-multimaster.md](i2c-multimaster.md)：多主机仲裁物理原理、隐藏多 master 场景、bus recovery 风险与工程方案。
- [i2c-smbus-timeout.md](i2c-smbus-timeout.md)：SMBus 三大 timeout 精确数值、与 bus recovery 的关系、常见错误。
- [i2c-linux-fault-injection.md](i2c-linux-fault-injection.md)：Linux i2c-stub / i2c-gpio fault injection / bus_recovery_info 实操与回归测试脚本。
- [i2c-state-machine.md](i2c-state-machine.md)：I2C 状态机 + DMA + 中断并发模型，常见死锁和竞态解决方案。
- [i2c-failure-cases.md](i2c-failure-cases.md)：21 个产线死机案例，案例驱动的实战参考。
- [i2c-vs-smbus-recovery.md](i2c-vs-smbus-recovery.md)：I2C vs SMBus bus recovery 行为对比——一句话核心差异、完整对比表、4 种场景行为差异、timeout 数值精确对比、混用策略、选型决策树。
- [i2c-index.md](i2c-index.md)：I2C 主题总览导航——四种读者路径、主题速查矩阵、学习路径推荐。

- [spi-practical.md](spi-practical.md)：SPI Mode、片选时序、dummy byte、多设备共享和故障定位。
- [spi-deep-dive.md](spi-deep-dive.md)：SPI 采样模式、CS 边界、dummy cycle、Flash 命令、高速信号和 QSPI/OSPI。
- [spi-failure-cases.md](spi-failure-cases.md)：21 个产线 SPI 死机案例（Mode 错、CS 时序、Flash 时序、DMA race、信号完整性等）。
- [spi-multislave-and-dma.md](spi-multislave-and-dma.md)：多从设备共享、菊花链、DMA 模式、中断协作、4 类 race condition 解决方案。
- [spi-rtos-integration.md](spi-rtos-integration.md)：RT-Thread / Zephyr / FreeRTOS 三平台集成模式、mutex 与 reconfig 优化、双缓冲、实战代码骨架。
- [spi-index.md](spi-index.md)：SPI 主题总览导航——5 种读者路径、主题速查矩阵、SPI vs I2C 选型速查。
- [qspi-ospi.md](qspi-ospi.md)：Flash 命令、QE、dummy、24/32-bit 地址、XIP/cache、DDR/DQS、信号完整性与故障树。
- [i2s.md](i2s.md)：BCLK/LRCLK/MCLK 时钟比、I2S/LJ/RJ/TDM 格式、主从、Codec 初始化、DMA underflow 与测量。

### 模拟与混合信号接口

- [adc-dac.md](adc-dac.md)：误差预算、采样时间/源阻抗、Vref、校准、过采样、DAC 建立时间与负载。
- [comparator.md](comparator.md)：模拟比较器、迟滞、窗口比较、零交叉、开漏/推挽、传播延迟与阈值精度。

### 物理层相关

- [rs232-rs485.md](rs232-rs485.md)：RS232/RS485 电平、DE/RE 时序、终端/偏置、隔离防护、拓扑与现场故障树。
- [can-phy.md](can-phy.md)：CAN 收发器、显性/隐性、终端/分裂终端、共模/隔离、环路延迟与 CAN FD 边界。
- [can-practical.md](can-practical.md)：CAN 调试流程速查、终端电阻详解、收发器选型、Linux SocketCAN 工具。
- [can-deep-dive.md](can-deep-dive.md)：CAN 物理层 / 帧格式 / 仲裁 / 错误处理 / 故障树（完整原理体系）。
- [can-multimaster-and-bus-off.md](can-multimaster-and-bus-off.md)：多 master 仲裁、节点状态机（Active / Passive / Bus Off）、错误计数器规则、Bus Off 恢复。
- [can-failure-cases.md](can-failure-cases.md)：21 个产线 CAN 死机案例（终端 / 波特率 / bus off / EMC 等）。
- [can-fd-and-can-xl.md](can-fd-and-can-xl.md)：CAN FD 数据段加速 + CAN XL 演进、双波特率配置、收发器选型。
- [can-rtos-integration.md](can-rtos-integration.md)：RT-Thread / Zephyr / FreeRTOS 三平台集成 + Linux SocketCAN 完整实战。
- [can-vs-other-bus.md](can-vs-other-bus.md)：CAN vs I2C / SPI / UART / RS485 / Ethernet / LIN / FlexRay 12 维度对比。
- [can-index.md](can-index.md)：CAN 主题总览导航——5 种读者路径、主题速查矩阵、CAN vs I2C/SPI/UART 主题对比。
- [ethernet-phy.md](ethernet-phy.md)：MAC-PHY 接口、MDIO、自协商、复位/时钟、磁性/Bob Smith、RGMII delay、PoE 与 EMC。
- [lvds.md](lvds.md)：LVDS 电气、显示 Lane/VESA/JEIDA、Pixel Clock、扩频、PCB 与屏线调试。

## 收录边界

放在 `basic` 的内容通常满足以下条件：

- 主要描述芯片外设本身，而不是完整应用层协议。
- 重点是信号线、时序、收发机制、硬件连接。
- 可以作为多个上层总线或协议的基础。

例如：`UART` 放在 `basic`，但 `Modbus RTU` 放在 `bus`；`RS485` 作为物理层可放在 `basic`，但基于 RS485 的完整协议应放在 `bus`。
