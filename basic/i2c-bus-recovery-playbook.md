# I2C Bus Recovery Playbook

## 目标

本文是 I2C 总线被拉低死锁的实战手册。`i2c-deep-dive.md` 讲原理和体系，本手册聚焦：
- 现场排障的 30 分钟快速定位流程
- 可直接拷进项目的 C 代码骨架
- 常见 MCU 平台的真实寄存器序列
- 产线验收清单和故障注入测试方案

当产线死机、客户投诉、CE/EMC 整改时，按本文顺序走。

## 30 分钟现场排障流程

### 5 分钟：抓现象

```text
1. 读死机日志
   - 死在哪一行: while(wait_ack) / HAL_I2C_Master_Transmit 阻塞 / sensor_read()
   - 哪个 bus, 哪个地址, 哪个寄存器
   - 错误码: HAL_ERROR / HAL_TIMEOUT / HAL_BUSY

2. 读最后一次成功事务的时间
   - 死机前最后访问的从设备地址
   - 系统刚做了什么: 上下电 / 切模式 / 切 MUX 通道
```

### 10 分钟：抓波形

```text
3. 接示波器或逻辑分析仪到 SCL/SDA
   - 高阻态用 10x 探头, 10MΩ 输入阻抗
   - 观察: SCL/SDA 真实电平, 是否被拉低

4. 记录三组数据
   - 死机瞬时的电平
   - 重新上下电后的电平
   - 把所有从设备拔掉, 只挂 MCU 时的电平
```

### 10 分钟：定位

```text
5. 死机时 SCL=1, SDA=0
   -> 经典 SDA stuck low
   -> 进入 bus recovery 流程
   -> 查: 从设备 datasheet 的 max stretching / 上下电时序

6. 死机时 SCL=0
   -> 可能是 Clock Stretching 超规格
   -> 可能是硬件短路
   -> 量 SCL 对地电阻, 拔从设备验证

7. 死机时 SCL=1, SDA=1
   -> 不是物理死锁
   -> 是协议层 NACK / 地址错 / 设备没上电
   -> 查电源域、地址、电平转换器
```

### 5 分钟：恢复

```text
8. 标准 bus recovery
   - 关 I2C 外设, 停 DMA, mask IRQ
   - SCL/SDA 切 GPIO 开漏
   - 释放 SDA, 等 SCL 回高
   - 9~16 个 SCL 脉冲, 每高电平采样 SDA
   - SDA 释放后生成 STOP
   - RCC reset + 重新 init I2C

9. 恢复失败
   - L4 兜底: reset GPIO / load switch / MUX 隔离
   - 上报: last_addr, stage, pulse_count, SCL/SDA 电平

10. 验证
    - 下一次访问: 读 WHO_AM_I 或 ID 寄存器
    - 连续读写 100 次无错误
    - 故障注入: 强制 SDA 低, 触发 recovery, 验证能恢复
```

## 可移植 C 代码骨架

把下列代码直接拷到项目, 替换 `xxx` 为平台函数即可。

```c
/* i2c_recovery.h - 平台无关接口 */

#ifndef I2C_RECOVERY_H
#define I2C_RECOVERY_H

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#define I2C_RECOVERY_MAX_PULSES     16U
#define I2C_RECOVERY_T_HIGH_US      10U
#define I2C_RECOVERY_T_LOW_US       10U
#define I2C_RECOVERY_BUS_FREE_US    10U
#define I2C_RECOVERY_SCL_WAIT_US    100U

typedef enum {
    I2C_RECOVER_RESULT_SUCCESS              = 0,
    I2C_RECOVER_RESULT_INVALID_ARG          = -1,
    I2C_RECOVER_RESULT_PREPARE_FAIL         = -2,
    I2C_RECOVER_RESULT_GPIO_INIT_FAIL       = -3,
    I2C_RECOVER_RESULT_SCL_STUCK_LOW        = -4,
    I2C_RECOVER_RESULT_SDA_STUCK_LOW        = -5,
    I2C_RECOVER_RESULT_STOP_FAIL            = -6,
    I2C_RECOVER_RESULT_UNPREPARE_FAIL       = -7,
    I2C_RECOVER_RESULT_TARGET_RESET_FAIL    = -8,
} i2c_recover_result_t;

typedef struct {
    int  (*prepare)(void *ctx);
    int  (*unprepare)(void *ctx);
    int  (*gpio_od_init)(void *ctx);
    void (*release_scl)(void *ctx);
    void (*drive_scl_low)(void *ctx);
    void (*release_sda)(void *ctx);
    void (*drive_sda_low)(void *ctx);
    bool (*read_scl)(void *ctx);
    bool (*read_sda)(void *ctx);
    void (*delay_us)(void *ctx, uint32_t us);
    int  (*reset_target)(void *ctx);
} i2c_recovery_ops_t;

int i2c_bus_recover(const i2c_recovery_ops_t *ops, void *ctx);

#endif /* I2C_RECOVERY_H */
```

```c
/* i2c_recovery.c - 平台无关实现 */

#include "i2c_recovery.h"

static int wait_scl_high(const i2c_recovery_ops_t *ops, void *ctx) {
    const uint32_t retries = I2C_RECOVERY_SCL_WAIT_US;
    for (uint32_t i = 0; i < retries; i++) {
        if (ops->read_scl(ctx)) return 0;
        ops->delay_us(ctx, 1U);
    }
    return -1;  /* SCL stuck low */
}

static int generate_stop(const i2c_recovery_ops_t *ops, void *ctx) {
    ops->drive_sda_low(ctx);
    ops->delay_us(ctx, I2C_RECOVERY_T_LOW_US);

    ops->release_scl(ctx);
    if (wait_scl_high(ops, ctx) != 0) return -1;

    ops->delay_us(ctx, I2C_RECOVERY_T_HIGH_US);
    ops->release_sda(ctx);
    ops->delay_us(ctx, I2C_RECOVERY_BUS_FREE_US);

    return ops->read_sda(ctx) ? 0 : -1;
}

int i2c_bus_recover(const i2c_recovery_ops_t *ops, void *ctx) {
    if (!ops || !ops->prepare || !ops->unprepare || !ops->gpio_od_init ||
        !ops->release_scl || !ops->drive_scl_low ||
        !ops->release_sda || !ops->drive_sda_low ||
        !ops->read_scl    || !ops->read_sda    || !ops->delay_us) {
        return I2C_RECOVER_RESULT_INVALID_ARG;
    }

    int ret = ops->prepare(ctx);
    if (ret != 0) return I2C_RECOVER_RESULT_PREPARE_FAIL;

    ret = ops->gpio_od_init(ctx);
    if (ret != 0) {
        (void)ops->unprepare(ctx);
        return I2C_RECOVER_RESULT_GPIO_INIT_FAIL;
    }

    ops->release_scl(ctx);
    ops->release_sda(ctx);
    ops->delay_us(ctx, I2C_RECOVERY_T_HIGH_US);

    if (wait_scl_high(ops, ctx) != 0) {
        ret = I2C_RECOVER_RESULT_SCL_STUCK_LOW;
        goto fallback;
    }

    if (!ops->read_sda(ctx)) {
        for (uint32_t i = 0; i < I2C_RECOVERY_MAX_PULSES; i++) {
            ops->drive_scl_low(ctx);
            ops->delay_us(ctx, I2C_RECOVERY_T_LOW_US);
            ops->release_scl(ctx);
            if (wait_scl_high(ops, ctx) != 0) {
                ret = I2C_RECOVER_RESULT_SCL_STUCK_LOW;
                goto fallback;
            }
            ops->delay_us(ctx, I2C_RECOVERY_T_HIGH_US);
            if (ops->read_sda(ctx)) break;
        }
    }

    if (generate_stop(ops, ctx) != 0) {
        ret = I2C_RECOVER_RESULT_STOP_FAIL;
        goto fallback;
    }

    ret = ops->unprepare(ctx);
    if (ret != 0) return I2C_RECOVER_RESULT_UNPREPARE_FAIL;

    return I2C_RECOVER_RESULT_SUCCESS;

fallback:
    if (ops->reset_target) (void)ops->reset_target(ctx);
    (void)ops->unprepare(ctx);
    return ret;
}
```

## STM32 HAL 平台适配层

```c
/* platform_stm32.c - STM32 HAL 适配 */

#include "stm32f4xx_hal.h"
#include "i2c_recovery.h"

typedef struct {
    I2C_HandleTypeDef *hi2c;
    GPIO_TypeDef      *port;
    uint16_t           scl_pin;
    uint16_t           sda_pin;
} stm32_recover_ctx_t;

/* 假设: hi2c1 -> SCL=PB6, SDA=PB7 */
static stm32_recover_ctx_t g_ctx = {
    .hi2c    = &hi2c1,
    .port    = GPIOB,
    .scl_pin = GPIO_PIN_6,
    .sda_pin = GPIO_PIN_7,
};

static int stm32_prepare(void *ctx) {
    stm32_recover_ctx_t *c = (stm32_recover_ctx_t *)ctx;
    HAL_I2C_DeInit(c->hi2c);
    __HAL_I2C_DISABLE(c->hi2c);
    HAL_NVIC_DisableIRQ(I2C1_EV_IRQn);
    HAL_NVIC_DisableIRQ(I2C1_ER_IRQn);
    if (c->hi2c->hdmatx) HAL_DMA_Abort(c->hi2c->hdmatx);
    if (c->hi2c->hdmarx) HAL_DMA_Abort(c->hi2c->hdmarx);
    c->hi2c->State     = HAL_I2C_STATE_READY;
    c->hi2c->ErrorCode = HAL_I2C_ERROR_NONE;
    return 0;
}

static int stm32_unprepare(void *ctx) {
    stm32_recover_ctx_t *c = (stm32_recover_ctx_t *)ctx;
    GPIO_InitTypeDef gpio = {0};

    /* 切回 AF_OD */
    gpio.Pin       = c->scl_pin | c->sda_pin;
    gpio.Mode      = GPIO_MODE_AF_OD;
    gpio.Pull      = GPIO_NOPULL;
    gpio.Speed     = GPIO_SPEED_FREQ_HIGH;
    gpio.Alternate = GPIO_AF4_I2C1;
    HAL_GPIO_Init(c->port, &gpio);

    /* RCC reset 后重新 init */
    __HAL_RCC_I2C1_FORCE_RESET();
    __HAL_RCC_I2C1_RELEASE_RESET();

    if (HAL_I2C_Init(c->hi2c) != HAL_OK) return -1;
    return 0;
}

static int stm32_gpio_od_init(void *ctx) {
    stm32_recover_ctx_t *c = (stm32_recover_ctx_t *)ctx;
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin   = c->scl_pin | c->sda_pin;
    gpio.Mode  = GPIO_MODE_OUTPUT_OD;
    gpio.Pull  = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(c->port, &gpio);
    return 0;
}

static void stm32_release_scl(void *ctx) {
    stm32_recover_ctx_t *c = (stm32_recover_ctx_t *)ctx;
    HAL_GPIO_WritePin(c->port, c->scl_pin, GPIO_PIN_SET);
}
static void stm32_drive_scl_low(void *ctx) {
    stm32_recover_ctx_t *c = (stm32_recover_ctx_t *)ctx;
    HAL_GPIO_WritePin(c->port, c->scl_pin, GPIO_PIN_RESET);
}
static void stm32_release_sda(void *ctx) {
    stm32_recover_ctx_t *c = (stm32_recover_ctx_t *)ctx;
    HAL_GPIO_WritePin(c->port, c->sda_pin, GPIO_PIN_SET);
}
static void stm32_drive_sda_low(void *ctx) {
    stm32_recover_ctx_t *c = (stm32_recover_ctx_t *)ctx;
    HAL_GPIO_WritePin(c->port, c->sda_pin, GPIO_PIN_RESET);
}
static bool stm32_read_scl(void *ctx) {
    stm32_recover_ctx_t *c = (stm32_recover_ctx_t *)ctx;
    return (HAL_GPIO_ReadPin(c->port, c->scl_pin) == GPIO_PIN_SET);
}
static bool stm32_read_sda(void *ctx) {
    stm32_recover_ctx_t *c = (stm32_recover_ctx_t *)ctx;
    return (HAL_GPIO_ReadPin(c->port, c->sda_pin) == GPIO_PIN_SET);
}
static void stm32_delay_us(void *ctx, uint32_t us) {
    /* 用 DWT 或硬件 timer, 禁止裸循环 */
    extern void delay_us(uint32_t);
    delay_us(us);
}
static int stm32_reset_target(void *ctx) {
    /* 示例: 通过另一个 GPIO 复位下游 IMU */
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_RESET);
    HAL_Delay(10);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_SET);
    HAL_Delay(50);  /* 等待从设备启动 */
    return 0;
}

const i2c_recovery_ops_t stm32_recovery_ops = {
    .prepare        = stm32_prepare,
    .unprepare      = stm32_unprepare,
    .gpio_od_init   = stm32_gpio_od_init,
    .release_scl    = stm32_release_scl,
    .drive_scl_low  = stm32_drive_scl_low,
    .release_sda    = stm32_release_sda,
    .drive_sda_low  = stm32_drive_sda_low,
    .read_scl       = stm32_read_scl,
    .read_sda       = stm32_read_sda,
    .delay_us       = stm32_delay_us,
    .reset_target   = stm32_reset_target,
};

/* 在 bus 层调用: */
void i2c1_recover_if_needed(void) {
    i2c_bus_recover(&stm32_recovery_ops, &g_ctx);
}
```

## 集成到 RTOS 驱动

```c
/* 在 adapter 层检测到 timeout 后调度恢复 */

static void i2c_adapter_recover_dispatch(struct i2c_adapter *adap) {
    /* 1. 设状态 */
    atomic_store(&adap->state, I2C_ADAPTER_RECOVERING);

    /* 2. 唤醒恢复工作线程 (而不是在 ISR / 调用线程里做) */
    osSemaphoreRelease(adap->recover_sem);
}

static void i2c_recover_thread(void *arg) {
    struct i2c_adapter *adap = (struct i2c_adapter *)arg;

    while (1) {
        osSemaphoreAcquire(adap->recover_sem, osWaitForever);

        /* 3. 拿 bus mutex, 阻止新事务 */
        osMutexAcquire(adap->bus_mutex, osWaitForever);

        /* 4. 调平台无关的恢复 */
        int ret = i2c_bus_recover(adap->recovery_ops, adap->recovery_ctx);

        /* 5. 记录结果 */
        i2c_recovery_log(adap, ret);

        /* 6. 状态切回 IDLE */
        atomic_store(&adap->state, I2C_ADAPTER_IDLE);

        /* 7. 释放 mutex, 唤醒等待的 client */
        osMutexRelease(adap->bus_mutex);
    }
}
```

## 产线故障注入测试方案

### 硬件方案 1: MOSFET 拉低

```text
+3.3V
  |
 [R_pullup] 4.7k
  |
  +-------+-------> SDA
  |       |
  |      [Q] N-MOSFET (2N7000)
  |       |
  |      GPIO_TEST_SDA_PULLDOWN (MCU 另一个 GPIO)
  |       |
  |      GND

测试流程:
  1. 正常运行 I2C
  2. 测试 GPIO 拉高, Q 导通, SDA 被强制拉低
  3. 观察: 驱动进入 recovery
  4. 测试 GPIO 拉低, Q 关断, SDA 释放
  5. 观察: recovery 成功, 总线恢复
```

### 硬件方案 2: 跳线 + 按钮

产线人工测试用, 简单但不可重复。

### 软件方案: Linux fault injection

```bash
# Linux 下用 GPIO fault injection
mount -t debugfs debugfs /sys/kernel/debug
echo 1 > /sys/kernel/debug/i2c-fsi/

# 强制拉低 SDA
echo "force_sda_low" > /sys/kernel/debug/i2c-fsi/inject

# 观察 dmesg
dmesg | grep -i i2c
```

### 测试用例矩阵

| 用例 | 注入 | 期望 | 通过标准 |
| --- | --- | --- | --- |
| SDA 拉低 | MOSFET 拉低 100ms | recovery 成功 | 1s 内恢复 |
| SDA 拉低 - 恢复中 | 拉低 1s, 中途释放 | recovery 提前 break | pulse<16 成功 |
| SCL 拉低 | 强制 SCL 低 100ms | 识别 SCL stuck, 走 L4 兜底 | 不误报 success |
| 主机复位 | 读事务中 NVIC reset | 启动后 bus idle check 成功 | 10s 内恢复 |
| 从设备掉电 | 切断从设备 VCC | 从设备 reset 兜底成功 | 30s 内恢复 |
| 多线程并发 | RTOS 2 任务同时访问 | bus lock 有效, 不并发 | 无死锁 |
| 长时间老化 | 连续 10w 次读写 | 错误计数稳定 | 恢复成功率 > 99.9% |

## 产线验收清单

工程交付时, 验证下列项全部通过:

- [ ] 所有 `while` 等待有 timeout, 用 DWT/timer 不用裸循环
- [ ] timeout 触发的恢复动作在 workqueue / 恢复线程, 不在 ISR
- [ ] bus mutex 保护下执行 recovery
- [ ] GPIO 切 OD 输出, 不推挽
- [ ] 读 IDR 不读 ODR
- [ ] SCL stuck 和 SDA stuck 分开处理
- [ ] SCL 脉冲有上限 (max_pulses = 16), 每高电平采样 SDA
- [ ] SDA 释放后生成 STOP
- [ ] 恢复后 RCC reset + HAL/LL 重新 init
- [ ] 恢复失败有 reset_target 兜底
- [ ] 自动重试有限次 (建议每事务 1 次, 每设备窗口内 3 次)
- [ ] 日志含 bus / addr / stage / line level / result
- [ ] 日志有限频, 计数器累加
- [ ] 暴露计数器给 MES / 测试系统
- [ ] 产线有 SDA/SCL fault injection 用例
- [ ] 老化测试通过 (10w+ 读写, 恢复成功率 > 99.9%)

## 面试回答模板

### 1 分钟版本

> 这是 I2C Bus Recovery 问题, 不是单纯加超时。超时让线程不死, 恢复让物理总线回 IDLE。
>
> 标准做法: 关 I2C 外设和中断 DMA, SCL/SDA 切 GPIO 开漏, 释放 SDA, 打 9~16 个 SCL 脉冲, 每高电平采样 SDA, SDA 释放后生成 STOP, 然后复位 I2C 控制器。
>
> 恢复失败要 reset 从设备或电源域, 不能无限重试。整体必须有 mutex、timeout、错误码、计数器。
>
> 关键规范: NXP UM10204 Bus clear, Linux I2C core bus_recovery_info, Zephyr i2c_recover。

### 5 分钟版本

按四层结构答:
1. L1 事务超时
2. L2 GPIO bus recovery
3. L3 控制器复位
4. L4 从设备兜底

每层讲清楚:
- 解决什么问题
- 关键动作
- 失败兜底
- 为什么这一步不能省

## 关联文档

- `i2c-deep-dive.md` 原理和体系
- `i2c-practical.md` 速查
- `smbus-pmbus-practical.md` SMBus timeout 差异
- `i3c-deep-dive.md` I3C 演进和兼容性
- `mipi-csi-dsi-debug.md` 传感器侧 I2C 初始化
- `fpd-link-gmsl-practical.md` 远端 I2C / 反向通道

## 来源

- wdfk-prog 公众号: 嵌入式面试真题第 06 题 - I2C SDA 被拉低死锁后的软件恢复
- NXP UM10204 I2C-bus specification and user manual
- Linux I2C and SMBus Subsystem Documentation
- Linux I2C GPIO Fault Injection
- Zephyr I2C API Documentation
