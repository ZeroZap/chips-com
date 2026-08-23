# Thread Practical Guide

## 目标

本文用于 Thread 工程调试：入网、Commissioner / Joiner、Border Router、Channel Mask、Network Data、6LoWPAN、产线常见故障的快速定位。

## 最小接线（以 nRF52840 为例）

```text
VDD ──── VDD (1.7~5.5V)
GND ──── GND
ANT ──── 2.4GHz 天线（PCB 走线 / 陶瓷 / IPEX）
DEC1 ──── 100nF + 10µF 紧靠 VDD
DEC2 ──── 100nF 紧靠 DEC1 引脚
SWD ────── 调试口
RESETn ─── 10kΩ 上拉
```

**关键约束**：

- 2.4 GHz 天线 50Ω 匹配
- 走线避开 DC-DC 噪声
- Reset 引脚必须上拉
- DC-DC 模式（nRF52840）需外置 L/C 滤波器

## 关键参数

### Channel

```text
IEEE 802.15.4 信道 11~26 (2.4 GHz)
  间隔 5 MHz
  Channel Page 0: 2.4 GHz 11-26（Thread 主用）
  Channel Page 1: 868 / 915 MHz（Thread 备用）
```

**信道选择**：

| Channel | 中心频率 (MHz) | Wi-Fi 重叠 |
| --- | --- | --- |
| 11 | 2405 | Wi-Fi 1（最差） |
| 15 | 2425 | Wi-Fi 1~4 |
| 20 | 2450 | **Wi-Fi 6**（最差） |
| 25 | 2475 | Wi-Fi 11+ |
| 26 | 2480 | Wi-Fi 14（部分国家禁用） |

**推荐**：避 Wi-Fi 1/6/11 → 选 12-14, 16-19, 21-24。

**Channel Mask**：

```c
// 避 Wi-Fi 1, 6, 11
uint32_t channel_mask = 0x07FFE400;
// bit 11=0, 20=0, 25=0, 其余 1
```

### Network 标识

```text
PAN ID（2 字节）：
  0x0000~0xFFFE（用户可用）
  0xFFFF reserved

Extended PAN ID（8 字节）：
  全网唯一
  工厂批量烧录

Network Name（≤16 字节）：
  ASCII 字符串
  工厂批量烧录

Network Key（16 字节）：
  AES-128
  整个网络共享
  派生自 Master Key

Master Key（16 字节）：
  派生 Network Key 的种子
  仅 Border Router / Commissioner 持有
```

### 地址

```text
EUI-64（8 字节）：
  IEEE 802.15.4 设备唯一
  工厂烧录
  不可变

ML-EID（Mesh-Local EID）：
  IPv6 地址
  派生自 Extended Address + Network Prefix
  网络内唯一

RLOC（Routing Locator）：
  IPv6 地址
  派生自 Router ID + Child ID
  用于 RPL 路由

ALOC（Anycast Locator）：
  IPv6 地址
  用于服务发现（Commissioner / Leader / DHCP 等）
```

### PSKc

```text
PSKc (Pre-Shared Key for the Commissioner)：
  派生 Joiner Key
  公式：
    PSKc = HMAC-SHA256(Master Key, 
                        EUI-64 || JoinerID || Extended PAN ID)
  Joiner 用 PSKc + EUI-64 派生 Joiner Key
  Joiner Key 用于 DTLS 加密与 Commissioner 通信
```

## 抓包工具

| 工具 | 平台 | 优势 | 限制 |
| --- | --- | --- | --- |
| nRF Sniffer for Thread | nRF52840 DK | 免费 | 仅 Thread 流量 |
| Wireshark + Thread dissector | 全平台 | 开源 | 需 dongle |
| OT CLI | CLI | 厂商自带 | 仅本地设备 |
| Simplicity Studio Network Analyzer | Windows | EFR32 官方 | 仅 Silicon Labs |
| Border Router Web UI | Browser | 看完整网络拓扑 | 需 BR |
| Home Assistant + OpenThread Border Router | 树莓派 | 真实生态 | 需树莓派 |

**产线推荐**：

```text
研发：nRF Sniffer for Thread + Wireshark
产线：OT CLI 看 thread start / state / neighbor / child
客户：Border Router Web UI 看拓扑 + 设备状态
```

**OT CLI 常用命令**：

```text
> state                    // 看本节点状态（disabled/detached/child/router/leader）
> networkname              // 看网络名
> channel                  // 看信道
> panid                    // 看 PAN ID
> extpanid                 // 看 Extended PAN ID
> networkkey               // 看 Network Key
> masterkey                // 看 Master Key
> ipaddr                   // 看 IPv6 地址
> child list               // 看子节点
> child table              // 看子节点表
> router list              // 看路由器列表
> router table             // 看路由表
> neighbor list            // 看邻居表
> parent                   // 看父节点
> leaderdata               // 看 Leader Data
> networkdata              // 看 Network Data
> scan                     // 扫描信道
> joiner start <PSKd>      // 启动 Joiner（用 PSKd 派生 PSKc）
> commissioner start       // 启动 Commissioner
> commissioner add <eui64> <PSKd> <timeout>  // 配对 Joiner
> thread start             // 启动 Thread 网络
> thread stop              // 停止 Thread 网络
> factoryreset             // 恢复出厂
> reset                    // 软重启
```

## 调试步骤

1. **量天线**：VNA 验证 S11 < -10 dB
2. **看 Network Key / Master Key 配齐**：工厂烧录正确
3. **看 Commissioner**：OT CLI `commissioner start`
4. **看 Joiner 入网**：OT CLI `joiner start <PSKd>`
5. **看 Router / End Device 状态**：`state` 命令
6. **看 Thread 网络**：`neighbor` `router` `child`
7. **看 Network Data**：`networkdata` 看 prefix / route / service
8. **测 Border Router**：从 Wi-Fi ping Thread 设备
9. **测端到端延迟**：ping / curl 测时延

## 常见问题速查

| 现象 | 优先检查 |
| --- | --- |
| Joiner 入网失败 | PSKc 派生错 / Channel Mask 错 / IEEE 错位 |
| Commissioner 找不到 Joiner | 信道错 / Network Key 不匹配 / 时间窗过 |
| End Device 找不到父节点 | 父节点已掉 / 网络饱和 / RSSI 弱 |
| Border Router 不通 | Wi-Fi 切换 / IP 冲突 / SLAAC 错 |
| RPL 路由震荡 | 链路质量差 / Leader 切换 |
| Channel Mask 限制错 | 误限制可用信道 / 全部清 0 |
| 多 Thread 网络互踩 | 邻居 PAN 干扰 / Channel Mask 不一致 |
| Sleepy End Device 频繁唤醒 | Poll Interval 错 / 父节点丢失 |
| 设备不支持 Router | 默认 MED（不是 FTD） |
| IPv6 不通 | MLE 链路错 / RPL 路由错 |

## 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| Joiner 找不到 Commissioner | PSKc / 信道 / 网络 Key 错 | 核对配置 + scan |
| 入网后立即掉 | 网络 Key 不匹配 | 重新配 Network Key |
| End Device 找不到父 | 网络饱和 / 距离远 | 加 Router 备份 |
| RPL 路由震荡 | 链路质量差 | 看 neighbor RSSI |
| Border Router 不通 | Wi-Fi 切换 | 重启 BR |
| 设备支持不了 Router | 默认 MED | 改 FTD 配置 |
| 跨 PAN 互踩 | 邻居干扰 | 改 Channel / Extended PAN ID |
| IPv6 通信断 | MLE 链路错 | 看 neighbor / child table |
| Sleepy 频繁醒 | Poll Interval 错 | 调到 60s+ |
| 多网共信道 | Channel Mask 没限 | 加 Channel Mask |

## 错误码速查

### MLE 错误

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x01 | Disconnect | MLE 断开 |
| 0x02 | Resource exhaustion | 资源耗尽 |
| 0x03 | Parse error | 解析错 |
| 0x04 | Unsupported Version | MLE 版本不支持 |
| 0x05 | Key Identifier | Key 错 |
| 0x06 | No Address | 无可用地址 |
| 0x07 | Duplicate Address | 地址冲突 |
| 0x08 | Max Children | 子节点超限 |
| 0x09 | Not Found | 找不到 |

### Commissioner / Joiner 错误

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x00 | Success | 正常 |
| 0x01 | Scan Timeout | 扫描超时 |
| 0x02 | Scan Err | 扫描错 |
| 0x03 | Join Failed | 加入失败 |
| 0x04 | Join Timeout | 加入超时 |
| 0x05 | Join Security | 安全校验失败 |
| 0x06 | Join InvalidArgs | 参数无效 |
| 0x07 | Join Operational | 状态错（未停） |
| 0x08 | Join Detached | 状态错（已 detached） |
| 0x09 | Join No Thread | 无 Thread 网络 |
| 0x0A | Join Bus | 忙 |

### RPL 错误

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x00 | Success | 正常 |
| 0x10 | General Failure | 通用失败 |
| 0x11 | Authentication Failure | 验证失败 |
| 0x12 | Key Refresh | Key 更新中 |
| 0x13 | Memory | 内存不足 |
| 0x20 | Loss | 链路丢包 |
| 0x21 | Config Error | 配置错 |

## Border Router 配置

**OpenThread Border Router (OTBR)**：

```bash
# 1. 树莓派 + nRF52840 USB dongle
sudo ot-cli-ftd > /dev/null &
sudo ot-ctl

# 2. 启动网络
panid 0x1234
channel 15
networkname "MyThreadNet"
networkkey 00112233445566778899aabbccddeeff
masterkey 00112233445566778899aabbccddeeff
extpanid 0011223344556677
ipaddr fd00::1/64
ifconfig up
thread start

# 3. 启动 Border Router
sudo otbr-agent -I wpan0 -B eth0
```

**Home Assistant 集成**：

```yaml
# configuration.yaml
otbr:
  url: http://localhost:8081
  # 自动发现 Thread 设备
```

**Apple Home / Google Home 共享 Border Router**：

```text
iOS Home:
  - 系统设置 → Thread → 加入 Border Router
  - 一键把 BR 加入 Apple Thread Fabric

Google Home:
  - Google Home → Thread → 加入
```

## Sleepy End Device 配置

```c
// 关键参数
#define SED_POLL_INTERVAL    3000    // 3s（典型）
#define SED_KEEPALIVE        7000    // 7s
#define SED_TIMEOUT          240     // 4 分钟（默认）
// Sleepy End Device 必须 ≥ 父节点 Timeout
// 父节点 Child Timeout 需 ≤ SED_TIMEOUT
```

**功耗估算**：

```text
唤醒 30ms / 周期 3s = 1% duty
唤醒 8 mA，平均 = 8 × 0.01 = 80 µA
睡眠 3 µA
总平均 ≈ 83 µA

CR2477 = 1000 mAh
1000 / 0.083 / 24 / 365 = 1.37 年 ≈ 撑 1.5 年
```

## Channel Mask 实战

```c
// 默认 Channel Mask（包含所有 11-26）
uint32_t channel_mask = 0x07FFF800;

// 推荐（避 Wi-Fi 1, 6, 11）
uint32_t channel_mask = 0x07FFE400;
// 11=0, 20=0, 25=0

// 楼宇（仅 12-14, 16-19, 21-24）
uint32_t channel_mask = 0x07FFE400;

// 工厂 / 仓库（Wi-Fi 6 干扰大）
// 改用 11+15+19+25（5 MHz 间隔）
uint32_t channel_mask = 0x08280000;  // bit 11, 15, 19, 25 = 1
```

## 调试检查清单

```text
□ 电源：1.7~5.5V 稳压，纹波 < 50mV
□ 去耦：每个 VDD 引脚 100nF + 10µF 紧靠
□ 天线：50Ω 匹配，VNA 验证 S11 < -10dB
□ 晶振：32 MHz（HFXO）+ 32.768 kHz（LFXO）
□ Reset：10kΩ 上拉
□ 协议栈：OpenThread 1.3+ / nRF Connect SDK
□ EUI-64：工厂烧录唯一
□ Network Key：全网共享，Master Key 仅 BR/Commissioner
□ PSKc：派生正确（HMAC-SHA256）
□ Channel：避 Wi-Fi 1, 6, 11
□ Channel Mask：限制可用信道
□ Extended PAN ID：全网唯一
□ 设备类型：FTD（Router）vs MED（End Device）vs SED（Sleepy）
□ 子节点数限制：默认 10
□ RPL 路由：链路质量监控
□ Border Router：Wi-Fi/Ethernet 接入配置
□ Network Data：prefix / route / service
□ Sleepy 配置：Poll Interval + Timeout 配对
□ 抓包：nRF Sniffer for Thread
```

## 关联文档

- `bus/thread.md` 主题入口
- `bus/thread-deep-dive.md` 协议栈深挖
- `bus/thread-failure-cases.md` 产线实战案例
- `bus/thread-index.md` 主题地图 + 导航
- `bus/matter-*.md` Matter over Thread
- `bus/zigbee-*.md` 同源 PHY 对比
