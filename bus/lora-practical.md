# LoRa Practical Guide

## 目标

本文用于 LoRa / LoRaWAN 工程调试：频段配置、SF/BW/CR 参数、OTAA 配网、ADR 调优、抓包、错误码、产线常见故障的快速定位。

## 最小接线（以 SX1262 + STM32 为例）

```text
VDD      ──── 3.3V (1.8~3.7V)
GND      ──── GND
SCK      ──── SPI SCK
MOSI     ──── SPI MOSI
MISO     ──── SPI MISO
NSS      ──── 片选（拉低有效）
BUSY     ──── 忙信号（高电平表示命令未处理完）
DIO1     ──── 中断（TxDone / RxDone / CadDone）
RESET    ──── 复位（低电平复位）
ANT      ──── Sub-GHz 天线（弹簧天线 / SMA / PCB 走线）
```

**关键约束**：

- 天线 50Ω 阻抗匹配到 RF 输出引脚
- 走线避开 DC-DC、晶振、时钟线
- Sub-GHz 频段（470/868/915 MHz）走线比 2.4 GHz 长
- BUSY 引脚必须接 MCU 中断，不能漏
- DIO1 多源中断（必须看 status register 区分）

## 频段与通道速查

### CN470（中国主流）

```text
上行（终端 → 网关）：
  频率：470.3 ~ 489.3 MHz
  通道：96 个，间隔 200 kHz
  起始公式：f = 470.3 + n × 0.2 MHz, n = 0..95
  必须支持 SF7~SF12 + BW 125/250/500 kHz

下行（网关 → 终端）：
  频率：490.1 ~ 509.7 MHz
  通道：48 个，间隔 200 kHz
  起始公式：f = 490.1 + n × 0.2 MHz, n = 0..47
```

**实战要点**：CN470 是国内出货必选，固件必须支持 0~7 速率档位（DR0~DR7）。

### EU868（欧洲）

```text
强制信道：868.1 / 868.3 / 868.5 MHz（必选）
可选信道：867.1 / 867.3 / 867.5 / 867.7 / 867.9 MHz
Duty Cycle：1%（每小时只能发 36 秒）
```

**实战要点**：EU868 Duty Cycle 是法规硬约束，1% 超了 NS 直接拒，终端数据丢失。

### US915（美国）

```text
上行：902.3 ~ 914.9 MHz，64 个 125 kHz 信道
下行：923.3 ~ 927.5 MHz，8 个 500 kHz 信道
子带：8 个 125 kHz 子带
```

**实战要点**：US915 通道分 8 个子带，终端默认只占 1 个子带（8 信道），要 hopping 必须 NS 端配置。

## 关键参数

### SF / BW / 速率关系

| DR | SF | BW | 比特率 | 灵敏度 | 空中时间（11B） | 适用 |
| --- | --- | --- | --- | --- | --- | --- |
| DR0 | SF12 | 125 kHz | 250 bps | -137 dBm | ~1.5 s | 极限远距 |
| DR1 | SF11 | 125 kHz | 440 bps | -134.5 dBm | ~750 ms | 远距 |
| DR2 | SF10 | 125 kHz | 980 bps | -132 dBm | ~370 ms | 远距 |
| DR3 | SF9 | 125 kHz | 1760 bps | -129 dBm | ~185 ms | 平衡 |
| DR4 | SF8 | 125 kHz | 3125 bps | -126 dBm | ~100 ms | 平衡 |
| DR5 | SF7 | 125 kHz | 5470 bps | -123 dBm | ~56 ms | 高速 |
| DR6 | SF7 | 250 kHz | 11000 bps | -120 dBm | ~28 ms | 高速 |
| DR7 | SF7 | 500 kHz | 50000 bps | -116 dBm | ~14 ms | 高速短距 |

**实战档位**：

```text
极限档（DR0/DR1）：电池供电远距（农业 / 远距传感）
平衡档（DR3/DR4）：智能水表 / 智能停车
高速档（DR6/DR7）：固件 OTA / 高频上报
```

### CR（Coding Rate）

```text
CR 4/5  → 1.25 倍有效负载比例（无 FEC，理论）
CR 4/6  → 1.5 倍
CR 4/7  → 1.75 倍
CR 4/8  → 2 倍（最强 FEC，最远最慢）
```

**实战建议**：默认 CR 4/5，干扰强场景切到 CR 4/8。

### TX Power

| 频段 | 典型最大 | 法规限制 |
| --- | --- | --- |
| CN470 | +17 dBm | 50 mW EIRP（中国） |
| EU868 | +14 dBm | 25 mW EIRP（欧洲 ETSI） |
| US915 | +20~30 dBm | 取决于子带 FCC |
| AS923 | +14~20 dBm | 100 mW EIRP（部分国家） |

**实战要点**：EU868 法规限制 14 dBm，但 SX1262 实际可输出 22 dBm，必须软件限幅。

## 抓包工具

| 工具 | 平台 | 优势 | 限制 |
| --- | --- | --- | --- |
| LoRa Sniffer + Wireshark | SX1276/SX126x 改装 | 协议解析全，免费 | 仅一个信道，需多 sniffer |
| ChirpStack Frame Log | 服务端 | 看应用层 payload + 帧时间 | 需自建 NS |
| TTN Console Live Data | 公有云 | 网页直接看 | 公有云依赖 |
| HackRF / LimeSDR + gr-lora | SDR | 看 RF 物理层 | 协议解析复杂 |
| LoRaMac-node (Semtech) | 源码 | 协议栈参考 + sniffer 源码 | 移植工作量大 |
| OTII / Joulescope | 硬件 | 精确功耗 | 需外购 |

**产线推荐组合**：

```text
研发：LoRa Sniffer + Wireshark + ChirpStack 自建 + OTII 测功耗
产线：ChirpStack GW + 自动 Join 测试脚本 + 串口打印 RSSI/SNR
压测：多台 GW + 模拟 1000 节点 + 流量回放
```

## 调试步骤

1. **看固件版本**：烧录确认 Log/版本号，验证 LoRaMac-node 或厂商 SDK 版本
2. **看频段配置**：用 `lora-cli` 或串口命令查频段（CN470 / EU868）
3. **看 Join 流程**：Wireshark 抓 Join Request → Join Accept，确认 AppEUI/AppKey/DevEUI
4. **看 RSSI / SNR**：连接后打印 RSSI（应 > -110 dBm）、SNR（应 > -5 dB）
5. **看 ADR 状态**：NS 端查 NS LinkADRReq 历史，终端查当前 SF/BW
6. **看 Duty Cycle**：EU868 必须守 1%，每帧记录发射时间戳
7. **跑距离测试**：10m / 100m / 1km / 视距，逐档验证

## 常见问题速查

| 现象 | 优先检查 |
| --- | --- |
| 完全 Join 失败 | 频段错配 / AppKey 不匹配 / DevEUI 注册到 NS |
| Join 慢（> 30s） | SF12 起步 / 信号弱 / 频段未对齐 |
| MIC Failure | AppKey 错配 / NS 端密钥 / payload 损坏 |
| 频繁断连 | Class A 下行窗口错过 / 网关信道变更 |
| 距离近（< 500m） | 天线匹配差 / 走线错 / 频段错 |
| 功耗偏高 | SF 太高 / Duty Cycle 触发限流 / 模块一直 wake |
| NS 收不到数据 | DevEUI 未注册 / 频段错 / 网关没上线 |
| OTA 失败 | 空中时间超限（DR0 一次只能传几 KB） |
| Frame Counter 溢出 | 16-bit 跑 5~10 年会到 65535 |

## 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| Join Fail | DevNonce 重复 / AppKey 错 | 终端打印 DevNonce，NS 端清 device registry |
| MIC Failure | 密钥不匹配 | 比对 AppKey（烧录 vs NS 配置） |
| 频段错配 | 终端与 NS 频段不一致 | 烧对应频段固件 |
| 距离近 | 天线 / 走线 | VNA 量 868/915 MHz 阻抗 |
| EU868 数据丢失 | Duty Cycle 超 | 降占空比到 1% 以下 |
| 功耗大 | SF / BW 没优化 | 启用 ADR，目标 DR3~DR5 |
| Class B 不下行 | GPS 失锁 / beacon 错过 | 检查 GW GPS + 终端 drift |
| NS 收不到 | DevEUI 未注册 | 在 NS 创建设备 profile |
| OTA 失败 | 空中时间太长 | 切 DR5/DR6 + 分片传输 |
| GW 容量打满 | 8 信道被占 | 加 GW 扩容 + 启用 ADR |

## 错误码速查

### LoRaWAN MAC 命令错误（TS001 §6.2）

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x00 | UNSPECIFIED_ERROR | 通用错 |
| 0x01 | MIB_NOT_SUPPORTED | MIB 标识不支持 |
| 0x02 | MIB_UNAUTHORIZED | 无权限 |
| 0x03 | MIB_INVALID_VALUE | 值错 |
| 0x04 | MIB_READ_ONLY | 只读 MIB 写 |
| 0x05 | MIB_WRITE_ONLY | 只写 MIB 读 |
| 0x06 | UNSUPPORTED_BANDWIDTH | BW 不支持 |
| 0x07 | UNSUPPORTED_SPREADING_FACTOR | SF 不支持 |
| 0x08 | UNSUPPORTED_FSK_MODULATION | FSK 不支持 |
| 0x09 | UNSUPPORTED_OUTPUT_POWER | TX Power 不支持 |
| 0x0A | UNSUPPORTED_CHANNEL_MASK | 信道掩码错 |
| 0x0B | UNSUPPORTED_DATARATE | DR 不支持 |
| 0x0C | INVALID_DATARATE | DR 索引错 |
| 0x0D | INVALID_FREQUENCY | 频率不在频段内 |
| 0x0E | INVALID_CHANNEL_MASK | 信道掩码错 |
| 0x0F | INVALID_CHANNEL_INDEX | 信道索引超出 |
| 0x10 | INVALID_CHANNEL_FREQUENCY | 频率错 |

### Semtech SX126x 错误（API 状态返回）

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x00 | OK | 正常 |
| 0x01 | UNSUPPORTED_FEATURE | 命令不支持 |
| 0x02 | CRC_ERR | 包 CRC 错 |
| 0x03 | INVALID_SIZE | 包大小错 |
| 0x04 | RADIO_BUSY | 芯片忙 |
| 0x05 | TIMEOUT | 通信超时 |
| 0x06 | CMD_ERROR | 命令格式错 |
| 0x07 | CMD_FAIL | 命令执行失败 |
| 0x08 | TX_RX_FAIL | 收发失败 |

### ChirpStack 常见错误（NS 端）

| 错误 | 触发 |
| --- | --- |
| `DevNonce already used` | DevNonce 重复（终端复位后用同一 Nonce） |
| `MIC mismatch` | 密钥错 / payload 损坏 |
| `frame-counter does not match` | Frame Counter 不连续（丢帧 / 重启） |
| `device-session does not exist` | 设备未 Join / 已被 NS 删 |
| `activation missing` | 终端没 Join 就发数据 |
| `duty-cycle exceeded` | EU868 1% 超 |
| `frequency not allowed` | 频率不在 NS 信道计划 |
| `device address already used` | DevAddr 冲突（ABP 烧录重复） |

### TTN (v3) 错误

| 错误 | 触发 |
| --- | --- |
| `rate_limit_exceeded` | 上行速率超限 |
| `device_not_found` | DevEUI 未注册 |
| `invalid_payload` | payload 解码失败 |
| `mic_check_failed` | MIC 校验失败 |
| `f_cnt_reset` | Frame Counter 重启 |

## SX1262 实战注意

- **BUSY 引脚必须接 MCU 中断或轮询**，否则错过 TxDone/RxDone
- **TCXO 选型**：SX1262 强烈推荐 TCXO（温度补偿晶振），普通晶振温漂导致频偏
- **SX1262 复位后必须 SetStandby + SetPacketType + SetRfFrequency** 全套初始化
- **SX1262 切换频段必须用 SetPaConfig**，不同频段 PA 配置不同（高压 vs 低压）
- **SPI 时钟**：SX1262 最高 16 MHz，超过会通信失败
- **BUSY 引脚在低功耗时被拉低**，唤醒后会拉高，MCU 必须等 BUSY 拉高再发 SPI
- **DIO1 多源中断**：必须读 IRQ 寄存器判断是 TxDone / RxDone / CadDone

## 14 步 LoRa 调试方法论（symptom → evidence gap → correction → 复检）

IoTClass 总结的 14 类坑 + "四件套 review rule"：

```text
14 类症状（symptoms，按 4 大类组织）：
  missing uplinks（5 类）：
    1. Join Failed（AppKey / DevNonce / 频段）
    2. Uplink 后无 ACK（窗口错 / 频偏）
    3. 节点能 join 但数据收不到（FCnt / payload 格式）
    4. 多节点轮流丢包（GW 容量满）
    5. 升级后掉线（NV 残留 / 固件不兼容）
  
  rejected frames（3 类）：
    6. MIC Mismatch（AppKey 误填 APPSKEY）— 90% 是这个
    7. Frame Counter 异常（ABP 重启归零）
    8. DevNonce 重复（OTAA 失败）
  
  missed downlinks（3 类）：
    9. RX1/RX2 窗口错位（CN470 同异频）
    10. Class A 18s 延迟
    11. Class B beacon 漂移
  
  release surprises（3 类）：
    12. 频段不匹配（US915 8/16 vs 72 信道）
    13. payload 0x00（MAC 命令拆分）
    14. 32MHz ppm 漂移致 LDRO 失效

四件套 review rule：
  symptom → evidence gap → correction → 复检条件
  1. 描述症状（log / 抓包 / 现场）
  2. 找证据缺口（缺什么数据？抓什么包？）
  3. 修一项（最小化修改）
  4. 复检条件（如何确认修好？）

基线数据：
  60 设备 × 4 上行/h = 240/h
  弱 SF 触顶占空比（EU868 1% duty cycle）
  ADR 启用无后继 = 失效
```

**实战例 1：MIC Mismatch 90% 是 AppKey 误填 APPSKEY**

```text
症状：所有节点 Join Accept 后第一个 uplink 被拒
抓包：Wireshark 解析 MIC 错误
证据缺口：DevEUI / AppEUI / AppKey / NwkSKey / AppSKey 哪个错？
复检：节点 + NS 两边密钥对比
修复（90% 是这个）：
  - 烧录时 AppKey 字段误填了 AppSKey
  - 改：Node 烧入 AppKey = "0x1234..."（不是 AppSKey 字段）
  - NS 配置 NwkSKey / AppSKey = 派生
```

**实战例 2：US915 默认 8/16 信道 ≠ TTN 全 72 频**

```text
症状：US915 节点在 TTN 后台看不到
抓包：节点只发在 8 个默认信道
证据缺口：US915 子带 plan 不匹配
复检：节点 + NS 信道 plan 对比
修复：
  - 节点烧入 US915 完整 72 信道
  - NS 配置 US915 完整 plan
  - 不能用默认 8 信道（会丢 64 个信道）
```

### Dragino Wiki 14 步 checklist（产线排错 SOP）

```text
14 步产线排错 checklist（Dragino Wiki 标准）：
  1. 频段 / sub-band 匹配（US915/AU915/CN470 各自 8 子带）
  2. AppKey / AppEUI / DevEUI 配置正确
  3. DevNonce 范围（0x0001-0xFFFF 严格去重）
  4. Frame Counter 持久化（NV 存储）
  5. payload 格式（不是 0x00 = MAC 命令）
  6. MIC 校验（AppKey 误填 APPSKEY = 90% 错）
  7. 32MHz 晶振 ppm 漂移（频偏 > 30ppm 致 LDRO 失效）
  8. SPI 通信（CS / CLK / MOSI / MISO / BUSY）
  9. 频偏 0.1MHz（频谱仪验证）
  10. 频段不匹配（470 vs 433 vs 868 vs 915）
  11. ABP / OTAA 模式选择（节点 + NS 一致）
  12. Join Accept 加密（AppKey 正确）
  13. Class A / B / C 模式（NS 配置）
  14. 上行 / 下行窗口（CN470 同异频）
```

## 检查清单

```text
□ 电源：稳压到 1.8~3.7V，纹波 < 50mV
□ 去耦：每个 VDD 引脚 100nF + 10µF 紧靠
□ 晶振：TCXO 优先（温漂 ±10 ppm 以内）
□ 天线：50Ω 匹配，VNA 验证 S11 < -10 dB @ 目标频段
□ 固件：协议栈版本（LoRaMac-node 4.7+）与频段匹配
□ 频段：CN470 / EU868 / US915 选对，烧对应固件
□ DevEUI / AppKey：终端烧录值与 NS 完全一致
□ Join 流程：OTAA 必走 Join，ABP 仅生产测试
□ SF / BW：默认 SF7~SF9 + BW 125 kHz + CR 4/5
□ TX Power：EU868 限 14 dBm，CN470 限 17 dBm
□ Duty Cycle：EU868 守 1%（36s/h）
□ ADR：默认开启，监控收敛到 DR3~DR5
□ Frame Counter：上下行严格 +1
□ MIC 校验：每次接收都要验证
□ 错误码：LoRaWAN MAC + Semtech API + NS 端三套都要能解析
```

## 关联文档

- `bus/lora.md` 主题入口
- `bus/lora-deep-dive.md` 协议栈深挖
- `bus/lora-failure-cases.md` 产线实战案例
- `bus/lora-index.md` 主题地图 + 导航
