# I2C Deep Dive

## 目标

本文深入 I2C 工程细节，重点解决上拉电阻、总线电容、地址混淆、Repeated START、Clock Stretching、总线恢复、I2C MUX、EEPROM/传感器/PMIC 特性和现场排障。

## I2C 的工程定位

I2C 适合板内低速管理类通信：

- 传感器配置和读取。
- EEPROM/RTC。
- PMIC 和电源监控。
- 触摸控制器。
- 小型外设寄存器访问。

I2C 不适合：

- 长距离线缆。
- 强干扰工业现场。
- 高速连续大数据。
- 大量设备高频轮询。

工程直觉：

```text
I2C 是板内管理总线，不是通用远距离通信总线。
```

## 开漏结构为什么重要

I2C 的 `SCL` 和 `SDA` 通常是开漏或开集结构。

设备只能：

```text
主动拉低 = 0
释放总线 = 1，由上拉电阻拉高
```

这个特性支持：

- 多设备共享总线。
- ACK/NACK。
- 仲裁。
- Clock Stretching。
- 避免多个设备推挽硬冲突。

代价是：

```text
上升沿由 RC 决定，速度和总线电容强相关。
```

## 上拉电阻选择

常见取值：

| 场景 | 常见取值 |
| --- | --- |
| 100 kHz，短线，少设备 | 4.7k 或 10k |
| 400 kHz，普通板内 | 2.2k 或 4.7k |
| 1 MHz，电容较大 | 1k 到 2.2k |
| 长线或多设备 | 需要计算和实测 |

上拉太大：

- 上升沿慢。
- 高速通信失败。
- 偶发 NACK。
- 波形像斜坡。

上拉太小：

- 拉低电流过大。
- 功耗增加。
- 低电平可能不够低。
- 设备驱动压力增加。

## 总线电容

总线电容来自：

- PCB 走线。
- 芯片引脚。
- 连接器。
- 线缆。
- 电平转换器。
- 逻辑分析仪和示波器探头。

I2C 高速失败时，不要只看软件配置。重点看：

```text
上拉电阻 × 总线电容
```

总线越重，上升沿越慢。

## 速度调试策略

推荐顺序：

```text
100 kHz 跑通功能
400 kHz 验证稳定
1 MHz 或更高只在硬件允许时使用
```

如果 400 kHz 不稳定但 100 kHz 稳定，优先怀疑：

- 上拉太弱。
- 总线电容太大。
- 电平转换器太慢。
- 飞线或连接器影响。
- 波形上升沿不满足要求。

## 7-bit 地址和 8-bit 地址

I2C 标准常用 7-bit 地址。

例如设备地址：

```text
0x68
```

线上发送时会变成：

```text
写：0xD0
读：0xD1
```

因为：

```text
0x68 << 1 = 0xD0
0xD0 | 1 = 0xD1
```

很多驱动 API 要求传 7-bit 地址：

```c
i2c_read(0x68, reg, buf, len);
```

不要误传：

```c
i2c_read(0xD0, reg, buf, len);
```

除非驱动明确要求 8-bit 地址。

## ACK/NACK 定位

I2C 每 8 bit 后有 1 bit 应答。

```text
ACK = 0
NACK = 1
```

地址阶段 NACK，优先检查：

- 地址是否正确。
- 设备是否上电。
- RESET/PWDN 是否释放。
- 上拉是否存在。
- 电平域是否匹配。
- 设备是否处于睡眠或忙状态。

数据阶段 NACK，优先检查：

- 寄存器地址是否存在。
- 命令格式是否正确。
- 写保护是否开启。
- 设备内部是否忙。
- 是否需要延时或状态轮询。

## Repeated START

寄存器读常见流程：

```text
START
Address + Write
Register Address
Repeated START
Address + Read
Data
NACK
STOP
```

不要默认改成：

```text
START -> Write Register -> STOP -> START -> Read
```

某些设备把 `STOP` 视为事务结束，会清除内部状态或改变寄存器指针。

驱动应提供：

```text
write_then_read with repeated start
```

## Clock Stretching

Clock Stretching 是从设备拉低 `SCL`，让主控等待。

用途：

- 从设备还没准备好数据。
- 内部转换未完成。
- 低速设备需要更多处理时间。

风险：

- 某些主控不支持或支持有限。
- 软件模拟 I2C 容易漏处理。
- Linux/RTOS 驱动可能有超时限制。

如果目标器件手册要求 Clock Stretching，必须确认控制器支持。

## 总线被拉死

常见现象：

```text
SDA 一直为低
SCL 一直为低
I2C 控制器一直 BUSY
while(wait_ack) 永久阻塞
```

可能原因：

- 主控复位发生在传输中间。
- 从设备状态机停在等待时钟阶段。
- 从设备异常掉电。
- 电源时序不一致：主机已复位，从设备仍带电。
- 驱动被高优先级任务抢断，状态机错位。
- ESD/干扰导致状态错乱。
- 硬件短路。
- 从设备固件 bug，内部状态机卡死。

### 先区分：超时和总线恢复不是一回事

- **超时** 解决软件控制流：给 `while` 加 deadline，线程不再永久卡死。
- **总线恢复** 解决物理总线状态：把 SDA/SCL 真正拉回 IDLE。

工程上必须分四层处理：

| 层级 | 解决问题 | 关键动作 |
| --- | --- | --- |
| L1 事务超时 | 软件控制流 | 等待点加 deadline，返回明确 errno |
| L2 GPIO 总线恢复 | 物理总线状态 | 9~16 个 SCL 脉冲 + STOP |
| L3 控制器复位 | 外设状态机 | deinit / init，清 BUSY/BERR/ARLO |
| L4 从设备兜底 | 设备挂死 | reset GPIO / load switch / mux 隔离 |

只加 L1 等于"每次都超时，设备还是不可用"。面试里答出这四层是核心得分点。

### 死锁时序

```text
主机 I2C                 SCL/SDA                  从设备
   |                         |                       |
   |---START + ADDR + R------>|                       |
   |                         |---ACK(拉低 SDA)------>|
   |                         |<----数据 bit 0---------|
   |  (主机异常复位/跳出)     |                       |
   |                         |    SDA 仍被拉低        |
   |                         |    从设备等下一拍 SCL  |
   |<--再 init I2C 读 BUSY--->|                       |
   |                         |    SDA 仍低，BUSY=1    |
```

主机硬件 I2C 看到 SDA=0 判 BUSY，不再发 SCL；从设备停在 bit/ACK 状态等 SCL —— **互等死锁**。

### 8 步恢复 SOP

把恢复流程实现为总线级函数 `i2c_bus_recover()`，由 adapter 层在发现异常后调用。**不要散落在每个 client driver**。

```text
1. 拿 bus mutex            -> 状态切 RECOVERING
                              新事务返 -EBUSY / -EAGAIN / 有限重试
2. 退出 I2C 外设           -> 关中断、停 DMA、外设 reset
                              清 busy/msg/error，清 pending 中断
3. pinmux -> GPIO OD       -> 切开漏！禁止推挽强拉高
4. 采样真实电平            -> 读 IDR，不是 ODR
                              SCL/SDA 分别判断
5. 9~16 个 SCL 脉冲        -> 每高电平采样 SDA，提前 break
                              上限固定，禁止无限
6. 手动 STOP               -> drive_low(SDA)
                              release(SCL) 等高
                              release(SDA)
7. 复位 I2C 外设           -> 清 BUSY/BERR/ARLO/NACK/DMA
                              重新 init，adapter 切回 IDLE
8. 失败兜底                -> reset GPIO / load switch / mux 隔离
                              上报故障，禁止无限重试
```

### 为什么是 9 个 SCL 脉冲

一次字节传输 = 8 数据位 + 1 ACK/NACK。卡在字节内任意位置 → 9 个边沿推进到字节边界 → NACK/STOP 退出。

工程经验值：

- 规范最小值：`max_pulses = 9`
- 工程上限：`max_pulses = 16` 或 `18`（多字节读中断、内部 FIFO 异常可能需要更多）
- **必须设上限**，不能无限打

更稳妥的做法是每个高电平阶段都采样 SDA，一旦 SDA 释放为高立即 break，转入 STOP 生成。

### 8 步对应代码骨架

```c
/* 简化的可移植伪代码，仅展示结构与状态机，不绑定具体 MCU */

#define I2C_RECOVERY_MAX_PULSES     16U
#define I2C_RECOVERY_T_HIGH_US      10U
#define I2C_RECOVERY_T_LOW_US       10U
#define I2C_RECOVERY_BUS_FREE_US    10U

typedef struct {
    bool scl_high;   /* 物理 SCL 真实电平 */
    bool sda_high;   /* 物理 SDA 真实电平 */
} i2c_line_state_t;

typedef struct {
    int  (*prepare)(void *ctx);          /* 关 I2C 中断/DMA/外设 */
    int  (*unprepare)(void *ctx);        /* 恢复 pinmux + 重新 init 控制器 */
    int  (*gpio_od_init)(void *ctx);     /* SCL/SDA 切 GPIO 开漏 */
    void (*release_scl)(void *ctx);
    void (*drive_scl_low)(void *ctx);
    void (*release_sda)(void *ctx);
    void (*drive_sda_low)(void *ctx);
    bool (*read_scl)(void *ctx);         /* 读 pin input，不能读 ODR */
    bool (*read_sda)(void *ctx);
    void (*delay_us)(void *ctx, uint32_t us);
    int  (*reset_target)(void *ctx);     /* 可选：reset GPIO / load switch */
} i2c_recovery_ops_t;

int i2c_bus_recover(const i2c_recovery_ops_t *ops, void *ctx)
{
    int ret;

    if (!ops || !ops->prepare || !ops->unprepare || !ops->gpio_od_init ||
        !ops->release_scl || !ops->drive_scl_low ||
        !ops->release_sda || !ops->drive_sda_low ||
        !ops->read_scl    || !ops->read_sda    || !ops->delay_us) {
        return -EINVAL;
    }

    /* step 2: 退出 I2C 外设 */
    ret = ops->prepare(ctx);
    if (ret != 0) return ret;

    /* step 3: 切 GPIO 开漏 */
    ret = ops->gpio_od_init(ctx);
    if (ret != 0) { (void)ops->unprepare(ctx); return ret; }

    ops->release_scl(ctx);
    ops->release_sda(ctx);
    ops->delay_us(ctx, I2C_RECOVERY_T_HIGH_US);

    /* step 4: SCL 必须能回高，否则 SDA 恢复没有意义 */
    if (!wait_scl_high(ops, ctx)) {
        ret = -EBUSY; goto fallback;
    }

    /* step 5: SDA 仍低就打脉冲，每高电平采样一次 */
    if (!ops->read_sda(ctx)) {
        for (uint32_t i = 0; i < I2C_RECOVERY_MAX_PULSES; i++) {
            ops->drive_scl_low(ctx);
            ops->delay_us(ctx, I2C_RECOVERY_T_LOW_US);
            ops->release_scl(ctx);
            if (!wait_scl_high(ops, ctx)) { ret = -EBUSY; goto fallback; }
            ops->delay_us(ctx, I2C_RECOVERY_T_HIGH_US);
            if (ops->read_sda(ctx)) break;   /* SDA 释放，提前退出 */
        }
    }

    /* step 6: 生成 STOP — SCL 高时 SDA 产生低到高跳变 */
    if (generate_stop(ops, ctx) != 0) { ret = -EBUSY; goto fallback; }

    /* step 7: 复位 I2C 外设并恢复复用 */
    return ops->unprepare(ctx);

fallback:
    if (ops->reset_target) (void)ops->reset_target(ctx);
    (void)ops->unprepare(ctx);
    return ret;
}
```

### 恢复状态机

不要写成几个散乱的 `goto`。建议显式建模：

```text
Normal
  -> (timeout/BUSY/SDA_low 检测) -> RecoveryPrepare
  -> (关中断/DMA/外设)          -> GpioMode
  -> (pinmux -> GPIO OD)        -> CheckLines
       SCL=1, SDA=1   -> StopOnly
       SCL=1, SDA=0   -> ClockRecovery
       SCL=0 timeout  -> SlaveReset
  -> (SDA 释放 / 脉冲上限到)    -> generate STOP
  -> (复位 I2C + 恢复 AF)       -> ControllerReset
       成功              -> VerifyIdle -> Normal
       仍 BUSY / line低 -> Failed
                              -> reset_target / 上报 / 降级
```

每个状态都要有**进入条件、退出条件、超时、日志字段**。

### 必带的可观测字段

```text
bus_id            i2c0 / i2c1
last_addr         最近一次访问的从设备地址
last_op           read/write/write-read/register-read
last_reg          若是寄存器访问
timeout_stage     BUSY / ADDR / ACK / TXE / RXNE / STOP / DMA
scl_level         恢复前后真实电平
sda_level         恢复前后真实电平
pulse_count       实际打了多少个 SCL
recover_result    success / scl_stuck / sda_stuck / ctrl_reset_fail
retry_count       本设备/本事务的重试次数
```

产线最怕"恢复了但没证据"。日志必须能统计和被测试系统读取。

### 7 条常见错误实现

| # | 错误 | 后果 |
| --- | --- | --- |
| 1 | 只加超时，不恢复总线 | 每次访问都超时，设备功能仍不可用 |
| 2 | 推挽强拉 SDA/SCL | 与从设备拉低形成电气冲突，可能烧 IO |
| 3 | 只打 9 个 SCL 不生成 STOP | 从设备内部状态未重置 |
| 4 | 恢复后不复位 I2C 外设 | BUSY/BERR/ARLO 仍卡 |
| 5 | 读 ODR 而非 IDR | 误判总线真实电平 |
| 6 | 无限恢复 / 无限重试 | 拖垮系统；每个事务最多 1 次，每个设备窗口内有限次 |
| 7 | 业务驱动里各自写恢复 | 并发冲突；恢复必须在 bus/adapter 层统一管理 |

### 与规范 / 开源机制的对应

| 机制 | 出处 | 价值 |
| --- | --- | --- |
| SDA stuck -> 9 个 SCL | NXP UM10204 Bus clear | 规范级原则，所有平台都应参考 |
| bus_recovery_info hooks | Linux I2C core | adapter 抽象：get/set_scl/sda 适配点 |
| i2c_recover API | Zephyr | RTOS 同样应把恢复放总线层 |
| GPIO fault injection | Linux 6.x | 产线测例设计依据 |
| errno 语义 | Linux fault codes | NACK/timeout/ARLO/EBUSY 要分开返回 |

### 工程分层原则

```text
Application  -> 感知设备不可用、决定降级策略
Client Driver-> 协议语义 + 幂等性标注 + reinit()
Bus Layer    -> mutex / 状态机 / recovery / 控制器 reset / 统一日志
Board        -> 拓扑、reset GPIO、load switch、mux、device tree
```

**金句**：恢复动作只能放在 Bus 层。Client 层只标"我这个事务能不能重试"，不直接动 GPIO。

### SCL 被拉低怎么办

SCL 低可能是合法 Clock Stretching，也可能是从设备挂死或总线短路。SCL 不回高，SDA 恢复脉冲无法形成有效边沿。

处理顺序：

1. 释放 SCL，等待有限时间。
2. SCL 能回高 → 进入 SDA stuck recovery。
3. SCL 长期低 → 查设备 datasheet 是否允许长时间 stretching；不允许就视为异常。
4. 不要再 bit-bang（低电平阶段无上升沿）。
5. 复位从设备、电源域或 mux 分支。
6. 仍失败 → 记录硬件故障，禁止访问该总线。

很多驱动只检测 SDA 不检测 SCL，结果"恢复代码"实际没产生任何有效时钟，误报成功。

### 与 SMBus 的区别

SMBus 设备对 clock low timeout 有要求，SCL 长期低时设备可能**自行复位**通信状态。普通 I2C 设备不一定有这机制。混用 I2C 和 SMBus 时，恢复策略按最严格设备要求设。

### 与产线/低功耗的协同

- **系统启动时**：先做 bus idle check，再 init I2C 控制器。
- **进入低功耗前**：确保无在途事务；不能从设备正在 ACK 时直接关 I2C。
- **退出低功耗后**：重新采样 SCL/SDA，必要时再恢复。
- **主从 reset 域不同步**：关键从设备的 reset 应接到 MCU 可控 GPIO，否则只能恢复一部分情况。

### 故障恢复策略矩阵

| 错误类型 | 线电平 | 首选动作 | 兜底 |
| --- | --- | --- | --- |
| NACK | SCL=1, SDA=1 | 有限重试 | 检查电源和初始化顺序 |
| BUSY timeout | SDA=0 或 SCL=0 | bus recovery | controller reset / target reset |
| ACK wait timeout | 常见 SDA=0 | STOP + recovery | target reset |
| RX timeout | 可能 SCL stretching | 检查 SCL，必要时 STOP | target reset |
| STOP timeout | 控制器状态异常 | GPIO STOP + controller reset | bus recovery |
| ARLO | 多主机 | 退避重试 | 多主机仲裁设计 |
| Bus error | 时序异常 | 清错误并恢复 | 硬件波形检查 |

### 产线验证

不要只靠"跑一天没复现"。设计可重复故障注入测试：

| 用例 | 注入方式 | 期望 |
| --- | --- | --- |
| SDA 强制拉低 | 夹具 MOSFET 拉低 SDA | 驱动超时不死循环；释放后 recovery 成功 |
| SDA 在 ACK 周期拉低 | 逻辑分析仪触发或从设备模拟器 | 主机输出 SCL 脉冲并生成 STOP |
| SCL 强制拉低 | 夹具拉低 SCL | 识别 SCL stuck，不误报成功 |
| 主机事务中复位 | 读事务中 reset MCU | 启动阶段 bus idle check 能恢复 |
| 从设备掉电/上电抖动 | 单独控制从设备电源 | 软件能复位/隔离，不影响主循环 |
| 多线程并发 | 多任务同时访问不同 client | bus lock 有效，恢复期无并发 |
| 长时间老化 | 连续读写加随机 reset | 错误计数稳定，恢复成功率可统计 |

### 代码审查 / 产线验收清单

- [ ] 所有 `while` 等待 ACK/BUSY/TX/RX/STOP 都有 timeout
- [ ] timeout 用时间基准，不用裸循环计数
- [ ] bus recovery 在 bus mutex 下执行
- [ ] 恢复前关闭 I2C 中断和 DMA
- [ ] SCL/SDA 切 GPIO open-drain，不推挽强拉高
- [ ] 读 pin input（IDR），不读 ODR
- [ ] SCL stuck 和 SDA stuck 分开处理
- [ ] SCL 脉冲有上限 + 每高电平采样 SDA + 提前 break
- [ ] SDA 释放后生成 STOP
- [ ] 恢复后复位或重新 init I2C 控制器
- [ ] 恢复失败有 target reset + 错误上报
- [ ] 自动重试有限次 + 考虑事务幂等性
- [ ] 日志含 bus / addr / stage / line level / result
- [ ] 产线有 SDA/SCL fault injection 测例

## 总线被拉死：故障树

把 SDA/SCL 异常的所有可能根因画成一张决策树，从现场现象一路推到具体验证手段。

```text
现象: 通信失败
  |
  +-- 抓波形判断线电平
        |
        +-- SCL=1, SDA=1, 但 NACK
        |     -> 地址错/设备没上电/写保护/设备忙/电平域不对
        |     -> 验证: 示波器量从设备 VCC、reset、地址扫描
        |
        +-- SCL=1, SDA=0 (典型死锁)
        |     -> 从设备卡在 bit/ACK 状态
        |     -> 进入 bus recovery
        |     -> 验证: GPIO 切开漏 + 9~16 SCL + STOP
        |     |
        |     +-- recovery 成功 -> 恢复后复位 I2C 外设 + reinit
        |     +-- recovery 失败:
        |           +-- 9 个脉冲后 SDA 仍低
        |           |     -> 可能是多字节卡死 -> 试 16/18 脉冲
        |           +-- SCL 一直低
        |           |     -> Clock stretching 超规格 / 硬件短路 / 电源异常
        |           |     -> 验证: 测从设备 VCC 时序、量对地电阻、查 EMC
        |           +-- 仍异常
        |                 -> 走 L4 兜底: reset GPIO / load switch / mux 隔离
        |                 -> 上报硬件故障 + 降级
        |
        +-- SCL=0 (stretching 或卡死)
        |     -> 先判断是合法 stretching 还是硬件异常
        |     -> 等一个 stretching timeout
        |     -> 仍低 -> 检查电源/短路/EMC
        |     -> 复位从设备
        |
        +-- I2C 控制器一直 BUSY
              -> 多半是上面 SDA/SCL 低传导过来
              -> 必走 bus recovery
              -> 恢复后必须 controller reset 清 BUSY 位
```

### 故障树对应的快速判定

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 偶发 NACK, SCL=1, SDA=1 | 协议错误, 非物理死锁 | 检查地址/电源/上拉 |
| 持续 NACK, 同一地址 | 设备没上电或挂了 | 量 VCC/reset, 必要时切 MUX 通道 |
| while 等 ACK 永久阻塞 | 驱动没加 timeout | 先加 timeout |
| while 退出但下次仍失败 | SDA 物理卡死 | bus recovery |
| recovery 失败 SCL=0 | stretching 异常或硬件 | 查从设备时序 + 量电气 |
| 同一 bus 偶发多设备失败 | 上拉过弱 / 总线电容大 | 算 RC, 降速, 减设备 |
| 掉电/上电后立刻失败 | 上下电时序错 | bus idle check + 从设备 reset |
| 多线程同时访问 | 并发竞争 | 强制 bus mutex, 恢复期 -EBUSY |

---

## STM32 实战序列

把通用 SOP 落到 STM32 HAL / LL 上。STM32 不同代际（F1/F4/F7/H7/H5）的 I2C IP 有差异，但工程动作一致。

### 1. 关 I2C 外设

```c
/* HAL 版 */
HAL_I2C_DeInit(&hi2c1);
__HAL_I2C_DISABLE(&hi2c1);
HAL_NVIC_DisableIRQ(I2C1_EV_IRQn);
HAL_NVIC_DisableIRQ(I2C1_ER_IRQn);
/* 如果用 DMA, 这里也要停 */
HAL_DMA_Abort(hi2c1.hdmatx);
HAL_DMA_Abort(hi2c1.hdmarx);
hi2c1.hdmatx->State = HAL_DMA_STATE_READY;
hi2c1.hdmarx->State = HAL_DMA_STATE_READY;
hi2c1.State = HAL_I2C_STATE_READY;
hi2c1.ErrorCode = HAL_I2C_ERROR_NONE;
```

```c
/* LL 版 */
LL_I2C_Disable(I2C1);
LL_I2C_DisableDMAReq_RX(I2C1);
LL_I2C_DisableDMAReq_TX(I2C1);
NVIC_DisableIRQ(I2C1_EV_IRQn);
NVIC_DisableIRQ(I2C1_ER_IRQn);
/* 清 pending */
WRITE_REG(I2C1->ICR, 0xFFFFFFFFU);
```

### 2. RCC 外设 reset

```c
/* 关键: 很多 STM32 I2C errata 说"只有 RCC reset 才能彻底清 BUSY 位" */
__HAL_RCC_I2C1_FORCE_RESET();
__HAL_RCC_I2C1_RELEASE_RESET();
/* 或者 */
LL_APB1_GRP1_ForceReset(LL_APB1_GRP1_PERIPH_I2C1);
LL_APB1_GRP1_ReleaseReset(LL_APB1_GRP1_PERIPH_I2C1);
```

### 3. Pinmux 切 GPIO 开漏

```c
/* GPIO 配开漏输出 */
GPIO_InitTypeDef gpio = {0};
gpio.Pin = GPIO_PIN_6 | GPIO_PIN_7;          /* SCL=PB6, SDA=PB7 */
gpio.Mode = GPIO_MODE_OUTPUT_OD;
gpio.Pull = GPIO_NOPULL;                      /* 外部上拉 */
gpio.Speed = GPIO_SPEED_FREQ_LOW;             /* recovery 不追高速 */
HAL_GPIO_Init(GPIOB, &gpio);

/* 释放 = 写 1 */
HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_SET);
HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_SET);
```

```c
/* 读真实电平, 用 IDR 不是 ODR */
static inline bool sda_is_high(void) {
    return (GPIOB->IDR & GPIO_PIN_7) != 0;
}
static inline bool scl_is_high(void) {
    return (GPIOB->IDR & GPIO_PIN_6) != 0;
}
```

### 4. 9 个 SCL 脉冲

```c
#define I2C_RECOVERY_MAX_PULSES  16U
#define I2C_RECOVERY_T_LOW_US   10U
#define I2C_RECOVERY_T_HIGH_US  10U

static void delay_us(uint32_t us) {
    /* 用 DWT 或硬件 timer, 不要裸循环 */
    volatile uint32_t cnt = us * (SystemCoreClock / 1000000U / 5U);
    while (cnt--);
}

static int i2c_stm32_pulse_recovery(void) {
    for (uint32_t i = 0; i < I2C_RECOVERY_MAX_PULSES; i++) {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_RESET);  /* SCL low */
        delay_us(I2C_RECOVERY_T_LOW_US);

        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_SET);    /* SCL release */
        delay_us(I2C_RECOVERY_T_HIGH_US);

        if (sda_is_high()) return 0;   /* SDA 释放, 提前退出 */
    }
    return -EBUSY;  /* 16 个后仍低 */
}
```

### 5. 生成 STOP

```c
static int i2c_stm32_generate_stop(void) {
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_RESET);  /* SDA low */
    delay_us(I2C_RECOVERY_T_LOW_US);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_SET);    /* SCL release */
    delay_us(I2C_RECOVERY_T_HIGH_US);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_SET);    /* SDA release */
    delay_us(I2C_RECOVERY_T_LOW_US);
    return sda_is_high() ? 0 : -EBUSY;
}
```

### 6. 恢复 pinmux 和 I2C 控制器

```c
/* 切回 AF_OD */
gpio.Mode = GPIO_MODE_AF_OD;
gpio.Pull = GPIO_NOPULL;
gpio.Alternate = GPIO_AF4_I2C1;
HAL_GPIO_Init(GPIOB, &gpio);

/* RCC reset 后重新 init */
__HAL_RCC_I2C1_FORCE_RESET();
__HAL_RCC_I2C1_RELEASE_RESET();

if (HAL_I2C_Init(&hi2c1) != HAL_OK) {
    return -EIO;
}
/* 重新配 timing/filter/DMA */
```

### 7. STM32 特有的坑

| 坑 | 说明 |
| --- | --- |
| F1/F2/F4 老款 I2C errata | BUSY 位异常不清，必须 RCC reset |
| F7/H7 多主机 | 必须确认总线所有权 |
| H5/U5 新 IP | 寄存器布局不同，按 Reference Manual |
| HAL 库的 ErrorCode 累加 | 恢复前要清零, 否则下次 HAL_I2C_Master_xx 会立刻返 HAL_ERROR |
| NVIC pending | 关 NVIC 后清 pending bit, 否则恢复完立刻进 ISR |

---

## 多平台差异表

不同 MCU 的 pinmux / 复位 / GPIO 释放语义差异很大, 恢复代码必须写平台适配层, 不能硬编码到通用逻辑里。

| 平台 | pinmux API | 释放 SDA/SCL | reset 控制器 | 关键 errata |
| --- | --- | --- | --- | --- |
| STM32 F/H/L | HAL_GPIO / LL_GPIO | `HAL_GPIO_WritePin(PORT, PIN, SET)` (开漏模式下 = 释放) | `__HAL_RCC_I2Cx_FORCE_RESET` | F1/F2/F4 老款 BUSY 位异常 |
| NXP LPC / i.MX RT | IOCON / FLEXCOMM | `GPIO_PinWrite(GPIO, PORT, PIN, 1)` (开漏) | `SYSCON->PRESETCTRL` 清位再置位 | 多主机必须先验总线所有权 |
| NXP Kinetis | PORT / FGPIO | `FGPIO_PinSet` 或写 PDOR 1 | `SIM->SCGC` 先关再开时钟 | 部分型号无独立 reset, 靠 disable |
| Nordic nRF52/53 | NFCT/TWIM 共享 | `nrf_gpio_pin_set` | `NRF_TWIM->ENABLE = 0` | TWIM 没 BUSY 位, 用 SDA 采样 |
| Renesas RA | R_IIC / R_GPIO | `R_GPIO_PinWrite` (开漏配置) | `R_IIC->IICCR1.SDIE` 序列 | Clock Stretching 需开 SSE bit |
| TI MSPM0 / C2000 | I2C / GPIO | `GPIO_writeDio` (开漏) | `I2C->GPRCM.RSTCTL` | 部分型号 BUSY 在 CTR 寄存器 |
| ESP32 | driver/i2c | `gpio_set_level(pin, 1)` | `i2c_driver_delete` | SDA 被拉低时无 BUSY, 靠超时 |

**核心原则**: 恢复代码通过 `i2c_recovery_ops_t` 抽象, 每个平台实现自己的 7 个回调 (prepare/unprepare/gpio_od_init/release/drive/read/delay)。**绝不把某个平台的寄存器序列硬编码到通用逻辑**。

---

## 产线日志样板

好的日志能让产线系统直接做 SPC (统计过程控制) 分析, 而不是事后追"昨天那块板死了几次"。

### 成功恢复

```text
[I2C1] xfer timeout: addr=0x68 op=reg_read reg=0x75 stage=WAIT_ACK scl=1 sda=0
[I2C1] recovery: enter reason=SDA_LOW last_addr=0x68 last_op=reg_read
[I2C1] recovery: prepare done, dma aborted, irq masked
[I2C1] recovery: pinmux to GPIO_OD
[I2C1] recovery: scl_high=1 sda_high=0 -> enter clock recovery
[I2C1] recovery: pulse=1 scl=1 sda=0
[I2C1] recovery: pulse=2 scl=1 sda=0
[I2C1] recovery: pulse=3 scl=1 sda=0
[I2C1] recovery: pulse=4 scl=1 sda=1 -> sda released
[I2C1] recovery: stop generated
[I2C1] recovery: rcc reset + hal init done
[I2C1] recovery: verify scl=1 sda=1 -> OK
[I2C1] recovery: result=success duration_ms=12
[I2C1] retry: addr=0x68 op=reg_read result=ok duration_ms=2
```

### 恢复失败 + 从设备复位兜底

```text
[I2C1] recovery: enter reason=SDA_LOW last_addr=0x68
[I2C1] recovery: pinmux to GPIO_OD
[I2C1] recovery: scl_high=1 sda_high=0
[I2C1] recovery: pulse=1..16 sda never released
[I2C1] recovery: stop attempt -> sda still low
[I2C1] recovery: result=FAIL sda_stuck=1
[I2C1] target-reset: addr=0x68 reset_gpio=PB12 toggle=1 delay_ms=10
[I2C1] target-reset: after_reset scl=1 sda=1
[I2C1] recovery: result=success_after_target_reset duration_ms=42
[I2C1] target-reinit: addr=0x68 -> client driver reinit OK
```

### 故障注入 (SDA 拉低测试)

```text
[TEST] inject: SDA forced low by fixture, addr=0x68
[I2C1] xfer: addr=0x68 op=reg_read -> ETIMEDOUT stage=WAIT_ACK sda=0
[I2C1] recovery: enter reason=SDA_LOW
[I2C1] recovery: pulse=4 sda released, stop generated, ctrl reset
[I2C1] recovery: result=success
[I2C1] retry: ok
[TEST] inject: SDA released by fixture
[TEST] inject: PASS
```

### 关键计数器 (暴露给 MES)

```text
i2c_xfer_total{bus, addr}
i2c_xfer_timeout{bus, addr, stage}
i2c_recover_attempt{bus}
i2c_recover_success{bus}
i2c_recover_fail_scl_stuck{bus}
i2c_recover_fail_sda_stuck{bus}
i2c_recover_fail_ctrl_reset{bus}
i2c_target_reset_count{bus, addr}
i2c_bus_disabled{bus}
i2c_recover_duration_ms{bus, p50, p99}
```

### 日志原则

- **限频**: 高频路径同 bus 同 addr 错误做限频, 避免日志刷屏
- **保留计数器**: 即使限频, 计数器必须累加
- **含时间戳**: 精确到 ms, 便于和上下电日志对齐
- **含上下文**: bus/addr/reg/stage 缺一不可
- **含结果**: result=success/fail + reason, 不只打 "i2c error"

---

## 电平转换

常见 I2C 电压：

```text
1.8V
3.3V
5V
```

不同电压域不能直接混接。

常见方案：

```text
BSS138 MOS 转换
PCA9306
TCA9517
专用 I2C buffer/level shifter
```

注意：

- 转换器增加电容。
- 转换器有速度限制。
- 某些 buffer 有方向、偏置或电压要求。
- 高速 I2C 问题常常出在电平转换器。

## 地址冲突

两个同地址设备挂在同一总线上会冲突。

解决方式：

- 使用地址选择引脚。
- 换不同地址型号。
- 使用多个 I2C 控制器。
- 使用 I2C MUX。
- 迁移到 I3C 动态地址。

常见 I2C MUX：

```text
TCA9548A
```

## I2C MUX

访问 MUX 后面的设备前，必须先选择通道：

```text
写 MUX 控制寄存器，打开通道 N
访问目标设备
必要时关闭通道
```

MUX 带来的问题：

- 软件路径更复杂。
- 扫描地址时要逐通道扫描。
- 忘记切通道会扫不到设备。
- 通道切换增加延迟。
- 故障定位要区分 MUX 前后两段总线。

## EEPROM 特性

I2C EEPROM 写入后需要内部写周期。

写周期内设备可能对地址 NACK。

这通常不是错误。

常见策略：

```text
ACK polling
```

也就是写完后轮询设备地址，直到重新 ACK。

EEPROM 还要注意 page boundary：

```text
跨页写可能回卷覆盖页内前面的数据
```

驱动必须按页切分写入。

## 传感器特性

很多传感器不是读寄存器就立刻有新数据。

常见流程：

```text
配置模式
启动测量
等待转换时间
读取 data ready 状态
读取数据寄存器
清除中断或状态位
```

如果没有等待转换完成，可能读到：

- 旧数据。
- 全 0。
- 无效标志。
- NACK。

## PMIC 和电源芯片特性

PMIC 常见机制：

- 写保护。
- 解锁序列。
- PAGE 多通道选择。
- 故障状态锁存。
- 写 RAM 和保存 NVM 分离。
- 某些状态下禁止改参数。

所以写寄存器不生效，不一定是 I2C 通信问题。

要结合设备状态机和手册限制排查。

## 驱动分层建议

推荐分层：

```text
i2c_transfer
  |
regmap / register access
  |
device driver
  |
application
```

基础访问接口建议支持：

```c
int read_reg8(uint8_t addr, uint8_t reg, uint8_t *value);
int write_reg8(uint8_t addr, uint8_t reg, uint8_t value);
int read_block(uint8_t addr, uint8_t reg, uint8_t *buf, size_t len);
int write_block(uint8_t addr, uint8_t reg, const uint8_t *buf, size_t len);
```

底层应统一处理：

- 超时。
- 重试。
- 错误码。
- 总线恢复。
- MUX 通道。
- 线程互斥。

## 错误码设计

不要只返回 `false`。

建议区分：

```text
address_nack
data_nack
timeout
bus_busy
arbitration_lost
clock_stretch_timeout
invalid_param
crc_error
```

这样现场日志才能定位问题阶段。

## 重试策略

推荐：

```text
最多重试 3 次
每次间隔 1~10 ms
失败后记录错误类型
bus_busy 或 timeout 后尝试恢复总线
```

不要无脑死循环重试。

如果设备持续 NACK，应上报设备离线或状态异常。

## 逻辑分析仪排查

重点看：

```text
START/STOP
7-bit/8-bit 地址显示方式
ACK/NACK 出现在哪一字节后
Repeated START 是否存在
SCL 是否被拉长
寄存器地址和数据是否符合手册
```

如果解码正常但设备行为不对，继续检查：

- 设备模式。
- 状态位。
- 延时要求。
- 字节序。
- 写保护。

## 示波器排查

示波器重点看电气质量：

- 高电平幅度。
- 低电平幅度。
- 上升沿时间。
- 振铃和过冲。
- 毛刺。
- SCL/SDA 串扰。

如果上升沿太慢：

```text
减小上拉电阻
降低速度
减少总线电容
缩短走线或线缆
减少挂载设备
检查电平转换器
```

## I2C 与 SMBus

SMBus 和 I2C 相似，但更严格。

SMBus 可能涉及：

- 超时。
- PEC。
- Alert。
- 标准事务格式。
- 特定速度范围。

访问 SMBus/PMBus 设备时，普通 I2C 读写可能不够，需要按对应事务实现。

## I2C 与 I3C

如果系统出现：

- 多传感器地址冲突。
- 中断 GPIO 不够。
- I2C 速度不够。
- 需要更好总线管理。

可以考虑 I3C。

但 I3C 需要控制器、目标设备、驱动和调试工具共同支持。成熟度和兼容性要提前评估。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 扫不到设备 | 电源、RESET、上拉、地址、电平 |
| 只有 100 kHz 稳定 | 上拉、电容、电平转换器、线长 |
| 地址 ACK 后数据 NACK | 寄存器地址、写保护、设备状态 |
| SDA 一直低 | 总线卡死、从设备异常、短路 |
| 读值全 FF | 设备未响应、SDA 上拉、地址错 |
| 读值全 00 | SDA 被拉低、寄存器/状态不对 |
| 传感器数据不变 | 未启动转换、未等 data ready |

## 深度检查清单

- SCL/SDA 空闲为高。
- 上拉接到正确电压域。
- 上拉阻值和总线电容满足目标速度。
- 地址按 7-bit/8-bit 规则确认。
- 寄存器读使用 Repeated START。
- 主控支持目标设备需要的 Clock Stretching。
- 有总线恢复机制。
- 多设备无地址冲突。
- I2C MUX 通道选择逻辑正确。
- EEPROM 页写和 ACK polling 已处理。
- 传感器转换时间和 data ready 已处理。
- PMIC 写保护、PAGE 和故障锁存已处理。
- 日志能区分地址 NACK、数据 NACK、超时和 bus busy。
