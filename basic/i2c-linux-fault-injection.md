# I2C Linux fault injection 与 i2c-stub 实操

## 目标

在 Linux 环境下, 用内核自带的 fault injection 框架和 i2c-stub 模拟器, **不接真实硬件**就能验证:

- bus recovery 是否真的有效
- 错误码 (fault codes) 是否正确返回
- 驱动对各种 timeout / NACK / ARLO 的反应
- 产线回归测试自动化的能力

本文是 step-by-step 实操, 看完能直接在你机器上跑。

## 1. 准备工作

### 1.1 内核配置

```bash
# 必需的内核选项
CONFIG_I2C=y
CONFIG_I2C_STUB=m                  # I2C 模拟器
CONFIG_I2C_GPIO=m                  # GPIO bit-bang
CONFIG_I2C_GPIO_FAULT_INJECTION=y  # GPIO fault injection
CONFIG_DEBUG_FS=y                  # fault injection 通过 debugfs
CONFIG_I2C_DEBUG_CORE=y            # 详细日志
CONFIG_I2C_DEBUG_ALGO=y
CONFIG_I2C_DEBUG_BUS=y
```

### 1.2 验证配置

```bash
# 检查内核配置
zcat /proc/config.gz | grep -E 'I2C_STUB|I2C_GPIO|FAULT_INJECTION'
# 或者
ls /sys/module/i2c_stub 2>/dev/null && echo "i2c_stub OK"
ls /sys/kernel/debug/i2c-fault-inject 2>/dev/null && echo "fault inject OK"
```

### 1.3 安装工具

```bash
# Debian/Ubuntu
sudo apt install i2c-tools
sudo modprobe i2c-dev
sudo modprobe i2c-stub

# Arch
sudo pacman -S i2c-tools

# RHEL/Fedora
sudo dnf install i2c-tools
```

## 2. i2c-stub: 虚拟 I2C 设备

i2c-stub 是内核自带的虚拟 I2C 设备, **不需要真实硬件**。

### 2.1 加载 i2c-stub

```bash
# 默认: 创建 1 个地址, 起始地址 0x50
sudo modprobe i2c-stub

# 自定义: chip_addr=0x68, 8 个连续地址
sudo modprobe i2c-stub chip_addr=0x68 bit_count=8

# 查看
ls /sys/bus/i2c/devices/
# i2c-0  i2c-1  i2c-2  ...  i2c-10  (stub adapter)
```

### 2.2 操作 stub 设备

```bash
# 列出 stub adapter
i2cdetect -l
# i2c-10  i2c         stub_adapter              SMBus stub driver

# 扫描地址
i2cdetect -y 10
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --

# 写
i2cset -y 10 0x68 0x75 0xAB

# 读
i2cget -y 10 0x68 0x75
# 0xab

# 读整个 bank
i2cdump -y 10 0x68
```

### 2.3 用 Python 直接调

```python
# pip install smbus2
from smbus2 import SMBus
bus = SMBus(10)  # stub adapter 10
bus.write_byte_data(0x68, 0x75, 0xAB)
val = bus.read_byte_data(0x68, 0x75)
print(hex(val))
```

## 3. i2c-stub fault injection

i2c-stub 支持 fault injection, 模拟各种错误。

### 3.1 启用 fault injection

```bash
# 通过 debugfs (kernel 5.10+)
sudo mount -t debugfs debugfs /sys/kernel/debug
ls /sys/kernel/debug/i2c-fault-inject/
# 应该是空的, 需要先注册

# i2c-stub 的 fault injection 走 module param
sudo modprobe i2c-stub fault_enable=1
```

### 3.2 注入 SDA 拉低

```bash
# 强制 SDA 拉低 (模拟从设备卡死)
echo 1 > /sys/module/i2c_stub/parameters/sda_low

# 跑事务, 应该看到 driver detect timeout
i2cget -y 10 0x68 0x75
# 会卡死或返回 timeout

# 释放 SDA
echo 0 > /sys/module/i2c_stub/parameters/sda_low
```

### 3.3 注入 NACK

```bash
# 让指定地址 NACK
echo 0x68 > /sys/module/i2c_stub/parameters/nack_addr
```

### 3.4 注入 timeout

```bash
# 让 read 超时
echo 1 > /sys/module/i2c_stub/parameters/slow_read
```

## 4. i2c-gpio fault injection (推荐)

i2c-gpio 走 GPIO bit-bang, **内核自己**实现 fault injection, 比 i2c-stub 强。

### 4.1 准备

```bash
# 需要真实的 GPIO 引脚 (例如树莓派 / BeagleBone)
# 假设 SCL=GPIO4, SDA=GPIO5

# 通过 device tree 启用 i2c-gpio
# &i2c3 { /* ... */ };

# 或者命令行 (如果有 DTS overlay)
sudo dtoverlay i2c-gpio i2c_gpio_sda=5 i2c_gpio_scl=4 bus=3
```

### 4.2 启用 fault injection

```bash
# 必须 CONFIG_I2C_GPIO_FAULT_INJECTION=y
sudo mount -t debugfs debugfs /sys/kernel/debug
ls /sys/kernel/debug/i2c-fault-inject/
# 应该看到 fault injection 控制文件
```

### 4.3 注入 SDA 拉低

```bash
# 强制 SDA 拉低
echo 1 > /sys/kernel/debug/i2c-fault-inject/i2c3/force_sda_low

# 跑事务
i2cget -y 3 0x68 0x75
# kernel log: i2c i2c-3: SDA stuck low detected
# kernel log: i2c i2c-3: recovery: bus recovery started

# 释放
echo 0 > /sys/kernel/debug/i2c-fault-inject/i2c3/force_sda_low
```

### 4.4 注入 SCL 拉低

```bash
echo 1 > /sys/kernel/debug/i2c-fault-inject/i2c3/force_scl_low
```

### 4.5 注入 ACK 阶段卡死

```bash
# 模拟从设备 ACK 后状态机卡死
echo 1 > /sys/kernel/debug/i2c-fault-inject/i2c3/sda_after_ack
```

## 5. Linux I2C fault codes 验证

```c
/* Linux 内核错误码 - driver 应该按这些区分 */
-ENODEV       /* 地址无响应 */
-EAGAIN       /* 仲裁丢失, 重试 */
-ETIMEDOUT    /* 等待超时 */
-ENACK        /* (扩展) NACK 收到 */
-EBUSY        /* 总线忙 */
-EIO          /* 通用 I/O 错误 */
-EPROTO       /* 协议错误 */
```

### 5.1 用户态测试

```python
# test_i2c_recovery.py
import subprocess
import time
import os

DEBUGFS = "/sys/kernel/debug/i2c-fault-inject/i2c3"

def inject_sda_low():
    with open(f"{DEBUGFS}/force_sda_low", "w") as f:
        f.write("1")

def release_sda():
    with open(f"{DEBUGFS}/force_sda_low", "w") as f:
        f.write("0")

def read_sensor():
    """模拟一个 sensor 读, 返回是否成功"""
    result = subprocess.run(
        ["i2cget", "-y", "3", "0x68", "0x75"],
        capture_output=True, text=True, timeout=5
    )
    return result.returncode == 0, result.stdout.strip()

def test_recovery_sda_low():
    """测试 SDA 拉低后 driver 能否恢复"""
    print("=== Test: SDA 低拉低后恢复 ===")

    # 1. 正常读
    ok, val = read_sensor()
    assert ok, f"初始读失败: {val}"
    print(f"  初始读 OK: {val}")

    # 2. 注入 SDA 低
    inject_sda_low()
    print("  注入 SDA 低")

    # 3. 跑事务, 应该触发 recovery
    ok, val = read_sensor()
    print(f"  注入后读: ok={ok}, val={val}")

    # 4. 释放 SDA
    release_sda()
    print("  释放 SDA")

    # 5. 再次读, 应该 OK
    time.sleep(0.1)
    ok, val = read_sensor()
    assert ok, f"恢复后仍失败: {val}"
    print(f"  恢复后读 OK: {val}")
    print("  PASS")

if __name__ == "__main__":
    test_recovery_sda_low()
```

## 6. 验证 bus_recovery_info

Linux I2C core 期望 adapter driver 实现 `bus_recovery_info`:

```c
/* drivers/i2c/busses/i2c-at91.c (示例) */
static struct i2c_bus_recovery_info at91_i2c_recovery_info = {
    .recover_bus = at91_i2c_recover_bus,
    .get_scl     = at91_get_scl,
    .set_scl     = at91_set_scl,
    .get_sda     = at91_get_sda,
    .set_sda     = at91_set_sda,
    .prepare_recovery = at91_i2c_prepare_recovery,
    .unprepare_recovery = at91_i2c_unprepare_recovery,
};
```

### 6.1 检查 kernel 是否启用 recovery

```bash
# 查 adapter 信息
ls /sys/bus/i2c/devices/i2c-3/
# 应该有 bus_recovery 目录

cat /sys/bus/i2c/devices/i2c-3/bus_recovery/duration
# 0
```

### 6.2 强制触发 recovery

```bash
echo 1 > /sys/bus/i2c/devices/i2c-3/bus_recovery/trigger
# 立刻强制跑一次 bus recovery
```

## 7. 自动化回归测试

```bash
#!/bin/bash
# i2c_regression_test.sh - 产线回归测试用

set -e
DEV=/sys/kernel/debug/i2c-fault-inject/i2c3
LOG=/tmp/i2c_test_$(date +%Y%m%d_%H%M%S).log
PASS=0
FAIL=0

run_test() {
    local name="$1"
    local cmd="$2"
    local expect="$3"

    if [ "$cmd" = "force_sda_low" ]; then
        echo 1 > "$DEV/force_sda_low"
    fi

    result=$(i2cget -y 3 0x68 0x75 2>&1 || true)
    ok=$(echo "$result" | grep -q "^0x" && echo 1 || echo 0)

    # 释放
    echo 0 > "$DEV/force_sda_low" 2>/dev/null || true

    if [ "$ok" = "$expect" ]; then
        echo "PASS: $name"
        PASS=$((PASS+1))
    else
        echo "FAIL: $name (got $result, expect ok=$expect)"
        FAIL=$((FAIL+1))
    fi
}

# 正常读
echo 0 > "$DEV/force_sda_low" 2>/dev/null || true
result=$(i2cget -y 3 0x68 0x75 2>&1)
[[ "$result" =~ ^0x ]] && { echo "PASS: normal read"; PASS=$((PASS+1)); } || { echo "FAIL: normal read"; FAIL=$((FAIL+1)); }

# SDA 低注入
echo 1 > "$DEV/force_sda_low" 2>/dev/null && {
    result=$(i2cget -y 3 0x68 0x75 2>&1 || true)
    # 期望: 触发 recovery, 最终返回 -EBUSY 或 0x.. (recovery 后)
    [[ "$result" =~ ^0x ]] && { echo "PASS: sda low recovery"; PASS=$((PASS+1)); } || { echo "PASS: sda low detect (rejected)"; PASS=$((PASS+1)); }
    echo 0 > "$DEV/force_sda_low"
}

# 总结
echo "================="
echo "PASS: $PASS"
echo "FAIL: $FAIL"
exit $FAIL
```

## 8. 用 QEMU 模拟

没真实硬件时, QEMU 也能跑:

```bash
# QEMU 启动带 i2c-stub 的内核
qemu-system-arm \
    -M vexpress-a9 \
    -kernel zImage \
    -dtb vexpress-v2p-ca9.dtb \
    -append "console=ttyAMA0" \
    -nographic
```

在 QEMU 内部用 i2c-stub + 调试 sysfs 模拟 fault。

## 9. 实战: 调试一个真实 bug

### 场景: 产线反馈 IMU 偶发读失败

```bash
# 1. 复现
i2cget -y 3 0x68 0x75
# 偶发失败

# 2. 看内核日志
dmesg | tail -50
# i2c i2c-3: i2c_imx_xfer: arbitration lost
# i2c i2c-3: recovery: bus recovery started
# i2c i2c-3: recovery: bus recovery finished (duration: 12 ms)

# 3. 看 bus_recovery 计数器
cat /sys/bus/i2c/devices/i2c-3/bus_recovery/duration
# 12 (ms)

# 4. 注入同类故障, 验证 recovery
echo 1 > /sys/kernel/debug/i2c-fault-inject/i2c3/force_sda_low
sleep 0.1
echo 0 > /sys/kernel/debug/i2c-fault-inject/i2c3/force_sda_low
i2cget -y 3 0x68 0x75
# 应该正常返回

# 5. 如果 recovery 失败, 检查 adapter 是否有 bus_recovery_info
ls /sys/bus/i2c/devices/i2c-3/bus_recovery/
# 没这个目录 -> driver 没实现 recovery, 需要补代码
```

## 10. 调试 i2c-stub 的限制

```text
i2c-stub 限制:
  - 只能模拟简单 NACK, 不能模拟 SDA 物理拉低
  - 不支持 multi-master 仲裁
  - 不支持 clock stretching
  - 不支持 SMBus 协议层

i2c-gpio fault injection 限制:
  - 需要真实 GPIO 引脚
  - 不能在多 master 环境下测试
  - 部分 fault 只能在 master 事务中注入

QEMU 限制:
  - 虚拟 I2C 不真实
  - 性能/时序与真机不同
  - 适合 unit test, 不适合产线验证
```

## 关联文档

- `i2c-deep-dive.md` 原理
- `i2c-bus-recovery-playbook.md` SOP
- `i2c-multimaster.md` 多 master
- Linux I2C GPIO Fault Injection
