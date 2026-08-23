# Thread Deep Dive

## 目标

深入 Thread 协议栈各层：IEEE 802.15.4 PHY/MAC / 6LoWPAN / IPv6 / UDP / CoAP / DTLS / MLE / RPL / Network Data / Commissioning / Border Router。目标读者：协议栈移植、产线深度故障定位、Thread 1.3+ / Matter 集成工程师。

## 协议栈分层

```text
┌─────────────────────────────────────────────────────┐
│ Application Layer                                  │
│  Matter / CoAP / MQTT / 私有应用                    │
├─────────────────────────────────────────────────────┤
│ CoAP (Constrained Application Protocol)            │
│  UDP 上运行的轻量 HTTP 替代                          │
├─────────────────────────────────────────────────────┤
│ DTLS 1.2 / TLS 1.3                                 │
│  UDP 加密                                            │
├─────────────────────────────────────────────────────┤
│ UDP                                                 │
├─────────────────────────────────────────────────────┤
│ IPv6 / 6LoWPAN                                      │
│  IPv6 头压缩 + 分片                                  │
├─────────────────────────────────────────────────────┤
│ RPL（路由协议）/ MLE（链路建立）                      │
│  DODAG 路由 + Mesh Link                             │
├─────────────────────────────────────────────────────┤
│ IEEE 802.15.4 MAC                                  │
│  CSMA/CA / ACK / Beacon                            │
├─────────────────────────────────────────────────────┤
│ IEEE 802.15.4 PHY                                  │
│  2.4 GHz OQPSK, 250 kbps                            │
└─────────────────────────────────────────────────────┘
```

**关键设计**：

- 基于 IPv6：每个设备有 IPv6 地址，端到端
- 基于 CoAP：轻量 RESTful 协议
- 基于 UDP：低功耗场景，不需 TCP 三次握手
- RPL：低功耗 mesh 路由标准
- 6LoWPAN：IPv6 over 802.15.4

## IEEE 802.15.4 PHY/MAC

Thread 用 IEEE 802.15.4 同 ZigBee：

```text
PHY：
  2.4 GHz OQPSK
  250 kbps
  信道 11-26
  DSSS 16-chip / 4-bit
  
MAC：
  CSMA/CA
  ACK（可选）
  Beacon（可选，Thread 实务不用）
```

## 6LoWPAN

### IPHC 头压缩

```text
IPv6 头（40 字节）：
  Version / TC / FL (4)
  Payload Length (2)
  Next Header (1)
  Hop Limit (1)
  Source Address (16)
  Destination Address (16)

6LoWPAN 头压缩后：
  IPHC header (2 字节)
  压缩源地址 (0-16 字节)
  压缩目标地址 (0-16 字节)
  压缩 Next Header (0-1 字节)

典型压缩比：40 字节 → 6-8 字节
```

### 6LoWPAN 分片

```text
IPv6 包 ≤ 1272 字节
802.15.4 MAC 帧 ≤ 127 字节（含 FCS）
IPv6 头压缩后剩余 ~ 100 字节

需要分片：
  第一个分片：Mesh + Frag1 header
  后续分片：FragN header
  分片重组：目标设备按 datagram tag + offset
```

### Mesh 转发

```text
Mesh 头：
  Origin address
  Final destination
  Hop count

多跳场景：
  Source → Router1 → Router2 → Destination
  每跳：Mesh header 减少 1 跳
```

## MLE（Mesh Link Establishment）

### 5 种 MLE 消息

```text
1. Link Request
   - 新节点发，发现邻居
   - 包含 Verkehrium 模式

2. Link Accept
   - Router 响应 Link Request
   - 包含 Leader Data + Source Address

3. Link Accept and Request
   - 双向链路确认 + 进一步请求

4. Link Update
   - 链路状态更新
   - 包含 Network Data

5. Data Request / Data Response
   - 拉取 Network Data
```

### MLE Parent Selection

```text
新节点选择父节点流程：
1. Discovery Request（MLE Link Request）
2. Discovery Response（MLE Link Accept）
3. 候选父节点列表
4. 根据 RSSI / 跳数 / 子节点数选最佳
5. 发送 Child ID Request
6. 收到 Child ID Response（含 RLOC16）
7. 进入 Child 状态
```

### MLE Security

```text
MLE 消息加密：
  - AES-CCM-32
  - 用 Network Key
  - 防重放：MLE Counter
```

## RPL（Routing Protocol for Low-Power and Lossy Networks）

### DODAG

```text
DODAG (Destination-Oriented Directed Acyclic Graph)：
  - 根节点：Border Router / Leader
  - 叶子节点：End Device
  - 中间节点：Router

DODAG 形态：
       Border Router (Rank=0)
         ├── Router (Rank=256)
         │     ├── End Device
         │     └── Router (Rank=512)
         └── Router (Rank=256)
                └── End Device
```

### RPL 消息

```text
DIO (DODAG Information Object)：
  Router → 广播 DODAG 信息
  包含：Rank / Instance ID / DODAG Version / Configuration

DAO (Destination Advertisement Object)：
  节点 → 父节点
  通告：前缀 / 目标地址 / Route

DIS (DODAG Information Solicitation)：
  节点 → 广播
  请求 DIO

CC (Consistency Check)：
  节点 → Leader
  一致性检查
```

### Objective Function (OF)

```text
OF0 (默认)：
  Rank = parent_rank + 255
  跳数大致

MRHOF (Minimum Rank with Hysteresis Objective Function)：
  Rank = parent_rank + 255 × weight / path_cost
  基于 ETX（Expected Transmission Count）
  防频繁切换
```

### RPL 修复

```text
DODAG 故障检测：
  链路超时 → 切父节点
  父节点全失败 → 上行切
  上行切失败 → Local Repair
  Local Repair 失败 → Global Repair（Leader 重选）
```

## Network Data

### 组成

```text
Network Data:
  - Prefix TLV
    - 网络 prefix（fd00::/64）
    - Border Router 拥有
  - Route TLV
    - 路由信息
    - 跨 prefix 路由
  - Service TLV
    - 服务发现
    - Leader / Commissioner / DHCP 等
```

### Network Data 同步

```text
Leader 维护 Network Data
子节点通过 MLE Data Response 拉取
Router 之间通过 MLE Data Request / Response 同步
```

## 地址

### 6 种 IPv6 地址类型

```text
1. ML-EID (Mesh-Local EID)
   形如 fdde:ad00:beef:0:fdad:beff:fe00:xxxx
   用于应用层
   派生自 EUI-64

2. RLOC (Routing Locator)
   形如 fdde:ad00:beef:0:ff:fe00:xxxx
   用于路由
   派生自 Router ID + Child ID

3. ALOC (Anycast Locator)
   形如 fdde:ad00:beef:0:fc00
   特殊功能（Leader / DHCP / Commissioner / ...）

4. Link-Local
   fe80::xxxx
   仅链路本地

5. ULA (Unique Local Address)
   全网唯一
   类似 IPv4 私有地址

6. GUA (Global Unicast Address)
   公网 IPv6
   Thread 不直接用，但 Border Router 可分配
```

### RLOC16 分配

```text
RLOC16 = Router ID (8 bits) × 0x0400 + Child ID (8 bits)
  
Router ID:
  0~62 (63 保留给 Leader)
  Leader 自动分配 Router ID
  Router ID 冲突 → Router ID 释放 / 重分配

Child ID:
  0 = Router 自身
  1~511 = 子节点
  子节点数：最大 511 / 父节点
  实际：默认 10，可配
```

## Border Router

### 角色

```text
Border Router:
  - 连接 Thread 网络 ↔ 外部 IP 网络（Wi-Fi / Ethernet）
  - 通告 Network Data（前缀 / 路由）
  - DHCPv6 / SLAAC 分配
  - NAT64 / DNS64（可选）
```

### 类型

```text
1. Basic Border Router
   - 仅路由

2. Border Router with DHCPv6 Server
   - 分配 IPv6

3. Border Router with SLAAC
   - 自动配置 IPv6

4. NAT64 Border Router
   - IPv6 ↔ IPv4 转换

5. DNS64 Border Router
   - DNS A 记录 → AAAA 记录合成
```

### 典型部署

```text
Border Router（树莓派 / NAS / Home Assistant Hub）
  │
  ├── Thread 网络
  │     ├── Router
  │     ├── End Device
  │     └── Sleepy End Device
  │
  ├── Wi-Fi 网络
  │     ├── 手机（Apple Home / Google Home）
  │     ├── 智能音箱
  │     └── 笔记本
  │
  └── Ethernet
        └── 桌面
```

## Commissioning（配网）

### 角色

```text
Commissioner:
  - 已有 Thread 设备
  - 负责验证 Joiner
  - 持有 Master Key

Joiner:
  - 未入网设备
  - 仅有 PSKd
  - 等待配对

Commissioner Candidate:
  - 候选 Commissioner
  - 等待被选
```

### 配网流程

```text
Step 1: 准备工作
  - Commissioner 启动（`commissioner start`）
  - Commissioner 加入自身到 Thread 网络

Step 2: 配 Joiner
  - Commissioner `add <EUI-64> <PSKd> <timeout>`
  - 内部派生 Joiner Key
  - Joiner Router Discovery：Joiner 找到 Commissioner

Step 3: Joiner 入网
  - Joiner 启动 Discovery Request
  - Commissioner 响应 Discovery Response
  - DTLS 握手（用 Joiner Key）
  - 验证 PSKd + EUI-64

Step 4: 分配 Network Key
  - Commissioner 发 Network Key + Master Key 派生
  - Joiner 用 Joiner Key 解密

Step 5: 加入 Thread 网络
  - Joiner 用 Network Key 加入
  - Leader 分配 RLOC16
  - 同步 Network Data

Step 6: 完成
  - Commissioner 显示 "Join success"
  - Joiner 进入 Child / Router 状态
```

### PSKc / Joiner Key 派生

```text
PSKc (Pre-Shared Key for the Commissioner)：
  PSKc = HMAC-SHA256(Master Key, EUI-64 || Joiner ID || Extended PAN ID)
  - Joiner ID：用户选择（PSKd 字符串）
  - Extended PAN ID：网络标识

Joiner Key：
  Joiner Key = PBKDF2(PSKc, "J-PANID||EUI-64||JoinerID", 1000, 256 bits)
  或
  Joiner Key = HMAC-SHA256(PSKc, "Thread")

差异：
  - 第一种（旧）：用 PSKd 直接派生
  - 第二种（Thread 1.3+）：PBKDF2 加强
```

### PSKd 编码

```text
PSKd = 8+ 字节 ASCII 字符串
  或 Base64 编码

常用 PSKd 格式：
  J01NME  → 6 位
  MTDOYSP  → 7 位
  123456  → 6 位数字

强度：
  8 字节 PSKd = 64 bits 安全
  16 字节 PSKd = 128 bits 安全
```

## 安全

### 密钥层级

```text
Master Key (16 字节)
  │
  ├── 派生 Network Key (16 字节)
  │     - 全网共享
  │     - MLE + MAC 加密
  │     - 通过 Network Data 同步
  │
  └── 派生 PSKc (16 字节)
        - Joiner 唯一
        - 派生 Joiner Key
        - DTLS 加密 Joiner 配对
```

### MLE Security

```text
MLE 消息加密：
  - AES-CCM-32
  - 加密：MLE 头 + MLE payload
  - 抗重放：MLE Counter + Timestamp

Network Key 派生：
  Network Key = HMAC-SHA256(Master Key, "ThreadMasterKey")
  或厂商自定
```

### DTLS

```text
Joiner ↔ Commissioner:
  - DTLS 1.2 over CoAP
  - Pre-Shared Key 模式
  - 验证 PSKd

CoAP：
  - 默认端口 61631
  - 资源：/c/cs (commissioning session)
  - 资源：/c/cl (commissioning leader)
  - 资源：/c/ca (commissioning auxiliary)
```

### 链路层加密

```text
802.15.4 MAC 加密：
  - AES-CCM-32
  - Network Key
  - Frame Counter 防重放
  - Key Identifier
```

## 数据流（端到端）

### 端到端通信

```text
应用层
  ↓ CoAP request/response
UDP（端口 61631 等）
  ↓ IPv6 头压缩
6LoWPAN
  ↓ 路由（RPL）
RPL Router
  ↓ 802.15.4 MAC（加密）
802.15.4 PHY
  ↓ RF（OQPSK）
无线 mesh
  ↓ 多跳
目标设备

跨 Thread ↔ Wi-Fi：
  Border Router
  ↓ 802.15.4 ↔ 802.11
Wi-Fi 网络
  ↓
手机 / 智能音箱
```

### 延迟

```text
单跳：~10-30 ms
多跳：~10-30 ms/跳
最大跳数：默认 30（协议规定）
推荐深度：≤ 5
```

## 性能数据

```text
入网时间：
  Discovery: ~1-2 s
  DTLS 握手: ~500 ms
  Network Key 传输: ~100 ms
  加 Thread: ~500 ms
  总: ~3-5 s

吞吐：
  应用层（CoAP）：~30-50 kbps（802.15.4 250 kbps PHY）
  多跳：~10-20 kbps

功耗（Sleepy End Device）：
  唤醒 30ms / 周期 3s = 1% duty
  平均 ~80 µA
  CR2477 撑 1.5 年
```

## 厂商协议栈对比

| 维度 | OpenThread | nRF Connect SDK | GSDK (Silicon Labs) | Z-Stack + Thread (TI) |
| --- | --- | --- | --- | --- |
| 厂商 | OpenThread / Google | Nordic | Silicon Labs | TI |
| License | BSD | Apache 2.0 | Zephyr-based | TI Proprietary |
| 芯片 | 通用（Linux / MCU） | nRF52840/nRF5340 | EFR32 | CC2652 |
| Matter 集成 | Yes | Yes | Yes | Yes |
| Border Router | Yes（OTBR） | Yes | Yes | Yes |
| Commissioner | Yes | Yes | Yes | Yes |
| 文档 | 详尽 | 详尽 | 详尽 | 一般 |
| 社区 | 活跃 | 活跃 | 活跃 | 较小 |

## 实战经验

- **Commissioner 找不到 Joiner**：PSKc 派生错 + 信道错
- **Channel Mask 全部清 0**：工程师测试时清空，恢复时忘记写
- **多 Thread 网络共信道**：邻居 PAN ID 干扰
- **REED 升级 Router 失败**：子节点数限制 + 路由表满
- **RPL 路由震荡**：链路质量差 + 频繁切换
- **Border Router 切换**：IP 冲突 / Wi-Fi 切换
- **Sleepy End Device 频繁唤醒**：Poll Interval 错 + 父节点丢失

## 关联文档

- `bus/thread.md` 主题入口
- `bus/thread-practical.md` 调试流程速查
- `bus/thread-failure-cases.md` 产线实战案例
- `bus/thread-index.md` 主题地图 + 导航
- `bus/matter-*.md` Matter over Thread
- `bus/zigbee-*.md` 同源 PHY 对比
