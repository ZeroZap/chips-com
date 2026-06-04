# SMBus

## 定位

SMBus 是 System Management Bus，基于 I2C 思想，面向系统管理场景。

常见于：

- 智能电池。
- 温度传感器。
- 风扇控制器。
- 主板管理。
- BMC。

## 与 I2C 的关系

SMBus 比普通 I2C 更强调：

- 标准事务。
- 超时。
- PEC。
- SMBALERT#。
- Host Notify。

## 延伸阅读

- `bus/smbus-pmbus-practical.md`
