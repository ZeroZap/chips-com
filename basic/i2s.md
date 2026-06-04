# I2S

## 定位

I2S 是音频串行接口，用于数字音频数据传输。

常见设备：

- 音频 Codec。
- 数字麦克风。
- DAC。
- ADC。
- SoC 音频接口。

## 常见信号

```text
BCLK：Bit Clock
LRCLK / WS：左右声道选择
SD：串行音频数据
MCLK：主时钟，可选但常见
```

## 核心参数

```text
Sample Rate：采样率，如 44.1k/48k
Bit Depth：位深，如 16/24/32 bit
Channels：声道数
Format：I2S/Left Justified/Right Justified/DSP
Clock Master：谁提供时钟
```

## 主从关系

音频链路必须明确谁提供：

```text
BCLK
LRCLK
MCLK
```

SoC 可做 Master，Codec 也可能做 Master。

两边都做 Master 或都做 Slave 都会失败。

## 常见错误

| 现象 | 优先检查 |
| --- | --- |
| 无声音 | 时钟、Codec 初始化、静音、功放使能 |
| 声音变速 | 采样率、MCLK 倍频 |
| 噪声/爆音 | 位宽、格式、DMA underflow |
| 左右声道反 | LRCLK 极性、通道映射 |

## 检查清单

- BCLK/LRCLK/MCLK 存在且频率正确。
- Master/Slave 角色明确。
- 位深和格式两端一致。
- Codec 通过 I2C/SPI 初始化完成。
- DMA 缓冲区持续供给数据。
