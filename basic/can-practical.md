# CAN Practical Guide

## 目标

本文用于 CAN 工程调试: 接线、波特率、帧格式、收发器选型、错误定位和常见故障。

## 最小接线

```text
CAN_H <-> CAN_H (收发器输出)
CAN_L <-> CAN_L (收发器输出)
GND  <-> GND    (必须共地)
```

**关键约束**:

- CAN 总线两端各加 120 ohm 终端电阻
- 总线最长 40m @ 1M baud (CAN)
- CAN FD 高速档 (>1M) 距离更短
- 必须共地, 工业现场用屏蔽双绞线
- CAN_H 和 CAN_L 是差分信号, 走线必须双绞

## 关键参数

### 波特率 vs 距离

| 波特率 | 最大距离 | 典型场景 |
| --- | --- | --- |
| 1 Mbaud | 40 m | 车内部 |
| 500 kbaud | 100 m | 工业设备 |
| 250 kbaud | 250 m | 长距离设备 |
| 125 kbaud | 500 m | 楼宇 / 远距离 |
| 50 kbaud | 1 km | 现场总线 |

### 帧类型

```text
数据帧 (Data Frame):     发送数据, 标准用法
远程帧 (Remote Frame):   请求数据, 已被 CAN FD 废弃
错误帧 (Error Frame):    节点发现错误, 强制发送
过载帧 (Overload Frame):  接收方未准备好, CAN 中保留, CAN FD 移除
帧间隔 (Interframe Space): 帧之间的间隔
```

### 标准 vs 扩展 ID

| 模式 | ID 长度 | 节点数 | 备注 |
| --- | --- | --- | --- |
| CAN 2.0A | 11 bit | 2048 | 标准帧 |
| CAN 2.0B | 29 bit | 5 亿+ | 扩展帧 |
| CAN FD | 11/29 bit | 同上 | 数据段 0-64 字节 |
| CAN XL | 11/29 bit | 同上 | 数据段 1-2048 字节 |

## 收发器选型

### 关键参数

```text
1. 速率: 1M / 2M / 5M (CAN FD)
2. 故障保护: 是否支持 ±70V 总线故障
3. 隔离: 无 / 数字隔离 / 磁隔离
4. 功耗: 待机电流 (车规要求 < 100uA)
5. ESD: ±15kV (工业) / ±8kV (消费)
```

### 典型收发器

| 型号 | 速率 | 隔离 | 故障保护 | 备注 |
| --- | --- | --- | --- | --- |
| TJA1050 | 1M | 无 | ±60V | 老款, 经典 |
| TJA1042 | 1M | 无 | ±58V | NXP 主推 |
| TJA1057 | 1M | 无 | ±58V | 低功耗 |
| TJA1443 | 5M | 无 | ±70V | CAN FD |
| SN65HVD230 | 1M | 无 | ±36V | TI |
| SN65HVD257 | 5M | 无 | ±70V | TI CAN FD |
| ISO1050 | 1M | 磁隔离 | ±60V | TI 隔离 |
| ADM3053 | 1M | 数字隔离 | ±25V | ADI 隔离 |
| IFX1051LE | 1M | 无 | ±40V | Infineon |

## 调试步骤

1. **量总线电阻**: 总线两端 120 ohm 电阻并联, 量 A-B 之间应该 60 ohm
2. **量总线电平**:
   - 隐性 (idle): CAN_H ≈ CAN_L ≈ 2.5V
   - 显性 (dominant, 数据 0): CAN_H ≈ 3.5V, CAN_L ≈ 1.5V
   - 差分电压 ≥ 0.9V (dominant) / ≤ 0.5V (recessive)
3. **跑 1 Mbaud 短距离 (1m)** 先验证
4. **用 CAN 分析仪** (如 PEAK CAN, Vector VN1610) 抓帧
5. **看错误计数器**: TEC (发送) / REC (接收), > 96 进入 error passive
6. **逐个节点断开**, 定位哪个节点让总线异常

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| 完全没数据 | 终端电阻 / 收发器供电 / 接线 / 波特率 |
| 错误帧多 | 波特率不匹配 / 终端电阻错 / 总线短路 |
| 偶发丢帧 | 干扰 / 电磁兼容 / 屏蔽 / 接地 |
| 节点一直 error passive | 这个节点收发器坏 / MCU CAN 控制器配置错 |
| 总线关闭 (bus off) | 节点错误率太高, 自动脱离总线 |
| CAN FD 跑不通 | 收发器不支持 CAN FD / 物理层参数错 |

## 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 完全没数据 | 终端电阻 / 收发器供电 | 量 60 ohm, 量 VCC |
| 错误帧多 | 波特率不匹配 / 终端 | 逐个节点断开测试 |
| 节点 bus off | 错误率超限 | 查 TEC/REC, 复位节点 |
| CAN FD 跑不通 | 收发器不支持 | 查收发器型号 |
| 偶发丢帧 | 干扰 / 屏蔽 | 示波器看波形 |
| 只能收不能发 | ACK 机制 / 总线冲突 | 检查其他节点 |
| 多节点冲突 | 总线仲裁 / 配置错 | 用 CAN 分析仪 |

## 速率档位

```text
低速档 (调试):       125 kbaud, 250 kbaud
中速档 (多数应用):    500 kbaud
高速档 (汽车):       1 Mbaud
超高速 (CAN FD):    2 Mbaud, 5 Mbaud
```

## 终端电阻详解

### 必备: 总线两端 120 ohm

```text
Node A --- CAN_H ----- CAN_H --- ... --- CAN_H --- Node B
           CAN_L ----- CAN_L --- ... --- CAN_L
       
[120 ohm]                                  [120 ohm]
   A-B                                        A-B
```

### 量总线电阻

```text
电源断开, 节点保持接在总线上
量 CAN_H 和 CAN_L 之间电阻
期望: 60 ohm (两个 120 ohm 并联)
```

**如果**:

- 量到 120 ohm → 只有 1 个终端电阻, 缺 1 个
- 量到 40 ohm → 有 3 个终端电阻, 多 1 个
- 量到 0 ohm → 总线短路
- 量到无穷大 → 总线开路 / 收发器没接

### 何时不要终端电阻

- 总线极短 (< 1m), 2 个节点
- 用 split termination (收发器内置) 替代

## CAN 错误码

| 错误 | 触发 |
| --- | --- |
| 位错误 (Bit Error) | 发送的位和监听到的位不一致 |
| 填充错误 (Stuff Error) | 连续 5 个相同位后未插入反相位 |
| CRC 错误 (CRC Error) | 接收方 CRC 校验失败 |
| 形式错误 (Form Error) | 固定格式位错 |
| 应答错误 (ACK Error) | 发送方未收到 ACK |

错误计数器:
- TEC (Transmit Error Counter)
- REC (Receive Error Counter)
- TEC/REC > 127 → error passive
- TEC > 255 → bus off

## DMA 触发

```text
适合 DMA:
  - 高负载 (>= 50% 总线利用率)
  - 多节点接收 (过滤多 ID)
  - 大数据帧 (CAN FD 64 字节)

不适合 DMA:
  - 低速 (< 125 kbaud)
  - 单节点接收
  - 调试 (排障)
```

## 物理层检查清单

```text
□ 总线两端 120 ohm 终端电阻
□ CAN_H 和 CAN_L 差分电平符合规范
□ 收发器供电正常 (VCC, 多数 5V)
□ 总线共地
□ 屏蔽双绞线 (工业)
□ 走线避开噪声源
□ 收发器旁路电容近 (100nF + 10uF)
□ 隔离芯片两端独立电源
□ 节点数 <= 收发器支持 (多数 32, 高速收发器支持更多)
```

## 错误码细分 (Linux SocketCAN)

```c
/* Linux net/can/error.h 定义的错误码 */
#define CAN_ERR_TX_TIMEOUT   0x00000001U  // TX 超时
#define CAN_ERR_LOSTARB      0x00000002U  // 仲裁失败
#define CAN_ERR_CRTL         0x00000004U  // 控制器状态变化
#define CAN_ERR_PROT         0x00000008U  // 协议违规
#define CAN_ERR_TRX          0x00000010U  // 收发器状态
#define CAN_ERR_ACK          0x00000020U  // ACK 错误
#define CAN_ERR_BUSOFF       0x00000040U  // 总线关闭
#define CAN_ERR_BUSERROR     0x00000080U  // 总线错误
#define CAN_ERR_RESTARTED    0x00000100U  // 重启
```

## 关联文档

- `can-deep-dive.md` 原理和体系
- `can-failure-cases.md` 产线死机案例
- `can-multimaster-and-bus-off.md` 多 master + 总线关闭
- `can-fd-and-can-xl.md` 演进
- `can-rtos-integration.md` RTOS + SocketCAN
- `can-vs-other-bus.md` 跨总线对比
- `can-index.md` 导航
- `bus/can-canopen-deep-dive.md` CANopen (CAN 之上的应用层协议)
- `bus/can-canopen-practical.md` CANopen 实战
- `basic/can-phy.md` CAN 物理层
