# LoRa / LoRaWAN 候选素材 @ 2026-09-17 00:00

## 协议速览
- 是什么：Sub-GHz 远距离 CSS 扩频物理层 + LoRaWAN MAC/网络层
- 解决什么：电池供电设备公里级组网（远距抄表、定位追踪、智能门锁）
- 关联：IoT/可穿戴方向实战富矿，板级故障案例可直接补 L4 调试章节

## 候选文章（5 条）

### 1. ESP32 LoRaWAN Troubleshooting: Fix Join & TX Errors
- 链接：https://electricalflux.com/mcu-general/esp32-lorawan-troubleshooting-join-errors
- 来源：electricalflux.com（嵌入式开发者 blog）
- 摘要：ESP32+SX1262/SX1276 三大实战故障——sub-band mask 缺失致 join 失败、TX 电流尖峰触发 brownout、空载烧毁天线致 RSSI -120dBm
- 关键实战点：RadioLib vs MCCI LMIC 选型；US915/AU915 必配 sub-band mask；TX 前必焊 470µF 缓冲电容（SF10-SF12 瞬时 > 120mA）
- 推荐动作：扩 deep-dive（推荐）

### 2. ESP32 LoRaWAN Node Build: Heltec V3 TTN Debugging
- 链接：https://electricalflux.com/mcu-coding/heltec-v3-esp32-lorawan-ttn-setup-debug
- 来源：electricalflux.com
- 摘要：按错误码 -707/-706 排序排查树，定位 90% 初始化失败根因；TTN "MIC Mismatch" 字节序问题；单 channel gateway 切换 ABP 跳过 join
- 关键实战点：V2/V3 板卡混淆致 -707（SX1278 vs SX1262 SPI 映射完全不同）；board variant 必须对应 lmic_pinmap；MSB/LSB 字节序高频坑
- 推荐动作：扩 deep-dive（推荐）

### 3. STM32WLE5 LoRaWAN 初始化卡死排查
- 链接：http://www.mhpq.cn/news/369142
- 来源：mhpq.cn（中文实战 blog）
- 摘要：STM32WLE5 自研板智能门锁方案，modem_supervisor_init() 卡死的 5 步排查全过程
- 关键实战点：90% 是 HSE32 未起振；TCXO 供电由 DIO3 控制（软件未配就永远断电）；焊完先查 RCC-CR.HSE32RDY
- 推荐动作：扩 deep-dive（推荐）

### 4. Mastering LoRa: SPI Wiring + Bus Sniffing
- 链接：https://electricalflux.com/learn-guides/lora-communication-protocol-spi-rf-primer
- 来源：electricalflux.com
- 摘要：物理层经典故障（NSS pull-up 缺失、SPI 16MHz 限制、DevEUI 冲突）+ SPI/RF 双总线嗅探
- 关键实战点：SPI Mode 0 / SX1262 max 16MHz，长杜邦线 ≤ 10MHz；SDR 看 CSS 斜线 chirp 验 TX；DevEUI 复用致 NS nonce mismatch
- 推荐动作：扩 deep-dive（推荐）

### 5. LoRaWAN Firmware Tips (SDR + Gateway + ChirpStack)
- 链接：https://www.lab5e.com/docs/lora/developing_firmware
- 来源：lab5e.com（LoRaWAN 网络服务商）
- 摘要：完整调试三层法——RTL-SDR 看空口、$100 自建 gateway 看连接、ChirpStack 栈诊断
- 关键实战点：RTL2832 USB dongle 看空口；IC880A+Pi 自建 concentrator（约 €150）；ChirpStack 是栈诊断开源首选
- 推荐动作：写实战案例（推荐）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃