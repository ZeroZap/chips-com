---
tags:
  - layer/basic
  - type/index
  - protocol/spi
---

# SPI 主题总览

## 目标

SPI 是 chips-com 的核心主题之一, 围绕"板内高速串行通信"已经形成 6 篇专题笔记。本文档是**总览导航**, 帮助不同读者快速找到自己需要的资料。

## 主题地图

```text
chips-com/basic/spi-*.md
│
├── 速查层
│   └── spi-practical.md             调试流程速查
│
├── 原理层
│   └── spi-deep-dive.md             完整原理 + 故障树 + 速度档 + 信号完整性
│
├── 实战层
│   ├── spi-failure-cases.md         21 个产线死机案例
│   ├── spi-multislave-and-dma.md    多从 / 菊花链 / DMA / 中断
│   └── spi-rtos-integration.md      RT-Thread / Zephyr / FreeRTOS 集成
│
└── 导航
    └── spi-index.md (本文件)
```

## 读者路径

### 路径 A: "我刚接触 SPI, 想入门" (新人)

按顺序读, 1 天能上手:

1. **[[basic/spi-practical|spi-practical]]** — 调试流程速查, 10 分钟
2. **[[basic/spi-deep-dive|spi-deep-dive]]** — 原理, 重点:
   - "## SPI 的本质"
   - "## CPOL 和 CPHA 的真实含义"
   - "## CS 是事务边界"
   - "## SPI 速度不是越高越好"
3. **[[basic/spi-multislave-and-dma|spi-multislave-and-dma]]** 第 1-2 节 — 多从设备和 DMA

### 路径 B: "我在做产线 SPI 通信失败" (现场救火)

1. **[[basic/spi-practical|spi-practical]]** "## 5 秒钟定位"
2. **[[basic/spi-deep-dive|spi-deep-dive]]** "## SPI 故障树"
3. **[[basic/spi-failure-cases|spi-failure-cases]]** — 找类似案例 (21 个)
4. **[[basic/spi-multislave-and-dma|spi-multislave-and-dma]]** 第 4 节 — race condition

### 路径 C: "我在写 SPI 驱动, 要落地代码" (工程实现)

1. **[[basic/spi-multislave-and-dma|spi-multislave-and-dma]]** — 完整代码骨架
2. **[[basic/spi-rtos-integration|spi-rtos-integration]]** — RTOS 集成
3. **[[basic/spi-deep-dive|spi-deep-dive]]** "## SPI 状态机" / "## SPI 错误码设计"
4. **[[basic/spi-failure-cases|spi-failure-cases]]** — 看常见坑

### 路径 D: "我在做高速 SPI / QSPI" (Flash / LCD)

1. **[[basic/spi-deep-dive|spi-deep-dive]]** "## SPI 速度不是越高越好" / "## 高速 SPI 信号完整性"
2. **[[basic/spi-multislave-and-dma|spi-multislave-and-dma]]** "## SPI + DMA 模式" / "## DMA + Cache 一致性"
3. **[[basic/qspi-ospi|qspi-ospi]]** — 高速 SPI Flash 专题

### 路径 E: "我在做产品架构, 选型" (架构师)

1. **[[basic/spi-deep-dive|spi-deep-dive]]** "## SPI vs I2C 选型决策"
2. **[[basic/spi-practical|spi-practical]]** "## SPI vs I2C 选型速查"
3. **[[basic/spi-rtos-integration|spi-rtos-integration]]** "## 方案 3: 多 SPI 控制器" — 性能 vs 复杂度

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| SPI Mode 0/1/2/3 怎么选 | [[basic/spi-deep-dive\|spi-deep-dive]] "## CPOL 和 CPHA 的真实含义" |
| CS 时序有什么要求 | [[basic/spi-deep-dive\|spi-deep-dive]] "## CS 是事务边界" / "## 硬件 NSS 和软件 CS" |
| dummy byte / dummy cycle 是什么 | [[basic/spi-deep-dive\|spi-deep-dive]] "## Dummy byte 和 dummy cycle" |
| 多从设备怎么管理 | [[basic/spi-multislave-and-dma\|spi-multislave-and-dma]] 第 1 节 |
| 菊花链怎么接 | [[basic/spi-multislave-and-dma\|spi-multislave-and-dma]] 第 2 节 |
| DMA 怎么用 | [[basic/spi-multislave-and-dma\|spi-multislave-and-dma]] 第 3 节 |
| 中断优先级怎么配 | [[basic/spi-multislave-and-dma\|spi-multislave-and-dma]] 第 4 节 / [[basic/spi-rtos-integration\|spi-rtos-integration]] |
| SPI 失败怎么定位 | [[basic/spi-deep-dive\|spi-deep-dive]] "## SPI 故障树" |
| 产线 SPI 死机案例 | [[basic/spi-failure-cases\|spi-failure-cases]] |
| SPI vs I2C 选哪个 | [[basic/spi-deep-dive\|spi-deep-dive]] "## SPI vs I2C 选型决策" |
| 高速 SPI 怎么稳定 | [[basic/spi-deep-dive\|spi-deep-dive]] "## 高速 SPI 信号完整性" |
| SPI Flash 写不进 | [[basic/spi-failure-cases\|spi-failure-cases]] 案例 2 / [[basic/spi-deep-dive\|spi-deep-dive]] "## SPI Flash 基础命令" |
| 多任务并发访问 | [[basic/spi-rtos-integration\|spi-rtos-integration]] "## 多任务并发访问" |
| RTOS 怎么集成 | [[basic/spi-rtos-integration\|spi-rtos-integration]] |
| QSPI 怎么用 | [[basic/qspi-ospi\|qspi-ospi]] |

## 关键概念地图

```text
SPI 总线
├── 物理层
│   ├── SCLK 时钟
│   ├── MOSI / MISO / SIO
│   ├── CS 片选
│   └── 模式 (Mode 0/1/2/3)
│
├── 协议层
│   ├── 命令 + 地址 + 数据
│   ├── Dummy cycle
│   ├── 单/双/四线 (1/2/4-line)
│   └── 菊花链
│
├── 设备
│   ├── Flash (JEDEC ID, Write Enable, WIP, 跨页)
│   ├── LCD / Display
│   ├── ADC / DAC
│   ├── Sensor (IMU, 气压, ...)
│   └── 移位寄存器
│
├── 工程
│   ├── 多从设备 (独立 CS)
│   ├── 速度切换 (Mode, hz, bit order, word size)
│   ├── DMA + 中断
│   ├── 互斥 (mutex, 多 SPI)
│   └── 错误处理 (重试, abort)
│
└── 演进
    ├── QSPI / OSPI (4/8 线, 高速)
    ├── SPI 兼容 I2S (音频)
    └── SDIO (SD 卡)
```

## 文档关系图

```text
spi-practical.md (速查, 入门)
   ↓ 引用
spi-deep-dive.md (原理, 体系)
   ↓ 引用
spi-failure-cases.md (案例, 实战)
spi-multislave-and-dma.md (代码骨架)
spi-rtos-integration.md (RTOS 集成)
   ↓ 全部引用
spi-index.md (本文件, 导航)
```

## 学习路径推荐 (按角色)

### 嵌入式软件工程师
```text
速查 → 原理 → 多从/DMA → 产线案例 → RTOS 集成
  0.5d   1d      1d         1d         1d
```

### 嵌入式硬件工程师
```text
速查 → 原理 (Mode, CS, 速度) → 案例 (接线, EMC) → 高速信号完整性
  0.5d   1d                  0.5d              0.5d
```

### 产品架构师 / 技术负责人
```text
原理 (定位) → 选型决策 → RTOS 集成方案
  0.5d       0.5d         0.5d
```

## SPI vs I2C 速查

| 维度 | SPI | I2C |
| --- | --- | --- |
| 速度 | 高 (10MHz ~ 100MHz+) | 低 (<= 3.4MHz) |
| 引脚 | 4-7 (含 CS) | 2 (SCL, SDA) |
| 多设备 | 独立 CS 或菊花链 | 地址 + 7/10 bit |
| 协议复杂度 | 简单 (无地址, 无 ACK) | 复杂 (地址, ACK/NACK) |
| 时序要求 | Mode + CS 时序 | 开漏 + 上拉 + timeout |
| 可靠性 | 高 (推挽) | 中 (开漏, 易受干扰) |
| 长距离 | 短 (< 30cm) | 短 (< 30cm) |
| 总线恢复 | 不需要 | 必须 (8 步 SOP) |
| 典型场景 | Flash, LCD, ADC, 高速 sensor | PMIC, 温度, RTC, 低速 sensor |

**选型建议**:

- 高速 + 短距离 + 少量设备 → **SPI**
- 低速 + 板内管理 + 多设备 → **I2C**
- 简单点对点 → 都可以
- 距离 > 30cm → 都不推荐, 改 RS485 / 差分

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| [[basic/spi-practical\|spi-practical]] | 改版才更新 | 速查 / 调试流程 |
| [[basic/spi-deep-dive\|spi-deep-dive]] | 改版才更新 | 原理体系 |
| [[basic/spi-failure-cases\|spi-failure-cases]] | **持续更新** | 产线案例 |
| [[basic/spi-multislave-and-dma\|spi-multislave-and-dma]] | 改版才更新 | 多从 / DMA |
| [[basic/spi-rtos-integration\|spi-rtos-integration]] | RTOS 改版时 | RTOS 集成 |
| [[basic/spi-index\|spi-index]] | 新增 / 删除文档时 | 导航 |

## 关联主题 (chips-com 其他目录)

- **[[basic/i2c-index|I2C]]** — I2C 主题 (12 篇, 145 KB, 对比)
- **[[basic/qspi-ospi|qspi-ospi]]** — 高速 SPI Flash
- **[[basic/spi-deep-dive|spi-deep-dive]]** "## SPI 与 QSPI 区别" 部分

## 一句话总结

SPI 是简单的高速总线, 关键是 **Mode 选对 + CS 时序对 + 速度分档 + DMA 边界**。从原理到产线案例, 6 篇笔记覆盖完整。

## 更新记录

- 2026-07-24: 初版, 6 篇笔记全部完成
