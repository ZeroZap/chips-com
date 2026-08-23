# CAN FD / CAN XL 实战案例库

## 目标

把 CAN FD（数据段 8→64B、BRS 双波特率、5+ Mbps）和 CAN XL（10+ Mbps、2048B）的产线实战案例集中：

- 采样点 / 位定时 / 晶振频偏 = 80% 产线问题根因
- 高速段（>2 Mbps）BRS 时序失配放大误差
- SocketCAN / TDC / CRC-17 等新机制
- STM32 / NXP / 瑞萨 / 瑞芯微等不同平台工具链差异

## 主题地图

```text
chips-com/bus/can-*.md（CAN FD 部分）
├── can.md                          CAN 总览（FD 在 §1 简介）
├── can-canopen-deep-dive.md        已有「## CAN FD」段
├── can-canopen-practical.md        调试实践
└── can-fd-failure-cases.md (本文件) 产线实战案例
```

## 案例 1：STM32H743 + TJA1145 多节点实车脱网（位定时 + BRS 时序）

### 现象

四节点车载子系统（STM32H743 + TJA1145）：

- 实验室 4 节点全功能正常
- 实车频繁脱网（每 30-60s 断 1 个）
- 错误：Stuff Error + CRC 失败集中在 >2 Mbps 段
- 报警：CAN Error Counter 累加 → Bus Off

### 抓包 / 根因

```text
示波器抓 TX/RX：
  - 仲裁段 1 Mbps：位定时正常
  - 数据段 2 Mbps（FD BRS）：位定时偏移
  - 单 bit 偏差 50-80 ns
  - 高速段抖动放大

根因（多节点位定时因晶振容差累积偏差 >10%）：
  - 节点 1 晶振 ±20 ppm
  - 节点 2 晶振 ±20 ppm
  - 节点 3 晶振 ±20 ppm
  - 节点 4 晶振 ±20 ppm
  - 最坏组合：±80 ppm 累积
  - 高速段 2 Mbps 周期 = 500 ns
  - 500 ns × 80 ppm = 0.04 ns/cycle（实际更大）
  - 4 节点累积偏差 → 采样点偏移 → Stuff Error

关键：FDCAN_FRAME_FD_BRS 才是真提速
  - 不开 BRS = 整帧 1 Mbps（不是 FD）
  - 开了 BRS = 仲裁段 1 Mbps + 数据段 5 Mbps
  - 不开 BRS 配 FD 帧头 = 速度退化
```

### 定位

```text
Step 1：示波器抓各节点 TX 位定时
  - 节点 1：TQ = 125 ns（标准）
  - 节点 2：TQ = 125 ns
  - 节点 3：TQ = 124 ns（偏差 -1 ns）
  - 节点 4：TQ = 127 ns（偏差 +2 ns）
  - 累积偏差：3 ns @ 2 Mbps = 6% 误差

Step 2：算采样点
  - 节点 1 采样点：80%
  - 节点 3 采样点：80.4%
  - 节点 4 采样点：79.6%
  - 节点差异 0.8%（< 1% 临界）

Step 3：晶振精度
  - 全部节点用 8 MHz 外部晶振
  - 实测频率：
    - 节点 1：8.0000 MHz
    - 节点 2：7.9999 MHz
    - 节点 3：7.9995 MHz
    - 节点 4：8.0002 MHz
  - ppm 差异：节点 3 = -62.5 ppm
```

### 修复

```text
硬件（必须做）：
  1. 晶振精度统一 ±10 ppm（车载级）
  2. CAN 收发器用 TJA1145（带总线故障诊断）
  3. 节点 / 总线阻抗匹配 120Ω 终端电阻
  4. 屏蔽双绞线（车载 CAN 用 STP）

固件（必须做）：
  1. FDCAN 配置：
     - 仲裁段：1 Mbps / 80% 采样点
     - 数据段：5 Mbps / 80% 采样点
     - BRS = ENABLE
     - TDC = ENABLE（高速段自动补偿）
  2. STM32 HAL 配置示例：
     hfdcan1.Init.NominalPrescaler = 8;   // 64 MHz / 8 = 8 MHz TQ
     hfdcan1.Init.NominalTimeSeg1 = 7;    // 7 TQ
     hfdcan1.Init.NominalTimeSeg2 = 2;    // 2 TQ
     hfdcan1.Init.DataPrescaler = 2;       // 5 Mbps
     hfdcan1.Init.DataTimeSeg1 = 7;
     hfdcan1.Init.DataTimeSeg2 = 2;
     hfdcan1.Init.FrameFormat = FDCAN_FRAME_FD_BRS;
  3. 位定时必须所有节点统一
  4. 启动后做 1000 包压力测试（0 错误）

产线（必须做）：
  1. 100% 老化测试：实车环境 24h
  2. 晶振出厂频率校验
  3. 错误帧监控：CAN Error Counter > 96 报警
  4. 节点温度测试：-40 ~ +85°C 全温区稳定
```

### 复盘

- **位定时名义相同 ≠ 实际相同**——晶振精度是隐藏杀手
- BRS 切换后采样点偏移 = 多节点累积偏差
- 高速段（>2 Mbps）误差放大 5-10 倍
- TDC 自动补偿是 STM32 FDCAN 的关键能力
- 多节点车载 = 必须统一晶振等级（±10 ppm 起步）

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-08-13-candidates.md 候选 1
- STM32H743 Reference Manual §56
- TJA1145 datasheet

---

## 案例 2：TC275 MultiCAN 域控制器（混合高频小包 + 低频大包）

### 现象

英飞凌 TC275 域控制器（4 节点 MultiCAN）：

- 仲裁段 1 Mbps 兼容 CAN 2.0
- 数据段 5 Mbps（CAN FD）
- 混合业务：电机 8B 高频（1ms 周期）+ 日志 64B 低频（100ms 周期）
- 实测：高频小包正常，但日志大包频繁丢

### 抓包 / 根因

```text
MultiCAN 配置 17 种中断源：
  - 接收中断
  - 发送完成中断
  - 错误中断
  - FIFO 满
  - 等等

TXD 必须推挽（不能开漏）：
  - TC275 默认 TXD = 推挽
  - 部分场景错配开漏 → 上升沿慢 → 失帧
  - 实测：开漏 100ns 上升沿 → 5 Mbps 失帧

RXD 工业环境 20kΩ 上拉：
  - 工业环境 EMI 严重
  - RXD 必须上拉 + 去耦
  - 20kΩ 上拉 + 100nF 去耦
  - 默认不上拉 → 浮空 → 噪声引入

混合负载问题：
  - 高频 8B 小包：1ms 周期 → 1000 包/秒
  - 低频 64B 大包：100ms 周期 → 10 包/秒
  - 总带宽 1×8 + 10×64 = 648 字节/秒（不算高）
  - 但混合优先级 / FIFO 错位 → 丢包
```

### 修复

```text
硬件（必须做）：
  1. TXD 推挽（不能开漏）
  2. RXD 20kΩ 上拉 + 100nF 去耦
  3. 总线阻抗匹配 120Ω
  4. 屏蔽双绞线

固件（必须做）：
  1. MultiCAN 中断优先级分层：
     - 高频 8B 小包：优先级 0（最高）
     - 低频 64B 大包：优先级 2
     - 错误处理：优先级 1
  2. FIFO 配置：
     - RX FIFO 0：高频小包
     - RX FIFO 1：低频大包
  3. 错误处理：CAN Error Counter > 96 进 Error Passive
  4. 启动后跑 1 小时压测

调试（TSMaster 工具）：
  - 统计各节点错误帧率
  - 错误率 < 0.01% 合格
  - 监控 MultiCAN 17 个中断源
```

### 复盘

- 混合负载 = 优先级分层是核心
- MultiCAN 17 中断源要按业务分层，不能用默认
- TXD 推挽 / RXD 上拉是工业环境必做
- 域控制器 CAN FD 选型 = TC275 / NXP S32K3 / STM32H7
- 错误率 < 0.01% 是量产基准

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-08-13-candidates.md 候选 2
- 英飞凌 TC275 Reference Manual
- TSMaster 工具文档

---

## 案例 3：TSMaster 采样点偏移致 ECU 中断（产线 checklist）

### 现象

新能源车 ECU 量产 500 台/天：

- ECU 偶发中断（一周内 5-10 次）
- TSMaster 抓包显示错误帧集中在某个 ECU
- 该 ECU 采样点被误设 60%（标准 80%）
- 工业节点间采样点差异 > 15% → 持续错误帧

### 抓包 / 根因

```text
采样点计算公式：
  采样点 = (Sync_Seg + Prop_Seg + Phase_Seg1) / TQ × 100%
  
标准 500 kbps / 16 TQ / 80% 采样点：
  Sync_Seg = 1 TQ
  Prop_Seg = 2 TQ
  Phase_Seg1 = 10 TQ (Phase_Seg2 = 3 TQ)
  采样点 = (1+2+10) / 16 = 81.25%

ECU 误设 60% 采样点：
  Phase_Seg1 = 7 TQ (太短)
  采样点 = (1+2+7) / 16 = 62.5%
  偏差：-20% → 接收端采样点不匹配 → 错误帧

节点间差异 > 15% 是硬伤：
  - 节点 A 采样点 80%
  - 节点 B 采样点 60%
  - 差异 20% → 持续错误帧
```

### 定位

```text
Step 1：TSMaster 抓包
  - 看错误帧分布
  - 集中在某个 ECU 节点
  - 该 ECU 错误率 5%+

Step 2：导出位定时配置
  - 节点 A：80% 采样点（标准）
  - 节点 B：60% 采样点（异常）
  - 差异 20%

Step 3：找配置来源
  - ECU B 用 e2 studio 自动生成代码
  - 工具默认 Phase_Seg1 = 7
  - 没改 = 错配置
```

### 修复

```text
产线（必须做）：
  1. 100% 采样点校验
     - 烧录后自动跑 100 包测试
     - 错误率 > 0.1% 标红拒收
  2. 工具链配置统一
     - 工具默认 Phase_Seg1 = 10
     - 不允许覆盖
  3. 节点间采样点差异 < 1%
     - 多节点项目必须统一配置
     - 校准表烧入

代码（示例）：
  // 500 kbps / 16 TQ / 80% 采样点
  CAN_baudcfg_t baud = {
      .baud_rate = 500000,
      .sample_point = 80,    // 关键
      .sync_jump = 1,
      .prescaler = 8,        // 64 MHz / 8 = 8 MHz TQ
      .seg1 = 12,            // Prop + Phase1
      .seg2 = 3,
      .prop = 2
  };
  
  // 1 Mbps 高速段（CAN FD 数据段）
  CAN_baudcfg_t baud_fd = {
      .baud_rate = 2000000,
      .sample_point = 80,
      .sync_jump = 1,
      .prescaler = 2,
      .seg1 = 12,
      .seg2 = 3
  };
```

### 复盘

- 采样点是 CAN FD 头号坑——**所有节点必须统一**
- 工具链默认配置**经常错**——必须 review
- TSMaster 工具能直接看采样点 → 量产必备
- 节点间差异 > 15% = 协议不能工作
- 2 Mbps 高速段要缩短 Prop 段（缩短 0-1 TQ）

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-08-13-candidates.md 候选 3
- TSMaster 工具文档
- CAN 2.0 / CAN FD ISO 11898-1:2015

---

## 案例 4：RA6M5 客户 CANFD 发送异常（Sample point + Manual 未配）

### 现象

瑞萨 RA6M5 客户量产：

- "CAN 正常，CANFD 异常"
- 收发 CAN 2.0 帧 100% 正常
- 收发 CAN FD 帧 100% 失败
- 错误：Stuff Error

### 抓包 / 根因

```text
e2 studio 工具链默认配置：
  - Sample point = 80%（看似对）
  - Manual = 自动勾选（看似自动）
  - 但实际：
    - Sample point 字段被 disabled
    - Manual 实际是"手动 = 默认值"
    - 实际采样点 = 50%（而非 80%）

e2 studio CANFD 需 40MHz 时钟：
  - RA6M5 默认外设时钟 20 MHz
  - CANFD 需要 40 MHz
  - 不改 → 波特率计算错位

Normal + FD 双配：
  - Normal CAN：1 Mbps / 80% 采样点
  - FD CAN：5 Mbps / 80% 采样点
  - 必须分开配
  - 默认共用 → 错配

Sample point 漏配直接报 Stuff Error：
  - 默认 50% 采样点 + 5 Mbps
  - 边沿抖动 > 50% → Stuff Error
```

### 定位

```text
Step 1：客户 e2 studio 工程对比
  - 工作工程：Sample point = disabled
  - 默认模板：Sample point = enabled + 80%

Step 2：e2 studio 配置差异
  - CAN Module: 选错（CANFD vs CAN）
  - 时钟源：20 MHz（应该 40 MHz）
  - Manual 勾选但实际无作用

Step 3：手算采样点
  - 20 MHz / Prescaler=4 = 5 MHz TQ
  - 5 MHz TQ / 1 Mbps = 5 TQ per bit
  - 默认 Phase_Seg1 = 2, Phase_Seg2 = 2
  - 采样点 = (1+1+2)/5 = 80%（理论）
  - 但实际 = 50%（e2 studio 错算）
```

### 修复

```c
// 瑞世 e2 studio CANFD 正确配置（RA6M5）
// 1. 时钟配置
//    System clock → CANFD clock = 40 MHz
//    → 不是 20 MHz！

// 2. 采样点必须手动配（不能信默认）
#define CANFD_BAUD_RATE_PRESCALER    2
#define CANFD_BAUD_RATE_TSEG1        13   // 关键
#define CANFD_BAUD_RATE_TSEG2        4    // 关键
// 40 MHz / 2 = 20 MHz TQ
// 20 TQ / bit
// 采样点 = (1+1+13) / 20 = 75%（仍偏）
// 正确：TSEG1=15, TSEG2=3
// 采样点 = (1+1+15)/20 = 85%（标准）

// 3. Manual 必须勾选 + 填值
//    不是勾选就行，必须填值
```

### 复盘

- 瑞萨 e2 studio 工具链**默认配置经常错**——必须手动校验
- Sample point + Manual 双配置 = 配错一项就全错
- 时钟源 20 MHz / 40 MHz 必须对齐 CANFD 要求
- Normal + FD 双配 = 容易漏
- 客户工程 review 必须包含位定时全参数

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-08-13-candidates.md 候选 4
- 世强（瑞萨代理）
- RA6M5 User Manual §36

---

## 案例 5：RK3576 + ISO 11898-1:2015 SocketCAN TDC + CRC-17

### 现象

瑞芯微 RK3576 Linux 平台：

- `ip link set can0 up` 报 "Invalid argument"
- 旧 ip 命令 `ip link set can0 up type can bitrate 500000` 不报错
- 但收发包全部失败

### 抓包 / 根因

```text
ISO 11898-1:2015（CAN FD）：
  - 经典 CAN 2.0：CRC 15-bit
  - CAN FD：CRC 17-bit (poly 0x1685B) / CRC 21-bit
  - 旧 ip 命令不识别 CAN FD

错误命令：
  $ ip link set can0 up type can bitrate 500000
  RTNETLINK answers: Invalid argument

正确命令（CANFD 三件套）：
  $ ip link set can0 up type can bitrate 500000 dbitrate 2000000 fd on
                          ^^^^^^^^^^^^^^     ^^^^^^^^^^^^^   ^^^^
                          仲裁段 500k        数据段 2M        FD 标志
  必须同时配：
  1. bitrate（仲裁段）
  2. dbitrate（数据段）
  3. fd on（FD 标志）

TDC 必须 fd on 生效：
  - TDC = Transceiver Delay Compensation
  - 高速段必需
  - 默认 ip 命令不配
  - 需手动：fd on + TDC 自动

BRS 位 bit 96（ISO §12.3.2）：
  - ISO 11898-1:2015 BRS 位在 bit 96
  - 不是 bit 0
  - C 工具链必须按位 bit 96 解析
  - 老 CAN 2.0 库解析错位
```

### 修复

```bash
# 1. 正确 up 命令
$ ip link set can0 up type can bitrate 500000 dbitrate 2000000 fd on
$ ip link show can0
    can0: <NOARP,UP,LOWER_UP> mtu 72
         link/can

# 2. 工具链
$ ip -details link show can0
    can state ERROR-ACTIVE restart-ms 0
          bitrate 500000 sample-point 0.800
          tq 125 prop-seg 2 phase-seg1 13 phase-seg2 2 sjw 1
          dbitrate 2000000 dsample-point 0.800
          dtq 125 dprop-seg 2 dphase-seg1 13 dphase-seg2 2 dsjw 1
          clock 80000000
          re-started bus-errors counter 0
          TDC 6
          fd on
          ...

# 3. C 工具链（SocketCAN + CRC-17）
#include <linux/can.h>
#include <linux/can/raw.h>

struct canfd_frame frame;
frame.can_id = 0x123;
frame.len = 16;  // CAN FD 支持 0-64
frame.flags = CANFD_BRS;  // BRS = bit 96 标志
memcpy(frame.data, payload, 16);
send(sock, &frame, sizeof(frame), 0);
```

### 复盘

- CAN FD 在 Linux 上必须 `fd on` + `dbitrate` + `bitrate` 三件套
- 旧 ip 命令不识别 FD 帧
- TDC 默认开，但需要 `fd on` 才生效
- BRS 在 ISO §12.3.2 = bit 96 字段（C 工具链必须按位解析）
- SocketCAN 库 + CANFD_BRS 标志 = 正确组合

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-08-13-candidates.md 候选 5
- RK3576 Reference Manual §17
- ISO 11898-1:2015

---

## 案例汇总

| # | 现象 | 根因 | 难度 |
| --- | --- | --- | --- |
| 1 | STM32H743 实车脱网 | 位定时累积偏差 + BRS 时序 | 高 |
| 2 | TC275 大包丢 | MultiCAN 优先级 + 推挽/上拉 | 中 |
| 3 | ECU 偶发中断 | 采样点偏移 60%（应为 80%）| 中 |
| 4 | RA6M5 CANFD 失败 | 工具链默认错 + Manual 漏配 | 中 |
| 5 | RK3576 ip 失败 | fd on + dbitrate 漏配 | 低 |

---

## 关联文档

- `can.md`：CAN 总览
- `can-canopen-deep-dive.md`：位时序 + 采样点 + CAN FD 协议层
- `can-canopen-practical.md`：调试实践
- `iso-tp-deep-dive.md`：CAN 多帧传输
- `uds-practical.md`：UDS 诊断（基于 CAN）
