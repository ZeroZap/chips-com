# SMBus / PMBus Practical Guide

## 目标

本文用于把 SMBus 和 PMBus 落到工程实践，重点覆盖 SMBus 与 I2C 的差异、标准事务、PEC、SMBALERT、Host Notify、PMBus 命令模型、Linear 数据格式、PAGE、多路电源、故障状态和调试流程。

## 分层关系

先把三者关系分清：

```text
I2C：底层双线通信接口
SMBus：基于 I2C 思想的系统管理总线规范
PMBus：基于 SMBus 的电源管理命令协议
```

不是所有 I2C 设备都是 SMBus 设备。

不是所有 SMBus 设备都是 PMBus 设备。

PMBus 通常建立在 SMBus 事务和电气/时序约束之上。

## SMBus 适合什么场景

SMBus 常见于系统管理：

- 智能电池。
- 笔记本主板。
- 服务器主板。
- BMC 管理控制器。
- 温度传感器。
- 风扇控制器。
- 电压电流监控。
- 内存 SPD EEPROM。

它比普通 I2C 更强调：

- 事务格式。
- 超时。
- 可选 PEC。
- Alert 通知。
- 系统级管理一致性。

## PMBus 适合什么场景

PMBus 常见于电源管理：

- 数字电源模块。
- DC/DC 转换器。
- VRM。
- 服务器电源。
- 通信电源。
- 热插拔控制器。
- 电源监控芯片。
- 电池管理。

它用于：

- 读取输入/输出电压。
- 读取电流、温度、功率。
- 控制电源开关。
- 设置输出电压。
- 配置保护阈值。
- 读取和清除故障状态。
- 保存和恢复配置。

## SMBus 与 I2C 的关键差异

| 项目 | I2C | SMBus |
| --- | --- | --- |
| 定位 | 通用芯片间通信 | 系统管理通信 |
| 数据格式 | 灵活，由设备定义 | 定义标准事务类型 |
| 超时 | 原生不强调 | 有超时要求 |
| 校验 | 通常无 | 可选 PEC |
| Alert | 无统一标准 | SMBALERT# |
| 主机通知 | 无统一标准 | Host Notify |

工程上，很多 SMBus 设备能用 I2C 控制器访问，但不能忽略 SMBus 事务和 PEC 要求。

## SMBus 标准事务

常见事务：

```text
Quick Command
Send Byte
Receive Byte
Write Byte
Read Byte
Write Word
Read Word
Block Write
Block Read
Process Call
Block Write-Block Read Process Call
```

工程中最常见：

- Read Byte。
- Write Byte。
- Read Word。
- Write Word。
- Block Read。
- Block Write。

## Read Byte 示例

读取设备某个命令码对应的 1 字节数据：

```text
START
Address + Write
Command Code
Repeated START
Address + Read
Data Byte
STOP
```

这看起来像 I2C 读寄存器，但 SMBus 语义上叫 `Command Code`。

## Read Word 示例

读取 16-bit 数据：

```text
START
Address + Write
Command Code
Repeated START
Address + Read
Data Low Byte
Data High Byte
STOP
```

注意：

```text
SMBus Word 通常低字节在前
```

这和很多普通 I2C 寄存器“高字节在前”的习惯不同。

## Block Read 示例

Block Read 通常返回：

```text
Byte Count
Data[0]
Data[1]
...
Data[N-1]
```

注意：

- 第一个字节是长度。
- 最大长度受规范和设备限制。
- 如果启用 PEC，最后还有 PEC 字节。

驱动必须先解析长度，再读对应数据。

## PEC

`PEC` 是 Packet Error Code。

它通常是 CRC-8，用于检测传输错误。

注意事项：

- PEC 是可选的。
- 有些设备要求启用 PEC。
- 有些设备默认关闭 PEC。
- PEC 计算覆盖地址、读写位、命令码和数据。
- Read 场景中 repeated start 前后的地址也参与计算。

常见错误：

```text
PEC 多算或少算地址字节
读写方向位算错
把 PEC 字节本身也参与计算
设备未启用 PEC 但主机发送 PEC
设备要求 PEC 但主机没发 PEC
```

## SMBALERT#

`SMBALERT#` 是 SMBus 可选告警线。

它通常低有效。

用途：

```text
设备主动通知主机有事件需要处理
```

典型流程：

```text
设备拉低 SMBALERT#
主机检测到告警
主机执行 Alert Response Address 流程或轮询状态
定位触发设备
读取状态并清除事件
```

它和 I3C IBI 的思想类似，但实现方式不同：

```text
SMBus Alert：额外引脚
I3C IBI：带内中断
```

## Host Notify

Host Notify 允许设备向主机发送通知事务。

常见用途：

- 电池状态变化。
- 温度事件。
- 电源故障。
- 管理控制事件。

不是所有 SMBus 控制器和设备都支持 Host Notify。

设计前要确认硬件和驱动能力。

## PMBus 命令模型

PMBus 使用命令码访问电源设备功能。

常见命令：

| 命令 | 含义 |
| --- | --- |
| OPERATION | 控制电源输出开关 |
| ON_OFF_CONFIG | 配置开关控制方式 |
| CLEAR_FAULTS | 清除故障状态 |
| WRITE_PROTECT | 写保护 |
| VOUT_COMMAND | 设置输出电压 |
| READ_VIN | 读取输入电压 |
| READ_VOUT | 读取输出电压 |
| READ_IOUT | 读取输出电流 |
| READ_TEMPERATURE_1 | 读取温度 |
| READ_POUT | 读取输出功率 |
| STATUS_BYTE | 读取基础状态 |
| STATUS_WORD | 读取综合状态 |

命令支持情况以设备手册为准。

PMBus 标准命令不代表每颗芯片都完整实现。

## OPERATION

`OPERATION` 常用于控制输出开关。

但是否生效取决于：

- `ON_OFF_CONFIG`。
- 硬件 EN 引脚。
- 设备状态。
- 写保护。
- 厂商限制。

如果写 `OPERATION` 后电源没开，不要立刻认为通信失败。

应检查电源控制模式和状态寄存器。

## PAGE

多路电源设备常用 `PAGE` 选择通道。

例如：

```text
PAGE = 0：输出通道 0
PAGE = 1：输出通道 1
PAGE = 2：输出通道 2
```

读写通道相关命令前，先设置 PAGE。

常见错误：

```text
忘记切 PAGE，读写到了错误电源 rail
```

驱动建议把通道作为显式参数，不要隐藏在全局状态里。

## PMBus 数据格式

PMBus 数据不总是普通整数。

常见格式：

```text
Linear11
Linear16
Direct
VID
厂商自定义格式
```

必须看手册确认每个命令使用哪种格式。

## Linear11

Linear11 常用于电压、电流、温度等读数。

它通常把 16-bit 数据拆成：

```text
5-bit exponent
11-bit mantissa
```

实际值：

```text
Value = Mantissa * 2^Exponent
```

注意 exponent 和 mantissa 通常都是有符号数。

如果直接把原始 word 当整数，会得到完全错误的物理值。

## Linear16

Linear16 常用于某些电压命令。

它通常由：

```text
16-bit mantissa
配合 VOUT_MODE 中的 exponent
```

换算时要先读取：

```text
VOUT_MODE
```

再解析 `READ_VOUT` 或 `VOUT_COMMAND`。

## Direct Format

Direct Format 通过设备定义的系数换算。

常见形式：

```text
Y = (mX + b) * 10^R
```

具体 `m`、`b`、`R` 由设备手册给出。

这类设备必须严格按手册实现转换。

## STATUS_BYTE 和 STATUS_WORD

PMBus 故障排查优先读状态命令：

```text
STATUS_BYTE
STATUS_WORD
STATUS_VOUT
STATUS_IOUT
STATUS_INPUT
STATUS_TEMPERATURE
STATUS_CML
```

状态可能表示：

- 输出过压。
- 输出欠压。
- 过流。
- 输入欠压。
- 过温。
- 通信错误。
- 设备忙。
- 电源未就绪。

故障状态可能锁存，需要 `CLEAR_FAULTS` 清除。

## CLEAR_FAULTS

`CLEAR_FAULTS` 用于清除故障状态位。

注意：

```text
清除状态不代表故障原因消失
```

如果过压/过流/过温仍存在，状态会再次置位。

正确流程：

```text
读取状态
定位故障原因
处理硬件或配置问题
执行 CLEAR_FAULTS
再次读取状态确认
```

## WRITE_PROTECT

很多 PMBus 设备支持写保护。

写入参数不生效时检查：

- WRITE_PROTECT。
- 厂商密码。
- NVM 解锁。
- 当前状态是否允许写。
- 命令是否为只读。

不要只看 I2C/SMBus ACK 就认为写成功。

## 保存配置

PMBus 写命令可能只修改 RAM 运行配置。

掉电后是否保持取决于是否保存到 NVM。

常见命令：

```text
STORE_DEFAULT_ALL
RESTORE_DEFAULT_ALL
STORE_USER_ALL
RESTORE_USER_ALL
```

有些设备使用厂商自定义保存流程。

保存 NVM 时要注意：

- 写入次数限制。
- 保存期间设备 busy。
- 不能断电。
- 可能需要解锁。

## 调试流程

推荐步骤：

1. 先用普通 I2C/SMBus 扫描确认地址。
2. 读取固定 ID 或厂商信息。
3. 确认是否启用 PEC。
4. 读取 `STATUS_BYTE` 和 `STATUS_WORD`。
5. 读取基础遥测值，如 `READ_VIN`、`READ_VOUT`。
6. 按手册换算数据格式。
7. 多通道设备先验证 `PAGE`。
8. 尝试只读命令稳定后再写配置。
9. 写配置前确认写保护。
10. 保存 NVM 前确认流程和风险。

## Linux 工具

Linux 下常见工具：

```text
i2cdetect
i2cdump
i2cget
i2cset
```

注意：

- `i2cdetect` 对某些设备可能有副作用。
- `i2cdump` 不适合随便扫 PMBus 设备。
- 某些命令需要 SMBus word/block 事务。
- PEC 支持取决于驱动和工具。

服务器/BMC 场景还可能使用：

```text
hwmon
pmbus driver
OpenBMC sensors
```

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 设备 NACK | 地址、电源、总线、PEC、设备忙 |
| 读数不合理 | Linear/Direct 格式、字节序、PAGE |
| 写不生效 | WRITE_PROTECT、状态限制、NVM 未保存 |
| 故障清不掉 | 真实故障仍在、CLEAR_FAULTS 流程 |
| Alert 一直有效 | 状态未清、事件源未处理、告警线共享 |
| 多路电源读错 | PAGE 未切换或驱动全局状态混乱 |
| Linux 工具读错 | 事务类型不对、PEC 不匹配 |

## 驱动设计建议

驱动应明确区分：

```text
raw register value
converted physical value
status bit
fault event
configuration value
NVM stored value
```

建议接口：

```text
read_word(command)
write_word(command, value)
read_block(command)
read_status()
clear_faults()
select_page(page)
convert_linear11(raw)
convert_linear16(raw, exponent)
```

多通道设备中，所有通道访问都应显式传入 page。

## 实战检查清单

- 已确认设备是 I2C、SMBus 还是 PMBus。
- 已确认 7-bit 地址。
- 已确认是否需要 PEC。
- SMBus word 低字节在前已处理。
- PMBus 数据格式按手册换算。
- 多通道设备访问前已设置 PAGE。
- 写配置前已检查 WRITE_PROTECT。
- 故障状态读取和 CLEAR_FAULTS 流程完整。
- NVM 保存流程和风险已确认。
- Linux 工具使用的事务类型正确。
