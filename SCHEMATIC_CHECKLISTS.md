# Schematic Checklists

## 目标

本文提供常见通信接口的原理图评审清单，用于设计阶段发现接线、电平、终端、保护和调试可测性问题。

## 通用检查

- 电源电压符合器件要求。
- IO 电平域一致或已有电平转换。
- GND 连接策略明确。
- RESET/ENABLE 默认状态正确。
- 关键信号有测试点。
- 连接器引脚定义和线缆方向明确。
- ESD/浪涌/隔离按应用场景配置。

## UART / TTL

- TX 接对方 RX，RX 接对方 TX。
- GND 共地。
- 电平兼容，5V 不直接进 3.3V 非耐压 RX。
- 调试口有 GND、TX、RX、Vref 标识。
- 若接模块，确认 RTS/CTS 是否需要。

## I2C / SMBus / PMBus

- SCL/SDA 有上拉。
- 上拉接到正确电压域。
- 上拉阻值符合速度和电容。
- 多设备地址无冲突。
- 不同电压域有 I2C 专用电平转换。
- SMBALERT、PMBus CONTROL、PAGE 相关信号按需连接。

## SPI / QSPI / OSPI

- SCLK/MOSI/MISO/CS 接线方向正确。
- 每个从设备有独立 CS。
- CS 默认上拉或复位期间保持未选中。
- 多设备 MISO 不冲突。
- QSPI/OSPI IO0~IO7 顺序正确。
- Flash HOLD/WP 引脚处理正确。

## RS485

- MCU UART 通过 RS485 收发器连接 A/B。
- DE/RE 控制脚连接到 MCU 或自动方向电路。
- A/B 端子定义清晰。
- 总线端节点预留 120Ω 终端。
- 偏置电阻策略明确。
- 工业现场考虑隔离、TVS、共模电感。

## CAN

- MCU CAN_TX/RX 通过 CAN 收发器连接 CANH/CANL。
- CANH/CANL 端子定义清晰。
- 总线端节点有 120Ω 终端。
- 断电总线目标约 60Ω。
- 车载或工业环境加 TVS 和共模电感。
- STB/EN/Silent 引脚默认状态正确。

## Ethernet

- MCU/SoC 是否内置 MAC，外部 PHY 是否需要。
- RMII/MII/RGMII 信号完整。
- 50 MHz RMII 时钟来源明确。
- PHY 地址 strap 与软件匹配。
- MDIO 有上拉。
- PHY 复位时序可控。
- 磁性器件和 RJ45 引脚与 PHY 参考设计匹配。

## USB

- Host/Device/OTG 角色明确。
- VBUS 供电和检测正确。
- D+/D- 没接反。
- ESD 器件电容符合 USB 速度。
- Type-C CC 上拉/下拉正确。
- Device 不向 VBUS 反灌。

## PCIe

- RC/EP 角色明确。
- TX/RX 方向正确。
- REFCLK 连接和要求符合规范。
- PERST# 时序可控。
- AC 耦合电容位置正确。
- Lane 极性和顺序确认。
- 电源和时钟满足模块要求。

## MIPI CSI/DSI

- Lane 数、顺序、P/N 极性正确。
- D-PHY 差分阻抗和走线匹配。
- Sensor/Panel 电源 rail 完整。
- MCLK、RESET、PWDN、背光控制连接正确。
- I2C 控制接口可访问。
- FPC 引脚定义和方向确认。

## 调试接口

- SWD/JTAG 有 GND 和 VTref。
- NRST 可访问。
- 调试引脚未被不可恢复复用。
- 量产测试点机械可靠。
