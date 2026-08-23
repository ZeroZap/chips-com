# LTE-IoT（蜂窝物联网）

## 定位

LTE-IoT 是 3GPP 在 Release 13（2016）起为物联网定义的蜂窝接入技术族，统称 CIoT（Cellular IoT）。三大类别：

```text
Cat 1        → 中速（10 Mbps DL / 5 Mbps UL），全 LTE 协议栈，移动性好
Cat M1       → 中速移动（eMTC，~300 kbps），半双工，省电
NB-IoT       → 静态低功耗（Cat NB1 / NB2，~26 kbps），深覆盖，10 年电池
```

核心特点：

- **复用 LTE 基础设施**：基站、核心网（EPC / 5GC）共享。
- **频谱授权**：与 4G / 5G 共存或独立部署。
- **覆盖增强**：Cat M1 15 dB、NB-IoT 20 dB MCL。
- **海量连接**：每小区 ~5 万设备（NB-IoT）。
- **嵌入式产线最常见的"装卡就上网"无线方案**。

## 三大类对比

| 维度 | Cat 1 | Cat M1 (eMTC) | NB-IoT (Cat NB1/NB2) |
| --- | --- | --- | --- |
| 峰值速率 DL | 10 Mbps | ~300 kbps | ~26 kbps / ~127 kbps |
| 带宽 | 20 MHz | 1.4 MHz | 200 kHz |
| 双工 | 全双工 FDD | 半双工 FDD | 半双工 |
| 移动性 | 高（小区切换） | 中 | 低（不支持切换） |
| 语音 | VoLTE | VoLTE | 不支持 |
| 覆盖增强 | 0 dB | 15 dB | 20 dB |
| 待机功耗 | mA 级 | µA 级（PSM 10 µA） | µA 级（PSM < 5 µA） |
| 典型场景 | POS、车载、监控 | 穿戴、车队、追踪 | 抄表、烟雾、停车 |

## 跟其它无线技术的关系

```text
5G RedCap (eRedCap)         → 3GPP R17/18，下行 ~10 Mbps，5G IoT 过渡
传统 4G LTE Cat 4/6/12     → 高带宽，非 IoT 优化，CPE / 移动终端
LTE-IoT (Cat 1 / M1 / NB)  → 蜂窝 IoT 三大类，授权频谱
BLE / ZigBee / Thread      → 短距非授权（2.4 GHz），互补
LoRa / Sigfox              → 远距非授权（Sub-1 GHz），更远更低速
```

## 国内频段

| 运营商 | 频段 | 频率 | 主力类 |
| --- | --- | --- | --- |
| 中国移动 | B8 | 900 MHz (FDD) | NB-IoT |
| 中国移动 | B39 / B40 / B41 | 1880~2675 MHz (TDD) | Cat 1 |
| 中国电信 | B1 / B3 | 1800/2100 MHz (FDD) | Cat 1 / Cat M1 |
| 中国电信 | B5 | 850 MHz (FDD) | NB-IoT |
| 中国联通 | B1 / B3 | 1800/2100 MHz | Cat 1 / Cat M1 |
| 中国联通 | B8 | 900 MHz | NB-IoT |
| 广电 | B28 | 700 MHz (FDD) | NB-IoT（新频段） |

模组选频段必查运营商部署白皮书，国内 NB-IoT 主流是 B3/B5/B8。

## 关键概念

- **LTE Category**：3GPP UE 能力等级（Cat 1 / M1 / NB1/NB2）。
- **SIM / eSIM / iSIM**：物理卡 / 焊板嵌入式 / 集成到 SoC 内部。
- **IMSI / IMEI**：用户识别 / 设备识别，各 15 位。
- **APN (Access Point Name)**：接入点，决定公网 / 专网。
- **蜂窝模组**：射频 + 基带 + 协议栈一体化，通过 AT 命令控制。
- **PSM / eDRX / DRX**：省电三件套（连接态 / 空闲态 / 极致省电）。
- **PLMN / EPS / EPC**：运营商识别 / LTE 端到端 / LTE 核心网。
- **Bearer**：EPS 承载，附着时建立默认承载。

## 典型芯片 / 模组

| 模组 | 平台 | 类 | 频段 |
| --- | --- | --- | --- |
| 移远 EC200N / EC600N | 紫光展锐 UIS8910 | Cat 1 bis | B1/B3/B5/B8 + TDD |
| 移远 EC800N | 紫光展锐 UIS8910DM | Cat 1 bis（mini PCIe） | B1/B3/B5/B8 |
| 移远 BG95 / BG77 | Qualcomm MDM9205 / 212 | Cat M1 / Cat NB1/NB2 | 全球多频段 |
| 广和通 L610 | 紫光展锐 UIS8910 | Cat 1 bis | 全 TDD + FDD |
| 广和通 MC615 | Qualcomm MDM9205 | Cat M1 / NB-IoT | 多频段 |
| 芯讯通 SIM7000 | Qualcomm MDM9206 | Cat M1 / NB1 / GSM | 多频段 |
| 芯讯通 SIM7080 | Qualcomm MDM9205 | Cat M1 / NB1/NB2 | 多频段 |
| 芯讯通 SIM7600 | 高通 / 联发科 | Cat 4 / Cat 1 | 多频段 |
| 有方 N58 | 紫光展锐 UIS8910 | Cat 1 bis | 全 TDD + FDD |
| 有方 N21 | Qualcomm | Cat M1 / NB-IoT | 多频段 |
| Nordic nRF9160 | Qualcomm 内核 | Cat M1 / NB-IoT + GPS | 集成 Cortex-M33 应用核 |

## 抓包工具

| 工具 | 平台 | 优势 | 限制 |
| --- | --- | --- | --- |
| QLog / QXDM | Qualcomm 平台 | 完整 NAS / AS / RRC / PDCP log | 需高通平台 |
| 串口 log + AT 回显 | 通用 | 必备、最快 | 浅层 |
| Wireshark + 3GPP dissector | PC | 解析 S1AP / NAS / Diameter | 需 pcap 源 |
| Tracealyzer | 通用 RTOS | 任务级时序 | 不解析蜂窝 |
| MobileInsight | 开源 Python | 解析 Android logcat LTE | 仅 Android |
| CMW500 / MT8821C | 协议分析仪 | 商用级 L3 + 模拟弱信号 | 贵 |

**产线推荐组合**：串口 log + AT 回显（必）+ QXDM（高通可选）+ CMW500（弱信号压测）。

## 典型故障速览

- **+CME ERROR 514**：并发 AT 命令阻塞。
- **+CMS ERROR 30**：搜不到网络。
- **附着失败 / PDP 激活失败**：APN 错、SIM 未识别、PLMN 不匹配。
- **DNS 解析失败**：APN 没带 DNS、私网限制。
- **TCP 连接超时**：RSRP < -110 dBm、NAT 老化、空口拥塞。
- **PSM 退出失败**：T3412 / T3324 定时器未到。

## 延伸阅读

- `bus/lte-iot-practical.md` 调试流程速查 / 5 秒定位 / 错误码表
- `bus/lte-iot-deep-dive.md` 协议栈 / 蜂窝注册 / PSM/eDRX / 信令深挖
- `bus/lte-iot-failure-cases.md` 产线实战案例（附着 / PDP / DNS / TCP 等）
- `bus/lte-iot-index.md` 主题地图 + 读者路径
