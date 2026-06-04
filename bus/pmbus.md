# PMBus

## 定位

PMBus 是 Power Management Bus，通常建立在 SMBus 上，用于电源控制和监控。

常见于：

- 数字电源。
- VRM。
- 服务器电源。
- 通信电源。
- 热插拔控制器。

## 常见能力

- 读取输入/输出电压。
- 读取电流、功率、温度。
- 设置输出电压。
- 控制开关。
- 读取故障状态。
- 保存配置到 NVM。

## 常见注意点

- Linear11/Linear16 数据格式。
- PAGE 多通道选择。
- WRITE_PROTECT。
- CLEAR_FAULTS。
- NVM 保存流程。

## 延伸阅读

- `bus/smbus-pmbus-practical.md`
