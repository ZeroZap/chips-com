# CAN vs 其他总线对比

## 目标

把 CAN 和其他常见总线 / 协议做横向对比, 帮助:
- 新项目选型
- 老系统升级路径
- 跨协议桥接设计
- 培训新人理解 CAN 的定位

## 一句话核心差异

> **CAN 是"可靠的实时多 master 现场总线", 强在错误检测、仲裁和实时性, 但速度和带宽有限。I2C/SPI 是板内通信, UART/RS485 是异步串行, Ethernet 是网络通信——每种总线有各自的优势场景。**

## 横向对比表

### 完整对比 (12 维度)

| 维度 | CAN | I2C | SPI | UART | RS485 | Ethernet |
| --- | --- | --- | --- | --- | --- | --- |
| 速度 | 1M-5M | < 3.4M | 10M-200M | < 6M | < 1M | 10M-10G |
| 物理层 | 差分 | 开漏单端 | 推挽单端 | 推挽单端 | 差分 | 差分 |
| 多 master | 硬件仲裁 | 软件地址 | CS 选主 | 无 | 需协议 | CSMA/CD |
| 错误检测 | 强 (CRC + 5 类) | 弱 (ACK) | 无 | 弱 (parity) | 无 | 强 (CRC) |
| 数据长度 | 0-64B | 任意 | 任意 | 任意 | 任意 | 0-1500B |
| 距离 | 1km (低速) | 短 | 短 | 1m | 1200m | 100m |
| 节点数 | 32-256 | 多个 | 多个 (CS) | 2 | 32 | 254 / IPv4 |
| 实时性 | 高 (仲裁) | 中 | 高 | 低 | 中 | 中 (QoS) |
| 成本 | 中 | 低 | 低 | 低 | 低 | 中 |
| 复杂度 | 中 | 低 | 低 | 低 | 中 | 高 |
| 典型应用 | 汽车/工业 | 板内 | Flash/LCD | 调试 | 工业长距离 | 网络 |
| 演进 | CAN FD / XL | I3C | QSPI | USB CDC | - | TSN |

### 选型决策矩阵

```text
场景                       推荐总线     理由
────────────────────────────────────────────────────────
板内 sensor 通信           I2C         简单, 多设备
板内 Flash / LCD           SPI         高速
汽车 ECU / 动力总成         CAN         实时, 可靠
商用车 (卡车 / 巴士)        CAN + J1939
工业设备 (PLC / 电机)       CANopen / RS485
建筑自动化                 RS485 + Modbus
调试口                     UART        printf
长距离 (>10m)              RS485 / CAN
网络通信                   Ethernet    TCP/IP
视频 / 大数据              Ethernet / USB 3.0
```

## CAN vs I2C

| 维度 | CAN | I2C |
| --- | --- | --- |
| 物理层 | 差分 | 开漏单端 |
| 速度 | 1M-5M | < 3.4M |
| 多 master | 硬件仲裁 | 软件地址 |
| 实时性 | 高 (仲裁确定优先级) | 中 (地址轮询) |
| 距离 | 1km (低速) | 短 (< 30cm) |
| 错误检测 | 强 (5 类) | 弱 (1 类) |
| 节点数 | 32-256 | 多个 (地址 7/10 bit) |
| 成本 | 中 | 低 |
| 复杂度 | 中 | 低 |

**关键差异**: CAN 是"差分 + 强错误检测 + 硬件仲裁"的车规/工规总线; I2C 是"开漏 + 地址 + 多 master" 的板内总线。

**选型**:
- 板内 1-2 个 sensor → I2C
- 板间 / 实时多节点 → CAN
- 短距离 (< 1m) 实时 → CAN 或 I2C (看速度)

### 共同点
- 都有多 master 能力
- 都有错误检测
- 都能跑"长距离" (CAN 1km, I2C 30cm)

### I2C 转 CAN 桥接

```c
/* 典型应用: 板内用 I2C sensor, 板间用 CAN */
/* 桥接 MCU 接收 I2C sensor 数据, 通过 CAN 发给其他节点 */

void i2c_to_can_bridge() {
    uint8_t sensor_data[8];
    
    /* I2C 读 sensor */
    i2c_read(SENSOR_ADDR, SENSOR_REG, sensor_data, 8);
    
    /* CAN 发 */
    can_send(CAN_BRIDGE_ID, sensor_data, 8);
}
```

## CAN vs SPI

| 维度 | CAN | SPI |
| --- | --- | --- |
| 速度 | 1M-5M | 10M-200M |
| 物理层 | 差分 | 推挽单端 |
| 距离 | 1km | 短 (< 30cm) |
| 多 master | 硬件仲裁 | CS 选主 |
| 节点数 | 32-256 | 多个 (CS 引脚) |
| 实时性 | 高 | 极高 |
| 错误检测 | 强 | 无 |
| 典型应用 | 汽车/工业 | Flash / LCD / 高速 ADC |

**关键差异**: CAN 是"分布式总线", SPI 是"点对点或点对多"。CAN 强在多节点 + 错误检测, SPI 强在速度。

**选型**:
- 单个高速设备 (Flash / LCD / sensor) → SPI
- 多个 ECU 联网 → CAN
- 板内高速 + 板间实时 → SPI + CAN

### SPI 转 CAN 桥接

```c
/* 典型应用: 板内有 SPI Flash, 板间用 CAN 共享数据 */

void spi_to_can_bridge() {
    /* SPI 读 Flash */
    uint8_t flash_data[64];
    spi_flash_read(FLASH_ADDR, flash_data, 64);
    
    /* CAN 发 (注意: CAN FD 单帧最多 64 字节, 刚好) */
    can_send_fd(CAN_DATA_ID, flash_data, 64);
}
```

## CAN vs UART/RS485

| 维度 | CAN | UART | RS485 |
| --- | --- | --- | --- |
| 速度 | 1M-5M | < 6M | < 10M |
| 物理层 | 差分 | 推挽 | 差分 |
| 距离 | 1km | 1m | 1200m |
| 多 master | 硬件仲裁 | 无 | 软件协议 |
| 错误检测 | 强 | 弱 (parity) | 弱 |
| 实时性 | 高 | 低 | 中 |
| 协议复杂度 | 中 | 简单 | 中 |
| 成本 | 中 | 低 | 低 |

**关键差异**: CAN 是"硬件仲裁的实时总线", RS485 是"半双工长距离串口"。

**选型**:
- 实时多节点 (汽车) → CAN
- 长距离 (1km) 异步通信 → RS485
- 调试口 → UART

### 共同点
- 都是异步 / 帧式通信
- 都用差分 (CAN 和 RS485)
- 都需要终端电阻 (CAN 120 ohm, RS485 120 ohm)

### CAN 转 RS485 桥接

```c
/* 典型应用: 老设备用 RS485 Modbus, 新系统用 CAN */

void can_to_rs485_bridge() {
    struct can_frame frame;
    can_recv(&frame);
    
    /* 转发到 RS485 (Modbus 协议) */
    uint8_t modbus_pdu[256];
    int len = encode_can_to_modbus(&frame, modbus_pdu);
    
    rs485_send(modbus_pdu, len);
}
```

## CAN vs Ethernet

| 维度 | CAN | CAN FD | CAN XL | Ethernet |
| --- | --- | --- | --- | --- |
| 速度 | 1M-5M | 2M-5M | 10M+ | 10M-10G |
| 数据长度 | 0-8B | 0-64B | 1-2048B | 0-1500B |
| 距离 | 1km | 100m | 40m | 100m |
| 实时性 | 极高 | 极高 | 高 | 中 (QoS) |
| 协议栈 | 简单 | 简单 | 中 | 复杂 (TCP/IP) |
| 成本 | 低 | 中 | 高 | 中 |
| 应用 | 实时控制 | 实时 + 较大数据 | 高速主干 | 网络 |

**关键差异**: CAN/CAN FD 是"实时控制总线", Ethernet 是"网络"。CAN 强在确定性和简单, Ethernet 强在带宽和标准化。

**选型**:
- 实时控制 (< 1ms 确定性) → CAN
- 高速主干 / 视频 → Ethernet
- 复杂协议 / 远程访问 → Ethernet
- ECU 域内通信 → CAN FD
- ECU 域间通信 → Ethernet

### CAN 与 Ethernet 共存

```text
现代汽车网络架构:
  ADAS 域:     Ethernet (高速, 大数据)
  动力总成域:   CAN FD (实时, 可靠)
  车身域:      CAN / LIN (低成本)
  信息娱乐域:   Ethernet (多媒体)
  
域控制器:   跨域桥接 (CAN <-> Ethernet)
  - CAN -> CAN over IP (CoAP / SOME/IP)
  - 协议转换网关
```

## CAN vs LIN

| 维度 | CAN | LIN |
| --- | --- | --- |
| 速度 | 1M | 20K |
| 多 master | 是 | 否 (单 master 多 slave) |
| 错误检测 | 强 | 弱 (checksum) |
| 成本 | 中 | 低 |
| 节点数 | 32-256 | 16 (典型 < 8) |
| 应用 | 实时控制 | 车身 (雨刷, 窗, 灯) |

**关键差异**: CAN 是"实时多 master 总线", LIN 是"低成本单 master 总线"。

**选型**:
- 高实时性, 多节点 → CAN
- 低成本, 简单 sensor / 开关 → LIN

LIN 是 CAN 的简化版, 用于对实时性要求不高的低成本场景。

## CAN vs FlexRay

| 维度 | CAN | CAN FD | FlexRay |
| --- | --- | --- | --- |
| 速度 | 1M | 5M | 10M |
| 时间触发 | 无 | 无 | 有 (TDMA) |
| 双通道 | 无 | 无 | 有 (冗余) |
| 实时性 | 仲裁 | 仲裁 | 时间片 |
| 应用 | 普通 | 普通 | 高级驾驶 (X-by-Wire) |
| 复杂度 | 中 | 中 | 高 |
| 状态 | 主流 | 主流 | 已被 Ethernet 替代 |

**关键差异**: FlexRay 强在时间确定性和双通道冗余, 用于 X-by-Wire (线控)。但被 Ethernet TSN 替代, 现在用得少。

**选型**:
- 普通 ECU → CAN / CAN FD
- X-by-Wire (转向, 制动) → FlexRay (老) 或 Ethernet TSN (新)

## CAN vs CAN FD 决策

| 场景 | 推荐 |
| --- | --- |
| 现有 CAN 2.0 网络 | 保持经典 CAN |
| 新设计, 简单 sensor | 经典 CAN |
| 新设计, 多节点 + 中等数据 | CAN FD |
| 固件下载, 大数据 (e.g. ECU 升级) | CAN FD |
| 高速主干 (> 5M) | CAN XL (评估) |

## CAN vs I3C (新一代 I2C)

| 维度 | CAN | I3C |
| --- | --- | --- |
| 物理层 | 差分 | 开漏 / 推挽混合 |
| 速度 | 1M-5M | 12.5M (SDR), 25M (HDR-DDR) |
| 多 master | 是 | 是 (动态地址) |
| 错误检测 | 强 | 中 |
| 距离 | 1km | 短 (板内) |
| 节点数 | 32-256 | 多个 (动态地址) |
| 应用 | 汽车/工业 | sensor hub / 移动设备 |

**关键差异**: CAN 是"汽车/工规多节点", I3C 是"移动设备 sensor hub"。两者目标场景不同, 不是直接竞争。

**选型**:
- 汽车 / 工规 → CAN
- 移动 sensor hub → I3C

## CAN vs MOST (Media Oriented Systems Transport)

| 维度 | CAN | MOST |
| --- | --- | --- |
| 应用 | 控制 | 多媒体 |
| 速度 | 1M-5M | 25M-150M |
| 实时性 | 高 | 中 |
| 协议 | 简单 | 复杂 |
| 应用 | ECU 通信 | 车载娱乐 |

**选型**:
- 控制信号 → CAN
- 多媒体 (音频 / 视频) → MOST (老) / Ethernet (新)

## 跨总线桥接设计

### 常见桥接场景

```text
1. CAN <-> Ethernet 网关
   - 应用: 车载 OBD 接口 / 远程诊断 / 大数据上传
   - 实现: MCU 跑 CAN 协议栈 + Ethernet 协议栈, 协议转换

2. CAN <-> RS485 桥
   - 应用: 老 Modbus 设备接入新 CAN 网络
   - 实现: 桥接 MCU, 解析 Modbus 帧, 映射到 CAN ID

3. CAN <-> SPI 桥
   - 应用: 板内 SPI device 通过 CAN 共享
   - 实现: 桥接 MCU, SPI master 读, CAN 发

4. CAN <-> I2C 桥
   - 应用: 板内 I2C sensor 数据通过 CAN 共享
   - 实现: 桥接 MCU, I2C 读, CAN 发
```

### 桥接 MCU 选型

```text
- 资源: 至少 1 路 CAN + 1 路其他接口
- 例: STM32H7 (CAN FD + SPI/I2C + Ethernet)
- 例: ESP32 (CAN + WiFi) -> CAN <-> WiFi 桥
- 例: 国产 GD32F450 / HC32F4A0 (CAN FD + 多接口)
```

## 实战选型决策树

```text
新项目, 需要多节点实时通信
  |
  +-- 距离 < 1m, 节点数 < 10, 速度 < 1M
  |     -> SPI / I2C
  |
  +-- 距离 < 1m, 节点数 >= 10, 速度 < 1M
  |     -> I2C (低速) / SPI (高速)
  |
  +-- 距离 1m-10m, 多节点, 速度 1M-5M
  |     -> CAN
  |
  +-- 距离 1m-10m, 多节点, 速度 > 5M, 大数据
  |     -> CAN FD / CAN XL (评估)
  |
  +-- 距离 10m-1km, 多节点
  |     -> RS485 (低速) / CAN (1km 低速)
  |
  +-- 距离 > 1km, 多节点
  |     -> RS485 + Modbus / CAN 长距离
  |
  +-- 需要 TCP/IP / 远程访问
  |     -> Ethernet / WiFi / 4G
  |
  +-- 多媒体 (视频 / 音频)
        -> Ethernet / USB / HDMI
```

## 7 条选型原则

```text
1. 实时性优先 -> CAN
2. 板内通信, 简单 -> I2C
3. 板内通信, 高速 -> SPI
4. 调试 / 配置 -> UART
5. 长距离, 异步 -> RS485
6. 网络 / TCP/IP -> Ethernet
7. 多媒体 / 高速数据 -> USB / Ethernet / HDMI
```

## 关联文档

- `can-practical.md` 速查
- `can-deep-dive.md` 原理
- `can-failure-cases.md` 产线案例
- `can-multimaster-and-bus-off.md` 多 master
- `can-fd-and-can-xl.md` 演进
- `can-rtos-integration.md` RTOS + Linux
- `can-index.md` 导航
- `bus/can-canopen-deep-dive.md` CANopen (CAN 之上的应用层)
- `bus/j1939-*.md` J1939 (商用车主从)
- `bus/uds-*.md` UDS (诊断)
- `bus/modbus-rs485-*.md` Modbus RS485
- `bus/ethernet-*.md` Ethernet
- `i2c-vs-smbus-recovery.md` 跨协议对比参考
