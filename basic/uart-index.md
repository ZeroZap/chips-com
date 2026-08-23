# UART 主题总览

## 目标

UART 是 chips-com 的核心主题之一, 围绕"板间异步串行通信"已经形成 6 篇专题笔记。本文档是**总览导航**, 帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/basic/uart-*.md
│
├── 速查层
│   └── uart-practical.md             调试流程速查
│
├── 原理层
│   └── uart-deep-dive.md             完整原理 + 故障树 + 波特率 + 错误码
│
├── 实战层
│   ├── uart-failure-cases.md         20 个产线死机案例
│   ├── uart-rs485-and-flow-control.md  RS485 / 流控专题
│   └── uart-dma-circular-and-rtos.md   DMA + 环形缓冲 + RTOS
│
└── 导航
    └── uart-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 UART, 想入门" (新人)

1. **`uart-practical.md`** — 调试流程速查, 10 分钟
2. **`uart-deep-dive.md`** — 原理, 重点:
   - "## UART 接收为什么能不同步"
   - "## 过采样"
   - "## 波特率误差"
   - "## 校验位能解决什么"
3. **`uart-dma-circular-and-rtos.md`** 第 1-2 节 — DMA 和环形缓冲

### 路径 B: "我在做产线 UART 通信失败" (现场救火)

1. **`uart-practical.md`** "## 5 秒钟定位"
2. **`uart-deep-dive.md`** "## UART 故障树"
3. **`uart-failure-cases.md`** — 找类似案例 (20 个)
4. **`uart-rs485-and-flow-control.md`** 第 4 节 — RS485 方向控制

### 路径 C: "我在做 RS485 / Modbus / 工业通信" (工程实现)

1. **`uart-rs485-and-flow-control.md`** — RS485 完整专题
2. **`uart-dma-circular-and-rtos.md`** — DMA + 环形缓冲
3. **`uart-failure-cases.md`** 案例 4 / 9 / 10 — RS485 方向 + 距离 + 冲突
4. **`rs485-modbus-rtu-deep-dive.md`** — Modbus RTU 协议

### 路径 D: "我在写 UART 驱动, 要落地代码" (工程实现)

1. **`uart-dma-circular-and-rtos.md`** — 完整代码骨架
2. **`uart-rs485-and-flow-control.md`** — RS485 严格时序
3. **`uart-deep-dive.md`** "## UART 状态机" / "## UART 错误码设计"
4. **`uart-failure-cases.md`** — 看常见坑

### 路径 E: "我在做高速 (>= 1M) UART / 固件下载" (性能)

1. **`uart-deep-dive.md`** "## 波特率计算与误差"
2. **`uart-dma-circular-and-rtos.md`** — DMA + 环形缓冲 + 性能
3. **`uart-rs485-and-flow-control.md`** 第 5 节 — 硬件流控
4. **`uart-failure-cases.md`** 案例 3 / 12 — 高速丢包 + 流控

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| 波特率怎么算, 误差多少 | uart-deep-dive.md "## 波特率计算与误差" |
| 帧格式 (8N1, 8E1) 是什么 | uart-deep-dive.md "## UART 帧格式细节" |
| TX/RX 接反了 | uart-failure-cases.md 案例 1 |
| 乱码怎么定位 | uart-deep-dive.md "## UART 故障树" + uart-failure-cases.md 案例 2 |
| 高速丢字节 | uart-failure-cases.md 案例 3 / uart-dma-circular-and-rtos.md |
| RS485 怎么接 | uart-rs485-and-flow-control.md 第 1-2 节 |
| RS485 方向控制时序 | uart-rs485-and-flow-control.md 第 3 节 |
| RS485 总线冲突 | uart-failure-cases.md 案例 10 |
| 长距离 RS485 | uart-failure-cases.md 案例 9 |
| 硬件流控 (RTS/CTS) | uart-rs485-and-flow-control.md 第 5 节 |
| 软件流控 (XON/XOFF) | uart-rs485-and-flow-control.md 第 6 节 |
| DMA 怎么用 | uart-dma-circular-and-rtos.md 第 2 节 |
| 环形缓冲怎么实现 | uart-dma-circular-and-rtos.md 第 1 节 |
| 不定长接收 (idle) | uart-dma-circular-and-rtos.md 第 3 节 |
| RTOS 怎么集成 | uart-dma-circular-and-rtos.md 第 5 节 |
| 多任务并发 | uart-dma-circular-and-rtos.md 第 6 节 |
| 协议分帧 | uart-dma-circular-and-rtos.md 第 4 节 |
| 产线死机案例 | uart-failure-cases.md |
| UART vs SPI vs I2C | uart-deep-dive.md "## UART vs SPI vs I2C 选型决策" |
| Modbus RTU | rs485-modbus-rtu-deep-dive.md |

## 关键概念地图

```text
UART 总线
├── 物理层
│   ├── TTL (MCU 引脚, 0/3.3V)
│   ├── RS232 (+/-12V, MAX232)
│   ├── RS485 (差分 A/B, 半双工/全双工)
│   └── RS422 (差分, 全双工)
│
├── 协议层
│   ├── 异步 (无时钟)
│   ├── 帧 (start + data + parity + stop)
│   ├── 波特率 (双方匹配)
│   └── LSB first
│
├── 错误处理
│   ├── ORE (overrun)
│   ├── PE (parity)
│   ├── FE (framing)
│   ├── NE (noise)
│   └── Break
│
├── 工程
│   ├── DMA + 环形缓冲
│   ├── 协议分帧 (SOF + LEN + CRC)
│   ├── 多任务并发 (mutex)
│   ├── RS485 方向控制 (TC 标志)
│   └── 流控 (RTS/CTS / XON-XOFF)
│
└── 演进
    ├── Modbus RTU (主从协议)
    ├── 工业总线 (Profibus, CAN)
    └── USB CDC (USB 模拟串口)
```

## 文档关系图

```text
uart-practical.md (速查, 入门)
   ↓ 引用
uart-deep-dive.md (原理, 体系)
   ↓ 引用
uart-failure-cases.md (案例, 实战)
uart-rs485-and-flow-control.md (RS485 / 流控)
uart-dma-circular-and-rtos.md (代码骨架)
   ↓ 全部引用
uart-index.md (本文件, 导航)
```

## 学习路径推荐 (按角色)

### 嵌入式软件工程师
```text
速查 → 原理 → DMA/环形缓冲 → RS485/流控 → RTOS 集成
  0.5d   1d       1d             1d         1d
```

### 嵌入式硬件工程师
```text
速查 → 原理 (baud, 帧, 电平) → RS485 硬件 → 案例 (接线, EMC)
  0.5d   1d                       0.5d          0.5d
```

### 工业 / 自动化工程师
```text
速查 → RS485 / 流控 → Modbus RTU → 案例 (距离, 冲突)
  0.5d   1d              1d           0.5d
```

### 产品架构师
```text
原理 (定位) → 选型决策 → RS485 / Modbus 选型
  0.5d       0.5d         0.5d
```

## UART vs SPI vs I2C 速查

| 维度 | UART | SPI | I2C |
| --- | --- | --- | --- |
| 速度 | 中 (<= 6M) | 高 (10M~200M) | 低 (<= 3.4M) |
| 引脚 | 2-4 (TX, RX, RTS, CTS) | 4-7 (SCLK, MOSI, MISO, CS) | 2 (SCL, SDA) |
| 多设备 | 地址 / 协议层 | 独立 CS / 菊花链 | 地址 (7/10 bit) |
| 协议复杂度 | 简单 (字节流) | 简单 (无地址) | 中等 (ACK, 地址) |
| 时钟 | 异步 (无时钟线) | 同步 | 同步 |
| 物理距离 | 长 (RS485 可 1km) | 短 (< 30cm) | 短 (< 30cm) |
| 总线恢复 | 不需要 | 不需要 | 必须 (8 步 SOP) |
| 典型场景 | 调试口, RS485, GPS, 蓝牙 | Flash, LCD, ADC | PMIC, 温度, RTC, sensor |

**选型建议**:

- 异步 + 长距离 + 多设备 → **UART/RS485**
- 高速 + 短距离 + 大量数据 → **SPI**
- 板内低速 + 多个设备 → **I2C**
- 调试口 (printf) → **UART**

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| uart-practical.md | 改版才更新 | 速查 / 调试流程 |
| uart-deep-dive.md | 改版才更新 | 原理体系 |
| uart-failure-cases.md | **持续更新** | 产线案例 |
| uart-rs485-and-flow-control.md | 改版才更新 | RS485 / 流控 |
| uart-dma-circular-and-rtos.md | 改版才更新 | DMA / RTOS |
| uart-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题 (chips-com 其他目录)

- **`i2c-*.md`** — I2C 主题 (12 篇, 145 KB, 对比)
- **`spi-*.md`** — SPI 主题 (6 篇, 75 KB, 对比)
- **`rs232-rs485.md`** — 物理层基础
- **`modbus.md`** / **`rs485-modbus-rtu-deep-dive.md`** — Modbus RTU
- **`can.md`** — CAN 总线 (用户后续单独做)
- **`mipi-csi-dsi-debug.md`** — 串口调试 sensor

## 一句话总结

UART 是最简单的异步总线, 但**协议分帧 + RS485 时序 + 流控 + 异步日志**是产线死机的 4 大根因区。从原理到产线案例, 6 篇笔记覆盖完整。

## 更新记录

- 2026-07-24: 初版, 6 篇笔记全部完成
