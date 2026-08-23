# BLE（Bluetooth Low Energy）

## 定位

BLE 是 Bluetooth 4.0 引入的低功耗扩展，2010 年起在 Nordic、TI、Dialog（现 Renesas）的推动下成为 IoT / 可穿戴 / 资产追踪的事实标准。2.4 GHz GFSK，1~2 Mbps PHY（BLE 5.x 引入 LE 2M / LE Coded），峰值电流 < 15 mA，待机 < 1 µA。

核心特点：

- 低功耗（纽扣电池撑年）。
- 间歇性连接（小数据突发）。
- 短距（10~50 m 典型，BLE 5.x 长距模式可达 300 m）。
- 协议栈分层：PHY → LL → HCI → L2CAP → ATT/GATT → GAP → 应用 Profile。
- 嵌入式产线最常见的无线故障源。

## 跟经典 Bluetooth（BR/EDR）的差异

```text
经典 BT:     持续连接、流媒体音频、高功耗
BLE:         间歇连接、属性数据、低功耗
```

两者不兼容（双模芯片如 nRF52832 同时支持，但协议栈分开）。A2DP / HFP / AVRCP 走经典 BT；GATT / HID-over-GATT / Battery Service 走 BLE。

## 角色

```text
Advertiser / Scanner    → 发现阶段（无连接）
Peripheral / Central    → 连接阶段（Peripheral = 外设，Central = 手机/网关）
Broadcaster / Observer  → 无连接单向广播（BLE 5.x 扩展）
```

## 关键概念

- **GATT (Generic Attribute Profile)**：基于属性的数据模型，Server 暴露 Service/Characteristic，Client 读写。
- **Service / Characteristic / Descriptor**：数据组织三层。
- **MTU (Maximum Transmission Unit)**：单次 ATT PDU 大小，默认 23 字节，协商可到 247。
- **Connection Interval / Slave Latency / Supervision Timeout**：连接参数三件套，决定功耗 vs 吞吐。
- **PHY**：LE 1M（默认）/ LE 2M（BLE 5）/ LE Coded S2/S8（BLE 5 长距）。
- **Advertising Interval**：广播间隔，影响发现速度 vs 功耗。

## 典型芯片

| 芯片 | 厂商 | 特点 |
| --- | --- | --- |
| nRF52832 / nRF52840 | Nordic | BLE 5 / Thread / Zigbee，主流通用 |
| nRF5340 | Nordic | 双核 Cortex-M33，BLE 5.3 |
| CC2640 / CC2652 | TI | BLE 5 / Thread / Zigbee |
| EFR32BG | Silicon Labs | BLE 5 / Zigbee，NCP/SoC 双形态 |
| RTL8762E | Realtek | 低成本消费电子，曾爆 DoS 漏洞 |
| STM32WB | ST | Cortex-M4 + M0 双核，BLE 5.3 |
| CH32V208 | WCH | RISC-V BLE 5.3，国产 |
| PHY62xx | 博通集成 | 国产超低成本 |

## 嵌入式产线典型故障

- **0x3E 断开**（CONN_FAILED）：连接请求同步包丢失，信道拥塞。
- **0x3D 断开**（MIC_FAILURE）：加密链路校验失败，多为配对参数错。
- **0x08 断开**（CONN_TIMEOUT）：连接监控超时，slave latency 设太大。
- **0x13 / 0x16 断开**：远端/本地主动终止，应用层逻辑错。
- **SMP 状态机 DoS**：配对流程中顺序错，攻击者可阻断配对。
- **ADC 干扰晶振**：nRF51 等芯片 ADC 启停耦合到外置晶振链路，BLE 链路失锁。
- **外设响应慢导致 L2CAP 拥塞**：nRF52832 必须等 `BLE_GATTS_EVT_HVN_TX_COMPLETE` 再发下一包。

## 延伸阅读

- `bus/ble-practical.md` 调试流程速查
- `bus/ble-deep-dive.md` 协议栈 / 状态机 / 配对 / 安全深挖
- `bus/ble-failure-cases.md` 产线实战案例（0x3E / DoS / ADC 干扰等）
- `bus/ble-index.md` 主题地图 + 读者路径
