# BLE 产线实战案例库

## 目标

把产线常见的 BLE 通信失败、配对错、0x3E 断开、SMP DoS、ADC 干扰晶振、bonding 残留等问题写成案例库。每个案例：

- 现象（现场）
- 抓包 / 抓 log（判断）
- 定位（根因）
- 修复（代码 / 硬件 / 配置）
- 复盘（如何预防）

案例来源：_Inbox/ 候选素材 + 实战复盘。

## 案例 1：RTL8762E 配对 DoS 漏洞

### 现象

配对流程中，攻击者在距离 10m 范围内发起配对请求，目标设备配对永远失败。远端 central 显示"配对被设备拒绝"。

### 抓包

nRF Sniffer 抓 SMP 流程：

```text
正常顺序：Public Key → Pairing Random → Pairing Confirm
攻击顺序：攻击者先发 Pairing Random（pre-emptive）
          → 设备未强制 Public Key 在前
          → 状态机错乱，配对失败
          → 攻击者重发，循环阻断
```

抓包关键帧：SMP `Pairing Random` 在 `Pairing Public Key` 之前出现。

### 定位

Realtek RTL8762E SDK v1.4.0 的 SMP 状态机未强制执行 Core Spec 5.3 §3.5.1 的 sequencing：

> **Public Key SHALL be sent before Pairing Random.**

状态机实现：

```c
// SDK v1.4.0 错实现
void smp_handle_random(smp_ctx_t *ctx, uint8_t *random) {
    smp_send_confirm(ctx);  // 状态机没校验前序
    ...
}

// 修复后
void smp_handle_random(smp_ctx_t *ctx, uint8_t *random) {
    if (ctx->state != SMP_PK_SENT) {
        smp_send_pairing_failed(ctx, SMP_ERR_INVALID_SEQ);
        return;
    }
    smp_send_confirm(ctx);
    ...
}
```

PoC 工具：`pairing_random_before_pairing_public_key.py`，单文件 < 100 行，用 `l2cap_send` 注入。

### 修复

```c
// 1. SDK 升级 v1.4.0 → v1.5.2
// 2. 应用层加固：限制每个设备的配对失败重试次数
#define SMP_PAIRING_MAX_RETRY 3
static uint8_t s_retry_count[BLE_PEER_MAX] = {0};

void smp_pairing_complete(uint16_t conn_handle, uint8_t status) {
    if (status != 0) {
        if (++s_retry_count[conn_handle] >= SMP_PAIRING_MAX_RETRY) {
            // 拉黑 + 永久断开
            ble_gap_disconnect(conn_handle, 0x13);  // REMOTE USER TERM
            memcpy(blacklist, peer_addr, 6);
        }
    } else {
        s_retry_count[conn_handle] = 0;
    }
}
```

**临时缓解**（无 SDK 升级）：

```c
// 应用层：检测异常 Pairing Random 在 PK 之前的事件，直接断开
void smp_handler(uint16_t conn_handle, uint8_t event, void *data) {
    if (event == SMP_EVT_PAIRING_RANDOM &&
        !ctx->public_key_sent) {
        ble_gap_disconnect(conn_handle, 0x05);  // AUTH FAILURE
    }
}
```

### 复盘

- BLE 协议栈的安全实现必须严格遵循 Core Spec，**任何顺序错位都是安全漏洞**
- 配对流程中**任何一次失败都应有重试上限**，防止 DoS
- 采购芯片时关注厂商 SDK 的 CVE 历史，开源协议栈（Zephyr / NimBLE / Apache NimBLE）的修复更及时

### 来源

- _Inbox/BLE-2026-07-31-candidates.md 候选 1
- Realtek SDK 修复公告 2024-Q1
- CVE 待定

---

## 案例 1.5：Kali + Ubertooth 实战 Just Works 配对 MitM 攻击

### 现象

某 TWS 耳机厂出厂固件默认配对模式 = Just Works（IO Capability = NoInput/NoOutput）。安全团队在产线环境用 Kali Linux + Ubertooth One 复现：

- 任何攻击者手机都能在配对过程中拦截 LTK
- 重放加密帧成功，攻击者可解全部 GATT 流量
- OEM 私有的 OTA 命令被解码、签名被绕过

### 攻击链

```text
Step 1: Ubertooth 监听广播（37/38/39 信道跳频）
        → 拿到设备地址 + Service UUID
Step 2: 攻击者手机发起连接
        → 配对进入 Phase 1（Pairing Feature Exchange）
        → 两端 IO Capability 都是 NoInput → 协商为 Just Works
Step 3: 攻击者用 btlejack / gatttool 注入中间人 LL 层
        → 在 Phase 2 截获 TK（Just Works 时 TK = 0）
        → 解出 STK
        → 解出后续分发的 LTK / IRK / CSRK
Step 4: 用解出的 LTK 持续解密 GATT 流量
        → 重放 OTA 写命令 → 绕过签名校验（部分厂商签名校验位置在加密前）
```

### 定位

```text
防御端判断被攻击：
  1. HCI log 看 Pairing Feature 阶段，IO Capability 字段 = NoInput
  2. 看配对过程是否走了 LE Secure Connections（ECDH P-256）
     → 没走 → 用了 LE Legacy → TK 固定为 0
  3. 看 Phase 3 是否真发了加密后的 LTK
     → 发了但 TK=0 → 攻击者可解

抓包端复现工具链：
  - Ubertooth One 硬件（2.4GHz 监听 + 注入）
  - hostapd / btlejack / gatttool（Kali 自带）
  - Wireshark + btsnoop 解析 SMP PDU
```

### 修复

```text
固件侧（必须做）：
  1. 默认 IO Capability 改 DisplayYesNo + Numeric Comparison
     → 用户必须按键确认 6 位对比码，攻击者无法解出 STK
  2. 强制 LE Secure Connections（AuthReq SC 位 = 1）
     → 用 ECDH P-256 替代 TK + STK，TK 永远不进空中
  3. 配对过程加超时 + 失败计数
     → 失败 N 次拒绝该地址 5 分钟
  4. OTA 写命令签名验证放在加密链路**之外**做
     → 即使 LTK 泄漏，签名仍要防

产线测试侧（建议加）：
  1. 产测脚本里加「强制走 SC 配对」检查项
  2. 固件版本号禁止降级（防回滚到老 Just Works 固件）
  3. 量产烧录时写死 Secure Connections 标志位
```

### 复盘

- BLE 默认配对模式在「IoT/可穿戴 + 无屏」场景最容易踩 Just Works
- Just Works + LE Legacy = **等于明文**，任何用 Wireshark 的人都能解
- 修这个的成本很低：固件改两个字段就上 SC，**不需要硬件改动**
- TWS / 智能锁 / 健康设备三大类是重灾区

### 来源

- _Inbox/BLE-2026-08-02-candidates.md 候选 3
- BLE Core Spec 5.3 Vol 3 Part H Section 2.3（Just Works / Numeric Comparison）
- CVE-2023-XXXX（多品牌 TWS 耳机）

---

## 案例 2：BLE 0x3E 断开，信道拥塞

### 现象

产线 50 台设备同时上电，中央网关连接成功率 60%。失败的设备 Wireshark 抓包显示：

```text
CONNECT_REQ
LL_DATA (空)
DISCONNECT_COMPLETE: status=0x3E CONNECTION FAILED TO BE ESTABLISHED
```

### 抓包

nRF Sniffer 多信道扫描：

- 0x3E 集中发生在 2.4 GHz Wi-Fi 信道 1~6 重叠的 BLE 数据信道
- 失败集中在 peak time（早上 9 点、下午 2 点），Wi-Fi 高峰
- 成功连接后稳定不掉线 → 排除供电 / 硬件问题

### 定位

**0x3E CONN FAILED**：CONNECT_REQ 后第 5/6 步同步包丢失。

```text
CONNECT_REQ 步骤：
1. CONNECT_REQ 发出
2. 跳到 1st Connection Event（CONNECT_IND 指定信道）
3. 主从交换空包（同步）
4. 主从交换数据 PDU
5. 第 5/6 步同步包（master 端）未收到从机响应
6. 超时 → 0x3E
```

**根因**：

- 50 台设备同时 CONNECT_REQ 在同一信道（37/38/39）
- Wi-Fi 干扰下，第 5/6 步同步包被 Wi-Fi 帧淹没
- 步骤 5/6 是连接成功的关键，丢了就无法建立链路

### 修复

```c
// 1. 应用层：错峰发起连接
// 50 台设备，分 5 批，每批 10 台，间隔 1s
for (int i = 0; i < device_count; i++) {
    if (i % 10 == 0 && i > 0) {
        k_msleep(1000);  // 错峰
    }
    start_connect(device[i]);
}

// 2. 重试策略：失败后 backoff，指数退避
static int s_retry = 0;
void conn_failed(uint16_t conn_handle, uint8_t status) {
    if (status == 0x3E && s_retry < 3) {
        s_retry++;
        k_msleep(500 * (1 << s_retry));  // 1s, 2s, 4s
        start_connect(...);
    }
}

// 3. Channel Map：禁掉 Wi-Fi 密集信道
// 跳过 0~10（Wi-Fi 信道 1~6 重叠）
uint8_t channel_map[5] = {0x00, 0x7F, 0xFF, 0xF8, 0x1F};
// 信道 0~10 = 0, 信道 11~36 = 1
ble_gap_chan_map_set(channel_map);

// 4. 调连接参数：降低快速失败概率
ble_conn_param_t conn = {
    .interval_min = 50,  // 50ms，比 7.5ms 抗干扰强
    .interval_max = 70,
    .latency = 0,
    .timeout = 2000,     // 2s 监控
};
```

### 复盘

- **0x3E 80% 是 Wi-Fi 干扰**。先调 Channel Map + 错峰。
- **错误重试要用指数 backoff**，不要硬冲（加重拥塞）
- **CONNECT_IND 跳到指定信道时**，如果该信道是 Wi-Fi 热点就是赌博
- **高密度场景永远不要用 7.5ms 连接间隔**，间隔越短越脆弱

### 来源

- _Inbox/BLE-2026-07-31-candidates.md 候选 2
- BLE Core Spec Vol 6 Part B §4.5.1
- Wireshark + nRF Sniffer 实战

---

## 案例 3：nRF51 ADC 启停导致 BLE 链路失锁

### 现象

nRF51822 产品，电池供电，电池电压 3.0V。启用 ADC（AIN0 / AIN1）做温度采集，BLE 链路随机断连，断连率 ~5%。关闭 ADC 后正常。

### 抓包

```text
正常时：DISCONNECT_COMPLETE status=0x16 LOCAL HOST TERMINATED（应用层主动断）
异常时：DISCONNECT_COMPLETE status=0x08 CONNECTION TIMEOUT

Wireshark 解析：BLE 连接间隔 100ms，5 分钟后突然多个连续 anchor point 未应答
        → 监控超时 → 0x08
```

**关键证据**：在 ADC 启停瞬间示波器看晶振引脚：

```text
正常：32.768 kHz 晶振波形稳定
ADC 启瞬间：晶振引脚振幅下降 30%
         + 高频毛刺（~50 MHz 噪声）
```

### 定位

**nRF51 系列晶振走线坑**：

```text
晶振（32.768 kHz）走线经过 P0.26（AIN0）和 P0.27（AIN1）附近
ADC 启停瞬间：
  1. 内部多路开关切换 → 50 MHz 切换噪声耦合到晶振
  2. P0.26/27 ADC 采样保持电容充放电
  3. 晶振负载电容瞬间变化 → 频率偏移 ~ 80 ppm
  4. 频率超差 → 从机 anchor point 错过 → 监控超时
```

**关键参数**：nRF51822 数据手册 §5.4.1 提到：

> "ADC should not be used simultaneously with the 32.768 kHz crystal oscillator. Disable ADC when LFCLK is running."

但很多应用层工程师忽略这个。

### 修复

```c
// 修复 1：分时复用，ADC 采完关闭
void read_temperature(void) {
    NRF_ADC->ENABLE = 1;
    NRF_ADC->TASKS_START = 1;
    while (!NRF_ADC->EVENTS_END);
    uint16_t value = NRF_ADC->RESULT;
    NRF_ADC->ENABLE = 0;
    // ADC 关闭后再处理 BLE 事件
    ble_event_poll();
}

// 修复 2：改用内部温度传感器（nRF51 内部 TEMP）
// 不走外置 ADC，无 P0.26/27 冲突
NRF_TEMP->TASKS_START = 1;
while (!NRF_TEMP->EVENTS_DATARDY);
int8_t temp = NRF_TEMP->TEMP;

// 修复 3：硬件重新布局
// 晶振走线避开 ADC 通道
// 晶振加地屏蔽
// ADC 走线远离高频开关
```

### 复盘

- **晶振是模拟电路**，任何高频开关都要远离
- **nRF51 / nRF52 的 ADC 启停有内部耦合**，手册明确警告就要严格遵守
- **排障顺序**：外设逐一 enable → 看哪个触发问题 → 锁定 → 修复
- **温度传感器内部版（nRF 系列都有）** 优先级永远 > 外置 ADC 方案

### 来源

- _Inbox/BLE-2026-07-31-candidates.md 候选 4
- nRF51 实战复盘（cnblogs 案例）
- nRF51822 Product Spec §5.4.1

---

## 案例 4：Bonding Flash 残留导致配对反复失败

### 现象

设备出厂测试 OK，量产 1000 台后，售后返修 50 台。返修设备重新配对时配对失败，log 显示"Encryption Failed"。

### 抓包

```text
LL_START_ENC_REQ
LL_REJECT_INDIRECTED (status 0x06 LMP RESPONSE TIMEOUT / LL RESPONSE TIMEOUT)
```

HCI log：配对流程看似正常（Passkey Entry），但到 LL_START_ENC_REQ 时从机返回 REJECT。

### 定位

**flash 残留**：

```text
量产测试 → 工厂测试模式跳过 bonding → bonding 区域没初始化
销售 → 用户首次配对 → bonding 写入 fds 区域
售后退换 → 维修时 flash 擦除不全（仅擦 application）
        → bonding LTK 残留
新用户配对 → 新 LTK 与残留冲突 → 加密失败
```

**根因**：fds（Flash Data Storage）布局错：

```c
// 错：把 bonding 和 application 放在同一 page
#define FDS_PAGE_START  0x6F000   // page 111
#define APPLICATION_END 0x70000   // page 112
// 擦 application 时连带擦 fds

// 对：bonding 放独立 page，与 application 隔离
#define FDS_PAGE_START  0x6E000   // page 110
#define APPLICATION_END 0x6E000
```

### 修复

```c
// 修复 1：flash 布局调整（重编 bootloader + application）
// 修复 2：fds GC 策略：每次开机检查 fds 完整性
void fds_check(void) {
    ret_code_t err = fds_init();
    if (err != FDS_SUCCESS) {
        // fds 损坏 → 全清
        fds_uninit();
        nrf_fstorage_erase(&fds_default_config, NULL);
        NVIC_SystemReset();
    }
}

// 修复 3：bonding 数量上限
#define BONDING_MAX 8
// 满了 → FIFO 替换最早的一条
```

### 复盘

- **bonding flash 区域** 必须与 application 严格隔离
- **量产测试模式** 不应写入 bonding flash
- **开机检查 fds 完整性**，损坏自动清
- **配对失败不要立即重试**，先清旧 bonding 再配

---

## 案例 5：Notify 没启动导致应用收不到数据

### 现象

iOS App 显示"已连接"，但 App 端实时数据一直不刷新。Android 上正常。

### 抓包

Wireshark 解析 GATT：

```text
Server → Client: ATT Notification
Client → Server: (无)
```

iOS App：log 显示 "Characteristic notifications enabled" 但数据 0 字节。

### 定位

**CCCD 没写**：

```c
// iOS / Android 在连接成功后会自动写 CCCD
// 但 iOS 15+ 在某些 Service UUID 上不会自动写
// 需要在 didConnectToPeripheral 里手动写
- (void)peripheral:(CBPeripheral *)peripheral
   didDiscoverServices:(NSError *)error {
    for (CBService *s in peripheral.services) {
        for (CBCharacteristic *c in s.characteristics) {
            if (c.properties & CBCharacteristicPropertyNotify) {
                [peripheral setNotifyValue:YES forCharacteristic:c];
            }
        }
    }
}
```

但更深层：iOS 在某些情况下只写 `Indicate`（0x0002）不写 `Notify`（0x0001），而 server 端只发 Notification。

**最稳的修复**：

```c
// 1. Server 端同时支持 Notify 和 Indicate
// 2. 看到 CCCD=0x0001 发 Notify，CCCD=0x0002 发 Indicate
// 3. CCCD 状态切换时打印 log
static void cccd_write_handler(uint16_t conn_handle, uint8_t value) {
    if (value & 0x0001) {
        // Notify 启用
    } else if (value & 0x0002) {
        // Indicate 启用
    }
}
```

### 复盘

- **CCCD 是产线常见坑**，iOS / Android / Windows 三端默认行为不同
- **server 端同时支持 Notify + Indicate**，最稳
- **每个 CCCD 写入都打 log**，方便排障

---

## 案例 6：连接间隔 7.5ms + Slave Latency=0 烧电

### 现象

nRF52832 产品宣称"纽扣电池 CR2032 撑 2 年"，实测只能撑 3 个月。

### 抓 log

功率分析仪：

```text
连接间隔 7.5ms  → 平均电流 250 µA
连接间隔 100ms → 平均电流 30 µA
```

**根因**：连接间隔每 7.5ms 醒来一次收发，Radio + CPU 唤醒电流约 8 mA × 0.5ms = 4 µAs，加一起 250 µA 平均。

CR2032 容量 220 mAh：

```text
理论 220 / 0.250 / 24 / 365 = 100 天 ≈ 3 个月（吻合）
```

### 修复

```c
// 按场景分档
typedef enum {
    BLE_PROFILE_LOWPOWER,    // 1s interval, latency=4
    BLE_PROFILE_BALANCED,    // 100ms interval, latency=1
    BLE_PROFILE_HIGHPERF,    // 15ms interval, latency=0
} ble_profile_t;

// 选型
// 传感器/信标 → LOWPOWER
// 可穿戴/BLE 耳机控制 → BALANCED
// OTA/音频流 → HIGHPERF

ble_profile_t profile = BLE_PROFILE_LOWPOWER;
ble_conn_param_t conn = profile_to_param(profile);
```

### 复盘

- **7.5ms 间隔是 BLE 最小值**，不是默认值
- **功耗和延迟永远反向 trade-off**，明确应用场景
- **实测永远比理论算准**——功率分析仪 + 1-2 周 battery cycle test
- **"撑 2 年"是营销话术**，实测数据要写 datasheet

---

## 案例 7：HCI 错误码误读导致 0x3D MIC_FAILURE 排查方向错

### 现象

加密链路断开，log 显示 `BLE_HCI_STATUS_CODE_MIC_FAILURE (0x3D)`。工程师以为是 MIC 算法错，调试加密算法 3 天无果。

### 抓包

Wireshark 完整链路：

```text
LL_START_ENC_REQ
LL_START_ENC_RSP
LL_PAUSE_ENC_REQ
LL_REJECT_EXT (0x3D MIC_FAILURE)
```

LL 流程正常，MIC 是链路层 4 字节校验，**不是 SMP 层的加密 MIC**。

### 定位

**0x3D MIC_FAILURE 实际是 LL 层的 PDU 校验失败**，触发场景：

- 加密参数错（LTK / EDIV / Rand 不匹配）
- 时序错（启动加密前收到加密 PDU）
- 硬件链路错误（实际是数据损坏）— 罕见但可能是内存翻转

**根因**：bonding 信息残留，LTK 错位。3 天调试加密算法完全走错方向。

### 修复

```c
// MIC 失败排查顺序（按概率）
// 1. bonding 残留（80%）→ 清 fds
// 2. LTK 长度 / 格式错（10%）→ 检查配对参数
// 3. 加密启动时序错（5%）→ LL_START_ENC_REQ 流程
// 4. 硬件链路错（5%）→ 内存翻转 / RF 干扰

// 应用层：MIC 失败自动重置
void mic_failure_handler(void) {
    log("MIC failure, reset bonding");
    fds_clear_all();
    NVIC_SystemReset();
}
```

### 复盘

- **HCI 错误码是 LL 层还是 SMP 层，要看上层上下文**
- **MIC_FAILURE 第一反应是 bonding 残留**，不是加密算法
- **排障按概率，不按直觉**

---

## 案例 8：天线匹配差导致 BLE 距离仅 1m

### 现象

产品标称"10m 距离"，实测 1m 内就开始丢包。

### 抓 log

功率分析仪 + RSSI 监控：

```text
1m 处 RSSI  = -55 dBm
5m 处 RSSI  = -85 dBm（开始掉包）
10m 处 RSSI = -100 dBm（无连接）
```

**对比正常板**：

```text
1m 处 RSSI  = -40 dBm
10m 处 RSSI = -75 dBm（稳定）
30m 处 RSSI = -90 dBm（开始掉包）
```

差 15 dB！

### 抓波形

VNA 扫 S11：

```text
2.44 GHz 谐振点 → 实测 2.38 GHz（偏 60 MHz）
S11 = -6 dB（-10 dB 才是合格）
```

### 定位

**天线匹配网络算错**：

```text
参考设计：π 型匹配 (2pF + 0 ohm + 1.5pF)
实际物料：MLCC 选错，C0G 变 X7R
            → 容值漂移 ±15%
            → 谐振点偏移
            → 2.4 GHz 反射大
```

**额外问题**：PCB 走线下铺了地，违反"天线下方禁止铺地"原则。

### 修复

```text
1. 选 C0G / NP0 材质 MLCC（容值稳定）
2. 调谐天线匹配网络（实际谐振在 2.44 GHz）
3. 移除天线下方铺地（净空区 ≥ 5mm）
4. VNA 验证 S11 < -10 dB @ 2.44 GHz
```

### 复盘

- **天线是 BLE 设计第一坑**，参考设计不能照抄
- **MLCC 材质**：高频必选 C0G/NP0
- **净空区**：天线正下方禁铺地
- **VNA 验证**：每个频段量产前必做

---

## 案例 10：跨平台蓝牙协议栈差异（SM/L2CAP/GAP 三大雷区）

### 现象

某心率带项目（nRF52832 + Nordic S140 SoftDevice）量产发现：
- 三星 S21 偶发 "Reason 5"（0x05 AUTHENTICATION_FAILURE）连接失败
- iPhone 13 偶发连接成功 30s 后突然断链
- 小米 11 / 华为 P40 永远扫不到设备广播

### 抓包

```text
三星 Reason 5 复现：
  nRF Sniffer 抓 → 配对 Phase 2 STK 协商失败
  对比 Apple/Google 协议栈日志：
    Nordic 默认走 LE Legacy 配对
    Samsung 自研协议栈强制 LE Secure Connections
    两端协商机制不一致 → 0x05

iPhone 断链：
  nRF Sniffer 抓 → 30s 后 L2CAP Credit-Based Channel 信令出现
  Apple 协议栈发 ECFC Request（Enhanced Credit Flow Control）
  Nordic S140 v5.x 收到未知 L2CAP 信令 → 直接断链
  Wireshark 解码：APP 帧 "unknown signaling command" 0x09
  修复：nRF SDK 升级到 v7.x（含 L2CAP ECFC 支持）

小米/华为搜不到：
  广播数据：Flags = 0x06（LE General Discoverable + BR/EDR not supported）
  按规范应该 = 0x1F？实测：
    0x06 = 0b00000110 → 缺 Bit2 (BR/EDR not supported) 错位
    Android 部分机型强制要求 Bit2 (Bit5 of Flags AD type 0x01) = 1
    缺这个 bit → Android 标为 non-discoverable → 不进扫描结果
  正确值：0x1F（LE General Discoverable + BR/EDR not supported + SIMUL）
  Apple 兼容任意 Flags，Android 严格按位检查
```

### 定位

```text
Step 1: 用 5 个平台（iOS / 三星 / 小米 / 华为 / Pixel）逐个连设备
Step 2: nRF Sniffer 抓空口，看配对 / L2CAP / 广播三段流程
Step 3: 对比标准 Spec Vol 3 Part C / Part G 找差异点
Step 4: 锁定 3 个差异：
        - Samsung 强制 LE-SC vs Nordic LE-Legacy
        - Apple L2CAP ECFC vs Nordic 未知信令
        - Android Flags Bit5 强制要求
```

### 修复

```text
固件侧（必须做）：
  1. 配对：双模式兼容，强制 LE-SC + Legacy 回退
     #define BLE_PAIRING_MODE_LEGACY_ONLY  0
     #define BLE_PAIRING_MODE_SC_ONLY       1
     #define BLE_PAIRING_MODE_SC_LEGACY     2  ← 推荐
     
     if (peer_supports_sc) {
         use_sc_mode();
     } else {
         use_legacy_mode();
     }
  
  2. L2CAP：未知信令不能断链，必须 Command Reject
     L2capSignalCommandReject(0x0000)  // 0x0000 = reject all unknown
     → 设备保持连接，对端超时后自然断
     
  3. 广播 Flags = 0x1F（不是 0x06）
     // 0x1F = 0b00011111 = LE General + BR/EDR not + LE only + SIMUL
     adv_data[0] = 0x1F;

  4. 配对参数 AuthReq 全部置位（Bonding + MITM + SC + Keypress）

产线侧（必须做）：
  1. 跨平台测试矩阵：iOS + 三星 + 小米 + 华为 + Pixel + OPPO + VIVO
  2. 每平台过完整配对 + 一次断连 + 重连流程
  3. 自动跑脚本，失败直接标红
  4. 不允许"只在 iOS 上能连就出货"
```

### 复盘

- BLE 标准"理论上通用"——实际各厂商协议栈实现差异巨大
- 同一份固件在 iOS 上完美，可能在 Android / Samsung / Huawei 上完全不工作
- **跨平台测试矩阵是 BLE 产线必修**——不是可选项
- 配对 / L2CAP / 广播三个层面都可能踩雷，每个层都要测
- 跟 OEM 协议栈有 bug 时，要么改固件绕开，要么打 vendor patch（但要等几个月）

### 来源

- _Inbox/BLE-2026-08-07-candidates.md 候选 3
- Nordic DevZone 论坛
- Android Bluetooth CTS 测试报告

---

## 案例 11：Zephyr 绑定被静默覆盖（IoT 安全风险）

### 现象

某 Zephyr 1.14 智能锁项目（外设 + 手机中心模式）：

- 外设已和手机 A 绑定
- 手机 B 首次连接，**未发起配对**直接发 "Clear All Bonds" 命令
- 手机 B 发起安全配对，**无任何用户交互**就成功
- 绑定关系从手机 A 被静默覆盖到手机 B

### 抓包

```text
原始流程（Zephyr v1.14）：
  1. 手机 A 已在绑定列表
  2. 手机 B 连接
  3. 手机 B 发送 SMP 命令 "Security Request" 但不指定 LTK
  4. 外设回应 SMP "Pairing Request"，reason = 0x03 (No Bonding / Re-pair)
  5. Zephyr 协议栈自动删除手机 A 的旧绑定
  6. 走 Just Works 配对 → 新 LTK 分发 → 绑定到手机 B
  7. 手机 A 下次连接发现绑定丢失 → 需重新配对

Zephyr 内部逻辑（issue #24086 复现）：
  - bt_smp.c smp_pairing() 收到 Security Request
  - if (existing_bond) {
      // 旧版本：直接 delete + 走 LE-SC
      // 新版本：先校验 peer 身份，再决定是否覆盖
    }
  - 旧版本没有"身份校验"步骤 → 任何中心都能覆盖
```

### 定位

```text
1. 复现：手机 A 已绑定 → 手机 B 连接（无任何用户操作）→ 绑定覆盖
2. 抓 SMP 流程：旧绑定被无感删除，新绑定无用户确认
3. 查 Zephyr GitHub Issues：#24086 标记为 "Security: high" → 已修复
4. 修复 commit 引入配置：BT_SMP_ALLOW_UNAUTH_OVERWRITE
5. 升级到 Zephyr 2.6+ 后该配置默认 0（拒绝覆盖）
```

### 修复

```text
固件侧（必须做）：
  1. 升级 Zephyr ≥ 2.6（或 cherry-pick 修复 commit）
  2. 配置确认：
     CONFIG_BT_SMP=y
     CONFIG_BT_SMP_ALLOW_UNAUTH_OVERWRITE=n  ← 关键
  3. 业务层加固：
     - 收到 Security Request 时检查 peer 是新设备还是已绑定设备
     - 已绑定设备直接拒绝，重新发需要用户按钮确认
     - 新设备必须 App 端弹"是否覆盖绑定"对话框
  4. 配对过程加物理按钮触发（不能纯 BLE 触发）
  5. 配对超过 5 次失败 → 锁定 5 分钟，防暴力配对

产线侧（必须做）：
  1. 固件烧录检查：grep CONFIG_BT_SMP_ALLOW_UNAUTH_OVERWRITE 必须是 =n
  2. 出货前跑"绑定覆盖"复现测试
  3. 用户文档：明确说明"绑定覆盖需要 App 二次确认 + 物理按钮"
  4. OTA 升级：旧版本固件发公告通知升级（不能留老漏洞）

业务侧（产品设计）：
  1. 智能锁 / 支付类设备**绝对不允许**绑定被静默覆盖
  2. 配对流程必须：手机 App 主动 + 物理按钮 + 用户在 App 上确认
  3. "一键换绑"是产品需求，但必须显式操作
```

### 复盘

- 蓝牙绑定机制有"跨设备覆盖"风险，是 **IoT 安全盲区**
- Zephyr 1.14 之前没有"身份校验 + 用户确认"步骤 → 任何中心都能覆盖
- **默认安全策略 = 拒绝覆盖**（"secure by default"），不是反过来
- IoT 设备出货前必须做"绑定覆盖"安全测试，不能只测功能
- 配对流程不能纯软件触发，必须有物理按钮辅助

### 来源

- _Inbox/BLE-2026-08-07-candidates.md 候选 5
- Zephyr issue #24086（已修复）
- Bluetooth Core Spec 5.3 Vol 3 Part H Section 2.3.5

---

## 案例 12：RTL8762 配对失败 7 项 SM 配置错误表

### 现象

某 Realtek RTL8762 量产 BLE 模组，产线反馈三类故障高发：

1. 配对请求无响应（手机发起配对，模组静默忽略）
2. 连接立即断（配对完成到连接断开 < 2s）
3. 绑定写 NVDS 失败（重启后绑定丢失，重复配对）

### 抓包 / 诊断路径图

```text
手机发起配对 → 模组收到 SMP_PAIRING_REQ
                ↓
            模组检查 SM 配置
                ↓
        ┌───────┴───────┐
        ↓               ↓
    配置正确          配置错误
        ↓               ↓
    正常进入配对      无响应 / 立即断 / 绑定失败
```

### 定位（7 项 SM 配置错误表）

| # | 错误配置 | 现象 | 修复 |
| --- | --- | --- | --- |
| 1 | Security Level = 0 (No Security) | 配对请求被忽略 | 改为 Level 2 或 Level 4 |
| 2 | IO Capability = NoInput/NoOutput + Just Works | 配对成功但易被 MitM | 改 DisplayYesNo + Numeric Comparison |
| 3 | MITM Flag = 0 | 配对期间无中间人保护 | 置 1（除非强制 Just Works） |
| 4 | Key Distribution 缺 IRK | 绑定后 Privacy 失效 | 4 个 Key 全发：LTK + IRK + CSRK + EDIV+Rand |
| 5 | NVDS 写失败（BD_ADDR 校验错） | 绑定信息丢失 | 校验 NVDS BD_ADDR = 实际 MAC |
| 6 | SMP 事件回调只注册 1 个 | 4 个关键事件缺回调 | 必须注册 PAIRING_REQ / PAIRING_RSP / ENC_CHANGE / BOND_MODIFY |
| 7 | Bonding 容量 < 5 | 绑定满后新绑定覆盖 | 改 nvds_bond_max = 8（典型） |

### 修复

```c
// RTL8762 正确配对初始化（生产模板）
void smp_init(void) {
    // 1. Security Level：Level 2（加密 + 认证）
    gap_set_security_level(2);
    
    // 2. IO Capability：DisplayYesNo（支持 Numeric Comparison）
    gap_set_io_cap(GAP_IO_CAP_DISPLAY_YES_NO);
    
    // 3. AuthReq：Bonding + MITM + SC 全开
    gap_set_auth_req(GAP_AUTH_BOND | GAP_AUTH_MITM | GAP_AUTH_SC);
    
    // 4. Key Distribution：4 个 Key 全发
    gap_set_key_distribution(
        GAP_KDIST_ENCKEY |     // LTK
        GAP_KDIST_IDKEY |      // IRK
        GAP_KDIST_SIGNKEY |    // CSRK
        GAP_KDIST_LINKKEY      // EDIV + Rand
    );
    
    // 5. NVDS BD_ADDR 校验
    uint8_t nvds_mac[6];
    nvds_get_bd_addr(nvds_mac);
    if (memcmp(nvds_mac, get_actual_mac(), 6) != 0) {
        nvds_set_bd_addr(get_actual_mac());
        nvds_commit();
    }
    
    // 6. 注册 4 个 SMP 事件回调
    smp_register_callback(SMP_EVT_PAIRING_REQ,    on_pairing_req);
    smp_register_callback(SMP_EVT_PAIRING_RSP,    on_pairing_rsp);
    smp_register_callback(SMP_EVT_ENC_CHANGE,     on_enc_change);
    smp_register_callback(SMP_EVT_BOND_MODIFY,    on_bond_modify);
    
    // 7. 绑定容量
    nvds_set_bond_max(8);  // ≥ 5，避免满了被覆盖
}
```

### 复盘

- RTL8762 量产坑 90% 是 **SM 配置没初始化**或初始化不完整
- 7 项配置任何一项错都会触发一类故障——**必须全对**才工作
- 产线测试脚本要包含"配对 + 绑定 + 重连"完整流程
- Realtek SDK 默认值不一定对所有场景，**需要逐项确认**
- 烧录后 100% 跑配对 + 绑定持久化测试（断电 1 分钟看 NVDS 能否恢复）

### 来源

- _Inbox/BLE-2026-08-09-candidates.md 候选 1
- Realtek SDK 量产 FAQ
- CSDN 高赞答案（RTL8762 配对诊断）

---

## 案例 13：CC2340R5 换芯片变体（32KB→64KB）ICall abort 调试

### 现象

TI CC2340R53（64KB RAM）替换 R52（32KB RAM）量产：

- 旧 SDK 8.10 的 linker 文件不适用 64KB 部件
- BLE 初始化卡在 ICall abort()，无错误码
- 同样固件在 EVM 板正常，定制板异常

### 抓包 / 调试路径

```text
症状：
  1. 上电后串口输出 "ICall abort: 0x40, 0x08"
  2. 不进入 BLE 任务（gap_init 后续全部跳过）
  3. Wireshark / sniffer 看不到任何广播

EVM 板 vs 定制板对比：
  EVM（TI LaunchPad）：固件运行 ✅
  定制板：固件挂起 ❌
  差异：定制板用了 PCB 天线（非陶瓷天线）
  差异：定制板无外部 32 kHz 晶振（用内部 RC）

TI 官方工程师回复（Case 200496）：
  - 32KB→64KB 变体必须迁移 SDK 8.40
  - SDK 8.10 linker 文件假设 32KB RAM 布局
  - 64KB 部件堆栈 / .bss 段位置不同
  - 旧 SDK 跑在新硬件上 → 堆栈溢出 → ICall abort
```

### 定位（4 步）

```text
Step 1：复现
  - 烧固件 → 重启 → 看串口 log
  - 必有 ICall abort 错误码

Step 2：假设
  - 假设 1：linker 文件不匹配
  - 假设 2：硬件差异（PCB 天线 / 无 32 kHz 晶振）
  - 假设 3：固件版本不对

Step 3：验证
  - 把 EVM 板的 32 kHz 晶振拆到定制板 → 仍异常
  - 排除假设 2
  - 改用 EVM 板的 PCB 天线 → 仍异常
  - 排除假设 2 完全
  - 升级到 SDK 8.40 → 异常消失 ✅
  - 确认假设 1

Step 4：固化
  - linker 文件改成 R53 专用（cc23x0r53.cmd）
  - 工具链：CCS / IAR 都需同步
  - 加 RAM 大小检查宏：assert(RAM_SIZE == 65536)
```

### 修复

```c
// 1. 升级 SDK：simplelink_cc23xx_sdk_8_40_xx_xx
// 2. 选对 linker：
//    cc23x0r5x.cmd（R5x 系列通用）
//    cc23x0r53.cmd（R53 专用，含 64KB RAM 布局）
// 3. 工具链配置：CCS → Project Properties → ARM Linker → Basic Options
// 4. 运行时检查：
void assert_ram_size(void) {
    extern uint32_t __ram_size;
    assert(__ram_size == 65536);  // R53 = 64KB
}
```

### 复盘

- **芯片变体（RAM/ROM 容量）必须配套迁移 linker / SDK**——这是 TI 工程师亲口回复
- EVM 板正常 ≠ 定制板正常（天线 / RF 布局 / 晶振都可能是坑）
- TI 官方支持流程：复现 → 假设 → 验证 → SDK 升级，是标准路径
- 量产前必须做"芯片变体全矩阵"测试（不能只看一个型号）
- linker / SDK / 工具链 三件套必须同步升级

### 来源

- _Inbox/BLE-2026-08-15-candidates.md 候选 3
- TI E2E Forum Case 200496
- TI CC2340R5x datasheet

---

## 案例 14：工业 BLE 现场 "lab 跑得好 / 现场掉链"——best-effort 调度被 RF 打穿

### 现象

工业 / 医疗 / 机器人 BLE 设备在实验室跑 100% 通过，**到现场后延迟抖动、莫名断连**。

### 抓包 / 数据

```text
现场实测（德国 DEWINE Labs 工业 BLE 报告）：
  - 实验室 P50 延迟 = 5ms，P99 延迟 = 12ms
  - 工业现场 P50 延迟 = 8ms，P99 延迟 = 80ms+
  - P99/P50 比：实验室 2.4x，现场 10x+
  - 现场掉线率 = 1.5%/小时

团队误归因：
  - 60% 团队：天线问题 → 换天线没解决
  - 30% 团队：PCB 阻抗 → 改 layout 没解决
  - 10% 团队：固件调度 → **正解**
```

### 定位

```text
三个真实原因（按概率降序）：

1. 实验室 RF 环境 vs 现场 RF 环境
   - 实验室：仅 1-2 个 Wi-Fi AP + 1-2 个 BLE 设备
   - 现场：20+ Wi-Fi AP + 50+ BLE 设备 + 工业 2.4GHz 噪声（电机 / 变频器）
   - 跳频图谱完全不同

2. 平均延迟掩盖 P99 抖动
   - 团队看 P50 延迟 = 5ms 觉得 OK
   - 但 P99 = 80ms 在实时控制场景下断链
   - 必须看 P99 / Pmax，不能只看 P50

3. best-effort 调度被真实 RF 打穿
   - 固件用 RTOS 默认调度（优先级 + 时间片）
   - RF 拥塞 → MAC 重传 → 占用 CPU 时间片
   - 关键 GATT 操作被延迟
```

### 修复

```text
固件侧（必须做）：
  1. 测量 P99 延迟，不要只看 P50
     - 在现场跑 24h 收集 P99 / Pmax
     - 阈值：P99 < 30ms（实时）/ < 100ms（一般）
     
  2. 关键 GATT 操作用专用任务 + 高优先级
     - 不和连接管理任务共用时间片
     - 优先级分层：GAP / GATT / Scan / Adv 分开
     
  3. RF 拥塞感知
     - 监测连接事件成功率（CEV）
     - CEV < 90% → 主动断开 + 重连（换信道）
     - CEV < 70% → 报警（现场 RF 环境异常）
     
  4. 应用层重发 + 业务幂等
     - 重要数据发送 3 次
     - 接收端去重（timestamp + seq）

测试侧（必须做）：
  1. 不在实验室测 RF 拥堵
     - 用 Wi-Fi + 蓝牙干扰器模拟
     - 或到现场拿真实环境测
     
  2. 自动化 24h 抖动测试
     - 跑 1000 次 GATT 写，读 P99 / Pmax
     - 不只看平均成功率
     
  3. 多设备并行测试
     - 50+ BLE 设备同时连 1 个中心
     - 看 CEV 下降曲线
```

### 复盘

- **实验室测试无法复现现场 RF 拥堵**——必须现场测或干扰器模拟
- **平均延迟掩盖 P99 抖动**——必须看 P99 / Pmax
- 多数团队**误归因天线 / PCB**，实际是固件调度问题
- 工业 BLE 部署"lab 跑得好现场掉链" = best-effort 调度被真实 RF 打穿
- 关键 GATT 操作必须专用任务 + 高优先级，不能和连接管理共享

### 来源

- _Inbox/BLE-2026-08-20-candidates.md 候选 1
- DEWINE Labs 工业 BLE blog
- Nordic DevZone 工业 BLE 部署经验

---

## 案例 15：Nordic DTM 产线筛片（10 万级日产能）

### 现象

某可穿戴产线日产能 10 万级，传统功能测试 30s/工位太慢。

### 抓包 / DTM 简介

```text
DTM（Direct Test Mode）= BLE SIG 认证的强制 RF 测试模式
  - 发送连续 PN9 序列（伪随机码）
  - 接收 PER（Packet Error Rate）
  - 不需要建链（最简 RF 通路测试）

Nordic DTM 工具链：
  - 2 块 nRF51 DK（或 nRF52 DK）
  - 一块当 Tx，一块当 Rx
  - 屏蔽盒隔离外部干扰
  - 同轴衰减器模拟 -50dBm 接收
  - UART 串口控制 Tx → 自动跑 PER

实测（DTM vs 功能测试）：
  - 功能测试：30s/工位（建链 + 服务发现 + 读写）
  - DTM 筛片：5s/工位（Tx + Rx 5s PER）
  - 日产能：10 万级（2 工位并行）
  - 筛片 ≠ 功能测试：只查 RF 性能 + 可启动
    - 冷焊
    - 物料贴错（晶振 / 匹配网络）
    - RF 性能（PER < 1%）
```

### 修复（产线 DTM 部署）

```text
硬件：
  - 屏蔽盒（10x10x10 cm 即可）
  - 2 块 nRF51/52 DK
  - 同轴衰减器（30-50 dB）
  - 自动化治具（机械臂 / 推杆）

固件：
  - nRF51/52 烧入 DTM 固件（Nordic SDK 自带）
  - 上电自动跑 PER 测试
  - UART 输出 pass/fail
  - 失败 = 拒收，不进功能测试工位

扩展（多工位并行）：
  - 2 块 DK 扩 N 工位
  - 每工位 5s
  - 10 工位 = 50s 测试 10 个 = 5s/个（极限）
```

### 复盘

- DTM 是 BLE SIG 强制认证环节，**Nordic SDK 自带 DTM 固件**直接复用
- 筛片 ≠ 功能测试，只查 RF + 可启动
- 日产能 10 万级 = 2 工位并行 + 5s/工位
- 屏蔽盒 + 同轴衰减器是产线 RF 测试标配
- DTM 失败 = 拒收，不进功能测试 = 节省 30s/工位 × 10 万 = 833 工时/天

### 来源

- _Inbox/BLE-2026-08-20-candidates.md 候选 2
- Nordic DevZone Blog "Fast Production Screening"
- Bluetooth Core Spec Vol 6 Part F (DTM)

---

## 案例 16：Goodix GR551x/5525/5526 私有错误码 + GPIO Diagnostic 抓信号

### 现象

国产 BLE 模组（Goodix GR551x/5525/5526）量产断连问题：

- 标准 Spec 错误码（0x08/0x22/0x3D 等）无法直接定位
- 模组内部还有一层私有错误码（0x98/0xB8/0xB2/0xA3/0xCD）
- 必须用 GPIO Diagnostic + 中断钩子抓基带信号

### 抓包 / 私有码映射

```text
Goodix 私有错误码映射（GR551x 系列）：

| Spec 错误码 | Goodix 私有码 | 含义       | 排查方向               |
| --- | --- | --- | --- |
| 0x08 / 0x28 | 0x98          | 超时       | 先查射频再查中断         |
| 0x22        | 0xB2          | LL 响应超时 | 调度不同步，看 ISR/start |
| 0x13        | 0xA3          | 远端断     | 配对加密中插 LLCP        |
| 0x3D        | 0xCD          | MIC 失败   | 配对加密中插 LLCP 是根因 |

两根定位信号（GPIO 钩子）：
  1. GPIO_RF_ACTIVE：高电平 = RF 工作
     → 看 RF 实际工作时间 vs 协议时间
     → 偏差 > 10% = RF 链路异常
     
  2. GPIO_LLCP_PENDING：高电平 = LLCP 在等
     → 看 LLCP 等待时长
     → 等待 > 100ms = 调度卡死
```

### 定位（3 步）

```text
Step 1：0x98（超时）排查
  - 量 GPIO_RF_ACTIVE：低电平占空比 > 50% → RF 链路问题
    → 查天线 / PCB / 晶振
  - 量 GPIO_RF_ACTIVE：高电平占空比正常 → 中断问题
    → 查优先级 / ISR 时长

Step 2：0xB2（指令错过）排查
  - 抓 ISR 触发时序：1ms 周期
  - 如果 start 命令和 ISR 撞期 → 调度不同步
  - 修复：start 命令挪到 ISR 之后

Step 3：0xCD（加密失败）排查
  - 配对加密中插 LLCP 命令 → 加密链路被打断
  - MIC 校验失败 → 0xCD
  - 修复：LLCP 命令延后到加密完成之后
```

### 修复

```c
// Goodix 模组 SDK 钩子（伪代码）
// 1. GPIO 初始化
void hal_gpio_diag_init(void) {
    GPIO_SetPin(GPIO_RF_ACTIVE);
    GPIO_SetPin(GPIO_LLCP_PENDING);
}

// 2. 调度错位修复
void schedule_llcp_after_enc(void) {
    if (encryption_state == COMPLETE) {
        // LLCP 命令排队
        llcp_queue_send(...);
    } else {
        // 等待加密完成
        llcp_queue_defer(...);
    }
}
```

### 复盘

- 国产模组有**私有错误码**（GR551x/Realtek 等都有）——产线文档必须熟读
- GPIO Diagnostic + 中断钩子 = 国产模组定位标配
- 0x98 / 0xB2 / 0xCD 三件套覆盖 80% 国产 BLE 产线问题
- **配对加密中插 LLCP** 是国产模组常见 bug（Spec 允许但模组实现有 bug）
- 国产模组调试必须结合模组厂商 FAE，不能只看 Spec

### 来源

- _Inbox/BLE-2026-08-20-candidates.md 候选 4
- Goodix 官方开发者社区
- GR551x datasheet §15 Error Codes

---

## 案例 17：nRF52832 sd_power_system_off 间歇性 NRF_ERROR_NOT_SUPPORTED

### 现象

nRF52832 + S140 SoftDevice 项目，调 `sd_power_system_off()` 进入 System OFF：

- **间歇性**返回 `NRF_ERROR_NOT_SUPPORTED (0xFFFFFFFF)`
- 只有物理断电才能恢复
- 量产 1% 概率出现
- Nordic DevZone Case 200496

### 抓包 / 根因

```text
触发条件（按概率降序）：
  1. SPI DMA 未完成时进入 sleep
     - 之前启动的 SPI/I2S 传输还在 pending
     - SoftDevice 内部检查 → 返回错误
     
  2. I2S / PWM / TWI 任意外设未 uninit
     - 这些外设占用 EasyDMA
     - sleep 前必须 nrfx_*_uninit()
     
  3. Power Management 模块未 poll DMA
     - 默认 pm_handler 未注册
     - DMA 完成事件丢失

关键代码（错误模式）：
  void enter_sleep(void) {
      // ❌ 错：直接进 sleep
      sd_power_system_off();
      // 偶发 NRF_ERROR_NOT_SUPPORTED
  }
  
  void enter_sleep_correct(void) {
      // ✅ 对：先 uninit 所有外设
      nrfx_spi_uninit(&spi);
      nrfx_twi_uninit(&twi);
      nrfx_pwm_uninit(&pwm);
      nrfx_i2s_uninit(&i2s);
      
      // Power Management poll
      nrf_pwr_mgmt_run();
      
      // 再 sleep
      sd_power_system_off();
  }
```

### 定位（4 步）

```text
Step 1：复现
  - 跑 1000 次 sleep / wake
  - 记录失败次数
  - 通常 1/100 ~ 1/1000 概率

Step 2：加 log
  - 失败时打印哪些外设还在使用
  - 通常是 SPI 或 I2S 残留

Step 3：uninit 修复
  - sleep 前全部 uninit
  - 重新测试 1000 次
  - 失败率降到 0

Step 4：DMA 检查
  - 加 nrf_pwr_mgmt_run() poll
  - 处理 pending DMA 完成事件
```

### 复盘

- `sd_power_system_off()` 偶发 NRF_ERROR_NOT_SUPPORTED = **外设未 uninit + DMA 未 poll**
- 间歇性 bug 量产时**必踩**——1% 概率出厂 10 万台 = 1000 台返修
- sleep 前必须：uninit 所有外设 + nrf_pwr_mgmt_run() poll
- Power Management 模块默认未启，需要 app_pwr_mgmt_init() 初始化
- Nordic DevZone 200496 是官方答复，按流程做

### 来源

- _Inbox/BLE-2026-08-14-candidates.md 候选 2
- Nordic DevZone Case 200496
- nRF5 SDK Power Management 文档

---

## 案例 18：Nordic nRF52832 量产 OTA 工具链（micro-ecc + nrfutil + mergehex）

### 现象

nRF52832 量产 OTA 工具链踩坑：

- micro-ecc 编译不过（wchar_t 16/32 位不兼容）
- nrfutil 6.0.0a1 OTA 校验失败（必须 6.0.0）
- mergehex 工具版本错（合并后 SDID 错）
- nrfjprog 一次烧录不工作

### 抓包 / 工具链流程

```text
量产 OTA 工具链标准流程（6 步）：
  1. micro-ecc 编译 ECC 库
     - 用于 bootloader 验签
     - 编译：wchar_t 必须 16 位（IAR 默认）/ 32 位（Keil / GCC）
     - 切换编译器必须重新编译
     
  2. nrfutil keys generate 生成密钥对
     - private.pem + public.pem
     - 私钥保密（不在 git 提交）
     - 公钥烧入 bootloader
     
  3. nrfutil pkg generate 生成 DFU 包
     - 签名 + 压缩 + 校验
     - nrfutil ≥ 6.0.0（6.0.0a1 校验 bug）
     - 错误：6.0.0a1 → 切换 6.0.0
     
  4. mergehex 合并 hex
     - bootloader + softdevice + application
     - --sd-req 必须与 bootloader sd_config.h 一致
     - 不一致 → 升级失败
     
  5. nrfjprog 一次烧录
     - nrfjprog --program merged.hex --chiperase
     - 量产治具自动跑
     
  6. OTA 升级（产线 / 现场）
     - 手机 nRF Connect / nrfutil dfu ble
     - 校验签名 + 写入 + 校验
```

### 定位（4 个量产坑）

```text
坑 1：wchar_t 16/32 位
  - IAR 默认 16 位
  - Keil / GCC 默认 32 位
  - 切换工具链时 micro-ecc 编译必须重新做
  - 解决：CI 脚本里强制指定 -fshort-wchar

坑 2：nrfutil 版本
  - 6.0.0a1（alpha）OTA 校验失败
  - 6.0.0（稳定）正常
  - 解决：CI 锁定 nrfutil ≥ 6.0.0

坑 3：--sd-req 不一致
  - bootloader 烧入时 SDID = 0xAE
  - merged.hex 写 SDID = 0xB7
  - 升级时校验失败
  - 解决：mergehex 时显式指定 --sd-req 0xAE

坑 4：nrfjprog 一次烧录
  - 默认 nrfjprog --program 不擦除
  - 必须 --chiperase
  - 否则旧固件残留
```

### 修复（量产工具链脚本模板）

```bash
#!/bin/bash
# 1. 编译 micro-ecc
cd external/micro-ecc
make clean && make wchar=16
cd ../..

# 2. 编译 bootloader
cd examples/dfu/secure_bootloader
make
cd ../../..

# 3. 生成密钥
nrfutil keys generate private.pem
mv public.pem bootloader/bootloader-pub-key.pem

# 4. 编译 application
make -C examples/ble_peripheral/ble_app_hrs

# 5. 生成 DFU 包
nrfutil pkg generate \
  --hw-version 52 \
  --application-version 1 \
  --application examples/ble_peripheral/ble_app_hrs/armgcc/_build/nrf52832_xxaa.hex \
  --sd-req 0xAE \
  --key-file private.pem \
  app_dfu_package.zip

# 6. 合并 hex（量产用）
mergehex --merge \
  examples/dfu/secure_bootloader/armgcc/_build/nrf52832_xxaa_s132.hex \
  components/softdevice/s132/hex/s132_nrf52_6.1.1_softdevice.hex \
  examples/ble_peripheral/ble_app_hrs/armgcc/_build/nrf52832_xxaa.hex \
  --output merged.hex

# 7. 烧录（量产治具）
nrfjprog --program merged.hex --chiperase --verify
```

### 复盘

- Nordic 量产 OTA 工具链 = **micro-ecc + nrfutil + mergehex + nrfjprog** 四件套
- 版本必须严格锁定：nrfutil 6.0.0+ / SDID 一致 / --chiperase
- 切换工具链（IAR / Keil / GCC）必须重新编译 micro-ecc（wchar_t 差异）
- 量产治具烧录脚本**必须包含 --chiperase --verify**
- OTA 升级失败 90% = 签名 / 校验问题，先看 bootloader 公钥对不对

### 来源

- _Inbox/BLE-2026-08-14-candidates.md 候选 5
- Nordic 量产工具链实战（知乎）
- nrfutil GitHub releases

---

## 案例 19：Ellisys 抓包 + GATT 错误码 133/257 真实根因

### 现象

智能锁 + 医疗血压计两个 BLE 量产项目：

- 智能锁 OTA 在小米机型 20% 失败
- 医疗血压计华为 P50 首次连接成功率仅 60%
- 看 log 都是"GATT 失败"，具体根因不明

### 抓包（Ellisys 全栈解码）

```text
工具：Ellisys Bluetooth Tracker（USB 硬件 + 同步 2.4GHz 波形）
      Ellisys 能从 PHY 到 ATT/GATT 全栈解码 + 时间同步

智能锁 OTA 失败（小米机型）：
  正常 connectGatt → MTU 协商 = 185
  小米机型收到 OTA Write → 立即发 ATT Error Response
  Ellisys 解析 ATT PDU：
    - Error Code = 0x85 (INVALID_VALUE) / 0x85
    - 实际根因：transmitWindowOffset 超从设备能力
    - 从设备要求 transmitWindowOffset ≤ 15ms
    - 小米发 50ms → 设备拒
    → 改 transmitWindowOffset = 10ms

医疗血压计（华为 P50）：
  首次连接返回 GATT_FAILURE (0x85)
  Ellisys 解析：
    - 设备发 Connection Request
    - 华为 P50 立即回 LL_REJECT_IND
    - 原因码 0x13 (Reject due to Resources)
  实际根因：华为 P50 同时开 3 个 BLE 设备，资源耗尽
  → 等 200ms 再连 → 成功率 99%
```

### GATT 错误码 133/257 真实根因

```text
Android BluetoothGatt 错误码：
  133 (GATT_ERROR) = 上层 GATT 协议失败
    实际可能 = 0x85 / 0x0D / 0x06 / 0x08 等多个底层
    必须用 Ellisys 抓到具体 LL PDU 才能定位
    
  257 (GATT_AUTH_FAIL) = 鉴权失败
    实际可能 = bonding 残留 + 加密参数不匹配
    必须看 SMP 流程

实战对照表：
| Android 错误码 | 可能底层 | Ellisys 定位方法 |
| --- | --- | --- |
| 133         | LL_REJECT_IND 0x13 | 抓 LL 层 |
| 133         | ATT Error 0x85    | 抓 ATT PDU |
| 133         | transmitWindowOffset 超限 | 抓 Connection Request |
| 257         | 加密失败（SMP 阶段）| 抓 SMP 流程 |
| 0           | GATT 正常但业务失败 | 看 notify callback |
```

### 修复

```text
1. transmitWindowOffset 调整
   - 设备 spec：transmitWindowOffset ≤ 15ms
   - Android 默认 50ms → 改 10ms
   - 代码：BluetoothGattCallback.onConnectionStateChange
   - 反射 BluetoothGatt.refresh() 刷缓存

2. 多设备资源竞争
   - 业务逻辑：retry 3 次 + 200ms 延迟
   - 系统层：关掉其他 BLE 连接
   - 设备侧：错峰连接（不同时间窗）

3. 错误码 133/257 定位流程
   - 上 Ellisys 抓包（不是只看 log）
   - 解析 LL / ATT / SMP 三层 PDU
   - 对照 Core Spec 找根因
   - 不要只看 Android 上层错误码
```

### 复盘

- Android 错误码 133/257 = **上层封装**，实际根因必须 Ellisys 抓底层
- transmitWindowOffset 是小米 / 华为机型典型 bug 来源
- Ellisys = **专业级抓包工具**，破解 BLE 疑难杂症唯一可靠方案
- 量产必须配 Ellisys / nRF Sniffer，**不能只靠手机 log**
- Ellisys 还能看 2.4GHz 波形 = 同步判断 RF 链路质量

### 来源

- _Inbox/BLE-2026-08-12-candidates.md 候选 1
- _Inbox/BLE-2026-08-10-candidates.md 候选 1
- Ellisys Bluetooth Tracker 官方文档
- CSDN 实战博客

---

## 案例 20：SAMD21 + CircuitPython 小内存 MCU+BLE 内存预算模型

### 现象

SAMD21（Cortex-M0，32KB RAM）+ CircuitPython + BLE：

- 跑 BLE 服务偶发 MemoryError
- BLE 连接失踪
- 列表/字符串失控 → 内存碎片化

### 抓包 / 内存预算

```text
SAMD21 内存预算（典型 32KB RAM）：
  - CircuitPython 内核：~12KB
  - BLE 协议栈：~6KB
  - 业务代码：~4KB
  - 保留 buffer：~2KB
  - 合计：~24KB
  - 余量：8KB（25%）

常见踩坑（按内存压力降序）：
  1. .py vs .mpy
     - .py 源码加载到 RAM
     - .mpy 预编译字节码，体积小 30-50%
     - 大型项目必须 .mpy
     
  2. 列表 / 字符串增长
     - 业务 list.append() 不断增长
     - GC 触发不及时 → MemoryError
     - 修复：定期 list.clear() / del
     
  3. BLE notify 缓存
     - notify buffer 默认 4 个
     - 客户端不读 → 缓存满 → 写失败
     - 修复：客户端及时 read 或加流控
     
  4. import 模块过多
     - 每个 import 加载到 RAM
     - 大型项目 20+ import = 8KB+ 占用
     - 修复：拆分代码 + __init__.py 优化

REPL 实时监控：
  import gc
  gc.mem_free()  # 实时查可用内存
  gc.collect()    # 手动 GC
  import micropython
  micropython.mem_info()  # 详细内存分布
```

### 修复

```text
1. 全部用 .mpy（不是 .py）
   - 编译：circuitpython_tools/circup bundle-build
   - 项目下全部 .mpy

2. 内存监控
   - 启动后立即打 gc.mem_free()
   - 每 5 分钟打一次
   - 趋势分析

3. BLE notify 流控
   - 服务端检测 buffer 满 → 暂时停发
   - 客户端每次 read 后才能再 notify
   - 业务层加 ack 机制

4. N32L40X 联动（128KB RAM）
   - BareOS 平台：内存比 SAMD21 多 4 倍
   - 但业务规模也对应增长
   - 仍需 .mpy + 内存监控
   - 碎片化同样是 32-bit MCU 通病
```

### 复盘

- 32KB RAM 是 BLE 工程的"贫民线"——SAMD21 极小众
- **内存预算 = 8KB 余量是底线**，低于 4KB 必出问题
- `.mpy` 编译 + `gc.collect()` + 业务流控 = 3 件套
- N32L40X (128KB) / nRF52832 (64KB) 更宽松，但 SAMD21 经验可直接迁移
- BLE notify buffer 满是最常被忽略的内存杀手

### 来源

- _Inbox/BLE-2026-08-12-candidates.md 候选 3
- CircuitPython 官方文档
- Adafruit SAMD21 BLE 实战

---

## 案例 22：Android requestMtu 断连 + BluetoothGatt 缓存残留

### 现象

Android 主机端连接 GATT 后立即调 `requestMtu(512)`：

- 部分 Android 机型立即断链
- 重连时缓存残留
- log 报"MTU 失败 -100"

### 抓包

```text
手机-外设互通时序错（Android 端）：
  Step 1：connectGatt → onConnectionStateChange (STATE_CONNECTED)
  Step 2：❌ 直接 requestMtu(512) → 部分机型断链
  Step 3：cache 残留 → 下次 connect 立即失败
  
正确时序：
  Step 1：connectGatt
  Step 2：onConnectionStateChange (CONNECTED) → 缓存 callback
  Step 3：discoverServices() → onServicesDiscovered
  Step 4：requestMtu(512) → onMtuChanged
  Step 5：业务读写

错误时序（断链）：
  Step 1：connectGatt
  Step 2：onConnectionStateChange (CONNECTED) → 
  Step 3：❌ requestMtu(512) 立即调，部分机型 ATT 请求并发
  Step 4：底层 L2CAP 死锁 → 断链
```

### 修复

```java
// 1. 反射 refresh() 刷 GATT 缓存
private void refreshGatt(BluetoothGatt gatt) {
    try {
        Method refresh = gatt.getClass()
            .getMethod("refresh");
        if (refresh != null) {
            refresh.invoke(gatt);
        }
    } catch (Exception e) {
        Log.e("BLE", "refresh failed", e);
    }
}

// 2. 断开时降 MTU 100 退避重连
private void reconnectWithBackoff() {
    int mtu = 100;  // 降档
    if (mBluetoothGatt != null) {
        mBluetoothGatt.disconnect();
        mBluetoothGatt.close();
        mBluetoothGatt = null;
    }
    new Handler().postDelayed(() -> {
        scanAndConnect();
    }, 500);
}

// 3. 正确时序
private final BluetoothGattCallback mCallback = 
    new BluetoothGattCallback() {
    @Override
    public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
        if (newState == BluetoothProfile.STATE_CONNECTED) {
            // 等 200ms 再 discoverServices（避免与 MTU 冲突）
            new Handler().postDelayed(() -> {
                gatt.discoverServices();
            }, 200);
        }
    }
    
    @Override
    public void onServicesDiscovered(BluetoothGatt gatt, int status) {
        if (status == BluetoothGatt.GATT_SUCCESS) {
            // discoverServices 完成后再 MTU
            gatt.requestMtu(247);
        }
    }
    
    @Override
    public void onMtuChanged(BluetoothGatt gatt, int mtu, int status) {
        if (status == BluetoothGatt.GATT_SUCCESS) {
            // MTU 协商成功后业务读写
            doBusiness();
        }
    }
};
```

### 复盘

- Android MTU 时序错位是 50% BLE App 失败的根因
- **正确顺序**：onConnectionStateChange → 200ms 延迟 → discoverServices → onServicesDiscovered → requestMtu → onMtuChanged → 业务
- requestMtu 失败时**降档**（247 → 100 → 23），不能死循环
- `BluetoothGatt.refresh()` 是系统隐藏 API，**反射调用**刷缓存
- 缓存残留必须 disconnect + close + nullify 三件套清

### 来源

- _Inbox/BLE-2026-08-12-candidates.md 候选 5
- _Inbox/BLE-2026-08-14-candidates.md 候选 3
- 博客园 developer-wang 实战
- Android BluetoothGatt 源码

---

## 案例 23：华为 / 小米 / OPPO 机型 BLE GATT 平台碎片化

### 现象

国产 Android 机型（华为 / 小米 / OPPO / VIVO）BLE GATT 行为各异：

- 连接已建立、广播显示成功，但 `discoverServices()` 不回调
- 部分机型 `connectGatt` 不会真正建链
- discoverServices 跨线程调用不生效

### 抓包 / 平台差异表

```text
| 平台    | connectGatt 行为              | discoverServices 触发           | 缓存 |
| --- | --- | --- | --- |
| 华为   | 需要手动调 mBluetoothGatt.connect() | 必须在 connect() 回调里立即调 | 强 |
| 小米   | 自动建链                       | 必须等 onConnectionStateChange(STATE_CONNECTED) | 强 |
| OPPO  | 自动建链                       | 必须等 onConnectionStateChange(STATE_CONNECTED) | 中 |
| VIVO  | 自动建链                       | 必须等 onConnectionStateChange(STATE_CONNECTED) | 强 |
| 谷歌 Pixel | 自动建链                  | onServicesDiscovered 自动调 | 弱 |

华为特殊坑：
  - connectGatt() 返回成功
  - 但实际没建链
  - 必须手动调 mBluetoothGatt.connect() 触发真建链
  - 否则一直不回调 onConnectionStateChange(STATE_CONNECTED)
```

### 修复

```java
// 1. 华为专用：手动补一次 connect()
private void connectHuawei(BluetoothDevice device) {
    if (mBluetoothGatt == null) {
        mBluetoothGatt = device.connectGatt(this, false, mCallback);
    }
    // 关键：手动调一次 connect()
    mBluetoothGatt.connect();
}

// 2. 通用：discoverServices 必须在连接回调里
private final BluetoothGattCallback mCallback = 
    new BluetoothGattCallback() {
    @Override
    public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
        if (newState == BluetoothProfile.STATE_CONNECTED) {
            // 跨线程不行，必须连接回调里同步
            gatt.discoverServices();
        }
    }
};

// 3. 平台检测 + 差异化
private void connectSmart(BluetoothDevice device) {
    String manufacturer = Build.MANUFACTURER;
    if ("HUAWEI".equalsIgnoreCase(manufacturer)) {
        connectHuawei(device);
    } else {
        mBluetoothGatt = device.connectGatt(this, false, mCallback);
    }
}
```

### 复盘

- **国产手机 BLE GATT 平台碎片化严重**——必须做平台检测
- 华为需要手动 `mBluetoothGatt.connect()` 触发真建链（特殊坑）
- discoverServices **跨线程不行**（不同机型实现不同）
- 缓存：国产机缓存强，必须每次清
- 测试矩阵：iOS / Pixel / 华为 / 小米 / OPPO / VIVO 至少 5 平台

### 来源

- _Inbox/BLE-2026-08-15-candidates.md 候选 5
- CSDN 国产手机 BLE 实战
- Android 源码差异（华为 EMUI / 小米 MIUI）

---

## 案例 24：实时日志把 BLE 间歇性 bug 排查从天压到 10 分钟

### 现象

某 BLE 设备间歇性 bug：

- 现场偶发（5% 概率）
- 抓包困难：Wireshark 抓不到关键时刻
- 老排查方式：抓 log → 分析 → 改 → 重测（按天计）

### 抓包 / 实时日志方案

```text
实时日志（而非事后 log）：
  - 固件实时 RTT 输出（SEGGER RTT / 串口 1Mbps）
  - 关键事件打点：
    - 收到 LL_CONNECT_REQ
    - 收到 LL_DATA_PDU
    - 收到 ATT PDU
    - 收到 HCI Command
    - HCI Event
  - 每个事件带 timestamp（ms 级）
  - PC 端实时显示（PuTTY / 自定义 viewer）

10 分钟定位实战（dev.to 案例）：
  Step 1（1 min）：开实时日志
  Step 2（2 min）：复现 bug
  Step 3（3 min）：看日志时间线
  Step 4（2 min）：定位根因
  Step 5（2 min）：改 + 验证
  
vs 老排查方式：
  Step 1（1h）：抓 log
  Step 2（2h）：分析
  Step 3（1h）：改
  Step 4（1h）：重测
  = 5h/天/问题
```

### 实战坑

```text
坑 1：Write Without Response 丢包
  - 写命令不带 ACK
  - 协议栈 buffer 满 → 写失败
  - 关键：必须等 buffer 空再写
  - 老固件：直接发下一包 → 丢
  - 新固件：等 BLE_EVT_TX_COMPLETE

坑 2：连接参数被任一方拒绝
  - 任何一方拒绝 → 立即不稳
  - 0x3B 错误码
  - 老固件：直接 reject
  - 新固件：log reject reason + 重试

坑 3：多 Central 共享写顺序错乱
  - 2 个 Central 同时写同一 characteristic
  - 顺序错乱 → 状态损坏
  - 关键：加锁（互斥）
  - 老固件：无锁 → 数据错乱
  - 新固件：mutex + 顺序号
```

### 修复

```c
// 实时日志打点（SEGGER RTT）
void log_event(const char *event, uint32_t param) {
    SEGGER_RTT_printf(0, "[%u] %s: 0x%08X\n",
                       HAL_GetTick(), event, param);
}

// 关键事件都打点
void on_ble_evt(ble_evt_t *p_ble_evt) {
    log_event("BLE_EVT", p_ble_evt->header.evt_id);
    // ...
}
```

### 复盘

- **实时日志 = BLE 排查效率提升 10x**（5h → 30min）
- SEGGER RTT 不占用 UART，跑 1Mbps 不影响业务
- 关键事件打点是基础，每个 characteristic 操作都要打
- 多 Central 写顺序错乱是 5% 概率的真坑
- dev.to 实战案例：从"按天"压到"10 分钟"

### 来源

- _Inbox/BLE-2026-08-20-candidates.md 候选 3
- dev.to BLE 实战博客
- SEGGER RTT 文档

---

## 案例 25：ESP32-C3 + mDNS + WiFi coex 单芯片 30s 必断

### 现象

ESP32-C3 + NimBLE 量产手环：

- 连接稳定 30 秒后**准时**断
- HCI log 只显示 `disconnect reason 0x08 (CONNECTION TIMEOUT)`
- 重连后同样 30 秒
- 排查 2 天协议栈无果

### 抓包 / 根因

```text
抓包：nRF Sniffer 抓空中 PDU
  - 连接建立后 6 个 connection event 全 OK
  - 第 7 个 connection event miss
  - 之后连续 miss 到 supervision timeout
  - 30s 后必断（supervision = 30s）

根因（致命级别）：
  1. mDNS 周期性 announce
     - 同一片 ESP32-C3 跑 WiFi（OTA 用）
     - mDNS announce 占用 2.4 GHz 时隙
     - 抢占 BLE connection event 时隙
  2. ESP32 单 2.4 GHz 射频
     - WiFi + BLE 共存
     - 时隙分配：WiFi > mDNS > BLE
     - BLE 一直低优先级
  3. NimBLE HCI log 0x08
     - **log 不会告诉你 coex 争用**
     - 看起来是"超时"，实际是"时隙丢"
```

### 修复（3 件套）

```c
// 1. 调大 supervision timeout
esp_ble_gap_set_prefer_conn_params(0x18, 0x28, 0, 400, 0);  
// min = 30ms, max = 50ms, latency = 0, timeout = 4000ms

// 2. 调大连接间隔（50ms，避免 mDNS 抢）
esp_ble_gap_set_prefer_conn_params(0x32, 0x32, 0, 400, 0);
// 50ms 间隔，留出 50% 时隙给 mDNS

// 3. 配置 coex 偏好（关键）
#include "esp_coexist.h"
esp_coex_preference_set(ESP_COEX_PREFER_BT);
// 或 ESP_COEX_PREFER_BALANCED（不极致偏 BLE）

// 4. 关闭 mDNS（或减少频率）
// mDNS announce 间隔默认 1s
// 改 30s 一次（如果不需要频繁发现）
mdns_set_ttl(30);
```

### 复盘

- **ESP32 / nRF52840 / EFR32 单 2.4 GHz 芯片普遍问题**
- BLE log 0x08 不指向 coex
- 排查要查 WiFi / mDNS / 蓝牙经典 共存
- 单芯片 + 多 radio 必做 `esp_coex_preference_set(ESP_COEX_PREFER_BT)`
- 30s 准时断 = supervision 周期，coex 时隙丢的典型特征

### 来源

- _Inbox/BLE-2026-08-24-candidates.md 候选 2
- _Inbox/BLE-2026-08-25-candidates.md 候选 1
- _Inbox/BLE-2026-08-29-candidates.md 候选 4
- moltbook 工程师实战帖

---

## 案例 26：STM32 + nRF52840 外挂架构 3.2mA 假休眠（ISR 三不原则）

### 现象

手环项目：STM32 主控 + nRF52840 BLE 外挂（SPI）

- 理论功耗：5μA（电池续航 2 年）
- 实测功耗：3.2mA（电池续航 5 天）
- 600 倍差距

### 抓包 / 3 类异常模式

```text
模式 1：持续高平台
  现象：电流稳定在 1.5mA
  根因：CPU 睡了但 SPI / BLE_INT 还在工作
        → 实际是"假休眠"
  诊断：Keithley 2450 测静态电流
        → 应该 < 50μA，实测 1.5mA

模式 2：周期尖峰
  现象：每 60s 一个 18mA 脉冲（持续 100ms）
  根因：BLE 广播间隔 100ms × 11mA = 0.92mAh / 小时
        比预期 1.83μAh 高 500 倍
  诊断：TCP0030A 电流探头看波形

模式 3：长时唤醒
  现象：CPU 醒来 1.5s（不是预期的 200ms）
  根因：协议栈重传 + ISR 阻塞
  诊断：Saleae 抓 GPIO wake/sleep 时序
```

### 修复（ISR 三不原则 + 零拷贝缓冲）

```c
// ISR 三不原则：
//   1. 不打印日志（UART 慢、阻塞）
//   2. 不访问 SPI（与主线程竞争）
//   3. 不调阻塞 API（信号量、队列等）

// ❌ 错版：ISR 慢
void SPI1_IRQHandler(void) {
    LOG("SPI RX: 0x%02X\n", rx_byte);  // 不允许
    spi_tx(&main_spi, next_byte);         // 不允许
    xSemaphoreGiveFromISR(xSem, NULL);     // 不允许
}

// ✅ 对版：ISR 只 set flag
volatile bool spi_done = false;
void SPI1_IRQHandler(void) {
    spi_done = true;  // 1 行
}

// 主线程查 flag
while (!spi_done) {
    __WFE();  // 等待事件
}
process_spi_data();
```

### 零拷贝环形缓冲

```c
// 不用 malloc 分配包
// 静态环形缓冲复用
static uint8_t ring_buf[4096] __attribute__((aligned(4)));
static volatile uint16_t head = 0, tail = 0;

void spi_rx_put(uint8_t b) {
    ring_buf[head++ & 0xFFF] = b;
}
uint8_t spi_rx_get(void) {
    return ring_buf[tail++ & 0xFFF];
}
```

### 动态连接参数（3 档切换）

```c
// 3 档：活动档 / 平衡档 / 休眠档
typedef enum { BLE_ACTIVE, BLE_BALANCED, BLE_SLEEP } ble_mode_t;

void ble_set_mode(ble_mode_t mode) {
    switch (mode) {
        case BLE_ACTIVE:
            // 7.5ms interval, 0 latency, 50ms supervision
            update_conn_params(7, 7, 0, 50);
            break;
        case BLE_BALANCED:
            // 50ms interval, 4 latency, 500ms supervision
            update_conn_params(40, 80, 4, 500);
            break;
        case BLE_SLEEP:
            // 1s interval, 30 latency, 30s supervision
            update_conn_params(800, 1600, 30, 30000);
            break;
    }
}
```

### 实测效果

```text
原状态：3.2mA / 续航 5 天
优化后：2.08mA / 续航 35 天（-35%）
  - 持续高平台：1.5mA → 0.2mA（-87%）
  - 周期尖峰：18mA × 100ms → 18mA × 50ms（-50%）
  - 长时唤醒：1.5s → 800ms（-47%）
目标功耗：50μA（理论值）
仍差 40 倍 → 需进一步深度优化
```

### 复盘

- **"假休眠" = CPU 睡了但外设还在工作**——最隐蔽
- ISR 阻塞 1ms = 100μs × 10 = CPU 浪费巨大
- BLE 广播突发 vs 分散 = 3 条 180μs → 1 条 burst 80μs（-55%）
- Python + Monsoon 自动化测试平台 = 量产必备
- 连接参数保守区间 = 关键工程化

### 来源

- _Inbox/BLE-2026-08-24-candidates.md 候选 5
- _Inbox/BLE-2026-08-27-candidates.md 候选 3
- 夸智网长文（STM32 + nRF52840 案例）
- CSDN 实战

---

## 案例 27：CH582 沁恒国产 RISC-V+BLE 5.3 信标 1.2mA→5μA 排查全记录

### 现象

CH582（RISC-V + BLE 5.3）温湿度信标项目：

- 标称续航：6 个月
- 实测续航：**3 周**（差 7.5 倍）
- 国产 BLE MCU 真实量产坑

### 抓包 / 72h 排查全记录

```text
工具配置：
  - Keithley 2450 源表（μA 静态）
  - TCP0030A 电流探头
  - Saleae 16 通道逻辑分析仪

步骤 1（0-12h）：测基础功耗
  - 实测空闲：1.2mA（应 < 50μA）
  - 24 倍差距
  - 第一怀疑：DC-DC 不关

步骤 2（12-24h）：DC-DC 验证
  - 关闭 DC-DC 模式（LDO 模式）
  - 电流：1.2mA → 1.15mA（差距 50μA）
  - 第二怀疑：DEBUG 宏没关

步骤 3（24-36h）：DEBUG 宏
  - 关闭 DEBUG UART 输出
  - 电流：1.15mA → 0.8mA
  - 解决一部分
  - 第三怀疑：浮空 GPIO 漏电

步骤 4（36-48h）：浮空 GPIO
  - 38 个 GPIO 中发现 1 个浮空
  - 漏电 200μA（外加 ESD 二极管漏电）
  - 配置为 Analog + 下拉
  - 电流：0.8mA → 0.6mA

步骤 5（48-60h）：软件定时器
  - CH582 SDK 1 个软件定时器泄漏
  - 持续唤醒 CPU
  - 修复：禁用未用定时器
  - 电流：0.6mA → 50μA

步骤 6（60-72h）：验证
  - 24h 持续录波
  - 电流稳定 5μA
  - 续航：3 周 → 6 个月 ✅
```

### 3 漏电陷阱总结

```text
陷阱 1：DEBUG 宏 UART 活跃
  - 默认开启（开发友好）
  - 实际出货必须关闭
  - 漏电：~400μA
  - 修：DEBUG = 0 / 关 PB0 串口

陷阱 2：浮空 GPIO 单引脚漏电
  - 38 个 GPIO 中 1 个浮空
  - 漏电 200μA
  - 修：Analog 模式 + 下拉电阻
  - 警告：所有未用 GPIO 必显式配置

陷阱 3：软件定时器泄漏
  - SDK 1 个未用定时器
  - 持续触发唤醒
  - 漏电 50μA+
  - 修：禁用所有未用定时器
```

### 测量前置（必做）

```text
**测功耗前必断 J-Link**（否则测的是调试器电流）
  - J-Link 自身供电 30mA+
  - 任何测量都失效
  - 物理断开
  - 或用电池供电测试板
```

### 修复代码

```c
// 沁恒 CH582 出货配置模板
void ble_beacon_init_ship(void) {
    // 1. 关闭 DEBUG
    #undef DEBUG
    DEBUG_INIT();
    
    // 2. 配置所有 GPIO 为 Analog
    GPIOA_ModeCfg(GPIO_Pin_All, GPIO_ModeIN_Floating);
    GPIOB_ModeCfg(GPIO_Pin_All, GPIO_ModeIN_Floating);
    
    // 3. 关键 GPIO 显式下拉
    for (int i = 0; i < 38; i++) {
        if (i == BLE_ANT_PIN) continue;  // 保留天线
        if (i == LED_PIN) continue;       // 保留 LED
        GPIOA_ModeCfg(1 << i, GPIO_ModeIN_PD);
    }
    
    // 4. 禁用未用软件定时器
    TMR0_Disable();  // 未用
    TMR1_Disable();  // 未用
    
    // 5. 设置睡眠模式
    PWR_EnterSLEEP(PWR_ROM_CONSUMPTION_MODE);
    
    // 6. 验证电流
    // 应 < 50μA
}
```

### 复盘

- **国产 BLE MCU 跟 Nordic 一样有低功耗坑**——只是文档少
- CH582 是 RISC-V 内核 + BLE 5.3，国产替代 nRF51822 / nRF52832
- 72h 排查路径 = 量产标准 SOP
- 3 漏电陷阱 = **出货前 100% 测试**
- **测功耗前必断 J-Link**（最常被忽略）
- Keithley 2450 + TCP0030A = μA 级测试金标准

### 来源

- _Inbox/BLE-2026-08-27-candidates.md 候选 2
- CSDN 沁恒 CH582 实战
- 沁恒官方 SDK 文档

---

## 案例 28：STM32WB 0x02 BlueCore Time Overrun 部分单元良率坑

### 现象

STM32WB 量产项目，BLE Stack v1.11.0 + FUS v1.2.0：

- **同 PCB / 同固件**，5% 单元报 `HCI_HARDWARE_ERROR_EVENT (0x02)`
- BlueCore time overrun
- 良率 95%（不达标）

### 抓包 / 定位

```text
HCI 抓包：
  - 错误事件 0x02 = HCI_HARDWARE_ERROR_EVENT
  - 持续触发，每秒 1-2 次
  - 单元重启可恢复，但几分钟后复发
  - 只部分单元出问题

可能原因排查：
  1. HSE 精度：单元间晶振差异（±20 ppm 变 ±40 ppm）
  2. LSE 精度：32.768 kHz 晶振精度差
  3. RF 匹配：板级差异
  4. 电源纹波：单元间 PCB 差异
  5. 固件 bug：旧版本 SDK 已知问题

实测：
  - 升级到 BLE Stack v1.24.0 + FUS v2.2.0
  - 问题**消失**
  - 验证：100 台新固件，0 台报错 0x02
```

### 修复

```text
短期方案：
  1. 升级到 BLE Stack v1.24.0 + FUS v2.2.0
  2. 验证 100+ 单元
  3. 良率 95% → 100%

长期方案：
  1. 选型时优先最新稳定版固件
  2. 量产前跑 200+ 单元老化测试
  3. 旧固件不上量产
  4. 升级到 v1.24.0 后良率稳定

厂商建议：
  - STM32WB 文档明确 v1.11.0 有 BlueCore overrun 问题
  - v1.24.0 已修
  - 升级路径：FUS v2.2.0 + 重新烧录 stack
```

### 复盘

- **同 PCB / 同固件 / 部分单元出错 = 良率问题**
- 排查方向：HSE / LSE / RF 匹配 / 电源纹波 / **固件版本**
- BLE stack 大版本升级 = 量产良率直接 fix
- 选型时不能只看 datasheet，要看 release notes
- 量产前 200+ 单元老化测试 = 必做

### 来源

- _Inbox/BLE-2026-08-29-candidates.md 候选 3
- ST Community 实战
- STM32WB Release Notes

---

## 案例 29：Abbott FreeStyle Libre 3 FDA Warning Letter + 3M 召回（IoT 医疗验收教训）

### 现象

2025-10 FDA 检查 Abbott 厂 4 项 GMP 违规：

1. 未传精度
2. 无验收测试
3. 抽样无依据
4. release 未对齐

**关键指控**：FDA 警告信指 **BLE connectivity testing 替代了 glucose accuracy 测试**——意思是用 BLE 连通性测试**替代**了血糖精度测试，导致假低血糖读数（实际上血糖正常但设备报低）。

召回：3M Libre 3 / 3+ 设备
- 严重等级：Class I（FDA 最严重）
- 伤害：860 重伤 + 7 死
- 触发：传感器在体温变化时读数漂移

### 抓包 / 根因

```text
真问题不是 BLE 协议问题，是验收流程问题：

1. 设计 transfer 失守
   - 设计阶段 R&D 验证了 BLE connectivity ✅
   - 但**没**验证 glucose accuracy（传感器精度）
   - 设计 transfer 没把精度测试当必做项

2. 成品 acceptance 失守
   - 100% 验收 = BLE 连通 + 基本功能
   - 抽样验收 = 缺统计学依据
   - 抽样不包含温度变化场景

3. 统计抽样失守
   - n=10 抽样不够
   - 没覆盖全温区（-10°C ~ +50°C）
   - 没考虑身体部位（手臂 vs 腹部）

4. release 未对齐
   - 实际出货的固件 ≠ 验证过的固件
   - 后期 OTA 改了读数算法但没重做验收
```

### 修复（IoT 医疗验收 3 大原则）

```text
原则 1：设计 transfer 必须包含端到端精度测试
  - 不是 BLE 连通性 = 验收
  - 是传感器 + BLE + 应用 = 端到端精度
  - 21 CFR 862.1355（iCGM）要求：
    - 血糖读数误差 < 20%
    - 95% 读数在 ±15% 内
    - 99% 读数在 ±40% 内

原则 2：成品 acceptance 必须全温区
  - 低温 -10°C
  - 室温 25°C
  - 高温 50°C
  - 高湿 95% RH
  - 振动 + 跌落

原则 3：OTA 升级必须重新验收
  - 不只是 BLE 协议
  - 必须重做精度测试
  - 必须重做统计抽样
  - 必须 FDA 报告
```

### 复盘

- **BLE connectivity ≠ 验收**——医疗 IoT 必须端到端精度
- **OTA 改了算法 = 重新验收**——不只是"功能正常"
- **FDA Warning Letter = 工业级别**——影响出货资格
- 3M 召回 + 7 死 = 人命代价
- **设计 transfer + 成品 acceptance + 统计抽样** = 三大失守点
- iCGM 21 CFR 862.1355 = 法规硬约束

### 来源

- _Inbox/BLE-2026-08-29-candidates.md 候选 5
- Manufacturing Chemist 报道
- FDA Warning Letter 公开数据
- iCGM 21 CFR 862.1355 法规

---

## 案例 30：NVIDIA Tegra SE ELP 硬件 ECDH 错误——BLE OOB 配对 0x05 静默失败

### 现象

NVIDIA Jetson Xavier NX + L4T R35.6.0：

- BLE SMP OOB（Out-of-Band）配对 0x05
- 静默失败：**无 panic 无 log 无错误码**
- 配对 confirm 不匹配
- 同 OOB 数据在 Android / 非 Tegra Linux 上正常

### 抓包 / 根因

```text
追踪：
  - 抓 BLE 空中 PDU
  - 配对 request → pairing confirm
  - 比较 confirm value（应该匹配）
  - 不匹配 → 0x05 AUTHENTICATION_FAILURE

源码层：
  - Linux BLE 协议栈调用 `tegra-se-ecdh`
  - Tegra Security Engine 的 ECDH 硬件加速驱动
  - 返回值错误（跟 RFC 7748 / SEC 1 不一致）
  - 协议栈拿到错误 ECDH = 配对 confirm 不匹配

影响：
  - Orin（更老）上：kernel panic
  - Xavier NX：静默失败（无任何错误）
  - 同根因，不同表现 = 排查噩梦
```

### 修复（workaround）

```bash
# 1. unbind Tegra SE ECDH 驱动
echo 3ad0000.se_elp > /sys/bus/platform/drivers/tegra-se-ecdh/unbind
# 或
sudo rmmod tegra_se_ecdh

# 2. 系统自动 fallback 到 ecdh-generic（软件实现）
#    验证：dmesg | grep ecdh-generic

# 3. 重新跑 OOB 配对测试
sudo btmgmt pairable on
sudo btmgmt bondable on
```

### 关键工程认知

```text
1. 硬件 crypto 加速器 ≠ 正确实现
   - 加速器可能实现错
   - 测试时必须验证
   - 不能信加速器

2. 静默失败是排查噩梦
   - 无 panic、无 log、无错误码
   - 不同硬件表现不同
   - 升级固件/内核可能恶化

3. Workaround 是临时方案
   - unbind 加速器
   - 回退到软件实现
   - 性能降低但能用
```

### 选型教训

```text
- 新平台 BLE 配对必须 multi-platform 验证
  - Android / iOS / Linux / Windows
  - 不能只测一个
- 配对 confirm/value 不匹配 = 0x05 立刻报
- 静默失败（0 错误）= 排查地狱
- 硬件加速器 = **必须回归测试**
```

### 跟 SimCardReader DRK 交叉

```text
两案例同根因：
  - Tegra SE ECDH 错误 = 硬件 crypto bug
  - SimCardReader DRK/RDP 错误 = 硬件 crypto bug
  - 都是"硬件加速器 ≠ 正确实现"

教训：
  - 任何硬件 crypto 集成后必须 RFC 测试向量
  - 不能只跑功能测试
  - 必须用已知输入对比期望输出
```

### 复盘

- **硬件 crypto 加速器 ≠ 正确实现**——必须回归测试
- 静默失败（无 log）= 排查噩梦
- 多平台交叉验证 = 唯一发现途径
- workaround = unbind 加速器 + 回退软件
- 跟 SimCardReader DRK = 同根因（硬件 crypto bug）

### 来源

- _Inbox/BLE-2026-09-01-candidates.md 候选 5
- NVIDIA 官方论坛（Jetson Xavier NX, L4T R35.6.0）
- Bluetooth Core Spec Vol 3 Part H

---

## 案例 31：Arduino Nano 33 BLE 18mA 突 brownout——BareOS 128KB RAM 板级规范

### 现象

nRF52840 Arduino Nano 33 BLE 实测：

- 标称 TX 电流：5-10mA
- 实测 TX 电流：18mA 突发（+4 dBm）
- 3.3V 跌穿 2.7V brownout → MCU 重置 → 掉链
- 10m 距离直接掉到 30cm

### 抓包 / 根因（3 个并发）

```text
根因 1：TX 突发电流预算 = 板级设计必做
  - nRF52840 TX +4 dBm 峰值 = 18mA
  - LDO 3.3V 跌穿 2.7V brownout
  - MCU 重置
  - 修复：100 µF 钽 + 100 nF 陶瓷去耦

根因 2：面包板金属弹簧引脚
  - 寄生电容把 chip antenna 调偏
  - 10m 距离 → 30cm
  - 修复：直接焊 PCB

根因 3：MTU / connection interval 不匹配
  - 移动端静默断开
  - 修复：iOS/Android 平台适配参数
```

### 修复（板级硬规范）

```text
1. 去耦电容
   - 100 µF 钽（bulk）
   - 100 nF 陶瓷（高频）
   - 紧挨 VCC 引脚
   - 短走线（< 5mm）

2. RF keep-out
   - 15 mm RF 净空区
   - 不能铺地
   - 不能走线

3. PCB 接地铜皮距天线 ≥ 5 mm
   - chip antenna 默认参考地
   - 距离不够 = 谐振偏移

4. 电源设计
   - 峰值电流 1.5x 标称
   - LDO dropout < 100 mV
   - DC-DC 纹波 < 30 mV
```

### BareOS 128KB RAM 板级规范对照

```text
BareOS 平台（N32L40X，128 KB RAM / 512 KB ROM）：

板级设计：
  - 100 µF 钽 + 100 nF 陶瓷（必）
  - 15 mm RF keep-out
  - chip antenna 距地 ≥ 5 mm
  - 3.3V LDO 输出纹波 < 30 mV
  - TX 峰值电流预算 = 1.5x 标称

软件侧：
  - 启动延迟 10ms（等晶振稳）
  - 启动后立即测电源电压（ADC）
  - 异常立即进 safe mode
  - 看门狗复位后重新 init RF

测试侧：
  - 100% 老化测试 24h
  - 实测 TX 突发电流波形
  - 100% brownout 复位测试
```

### 复盘

- **TX 突发电流预算 = 板级设计必做项**（不是芯片 spec 兜底）
- chip antenna 调偏比选错芯片更要命
- MTU / connection interval 不匹配 = 移动端静默断开
- BareOS 128KB RAM 板设计**直接套用本案例规范**
- 3 规范：去耦 / keep-out / 接地距天线

### 来源

- _Inbox/BLE-2026-08-30-candidates.md 候选 3
- electricalflux.com 实战
- nRF52840 datasheet §5.3.1
- BareOS 板级设计规范

---

## 案例 32：零售 IoT "overnight degradation"——可自诊断是部署级硬需求

### 现象

spörk 嵌入式无线工程师 LinkedIn 实战：

- 零售 IoT 部署一夜之间全面劣化
- 无硬件 / 无固件 / 无安装改动
- 现场勘察：邻居 IoT 网 OTA 升级后占用更多共享频谱

### 抓包 / 根因

```text
事实：
  - 自家设备没坏
  - 是 RF 环境变了
  - 共享 ISM 频段无法独占
  - 邻居 OTA = 直接拖垮你

"症状"：
  - 延迟突刺
  - 间歇断开
  - 吞吐随日变化
  - 无法复现
```

### 修复（可自诊断部署）

```text
"可自诊断"是部署级硬需求：
  - 不然每次派人上站
  - 成本爆炸

远程诊断必须采集：
  1. RSSI 历史曲线
  2. 动态协商 TX 功率
  3. 噪声底
  4. 干扰事件
  5. 设备状态
  6. 重启次数
  7. 错误率
  8. 带宽占用

实现：
  - 设备本地缓存 24h 数据
  - 远程查询接口
  - 告警阈值 + 工单触发
  - 现场人员带数据去找问题
```

### 实战 ROI

```text
可自诊断 vs 不可自诊断：
  不可自诊断：
    - 每次故障派人上站
    - 平均 4 小时 / 站
    - 现场测量、排查
    - 全凭经验
    
  可自诊断：
    - 远程看数据 30 分钟
    - 现场直奔问题
    - 2 小时搞定
    - ROI = 8x
```

### BLE 工业 4 维排查 SOP（综合）

```text
4 维独立排查（gutab.cn 实战）：

1. 射频物理层
   - VSWR（天线匹配）
   - AFH 信道图（自适应跳频）
   - LOS（视距）
   - 多径 / 阻挡

2. 协议栈 GAP / GATT
   - 广播间隔 vs 扫描窗口
   - 连接参数交集
   - 配对 MAC 白名单
   - Service UUID 匹配

3. 电源管理
   - 瞬时跌落（TX 峰值）
   - USB Selective Suspend（Host 端）
   - ACPI 策略（OS 端）
   - 电池内阻

4. 固件 / 驱动
   - HCI 队列溢出
   - MTU 协商
   - 状态机占线
   - ISR 阻塞

4 维并行 = 快速定位
```

### 关键认知

```text
- "可自诊断" = 部署级硬需求
- 共享 ISM 频段无法独占 = 必须假设邻居会干扰
- 邻居 OTA = 直接拖垮你
- 4 维排查 = 工业 BLE 故障定位 SOP
- HCI 错误码比应用错误码值钱 10 倍
- ACPI 切蓝牙电源 = 工业 OS 隐藏地雷
```

### 复盘

- **可自诊断 = 部署级硬需求**（不是 nice-to-have）
- 共享频段无法独占 = 必须自适应
- 4 维排查 SOP = 工业 BLE 实战工具
- 远程诊断 = 部署 ROI 关键
- 跟 #1 (DEWINE lab→field) + #2 (spörk overnight) 配套 = lab→field 完整闭环

### 来源

- _Inbox/BLE-2026-08-30-candidates.md 候选 1 + 候选 2 + 候选 4
- DEWINE Labs 工业 BLE blog
- LinkedIn Michael Spörk
- gutab.cn 工业平板厂商

---

## 案例 33：BLE sensor 节点 60s 上报能量账本——精确到 µA

### 现象

某 BLE sensor 节点（nRF52 / STM32WB / ESP32-C3 任一选型）：

- 设计目标：CR2032 续航 2 年
- 实际测试：1 年掉链
- 续航差 50%

### 抓包 / 能量账本

```text
60s 上报周期（实测）：
  - 睡眠 2 µA × 60s = 120 µA·s
  - 读传感器 5 mA × 15 ms = 75 µA·s
  - BLE 广播 11 mA × 8 ms = 88 µA·s
  - 合计：283 µA·s / 60s = 4.7 µA 平均
  
CR2032（220 mAh）：
  - 理论续航：220 / 4.7 × 1 / 24 / 365 = 5.35 年
  - 折扣后：3-4 年（考虑自放电）

但实际只 1 年？问题在哪？
```

### 隐藏 µA 漏电（7 项）

```text
1. LDO 静态电流
   - 典型 LDO：1-2 µA
   - 但有些 LDO 在 disable 时漏 50 µA
   - 修：选 IQ < 1 µA LDO（如 XC6206 = 0.7 µA）

2. I2C 上拉电阻
   - 默认 10 kΩ 上拉 + 3.3V = 330 µA
   - sleep 时 I2C device 漏电
   - 修：1 MΩ 上拉 + I2C switch 控制

3. 状态 LED
   - 状态 LED 常亮 = 5-20 mA
   - 修：sleep 关闭 + 触发点亮

4. 大电容漏电
   - 100 µF 电容漏电 1-5 µA
   - 多个电容叠加
   - 修：减小到 10 µF + 选低漏电型号

5. 浮空 GPIO
   - 单引脚 200 µA
   - 修：Analog + 下拉

6. 传感器本身漏电
   - 温湿度传感器 sleep 时 0.5 µA
   - 但有些国产芯片 5-10 µA
   - 修：选低功耗型号

7. 调试接口
   - SWD / UART sleep 时漏电
   - 修：出货关闭调试接口
```

### 48h 连续录波案例

```text
某 IoT 节点 48h 连续录波发现：
  - 第 23h：触发异常
  - 5 µA 静态 → 18 µA
  - 持续 30s
  - 原因：内部定时器 23h 周期
  - 修：禁用未用定时器

教训：
  - 短时间测试看不到长周期异常
  - 48h 录波才暴露
  - 量产前 48h 录波 = 必做
```

### 量产前 7 项必查

```text
□ 1. 选型决策
   - MCU: nRF52 / STM32WB / ESP32-C3
   - LDO: IQ < 1 µA
   - 传感器: 静态 < 1 µA

□ 2. 电路设计
   - 100 µF 钽 + 100 nF 陶瓷
   - I2C 1 MΩ 上拉 + switch
   - 所有 GPIO 显式配置

□ 3. 固件优化
   - 禁用 DEBUG 宏
   - 关闭未用定时器
   - 关闭未用外设
   - 关闭状态 LED

□ 4. 报告周期
   - 60s 起步
   - 业务侧优化（边缘计算）
   - dynamic CI（活动/平衡/休眠）

□ 5. 测试方法
   - Keithley 2450 测静态
   - TCP0030A 测瞬时
   - 48h 录波
   - 实电池续航测试

□ 6. 现场验证
   - 多平台测试（iOS/Android）
   - 2.4 GHz 共存
   - 金属环境
   - 温度漂移

□ 7. 数据驱动
   - 7 项 µA 漏电表
   - 60s 周期能量账本
   - 续航预测公式
   - 现场校准
```

### 复盘

- **能量账本精确到 µA** = L4 sensor 节点核心
- 60s 周期 + 3 µA 平均 = 3-4 年 CR2032
- 隐藏 7 项 µA 漏电 = 70 µA 睡眠漏电 = 130 天 vs 2 年
- 48h 连续录波 = 唯一发现长周期异常
- 法拉第笼隔离法 = 判内/外因
- **跟 #27 CH582 1.2mA→5μA 配套** = 国产+国外双示例

### 来源

- _Inbox/BLE-2026-08-30-candidates.md 候选 5
- wmrh.cn IoT 实战 blog
- nRF52 / STM32WB / ESP32-C3 选型手册

---

## 案例 34：BLE 工业断连 3 案例合集——Ellisys PHY + Nordic Out-of-Order + EFR32 OTA

### 案例 A：Ellisys 抓 PHY Channel Map 工业频谱避让

```text
现象：工业现场断连
抓包：Ellisys（同步 PHY + 协议）
  - 毫秒级数十次 Channel Map 重协商
  - PHY 不断在 1M / 2M / Coded 间切换
  - 工业 Wi-Fi / 变频器噪声逼出 LL_CONNECTION_UPDATE_IND 超时
  - MIC Failure 反复

根因：
  - PHY 切换频繁 → MAC 重协商 → 累积延迟
  - 工业噪声 + 重协商 = 链路瘫痪

修复（3 步）：
  1. 主动屏蔽工业拥堵频段
     - 频谱仪扫 2.4 GHz
     - 排除 Wi-Fi 1/6/11 + 变频器谐波
  2. 天线远离金属屏蔽罩
     - 5m 净空
  3. RF Ground 与 Digital Ground 单点接
     - 避免高频串扰
```

### 案例 B：Nordic DevZone BLE Data Integrity Failures（Out-of-Order Segments）

```text
现象：nRF 网关 BLE → Wi-Fi bridge 800 KB 大文件
  - 应用层 SAR（Segmentation and Reassembly）
  - 双 radio 高负载触发 SFP CRC fail
  - SAR 出现 A1/A2/**A2**/A4 重排序（重复！）
  - Wi-Fi tcp_window_full 与 BLE CRC 失败时间窗精确对齐

根因：
  - 双 radio 共存 throughput 互相挤兑
  - CRC 失败 → 重传 → 乱序
  - 应用层无 seq 校验

修复（3 件套）：
  1. SAR 必须自带 seq num
     - 容忍乱序
     - 检测丢失
  2. 双 radio 优先级
     - BLE 优先（短时突发）
     - Wi-Fi 限速
  3. 多路 log 时间戳对齐
     - 唯一诊断法
     - 跨 radio 时间同步
```

### 案例 C：EFR32 NCP OTA 0x19 buffer out

```text
现象：EFR32MG21 NCP + host + 5 终端并发 OTA
  - NCP 偶发阻塞 50ms+
  - host 端报 assert
  - log：`NCP has run out of buffers, error 0x19`

根因：3 重打爆 NCP buffer
  - OTA 70min+ 持续传输
  - 0.5s OTA polling
  - 主机小时级属性读

修复（3 板斧）：
  1. `EZSP_CONFIG_PACKET_BUFFER_COUNT = 0xFF`（默认 0x40 = 64）
  2. 检查 OTA Bootload Cluster
  3. **禁用 Packet Handoff plugin**

详见 ZigBee 案例 24（同根因，跨主题）。
```

### 综合教训（3 案例同根因）

```text
- 工业 BLE = PHY 切换 / 双 radio / NCP 缓冲 三大主坑
- Ellisys = 工业抓包金标准
- 双 radio 必须时戳对齐
- NCP OTA 缓冲区必须 0xFF
- 跨主题根因复用：ZigBee 案例 24 跟 BLE 案例 C 同根因
```

### 复盘

- **工业 BLE 三大坑 = PHY / 双 radio / NCP 缓冲**
- Ellisys = 工业抓包金标准（同步 PHY + 协议）
- 双 radio 时间戳对齐 = 唯一诊断法
- NCP buffer 0xFF + 禁用 handoff = 量产必设
- 跨主题案例 = 根因复用价值高

### 来源

- _Inbox/BLE-2026-09-01-candidates.md 候选 1 + 候选 3
- tsight.io 实战
- Nordic DevZone 实战
- Silicon Labs 社区

---

## 案例 35：BLE 不是协议——5 大系统级错误（事件驱动子系统设计）

### 现象

某部署级 BLE 产品（部署到 1000+ 客户）：

- 现场偶发失联
- 客户手机端应用崩
- 售后工单激增
- 固件团队 + 应用团队各排查 1 周无果

### 5 大系统级错误

```text
错误 1：BLE 当 transparent pipe
  现象：app 端写 100 byte，GATT 通知 100 次
  根因：BLE 当 socket 用
        → 协议层 chunking / reassembly
        → 调度复杂
  解决：
    - BLE 当事件驱动子系统
    - 上层只发"事件"
    - 协议层处理分片 / 重传 / 限流

错误 2：忽略 central 端 OS 后台策略
  现象：iOS 锁屏后 BLE 链路掉
        Android 灭屏 5min 后 BLE 通知延迟
  根因：central 端 OS 调度：
    - iOS 后台 BLE 受限（需 peripheral 主动通知）
    - Android Doze 模式切断 BLE
  解决：
    - iOS 用 ANCS（Apple Notification Center Service）
    - Android 用 background scan 限制
    - 不能假设 central 端永远在线

错误 3：功耗 afterthought
  现象：硬件设计 OK，固件功耗高
  根因：功耗优化放在最后
        架构层面没考虑 low-power
  解决：
    - 架构阶段就考虑低功耗
    - 连接 / 广播 / 扫描分场景
    - 事件驱动 + sleep

错误 4：状态爆炸 / 老 bond
  现象：重连失败，bond 信息污染
  根因：central 端切换 → 旧 bond 残留
        状态机设计不显式 → 状态爆炸
  解决：
    - 状态机必须显式定义
    - bond 数量限制
    - 状态转移显式管理

错误 5：安全配置一次定终身
  现象：早期产品默认 key 终身不变
  根因：key rotation 没设计
  解决：
    - 强制 key rotation
    - Trust Center Rejoin 改 Secure Rejoin
    - 量产前重新评估
```

### 实战设计原则

```text
1. BLE 当事件驱动子系统
   - 上层不直接管 GATT
   - 协议层封装分片 / 重传

2. central 端视为不可信
   - iOS / Android 端 OS 策略多变
   - 不能假设链路永远稳定
   - 必须本地状态自管理

3. 状态转换显式管理
   - 状态机不变量
   - 所有转移都显式记录
   - 测试覆盖所有转移

4. 安全分层
   - 默认 key 限缩
   - 强制 key rotation
   - 远程可升级安全策略
```

### 复盘

- **BLE 是子系统不是协议**——架构级认知
- 5 大错误 = 部署级常见坑
- central 端不可信 = 核心原则
- 状态机显式 = 长期维护关键
- 安全分层 = 一次性配置不可取

### 来源

- _Inbox/BLE-Bluetooth-LE-2026-09-03-candidates.md 候选 4
- EurthTech 实战

---

## 案例 36：40 万台安全产品 BLE 重设计——按需广播 vs 持久连接

### 现象

某天花板安防产品（40 万台出货）：

- 固件思路：持久连接 + keepalive
- 问题：电池续航 6 个月 → 期望 2 年
- 现场：安全产品 silent fail 比 crash 更致命
- 重设计：把"持久连接"反转为"按需广播 + 控制端常扫"

### 抓包 / 根因

```text
原方案：持久连接
  设备：扫描 + 保持连接 + keepalive
  控制端：始终连着
  
问题：
  - 设备 keepalive 每 30-60s 一次 → 占空比 5-10%
  - 连接建立 + 维护 = 持续耗电
  - 中心端 OS 调度限制（iOS 后台）
  - 累计 100+ mAh / 年

重设计：按需广播
  设备：周期性广播（5-10s）含状态信息
  控制端：常扫（iOS 用 ANCS / Android 用 background scan）
  业务触发：才建立连接 + 传数据
  
收益：
  - 广播 vs 持久连接 = 1/10 功耗
  - 业务数据传输 < 1s（连接 + 传 + 断开）
  - 控制端 OS 友好
```

### 实战设计

```text
架构：
  ┌─────────────────────┐
  │ 设备（电池）         │
  │  - 5s 周期广播       │  ← 90% 时间
  │  - 收到控制 → 连接  │  ← 5% 时间
  │  - 传数据 → 断开    │
  └─────────────────────┘
            ↕
  ┌─────────────────────┐
  │ 控制端（手机/网关）  │
  │  - 常扫             │
  │  - 收广播显示状态   │
  │  - 用户操作 → 连设备│
  └─────────────────────┘
```

### 修复（4 件套）

```text
1. 重新设计连接 / 扫描 / 广播 / 参数
   - 不能照抄 SDK 默认
   - 按场景定制

2. 持久连接 → 按需广播
   - 业务触发才建链
   - 数据传完立即断

3. 安全产品 silent fail
   - 必须有故障指示
   - 不能默默失败
   - 配 Boot POST + 周期 self-test
   - 失败 = loud（LED / 蜂鸣器）

4. build system 隔离驱动与报警
   - driver 故障 ≠ 报警失能
   - watchdog 独立线程
   - 报警比功能优先
```

### 能量预算重新分配

```text
原方案：
  - 维护连接：60%
  - keepalive：20%
  - 业务：10%
  - 待机：10%

重设计：
  - 广播：30%
  - 业务触发连接：5%
  - 待机：65%  ← 提升 55%
  
续航：
  原：6 个月
  新：2 年（+4x）
```

### 关键认知

```text
- "持久连接"是反模式（IoT 电池场景）
- 按需广播 + 控制端常扫 = 工业标准
- 安全产品 silent fail 致命
- 故障指示必须 loud（不能静默）
- build system 隔离驱动与报警
- Boot POST + 周期 self-test = 必做
```

### 复盘

- **按需广播 vs 持久连接** = 6 个月 → 2 年
- 40 万台出货 = 决策影响巨大
- 安全产品 silent fail = 致命
- 故障指示必须 loud（不是 nice-to-have）
- 业务传输 < 1s 完成
- 控制端 OS 友好 = iOS ANCS / Android BG scan

### 来源

- _Inbox/BLE-Bluetooth-LE-2026-09-03-candidates.md 候选 5
- needCode（产线出货级实战）

---

## 案例 37：Zephyr + nRF52840 自制板 SCA 时钟精度 ±500ppm 掉链

### 现象

Laird BL654（nRF52840 SOM）+ Zephyr RTOS：

- 开发板（带 32.768 kHz 晶振）：BLE 连接稳定
- 自制板（**未贴 32.768 kHz 晶振**）：连接反复掉
- BOM 差异：晶振

### 抓包 / 根因

```text
Zephyr 默认 SCA（Sleep Clock Accuracy）：
  - 50 ppm（要求 32.768 kHz 晶振精度）
  - nRF52840 内部 RC：±500 ppm
  - 自制板未贴 32.768 kHz → 默认走 RC
  - SCA 实际 500 ppm vs 默认 50 ppm → 链路层连接参数违规
  - 中央端检测到 SCA 超标 → 拒绝连接或频繁掉链

nRF52840 SCA 7 档：
  - 0 = 250 ppm
  - 1 = 150 ppm
  - 2 = 100 ppm
  - 3 = 75 ppm
  - 4 = 50 ppm（默认，32.768 kHz 晶振）
  - 5 = 30 ppm
  - 6 = 20 ppm
```

### 修复

```c
// Zephyr 改 SCA 精度
// prj.conf
CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y
CONFIG_CLOCK_CONTROL_NRF_K32SRC_ACCURACY=0  // 250 ppm（用 RC）

// 如果用晶振：
CONFIG_CLOCK_CONTROL_NRF_K32SRC_XTAL=y
CONFIG_CLOCK_CONTROL_NRF_K32SRC_ACCURACY=4  // 50 ppm
```

### 复盘

- **"开发板没事/自制板频繁掉" = 99% BOM/晶振/天线差异**
- 32.768 kHz 晶振 → 直接进 BLE SCA
- Zephyr `CLOCK_CONTROL_NRF_K32SRC_ACCURACY` 7 档 = 0-6
- ppm 越大连接越容易掉
- 自制板必检 BOM 完整性（晶振/天线/匹配）

### 来源

- _Inbox/BLE-2026-09-04-candidates.md 候选 1
- MAB Labs 实战

---

## 案例 38：ESP32 Bluedroid vs NimBLE 内存对比 + 错误码表实战

### 现象

某 ESP32 BLE 项目，BLE 服务偶发崩：

- 错误：`ESP_ERR_NO_MEM` / `Guru Meditation`
- 内存吃紧（220KB 板子）
- 选 Bluedroid 还是 NimBLE？

### 内存对比

```text
ESP32 BLE 协议栈选择：
  - Bluedroid（默认）：110-140 KB SRAM
  - NimBLE：30 KB SRAM
  - 节省：80-110 KB

选择决策：
  - BLE-only 项目：选 NimBLE（30 KB）
  - 蓝牙经典 + BLE：必须 Bluedroid（110 KB+）
  - 220 KB 板子：NimBLE 可行
  - 100 KB 板子：必须 NimBLE
```

### 错误码表（实战）

```text
ESP32 BLE 错误码表：
  0x103  ESP_ERR_NO_MEM
        - GATT 队列满
        - notify buffer 满
        - 多 service 同时操作
        
  0x106  ESP_ERR_INVALID_STATE
        - profile 未注册就调用
        - service 注册顺序错
        - 回调未注册
        
  0x3008 GATT_INSUF_RESOURCE
        - MTU 协商失败
        - characteristic 超过 20 字节
        - 多个 notify 同时发
        
  0x2002 LINK_LAYER_NO_MEM
        - LL 队列满
        - 多连接 + 大数据
        
  0x2003 LL_HCI_BUF_ALLOC
        - HCI 缓冲区分配失败
        - 短时间多个 connectGatt
```

### 修复（4 件套）

```text
1. 释放经典蓝牙内存
   esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT);
   // 节省 30 KB
   // 必须 esp_bt_controller_init() 之后调用

2. 选 NimBLE
   // menuconfig → Component config → Bluetooth → NimBLE
   CONFIG_BT_BLUEDROID_ENABLED=n
   CONFIG_BT_NIMBLE_ENABLED=y

3. 实现 onMtuChanged 回调
   void mtu_changed(...) {
       uint16_t mtu = p_mtu->mtu;
       // 通知应用层更新 buffer
   }
   // 不实现 = Guru Meditation 风险

4. 限制 notify 频率
   - 每个 characteristic < 10 notify/s
   - 多个 characteristic 总和 < 50 notify/s
   - 超限 → ESP_ERR_NO_MEM
```

### 实战代码

```c
// ESP32 BLE 初始化（推荐 NimBLE 模板）
void ble_init(void) {
    esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT);
    
    esp_nimble_hci_init();
    nimble_port_init();
    
    // 注册 GATT 回调
    ble_svc_gap_init();
    ble_svc_gatt_init();
    
    // 启动
    nimble_port_freertos_init(ble_host_task);
}

void ble_host_task(void *param) {
    nimble_port_run();
    // 不会返回
}
```

### 复盘

- **Bluedroid 110KB vs NimBLE 30KB** = L4 ESP32 BLE 必收表
- ESP32 BLE 错误码表 = 实战必备
- 释放经典蓝牙 = 节省 30KB
- 选 NimBLE = BLE-only 项目标准
- onMtuChanged 必须实现
- notify 频率限制 = Guru Meditation 预防

### 来源

- _Inbox/BLE-2026-09-04-candidates.md 候选 2
- electricalflux.com 实战
- ESP-IDF 文档 §9.3

---

## 案例 39：工业 BLE 4 维排查 + USB Selective Suspend 隐性断电

### 现象

工业平板（Windows 主机）+ BLE 外设：

- 现场偶发"找不到设备"
- 重启主机后能连接
- log 没规律

### 4 维排查

```text
维度 1：射频物理层
  - VSWR（天线匹配）
  - AFH 信道表
  - LOS（视距）
  - 工业外壳金属屏蔽

维度 2：协议栈参数
  - 广播间隔 vs 扫描窗口
  - 连接参数协商
  - 安全/白名单
  - MTU 协商

维度 3：电源管理
  - 瞬时电流跌落
  - USB Selective Suspend  ← 关键！
  - 接地环路
  - 电池电量

维度 4：固件逻辑
  - 业务状态机挂起协议栈
  - SPP-over-BLE MTU 协商
  - GATT callback 阻塞
```

### USB Selective Suspend（隐性断电）

```text
Windows 默认行为：
  - USB 设备 3-5 分钟无数据
  - 自动进入 Selective Suspend
  - 关闭 USB 供电
  - 蓝牙适配器失电

现象：
  - 蓝牙"消失"
  - 设备管理器可见但失联
  - 重新插拔恢复

修复（4 选 1）：
  1. 设备管理器 → USB 根集线器 → 属性 → 电源管理
     取消"允许计算机关闭此设备以节省电源"
  2. powercfg /setacvalueindex scheme_current 2a737441-1930-4402-8d77-b2b0ba72180a 0
  3. 禁用 USB Selective Suspend（控制面板）
  4. 程序主动 keepalive（每分钟一次 IOCTL）
```

### "外设极长广播间隔 + 主机短扫描窗口"

```text
经典"设备找不到"组合：
  - 外设广播：1000ms（省电）
  - 主机扫描窗口：100ms
  - 重叠概率 = 10%
  - 90% 找不到

修复：
  - 调整广播间隔（兼容主机扫描窗口）
  - 或增加扫描窗口（兼容外设广播）
  - 主动扫描 + 报告
```

### HCI 日志诊断

```text
HCI 日志关键 pattern：
  - "Send HCI Command Failed" → 驱动层 buffer 溢出
  - "Event Queue Full" → HCI 上行队列满
  - "Command Disallowed" → 状态机错
  - "Connection Complete - TIMEOUT" → 链路层超时

HCI 比应用 log 准 10 倍。
```

### 复盘

- **4 维排查 SOP** = 工业 BLE 必走
- **USB Selective Suspend** = 工业 OS 隐藏地雷
- 主机端必须先关"省电"
- HCI 日志 = 工业 BLE 诊断金标准
- 广播间隔 vs 扫描窗口 = 必须匹配

### 来源

- _Inbox/BLE-2026-09-04-candidates.md 候选 3
- gutab.cn 工业平板厂商

---

## 案例 40：4 款 BLE 模块 Wi-Fi 干扰下 30ms 实时性实战对比

### 现象

某工业实时控制系统：

- 需求：100 B / 100 ms 控制环 ≤ 30 ms 延迟
- 4 款 Nordic 系 BLE 模块横向对比
- 干净 RF：都过
- Wi-Fi 干扰：标准 BLE 全崩

### 4 款模块对比

```text
DEWINE Labs 实测（30 ms 实时约束）：

| 模块 | 干净 RF | Wi-Fi 干扰 | 设计原则 |
| --- | --- | --- | --- |
| nRF52840 HCI (标准) | ✅ 通过 | ❌ 超 30ms | 标准协议栈 |
| BL654 (Laird) | ✅ 通过 | ❌ 超 30ms | 标准协议栈 |
| Proteus-III (Panasonic) | ✅ 通过 | ❌ 超 30ms | 标准协议栈 |
| NINA-B112 (u-blox) | ✅ 通过 | ❌ 超 30ms | 标准协议栈 |
| LinkBlu RT | ✅ 通过 | ✅ 通过 | 双通道隔离 + 自适应干扰处理 |

关键：标准 BLE 在 2.4 GHz 干扰下全超 30ms
      实时性 ≠ 吞吐量（吞吐能过但实时性不过）
```

### 根因

```text
工业 BLE 实时性崩盘根因：
  1. 固件 best-effort 调度
     - 默认 RTOS 调度（优先级 + 时间片）
     - RF 拥塞 → MAC 重传 → 占 CPU 时间
     - 关键 GATT 操作被延迟
     
  2. 控制 / 日志共享队列
     - 控制指令和日志混用同一队列
     - 日志拥塞时控制延迟
     
  3. late packet = invalid packet
     - 实时系统 = 过期包无价值
     - BLE 重传让包过期
     - 没用 = 丢
```

### LinkBlu RT 设计原则

```text
1. bounded latency
   - 硬性 30ms 延迟上限
   - 不允许超时
   - 软实时转硬实时

2. dual-channel isolation
   - 双通道隔离
   - 控制 / 数据分离
   - 不互相影响

3. adaptive interference handling
   - 实时监测 2.4 GHz 干扰
   - 动态调整 PHY
   - 避开拥堵频段
```

### 复盘

- **实时性 ≠ 吞吐量**——工业 BLE 真实门槛
- 4 款标准 BLE 全在干扰下超 30ms
- LinkBlu RT = 双通道隔离 + 自适应 = 唯一解
- best-effort 调度是工业 BLE 死结
- late packet = invalid packet（实时铁律）
- "吞吐量能过 / 实时性不过" = 工业实战

### 来源

- _Inbox/BLE-2026-09-04-candidates.md 候选 4
- _Inbox/BLE-2026-09-05-candidates.md 候选 1
- DEWINE Labs 行业 blog

---

## 案例 41：CC254x BLE 4.0 OSAL 调度死锁复盘（8KB RAM + 7.5ms 连接）

### 现象

CC254x（TI BLE 4.0）项目：

- 8 KB RAM
- 7.5 ms 连接间隔
- 死锁频繁：单线程 OSAL 遇死亡临界点
- 现象：连接后几秒断链

### 抓包 / 根因

```text
CC254x OSAL（Operating System Abstraction Layer）：
  - 单线程循环
  - LL 层硬实时 ISR 跑 radio
  - 应用任务长跑 → 占满时间片
  - LL 层 ISR 错过 → 链路层超时

时序：
  Step 1：LL 层 ISR 期待下个连接事件
  Step 2：应用任务占用 CPU 5-10 ms
  Step 3：LL 层 ISR 错过窗口
  Step 4：LL Timeout 触发
  Step 5：连接断开
```

### 调试方法（GPIO 翻转 + 逻辑分析仪）

```c
// OSAL 任务入口翻 GPIO
void MyApp_ProcessEvent(void) {
    GPIO_SET(P1_0);  // 任务开始
    // 业务逻辑
    MyApp_DoWork();
    GPIO_CLEAR(P1_0);  // 任务结束
}

// OSAL 任务出口翻 GPIO
void MyApp_ProcessEventEnd(void) {
    GPIO_CLEAR(P1_0);
}

// LL 层 ISR 入口翻 GPIO
void LL_ProcessEvent(void) {
    GPIO_SET(P1_1);  // LL 开始
    // LL 处理
    GPIO_CLEAR(P1_1);  // LL 结束
}
```

逻辑分析仪观测：
- P1_0（应用）：占空比 80-90%
- P1_1（LL）：被错过
- 7.5ms 是高负载分水岭

### 修复（反直觉 4 步）

```text
1. 禁用自动连接参数更新
   - 7.5ms 间隔保持不变
   - 不要让 central 改
   - 否则触发更多 ISR 冲突

2. 业务移出 OSAL 循环
   - 移到定时器 / DMA 中断
   - OSAL 只做轻量逻辑
   - 长任务异步化

3. 绕过 GATT 直透传 LL 层
   - 不走 GATT 协议栈
   - 直接 LL 层 data PDU
   - 节省 30-40% CPU

4. 加 LL_TIMEOUT 延长
   - 默认 6s
   - 改 10s
   - 给应用更多处理时间
```

### 复盘

- **CC254x 8KB RAM = 资源极端受限**
- OSAL 单线程 = LL ISR 必错过
- 7.5ms 是高负载分水岭
- 主动放弃部分标准换稳定
- 业务移出 OSAL 循环 = 关键
- GPIO 翻转 + 逻辑分析仪 = 必做调试手段

### 来源

- _Inbox/BLE-2026-09-05-candidates.md 候选 2
- TrueSight 实战
- TI OSAL Guide

---

## 案例 42：T20i 产线 A2 线 19.2% 蓝牙不良（KT6368A DMA + 2.4V 倒灌）

### 现象

T20i 产线新开 A2 线蓝牙不良率 19.2%（行业 < 1%）：

- 待机电流：20 mA（正常 3 mA）
- 看门狗 4s 不复位 = 深度死锁
- 现场工位 QC 6s 通过，但实际使用 15s 后才崩

### 抓包 / 根因（3 因子）

```text
因子 1：KT6368A DMA 异常
  - 蓝牙模组内部 DMA 控制器异常
  - 触发深度死锁
  - 看门狗不复位
  - 修：换料件 + 严格来料检验

因子 2：电压 2.4V
  - 模组供电不稳（< 2.7V 标称）
  - 内部逻辑错乱
  - 修：电源纹波 + 稳压

因子 3：TX/RX 倒灌
  - 上电时序错乱
  - 倒灌电流破坏其他模块
  - 修：串 100Ω 隔离电阻
```

### 3 因子实战

```text
1. 串 100Ω 隔离电阻
   - 在 TX/RX 各串 100Ω
   - 防止倒灌
   - 限制瞬态电流

2. 改料件检验
   - KT6368A 严格来料检验
   - 烧录后跑老化测试
   - 烧录异常率 > 1% 拒收

3. 测试延至 20s
   - 工位 QC 从 6s 延长到 20s
   - 触发深度死锁需要时间
   - 20s = 95% 缺陷被暴露
```

### 复盘

- **A2 线不良 19.2%** = 行业 19 倍（产线异常）
- 3 因子叠加：DMA + 电压 + 倒灌
- **QC 6s vs 触发 15s = 测试盲区**——20s 延长时间
- 倒灌电流破坏上电时序
- 热风枪复现 = 微裂纹（隐性缺陷）
- 100Ω 隔离 = 工业标准做法

### 来源

- _Inbox/BLE-2026-09-05-candidates.md 候选 3
- 人人文库 专项攻关 PPT
- KT6368A datasheet

---

## 案例 43：仓库 RTL8852BU 0xfcf0 -16 静默失败——单芯片故障放大 $47k

### 现象

某仓库 WMS（仓库管理系统）使用 Linux Fedora 44 + RTL8852BU combo Wi-Fi/BT 芯片：

- 错误：`Opcode 0xfcf0 failed: -16` (=EBUSY)
- 蓝牙子系统启动 22s 后自终止
- systemd 停服务
- WMS 全线瘫 48h
- 损失 $47k（仓库 throughput 损失）

### 抓包 / 根因

```text
dmesg 日志 pattern：
  - bluetoothd 启动 → 22s 后自终止
  - systemd 停服务
  - WMS 客户端全部断连

根因（3 个并发）：
  1. RTL8852BU firmware 初始化失败
     - 芯片 firmware 加载失败
     - 蓝牙子系统 init 异常
  2. Wi-Fi / BT 共存资源争抢
     - combo 芯片共享 2.4 GHz RF
     - 一方初始化失败影响另一方
  3. 24h 周期（猜测：内部定时器 / 证书续期）
     - 与 Azure IoT Edge LNS 静默卡死同模式
     - 需要长时监测
```

### 修复（3 步）

```text
1. dmesg 抓 pattern
   - 不看单行错误
   - 看 24h 日志 pattern
   - "bluetoothd 启动 → 22s 后自终止" 才是根因

2. 隔离 Wi-Fi / BT
   - 用 2 个独立芯片
   - 不要 combo
   - 单点故障放大 = 高风险

3. 备用路径
   - 仓库多 gateway
   - 蓝牙断了用 Wi-Fi 兜底
   - 不能 100% 依赖单芯片
```

### 关键认知

```text
- combo 芯片单点故障放大 = 工业设计禁忌
- dmesg pattern 比单行错误码更值钱
- 仓库 throughput ≠ WMS bug
- 24h 周期故障 = 必长时监测
- $47k / 48h = 单芯片故障放大代价
```

### 实战排查

```bash
# 1. 看 dmesg 24h 日志
sudo journalctl -k --since "24 hours ago" | grep -E "bluetooth|rtl|firmware"

# 2. 看蓝牙子系统状态
sudo systemctl status bluetooth
sudo btmgmt info

# 3. 单独测试 BT（隔离 Wi-Fi）
sudo modprobe -r rtw_8852bu
sudo modprobe bluetooth
sudo systemctl restart bluetooth
```

### 复盘

- **combo 芯片单点故障放大** = 仓库 48h 瘫
- dmesg pattern 比单行错误码值钱
- 仓库 throughput ≠ WMS bug
- combo = 1 个 chip 失败 = WiFi + BT 全瘫
- 必须双芯片 + 备用路径
- 24h 周期故障 = 长时监测

### 来源

- _Inbox/BLE-2026-09-05-candidates.md 候选 4
- Dre Dyson 物流技术 blog（12 年 IoT 顾问）

---

## 案例 44：Linux Kernel BLE 内存泄漏——4 天崩溃 + kmalloc-1k/-192 持续涨

### 现象

某嵌入式 Linux 平台（v5.13/5.15/6.5）：

- 跑 4 天后系统崩溃
- 复现条件："BLE 启但 peer 不存在"
- `kmalloc-1k/-192` 持续涨
- patch series + STM32 DK2 + QEMU 复现步骤都齐
- syzbot 2023 已报但无人修

### 抓包 / 根因

```text
复现链路：
  1. 启动 BLE 协议栈
  2. 没有任何 BLE peer 连接
  3. L2CAP 持续分配内存
  4. 4 天累计 OOM
  5. 系统崩溃

复现版本：
  - v5.13（5.x 系列）
  - v5.15（5.x LTS）
  - v6.5（6.x mainline）
  - 全部复现

kmalloc slab 涨幅：
  kmalloc-1k  +5 KB / hour
  kmalloc-192 +2 KB / hour
  = 7 KB / hour × 96 hour = 672 KB
  = 系统 OOM
```

### 调试（5 步法）

```bash
# 1. 看 slab 实时涨幅
watch -n 60 "cat /proc/slabinfo | grep -E 'kmalloc-1k|kmalloc-192'"

# 2. 找谁在分配
sudo ftrace -e 'kmem_cache_alloc' | head

# 3. 找 BLE 协议栈模块
lsmod | grep bluetooth
sudo lsof -p $(pidof bluetoothd) | grep -i kern

# 4. 复现补丁
git clone https://git.kernel.org/pub/scm/linux/kernel/git/bluetooth/bluetooth-next.git
# 应用 patch series
make modules SUBDIRS=net/bluetooth

# 5. QEMU 复现
qemu-system-x86_64 -kernel vmlinux -append "console=ttyS0" -m 1G
# 启动 BLE
bluetoothctl scan on
# 4 天等 OOM
```

### 修复

```text
短期方案：
  - 限制 BLE 启动时长
  - systemd 每日重启 bluetoothd
  - 监控 kmalloc slab 涨幅
  
中期方案：
  - 应用 patch series
  - 升级到修复版本内核
  
长期方案：
  - 永远不要在无 peer 时启 BLE
  - 应用启动时才 init BLE
  - 业务逻辑做去 init
```

### 复盘

- **Linux Kernel BLE 内存泄漏** = L4 内核层实战
- 4 天才能复现 = 必须长时监测
- kmalloc slab = 内核级 leak
- syzbot 已报但无人修 = 关注内核 mailing list
- 嵌入式 Linux BLE 项目 = 必做 4 天压力测试
- patch series 复现 = 内核调试金标准

### 来源

- _Inbox/BLE-Bluetooth-LE-2026-09-07-candidates.md 候选 2
- Mind 嵌入式团队 bug hunt 复盘
- syzbot 2023 report

---

## 案例 45：可穿戴 sensor 72h→31h 现场电池续航 3 因素叠加

### 现象

某可穿戴 IoT sensor：

- 设计续航：200 mAh 电池跑 72h（lab）
- 实际：31h（field，15°C 温差 + 真实 BLE）
- 续航差 2.3x
- **固件无 bug**，但**"为 lab 设计"**

### 抓包 / 根因（3 件事叠加）

```text
3 大 root cause：

1. 手机主动重协商连接间隔
   - 设计：CI = 200ms
   - 实际：手机 30min 后请求 CI = 100ms
   - 后果：radio-on 时间翻倍
   - 影响：+30% 功耗

2. 弱信号下 PER 8-15% → 重传
   - 现场 RSSI = -85dBm（弱）
   - PER 8-15% = 6-10 包重传 1 次
   - 每次重传 = 100ms radio-on
   - 后果：+50% 功耗

3. 低温晶振漂移 → sensor/BLE 事件碰撞
   - 现场 -15°C
   - 32 kHz 晶振漂移 ±200 ppm
   - sensor 采样事件 + BLE 广播事件碰撞
   - MCU 进不了 deep sleep
   - 后果：+20% 功耗
```

### 累计功耗账

```text
理论功耗：200 mAh / 72h = 2.78 mA 平均

实战（field 3 因素叠加）：
  - 基础：2.78 mA
  - CI 200→100ms：+30% = 3.61 mA
  - PER 8-15% 重传：+50% = 5.42 mA
  - 晶振漂移：+20% = 6.50 mA
  - 实际：6.50 mA

续航：200 mAh / 6.50 mA = 30.8h ≈ 31h ✅
```

### 修复（3 件事）

```text
1. 锁连接间隔
   - Peripheral 拒绝手机的 CI 协商
   - 强制 CI = 200ms
   - iOS 限制 ≥ 15ms 即可
   - 拒绝后功耗稳定

2. 优化信号链路
   - 改善天线
   - 优化 PCB 布局
   - 提高功率（法规允许）
   - 减少距离
   - 加 PA

3. 软件补偿低温漂移
   - 改用 TCXO（温补晶振）
   - 软件算法补偿
   - sensor + BLE 事件错峰
   - 事件分桶避免碰撞
```

### 关键工程认知

```text
- "固件无 bug" ≠ "field 跑得动"
- lab 续航 50-60% 是常态（40% 缩水）
- 手机会主动重协商 CI（Peripheral 不知道）
- 弱信号 PER = radio-on 翻倍
- 低温晶振漂移 = 事件碰撞 = 醒着
- 量产前必须 field 续航实测
```

### 复盘

- **3 因素叠加 = field 续航 50-60% lab** = 典型
- 手机主动重协商 = 关键工程盲点
- 锁 CI = 必须（不能让手机决定）
- 弱信号 = PER 翻倍 = radio-on 翻倍
- 低温晶振 = 事件碰撞 = 进不了 deep sleep
- 累计 2.3x 功耗 = 必须 field 实测

### 来源

- _Inbox/BLE-Bluetooth-LE-2026-09-07-candidates.md 候选 5
- Promwad 硬件/固件外包团队

---

## 案例 46：医疗血压计 BLE 适配器 6 个月 30% 测量丢失（256KB MCU）

### 现象

某医疗血压计 BLE 适配器：

- 部署后 30% 测量丢失
- MCU：256KB RAM（nRF52832 级别）
- Watchdog：8s 自愈
- 拉一周 470K 行 journal 定位

### 抓包 / 故障分布

```text
470K 行 journal 分析：
  - 62 个失败
  - 33 freeze（53%）
  - 8 安全 bug（13%）
  - 21 设备不在场（34%）
```

### 4 大根因

```text
根因 1：Central ≠ Peripheral 复杂度差 1 量级
  - Peripheral 简单：广播 + 连接响应
  - Central 复杂：扫描 + 主动连 + bond 管理 + 多服务发现
  - 适配器作为 Central = 复杂度爆炸
  - 解决：明确角色（能用 Peripheral 别做 Central）

根因 2：Bonding key 必持久化
  - 默认：RAM 存
  - 断电丢失 → 用户重新配对
  - 医疗设备 = 频繁掉电（移动）
  - 解决：bonding key 存 NVM / flash sector

根因 3：8s watchdog 是商业可靠线
  - 太短（< 4s）= 误复位
  - 太长（> 30s）= 用户等待久
  - 8s = 平衡点
  - 解决：所有 task 8s 内必须喂狗

根因 4：21 设备不在场（34%）
  - 医疗设备移动频繁
  - BluetoothGatt.refresh() 失败
  - 用户数据无法同步
  - 解决：本地缓存 + 下次连接补传
```

### 实战修复

```c
// 1. Bonding key 持久化
void save_bond_key(uint8_t *key, uint16_t len) {
    nvm_flash_write(BOND_ADDR, key, len);
    nvm_flash_commit();
}

void load_bond_key(uint8_t *key, uint16_t len) {
    nvm_flash_read(BOND_ADDR, key, len);
}

// 2. Watchdog 喂狗
void feed_watchdog(void) {
    NRF_WDT->RR[0] = WDT_RR_RR_Reload;
}

void vTask(void *pvParameters) {
    while (1) {
        do_work();
        feed_watchdog();
        delay_ms(100);
    }
}

// 3. 数据缓存 + 补传
typedef struct {
    uint8_t data[256];
    uint16_t len;
    bool pending;
    uint32_t timestamp;
} pending_data_t;

pending_data_t cache[100];

void cache_data(uint8_t *data, uint16_t len) {
    for (int i = 0; i < 100; i++) {
        if (!cache[i].pending) {
            memcpy(cache[i].data, data, len);
            cache[i].len = len;
            cache[i].pending = true;
            cache[i].timestamp = millis();
            return;
        }
    }
}

void flush_cache_on_connect(void) {
    for (int i = 0; i < 100; i++) {
        if (cache[i].pending) {
            send_data(cache[i].data, cache[i].len);
            cache[i].pending = false;
        }
    }
}
```

### 复盘

- **Central 复杂度差 1 量级** = 工程盲点
- Bonding key 持久化 = 必做
- 8s watchdog = 商业可靠线
- 30% 测量丢失 = 33 freeze + 21 设备不在场
- 数据缓存 + 补传 = 解决设备不在场
- 拉一周 log 定位 = 6 个月血泪教训

### 来源

- _Inbox/BLE-Bluetooth-LE-2026-09-08-candidates.md 候选 1
- QA Platform 工程 blog

---

## 案例 47：nRF52 GATT notify 5ms 推包被 30ms CI 压制——BLE 吞吐 = Central 协商窗口

### 现象

某 nRF52 BLE 数据流应用：

- 设计：5ms 推一次 notify（200 Hz）
- 实际：central 谈成 30ms 连接间隔
- 后果：每 connection event 只发 1 个 notify
- tx queue 静默溢出
- 大量丢包

### 根因

```text
BLE 吞吐公式：
  每秒包数 = 1000 / CI × 每 event 包数
  
  实测：
    CI = 30ms
    每 event 包数 = 1
    实际吞吐 = 33 包/s
    
  设计：
    期望 200 包/s
    需要 CI ≤ 5ms
    
  差距 6x = 大量丢包
```

### 修复（3 件套）

```text
1. 请求更短 CI
   - Peripheral 主动 update_conn_params
   - iOS 限制 ≥ 15ms（必须 15ms 倍数）
   - Android 限制 ≥ 7.5ms
   - 实测：请求 CI = 15ms（iOS 接受）

2. NRF_ERROR_RESOURCES backoff
   - 通知失败时不要 retry 立即
   - backoff 100ms
   - 等 tx queue 释放
   - 避免风暴

3. 等 TX_COMPLETE 事件
   - 不要连续发
   - 等 BLE_GATTS_EVT_HVN_TX_COMPLETE
   - 确认发送成功再发下一包
```

### 实战代码

```c
// 修复版 notify 推包
static bool tx_busy = false;
static uint32_t last_send_time = 0;
static const uint32_t RETRY_BACKOFF_MS = 100;

void send_data_notify(uint8_t *data, uint16_t len) {
    if (tx_busy) {
        uint32_t now = millis();
        if (now - last_send_time < RETRY_BACKOFF_MS) {
            return;  // backoff 中
        }
        // 超时强制清标志
        tx_busy = false;
    }
    
    uint32_t err_code = ble_nus_data_send(&m_nus, data, &len, m_conn_handle);
    if (err_code == NRF_SUCCESS) {
        tx_busy = true;
        last_send_time = millis();
    } else if (err_code == NRF_ERROR_RESOURCES) {
        // 队列满，backoff
    } else {
        // 其他错误
    }
}

void on_ble_evt(ble_evt_t *p_ble_evt) {
    switch (p_ble_evt->header.evt_id) {
        case BLE_GATTS_EVT_HVN_TX_COMPLETE:
            tx_busy = false;  // 释放锁
            break;
    }
}
```

### 关键工程认知

```text
- BLE 吞吐 = central 协商窗口（不是 peripheral 推包频率）
- iOS 最短 15ms
- Android 最短 7.5ms
- hvx 失败必 backoff（不能 retry 风暴）
- 5ms 推包 = 200 Hz 需 CI ≤ 5ms（iOS 拒）
- 实际 CI = 15ms（iOS 接受）
- 实际吞吐 = 1000/15 = 66 包/s
- 比 5ms 设计 200Hz 少 3x
```

### 复盘

- **BLE 吞吐 = Central 协商窗口** = 核心铁律
- 5ms 设计 30ms CI = 6x 丢包
- hvx 失败 backoff = 必做
- iOS 15ms 限制 = 真实物理边界
- 5 件套 backoff + 等 TX_COMPLETE + 请求短 CI = 稳
- 实战：50% 丢包 = 90% 是 CI 没谈妥

### 来源

- _Inbox/BLE-Bluetooth-LE-2026-09-08-candidates.md 候选 2
- moltbook 工程师复盘

---

## 案例 48：ESP32 蓝牙故障诊断 5 症状矩阵（Guru + 2m 内断连 + 堆耗尽）

### 现象

ESP32 BLE 项目 5 大故障：

1. Guru Meditation（崩溃）
2. Device Not Found
3. 2m 内断连
4. 堆耗尽
5. 距离衰减

### 5 症状 → 根因 → 修复对照

```text
症状 1：Guru Meditation
  根因：堆耗尽 / 数组越界 / NULL 指针
  修复：
    - 增大 task stack（如 8KB）
    - ESP_LOGI 替代 printf
    - 静态分配（避免 malloc）
    - 看 Guru 反汇编找具体行

症状 2：Device Not Found（找不到）
  根因：RPA 随机 MAC（每 15 分钟变）
  修复：
    - 用 BLE_ADDR_TYPE_PUBLIC（设备真 MAC）
    - 不用 RANDOM
    - 配对时绑定

症状 3：2m 内断连
  根因：发射功率太低 / 板载天线谐振偏移
  修复：
    - esp_ble_tx_power_set(ESP_PWR_LVL_P9)  // +9dBm
    - 不用 P7（仅 +3dBm）
    - 检查天线匹配网络

症状 4：堆耗尽
  根因：Bluedroid 110-140KB 占内存
  修复：
    - 改 NimBLE（30KB）
    - 减小服务数量
    - esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT)

症状 5：距离衰减
  根因：天线匹配 / PA 不够 / 障碍
  修复：
    - 改善天线设计
    - 加 PA（如 SKY66112）
    - 减少阻挡
```

### ESP32-S3 特殊点

```text
ESP32-S3 = 经典蓝牙硬件不存在
  - 只能 BLE（不能 SPP 经典蓝牙）
  - SPP 必须迁 NimBLE

迁移路径：
  menuconfig → Component config → Bluetooth:
    [ ] Bluedroid (disable)
    [x] NimBLE (enable)
    [x] NimBLE Host (enable)
```

### iPhone 连接参数硬约束

```text
iOS 拒收非标连接参数：
  - CI 必须是 15ms 倍数
  - Latency ≤ 30
  - Timeout ≥ 2s
  - Timeout > (1 + Latency) × CI × 2

放宽策略：
  esp_ble_gap_update_conn_params(30, 50, 0, 400);
  // CI_min=30, CI_max=50, latency=0, timeout=400
  // 给 iOS 选择空间
```

### HCI 错误码调试

```c
// Core Debug Level = Verbose 才会暴露 HCI 错误码
esp_log_level_set("*", ESP_LOG_VERBOSE);

// 关键 HCI 错误码
#define HCI_ERROR_CODE_CONN_FAILED_TO_BE_ESTABLISHED 0x3E
#define HCI_ERROR_CODE_AUTHENTICATION_FAILURE       0x05
#define HCI_ERROR_CODE_PIN_OR_KEY_MISSING           0x06
```

### 修复代码汇总

```c
// 1. 选 NimBLE
void ble_init_nimble(void) {
    esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT);
    esp_nimble_hci_init();
    nimble_port_init();
    ble_svc_gap_init();
    ble_svc_gatt_init();
    nimble_port_freertos_init(ble_host_task);
}

// 2. 设最大发射功率
void ble_set_max_power(void) {
    esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_DEFAULT, ESP_PWR_LVL_P9);
    esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, ESP_PWR_LVL_P9);
    esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_SCAN, ESP_PWR_LVL_P9);
}

// 3. 设 public MAC
void ble_set_public_mac(void) {
    uint8_t mac[6] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};
    esp_base_mac_addr_set(mac);
}
```

### 复盘

- **5 症状 → 根因 → 修复** = ESP32 BLE 必收
- ESP32-S3 经典蓝牙硬件不存在 = SPP 必迁 NimBLE
- iPhone 拒非标 CI = 必放宽 update_conn_params
- Core Debug Level = Verbose = 暴露 HCI 错误码
- `BLE_ADDR_TYPE_PUBLIC` = 修"找不到"
- `PWR_LVL_P9` = 修"2m 断连"
- NimBLE = 修"堆耗尽"

### 来源

- _Inbox/BLE-Bluetooth-LE-2026-09-10-candidates.md 候选 4
- electricalflux.com 嵌入式 MCU 实战博客
- ESP-IDF 文档 §9.3

---

## 案例 49：BLE 项目失败 4 大根因 + Deloitte 30-40% 调试降（系统级失败模式）

### 现象

某 IoT 产品 BLE 部署后失败率高：

- 团队按模块割裂（固件 / 应用 / QA）
- 没人拥有系统级行为
- 出问题无 single owner
- 用户信任崩塌

Deloitte 数据：

- 架构良好组织：调试时间降 30-40%
- 发布后缺陷降 30-40%

### 4 大根因

```text
根因 1：缺乏系统级设计
  现象：BLE 当 checkbox feature
  后果：架构不支撑场景
  解决：
    - 跨固件 / 应用 / QA 协作
    - 系统级 owner
    - 架构 review 必走

根因 2：QA 遮蔽真实变量
  现象：QA 通过 ≠ 量产可靠
  原因：QA 环境与生产环境差异
  解决：
    - 现场实测
    - 24h 长时压力测试
    - 多场景覆盖

根因 3：应用架构难以调试与扩展
  现象：GATT 表随固件变更 → central 缓存陈旧
  后果：看似发现失败实则是缓存 bug
  解决：
    - GATT 表版本化
    - 强制 service change indication
    - central 缓存失效机制

根因 4：后台 / 真实应用状态重连断裂
  现象：iOS / Android 后台策略差异
  后果：通知节流 + 权限变更让 BLE 行为突变
  解决：
    - 双端同步状态
    - 定期重连
    - 服务发现 + 状态同步
```

### 实战改进（4 步）

```text
Step 1：建立系统级 owner
  - 任命 BLE 架构师
  - 跨团队 review
  - 责任明确

Step 2：双轨测试（lab + field）
  - lab 自动化
  - field 真实数据采集
  - 数据驱动决策

Step 3：GATT 版本化
  - service change 强制
  - central 缓存失效
  - 主动推送

Step 4：状态机显式
  - 应用 + BLE 状态分离
  - 异常 recovery
  - 远程诊断
```

### 复盘

- **4 大根因 = 团队级问题**（不是技术 bug）
- Deloitte 30-40% 调试降 = 数据支撑
- 系统级 owner = 第一要务
- 团队按模块割裂 = 必出问题
- GATT 缓存陈旧 = 隐性失败
- 状态机显式 = 长期维护关键

### 来源

- _Inbox/BLE-Bluetooth-LE-2026-09-10-candidates.md 候选 5
- Aubergine Solutions（IoT 产品设计咨询）
- Deloitte 数据

---

## 案例 50：EBYTE 遥控器产线断连 4 大根因（brownout 50mV 触发 nRF52）

### 现象

遥控器产线 1000 台抽测 90% 出现"按 5 次有 1-2 次无响应"（用户视角"丢键"），抓包显示：
- 连接建立正常，notify 链路通
- 触发动作瞬间 → 连接突发断开（supervision timeout 7.5ms）
- 重连成功率约 60%，剩下"卡死"需手动复位

### 抓包 + 根因（4 大根因）

#### 根因 1：电源纹波 → nRF52 brownout（**主因，60% 案例**）

按键触发瞬间 nRF52 从 sleep（<5 µA）跳到 TX +4 dBm（18 mA 瞬态）。电源纹波：
- 锂电池 3.0V 标称，+4dBm TX 瞬态下沉 >50mV → VCC < 2.85V 触发 nRF52 brownout
- BOR 触发后 softdevice 不会自动恢复 → 必须手动复位（按键长按 5s）
- **50 mV 阈值是 Nordic spec 第 38 章明确写**（不是经验值），所有 nRF52/53/52840 同样适用

#### 根因 2：2.4 GHz 拥堵

产线隔壁工位 Wi-Fi AP × 3 + 蓝牙耳机 + ZigBee 网关 = -30 dBm 强干扰。  
抓包显示 PER（packet error rate）从 lab 的 0.5% 涨到产线 8%：
- BLE channel map 39 信道中可用降到 15 个
- connection event 7.5ms 内多次重传 → supervision timeout 累加

#### 根因 3：PCB 天线 VSWR > 3.0 失谐

板端采用 PCB trace antenna（chip antenna 之外的低成本方案）：
- DFM 阶段未做 PNA 网络分析仪校准
- VSWR 实测 3.2（spec 应 < 2.0）
- 反射损耗让 +4 dBm 实际只剩 +0 dBm 到空间
- 链路预算从设计 78 dB 跌到 ~62 dB，2m 内就触发 sensitivity edge

#### 根因 4：连接参数不当

application layer 设 connection interval 7.5ms（最快），但 slave latency = 4：
- 实际平均 30ms 才一次窗口
- 按键事件靠 polling 捕获 → 用户感"丢键"
- 同时 application 写 notify 频率 10Hz，超出 MTU 排队能力

### 定位（4 步法）

```text
Step 1：电源纹波定位
  - 示波器探头打 VCC（电池正极 PCB 端）
  - TX 触发时记录 Vmin
  - 判断：Vmin < 2.85V → root cause 1 命中

Step 2：频谱定位
  - 频谱仪看 2.4 GHz 占用
  - 或抓包看 channel map 有效信道数
  - 判断：有效信道 < 20 → root cause 2 命中

Step 3：天线定位
  - PNA 网络分析仪测 S11
  - VSWR > 2.0 → root cause 3 命中
  - 用铜箔调匹配 / 改 chip antenna 备选

Step 4：连接参数定位
  - 抓 connection interval / slave latency
  - application write notify 频率 vs 实际 throughput
  - 调 latency → 0 + interval 7.5ms
```

### 修复

| 根因 | 修复手段 | 验证 |
| --- | --- | --- |
| 1 brownout | 加 100µF 电容 + LDO 前置 + 限 TX 功率 0 dBm | 示波器 Vmin > 2.9V |
| 2 拥堵 | 频谱避让 + AFH（adaptive frequency hopping）打开 | channel map 有效 > 30 |
| 3 VSWR | 重画天线 + 调匹配网络 + 加 conductive shielding 罩 | VSWR < 1.8 |
| 4 参数 | slave latency → 0 + interval 7.5ms | 1m 距离丢包率 < 0.1% |

### 复盘

- **90% 产线断连根因是硬件 + RF 物理层**（不是协议 bug）
- 跌落 >50 mV 触发 brownout 是 nRF52 硬 spec，所有 nRF52 系列适用
- 表格化诊断矩阵可复用：4 步法 + 4 根因 → 任何 BLE 产线问题都从这 4 维切入
- **PCB 天线省钱是假省钱**——VSWR 失谐的链路预算损失不是软件能补的

### 来源

- _Inbox/BLE-Bluetooth-LE-2026-09-12-candidates.md 候选 2
- EBYTE 工业 BLE 模块厂商 blog

---

## 案例 51：STM32 主机 HCI 0x10 硬件错误 + ISR 延迟（SysTick 优先级倒置）

### 现象

STM32F4 主机 UART 接蓝牙模块（NRF52/CSR8811），偶发（每天 1-3 次）出现：
- HCI log 突然打 `HCI_HARDWARE_ERROR_EVENT (0x10)` 事件
- 紧跟 ISR 延迟 50-200ms 抖动
- FreeRTOS 任务卡死 / 随机崩溃
- 重启后正常，无明显规律

### 抓包 + 根因（4 大根因）

#### 根因 1：ISR 内 `HAL_Delay` → SysTick 优先级倒置（**最常见，70%**）

```c
void USART1_IRQHandler(void) {
    if (USART1->SR & USART_SR_RXNE) {
        uint8_t b = USART1->DR;
        hci_rx_buf[hci_rx_idx++] = b;
        HAL_Delay(1);  // ❌ ISR 内调 SysTick 延时
    }
}
```

- SysTick 中断优先级 = 最低（默认 15）→ 嵌套在 USART1 ISR 内被自己阻塞
- HAL_Delay 死等 SysTick downcounter → 1ms 实际等了 5-10ms
- 期间 USART FIFO 溢出 → 蓝牙模块重发 → 主机 HCI 帧错位

#### 根因 2：关中断超字节间隔 → HCI 帧错位

```c
__disable_irq();  // 关全局中断
memcpy(dst, src, len);  // 拷贝 200+ 字节
__enable_irq();
```

- UART @ 115200 baud 单字节 87 µs
- 拷 200 字节 ≈ 17 ms > UART 1 字节间隔 87 µs
- 关中断期间蓝牙模块来 5+ 字节 → RXNE 丢失 → HCI 帧解析错位 → 0x10 hardware error

#### 根因 3：NVIC 分组错（preemption vs sub-priority）

```c
HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_4);  // 4 bit preemption, 0 sub
HAL_NVIC_SetPriority(USART1_IRQn, 5, 0);            // preemption 5
HAL_NVIC_SetPriority(SysTick_IRQn, 0, 0);           // preemption 0  ← 错！
```

- SysTick preemption 0 = 最高优先级 → 任何 ISR 内都能嵌套进 SysTick
- 应设 SysTick preemption = 15（最低），让 USART 优先响应

#### 根因 4：阻塞 printf 在 ISR / 任务

```c
void hci_event_cb(uint8_t *evt, uint16_t len) {
    printf("HCI: %02x %02x %02x\n", evt[0], evt[1], evt[2]);  // ❌ 阻塞
}
```

- printf → 格式化 → UART 阻塞输出（数 ms 级）
- 如果在 ISR 或 FreeRTOS 高优先级任务 → 其他任务饥饿
- HCI 事件堆积 → 蓝牙模块看主机无应答 → 触发 0x10

### 定位（4 步法）

```text
Step 1：抓 Hardware Code
  - 0x10 错误码解析（看 spec 表 5.2）
  - 确定是 HCI 协议层错位还是真硬件坏

Step 2：GPIO 测 ISR 延迟
  - ISR 入口 GPIO 拉高，出口拉低
  - 示波器测脉宽 = ISR 耗时
  - 期望 < 50 µs，实际 1-200 ms → 命中根因 1 或 4

Step 3：硬件信号
  - 逻辑分析仪抓 UART TX/RX + flow control RTS/CTS
  - 看 RX 字节间隔 vs 期望 baud rate
  - 异常间隔 → 命中根因 2

Step 4：代码审查
  - 搜 HAL_Delay 在 ISR / __disable_irq 时长 / printf 在中断
  - NVIC priority 配置
```

### 修复

| 根因 | 修复 | 验证 |
| --- | --- | --- |
| 1 ISR 阻塞 | 用 RTOS queue + 信号量代替 `HAL_Delay`，ISR 只 enqueue | GPIO 测 ISR < 20 µs |
| 2 关中断 | 拆为小块 + 开中断窗口，或用 DMA + double buffer | UART 无 RX 丢失 |
| 3 NVIC 分组 | SysTick preemption 15，USART preemption 5 | `__get_IPSR()` 检查 |
| 4 阻塞 printf | 用 ringbuffer + 低优先级 task 异步刷 | task monitor 无饥饿 |

### 复盘

- **修 ISR 阻塞 > 改硬件优先级**——软件改动 ROI 远高于硬件 rework
- 排查序：Hardware Code → ISR 延迟波形 → 硬件信号 → 代码审查（4 步缺一不可）
- 覆盖 FreeRTOS 随机死机的根因排查（**80% 随机死机是 HCI 帧错位**）
- **中文资源**最完整可抄代码的就是 sheratonhq 这篇——STM32 蓝牙开发必读

### 来源

- _Inbox/BLE-Bluetooth-LE-2026-09-12-candidates.md 候选 4
- sheratonhq 技术 blog（中文 HCI 实战）

---

## 案例汇总

| # | 现象 | 根因 | 难度 |
| --- | --- | --- | --- |
| 1 | RTL8762E 配对 DoS | SMP 状态机 sequencing 错 | 中（CVE） |
| 2 | 0x3E 断开 | Wi-Fi 干扰 + 同步包丢失 | 低 |
| 3 | nRF51 ADC 干扰晶振 | 内部耦合 | 中 |
| 4 | Bonding 残留 | flash 布局错 | 中 |
| 5 | Notify 没启动 | CCCD 没写 | 低 |
| 6 | 7.5ms 烧电 | 连接参数没优化 | 低 |
| 7 | 0x3D MIC 误读 | 错误码方向错 | 中 |
| 8 | 距离近 | 天线匹配差 | 中 |

## 关联文档

- `bus/ble.md` 主题入口
- `bus/ble-practical.md` 调试流程速查
- `bus/ble-deep-dive.md` 协议栈深挖
- `bus/ble-index.md` 主题地图 + 导航
