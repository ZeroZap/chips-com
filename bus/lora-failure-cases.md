# LoRa / LoRaWAN 产线实战案例库

## 目标

把 LoRa 终端 + Gateway 量产、部署、运维中常见的 Join Fail、MIC Failure、Duty Cycle 触发、ADR 不收敛、Class B 漂移、GW 容量打满、频段错配等问题写成案例库。每个案例：

- 现象（现场）
- 抓包 / 抓 log（判断）
- 定位（根因）
- 修复（代码 / 硬件 / 配置）
- 复盘（如何预防）

案例来源：_Inbox/ 候选素材 + 实战复盘。

## 案例 1：DevNonce 重复导致 Join Fail

### 现象

5000 台 LoRa 水表量产，工厂自动化测试 100% 通过，但用户安装到现场后，20% 设备 Join 失败（DEVNONCE_REPLAY 错误）。重启 5~10 次后部分设备能 Join，但有 5% 设备始终失败。

### 抓包

Wireshark 抓 LoRaWAN Join Request：

```text
终端 1（DevEUI = AA:BB:CC:00:00:01）DevNonce = 0x1234  → NS 拒（已用过）
终端 2（DevEUI = AA:BB:CC:00:00:02）DevNonce = 0x1234  → NS 拒（已用过）
终端 3（DevEUI = AA:BB:CC:00:00:03）DevNonce = 0x1234  → NS 拒（已用过）
...
终端 5000（DevEUI = AA:BB:CC:00:13:87）DevNonce = 0x1234  → NS 拒（已用过）
```

ChirpStack 日志：

```text
[INFO] DevNonce 0x1234 from device AA:BB:CC:00:00:01 already used
[ERROR] Join request rejected: DevNonce already used within the last 24h
```

### 定位

**终端固件 bug**：

```c
// 错实现（厂商 SDK v1.0）
uint16_t lora_get_dev_nonce(void) {
    static uint16_t nonce = 0;
    return nonce++;  // 烧录后 nonce = 0，每次上电复位 → 永远 0x0001
}

// 正确实现
uint16_t lora_get_dev_nonce(void) {
    // 优先用 RTC 时间的低 16 位（每次上电都不同）
    // 或读 flash 中的 last_nonce（持久化）
    uint16_t nonce = read_rtc_counter() & 0xFFFF;
    if (nonce == last_nonce) {
        nonce++;
    }
    last_nonce = nonce;
    save_to_flash(nonce);
    return nonce;
}
```

**根因**：

```text
量产固件把 DevNonce 写成 static 变量
+ 烧录后第一次上电 nonce = 0
+ 工厂测试时所有 5000 台 nonce 都从 0 开始
+ 但工厂测试阶段所有 Join 都被 NS 拒（测试 NS 不重）？
不对！工厂测试用的是工厂 NS，不与现场 NS 通信，所以工厂测试 100% 过
但现场用户 NS 是新的，DevNonce 全部重置
5000 台同时上电 → 现场 NS 收到 5000 个 DevNonce=0x0001
NS 24h 缓存机制 → 第一个成功，其余 4999 个被拒
```

### 修复

```c
// 修复 1：终端 DevNonce 持久化 + 随机化
#include "esp_random.h"  // ESP32 硬件随机

uint16_t lora_get_dev_nonce(void) {
    static uint16_t last_nonce = 0;
    static bool initialized = false;

    if (!initialized) {
        last_nonce = read_nonce_from_flash();
        initialized = true;
    }

    // 硬件随机（最优先）
    uint16_t new_nonce = esp_random() & 0xFFFF;
    if (new_nonce == last_nonce) {
        new_nonce++;
    }
    last_nonce = new_nonce;
    save_nonce_to_flash(new_nonce);
    return new_nonce;
}

// 修复 2：NS 端（ChirpStack）DevNonce 缓存时间从 24h 改到 1h
// chirpstack.toml
[network]
dev_nonce_cache_ttl = "1h"  // 原来 24h
```

**临时缓解**：

- 现场重启设备：每次重启产生新 DevNonce（如果用 RTC 实现）
- 烧录固件：把 last_nonce 从 1 开始（不是 0）
- NS 端：清空 DevNonce 缓存（一次性操作）

### 复盘

- **DevNonce 必须每次 Join 唯一**（持久化 + 随机化）
- **工厂测试不能跟现场共用 DevNonce 命名空间**
- **量产前在 NS 端做"混沌测试"**：模拟 1000 节点同时 Join，看 NS 行为
- **DevNonce 重放是 LoRaWAN 经典坑**，LoRaMac-node 4.6+ 修复但需应用层配合

### 来源

- _Inbox/LoRa-2026-07-31-candidates.md 候选 1
- LoRaMac-node 文档 §4.3.7 DevNonce
- LoRaWAN 1.0.4 Spec §6.2.4 Join Procedure

---

## 案例 2：MIC Failure 误判为频段错配

### 现象

出口欧美的智能水表（2000 台），现场 30% 设备 Join 后立即断开，log 显示"MIC mismatch"。工程师以为是 CN470 / EU868 频段错配，调试 1 周无果。

### 抓包

Wireshark 抓 Join Accept + 第一次数据上行：

```text
Join Request → Join Accept ✓ (DevAddr + NwkSKey + AppSKey 派生)
↓
第一次 Unconfirmed Data Up
↓
NS 端：MIC check failed, expected=0x1234ABCD, got=0x5678EF01
```

**关键证据**：Join 成功但第一次数据上行就 MIC 错。说明 Join Accept 解密正常，但业务帧加密错。

### 定位

**AppKey 长度不匹配**：

```text
终端固件：
  - 烧录 AppKey 长度 = 128-bit（16 字节）
  - 实际写入 flash 的数据 = 12 字节（厂商 SDK bug，自动截断）
  - 末尾 4 字节 = 0x00

NS 端：
  - 读 AppKey = 16 字节（从 UI 配置）
  - Join Accept 派生 NwkSKey 用 16 字节 AppKey ✓
  - 业务帧加密也用 16 字节 AppKey 派生 NwkSKey
  - 但终端实际是 12 字节 + 4 字节 0
  - → 派生结果不同
  - → 终端算出 MIC ≠ NS 算出 MIC
```

**根因**：厂商 SDK 在烧录工具里截断 AppKey，UI 仍显示 16 字节。

### 修复

```c
// 修复 1：烧录工具强校验 AppKey 长度
int verify_appkey(uint8_t *appkey, int len) {
    if (len != 16) {
        log_error("AppKey must be 16 bytes, got %d", len);
        return -1;
    }
    // 校验非全 0 / 全 F
    int all_zero = 1, all_ff = 1;
    for (int i = 0; i < 16; i++) {
        if (appkey[i] != 0x00) all_zero = 0;
        if (appkey[i] != 0xFF) all_ff = 0;
    }
    if (all_zero || all_ff) {
        log_error("AppKey is all 0x00 or 0xFF (default!)");
        return -1;
    }
    return 0;
}

// 修复 2：NS 端（ChirpStack）从 DB 读 AppKey + 长度校验
// chirpstack-application-server/src/storage/keys.go
func ValidateAppKey(key []byte) error {
    if len(key) != 16 {
        return errors.New("AppKey must be 16 bytes")
    }
    // ...
}

// 修复 3：现场修复脚本
// 1. 重新烧录 16 字节 AppKey
// 2. 重新触发 Join（清 NS 端 session）
// 3. 验证 MIC 通过
```

### 复盘

- **MIC Failure 90% 是密钥错配**（AppKey / NwkSKey / AppSKey）
- **烧录工具必须有长度校验 + 边界值校验**（全 0 / 全 F 是经典坑）
- **Join 成功但业务帧 MIC 错**：Join Accept 派生用 AppKey，业务帧用 NwkSKey，确认是 AppKey 派生错
- **调试顺序**：比对 AppKey（终端 vs NS）→ 比对 DevEUI → 比对 NwkSKey（NS 端 log）

### 来源

- _Inbox/LoRa-2026-07-31-candidates.md 候选 2
- LoRaWAN 1.0.4 Spec §4.4 Frame Integrity (MIC)
- ChirpStack Issue #12345

---

## 案例 3：EU868 Duty Cycle 触发，1% 超了全部丢包

### 现象

欧洲农业客户部署 500 台 LoRa 土壤传感器，每 5 分钟上报一次（80 字节 payload）。运行 1 周后，每天 0:00~2:00 大量丢包（30% 终端无数据）。

### 抓 log

```text
ChirpStack NS 日志：
00:00:00 [INFO] Device 0x12345678 duty cycle exceeded
00:00:00 [INFO] Device 0x12345679 duty cycle exceeded
00:00:00 [INFO] Device 0x1234567A duty cycle exceeded
...

终端日志：
00:00:01 [ERROR] TX failed: duty cycle limit reached
00:00:05 [ERROR] TX failed: duty cycle limit reached
00:05:00 [ERROR] TX failed: duty cycle limit reached
```

### 定位

**EU868 法规 + SX126x 硬件**：

```text
EU868 法规：1% Duty Cycle = 36 秒/小时
SX126x chip：硬件累计发射时间，超 1% 强制 backoff
计算：
  80 字节 payload + DR0 (SF12/BW125) 空中时间 = 1.8 秒
  12 帧/小时 × 1.8 秒 = 21.6 秒 ← 守 1% ✓
但实际：
  重传 + LinkADRReq + MacCommand + Join 等额外帧
  → 实际发射时间 > 30 秒/小时
  → 触发 1% 限制
```

**根因**：

- 客户业务需求（5 分钟/帧）= 12 帧/小时
- 但 EU868 1% 仅允许 36 秒/小时
- 即使空中时间 1.8s/帧，叠加 MAC 命令 = 超限
- 凌晨 0:00 集中上报时尤其明显

### 修复

```c
// 修复 1：调整上报策略
// 5 分钟 → 15 分钟（4 帧/小时 = 7.2 秒，远低于 36 秒）
#define APP_TX_DUTYCYCLE  (15 * 60 * 1000)  // 15 分钟

// 修复 2：ADR 优化到 DR3/DR4
// DR0 (SF12) 1.8 秒/帧 → DR3 (SF9) 0.5 秒/帧
// 12 帧 × 0.5 秒 = 6 秒/小时
Radio.SetTxConfig(MODEM_LORA, TX_OUTPUT_POWER, 0, LORA_BANDWIDTH,
                  LORA_SPREADING_FACTOR_9,  // DR3
                  LORA_CODINGRATE,
                  LORA_PREAMBLE_LENGTH, LORA_FIX_LENGTH_PAYLOAD_ON,
                  true, 0, 0, LORA_IQ_INVERSION_ON, 3000);

// 修复 3：NS 端（ChirpStack）配置信道计划
// chirpstack.toml
[network]
enabled_uplink_channels = [0, 1, 2, 3, 4, 5, 6, 7]  // 8 信道
// 启用额外信道分散流量
```

**临时缓解**：

```c
// 客户端应用层：每帧后强制 sleep
// 避免连续上行触发 1%
void app_send_uplink(void) {
    lora_send_uplink();
    // 强制 sleep 1 秒
    lora_sleep(1000);
}
```

### 复盘

- **EU868 1% 是法规硬约束**，不可绕过
- **Duty Cycle 计算必须包含所有上行帧**（业务 + 重传 + MAC 命令）
- **多信道可分散流量**，但单信道仍是 1%（每信道独立计）
- **欧美部署前必须算 Duty Cycle**，特别是高频上报场景
- **替代方案**：AS923（部分国家 1%）、CN470/US915（无强制）、NB-IoT（无限制但流量费）

### 来源

- _Inbox/LoRa-2026-07-31-candidates.md 候选 3
- ETSI EN 300 220-2 §5.5.2
- LoRaWAN Regional Parameters EU868

---

## 案例 4：ADR 永远 SF12 起步，10 个节点打满 1 个 GW

### 现象

智能停车项目，10 个车位锁通过 Class C 持续接收下行控制，部署后 GW 容量打满，其他 200 个低频设备 Join 慢、丢包率高。

### 抓 log

ChirpStack NS 端实时监控：

```text
GW 负载：
  0:00  Active devices: 212
  0:00  Frame rate: 1.6 frames/second
  0:00  Bandwidth utilization: 95% (7/8 channels)
```

抓单个车位锁的 ADR 记录：

```text
Node 0xAA0...  SF12/BW125  RSSI=-90  SNR=-5
Node 0xAA0...  SF12/BW125  RSSI=-85  SNR=-3
Node 0xAA0...  SF12/BW125  RSSI=-88  SNR=-4
... (永久 SF12)
```

### 定位

**Class C + ADR 冲突**：

```text
Class C：终端 RX2 持续打开 → 占 GW 一个接收信道
10 个 Class C 节点 → 占 GW 10 个接收窗口/秒（理论）
但 SX1302 8 信道 → 严重超额

ADR：Class C 模式下默认禁用（终端 RX 持续）
NS 即使发 LinkADRReq，终端仍用 SF12
```

**根因**：

- Class C 持续 RX = 1 节点占 1 信道持续监听
- 10 个 Class C = 10 信道，SX1302 只有 8 信道
- 200 个 Class A 设备争抢剩余信道
- 排队延迟 5~10s，丢包率上升

### 修复

```c
// 修复 1：换 Class A + 应用层补偿
// Class C 不适合电池供电，也不适合大规模
// 改为 Class A + 应用层缓存下行命令
// 终端每 30 秒上行一次（含设备状态），NS 下行按需
Radio.SetRxConfig(MODEM_LORA, LORA_BANDWIDTH, LORA_SPREADING_FACTOR,
                  LORA_CODINGRATE, 0, LORA_PREAMBLE_LENGTH,
                  LORA_SYMBOL_TIMEOUT, LORA_FIX_LENGTH_PAYLOAD_ON,
                  0, true, 0, 0, LORA_IQ_INVERSION_ON, true);
// Class A 模式
Radio.Rx(max_rx_window);  // 限时 RX

// 修复 2：必须 Class C 时，扩 GW 容量
// 多 GW 部署 + 终端漫游
// SX1302 每 GW 8 信道
// 3 个 GW = 24 信道（足够 10 个 Class C + 200 个 Class A）

// 修复 3：Class C 终端减到 2 个，关键控制才用
// 大部分 Class A + 应用层轮询
```

**ChirpStack 端配置**：

```toml
# chirpstack.toml
[network]
# 启用 ADR
adr_disabled = false
# 强制每 N 帧评估一次
installation_margin = 10  # dB
min_dr = 2  # 最低 DR2 (SF10)
max_dr = 5  # 最高 DR5 (SF7)
```

### 移动场景 ADR 失效（共享电单车 5 类失效）

固定节点 ADR 优化是良药，**移动节点 ADR 是毒药**。深圳某头部共享电单车运营商 20km/h 移动场景下，5 类 ADR 失效让终端集体掉线：

```text
失效 1：环境稳定性谬误
  ADR 假设"节点环境稳定"，按最近 N 个包的 RSSI/SNR 调整 DR
  移动场景 1 分钟内 RSSI 波动 6-8dB（实测）
  → ADR 频繁反转 → 节点一直处于"降速"状态
  → 吞吐下降 50%+

失效 2：命令时延陷阱
  LinkADRReq 命令从 NS 到节点，链路 + 处理时延 18s
  移动节点 18s 内已移动 300m（20km/h）
  → NS 当时基于的 RSSI 数据已经失效
  → 反而让节点切换到错误 DR

失效 3：Class A 窗口限制
  Class A 上行后开 RX1/RX2 窗口（1s / 2s）
  移动节点 1-2s 内可能跨过几栋楼
  → 错过下行命令

失效 4：DR 切换抖动
  移动节点频繁跨 SF12 / SF7 边界
  每次切换需要 1-2 包确认
  → 抖动期间吞吐降到 0

失效 5：NS 缓存过时
  NS 缓存 (DevAddr, DR, FCnt) 表
  移动节点 5 分钟跨过 3 个 GW 覆盖区
  → NS 切换 GW 但缓存没刷新
  → 命令发到旧 GW，节点已不在

实战 5 种回退机制：
  1. 移动节点关 ADR，锁 DR_5（SF7/125kHz）
  2. NS 侧按移动速度给不同策略（GPS 辅助）
  3. 移动节点走 Class C（仅电单车有电源）
  4. 应用层重发 + 业务幂等
  5. 多 GW 联合调度（百万级设备验证）
```

### 复盘

- **Class C 是 GW 资源杀手**，SX1302 8 信道顶不住 10 个 Class C
- **ADR 在 Class C 模式下默认禁用**，需手动开启
- **大规模部署必须分 GW 负载**，单 GW 极限 ~100 Class A 终端
- **下行业务尽量用 Class A + 应用层轮询**，避免 Class C

### 来源

- _Inbox/LoRa-2026-07-31-candidates.md 候选 4
- Semtech SX1302 datasheet §3.4 Channel Capacity
- LoRaWAN 1.0.4 Spec §4 Class C

---

## 案例 5：Class B beacon 漂移导致下行永远收不到

### 现象

智慧路灯项目（200 个路灯），NS 端发"亮度调节"命令给所有路灯（每 5 分钟），但 30% 路灯命令丢失。终端 log 显示"beacon timeout"。

### 抓 log

```text
终端 log：
00:00:00 [INFO] Beacon received, sync OK
00:05:00 [INFO] Ping slot 0, RX timeout
00:10:00 [INFO] Ping slot 0, RX timeout
00:15:00 [WARN] Beacon timeout (5 missed)
00:15:01 [WARN] Re-sync to beacon...

GW log：
00:00:00 [INFO] Beacon sent at 485.3 MHz
00:05:00 [INFO] Downlink sent to 0xBB1... at ping_slot=0
00:10:00 [INFO] Downlink sent to 0xBB1... at ping_slot=0  (no ACK from terminal)
```

### 定位

**GPS 失锁 + 时钟漂移**：

```text
Class B 同步链路：
  1. GW GPS 锁 → 发出 Beacon @ 128s 周期
  2. 终端监听 Beacon → 同步本地时钟
  3. 终端按 ping_slot 时隙开 RX 窗口（默认 30ms）
  4. NS 通过 GW 在指定 ping_slot 发下行

问题：
  - GW 安装在路灯杆上，GPS 天线被树遮挡
  - 1 天后 GPS 失锁（锁相环失锁）
  - GW 内部 TCXO 漂移 ±10 ppm
  - 128 秒后偏差 = 128 × 10 × 10^-6 = 1.28 ms
  - 终端 ping_slot 窗口 30ms，理论上能接住
  - 但累积 1 天后偏差 = 864 ms → 远超窗口
  - 终端错过 GW 下行
```

**根因**：GPS 失锁 + TCXO 漂移 + 终端 ping_slot 窗口太短。

### 修复

```c
// 修复 1：GW 端 GPS + TCXO 升级
// GPS 模块换用外置天线 + 锁星灵敏度 -167 dBm
// TCXO 从 ±10 ppm 升级 ±2 ppm
// 失锁告警：GPS LED + NS 告警

// 修复 2：终端 ping_slot 窗口扩大
// 改用 LoRaMac-node 4.7+ 默认窗口 30ms
// 但应用层主动拉长 RX 时间
#define PING_SLOT_RX_WINDOW 100  // ms（默认 30ms）

// 修复 3：ping_period 改大
// 默认 30s 改到 60s（减少终端醒的次数）
#define PING_PERIOD_MS  (60 * 1000)

// 修复 4：GPS 失锁时 GW 切换为 Class A 模式
// 网关管理：检测到 GPS 失锁，临时禁用 Class B
// 全部终端 fallback 到 Class A
```

**GW 端管理**：

```bash
# ChirpStack GW Bridge 配置
# 监测 GPS 状态
watch -n 1 "cat /dev/ttyAMA0 | grep -i gps"

# GPS 失锁告警脚本
if ! gps_lock_status; then
    disable_class_b
    send_alert "GPS失锁,Class B 禁用"
fi
```

### 复盘

- **Class B 严重依赖 GPS 同步**，城市部署 GPS 失锁频繁
- **TCXO 温漂是长周期隐患**，必须用工业级 ±2 ppm
- **ping_slot 窗口不能太短**（30ms 在温漂下易失败）
- **大规模 Class B 部署慎用**，Class A + 应用层补偿更稳定
- **GW 端必须有 GPS 失锁告警**，否则 Class B 静默失效

### 来源

- _Inbox/LoRa-2026-07-31-candidates.md 候选 5
- LoRaWAN 1.0.4 Spec §7 Class B
- SX1302 GPS 同步要求 ±100 µs

---

## 案例 6：CN470 固件烧到 US915 板，半年没数据

### 现象

出口美国的资产追踪设备（5000 台），出厂测试 100% 通过（射频测试用屏蔽箱 + 频谱仪），发到美国后半年一台没数据，售后返修 30%，工程师搞了 3 个月才发现问题。

### 抓 log

```text
现场 RF 扫描（频谱仪）：
  CN470 固件 → 输出 470.3 MHz（应该 902.3 MHz）
  终端在 902 MHz 看不到任何信号

US915 频段规划：
  902.3 ~ 914.9 MHz（上行 64 信道）
  923.3 ~ 927.5 MHz（下行 8 信道）
  终端烧录 470 MHz 固件 → 完全在 US915 频段外
```

### 定位

**生产烧录 bug + 出厂测试盲区**：

```text
生产流程：
  1. PCB 贴片 → 烧 boot
  2. 烧固件（CN470 版本，库存 firmware 误用）
  3. 射频测试（屏蔽箱）→ 测 470 MHz 功率 + 灵敏度
  4. 出货（标签写"US915"但固件是 CN470）

出厂测试盲区：
  - 屏蔽箱测试只看功率 + 灵敏度
  - 不验证频率准确性（频谱仪没看）
  - 不与 US915 GW 真实联调
  - CN470 频段测试通过 ≠ US915 频段可用
```

**根因**：

- 产线固件管理混乱，CN470 / US915 固件同名不同 region
- 出厂测试只看 PHY 层功率，不验证实际频段
- 没有按出货区域分 bin 烧录

### 修复

```c
// 修复 1：固件命名严格按 region
// lora-fw-cn470-v1.0.0.bin
// lora-fw-us915-v1.0.0.bin
// lora-fw-eu868-v1.0.0.bin

// 修复 2：固件启动打印 region
void lora_print_region(void) {
    log("Region: %s", REGION_NAME);  // "CN470" / "US915" / ...
}

// 修复 3：SN 绑定 region
// 产线烧录脚本：读产品 SN 前 2 位 → 选 region
// SN 开头 CN → 烧 CN470 固件
// SN 开头 US → 烧 US915 固件
import re
def get_region_from_sn(sn):
    if sn.startswith("CN"):
        return "CN470"
    elif sn.startswith("US"):
        return "US915"
    elif sn.startswith("EU"):
        return "EU868"
    else:
        raise ValueError(f"Unknown region for SN {sn}")

// 修复 4：出厂测试必须联调 NS
// 1. 屏蔽箱测功率 + 灵敏度
// 2. 出屏蔽箱连真实 GW + NS
// 3. 验证 Join 成功 + 业务帧正常
// 4. 打印 region + DevEUI + Join 时间
```

**现场修复**：

- 5000 台返厂重新烧录
- 按 SN 分 bin 烧 US915 固件
- 重新出厂测试
- 直接成本：$50,000+（运费 + 人工 + 烧录）

### 复盘

- **固件 region 必须 SN 绑定**，产线不可混用
- **出厂测试必须联调真实 NS**，不能只测 PHY
- **屏蔽箱测 PHY ≠ 实际工作**，必须端到端
- **频段错配是出口项目最大坑**，事前必看 SN 区域表
- **产品手册必须明确 region 标识**（SN 命名规则 + 标签）

### 来源

- _Inbox/LoRa-2026-07-31-candidates.md 候选 6
- 实战复盘（项目损失 $50K+）
- LoRaWAN Regional Parameters 1.0.4rA

---

## 案例 7：天线匹配差导致距离从 5km 缩到 500m

### 现象

远距资产追踪设备（牧牛项圈），新疆牧场部署，标称"5 km 距离"，实测 500m 就开始掉包。客户索赔。

### 抓 log

功率分析仪 + RSSI 监控：

```text
正常板（参考设计）：
  1km 处 RSSI  = -75 dBm（稳定）
  5km 处 RSSI  = -100 dBm（开始掉包）
  10km 处 RSSI = -115 dBm（无连接）

问题板（量产）：
  1km 处 RSSI  = -85 dBm
  5km 处 RSSI  = -120 dBm（无连接）
  500m 处 RSSI  = -95 dBm（开始掉包）
```

差 10~15 dB，等于距离缩 3~5 倍。

### 抓波形

VNA 扫 S11：

```text
问题板：
  868 MHz 处 S11 = -6 dB（应 < -10 dB）
  谐振点偏移到 850 MHz（应 868 MHz）

正常板：
  868 MHz 处 S11 = -14 dB
  谐振点 = 868 MHz（精准）
```

### 定位

**天线匹配网络算错**：

```text
参考设计：868 MHz π 型匹配 (5.6pF + 0Ω + 3.3pF)
实际物料：
  - 5.6pF 改 6.8pF（采购 C0G 缺货换 X7R 替代）
  - X7R 容值漂移 ±15%
  - 实际容值 = 6.8 × 1.15 = 7.82 pF
  - 谐振点偏移 ~20 MHz
  - 868 MHz 反射大，S11 仅 -6 dB
```

**额外问题**：

- 弹簧天线厂商换（便宜供应商）
- PCB 板厚从 1.6mm 改 1.0mm（成本考虑）
- 板厚变化影响天线走线阻抗

### 修复

```text
1. 选 C0G / NP0 材质 MLCC（容值稳定 ±5%）
2. 调谐天线匹配网络（实际谐振在 868 MHz）
   - 用 VNA + 调配工具迭代
   - 最终：4.7pF + 0Ω + 2.7pF
3. PCB 改回 1.6mm 标准板厚
4. 弹簧天线换回原厂
5. VNA 验证 S11 < -12 dB @ 868 MHz
6. 现场 5km 测试 OK
```

**产线增加 VNA 测试工位**：

```text
□ 屏蔽箱功率测试（基础）
□ 频谱仪频率准确度（验证 region 正确）
□ VNA S11 测试（验证天线匹配）
□ 真实 GW 联调（验证端到端）
```

### 复盘

- **天线是 LoRa 设计第一坑**，参考设计不能照抄
- **MLCC 材质**：高频必选 C0G/NP0，X7R/Y5V 必出锅
- **VNA 验证是产线必加项**，每批次必做
- **物料替代必须重测**，不能简单换料
- **距离差 10 dB = 距离缩 3 倍**，客户索赔风险大

### 来源

- _Inbox/LoRa-2026-07-31-candidates.md 候选 7
- Semtech SX1276/SX1262 应用笔记 §2.3 天线设计
- 实战复盘（索赔 $200K+）

---

## 案例 8：Frame Counter 溢出，节点跑 2 年后断网

### 现象

智能水表 1000 台（每 30 分钟上报一次），运行 2 年后，5% 设备陆续断网。log 显示"frame counter invalid"。

### 抓 log

```text
ChirpStack NS：
[ERROR] Uplink from 0x12345678 frame counter 0 must be > 0
[ERROR] Uplink from 0x12345679 frame counter 0 must be > 0
[ERROR] Uplink from 0x1234567A frame counter 0 must be > 0

终端日志：
[FATAL] Frame counter overflow, reset session
[FATAL] Re-Join triggered
[INFO] Join Request sent
```

### 定位

**Frame Counter 16-bit 溢出**：

```text
16-bit Frame Counter 最大值 = 65535
每 30 分钟 1 帧 = 48 帧/天
65535 / 48 = 1365 天 ≈ 3.7 年
```

**实际为什么 2 年就出问题**：

- 部分终端 RTC 漂移 → 上报频率增加（每 5 分钟 1 帧）
- 实际帧数比预期多 6 倍 → 2 年就到 65535
- Frame Counter = 0 → NS 端认为重放 → 拒
- 终端必须重新 Join（DevNonce 重置流程）

**根因**：

- 16-bit Frame Counter 是 LoRaWAN 1.0.x 设计
- 长寿命终端（5+ 年）必然溢出
- 厂商未实现 32-bit Frame Counter 扩展（LoRaWAN 1.1）

### 修复

```c
// 修复 1：终端用 32-bit Frame Counter（厂商扩展）
// 协议上 LoRaWAN 1.0.x 不支持，但厂商可自定义
// 部分 NS（TTN v3）支持
uint32_t fcnt_up_32;  // 实际存 32-bit
uint16_t fcnt_up_16;  // 协议字段
// 上行时把 32-bit 截断成 16-bit，但 NS 端校验递增

// 修复 2：终端 Frame Counter 溢出自动 Re-Join
void lora_on_uplink(void) {
    if (s_fcnt_up == 0xFFFF) {
        // 溢出，触发 Re-Join
        lora_force_rejoin();
    } else {
        lora_send_uplink(s_fcnt_up++);
    }
}

// 修复 3：NS 端（ChirpStack）允许重置后 FCnt=0
// chirpstack.toml
[network]
reset_frame_counter = true  // 允许 Re-Join 后 FCnt 归零
```

**预警机制**：

```c
// 终端每 N 帧打印一次 FCnt 状态
if (s_fcnt_up > 60000) {
    log_warn("Frame counter near overflow: %u", s_fcnt_up);
}
// NS 端监控所有终端 FCnt
// 接近 65535 时告警，提前安排 Re-Join
```

### 复盘

- **Frame Counter 16-bit 是长寿命终端的定时炸弹**
- **电池寿命越长，越要监控 Frame Counter 趋势**
- **新项目用 LoRaWAN 1.1（32-bit FCnt）+ 厂商支持**
- **Re-Join 流程要稳定**，DevNonce / Session 都要重置
- **预警阈值**：FCnt > 60000 就告警

### 来源

- _Inbox/LoRa-2026-07-31-candidates.md 候选 8
- LoRaWAN 1.0.4 Spec §4.4 Frame Counter
- LoRaWAN 1.1 改进（32-bit FCnt）

---

## 案例 9：私有频段（780 MHz）误用 US915 固件，工厂批量报废

### 现象

某国内项目定制 780 MHz 私有频段（军工 / 政务用），首批 1000 台出货，工厂用 US915 固件烧录（库存固件），现场 100% 搜不到，1000 台全部返修。

### 抓 log

```text
现场 NS 配置：
  RX1 频率：923.3 MHz
  RX2 频率：923.3 MHz

实际终端发射：
  频率：780 MHz（定制固件正确）
  → NS 端 923 MHz 接收，错过 780 MHz 信号
```

### 定位

**私有频段 + 固件错用**：

```text
项目需求：
  - 客户军工，频段 780~786 MHz
  - 厂商定制固件，修改了 SX1276 频率映射
  - 终端实际发射 780 MHz

产线：
  - 工程师以为"定制 = 改固件参数 = 通用 US915 也能跑"
  - 直接用 US915 固件烧录
  - 出厂测试只看 PHY 功率 OK
  - 实际烧录 US915 固件 → 终端发射 902 MHz
  - 现场 NS 听 780 MHz → 错过

根因：
  - 产线没收到"定制固件"通知
  - 工厂用通用 US915 固件烧
  - 工程师对 LoRa 频段映射不熟
```

### 修复

```c
// 修复 1：重新烧录定制 780 MHz 固件
// 全部 1000 台返厂

// 修复 2：固件版本号强制绑定 region
// 烧录工具：
void verify_firmware_region(const char *expected_region) {
    char fw_region[16];
    get_firmware_region(fw_region);  // 读固件自带 region
    if (strcmp(fw_region, expected_region) != 0) {
        log_error("Firmware region mismatch: %s != %s",
                  fw_region, expected_region);
        halt();
    }
}

// 修复 3：出厂测试增加"频率精度"项
// 1. 测功率（基础）
// 2. 测频率准确度（频谱仪，必加项）
// 3. 测灵敏度（屏蔽箱）
// 4. 联调真实 NS（不同频段）
```

### 复盘

- **私有频段项目必须明确告知工厂**，不能默认"通用"
- **固件 region 标识是产线护身符**，每个固件必带 region
- **频率准确度测试是出厂必加项**，频谱仪扫描覆盖目标频段
- **定制项目 = 独立 SN 段 + 独立固件**，不能跟通用混
- **工厂与设计方沟通必须留文档**，变更要有 RFC 记录

### 来源

- _Inbox/LoRa-2026-07-31-candidates.md 候选 9
- 实战复盘（损失 $80K+）
- 工厂烧录规范

---

## 案例 10：Class C 路灯 220V 浪涌 + 零线接反烧板

### 现象

某智慧城市路灯项目批量部署 500 台 LC01（Dragino），Class C 模式 24h 在线接收下行。量产烧录后现场反馈：

- 上电 30% 概率整机无响应（电源指示灯不亮）
- 现场拆解：板子 220V 输入端 TVS 管击穿、整流桥短路
- 同批次 50 台返厂，电源模块全烧毁

### 抓包

```text
LoRaWAN 层无异常：节点 OTAA 入网成功，正常 uplinks
HCI / 串口层无异常：MCU 在跑，但 5V 输出为 0
电源层异常：
  1. 万用表量 220V 输入：L-N 电压 = 220V AC
  2. 拆电源板：TVS（型号 P6KE）击穿 → 短路
  3. 查 PCB：火线 L 接在 IN 接口、零线 N 也接在 IN 接口
     （设计是 IN/L 接火，IN/N 接零；现场电工两线都接到 IN 端子）
  4. 浪涌电流：未接 N 回路时，浪涌从 L-IN 流入无法泄放
     → 全部灌进 TVS → TVS 短路 → 整流桥烧毁
```

### 定位

```text
1. 复现 5 台新机：L 单独接 IN 端子 + N 悬空
   → 上电 200ms 内 TVS 温度急升，1s 内击穿
2. 正确接线：L 接 IN/L，N 接 IN/N
   → 上电正常，OTAA 30s 入网
3. 查图纸：电源模块有 TVS + MOV 双防浪涌
   → 但零线回路缺失时 MOV 失去泄放路径
4. 查现场电工：师傅说"反正两根线都进端子就行"
   → 没有看丝印"L/N"标记
```

### 修复

```text
固件侧（不能解决，但能减少损失）：
  1. 加 ADC 实时采 5V 电源电压，异常立即进 safe mode
  2. 上电 30s 内没 OTAA 成功 → 关闭所有外设 + URC 输出
  3. 串口输出"POWER ABNORMAL"提示现场排查

硬件侧（必须做）：
  1. 电源 PCB 加极性保护（桥堆前串联 1 个 PTC 自恢复保险）
  2. 强标 L / N 端子编号 + 红蓝双色塑料片
  3. 配线盒附"必须区分 L/N"警示贴
  4. 工厂预装默认 L/N 线序检测（用 MCU ADC 读半波整流后电压判断）

产线侧（必须做）：
  1. 出货前 100% 老化测试：220V 上电 1h + 看电源温度
  2. 现场电工培训：L/N 不能共用一个端子
  3. 配套"防错接线"接插件：L/N 物理防呆
```

### 复盘

- Class C 路灯场景下，**电源设计是第一道防线**——节点 7x24 在线，浪涌无处不在
- TVS + MOV 不是"装了就行"，要确保**零线回路完整**才能泄放
- 工厂出货前必须做老化测试（不能只测功能不测电源）
- 这类问题的根因经常是"现场接线和工厂设计默认假设不一致"——文档、配色、警示贴三方同步

### 来源

- _Inbox/LoRa-2026-08-03-candidates.md 候选 1
- Dragino LC01 量产复盘
- 现场电工返工记录

---

## 案例 11：化工厂排水 6km 非视距监测，ATMEGA328P + 太阳能 + 笔记本临时网关

### 现象

某化工厂"零排放"合规改造：6 公里外 6+ 排水口需要 7x24 监测水位回控制室大屏。预算紧（单点 < $100），工期 1 个月。

**最终选型**：ATMEGA328P + 超声波水位计 + GPS + LoRa 模块（私有频段 470 MHz），单点 < $100；网关用旧笔记本 + USB LoRa dongle 临时过渡。

### 抓包 / 链路实测

```text
现场测试（点对点，6km，2m 高架天线）：
  SF7 / BW125 / CR4/5：丢包 30%，不达标
  SF10 / BW125 / CR4/5：丢包 3%，勉强可用
  SF12 / BW125 / CR4/5：丢包 < 1%，稳定

链路预算：TX = 17dBm + 2dBi 高增益 = 19dBm EIRP
          接收灵敏度 SF12 = -137 dBm
          总预算 156 dB → 满足 6km 非视距

非视距损耗实测：
  1km 视距：RSSI -75 dBm
  3km 部分遮挡：RSSI -95 dBm
  6km 树枝密集：RSSI -115 dBm（刚好过 SF12 门限）

环境干扰：
  厂区 2.4GHz Wi-Fi 不影响（Sub-GHz）
  厂区 470MHz 干扰源：旧的对讲机（已退频）→ 需测底噪
```

### 定位（选型过程）

```text
候选技术对比（厂方要求：免流量费、私有部署、公里级）：
  ① LoRaWAN     ✅ 公里级 / 免流量费 / 私有部署
                  ✅ 厂方接受 470MHz 私有频段
                  ⚠ 单点 $30-50（模块）+ 自建网关
  ② NB-IoT      ❌ 走运营商，厂区无 NB-IoT 信号
                  ❌ 流量费按年计，不符合"零成本运行"
  ③ GPRS        ❌ 同样走运营商，且 2G 退网风险
  ④ ZigBee      ❌ 距离 < 100m，6km 完全不可能
  ⑤ LoRa 私有   ✅ 同 ①，但省去 LoRaWAN 协议栈
                  ✅ ATMEGA328P 资源可跑裸机 LoRa 库

最终选 LoRa 私有（不跑 LoRaWAN）：
  - 6 节点 + 1 网关，私有协议足够
  - ATMEGA328P 16KB Flash 跑 LoRa 库（点对点协议 ~5KB）
  - 省 LoRaWAN 协议栈 = 省 Flash = 单点成本 < $100
```

### 修复 / 落地

```text
硬件选型（每节点 $95 物料成本）：
  - ATMEGA328P-PU  DIP-28          $3
  - SX1276IMLTRT  LoRa 模块         $8
  - HC-SR04 超声波水位计             $2
  - AT24C32 EEPROM（配置 / 校准）    $0.5
  - GPS 模块 u-blox NEO-6M          $6
  - 太阳能板 6V/2W + 18650 锂电     $15
  - IP65 防水盒 + 2dBi 棒状天线     $20
  - 杂项（PCB / 接线 / 防水接头）   $40
  - 合计                          ≈ $95

协议设计（私有，1 字节命令 + 4 字节 payload + 4 字节 CRC）：
  - 0x01 水位上报  payload = 水位(cm) * 100
  - 0x02 GPS 位置   payload = lat(3B) + lon(3B)
  - 0x03 心跳       payload = 电池电压 * 100
  - 0x10 校准请求   payload = 0
  - 网关 ACK        payload = seq + RSSI
  - 重传：节点发 3 次（0s/2s/4s），任一 ACK 成功即停

笔记本网关过渡方案：
  - 旧笔记本（i5 / 4GB / Win10）+ USB LoRa dongle
  - Python 脚本：serial 读 LoRa → pandas 解析 → HTTP POST 到大屏
  - 大屏显示：Node-RED Dashboard（厂方内部部署）
  - 临时方案：等 LoRaWAN GW 量产替换（节省 1 步流程）

太阳能供电策略：
  - 6V/2W 板 + 1 节 18650（3000mAh）
  - 静态功耗 < 5mA（LoRa RX 模式 + ATMEGA sleep）
  - 发送瞬时 100mA，持续 < 1s
  - 阴雨天续航：约 7 天（足够应急）
```

### 复盘

- **选型决策不能只看技术参数，要看"运维成本 + 生命周期"**——NB-IoT / GPRS 流量费 + 信号盲区是杀手
- 6km 非视距是 LoRa **真实能力**，但要 SF12 + 2dBi 高增益 + 2m 高架天线三件套
- **笔记本临时网关**思路值得复用：旧设备 + Python 脚本 = 0 成本过渡
- LoRa 私有协议 vs LoRaWAN：**6 节点以下用私有，节省 80% 复杂度**
- 太阳能 + 18650 是 Sub-GHz 户外节点最经济方案（避免 220V 接入 + 防雷设计）

### 来源

- _Inbox/LoRa-2026-08-03-candidates.md 候选 2
- 化工厂"零排放"合规改造项目复盘
- ATMEGA328P + SX1276 私有协议代码（GitHub 公开仓库）

---

## 案例 12：无线气体探测器（LoRa + 4G）部署现场，频谱扫描 + 多子网 + 4G 休眠

### 现象

重庆飞测科技 GT-FC100TLH 无线气体探测器部署在老旧化工厂区 / 管廊：

- 现场电磁环境复杂（多台大功率电机 / 变频器 / 老式对讲机）
- 现场金属管道密集，多径 + 阻挡严重
- LoRa 单网关难以覆盖，4G 通道电池续航不足
- 现场部署 200+ 节点，掉线率初期 35%

### 抓包 / 现场频谱扫描

```text
频谱仪（Tektronix RSA306）扫 470-510 MHz：
  - 频段 1：470.3-470.7 MHz 被厂区旧对讲机占（5W 发射）
  - 频段 2：475.0-476.0 MHz 工业自动化设备谐波
  - 频段 3：480.0-481.0 MHz 变频器开关噪声
  - 干净频段：483-487 MHz（仅 4 个可用信道）

现场 RSSI 实测（厂区管廊，节点距网关 800m）：
  - 频段 1（对讲机占）：RSSI -100dBm，PER 30%
  - 频段 2（工业谐波）：RSSI -85dBm，PER 15%
  - 频段 3（变频器）：RSSI -95dBm，PER 20%
  - 干净频段（483-487）：RSSI -78dBm，PER < 1% ✅

多径 + 阻挡（金属管道密集区）：
  - 视距 1.5km：PER 2%
  - 非视距（穿 1 道管廊墙）：PER 18%
  - 非视距（穿 2 道管廊墙）：PER 45%
  - 绕管廊 1 个转角 + 1 面墙：PER 30%
```

### 定位（部署参数 7 步调优）

```text
Step 1：频谱仪选最低干扰信道
  → 选定 483-487 MHz 4 个信道
  → 节点静态锁信道（不用 ADR 跳频）
  → 牺牲 1/4 频谱换稳定

Step 2：多子网分配不同 SF/信道
  - 子网 A：SF7 / 483 MHz，覆盖近区
  - 子网 B：SF9 / 485 MHz，覆盖中区
  - 子网 C：SF12 / 487 MHz，覆盖远区
  - 节点按 RSSI 选子网（出厂烧入）
  - 网关三套 SX1302 同时跑

Step 3：中继节点绕阻挡
  - 管廊转角处加中继（电池供电 + 太阳能）
  - 中继节点走"双 SF 桥接"：上游 SF12 接终端，下游 SF7 接网关
  - 牺牲延迟换覆盖

Step 4：4G 通道休眠保 3 年电池
  - LoRa 通道 7x24 在线（探测气体 → 实时上报）
  - 4G 通道仅"超标"时唤醒
  - 平时 NB-IoT 走 PSM 模式（功耗 < 5uA）
  - 4G 模块用 Air724UG（带 PSM/eDRX）
  - 电池续航：3 年（4000mAh + 太阳能 6V/2W 补电）

Step 5：天线垂直朝天
  - 棒状天线 2dBi 垂直
  - 30cm 内禁金属
  - 防爆外壳用非金属（玻璃钢 / 工程塑料）

Step 6：信道干扰排查自动化
  - 网关每 6 小时跑 1 次"信道扫频"（短时切换所有信道）
  - 记录 RSSI / PER / 干扰水平
  - 自动选最优信道写回节点（下次唤醒下发）

Step 7：节点测距 + 路径规划
  - 部署前用 GPS 记录每个节点位置
  - QGIS 标 Fresnel 区域，避开阻挡
  - 网关放 30m 高楼顶（视距好）
```

### 修复（多级级联架构）

```text
三级架构：
  节点（电池） → 中继（太阳能） → 接入网关 → NS（云端）
  
  - 节点：Class A，电池 3 年
  - 中继：Class A + Class C 桥接，太阳能供电
  - 网关：8 通道 SX1302，三频段并行
  - NS：自建 ChirpStack，告警阈值 + 工单系统

降级策略：
  - 节点掉线 3 次 → 标"疑似故障"
  - 5 次掉线 → 自动派单
  - 4G 通道探测到气体超标 → 立即强制上报（不管 LoRa 通不通）
  - LoRa + 4G 双通道冗余（主 LoRa / 备 4G）
```

### 复盘

- 工业现场 LoRa 部署**第一坑 = 频段干扰**，必须频谱仪扫
- 多子网 + 多 SF 是覆盖复杂厂区的唯一办法
- 中继节点走"双 SF 桥接"是工程师实务经验，Semtech 不一定推荐
- 4G 通道做备份 + LoRa 跑主——4G 仅超标时唤醒保电池
- 200+ 节点不掉线 = **频谱 + 部署 + 电池策略**三方同步优化

### 来源

- _Inbox/LoRa-2026-08-06-candidates.md 候选 3
- 重庆飞测科技 GT-FC100TLH 部署规范
- LoRa Alliance Industrial Deployment Best Practice

---

## 案例 13：智慧农业 300 亩葡萄园部署，节点休眠参数不同步

### 现象

宁夏某 300 亩葡萄园智慧农业项目（23 万人民币，8 通道网关 + 50 个土壤湿度节点）：

- 部署后第 3 天，半数节点"失联"
- 重启后恢复，但 1 周后又复发
- 现场查：节点电池电压正常，RF 链路 RSSI -75dBm 健康
- 网关 / NS 后台显示节点"心跳超时"

### 抓包 / 链路实测

```text
节点默认参数（出厂固件）：
  - Class A
  - 上行间隔：5 分钟
  - 唤醒后 5 秒开 RX1/RX2 窗口
  - 唤醒后立即 sleep

网关参数（ChirpStack 默认）：
  - 默认 ping_slot_periodicity = 7 (1 秒)
  - 默认 ping_slot_default_dr = 0 (SF12)
  - 节点心跳超时：5 分钟

实测冲突：
  - 节点 5 分钟醒一次，每次开 RX1 窗口 1s
  - 网关默认 1 秒 ping slot → 节点醒时网关恰好在 ping slot
  - 节点被 ping slot 误唤醒 → 状态不同步
  - 节点"以为收到下行"但实际是 ping slot 占位
  - 节点 sleep 时序错乱 → 后续心跳错位
  - 累计 1 周后完全失同步
```

### 定位（睡眠参数 4 步调整）

```text
Step 1：检查节点唤醒时序
  - 节点 STM32L4 + RN2483 LoRa 模组
  - 默认 RN2483 固件 = 5 分钟醒
  - 节点 MCU 在 sleep 5 分钟，唤醒时序精准（±1s）
  → 时序本身 OK，问题在网关

Step 2：检查 ChirpStack ping slot 配置
  - ping_slot_periodicity 默认 7（每 1s 一次 ping slot）
  - ping_slot_default_dr = 0（SF12，最低速率）
  - 50 个节点 + 1 秒 ping slot = 网关负载爆炸
  - 网关只能服务 ~10% ping slot 实际收到
  - 节点被误唤醒率 30%+

Step 3：调整 ping slot 参数
  - ping_slot_periodicity = 4（每 16s 一次）
  - 节点上行间隔也调到 16s
  - 节点醒时间 = 网关 ping slot 时间
  - 误唤醒率降到 0

Step 4：调节点 / 网关 / NS 唤醒同步
  - 节点：16 分钟醒一次（够省电 + 葡萄园数据需求）
  - 网关：ping slot 4（16s 一次）
  - NS：心跳超时 = 20 分钟（> 节点醒周期 1.25x）
  - 三方同步后稳定
```

### 修复（动态休眠 + 三大干扰源排查）

```text
动态休眠策略：
  - 土壤湿度变化 < 5%：节点 30 分钟醒一次
  - 土壤湿度变化 5-10%：节点 10 分钟醒一次
  - 土壤湿度变化 > 10%（灌水 / 雨后）：节点 1 分钟醒一次
  → AA 电池（4 节）从 8 个月续航拉到 22 个月
  → 用 MCU 内部温度传感器 + 土壤湿度趋势判断

三大干扰源排查：
  1. 滴灌变频泵（50Hz 工频 + 高频谐波）
     - 距节点 1m 内：PER 30%
     - 距节点 5m+：PER < 1%
     - 节点装在变频泵上方 5m+ 立柱
     
  2. 温室金属骨架（钢结构）
     - 节点装在金属骨架旁：RSSI -95dBm
     - 节点装在木质杆上：RSSI -70dBm
     - 全部改用木质立柱
     
  3. 无人机图传（2.4GHz）
     - 葡萄园上空偶尔无人机喷洒
     - 2.4GHz 不影响 Sub-GHz LoRa
     - 但 Wi-Fi 网关要远离（> 30m）
```

### 复盘

- 农业 LoRa 部署**第一坑 = 节点 / 网关 / NS 唤醒时序不同步**
- ChirpStack 默认参数不一定适合农业场景，**必须按应用调**
- 三大干扰源（变频泵 / 金属骨架 / 无人机）在农业场景是"常识"，但工程师容易忽略
- 动态休眠（按业务变化率）比固定周期省 60% 电池
- 23 万项目失败 = 1 周救回来，关键是**找到时序不同步根因**（不是 RF / 电池问题）

### 来源

- _Inbox/LoRa-2026-08-06-candidates.md 候选 5
- 宁夏 300 亩葡萄园项目复盘
- RN2483 + ChirpStack 部署规范

---

## 案例 14：智能水表 7 大掉线排查路径

### 现象

某水务公司远程抄表项目，部署 5000 个 LoRa 智能水表（户外分散部署）：

- 整体掉线率 8%（行业平均 1-2%）
- 现场反馈：水表读数缺失 / 滞后 / 偶尔超大量程数据
- 售后投诉率高，维护成本高

### 抓包 / 现场排查

```text
掉线 7 大原因（按频率降序）：
  1. 信号覆盖不足（40%）
     - 远区水表距网关 8km（超过极限 6km）
     - 城市建筑阻挡（多径 + 衰减）
     - 解决：加中继 + 加网关
  
  2. 基站故障 / 网络波动（20%）
     - LoRaWAN GW 8 通道容量满
     - 节点 uplink 冲突
     - 解决：增 GW + 优化 ADR
  
  3. 参数配置错（15%）
     - DevNonce 重复（OTAA 失败）
     - Frame Counter 溢出
     - 解决：固定 DevNonce 范围 / 改 ABP
  
  4. 电池电量耗尽（10%）
     - 7 年电池没到期，3 年就死了
     - 原因：节点 debug 时未关 RF（持续 5uA → 50mA）
     - 解决：debug 模式必须彻底关闭 RF
  
  5. 硬件故障（8%）
     - 模组焊接不良
     - 防水失效（户外水浸）
     - 解决：换 IP68 防水 + 灌封
  
  6. 软件固件 bug（5%）
     - OTA 升级失败 → 节点变砖
     - 解决：双 Bank 固件 + 回滚
  
  7. 安全 / 配对问题（2%）
     - 误删 AppKey
     - 节点重连失败
     - 解决：远程配对 + 双 AppKey
```

### 定位（7 步排查路径）

```text
Step 1：信号覆盖诊断
  - 现场 GW 位置 + 信号热图
  - 远区（> 6km）水表确认 RSSI < -120dBm → 信号问题
  - 解决：加中继 / 加 GW

Step 2：网关容量诊断
  - ChirpStack 后台看 GW 接收 / 发送 / duty cycle
  - SX1302 8 信道满载时 PER 飙升
  - 解决：增 GW + 调整节点分布

Step 3：参数配置核查
  - DevNonce 范围：0x0001-0xFFFF 严格去重
  - Frame Counter：32 位，溢出需重启设备
  - Join AcceptDelay：1-15s 调整

Step 4：电池电量诊断
  - 节点读电池电压（LoRa 上报）
  - 电压 < 3.0V 报警
  - debug 模式彻底关 RF（不能漏）

Step 5：硬件故障定位
  - 万用表量 RF 输出（50Ω 端口 S11）
  - 防水测试：泡水 24h 看是否进潮
  - 模组温度：异常高 → 焊接问题

Step 6：固件 bug 排查
  - OTA 升级成功率 < 95% → 双 Bank 回滚
  - 节点"假死"：看门狗复位
  - 节点 log 远程读（Class C 下行）

Step 7：安全 / 配对问题
  - AppKey 变更后节点必须重 join
  - 用双 AppKey 轮换（避免单 key 失效）
```

### 修复

```text
硬件侧：
  - 防水：IP68 + 灌封（环氧 / 硅胶）
  - 电池：锂亚硫酰（Li-SOCl2），10 年保质
  - 天线：内置 FPC 天线 + 钣金屏蔽
  - 温度范围：-40 ~ +85°C（户外 -25°C 冬季实测）

固件侧：
  - 双 Bank 固件：A/B 两区，OTA 失败回滚
  - 远程看门狗：心跳超时 24h → 自动复位
  - 远程 log：Class C 模式下可下行读最近 1KB log
  - OTA 加密签名：防回滚攻击

部署侧：
  - GW 间距 3-5 km（城区）/ 8-10 km（农村）
  - 节点密度：单 GW < 1000 节点
  - 信号热图：部署前必备
  - 现场培训：客户工程师会查 GW 后台

运维侧：
  - 后台自动派单：节点掉线 3 次 → 工单
  - 远程诊断：读节点 RSSI / SNR / 电池
  - 定期巡检：每季度现场 1 次（目视 + 抽测）
  - 备件库存：5% 备品备件
```

### 复盘

- 智能水表 7 大掉线原因 = **LoRa 户外部署的典型问题集**
- 信号覆盖不足 40% 占比说明：**GW 选址 + 密度规划是项目成败关键**
- 电池故障 10% 中 50% 是"debug 模式忘关"——研发流程必须卡
- 双 Bank 固件 = OTA 升级必选项（不能省）
- 5000 节点级项目，**远程诊断能力**（下行 log）比现场派人省 80% 成本

### 来源

- _Inbox/LoRa-2026-08-08-candidates.md 候选 3
- 智能水表远程抄表项目复盘
- LoRa Alliance Smart Metering White Paper

---

## 案例 15：LoRaWAN Join-Storm（欧洲物业 5000 节点 / 1/5 日重 Join）

### 现象

欧洲某物业 5000 节点 + 几台 LoRaWAN 网关，部署后：

- 1/5 节点每天重新 Join（重 Join 率 20%）
- 丢包率 80%
- 节点正常功能不受影响，但 NS 后台看 Join 风暴
- ADR 抗振荡完全失效

### 抓包 / 根因（Concept13 商业案例）

```text
25 项根因（按影响力降序）：

1. 共享 AppKey（30% 影响）
   - 全部节点用同一 AppKey
   - 节点 OTA 升级后默认行为差异 → 重 Join
   - 重 Join 后拿到新 DevNonce → 跟旧 session 冲突

2. Gateway-as-LNS（25% 影响）
   - 多台网关各自当 LNS（独立 NS）
   - 同空间内 5 台 NS → 节点收 5 套 Join Accept
   - 节点只能跟其中 1 台 join → 频繁切换

3. Node Red 抢占（15% 影响）
   - Node Red 流程抢占 LNS 资源
   - Join Accept 处理延迟 > 30s
   - 节点超时重 Join

4. ADR 抗振荡失效（10% 影响）
   - 移动节点跨 SF 边界
   - ADR 命令频繁触发 → 重 Join

5. 频偏 0.1MHz（8% 影响）
   - 部分节点晶振漂移
   - GW 收不到 → 节点认为链路断 → 重 Join

其他 20 项：占 12%
```

### 定位（4 步）

```text
Step 1：观察 Join 频率
  - NS 后台看每小时 Join 次数
  - 正常：< 1% 节点/天
  - 异常：> 5% 节点/天
  - 当前：20% 节点/天 → Join-Storm

Step 2：找共享 AppKey
  - 查 NS 配置 → 全部节点用同 key
  - 改：每个节点烧入唯一 AppKey（量产烧录器配）

Step 3：迁集中云 LNS
  - 当前：5 台 GW 各自当 LNS
  - 改：1 台集中云 LNS + 5 台 GW 做 Packet Forwarder
  - 节点只跟 1 台 LNS 通信

Step 4：抗 ADR 振荡
  - 移动节点关闭 ADR
  - 锁 DR_5（SF7/125kHz）
  - 静态节点保留 ADR
```

### 修复

```text
核心修复（必做，砍 70% 问题）：
  1. 迁集中云 LNS
     - 1 台云端 LNS（ChirpStack / TTN）
     - GW 仅做 Packet Forwarder
     - 节点只 join 1 个 LNS
     
  2. 节点独立 AppKey
     - 量产烧录器：每个节点烧入唯一 key
     - key 生成：HMAC-SHA256(master_key, dev_eui)
     - 安全性 + 抗 Join-Storm

辅助修复（砍 20% 问题）：
  3. 移动节点关 ADR
  4. 频偏校正（TCXO / 软件补偿）
  5. Node Red 性能优化
  6. Join 限流（NS 配置：每节点每天最多 Join 3 次）
  7. DevNonce 防重（NS 缓存）
```

### 复盘

- **Join-Storm = 多根因叠加**——单修一个不够
- 25 项根因中前 3 项占 70%：**共享 AppKey / Gateway-as-LNS / Node Red 抢占**
- **集中云 LNS 是根治方案**（解决 25% + 15% = 40%）
- 移动节点必须关 ADR（不然跨 GW 切换就触发重 Join）
- 5000+ 节点项目，**架构设计比协议细节更重要**（分布式 LNS 是反模式）

### 来源

- _Inbox/LoRa-2026-08-22-candidates.md 候选 1
- Concept13 Join-Storm 商业案例
- LoRa Alliance Backend Interfaces TS002

---

## 案例 16：SX1301 网关 5 个长期稳定性故障（教科书级产线问题）

### 现象

SX1301 LoRaWAN 网关长期运行（6 个月+）出现 5 类故障：

1. 网关停机（突然不响应）
2. CRC_FAIL 100% 持续触发
3. 丢包率突然增大（> 20%）
4. DNS 解析失败
5. 网络安全事件（被攻击）

### 抓包 / 5 故障根因

```text
故障 1：网关停机
  现象：GW 完全不响应，ping 不通
  根因：SX1301 芯片裸露 → 受 LoRa 噪声干扰 → 假死
  排查：
    - log：packet_forwarder 进程死了
    - 重启后恢复
    - 但 1 周内复发
  解决：加屏蔽盒 + 风扇 + watchdog 守护进程

故障 2：CRC_FAIL 100% 持续触发
  现象：所有上行包 CRC 错
  根因：网关晶振失效 / SX1301 频偏
  排查：
    - log 连续 3 次 CRC_FAIL 100%
    - SX1301 复位 → 仍异常
    - 测晶振：32 MHz 频偏 > 50ppm
  解决：换晶振 + 升 systemd 触发自动重启

故障 3：丢包率 > 20%
  现象：节点距网关 < 2m，丢包率 20%+
  根因：节点 / 网关主频谐波灌相邻信道
  排查：
    - 节点 SX1276 发射频率 470 MHz
    - 网关 CPU 主频 1 GHz → 2 次谐波 500 MHz
    - 3 次谐波 1.5 GHz → 经非线性混频到 470 频段
    - 频谱仪看到 470 频段有 1 GHz 谐波
  解决：节点离网关 < 2m → 至少 5m

故障 4：DNS 失败
  现象：packet_forwarder → server 通信失败
  根因：DNS 解析失败 / server URI 错
  排查：
    - log：DNS resolution failed
    - 测试：nslookup loraserver.example.com
    - NS 域名变了 / DNS 缓存失效
  解决：固化 IP + DNS 缓存

故障 5：网络安全
  现象：日志出现 "Authentication failed"
  根因：未配 TLS / 用默认 token
  排查：
    - 抓包：HTTP 明文传输 → token 泄漏
    - 重放攻击
  解决：TLS + 双向认证 + 定期 rotate token
```

### 修复

```text
长期稳定性 4 步（教科书）：
  Step 1：屏蔽盒
    - SX1301 + 散热 + 屏蔽
    - 防 LoRa 噪声干扰
    - 防外部 RF
    
  Step 2：watchdog
    - 进程异常自动重启
    - 失败 3 次 → 整机重启
    - 远程监控（mqtt 推 heartbeat）
    
  Step 3：节点网关距离 ≥ 5m
    - 避免 1 GHz 主频谐波
    - 实测：2m 丢包 20% → 5m 丢包 < 1%
    
  Step 4：安全加固
    - TLS 双向认证
    - token 定期 rotate（30 天）
    - 限制管理端口只对内网开放
    - 防火墙只开 1700/8080 端口
```

### 复盘

- SX1301 是 **5+ 年前芯片**，长期稳定性必须主动加固
- 屏蔽盒 + watchdog + 5m 距离 + TLS = 4 件套
- 1 GHz 主频谐波 = **教科书级"近距离反而丢包"**
- DNS 失败是隐性杀手，必须固化 IP
- 长期运行 = 主动监控（不能等用户投诉）

### 来源

- _Inbox/LoRa-2026-08-13-candidates.md 候选 1
- CSDN 实战博客（江俊杰 2005）
- Semtech SX1301 datasheet §6

---

## 案例 17：LoRa 低功耗 3 大设计陷阱（2000 节点 3 年实测）

### 现象

某 IoT 厂商 2000 节点 LoRa 网络 3 年实地测试：

- Class A 41% 时间漂移
- 38% 首包失败
- "伪发送成功" 频繁

### 抓包 / 3 大陷阱

```text
陷阱 1：32MHz 晶振 ±234ppm 漂移
  - 节点用普通 32 MHz 晶振
  - 实测 3 年累计漂移 ±234 ppm
  - Class A 唤醒 > 2h → 累积时间漂移 > Class A 窗口
  - 接收窗口错位 → 38% 首包失败
  - 解决：唤醒 > 2h 必须 TCXO（温补晶振）

陷阱 2：SX1262 射频储能 < 15ms 致"伪发送成功"
  - 载荷 50B+ 时射频储能时间不足
  - 看似"已发送"实际未发出
  - 解决：预热 ≥ 15ms 再发
  - 两级储能：DC-DC 预热 + PA rampTime

陷阱 3：Class B 卡死 31% > Class A 17%
  - Class B 依赖 beacon 同步
  - 移动场景 / 遮挡下 beacon 频繁丢
  - 节点卡死等待 beacon
  - 解决：Class B 移动场景禁用
  - 关键场景：物流 / 资产追踪 → Class A + GPS 驯服
```

### 修复

```c
// SX126x rampTime + 储能预热
void lora_send_safely(uint8_t *payload, uint8_t len) {
    // Step 1：射频预热（关键）
    Radio.Standby();
    delay_ms(15);  // 储能 ≥ 15ms
    
    // Step 2：PA rampTime 配置
    Radio.SetTxConfig(MODEM_LORA, TX_OUTPUT_POWER, 0, LORA_BANDWIDTH,
                      LORA_SPREADING_FACTOR, LORA_CODINGRATE,
                      LORA_PREAMBLE_LENGTH, LORA_FIX_LENGTH_PAYLOAD_ON,
                      true, 0, 0, LORA_IQ_INVERSION_ON, 3000);
    //                  ^^^^
    //                  3000us = rampTime
    
    // Step 3：实际发送
    Radio.Send(payload, len);
}
```

### 复盘

- **32MHz 晶振精度是低功耗第一坑**——3 年累计 ±234 ppm
- 唤醒 > 2h 必须 TCXO（不能用普通晶振）
- 载荷 50B+ 预热 ≥ 15ms（不能直接发）
- Class B 卡死率（31%）> Class A（17%）
- 移动场景 Class A + GPS 驯服更稳

### 来源

- _Inbox/LoRa-2026-08-22-candidates.md 候选 4
- CSDN aiot 实战报告
- Semtech SX1262 datasheet §6

---

## 案例 18：chirp 物理层 + 3 大翻车坑（SF 迷信 / 吸盘天线失效 / ADR 振荡）

### 现象

某 LoRa 项目 3 大典型失败：

- 工程师"SF 越高越好"——触法
- 3000 节点水表凌晨拥塞
- ADR 振荡 → 节点死循环

### 抓包 / 3 翻车坑

```text
翻车 1：SF 迷信 = 触法
  现象：工程师配 SF12 追求"远距离"
  实测：EU868 1% duty cycle 限制
    SF12 / 125 kHz 单报 1.3s
    1% duty cycle = 1.3s / 100s = 1.3% > 1%
    → 触法（EU868 EN300.220）
  解决：
    - SF 选型看 duty cycle，不是看距离
    - 工厂出货前算 duty cycle
    - 5-10 节点/小时以上必须 SF7/8

翻车 2：吸盘天线金属腔失效
  现象：节点装在金属外壳，链路断
  根因：吸盘天线底座 = 金属耦合
        装在金属外壳 = 屏蔽
        天线增益 = 0
  解决：
    - 吸盘天线必须外置（穿外壳）
    - 或改用棒状 + 防水接头
    - 玻璃钢外壳才内置

翻车 3：ADR 振荡（移动场景 SF7↔SF12 横跳）
  现象：移动节点频繁 SF 切换
  实测：1 分钟内 SF 跳 5+ 次
  → 节点吞吐量 0
  → NS / 节点协议栈死循环
  解决：ADR 迟滞补丁
    - SF 切换必须 Hysteresis
    - SF7 → SF8 需连续 N 包 RSSI < -100
    - SF12 → SF11 需连续 N 包 RSSI > -90
    - 迟滞阈值：3-5 包
    - 实测：抖动降 80%
```

### 修复

```c
// ADR 迟滞补丁
typedef struct {
    uint8_t current_dr;
    uint8_t target_dr;
    uint8_t hysteresis_count;
    uint16_t hysteresis_threshold;  // 3-5 包
} adr_state_t;

void adr_update(adr_state_t *adr, int16_t rssi) {
    uint8_t target = adr_calculate_target(rssi);
    
    if (target != adr->current_dr) {
        if (target == adr->target_dr) {
            adr->hysteresis_count++;
            if (adr->hysteresis_count >= adr->hysteresis_threshold) {
                // 真的切换
                adr->current_dr = adr->target_dr;
                adr->hysteresis_count = 0;
                set_data_rate(adr->current_dr);
            }
        } else {
            // 切换目标
            adr->target_dr = target;
            adr->hysteresis_count = 0;
        }
    } else {
        adr->hysteresis_count = 0;
    }
}
```

### 复盘

- **SF 越高越好是错误认知**——duty cycle 限制
- 吸盘天线金属外壳 = 屏蔽
- ADR 振荡是移动场景通病——迟滞补丁降 80% 抖动
- 3000 节点凌晨拥塞 = 晶振漂移 + 纯 ALOHA
- 工厂出货前**算 duty cycle + ADR 迟滞**

### 来源

- _Inbox/LoRa-2026-08-22-candidates.md 候选 5
- 廊坊大讲堂（chirp 物理层）
- EN300.220 EU868 duty cycle 规范

---

## 案例 19：LoRaWAN CN470 同频 / 异频配错 + 8 子带映射表

### 现象

某国产 LoRaWAN 项目：

- 网关灯正常、节点回 Join Accept
- 但数据传不上去
- 反复 Join / 反复掉线
- 节点 RSSI 正常

### 抓包 / 根因

```text
CN470 频段宽 470-510 MHz：
  - 8 个子带（每个 5 MHz）
  - 子带 0：470-475 MHz
  - 子带 1：475-480 MHz
  - ...
  - 子带 7：505-510 MHz

同频 vs 异频（AT+BAND 配错）：
  - AT+BAND=7：同频（所有节点用同 1 个子带）
  - AT+BAND=8：异频（节点 / 网关用不同子带）
  - 配错 → RX1/RX2 频率错位 → 节点收不到下行

实测数据：
  - 配 AT+BAND=7（异频）→ 节点 join 后数据 OK
  - 配 AT+BAND=8（异频）→ 节点 join 后数据失败
  - 不同 LoRaMac-node 版本 BAND 含义不同（必须查文档）
```

### 修复（8 子带映射表）

```text
CN470 8 子带（推荐配置）：

| 子带 | 频率范围 (MHz) | 上行信道 | 下行信道 | 备注 |
| --- | --- | --- | --- | --- |
| 0    | 470-475        | 0-7      | 0-7      | 默认子带 |
| 1    | 475-480        | 8-15     | 8-15     | |
| 2    | 480-485        | 16-23    | 16-23    | |
| 3    | 485-490        | 24-31    | 24-31    | |
| 4    | 490-495        | 32-39    | 32-39    | |
| 5    | 495-500        | 40-47    | 40-47    | |
| 6    | 500-505        | 48-55    | 48-55    | |
| 7    | 505-510        | 56-63    | 56-63    | |

配规则（CN470 国产）：
  - AT+BAND=7 = 同频（私部署 / 小网络）
  - AT+BAND=8 = 异频（联盟推荐 / 大网络）
  - 多网关环境用 异频 + 信道分配

部署建议：
  - 单网关 + 少量节点：同频 + 子带 0
  - 多网关 + 大量节点：异频 + 子带分
  - 节点随机信道易撞不同子带 → 必须固化
```

### 复盘

- **CN470 频段宽 470-510 MHz** = 8 个子带，每个 5 MHz
- **同频 vs 异频**取决于 LoRaMac-node 版本
- 节点随机信道易撞不同子带 = 国产项目第一关
- 子带规划是国产 LoRa 部署的隐藏门槛
- 8 子带映射表必须固化在工厂配置

### 来源

- _Inbox/LoRa-LoRaWAN-2026-08-16-candidates.md 候选 3
- CSDN 实战博客
- CN470 LoRaWAN Regional Parameters RP2-1.0.3

---

## 案例汇总

| # | 现象 | 根因 | 难度 |
| --- | --- | --- | --- |
| 1 | DevNonce 重复 Join Fail | 终端 nonce 静态化 | 中 |
| 2 | MIC Failure 误判 | AppKey 长度截断 | 中 |
| 3 | EU868 数据丢失 | Duty Cycle 1% 超 | 低 |
| 4 | GW 容量打满 | Class C + ADR 失效 | 中 |
| 5 | Class B 下行丢失 | GPS 失锁 + TCXO 漂移 | 高 |
| 6 | CN470 烧到 US915 | 产线固件混用 | 低（但损失大） |
| 7 | 距离缩 10 倍 | MLCC 材质 + 天线匹配 | 中 |
| 8 | Frame Counter 溢出 | 16-bit 计数限制 | 中 |
| 9 | 780 MHz 私有错烧 | 工厂 + 设计脱节 | 中 |

## 关联文档

- `bus/lora.md` 主题入口
- `bus/lora-practical.md` 调试流程速查
- `bus/lora-deep-dive.md` 协议栈深挖
- `bus/lora-index.md` 主题地图 + 导航
