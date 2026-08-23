# SPI Deep Dive

## 目标

本文深入 SPI 工程细节，重点解决模式配置、片选时序、dummy cycle、SPI Flash 命令、多设备共享、高速信号完整性和 QSPI/OSPI 扩展问题。

## SPI 的本质

SPI 是由控制器驱动时钟的同步串行接口。

核心关系：

```text
SCLK：控制器输出时钟
MOSI：控制器到目标设备
MISO：目标设备到控制器
CS：选择目标设备并定义事务边界
```

SPI 没有统一的应用层协议。

每个芯片都可以定义自己的：

- 命令字。
- 地址长度。
- dummy cycle。
- 读写方向。
- 状态寄存器。
- CS 时序。

所以调 SPI 时，手册时序图比“SPI 标准印象”更重要。

## CPOL 和 CPHA 的真实含义

`CPOL` 决定时钟空闲电平：

```text
CPOL = 0：SCLK 空闲为低
CPOL = 1：SCLK 空闲为高
```

`CPHA` 决定第几个边沿采样：

```text
CPHA = 0：第一个有效边沿采样
CPHA = 1：第二个有效边沿采样
```

四种模式：

| Mode | CPOL | CPHA | 常见描述 |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 空闲低，上升沿采样 |
| 1 | 0 | 1 | 空闲低，下降沿采样 |
| 2 | 1 | 0 | 空闲高，下降沿采样 |
| 3 | 1 | 1 | 空闲高，上升沿采样 |

不要只凭经验猜 Mode。

正确做法：

```text
看目标芯片时序图中数据在哪个边沿稳定
看目标芯片要求在哪个边沿采样
再配置 CPOL/CPHA
```

## Mode 配错的表现

Mode 配错时常见现象：

- 读 ID 固定错误。
- 数据整体左移或右移 1 bit。
- 低速偶尔正常，高速错误增多。
- 读回值看似接近但不稳定。
- 第一个 bit 或最后一个 bit 错误。

调试建议：

```text
先低速
读固定 ID
逐个尝试 Mode 0~3
用逻辑分析仪确认采样边沿
```

## CS 是事务边界

SPI 的 `CS` 不只是“选中设备”。

很多目标设备把 `CS` 的下降沿和上升沿当成事务边界：

```text
CS 下降：开始解析命令
CS 上升：结束当前命令或锁存数据
```

常见错误：

```text
发送命令后 CS 被硬件自动拉高
再读数据时重新拉低 CS
目标设备认为这是另一条新命令
```

正确做法通常是：

```text
CS low
发送 command
发送 address
发送 dummy
读取 data
CS high
```

整个事务中 CS 保持有效。

## 硬件 NSS 和软件 CS

很多 MCU SPI 控制器支持硬件 NSS，但实际项目常用 GPIO 手动控制 CS。

原因：

- 一次事务可能包含多段发送和接收。
- DMA 分段传输期间 CS 不能跳变。
- 不同设备 CS 时序要求不同。
- 多设备共享时需要灵活控制。

建议：

```text
简单传感器可用硬件 NSS
复杂 Flash/屏幕/多段事务优先软件 GPIO 控 CS
```

## Dummy byte 和 dummy cycle

SPI 读数据时必须有时钟。

控制器产生时钟的方式通常是发送 dummy 数据：

```text
0x00
0xFF
```

对 SPI Flash，还经常有 dummy cycle。

例如 Fast Read：

```text
Command 0x0B
24-bit Address
8 dummy clocks
Data out
```

如果 dummy cycle 少了或多了，数据会错位。

常见表现：

- 读出的数据前几个字节错误。
- 整体偏移。
- 低速普通读正常，Fast Read 异常。

## SPI Flash 基础命令

常见 SPI NOR Flash 命令：

| 命令 | 含义 |
| --- | --- |
| 0x9F | Read JEDEC ID |
| 0x03 | Read Data |
| 0x0B | Fast Read |
| 0x06 | Write Enable |
| 0x04 | Write Disable |
| 0x05 | Read Status Register |
| 0x02 | Page Program |
| 0x20 | Sector Erase |
| 0xC7/0x60 | Chip Erase |

典型写流程：

```text
Write Enable
Page Program
Poll WIP bit until 0
```

典型擦除流程：

```text
Write Enable
Sector Erase
Poll WIP bit until 0
```

关键点：

```text
写和擦除前通常必须 Write Enable
写和擦除后必须等待 busy 结束
Page Program 不能随意跨页
Flash 只能把 1 写成 0，恢复 1 需要擦除
```

## 页写和擦除粒度

SPI NOR Flash 常见：

```text
Page Program：256 bytes
Sector Erase：4 KB
Block Erase：32 KB / 64 KB
```

如果写入跨越 page boundary，很多 Flash 会在页内回卷，导致覆盖前面的数据。

驱动必须按页切分。

## 状态寄存器

Flash 写入和擦除不是立即完成。

常见状态位：

```text
WIP：Write In Progress
WEL：Write Enable Latch
BP：Block Protect
QE：Quad Enable
```

写驱动时要：

- 检查 WEL 是否置位。
- 写/擦后轮询 WIP。
- 处理超时。
- 注意写保护位。
- QSPI 前确认 QE 位。

## 多设备 MISO 冲突

多设备共享 SPI 时，未选中的目标设备应释放 MISO。

如果某个设备未释放 MISO，会造成：

- 总线读值异常。
- 两个设备互相影响。
- 某个设备单独接正常，多个一起接异常。
- MISO 电平被强拉。

排查方法：

```text
只焊一个设备测试
逐个增加设备
示波器看未选中设备 MISO 是否高阻
确认每个 CS 默认上拉
```

## CS 默认状态

上电时所有 CS 应保持未选中。

通常需要：

```text
CS 上拉
MCU 复位期间不会误拉低
初始化 SPI 前先把 CS 配成高
```

否则可能出现：

- Flash 误进入命令状态。
- 屏幕误接收垃圾命令。
- 多设备 MISO 冲突。
- 上电偶发异常。

## SPI 速度不是越高越好

SPI 高速限制因素：

- 目标设备最大 SCLK。
- PCB 走线长度。
- 负载电容。
- 电平转换器速度。
- 探头和飞线。
- SCLK 边沿过快导致振铃。
- MISO 返回路径延迟。

调试策略：

```text
100 kHz 验证功能
1 MHz 验证稳定
逐步提高到目标频率
每档跑长时间读写校验
```

## MISO 时序裕量

高速 SPI 读数据时，MISO 数据由目标设备输出，控制器采样。

时序裕量受影响：

```text
目标设备输出延迟
PCB 传播延迟
电平转换器延迟
控制器采样边沿
SCLK 占空比
```

如果高速读错误但低速正常，重点检查：

- Mode 是否正确。
- SCLK 是否过快。
- MISO 走线是否过长。
- 是否经过慢速电平转换器。
- 是否需要调整采样延迟或使用半周期采样配置。

## SPI 屏幕和 Flash 的差异

SPI Flash 关注：

```text
命令、地址、dummy、读写擦、状态寄存器
```

SPI 屏幕关注：

```text
初始化命令、DC 引脚、RESET、背光、像素格式、刷屏速度
```

很多 SPI 屏幕还有 `DC` 引脚：

```text
DC = 0：命令
DC = 1：数据
```

这不是标准 SPI 的信号，而是屏幕控制器额外定义。

## 3-Wire SPI

3-Wire SPI 把 MOSI 和 MISO 合并为一根双向数据线：

```text
SCLK
SDIO
CS
```

注意点：

- 读写方向切换要正确。
- 主控要释放 SDIO 后目标设备才能输出。
- 不能全双工。
- GPIO/外设方向切换时序很关键。

## QSPI 和 OSPI

QSPI 使用 4 根数据线：

```text
IO0
IO1
IO2
IO3
```

OSPI 使用 8 根数据线：

```text
IO0~IO7
```

它们常用于外部 Flash，提高读取带宽。

需要关注：

- Quad Enable 位。
- 命令阶段是单线还是多线。
- 地址阶段是单线还是多线。
- 数据阶段是几线。
- dummy cycle 数量。
- memory-mapped 模式。
- XIP 执行时的缓存一致性。

普通 SPI 驱动不能直接等同于 QSPI/OSPI 驱动。

## DMA 与缓存

SPI 大数据传输常用 DMA。

注意点：

- TX/RX DMA 同步启动。
- 全双工场景接收缓冲区不能为空。
- DMA 完成不一定代表目标设备内部操作完成。
- 有 Cache 的系统要 clean/invalidate。
- CS 必须覆盖整个 DMA 事务。

Flash 写入时，DMA 传输完成后还要轮询 WIP。

## 逻辑分析仪怎么看 SPI

重点看：

```text
Mode 解码是否正确
CS 是否覆盖完整事务
命令字是否正确
地址字节顺序是否正确
dummy clocks 是否正确
MISO 返回是否在预期时刻出现
```

如果解码出来全错，不一定是总线错，也可能是分析仪 Mode 设置错。

## 示波器怎么看 SPI

重点看：

- SCLK 是否有振铃和过冲。
- MOSI/MISO 在采样边沿是否稳定。
- CS 与 SCLK 的建立/保持时间。
- MISO 是否被多个设备争用。
- 高速下电平是否达到阈值。

飞线、面包板、长探头地线都会显著影响高速 SPI。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| JEDEC ID 全 FF | MISO 悬空、CS 未选中、供电异常 |
| JEDEC ID 全 00 | MISO 被拉低、Mode 错、设备未启动 |
| ID 错 1 bit | CPHA、采样边沿、速度过高 |
| Fast Read 错 | dummy cycle、频率、MISO 延迟 |
| 写入无效 | 未 Write Enable、写保护、未等 WIP |
| 擦除无效 | 未 Write Enable、保护位、地址未对齐 |
| 多设备异常 | CS 默认态、MISO 冲突、Mode 切换 |

## 驱动设计建议

推荐分层：

```text
spi_transfer
  |
device_transaction
  |
flash_driver / display_driver / sensor_driver
  |
application
```

每个设备维护独立配置：

```text
mode
max_hz
cs_gpio
bit_order
word_size
```

切换设备前重新配置 SPI 控制器。

## 深度检查清单

- CPOL/CPHA 根据时序图确认。
- CS 覆盖完整事务。
- 读数据时产生足够 dummy clocks。
- 多设备 MISO 无冲突。
- CS 上电默认未选中。
- 低速跑通后再提高频率。
- SPI Flash 写/擦前执行 Write Enable。
- 写/擦后轮询 WIP 并处理超时。
- QSPI/OSPI 已确认 QE、dummy 和命令模式。
- DMA 场景处理 CS、Cache 和完成时序。

## SPI 故障树

把 SPI 通信异常的所有可能根因画成一张决策树, 从现场现象一路推到具体验证手段。

```text
现象: SPI 通信失败
  |
  +-- 抓波形
        |
        +-- CS 不拉低
        |     -> CS GPIO 错 / CS 极性反 / pinmux 错 / 软件没拉低
        |     -> 验证: 示波器看 CS, 改 GPIO 寄存器直接拉低验证
        |
        +-- SCLK 没输出
        |     -> SPI 控制器没 enable / pinmux 错 / 控制器被 disable
        |     -> 验证: 检查 SPIx->CR1 SPE bit, 检查 GPIO AF
        |
        +-- MOSI 没数据
        |     -> TX buffer 没数据 / 控制器没启动 / pinmux 错
        |     -> 验证: 检查 TXDR 寄存器, 看 TXE flag
        |
        +-- MISO 没数据
        |     -> 设备未选中 / Mode 错 / MISO 接反 / 设备未上电
        |     -> 验证: 查 CS, 切 Mode 0/1/2/3 试
        |
        +-- 数据错位
        |     -> CPHA 错 / 采样边沿错 / 速度过高 / 噪声
        |     -> 验证: 切 Mode 0, 降到 100 kHz
        |
        +-- 数据全 0xFF
        |     -> MISO 悬空 / 设备未上电 / CS 极性反
        |     -> 验证: 量 MISO 上拉电阻, 量 VCC
        |
        +-- 数据全 0x00
        |     -> MISO 被拉低 / 设备锁死 / Mode 错
        |     -> 验证: 单独验证设备, 切 Mode 试
        |
        +-- 偶发失败
              -> 速度过高 / 时序裕量不足 / 电源纹波 / EMC 干扰
              -> 验证: 降速看是否消失, 量电源纹波
```

### 故障树对应的快速判定

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 读不到 ID | 接线 / Mode / CS | 示波器看 4 根线 |
| 数据错位 | CPHA / 采样边沿 | 切 Mode 0, 降速 |
| 全 0xFF | MISO 悬空 / 未选中 | 查 CS 极性, 量 MISO |
| 全 0x00 | MISO 拉低 / 设备锁死 | 单独验证设备 |
| 多设备互影响 | MISO 冲突 / CS 漏拉 | 单独 CS 控制 |
| 偶发失败 | 时序裕量 / EMC | 降速, 加屏蔽 |
| 写入无效 | 未 Write Enable / WIP 忙 | 查 SR1, 轮询 WIP |
| Fast Read 错 | dummy cycle 不够 | 加 dummy, 查手册 |
| DMA 跑到一半挂 | ISR race / DMA 配错 | 改 IT 模式对比 |

## SPI vs I2C 选型决策

```text
选 I2C 当:
  - 速度 < 400 kHz
  - 设备数 >= 2 (省引脚)
  - 板内管理类设备 (PMIC, 温度, RTC)
  - 接受外加上拉 + 多 master 复杂性
  - 总线短 (< 30cm)

选 SPI 当:
  - 速度 > 1 MHz
  - 单个高速设备 (Flash, LCD, ADC, sensor)
  - 接受 4-7 根引脚开销
  - 不需要长距离
  - 需要 DMA 高吞吐

选 UART 当:
  - 点对点异步通信
  - 调试口 (printf)
  - RS485 / RS422 长距离
  - 不需要时钟线

选 CAN 当:
  - 汽车 / 工业现场
  - 多节点, 强实时
  - 强抗干扰
  - 距离 > 1m
```

## SPI 速度边界

```text
低速档 (调试用):     100 kHz ~ 1 MHz
  - 适合: 调试, 验证设备, 长走线
  - 优势: 抗干扰, 调试容易

中速档 (多数应用):    1 MHz ~ 10 MHz
  - 适合: 普通 sensor, Flash
  - 优势: 平衡

高速档 (Flash, LCD):  10 MHz ~ 50 MHz
  - 适合: SPI Flash, LCD 显示
  - 风险: 信号完整性, MISO 延迟

超高速 (QSPI):       50 MHz ~ 200 MHz+
  - 适合: QSPI Flash, 高端 LCD
  - 风险: 走线, 阻抗匹配, 屏蔽
```

## 高速 SPI 信号完整性

高速 (>10 MHz) 时, SPI 的"信号完整性"成为产线死机的最大根因区。

### 4 个常见问题

```text
问题 1: MISO 边沿慢
  - 原因: MISO 内部上拉弱, 容性负载大
  - 解决: 加外部上拉 (10k-47k), 短走线
  - 验证: 示波器看 MISO 上升时间

问题 2: 时钟边沿有振铃
  - 原因: 走线电感 + 寄生电容, 阻抗不匹配
  - 解决: 加 series 电阻 (22-100 ohm), 缩短走线
  - 验证: 示波器看 SCLK 边沿

问题 3: 数据建立时间不足
  - 原因: MISO 延迟 > 时钟周期 / 2
  - 解决: 降速, 调整采样边沿 (CPHA)
  - 验证: 量 MISO 边沿到下一 SCLK 边沿时间

问题 4: 跨地电位差
  - 原因: 多个 GND 点, 大电流经过 GND
  - 解决: 单点接地, 加地线, 隔离
  - 验证: 量两端 GND 电压差
```

### 信号完整性检查清单

```text
□ MISO 上升时间 < 时钟周期 / 4
□ SCLK 边沿无振铃 (过冲 < 0.5V)
□ 数据建立时间 > 5 ns
□ 保持时间 > 5 ns
□ 走线 < 10 cm (高速档)
□ 走线阻抗 50 ohm 匹配
□ 串接电阻 (22-100 ohm) 防反射
□ VCC 纹波 < 50 mV
□ GND 单点或低阻抗
□ 高速信号线远离噪声源
```

## SPI 与 DMA 配合

### 何时用 DMA

```text
适合 DMA:
  - 数据长度 > 16 字节
  - 高速 (10MHz+) 持续传输
  - CPU 忙其他任务
  - LCD / Flash 大量数据

不适合 DMA:
  - 数据长度 < 8 字节
  - 调试 (排障难)
  - 多设备频繁切换
  - 短命令
```

### DMA + SPI 模式

```c
/* 模式 1: 全双工 DMA (主推) */
HAL_SPI_TransmitReceive_DMA(&hspi1, tx_buf, rx_buf, len);

/* 模式 2: 半双工 DMA (写 + 读分两次) */
HAL_SPI_Transmit_DMA(&hspi1, tx_buf, len);
HAL_SPI_Receive_DMA(&hspi1, rx_buf, len);

/* 模式 3: 循环 DMA (连续采集) */
HAL_SPI_TransmitReceive_DMA(&hspi1, tx_buf, rx_buf, len);
HAL_SPI_DMAPause(&hspi1);  // 暂停
HAL_SPI_DMAResume(&hspi1); // 恢复
```

### DMA 完成后的 CS 处理

```c
/* 问题: DMA 完成后 CS 立刻拉高, 从设备还没处理完最后一字节 */
/* 解决: CS 拉高前等几个 dummy clock */

void spi_tx_with_delay_cs(SPI_HandleTypeDef *hspi, ...) {
    HAL_SPI_Transmit_DMA(hspi, data, len);
    /* 等 DMA 完成 */
    osSemaphoreAcquire(dma_done_sem, timeout);
    /* 关键: 多等几个 clock, 确保设备锁存最后字节 */
    delay_us(5);
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);
}
```

## SPI 状态机

```text
IDLE
  -> (发起事务) -> CS_LOW
CS_LOW
  -> (开始传输) -> XFER
XFER
  -> (DMA/IT 完成) -> CS_HIGH
  -> (timeout) -> ABORT
  -> (CRC 错) -> ERROR
CS_HIGH
  -> (返回 IDLE) -> IDLE
ABORT
  -> (force CS_HIGH) -> CS_HIGH
ERROR
  -> (返回 IDLE, 上报) -> IDLE
```

## SPI 错误码设计

```c
typedef enum {
    SPI_OK              = 0,
    SPI_ERR_TIMEOUT     = -1,   // 等待超时
    SPI_ERR_CRC         = -2,   // CRC 错误 (高速 QSPI)
    SPI_ERR_MODE        = -3,   // Mode 错
    SPI_ERR_CS          = -4,   // CS 时序错
    SPI_ERR_DMA         = -5,   // DMA 失败
    SPI_ERR_OVERRUN     = -6,   // overrun
    SPI_ERR_UNDERRUN    = -7,   // underrun
} spi_err_t;
```

## 7 条 SPI 常见错误

| # | 错误 | 后果 |
| --- | --- | --- |
| 1 | Mode 配错 | 数据全错 |
| 2 | MOSI/MISO 接反 | 读到固定值, 写不进去 |
| 3 | CS 默认拉低 | 多设备总线冲突 |
| 4 | CS 拉高过早 | 从设备丢最后一字节 |
| 5 | dummy byte 缺失 | 读不到数据 |
| 6 | 速度过高 | 数据错位 |
| 7 | 未写 Write Enable | Flash 写不进去 |
| 8 | 未等 WIP 忙 | Flash 写丢失 |

## 产线 SPI 验收清单

- [ ] Mode 与 datasheet 一致
- [ ] CS 默认高 (未选中)
- [ ] CS 覆盖完整事务 (不中途拉高)
- [ ] 读数据有 dummy byte
- [ ] MISO 无三态冲突
- [ ] 100 kHz 跑通后再提速
- [ ] Flash 写/擦前 Write Enable
- [ ] 写/擦后轮询 WIP
- [ ] DMA 完成后再拉高 CS
- [ ] 高速 (10MHz+) 验证信号完整性
- [ ] 产线 fault injection (CS 抖动, 速度, EMC)
- [ ] 老化测试 (1000 小时)

## 关联文档

- `spi-practical.md` 速查
- `spi-failure-cases.md` 产线死机案例
- `spi-multislave-and-dma.md` 多从 / 菊花链 / DMA
- `spi-rtos-integration.md` RTOS 集成
- `spi-index.md` 导航
- `qspi-ospi.md` 高速 SPI Flash
- `i2c-deep-dive.md` I2C 原理 (对比)
