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
