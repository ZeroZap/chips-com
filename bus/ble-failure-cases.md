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
