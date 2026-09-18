# BLE 候选素材 @ 2026-09-01 00:00

- 是什么：低功耗蓝牙，2.4 GHz 跳频 + GATT
- 解决什么：IoT/可穿戴/工业低功耗连网
- L4 关联：用户主做 IoT/可穿戴（IOT 🥇），BLE 是产线故障率前 3 的协议

## 1. 从信号完整性视角重构蓝牙连接逻辑：跳频与时序的物理真相
- 链接：https://tsight.io/articles/15176126?lang=zh | 来源：tsight.io
- 摘要：Ellisys 抓工业现场真实断连——PHY 毫秒级数十次 Channel Map 重协商；工业 Wi-Fi/变频器噪声逼出 LL_CONNECTION_UPDATE_IND 超时与 MIC Failure
- 实战：①主动屏蔽工业拥堵频段 ②天线远离金属屏蔽罩 ③RF Ground 与 Digital Ground 单点接
- 推荐：**扩 deep-dive**（PHY 跳频 + 工业频谱避让）

## 2. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/ | 来源：Dewi Labs
- 摘要：工业/机器人/医疗生产环境 latency spike / 断连 / throughput 崩溃——团队先甩锅硬件，调天线/TX power/换模块都治标；根本是消费级固件 best-effort 调度对实时系统不友好
- 实战：①lab→field 主因 env complexity ②怀疑硬件前先看 latency profile ③firmware scheduling 才是根因
- 推荐：**写实战案例**（"lab→field 失效"框架）

## 3. BLE Data Integrity Failures (Out-of-Order Segments) — Nordic DevZone
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/125365/ble-data-integrity-failures-out-of-order-segments | 来源：Nordic 官方社区
- 摘要：nRF 网关 BLE→Wi-Fi bridge 800KB 大文件（应用层 SAR），双 radio 高负载触发 SFP CRC fail → SAR 出现 A1/A2/**A2**/A4 重排序；Wi-Fi tcp_window_full 与 BLE CRC 失败时间窗精确对齐
- 实战：①双 radio 共存 throughput 互相挤兑 ②SAR 必须自带 seq num 容忍乱序 ③多路 log 时间戳对齐是唯一诊断法
- 推荐：**写实战案例**（"双 radio + SAR"工程案例）

## 4. BLE 常见断连原因分析方法分享 | 低功耗蓝牙
- 链接：https://developers.goodix.com/zh/bbs/detail/c649c96ac97a4959a855b326b9b11f8b | 来源：Goodix 官方社区（GR551x/5525/5526/5331）
- 摘要：基带信号 GPIO 引出 + 钩子函数（evt_start / ble_isr）还原断连现场；按错误码分类——0x98 超时 / 0xB8 即时指令错过 / 0xB2 响应超时 / 0xCE 建连失败 / 0xA3 远端主动 / 0xA6 本端主动 / 0xCD 加密相关
- 实战：①调试器一连看 watchdog 失效是隐藏陷阱 ②ISR/evt_start 规律均匀 = 调度健康 ③0xCD 常见 = 配对加密过程插入非配对 LLCP
- 推荐：**扩 deep-dive**（错误码 + 钩子调试，入 L4 故障速查表）

## 5. Tegra SE ELP incorrect ECDH — BLE OOB pairing 0x05 silent fail
- 链接：https://forums.developer.nvidia.com/t/tegra-security-engine-elp-produces-incorrect-ecdh-results-ble-oob-pairing-fails-with-auth-error-0x05/364940/12 | 来源：NVIDIA 官方论坛（Jetson Xavier NX, L4T R35.6.0）
- 摘要：tegra-se-ecdh 硬件驱动算 BLE SMP OOB ECDH 返回错误值，confirm 不匹配 → 0x05 静默失败（无 panic 无 log）；同 OOB 数据在 Android / 非 Tegra Linux 正常
- 实战：①workaround = unbind 3ad0000.se_elp 强制回退 ecdh-generic ②静默失败是排查噩梦，同根因在 Orin 表现为 kernel panic ③硬件 crypto 加速器 ≠ 正确实现
- 推荐：**入主题笔记**（"硬件 crypto silent corruption"反面教材，可与 SimCardReader DRK/RDP 交叉）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
