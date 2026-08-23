# BLE Deep Dive

## 目标

深入 BLE 协议栈各层：PHY / LL / HCI / L2CAP / ATT / GATT / GAP / SMP。覆盖广播、连接、加密、配对、状态机、BLE 5.x 扩展、Privacy。目标读者：协议栈移植、驱动调试、安全加固、产线深度故障定位的工程师。

## 协议栈分层

```text
┌─────────────────────────────────────────────────────┐
│ Profile (应用层)                                     │
│  Battery Service / Heart Rate / HID / Mesh / ...    │
├─────────────────────────────────────────────────────┤
│ GAP      角色 / 广播 / 扫描 / 连接管理               │
│ GATT     Service / Characteristic / CCCD            │
│ ATT      属性读写协议                                │
├─────────────────────────────────────────────────────┤
│ L2CAP    逻辑链路 + 拥塞控制 + 分片                   │
├─────────────────────────────────────────────────────┤
│ HCI      Host-Controller Interface（命令/事件/数据） │
├─────────────────────────────────────────────────────┤
│ LL       Link Layer（设备地址 / 广播 / 连接 / 加密）  │
├─────────────────────────────────────────────────────┤
│ PHY      2.4GHz GFSK 调制                            │
└─────────────────────────────────────────────────────┘
```

**两种实现形态**：

- **SoC（System on Chip）**：协议栈全部在 MCU 内跑，nRF52832 + SoftDevice S140 / EFR32BG + GSDK
- **NCP（Network Co-Processor）**：协议栈在独立芯片，MCU 通过 HCI（UART / SPI / USB）通信

**实战选型**：

```text
SoC：固件简单，功耗低（无 HCI 协议转换），推荐 IoT / 穿戴
NCP：MCU 资源紧张 / 已有 MCU 不换，外部加蓝牙模块
HCI：手机、PC 调试场景
```

## 物理层（PHY）

### 频段与信道

```text
2.400 ~ 2.4835 GHz ISM 频段
40 个 RF 信道，间隔 2 MHz
  f = 2402 + k × 2 MHz, k = 0..39
信道索引：37 / 0 / 1 / ... / 39
```

**广播信道**：37, 38, 39（避开了 Wi-Fi 信道 1~6 的密集区，但现代 Wi-Fi 40MHz 仍可能影响）

**数据信道**：0~36, 38~39（自适应跳频算法选）

### 调制

```text
GFSK（Gaussian Frequency Shift Keying）
  BT = 0.5
  调制指数 h = 0.45 ~ 0.55
  比特率 1 Mbps（LE 1M）
```

### BLE 5.x PHY 档位

| PHY | 比特率 | 编码 | 灵敏度 | 应用 |
| --- | --- | --- | --- | --- |
| LE 1M | 1 Mbps | 无 | -94 dBm | 默认 |
| LE 2M | 2 Mbps | 无 | -91 dBm | 高速 |
| LE Coded S=2 | 500 kbps | FEC | -97 dBm | 中距 |
| LE Coded S=8 | 125 kbps | FEC | -103 dBm | 长距 |

**LE Coded** 用前向纠错（FEC）扩展范围，符号速率仍 1 Msps，每个 bit 用 2 或 8 个符号编码。

## 链路层（LL）

### 设备地址

```text
BD_ADDR（48-bit，类似 MAC）：
  Public Address：IEEE 注册，固定
  Random Address：可随机生成
    Static Random：上电生成，断电丢失
    Private Resolvable (RPA)：含 IRK hash，可识别
    Private Non-Resolvable：完全匿名
```

**Privacy 机制**：

```text
RPA 定期更换（典型 15 分钟）
远端用本地 IRK 解 hash 识别身份
未在白名单的扫描请求直接拒
```

### 广播 PDU 类型

```text
ADV_IND              → 可连接可扫描通用广播
ADV_DIRECT_IND       → 定向可连接（高速发起连接）
ADV_NONCONN_IND      → 不可连接（单向广播，BLE 4.x）
ADV_SCAN_IND         → 可扫描不可连接
ADV_SCAN_REQ         → 扫描请求
ADV_SCAN_RSP         → 扫描响应
ADV_CONNECT_IND      → 连接请求（携带连接参数）
```

**PDU 长度**：

```text
BLE 4.x：最大 37 字节
BLE 5.x：扩展广播最大 255 字节
```

### 连接 PDU

```text
LL Data PDU：
  LL Control PDU     → 链路控制（更新参数、加密、PHY 切换等）
  LL Data PDU        → 承载 L2CAP 数据

每个连接事件：Master 在 Connection Interval 时刻发送，从机 Slave Latency 范围内响应
```

### 自适应跳频（AFH）

```text
信道图（Channel Map）：37 bit，每 bit 对应一个信道
  0 = 禁用，1 = 允许
Master 每 T_AFH（> 6s）广播新 Channel Map
禁用信道：Wi-Fi 占用 / 干扰严重 / RSSI 持续低
```

**实战**：

```text
产线 2.4GHz 干扰大 → 调 Channel Map 跳过 Wi-Fi 信道
跳频算法：c = (lastUsedChannel + hopIncrement) mod 37
hopIncrement 由主机选（5~16）
```

### CRC 与数据完整性

```text
CRC-24：所有 LL PDU 自带
MIC-32：加密 PDU 带，BLE 4.2+ Secure Connections
Whitening：解扰（信道频率相关）
```

## HCI（Host-Controller Interface）

### 三种 packet

```text
Command  → Host → Controller
Event    → Controller → Host
Data     ↔ 双向（ACL 数据 + SCO 音频）
```

### 传输方式

```text
UART（H4 / H5）：传统 NCP，1 Mbps 起步
SPI（HCI Over SPI）：高速
USB（H2）：手机 / PC
SDIO：少数芯片
```

### 关键 HCI 命令

```text
HCI_RESET
HCI_LE_SET_ADVERTISE_ENABLE
HCI_LE_SET_ADVERTISING_PARAMETERS
HCI_LE_CREATE_CONNECTION
HCI_LE_CONNECTION_UPDATE
HCI_LE_READ_RSSI
HCI_LE_ENCRYPT
HCI_LE_START_ENCRYPTION
HCI_LE_SET_PHY
```

### 关键 HCI Event

```text
HCI_COMMAND_COMPLETE
HCI_COMMAND_STATUS
HCI_LE_META_EVENT（子事件）：
  HCI_LE_ADVERTISING_REPORT
  HCI_LE_CONNECTION_COMPLETE
  HCI_LE_DISCONNECTION_COMPLETE
  HCI_LE_CONNECTION_UPDATE_COMPLETE
  HCI_LE_READ_REMOTE_USED_FEATURES_COMPLETE
  HCI_LE_PHY_UPDATE_COMPLETE
  HCI_LE_ENHANCED_CONNECTION_COMPLETE
```

## L2CAP（Logical Link Control and Adaptation Protocol）

### 信道

```text
LE-U  → 0x0004（无连接）
LE-C  → 0x0005（连接，固定信道 ID）
动态信道 → 0x0040 ~ 0x007F（BLE，5 个）
经典蓝牙 → 0x0040 ~ 0xFFFF
```

### 功能

```text
分片 / 重组：上层大包拆 LL PDU（≤ 251 字节）
MTU 协商：默认 23，可扩到 247
信道管理：经典蓝牙才有完整信道管理
```

### MTU 流程

```text
Client → Server：Exchange MTU Request (Client Rx MTU)
Server → Client：Exchange MTU Response (Server Rx MTU)
双方取 min(Client MTU, Server MTU) 作为最终 MTU
ATT 实际载荷 = MTU - 3
```

### L2CAP 进阶：ECFC + EATT（BLE 5.2+）

L2CAP 在 BLE 5.2+ 引入两个新机制，是协议深度的标志：

```text
LE Credit Based Flow Control（LE Credit Based FC / ECFC）：
  - 解决单 L2CAP 信道拥塞
  - 通过 credit 机制（初始 1-255 credit）控流
  - 接收端消耗 credit 后才能发新 PDU
  - 用于高吞吐场景（OTA / 音频）

Enhanced ATT（EATT）：
  - 走 ECFC 通道而非传统 ATT 信道
  - 多 ATT 通道并行
  - SPSM = 0x0027（EATT 协议标识）
  - 优势：可并发多个 GATT 操作（不死锁）

SPSM（Simplified Protocol Service Multiplexer）：
  - 0x0001：传统 L2CAP
  - 0x0002：SMP
  - 0x0027：EATT
  - 0x0080~0x00FF：厂商自定义

实战（NCP 模式 vs SoC 模式）：
  - BlueNRG-2/3 NCP 框架下：aci_* API 体系
  - Connection_Interval [7.5ms, 4000ms]（NCP 限制）
  - NCP 模式下 aci_* 不可在 SoC 单芯片直接调用
  - 必须先初始化 HCI 通道
```

### Connection Parameter 三件套（实战总结）

```text
NCP 框架下 Connection Parameter：
  - Connection_Interval：7.5ms ~ 4000ms（NCP 默认 30ms）
  - Slave_Latency：0 ~ 499（NCP 限制 < 100）
  - Supervision_Timeout：100ms ~ 32s（必须 > 2×（1+Latency）×Interval）

SPSM 用法：
  - Client 发起 L2CAP_Connect_Req (SPSM=0x0027) → 建立 EATT
  - Server 回 L2CAP_Connect_Rsp
  - 双方用 EATT 通道传 ATT PDU
  - 失败回退到传统 ATT（CID=0x0004）
```

## ATT（Attribute Protocol）

### 数据模型

```text
Attribute：
  Handle   → 16-bit 索引
  Type     → 128-bit UUID（16-bit 短 UUID 是别名）
  Value    → 任意二进制
  Permission → Read / Write / Encrypt / Authenticate
```

### PDU 类型

```text
Requests / Responses：成对，请求 - 应答模式
Commands / Notifications / Indications：单向
  Notifications → Server → Client，无需 ACK
  Indications  → Server → Client，需要 Client ACK
```

### Error Response

```text
0x01 INVALID HANDLE
0x02 READ NOT PERMITTED
0x03 WRITE NOT PERMITTED
0x05 INSUFFICIENT AUTHENTICATION
0x06 INSUFFICIENT AUTHORIZATION
0x07 INSUFFICIENT ENCRYPTION
0x0D INVALID ATTRIBUTE VALUE LENGTH  ← 长包没分片
0x0E UNLIKELY ERROR
0x13 APPLICATION ERROR 0x80+
```

## GATT（Generic Attribute Profile）

### 层级

```text
GATT Server 暴露：
  Service
    └─ Characteristic
          ├─ Value（数据）
          ├─ Descriptor（CCCD / Presentation Format / ...）
          └─ 多个 Characteristic
```

### 预定义 Service（UUID 16-bit）

| Service | UUID | 用途 |
| --- | --- | --- |
| Generic Access | 0x1800 | 设备名 / Appearance |
| Generic Attribute | 0x1801 | Service Changed（OTA 必须） |
| Battery Service | 0x180F | 电池电量 |
| Heart Rate | 0x180D | 心率 |
| Environmental Sensing | 0x181A | 温湿度气压 |
| HID | 0x1812 | 键盘鼠标 |
| Device Information | 0x180A | 厂商/固件版本 |
| Scan Parameters | 0x1813 | 扫描参数 |

### CCCD（Client Characteristic Configuration Descriptor）

```text
UUID 0x2902
Value：0x0000 = disable
       0x0001 = Notification
       0x0002 = Indication
CCCD 必须写入才能收到 Notify/Indicate，这是产线常见坑
```

### GATT 操作流程

```text
Discovery：
  Discover All Primary Services (0x2800)
    → 返回 Service 句柄范围
  Discover All Characteristics of Service
    → 返回 Characteristic Declaration
  Discover All Characteristic Descriptors
    → 返回 Descriptor 句柄

Read：
  Read Characteristic Value
  Read Characteristic Descriptors

Write：
  Write Characteristic Value
  Write Without Response
  Write Long（prepare + execute）

Notify / Indicate：
  Server 主动发，Client 必须先写 CCCD
```

## GAP（Generic Access Profile）

### 角色

```text
Broadcaster     → 单向广播
Observer        → 单向扫描
Peripheral      → 广播 + 可连接
Central         → 扫描 + 发起连接
```

### 状态机

```text
Standby → Advertising → Connection
Standby → Scanning → Initiating → Connection
Connection → Disconnection → Standby
```

### 配对方式

```text
Just Works      → 无用户交互，鉴权最弱
Passkey Entry   → 6 位数字码，安全性高
Numeric Comparison → LE Secure Connections 默认
Out of Band (OOB) → NFC 等带外传递
```

## SMP（Security Manager Protocol）

### 配对流程（LE Legacy）

```text
Phase 1（Pairing Feature Exchange）
  → 交换 IO Capability / AuthReq / 配对算法
  → 决定 STK 生成方式
Phase 2（Short Term Key 生成）
  → Just Works / Passkey / OOB → STK
  → STK 加密后续配对
Phase 3（Key Distribution）
  → IRK / CSRK / LTK / EDIV / Rand 分发
  → 存入 bonding flash
```

### LE Secure Connections（BLE 4.2+）

```text
ECDH P-256 替代 TK + STK
抗中间人（MITM）攻击
Passkey Entry：每次按键 1 bit，参与 ECDH
Numeric Comparison：双方算 6 位比较码，用户确认
```

### 配对参数 AuthReq

```text
Bonding Flag         → 是否存 bonding
MITM Flag            → 是否需中间人保护
SC Flag              → 是否 LE Secure Connections
Keypress Notification → 配对按键通知
CT2 / IO Capabilities → IO 能力
```

### 加密

```text
LL Encryption Start：
  Master → Slave: LL_START_ENC_REQ (Rand, EDIV, LTK)
  Slave 响应
  Master → Slave: LL_START_ENC_RSP
 双方启用加密，后续 PDU 带 MIC-32
```

### 加密源码级要点（Cordio 视角）

LL 加密的协议字段在 Cordio（以及大多数协议栈）里经过 `PalCryptoAesCcmEncrypt/Decrypt` 直接进 CCM-AES 引擎，下面这些是产线最容易踩的源码级细节：

```text
加密启动三步握手（顺序固定）：
  1. Master 发 LL_START_ENC_REQ，附 Rand（64-bit）/ EDIV（16-bit）/ LTK（128-bit）
  2. Slave 收到后，从 bonding flash 查 LTK，匹配 EDIV+Rand 才接受
  3. 双方 LL_START_ENC_RSP 之后立即启用加密

加密启动后所有 PDU 都带 MIC-32（CBC-MAC）：
  MIC 校验失败 → 立即断连，HCI 报 0x3D（MIC Failure）
  原因高发：时钟漂移导致 CCM Nonce 错位 / 重传时 PacketCounter 异常

LL_PAUSE_ENC_REQ / LL_PAUSE_ENC_RSP：
  Master 可以临时暂停加密（例如发身份挑战、更新 LTK）
  Slave 必须接受；Master 用 LL_START_ENC_REQ 重启加密
  Cordio 默认实现是立即回复，源码无需修改
```

### 异常码处理路径

```text
0x06  Memory Capacity Exceeded     设备 bonding flash 写满 → 清除 FDS 整片
0x1A  Pin or Key Missing           找不到匹配 LTK → 用户已解绑 / bonding 残留冲突
0x3D  MIC Failure                  加密链路被攻击或时钟漂移 → 立即断连 + 重新配对
0x3E  Connection Terminated         通用断开，看原因码（auth fail / user / low resource）
```

### Nonce 与 PacketCounter 关键点

```text
CCM Nonce = PacketCounter（39-bit）+ IV（8-bit）+ 方向 bit（1-bit）
  PacketCounter 永不复位，重传不会重新计数
  每发一包 +1，发完不归零，溢出后强制重连
非加密链路下 PacketCounter 仍递增（底层 LL 计数器）
加密启动前已发的包不加密；加密启动后从下一包开始加密
```

## BLE 5.x 扩展

### LE 2M PHY

```text
双倍速率，相同灵敏度略低
适合音频 / OTA 升级
HCI_LE_SET_PHY 切换
```

### LE Coded PHY

```text
前向纠错（FEC）：S=2 / S=8
S=8 比 LE 1M 灵敏度高 9 dB，速率 1/8
适合远距 / 工业传感
```

### Extended Advertising

```text
最大广播包：255 字节（BLE 4.x 仅 37 字节）
二级广播：ADV_EXT_IND 指到 AUX_ADV_IND
支持多 PHY 广播
```

### Periodic Advertising

```text
固定间隔的扩展广播 + AUX_SYNC_IND
多个 Observer 同步接收
适合 beacon / 传感器
```

### Connected Isochronous Stream（CIS / BIS）

```text
CIS：连接同步流（LE Audio 基础）
BIS：广播同步流
低延迟音频传输
```

## Privacy 与地址轮换

```text
Resolvable Private Address (RPA)：
  RPA = AES-128(IRK, prand) ^ 0x400000000000
  prand 高 2 bit = 01（标记为 Resolvable）
  每 15 分钟换一次

白名单扫描：
  Peer 用 IRK 解 hash
  不在白名单的扫描直接拒
```

## SoC vs NCP 调试差异

| 维度 | SoC | NCP |
| --- | --- | --- |
| 协议栈调试 | 用厂商 IDE（nRF Connect / Simplicity Studio） | 通过 HCI 命令（hcitool / btmon） |
| Crash 抓取 | IDE 内置 backtrace | NCP assert 通常只能断电重启，需 SWO 抓 |
| 内存占用 | 协议栈 + 应用共 RAM | 主机只跑 HCI，应用 RAM 充足 |
| 实时性 | 协议栈中断与应用耦合 | 主机可独立优化 |
| 升级 | OTA 协议栈 + 应用双区 | 协议栈固化在模块，只升级主机 |

**NCP 调试额外准备**：

- 留出 SWO 引脚
- 用 AN958 推荐的 10-pin Simplicity Connector
- 启用 ncp-debug-print 插件（依赖 Ember Minimal + Printf + Serial）

## 性能数据参考

```text
连接建立时间：~3 ms ~ 100 ms（取决于扫描窗口）
最大吞吐（LE 2M）：
  应用层 ~ 1.4 Mbps（理论）
  实际 ~ 800 kbps（受 LL PDU 间隔影响）

功耗（nRF52832 + Sensor）：
  连接（100ms interval）：平均 ~ 50 µA
  广播（1s interval）：   平均 ~ 200 µA
  深度睡眠：                ~ 1.5 µA
```

## 实战经验

- **0x3E CONN FAILED** 80% 是 Wi-Fi 干扰。解决：Channel Map 跳频 / 改连接参数避开 Wi-Fi 信道密集时段
- **配对反复失败**：bonding flash 残留老 LTK + 新 LTK 冲突。解决：清除 fds 整片
- **Notify 卡死**：CCCD 没写 0x0001。解决：连接后先做 Service Discovery → 写 CCCD
- **OTA 后连接不上**：Service Changed 没实现。解决：实现 0x2A05 特征
- **nRF51 频繁断连**：ADC 启停干扰晶振。解决：ADC 采集完关、晶振走线远离 ADC

## 关联文档

- `bus/ble.md` 主题入口
- `bus/ble-practical.md` 调试流程速查
- `bus/ble-failure-cases.md` 产线实战案例
- `bus/ble-index.md` 主题地图 + 导航
