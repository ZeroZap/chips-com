# Modbus

## 定位

Modbus 是工业通信协议，常用于 PLC、仪表、传感器、IO 模块和电机驱动器。

常见形态：

```text
Modbus RTU：常跑在 RS485/RS232 上
Modbus TCP：跑在 TCP/IP 上
Modbus ASCII：较少使用
```

## 数据模型

Modbus 传统数据区：

| 类型 | 访问 | 含义 |
| --- | --- | --- |
| Coil | 读写 bit | 开关量输出 |
| Discrete Input | 只读 bit | 开关量输入 |
| Input Register | 只读 16-bit | 输入寄存器 |
| Holding Register | 读写 16-bit | 保持寄存器 |

## 常用功能码

| 功能码 | 含义 |
| --- | --- |
| 01 | Read Coils |
| 02 | Read Discrete Inputs |
| 03 | Read Holding Registers |
| 04 | Read Input Registers |
| 05 | Write Single Coil |
| 06 | Write Single Register |
| 0F | Write Multiple Coils |
| 10 | Write Multiple Registers |

## 常见坑

- `40001` 和协议地址 `0x0000` 的偏移关系。
- RTU CRC 低字节在前。
- TCP 使用 MBAP，不使用 RTU CRC。
- 32-bit 数据跨寄存器存在 word swap。
- 异常响应功能码为原功能码加 `0x80`。

## 延伸阅读

- `bus/rs485-modbus-rtu-practical.md`
- `bus/rs485-modbus-rtu-deep-dive.md`
- `bus/ethernet-modbus-tcp-practical.md`
