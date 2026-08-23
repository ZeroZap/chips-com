# I2C vs SMBus Bus Recovery 对比

## 目标

I2C 和 SMBus 物理层兼容, 但 **bus recovery 行为差异巨大**。本文用对比表 + 实操建议, 帮你一眼看清:

- SMBus 设备和普通 I2C 设备在卡死时谁负责救
- master timeout 数值应该怎么选
- 混用时按哪个标准
- 怎么判断一个设备是 SMBus 还是普通 I2C

如果你已经熟悉 I2C recovery, 只想知道 SMBus 多了什么, 看第 3 节"bus recovery 行为差异"。

## 一句话核心差异

> **SMBus 在 I2C 物理层之上强制加了"双向 timeout 机制"——从设备 25-35ms 内必须自己重置并释放 SCL, master 50us-10ms 内必须检测 SCL 卡高并 abort。普通 I2C 完全没有这套机制。**

后果:
- SMBus 设备卡死 → **设备自己** 25-35ms 后释放总线
- I2C 设备卡死 → **master 必须** 主动打 9~16 SCL + STOP 才能救

## 完整对比表

| 维度 | 普通 I2C | SMBus |
| --- | --- | --- |
| 协议定位 | 物理层 + 轻量协议 | 基于 I2C 的系统管理规范 |
| 规范来源 | NXP UM10204 | SMBus 2.0 / 3.0 spec |
| 强制 timeout | ❌ 无 | ✅ 三大 timeout 强制 |
| 卡死恢复责任 | **master 单方面** | **master + 设备双方** |
| 从设备重置要求 | 无, 设备可以永远 stretching | 25-35ms 内必须自己重置 |
| Master 检测要求 | 自选, 通常 1s | 强制 50us-10ms (T_HIGH) |
| 速度范围 | 100kHz~3.4MHz+ | 10kHz~100kHz |
| 总线电容上限 | 400pF (标准模式) | 更严格 |
| PEC (CRC) | 无 | 部分场景强制 |
| SMBALERT 中断 | 无 | 有, 设备主动通知 master |
| 设备地址 | 7-bit / 10-bit | 8-bit (7-bit + R/W) |
| Reserved 地址 | 少 | 多 (含 SMBus 特有地址) |
| 典型设备 | 通用 sensor / EEPROM / RTC | PMIC / 电池 / 温度传感器 |
| 常见封装 | 通用 MCU 控制器 | 多数现代 MCU 都支持 |
| 调试工具 | i2cdetect / i2cdump | 同 I2C |

## Bus Recovery 行为差异详解

### 场景 1: 从设备卡在 bit / ACK 状态, SDA 拉低

```text
普通 I2C 设备:
  1. 设备一直拉低 SDA, 等 SCL
  2. master 看 SDA=0 判 BUSY, 不发 SCL
  3. master 死等 → 必须 master 主动打 9~16 SCL 推设备状态机
  4. master 生成 STOP, 复位控制器
  5. 通常需要 100ms~秒级才能恢复

SMBus 设备:
  1. 设备一直拉低 SDA
  2. 25-35ms 仍未完成, 设备**自己重置**内部状态机
  3. 设备自动释放 SDA
  4. master 检测到 SDA 释放后, 重新发起事务
  5. 通常 25-50ms 内自动恢复, master 不需要打 SCL 脉冲
```

### 场景 2: SCL 被从设备 clock stretching 拉低

```text
普通 I2C 设备:
  - 某些老 EEPROM 可以 stretching 几秒
  - master 必须按 datasheet 设置 timeout
  - 超时后必须 master 强制恢复

SMBus 设备:
  - 25-35ms 内必须自己重置
  - 即使 datasheet 写 "max stretching 100ms", 实际 SMBus 设备会强制 35ms reset
  - master 检测 T_TIMEOUT 后做 recovery
```

### 场景 3: Master 自身卡死 (SCL 卡高)

```text
普通 I2C:
  - 没有强制 T_HIGH 检测
  - master 通常用大 timeout (1s) 等事务完成
  - 风险: 总线被卡高 1s, 期间所有 master / 设备都不能用

SMBus:
  - 强制 T_HIGH = 50us~10ms
  - master 启动 START 后 10ms 内必须有 SCL 下降沿
  - 否则 master abort, 退避重试
  - 不影响总线其他 master
```

### 场景 4: 多 master 仲裁失败

```text
普通 I2C:
  - 仲裁失败后 master 退避重试
  - 没有强制时间窗口
  - 容易出现 "两个 master 都死等" 的次优行为

SMBus:
  - 仲裁失败时, T_HIGH 检测生效
  - 失败的 master 在 10ms 内必须放弃
  - 退避算法有更明确的规范
```

## Timeout 数值精确对比

| Timeout | SMBus 2.0 / 3.0 spec | 普通 I2C 习惯 | 实际差异 |
| --- | --- | --- | --- |
| **T_TIMEOUT** (SCL 单次低) | 25-35 ms | 1-1000 ms | SMBus 严格 25 倍以上 |
| **T_LOW (累积)** (SMBus 3.0) | 25 ms | 不检测 | SMBus 独有 |
| **T_HIGH** (SCL 高) | 50us - 10 ms | 不检测 / 100ms | SMBus 独有 |
| **T_BUF** (总线空闲) | 4.7us @ 100kHz | 1.3us @ 400kHz | 速度相关 |

**关键**: SMBus 的 25-35ms 是**设备自己**的硬性要求, 不是 master 等得起等不起的问题。即使 master 设 1s timeout, 25ms 后设备也会自己重置。

## Master 端实现差异

### 普通 I2C master

```c
/* 典型 HAL 写法 */
HAL_I2C_Master_Transmit(&hi2c1, addr<<1, buf, len, 1000);  /* 1s 大 timeout */
if (HAL_OK != HAL_ERROR) { ... }

/* 失败后: master 主动 recovery */
if (HAL_I2C_GetError(&hi2c1) & HAL_I2C_ERROR_TIMEOUT) {
    i2c_recover_bus(&hi2c1);  /* 9 SCL + STOP + reset */
}
```

### SMBus 兼容 master

```c
/* 严格 timeout, 25ms */
HAL_I2C_Master_Transmit(&hi2c1, addr<<1, buf, len, 25);
if (HAL_OK != HAL_ERROR) { ... }

/* 失败后: 通常不需要打 9 SCL, 设备自己已经 reset */
if (HAL_I2C_GetError(&hi2c1) & HAL_I2C_ERROR_TIMEOUT) {
    /* 1. 等设备 reset 完成 (再多等 5-10ms) */
    HAL_Delay(10);
    /* 2. 检查 SDA 是否已经释放 */
    if (sda_is_high()) {
        /* 设备已自恢复, 直接 retry */
        return HAL_I2C_Master_Transmit(...);
    } else {
        /* 设备没自恢复, 走 I2C recovery */
        i2c_recover_bus(&hi2c1);
    }
}
```

## 错误处理差异

| 错误 | 普通 I2C 行为 | SMBus 行为 |
| --- | --- | --- |
| 从设备 NACK | Master 重试, 设备无动作 | Master 重试, 设备无动作 |
| 总线忙 (BUSY) | Master 等或 abort | 同 I2C |
| SDA 卡低 | Master 主动 recovery | 设备 25-35ms 自重置, 不需要 recovery |
| SCL 卡低 | Master 主动 recovery | 设备 25-35ms 自重置, 不需要 recovery |
| 仲裁失败 (ARLO) | Master 退避重试 | T_HIGH 强制检测 + 退避重试 |
| 数据错误 / PEC 错误 | 不支持 PEC | 启用 PEC 时 master 验证 CRC, 错误重传 |
| 设备主动通知 | 不支持 | SMBALERT 引脚, 设备主动通知 |

## 速度对比

```text
普通 I2C:
  - Standard mode:   100 kHz
  - Fast mode:       400 kHz
  - Fast mode plus:  1 MHz
  - High speed:      3.4 MHz
  - Ultra fast:      5 MHz (推挽, 不兼容 SMBus)

SMBus:
  - SMBus:           10-100 kHz
  - SMBus 3.0:       可达 1 MHz (新增 high-speed)
  - 典型应用:       100 kHz
```

**关键**: 高速 I2C 设备 (1MHz+) 几乎都不是 SMBus。SMBus 主要用于**低速、可靠性优先**的系统管理类设备。

## 典型设备对比

| 设备类型 | I2C | SMBus | 备注 |
| --- | --- | --- | --- |
| EEPROM (24Cxx) | ✅ | 部分 | 普通 I2C |
| RTC (DS1307) | ✅ | 部分 | 多数是 I2C, 少数 SMBus |
| 温度传感器 (LM75) | ✅ | 部分 | LM75 是 SMBus |
| 温度传感器 (TMP102) | ✅ | 部分 | TMP102 是 SMBus |
| GPIO 扩展 (PCF8574) | ✅ | 部分 | PCF8574 是 I2C, PCF8575 类似 |
| PMIC (BQ 系列) | 部分 | ✅ | 多数 BQ 是 SMBus |
| 电池 (BQ27441) | 部分 | ✅ | SMBus + PEC |
| 触摸 IC | ✅ | 部分 | 多数是普通 I2C |
| IMU (MPU6050) | ✅ | ❌ | 普通 I2C |
| 摄像头 sensor | ✅ | ❌ | 普通 I2C |
| HDMI EDID DDC | ✅ | ❌ | DDC 是 I2C 协议 |
| LED 驱动 (LP3943) | ✅ | ❌ | 普通 I2C |

## 混用策略 (最重要)

如果一条总线上同时挂 SMBus 设备和 I2C 设备:

### 推荐: 物理隔离 (MUX)

```text
+3.3V
  |
 [R_pullup]
  |
  +-------+-------> SMBus 段 (PMIC, 温度, 电池)
  |       |        -> 严格 timeout 25ms
  |      [PCA9548A MUX]
  |       |
  |       +-------> 普通 I2C 段 (sensor, RTC)
  |                  -> 宽松 timeout 1s
```

### 不可行物理隔离: 按最严标准做

```c
/* 同一总线既有 SMBus 设备又有 I2C 设备, 用 SMBus 标准 */
bus->t_timeout_ms = 25;       /* 而不是 1s */
bus->t_high_us    = 10000;    /* 10ms T_HIGH */
/* 风险: 慢速 I2C 设备可能误触发, 需要设备层标注 */
```

### 设备层标注

```c
struct i2c_client {
    uint8_t addr;
    bool is_smbus;            /* 这个设备是不是 SMBus */
    uint32_t max_stretch_ms;  /* datasheet 声明的最大 stretching */
};

/* 在 bus 层做 timeout 判定 */
uint32_t effective_timeout(struct i2c_client *c) {
    if (c->is_smbus) return 25;
    if (c->max_stretch_ms) return c->max_stretch_ms;
    return 1000;  /* 默认 */
}
```

## 怎么判断设备是 SMBus 还是 I2C

```text
查 datasheet, 命中以下 4 项中 2 项以上 → SMBus:

□ Datasheet 明确说 "SMBus compliant" 或 "SMBus 2.0/3.0"
□ 设备是电源/电池/温度/系统管理类
□ 有 SMBALERT 引脚
□ 有 clock low timeout 规格 (25-35ms)
□ 启用 PEC
□ 速度只有 10-100kHz, 不支持 400kHz+

如果不确定, 默认按普通 I2C 处理, 但 timeout 建议不超过 100ms。
```

## 实操建议

### 写新代码

```c
/* 1. 板级配置: 标每个设备的类型 */
struct i2c_bus_config {
    bool has_smbus_device;     /* 总线上是否有 SMBus 设备 */
    uint32_t t_timeout_ms;     /* 按此值设 timeout */
    bool enable_pec;           /* 是否启用 PEC */
};

/* 2. master driver: 按 config 调 timeout */
HAL_I2C_Master_Transmit(..., config->t_timeout_ms);

/* 3. recovery: 区分 SMBus / I2C */
int i2c_recover(struct i2c_bus *bus) {
    if (bus->config.has_smbus_device) {
        /* SMBus 设备 25ms 内自重置, 等设备即可 */
        HAL_Delay(50);
        if (sda_is_high()) return 0;
        /* 还不行才打 9 SCL */
    }
    /* 普通 I2C, 必须打 9 SCL */
    return i2c_bitbang_recovery(bus);
}
```

### 调试老代码

```c
/* 看现有代码, 几个快速判断点: */
if (HAL_I2C_Master_Transmit(..., 1000)) {  /* timeout > 100ms, 多半是普通 I2C 习惯 */
    /* ... */
}
if (bus->has_pmic || bus->has_battery) {  /* 有电源设备, 多半要按 SMBus 严格做 */
    /* 改 timeout 为 25ms */
}
```

## 选型决策树

```text
你的系统用什么 I2C timeout?
|
+-- 25ms
|     -> 总线上有 SMBus 设备 (PMIC, 电池, 温度)
|     -> 严格模式, 设备会自重置
|
+-- 100ms
|     -> 总线只有普通 I2C 设备, 但有老/慢设备
|     -> 折中模式
|
+-- 1s
      -> 总线只有普通 I2C 设备, 包括可能 stretching 几秒的老 EEPROM
      -> 宽松模式, 设备不会自重置, master 必须能 recovery
```

## 产线故障模式对比

| 故障 | I2C 系统常见 | SMBus 系统常见 |
| --- | --- | --- |
| 死机根因 | 设备状态机卡死 (无自重置) | 概率更低, 但 PEC 错误常见 |
| 恢复时间 | 100ms~秒级 (master 主动) | 25-50ms (设备自重置) |
| Bus recovery 触发频率 | 高 (必须主动) | 低 (设备自重置够用) |
| 总线可用性 | 依赖 master 实现的鲁棒性 | 设备 + master 双方保障 |
| 调试难度 | 高 (要查 master 行为) | 中 (要查 PEC 和 timeout) |

## 常见误用

### 误用 1: 用普通 I2C 习惯访问 SMBus 设备

```c
/* 错: timeout 1s 访问 PMIC */
HAL_I2C_Master_Transmit(..., 1000);  /* 1s */
/* 问题: PMIC 在 25-35ms 后已经自重置, 但 master 还在等 ACK */
/*      1s 后 master timeout, 误以为 PMIC 死了 */
```

### 误用 2: 用 SMBus 严格 timeout 访问普通 I2C 设备

```c
/* 错: timeout 25ms 访问老 EEPROM */
HAL_I2C_Master_Transmit(..., 25);  /* 25ms */
/* 问题: 老 EEPROM 写周期可能 5ms, stretching 100ms+, 25ms 误触发 */
```

### 误用 3: 不知道总线上混了什么设备

```c
/* 错: 没标设备类型, 整条总线用 1000ms timeout */
HAL_I2C_Master_Transmit(..., 1000);
/* 总线上既有 SMBus PMIC 又有普通 I2C EEPROM */
/* PMIC 早就自己重置了, master 在等, 浪费 1s */
```

## 国产 MCU 兼容 SMBus 的真相

产线经常听到"国产 MCU 兼容 SMBus", 这句话**很容易被误解**。

### 一句话澄清

> **国产 MCU 兼容 SMBus = master 端协议兼容 (PEC + T_HIGH + 时序), 并不意味着 slave 端会自动 reset, 也不意味着 master 能强制 slave 重置。自动 reset 是 slave 自己内部电路的事。**

### 拆开看: master 和 slave 两端

| 端 | 谁来做 | 自动 reset 责任 |
| --- | --- | --- |
| Master 端 (国产 MCU 控制器) | 国产 MCU 厂商 | N/A (master 不会自己重置) |
| Slave 端 (从设备) | 从设备厂商 | **从设备自己内部电路** |

国产 MCU 兼容 SMBus, **只在 master 端**做了这些事:

- PEC 校验 (CRC)
- T_HIGH 检测 (监控 SCL 卡高)
- 更严格的时序参数
- PEC 错误处理

它**不能**:

- 强制外部从设备 25-35ms 内 reset
- 替代从设备自己的 clock low timeout 电路
- 在 master 端模拟从设备的 self-reset 行为

### 从设备的"自动 reset"是硬件事

要自动 reset, 从设备内部必须有专门的电路:

```text
从设备内部
  |
  +-- I2C 状态机 (FSM)
  |     ↑
  |     | 监控
  |     |
  +-- Clock Low Timer (25-35ms 定时器)
  |     | 超时触发
  |     ↓
  +-- 内部复位电路
  |     -> FSM 复位
  |     -> 释放 SCL
  |     -> 释放 SDA
  |     -> 不响应总线
  |
  +-- 数据传输通路
```

**只有从设备自己有这个电路时, master 端才能"等 25-35ms 让它自己救自己"。**

### 国产 MCU 的两种使用场景

#### 场景 1: 国产 MCU 作为 master, 访问外部从设备

```text
国产 MCU (master) ---I2C---> 外部 sensor (slave)
```

- 国产 MCU 说自己兼容 SMBus → master 端 PEC, T_HIGH 检测能开
- **但 sensor 是不是会在 25-35ms 内自动 reset, 完全看 sensor 的 datasheet**
- 很多国产 sensor / EEPROM 实际**没有**实现 clock low timeout

#### 场景 2: 国产 MCU 自己作为从设备, 被其他 master 访问

```text
外部 master ---I2C---> 国产 MCU (slave, e.g. 作为协处理器)
```

- 国产 MCU 的 **I2C slave 控制器** 有没有内置 clock low timeout?
- **要查具体型号的 datasheet**:
  - 多数国产 MCU 的 slave 端**有**超时检测 (一般 25-35ms)
  - 少数低端型号**没有**
  - 高端型号 (华大 HC32F4A0, GD32F4) 通常有

### 国产 MCU 厂商 SMBus 兼容矩阵

下表是常见国产 MCU 厂商**典型型号**的 SMBus 兼容情况, **具体型号仍需查手册**:

| 厂商 | 代表型号 | Master 端 SMBus 兼容 | Slave 端 timeout | 备注 |
| --- | --- | --- | --- | --- |
| 兆易创新 (GD) | GD32F450, GD32F303 | ✅ 支持 (需配置) | ✅ 多数有 | 高端型号更完整 |
| 兆易创新 (GD) | GD32F130, GD32E230 | 部分支持 | 部分 | 低端型号查手册 |
| 沁恒 (WCH) | CH32V307, CH32V203 | ✅ 支持 | ✅ 有 | RISC-V 生态 |
| 国民技术 | N32G4FR, N32G020 | 部分支持 | 部分 | 通用 MCU |
| 华大半导体 | HC32F4A0, HC32L136 | ✅ 较完整 | ✅ 有 | 老牌国产 |
| 复旦微电子 | FM33LG0, FM33A0 | 部分支持 | 部分 | 车规 / 工业 |
| 雅特力 (Artery) | AT32F403A, AT32F421 | ✅ 支持 | ✅ 有 | 兼容 STM32 |
| 灵动微 (MindMotion) | MM32F3270, MM32SPIN | 部分支持 | 部分 | 通用 |
| 恒玄 (BES) | BES2500, BES2700 | ✅ 较完整 | ✅ 有 | 蓝牙音频 SoC |
| 博通集成 | BK7251, BK7231 | ✅ 较完整 | ✅ 有 | WiFi/BT SoC |
| 翱捷 (ASR) | ASR5801, ASR3601 | ✅ 较完整 | ✅ 有 | 蜂窝 SoC |
| 紫光展锐 | UNISOC 平台 | ✅ 较完整 | ✅ 有 | 蜂窝平台 |

**注意**: "✅ 支持" 是 master 端协议兼容, 不是"自动 reset 兼容"。slave 端自动 reset 仍要查具体型号 + 实测。

### 怎么验证从设备是否自动 reset

产线上碰到怀疑 slave 不自动 reset:

```text
1. 抓波形: master 发 START 后等 50ms
2. 看 slave 是否自动释放了 SDA/SCL
3. 如果 50ms 后 SDA 仍低 -> slave 没自动 reset
4. 此时只能靠 master 主动打 9 SCL 救
```

代码验证:

```c
/* 测试 1: 不做 master recovery, 等 50ms */
HAL_I2C_Master_Transmit(..., 50);
HAL_Delay(50);  /* 再多等 20ms */
if (sda_is_high()) {
    /* slave 自动 reset 成功 */
    log("slave self-recovered");
} else {
    /* slave 没自动 reset */
    log("slave STUCK, need master recovery");
    i2c_bitbang_recovery();
}
```

### 实战建议 (针对国产 MCU 项目)

不管从设备 datasheet 写没写"支持 SMBus", **都按 25ms 严格来**:

```c
/* 1. 板级配置: 标每个设备的实际行为 */
struct i2c_client {
    bool is_smbus;              /* 厂商说兼容 SMBus? */
    bool has_self_reset;        /* 实际验证有自动 reset? (产线测试填) */
};

/* 2. master: timeout 严格 25ms */
#define T_TIMEOUT_MS  25
HAL_I2C_Master_Transmit(..., T_TIMEOUT_MS);

/* 3. recovery: 优先等设备自重置, 不行再主动 recovery */
int i2c_recover(struct i2c_client *c) {
    if (timeout_occurs) {
        HAL_Delay(10);  /* 等设备可能的自重置 */
        if (sda_is_high()) {
            /* 设备自重置了 */
            return 0;
        }
        /* 不行, master 主动救 */
        return i2c_bitbang_recovery();
    }
}
```

### 选国产 MCU 时, 验证清单

```text
□ Master 端 SMBus 配置项 (PEC, T_HIGH 检测) 是否完整
□ Slave 端 clock low timeout 是否有, 数值多少
□ 控制器 BUSY 位清除是否需要 RCC reset (类似 STM32 errata)
□ I2C 中断优先级如何在 NVIC 配
□ 是否有官方 SMBus 示例代码
□ HAL / LL 库的 timeout 处理是否健壮
□ 多个 I2C controller 是否都能独立 SMBus 配
□ DMA + I2C 是否有 race condition 已知问题
```

## 进阶: SMBus 3.0 增强

SMBus 3.0 (2014+) 相对 2.0 多了:

- **T_LOW 累积检测**: 即使单次 stretching < 25ms, 累积 > 25ms 也视为异常
- **更高的速度**: 可达 1 MHz (high-speed)
- **更强的鲁棒性**: 设备状态机更严格

master 实现时, T_LOW 累积需要单独计时:

```c
typedef struct {
    uint32_t accum_low_ms;
    uint32_t last_low_start;
} smbus_tlow_t;

void smbus_tlow_enter_low(smbus_tlow_t *t) {
    t->last_low_start = systick_ms();
}

void smbus_tlow_exit_low(smbus_tlow_t *t) {
    t->accum_low_ms += (systick_ms() - t->last_low_start);
    if (t->accum_low_ms > 25) {
        /* 累积 stretching 超标, 强制 abort */
        trigger_fault();
    }
}

void smbus_tlow_reset_per_xfer(smbus_tlow_t *t) {
    t->accum_low_ms = 0;
}
```

## 总结: 一张表选 timeout

| 设备组合 | T_TIMEOUT | T_HIGH | 行为 |
| --- | --- | --- | --- |
| 纯 SMBus 设备 (PMIC, 电池) | 25 ms | 10 ms | 等设备自重置, 必要时 recovery |
| 纯普通 I2C 设备 (sensor, EEPROM) | 1-1000 ms | 不必检测 | 必须 master 主动 recovery |
| 混用 (I2C + SMBus) | 25 ms | 10 ms | 严格模式, 设备层标注 |
| 多 master | 25 ms | 10 ms | 退避重试, 不主动 recovery |

## 关联文档

- `i2c-deep-dive.md` I2C 原理 + 故障树
- `i2c-bus-recovery-playbook.md` 8 步恢复 SOP
- `i2c-smbus-timeout.md` SMBus timeout 详细数值
- `smbus-pmbus-practical.md` SMBus 事务 / PEC / Alert
- `i2c-multimaster.md` 多 master 仲裁
- `i2c-failure-cases.md` 案例 2 (PMIC 上电时序)
- SMBus 2.0 spec
- NXP UM10204 I2C spec
