# BLE 候选素材 @ 2026-10-06 12:00

BLE 2.4 GHz 跳频，GAP/GATT/ATT/L2CAP；手机↔外设 10 m 低带宽；L4 = 「实验室 OK 产线挂」根因常在物理层/RF/电源/状态机。

## 候选（5 条按优先级）

### 1. tsight.io「从信号完整性视角重构蓝牙连接逻辑」（中文·深度）
- https://tsight.io/articles/15176126 ｜ tsight.io（无线测试仪器商）
- Ellisys/Frontline 工业抓包：毫米级 Channel Map 重协商是断连根因；固件未及时更新 Channel Map + T_IFS 偏移 = ACK 空转释放链路。重传次数是表象，channel map 是底层。
- 推荐：扩 deep-dive（与 LBT/CSMA 工业实测合框架）

### 2. Hubble「Why Your BLE Connection Drops Every 30 Seconds」
- https://hubble.com/community/guides/why-your-ble-connection-drops-every-30-seconds-supervision-timeout-explained ｜ hubble.com
- 「整 30s」掉线决策树：ATT 30s 固定超时 vs supervision timeout；HCI 码 0x08/0x13/0x16/0x22/0x3E 完整映射；iOS `interval ≥15ms`/`latency ≤30`/`timeout ≤6s`。
- 排错序：reason code → `(1+latency)×interval×2 < timeout` → RSSI → RTT 找 reset → Sniffer 翻 PDU 沉默侧
- 推荐：入主笔记「BLE 30s 掉线 v1」

### 3. Hubble「The 10 Most Common BLE Bugs and How to Find Them」
- http://hubble.com/community/guides/the-10-most-common-ble-bugs-and-how-to-find-them ｜ hubble.com
- 10 类 BLE bug：CCCD/睡眠 mA 漏电/广播 PHY/字节序/5-10 kbps 吞吐/iOS 参数…每条给 Nordic PPK II / nRF Sniffer 实操。
- 关键：sleep 5mA 高先关 BLE 测基线（常是替罪羊）；throughput = `(payload × ppe) / interval`
- 推荐：扩 deep-dive + 入 nrf52-known-bugs.md

### 4. Brinztech「Zephyr BLE L2CAP OOB CVE-2026-5068」（2026-06-09）
- https://www.brinztech.com/breach-alerts/brinztech-hardware-ecosystem-advisory-bluetooth-host-stack-memory-corruption-and-denial-of-service-zephyr-project-rtos-cve-2026-5068-euvd-2026-35353/ ｜ brinztech.com
- Zephyr L2CAP LE CoC SDU 重组 2B OOB 写（CWE-787）；`user_data_size` < 头部 → 100m 内畸形碎片包 → MCU assertion/DoS；不需配对鉴权，FDA 监控可穿戴医疗。
- 推荐：入「BLE 安全漏洞 2026」（合 Frontier X CVE-2026-5768 / ESP32 CVE-2025-27840 / SweynTooth 12 CVE）

### 5. Electricalflux「BLE Arduino Nano 33 BLE Troubleshooting 2026」
- https://electricalflux.com/mcu-general/fix-ble-arduino-nano33-connection-dropouts ｜ electricalflux.com
- Nano 33 BLE（nRF52840）量产失败模式矩阵；TX 突发 18mA @ +4dBm 跌破 2.7V brownout → 中央看是 drop；面包板天线寄生电容把 10m 干到 30cm。
- 实战：100µF 钽+0.1µF 瓷跨 VCC/GND < $0.60 解 95% reset；chip antenna keep-out ≥ 5mm
- 推荐：扩 deep-dive（电源 + RF keep-out 两条独立）

## 下一步
P1 = 2（决策树）+ 3（10 bug 骨架）→「BLE 30s 掉线 v1」主笔记
P2 = 1（信号完整性）→ LBT/CSMA 合框架
P3 = 4（CVE-2026-5068）→ 安全合集
P4 = 5（Nano 33 2026）→ 硬件实战
下个协议 = **ZigBee**（24h 内未跑）