# CAN 产线死机案例库

## 目标

把产线常见的 CAN 通信失败、节点 bus off、错误帧等问题写成案例库。每个案例:
- 现象 (现场)
- 抓波形 / 分析仪 (判断)
- 定位 (根因)
- 修复 (代码 / 硬件)
- 复盘 (如何预防)

## 案例 1: 节点频繁 bus off, 整个网络瘫

### 现象

新板上线 5 分钟, 一个 ECU 节点开始错误帧, 然后整个网络瘫。所有节点都收不到有效数据。

### 抓波形

用 CAN 分析仪抓帧: 一个节点连续发 6 个 dominant (主动错误帧), 然后 6 个 recessive (被动错误帧), 然后 bus off 静默。

### 定位

那个 ECU 节点的 CAN 收发器硬件故障, 导致发送的位和监听到的位不一致, 触发位错误。错误计数器 (TEC) 持续上升, 达到 255 后进入 bus off。

但 bus off 不应该让整个网络瘫——除非这个节点一直发主动错误帧, 阻塞了其他节点。

```text
主动错误帧: 6 个 dominant 位
多个节点同时发: 显性优先 -> 持续阻塞
```

### 修复

```c
/* 1. 启用 AutoBusOff */
hcan1.Init.AutoBusOff = ENABLE;
HAL_CAN_Init(&hcan1);

/* 2. 监控 TEC/REC, 异常时通知 */
void can_error_handler(uint32_t err) {
    if (err & CAN_ESR_BOFF) {
        log_error("CAN bus off, reset node");
        HAL_CAN_Stop(&hcan1);
        HAL_Delay(100);
        HAL_CAN_Start(&hcan1);
    }
}
```

```text
硬件: 换有问题的 ECU 节点的 CAN 收发器
软件: 加 bus off 自动恢复机制
```

### 复盘

- Bus off 不应让网络瘫, 但错误帧会
- 主动错误帧 = 6 dominant 位, 持续阻塞
- 必须有 bus off 自动恢复 (AutoBusOff)

---

## 案例 2: 终端电阻缺失, 高速通信失败

### 现象

500 kbaud 跑通, 1 Mbaud 失败。错误帧很多。

### 抓波形

示波器看 CAN_H / CAN_L, 边沿有阶梯, 像反射。

### 定位

终端电阻缺失, 高速下信号反射严重。

```text
总线电阻量: 60 ohm 期望, 实际 120 ohm (只有一端)
```

### 修复

补上另一端 120 ohm 终端电阻。

### 复盘

- 总线两端各 120 ohm, 不能少
- 高速 (>500 kbaud) 必须有终端
- 量 A-B 电阻 = 60 ohm 是正确状态

---

## 案例 3: 波特率算错, 一直 error passive

### 现象

代码里设 1 Mbaud, 实际总线速率 800 kbaud。节点一直 error passive。

### 抓波形

量 1 bit 时长 1.25us, 不是 1us (1 Mbaud)。

### 定位

CAN 控制器的 Tq (Time Quantum) 配错, 波特率算错。

```c
/* 错: 36 MHz 时钟, 期望 1 Mbaud */
/* Tq = 9 × (1/36M) = 0.25 us */
/* Bit = 8 Tq = 2 us -> 500 kbaud (不是 1M) */

hcan1.Init.Prescaler = 9;  // 错
hcan1.Init.TimeSeg1 = 6;
hcan1.Init.TimeSeg2 = 1;
```

### 修复

```c
/* 对: 36 MHz, 1 Mbaud */
/* Bit = 8 Tq = 1us -> Tq = 0.125 us */
/* Prescaler = 36M / (1/Tq) = 36M * 0.125u = 4.5 (整数 4 或 5) */
/* 用 4: Tq = 0.111us, Bit = 0.889us, Baud = 1.125M (不精确) */
/* 用 5: Tq = 0.139us, Bit = 1.111us, Baud = 0.9M */
/* 实际: 改成 BS1=3, BS2=1 -> Bit = 5 Tq -> Prescaler = 7.2 (整数 7) */
/*      Tq = 0.194us, Bit = 0.972us, Baud = 1.029M (接近 1M) */

hcan1.Init.Prescaler = 4;
hcan1.Init.TimeSeg1 = 6;
hcan1.Init.TimeSeg2 = 1;
/* 实际: 用 1 + 13 + 2 = 16 Tq, Prescaler = 2 (72M 时钟) */
/*      Tq = 0.0278us, Bit = 0.444us, Baud = 2.25M (不对) */
```

**用工具计算**:
- 多数 MCU 工具 (STM32CubeMX) 自动算波特率
- 手动算: Bit = (1 + BS1 + BS2) × (Prescaler / Fclk)
- 验证: 示波器量 1 bit 时长

### 复盘

- 波特率算错是经典错误
- 任何 CAN 通信先验证波特率
- 用示波器量 1 bit 时长, 反推 baud

---

## 案例 4: 节点数超过 32, 总线负载过重

### 现象

总线上挂 50 个节点, 错误帧率上升, 偶发丢帧。

### 抓波形

总线利用率 80%+, 大量 ACK 应答。

### 定位

多数标准 CAN 收发器 (如 TJA1050) 最多支持 32 个节点。超过 32 时, 总线电阻累积过大, 显性驱动能力不足。

```text
每个节点收发器有输入电阻, 32 个并联 < 几十 ohm
显性驱动 (典型 50 mA) / 节点数 -> 显性电压不够低
```

### 修复

```text
1. 用中继器 (CAN repeater) 分段
2. 升级收发器 (支持更多节点)
3. 用 CAN bridge 把网络拆小
4. 用网关做协议转换
```

### 复盘

- 32 节点是 CAN 收发器的常见上限
- 超过 32 要用中继
- CAN bridge 网关是大型 CAN 网络必备

---

## 案例 5: CAN FD 跑不通, 用经典 CAN 收发器

### 现象

板子用 TJA1050 (经典 CAN 收发器), 想跑 CAN FD 2 Mbaud, 数据段错误率高。

### 抓波形

仲裁段 (1 Mbaud) 正常, 数据段 (2 Mbaud) 边沿畸变, 错误帧。

### 定位

TJA1050 不支持 CAN FD。CAN FD 数据段 > 1 Mbaud 需要支持 CAN FD 的收发器。

### 修复

```c
/* 换收发器: TJA1443, SN65HVD257 等支持 CAN FD */
/* 注意: CAN FD 控制器 + 经典 CAN 收发器 + CAN FD 速率 = 失败 */
/*      CAN 2.0 控制器 + 经典 CAN 收发器 = 正常 (1 Mbaud) */
/*      CAN 2.0 控制器 + CAN FD 收发器 = 正常 (兼容, 1 Mbaud) */
/*      CAN FD 控制器 + CAN FD 收发器 = 正常 (CAN FD 模式) */
```

### 复盘

- CAN FD 收发器向下兼容 CAN 2.0
- CAN 2.0 收发器不能跑 CAN FD 数据段 > 1M
- 数据段速率 > 1M 必须用 CAN FD 收发器

---

## 案例 6: 屏蔽线没接, EMC 失败

### 现象

车间内电机附近, CAN 偶发错误帧, 丢帧率 5%。

### 抓波形

CAN_H / CAN_L 上有 10MHz 噪声叠加。

### 定位

屏蔽双绞线屏蔽层没接地, 电机 PWM 干扰耦合。

### 修复

```text
1. 屏蔽层单点接地 (工业)
   或两端都接 + 中间有去耦电容
2. 远离电机 / 电源走线
3. 加磁环
4. 降速 (1M -> 500k)
```

### 复盘

- 工业 / 汽车环境, EMC 是隐性死因
- 屏蔽层必须正确接地
- 详细见 `i2c-failure-cases.md` EMC 案例

---

## 案例 7: ID 分配冲突, 仲裁时两个节点都失败

### 现象

两个 ECU 用相同的 CAN ID 发数据, 仲裁时两个节点都以为仲裁失败, 同时退出发送, 数据丢失。

### 抓波形

CAN 分析仪看到两个节点同时发, 但都"消失"在总线上, 无帧完成。

### 定位

ID 冲突。CAN 仲裁假设每个 ID 唯一, 冲突时两个节点都会检测到位错误 (发 0 收到 0, 应该一致, 但如果两个都发 0 期望对方也发 0——但实际是隐性问题)。

实际上, 同 ID 不会仲裁失败, 而是一个节点发的帧 vs 另一个节点发的帧, 数据位不同就会被检测到位错误。

### 修复

```c
/* 严格管理 ID 分配 */
/* 用 DBC 文件描述 CAN 网络 */
BO_ 256 ECU1_State: 8 ECU1
 SG_ Speed : 0|16@1+ (0.01,0) [0|655.35] "km/h" Vector__XXX
 SG_ Rpm    : 16|16@1+ (1,0) [0|65535] "rpm" Vector__XXX

BO_ 257 ECU2_State: 8 ECU2
 SG_ ... 

/* 每个 ID 唯一, 写工具检查 */
```

### 复盘

- ID 分配是 CAN 网络的核心工程
- 建议用 DBC 文件统一管理
- 写工具检查 ID 冲突

---

## 案例 8: 接收节点 ID 过滤器没配, 收不到帧

### 现象

ECU1 正常发 0x123 ID 的数据, ECU2 收不到。CAN 分析仪看, 总线上确实有 0x123 帧。

### 抓波形

正常。

### 定位

ECU2 的 CAN 接收过滤器 (filter) 配置错, 0x123 没匹配上, 帧被过滤。

```c
/* 错: 过滤器配错 */
filter.FilterIdHigh = 0x456 << 5;  /* 期望 0x456, 实际收 0x123 */
filter.FilterMaskIdHigh = 0x7FF << 5;
```

### 修复

```c
/* 对: 过滤器配对 0x123 */
filter.FilterIdHigh = 0x123 << 5;  /* 0x123 ID */
filter.FilterMaskIdHigh = 0x7FF << 5;  /* 11 bit ID 全匹配 */
HAL_CAN_ConfigFilter(&hcan2, &filter);
```

### 复盘

- 过滤器错是经典 "收不到" 案例
- 用 CAN 分析仪确认总线有数据, 再查过滤
- 过滤器配好, 用 RX FIFO 而不是硬中断

---

## 案例 9: CAN 控制器进入 bus off, 永远不会自动恢复

### 现象

节点因为某些原因进入 bus off, 然后永远沉默。其他节点继续正常工作, 但这个节点再也没发过帧。

### 抓波形

这个节点发到一半, 然后从总线上消失。

### 定位

软件没启用 AutoBusOff, 节点进 bus off 后没有软件重置。

```c
/* 错: AutoBusOff 关闭 */
hcan1.Init.AutoBusOff = DISABLE;
/* 节点进 bus off 后, 永远沉默 */
```

### 修复

```c
/* 对: AutoBusOff 开启 */
hcan1.Init.AutoBusOff = ENABLE;
/* 节点进 bus off 后, 自动停止, 然后等 128 次 11 recessive 位, 自动重连 */

/* 或者: 软件监控 + 手动重连 */
void can_check_bus_off() {
    if (hcan1.Instance->ESR & CAN_ESR_BOFF) {
        HAL_CAN_Stop(&hcan1);
        HAL_Delay(100);
        HAL_CAN_Start(&hcan1);
    }
}
```

### 复盘

- 产线必须能 "自动恢复"
- AutoBusOff 开启, 或软件监控 + 手动重连
- 关键应用: 看门狗 + bus off 双重保护

---

## 案例 10: 收发器供电不稳, 偶发错误

### 现象

电源纹波大, CAN 偶发错误帧, 和电源耦合。

### 抓波形

错误帧时刻, VCC 有尖峰。

### 定位

收发器 VCC 没加足够去耦, 或电源本身纹波大。

```c
/* 错: 收发器 VCC 只加 100nF */
VCC -> 收发器 VCC
       100nF
       GND
```

### 修复

```text
VCC -> 收发器 VCC
       100nF (高频)
       10uF  (低频)
       GND

* 100nF 放最靠近 VCC 引脚
* 10uF 放 VCC 总入口
```

### 复盘

- 收发器供电是隐性死因
- 必须有高频 + 低频双重去耦
- 详细见 `i2c-failure-cases.md` 电源案例

---

## 案例 11: 多 master 仲裁失败, 数据丢

### 现象

两个节点几乎同时发, 仲裁失败的节点的数据丢失。

### 抓波形

CAN 分析仪看, 一个节点发了一半后停止 (仲裁失败), 另一个节点继续发。

### 定位

**这是正常 CAN 行为**, 不是 bug。CAN 仲裁是"非破坏性", 失败的节点会自动重试, 应用层不应该看到丢数据。

但如果应用层看到丢数据, 可能是:
- 节点没启用自动重传
- 失败节点没检查发送状态

### 修复

```c
/* 对: 启用自动重传 */
hcan1.Init.AutoRetransmission = ENABLE;

/* 对: 检查发送状态 */
HAL_CAN_AddTxMessage(&hcan1, &header, data, &mailbox);
HAL_CAN_GetTxMailboxesFreeLevel(&hcan1);  // 0 = 满了, 失败
```

### 复盘

- 仲裁失败不是 bug, 是 CAN 设计
- 自动重传必须开
- 详细见 `can-multimaster-and-bus-off.md`

---

## 案例 12: CAN 收发器引脚接错, 收发方向反

### 现象

板子发不出数据, 但能收到数据 (反之亦然)。

### 抓波形

正常时: MCU TX -> 收发器 TXD
错时: MCU TX -> 收发器 RXD (接反了)

### 定位

硬件接线错。TX 接 RX, RX 接 TX (类似 UART)。

### 修复

查 datasheet, 改接线。

### 复盘

- MCU CAN TX -> 收发器 TXD
- MCU CAN RX -> 收发器 RXD
- TXD/RXD 收发器内部是输入, 容易搞混

---

## 案例 13: 总线短路, 所有节点都收不到

### 现象

多个节点同时报告 "无 ACK", 总线 0 数据流。

### 抓波形

CAN_H = CAN_L = 0V, 总线被强拉到低。

### 定位

总线短路 (CAN_H 和 CAN_L 之间, 或 CAN_H 和 GND 之间)。

### 修复

```text
1. 量 A-B 电阻: 期望 60 ohm, 实际 0 ohm -> 短路
2. 断开所有节点, 逐个接回, 定位故障段
3. 查硬件: 焊接短路 / 连接器短路 / 收发器坏
```

### 复盘

- 总线短路是产线常见物理故障
- 必须能快速定位故障段
- 详细见 `i2c-failure-cases.md` 短路案例

---

## 案例 14: OBD 诊断接口响应慢

### 现象

诊断工具 (OBD) 读 ECU 数据, 响应慢, 偶尔超时。

### 抓波形

ECU 收到请求到发出响应之间有 100ms 延迟。

### 定位

ECU 优先级处理不当, 高优先级报文 (动力总成) 阻塞了诊断响应。

```c
/* 错: 所有报文用同一 FIFO */
hcan1.Init.TransmitFifoPriority = DISABLE;
```

### 修复

```c
/* 对: 诊断响应走专用 mailbox, 优先级高 */
/* 或者: 用专门 mailbox 发送, 不用 FIFO */

/* 或者: 软件调度, 周期性报文让位给诊断请求 */
```

### 复盘

- 多 master 仲裁 + 应用层调度 = 关键
- OBD 诊断有 ISO 14229 标准, 响应时间要求
- 详细见 `uds-*.md`

---

## 案例 15: 老化工 CAN 通信失败

### 现象

新板 100% pass, 1000 小时老化后, 5% CAN 通信失败。

### 抓波形

错误帧率上升, 偶发丢帧。

### 定位

焊点疲劳, 收发器 / 终端电阻接触不良。

### 修复

```text
1. 硬件: 改焊盘设计, 加 underfill
2. 老化测试必须做
3. 监控 CAN 错误计数器, 老化后统计
```

### 复盘

- 老化测试是产线良率的保证
- CAN 收发器对焊点质量敏感
- 错误计数器是老化测试的客观指标

---

## 案例 16: 远程帧被错误使用

### 现象

节点用远程帧请求数据, 偶尔没响应。

### 抓波形

远程帧发出, 但没节点响应。

### 定位

CAN 2.0B 的远程帧已被 CAN FD 废弃, 多数现代设备不支持。远程帧不可靠。

### 修复

```text
不用远程帧
用普通数据帧 + 应用层协议 (master 发请求, slave 监听后发数据)
```

### 复盘

- 远程帧 = 老协议, 现代 CAN 不用
- 永远用数据帧 + 应用层协议

---

## 案例 17: 不同厂商收发器混合, 故障保护不一致

### 现象

A 节点用 TJA1050 (故障保护 ±60V), B 节点用 TJA1042 (故障保护 ±58V), 整体故障保护取决于最弱者。

### 抓波形

正常。

### 定位

不同厂商收发器故障保护能力不同, 混用时整体能力取决于最弱者。

### 修复

```text
1. 选统一型号收发器
2. 或确认所有收发器故障保护 >= 系统要求
3. 工业级: 选 ±70V 保护型号
```

### 复盘

- 收发器选型是系统工程
- 故障保护能力必须统一
- 详细见收发器选型表

---

## 案例 18: 节点上电顺序错, 总线初期错乱

### 现象

系统上电后 100ms 内 CAN 错误帧多, 然后稳定。

### 抓波形

错误帧集中在上电初期。

### 定位

部分节点上电慢, 总线启动时其他节点未就绪。

### 修复

```text
1. 关键节点优先上电 (e.g. ECU)
2. 加 startup delay, 节点启动后等 100ms 再 enable CAN
3. 错误计数器监控, 启动期间忽略
```

### 复盘

- 上电时序是产线死机常见根因
- 详细见 `i2c-failure-cases.md` 上电时序案例

---

## 案例 19: 收发器 EN / STB 引脚未配置

### 现象

收发器一直处于 standby 模式, 收发数据错误。

### 抓波形

收发器输出不稳定。

### 定位

收发器的 EN (enable) 或 STB (standby) 引脚没配, 默认 standby。

```c
/* 错: 没配 EN 引脚 */
HAL_GPIO_WritePin(CAN_STB_PORT, CAN_STB_PIN, GPIO_PIN_RESET);  // STB = 0 = standby
```

### 修复

```c
/* 对: EN = high, STB = low (正常运行模式) */
HAL_GPIO_WritePin(CAN_EN_PORT, CAN_EN_PIN, GPIO_PIN_SET);
HAL_GPIO_WritePin(CAN_STB_PORT, CAN_STB_PIN, GPIO_PIN_RESET);
```

### 复盘

- 收发器的 mode 引脚必须显式配
- standby / sleep 模式是节能设计, 但要主动唤醒

---

## 案例 20: 跨地电位差, 长距离通信失败

### 现象

板 A 和板 B 通过长线连接, 板 B 是远端传感器, CAN 通信失败。

### 抓波形

CAN_H / CAN_L 在板 A 和板 B 看到的电平不一致, 差分电压被地电位差抵消。

### 定位

A 和 B GND 不等, 长距离通信有地电位差。

### 修复

```text
1. 用隔离 CAN 收发器 (如 ISO1050, ADM3053)
2. A 和 B 之间用隔离电源
3. 单点接地, GND 走线粗
```

### 复盘

- 长距离 / 工业场景, 隔离是必须的
- 详细见 `i2c-failure-cases.md` GND 电位差案例

---

## 案例汇总: 产线 CAN 死机根因分布

```text
终端电阻错                20%
波特率算错                15%
节点 bus off               12%
CAN FD 兼容问题            10%
EMC / 干扰                 10%
收发器硬件 / 供电           8%
ID 分配 / 过滤器           7%
多 master 仲裁 / 调度       5%
总线短路 / 接线            5%
其他                       8%
```

终端 + 波特率 + bus off 三类加起来近 50%, 是产线 CAN 死机的主要根因区。

## 产线 CAN 根因预防清单

```text
□ 总线两端各 120 ohm 终端电阻
□ 波特率精确 (示波器量验证)
□ AutoBusOff 开启
□ AutoRetransmission 开启
□ 错误计数器监控和上报
□ 收发器供电有高频 + 低频去耦
□ EMC 屏蔽和接地
□ ID 分配用 DBC 文件管理
□ 接收过滤器严格配置
□ 收发器 mode 引脚显式配置
□ 节点数 <= 32 (标准收发器)
□ CAN FD 收发器型号确认
□ 隔离收发器 (工业 / 长距离)
□ 老化测试 1000+ 小时
□ 产线 fault injection (短路, 终端断, 收发器拔)
```

## 关联文档

- `can-deep-dive.md` 原理 + 故障树
- `can-practical.md` 速查
- `can-multimaster-and-bus-off.md` 多 master + bus off
- `can-fd-and-can-xl.md` 演进
- `can-rtos-integration.md` RTOS + SocketCAN
- `can-vs-other-bus.md` 跨总线对比
- `can-index.md` 导航
- `bus/can-canopen-deep-dive.md` CANopen
- `bus/uds-*.md` UDS (诊断)
- `bus/j1939-*.md` J1939 (商用车)
