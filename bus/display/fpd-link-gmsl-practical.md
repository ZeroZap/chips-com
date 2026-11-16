# FPD-Link / GMSL Practical Guide

## 目标

本文用于车载视频 SerDes 工程调试，重点覆盖 Serializer/Deserializer 配对、远端 I2C、MIPI 桥接、链路锁定、同轴/双绞线、电源时序和多摄像头问题。

## 典型摄像头链路

```text
Image Sensor
  -> MIPI CSI
  -> Serializer
  -> Cable
  -> Deserializer
  -> MIPI CSI
  -> SoC
```

控制链路通常通过 SerDes 提供 I2C 透传或反向通道。

## 调试顺序

1. 确认本地 Deserializer 可通过 I2C 访问。
2. 确认远端 Serializer 链路锁定。
3. 确认远端 Sensor 电源和复位。
4. 通过反向通道读取 Sensor ID。
5. 配置 Sensor 输出。
6. 配置 SerDes 视频格式和 Lane。
7. 配置 SoC CSI Receiver。
8. 验证图像输出。

## I2C 透传

常见问题：

- 本地和远端 I2C 地址冲突。
- 地址别名配置错误。
- 反向通道未启用。
- 远端设备未上电。

多摄像头系统尤其要规划地址映射。

## 链路锁定

SerDes 通常有 link lock 状态。

无 lock 时优先检查：

- 线缆。
- 连接器。
- 供电。
- SerDes 配对型号。
- 速率配置。
- 同轴供电。

## MIPI 桥接

SerDes 两侧可能都涉及 MIPI：

```text
Sensor -> Serializer：MIPI CSI
Deserializer -> SoC：MIPI CSI
```

两侧 Lane 数、速率、VC、DT 都要匹配。

## 常见故障

| 现象 | 优先检查 |
| --- | --- |
| Deserializer 可见但无远端 | Link lock、线缆、Serializer 电源 |
| 远端 I2C 不通 | 反向通道、地址别名、Sensor 复位 |
| 有 lock 无图 | MIPI 格式、Lane、Sensor streaming |
| 多摄像头冲突 | I2C 地址、VC、同步、带宽 |
| 行车环境偶发掉线 | 线缆、EMC、连接器、电源瞬态 |

## 检查清单

- SerDes 型号配对。
- Link lock 稳定。
- 远端 I2C 可访问。
- Sensor ID 可读取。
- MIPI Lane 和格式一致。
- 多路系统地址和 VC 不冲突。
- 线缆和连接器满足车载环境要求。
