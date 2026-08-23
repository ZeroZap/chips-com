# CAN Deep Dive

## 目标

深入 CAN 总线工程细节, 重点覆盖:
- CAN 物理层 (差分, 收发器, 终端)
- CAN 帧格式 (标准 / 扩展 / FD)
- 仲裁机制
- 错误处理 (位错误, 错误帧, 错误计数器, 总线关闭)
- 故障树 (现象 → 根因 → 定位 → 修复)
- 多 master 仲裁
- 与 SMBus / I2C / SPI 的关键差异

## CAN 的工程定位

CAN (Controller Area Network) 是 Bosch 在 1986 年为汽车设计的串行通信协议。

**适用场景**:

- 汽车电子 (OBD, ECU, 车身网络, 动力总成)
- 工业控制 (CANopen, DeviceNet, J1939)
- 医疗设备 (可靠通信)
- 楼宇自动化 (BACnet)
- 嵌入式分布式系统

**不适用**:

- 高带宽视频 / 音频 (用 Ethernet)
- 长距离 (CAN FD 用 1km, 工业总线更合适)
- 大量节点 (> 32 用中继)

工程直觉:

```text
CAN 是"可靠的多 master 现场总线", 强在错误检测和仲裁
CAN 不是"高速总线", 速度是 UART 量级 (1-5M)
```

## CAN 物理层

### 差分信号

```text
        隐性 (recessive, 逻辑 1)
        ─────────────────────────
        CAN_H ─────── 2.5V
        CAN_L ─────── 2.5V
        差分 (H-L) ── 0V
        
        显性 (dominant, 逻辑 0)
        ─────────────────────────
        CAN_H ─────── 3.5V
        CAN_L ─────── 1.5V
        差分 (H-L) ── 2.0V
```

**关键**:

- 总线空闲 = 隐性 (1)
- 数据 0 = 显性 (0)
- **显性优先**: 多个节点同时发, 显性位会覆盖隐性位 → 仲裁的基础

### 终端电阻

```text
Node A                              Node B
[120]  CAN_H ──────────── CAN_H  [120]
       CAN_L ──────────── CAN_L
       
量 A-B 电阻: 60 ohm (两个 120 ohm 并联)
```

**为什么需要**: CAN 是高速差分信号, 没有终端电阻会有反射, 边沿畸变。

### 收发器作用

```text
MCU CAN TX/RX (TTL 数字) <---> 收发器 <---> 总线 CAN_H / CAN_L (差分模拟)
```

收发器负责:

- TTL ↔ 差分转换
- 显性驱动 (主动拉低总线)
- 隐性释放 (靠总线电阻回到 2.5V)
- 故障保护 (±60V / ±70V 总线故障时保护 MCU)
- ESD 保护
- 隔离 (部分型号)

### 收发器选型表

| 型号 | 速率 | 隔离 | 故障保护 | 车规 |
| --- | --- | --- | --- | --- |
| TJA1050 | 1M | 无 | ±60V | 准车规 |
| TJA1042 | 1M | 无 | ±58V | AEC-Q100 |
| TJA1443 | 5M | 无 | ±70V | AEC-Q100 |
| TJA1145 | 5M | 无 | ±58V + 睡眠 | AEC-Q100 |
| SN65HVD257 | 5M | 无 | ±70V | 工业 |
| ISO1050 | 1M | 磁隔离 | ±60V | 工业 |
| ADM3053 | 1M | 数字隔离 | ±25V | 工业 |
| IFX1051LE | 1M | 无 | ±40V | AEC-Q100 |

## CAN 帧格式 (经典 CAN)

### 数据帧结构

```text
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ SOF │  ID │ RTR │ Ctrl│ Data│ CRC │ ACK │ EOF │ IFS│
│ 1bit│ 11or29│ 1   │ 6  │ 0-8 │ 16  │ 2  │ 7   │ 3 │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

| 字段 | 长度 | 含义 |
| --- | --- | --- |
| SOF (Start of Frame) | 1 bit | 显性位, 标志帧开始 |
| ID (Identifier) | 11 or 29 bit | 帧标识, 也决定优先级 |
| RTR (Remote Transmission Request) | 1 bit | 0 = 数据帧, 1 = 远程帧 |
| Control (IDE, r0, DLC) | 6 bit | IDE (标准/扩展), DLC (数据长度码) |
| Data | 0-8 byte | 实际数据 (CAN 2.0) |
| CRC | 16 bit | 15 位 CRC + 1 位定界符 |
| ACK | 2 bit | 接收方应答 |
| EOF (End of Frame) | 7 bit | 连续隐性位 |
| IFS (Interframe Space) | 3 bit | 帧间隔 |

### 标准 vs 扩展

```text
标准帧 (CAN 2.0A):  11 bit ID
扩展帧 (CAN 2.0B):  29 bit ID
                     29 = 11 + 18 + SRR + IDE

两者在总线上共存, 扩展帧优先级低于标准帧
```

### 位填充 (Bit Stuffing)

CAN 用 NRZ 编码, 但规定:

- **5 个连续相同位后必须插入 1 个反相位**
- 接收方反填充恢复

```text
原始:  11111 00000 11111
填充:  11111 0 00000 1 11111
      ^填充位  ^填充位
```

**原因**: 防止长串 0/1 导致接收方时钟漂移。

## CAN 仲裁机制

### 显性优先

```text
总线特性: 显性 (0) > 隐性 (1)
多个节点同时发, 显性位会"盖掉"隐性位
```

### 仲裁过程

```text
时序:
1. 所有节点同时开始发 SOF (显性)
2. 节点发自己的 ID (从 MSB 开始)
3. 节点监听总线:
   - 如果发的位 = 监听到的位 -> 继续发
   - 如果发的位 = 1 (隐性), 但监听到 0 (显性) -> 仲裁失败, 立即退出
4. 最后剩下的节点赢得仲裁, 继续发剩余帧
```

**示例**:

```text
节点 A ID: 0x123 = 001 0010 0011 (11 bit)
节点 B ID: 0x456 = 100 0101 0110
节点 C ID: 0x789 = 111 1000 1001

bit 0 (MSB): A=0, B=1, C=1  -> 总线 = 0 (A 显性)
bit 1:       A=0, B=0, C=1  -> 总线 = 0
bit 2:       A=1, B=0, C=1  -> 总线 = 0
            A 发 1, 听到 0, A 退出 (但 B 不知道 A 在听)
            C 发 1, 听到 0, C 退出
bit 3:       B=0, C=0        -> B 和 C 继续
...
最后 B 赢得仲裁
```

**关键**: **ID 越小, 优先级越高** (因为 0 是显性, 更早出现)。

## CAN 错误处理

### 5 种错误类型

| 错误 | 触发 | 检测方 |
| --- | --- | --- |
| 位错误 (Bit Error) | 发送的位和监听到的位不一致 (仲裁和 ACK 阶段除外) | 发送方 |
| 填充错误 (Stuff Error) | 6 个连续相同位 (违反位填充规则) | 接收方 |
| CRC 错误 (CRC Error) | 接收方 CRC 校验失败 | 接收方 |
| 形式错误 (Form Error) | 固定格式位错 (CRC 定界符, ACK 定界符, EOF) | 接收方 |
| 应答错误 (ACK Error) | 发送方未收到 ACK (没有节点收到) | 发送方 |

### 错误计数器

每个 CAN 节点有 2 个错误计数器:

```text
TEC (Transmit Error Counter): 发送错误计数
REC (Receive Error Counter): 接收错误计数
```

**规则**:

```text
发送方检测到错误:
  -> TEC + 8 (主动错误)
  -> TEC + 8, 但如果之前是 error passive: TEC += 1
  -> 如果成功发送: TEC - 1 (>= 0)

接收方检测到错误:
  -> REC + 8 (主动错误)
  -> 成功接收: REC - 1 (>= 0)
```

### 节点状态

```text
                        TEC/REC <= 127
              ┌─────────────────────────────┐
              │       Error Active          │  (正常)
              │  发主动错误帧 (6 dominant)  │
              └─────────────────────────────┘
                            │
                            │ TEC 或 REC > 127
                            ↓
              ┌─────────────────────────────┐
              │      Error Passive          │  (降级)
              │  发被动错误帧 (6 recessive) │
              │  发送后必须等待 8 bit 暂停   │
              └─────────────────────────────┘
                            │
                            │ TEC > 255
                            ↓
              ┌─────────────────────────────┐
              │        Bus Off              │  (离线)
              │  节点完全脱离总线            │
              │  必须软件 reset 重新加入     │
              └─────────────────────────────┘
```

**关键**:

- 主动错误帧: 6 个显性位, 强制其他节点看到错误
- 被动错误帧: 6 个隐性位, 不影响其他节点 (但其他节点会因填充错误报告)
- Bus Off: 节点必须软件重置才能回总线

### 自动重连

多数 CAN 控制器有自动重连机制:

```c
/* STM32 HAL 例子 */
HAL_CAN_Start(&hcan1);  // 启动 CAN
/* 如果 bus off, 控制器进入 bus off 状态, 不再发帧 */
/* 软件可以设 ABBOM (Automatic Bus-Off Management) 启用自动重连 */

hcan1.Init.AutoBusOff = ENABLE;  // 自动恢复
```

## CAN FD 简介

### 与 CAN 2.0 的差异

| 维度 | CAN 2.0 | CAN FD |
| --- | --- | --- |
| 速率 (仲裁段) | 1 Mbaud | 1 Mbaud (不变) |
| 速率 (数据段) | 1 Mbaud | 2-5 Mbaud (可更高) |
| 数据长度 | 0-8 byte | 0-64 byte |
| 帧格式 | 1 种 | CAN 2.0 + CAN FD 兼容 |
| 收发器 | 标准 | 必须支持 CAN FD |
| 控制器 | 经典 CAN | bxCAN + CAN FD 模式 |

### CAN FD 帧格式

```text
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ SOF │  ID │RRS/│ FD  │   │  BRS│ ESI│ Data│ CRC │ ACK │ EOF │
│     │     │FDF  │  FMT│ DLC│     │    │     │     │     │     │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
                              ↑     ↑    ↑
                              切换  切换  长度可变
                              速率  状态
```

**关键字段**:

- FDF: 0 = 经典 CAN, 1 = CAN FD
- BRS: 0 = 数据段用仲裁段速率, 1 = 数据段用更高速率
- ESI: 错误状态指示 (0 = 主动, 1 = 被动)

## CAN XL 简介

### 与 CAN FD 的差异

| 维度 | CAN FD | CAN XL |
| --- | --- | --- |
| 数据长度 | 0-64 byte | 1-2048 byte |
| 最大速率 | 5 Mbaud (实际) | 10+ Mbaud |
| 应用 | 控制器 | 主干网 / 高速 |

### CAN XL 帧格式

```text
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ SOF │  ID │ SDT │  VC │  AD │SADL │ SEC │ Data│ CRC │EOF│
│     │     │     │     │     │     │     │     │     │   │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
                        ↑     ↑     ↑
                        虚拟通道 加速  安全
```

CAN XL 还在演进, 多数 MCU 尚未支持, 但 Bosch / NXP 已有 IP。

## CAN 故障树

把 CAN 通信异常的所有可能根因画成决策树:

```text
现象: CAN 通信失败
  |
  +-- 抓波形 (用示波器 / CAN 分析仪)
        |
        +-- 总线没波形
        |     -> 收发器供电错 / 终端电阻错 / 接线错
        |     -> 验证: 量 VCC, 量 60 ohm 终端
        |
        +-- 总线电平错
        |     -> 收发器坏 / 终端电阻错 / 总线短路
        |     -> 验证: 量隐性 2.5V, 显性 H=3.5 L=1.5
        |
        +-- 大量错误帧
        |     -> 波特率不匹配 / 终端电阻错 / 总线干扰
        |     -> 验证: 用 CAN 分析仪看错误率, 逐个节点断开
        |
        +-- 节点 bus off
        |     -> 节点错误率太高 / 收发器坏 / 控制器配置错
        |     -> 验证: 查 TEC, 复位节点
        |
        +-- 偶发丢帧
        |     -> 干扰 / EMC / 总线波形畸变
        |     -> 验证: 示波器看波形, 加屏蔽
        |
        +-- CAN FD 跑不通
              -> 收发器不支持 / 物理层参数错 / 控制器的 FD 模式没开
              -> 验证: 查收发器型号, 重新配置
```

### 故障树对应快速判定

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 总线没波形 | 收发器 / 终端 / 接线 | 量 VCC, 量 60 ohm |
| 总线电平错 | 收发器坏 / 短路 | 量隐性 / 显性 |
| 大量错误帧 | 波特率不匹配 | 用分析仪看错误率 |
| 节点 bus off | 错误率超限 | 查 TEC, 复位 |
| 偶发丢帧 | 干扰 / EMC | 示波器 + 屏蔽 |
| CAN FD 跑不通 | 收发器不支持 | 查型号, 配参数 |

## CAN vs I2C vs SPI vs UART 关键差异

| 维度 | CAN | I2C | SPI | UART |
| --- | --- | --- | --- | --- |
| 速度 | 1M-5M | < 3.4M | 10M-200M | < 6M |
| 物理 | 差分 | 单端开漏 | 单端推挽 | 单端推挽 |
| 多 master | 硬件仲裁 | 软件地址 | CS 选主 | 无 |
| 错误检测 | 强 (CRC + 5 类) | 弱 (ACK) | 无 | 弱 (parity) |
| 距离 | 1km (低速) | 短 | 短 | RS485 1km |
| 节点数 | 32-256 | 多个 | 多个 (CS) | 2 (RS485 多) |
| 可靠性 | 高 | 中 | 中 | 中 |
| 典型场景 | 汽车 / 工业 | 板内 | Flash / LCD | 调试口 |

**选型**:

- 板内管理, 多个设备 → I2C
- 高速短距离, 单向 → SPI
- 异步长距离, 简单 → UART/RS485
- 实时多节点, 强可靠 → **CAN**

## CAN 控制器常见配置

```c
/* STM32 HAL 例子 */
hcan1.Instance = CAN1;
hcan1.Init.Prescaler = 9;              // 时钟分频
hcan1.Init.Mode = CAN_MODE_NORMAL;      // 正常模式 (vs LOOPBACK, SILENT)
hcan1.Init.SyncJumpWidth = 1;           // 同步跳转宽度
hcan1.Init.TimeSeg1 = 6;                // BS1 (时间段 1)
hcan1.Init.TimeSeg2 = 1;                // BS2 (时间段 2)
hcan1.Init.TimeTriggeredMode = DISABLE; // 时间触发模式
hcan1.Init.AutoBusOff = ENABLE;         // 自动重连
hcan1.Init.AutoWakeUp = DISABLE;        // 自动唤醒
hcan1.Init.AutoRetransmission = ENABLE; // 自动重传
hcan1.Init.ReceiveFifoLocked = DISABLE; // FIFO 锁定
hcan1.Init.TransmitFifoPriority = ENABLE; // TX FIFO 优先级

HAL_CAN_Init(&hcan1);
```

### 波特率计算

```text
NominalBitTime = (SyncSeg + BS1 + BS2) × Tq
                = (1 + 6 + 1) × Tq
                = 8 × Tq

Tq = (Prescaler × Tclk) = 9 × (1/36 MHz) = 0.25 us

BitTime = 8 × 0.25 us = 2 us
Baud = 1 / BitTime = 1 Mbaud
```

**常见错误**: 算出来的 baud 和实际不符, 多半是 Tq 配错。

## CAN 过滤器

CAN 控制器通常有硬件 ID 过滤器, 减少 CPU 中断负担。

```c
/* STM32 HAL 过滤器配置 */
CAN_FilterTypeDef filter;
filter.FilterBank = 0;
filter.FilterMode = CAN_FILTERMODE_IDMASK;  // 掩码模式
filter.FilterScale = CAN_FILTERSCALE_32BIT; // 32 位
filter.FilterIdHigh = 0x123 << 5;           // ID = 0x123
filter.FilterIdLow = 0x0000;
filter.FilterMaskIdHigh = 0x7F8 << 5;       // 只匹配 11 bit ID
filter.FilterMaskIdLow = 0x0000;
filter.FilterFIFOAssignment = CAN_RX_FIFO0;
filter.FilterActivation = ENABLE;

HAL_CAN_ConfigFilter(&hcan1, &filter);
```

**关键**: 过滤器不对, 节点会"听不到"特定 ID。

## CAN 状态机

```text
IDLE
  -> (发起发送) -> TRANSMIT
TRANSMIT
  -> (发送成功) -> IDLE
  -> (仲裁失败) -> BACKOFF (自动重试)
  -> (发送错误) -> ERROR_ACTIVE
ERROR_ACTIVE
  -> (TEC > 127) -> ERROR_PASSIVE
ERROR_PASSIVE
  -> (TEC > 255) -> BUS_OFF
BUS_OFF
  -> (软件 reset) -> IDLE
RECEIVE
  -> (匹配 ID) -> APP_NOTIFY
  -> (不匹配) -> IDLE
  -> (CRC 错) -> ERROR_ACTIVE
```

## 协议层检查清单

```text
□ 波特率匹配 (双方)
□ 帧格式匹配 (标准/扩展/FD)
□ ID 分配不冲突
□ 过滤器配对 (接收方)
□ 终端电阻两端各 120 ohm
□ 收发器供电正常
□ AutoBusOff 配置
□ 错误计数器监控
□ 节点数 <= 32 (标准收发器)
```

## 7 条 CAN 常见错误

| # | 错误 | 后果 |
| --- | --- | --- |
| 1 | 缺终端电阻 | 波形反射, 错误帧 |
| 2 | 终端电阻只一端 | 反射, 距离 1/2 之外不可靠 |
| 3 | 多个 120 ohm 并联 | 阻值过小, 信号衰减 |
| 4 | 波特率算错 | 一直 error passive |
| 5 | CAN FD 用经典 CAN 收发器 | 数据段错 |
| 6 | 节点数 > 32 | 总线负载过重 |
| 7 | ID 分配冲突 | 仲裁时两个节点都失败 |

## 关联文档

- `can-practical.md` 速查
- `can-failure-cases.md` 产线死机案例
- `can-multimaster-and-bus-off.md` 多 master + 总线关闭
- `can-fd-and-can-xl.md` 演进
- `can-rtos-integration.md` RTOS + SocketCAN
- `can-vs-other-bus.md` 跨总线对比
- `can-index.md` 导航
- `bus/can-canopen-deep-dive.md` CANopen
- `bus/can-canopen-practical.md` CANopen 实战
- `basic/can-phy.md` CAN 物理层
- `i2c-bus-recovery-playbook.md` I2C recovery (I2C 也有错误恢复)
- `i2c-state-machine.md` I2C 状态机 (对比)
