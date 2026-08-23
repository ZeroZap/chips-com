# Thread

## 定位

Thread 是基于 IEEE 802.15.4 的低功耗 mesh 网络协议，跑 6LoWPAN（IPv6 over Low-Power Wireless Personal Area Networks）。2014 年由 Nest Labs（后被 Google 收购）发起，2015 年成立 Thread Group，2016 年发布 1.0。是 Matter 协议的核心网络层之一（与 Wi-Fi / Ethernet 并列）。

核心特点：

- **IPv6 端到端**（每个设备有唯一 IPv6 地址）
- **Mesh 自愈**（节点掉线自动绕路）
- **低功耗**（Sleepy End Device 纽扣电池可撑年）
- **免授权频段**（2.4 GHz 11-26 信道）
- **无单点故障**（无主从结构，Leader 自动选举）
- **互操作**（基于 IPv6 跑任意 TCP/UDP/MQTT 应用）

## 跟 ZigBee / Wi-Fi / BLE 的关系

```text
ZigBee : 同源 PHY（802.15.4），跑 ZigBee 私有协议
Thread : 同源 PHY（802.15.4），跑 6LoWPAN / IPv6 / UDP
Wi-Fi  : 802.11，高速高功耗
BLE    : 802.15.4 子集（BLE 5 PHY），非 mesh

Thread 是 ZigBee 的"IPv6 化"演进
Matter 是跑在 Thread / Wi-Fi / Ethernet 之上的应用层
```

## 设备类型

```text
Router (Full Thread Device, FTD)
  - 始终活跃，不睡眠
  - 转发 + 路由
  - 维护子节点
  - 推荐给带电源的设备（插座、HVAC）

REED (Router-Eligible End Device)
  - 默认是 End Device
  - 路由能力可启用
  - 适合电池供电但偶尔路由的设备

End Device (MED, Minimal End Device)
  - 不转发
  - 可睡眠
  - 通过父节点通信

Sleepy End Device (SED)
  - 默认睡眠
  - 周期性 poll 父节点
  - 纽扣电池首选
```

**典型网络结构**：

```text
Border Router (Thread ↔ Wi-Fi / Ethernet)
  │
  ├── Router (FFD)
  │     ├── End Device
  │     ├── Sleepy End Device
  │     └── REED
  ├── Leader (选举出的)
  │     ├── Router
  │     └── End Device
  └── Router
        └── Sleepy End Device
```

## 关键概念

- **6LoWPAN**：IPv6 over 802.15.4（压缩 + 分片）
- **MLE（Mesh Link Establishment）**：节点间链路建立
- **RPL（Routing Protocol for Low-Power and Lossy Networks）**：mesh 路由协议
- **DODAG（Destination-Oriented Directed Acyclic Graph）**：RPL 路由拓扑
- **Border Router**：连接 Thread 和其他 IP 网络（Wi-Fi / Ethernet）
- **Commissioner**：负责新设备入网
- **Joiner**：等待入网的新设备
- **Network Data**：网络配置（prefix, route, service）
- **Network Key**：Thread 网络加密密钥
- **PAN ID**：网络标识
- **Extended PAN ID**：网络扩展标识
- **Channel**：11~26 (2.4 GHz)
- **Master Key**：派生 Network Key 的种子
- **PSKc**：Pre-Shared Key for the Commissioner

## 典型芯片

| 芯片 | 厂商 | 协议栈 | Thread 1.x | Thread 1.3+ |
| --- | --- | --- | --- | --- |
| nRF52840 | Nordic | nRF Connect SDK | ✅ | ✅ |
| nRF5340 | Nordic | nRF Connect SDK | ✅ | ✅ |
| EFR32MG12/MG13/MG21/MG24 | Silicon Labs | GSDK | ✅ | ✅ |
| CC2652 / CC2674 | TI | Z-Stack + Thread | ✅ | ✅ |
| K32W0x1 | NXP | NXP Thread | ✅ | ✅ |
| STM32WB / WBA | ST | ST Thread | ✅ | 部分 |
| ESP32-H2 / C5 / C6 | Espressif | ESP-IDF | ✅ | ✅ |
| Realtek Ameba | Realtek | Ameba | ✅ | 部分 |

## 嵌入式产线典型故障

- **Commissioner 找不到 Joiner**：PSKc 错 / 信道错 / 网络 Key 不一致
- **Joiner 入网失败**：IEEE 错位 / 凭据错 / 时间窗口过
- **End Device 找不到父节点**：网络饱和 / RSSI 弱
- **Border Router 切换导致网络重组**：IP 冲突 / Wi-Fi 切换
- **REED 升级 Router 失败**：路由表满 / 节点数限制
- **RPL 路由震荡**：链路质量差 / 频繁切换
- **Channel Mask 限制错**：误限制可用信道
- **多 Thread 网络共信道干扰**：多个 PAN 互踩

## 延伸阅读

- `bus/thread-practical.md` 调试流程速查
- `bus/thread-deep-dive.md` 协议栈 / 路由 / 安全深挖
- `bus/thread-failure-cases.md` 产线实战案例
- `bus/thread-index.md` 主题地图 + 读者路径
- `bus/matter-*.md` Matter over Thread（最常见部署）
- `bus/zigbee-*.md` 同源 PHY 对比
- `bus/ble-deep-dive.md` BLE Commissioning 通道
