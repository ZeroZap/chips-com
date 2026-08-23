# I2C 多主机仲裁

## 目标

I2C 总线是开漏结构, 天然支持多主机 (multi-master) 仲裁。但**单主机系统**也很容易在不经意间变成多主机场景 (外部测试治具、协处理器、PMIC 内部 master、EC/BMC)。

本文讲清楚:

- 仲裁的物理原理
- 单 master 系统如何避免被外部 master 坑
- 多 master 系统的 bus recovery 特殊性
- 典型多 master 场景的处理

## 仲裁物理原理

I2C 仲裁基于"线与"特性:

```text
仲裁规则:
  - 主机 A 发送地址/数据时, 同时监听 SDA
  - 如果主机 A 想发 1, 但 SDA 上读到 0, 说明有其他 master 在发 0
  - 主机 A 仲裁失败, 立即退出, 变从机
  - 主机 B 继续完成事务
```

SDA 仲裁的 wire-AND 特性:

```text
        master_A_out     master_B_out     总线 SDA
        发 bit 1         发 bit 0         0   (0 wins)
        发 bit 0         发 bit 1         0   (0 wins)
        发 bit 1         发 bit 1         1
        发 bit 0         发 bit 0         0
```

**SCL 同步**: 多 master 同时发 SCL 时, "clock synchronization"机制让 SCL 拉低的所有 master 都被"拉低" (低电平 AND 高电平 = 低电平), 直到所有 master 释放 SCL, 总线 SCL 才回高。

**重要**: 仲裁只能在地址位 + 数据位 + ACK 位进行, **不能在 START/STOP 之间**。所以 START/STOP 期间如果有其他 master 抢, 不会仲裁, 直接冲突。

## 单主机系统为啥要关心

### 隐藏的多 master 场景

```text
你以为的单 master:
  MCU I2C0 <-> sensor
  MCU I2C1 <-> PMIC

实际可能是:
  MCU I2C0 <-> sensor <- 测试治具 probe (夹具上有 master)
  MCU I2C1 <-> PMIC  <- PMIC 内部 master (读 charger IC 状态)
  MCU I2C2 <-> EC    <- EC 是独立 master, 在某些事件下抢总线
  MCU I2C3 <-> 外部 connector -> 上位机/master 控制器
```

**单 master 不再"单"** 时:

- 测试治具: 夹具上有 FTDI / 总线分析仪, 可能发 START
- PMIC 内部 master: 部分 PMIC 自带 I2C master, 用于读 fuel gauge / charger
- EC / BMC: 服务器/笔记本上常见, 独立 master 监控电池/温度
- 上位机 / 调试器: 某些板子留 I2C 测试口, 上位机可能扫描总线
- 桥接芯片: SPI-to-I2C bridge, USB-to-I2C bridge

## 多 master 下的 bus recovery 风险

### 风险 1: 误触发 STOP 破坏其他 master 事务

```text
时序:
  1. master A 启动事务, 发地址 bit 7
  2. 某个 master B 抢, 仲裁中
  3. master C 看到 SDA 异常 (有外部干扰), 触发 bus recovery
  4. master C 打 9 个 SCL + STOP
  5. master A 事务被中断
  6. master B 看到 STOP, 也退出
```

**后果**: master A/B 的事务被 master C 误伤。

### 风险 2: 恢复动作期间其他 master 不知情

```text
时序:
  1. master A 检测到 SDA 异常
  2. master A 开始 bus recovery: 关外设, 切 GPIO
  3. master B 此时正在用总线, 完全不知 master A 在做什么
  4. master A 打 9 个 SCL + STOP
  5. master B 的从设备看到 STOP, 状态机错乱
```

### 风险 3: 多 master 都试图恢复

```text
  1. 三个 master 同时看到 SDA 异常
  2. 三个都启动 recovery
  3. 互相打 SCL, 互相 STOP
  4. 谁也恢复不了
```

## 多 master 系统的工程方案

### 方案 1: 硬件隔离 (推荐)

**最稳的方案是物理上避免多 master**:

```text
+3.3V
  |
 [R_pullup]
  |
  +-------+-------> 主 I2C 总线 (只有 MCU 访问)
          |
          +-------> I2C Mux (PCA9548A)
                    |
                    +-- Ch0: 安全传感器 (可被外部访问)
                    +-- Ch1: 关键外设 (只 MCU 访问)
                    +-- Ch2: 调试端口 (外部测试治具)
```

关键:

- 关键外设**独占一条 I2C**, 外部 master 物理不可达
- 调试/测试口走 mux, 调试时由 MCU 控制 mux 开放
- 调试完关 mux, 隔离

### 方案 2: Master Owner 选举

只有一个 master 负责 recovery, 其他 master 看到异常就放弃:

```c
/* 在 adapter 初始化时设置 */
bool is_recovery_owner = false;

/* 所有 master 启动时先抢 owner */
if (atomic_cas(&recovery_owner, -1, my_id) == 0) {
    is_recovery_owner = true;
}

/* 异常时只有 owner 跑 recovery, 其他只等 */
void on_sda_low() {
    if (is_recovery_owner) {
        schedule_recovery();
    } else {
        abort_xfer();
    }
}
```

### 方案 3: 总线所有权 (Bus Owner)

每次只有一个 master 是 bus owner, 其他用 bus 前必须先请求:

```c
typedef enum {
    BUS_OWNER_NONE,
    BUS_OWNER_ME,
    BUS_OWNER_OTHER,
} bus_owner_t;

int request_bus(bus_owner_t who) {
    atomic_compare_exchange(&bus_owner, BUS_OWNER_NONE, who);
    return atomic_load(&bus_owner) == who;
}

void release_bus(bus_owner_t who) {
    if (atomic_load(&bus_owner) == who) {
        atomic_store(&bus_owner, BUS_OWNER_NONE);
    }
}

/* 用总线前 */
if (request_bus(BUS_OWNER_ME) != 0) {
    /* 拿到所有权, 跑事务 */
    do_xfer();
    release_bus(BUS_OWNER_ME);
} else {
    /* 其他 master 正在用, 退避重试 */
    retry();
}
```

### 方案 4: 检测仲裁 + 不主动 recovery

多 master 系统的金科玉律: **看到仲裁失败, 不要主动 recovery**:

```c
void i2c_xfer_done(int status) {
    if (status == -EAGAIN) {
        /* 仲裁失败, 退避重试 */
        delay_random_us();
        retry_xfer();
    } else if (status == -ETIMEDOUT) {
        if (is_only_master()) {
            schedule_recovery();  /* 只有确认自己是唯一 master 才恢复 */
        } else {
            /* 多 master, 等待, 让 owner 处理 */
            wait_ms(100);
            retry_xfer();
        }
    }
}
```

### 方案 5: 软件层做 bus 仲裁 (不推荐, 但作为最后手段)

```c
/* 每次发 START 前, 先看 SDA 是否空闲, 再等一个 "安全窗口" */
int i2c_safe_start(I2C_TypeDef *i2c) {
    if (!sda_is_high()) return -EBUSY;
    delay_ms(BUS_IDLE_TIME_MS);  /* 等 4.7ms (100kHz 周期) */
    if (!sda_is_high()) return -EBUSY;
    LL_I2C_GenerateStart(i2c);
    return 0;
}
```

**问题**: 仍可能和其他 master 同时发 START, 不会改善, 只能减少。

## 多 master + 总线 recovery 时的规范做法

参考 NXP UM10204 第 16 节:

```text
1. 不要在多 master 环境下做主动 bus recovery
2. 仲裁失败时, master 立即释放 SDA 和 SCL
3. 等待一个超时 (例如 1s) 让 owner 恢复
4. 超时后再尝试, 不要无限重试
5. 如果多个 master 同时尝试 recovery, 用 master 选举避免冲突
```

## 测试: 多 master 场景

```c
/* 测试用例 1: 两个 MCU 共享一条 I2C, 同时访问不同地址 */
- 主 MCU 持续读 sensor A (地址 0x68)
- 副 MCU (FPGA 模拟) 持续读 sensor B (地址 0x53)
- 观测: SDA 上的实际波形, 仲裁是否正常
- 期望: 两个 master 都能正常完成, 没有 deadlock

/* 测试用例 2: 副 MCU 故意把 SDA 拉低 */
- 主 MCU 在事务中
- 副 MCU 强行拉低 SDA
- 观测: 主 MCU 仲裁失败, 退避, 重试
- 期望: 主 MCU 不死锁, 最终成功

/* 测试用例 3: 副 MCU 不响应 */
- 主 MCU 发地址
- 副 MCU 模拟不拉低 SDA (模拟 NACK)
- 观测: 主 MCU 收到 NACK, 不死锁
- 期望: 主 MCU 返回 NACK 错误, 不触发 bus recovery

/* 测试用例 4: 主 MCU recovery, 副 MCU 在场 */
- 主 MCU 触发 bus recovery
- 副 MCU 同时在用总线
- 观测: 副 MCU 事务是否被打断
- 期望: 如果多 master recovery 启用, 副 MCU 应该看到 STOP 并优雅退出
```

## 常见多 master 系统的反模式

### 反模式 1: 假设自己是唯一 master

```c
/* 错 */
void i2c_xfer_done(int status) {
    if (status == -ETIMEDOUT) {
        schedule_recovery();  /* 假设自己是唯一 master, 暴力恢复 */
    }
}

/* 对 */
void i2c_xfer_done(int status) {
    if (status == -ETIMEDOUT) {
        if (is_only_master()) {
            schedule_recovery();
        } else {
            wait_for_bus_owner_to_handle();
        }
    }
}
```

### 反模式 2: 调试口直接暴露到生产 I2C

```c
/* 错 */
I2C0_SCL/SDA -- 直接连到测试点
             -- 也连到生产 sensor

/* 对 */
生产 I2C 总线 -- 不暴露
调试 I2C 总线 -- 单独走, 或者通过 MUX
MUX 通道在生产模式下常闭
```

### 反模式 3: PMIC 内部 master 被忽略

部分 PMIC (例如某些 BQ 系列) 自带 master, 用于内部 fuel gauge 通信。如果 MCU 不感知, 仲裁失败就被当成 "I2C 卡死" 误恢复。

```c
/* 对: 查 PMIC 手册, 在 PMIC 通信时先 disable 内部 master */
/* 或者: 在 recovery 逻辑里, 列出 "已知 secondary master 列表" */
struct i2c_known_secondary_master {
    uint8_t addr;
    const char *name;
    bool is_secondary_master;  /* 这个地址是 master, 不是 slave */
};
```

## 总结: 多 master 系统的"安全清单"

```text
□ 画出当前系统所有可能的 I2C master (含外部夹具/PMIC/EC/上位机)
□ 关键外设不暴露到外部可达的 I2C 总线
□ 调试/测试口走 MUX, 生产模式下关闭
□ 仲裁失败时退避重试, 不要立刻触发 recovery
□ 只有一个 master 负责 recovery (owner 选举)
□ 写进代码注释, 标明 "此 bus 有 secondary master: XXX"
□ 产线测试包含: 外部 master 干扰场景
□ 文档说明 recovery 行为: "此 bus 多 master, recovery 需要 owner 选举"
```

## 关联文档

- `i2c-deep-dive.md` 总线恢复基础
- `i2c-bus-recovery-playbook.md` 单 master 恢复 SOP
- `i2c-state-machine.md` 状态机
- NXP UM10204 第 16 节: Multi-master
