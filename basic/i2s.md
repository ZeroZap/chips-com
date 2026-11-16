---
tags:
  - layer/basic
  - type/overview
  - protocol/i2s
---

# I2S

## 定位

I2S（Inter-IC Sound）是数字音频串行接口，用于在 SoC、Codec、DAC、ADC、数字麦克风和音频模块之间传输 PCM 音频数据。

I2S 只负责音频数据流；Codec 的寄存器配置通常走 I2C 或 SPI。因此一个典型音频链路是：

```text
SoC I2S <-> Codec（数据）
SoC I2C/SPI <-> Codec（控制）
Codec <-> 功放/耳机/扬声器（模拟）
```

I2S 工程问题通常来自：

- 主从角色不明确。
- MCLK/BCLK/LRCLK 频率不匹配。
- 数据格式/位宽/对齐方式不一致。
- Codec 初始化顺序错误。
- DMA 供数不足导致 underflow。
- 时钟抖动和地噪声导致爆音。

## 常见信号

| 信号            | 作用         | 说明                                  |
| --------------- | ------------ | ------------------------------------- |
| BCLK / SCK      | 位时钟       | 每个音频位一个周期                    |
| LRCLK / WS      | 左右声道时钟 | 频率等于采样率                        |
| SD / DIN / DOUT | 串行数据     | 发送或接收                            |
| MCLK            | 主时钟       | 常为 256/384/512 × fs，Codec 可能需要 |
| FS / SYNC       | 帧同步       | 有些器件称 LRCLK 为 FS                |

## 核心参数

```text
Sample Rate：44.1 kHz / 48 kHz / 96 kHz 等
Bit Depth：16 / 24 / 32 bit
Channels：2（立体声）或更多（TDM）
Format：I2S / Left Justified / Right Justified / DSP / TDM
Clock Master：SoC 或 Codec
MCLK：是否需要、倍频关系
```

## 时钟计算

对于标准立体声 I2S：

```text
BCLK = SampleRate × Channels × BitsPerChannel
LRCLK = SampleRate
```

例如 48 kHz、2 声道、32 bit 槽宽：

```text
BCLK = 48 kHz × 2 × 32 = 3.072 MHz
LRCLK = 48 kHz
```

MCLK 常见：

```text
MCLK = 256 × fs = 12.288 MHz
MCLK = 384 × fs = 18.432 MHz
MCLK = 512 × fs = 24.576 MHz
```

注意：

- “32 bit 槽宽”不等于“32 bit 有效数据”。24 bit 数据常放在 32 bit 槽中。
- BCLK 必须足够容纳槽宽和通道数。
- Codec 可能要求特定 MCLK/fs 比。
- 44.1 kHz 家族和 48 kHz 家族需要不同的时钟源/PLL。

## 数据格式

### I2S 标准格式

- LRCLK 变化后，数据延迟一个 BCLK 周期才开始。
- 左声道通常在 LRCLK 低电平时传输（具体以器件定义为准）。
- 数据 MSB 先传。

### Left Justified（LJ）

- LRCLK 变化后立即开始数据。
- 没有 I2S 的一周期延迟。
- 需要确认接收端是否支持。

### Right Justified（RJ）

- 数据对齐到 LRCLK 边沿的末尾。
- 位宽和槽宽必须匹配。

### DSP / TDM

- 一帧内多个时隙。
- 适合多通道音频、数字麦克风阵列。
- 需要配置时隙数、时隙宽度、通道映射。

格式不匹配的典型表现：

- 声音变调/变速。
- 左右声道交换。
- 噪声、爆音。
- 只有一半数据或全静音。
- 24 bit 数据被当成 32 bit，幅度异常。

## 主从关系

音频链路必须明确谁提供：

```text
BCLK
LRCLK
MCLK
```

常见模式：

| 模式         | 时钟提供者                         | 适用              |
| ------------ | ---------------------------------- | ----------------- |
| SoC Master   | SoC 提供 BCLK/LRCLK，可能提供 MCLK | 常见              |
| Codec Master | Codec 提供 BCLK/LRCLK              | Codec 有 PLL/晶振 |
| 外部时钟     | 专用时钟芯片提供 MCLK              | 高音质/多设备同步 |

两边都做 Master 或都做 Slave 都会失败。主从配置错误时，常见现象是完全没有数据或时钟频率不对。

## Codec 初始化

典型顺序：

1. 上电，等待 Codec 电源稳定。
2. 提供 MCLK（如需要）。
3. 通过 I2C/SPI 写寄存器：时钟源、采样率、位宽、格式、通路、增益、静音。
4. 配置 I2S 主从和格式。
5. 使能 DAC/ADC、功放。
6. 启动 DMA/音频流。
7. 取消静音。

注意：

- Codec 寄存器写入需要延时/轮询确认。
- 功放使能顺序不当会产生爆音。
- 先静音再切换采样率/时钟。
- 低功耗唤醒后要重新配置时钟和通路。

## DMA 与缓冲

音频是连续流，DMA 缓冲不足会导致：

- underflow：播放断音、爆音。
- overflow：录音丢样。
- 周期性咔哒声。
- CPU 负载高时更明显。

常见策略：

- 双缓冲/多缓冲。
- 半传输/传输完成中断。
- 缓冲区按音频周期对齐。
- 高优先级音频线程/中断。
- 避免在音频回调里做阻塞操作。
- 监控 underflow/overflow 计数。

## 常见故障树

```text
完全无声
├── 电源/复位/功放使能
├── MCLK/BCLK/LRCLK 缺失
├── 主从配置错误
├── Codec 未初始化/静音
├── I2S 数据线接反
└── DMA 未启动

声音变速/变调
├── 采样率配置错误
├── MCLK 倍频错误
├── BCLK/LRCLK 比例错误
├── 时钟源不稳定
└── 两端格式不一致

噪声/爆音
├── 位宽/格式不匹配
├── DMA underflow
├── 时钟抖动/地噪声
├── 功放使能顺序
└── 电源纹波

左右声道反
├── LRCLK 极性
├── 通道映射
├── PCB 接线
└── Codec 寄存器
```

| 现象            | 优先检查                           |
| --------------- | ---------------------------------- |
| 无声音          | 时钟、Codec 初始化、静音、功放使能 |
| 声音变速        | 采样率、MCLK 倍频、BCLK/LRCLK      |
| 噪声/爆音       | 位宽、格式、DMA underflow、地噪声  |
| 左右声道反      | LRCLK 极性、通道映射、接线         |
| 只有单声道      | 槽宽/通道数、数据线、Codec 通路    |
| 24 bit 幅度异常 | 数据对齐、槽宽、有效位             |
| 录音丢样        | DMA overflow、CPU 负载、缓冲大小   |

## 测量方法

- 示波器测量 MCLK、BCLK、LRCLK 频率和相位。
- 逻辑分析仪解码 I2S 数据和通道。
- 用音频分析仪/示波器 FFT 看失真、噪声和频率响应。
- 用已知正弦波测试左右声道和幅度。
- 长时间播放/录音，统计 underflow/overflow。

## 设计检查清单

- 主从角色明确。
- MCLK/BCLK/LRCLK 频率和倍频关系正确。
- 数据格式、位宽、槽宽、对齐方式两端一致。
- Codec 初始化顺序和静音/功放时序正确。
- I2S 数据线方向和 PCB 连接正确。
- DMA 缓冲大小和音频周期匹配。
- 时钟走线短、远离噪声源。
- 电源和地回流满足音频噪声要求。
- 低功耗唤醒后重新配置音频通路。
- 量产测试覆盖左右声道、采样率、音量和底噪。

## 最小实验

1. 输出 1 kHz 正弦波，测量左右声道和频率。
2. 切换 44.1 kHz/48 kHz，确认 MCLK/BCLK/LRCLK 变化。
3. 把 24 bit 数据放入 32 bit 槽，验证幅度和对齐。
4. 减小 DMA 缓冲，观察 underflow 和爆音。
5. 用逻辑分析仪解码 I2S，确认 LRCLK 极性和通道映射。

## 关联文档

- [i2c-deep-dive.md](i2c-deep-dive.md)：Codec 的 I2C 控制通路。
- [spi-deep-dive.md](spi-deep-dive.md)：Codec 的 SPI 控制通路。
- [../guides/troubleshooting/MEASUREMENT_EXAMPLES.md](../guides/troubleshooting/MEASUREMENT_EXAMPLES.md)：测量样例。
- [../guides/troubleshooting/SCHEMATIC_CHECKLISTS.md](../guides/troubleshooting/SCHEMATIC_CHECKLISTS.md)：原理图检查清单。
