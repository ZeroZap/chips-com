# I2C / SMBus Timeout 专题

## 目标

SMBus (System Management Bus) 基于 I2C 物理层, 但在 timeout 上有更严格的要求。混用 I2C 和 SMBus 设备, 或者用普通 I2C 控制器访问 SMBus 设备时, timeout 处理不到位是产线卡死的常见根因。

本文讲清楚:

- SMBus 三大 timeout 的精确数值
- 为什么普通 I2C 设备没这些 timeout
- 实现 timeout 检测的代码
- timeout 和 bus recovery 的关系
- 常见错误实现

## SMBus 三大 timeout

SMBus 2.0 spec 定义了三个 timeout:

```text
T_TIMEOUT:    25 ~ 35 ms    SCL 拉低单次最大时间 (clock low timeout)
T_LOW:        25 ~ 35 ms    SCL 累积拉低时间 (cumulative clock low extend)
T_HIGH:       50 us ~ 10 ms SCL 拉高最大时间 (clock high timeout)
```

| 名称 | 范围 | 含义 | 检测方 |
| --- | --- | --- | --- |
| T_TIMEOUT | 25~35 ms | 一次 SCL 低不能超过这个 | 设备自检 (复位状态机) |
| T_LOW (SMBus 3.0) | 25 ms | SCL 累积拉低时间 | 设备自检 |
| T_HIGH | 50us~10ms | SCL 拉高时间 (master 仲裁丢失) | Master |

### T_TIMEOUT (25~35 ms)

SCL 一次连续低电平时间不能超过 25~35 ms。如果从设备 clock stretching 超过这个时间, SMBus 设备必须**自动复位自己**的 I2C 状态机并释放 SCL。

**关键**: 这是**从设备自己**实现的, 不是说 master 要等 25ms。

### T_LOW / Cumulative (SMBus 3.0)

SMBus 3.0 新增。累积 stretching 超过 25ms 也视为异常, 设备重置。

### T_HIGH (50us ~ 10ms)

SCL 高电平时间太长 = master 没产生 SCL 边沿 = 可能是 master 卡住, 或仲裁丢失后 SCL 卡高。

Master 必须检测: 启动一次事务后, 50us ~ 10ms 内 SCL 必须有下降沿, 否则视为异常。

## 为什么普通 I2C 设备没这些 timeout

普通 I2C spec (UM10204) **没有强制 timeout 要求**。一些老旧 I2C 设备:

- 可能 stretching 几秒 (早期 EEPROM 常见)
- 可能完全不实现 timeout 检测
- 内部状态机卡死后只能靠外部 master 救

**后果**: 写普通 I2C 控制器 (不带 timeout 检测) 访问 SMBus 设备, 如果设备卡死, 整个 bus 可能卡死。

## Timeout 在 I2C 总线卡死中的作用

```text
卡死场景 1: 从设备 stretching 异常
  普通 I2C 设备: 可能 stretching 几秒
  SMBus 设备:  25~35ms 内必须自己 reset
  -> 选 SMBus 设备, 设备侧有兜底

卡死场景 2: 从设备状态机卡死, SDA 拉低
  普通 I2C 设备: 自己不 reset, 等 master 来救
  SMBus 设备:  25~35ms 仍未完成, 设备 reset (释放 SDA)
  -> 选 SMBus 设备, 物理层更可靠

卡死场景 3: Master 仲裁失败, SCL 卡高
  普通 I2C:     Master 自己必须检测 T_HIGH (50us ~ 10ms)
  SMBus Master: 强制要求
  -> 任何 master 都要做 T_HIGH 检测
```

## 实现 timeout 检测

### T_TIMEOUT (SCL 单次低超时) - Master 端

```c
#define SMBUS_T_TIMEOUT_MS  25U   /* SMBus 2.0 spec: 25~35ms */

/* 在 master 拉低 SCL 后, 启动定时器 */
void master_pull_scl_low(I2C_TypeDef *i2c) {
    LL_I2C_GenerateStart(i2c);
    start_timer(SMBUS_T_TIMEOUT_MS);  /* 硬件 timer */
}

void on_scl_still_low_after_timeout(void) {
    /* 1. 标记错误 */
    xfer->err_stage = STAGE_SCL_TIMEOUT;
    /* 2. 强制释放 SCL (write SDA/SCL high) */
    LL_I2C_GenerateStop(i2c);  /* 内部会尝试 */
    /* 3. 触发 bus recovery */
    schedule_recovery();
}
```

### T_HIGH (SCL 高超时) - Master 端

```c
#define SMBUS_T_HIGH_MIN_US  50U
#define SMBUS_T_HIGH_MAX_US  10000U  /* 10ms */

/* Master 在 START 后启动 T_HIGH 定时器 */
void master_after_start(I2C_TypeDef *i2c) {
    start_timer_us(SMBUS_T_HIGH_MAX_US);  /* 10ms 内必须有 SCL 下降沿 */
}

void on_scl_high_timeout(void) {
    /* SCL 卡高 = master 仲裁失败 / 总线被外部干扰 */
    xfer->err_stage = STAGE_SCL_HIGH_TIMEOUT;
    /* 退避重试, 不要直接 recovery */
    xfer->need_retry = true;
    schedule_retry_with_backoff();
}
```

### T_LOW 累积检测 (SMBus 3.0)

```c
typedef struct {
    uint32_t accum_low_ms;
    uint32_t last_low_start_tick;
} smbus_tlow_t;

void smbus_tlow_enter_low(smbus_tlow_t *t) {
    t->last_low_start_tick = systick_ms();
}

void smbus_tlow_exit_low(smbus_tlow_t *t) {
    uint32_t now = systick_ms();
    t->accum_low_ms += (now - t->last_low_start_tick);
    if (t->accum_low_ms > SMBUS_T_LOW_MAX_MS) {
        /* 累积 stretching 超标, 强制 abort */
        trigger_fault();
    }
}

void smbus_tlow_reset_per_xfer(smbus_tlow_t *t) {
    t->accum_low_ms = 0;
    t->last_low_start_tick = 0;
}
```

## Timeout 和 Bus Recovery 的关系

```text
                  +-------------------+
                  |   正常事务         |
                  +---------+---------+
                            |
                  +---------v---------+
                  | 等待 SCL 边沿      |
                  +---------+---------+
                            |
                +-----------+-----------+
                |                       |
        等待 < timeout            等待 > timeout
                |                       |
        +-------v-------+       +-------v-------+
        | 继续等         |       | timeout 触发   |
        +---------------+       +-------+-------+
                                        |
                                +-------v-------+
                                | 是 T_TIMEOUT  |
                                | (SCL 卡低)   |
                                +-------+-------+
                                        |
                                +-------v-------+
                                | 触发 recovery  |
                                +-------+-------+
                                        |
                                +-------v-------+
                                | 走 bus recovery|
                                +---------------+
```

**关键**: timeout 触发的恢复, 要区分错误类型:

- **T_TIMEOUT (SCL 单次低)**: 一定触发 bus recovery
- **T_HIGH (SCL 卡高)**: 仲裁失败, 退避重试, **不**触发 recovery
- **T_LOW 累积**: 触发 recovery 或 abort 事务
- **普通 I2C 设备 stretching 超时**: 视情况, 可能 recovery

## 常见错误

### 错误 1: 用普通 I2C 控制器访问 SMBus 设备, 没 timeout

```c
/* 错 */
HAL_I2C_Master_Transmit(&hi2c1, 0x10, buf, len, 1000);  /* 1000ms 死等 */
```

```c
/* 对: 实现 timeout 检测, 25ms 后触发处理 */
if (HAL_I2C_Master_Transmit(&hi2c1, 0x10, buf, len, 25) != HAL_OK) {
    if (timeout_occurs) {
        schedule_recovery();
    }
}
```

### 错误 2: T_TIMEOUT 和 bus recovery 串了

```c
/* 错: T_TIMEOUT 后直接 reset 控制器, 不发 SCL 脉冲 */
void on_t_timeout() {
    HAL_I2C_DeInit(&hi2c1);
    HAL_I2C_Init(&hi2c1);  /* 这只清 BUSY, 不发 SCL 脉冲 */
    /* SDA 仍被从设备拉低, 下次事务还卡 */
}

/* 对: T_TIMEOUT 后, 先发 SCL 脉冲再 reset */
void on_t_timeout() {
    /* 1. 关闭外设 (disable, 不 reset) */
    __HAL_I2C_DISABLE(&hi2c1);
    /* 2. GPIO 切开漏 */
    /* 3. 9~16 个 SCL 脉冲 */
    /* 4. STOP */
    /* 5. controller reset + init */
}
```

### 错误 3: T_HIGH 误触发 recovery

```c
/* 错 */
void on_t_high_timeout() {
    schedule_recovery();  /* T_HIGH 是仲裁失败, 不是 SDA 卡死 */
    /* recovery 把其他 master 事务打掉 */
}

/* 对 */
void on_t_high_timeout() {
    xfer->need_retry = true;  /* 退避重试 */
    schedule_retry_with_backoff();
}
```

### 错误 4: timeout 数值用错

```c
/* 错: 100ms 太大 */
#define SMBUS_T_TIMEOUT_MS  100

/* 对: SMBus 2.0 spec 是 25~35ms */
#define SMBUS_T_TIMEOUT_MS  25
```

### 错误 5: 混用 I2C 和 SMBus 设备, 用最严标准

```c
/* 对: 总线有 SMBus 设备, 用 SMBus timeout 约束整个总线 */
if (bus_has_smbus_device()) {
    bus->t_timeout_ms = 25;
} else {
    bus->t_timeout_ms = 1000;  /* 普通 I2C 设备可能 stretching 几秒 */
}
```

## 产线测试 timeout 行为

```text
测试用例:
  T_TIMEOUT 检测:
    1. 接入 SMBus 设备 (e.g. EMC1414 温度传感器)
    2. 用测试固件让设备进入 stretching > 25ms
       (可以读一个不存在的寄存器, 或者用 bit-bang 模拟)
    3. 观测: master 25ms 内 abort
    4. 观测: master 触发 recovery 或 retry

  T_HIGH 检测:
    1. 接入 master + 1 个从设备
    2. 强制 SCL 卡高 (MOSFET)
    3. 观测: master 在 10ms 内检测, 退避重试
    4. 期望: 不触发 recovery, 不影响其他 master
```

## 跨设备/跨总线的 timeout 策略

```text
单一 I2C 总线:
  - 如果只挂普通 I2C 设备, 用宽松 timeout (1s)
  - 如果有 SMBus 设备, 严格 timeout (25ms)

混合 I2C + SMBus 设备 (同一总线):
  - 用最严标准: 25ms
  - 风险: 某些慢速 I2C 设备可能误触发, 需要设备层标记 "我需要更长 timeout"

多总线:
  - 关键 SMBus 总线 (电池/PMIC): 25ms 严格
  - 普通 I2C 总线 (sensor): 100ms
  - debug/test 总线: 1s
```

## 总结: Timeout 选型表

| 设备类型 | T_TIMEOUT | T_HIGH | 行为 |
| --- | --- | --- | --- |
| SMBus 2.0 | 25~35 ms | 50us~10ms | 触发 recovery + retry |
| SMBus 3.0 | 25 ms (累积) | 50us~10ms | 同上 |
| 严格 I2C (e.g. PMIC) | 100 ms | 50us~10ms | 触发 recovery + retry |
| 普通 sensor | 500 ms | 不必检测 | 触发 recovery |
| EEPROM | 1000 ms | 不必检测 | 仅 retry |
| 多 master 系统 | 25 ms | 50us~10ms | 退避 retry, 不 recovery |

## 关联文档

- `i2c-deep-dive.md` 总线恢复基础
- `i2c-bus-recovery-playbook.md` 实战 SOP
- `smbus.md` / `smbus-pmbus-practical.md` SMBus 基础
- SMBus 2.0 spec 第 4.3.3 节 (Timeouts)
- SMBus 3.0 spec 第 4.3.3 节
