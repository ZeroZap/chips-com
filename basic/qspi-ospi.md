---
tags:
  - layer/basic
  - type/overview
  - protocol/qspi-ospi
---

# QSPI / OSPI

## 定位

QSPI（Quad SPI）和 OSPI（Octal SPI）是 SPI NOR Flash 的高速扩展接口。它们在同一套 SPI 事务模型上增加数据线数量、双倍数据速率（DDR）、DQS 和 memory-mapped/XIP 能力。

常见用途：

- 外部 NOR Flash 存放固件、字库、图片。
- MCU/SoC 从外部 Flash 直接执行代码（XIP）。
- 高速启动介质。
- FPGA/SoC 配置存储。
- 需要大容量、低引脚数、可随机读的嵌入式存储。

QSPI/OSPI 的难点不在“读 ID”，而在**高速模式切换、dummy cycle、地址模式、XIP 缓存和信号完整性**。

## 与普通 SPI 的区别

| 接口      | 数据线              | 典型速率          | 特点                        |
| --------- | ------------------- | ----------------- | --------------------------- |
| SPI       | 1 主出 + 1 主入     | 几 MHz ~ 几十 MHz | 简单、兼容性好              |
| Dual SPI  | IO0/IO1             | 约 2 倍           | 命令后可切换双线            |
| Quad SPI  | IO0~IO3             | 约 4 倍           | 常见于 NOR Flash            |
| Octal SPI | IO0~IO7             | 约 8 倍           | 更高带宽，常带 DQS/DDR      |
| HyperBus  | 8 位数据 + 额外控制 | 高                | 另一类 Xccela/HyperRAM 体系 |

QSPI/OSPI 仍然使用片选、时钟和命令/地址/数据阶段，只是数据阶段可以并行使用多根线。

## 传输阶段

一次 Flash 访问通常包括：

```text
CS 拉低
Command
Address
Mode / Wait states
Dummy cycles
Data
CS 拉高
```

每个阶段可以使用不同线宽，常见表示：

```text
1-1-4：命令 1 线，地址 1 线，数据 4 线
1-4-4：命令 1 线，地址 4 线，数据 4 线
4-4-4：命令/地址/数据都用 4 线
8-8-8：OSPI 全八线
1-8-8：OSPI 命令单线，地址/数据八线
```

**线宽必须和 Flash 支持的模式一致**。命令阶段用错线宽，后续数据全部错位。

## 常见 Flash 命令

| 命令            | 作用                           | 注意                         |
| --------------- | ------------------------------ | ---------------------------- |
| `0x9F`          | Read JEDEC ID                  | 最基础的识别命令，通常单线   |
| `0x03`          | Read Data                      | 低速读，24 位地址            |
| `0x0B`          | Fast Read                      | 需要 dummy cycle             |
| `0x6B`          | Fast Read Quad Output          | 数据阶段四线                 |
| `0xEB`          | Fast Read Quad I/O             | 地址/数据四线，需 mode/dummy |
| `0x02`          | Page Program                   | 页写                         |
| `0x20` / `0xD8` | Sector/Block Erase             | 擦除粒度                     |
| `0x05`          | Read Status Register           | WIP、WEL、保护位             |
| `0x06`          | Write Enable                   | 写/擦前必须                  |
| `0x01`          | Write Status Register          | 配置 QE、保护位              |
| `0xB7` / `0xE9` | Enter/Exit 4-byte address mode | 大容量 Flash                 |

不同厂商的命令集和 dummy 要求可能不同，必须以数据手册为准。

## Quad Enable（QE）

Quad 模式通常需要先设置状态寄存器中的 QE 位：

1. 用单线 SPI 读 JEDEC ID，确认器件和容量。
2. 读状态寄存器，确认 QE 当前值。
3. 写使能（WREN）。
4. 写状态寄存器，置 QE。
5. 等待 WIP 清零。
6. 再切换到 Quad 命令/线宽。

常见错误：

- 没置 QE 就发 Quad 命令。
- 写状态寄存器后没等 WIP。
- 保护位阻止状态寄存器写入。
- 不同厂商 QE 位位置不同。

## Dummy Cycle

高速读通常需要 dummy cycle 给 Flash 内部留出访问时间：

```text
Command + Address + Dummy + Data
```

dummy 数量与：

- Flash 型号。
- 时钟频率。
- 供电电压。
- 温度。
- 线宽模式。

有关。dummy 太少会读到错位数据，太多会降低有效带宽。高频、低压、低温场景要特别验证。

工程做法：

- 先用保守的 dummy 值打通。
- 用已知 pattern 做读写比对。
- 逐步提高频率，观察误码。
- 以数据手册的 frequency-dummy 表为基线。

## 地址模式

小容量 Flash 使用 24 位地址（3 字节）。超过 16 MB 的器件通常需要 32 位地址（4 字节），或者进入 4-byte address mode。

常见问题：

- 低地址读写正常，高地址错位。
- 24/32 位模式切换后命令长度不对。
- XIP 映射窗口只覆盖部分容量。
- 地址相位/线宽与命令不匹配。

## XIP 与 Memory-Mapped

XIP（Execute In Place）把 Flash 映射到 CPU 地址空间，CPU 可以直接取指，而不需要每次软件搬运。

关键配置：

- 映射窗口基地址和大小。
- 读命令、线宽、dummy。
- 地址字节数。
- 时钟和读等待周期。
- Cache/预取策略。
- 写/擦除时的总线停顿。

XIP 场景注意：

- Flash 擦写时通常不能同时取指，需要切换到 RAM 执行或暂停总线。
- Cache 可能缓存旧数据，擦写后要失效。
- 高频 XIP 对 PCB 和 Flash 速度等级要求更高。
- 安全启动可能要求校验后再映射。

## DDR 与 DQS

OSPI 高速模式常使用 DDR（双沿采样）和 DQS（数据选通）：

- DDR 在时钟上升沿和下降沿都传数据。
- DQS 由 Flash 输出，用于接收端对齐。
- 需要训练/校准读延迟。
- PCB 走线等长和阻抗控制更严格。

DQS 训练失败的表现：

- 低速正常，高速误码。
- 温度变化后偶发读错。
- 不同板子良率不一致。
- XIP 随机崩溃。

## 信号完整性

QSPI/OSPI 高速时按高速数字链路处理：

- 50 Ω 单端/100 Ω 差分阻抗（按器件和板级要求）。
- SCK 与数据线长度匹配。
- 减少过孔和分支。
- 片选走线短，避免长 stub。
- 必要时串阻/端接。
- Flash 电源去耦充分。
- 时钟和数据避免跨分割。

## 常见故障树

```text
QSPI 读不到 ID
├── 电源/复位
├── CS/SCK 无波形
├── IO0/IO1 接反
├── Flash 处于错误模式
└── 上电时序/保持脚

普通 SPI 正常，Quad 失败
├── QE 未使能
├── 命令/地址线宽错误
├── dummy 不足
├── IO2/IO3 未连接或复用错误
└── Flash 不支持该命令

高地址读错
├── 24/32 位地址模式
├── 地址线宽/相位
├── 映射窗口越界
└── 容量识别错误

XIP 崩溃
├── dummy/时钟过高
├── cache 未失效
├── 擦写期间取指
├── 映射配置错误
└── 信号完整性

写入失败
├── 未 Write Enable
├── WIP 未等待
├── 保护位/锁定位
├── 擦除粒度/地址对齐
└── 电源跌落
```

| 现象               | 优先检查                           |
| ------------------ | ---------------------------------- |
| 单线能读，四线不能 | QE、线宽、dummy、IO2/IO3           |
| 读数据整体错位     | dummy、地址字节数、采样边沿        |
| 高地址异常         | 4-byte 地址模式、映射窗口          |
| 偶发误码           | 时钟过高、PCB、电源、温度          |
| XIP 随机死机       | cache、dummy、擦写冲突、信号完整性 |
| 写入失败           | WREN、WIP、保护位、擦除对齐        |
| 不同板子表现不同   | 走线长度、端接、Flash 批次         |

## 测量方法

- 逻辑分析仪解码命令/地址/数据，确认线宽和 dummy。
- 示波器看 SCK、CS、IO0~IO7 的边沿、过冲和建立/保持。
- 用已知 pattern 做全地址读写比对。
- 高低温、低压、不同板子做余量测试。
- XIP 场景做长时间取指、擦写和复位循环。

## 设计检查清单

- Flash 型号、容量、电压、速度等级确认。
- 单线 SPI 能读 JEDEC ID。
- QE/OPI 模式使能流程正确。
- 命令、地址、dummy、线宽与手册一致。
- 24/32 位地址模式正确。
- XIP 映射窗口、cache、擦写停顿处理正确。
- SCK/CS/IO 走线阻抗和长度匹配。
- Flash 电源去耦和复位时序满足要求。
- 高速前先做低速全地址读写擦。
- 量产测试覆盖 ID、全地址 pattern、擦写和 XIP 启动。

## 最小实验

1. 单线 SPI 读 JEDEC ID 和状态寄存器。
2. 置 QE，切换到 Quad 读，比较单线和四线读出的同一段数据。
3. 扫描 dummy cycle，找到不同频率下的稳定边界。
4. 写入递增 pattern，覆盖低/高地址，读回比对。
5. 配置 XIP，从 Flash 执行代码，再做一次擦写和 cache 失效测试。

## 关联文档

- [spi-deep-dive.md](spi-deep-dive.md)：SPI 模式、CS 边界和 Flash 命令。
- [spi-failure-cases.md](spi-failure-cases.md)：SPI Flash 产线案例。
- [../guides/troubleshooting/MEASUREMENT_EXAMPLES.md](../guides/troubleshooting/MEASUREMENT_EXAMPLES.md)：SPI Flash 测量样例。
- [../guides/troubleshooting/SCHEMATIC_CHECKLISTS.md](../guides/troubleshooting/SCHEMATIC_CHECKLISTS.md)：原理图检查清单。
