# ZigBee

## 定位

ZigBee 是基于 IEEE 802.15.4 的低功耗 mesh 网络协议，2003 年由 ZigBee Alliance（现 Connectivity Standards Alliance）发布，2020 年起 ZigBee 3.0 兼容主流 IoT 协议（Thread / Matter 部分）。2.4 GHz OQPSK（部分频段 868 MHz / 915 MHz），250 kbps PHY 速率，典型功耗介于 BLE 和 Wi-Fi 之间。

核心特点：

- **Mesh 自组网**（最多 1000+ 节点，多跳路由）。
- **低功耗**（End Device 可纽扣电池撑年）。
- **自愈**（节点掉线自动绕路）。
- **互操作**（ZigBee 3.0 / ZCL 标准化 Cluster）。
- **嵌入式产线最常见 mesh 掉线 / 重入网问题**。

## 跟 Wi-Fi / BLE / Thread 的差异

```text
Wi-Fi  : 高速流媒体，mesh 弱，功耗高
BLE    : 点对点星型，无 mesh，功耗最低
Thread : 6LoWPAN mesh，IPv6，IoT 互联网融合
ZigBee : 经典 mesh，IoT 自组网事实标准
```

## 设备类型

```text
Coordinator（协调器）  → 1 个 PAN，分配 16-bit 网络地址
Router（路由器）        → 转发 + 路由 + 永不上电睡眠
End Device（终端）      → 不转发，可睡眠（典型 30s ~ 数分钟唤醒一次）
```

**典型网络结构**：

```text
Coordinator
   ├── Router (1)
   │     ├── End Device
   │     ├── End Device
   │     └── Router (2)
   │           ├── End Device
   │           └── End Device
   └── Router (3)
         └── End Device
```

## 关键概念

- **IEEE 802.15.4 PHY/MAC**：物理层和媒体接入层，ZigBee 协议栈的基础
- **NWK 层**：网络层，处理 mesh 路由（树状路由 + 路由表）
- **APS 层**：应用支持子层，端到端确认 + 绑定表
- **ZDO**：ZigBee Device Object，设备管理（入网 / 离开 / 绑定）
- **ZCL**：ZigBee Cluster Library，标准化 Cluster 集合
- **Trust Center**：网络安全中心，分配 Network Key
- **Bind / Group / Scene**：应用层寻址方式
- **16-bit NWK 地址**：节点在网络内的短地址（与 64-bit IEEE 地址对应）
- **PAN ID**：网络标识（0x0000 ~ 0x3FFF）
- **Channel**：11~26（2.4 GHz），避开 Wi-Fi 重叠信道

## 典型芯片

| 芯片 | 厂商 | 协议栈 | 特点 |
| --- | --- | --- | --- |
| CC2530 / CC2538 | TI | Z-Stack | 经典，已 EOL，新设计不推荐 |
| CC2652 / CC1352 | TI | Z-Stack 3.0+ | BLE + Thread + Zigbee 多协议 |
| EFR32MG | Silicon Labs | EmberZNet | Zigbee / Thread / BLE / Matter |
| nRF52840 | Nordic | nRF Connect for ZB | Thread / Zigbee |
| K32W041 / K32W061 | NXP | NXP Zigbee | 工业 / 楼宇 |
| MG21 / MG24 | Silicon Labs | EmberZNet 7+ | 最新 Zigbee 3.0 / Matter |
| ZGM230S | Silicon Labs | EmberZNet | 模块化方案 |

## 嵌入式产线典型故障

- **CC2530 ReJoinRequest 概率性返回错误**：NLME 状态机 BUG，密封水壶屏蔽信号抓包发现
- **zigbee2mqtt 50+ 设备 20% 随机离线**：USB 适配器固件 / MQTT 队列积压
- **NV 残留致误关联邻居网关**：flash PAN ID 限定回原网络
- **EFR32 NCP crash 看不到原因**：NCP 模式 assert/CRS/SW 重启必须靠 SWO 抓
- **OrphanJoin 卡死**：CC2530 ReJoinRequest 状态机 BUG 兜底
- **End Device 不睡眠**：Poll Control 错配，纽扣电池撑不过 1 周
- **多 Coordinator 冲突**：同一信道多个 PAN ID 互踩

## 延伸阅读

- `bus/zigbee-practical.md` 调试流程速查
- `bus/zigbee-deep-dive.md` 协议栈 / 入网 / 路由 / 安全深挖
- `bus/zigbee-failure-cases.md` 产线实战案例（CC2530 BUG / 50+ 设备掉线 / NCP crash 等）
- `bus/zigbee-index.md` 主题地图 + 读者路径
