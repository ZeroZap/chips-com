# I2C Deep Dive

## 目标

本文深入 I2C 工程细节，重点解决上拉电阻、总线电容、地址混淆、Repeated START、Clock Stretching、总线恢复、I2C MUX、EEPROM/传感器/PMIC 特性和现场排障。

## I2C 的工程定位

I2C 适合板内低速管理类通信：

- 传感器配置和读取。
- EEPROM/RTC。
- PMIC 和电源监控。
- 触摸控制器。
- 小型外设寄存器访问。

I2C 不适合：

- 长距离线缆。
- 强干扰工业现场。
- 高速连续大数据。
- 大量设备高频轮询。

工程直觉：

```text
I2C 是板内管理总线，不是通用远距离通信总线。
```

## 开漏结构为什么重要

I2C 的 `SCL` 和 `SDA` 通常是开漏或开集结构。

设备只能：

```text
主动拉低 = 0
释放总线 = 1，由上拉电阻拉高
```

这个特性支持：

- 多设备共享总线。
- ACK/NACK。
- 仲裁。
- Clock Stretching。
- 避免多个设备推挽硬冲突。

代价是：

```text
上升沿由 RC 决定，速度和总线电容强相关。
```

## 上拉电阻选择

常见取值：

| 场景 | 常见取值 |
| --- | --- |
| 100 kHz，短线，少设备 | 4.7k 或 10k |
| 400 kHz，普通板内 | 2.2k 或 4.7k |
| 1 MHz，电容较大 | 1k 到 2.2k |
| 长线或多设备 | 需要计算和实测 |

上拉太大：

- 上升沿慢。
- 高速通信失败。
- 偶发 NACK。
- 波形像斜坡。

上拉太小：

- 拉低电流过大。
- 功耗增加。
- 低电平可能不够低。
- 设备驱动压力增加。

## 总线电容

总线电容来自：

- PCB 走线。
- 芯片引脚。
- 连接器。
- 线缆。
- 电平转换器。
- 逻辑分析仪和示波器探头。

I2C 高速失败时，不要只看软件配置。重点看：

```text
上拉电阻 × 总线电容
```

总线越重，上升沿越慢。

## 速度调试策略

推荐顺序：

```text
100 kHz 跑通功能
400 kHz 验证稳定
1 MHz 或更高只在硬件允许时使用
```

如果 400 kHz 不稳定但 100 kHz 稳定，优先怀疑：

- 上拉太弱。
- 总线电容太大。
- 电平转换器太慢。
- 飞线或连接器影响。
- 波形上升沿不满足要求。

## 7-bit 地址和 8-bit 地址

I2C 标准常用 7-bit 地址。

例如设备地址：

```text
0x68
```

线上发送时会变成：

```text
写：0xD0
读：0xD1
```

因为：

```text
0x68 << 1 = 0xD0
0xD0 | 1 = 0xD1
```

很多驱动 API 要求传 7-bit 地址：

```c
i2c_read(0x68, reg, buf, len);
```

不要误传：

```c
i2c_read(0xD0, reg, buf, len);
```

除非驱动明确要求 8-bit 地址。

## ACK/NACK 定位

I2C 每 8 bit 后有 1 bit 应答。

```text
ACK = 0
NACK = 1
```

地址阶段 NACK，优先检查：

- 地址是否正确。
- 设备是否上电。
- RESET/PWDN 是否释放。
- 上拉是否存在。
- 电平域是否匹配。
- 设备是否处于睡眠或忙状态。

数据阶段 NACK，优先检查：

- 寄存器地址是否存在。
- 命令格式是否正确。
- 写保护是否开启。
- 设备内部是否忙。
- 是否需要延时或状态轮询。

## Repeated START

寄存器读常见流程：

```text
START
Address + Write
Register Address
Repeated START
Address + Read
Data
NACK
STOP
```

不要默认改成：

```text
START -> Write Register -> STOP -> START -> Read
```

某些设备把 `STOP` 视为事务结束，会清除内部状态或改变寄存器指针。

驱动应提供：

```text
write_then_read with repeated start
```

## Clock Stretching

Clock Stretching 是从设备拉低 `SCL`，让主控等待。

用途：

- 从设备还没准备好数据。
- 内部转换未完成。
- 低速设备需要更多处理时间。

风险：

- 某些主控不支持或支持有限。
- 软件模拟 I2C 容易漏处理。
- Linux/RTOS 驱动可能有超时限制。

如果目标器件手册要求 Clock Stretching，必须确认控制器支持。

## 总线被拉死

常见现象：

```text
SDA 一直为低
SCL 一直为低
I2C 控制器一直 BUSY
```

可能原因：

- 主控复位发生在传输中间。
- 从设备状态机停在等待时钟阶段。
- 从设备异常掉电。
- ESD/干扰导致状态错乱。
- 硬件短路。

恢复方法：

```text
关闭 I2C 外设
SCL/SDA 改 GPIO
发送 9 个 SCL 脉冲
尝试生成 STOP
重新初始化 I2C
必要时复位从设备
```

## 电平转换

常见 I2C 电压：

```text
1.8V
3.3V
5V
```

不同电压域不能直接混接。

常见方案：

```text
BSS138 MOS 转换
PCA9306
TCA9517
专用 I2C buffer/level shifter
```

注意：

- 转换器增加电容。
- 转换器有速度限制。
- 某些 buffer 有方向、偏置或电压要求。
- 高速 I2C 问题常常出在电平转换器。

## 地址冲突

两个同地址设备挂在同一总线上会冲突。

解决方式：

- 使用地址选择引脚。
- 换不同地址型号。
- 使用多个 I2C 控制器。
- 使用 I2C MUX。
- 迁移到 I3C 动态地址。

常见 I2C MUX：

```text
TCA9548A
```

## I2C MUX

访问 MUX 后面的设备前，必须先选择通道：

```text
写 MUX 控制寄存器，打开通道 N
访问目标设备
必要时关闭通道
```

MUX 带来的问题：

- 软件路径更复杂。
- 扫描地址时要逐通道扫描。
- 忘记切通道会扫不到设备。
- 通道切换增加延迟。
- 故障定位要区分 MUX 前后两段总线。

## EEPROM 特性

I2C EEPROM 写入后需要内部写周期。

写周期内设备可能对地址 NACK。

这通常不是错误。

常见策略：

```text
ACK polling
```

也就是写完后轮询设备地址，直到重新 ACK。

EEPROM 还要注意 page boundary：

```text
跨页写可能回卷覆盖页内前面的数据
```

驱动必须按页切分写入。

## 传感器特性

很多传感器不是读寄存器就立刻有新数据。

常见流程：

```text
配置模式
启动测量
等待转换时间
读取 data ready 状态
读取数据寄存器
清除中断或状态位
```

如果没有等待转换完成，可能读到：

- 旧数据。
- 全 0。
- 无效标志。
- NACK。

## PMIC 和电源芯片特性

PMIC 常见机制：

- 写保护。
- 解锁序列。
- PAGE 多通道选择。
- 故障状态锁存。
- 写 RAM 和保存 NVM 分离。
- 某些状态下禁止改参数。

所以写寄存器不生效，不一定是 I2C 通信问题。

要结合设备状态机和手册限制排查。

## 驱动分层建议

推荐分层：

```text
i2c_transfer
  |
regmap / register access
  |
device driver
  |
application
```

基础访问接口建议支持：

```c
int read_reg8(uint8_t addr, uint8_t reg, uint8_t *value);
int write_reg8(uint8_t addr, uint8_t reg, uint8_t value);
int read_block(uint8_t addr, uint8_t reg, uint8_t *buf, size_t len);
int write_block(uint8_t addr, uint8_t reg, const uint8_t *buf, size_t len);
```

底层应统一处理：

- 超时。
- 重试。
- 错误码。
- 总线恢复。
- MUX 通道。
- 线程互斥。

## 错误码设计

不要只返回 `false`。

建议区分：

```text
address_nack
data_nack
timeout
bus_busy
arbitration_lost
clock_stretch_timeout
invalid_param
crc_error
```

这样现场日志才能定位问题阶段。

## 重试策略

推荐：

```text
最多重试 3 次
每次间隔 1~10 ms
失败后记录错误类型
bus_busy 或 timeout 后尝试恢复总线
```

不要无脑死循环重试。

如果设备持续 NACK，应上报设备离线或状态异常。

## 逻辑分析仪排查

重点看：

```text
START/STOP
7-bit/8-bit 地址显示方式
ACK/NACK 出现在哪一字节后
Repeated START 是否存在
SCL 是否被拉长
寄存器地址和数据是否符合手册
```

如果解码正常但设备行为不对，继续检查：

- 设备模式。
- 状态位。
- 延时要求。
- 字节序。
- 写保护。

## 示波器排查

示波器重点看电气质量：

- 高电平幅度。
- 低电平幅度。
- 上升沿时间。
- 振铃和过冲。
- 毛刺。
- SCL/SDA 串扰。

如果上升沿太慢：

```text
减小上拉电阻
降低速度
减少总线电容
缩短走线或线缆
减少挂载设备
检查电平转换器
```

## I2C 与 SMBus

SMBus 和 I2C 相似，但更严格。

SMBus 可能涉及：

- 超时。
- PEC。
- Alert。
- 标准事务格式。
- 特定速度范围。

访问 SMBus/PMBus 设备时，普通 I2C 读写可能不够，需要按对应事务实现。

## I2C 与 I3C

如果系统出现：

- 多传感器地址冲突。
- 中断 GPIO 不够。
- I2C 速度不够。
- 需要更好总线管理。

可以考虑 I3C。

但 I3C 需要控制器、目标设备、驱动和调试工具共同支持。成熟度和兼容性要提前评估。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 扫不到设备 | 电源、RESET、上拉、地址、电平 |
| 只有 100 kHz 稳定 | 上拉、电容、电平转换器、线长 |
| 地址 ACK 后数据 NACK | 寄存器地址、写保护、设备状态 |
| SDA 一直低 | 总线卡死、从设备异常、短路 |
| 读值全 FF | 设备未响应、SDA 上拉、地址错 |
| 读值全 00 | SDA 被拉低、寄存器/状态不对 |
| 传感器数据不变 | 未启动转换、未等 data ready |

## 深度检查清单

- SCL/SDA 空闲为高。
- 上拉接到正确电压域。
- 上拉阻值和总线电容满足目标速度。
- 地址按 7-bit/8-bit 规则确认。
- 寄存器读使用 Repeated START。
- 主控支持目标设备需要的 Clock Stretching。
- 有总线恢复机制。
- 多设备无地址冲突。
- I2C MUX 通道选择逻辑正确。
- EEPROM 页写和 ACK polling 已处理。
- 传感器转换时间和 data ready 已处理。
- PMIC 写保护、PAGE 和故障锁存已处理。
- 日志能区分地址 NACK、数据 NACK、超时和 bus busy。
