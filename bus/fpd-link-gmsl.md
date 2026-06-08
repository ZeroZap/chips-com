# FPD-Link / GMSL

## 定位

FPD-Link 和 GMSL 是常见高速串行视频链路，广泛用于车载摄像头和显示屏远距离连接。

它们常用于把摄像头或显示数据通过同轴线或双绞线传输到主控。

## 典型结构

摄像头链路：

```text
Image Sensor -> Serializer -> Cable -> Deserializer -> SoC CSI
```

显示链路：

```text
SoC Display -> Serializer -> Cable -> Deserializer -> Panel
```

## 为什么需要它们

MIPI CSI/DSI 适合板内短距离。

车载摄像头和显示屏通常需要更长线缆和更强抗干扰。

FPD-Link/GMSL 解决：

- 长距离视频传输。
- 供电和控制复用。
- 反向控制通道。
- 车载 EMC 环境。

## 常见配套接口

- MIPI CSI/DSI。
- I2C 控制通道。
- GPIO 同步或复位。
- 同轴供电，视方案而定。

## 工程注意

- Serializer/Deserializer 配对。
- 链路速率和视频格式匹配。
- I2C 透传地址冲突。
- 同轴或双绞线线缆质量。
- EMC 和 ESD 设计。
- 上电时序和远端设备复位。

## 常见故障

| 现象 | 优先检查 |
| --- | --- |
| 远端 I2C 不通 | SerDes 配置、反向通道、地址 |
| 有链路无图 | MIPI 格式、Lane、视频时序 |
| 偶发掉线 | 线缆、连接器、EMC、电源 |
| 多摄像头冲突 | I2C 地址、虚拟通道、同步配置 |

## 延伸阅读

- `bus/mipi-csi-dsi-deep-dive.md`
- `bus/display-interfaces.md`
