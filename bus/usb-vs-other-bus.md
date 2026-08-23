# USB vs 其他总线对比

## 目标

把 USB 和其他常见总线 / 协议做横向对比, 帮助:
- 新项目选型
- 跨协议桥接设计
- 培训新人理解 USB 的定位

## 一句话核心差异

> **USB 是"PC 时代的标准接口", 强在通用性、类驱动生态和即插即用。但 USB 不是"工业实时总线"或"板内通信总线", 在长距离、实时性、板上多设备等场景不适用。**

## 横向对比表

### 完整对比 (12 维度)

| 维度 | USB | CAN | I2C | SPI | UART |
| --- | --- | --- | --- | --- | --- |
| 速度 | 1.5M / 12M / 480M / 5G | 1M-5M | < 3.4M | 10M-200M | < 6M |
| 物理层 | 差分 (D+/D-) | 差分 (CAN_H/L) | 开漏单端 | 推挽单端 | 推挽单端 |
| 多 master | Host-Device (1 对多) | 硬件仲裁 | 软件地址 | CS 选主 | 无 |
| 错误检测 | 强 (CRC + PID 校验) | 强 (5 类错误) | 弱 (ACK) | 无 | 弱 (parity) |
| 数据长度 | 任意 (Bulk) | 0-64B | 任意 | 任意 | 任意 |
| 距离 | 5m (无 Hub) | 1km (低速) | 短 (< 30cm) | 短 (< 30cm) | RS485 1km |
| 节点数 | 127 (含 Hub) | 32-256 | 多个 | 多个 (CS) | 2 / RS485 32 |
| 实时性 | 中 | 高 | 中 | 高 | 低 |
| 成本 | 中 | 中 | 低 | 低 | 低 |
| 复杂度 | 中 | 中 | 低 | 低 | 低 |
| 典型应用 | PC 外设 / 调试 | 汽车 / 工业 | 板内 sensor | Flash / LCD | 调试 |
| 演进 | USB4, Type-C | CAN FD / XL | I3C | QSPI | USB CDC |

### 选型决策矩阵

```text
场景                            推荐总线     理由
────────────────────────────────────────────────────
PC 外设 (键鼠 / U 盘)            USB         通用, 生态成熟
调试 / printf                  USB CDC / UART 简单, 通用
板内 sensor 通信                I2C          简单, 多设备
板内 Flash / LCD                SPI          高速
汽车 ECU / 动力总成              CAN         实时, 可靠
商用车 (卡车 / 巴士)             CAN + J1939
工业设备 (PLC / 电机)            CANopen / RS485
建筑自动化                     RS485 + Modbus
长距离 (>10m)                  RS485 / CAN
视频 / 大数据                  USB 3.x / Ethernet
多核处理器间通信                SPI / USB / Ethernet
```

## USB vs CAN

| 维度 | USB | CAN |
| --- | --- | --- |
| 速度 | 1.5M / 12M / 480M / 5G | 1M-5M |
| 物理层 | 差分 (D+/D-) | 差分 (CAN_H/L) |
| 多 master | Host-Device (1 对多) | 硬件仲裁 (多 master) |
| 错误检测 | 强 (CRC + PID 校验) | 强 (5 类错误) |
| 距离 | 5m | 1km (低速) |
| 节点数 | 127 (含 Hub) | 32-256 |
| 实时性 | 中 | 高 (确定性) |
| 协议 | 复杂 (类驱动) | 简单 (PGN) |
| 终端 | 1.5k 上拉 (全速) | 120 ohm (两端) |
| 编码 | NRZI + bit stuffing | NRZ + bit stuffing |

**关键差异**:
- USB 是 **Host-Device 模式** (主从), CAN 是 **多 master 仲裁**
- USB 协议栈更复杂 (类驱动), CAN 简单 (PGN)
- CAN 实时性高 (车规关键), USB 通用性高 (PC 外设)

**选型**:
- 汽车 ECU 通信 → **CAN** (实时 + 车规)
- 调试 / 数据采集 → **USB** (PC 通用)
- 工业控制 → **CAN** (实时)
- 消费电子 → **USB** (通用)

## USB vs I2C

| 维度 | USB | I2C |
| --- | --- | --- |
| 速度 | 1.5M-5G | < 3.4M |
| 物理层 | 差分 | 开漏单端 |
| 多 master | Host-Device | 软件地址 (7/10 bit) |
| 距离 | 5m | 短 (< 30cm) |
| 节点数 | 127 (含 Hub) | 多个 |
| 协议 | 类驱动 | 简单 |
| 成本 | 中 | 低 |
| 应用 | PC 外设 | 板内 |

**关键差异**:
- USB 是**外设接口** (PC ↔ 设备), I2C 是**板内总线**
- USB 协议栈复杂, I2C 简单
- USB 可以多个 Hub 串接, I2C 多设备直接挂

**选型**:
- 板内 sensor → **I2C**
- 调试口 / 数据上传 → **USB CDC**
- 屏幕 / Flash → **SPI** 或 **USB**

## USB vs SPI

| 维度 | USB | SPI |
| --- | --- | --- |
| 速度 | 1.5M-5G | 10M-200M+ |
| 物理层 | 差分 | 推挽单端 |
| 距离 | 5m | 短 (< 30cm) |
| 节点数 | 127 (Hub) | 多个 (CS) |
| 协议 | 类驱动 | 简单 |
| 应用 | PC 外设 | 板内高速 |

**关键差异**:
- USB 是**外设接口**, SPI 是**板内高速总线**
- USB 需要 Host (PC), SPI 是 MCU 内部
- USB 协议栈复杂, SPI 简单

**选型**:
- 板内 Flash / LCD / 高速 ADC → **SPI**
- PC 数据交换 → **USB**

## USB vs UART

| 维度 | USB | UART |
| --- | --- | --- |
| 速度 | 1.5M-5G | < 6M |
| 物理层 | 差分 | 单端推挽 |
| 距离 | 5m | 1m / RS485 1km |
| 协议 | 类驱动 | 字节流 |
| 应用 | PC 外设 / 调试 | 调试 / 异步通信 |

**关键差异**:
- USB 是**外设接口**, UART 是**异步串口**
- USB CDC 模拟 UART 行为, 适用于 PC
- 实际工程: **USB CDC + UART 桥接** 是常见模式

**选型**:
- PC 调试 → **USB CDC**
- 板内 / 模块间 → **UART**
- 长距离 / 工业 → **RS485 / UART**

## USB vs Ethernet

| 维度 | USB | Ethernet |
| --- | --- | --- |
| 速度 | 1.5M-5G | 100M-10G |
| 距离 | 5m | 100m+ |
| 协议栈 | 类驱动 | TCP/IP |
| 实时性 | 中 | 中 (QoS / TSN) |
| 应用 | PC 外设 | 网络 |

**关键差异**:
- USB 是**外设接口**, Ethernet 是**网络**
- USB 适合本地, Ethernet 适合远程
- 实际工程: USB 桥接到 Ethernet (USB over IP)

**选型**:
- PC 外设 / 调试 → **USB**
- 远程访问 / 视频 → **Ethernet**

## USB vs 无线协议 (BLE / ZigBee / WiFi)

| 维度 | USB | BLE | ZigBee | WiFi |
| --- | --- | --- | --- | --- |
| 速度 | 1.5M-5G | 1M-2M | 250K | 11M-600M |
| 距离 | 5m | 10m | 100m | 100m |
| 功耗 | 高 | 极低 | 低 | 中 |
| 协议 | 类驱动 | GATT | ZigBee | TCP/IP |
| 应用 | PC 外设 | IoT | Mesh | 网络 |

**关键差异**:
- USB 是有线, 无线协议是无线的替代方案
- USB 带宽高, BLE 极低功耗
- 现代趋势: USB Type-C 充电 + 无线数据

**选型**:
- PC 外设 / 充电 → **USB**
- IoT / 低功耗 → **BLE / ZigBee**
- 高带宽 / 远程 → **WiFi**

## USB 在汽车中的应用

### 现代汽车 USB

```text
车载 USB 场景:
  - 中控屏 USB: 充电 + 媒体播放
  - 诊断 USB (OBD): 诊断工具
  - 软件升级 USB: 工厂 / 4S 店固件更新
  - 内部 USB: 主机 / 仪表互联
  - 后排娱乐: USB 视频 / 音频

挑战:
  - EMC (汽车 EMC 严格)
  - 电源: 12V/24V -> 5V DC-DC
  - ESD 保护
  - 抗振动 (USB 接口机械可靠性)
```

### USB 桥接到 CAN

```c
/* 典型应用: OBD 诊断工具 */
/* 内部用 CAN 接 ECU, 外部 USB 接 PC */
void usb_to_can_bridge() {
    /* USB CDC 接收诊断命令 (PC) */
    uint8_t cmd[64];
    int len = usb_cdc_rx(cmd, sizeof(cmd));
    
    /* 解析 OBD 命令 */
    int can_len = encode_obd_to_can(cmd, len, can_frame);
    
    /* CAN 发出 */
    can_send(CAN_OBD_ID, can_frame, can_len);
    
    /* 接收 CAN 响应 */
    can_recv(&can_frame);
    
    /* USB CDC 发出响应 (PC) */
    usb_cdc_tx(can_to_obd(can_frame), can_len);
}
```

## 跨协议桥接设计

### 常见桥接场景

```text
1. USB <-> CAN 网关
   - 应用: 车载 OBD 诊断
   - 实现: MCU 跑 USB 协议栈 + CAN 协议栈, 协议转换

2. USB <-> SPI 桥
   - 应用: PC 配置 SPI 设备
   - 实现: 桥接 MCU, USB CDC <-> SPI master

3. USB <-> I2C 桥
   - 应用: PC 调试 I2C sensor
   - 实现: 桥接 MCU, USB CDC <-> I2C master

4. USB <-> UART 桥
   - 应用: PC 调试 UART 设备 (CP2102 / CH340)
   - 实现: 桥接 MCU, USB CDC <-> UART
```

### USB CDC + UART 桥接 (最常见)

```c
/* 简化版: USB CDC <-> UART 透明传输 */
void usb_cdc_uart_bridge() {
    /* USB CDC -> UART */
    uint8_t usb_buf[64];
    if (usb_cdc_rx(usb_buf, sizeof(usb_buf)) > 0) {
        uart_tx(usb_buf, 64);
    }
    
    /* UART -> USB CDC */
    uint8_t uart_buf[64];
    if (uart_rx(uart_buf, sizeof(uart_buf)) > 0) {
        usb_cdc_tx(uart_buf, 64);
    }
}
```

## 实战选型决策树

```text
新项目, 需要通信
  |
  +-- 板内, 距离 < 30cm, 多个设备
  |     +-- 速度 < 1M -> I2C
  |     +-- 速度 > 1M -> SPI
  |
  +-- 板间, 距离 < 1m, 单向高速
  |     -> SPI (板对板连接器)
  |
  +-- 距离 < 5m, 通用性
  |     -> USB (PC 接口)
  |
  +-- 距离 1m-10m, 多节点, 实时
  |     -> CAN
  |
  +-- 距离 > 10m, 多节点
  |     -> RS485 / CAN (低速)
  |
  +-- 网络 / TCP/IP
  |     -> Ethernet
  |
  +-- 无线 / IoT
        +-- 低功耗 -> BLE / ZigBee
        +-- 高带宽 -> WiFi
```

## 7 条选型原则

```text
1. PC 外设 / 调试 -> USB
2. 板内管理, 多设备 -> I2C
3. 板内高速, 单向 -> SPI
4. 异步串口 / 长距离 -> UART / RS485
5. 汽车 / 工业实时 -> CAN
6. 网络 / TCP/IP -> Ethernet
7. 无线 / IoT -> BLE / ZigBee / WiFi
```

## 关联文档

- `usb-deep-dive.md` 原理
- `usb-practical.md` 速查
- `usb-failure-cases.md` 产线案例
- `usb-enumeration-and-descriptors.md` 枚举
- `usb-class-drivers.md` CDC / HID / MSC / DFU
- `usb-dma-and-rtos.md` DMA + RTOS
- `usb-index.md` 导航
- `can-vs-other-bus.md` CAN vs 其他总线 (参考)
- `i2c-vs-smbus-recovery.md` 跨协议对比参考
