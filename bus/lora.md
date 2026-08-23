# LoRa / LoRaWAN

## 定位

LoRa（Long Range）是 Semtech 2013 年推出的 chirp spread spectrum（啁啾扩频）物理层调制，工作在 Sub-GHz ISM 免许可频段。LoRaWAN 是 LoRa Alliance 2015 年发布的 MAC 层协议，定义在 LoRa PHY 之上。典型覆盖 2~15 km（视距）、AA 电池寿命 5~10 年，是远距低功耗 IoT 事实标准。

典型场景：智能水电气表、智慧农业土壤/气象、资产追踪（集装箱/牲畜/共享设备）、环境监测、智慧停车。

核心特点：

- 远距（10 km+ 视距，城市场景 2~5 km，地下穿透强）
- 极低功耗（AA 电池 5~10 年，待机 < 2 µA）
- 小数据（典型 payload 11~51 字节）
- 免许可频段（CN470 / EU868 / US915 等）
- 强抗干扰（chirp 扩频 + FEC + 跳频）

## LoRa 与 LoRaWAN 的关系

```text
LoRa      → PHY 调制（Semtech 专利，芯片实现）
LoRaWAN   → MAC 层协议（LoRa Alliance 开放规范）
应用层    → 用户私有 / LoRaWAN Application Layer
承载网络  → LoRaWAN Network Server（TTN / ChirpStack / Helium / 自建）
```

LoRa 是"调制方式"（类似 FSK），LoRaWAN 是"网络协议"（类似 TCP/IP）。采购芯片主要看 LoRa 调制 + 频段支持，LoRaWAN 协议栈由 NS + 终端固件实现。

## 跟其它无线协议的关系

| 协议 | 距离 | 速率 | 功耗 | 频段 | 典型场景 |
| --- | --- | --- | --- | --- | --- |
| **LoRa / LoRaWAN** | 2~15 km | 0.3~50 kbps | 极低 | Sub-GHz | 远距传感 / 资产追踪 |
| Wi-Fi | 30~100 m | 几十~几百 Mbps | 高 | 2.4/5 GHz | 高速本地 / 视频 |
| BLE | 10~100 m | 1~2 Mbps | 极低 | 2.4 GHz | 可穿戴 / 手机外设 |
| ZigBee / Thread | 30~100 m | 250 kbps | 低 | 2.4 GHz | 智能家居 / Mesh |
| NB-IoT | 10+ km | 26/62 kbps | 中 | 蜂窝授权 | 蜂窝物联网 |

**互补关系**：LoRa vs Wi-Fi/BLE/ZigBee 完全互补（远距低速 vs 短距高速）。LoRa vs NB-IoT 是直接竞争（免许可自建网 vs 蜂窝流量费）。

## 设备类型（Class）

```text
Class A  → 双向（终端上行后开两个短下行窗口），最低功耗，必实现
Class B  → 双向 + 同步下行（网关周期性 beacon，终端按调度开窗）
Class C  → 双向 + 持续下行接收（仅在不发包时），功耗最高
```

实战选型：电池传感 → Class A（99% 场景）；需要周期性下行 → Class B；实时控制 → Class C（通常有外供电）。

## 关键概念

- **SF（Spreading Factor）**：SF7~SF12，越大越远越慢越省电（+2.5 dB/级灵敏度）
- **BW（Bandwidth）**：125 / 250 / 500 kHz，越窄越远越慢
- **CR（Coding Rate）**：4/5 ~ 4/8，FEC 开销
- **Duty Cycle**：EU868 强制 1%，CN470/US915 无强制
- **ADR（Adaptive Data Rate）**：NS 根据链路质量调 SF/BW/TX
- **OTAA（Over-The-Air Activation）**：动态入网，安全性高，量产必选
- **ABP（Activation By Personalization）**：烧录固定密钥，免 join，但重放风险
- **DevEUI / AppEUI / DevAddr**：64-bit 终端 ID / 64-bit 应用 ID / 32-bit 网络地址
- **AppKey / NwkSKey / AppSKey / MIC**：应用根密钥 / 网络会话密钥 / 应用会话密钥 / 4 字节完整性校验
- **Frame Counter**：上下行各 16-bit，防重放

## 频段（区域）

| 区域 | 频段 | 通道数 | Duty Cycle | 备注 |
| --- | --- | --- | --- | --- |
| CN470 | 470~510 MHz | 96 + 48 | 无强制 | 国内出货必选 |
| EU868 | 863~870 MHz | 8（必选 3） | 1%（强制） | 欧洲 |
| US915 | 902~928 MHz | 64 + 8 | 无强制 | 美国 |
| AS923 | 915~928 MHz | 16 | 1%（部分） | 东南亚 |
| AU915 | 915~928 MHz | 64 + 8 | 无强制 | 澳大利亚 |
| IN865 | 865~867 MHz | 3 | 1% | 印度 |

**重要**：CN470 是国内出货必选，EU868 / US915 出口需要换固件 + 改射频参数。

## 典型芯片

| 芯片 | 厂商 | 频段 | 特点 |
| --- | --- | --- | --- |
| SX1276 | Semtech | 137~1020 MHz | LoRa + FSK + OOK，远距基础款 |
| SX1278 | Semtech | 137~525 MHz | 433/470 MHz 优化，国内常用 |
| SX1262 | Semtech | 150~960 MHz | 新一代，低功耗 +14 dBm |
| SX1268 | Semtech | 410~810 MHz | SX1262 国内频段版 |
| SX1302 / SX1303 | Semtech | sub-GHz | **8 信道网关基带**，LoRaWAN NS 配套 |
| LLCC68 | Semtech | 150~960 MHz | 低成本端点，SX126x 简化版 |
| LoRa1280 | 国产 | 2.4 GHz | 2.4 GHz LoRa（非 ISM sub-GHz） |
| ASR6601 | 翱捷 | 150~960 MHz | SoC 集成（MCU + LoRa），国产优先 |

## 抓包 / 调试工具

- **LoRa Sniffer + Wireshark + LoRa TAP**：解 LoRaWAN MAC 帧
- **ChirpStack**：开源 NS，自带 frame log + payload decoder
- **TTN Decoder (Payload Formatter)**：应用层 payload JS 解析
- **LoRaMac-node (Semtech 官方)**：参考实现 + sniffer 源码
- **SDR (HackRF / LimeSDR)**：看空中 RF 定位干扰
- **OTII / Joulescope**：功耗测量

## Network Server（NS）

| NS | 形态 | 特点 | 适用 |
| --- | --- | --- | --- |
| TTN (The Things Network) | 公有云 | 免费层 200 节点 | 学习 / 小规模 PoC |
| ChirpStack | 开源自建 | 私有部署，PG + Redis + MQTT | 中大规模 / 商业 |
| Helium | 区块链激励 | 衰落，慎选 | 边缘场景 |
| AWS IoT Core for LoRaWAN | 云服务 | 集成 AWS IoT，按设备数计费 | 大规模 |

## 配网：OTAA vs ABP

```text
OTAA（推荐，量产必用）：
  1. 终端发 Join Request（DevEUI + AppEUI + DevNonce）
  2. NS 校验 → 生成 NwkSKey + AppSKey
  3. NS 下发 Join Accept（DevAddr + 密钥 + 频段）
  4. 每次重连换新会话密钥，安全性高

ABP（生产测试用，不推荐量产）：
  1. 出厂烧录 NwkSKey + AppSKey + DevAddr（固定）
  2. 直接用固定密钥发数据，不走 Join
  3. Frame Counter 重启后从 0 → 重放风险
```

## 安全

```text
AppKey      → 128-bit 应用根密钥（OTAA Join 用）
NwkSKey     → 128-bit 网络会话密钥（加密 MAC 头 + MIC）
AppSKey     → 128-bit 应用会话密钥（加密应用 payload + MIC）
MIC         → 4 字节 CMAC/AES-128 完整性校验
Frame Counter → 上下行各 16-bit，每次 +1
```

**实战要点**：AppKey 每批次独立（不要全网共用）；DevNonce 必须随机；ChirpStack 默认 root key 需改成 device-specific。

## 嵌入式产线典型故障

- **Join Fail（DevNonce 重放）**：终端 DevNonce 复位后重复 → NS 拒
- **MIC Failure**：AppKey 错配 / NS 端密钥不匹配
- **Duty Cycle 超限**：EU868 1% 超 → 数据丢失
- **ADR 收敛慢**：SF12 起步不收敛 → 流量低 / 功耗大
- **频段错配**：CN470 固件烧到 US915 设备 → 完全搜不到
- **天线匹配差**：868/915 MHz 走线不连续 → RSSI 差 10 dB
- **GW 容量打满**：8 信道 GW 跑 1000 节点 → 排队秒级
- **Class B sync 漂移**：GPS 失锁 → beacon 错过 → 下行丢失

## 延伸阅读

- `bus/lora-practical.md` 调试流程速查 / 5 秒定位 / 错误码
- `bus/lora-deep-dive.md` 协议栈 / 调制 / 配网 / 安全 / NS 深挖
- `bus/lora-failure-cases.md` 产线实战案例（Join Fail / MIC / Duty Cycle 等）
- `bus/lora-index.md` 主题地图 + 读者路径
