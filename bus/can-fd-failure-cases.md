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

## 案例 6：台架通 ≠ 装车通——TDC Stuff Error 200 节点装车后整网报错

### 现象

某主机厂 CAN FD 总线：

- 台架单测：4 节点全部 PASS
- 装车（200 节点，线束长度增加）：**整网狂报错**
- 拔节点：报错消失
- 错码：Stuff Error，集中在 bit 24 / bit 28
- 抓包：TX-RX 环路延迟变化

### 抓包 / 根因

```text
示波器抓 TX → RX 环路延迟：
  台架（线束 30cm）：环路延迟 = 80ns
  装车（线束 30m + 分支）：环路延迟 = 280ns
  
问题：TDC（Transceiver Delay Compensation）默认按台架校准
  - 装车后线束/分支长度改变环路延迟
  - SSP（Secondary Sample Point）错位
  - 数据段采样点错位 → 周期性 Stuff Error

关键约束（ISO 11898-1:2015）：
  - 采样点 75% - 82% 是硬性范围
  - TDCO = (PROP + TSEG1) × DBRP
  - 2 Mbps / 80% 采样点 = TDCO ≈ 400ns
  - 实际：装车后 TDCO 280ns
  - 偏差：120ns > SSP 容忍窗
```

### 定位

```text
Step 1：示波器量 TDCO
  - TX 边沿触发 → RX 边沿光标
  - 多节点测 100 个包取平均
  - 装车 TDCO = 280ns（台架 80ns）
  
Step 2：算 SSP
  - SSP = TDCO + 80% × bit_time
  - 80% × 500ns = 400ns
  - SSP = 280 + 400 = 680ns
  - 但默认 SSP = 400ns（台架校准）
  - 偏差 280ns = 整网错位

Step 3：尝试验证
  - 改 TDCO = 280ns（装车值）
  - 测试：100 包 PER
  - 失败 0%
  - ✅ 修复
```

### 修复

```c
// 装车校准 TDCO 流程
void calibrate_tdco_after_install(void) {
    uint32_t loop_delay_ns = measure_loop_delay();  // 示波器测
    uint32_t bit_time_ns = 500;  // 2 Mbps
    uint32_t sample_pct = 80;
    
    uint32_t tdco = loop_delay_ns;
    uint32_t ssp = tdco + (sample_pct * bit_time_ns / 100);
    
    // 写 TDCO 寄存器
    CAN_FDCAN_TDCV(ssp);
    CAN_FDCAN_TDCO(tdco);
    CAN_FDCAN_TDCEN(1);  // enable TDC
}
```

### 4 陷阱

```text
1. 单测思维：台架通 ≠ 装车通
   - 必须装车后重新校准
   - 不能用台架 TDCO 装车
   
2. 忽略 Loop Delay
   - 测的是 TX → RX 时间
   - 不是看 chip spec 兜底
   - 必须实测

3. TDCO 拍脑袋
   - 不能填经验值（如 150ns）
   - 必须示波器实测

4. SSP 落下一位
   - 采样点位置不对
   - SSP = TDCO + 采样点% × bit_time
   - 整网算 SSP，**不是单节点**
```

### 复盘

- **台架通 ≠ 装车通** = CAN FD 装车第一坑
- TDC 在台架校准 = 装车失效
- 线束/分支长度改变环路延迟 = 必须重测 TDCO
- ISO 11898-1:2015 采样点 75-82% 是硬性范围
- 4 陷阱 = 4 步装车前 checklist

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-08-26-candidates.md 候选 1
- 电子工程专辑 窦明佳
- 汽车电子 10+ 年工程师实战

---

## 案例 7：NXP S32K CAN-FD TDC SSP Bit Stuff Error 诊断实战

### 现象

NXP S32K3 + TJA1145 车载 ECU：

- 主采样点 80%
- 2 Mbps 数据段
- 实测：Stuff Error 100% 触发
- 错码集中在 SSP（Secondary Sample Point）

### 抓包 / 根因

```text
示波器量 TX → RX 延迟：
  实际：150ns
  2 Mbps 占位宽：30% × 500ns = 150ns
  偏移：50ns（占位宽 33%）

主采样点 80% 错位分析：
  - 默认 SSP = 80% × 500ns = 400ns
  - 实际 SSP = 400ns + 150ns（环路延迟）= 550ns
  - 但 TJA1145 实际输出位置 = 550ns
  - 接收端采样点仍是 400ns
  - 偏差 150ns > SSP 容忍窗
  - → 周期性 Stuff Error

关键：SSP 必须 = TDCO + 期望采样点 × bit_time
  - TDCO（环路延迟）= 150ns
  - 期望 SSP = 80% × 500ns = 400ns
  - 实际写入 SSP = 150 + 400 = 550ns
  - 但 NXP S32K TDCO 寄存器单位 = tq（time quantum）
  - 1 tq = 系统时钟周期（如 25ns）
  - 150ns = 6 tq
  - 但 TDCV 测量显示 = 25 tq（测量时含 TJA1145 收发器延迟）
```

### 定位

```text
Step 1：TDCV 测量
  - NXP S32K 提供 TDCV（Transceiver Delay Compensation Value）
  - 测量时 TJA1145 收发器延迟 100ns
  - TDCV = 100ns + 50ns（线束）= 150ns
  
Step 2：算 TDCO
  - TDCO = TDCV - 期望 SSP offset
  - 期望 SSP = 80% × 500ns = 400ns
  - 1 tq = 25ns
  - TDCO = (400 - 150) / 25 = 10 tq
  - 实际：调试发现 25 tq 才稳定
  
Step 3：手动设
  - TDCEN = 1
  - TDCO = 25（不是 10）
  - 测试：1000 包 PER = 0
```

### 修复

```c
// NXP S32K TDC 配置
void canfd_tdc_config(void) {
    CAN_FDCAN_TDC_Type tdc = {0};
    
    tdc.TDCEN = 1;  // enable TDC
    tdc.TDCO = 25;  // 实测值（不是算的）
    tdc.TDCV = 0;   // 自动测量
    
    // 启用 TDC 必须 fd on
    if (!canfd_fd_on) {
        while(1);  // 必须先 enable FD
    }
    
    CAN_FDCAN_SetTDC(can_fd, &tdc);
    
    // 验证
    uint32_t err_count = 0;
    for (int i = 0; i < 1000; i++) {
        if (CAN_FDCAN_GetError() != 0) err_count++;
    }
    return err_count;  // 期望 0
}
```

### 4 陷阱（重点）

```text
1. 单测思维
   - 用台架数据装车
   - 必须装车后校准

2. 忽略 Loop Delay
   - 收发器延迟 + 线束延迟
   - 不能省略

3. TDCO 拍脑袋
   - 算的值（10）≠ 实测值（25）
   - 必须示波器实测

4. SSP 落下一位
   - 偏差容忍只有 ±0.1 tq
   - 错一位就报错
```

### 复盘

- NXP S32K + TJA1145 组合 TDC 是硬性
- **TDCO 必须实测，不是算**（10 vs 25）
- 1000 包 PER = 0 是验证标准
- 4 陷阱 = 4 步装车前 checklist
- 调试经验：算 10 不对，试 15 / 20 / 25 才稳定

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-08-26-candidates.md 候选 2
- CSDN 汽车电子 10+ 年工程师
- NXP S32K Reference Manual

---

## 案例 8：Daimler Buses 铰接巴士 CAN XL 14.5Mbps 真实车装（99% bus load 仍稳定）

### 现象

2022 年夏，Daimler + Bosch + NXP + R&S + Vector 联合演示：

- 真实载客场景：铰接巴士（60+ 米拓扑）
- CAN FD 全面升级为 CAN XL
- 演示关键数据：
  - 仲裁段 500 kbps（兼容 CAN 2.0 / CAN FD）
  - 数据段 14.5 Mbps（CAN XL）
  - 60+ 米总线长度
  - **总线负载 99% 仍稳定通信**

### 关键参数

```text
CAN XL vs CAN FD：
  - CAN FD：仲裁 1 Mbps / 数据 5 Mbps / 64B 帧
  - CAN XL：仲裁 500 kbps / 数据 14.5 Mbps / 2048B 帧
  
兼容矩阵：
  - CAN XL 节点 ↔ CAN XL 节点：14.5 Mbps（最优）
  - CAN XL 节点 ↔ CAN FD 节点：桥接 1:1 映射 DLC
  - CAN XL 节点 ↔ CAN 2.0 节点：8B 帧 fallback

拓扑：
  - 60+ 米（铰接巴士两段连接）
  - 经典 CAN FD 物理层（差分线 120Ω 终端）
  - 不需要重新布线
```

### 桥接设计

```c
// CAN FD <-> CAN XL 桥接（Node 服务）
typedef struct {
    uint8_t fd_to_xl[8][8];    // 8B CAN FD 帧 → 8B CAN XL 帧
    uint8_t xl_to_fd[8][8];    // 8B CAN XL 帧 → 8B CAN FD 帧
} can_bridge_t;

void can_bridge_fd_to_xl(can_frame_t *fd, can_xl_frame_t *xl) {
    // DLC 1:1 映射
    xl->dlc = fd->dlc;
    xl->id = fd->id;  // ID 兼容
    memcpy(xl->data, fd->data, fd->len);
    xl->crc = can_xl_crc_compute(xl);
}

void can_bridge_xl_to_fd(can_xl_frame_t *xl, can_frame_t *fd) {
    if (xl->len > 8) {
        // CAN FD 8B 限制，超长帧丢弃
        return;
    }
    fd->dlc = xl->dlc;
    fd->id = xl->id;
    memcpy(fd->data, xl->data, xl->len);
}
```

### 实战数据

```text
Daimler 演示数据（2022 夏）：
  - 总线负载：99%
  - 通信稳定性：< 1 错误/小时
  - 拓扑长度：60+ 米
  - 节点数：30+ ECU
  
关键发现：
  - 99% bus load 仍能通信
  - 数据段延迟 < 1ms
  - 桥接透明（CAN FD 节点无感）
  
对比 CAN FD：
  - CAN FD @ 5 Mbps / 60 米 / 99% load = 大量错误
  - CAN XL @ 14.5 Mbps / 60 米 / 99% load = 稳定
  - 提升 3-5x 容量
```

### 商用里程碑

```text
时间线：
  - 2018：CAN XL 概念发布
  - 2020：NXP / Bosch / Vector 出原型
  - 2022：Daimler 巴士真实演示（首次车装）
  - 2024：Bosch / Continental 出商用 ECU
  - 2026：开始大规模量产

中国市场：
  - 2025：国内主机厂开始测试
  - 2026：长城 / 比亚迪部分车型小规模
  - 2027+：预计大规模
```

### 复盘

- **CAN XL 是 CAN FD 的 3-5x 容量升级**——保持物理层兼容
- **Daimler 巴士是 CAN XL 首个真实车装**——里程碑
- 桥接 DLC 1:1 映射 = 兼容老节点
- 99% bus load 仍稳定 = 容量远高于实际需要
- 国内厂商 2026-2027 量产 = 替代时间窗口

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-08-26-candidates.md 候选 4
- CiA + Daimler Truck 联合报道
- Bosch 商用 ECU 文档

---

## 案例 9：CAN FD 长距离 50m 非屏蔽线采样点 70%→90% 调参实战

### 现象

重卡 BMS 项目，40m / 50m 非屏蔽双绞线：

- 40m @ 1Mbps：误码率 10⁻³，频繁 Bus-Off
- 50m @ 2Mbps：采样点 70%→85% 误码率 10⁻⁵→10⁻⁷
- 调 90% 采样点：反而恶化
- 终端电阻折腾 2 周

### 抓包 / 根因

```text
40m / 8 Mbps 极限：
  - 位时间 = 125ns
  - 50m 延迟 = 400ns
  - 400ns >> 125ns = 多 bit 反射叠加
  - 信号失真严重
  - 必须降速

50m / 2 Mbps 误码 10⁻⁵→10⁻⁷（70%→85% 采样点）：
  - 70% 采样点：太早采样
  - 85% 采样点：临界（已能用但有噪声）
  - 90% 采样点：太晚，错过 bit
  - 反射波叠加导致最佳点不固定
  - 必须用屏蔽双绞线
```

### 实战参数

```text
长距离 CAN FD 速查：

| 线缆 | 速率 | 推荐采样点 | 备注 |
| --- | --- | --- | --- |
| 10m | 5 Mbps | 75-80% | 屏蔽双绞线 |
| 20m | 2 Mbps | 75-80% | 屏蔽双绞线 |
| 40m | 1 Mbps | 80% | 屏蔽双绞线 |
| 50m | 500 kbps | 80% | 屏蔽双绞线 |
| 50m+ | 250 kbps | 80% | 必须 CAN XL |

非屏蔽双绞线：
  - 距离 < 20m
  - 速率 < 1 Mbps
  - 否则误码爆
```

### 关键工程认知

```text
1. 位时间 vs 距离
   - 125ns 位时间 @ 8 Mbps
   - 50m 延迟 400ns = 3.2 bit
   - 不能跑 8 Mbps

2. 采样点 vs 反射波
   - 长线缆反射波叠加
   - 70% 太早
   - 85% 临界
   - 90% 太晚
   - 没有固定最佳点

3. 屏蔽双绞线 = 关键
   - 50m 不用屏蔽 = 误码爆
   - 用屏蔽 = 1-2 个数量级改善
```

### 修复

```text
1. 降速
   - 50m 非屏蔽：2 Mbps → 1 Mbps
   - 50m 屏蔽：1 Mbps → 2 Mbps

2. 用屏蔽双绞线
   - 替代非屏蔽
   - 改善 1-2 数量级

3. 换 CAN XL
   - 距离 > 50m 必选 CAN XL
   - 工业实践

4. 终端电阻调试
   - 100Ω ± 5%
   - 测 60-70Ω
   - 2 周排查
```

### 4 实战点

```text
① 40m / 8Mbps 位时间 125ns vs 50m 延迟 400ns
② 采样点 vs 反射波
③ CAN XL 对线缆更严（更高频率）
④ 终端电阻 2 周折腾
```

### 复盘

- **长距离 = 降速 + 屏蔽双绞线 + 采样点实验**
- 50m 非屏蔽 @ 2Mbps = 误码 10⁻⁵→10⁻⁷
- 50m 屏蔽 @ 1Mbps = 可用
- 50m+ 必须 CAN XL
- 采样点 70-90% 没有固定最佳 = 反射波叠加

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-09-02-candidates.md 候选 1
- CSDN 重卡 BMS 实战

---

## 案例 10：CAN 调试实战干货指南——4 层定位（80% 物理层 + STM32 源码）

### 现象

某量产 CAN 节点，1000+ 设备出货后故障率 5%：

- 故障现象：偶发丢帧 / 节点失联 / Bus-Off
- 看 log 找不到规律
- 调试 1 周无果

### 抓包 / 4 层定位（80/15/4/1 比例）

```text
4 层定位（80% / 15% / 4% / 1%）：

1. 物理层（80%）
   - 终端电阻：万用表量 55-65Ω
   - 屏蔽 / 接地
   - 线缆长度 / 反射
   - 收发器 VCC 稳定性

2. 链路层（15%）
   - 波特率一致
   - 采样点一致
   - BRS（FD）
   - CAN FD 与 CAN 2.0 混用

3. 协议层（4%）
   - TEC / REC
   - 三态：96 / 128 / 256
   - 自愈逻辑

4. 业务层（1%）
   - 应用层
   - 业务数据错误
```

### TEC/REC 三态详解

```text
TEC = Transmit Error Counter
REC = Receive Error Counter

状态机：
  Error Active：
    - TEC < 128 且 REC < 128
    - 主动错误帧（6 bit dominant）
    - 正常状态

  Error Passive：
    - 128 ≤ TEC < 256 或 128 ≤ REC < 256
    - 被动错误帧（6 bit recessive）
    - 限制发送（仅 7 bit recessive 之后）
    - 接近故障

  Bus Off：
    - TEC ≥ 256
    - 节点脱离总线
    - 自愈逻辑启动
    - Reset → Wait 2.8ms × 128 → Recovery
```

### Reset + Stop + Start 自愈

```text
// STM32 CAN 错误处理
void CAN_Error_Process(void) {
    if (hcan1.ErrorCode & HAL_CAN_ERROR_BOF) {
        // Bus Off
        HAL_CAN_Stop(&hcan1);
        HAL_Delay(10);  // 等待 2.8ms × 128
        HAL_CAN_Start(&hcan1);
    }
    
    if (hcan1.ErrorCode & HAL_CAN_ERROR_EPV) {
        // Error Passive
        log_warning("Error Passive state");
    }
    
    if (hcan1.ErrorCode & HAL_CAN_ERROR_CRC) {
        // CRC 错误
        log_warning("CRC error");
    }
}
```

### CANoe 三套参数

```text
1. Bit Timing Detection
   - 节点波特率
   - 节点采样点（隐藏不一致）
   - 例：所有节点标 1 Mbps，但实际 75% vs 90% 采样点

2. Stress Test
   - 高负载 100% 测试
   - 错误注入

3. Network Analysis
   - 拓扑图
   - 节点响应时间
   - 错误分布
```

### CAN FD 与 CAN 2.0 混用降级

```text
混用场景：
  - 旧节点 CAN 2.0
  - 新节点 CAN FD（BRS）
  - 仲裁段兼容
  - 数据段降级到 CAN 2.0

降级后果：
  - 实际带宽 = CAN 2.0 带宽
  - 浪费 FD 性能
  - 必须强制配置
```

### 修复

```text
1. 80% 物理层排查
   - 万用表量终端电阻
   - 示波器看波形
   - 查屏蔽 / 接地

2. 15% 链路层
   - CANoe Bit Timing Detection
   - 强制统一采样点
   - 强制 FD 启用

3. 4% 协议层
   - TEC/REC 监控
   - 自愈逻辑

4. 1% 业务层
   - 应用层 CRC
   - 业务数据校验
```

### 复盘

- **80/15/4/1 = CAN 故障分布**——物理层 80%
- 物理层：万用表 + 示波器 = 唯一手段
- 协议层：TEC/REC 三态 + 自愈
- CANoe Bit Timing Detection = 隐藏不一致杀手
- STM32 HAL CAN Error Code = 标准 API

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-09-02-candidates.md 候选 2
- 尧图网络 量产工程师
- STM32F4 Reference Manual §43.7
- Bosch CAN Specification 2.0

---

## 案例 11：TEC 256 Bus-Off + VCC 1.5V 跌落——CAN 状态机 + 电源完整性配对

### 现象

某车载网关装车后：

- 每 2-3h 某 ECU 间歇失联
- ECU 发全 0x00 后 TEC 飙 256
- 进入 Bus-Off
- 软件 / 拓扑均正常
- 排查 1 个月无果

### 抓包 / 根因

```text
1. 短时监测（看 1h）
   - 看不出来
   - 故障偶发

2. 长时监测（看 24h+）
   - 抓到规律：每 2-3h
   - 与空调吸合时序一致
   - 空调吸合 → 电源瞬态变化

3. 示波器量 SN65HVD230 VCC
   - 空调吸合时：VCC 跌落数十 ms × 1.5V
   - 标称 5V → 跌到 3.5V
   - 收发器 VCC 不稳 → 发送失败
   - TEC 累加 → 256 → Bus-Off

4. 软件 + 拓扑都正确
   - 不是协议问题
   - 不是布线问题
   - 是电源完整性问题
```

### 修复

```text
1. VCC 加 100µF 低 ESR 钽电容
   - 紧挨 VCC 引脚
   - 短走线 < 5mm
   - 吸收瞬态

2. 优化电源走线
   - 加宽走线
   - 减小电感
   - 多路去耦

3. 收发器选型
   - 改用宽 VCC 范围收发器
   - 4.5V - 5.5V 容差
   - 抗瞬态

4. 协议层自愈
   - Bus-Off 自动 Recovery
   - 2.8ms × 128 后重试
   - 上报业务层
```

### TEC/REC 监控

```c
// 长时监测代码
void can_error_monitor(void) {
    static uint32_t last_tec = 0, last_rec = 0;
    
    uint32_t tec = CAN->TSR >> 16 & 0xFF;  // 读 TEC
    uint32_t rec = CAN->ESR >> 16 & 0xFF;  // 读 REC
    
    if (tec != last_tec) {
        log_info("TEC: %d -> %d", last_tec, tec);
        last_tec = tec;
    }
    
    if (rec != last_rec) {
        log_info("REC: %d -> %d", last_rec, rec);
        last_rec = rec;
    }
    
    // REC 缓升 = 接收 EMC（外部干扰）
    if (rec > 64 && rec < 128) {
        log_warning("REC climbing: %d (EMC?)", rec);
    }
    
    // TEC 急升 = 发送硬件（自身问题）
    if (tec > 64) {
        log_error("TEC rising: %d (check TX)", tec);
    }
}
```

### 关键工程认知

```text
1. REC 缓升 = 接收 EMC（外部干扰）
2. TEC 急升 = 发送硬件（自身问题）
3. Bus Off 冷静期 = 2.8ms × 128 = 358ms
4. VCC 跌落 1.5V × 数十 ms = 收发器失效
5. 长时监测 = 必做（短时看不出来）
```

### 修复代码

```c
// VCC 跌落检测 + 自愈
void vcc_brownout_handler(void) {
    uint32_t vcc_mv = adc_read_vcc_mv();  // ADC 读 VCC
    
    if (vcc_mv < 4500) {  // 4.5V 阈值
        log_warning("VCC low: %d mV", vcc_mv);
        // 关闭 CAN 收发器
        CAN_DeInit();
        // 等待 VCC 恢复
        while (adc_read_vcc_mv() < 4500) {
            HAL_Delay(10);
        }
        log_info("VCC recovered: %d mV", adc_read_vcc_mv());
        // 重新初始化
        CAN_Init();
    }
}
```

### 复盘

- **TEC/REC 反映故障根因**：REC 缓升 = EMC / TEC 急升 = TX
- VCC 跌落 = 收发器失效 = TEC 急升
- 100µF 低 ESR 钽电容 = 电源完整性标配
- 长时监测 = 抓瞬态故障唯一手段
- 2.8ms × 128 = Bus-Off 冷静期

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-09-02-candidates.md 候选 4
- CSDN 车载网关
- SN65HVD230 datasheet §7.3

---

## 案例 12：400ns 边沿率 = $15K 幻影 ECU 保修（OBD-II 介电常数漂移）

### 现象

Stuttgart 实验室，欧洲 Tier 1 telematics 项目，6 周内累计收 63 件幻影保修件（客户反映"ECU 无响应"），累计成本 $15,000+：
- 客户车发回件，实验室检测**完全正常**（"no fault found"）
- 客户车替换 ECU 后，**新 ECU 装上又"挂"**
- 工程师现场复现不出，反复拉锯 8 天

### 抓包 + 根因

#### 根因 1：OBD-II 至 Molex 12-pin 诊断线束 65℃ 介电常数漂移

线束 3m 长，绝缘层材料 PP（polypropylene）：
- 25℃ 时介电常数 εr ≈ 2.2
- 65℃ 引擎舱环境 εr 漂移到 2.45
- 单位长度寄生电容从 11pF/m 涨到 12.3pF/m
- 3m 总寄生电容 = 36.9pF（超过收发器 spec 25pF 上限）

#### 根因 2：CAN FD 5Mbps 边沿率 400ns 超规格

ISO 11898-2:2024 §5.4 规定：
- 2 Mbps：边沿率 max 50 ns
- 5 Mbps：边沿率 max **15 ns**
- 实际实测 3m + 36.9pF 负载下边沿率 400ns（**超 spec 26 倍**）

#### 根因 3：200ns bit time 被 400ns 边沿吃掉

5Mbps 周期 = 200ns：
- 边沿 400ns + 稳定时间 100ns = 500ns > 1 个 bit
- 采样点（70% 位置 = 140ns）落在不确定区
- 收发器内部 comparator 还在 settling → bit 误判率 30%
- 误判累积 → CRC error → ECU 不应答 → 客户视角"ECU 无响应"

### 定位（4 步法）

```text
Step 1：故障件复核（"no fault found" 也要查）
  - 用 lab 测试设备单独测 ECU：完全正常
  - 排除 ECU 本身问题

Step 2：现场复现
  - 装回客户原车（原车完整线束）
  - 实测线缆端到端 CAN FD 5Mbps 通信：30% CRC error
  - lab 短缆（<30cm）正常

Step 3：物理层测量
  - 网络分析仪测线缆 S21（3m + Molex）
  - 看 -3dB 带宽：< 2 MHz（spec 应 > 25 MHz）
  - LCR 表测电容：37pF（超 spec）

Step 4：温度漂移
  - 加热舱 25℃→65℃→85℃
  - 抓 CAN FD error rate 变化
  - 65℃ 之后 error rate 30%→50%
  - 锁因 = 温度敏感介电常数
```

### 修复

| 手段 | 实施 | 成本 |
| --- | --- | --- |
| 短线缆 | OBD-II 转接线 3m→0.5m | $0.5/件 |
| 高规格线 | FPE/PTFE 介电常数温漂 < 5% | $2.5/件 |
| 降速 | 5Mbps → 2Mbps | $0 |
| 缓冲器 | 加中继器隔离线缆 | $8/件 |

### 复盘

- **$15K 幻影保修根因 = 3m 长 OBD-II 诊断线束的物理层失效**——8 天定位
- 温度敏感介电常数漂移在产线测试时**不显形**（25℃ vs 65℃）
- 200ns bit time 被 400ns 边沿吃掉 = 经典**带宽 × 距离 trade-off**
- 产线测试**未覆盖「满容性负载 + 真实收发器」**——必须用 HIL（hardware-in-loop）+ 温度舱
- 收 63 件 + 工程 8 天 = 单 case 实际 cost $250+——5 个 case 即 $1.25K

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-09-11-candidates.md 候选 1
- obd-cable.com（OBD 线缆工厂）
- ISO 11898-2:2024 §5.4

---

## 案例 13：工业现场总线 4 大 killer——lab 能用到产线就崩

### 现象

工业自动化（机器人 / CNC / 注塑机）项目，**lab 调试完美，产线装机就崩**。典型表现：
- 单台 ECU 单独测：通信正常
- 接入整网（5-30 节点）：error frame 飙到 5%-30%
- 长时间运行（>4 小时）：偶发 Bus-Off 整段断网
- 电机/VFD 启停瞬间：100% 通信失败 0.5-2s

### 抓包 + 根因（4 大 killer）

#### Killer 1：地电位差（GND 偏移 1-10V 推出共模）

工业现场**多点接地**是常态（电机外壳、PLC 柜、控制台各自接大地）：
- 大地本身在工厂里**不是等电位**——电机驱动柜 GND vs 控制台 GND 差 1-10V
- CAN 收发器共模输入范围 = **-2V ~ +7V**（ISO 11898-2 §6.2）
- 多点接地把 5V 共模电压直接打到收发器上 → 内部 comparator 饱和
- 表现：lab 短距离 OK，工业 30m 整网就出错

#### Killer 2：stub 长度违反（1Mbps 限 30cm）

工程师图省事**从主干拉短线到节点**：
- 1Mbps 时 stub ≤ 1m（ISO 11898-2 §5.3 严格版）
- 5Mbps 时 stub ≤ **30cm**（每加 10cm 反射增加 5%）
- 实际项目 stub 普遍 50-200cm → 信号反射叠加 → 采样点偏移

#### Killer 3：终端电阻错（>2/缺一/错位 → 100% 反射）

CAN 总线要求**两端各 120Ω**终端电阻：
- 多加 1 个终端（3 个 120Ω 并联 = 40Ω）：信号衰减 3 倍，distance 减半
- 少 1 个：信号在末端全反射，振铃 50% 振幅
- 错位（终端放中间）：总线一端无终端，反射叠加
- 现场 50% 项目**至少 1 个错**

#### Killer 4：屏蔽层断路成天线

工业现场强电磁干扰（VFD 谐波 100kHz-30MHz，电机电刷放电）：
- 屏蔽层单端接地（错）or 多点接地错位 → 屏蔽层电流不平衡 → 50Hz/工频干扰窜入
- 屏蔽层断路（中间 connector 接触不良）→ 整段屏蔽失效 → 变成接收天线
- 表现：VFD 启停瞬间整网 error frame 爆炸

### 定位（4 步法）

```text
Step 1：地电位差测试
  - 万用表 mV 档测任意两节点 GND 之间电压
  - 期望 < 50mV
  - 实际 > 1V → killer 1 命中

Step 2：stub 长度测量
  - 物理量主干到每个节点的支线长度
  - 查表：1Mbps < 1m / 5Mbps < 30cm
  - 超长 → killer 2 命中

Step 3：终端电阻测量
  - 万用表 Ω 档测 CAN_H - CAN_L 电阻
  - 总线无电时：60Ω（两个 120Ω 并联）= 正确
  - 40Ω = 多 1 终端，120Ω = 缺 1 终端 → killer 3 命中

Step 4：屏蔽层检查
  - 屏蔽层单端/双端接地状态
  - 屏蔽层连续性（无断点）
  - 错 → killer 4 命中
```

### 修复

| Killer | 修复 | 器件选型 |
| --- | --- | --- |
| 1 地电位差 | 每节点**隔离收发器** + 独立 DC/DC 供电 | ISO1050（TI）/ ADM3053（ADI）/ TJA1052i（NXP） |
| 2 stub | 严格按速率算 stub 上限（commissioning 实测） | 重新布主干 + 短 stub |
| 3 终端 | 标准化 commissioning checklist | 拔/插 120Ω 重新测 |
| 4 屏蔽 | 屏蔽层**双端接地**（通过 100nF Y 电容） | 重做 connector 压接 |

### 复盘

- **lab 通 ≠ 产线通** = 工业 CAN bus 头号陷阱，4 大 killer 全是物理层
- 地电位差 vs 电机/VFD 注入电流是最被忽视的——**隔离收发器是工业项目标配**
- 星形拓扑**隐性违标**（每个节点都是 stub）——必须用 hub/repeater 隔离
- commissioning checklist 比设计更关键——现场 4 项检查每项 5 分钟

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-09-11-candidates.md 候选 2
- Eurth Tech（工业现场总线供应商）
- ISO 11898-2:2016 §5.3 / §6.2

---

## 案例 14：Ford 438 万辆 ITRM 召回——CAN race 跨层调试教训

### 现象

2026-02-20 Ford 向 NHTSA 提交召回 **26V104000**：
- 涉及 4,380,609 辆车（F-150 / F-250 / Expedition / Maverick / E-Transit，MY 2021-2027）
- 根因：**ITRM（Integrated Trailer Relay Module）与 CAN Standby Control bit (STBCC) 启动时 race**
- 表现：trailer brake controller 失效（**刹车信号不发**）—— 安全相关
- 预计 1% 显形率 = **43,000+ 辆**

### 抓包 + 根因

#### 根因 1：STBCC race 9,999 vs 10,000 次启动

- Ford 内部 lab 测试 9,999 次启动 0 显形
- 第 10,000 次启动**温漂 + 中断时序叠加**触发
- **non-deterministic race**——单次发生概率 < 0.01%，但**绝对数量大**（438 万 × 启动频率）
- 10K 测试是 OEM 标准**置信度上限**——传统 HIL 测不出来

#### 根因 2：OEM / supplier 黑盒 + cross-layer observability 鸿沟

- ITRM 由 supplier A 提供，gateway ECU 由 supplier B 提供
- 两边对 STBCC bit 时序有**不同假设**（supplier A：启动时立刻 ready；supplier B：启动后 5ms 内 ready）
- 5ms 窗口外**有概率撞上**（温漂 / 中断时序抖动）
- 黑盒 = 跨厂商 cross-layer observability 几乎不可能

#### 根因 3：软件召回年比 3.3M → 13.4M 翻 4 倍

- NHTSA 2024 年统计：3.3M 辆因软件召回
- 2025 年 13.4M 辆（**4 倍增长**）
- 2026 年 Ford 438 万辆单次 = 2024 年全行业 1.3 倍
- 趋势：汽车软件**复杂度爆炸** >> 测试覆盖能力

### 定位（4 步法）

```text
Step 1：field 数据收集
  - 客户报修 → OTA 拉 log（带时间戳的 CAN 总线记录）
  - 数百例样本聚类：trailer brake 信号丢失前后 5s 的 CAN 帧

Step 2：lab 复现
  - HIL（hardware-in-loop）+ 温箱 -40℃ ~ 85℃
  - 1000 次启动 + 温变 → 0 显形
  - 10000 次启动 + 温变 → 0.1% 显形（命中根因 1）

Step 3：cross-layer trace
  - ITRM 内部 trace + gateway 内部 trace + 总线 trace
  - 三方时间戳对齐（误差 < 100µs）
  - 暴露：STBCC bit 翻转时间 supplier A 早 2ms，supplier B 5ms 才轮询

Step 4：fix 实施
  - supplier B 加 10ms 启动延迟（保守）
  - 5 月起 OTA 推送，所有受影响车次更新
```

### 修复

| 手段 | 实施 | 验证 |
| --- | --- | --- |
| 软件修 | supplier B gateway 加 10ms STBCC 等待 | HIL 10K 次启动 0 显形 |
| OTA 推送 | 5 月起 4.38M 辆分批推 | 推送率 95%+ |
| 备援方案 | 硬件加 timer 监督 supplier A ready | 即使软件失效不显形 |
| 测试升级 | HIL + 10K 次启动 + 温变强制入标准 | 未来 supplier 合同加条款 |

### 复盘

- **9,999 vs 10,000** = non-deterministic 量产最难抓的根因——传统 HIL 测不出来
- **OEM/supplier 黑盒 + cross-layer observability 鸿沟**——跨厂商合作是结构性 root cause
- 1% 显形率 = 43,000+ 辆 = 安全相关 = 必须召回 = $X 亿美元成本
- 软件召回年翻 4 倍 = **未来汽车 ECU 设计的核心挑战**
- **跨层调试** = 应用层（brake signal）+ 协议层（CAN STBCC）+ 物理层（CAN bus 干扰）三方时间戳对齐

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-09-11-candidates.md 候选 3
- NHTSA 26V104000（2026-02-20）
- logcat.ai（Android Automotive 调试博客，2026-03）

---

## 案例 15：SN65HVD234 量产 4% 失效率——RS pin 隐性 silent mode

### 现象

高压击穿检测仪项目（手持 40kV + 基站），4 芯螺旋线连 2 块 MCU + 1 个 sensor：
- 4% 出货良率**崩**（目标 0.5%）
- T24CAN TVS 完好无 PCB 缺陷
- 失效模式 3 种：
  - R pin 卡高（**35% 失效**）
  - 偶有 MCU D pin 损坏（**45% 失效**）
  - 多颗 IC 烧穿（**20% 失效**）
- 2 供应商 + 2 MCU 复现 100% 触发 → 排除单器件问题

### 抓包 + 根因

#### 根因 1：SN65HVD234 RS pin 隐性 silent mode（**主因，40%**）

SN65HVD234 的 RS（slope control / silent mode）pin 行为：
- RS = LOW：正常模式（高速）
- RS = HIGH（> 0.75 × VCC）：**silent mode**——内部 driver 关闭，**只收不发**
- 隐性 = datasheet 没明显标"接错就 silent"——只在 §7.3 electrical char 一笔带过

项目 MCU 启动时序：GPIO 默认 HIGH（很多 MCU 启动默认 high-Z + pull-up）→ RS 被拉高 → silent mode → "CAN 无应答"

#### 根因 2：40kV 瞬态耦合到 RS pin

手持 40kV 探头在 sensor 端产生**电弧**：
- 4 芯螺旋线**长 1.5m + 未屏蔽**（成本考虑）
- 40kV 瞬态通过分布电容耦合到 RS pin（电容分压）
- 1.5m 线缆耦合电容 ~ 5pF，40kV 瞬态 → RS pin 瞬态 50-100V
- 即使 RS pin 有 1kΩ pull-down，瞬态电压足够把 RS 拉到 silent 阈值以上

#### 根因 3：layout 缺陷——RS 走线紧邻 40kV 走线

PCB 布局 RS pin 走线**离 40kV 高压走线 < 1mm**：
- 40kV 高压走线 PCB 表面电场强度 > 1kV/mm
- RS 走线通过空气耦合电压 → silent mode
- 严重时直接击穿 RS pin ESD 保护 → R pin 卡高

#### 根因 4：4V7 齐纳限幅不够 + T24CAN TVS 钳位不够

原本加 4V7 齐纳 + T24CAN TVS 想钳位 RS pin：
- 4V7 齐纳：5mA 钳位下 4.7V，但**40kV 瞬态能量远超 5mA**
- T24CAN TVS：spec 24V 钳位，但**响应时间 1µs > 40kV 上升时间 100ns**
- 钳位失败 → RS pin 被打坏

### 定位（4 步法）

```text
Step 1：排除电源 latch-up / 短路 / 32V PSU 故障
  - 量 VCC 3.3V 正常
  - 量 CAN_H - CAN_L 60Ω 正常
  - 排除电源 / 总线 / PSU 故障

Step 2：单器件替换测试
  - 换不同供应商 SN65HVD234
  - 换不同 MCU（STM32 → NXP LPC）
  - 4% 失效率不变 → 排除单器件问题

Step 3：40kV 瞬态隔离测试
  - 拿掉 40kV 探头 / sensor 端断开
  - 1000 台无失效 → 锁定 40kV 耦合是触发器
  - 加屏蔽线 / 加 RS pin 100nF 去耦 → 失效率从 4% 降到 0.5%

Step 4：定位到 RS pin
  - 示波器看 RS pin 电压波形
  - 40kV 触发瞬间 RS pin 跳到 4.5V（> 0.75 × 3.3V）
  - 触发 silent mode
  - 验证：RS pin 加 10kΩ pull-down + 100nF cap → 失效消失
```

### 修复

| 手段 | 实施 | 验证 |
| --- | --- | --- |
| RS pin pull-down | 加 10kΩ pull-down 到 GND | MCU 启动后 RS < 0.5V |
| RS pin 去耦 | 100nF cap 紧靠 RS pin | 40kV 瞬态 RS < 1V |
| layout 整改 | RS 走线离 40kV > 5mm | 电场耦合 < 100V |
| 加 TVS | RS pin 加 PESD3V3L4UG（5ns 响应） | 钳位 < 1µs |
| 屏蔽线缆 | 4 芯螺旋线 → 屏蔽双绞线 | 耦合电容 < 1pF |

### 复盘

- **4% 失效率 = 良率灾难**（量产项目一般 0.5% 阈值）
- 两供应商 + 两 MCU 复现**排除单器件**——必然是 system-level 设计缺陷
- **RS pin 隐性 silent mode（> 0.75 × VCC → 不发只收）** = datasheet 角落陷阱
- 40kV 瞬态耦合 = 高压项目**默认就要做瞬态抑制**
- T24CAN TVS spec 看似够（24V），但**响应时间不够**是 TVS 选型常见坑
- **datasheet 第 7 章 electrical characteristics 必须逐行读**——不能只看 §1 overview

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-09-11-candidates.md 候选 4
- TI E2E 论坛（Mike Page 求助原帖）
- SN65HVD234 datasheet（TI SLLS877E §7.3）

---

## 案例 16：CAN FD 装车错误帧 bit 24/28 + TDCO 指纹（CSDN 窦明佳）

### 现象

OEM 样车装车后 CAN FD 大量错误帧：
- 单台样车 CAN FD 5Mbps 通信正常
- 入整车网络（30+ ECU）后大量错误帧
- 错误帧位置：**数据段 bit 24 和 bit 28**
- 报"Stuff Error"频率 100 次/分钟
- 影响安全相关 ECU（刹车 / 转向）响应延迟

### 抓包 + 根因（2 大根因 + 1 指纹）

#### 根因 1：TDCO（Transmitter Delay Compensation Offset）配错

CAN FD 5Mbps 数据段用 BRS（Bit Rate Switch），数据段采样点需要调整：
- CAN FD 标准：**TDCO = 数据段采样点位置**
- TDCO 必须补偿收发器环路延迟（典型 50-200ns）
- **本案例 TDCO 配成 0**（默认）→ 数据段采样点错位
- 错位后采样点在边沿过渡区 → 误判率 30%+
- 表现：位错误集中在数据段特定位置（bit 24 / bit 28）

#### 根因 2：物理层耦合 + 多 ECU 噪声叠加

- 单台样车 lab 测试：只有 1 个 ECU → 信号干净
- 入整车网络：30+ ECU 同时通信 → 总线电气环境变差
- **物理层耦合** = 线束间分布参数变化
- 多 ECU 收发器输出阻抗叠加 → 总线阻抗漂移
- 叠加 TDCO 错位 → **错误帧频发**

#### 指纹识别法：bit 24 / bit 28 错误 = TDCO 特征

错误帧位置有规律：
- bit 24 / bit 28 = **数据段中段**
- 数据段 BRS 后第 24/28 bit = TDCO 错位的特征位
- **TDCO 指纹 = 错误帧集中 bit 24/28 = TDCO 错位**
- 这是**软件配置问题**而非物理层问题

### 定位（4 步法）

```text
Step 1：错误帧位置统计
  - 抓 CAN FD 错误帧 → 解析位位置
  - 命中：bit 24/28 集中 = TDCO 指纹
  - 排除物理层

Step 2：TDCO 配置审计
  - 看 MCU CAN FD 控制器 TDCO 寄存器
  - 命中：TDCO = 0 = 配置错误

Step 3：收发器环路延迟测量
  - 用示波器测 TX → RX 环路延迟
  - 期望 50-200ns
  - 命中：实测 100ns → TDCO 应配 100ns

Step 4：物理层验证（排除）
  - 单 ECU 时正常 → 排除物理层
  - 多 ECU 才出错 → 物理层耦合 + TDCO 叠加
```

### 修复

| 维度 | 修复 | 验证 |
| --- | --- | --- |
| 1 TDCO 配置 | TDCO = 100ns（实测收发器环路延迟） | 错误帧从 100/min 降到 0 |
| 2 SSP 配置 | SSP（Secondary Sample Point） = 70-80% | 数据段采样点正确 |
| 3 物理层加固 | 节点加 choke（共模电感） | 总线噪声降 10dB |
| 4 lab 模拟 | lab 加 5 ECU 模拟器 | 早期暴露物理层耦合 |

### SSP（Secondary Sample Point）详解

- CAN FD 数据段 BRS 后有**二次采样点 SSP**
- SSP 位置 = TDCO + 数据段传播延迟补偿
- **正确公式**：
  ```
  SSP = (data bit time - TDCO - propagation delay) / data bit time
      = 70-80%（数据段采样点）
  ```
- 错误 SSP = 错误帧

### 复盘

- **Stuff Error bit 24/28 + 数据段 = TDCO 指纹**——快速识别法
- **单节点 OK / 入网挂掉 = 物理层耦合 + 软件叠加**——lab 必须模拟多 ECU
- **TDCO + SSP 是 CAN FD 5Mbps 必修课**——很多工程师忽略
- **错误帧位置统计 = CAN FD 调试利器**——必查错误位 + 时间戳
- 跟 R8-3 案例 5（RK3576 TDC + CRC-17）互补——本案例从**bit 24/28 指纹**角度
- 跟 R8-3 案例 7（NXP S32K SSP）互补——本案例从**OEM 装车实战**角度

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-09-15-candidates.md 候选 1
- CSDN 窦明佳

---

## 案例 17：模块化机箱背板插卡 120Ω 并联——万用表上电测电阻 SOP

### 现象

某模块化机箱（19 英寸工控机箱，10 个 CAN 插卡）：
- **少量插卡时**：总线通信正常
- **插满后**：总线瘫痪，所有插卡通信中断
- 软件（CAN 控制器配置 / 应用层）反复排查无效
- 资深工程师直接**万用表量 CAN_H↔CAN_L**，发现**每张卡自带 120Ω 终端并联**

### 抓包 + 根因（2 大根因）

#### 根因 1：每张插卡自带 120Ω 终端电阻

- 10 张插卡 × 120Ω = 12Ω 总线电阻（10 张并联）
- CAN 总线要求两端各 120Ω → 总阻 **60Ω**
- 实际 12Ω（5 倍低于 60Ω 匹配点）
- 信号电平严重衰减（3 倍），总线无法识别
- 表现：瘫痪

#### 根因 2：插卡 / 模块化设计自带终端 = 量产隐患

- 插卡设计"贴心配"了 120Ω 终端
- 工程师直觉："总线需要终端 → 加 120Ω 没错"
- **错**：只在**总线两端**加，不能每张卡都加
- 多张卡自带终端 = 终端并联 = 总阻灾难
- **模块化设计的典型陷阱**——**自带终端看似贴心 = 量产炸弹**

### 万用表上电测电阻 SOP（核心排错法）

```text
Step 1：完全断电（重要！）
  - 拔掉所有电源
  - 不能 hot-plug 测电阻

Step 2：万用表 Ω 档
  - 表笔接 CAN_H 和 CAN_L

Step 3：判读
  - 总线无终端：无穷大（> 1 MΩ）
  - 一端有 120Ω：120Ω
  - 两端各 120Ω：60Ω（典型正常）
  - 三端 120Ω：40Ω
  - N 端 120Ω：120/N Ω
  - 10 张卡：12Ω = 命中根因 1

Step 4：决策
  - 60Ω = 正确
  - 偏离 60Ω = 终端数量不对
  - 拆多余终端
```

### 修复

| 维度 | 修复 | 验证 |
| --- | --- | --- |
| 拆多余终端 | 保留 2 张卡（首尾）的 120Ω，拆 8 张卡的 | 测 60Ω = OK |
| 设计层 | 模块化插卡默认不焊终端电阻（贴 0Ω 跳线预留） | 出厂全 0Ω |
| 设计层 | 加拨码开关选配终端 | 现场可配 |
| SOP | 入 commissioning checklist："先测电阻" | 永远第一项 |

### 量产 Checklist（设计层预防）

```text
□ 模块化插卡默认不焊 120Ω（贴 0Ω 跳线）
□ 拨码开关 / 跳线预留终端选配位
□ 出厂默认 0Ω + commissioning 时由工程师选配
□ 标签 / 文档明确"两端各 120Ω"原则
□ commissioning SOP："上电前先量 CAN_H↔CAN_L"
□ 现场部署前必测电阻
```

### 复盘

- **任何总线"上电测电阻"应排第一**——**比看代码 / 看 log 优先级高**
- **插卡 / 模块化设计自带终端 = 量产隐患**——必须避免
- **资深工程师 vs 新手差距 = 排错顺序**——**先硬件后软件**
- 跟 R16-4 案例 13（4 大 killer lab 通产线崩）互补——本案例是 **killer 3（终端电阻错）** 的具体案例
- 跟 R8-3 案例 6（装车 TDC Stuff Error 200 节点）互补——本案例从 **背板插卡** 角度
- **任何 CAN 总线项目 = "先万用表量电阻"** 是**第一 SOP**

### 来源

- _Inbox/CAN-FD-CAN-XL-2026-09-15-candidates.md 候选 4
- LinkedIn（Kumar Swamy Naik 调试日记）

---

## 案例 18：STM32H5 FDCAN + 收发器 4 模式原子切换——5Mbps 反射 + 2000 msg/s Bus-Off

### 现象

STM32H562 多传感器边缘平台，CAN FD 部署：
- 仲裁段 1Mbps + 数据段 5Mbps
- 产线出货后**帧丢失** + **2000 msg/s 触发 Bus-off**
- 5Mbps 数据段反射问题
- 收发器模式机时序违例
- 根因 = **5Mbps 信号反射 + 收发器 4 模式原子切换缺失**

### 抓包 + 根因

#### 根因 1：5Mbps 信号反射致 Bus-off

- 数据段 5Mbps = 200ns bit time
- 反射叠加到边沿过渡区 → 采样点失败
- 错误计数（TEC/REC）迅速累加 → 256 = Bus-off
- **2000 msg/s** 速率 = **典型触发 Bus-off 阈值**
- 表现：ECU 频繁断网 1-2 秒恢复

**修复**：降到保守时序 + SP 余量

```c
// STM32H5 FDCAN 配置（保守 + 鲁棒）
hfdcan1.Init.NominalPrescaler = 16;    // 1Mbps 仲裁段 = 64MHz / 16 = 4 Mbps Tq
hfdcan1.Init.NominalTimeSeg1 = 14;     // SP 75%
hfdcan1.Init.NominalTimeSeg2 = 5;
hfdcan1.Init.DataPrescaler = 4;        // 5Mbps 数据段 = 64MHz / 4 = 16 MHz Tq
hfdcan1.Init.DataTimeSeg1 = 12;        // SP 80%
hfdcan1.Init.DataTimeSeg2 = 4;
hfdcan1.Init.TXCfgFdCan = FDCAN_TXCFGFD_CAN;
hfdcan1.Init.TxDelayCompensation = ENABLE;  // TDC enable
```

#### 根因 2：收发器 4 模式原子切换缺失

- 收发器（典型如 TJA1145 / ISO1050）有 4 模式：
  - **SLEEP**：最低功耗，仅监控 wake-up
  - **STANDBY**：待命，可监控 wake-up
  - **LISTEN**：只听不发（silent mode）
  - **NORMAL**：正常收发
- 模式切换时**收发器内部状态机有 10ms 稳定延迟**
- **如果原子切换**（SLEEP → NORMAL 立即收发）→ 收发器未稳定 → 第一帧丢失
- 表现：每次模式切换后**第一帧 100% 丢**

**修复**：原子切换 + 10ms 延迟

```c
// 4 模式原子切换（关键）
void canfd_set_normal_mode(CANFD_Handle_t *hcan) {
    // Step 1: SLEEP
    HAL_GPIO_WritePin(CANFD_STB_PIN, GPIO_PIN_SET);     // STB = HIGH
    HAL_GPIO_WritePin(CANFD_EN_PIN, GPIO_PIN_RESET);    // EN = LOW
    delay_ms(10);  // SLEEP 稳定
    
    // Step 2: STANDBY
    HAL_GPIO_WritePin(CANFD_STB_PIN, GPIO_PIN_RESET);   // STB = LOW
    delay_ms(10);  // STANDBY 稳定
    
    // Step 3: LISTEN
    HAL_GPIO_WritePin(CANFD_EN_PIN, GPIO_PIN_SET);      // EN = HIGH
    delay_ms(10);  // LISTEN 稳定
    
    // Step 4: NORMAL
    HAL_GPIO_WritePin(CANFD_STB_PIN, GPIO_PIN_SET);     // STB = HIGH
    delay_ms(10);  // NORMAL 稳定 → 可收发
}
```

### 修复 Checklist

```text
□ STM32H5 FDCAN 寄存器配置（Prescaler=16 / SP=87.5% / TDC enable）
□ 数据段 SP 加余量（80% → 87.5%）
□ 收发器模式切换加 10ms 稳定延迟
□ 收发器模式切换顺序：SLEEP → STANDBY → LISTEN → NORMAL
□ Bus-off 后等待 128 次 11 位 recessive（128 × 200ns = 25.6µs）
□ 量产测试 2000 msg/s 压力
□ 错峰上报避免瞬时高负载
```

### 定位（4 步法）

```text
Step 1：抓 FDCAN 寄存器配置
  - 期望 Prescaler=16 / SP=87.5% / TDC enable
  - 实际错 → 命中根因 1

Step 2：抓收发器 STB/EN 引脚
  - 期望 4 模式切换各 10ms 延迟
  - 实际立即切换 → 命中根因 2

Step 3：抓 Bus-off 触发时刻
  - 期望 ≤ 5 Mbps 错峰
  - 实际 2000 msg/s 触发 → 命中根因 1

Step 4：抓 Bus-off 恢复时间
  - 期望 128 × 11-bit recessive = 25.6 µs
  - 实际更长 → 检查电源固件
```

### 复盘

- **STM32H5 FDCAN 寄存器模板**——**Prescaler=16 / SP=87.5% / TDC enable** 是鲁棒配方
- **收发器 4 模式原子切换 + 10ms 稳定**——**第一帧丢的隐形原因**
- **数据段 SP 加余量**——**80% → 87.5%** 更鲁棒
- **Bus-off 触发条件 = 2000 msg/s**——错峰上报避免
- 跟 R16-4 案例 13（4 大 killer lab 通产线崩）**互补**——本案例从 **STM32H5 寄存器**视角
- 跟 R18-12 案例 16（TDCO 指纹）**互补**——本案例从**收发器模式机**视角

### 来源

- _Inbox/CAN-FD-2026-09-17-candidates.md 候选 2
- Hoomanely Tech Blog（STM32H562 多传感器边缘平台）

---

## 案例 19：CAN 错误状态机——TEC/REC 阈值 + REC↑=EMC/TEC↑=硬件 + FreeRTOS 监控模板

### 现象

车载网关装车后**每 2-3 小时某 ECU Bus-off**：
- SN65HVD230 VCC 在空调/ABS 启动时跌落 1.5V
- 加 100µF 钽电容修复
- **实战经验总结**：
  - **REC↑ = EMC 问题**
  - **TEC↑ = 发送端硬件缺陷**
- FreeRTOS 监控任务模板

### CAN 错误状态机详解

#### 3 个状态阈值

```text
TEC/REC 0-95：Error Active（主动错误）
  - 可正常收发
  - 错误时发 Active Error Flag（6 位显性位）

TEC/REC 96-127：Error Passive（被动错误）
  - 仍可收发
  - 错误时发 Passive Error Flag（6 位隐性位）
  - **警告！需排查**

TEC/REC ≥ 128：Error Passive
  - 仍可收发（但仍 passive）
  - **严重警告**

TEC ≥ 256 OR REC ≥ 256：Bus-Off
  - 完全禁止收发
  - 等待 128 次 11 位 recessive 信号后才尝试恢复
  - **必须排查根因**
```

#### REC↑ vs TEC↑ 的实战意义

| 指标 | 含义 | 排查方向 |
| --- | --- | --- |
| **REC↑（接收错）** | 收到的帧有 CRC 错误 / 位错误 / ACK 错误 | **EMC 问题**（外部干扰 / 总线噪声） |
| **TEC↑（发送错）** | 发送的帧被 ACK 否定 / 位错误 / 仲裁失败 | **发送端硬件问题**（收发器 / VCC / 时序） |
| **REC 和 TEC 同时↑** | 双向问题 | 总线物理层（共模 / 终端 / stub） |

### 真实车载案例

- 车载网关装车后 2-3 小时某 ECU Bus-off
- VCC 测量：3.3V 正常时 TEC/REC = 0
- 空调/ABS 启动瞬间：VCC 跌到 1.5V（**电源跌落**）
- VCC < 2.85V → 收发器 SN65HVD230 进入 shutdown 模式
- 收发器不工作 = 帧丢失 → 错误计数累加 → Bus-off
- **修复**：收发器 VCC 加 100µF 钽电容（局部稳压）
- **预防**：加 power waveform 测试，CI 验证 CAN 通信

### FreeRTOS 监控任务模板

```c
// can_monitor_task.c
void can_monitor_task(void *arg) {
    CAN_ErrorCounters_t ec;
    
    while (1) {
        // 每 100ms 读一次错误计数器
        vTaskDelay(pdMS_TO_TICKS(100));
        
        CAN_GetErrorCounters(&hcan1, &ec);
        
        // REC↑ 警告（EMC）
        if (ec.REC > 96 && ec.REC < 128) {
            log_warning("CAN REC %d (EMC 警告)", ec.REC);
        }
        
        // TEC↑ 警告（硬件）
        if (ec.TEC > 96 && ec.TEC < 128) {
            log_warning("CAN TEC %d (发送端硬件警告)", ec.TEC);
        }
        
        // 5s 节流报警
        static uint32_t last_alert = 0;
        if ((ec.REC >= 96 || ec.TEC >= 96) &&
            (HAL_GetTick() - last_alert) > 5000) {
            can_send_dtc_to_app(ec.REC, ec.TEC);  // 故障码上报
            last_alert = HAL_GetTick();
        }
        
        // Bus-Off 自动恢复
        if (hcan1.Instance->PSR & FDCAN_PSR_BO) {
            log_error("CAN Bus-Off detected");
            // 主动复位
            CAN_ResetBusOff(&hcan1);
        }
    }
}
```

### 错误计数器判读决策树

```text
REC > 96
  ├─ 仅 REC↑（TEC 0-50）
  │   → EMC 排查
  │   → 检查总线 noise、屏蔽、接地
  │
  └─ REC 和 TEC 同时↑
      → 总线物理层
      → 检查终端电阻、stub 长度、屏蔽

TEC > 96
  ├─ 仅 TEC↑（REC 0-50）
  │   → 发送端硬件
  │   → 检查 VCC、收发器、时钟、SP 配置
  │
  └─ REC 和 TEC 同时↑
      → 总线物理层（双向）

TEC ≥ 256 OR REC ≥ 256
  → Bus-Off
  → 等待自动恢复
  → 检查根因（上面任意一项）
  → 上报应用层
```

### 修复 Checklist

```text
□ FreeRTOS 监控任务 100ms 检查 TEC/REC
□ REC↑ = EMC 排查（屏蔽 / 接地 / 噪声）
□ TEC↑ = 硬件排查（VCC / 收发器 / 时序）
□ 收发器 VCC 加 100µF 钽电容（防跌落）
□ VCC 监控（电压跌落 < 2.85V 报警）
□ Bus-Off 自动恢复 + 上报
□ 错误码 DTC 上传到应用层
□ 5s 节流报警（避免 spam）
```

### 复盘

- **TEC/REC 阈值 = 状态机的关键数据**——必须监控
- **REC↑=EMC / TEC↑=硬件**——实战经验总结，跨项目通用
- **VCC 跌落 = 收发器 shutdown**——收发器 VCC 加 bulk cap
- **FreeRTOS 监控任务模板**——100ms 检查 + 5s 节流报警
- **Bus-Off 自动恢复**——128 × 11-bit recessive 后重连
- **错误码 DTC 上传**——业务层能看到
- 跟 R12-3 案例 11（TEC 256 Bus-Off + VCC 1.5V 跌落）**同源**但本案例强调 **TEC/REC 决策树**
- 跟 R18-12 案例 16（TDCO 指纹）**互补**——本案例从**状态机监控**视角

### 来源

- _Inbox/CAN-FD-2026-09-17-candidates.md 候选 4
- CSDN（汽车电子项目）

---

## 案例 20：STM32 FDCAN UDS——硬件 CRC 含位填充 vs 软件不含 + 2Mbps 才出现的 CRC 错

### 现象

STM32H7 车载网关量产项目，OEM 工厂 Vector CANoe v11 `CheckCRC()` 报 CRC 错误：
- 研发环境 100% 通过
- 量产工厂 100% 报 CRC 错
- OEM 客户工厂跟研发环境分别 100% 通过
- 同一个项目，3 个环境**结果完全不一致**
- 根因 = **STM32 硬件 CRC 含位填充 + 软件算法不含 + 2Mbps 才出现**

### 抓包 + 根因（3 大根因）

#### 根因 1：STM32 硬件 CRC 包含位填充

- CAN FD 协议规定：**CRC 计算覆盖位填充后的位流**
- 位填充：连续 5 个同极性位插入 1 个反极性位
- STM32 FDCAN 硬件 CRC 单元：**覆盖位填充后的整个位流**（包括 stuffed bits）
- **CANoe 软件算法**：`CheckCRC()` **覆盖** stuffing bits **但计算方式不同**
- 研发环境 vs 量产 = **测试工具算法不一致** → CRC 不匹配

#### 根因 2：2Mbps 速率下才出现

- 1Mbps @ 短帧：位填充触发次数少（5 个同极性位出现少）
- 2Mbps @ 长帧：位填充触发次数多
- **2Mbps 才暴露**是因为位填充概率与数据段长度/速率正相关
- 实测：1Mbps 完全 OK，2Mbps 100% CRC 错

#### 根因 3：UDS 栈集成时序坑

- UDS（Unified Diagnostic Services）基于 CAN/CAN-FD
- P2 Server timer（默认 50ms）：响应等待时间
- P2* Server timer（默认 5000ms）：NRC 0x78 响应等待时间
- S3 Server timer（默认 5000ms）：会话保持时间
- **常见错**：
  - tester 等待 P2 = 50ms 但 server 处理慢（>50ms）→ tester 报超时
  - tester 不识别 NRC 0x78 → 误判 server 无响应
  - server 不发 NRC 0x78 → tester 真超时

### 修复（4 维）

#### 修复 1：FDCAN 寄存器配置

```c
// FDCAN_CCCR.RETRAN 关闭 + 软件重传 + TIM16 超时控制
hfdcan1.Instance->CCCR &= ~FDCAN_CCCR_RETRAN;  // 关闭硬件自动重传
// 软件层处理重传 + 50ms 超时
```

#### 修复 2：FDCAN_TXBC.TFQS 配置

```c
// FDCAN_TXBC.TFQS ≥ 16（传输 FIFO 队列大小）
hfdcan1.Instance->TXBC |= FDCAN_TXBC_TFQS_16;
// 优先处理流控帧（避免 BRS 切换丢帧）
HAL_FDCAN_ConfigTxQueueFifo(&hfdcan1, FDCAN_TX_PRIORITY_HIGH, 0);
```

#### 修复 3：UDS 时序参数

```c
// P2 Server timer = 50ms（响应等待）
// P2* Server timer = 5000ms（NRC 0x78 等待）
// S3 Server timer = 5000ms（会话保持）
#define UDS_P2_SERVER_TIMER_MS 50
#define UDS_P2_STAR_SERVER_TIMER_MS 5000
#define UDS_S3_SERVER_TIMER_MS 5000
```

#### 修复 4：CRC 算法统一

```c
// 软件 CRC 必须跟硬件 CRC 算法一致
// CRC-17（CAN FD 数据段 ≤ 16B）：多项式 0x1685B
// CRC-21（CAN FD 数据段 17-64B）：多项式 0x102899
// CRC 算法必须包含位填充位流
```

### 量产 SOP 4 类验证清单

```text
□ 电气特性验证
  - Vmin/Vmax 边界
  - 共模电压范围
  - 终端电阻匹配

□ 协议一致性验证
  - CANoe CheckCRC() 100% pass
  - 多 firmware 版本兼容
  - 多 OEM 测试工具兼容（Vector / ETAS / CANalyzer）

□ 环境适应性验证
  - 高温（85℃）运行 24h
  - 高湿（85% RH）运行 24h
  - EMC 注入干扰

□ 产线专用验证
  - 自动化测试覆盖率 100%
  - 测试固件版本对齐
  - 测试设备校准
  - 失败率统计 + 8D 报告
```

### 修复 Checklist

```text
□ FDCAN_CCCR.RETRAN 关闭 + 软件重传
□ FDCAN_TXBC.TFQS ≥ 16
□ 优先处理流控帧
□ CRC 算法统一（包含位填充）
□ UDS P2/P2*/S3 timer 严格配置
□ NRC 0x78 必发 + tester 必识别
□ 量产 SOP 4 类验证清单全过
□ 工具差异（Vector vs ETAS）兼容性测试
```

### 复盘

- **STM32 硬件 CRC 含位填充**——**软件算法必须同步**
- **2Mbps 长帧位填充概率高**——1Mbps 不暴露的坑
- **UDS P2/P2*/S3 timer**——时序坑最隐蔽
- **NRC 0x78 是诊断协议响应**——必须识别
- **量产 SOP 4 类验证**——电气 + 协议 + 环境 + 产线
- **工具差异（CANoe vs ETAS）**——算法不一致会出 CRC 错
- 跟 R18-12 案例 16（TDCO 指纹）**互补**——本案例从**软件/算法/时序**视角
- 跟 R12-3 案例 7（NXP S32K SSP）**互补**——本案例从**UDS / CRC**视角

### 来源

- _Inbox/CAN-FD-2026-09-17-candidates.md 候选 5
- CSDN（STM32H7 车载网关量产经验）

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
