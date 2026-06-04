# QSPI / OSPI

## 定位

QSPI 和 OSPI 是 SPI Flash 的高速扩展接口。

常见用途：

- 外部 NOR Flash。
- XIP 执行代码。
- 字库、图片、固件存储。
- 高速启动介质。

## 与普通 SPI 的区别

普通 SPI：

```text
MOSI/MISO 单线收发
```

QSPI：

```text
IO0~IO3 四线数据
```

OSPI：

```text
IO0~IO7 八线数据
```

## 传输阶段

Flash 访问通常包括：

```text
Command
Address
Mode bits
Dummy cycles
Data
```

每个阶段可能使用不同线宽：

```text
1-1-4
1-4-4
4-4-4
8-8-8
```

## 关键配置

- 命令码。
- 地址长度，24-bit 或 32-bit。
- dummy cycle。
- Quad Enable 位。
- DDR/SDR 模式。
- memory-mapped 模式。
- XIP 缓存策略。

## 常见错误

| 现象 | 优先检查 |
| --- | --- |
| 普通 SPI 能读，QSPI 不能 | QE 位、线宽、dummy cycle |
| 大地址读错 | 3-byte/4-byte 地址模式 |
| XIP 崩溃 | cache、dummy、时钟过高、映射配置 |
| 写入失败 | Write Enable、WIP、保护位 |

## 检查清单

- 先用普通 SPI 读 JEDEC ID。
- 启用 QE 后再进入 Quad 模式。
- dummy cycle 与频率匹配。
- 24/32-bit 地址模式正确。
- 高速前先低速验证读写擦。
- XIP 场景处理 cache 和擦写限制。
