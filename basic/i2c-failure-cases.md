# I2C 产线死机案例库

## 目标

把产线上踩过的 I2C 死机坑写成案例库。每个案例:
- 现象 (现场)
- 抓波形 (判断)
- 定位 (根因)
- 修复 (代码 / 硬件)
- 复盘 (如何预防)

按主题分类, 配 `i2c-deep-dive.md` / `i2c-bus-recovery-playbook.md` 使用。

---

## 案例 1: STM32 死锁在 HAL_I2C_Master_Transmit

### 现象

产线 1% 板子在开机第一次读 IMU WHO_AM_I 时死机。日志最后一行:
```
[main] sensor init: read 0x75
[HAL] HAL_I2C_Master_Transmit(0x68, 0x75, ...)
[HAL] timeout 1000ms
[main] PANIC: sensor init failed
```

### 抓波形

- 死机时 SCL=1, SDA=0 (稳态)
- 重新上下电, 第一次读 SDA 立即低, IMU 没动

### 定位

IMU 内部状态机卡死, SDA 拉低不放。MCU 硬件 I2C 看到 BUSY=1, 不再发 SCL, 互等死锁。

### 修复

加 bus recovery:
```c
if (HAL_I2C_Master_Transmit(&hi2c1, 0x68<<1, buf, len, 100) != HAL_OK) {
    if (HAL_I2C_GetError(&hi2c1) & HAL_I2C_ERROR_TIMEOUT) {
        i2c_recover_bus(&hi2c1);  /* 9 SCL + STOP + 复位 */
    }
}
```

### 复盘

- **加 timeout** 只能让 caller 不死, 不能让总线恢复
- **首次 init 也要做 bus recovery**, 不要等业务报错才走恢复
- 修后产线通过率 100%

---

## 案例 2: PMIC 偶发读写失败, 概率 1/10000

### 现象

产线 10000 块板子 1 块失败, 日志:
```
[i2c1] write reg 0x12 val 0x34
[i2c1] err=-ETIMEDOUT stage=WAIT_ACK sda=0
```

重启后正常。

### 抓波形

失败时波形: PMIC 发了 ACK, 但 MCU 读到 NACK, 进入超时, 之后 SDA 被 PMIC 拉低不放。

### 定位

PMIC 内部 ACK 后状态机卡死。**只发生于 PMIC 刚被上电 100ms 内**, 此时 PMIC 时钟/PLL 还在 stable 中, I2C 状态机可能异常。

### 修复

1. PMIC 上电后延时 100ms 再访问 (硬件时序)
2. bus recovery 流程里加 "PMIC 专属: 失败后断 PMIC 电源 100ms 再上电" 的兜底

```c
int pmic_i2c_read(uint8_t reg, uint8_t *val) {
    if (i2c_xfer(...) != 0) {
        if (retry_count++ < 3) {
            HAL_Delay(10);
            return pmic_i2c_read(reg, val);  /* 简单重试 */
        }
        /* 重试仍失败, 触发 PMIC power cycle */
        pmic_power_cycle();
        return pmic_i2c_read(reg, val);
    }
    return 0;
}
```

### 复盘

- 通用 I2C 恢复不一定能救 PMIC, PMIC 有自己的 POR 流程
- 关键设备 (PMIC / EC) 需要 power cycle 兜底
- 产线应记录 PMIC 上电时序, 验证 datasheet

---

## 案例 3: 多任务并发访问同一 I2C, 偶发死锁

### 现象

RTOS 项目, 2 个 task 都调 `HAL_I2C_Master_Transmit`:
- task A: 读 sensor 1 (地址 0x68)
- task B: 读 sensor 2 (地址 0x53)

10% 概率 task A 死锁, 偶发 task B 也死锁。

### 抓波形

死锁时 SCL=0, SDA 浮空 (被 task A 卡在 mid-byte)。

### 定位

task A 调用 HAL 时, 被 task B 抢占, task B 也调 HAL, 两者都用同一个 hi2c1。
HAL 内部状态机被两个 caller 共享, tx_buf 指针错乱, 控制寄存器被覆盖。

**不是物理死锁, 是逻辑死锁**。

### 修复

加 mutex 串行化访问:

```c
static SemaphoreHandle_t g_i2c1_mutex;

int i2c1_xfer(uint8_t addr, uint8_t *buf, uint16_t len, uint32_t timeout) {
    xSemaphoreTake(g_i2c1_mutex, portMAX_DELAY);
    int ret = HAL_I2C_Master_Transmit(&hi2c1, addr<<1, buf, len, timeout);
    xSemaphoreGive(g_i2c1_mutex);
    return ret;
}
```

### 复盘

- HAL 库不是 thread-safe
- 任何被多 task 访问的外设, 必须 mutex
- I2C mutex 应该和 recovery mutex 是同一个, 避免恢复动作被打断

---

## 案例 4: 中断优先级问题导致 STOP 未生成

### 现象

低优先级 task 跑 I2C, 频繁死锁:
- 死锁时 SCL=0, SDA 有数据
- HAL 状态在 HAL_I2C_STATE_BUSY_TX
- 没有任何 ISR 触发

### 抓波形

逻辑分析仪看到 SCL 拉低但没有上升沿, 持续几十 ms。

### 定位

I2C EV 中断优先级 = 5, 但 DMA 中断优先级 = 3 (更高)。
DMA 完成时, 抢占 I2C EV 中断, 导致 I2C ISR 错过 STOP 生成时机。

STM32 HAL 内部靠 EV ISR 处理 STOP, EV ISR 一直被抢占, 永远等不到。

### 修复

I2C EV 中断优先级应比 DMA 中断更高, 或者用 RTOS 的中断安全 API:

```c
/* 调高 I2C EV 中断优先级 */
HAL_NVIC_SetPriority(I2C1_EV_IRQn, 2, 0);  /* 数字小 = 优先级高 */
HAL_NVIC_SetPriority(DMA1_Stream0_IRQn, 3, 0);
HAL_NVIC_EnableIRQ(I2C1_EV_IRQn);
```

### 复盘

- STM32 NVIC 数字小的优先级高
- I2C EV 中断需要能响应, 优先级不能比 DMA 低
- **重要**: HAL_I2C_EV_IRQHandler 必须在合理时间内响应, 否则超时

---

## 案例 5: 上拉电阻选错, 高速通信失败

### 现象

400 kHz 通信 100% 失败, 100 kHz 80% 失败。板子用了 10k 上拉。

### 抓波形

上升沿非常慢, 像 RC 充电曲线。SCL 上升时间 > 1us, 不满足 400 kHz 规格 (< 300ns)。

### 定位

总线电容太大 (走线 + 6 个设备 + 测试夹具), 10k 上拉太弱。

### 修复

- 短走线: 减小电容
- 用 4.7k 或 2.2k 上拉
- 验证: 上拉 × 总线电容 < 上升时间规格
- 走线: 减少 via, 远离高频线

### 复盘

- 上拉电阻是常见隐性 bug, 一定要用公式算
- 产线每块板子都应过 400 kHz 通信测试
- 高速失败时, 第一件事是看波形, 不是改代码

---

## 案例 6: 掉电顺序错乱, 总线死锁

### 现象

电池板断电, 再上电, 系统进不了 idle。日志:
```
[i2c1] xfer timeout
[i2c1] recovery: SDA stuck low
[i2c1] recovery: SCL stuck low
[i2c1] recovery: failed
```

### 抓波形

上电后 SCL=0 (稳态), SDA=0。
量 PMIC 输出: VCCIO=3.3V (正常), SCL 引脚有 0.7V。

### 定位

PMIC 还没完全启动 (POR 没完成), PMIC 的 SCL 引脚已经被内部 POR 电路拉低。MCU 切 GPIO 切不动, 因为 PMIC 是输出源, 不是灌电流。

**PMIC 在 POR 阶段会"主动"拉 SCL/SDA**, 直到自己起来。

### 修复

1. 上电后延时 200ms 再 init I2C (等 PMIC POR 完成)
2. init I2C 前做 bus idle check + recovery
3. 关键设备 reset 引脚接 MCU, 上电时序可控

```c
void system_init() {
    HAL_Delay(200);  /* 等所有 power domain 起来 */
    /* 关键: I2C init 前先 bus idle check */
    if (i2c_bus_idle_check(&hi2c1) != 0) {
        i2c_recover_bus(&hi2c1);
    }
    HAL_I2C_Init(&hi2c1);
}
```

### 复盘

- 上电时序是产线死机的大坑
- "MCU 复位时, 从设备可能没复位" 这句话要时刻记着
- Bus idle check 应该作为 init 流程的标准步骤

---

## 案例 7: 产线测试夹具引入额外电容

### 现象

研发环境 100% pass, 产线环境 30% fail。fail 现象都是 SDA 拉低后恢复慢。

### 抓波形

示波器探头点在 SDA 上, 比不接探头时慢 5 倍恢复。
拆掉测试夹具, 故障消失。

### 定位

测试夹具 1.5m 长, 加上双绞线 + 鳄鱼夹, 引入 100+ pF 电容, 上升沿极慢。
探头本身 10 pF 看起来不多, 但叠加上夹具就 100+ pF。

### 修复

1. 产线治具: 用短的 Pogo Pin, 不要长线
2. 探头: 选 100 MHz 以上 10x 探头, 不要用 1x
3. 产线夹具上加 buffer 隔离

### 复盘

- 测试夹具是产线特有干扰源
- 治具评审应包含 "对被测板电气特性的影响"
- 研发 pass 不等于产线 pass

---

## 案例 8: 同一地址的设备挂在两条不同总线上

### 现象

板子有 I2C0 和 I2C1, 两条总线上都挂 0x68 设备 (为了冗余, 设计如此)。
软件启动时只 init 一条总线, 跑业务时偶发读到的是另一条总线的设备, 数据错乱。

### 抓波形

SDA 上数据正常, 但读到的 ID 是错的, 不是预期 IMU 的 ID。

### 定位

业务代码调 `i2c_read(0x68, ...)` 时, 没指定是 I2C0 还是 I2C1, 用了全局 helper。
Helper 看到 "I2C0 失败就试 I2C1" 的逻辑, 实际读的是 I2C1 的设备。

**不是协议死锁, 是设计 bug**。

### 修复

业务代码必须显式指定 bus:
```c
/* 错 */
i2c_read(0x68, 0x75, buf);

/* 对 */
i2c0_read(0x68, 0x75, buf);
i2c1_read(0x68, 0x75, buf);
```

### 复盘

- 多 bus + 同地址 = 容易出错, 建议在硬件层隔离 (MUX)
- helper 函数不能隐式选 bus
- 设备树 / board config 应显式标 "这个设备在哪个 bus"

---

## 案例 9: I2C MUX 自身把 SDA 拉低

### 现象

I2C MUX (PCA9548A) 后面的 sensor 把 SDA 拉低, 整个上游总卡死。
即使关了 MUX 通道, 上游 SDA 仍低。

### 抓波形

MUX 上游 SDA=0, 拔 MUX 输出端, SDA 仍低。证明是 MUX 自己在拉。

### 定位

PCA9548A 在某些状态下, 上游 SDA 引脚被内部电路异常拉低。
**MUX 自身锁死**。

### 修复

1. MUX 的 RESET 引脚必须接 MCU GPIO
2. MUX 卡死时, 拉 RESET 保持 10ms, 释放, 等 MUX 启动
3. 重试 I2C 通信

```c
int i2c_mux_reset(struct i2c_mux *mux) {
    HAL_GPIO_WritePin(mux->reset_port, mux->reset_pin, GPIO_PIN_RESET);
    HAL_Delay(10);
    HAL_GPIO_WritePin(mux->reset_port, mux->reset_pin, GPIO_PIN_SET);
    HAL_Delay(50);  /* MUX 启动 */
    return 0;
}
```

### 复盘

- 关键桥接器 (MUX / 电平转换器) 的 reset 必须 MCU 可控
- MUX 卡死时, I2C 命令不能用, 只能 GPIO reset
- 关键设计: MUX 上电默认所有通道关闭, 减少故障传播

---

## 案例 10: 软件 bit-bang 与硬件 I2C 控制器抢总线

### 现象

调试时, 工程师接了 USB-I2C 适配器到产线板, 跑 i2c-tools 扫描地址。
然后 MCU 启动, 看到 BUSY, 进入恢复。

### 抓波形

USB-I2C 适配器正在用总线, MCU 突然插一脚。

### 定位

调试时多个 master 都在用总线, 仲裁失败但 MCU 误判为 SDA 拉低。

### 修复

1. 调试模式标志: 启动前检查是否有外部 master
2. 调试器使用单独 bus, 不与生产 bus 混
3. 多 master 检测: 见 `i2c-multimaster.md`

```c
int i2c_check_external_master() {
    /* 切到 GPIO 输入, 读 SDA 一段时间 */
    for (int i = 0; i < 100; i++) {
        if (!read_sda()) return 1;  /* 有外部 master */
        delay_us(10);
    }
    return 0;
}
```

### 复盘

- 调试工具 = 临时 master, 容易和产线 master 冲突
- 调试前应该先确认总线上没有其他 master
- 产线 test fixture 应该有 "屏蔽外部 I2C 干扰" 的能力

---

## 案例 11: I2C 控制器 BUSY 位异常不清

### 现象

STM32 F1 / F4 老款, I2C 控制器死锁后, 重新 init 后立刻看到 BUSY=1。

### 抓波形

SDA/SCL 都高, 但控制器读 BUSY=1, 拒发 START。

### 定位

STM32 老款 errata: SDA 拉低后, BUSY 位会卡死。
HAL_I2C_DeInit / Init 不清 BUSY 位, 必须 RCC reset。

### 修复

```c
void i2c_force_unbusy(I2C_HandleTypeDef *hi2c) {
    /* 关 DMA, 中断 */
    HAL_I2C_DeInit(hi2c);
    /* RCC reset, 这是关键 */
    if (hi2c->Instance == I2C1) {
        __HAL_RCC_I2C1_FORCE_RESET();
        __HAL_RCC_I2C1_RELEASE_RESET();
    }
    /* 重新 init */
    HAL_I2C_Init(hi2c);
}
```

### 复盘

- 不同 STM32 系列 errata 不同, 必须查手册
- F1/F2/F4 老款必走 RCC reset
- 通用 recovery 流程应包含 "RCC reset 控制器" 这一步

---

## 案例 12: DMA 完成中断和 I2C EV 中断 race condition

### 现象

用 DMA 发 100 字节, 偶发少发 1 字节, 卡在中间。

### 抓波形

DMA 完成中断触发后, SDA 应该由 I2C 自动 STOP, 但 STOP 没生成。

### 定位

DMA TCIF 中断 + I2C EV 中断 race condition。
两个 ISR 都想清状态, 一个清空了, 另一个看到的还是旧状态, 状态机错位。

### 修复

1. 提高 I2C EV 中断优先级, 比 DMA 高
2. 或: 不用 DMA, 用 IT 模式 (字节中断)
3. 或: 用 RTOS 的 ISR-safe 同步机制

```c
/* NVIC 优先级 */
HAL_NVIC_SetPriority(I2C1_EV_IRQn, 2, 0);
HAL_NVIC_SetPriority(DMA1_Stream0_IRQn, 3, 0);
```

### 复盘

- DMA + I2C 不是天然兼容, 中断优先级要明确
- 长数据 (>16 字节) 用 DMA, 短数据用 IT
- 调试 ISR race: 用断点暂停, 看状态机是否一致

---

## 案例 13: I2C 控制器在 STOP 阶段卡死

### 现象

事务在最后一步 (生成 STOP) 失败, HAL 永远等 STOPF。

### 抓波形

START, 数据, ACK 都正常, 但 STOP 没生成。SDA/SCL 都高, 没有 STOP 跳变。

### 定位

从设备在最后一字节 NACK 响应后, 主控自动 STOP, 但 STOPF flag 没置位。
可能原因: SCL 边沿在 STOP 时被从设备 clock stretching。

### 修复

1. 加 timeout, 1ms 内 STOPF 没置位就强制 abort
2. 强制 abort 后做 bus recovery
3. 降速: 100 kHz 而非 400 kHz, 减小从设备 stretching 概率

```c
uint32_t start = HAL_GetTick();
while (!__HAL_I2C_GET_FLAG(hi2c, I2C_FLAG_STOPF)) {
    if (HAL_GetTick() - start > 1) {
        /* STOP 超时 */
        i2c_force_unbusy(hi2c);
        return -ETIMEDOUT;
    }
}
```

### 复盘

- HAL 库的 I2C 状态机对 STOP 等待不够鲁棒
- 任何 flag 等待都要带 timeout
- 时序问题降速是最后手段, 但常有效

---

## 案例 14: 多 slave 同时掉电, 电流反灌

### 现象

板子断电瞬间, 多个 sensor 通过 SDA 反向灌电, 倒灌电流达 80 mA。

### 抓波形

断电瞬间, SDA 拉到 1.5V (sensor 通过 I2C 内部 ESD 二极管), 持续 200ms。

### 定位

Sensor VCC 先掉, 但 sensor 的 I2C 引脚通过内部 ESD 二极管反灌到 VDD_SDA。
多个 sensor 并联, 反灌电流过大, 触发 sensor 内部 POR, 状态机错乱。

### 修复

1. 硬件: sensor VCC 串入 load switch, MCU 可控断电
2. 硬件: SDA 上串联电阻 (限流, 100 ohm 左右)
3. 软件: 检测到 power 异常时, 主动关闭 sensor 电源再恢复

```c
/* 硬件修复: load switch */
HAL_GPIO_WritePin(SENSOR_PWR_PORT, SENSOR_PWR_PIN, GPIO_PIN_SET);  /* 上电 */
HAL_Delay(100);
HAL_I2C_Init(&hi2c1);
```

### 复盘

- 多 sensor 系统的 power 域管理是隐蔽问题
- 硬件设计阶段必须考虑 power 域隔离
- I2C 引脚串联电阻 (100 ohm) 是限流好习惯

---

## 案例 15: 产线 MES 系统误读 I2C 错误码

### 现象

MES 测试系统把 I2C 错误统一显示为 "I2C 错误", 不区分 NACK / timeout / ARLO。
产线死机 30% 误判为 sensor 坏, 实际是 recovery 失败但已自动重试成功。

### 抓波形

N/A (数据问题)。

### 定位

测试系统的 I2C 错误判定逻辑太粗, 不看 driver 返回的细分错误码, 也不看是否已 recovery 成功。

### 修复

1. Driver 错误码细分 (见 `i2c-deep-dive.md` 错误码设计)
2. MES 接收的测试结果包含:
   - error code (NACK / timeout / ARLO / recover_fail)
   - recover count
   - final result (pass / fail after recovery)
3. 产线判定: "已自动恢复" 算 pass, "无法恢复" 算 fail

```c
struct sensor_test_result {
    int err_code;
    int recover_count;
    bool final_success;
};

/* MES 判定 */
if (result.final_success) {
    pass_with_log("I2C recovered %d times", result.recover_count);
} else {
    fail("I2C unrecoverable err=%d", result.err_code);
}
```

### 复盘

- 测试系统的 "pass/fail" 判定要细
- 自动恢复成功 = pass, 产线继续
- 不可恢复 = fail, 需人工介入
- 错误码细分是产线良率分析的基础

---

## 案例 16: 长期老化, 焊点疲劳导致间歇 SDA 拉低

### 现象

产线良率 99.5%, 老化测试 (1000 小时) 后良率降到 80%。

### 抓波形

老化后偶发 SDA 拉低, 抓波形发现 SDA 在 0.5V 抖动。

### 定位

BGA 焊点疲劳, 接触电阻从 0.1 ohm 升到 10 ohm, I2C 拉低能力变弱, 但还没完全断开。

### 修复

1. 硬件: 改用更大焊盘, 加 underfill
2. 软件: 拉低电流不够时, 主动检测
3. 老化测试: 必须做, 不能省

### 复盘

- 产线良率 = 初始良率 × 老化系数
- 焊点设计是 I2C 可靠性的隐藏因素
- 1000 小时老化是 I2C 产品的标准测试

---

## 案例 17: 外部 I2C 干扰 (EMC)

### 现象

板子在电机附近工作, 偶发 I2C 通信失败。

### 抓波形

SDA 线上有 20MHz 噪声, 叠加在数据上。

### 定位

电机 PWM 干扰, 通过传导耦合到 I2C 线。

### 修复

1. 硬件: I2C 线远离 PWM 线, 加 shield
2. 硬件: SCL/SDA 加小电容 (10-100 pF) 滤波
3. 软件: 关键通信加重试 + CRC

### 复盘

- 工业 / 汽车环境 EMC 是产线常见问题
- I2C 抗干扰能力有限, 设计阶段就要考虑
- 软件补救: 重试 + CRC + 错误码细分

---

## 案例 18: 同一 I2C bus 上挂不同电平域设备

### 现象

3.3V sensor 和 1.8V sensor 挂在同一 I2C bus, 用电平转换器 (PCA9306)。
1.8V 设备偶发读失败。

### 抓波形

1.8V 侧 SDA 上升沿慢, 1.8V device 采样不到高电平。

### 定位

PCA9306 在 B-side (1.8V) 侧的上升沿依赖 1.8V 侧上拉, 上拉电阻太大 (10k) 配 1.8V, 上升沿慢。

### 修复

1. 1.8V 侧上拉改为 4.7k
2. 验证: 1.8V 侧 SDA 上升时间 < 300ns (400 kHz 规格)
3. 选更快的电平转换器 (TCA9517 等)

### 复盘

- 电平转换器两侧都要算上拉
- 慢速 I2C 转换器在高速下不可靠
- 测试: 在两侧都加波形测试点

---

## 案例 19: I2C 控制器在低功耗模式下行为异常

### 现象

MCU 进入 STOP 模式后, 唤醒时 I2C 通信失败 50%。

### 抓波形

唤醒后第一次 I2C 通信, SDA 时序异常, 像被卡了半拍。

### 定位

I2C 外设在 STOP 模式下被禁能, 唤醒后未重新 init, 控制器状态机异常。
HAL_I2C_Init 不会清 BUSY 残留状态。

### 修复

1. 唤醒后强制 HAL_I2C_DeInit + Init
2. 或者: 唤醒后做一次 bus idle check

```c
void on_wakeup() {
    HAL_I2C_DeInit(&hi2c1);
    __HAL_RCC_I2C1_FORCE_RESET();
    __HAL_RCC_I2C1_RELEASE_RESET();
    HAL_I2C_Init(&hi2c1);
    i2c_bus_idle_check(&hi2c1);
}
```

### 复盘

- 低功耗 + I2C = 隐性死锁
- 唤醒后必须重新 init 控制器
- 不能假设 HAL 会自动恢复

---

## 案例 20: 产线刷固件后 I2C 不通

### 现象

板子烧录新固件后, I2C sensor 全挂, 老固件正常。

### 抓波形

SDA 正常, SCL 一直低。

### 定位

新固件里有个 task 在 PVD (可编程电压检测) 中断里跑 I2C, 优先级最高, 但 PVD 触发时 I2C 状态机被半路打断。

**固件变更引入的 bug**。

### 修复

1. 任何中断里不应该直接跑 I2C 事务
2. 业务代码改完要做完整 I2C 回归测试
3. CI 流程包含 I2C 通信 smoke test

### 复盘

- 固件变更 = 产线灾难的潜在源
- 关键外设 (I2C, SPI) 的回归测试必须做
- 中断里跑 I2C 是常见反模式

---

## 案例汇总: 产线 I2C 死机根因分布

```text
电源 / 上电时序     25%
软件并发 / 优先级   20%
硬件设计 (上拉, MUX) 15%
从设备 lock-up      10%
EMC / 干扰          8%
ESD / 接触不良       7%
协议错误 (NACK)     5%
调试工具干扰         5%
其他                5%
```

电源和软件并发加起来近 50%, 是产线 I2C 死机的主要根因区。

## 产线根因预防清单

```text
□ 上电时序文档化, 包括从设备 POR 时间
□ 关键设备的 reset 由 MCU 控制
□ 软件中断优先级明文规定
□ 所有 task 通过 mutex 访问 I2C
□ Bus recovery 流程包含 RCC reset
□ 老化测试 1000+ 小时
□ MES 系统接收细分错误码
□ 产线夹具评审包含电气影响
□ 固件变更 CI 跑 I2C 回归
□ 上拉电阻根据总线电容计算
□ 关键设备 (PMIC, EC) 走 power cycle 兜底
□ 多 bus 同地址的设备在硬件层隔离
```

## 关联文档

- `i2c-deep-dive.md` 原理 + 故障树
- `i2c-bus-recovery-playbook.md` SOP
- `i2c-multimaster.md` 多 master
- `i2c-smbus-timeout.md` SMBus timeout
- `i2c-state-machine.md` 状态机
- `i2c-rtos-integration.md` RTOS 集成
