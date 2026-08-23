# Matter Practical Guide

## 目标

本文用于 Matter 工程调试：commissioning（配网）、fabric、cluster、跨生态测试、抓包、产线常见故障（配网失败 / CASE 失败 / 跨 Fabric 路由 / OTA 失败）的快速定位。

## 配网流程

### 1. Commissioning 概念

```text
配网（Commissioning）：
  把 Matter 设备加入 fabric 的过程

  1. Discovery（设备被发现）
     - BLE 广播 Matter Service Data (UUID 0xFEAF + Discriminator)
  2. 配网通道建立
     - BLE GATT 连接
  3. PASE（Password-Authenticated Session Establishment）
     - 用 Setup Passcode + Discriminator
  4. Operational Discovery
     - 设备找最佳 fabric 网络
  5. CASE（Certificate Authenticated Session Establishment）
     - 用 NOC（Node Operational Certificate）
  6. Fabric 加入完成
     - NOC 写入设备
     - 设备可被 fabric 内其他节点访问
```

### 2. Setup Payload

```text
11 位 Setup Passcode（10^11 种可能，但实际中常用预定义）
3 位 Discriminator（区分同一 Passcode 下多个未配网设备）
2 位 Version（1=1.0, 2=1.1+, 3=1.3+）

Manual Pairing Code (11 + 3 = 14 数字):
  格式：DDDDD DDDD DDD DC
  D = Passcode 数字
  C = Checksum

QR Code 编码:
  完整 payload = Version + Discriminator + Passcode + VendorID + ProductID
  应用层只需展示给用户扫码
```

**生成 Setup Payload 工具**：

```python
# CSA 官方 chip-tool
./chip-tool payload generate-manual-setup-payload \
    --discriminator 3840 \
    --passcode 20202021 \
    --vendor-id 0xFFF1 \
    --product-id 0x8000
```

### 3. Commissionable Discovery

```text
设备未配网时广播：
  BLE Service Data 0xFEAF
  - Vendor ID (2 bytes)
  - Product ID (2 bytes)
  - Discriminator (12 bits) + DiscriminatorBit + Version

手机 App 扫描时过滤：
  0xFEAF → Matter 设备
  Discriminator → 找到指定设备
```

## 关键参数

### 设备标识

| 参数 | 长度 | 备注 |
| --- | --- | --- |
| Vendor ID (VID) | 2 字节 | CSA 分配（测试用 0xFFF1） |
| Product ID (PID) | 2 字节 | 厂商自定义 |
| Setup Passcode | 4 字节 | 11 位数字（首位非 0） |
| Discriminator | 12 bits | 同 Passcode 下区分设备 |
| Node ID | 8 字节 | Fabric 内唯一，派生自 Fabric ID |
| Fabric ID | 8 字节 | Fabric 唯一标识 |

### 网络参数

| 网络 | 优势 | 限制 |
| --- | --- | --- |
| Wi-Fi | 高速、广泛 | 高功耗（IoT 挑战） |
| Thread | mesh、低功耗 | 需 Border Router |
| Ethernet | 稳定、高速 | 仅固定设备 |

**Wi-Fi** 适合供电设备（插座、Hub、Camera）；**Thread** 适合电池设备（传感器、按钮、门锁）。

### Cluster 速查

Matter 复用 ZigBee Cluster Library，标准 Cluster：

| Cluster ID | 名称 | 属性 / 命令 |
| --- | --- | --- |
| 0x0006 | On/Off | OnOff, On/Off/Toggle |
| 0x0008 | Level Control | CurrentLevel, MoveToLevel |
| 0x0300 | Color Control | CurrentHue, CurrentSaturation, CurrentX/Y |
| 0x0201 | Thermostat | LocalTemperature, OccupiedCoolingSetpoint |
| 0x0102 | Window Covering | CurrentPositionLiftPercent100, MoveToLevel |
| 0x0204 | Thermostat UI | TemperatureDisplayMode, KeypadLockout |
| 0x0402 | Temperature Measurement | MeasuredValue |
| 0x0406 | Occupancy Sensing | Occupancy |
| 0x0405 | Humidity Measurement | MeasuredValue |
| 0x000F | Binary Input Basic | PresentValue |
| 0x001D | Descriptor | DeviceTypeList, ServerList, ClientList |
| 0x0003 | Identify | IdentifyTime, Identify |

**Endpoint Device Type**（部分）：

| Device Type ID | 名称 | 强制 Cluster |
| --- | --- | --- |
| 0x0001 | On/Off Light | On/Off |
| 0x0101 | Dimmable Light | On/Off + Level |
| 0x0100 | Color Dimmable Light | On/Off + Level + Color |
| 0x0200 | On/Off Light Switch | Identify + On/Off (client) |
| 0x0103 | On/Off Plug-in Unit | On/Off + Level + Electrical Measurement |
| 0x0010 | Generic Switch | Identify + Switch |
| 0x000A | Thermostat | Thermostat + Thermostat UI |
| 0x0102 | Window Covering | Window Covering |
| 0x0106 | Temperature Sensor | Temperature Measurement |
| 0x0107 | Humidity Sensor | Humidity Measurement |
| 0x010A | Occupancy Sensor | Occupancy Sensing |
| 0x0302 | Door Lock | Door Lock + User Management |

## 抓包工具

| 工具 | 平台 | 优势 | 限制 |
| --- | --- | --- | --- |
| Simplicity Studio Network Analyzer | Windows | 官方 EFR32 / SiWx917 | 仅 Silicon Labs 芯片 |
| nRF Sniffer for Thread | nRF52840 DK | 免费 | 仅 Thread 流量 |
| Wireshark + Thread dissector | 全平台 | 开源，需 dongle | 需 Thread TAP 设备 |
| esp-idf monitor + Wireshark | Linux | ESP32-H2/C5/C6 抓 | 需 ESP32 设备 |
| chip-tool | CLI | CSA 官方，自动化测试 | 仅 Matter |
| Apple Home / Google Home 抓 log | 移动 | 现场真实生态测试 | 需 Apple/Google 设备 |

**产线推荐组合**：

```text
研发：chip-tool 跑 chip-all-clusters-app 自动化测试
产线：chip-tool + Wireshark 看 commissioning + cluster 流量
客户：iOS Home + Android Google Home 双生态验证
```

**chip-tool 常用命令**：

```bash
# 1. 配网
./chip-tool pairing ble-wifi <node-id> <ssid> <passwd> 20202021 3840

# 2. 开关灯
./chip-tool onoff on <node-id> 1

# 3. 读属性
./chip-tool onoff read on-off <node-id> 1

# 4. 订阅
./chip-tool onoff subscribe on-off <node-id> 1 0 2

# 5. 列出 fabric
./chip-tool fabric list

# 6. 删除 fabric
./chip-tool pairing unpair <node-id>
```

## 调试步骤

1. **看 BLE 广播**：手机 nRF Connect 看 0xFEAF Service Data
2. **尝试配网**：手机 App 扫码 / 输 Manual Pairing Code
3. **看 commissioning 流程**：chip-tool / Wireshark 抓 PASE → CASE
4. **验证 fabric 加入**：chip-tool 列出 fabric
5. **跑基础 cluster 测试**：On/Off、Level、订阅
6. **测跨生态**：iOS Home + Android Google Home 都能控制
7. **测 OTA**：用 chip-tool 推镜像

## 常见问题速查

| 现象 | 优先检查 |
| --- | --- |
| App 找不到设备 | BLE 广播没启 / Discriminator 错 / 0xFEAF 没注册 |
| Commissioning 失败 | Passcode 错 / Discriminator 错 / BLE 时序 |
| 配网卡在 PASE | Passcode 不匹配 / 时序错位 |
| CASE 失败 | NOC 写错 / Trust Root 错 / 时序错 |
| Cluster 不响应 | Endpoint 配置错 / Cluster ID 错 / Device Type 不匹配 |
| iOS 能用 Android 不能 | Cluster 命令权限错 / 跨生态 Attribute 不通用 |
| 跨 Fabric 设备不同步 | 设备只在一个 Fabric / 多 Fabric 同步逻辑缺 |
| OTA 失败 | OTA Provider 没配 / 镜像签名错 / 设备不在 fabric |
| 设备掉电后 fabric 丢失 | Fabric 持久化失败（KVS / Flash） |
| Wi-Fi 切换 fabric 掉线 | 设备没保存 Wi-Fi 凭据 / fabric 路由表丢失 |

## 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| App 找不到设备 | BLE 广播没起 | nRF Connect 看 0xFEAF |
| 配网卡 PASE | Passcode 错 | 核对 Passcode + Discriminator |
| 配网卡 CASE | NOC 写错 | 重新配对 + 看 chip-tool log |
| Cluster 无响应 | 缺强制 Cluster | 比对 Matter Device Library |
| 跨生态不同步 | 多 Fabric 没开 | 设备支持 Multi-Fabric 检查 |
| OTA 失败 | OTA Provider 错 | 重新配 OTA Provider |
| 设备掉电丢失 | KVS 没持久化 | 改 fabric 存储策略 |
| Wi-Fi 切换掉线 | 凭据没保存 | 看 Wi-Fi Manager 流程 |
| Thread 切换掉线 | Border Router 错 | 重启 Border Router |
| 认证测试 fail | Cluster 顺序错 | 比对 Matter Spec |

## 错误码速查

### CASE / PASE 错误

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x01 | FAILURE | 通用失败 |
| 0x02 | INVALID_PARAMETER | 参数无效 |
| 0x05 | INVALID_USE_OF_SESSION_KEY | 密钥使用错 |
| 0x06 | UNSUPPORTED_CIPHER_SUITE | 加密套件不支持 |
| 0x0C | INVALID_KEY_CONFIRMATION | 密钥验证失败 |
| 0x0D | UNSUPPORTED_KEY_EXPORT | 不支持密钥导出 |
| 0x0E | UNAUTHORIZED | 未授权 |
| 0x12 | INVALID_PROVISIONING_DATA | 配网数据错 |

### Matter IM 错误

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x0001 | Failure | 通用 |
| 0x0002 | InvalidSubscription | 订阅无效 |
| 0x0003 | UnsupportedAccess | 访问不支持 |
| 0x0004 | UnsupportedEndpoint | 端点不支持 |
| 0x0005 | InvalidAction | 动作无效 |
| 0x0006 | ScopedClustersMismatch | Cluster 不匹配 |
| 0x0007 | UnsupportedCluster | Cluster 不支持 |
| 0x0008 | UnsupportedAttribute | 属性不存在 |
| 0x0009 | ConstraintError | 约束错 |
| 0x000A | UnsupportedCommand | 命令不支持 |
| 0x000B | InvalidCommand | 命令格式错 |
| 0x000C | IngorredMessage | 消息忽略 |
| 0x0010 | ResourceExhausted | 资源耗尽 |
| 0x0011 | Busy | 忙 |
| 0x0012 | Timeout | 超时 |
| 0x0013 | InvalidDataType | 数据类型错 |
| 0x0014 | UnsupportedMode | 模式不支持 |
| 0x0015 | InvalidStateChange | 状态变更无效 |
| 0x0016 | NotFound | 找不到 |
| 0x0017 | AlreadyExists | 已存在 |
| 0x0020 | FabricNotFound | Fabric 找不到 |
| 0x0021 | ClusterNotFoundOnEndpoint | Cluster 不在该 EP |

## Commissioning 步骤详解

```text
Step 1: BLE 广播发现
  - 设备 BLE 广播 0xFEAF Service Data
  - 手机 App 扫描匹配
  - 显示设备名 + 厂商 + 产品

Step 2: CommissioningWindow 开启
  - 默认 15 分钟（可调）
  - 超时后需用户长按重置

Step 3: PASE 握手（Password-Authenticated Session Establishment）
  - 设备 + Commissioner 互相验证
  - 基于 SPAKE2+ 协议
  - 用 Setup Passcode + Discriminator

Step 4: Attestation
  - 设备给 Commissioner 看设备证书（DAC）
  - Commissioner 验证设备真伪

Step 5: Operational Discovery
  - 设备向 Commissioner 提供 Wi-Fi SSID / Thread Network
  - Commissioner 验证网络可访问

Step 6: CSR / NOC
  - 设备生成 CSR（Certificate Signing Request）
  - Commissioner 用 Fabric CA 签 NOC
  - NOC 写入设备

Step 7: CASE 握手
  - 设备 + Commissioner 互相验证 NOC
  - 建立加密 session

Step 8: 加 fabric
  - NOC + Fabric ID + Operational ID 写入设备
  - 设备保存 fabric 状态

Step 9: ACL 配置
  - 设备接受 fabric 内其他节点访问
  - ACL 配置权限
```

## 跨生态测试

```text
必备测试：
  1. Apple Home（iOS 16+）
  2. Google Home（Android 12+ / iOS）
  3. Amazon Alexa（iOS / Android）
  4. 三星 SmartThings（iOS / Android）
  5. 米家（国内 Android）
  6. Home Assistant（开源）

测试项目：
  - 配网
  - 设备控制
  - 状态同步
  - 场景 / 自动化
  - 语音控制（Alexa / Google）
  - 跨生态切换
  - 多 Fabric 共享
```

## Matter 认证测试

```text
CSA 认证流程：
  1. PICS（Protocol Implementation Conformance Statement）
     - 设备能力清单
  2. PIXIT（Protocol Implementation eXtra Information for Testing）
     - 设备测试配置
  3. Test Harness
     - 跑 mandatory test cases
     - 跑 optional test cases
  4. 提交认证
  5. 通过后获 Certification ID

测试时间：4-8 周
费用：会员费 + 认证费（数千美元）
```

## 检查清单

```text
□ BLE 0xFEAF Service Data 广播
□ Setup Passcode + Discriminator 配置
□ Vendor ID + Product ID 配齐
□ 配网流程跑通（PASE → CASE → Fabric）
□ 强制 Cluster 都实现
□ Cluster 顺序符合 Matter Device Library
□ 跨 5+ 生态测试
□ 订阅 / Binding 测试
□ OTA 升级测试
□ 持久化 fabric（KVS / Flash）
□ Wi-Fi 凭据保存
□ Thread 入网（如果是 Thread 设备）
□ Border Router 集成（如果是 Thread over Wi-Fi）
□ 安全：CASE / PASE 加密 + NOC 验证
□ 错误码：完整 IM 错误码实现
```

## 关联文档

- `bus/matter.md` 主题入口
- `bus/matter-deep-dive.md` 协议栈深挖
- `bus/matter-failure-cases.md` 产线实战案例
- `bus/matter-index.md` 主题地图 + 导航
- `bus/thread-*.md` Matter over Thread
- `bus/ble-deep-dive.md` BLE 配网通道
- `bus/zigbee-*.md` Cluster 沿用参考
