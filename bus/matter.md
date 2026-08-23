# Matter

## 定位

Matter 是 Connectivity Standards Alliance（CSA，原 ZigBee Alliance）2022 年发布的智能家居应用层互操作标准。跑在 Thread / Wi-Fi / Ethernet 之上，是 BLE/ZigBee/Wi-Fi 生态走向统一的关键协议。所有主流生态（Apple HomeKit / Google Home / Amazon Alexa / 三星 SmartThings / 米家）已全部支持。

核心特点：

- **互操作**：跨厂商、跨生态设备互通
- **IP 化**：基于 IPv6（Thread / Wi-Fi / Ethernet）
- **本地优先**：无云依赖，控制走本地
- **安全**：基于 BLE 配网 + PASE/CASE 加密
- **生态大一统**：2024 起成为智能家居新标准

## 跟 ZigBee / BLE / Wi-Fi 的关系

```text
Matter   →  应用层（互操作 / 标准化）
Thread   →  网络层（mesh / 6LoWPAN / IPv6）
Wi-Fi    →  网络层（IP 接入）
Ethernet →  网络层（IP 接入）
BLE      →  配网通道（commissioning）

Matter 不取代 BLE/ZigBee/Z-Wave / Thread/Wi-Fi/Ethernet
Matter 是建立在 IP 网络之上的应用层
```

**关键认知**：

- Matter ≠ Thread（虽然都来自 CSA）
- Matter 跑在 Thread/Wi-Fi/Ethernet 之上
- BLE 只用于配网（commissioning），不在 Matter 数据链路

## 设备类型

```text
Matter Node 概念：
  - Commissionable: 等待被发现和配网
  - Commissioned: 已被加入 fabric
  - Operational: 正常通信

Matter Fabric 概念：
  - 共享信任域（root certificate）
  - 一个设备可同时属于多个 fabric
  - 例如：设备同时在 Apple Home 和 Google Home 中
```

**Fabric 关系**：

```text
Apple Home      ┐
Google Home     ├── 共享同一 Matter 设备
Amazon Alexa    ┘
```

## 关键概念

- **Node**（节点）：Matter 设备单元
- **Endpoint**（端点）：功能单元（一个灯有 1 个 Endpoint，一个多功能设备有多个）
- **Cluster**（簇）：功能集合（On/Off Cluster、Level Cluster 等，ZigBee 沿用）
- **Commissioning**（配网）：把设备加入 fabric
- **Fabric**（信任域）：共享信任的设备群
- **PASE / CASE**：配对 / 通信加密协议
- **NOC / NOCSR**：Node Operational Certificate
- **ACL**：Access Control List
- **Subscription**：订阅模式（Server 主动上报）
- **Binding**：跨设备 Cluster 绑定（自动化）

## 典型芯片

| 芯片 | 厂商 | 协议栈 | Matter 支持 |
| --- | --- | --- | --- |
| EFR32MG24 | Silicon Labs | GSDK | Matter over Thread + Wi-Fi |
| nRF52840 / nRF5340 | Nordic | nRF Connect SDK | Matter over Thread |
| ESP32-H2 / C5 / C6 | Espressif | ESP-Matter | Matter over Thread / Wi-Fi |
| K32W0x1 | NXP | NXP Matter | Matter over Thread |
| STM32WB / WBA | ST | ST Matter | Matter over Thread |
| Realtek Ameba | Realtek | Ameba Matter | Matter over Wi-Fi |
| TI CC2652 / CC2674 | TI | Z-Stack + Matter | Matter over Thread |

**Matter 认证（CSA 认证）**：

```text
认证流程：
  1. 申请 CSA 会员（普通 / Promoter / Participant）
  2. 跑 Matter 1.x 认证测试
  3. 用 CSA Test Harness 跑所有 Mandatory Test Case
  4. 提交认证
  5. 通过后获 CSA Certification ID
  6. 产品可贴 Matter 标志

认证级别：
  Matter 1.0 → 1.1 → 1.2 → 1.3 → 1.4（持续演进）
  设备类型：Endpoint Cluster 必须符合 Matter Device Library
```

## 嵌入式产线典型故障

- **Commissioning 失败**：BLE 配网时序错 / Setup Payload 错
- **CASE 失败**：Operational Discovery / NOC 交换失败
- **跨 Fabric 路由**：Border Router 配错
- **Cluster 不响应**：Endpoint Cluster 配置错 / 不在 Matter Device Library
- **Wi-Fi 切换 fabric 掉线**：Wi-Fi 切换导致 fabric 路由变更
- **OTA 失败**：OTA Provider 配置错
- **认证测试 fail**：Mandatory Cluster 缺失 / Attribute 写权限错

## 延伸阅读

- `bus/matter-practical.md` 调试流程速查
- `bus/matter-deep-dive.md` 协议栈 / 数据模型 / 配网 / 安全深挖
- `bus/matter-failure-cases.md` 产线实战案例
- `bus/matter-index.md` 主题地图 + 读者路径
- `bus/thread-*.md` Matter over Thread（最常见部署）
- `bus/ble-deep-dive.md` BLE 配网通道
- `bus/zigbee-*.md` Cluster 沿用参考
