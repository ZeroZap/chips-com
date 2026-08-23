# I2C 主题总览

## 目标

I2C 是 chips-com 的核心主题之一, 围绕 "板内管理总线" 已经形成 10 篇专题笔记。本文档是**总览导航**, 帮助不同读者快速找到自己需要的资料。

如果你第一次接触 I2C, 建议按"读者路径"一节选一条路径读完。如果你已经有明确问题, 直接跳到"主题地图"。

## 主题地图

```text
chips-com/basic/i2c-*.md
│
├── 速查层
│   └── i2c-practical.md                调试流程速查
│
├── 原理层
│   └── i2c-deep-dive.md                完整原理 + 故障树 + 多平台 + 日志样板
│
├── 实战层
│   ├── i2c-bus-recovery-playbook.md    8 步恢复 SOP + 可拷代码 + 验收清单
│   └── i2c-failure-cases.md            20 个产线死机案例
│
└── 专题层
    ├── i2c-rtos-integration.md         RT-Thread / Zephyr / FreeRTOS 集成
    ├── i2c-multimaster.md              多主机仲裁
    ├── i2c-smbus-timeout.md            SMBus timeout
    ├── i2c-linux-fault-injection.md    Linux i2c-stub / fault injection
    ├── i2c-state-machine.md            状态机 + DMA + 中断
    └── i2c-vs-smbus-recovery.md        I2C vs SMBus 恢复行为对比
```

## 读者路径

### 路径 A: "我刚接触 I2C, 想入门" (新人)

按顺序读, 1-2 天能上手:

1. **`i2c-practical.md`** — 调试流程速查, 10 分钟读完
2. **`i2c-deep-dive.md`** — 原理 + 体系, 重点看:
   - "## I2C 的工程定位"
   - "## 开漏结构为什么重要"
   - "## 7-bit 地址和 8-bit 地址"
   - "## ACK/NACK 定位"
   - "## 总线被拉死" 章节
3. **`i2c-bus-recovery-playbook.md`** — 实战手册, 30 分钟现场排障流程

### 路径 B: "我在做产线死机, 卡在 SDA 拉低" (现场救火)

按顺序读, 30-60 分钟能定位:

1. **`i2c-bus-recovery-playbook.md`** 第 1-3 节 — 30 分钟排障流程
2. **`i2c-deep-dive.md`** "## 总线被拉死" 章节 — 故障树
3. **`i2c-failure-cases.md`** — 找类似案例 (20 个, 大概率命中)
4. **`i2c-state-machine.md`** 第 4 节 — 常见死锁和竞态

### 路径 C: "我在做面试题, 准备嵌入式面试" (求职)

按顺序读, 能答 I2C 任何题:

1. **`i2c-practical.md`** — 调试速查
2. **`i2c-deep-dive.md`** — 原理, 重点:
   - "## 开漏结构为什么重要"
   - "## 总线被拉死" 章节 (8 步 SOP)
3. **`i2c-bus-recovery-playbook.md`** 第 9 节 — 面试回答模板 (1 分钟 + 5 分钟版)
4. **`i2c-multimaster.md`** — 多主机面试加分
5. **`i2c-smbus-timeout.md`** — SMBus timeout 面试加分

### 路径 D: "我在写 I2C 驱动, 要落地代码" (工程实现)

按顺序读, 能产出可量产代码:

1. **`i2c-bus-recovery-playbook.md`** — 代码骨架直接拷
2. **`i2c-state-machine.md`** — 状态机 + ISR + 线程 + DMA
3. **`i2c-rtos-integration.md`** — RTOS 集成模式
4. **`i2c-deep-dive.md`** "## 多平台差异表" — 选你用的平台
5. **`i2c-smbus-timeout.md`** — timeout 选型

### 路径 E: "我在做产品架构, 要做选型 / 评审" (架构师)

按主题读, 各取所需:

1. **`i2c-deep-dive.md`** "## I2C 的工程定位" — 什么场景用 I2C
2. **`i2c-multimaster.md`** — 多 bus 设计的隐藏风险
3. **`i2c-failure-cases.md`** 案例 6, 9, 14, 19 — 硬件设计教训
4. **`i2c-bus-recovery-playbook.md`** 第 9 节 — 验收清单
5. **`i2c-rtos-integration.md`** 第 4 节 — RTOS 选型

## 主题速查矩阵

按问题找文档:

| 我想知道 | 看哪里 |
| --- | --- |
| I2C 上拉电阻怎么选 | i2c-deep-dive.md "## 上拉电阻选择" |
| 7-bit 和 8-bit 地址区别 | i2c-deep-dive.md "## 7-bit 地址和 8-bit 地址" |
| ACK / NACK 怎么排查 | i2c-deep-dive.md "## ACK/NACK 定位" |
| Repeated START 是什么 | i2c-deep-dive.md "## Repeated START" |
| Clock Stretching 是什么 | i2c-deep-dive.md "## Clock Stretching" |
| SDA 被拉低怎么救 | i2c-deep-dive.md "## 总线被拉死", i2c-bus-recovery-playbook.md |
| 产线死机 30 分钟定位流程 | i2c-bus-recovery-playbook.md 第 1 节 |
| Bus recovery 代码骨架 | i2c-bus-recovery-playbook.md 第 2 节 |
| STM32 HAL 怎么实现 | i2c-bus-recovery-playbook.md 第 3 节 |
| RT-Thread / Zephyr / FreeRTOS 怎么集成 | i2c-rtos-integration.md |
| 多 master 怎么仲裁 | i2c-multimaster.md |
| SMBus timeout 数值 | i2c-smbus-timeout.md |
| Linux 怎么 fault injection | i2c-linux-fault-injection.md |
| I2C 和 SMBus 恢复有什么区别 | i2c-vs-smbus-recovery.md |
| 怎么判断设备是 SMBus 还是 I2C | i2c-vs-smbus-recovery.md |
| 状态机怎么设计 | i2c-state-machine.md |
| DMA / 中断怎么协作 | i2c-state-machine.md 第 4 节 |
| 竞态 / 死锁怎么避免 | i2c-state-machine.md 第 4 节 |
| 产线真实死机案例 | i2c-failure-cases.md |
| 错误码怎么设计 | i2c-deep-dive.md "## 错误码设计" |
| 多设备共享总线定位 | i2c-deep-dive.md "## 多设备共享总线时如何定位谁拉低了 SDA" |
| 与 SMBus / I3C 区别 | i2c-deep-dive.md "## I2C 与 SMBus", "## I2C 与 I3C" |
| 面试怎么答 I2C Bus Recovery | i2c-bus-recovery-playbook.md 第 9 节 |

## 关键概念地图

```text
I2C 总线
├── 物理层
│   ├── 开漏 (开集) 结构
│   ├── 上拉电阻
│   ├── 总线电容
│   ├── SCL 同步
│   └── Clock Stretching
│
├── 协议层
│   ├── START / STOP
│   ├── 7-bit / 10-bit 地址
│   ├── ACK / NACK
│   ├── Repeated START
│   ├── 仲裁 (多 master)
│   └── 总线空闲检测
│
├── 可靠性
│   ├── 超时 (T_TIMEOUT / T_HIGH / T_LOW)
│   ├── 总线恢复 (Bus Recovery)
│   ├── 错误码
│   └── 重试策略
│
├── 工程
│   ├── 控制器 (Master) 驱动
│   ├── 设备 (Slave) 驱动
│   ├── 状态机 + DMA + 中断
│   ├── 互斥锁 (mutex)
│   ├── MUX / 电平转换
│   └── 多 master 仲裁
│
└── 演进
    ├── SMBus (超时严格化)
    ├── PMBus (电源管理)
    └── I3C (动态地址, 中断, 高速)
```

## 文档关系图

```text
i2c-practical.md (速查, 入门)
   ↓ 引用
i2c-deep-dive.md (原理, 体系)
   ↓ 引用
i2c-bus-recovery-playbook.md (实战, 代码)
   ↓ 引用
i2c-rtos-integration.md
i2c-multimaster.md
i2c-smbus-timeout.md
i2c-linux-fault-injection.md
i2c-state-machine.md
i2c-failure-cases.md
   ↓ 全部引用
i2c-index.md (本文件, 导航)
```

## 学习路径推荐 (按角色)

### 嵌入式软件工程师
```text
速查 → 原理 → 实战 (代码) → 状态机 → RTOS 集成 → fault injection
   1d      2d       2d          1d       1d           0.5d
```

### 嵌入式硬件工程师
```text
速查 → 原理 (上拉, 电平) → 多 master → 案例 (6, 9, 14) → 验收清单
   1d      1d              0.5d         1d            0.5d
```

### 产品架构师 / 技术负责人
```text
原理 (定位) → 多 master → 案例汇总 → 验收清单
   0.5d       0.5d       0.5d        0.5d
```

### 求职 / 面试准备
```text
速查 → 原理 (总) → 实战 (SOP) → 面试模板 → 多 master / SMBus 加分
   0.5d   1d         0.5d        0.5d          1d
```

## 文档维护

| 文档 | 更新频率 | 维护者 |
| --- | --- | --- |
| i2c-practical.md | 改版才更新 | 速查 / 调试流程 |
| i2c-deep-dive.md | 改版才更新 | 原理体系 |
| i2c-bus-recovery-playbook.md | 产线案例新增时 | 实战 SOP |
| i2c-rtos-integration.md | RTOS 改版时 | 平台集成 |
| i2c-multimaster.md | 改版才更新 | 多 master |
| i2c-smbus-timeout.md | 改版才更新 | SMBus |
| i2c-linux-fault-injection.md | kernel 大版本更新 | Linux 实操 |
| i2c-state-machine.md | 改版才更新 | 状态机 |
| i2c-failure-cases.md | **持续更新** | 产线案例 |
| i2c-index.md | 新增 / 删除文档时 | 导航 |

## 关联主题 (chips-com 其他目录)

- **`bus/smbus.md` / `smbus-pmbus-practical.md`** — SMBus / PMBus, I2C 的严格化扩展
- **`bus/i3c.md` / `i3c-deep-dive.md`** — I3C, I2C 的演进
- **`bus/mipi-csi-dsi-debug.md`** — 摄像头 I2C 初始化和调试
- **`bus/fpd-link-gmsl-practical.md`** — 远端 I2C, SerDes 反向通道
- **`bus/hdmi-edp-practical.md`** — DDC I2C, EDID 读取

## 一句话总结

I2C 是简单但容易出问题的总线。**核心是"开漏 + 超时 + 恢复"**。从原理到产线案例, 这 10 篇笔记覆盖完整知识体系。读者根据自己角色选一条路径读完即可。

## 更新记录

- 2026-07-24: 初版, 10 篇笔记全部完成
