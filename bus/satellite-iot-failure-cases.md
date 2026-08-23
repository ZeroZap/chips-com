# Satellite-IoT 产线实战案例库

## 目标

把卫星 IoT 常见的 5 大路线（NB-IoT NTN / 北斗短报文 / Iridium SBD / Starlink IoT / Garmin inReach）产线失败案例写成案例库。每个案例：

- 现象（现场）
- 抓包 / 抓 log（判断）
- 定位（根因）
- 修复（代码 / 硬件 / 配置）
- 复盘（如何预防）

案例来源：_Inbox/ 候选素材 + 实战复盘 + 客户返修。

---

## 案例 1：NB-IoT NTN 卫星搜不到，产线 100% 失败

### 现象

户外智能集装箱追踪器，使用移远 BG95-M3 + NTN 固件。量产 500 台，到户外开阔天空测试，**全部搜不到卫星**。终端 log 显示：

```text
+CFUN: 1
+CEREG: 0  // 始终 NOT REGISTERED
```

### 抓包

QXDM 抓 NB-IoT NTN NAS 信令：

```text
终端 → AT+COPS=?
模组:  +COPS: (3,"46000","46000","46000",9),(0-4),(0-2)
        // 仅扫到地面 PLMN 46000
        // 没有任何 NTN PLMN

模组 log 显示 SIB-NTN 接收：
  SIB-NTN: Band n255, freq 1626.5 MHz
  Ephemeris: <空>  ← 星历为空
  CellSpecificKoffset: 0
```

**关键证据**：QXDM log 显示 `Ephemeris: <空>`，即终端根本收不到有效的 NTN 星历。

### 定位

**根因**：

```text
1. 量产前未做"卫星入网"回归测试
2. 移远 BG95-M3 的 NTN 固件需要运营商 SIM 卡（含 NTN 入网凭证）
3. 量产时使用的 USIM 卡是地面 NB-IoT 卡，没有 NTN 业务授权
4. 即使地面 PLMN 扫到，没有 NTN 入网凭证，卫星注册失败
5. SIB-NTN 收到了，但 PLMN 不匹配 → 模组忽略
```

**关键参数**：3GPP R17 NTN 终端必须使用 NTN 专用 USIM 卡（含 SUPI（Subscription Permanent Identifier，用户永久标识符）/ K 凭证），普通 NB-IoT 卡无法用于 NTN。

### 修复

```c
// 1. 量产卡必须换 NTN 专用 USIM
//    联系运营商开通 NTN 业务 + NTN APN

// 2. 模组固件升级（移远 BG95-M3 必须 v2.4+ NTN 固件）
//    检查 AT+QGMR 返回固件版本

// 3. 应用层加预检：上电时检测 USIM 卡类型
int check_ntn_usim(void) {
    char iccid[20] = {0};
    AT_GetICCID(iccid);
    if (strncmp(iccid, "89860", 5) == 0) {
        // 中国电信 NTN 卡前缀（示例）
        return 1;
    }
    return 0;
}

// 4. 模组重置 USIM 卡权限
AT+QSIMDET=1   // 启用 SIM 检测
AT+QSIMSTAT=1  // 启用 SIM 状态通知
```

**临时方案**：

```text
1. 在户外实测前，确认 USIM 卡支持 NTN
2. 用 QXDM 抓 SIB-NTN，看 Ephemeris 是否非空
3. 看 +CEREG: 5 状态（roaming）+ +CEREG: 1（home）→ 注册成功
```

### 复盘

- **量产前必做"卫星入网回归测试"**：用真实 NTN USIM 卡 + 真实卫星测试
- **USIM 卡区分**：地面 NB-IoT 卡和 NTN 卡物理同尺寸但业务不同，库存必分区
- **模组固件版本**：BG95-M3 NTN 固件有版本要求，老固件不识别 NTN PLMN
- **SIB-NTN 接收 ≠ 入网成功**：必须 +CEREG: 1 或 5 才算

### 来源

- _Inbox/Satellite-IoT-2026-08-01-candidates.md 候选 1
- 移远 BG95-M3 NTN 固件升级说明
- 3GPP TS 23.122 NTN 终端要求

---

## 案例 2：北斗短报文"频度超限"导致产线集体失败

### 现象

户外测绘设备，使用华力创通 HWA-RDSS-101 模组。量产 200 台，户外实测时**所有设备发送北斗短报文失败**，模组返回 `RDSS_TX_FREQ_LIMIT`。

### 抓包

```text
模组串口 log:
AT+TX=...     // 用户发短报文
+TX OK
+SEND_FAIL: 0x04  // RDSS_TX_FREQ_LIMIT

模组内部 log:
  - 第一次发送: 14:30:12 成功
  - 第二次发送: 14:30:42 成功（间隔 30 s）
  - 第三次发送: 14:30:55 失败（间隔 13 s）
    → 触发"频度超限"
```

**关键证据**：模组返回错误码 0x04，查询手册为"RDSS_TX_FREQ_LIMIT"，普通卡入站频度限制 1 min / 1 条。

### 定位

**根因**：

```text
1. 普通北斗 RDSS 卡入站频度限制：
   - 1 min / 1 条（标准普通卡）
   - 1 s / 1 条（升级卡，需申请）
2. 产线测试时未考虑频度限制
3. 测试脚本连续发，触发频度超限
4. 户外定位 + 短报文组合测试时，定位和短报文分开走 RDSS 入站
5. 短报文发送失败 → 定位数据也丢失
```

### 修复

```c
// 1. 应用层加频度控制
static uint32_t g_last_tx_tick = 0;
#define RDSS_TX_MIN_INTERVAL_MS  65000  // 65 s（留 5 s 余量）

int rdss_send_packet(const uint8_t *data, uint16_t len) {
    uint32_t now = k_uptime_get_32();
    if (now - g_last_tx_tick < RDSS_TX_MIN_INTERVAL_MS) {
        // 频度超限，排队
        log("RDSS TX rate limit, wait %d ms",
            RDSS_TX_MIN_INTERVAL_MS - (now - g_last_tx_tick));
        return -1;
    }

    int ret = at_send_rdss(data, len);
    if (ret == 0) {
        g_last_tx_tick = now;
    }
    return ret;
}

// 2. 产线测试脚本：电文合并 + 频度错峰
// 每次测试只发 1 条，间隔 90 s
for (int i = 0; i < test_count; i++) {
    rdss_send_packet(test_data[i], 100);
    if (i < test_count - 1) {
        k_msleep(90000);  // 1.5 min 间隔
    }
}

// 3. 升级卡申请（量产优先）
// 联系北斗运营方申请升级卡（频度 1 s / 1 条，电文长度 1680 汉字）
```

### 复盘

- **北斗卡分等级**：普通卡 / 升级卡 / 集团卡，频度限制差异大
- **产线测试脚本必加频度控制**：与生产环境行为一致
- **RDSS 是双向信令**：入站 + 出站都占用通道，频度要算双程
- **频度限制文档化**：写入固件 + 测试脚本注释，避免重复踩坑

### 来源

- _Inbox/Satellite-IoT-2026-08-01-candidates.md 候选 2
- 北斗运营方卡管理规范
- 华力创通 HWA-RDSS 手册 §3.4

---

## 案例 3：Iridium SBD `+SBDI: 4` 网络未注册，产线 30% 失败

### 现象

户外资产追踪器，使用 Iridium 9602 模组。量产 1000 台，户外实测时约 300 台返回 `+SBDI: 4, x, 0, 0, 0, 0`（MO status=4，Gateway not available），其余 700 台成功。

### 抓包

Iridium Analyzer 抓 SBD MO 流程：

```text
正常流程:
  AT+SBDWB=100
  READY
  <写 100 字节 payload>
  AT+SBDI
  +SBDI: 0, 1234, 0, 0, 0, 0  // MO status=0 SUCCESS

异常流程:
  AT+SBDWB=100
  READY
  <写 100 字节 payload>
  AT+SBDI
  +SBDI: 4, 1234, 0, 0, 0, 0  // MO status=4 Gateway not available

模组 log:
  Failed to register SBD gateway
  +SBDREG: 0
  Signal: 0
```

**关键证据**：异常设备 `+SBDREG: 0`（未注册），信号强度 0（最低），表明模组根本没附网。

### 定位

**根因**：

```text
1. Iridium 9602 模组首次使用必须注册 IMEI
2. 量产 1000 台 IMEI 通过 Excel 表格批量录入
3. 录入时部分 IMEI 多 1 位（粘贴错位），实际只录入了 980 个
4. 未录入的 20 台设备 IMEI 在 Iridium 网关侧不存在
5. 模组搜星 + 附网 → 网关侧找不到 IMEI → 拒绝 → MO status=4

补充原因：
6. 量产测试场地在室内，卫星信号被屏蔽，部分设备信号 0
7. 室内测试本身就不可靠，需要户外测试
```

**根因 1 修复**：1000 台 IMEI 重新核对，实际是 Excel 粘贴错位。
**根因 2 修复**：测试场地必须户外开阔天空。

### 修复

```python
# 1. IMEI 入网注册脚本（自动化）
# Iridium 提供批量注册 API
import csv

def register_imei_batch(csv_path):
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            imei = row['imei'].strip()
            assert len(imei) == 15, f"IMEI 长度错: {imei}"
            response = iridium_api.register(imei, ...)
            if response.status != 'success':
                log(f"IMEI {imei} 注册失败: {response.error}")
                return False
    return True

# 2. 应用层：检测 +SBDI 返回码
int handle_sbdi(int mo_status, int momsn) {
    switch (mo_status) {
    case 0:
        log("MO success, MOMSN=%d", momsn);
        g_momsn = momsn;  // 持久化
        return 0;
    case 4:  // Gateway not available
        log("Gateway not available, retry");
        k_msleep(5000);
        return sbd_send_mo_retry();  // 重试
    case 12:  // IMEI not provisioned
        log("IMEI 未注册!");
        assert(0);  // 立即 fail，提示 IMEI 问题
    default:
        log("MO fail, status=%d", mo_status);
        return -1;
    }
}

// 3. 模组重置 + 重新搜星（自动恢复）
int sbd_recover(void) {
    AT_Send("AT+SBDDET");
    k_msleep(2000);
    AT_Send("AT+SBDREG");
    return 0;
}
```

### 复盘

- **IMEI 必须逐一核对**：批量导入 Excel 容易粘贴错位，写脚本 + 断言
- **Iridium 首次使用必须注册**：注册后 24 h 生效，量产前 1 周完成
- **室内测试不可靠**：必须户外开阔天空
- **`+SBDI: 4` 第一反应是 IMEI 未注册**：不是网络问题
- **`+SBDI: 12` 是 IMEI 错误**：assert 立即 fail，不要 retry

### 来源

- _Inbox/Satellite-IoT-2026-08-01-candidates.md 候选 3
- Iridium SBD Developer Guide §5.3
- 客户量产复盘

---

## 案例 4：NB-IoT NTN Doppler 未补偿，PRACH 接入失败

### 现象

户外环境监测终端，使用移远 BG95-M3 + 1.5 GHz 全向天线。量产 100 台，**60 台 NTN 搜星成功（看到 SIB-NTN），但 PRACH 接入失败**，返回 `+CEREG: 0`，`+CME ERROR: 515`（ABORTED）。

### 抓包

QXDM 抓 RRC 信令：

```text
SIB-NTN 接收: SUCCESS
  - Ephemeris: 完整
  - CellSpecificKoffset: 12345 (chips)
  - Sfn: 100

PRACH 发射:
  PreambleFormat: 0
  Frequency offset: 0  ← 关键！Doppler 未补偿
  Timing offset: 0     ← 关键！RTD 未补偿

PRACH 响应:
  No response
  Random access problem

模组 log:
  PRACH TX at 14:30:12
  Expected RX at 14:30:12.020 (RTD compensation missing)
  No response within 8 s
  → +CME ERROR: 515 ABORTED
```

**关键证据**：模组发射时 `Frequency offset: 0` 和 `Timing offset: 0`，Doppler 和 RTD 都没有预补偿。

### 定位

**根因**：

```text
1. 移远 BG95-M3 模组固件 v2.3 不支持 NTN Doppler pre-compensation
2. 升级到 v2.4 后才支持
3. 量产烧录时固件版本没核对，烧的是 v2.3
4. SIB-NTN 收到了，但模组没能力用
5. PRACH 频率未补偿 → 卫星接收时频偏超门限 → 无响应
```

**3GPP 规范**：3GPP TS 36.321 §5.1 规定 NTN 终端必须做 Doppler / Timing pre-compensation。

### 修复

```text
1. 升级模组固件到 v2.4+
   AT+QGMR
   BG95-M3 v2.4
   Build: 2024-08-12

2. 重新烧录所有模组

3. 升级后验证：
   AT+CEREG=5
   AT+COPS=?
   +COPS: (3,"xxx","xxx","xxx",9)
   AT+CGATT=1
   OK
   +CEREG: 1  // 注册成功
```

**应用层加固**：

```c
// 模组固件版本预检
int check_modem_firmware(void) {
    char fw[32] = {0};
    AT_GetModemVersion(fw);

    if (strstr(fw, "BG95-M3") && atof(fw + 8) < 2.4) {
        log("BG95-M3 NTN 固件版本 %s 低于 2.4，必须升级", fw);
        return -1;
    }
    return 0;
}
```

### 复盘

- **模组固件版本是关键参数**：NTN 固件版本号必须 ≥ 厂商最低要求
- **量产烧录时 100% 校验**：AT+QGMR 返回版本号，与 BOM 对照
- **PRACH 接入失败先看 Doppler 补偿**：SIB-NTN 收到 ≠ 能用
- **模组厂提供的"NTN Ready"清单**：升级前先查清单

### 来源

- _Inbox/Satellite-IoT-2026-08-01-candidates.md 候选 4
- 移远 BG95-M3 固件升级说明
- 3GPP TS 36.321 NTN random access procedure

---

## 案例 5：Iridium SBD MOMSN 越界，密钥失效

### 现象

户外油气管道监测器，使用 Iridium 9602。设备运行 18 个月后，远程 OTA 升级时 SBD MO 全部失败，返回 `+SBDI: 7, x, ...`（MOMSN out of range）。

### 抓包

```text
模组 log:
  AT+SBDI
  +SBDI: 7, 65535, 0, 0, 0, 0  // MO status=7, MOMSN=65535
  MOMSN overflow, message dropped

模组 eMMC 数据:
  MOMSN 起始: 0
  当前: 65535（运行 18 个月，每天 10 条）
  → 65535 后归零 → 中心站认为重放 → 拒绝
```

**关键证据**：MOMSN 计数器达到 65535 后归零（16-bit 溢出），Iridium 中心站认为重放攻击，拒绝所有消息。

### 定位

**根因**：

```text
1. MOMSN 是 16-bit 计数器，理论上限 65535
2. 模组每天发 10 条，65535/10 = 6553 天 ≈ 18 年（远不到）
3. 但模组在 18 个月内累计了 50 万条（含 OTA 重试）
4. 重试时 MOMSN 仍递增，没去重
5. 计数器溢出 → 归零 → 中心站拒绝
```

**Iridium 规范**：MOMSN 必须单调递增，从 0 → 65535 后保持 65535（不回 0），等待 24 h 中心站重置窗口。

### 修复

```c
// 1. 应用层：MOMSN 持久化 + 监控
static uint16_t g_momsn = 0;

int sbd_send_mo_persist(const uint8_t *data, uint16_t len) {
    // 从 fds 读取 MOMSN
    if (fds_load_u16("momsn", &g_momsn) != 0) {
        g_momsn = 0;
    }

    if (g_momsn == 0xFFFF) {
        // 即将溢出：保持 65535
        g_momsn = 0xFFFF;
        // 通知中心站重置
        log("MOMSN overflow, notify center");
        send_admin_reset_request();
    } else {
        g_momsn++;
    }

    // 写回 fds
    fds_save_u16("momsn", g_momsn);

    int ret = sbd_send_mo(data, len, g_momsn);
    return ret;
}

// 2. 模组 MOMSN 同步：每次启动从模组读取 + 持久化
int sync_momsn(void) {
    char resp[32];
    AT_Send("AT+SBDMTA=0");
    k_msleep(100);
    AT_Send("AT+SBDS");  // 查询 MOMSN
    AT_GetResponse(resp);
    if (strncmp(resp, "+SBDS:", 6) == 0) {
        uint16_t modem_momsn = atoi(resp + 6);
        if (modem_momsn > g_momsn) {
            g_momsn = modem_momsn;
            fds_save_u16("momsn", g_momsn);
        }
    }
    return 0;
}
```

**硬件加固**：

```text
- 用 STM32 RTC BKP 寄存器持久化 MOMSN（不掉电）
- fds（Flash Data Storage）必须擦 application 时不擦 bonding
- 量产时记录初始 MOMSN=0，OTA 时不能复位
```

### 复盘

- **MOMSN 是 16-bit 计数器**：必须监控，溢出前通知中心站
- **重试 MOMSN 必须递增**：失败也 +1，不能复用
- **持久化 MOMSN 到 fds / RTC BKP**：掉电不丢
- **OTA 不能复位模组**：会丢 MOMSN
- **24 h 中心站重置窗口**：MOMSN=0xFFFF 后保持，等待重置

### 来源

- _Inbox/Satellite-IoT-2026-08-01-candidates.md 候选 5
- Iridium SBD Developer Guide §5.4
- 客户 18 个月运行后复盘

---

## 案例 6：北斗短报文"卡未激活"导致入网失败

### 现象

户外救援设备，使用中斗微星 ZD-V100 模组。量产 500 台，户外测试时**所有设备入网失败**，模组返回 `RDSS_AUTH_FAIL`。

### 抓包

```text
模组串口 log:
  AT+RDSSREG
  +RDSSREG: 0  // 未入网

  模组 log:
  Sending registration request
  Reading RDSS card info
  Card status: 0x03 (CARD_NOT_ACTIVATED)
  → 拒绝入网
```

**关键证据**：模组读卡返回 `Card status: 0x03`（未激活），不是卡错或密钥错。

### 定位

**根因**：

```text
1. 北斗 RDSS 卡出厂后必须通过"中心站激活"流程才能使用
2. 厂商发的 500 张卡都是"出厂态"（未激活）
3. 量产时未走"中心站激活"流程
4. 模组正常，但卡未激活 → 入网失败
5. 与 SIM 卡不同：SIM 卡插入即用，RDSS 卡必须先激活
```

**北斗运营方规范**：RDSS 卡需要中心站下发激活指令（带 IMEI 列表），卡收到激活指令后才进入 active 态。

### 修复

```text
1. 量产前批量激活：
   - 提供 IMEI 列表给北斗运营方
   - 运营方下发激活指令
   - 24 h 内生效
   - 激活后卡状态 = 0x01 (ACTIVE)

2. 模组状态机：未激活时自动告警
   - 上电读卡 → 状态 0x03
   - 应用层告警："北斗卡未激活，请联系运营方"
   - 写入 log，便于返修定位

3. 量产测试用"测试卡"：
   - 测试卡由运营方预激活
   - 量产时用测试卡做功能测试
   - 出货前换"生产卡" + 激活
```

**应用层**：

```c
// 检查 RDSS 卡状态
int check_rdss_card_status(void) {
    uint8_t status = 0;
    at_rdss_get_card_status(&status);

    switch (status) {
    case 0x01:
        log("RDSS card ACTIVE");
        return 0;
    case 0x03:
        log("RDSS card NOT ACTIVATED");
        return -1;  // 提示运营方激活
    case 0x04:
        log("RDSS card SUSPENDED");
        return -2;
    default:
        log("RDSS card status 0x%02x", status);
        return -3;
    }
}
```

### 复盘

- **RDSS 卡必须激活**：不是插卡即用
- **量产前批量激活**：与运营方协作，IMEI 列表提前提交
- **测试卡 vs 生产卡分离**：测试卡预激活，量产用生产卡 + 激活
- **卡状态枚举化**：0x01 / 0x03 / 0x04 等，应用层处理

### 来源

- _Inbox/Satellite-IoT-2026-08-01-candidates.md 候选 6
- 北斗运营方卡管理规范
- 中斗微星 ZD-V100 手册

---

## 案例 7：Starlink IoT 频段未授权，模组无响应

### 现象

海外户外资产追踪项目，使用某 LTE Cat-1 模组（号称"Starlink Ready"）。实际发货到美国，户外测试**完全无信号**，模组返回 `+CEREG: 0`，扫星失败。

### 抓包

```text
模组 log:
  AT+COPS=?
  +COPS: (3,"310260","310260","T-Mobile",7)  // 扫到 T-Mobile PLMN
  +CEREG: 5  // 注册中
  
  ... 30 s ...
  +CEREG: 3  // 注册失败

频谱仪扫频:
  1.9 GHz 段（Starlink Direct to Cell）:
  卫星下行: -120 dBm
  卫星上行: 0 dBm（模组未发射）
  → 模组未在 1.9 GHz 段发射
```

**关键证据**：模组没在 Starlink Direct to Cell 频段（1.9 GHz T-Mobile 段）发射，仍在常规 LTE 频段尝试。

### 定位

**根因**：

```text
1. Starlink Direct to Cell 是 2024 Q1 商用
2. 模组厂"Starlink Ready"是指支持 1.9 GHz 频段硬件
3. 但需要 Starlink + T-Mobile 双方认证
4. 量产模组固件未带 Starlink 认证 profile
5. 即使硬件支持，软件上没激活 1.9 GHz 频段
6. → 模组在常规 LTE 频段扫，搜不到卫星
```

**Starlink 官方要求**：模组必须通过 Starlink 认证（包括固件、SIM、协议），否则无法接入 Starlink 卫星。

### 修复

```text
1. 联系模组厂确认 Starlink 认证状态
2. 升级到带 Starlink profile 的固件
3. SIM 卡换 Starlink 认证卡（T-Mobile IoT 卡）
4. 在 Starlink 覆盖区（美国本土）测试
5. 国内无法测试（Starlink 暂未覆盖）
```

**变通方案**：

```text
1. 短期：换 Iridium 9602 模组 + SBD 卡（覆盖全球）
2. 中期：等国内 NB-IoT NTN 商用 + 国产模组
3. 长期：Starlink 认证模组 + T-Mobile 卡
```

### 复盘

- **"Ready"不等于"已认证"**：硬件 Ready 与商用 Ready 不同
- **Starlink 认证流程严格**：模组 + 固件 + SIM + 网络协议
- **海外项目先确认卫星可用性**：美国用 Starlink，欧洲用 Inmarsat，国内用北斗
- **新卫星网络发布后 6 个月内谨慎**：认证模组少，固件不稳定

### 来源

- _Inbox/Satellite-IoT-2026-08-01-candidates.md 候选 7
- SpaceX + T-Mobile Direct to Cell 公告
- 客户海外项目复盘

---

## 案例 8：北斗短报文"电文超长"导致发送失败

### 现象

户外环境监测设备，采集温度/湿度/PM2.5 数据 + GPS 位置 + 时间戳 + 设备 ID，**总电文长度 1200 汉字**（超 1000 汉字），每次发送失败。

### 抓包

```text
模组串口 log:
  AT+TX="<1200 汉字>"
  +CME ERROR: 304  // 电文长度超限

  模组 log:
  电文长度: 1200 字符
  卡类型: 普通卡
  普通卡限制: 1000 字符
  → 超 200 字符，拒发
```

**关键证据**：电文长度 1200 > 普通卡限制 1000，模组拒绝。

### 定位

**根因**：

```text
1. 普通北斗 RDSS 卡电文长度上限 1000 汉字
2. 升级卡支持 1680 汉字（需申请）
3. 应用层未做电文分包
4. 数据量超出卡限制 → 失败
```

### 修复

```c
// 1. 应用层：电文分包
int rdss_send_long_packet(const uint8_t *data, uint32_t total_len) {
    const uint32_t MAX_LEN = 1000;  // 普通卡

    if (total_len <= MAX_LEN) {
        return rdss_send_single(data, total_len);
    }

    // 分包
    uint32_t sent = 0;
    uint16_t seq = 0;
    while (sent < total_len) {
        uint32_t chunk = MIN(MAX_LEN - 10, total_len - sent);
        // 头部: 4 字节 seq + 2 字节 total + 4 字节 offset
        uint8_t packet[1010];
        memcpy(packet, &seq, 4);
        memcpy(packet + 4, &total_len, 2);
        memcpy(packet + 6, &sent, 4);
        memcpy(packet + 10, data + sent, chunk);

        int ret = rdss_send_single(packet, chunk + 10);
        if (ret != 0) {
            return ret;
        }
        sent += chunk;
        seq++;
        k_msleep(70000);  // 1 min+ 频度限制
    }
    return 0;
}

// 2. 接收端：电文重组
int rdss_recv_reassemble(uint8_t *out, uint32_t *out_len) {
    // 等所有 seq 收齐
    // 校验 total / offset
    // 拼成完整电文
    // ...
}

// 3. 升级卡申请（更优）
// 联系北斗运营方升级为 1680 汉字卡
```

### 复盘

- **电文长度限制卡类型**：1000（普通）/ 1680（升级）/ 更大（集团）
- **应用层必做分包**：长电文必须切分
- **频度限制叠加**：分包越多，频度压力越大
- **设计阶段考虑电文长度**：先评估数据量 + 卡类型，再设计
- **压缩算法**：电文压缩可减少长度（如 LZ4、gzip）

### 来源

- _Inbox/Satellite-IoT-2026-08-01-candidates.md 候选 8
- 北斗运营方卡管理规范
- 户外监测项目复盘

---

## 案例 9：卫星过顶窗口短，电文丢失

### 现象

户外极地科考设备，使用 Iridium 9602 模组。在南极中山站，纬度 69°S，**短报文丢失率 30%**。

### 抓包

```text
模组 log:
  14:30:12  AT+SBDI  →  +SBDI: 1, x, ... (Timeout)
  14:32:15  AT+SBDI  →  +SBDI: 0, 100, ... (Success)
  14:35:30  AT+SBDI  →  +SBDI: 1, y, ... (Timeout)

  Iridium 过顶预测:
    14:30 - 仰角 5°  → 窗口期 8 min
    14:32 - 仰角 45° → 窗口期 4 min
    14:35 - 仰角 2°  → 窗口期 2 min
```

**关键证据**：低仰角（< 10°）时链路差，丢包率高。高仰角（> 30°）时稳定。

### 定位

**根因**：

```text
1. 极地地区 LEO 卫星仰角变化快（多普勒变化率 ±0.5 Hz/s × 3 = ±1.5 Hz/s）
2. 高纬度 Iridium 卫星波束密度下降
3. 仰角 < 10° 时，路径损耗 + 多径，链路预算不足
4. 模组默认"立刻发送"，不挑仰角
5. → 30% 短报文丢在高仰角转换到低仰角时段
```

### 修复

```c
// 1. 应用层：监控卫星仰角 + 挑窗口
int sbd_send_windowed(const uint8_t *data, uint16_t len) {
    // 查询当前卫星仰角（GPS + 卫星预测）
    for (int retry = 0; retry < 5; retry++) {
        float elevation = get_satellite_elevation();
        if (elevation >= 20.0) {
            // 仰角足够，立即发送
            return sbd_send_mo(data, len);
        }
        // 仰角不够，等待
        k_msleep(20000);  // 20 s
    }
    return -1;  // 5 次都没合适仰角
}

// 2. 仰角预测：用 Iridium 公开的 TLE（Two-Line Element，两行根数）数据
// 库：SGP4（Simplified General Perturbations 4）
#include "sgp4.h"

float predict_elevation(double lat, double lon, double alt) {
    // 用当前 TLE + SGP4 算下一颗过顶卫星
    // ...
    return elevation;
}

// 3. 频度策略：每 5 min 检测一次，仰角达标才发
//    即使失败，下次 5 min 后还有机会
```

**硬件加固**：

```text
- 极地用高增益定向天线（12 dBi）
- 极轴自动跟踪（不实用）
- 或加电控倾角平台（电动调整俯仰）
- 普通户外可省
```

### 复盘

- **极地是高难度场景**：卫星覆盖密度低，仰角变化快
- **仰角阈值**：20°+ 稳定，10° 以下基本丢
- **卫星预测库**：SGP4 + TLE（公开数据）
- **窗口期短不可控**：应用层必须挑窗口
- **极地设备选 Iridium**：覆盖好于其他网络

### 来源

- _Inbox/Satellite-IoT-2026-08-01-candidates.md 候选 9
- Iridium SBD Developer Guide §5.6
- 南极科考站实战复盘

---

## 案例汇总

| # | 现象 | 路线 | 根因 | 难度 |
| --- | --- | --- | --- | --- |
| 1 | NTN 卫星搜不到 | NB-IoT NTN | USIM 卡不是 NTN 卡 | 低 |
| 2 | 频度超限发送失败 | 北斗短报文 | 1 min/1 条限制 | 低 |
| 3 | +SBDI: 4 网络未注册 | Iridium SBD | IMEI 未注册 | 中 |
| 4 | PRACH 接入失败 | NB-IoT NTN | Doppler 未补偿 | 高 |
| 5 | MOMSN 越界 | Iridium SBD | 16-bit 溢出 | 中 |
| 6 | 入网失败 | 北斗短报文 | 卡未激活 | 低 |
| 7 | Starlink 无信号 | Starlink IoT | 模组未认证 | 高 |
| 8 | 电文超长失败 | 北斗短报文 | 1000 汉字限制 | 低 |
| 9 | 极地丢包高 | Iridium SBD | 仰角低 | 高 |

## 关联文档

- `bus/satellite-iot.md` 主题入口
- `bus/satellite-iot-practical.md` 调试流程速查
- `bus/satellite-iot-deep-dive.md` 协议栈 / 链路预算深挖
- `bus/satellite-iot-index.md` 主题地图 + 导航
