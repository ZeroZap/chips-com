# 主题完成度矩阵与执行计划

## 目标

把 chips-com 知识库当前状态做一份"完成度快照", 并对每个待做主题, 按今天 I2C 学习模式拆解成具体执行步骤。

本文是**元数据**, 指导后续每一轮主题的扩展。每完成一个主题, 更新对应行。

## 评分标准

| 分 | 等级 | 标准 | 典型形态 |
| --- | --- | --- | --- |
| 5 | L4 闭环 | 速查 + 原理 + 实战 + 案例 + 专题 + 导航, 6+ 篇 50+ KB | I2C / SPI / UART |
| 4 | L3 实战 | deep-dive + failure-cases, 2-3 篇 15+ KB | UDS / J1939 |
| 3 | L2 原理 | 单篇 deep-dive, 8-15 KB | I3C / FPD-Link / HDMI/eDP |
| 2 | L1 速查 | 单篇 practical, 2-5 KB | One-Wire / SDIO |
| 1 | L0 简介 | 1 KB 概念笔记 | GPIO / PWM / ADC |
| 0 | 空白 | 完全没有 | LoRa / Thread / Matter |

## 当前完成度矩阵 (2026-07-28)

### basic/ 物理层接口 (L0-L1)

| 主题 | 分 | 现状 | 升级目标 |
| --- | --- | --- | --- |
| GPIO | 1 | 1.6 KB 简介 | L2 (deep-dive + 故障树 + 案例) |
| PWM | 1 | 1.4 KB 简介 | L2 |
| ADC/DAC | 1 | 1.4 KB 简介 | L2 |
| JTAG/SWD | 1 | 1.2 KB 简介 | L2 |
| I2S | 1 | 1.2 KB 简介 | L2 |
| LVDS | 1 | 1.2 KB 简介 | L2 |
| CAN PHY | 1 | 1.1 KB 简介 | L2 |
| Ethernet PHY | 1 | 1.1 KB 简介 | L2 |
| RS232/RS485 | 1 | 1.4 KB 简介 | L2 |
| QSPI/OSPI | 1 | 1.2 KB 简介 | L2 |

### basic/ 协议层 ★ 完整闭环主题

| 主题 | 分 | 现状 | 升级目标 |
| --- | --- | --- | --- |
| **I2C** | **5** | **11 篇 151 KB 完整闭环** | 维护 |
| **SPI** | **5** | **6 篇 75 KB 完整闭环** | 维护 |
| **UART** | **5** | **6 篇 80 KB 完整闭环** | 维护 |

### bus/ 汽车与工业

| 主题 | 分 | 现状 | 升级目标 |
| --- | --- | --- | --- |
| **CAN** | **5** | **basic/can-* 8 篇 ~120 KB 完整闭环** | **维护** |
| CANopen | 3 | bus/canopen.md 0.7 KB + bus/can-canopen-*.md 15 KB | 升级为 CAN 闭环一部分 |
| J1939 | **5** | **bus/j1939-* 7 篇 ~88 KB L4 完整闭环** | **维护** |
| UDS | 3 | 3 篇 25.6 KB | L4 闭环 |
| ISO-TP | 2 | 3 篇 4.6 KB (简介级) | L3 |
| LIN | 1 | 1 篇 2.9 KB practical | L2-L3 |
| Profinet | 3 | 3 篇 18.6 KB | L4 |
| Profibus | 3 | 3 篇 13.7 KB | L4 |
| EtherCAT | 2 | 1 篇 4.4 KB deep-dive | L3 |
| Modbus RTU | 3 | 2 篇 12.3 KB | L3 |

### bus/ 高速总线

| 主题 | 分 | 现状 | 升级目标 |
| --- | --- | --- | --- |
| **USB** | **5** | **bus/usb-* 9 篇 ~118 KB 完整闭环（+DFU 子主题 3 篇）** | **维护** |
| USB DFU | 2 | 3 篇 4.5 KB (浅) | L3 |
| Ethernet | 3 | 2 篇 9.0 KB | L3 |
| EtherNet/IP | 3 | 3 篇 24.6 KB | L4 |
| TSN | 2 | 2 篇 11.2 KB | L3 |
| PCIe | 2 | 1 篇 4.5 KB practical | L2 |

### bus/ 显示 / 视频

| 主题 | 分 | 现状 | 升级目标 |
| --- | --- | --- | --- |
| HDMI/eDP | 3 | 3 篇 12.7 KB | L4 |
| FPD-Link/GMSL | 3 | 3 篇 18.0 KB | L4 |
| MIPI CSI/DSI | 2 | 2 篇 11.5 KB | L3 |

### bus/ I2C 生态

| 主题 | 分 | 现状 | 升级目标 |
| --- | --- | --- | --- |
| I3C | 3 | 3 篇 16.8 KB | L4 |
| SMBus/PMBus | 2 | 2 篇 10.6 KB (smbus + smbus-pmbus-practical) | L3 |

### bus/ 无线 / IoT / 简单总线

| 主题 | 分 | 现状 | 升级目标 |
| --- | --- | --- | --- |
| MQTT | 2 | 3 篇 5.0 KB (浅) | L3 |
| DMX512 | 3 | 3 篇 12.4 KB | L3 |
| One-Wire | 2 | 1 篇 2.8 KB practical | L2 |
| SDIO | 2 | 1 篇 3.4 KB practical | L2 |

### bus/ 新建 L4 闭环 (5 分) (2026-08-01 新建)

| 主题 | 分 | 现状 | 升级目标 |
| --- | --- | --- | --- |
| **BLE (Bluetooth LE)** | **5** | **bus/ble-* 5 篇 ~50 KB 完整闭环** | **维护** |
| **ZigBee** | **5** | **bus/zigbee-* 5 篇 ~60 KB 完整闭环** | **维护** |
| **Matter** | **5** | **bus/matter-* 5 篇 ~60 KB 完整闭环** | **维护** |
| **Thread** | **5** | **bus/thread-* 5 篇 ~55 KB 完整闭环** | **维护** |
| **LoRa / LoRaWAN** | **5** | **bus/lora-* 5 篇 ~70 KB 完整闭环（sub-agent 写）** | **维护** |
| **LTE-IoT (Cat 1 / Cat M1 / NB-IoT)** | **5** | **bus/lte-iot-* 5 篇 ~63 KB 完整闭环（sub-agent 写）** | **维护** |
| **Satellite-IoT (NB-IoT NTN / 北斗 / Iridium / Starlink / inReach)** | **5** | **bus/satellite-iot-* 5 篇 ~78 KB 完整闭环（sub-agent 写）** | **维护** |
| **PLB (Personal Locator Beacon)** | **5** | **bus/plb-* 5 篇 ~82 KB 完整闭环（sub-agent 写）** | **维护** |
| **Rescue-Communications (卫星 SOS / 短报文 / PLB / 应急)** | **5** | **bus/rescue-comms-* 5 篇 ~68 KB 完整闭环（sub-agent 写）** | **维护** |

### bus/ 完全空白 (0 分)

| 主题 | 备注 |
| --- | --- |
| (无 - 已清空) | 待补：CAN FD / FlexRay / SENT / USB 3.x / HDMI 2.1（汽车 / 高速总线 / 视频） |
| LoRa / LoRaWAN | 待新建 |
| CAN FD / CAN XL | 待新建 |
| FlexRay | 待新建 |
| SENT / PSI5 | 待新建 |
| SPDIF / PDM / TDM | 待新建 |
| USB 3.x / Thunderbolt | 待新建 |
| HDMI 2.1 / DP 2.0 | 待新建 |

## 横向 / 纵向汇总

```
横向覆盖: 49 协议, 87/100 分
纵向深度:
  L4 闭环: 15 个   (I2C / SPI / UART / CAN / J1939 / USB / BLE / ZigBee / Matter / Thread / LoRa / LTE-IoT / Satellite-IoT / PLB / Rescue-Comms)
  L3 实战: 4 个    (UDS / EtherNet/IP / Profinet / FPD-Link)
  L2 原理: 10+ 个
  L1 速查: 大量
  L0 简介: 大量
  0 空白: 5 个    (CAN FD / FlexRay / SENT / USB 3.x / HDMI 2.1)

整体深度: 90/100 分
```

## 通用执行模板 (按今天 I2C 模式)

每一个主题的闭环扩展, 严格按以下步骤做。每一步对应一篇笔记产出。

### 步骤 1: 起点

```text
- 找 1 篇高质公众号 / 技术博客作为"种子文章"
- 建议来源: 
  - wdfk-prog 公众号 (今日用过, 质量稳定)
  - 嵌入式与 Linux 那些事
  - 裸机思维
  - STM32 官方参考
  - 大疆 / 字节 / 字节跳动 / TI / NXP 工程师博客
- 抓全文 (微信用 webfetch 经常失败, 建议用户复制粘贴)
```

### 步骤 2: 6 角度结构化拆解 (T2)

```text
1. 题面 (一句话)
2. 触发原因 (4 类常见)
3. 软/硬恢复思路 (8 步 SOP)
4. 关键代码 (可移植 C 骨架)
5. 易错点 (7+ 条)
6. 面试 / 追问点 (8 题)
```

### 步骤 3: 知识库归档 (T3)

```text
- 找现有 practical / deep-dive, 扩充内容
- 写独立 failure-cases.md (10-20 个产线死机案例)
- 如果基础薄弱, 先写一篇 "原理完整版"
```

### 步骤 4: 8 题自测 + 答案 (T4)

```text
- Q1-Q3 概念层
- Q4-Q6 实现层
- Q7-Q8 产线 / 真实场景
- 答案分两段: 简答 1-3, 详答 4-8
```

### 步骤 5: 持续 Deep Learning (横向 + 纵向扩展)

```text
横向 (扩到协议族):
  - 同协议族的对比表 (e.g. I2C vs SMBus)
  - 厂商 / 芯片实现差异 (e.g. 国产 MCU 兼容矩阵)

纵向 (深挖到专题):
  - RTOS 集成模式
  - 状态机 + DMA + 中断
  - 多 master / 多从 / 冲突
  - 产线故障注入
  - Linux kernel 实现
```

### 步骤 6: 总览导航 (index.md)

```text
- 主题地图
- 5 种读者路径 (新人 / 现场救火 / 工程实现 / 性能优化 / 架构师)
- 主题速查矩阵
- 关键概念地图
- 跨主题对比速查
```

### 步骤 7: 更新元数据

```text
- 更新本文 (TOPIC_MATRIX.md) 对应行
- 更新 INDEX.md 加新文件引用
- 更新 LEARNING_PLAN.md 阶段进度
- 更新 README.md 索引
```

## 预期产出模板

每个主题闭环, 预期产出参考 I2C 模式:

```text
L4 闭环: 6-12 篇  /  60-150 KB
  - 速查层: 1 篇
  - 原理层: 1-2 篇 (扩)
  - 实战层: 1-3 篇 (failure-cases / playbook)
  - 专题层: 2-5 篇 (RTOS / state / Linux / 对比 / 子协议)
  - 导航: 1 篇

时间 (基于今天工作量):
  - 1 篇 deep-dive 扩: 30-60 分钟
  - 1 篇 failure-cases (10-20 案例): 60-90 分钟
  - 1 篇 RTOS / 专题: 60-90 分钟
  - 1 篇 index / 跨对比: 30-60 分钟
  ─────────────────────────
  L4 闭环总时间: 4-8 小时
```

## 待做主题执行计划 (按优先级)

> **v3.x 沉淀期封口声明（2026-07-29）**：
> 6 个 L4 闭环主题 + 47 篇 607 KB 已达实战密度，暂停主动扩展。
> 以下候选主题**挂起**，等真实项目需求或实战触发再激活。
> 详见 `LEARNING_PLAN.md` 阶段 6。

### 🥇 优先级 1: CAN 闭环 (用户指定单独做)

**起点**: can.md (0.8 KB) + can-canopen-practical.md + can-canopen-deep-dive.md (15 KB)

**目标**: L4 闭环 5 分, 8-10 篇 ~120 KB

**路径**:
```text
Step 1: 找 1 篇高质量 CAN 文章 (建议: wdfk-prog 的 CAN 系列 或 CiA 官方)
Step 2: 6 角度拆解
Step 3: 扩 can-canopen-deep-dive.md, 写 can-failure-cases.md (15 案例)
Step 4: 8 题自测
Step 5: Deep Learning
  - can-multimaster-and-bus-off.md (多 master, 总线关闭, 错误帧)
  - can-fd-and-can-xl.md (CAN FD, CAN XL)
  - can-rtos-integration.md (RTOS + SocketCAN)
  - can-vs-other-bus.md (CAN vs RS485 vs FlexRay)
Step 6: can-index.md
Step 7: 更新元数据
```

**预期产出**:
```text
can-practical.md              扩   5 KB
can-deep-dive.md              扩   20 KB
can-failure-cases.md          新   20 KB
can-multimaster-and-bus-off.md 新  15 KB
can-fd-and-can-xl.md          新   12 KB
can-rtos-integration.md       新   15 KB
can-vs-other-bus.md           新   8 KB
can-index.md                  新   7 KB
─────────────────────────────
8 篇                          ~102 KB
```

**预计工期**: 4-6 小时 (跨 1-2 轮)

### 🥈 优先级 2: USB 闭环 (消费 / 嵌入式通用)

**起点**: usb.md + usb-practical.md + usb-deep-dive.md (11.7 KB)

**目标**: L4 闭环 5 分, 6-8 篇 ~80 KB

**路径**:
```text
Step 1: USB 协议文章 (推荐 USB in a NutShell / 嵌入式 USB 公众号)
Step 2: 6 角度拆解 (枚举 / 端点 / 描述符 / 事务 / 错误 / 性能)
Step 3: 扩 usb-practical + usb-deep-dive
Step 4: 8 题自测
Step 5: Deep Learning
  - usb-enumeration-and-descriptor.md (枚举, 描述符)
  - usb-dma-and-rtos.md (DMA + RTOS)
  - usb-failure-cases.md (15 案例: 枚举失败 / 端点卡死 / 描述符错)
  - usb-vs-other-bus.md
Step 6: usb-index.md
```

**预计工期**: 4-6 小时

### 🥉 优先级 3: L2 主题升级到 L3/L4

**目标主题**: J1939, UDS, Profinet, FPD-Link, EtherNet/IP

每个主题执行计划: 找 1 篇种子文章 → 6 角度拆解 → 写 failure-cases (10 案例) → 扩 deep-dive → 8 题自测 → index

**预计工期**: 每个 1-2 小时

### 4️⃣ 优先级 4: 新建空白协议

**目标主题**: BLE, ZigBee, LoRa, CAN FD, FlexRay

每个主题执行计划: 找 1 篇种子文章 → 6 角度拆解 → 写 practical + deep-dive + failure-cases + 专题

**预计工期**: 每个 4-6 小时 (从 0 到 L4)

### 5️⃣ 优先级 5: basic/ 物理层升级 (L0 → L2)

**目标主题**: GPIO, PWM, ADC, JTAG, I2S, LVDS, QSPI

**预计工期**: 每个 1-2 小时 (1 篇扩 + 1 篇 failure-cases)

## 跨主题横向工作 (持续进行)

不绑定具体主题, 但每轮主题扩展时都应包括:

```text
1. 跨协议对比表
   - I2C vs SPI vs UART (已有, 见 uart-index.md)
   - CAN vs RS485 vs FlexRay
   - USB vs PCIe vs Ethernet
   - BLE vs ZigBee vs Thread
   - I3C vs I2C vs SMBus (已有, 见 i2c-vs-smbus-recovery.md)

2. 选型决策树
   - 按速度 / 距离 / 设备数 / 实时性 / 抗干扰 / 成本

3. 通用工程方法
   - DEBUG_PLAYBOOK.md 升级
   - PROTOCOL_SELECTION.md 升级
   - 故障注入测试方法
   - 产线验收清单
```

## 文档维护规则

| 触发 | 更新 |
| --- | --- |
| 新增任何 .md | INDEX.md + LEARNING_PLAN.md + TOPIC_MATRIX.md |
| 完成某主题闭环 | 该主题分 +1, 标记 ★ |
| 升级某主题 | 该主题分 +1, 记录升级时间 |
| 删除某笔记 | 该主题分 -1, 记录原因 |
| 整体策略调整 | LEARNING_PLAN.md 改版 |

## 关联文档

- `INDEX.md` - 知识库主索引
- `LEARNING_PLAN.md` - 学习计划阶段
- `PROTOCOL_SELECTION.md` - 选型矩阵
- `DEBUG_PLAYBOOK.md` - 跨协议排障
- `TROUBLESHOOTING_QUICKREF.md` - 故障速查
- `basic/i2c-index.md` - I2C 主题 (L4 闭环示例)
- `basic/spi-index.md` - SPI 主题 (L4 闭环示例)
- `basic/uart-index.md` - UART 主题 (L4 闭环示例)

## 更新记录

- 2026-07-24: 初版, 主题完成度矩阵 + 通用执行模板 + 待做主题执行计划
- 2026-07-28: USB 主题 L4 闭环完成 (5 分 / 9 篇 ~118 KB), 整体深度 65 → 70, L4 闭环 5 → 6
- 2026-07-29: 进入 v3.x 沉淀期（封口·阶段 6），配套拉起 2 个 cron：
  - `chips-com-blindspot-scan` (激进·每天 9:00) - 扫盲区 + 报告，不动笔记
  - `chips-com-external-materials` (激进·每 5 天 9:00) - 轮询 12 个候选协议 + web 搜，写到 `_Inbox/`
  - 输出位置：`_System/cron-reports/scan-*.md` 和 `_Inbox/<协议>-<日期>-candidates.md`
- 2026-07-30: A 盲区扫描首次跑通（`_System/cron-reports/scan-2026-07-30.md`）。关键发现：**实战案例 115 条已超额（2.3×）**，封口期结束条件之一已达成。10 倍频率生效（A 每天 12 次 / B 每天 2 次 + 24h 去重）。用户决定继续封口。
