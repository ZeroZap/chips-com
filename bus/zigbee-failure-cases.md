# ZigBee 产线实战案例库

## 目标

把产线常见的 ZigBee 通信失败、节点掉线、Rejoin 卡死、NCP crash、End Device 烧电、ZCL 误读等问题写成案例库。每个案例：

- 现象（现场）
- 抓包 / 抓 log（判断）
- 定位（根因）
- 修复（代码 / 硬件 / 配置）
- 复盘（如何预防）

案例来源：_Inbox/ 候选素材 + 实战复盘。

## 案例 1：CC2530 ReJoinRequest 概率性失败，密封水壶屏蔽信号抓包发现

### 现象

智能水表项目，TI CC2530 终端，电池供电。产线测试 100 台，30% 设备入网后反复掉线。掉线后 ReJoinRequest 失败，进入死循环。

### 抓包

密封水壶屏蔽信号法：

```text
设备放在密封水壶（屏蔽 RF）→ 模拟信号极差环境
TI Packet Sniffer 抓包 → 抓 ReJoin 完整流程
  1. 设备 Beacon Request
  2. 父节点 Beacon
  3. 设备 Rejoin Request
  4. 父节点验证 → 失败
  5. 设备等待 → 重新 Beacon Request
  6. 循环

根因定位：父节点返回 Rejoin Response 后，设备端 NLME 状态机
        → 概率性返回错误（不是协议错）
        → 跟信号强度无关
```

**复现规律**：

```text
前 5 次 ReJoin 全部成功
第 6 次起概率性失败
重置后又能成功 5 次
```

### 定位

CC2530 Z-Stack 的 NLME_ReJoinRequest 状态机 BUG：

```c
// 错实现（Z-Stack 1.x ~ 2.x）
void NLME_ReJoinRequest(uint16_t panId, uint8_t *extAddr) {
    // 状态机没正确处理 Orphan 后的 Rejoin
    if (nwkState == NWK_STATE_ORPHAN) {
        // 错：直接走 Association 流程
        NLME_JoinRequest(...);  // 不是 Rejoin
    }
    // 错：NV 残留 extAddr 没清
}

// 修复后
void NLME_ReJoinRequest(uint16_t panId, uint8_t *extAddr) {
    if (nwkState == NWK_STATE_ORPHAN) {
        // 1. 兜底：先 ZDO_MultipleJoinReq
        ZDO_MultipleJoinReq_t req;
        req.scanChannels = _NIB.scanChannels;
        req.scanDuration = _NIB.scanDuration;
        ZDO_InitDevice(...);
        // 2. NV 残留清
        osal_nv_delete(NV_NWK_NIB, ...);
        osal_nv_delete(NV_APS_USE_EXT_PANID, ...);
    }
    // 重新初始化 Rejoin 状态机
    nwkState = NWK_STATE_JOINING;
}
```

**根因汇总**：

1. NLME 状态机 Orphan → Rejoin 路径有 BUG
2. NV 残留致误关联邻居网关
3. flash PAN ID 没限定回原网络

### 修复

**修复 1：升级 Z-Stack**

```c
// Z-Stack 3.0.2 修复了 NLME Orphan→Rejoin 路径
// 见 Z-Stack 3.0.2 Release Notes
//   - Z-2190: NLME Rejoin 状态机在 Orphan 后错

// 应用层强制：
#if defined(ZSTACK_VERSION) && (ZSTACK_VERSION >= 300)
    // 3.0.2+ 已有修复
#else
    // 老版本应用层兜底
    osal_nv_delete(NV_NWK_NIB, sizeof(nwkIB_t));
    osal_nv_delete(NV_APS_USE_EXT_PANID, Z_EXTADDR_LEN);
#endif
```

**修复 2：应用层兜底 ZDO_MultipleJoinReq**

```c
// Orphan 失败 N 次 → 主动 MultipleJoinReq
#define ORPHAN_FAIL_THRESHOLD 3
static uint8_t orphan_fail_count = 0;

void nwkStateChangeCB(uint16_t nwkState) {
    if (nwkState == NWK_STATE_ORPHAN) {
        orphan_fail_count++;
        if (orphan_fail_count >= ORPHAN_FAIL_THRESHOLD) {
            orphan_fail_count = 0;
            // 兜底：触发 Multi-Join
            zAddrType_t dstAddr;
            dstAddr.addrMode = Addr16Bit;
            dstAddr.addr.shortAddr = 0xFFFC;
            // ... 调 ZDO_MultipleJoinReq
        }
    } else if (nwkState == NWK_STATE_END_DEVICE) {
        orphan_fail_count = 0;  // 入网成功清零
    }
}
```

**修复 3：NV 区域定期 GC**

```c
// 每次开机检查 NV 一致性
void checkNvConsistency(void) {
    uint16_t panId;
    if (osal_nv_read(NV_NWK_PANID, 0, sizeof(panId), &panId) == SUCCESS) {
        if (panId != EXPECTED_PANID) {
            // NV 残留 → 清
            osal_nv_delete(NV_NWK_NIB, sizeof(nwkIB_t));
            osal_nv_delete(NV_APS_USE_EXT_PANID, Z_EXTADDR_LEN);
        }
    }
}
```

**修复 4：密封水壶屏蔽法快速复现**

```text
产线 100% 测试：
  1. 设备放密封水壶 5 分钟
  2. 拿出水壶
  3. 触发 Rejoin
  4. 看是否成功（3 次内成功 → 合格）

调试环境 vs 产线环境差异大时，密封水壶屏蔽法是最快复现工具。
```

### 复盘

- **CC2530 是经典坑**，新设计强烈不推荐
- **NLME 状态机 BUG 必须用兜底机制**，不能只信协议栈
- **NV 残留必须定期 GC**，否则累积出莫名其妙问题
- **密封水壶屏蔽法是产线 100% 测试神器**
- **CC2538 / CC2652 才是替代方案**

### 来源

- _Inbox/ZigBee-2026-08-01-candidates.md 候选 1
- CSDN 月光 Linux 实战复盘

---

## 案例 2：zigbee2mqtt 50+ 设备 20% 随机离线

### 现象

智能家居客户，zigbee2mqtt 部署 50+ 设备（小米、Aqara、IKEA），20% 设备随机离线（断连），重启 zigbee2mqtt 后部分设备恢复。

### 抓包

```text
log 关键信息：
  - "Failed to execute LQI for ...."（LQI 邻居表查询失败）
  - "Device .... unavailable"（设备不可用）
  - "zigbee2mqtt: Restarting..."（服务自动重启）

mosquitto_pub/sub 状态：
  - 部分设备 availability 状态一直 "offline"
  - 实际设备上电正常
```

### 定位

**6 大故障分类**：

| 故障 | 现象 | 根因 |
| --- | --- | --- |
| USB 适配器权限/固件 | CC2531 启动慢、误报 | Z-Stack 3.0.x 之前固件 |
| 信号覆盖+QoS 缺失 | 边缘设备掉线 | 无 mesh 备份路径 |
| availability timeout 不当 | 偶发误报 | 默认 10 分钟太长 |
| MQTT 队列积压 | 离线时大量重发 | QoS 2 + retention |
| 自定义 converter 缺 | 新设备配对失败 | 需 fromZigbee/toZigbee |
| 设备固件 BUG | 部分设备反复掉线 | 厂商固件不成熟 |

**根因汇总**：

1. CC2531 USB 适配器固件太老（Z-Stack < 3.0.x）
2. availability timeout 配错，硬重试无效
3. 没有 backoff，失败后疯狂重试

### 修复

**修复 1：升级 USB 适配器固件**

```bash
# CC2531 必须 Z-Stack 3.0.x
# 推荐用 SONOFF Zigbee 3.0 USB Dongle Plus-P (CC2652P)
# 或 ZBOSS（推荐）

# 升级 CC2652P 固件
git clone https://github.com/Koenkk/Z-Stack-firmware
cd Z-Stack-firmware
./cc2538-bsl.py -p /dev/ttyUSB0 -e -w CC2652P_zigbee_2024xxxx.hex
```

**修复 2：availability + backoff 配**

```yaml
# zigbee2mqtt configuration.yaml
availability:
  active: {
    timeout: 60,         # 60s 离线算掉
    max_jitter: 0,
    backoff: 30          # 失败后 30s 退避
  }
  passive: {
    timeout: 300         # 被动设备 5 分钟
  }

advanced:
  cache_state: true       # 缓存状态
  cache_state_persistent: true
  transmit_power: 20      # 提高发射功率
  channel: 25             # 避 Wi-Fi 1
  network_key: GENERATE
```

**修复 3：自定义 converter**

```js
// 自定义 设备 converter
const fz = require('zigbee-herdsman-converters/converters/fromZigbee');
const tz = require('zigbee-herdsman-converters/converters/toZigbee');

const device = {
    zigbeeModel: ['lumi.sensor_magnet.magnet'],
    model: 'Aqara Door Sensor',
    vendor: 'Aqara',
    fromZigbee: [
        fz.aqara_opple,  // 标准转换器
        fz.aqara_door_state_simple,  // 自定义
    ],
    toZigbee: [
        tz.aqara_door_state,  // 自定义
    ],
};

module.exports = device;
```

**修复 4：场景管理**

```js
// zigbee2mqtt 设备离线时通知
const notification = {
    message: 'Device offline',
    title: 'Smart Home Alert',
};
mqtt.publish('zigbee2mqtt/alert', JSON.stringify(notification));
```

### 复盘

- **USB 适配器固件必须用最新版**（CC2652P > CC2531）
- **availability 是核心参数**，active vs passive 必须按设备类型分开
- **backoff 比硬重试有效**，失败后不要硬冲
- **fromZigbee/toZigbee converter** 是非标设备唯一通道
- **zigbee2mqtt 适合 100 设备以内**，再大要换专业方案（如 ZHA + Home Assistant）

### 来源

- _Inbox/ZigBee-2026-08-01-candidates.md 候选 2
- CSDN zigbee2mqtt 实战
- zigbee2mqtt GitHub Issue

---

## 案例 3：EFR32 NCP 模式 crash，SWO 抓 log 救场

### 现象

EFR32MG21 NCP 方案，zigbee 应用层跑主机 MCU。NCP 跑协议栈。偶发 crash，主机 MCU 通过 EZSP / CPC 与 NCP 通信时掉线。重启 NCP 后恢复，但根因无法定位。

### 抓包

```text
崩溃前 EZSP / CPC log：
  [ember.c:1234] emberSend(...) returned 0xE0 EMBER_ERR_FATAL
  [ezsp-frame.c:567] TX FIFO overflow
  [ezsp-frame.c:890] Resetting NCP

崩溃时：
  主机 → NCP: EZSP 帧（命令）
  NCP: 无响应
  主机: 监测 NCP 复位引脚 → 看到复位
```

**关键问题**：crash 时 NCP log 全部丢失，**无法复现 + 无法定位**。

### 定位

**EFR32 NCP 调试三大坑**：

1. **NCP 模式无 SoC 的 crash info 自动打印**
2. **assert/CRS/SW 重启原因无 print**
3. **没有 SWO 引脚 = 完全瞎抓**

**NCP 模式机制**：

```text
SoC 模式：
  协议栈在 MCU 内跑
  crash 时 IDE 抓 backtrace
  assert() 打印到 UART / SWO

NCP 模式：
  协议栈在独立芯片
  主机通过 UART 调命令
  crash 时 NCP 通常只复位
  log 完全丢失
```

### 修复

**修复 1：硬件留 SWO 引脚**

```text
10-pin Simplicity Connector 必备：
  Pin 1: VDD       Pin 2: GND
  Pin 3: SWDIO     Pin 4: SWCLK
  Pin 5: SWO       Pin 6: NC
  Pin 7: NC        Pin 8: GND
  Pin 9: RST       Pin 10: GND

AN958 推荐布局：
  - 10-pin 排针 1.27mm 间距
  - 离芯片 < 5cm
  - 走线远离 RF / DC-DC
```

**修复 2：启用 ncp-debug-print 插件**

```c
// Simplicity Studio
// Project > Software Components > EmberZNet 7.x
//   > Plugins
//     > [Enable] emberMinimal
//     > [Enable] printf
//     > [Enable] serial
//     > [Enable] ncp-debug-print  ← 关键
```

**修复 3：crash 抓取代码**

```c
// 应用层在主机上检测 NCP 复位
void onNcpReset(uint8_t resetReason) {
    // 抓 SWO log 存到文件
    // 通知后台
    log_to_flash("NCP reset: reason=0x%02x", resetReason);
}

// EZSP 协议层
void ezspErrorHandler(EzspStatus status) {
    if (status == EZSP_ERROR_RESET_SOFTWARE ||
        status == EZSP_ERROR_RESET_WATCHDOG) {
        onNcpReset(status);
    }
}
```

**修复 4：NCP 应用层保护**

```c
// 协议栈崩溃后 NCP 自动重启
// 主机做 watchdog:
//   3s 没收到 NCP 心跳 → 重置 NCP

#define NCP_WATCHDOG_TIMEOUT_MS 3000
static uint32_t last_ncp_heartbeat = 0;

void host_loop(void) {
    if (millis() - last_ncp_heartbeat > NCP_WATCHDOG_TIMEOUT_MS) {
        log_error("NCP watchdog timeout, reset");
        ncp_hardware_reset();
    }
}

void on_ezsp_frame_received(void) {
    last_ncp_heartbeat = millis();
}
```

### 复盘

- **NCP 模式调试** 必须留 SWO + 启用 debug-print
- **崩溃保护**：主机端加 watchdog，NCP 崩了能自动重置
- **EFR32 三个插件必须同开**：emberMinimal + printf + serial
- **AN958 是金标准**，新设计必读
- **没有 SWO = 没有调试能力**，产线故障无法复现

### 来源

- _Inbox/ZigBee-2026-08-01-candidates.md 候选 3
- Silicon Labs KBA
- AN958 Design Guide

---

## 案例 4：End Device Poll Control 错配，纽扣电池撑不过 1 周

### 现象

智能门锁，CR2477 电池，宣称"2 年寿命"，实测 7 天。log 显示平均电流 800 µA。

### 抓 log

```text
功率分析仪（20s 窗口）：
  周期：~2 秒
  唤醒电流：~8 mA，~30ms
  睡眠电流：~3 µA
  平均：8 × 0.03 / 2 + 3e-3 ≈ 123 µA（按 2s 算）

实际：~800 µA → 唤醒占空比 10%（不是 1.5%）
```

**问题**：唤醒次数比预期多 6-7 倍。

### 定位

**Z-Stack / EmberZNet Poll Control 错配**：

```c
// 错：End Device Poll Interval 太小
#define ZG_END_DEV_POLL_INTERVAL    1000    // 1s（太频繁）
// Keepalive 没配
// 实际：每 1s 醒来 1 次

// 期望：3s 1 次（续航可撑 2 年）
```

**根因**：

- 工程师没改 ZGlobals.h 默认 Poll Interval
- 默认值在不同协议栈版本不同
- Z-Stack 3.0.x 默认 7000ms（7s），但有些项目改成 1s
- Keepalive 时间不匹配 Poll Interval，导致父节点误判

### 修复

```c
// Z-Stack 配置（f8wConfig.cfg）
-DZG_END_DEV_POLL_INTERVAL=3000       // 3s
-DZG_END_DEV_KEEPALIVE=7000           // 7s
-DZG_END_DEV_REJOIN_ATTEMPTS=3
-DZG_END_DEV_REJOIN_INTERVAL=30
-DZG_END_DEV_MAX_PARENT_THRSH=3
```

```c
// EmberZNet 配置（ZigbeeZnetConfigurationPanel）
//  - Poll Interval: 3000ms
//  - Poll Timeout: 7000ms（必须 < Rejoin Interval × Rejoin Attempts）
//  - Rejoin Interval: 30000ms
//  - Rejoin Attempts: 3
```

**关键约束**：

```text
PollInterval < Parent NWK Link Status Timeout（默认 16s）
Keepalive < Rejoin Interval × Rejoin Attempts
```

**复算功耗**：

```text
唤醒 30ms / 周期 3s = 1% duty
唤醒 8 mA，平均 = 8 × 0.01 = 80 µA
睡眠 3 µA
总平均 ≈ 83 µA

CR2477 = 1000 mAh
1000 / 0.083 / 24 / 365 = 1.37 年 ≈ 撑 1.5 年（合理）
```

### 复盘

- **Poll Interval 是 End Device 续航第一参数**
- **默认值 ≠ 量产值**，必须按场景改
- **Keepalive / Rejoin / PollInterval 三者必须匹配**
- **功率分析仪实测永远比 datasheet 准**
- **纽扣电池 1 周 vs 2 年差 100 倍**，错配容易

---

## 案例 5：多 Coordinator 冲突致同信道互踩

### 现象

办公楼宇，2 个 ZigBee 网络在 12 信道（2410 MHz），两 Coordinator 在同 PAN ID 范围。50 设备混入两个网络，40% 设备掉线。

### 抓包

```text
Wireshark + nRF Sniffer 抓 12 信道：
  Beacon 1: PAN ID 0x1234, EPID 0xABCDEF...
  Beacon 2: PAN ID 0x1234, EPID 0x123456...（相同 PAN，不同 EPID）
  
两个 Coordinator 互踩：
  - 设备可能关联到 Coordinator A
  - Coordinator B Beacon 同样 PAN ID，设备又 Rejoin 到 B
  - 网络震荡
```

### 定位

**PAN ID 冲突**：

- 写字楼 5 家公司都用 0x1234 默认 PAN ID
- ZigBee 协议规定 PAN ID 不可同信道相同，但 EPID 区分
- 设备选 Coordinator 看 RSSI + LQI，频繁切换

**根因**：

- Coordinator 没开冲突检测
- 设备端 RSSI 漂移（人在中间走动）
- 无 Channel Mask 限制

### 修复

**修复 1：启用 Coordinator 冲突检测**

```c
// Z-Stack
-DZDAPP_CONFIG_PAN_ID=0x0001      // 自定义 PAN ID
-DZIGBEE_CHANLIST=0x07FFE400      // 避 Wi-Fi 1, 6, 11

// EmberZNet
sli_zigbee_network_pan_id_set(0x1234);  // 自定义
sli_zigbee_network_channel_mask_set(0x07FFE400);
```

**修复 2：Channel Mask 限制**

```c
// 限制到 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24
uint32_t mask = 0x07FFE400;
sli_zigbee_network_channel_mask_set(mask);
```

**修复 3：楼宇部署规范**

```text
- 每公司申请独立 PAN ID
- 不同楼栋用不同信道
- Coordinator 部署前扫信道
- Mgmt_NWK_Update_req 切信道
```

### 复盘

- **PAN ID 冲突是大楼部署头号问题**
- **每个 PAN ID 必须有管理员**
- **Channel Mask + 自定义 PAN ID 双保险**
- **生产前扫信道** Mgmt_NWK_Disc_req
- **多 Coordinator 部署必须有规范**

---

## 案例 6：ZCL 错误码 0x8A NOT_FOUND 误判

### 现象

ZHA 自动化失败："Cannot read attribute 0x0006 of cluster 0x0202 (Thermostat) from EP 1"，开发者以为是 Cluster ID 错，调了 3 天。

### 抓包

```text
Read Attribute Request:
  Cluster 0x0202 (Thermostat UI, 不是 Thermostat)
  Attribute 0x0006 (MaxHeatSetpoint, 不存在)

Server Response:
  Read Attribute Response
    Record 0: AttributeId=0x0006, Status=0x8A NOT_FOUND
```

### 定位

**0x8A NOT_FOUND** 不是 Cluster 错，是**属性不存在**：

```text
Cluster 0x0202 (Thermostat UI) 属性表：
  0x0000 = TemperatureDisplayMode
  0x0001 = KeypadLockout
  没有 0x0006

实际想读的 0x0006 MaxHeatSetpoint 在 Cluster 0x0201 (Thermostat) 上
```

**根因**：

- ZHA 配置文件 cluster_id 写错（0202 vs 0201）
- 两个 Cluster 名字相近（Thermostat vs Thermostat UI）

### 修复

```yaml
# zigbee2mqtt configuration.yaml
# 正确配置
thermostat_cluster: 0x0201  # Thermostat，不是 0x0202

# 自定义 converter 指定正确 cluster
toZigbee:
  - attribute_id: 0x0006  # MaxHeatSetpoint
    cluster_id: 0x0201
    ...
```

### 复盘

- **0x8A NOT_FOUND 多半是属性错，不是 Cluster 错**
- **相似名字的 Cluster 容易混**（Thermostat vs Thermostat UI）
- **抓包看完整 Read Attribute Response**，包括 cluster_id
- **ZHA / zigbee2mqtt 配置文件务必从官方 ZCL 字典查**

---

## 案例 7：Trust Center 默认 Link Key 量产踩雷

### 现象

产品 A 量产 1000 台，使用默认 Trust Center Link Key（"ZigBeeAlliance09"）。客户收到产品 A 和产品 B（其他厂商），两个网络互踩，安全风险。

### 抓包

```text
产品 A 设备入网时：
  Transport Key (Default Trust Center Link Key)
  → Trust Center 验证通过
  → 入网成功

产品 B 设备同样 Default Link Key
  → 可能误关联 A 的 Trust Center
  → 安全风险
```

### 定位

**默认 Link Key 公开**：

```text
"ZigBeeAlliance09" 是 ZigBee Alliance 测试用 key
所有 ZigBee 3.0 之前协议栈都内置
量产用默认 key = 不设防

攻击场景：
  1. 攻击者买任何 ZigBee 3.0 之前产品
  2. 提取 Default Link Key
  3. 发起 Transport Key 请求
  4. 拦截所有加密通信
```

### 修复

**方案 1：Install Code（推荐）**

```c
// 1. 每台设备出厂前烧 16 字节 Install Code + 2 字节 CRC
uint8_t install_code[18] = { /* unique per device */ };
halCommonWriteExternalNV(NV_INSTALL_CODE, install_code, 18);

// 2. Trust Center 配置
sli_zigbee_af_install_code_set_policy(
    EMBER_INSTALL_CODE_POLICY_REQUIRED  // 必须验证
);

// 3. 设备入网时自动用 Install Code 派生 Link Key
sli_zigbee_af_trust_center_add_install_code(ieee, install_code, 18);
```

**方案 2：Application Link Key（点对点）**

```text
适用：Bind / Report 加密
派生：
  HMAC-SHA256(InstallCode || 0x5A6967426565416C6C69616E63653039)
  → 16 字节 Link Key
```

**方案 3：Network Key 周期更新**

```c
// 强制所有节点 24h 切 1 次 NWK Key
sli_zigbee_af_network_key_update_period_set(24 * 3600);
```

### 复盘

- **默认 Link Key 绝对不能用于量产**
- **Install Code 是 ZigBee 3.0 推荐方案**
- **每设备唯一 Link Key 是底线**
- **Network Key 周期更新降低泄漏风险**
- **ZigBee 3.0 强制要求 Install Code，3.0 之前是可选**

---

## 案例 8：CC2530 老固件与新版 Z-Stack 互操作失败

### 现象

老产品 CC2530 + Z-Stack 2.5.1a 入网老网络 OK。升级新产品 CC2652 + Z-Stack 3.0.2 后，老 CC2530 设备无法入新网络。

### 抓包

```text
老 CC2530 → 新 Coordinator:
  Association Request
新 Coordinator:
  Association Response (Status 0x03 NOT_ACTIVE)

老 CC2530:
  Transport Key Request (Default Trust Center Link Key)
新 Coordinator:
  APS Transport Key 失败（安全模式不一致）
```

### 定位

**Z-Stack 版本差异**：

| 维度 | Z-Stack 2.5.1a | Z-Stack 3.0.2 |
| --- | --- | --- |
| 协议 | ZigBee 1.x / HA | ZigBee 3.0 |
| 信任中心 | 可选 Install Code | 强制 Install Code |
| 安全 | 旧 APS | 新 APS 安全 |
| Cluster | 旧 ZCL 库 | 新 ZCL 库 |

**根因**：

- 老 CC2530 用 Default Link Key
- 新 Coordinator 强制 Install Code
- 验证不一致 → 拒绝入网

### 修复

**方案 1：临时兼容（双 Trust Center）**

```c
// 新 Coordinator 同时支持 Default Link Key + Install Code
-DTC_LINKKEY_JOIN=1
-DUSE_INSTALL_CODE=1
```

**方案 2：老设备烧 Install Code**

```text
产线批量烧 Install Code + 升级固件
适用：可控量产环境
```

**方案 3：Coordinator 降级**

```text
新 Coordinator 降级到 Z-Stack 2.5.1a
不推荐：失去 ZigBee 3.0 安全
```

### 复盘

- **Z-Stack 主版本升级 = 协议不兼容**
- **ZigBee 3.0 强制 Install Code 是好事**
- **老产品过渡要双 Trust Center**
- **协议栈升级必须做端到端兼容测试**
- **新设计直接 Z-Stack 3.0.2+，不要 Z-Stack 2.x**

---

## 案例 9：EFR32MG21 卡 association response，无 transport key

### 现象

智慧工厂 ZigBee 网关项目批量部署：5 个 EFR32MG21 协调器（同一批次固件），50 个 EFR32MG21 路由器 + 200 个终端节点。量产烧录后：

- 5 个协调器中 1 个异常，4 个正常
- 异常协调器上所有终端节点"卡入网"：发完 Association Request 后**永远收不到 Association Response**，更没有 Transport Key
- 4 个正常协调器入网成功率 > 99%
- 拔掉异常协调器电源 30 分钟重启：仍然异常
- 退回到 Z-Stack 2.x 固件：仍然异常
- **加一个 EFR32MG21 路由器中继 C**：终端节点能绕过直连入网

### 抓包

```text
正常协调器（4 台）的入网流程：
  1. 终端发 Beacon Request
  2. 协调器回 Beacon（带允许入网标志）
  3. 终端发 Association Request
  4. 协调器回 Association Response（短地址 + 能力）
  5. 协调器发 Transport Key（APS encrypted with Trust Center Link Key）
  6. 终端回 Transport Key ACK
  → 全部成功

异常协调器（1 台）的入网流程：
  1. 终端发 Beacon Request
  2. 协调器回 Beacon（带允许入网标志）✅
  3. 终端发 Association Request
  4. 协调器回 Association Response（短地址 + 能力）✅
  5. 协调器**不发** Transport Key ❌ ← 关键断点
  → 终端认为入网失败，重试

Wireshark 抓包对比 5 个协调器的 Association Response payload：
  4 个正常：短地址 = 0x0001-0x00C8 连续分配
  1 个异常：短地址 = 0x0001-0x00C8 连续分配（payload 看起来一样）
  → 表面上 Association Response 没问题
  → 进一步看 APS 层加密：异常协调器在 Transport Key 阶段不发包
```

### 定位

```text
硬件排查（产线用示波器 / 万用表）：
  1. 量 RF 输出：异常协调器 TX Power = 10（默认），正常协调器也是 10 → 看似一致
  2. 量电源纹波：异常协调器 3.3V 纹波 50mV，正常协调器 15mV
  3. 查电源设计：异常协调器用了**早期版本 PCB**，3.3V LDO 缺一颗去耦电容
  4. 长时间运行下，异常协调器温度高 5°C，射频功放电流偏大

软排查：
  1. 对比 firmware bin：异常协调器是早期 build（v2.3.1），正常协调器是 v2.3.2
  2. 查 v2.3.2 changelog："Fix: power supply noise causing RF desense"
  3. 把异常协调器刷 v2.3.2 → 仍然异常（说明不只是固件问题）
  4. 换电源板（带去耦电容的新版）→ 异常消失 ✅

加路由器 C 的本质：
  路由器 C 距离异常协调器 8m，距离终端 12m
  终端通过路由器 C 入网时，链路比直连稳定（路由器中继 + 重新调度）
  验证了"异常协调器 + 远距离" = 失败的判断
  → 电源纹波 + TX Power 10 双重压力下，RF 链路裕量不足
```

### 修复

```text
硬件侧（必须做）：
  1. 协调器 3.3V LDO 后必须加 100nF + 10uF 去耦电容
  2. 协调器 PCB 改版，单独铺 RF 电源层
  3. TX Power 加大到 17（默认 10）—— 留 7dB 链路裕量
  4. 老化测试：批量前 5% 抽样 24h 老化，看入网成功率

固件侧（必须做）：
  1. 升级到最新 Z-Stack（含 RF desense 修复）
  2. 启动后 30s 内做 link quality 监测，异常立即重启
  3. Transport Key 重传机制：5s 内没收到 ACK → 重发 Association Request
  4. 入网失败 N 次 → 切换信道（Channel Mask 13-23 循环试）

产线侧（必须做）：
  1. 出货前 100% 跑 1h 老化（不能只跑 10 分钟）
  2. 老化过程用脚本：100 个节点入网测试，看成功率
  3. 异常协调器**不允许出货**（不是靠加路由器绕过）
  4. 现场部署：1 个协调器 + 1 个备援路由器，保证 24h 链路

运维侧（现场）：
  1. 加网状中继：每个协调器覆盖范围都加 1~2 个路由器
  2. 即使协调器临时异常，终端走路由器中继入网
  3. 协调器修复期间不影响整个网络
```

### 复盘

- **5 个协调器只有 1 个异常**——典型"批次内个体差异"，**产线必须 100% 老化测试**
- 表面现象（Association Response 正常）和实际根因（Transport Key 不发）不在同一层——**抓包要看完整流程，不能只看前 4 步**
- 电源纹波 → 射频灵敏度下降 → 长链路入网失败——**根因和表象相隔 3 层**
- 加路由器 C 能绕过，但**不应该作为最终方案**（只是临时缓解）
- 异常 + 短期 = 软问题；异常 + 长期 = 硬件问题；本案例两者叠加

### 来源

- _Inbox/ZigBee-2026-08-02-candidates.md 候选 1
- Silicon Labs EFR32MG21 量产复盘
- 工程师答复（世强 Sekorm 平台）

---

## 案例 10：Zigbee 模块产线 3.3V LDO 输入电压应力过低，浪涌烧毁

### 现象

广州致远电子产线 Zigbee 模块批量故障：

- 5V 轨经继电器 / 互感器 → 浪涌耦合到 3.3V LDO 输入
- LDO 输入电压应力过低，长期运行烧毁
- 返修率 12%（行业平均 < 1%）
- 现场环境：工业控制柜，继电器密集

### 抓包 / 电源分析

```text
示波器抓 LDO 输入（5V 轨）：
  - 正常 5.0V ± 50mV
  - 继电器吸合瞬间：5V 跌到 3.5V（30ms）
  - 互感器耦合：5V 上叠加 8V 尖峰（持续 1us）

LDO 输出（3.3V）实测：
  - 正常 3.3V ± 20mV
  - 继电器吸合时：3.3V 跌到 2.8V（节点复位）
  - 浪涌尖峰时：3.3V 上升到 3.8V（RF 链路劣化）

故障路径：
  路径 1：AC 220V → 5V 开关电源 → LDO 5V 输入
          → LDO 输出 3.3V
          → 5V 浪涌直接灌进 LDO → 烧毁
  
  路径 2：5V 继电器线圈反向 EMF → 5V 轨叠加尖峰
          → LDO 5V 输入过压（> 6V）→ LDO 永久损坏
```

### 定位

```text
Step 1：现场电源环境勘察
  - 工业控制柜，5V 继电器 8 个
  - 互感器 3 个（AC 电流采样）
  - 5V 电源和 3.3V 模组共地，但电源线走线 > 30cm
  
Step 2：示波器抓 5V 浪涌
  - 继电器吸合时 5V 跌到 3.5V
  - 互感器耦合 8V 尖峰
  - 浪涌频率 10Hz（每 100ms 一次继电器动作）

Step 3：LDO 失效分析
  - 旧设计：AMS1117-3.3（输入耐压 12V）
  - 失效模式：内部调整管击穿
  - 实测输入电压：8V 尖峰（< 12V 规格）
  - 但 AMS1117 在 8V + 1A 负载下热崩溃（SOIC-8 封装散热不足）
```

### 修复

```text
硬件侧（必须做）：
  1. 5V 输入加 TVS（P6KE6.8CA）+ 共模电感
     - TVS 钳位 6.8V，浪涌吸收
     - 共模电感滤除高频尖峰
  2. 改 LDO 型号：LM1117 → TPS7A4533
     - 输入耐压 20V（vs 12V）
     - 输出电流 1.5A（vs 1A）
     - 热阻低 30%（SO PowerPAD 封装）
  3. 电源线走线缩短到 < 5cm
  4. 5V 和 3.3V 之间加 π 型滤波（LC）
  5. PCB 加 TVS 二极管阵列（多路保护）

固件侧（次要）：
  1. 加电源电压 ADC 监测，异常立即进 safe mode
  2. 节点重启次数统计，看门狗复位超过 5 次报警

产线侧（必须做）：
  1. 100% 老化测试：上电 24h 看 LDO 温度
  2. 模拟现场浪涌：注入 6V / 8V / 10V 看 LDO 是否损坏
  3. 返修品 100% 分析失效模式
```

### 复盘

- **电源设计是产线第一坑**——5V 浪涌看似小问题，烧 LDO 是长期积累
- AMS1117 等老型号 LDO **耐压 / 散热都不适合工业环境**
- 工业现场必须用工业级 LDO（TPS7A / LP38690 / LT1963）
- 老化测试必须 100%，不能只抽样
- 浪涌路径分析（AC → 5V → LDO vs 继电器反灌）必须画完整电路图

### 来源

- _Inbox/ZigBee-2026-08-04-candidates.md 候选 1
- 广州致远电子产线故障复盘
- AMS1117 / TPS7A4533 datasheet

---

## 案例 11：才茂 CM210 工业级 Zigbee 模块 4 类典型故障

### 现象

工业现场（工厂 / 油田 / 矿区）批量部署才茂 CM210 工业 Zigbee 模块（IP65 防水 + DC 9-24V 宽压）：

- 4 类故障高发，覆盖 80% 现场问题
- 现场工程师常误判"模块坏了"，实际是配置 / 接线问题

### 抓包 / 4 类故障分类

```text
故障 1：电源灯不亮（25%）
  现场表现：模块上电后 PWR 灯不亮
  排查路径：
    1. 测输入电压：DC 9-24V 范围？
       - 24V DC 实测 26V → 过压保护触发 → 灯不亮
       - 9V DC 实测 7.5V → 欠压保护触发 → 灯不亮
    2. 测内部 3.3V：是否 3.3V 正常？
       - 3.3V 0V → 内部 LDO 烧毁
       - 3.3V 3.1V → 欠压但能跑（边沿异常）
    3. 看保险丝：1A 自恢复是否触发
       - 触发 → 负载短路
       - 正常 → 模块主板问题
  修复：
    - 24V 系统加 DC-DC 降压到 12V
    - 9V 系统加升压到 12V
    - 换主板

故障 2：配置态进不去（30%）
  现场表现：按 S 键，串口无回显
  排查路径：
    1. 串口参数：38400-8-N-1 无流控
       - 默认 9600 → 改 38400
       - 8-N-1 vs 8-E-1 → 默认 8-N-1
    2. 按 S 键时序：上电 5s 内按 S > 1s
       - 太早按：模块未进 boot
       - 太晚按：模块已进工作态
    3. HEX 模式 vs ASCII 模式
       - CAIMORE（私有协议）必须 HEX 发送
       - ASCII 模式（默认）只支持 AT 指令
    4. 串口线序：TX/RX/GND 三线制
       - 现场常把 TX/RX 接反 → 无回显
  修复：
    - 配 USB-TTL 适配器（CH340 / FTDI）
    - 现场用 Putty 测串口
    - 看模块 boot log（"CAIMORE V3.2"等）

故障 3：终端路由灯不亮（25%）
  现场表现：节点（路由模式）LINK 灯不亮
  排查路径：
    1. 协调器是否在工作？
       - 协调器 PWR 灯亮？LINK 灯亮？
       - 协调器 PANID = 节点 PANID？
    2. 信道是否一致？
       - 协调器信道 15，节点信道 20 → 入网失败
    3. 距离是否在范围内？
       - 室内 30m / 室外 100m 内？
       - 金属阻挡 > 50%？加中继
    4. 终端 / 路由模式是否正确？
       - 默认是终端（Route 模式）→ 上电入网后自动转路由
       - 部分模块需手动切到路由模式
  修复：
    - 协调器复位 + 节点重新入网
    - 检查 PANID / 信道 / 距离
    - 改路由模式（AT+ROLE=1）

故障 4：收不到数据（20%）
  现场表现：APP / 上位机收不到节点数据
  排查路径：
    1. PANID 不一致 = 收不到 #1 原因（占 50%）
    2. 端口号错（默认 0x0000，应用层监听 0x0001）
    3. Cluster ID 错（应用 Cluster 没注册）
    4. 加密 Key 错（默认开启加密，需 Trust Center Link Key）
    5. 节点没在 NS / 网关注册
  修复：
    - 强制统一 PANID（出厂烧入）
    - 验证 Cluster ID 注册
    - 关闭加密测试（临时）
    - 加中继 / 增网关
```

### 修复 / 现场调试 SOP

```text
工业现场 Zigbee 调试 SOP（5 步）：
  Step 1：电源检查
    - 测输入电压（DC 9-24V）
    - 看 PWR 灯
    - 测内部 3.3V
    
  Step 2：串口配置
    - 38400-8-N-1 无流控
    - 按 S 键 > 1s 进配置态
    - HEX 模式（CAIMORE 协议）
    
  Step 3：协调器状态
    - PWR / LINK 灯
    - PANID / 信道
    - 协调器已注册设备列表
    
  Step 4：节点入网
    - 信道 / PANID 一致
    - 距离 < 100m
    - 路由 / 终端模式正确
    
  Step 5：业务通信
    - Cluster ID 注册
    - 端口号一致
    - 加密 Key 一致
```

### 复盘

- 工业 Zigbee 现场 80% 问题 = 配置 / 接线 / 电源，**不是模块故障**
- 现场工程师常误判"模块坏了"，**4 类故障排查 SOP 必须固化**
- CAIMORE 协议 + HEX 模式是新手第一坑
- PANID 不一致是收不到 #1 原因（占 50%）
- 出厂前 100% 配 PANID + 信道 + Cluster ID 是关键

### 来源

- _Inbox/ZigBee-2026-08-04-candidates.md 候选 2
- 才茂 CM210 工业 Zigbee 厂商 FAQ
- 工业现场调试经验汇总

---

## 案例 12：CC2530 / CC2652 量产烧录 17 个真实错误

### 现象

CC2530 / CC2652 + Z-Stack 量产烧录过程 17 类典型错误（XDATA 溢出 / 断点失败 / 烧录模式冲突等），覆盖 95% 量产问题。

### 抓包 / 17 类错误分类

```text
错误 1-3：内存相关（30%）
  Fatal[e46]: XDATA overflow
    → 数组过大（如 uint8_t buf[8192]）
    → 解决：用 __code 修饰符搬到 code 段
    → const uint8_t __code buf[8192] = { ... };
  
  Fatal[e72]: IDATA overflow
    → 太大变量用 static 修饰
    → 改为大数组用 __xdata 修饰
  
  Fatal[e121]: CODE overflow
    → Flash 容量超 256KB
    → 减少功能 / 优化代码

错误 4-6：断点 / 调试失败（15%）
  Breakpoint not set
    → Flash 写保护未关闭
    → 解决：擦除整片 Flash + 烧录新固件
  
  IAR 找不到目标
    → XDS100v3 驱动问题
    → 解决：重装 TI 驱动
  
  仿真器 ID 错
    → 用了 CC2530 仿真器但板子是 CC2531
    → 解决：换对应仿真器

错误 7-9：烧录模式冲突（20%）
  Fatal Cp001
    → IAR license 失效
    → 解决：更新 license
    
  量产 hex vs debug 模式冲突
    → debug 模式下烧录的 hex 跑 release 模式死机
    → 解决：量产烧录**必须 release 模式 + .hex 扩展名**
  
  hex 文件被 IDE 改过
    → IDE 重新编译改了 hex 内容
    → 解决：量产前**锁定 hex 文件**，烧录专用副本

错误 10-12：工具链问题（15%）
  Fatal #E1
    → IAR 安装目录和 TI 工具链不在同盘（C 盘 vs D 盘）
    → 解决：装同盘
  
  链接脚本错
    → lnk51ew_cc2530F256.xcl 错选成 CC2530F128
    → 解决：选对芯片型号
  
  头文件路径错
    → #include <ioCC2530.h> 找不到
    → 解决：项目属性 → C/C++ Compiler → Preprocessor 加路径

错误 13-15：硬件相关（10%）
  仿真器接不上
    → 仿真器固件过旧
    → 解决：升级 cebal_fw_srf05dbg.hex（CC debugger）
  
  板子识别不到
    → CC2530 reset pin 虚焊
    → 解决：补焊 / 换板
  
  烧录时断电
    → 节点被烧坏
    → 解决：UPS + 烧录前测电源

错误 16-17：其他（10%）
  Z-Stack 版本兼容
    → 旧 Z-Stack 2.5 + 新 CC2652 → 协议不兼容
    → 解决：升级到 Z-Stack 3.0.2+
  
  加密 / Trust Center 错
    → Install Code 没配
    → 解决：参考案例 7
```

### 修复（量产烧录 SOP）

```text
量产烧录 8 步 SOP：
  Step 1：环境检查
    - IAR 8000 + Z-Stack 3.0.2
    - TI 工具链 v1.5+（同盘）
    - 仿真器固件最新（CC debugger）
  
  Step 2：项目配置
    - 选对芯片型号（CC2530F256 / CC2530F128）
    - 选对链接脚本
    - 选对头文件路径
    - 选 release 模式 + __code 优化
  
  Step 3：代码优化
    - 大数组用 __code 搬 code 段
    - 静态变量用 static / __xdata
    - 功能裁剪到 Flash < 200KB
  
  Step 4：编译
    - 清理工程（rebuild all）
    - 检查 .map 文件 XDATA / IDATA / CODE 用量
    - 看是否有 warning（warning 可能 = error）
  
  Step 5：生成 hex
    - 量产专用 hex：**不动 IDE 重新编译**
    - 备份 hex 文件到只读存储
  
  Step 6：烧录
    - 用量产烧录器（SmartRF Flash Programmer 2）
    - 不使用 IAR debug 模式
    - 烧录前擦除整片
  
  Step 7：验证
    - 烧录后读回 hex 对比
    - 实测节点入网
  
  Step 8：版本控制
    - hex 文件 + 版本号 + 日期归档
    - 出货时打 bin 唯一 ID
```

### 复盘

- CC2530/CC2652 量产 95% 问题 = **内存溢出 + 烧录模式 + 工具链路径**
- 量产 hex **绝对不能动 IDE 重新编译**——必须专用副本
- 调试 vs 量产模式不能混用，release 模式烧录
- 工具链路径必须在同盘（C 盘 vs D 盘）
- 仿真器固件 / 头文件 / 链接脚本 3 件套必须匹配

### 来源

- _Inbox/ZigBee-2026-08-07-candidates.md 候选 2
- CSDN CC2530/CC2652 量产 FAQ（17 类错误）
- TI Z-Stack 量产规范

---

## 案例 13：单子网 ≤60 节点上限 + E18/E180/Link72 选型经验

### 现象

某江苏工厂能耗管理项目（21 个 Zigbee 采集模块 + 82 块 485 电能表）：

- 工厂部署初期 200+ 节点，频繁掉线
- 缩小到 60 节点 / 子网后稳定
- 不同模块（E18 / E180 / Link72）性能差异巨大

### 抓包 / 单子网极限

```text
理论极限 vs 实际极限：
  理论：Zigbee 短地址 16-bit = 65535 节点
  实际工业部署：60 节点 / 子网（经验上限）
  
为什么差距这么大：
  1. 路由表满（路由节点默认 30-40 表项）
     → 超过 60 节点路由查询超时
  2. APS 表满（每个节点占 1-2 个 APS entry）
     → 超过 80 节点 APS 拒收
  3. 协调器 CPU 资源（Silicon Labs EFR32MG21 主频 80MHz）
     → 80 节点 + 周期 poll → CPU 80% 负载
  4. 无线信道冲突
     → 60 节点以上 RSSI 互相干扰
     → 需要切信道（11/15/20/25）

实测数据（江苏工厂）：
  - 子网 30 节点：掉线率 0.5%
  - 子网 60 节点：掉线率 2%
  - 子网 100 节点：掉线率 15%
  - 子网 200 节点：掉线率 50%+ → 系统不可用
```

### 定位（部署经验值）

```text
经验部署上限：
  - 协调器 + 路由：单子网 ≤ 60 节点
  - 协调器 + 全终端：单子网 ≤ 100 节点
  - 大量节点必须：多协调器 + 多子网（PANID 不同）
  - 推荐：60 节点 / 子网是工业产线安全值

密度经验值：
  - 路由节点每 50-100m 一个（保证 1-2 跳）
  - 终端节点 100-300m 半径
  - 工业金属环境：路由节点每 30-50m 一个

模块实测参数（成都亿佰特）：
  E18 系列（4dBm 棒状）：
    - 室内 10-30m
    - 室外视距 100-200m
    - 32 节点 / 子网（路由数少）
  
  E180 系列（20dBm PA）：
    - 室内 50-100m
    - 室外视距 500-1000m
    - 60 节点 / 子网
    - sleep 终端下行缓存默认 7s
  
  Link72 系列（27dBm）：
    - 室内 100-200m
    - 室外视距 2-3 km
    - 80 节点 / 子网
    - 适合室外 / 工业远距

选型决策：
  - 室内小规模（< 30 节点）：E18
  - 工业中型（30-60 节点）：E180
  - 室外 / 远距（> 1 km）：Link72
```

### 修复

```text
工业部署架构：
  - 工厂能耗：1 主协调器 + 21 路由 + 60 终端/路由
  - 上行：Zigbee → 网关 → 工业以太网 / 4G → 云端
  - 业务平台：实时数据 + 告警 + 工单
  - 多子网 PANID：每 60 节点一个子网

PCB 设计（参考）：
  - 协调器：EFR32MG21 + PA（20dBm）+ FPC 天线
  - 路由：E180 模块 + DC-DC 9-24V
  - 终端：E18 + 电池（CR2477 5 年）

部署注意：
  - 协调器放中心位置（各方向 ≤ 50m）
  - 路由节点避开金属门 / 大型设备
  - 终端节点不在路由节点背面
  - 工厂金属多 → 路由节点密度加倍

调试（多 PANID 部署）：
  - 协调器 A：PANID 0x0001 / 信道 11
  - 协调器 B：PANID 0x0002 / 信道 15
  - 协调器 C：PANID 0x0003 / 信道 20
  - 协调器 D：PANID 0x4A3B / 信道 25（自定）
```

### 复盘

- **单子网 ≤ 60 节点是工业产线安全值**（不要挑战 100+）
- 理论 65535 节点 vs 实际 60 节点 = 协调器 CPU / 路由表 / 信道冲突三重限制
- 选型要看 dBm 等级：**4dBm（E18）vs 20dBm（E180）vs 27dBm（Link72）差 1 个数量级**
- 工厂金属环境路由密度加倍（30-50m / 个）
- 多 PANID 多子网是大规模部署唯一方案

### 来源

- _Inbox/ZigBee-2026-08-07-candidates.md 候选 3、4
- 江苏工厂能耗管理项目复盘
- 成都亿佰特 E18/E180/Link72 实测数据

---

## 案例 14：ZigBee PAN ID 冲突（EmberZNet 63/min 阈值）

### 现象

某建筑 ZigBee 部署（50+ 设备）：

- 协调器频繁报 PAN ID 冲突
- 整网自爆 → 重新选 PAN ID
- 几分钟后又冲突
- 系统不可用

### 抓包 / 根因

```text
抓包工具：Wireshark + CC2652 dongle

异常 Beacon：
  - 设备 EPID（Extended PAN ID）反转
  - 同一个 PAN ID 出现 2 个不同 EPID
  - 协调器误判为冲突
  - 触发 PAN ID 重选
  - 重选后短时间内又冲突

冲突检测机制（EmberZNet）：
  - 阈值：63 次冲突/分钟
  - 超过 → 触发整网自爆
  - 大规模并发才暴露（EPID 反转）
```

### 定位

```text
Step 1：抓 Beacon
  - 跑 1 小时抓包
  - 看 Beacon 里的 EPID 字段
  - 发现 EPID 反转

Step 2：算冲突频率
  - 同一 PAN ID 冲突次数
  - 实测：80 次/分钟（> 63 阈值）
  - 触发自爆

Step 3：找 EPID 反转原因
  - 协调器烧入 EPID = 0x0001
  - 部分节点出厂 EPID = 0xFFFF
  - 节点 join 后协调器分配 PAN ID，但 EPID 仍是出厂值
  - 不同节点的 EPID 不同 → 协调器认为 EPID 反转
```

### 修复

```text
固件侧（必须做）：
  1. 节点出厂 EPID 统一
     - 全部节点烧入 EPID = 0x0001
     - 协调器检测时不会判冲突
     
  2. 协调器 PAN ID 分配策略
     - 启动时随机选 1 个 PAN ID（避免固定）
     - 节点 join 后协调器更新节点的 EPID（强制同步）
     
  3. 冲突检测阈值调整
     - EmberZNet 默认 63/min 太敏感
     - 改 1000/min（更宽容）
     - 或关闭自动自爆

部署侧：
  1. 出厂前 EPID 检查（节点 vs 协调器一致）
  2. PAN ID 唯一性验证（同一空间不同协调器不能同 PAN）
  3. 50+ 节点必须先建网络再批量入网
```

### 复盘

- EmberZNet 冲突检测 63/min 阈值是**默认值**，大规模并发才暴露
- EPID 反转 = **节点 / 协调器 EPID 不一致**，最常见产线坑
- 节点出厂 EPID 必须统一（不能节点用 0xFFFF，协调器用 0x0001）
- 大规模网络（50+ 节点）必须先建网络再批量入网
- 冲突检测阈值是 "tuneable" 参数，不是一成不变

### 来源

- _Inbox/ZigBee-2026-08-21-candidates.md 候选 1
- Justin Ethier dev.to 实战博客
- EmberZNet PAN ID Conflict Reference

---

## 案例 15：新疆哈密 4 万亩滴灌阀控节点失控（吸盘天线底座脱落）

### 现象

新疆戈壁 4 万亩滴灌项目，ZigBee 阀控节点批量失效：

- 节点失联率 30%+（远超正常 1%）
- 单点检测：节点正常、配置正确、距离足够
- 现场查：节点 0x0007 路由器下行方向性异常
- 根因：吸盘天线底座脱落，**临时用胶带固定**

### 抓包 / 根因

```text
Analyser 抓包：
  - 节点返回 0x0007（路由错误）
  - 0x0007 = ROUTE_ERROR
  - 上行方向 RSSI 正常
  - 下行方向 RSSI 异常（-95 dBm）
  - 节点日志：下行链路 NACK 占比 50%

根因分析：
  吸盘天线底座 = 大型金属接触面
  脱落 → 天线接触面只靠胶带（高阻）
  → 下行信号传输损耗增加 15-20dB
  → 上行（节点发）受天线效率影响小
  → 下行（协调器发）受影响大
  → 单向"能上不能下"

关键观察：
  单点检测通过 ≠ 网络中正常
  - 单点测试：直接 RSSI，节点能收到
  - 网络中：经过路由 / 中继，下行多跳
  - 下行链路弱 = 协调器命令丢失 = 节点失联
```

### 修复

```text
硬件侧（必须做）：
  1. 吸盘天线改成外置 SMA 天线
     - 棒状天线 + SMA 连接器
     - 防水密封
     - 接触面用焊锡固定
     
  2. 节点外壳设计
     - 金属外壳必须留 RF 窗口
     - 玻璃钢 / 工程塑料外壳
     - 防止天线位置被金属遮挡

部署侧（必须做）：
  1. 上行 + 下行双向测试
     - 不能只测上行 RSSI
     - 必须测下行 RSSI
     - 双向差异 > 10dB → 天线有问题
     
  2. 现场装机自动化测试
     - 装机后自动跑 100 包上行 + 100 包下行
     - 双向 PER < 1% 才算合格
     
  3. 定期巡检
     - 每月抽 10% 节点做双向 PER 测试
     - 发现异常及时换
```

### 复盘

- **单点检测通过 ≠ 网络中正常**——必须双向测
- 吸盘天线底座脱落是户外项目"低概率高影响"硬件缺陷
- 大规模项目（>1000 节点），**低概率硬件缺陷变必现**
- 部署前必须做"双向链路 + 长期稳定性"双重测试
- 方向性问题（上行 vs 下行）= 必须分开测

### 来源

- _Inbox/ZigBee-2026-08-21-candidates.md 候选 2
- 致远电子实战
- ZigBee PRO 部署规范

---

## 案例 16：50+ 节点 ZigBee Mesh 路由风暴 + Neighbor Table 溢出死锁

### 现象

某金属车间部署 50+ 节点 ZigBee Mesh：

- 部署初期正常
- 1 周后部分节点开始掉线
- 2 周后 30%+ 节点失联
- 协调器频繁重启

### 抓包 / 根因

```text
抓包分析（tsight.io 实战）：
  链路：密度高 + 链路波动 → 路由发现指数级广播
  → Neighbor Table 溢出
  → 死锁

Neighbor Table 容量（典型）：
  - EFR32MG21：26 条
  - CC2530：20 条
  - EFR32MG12：50 条
  50+ 节点 → 单节点 neighbor > 26 → 溢出

失败链路：
  Step 1：链路波动（金属车床启停）→ LQI 变化
  Step 2：节点 A 触发路由发现
  Step 3：路由请求广播
  Step 4：邻居节点转发
  Step 5：路由请求数量指数级增长
  Step 6：邻居表溢出
  Step 7：节点无法处理新邻居 → 静默丢包
  Step 8：路由发现失败 → 链路瘫痪
  Step 9：死锁

实测数据（金属车间 5m 距离）：
  - 普通办公环境丢包率：2%
  - 金属车间 5m：40%（屏蔽严重）
  - 协调器放车间中心：50% 节点频繁掉线
  - 协调器放车间边缘：95% 节点稳定
```

### 修复

```text
反直觉方案（协调器放边缘）：
  1. 协调器位置
     - 不要放金属车床中心（屏蔽最严重）
     - 放车间边缘靠墙位置
     - 信号"向外辐射"覆盖全车间
     
  2. 吸盘天线
     - 协调器吸盘天线（5dBi）
     - 棒状天线（2dBi）覆盖范围小
     
  3. 固件级防溢出
     - 限制路由发现频率（5s 一次）
     - Neighbor Table LRU 淘汰
     - 路由表满时拒绝新路由请求
     
  4. 工业部署选址
     - RF 现场勘测
     - 频谱仪扫 2.4 GHz
     - 找出"信号岛"
```

### 复盘

- **50+ 节点 Mesh"自愈"反向成瘫痪**——必须控路由发现
- Neighbor Table 容量是硬限制（EFR32MG21 = 26 条）
- 金属车间协调器放中心是反直觉，**放边缘反而好**
- 工业部署必须 RF 勘测，**不能凭经验选点**
- 固件级防溢出 + 路由发现限速是必须做的

### 来源

- _Inbox/ZigBee-2026-08-21-candidates.md 候选 3
- tsight.io 工业部署实战
- ZigBee PRO Mesh 部署规范

---

## 案例 17：ZigBee 5 大入网失败原因 + 200 节点 85%→99.5%

### 现象

某工业项目 200 节点 ZigBee 部署：

- 初次入网率 85%（失败 30 个）
- 排查后入网率 99.5%
- 金属货架盲区 -82dBm 是元凶

### 抓包 / 5 大原因

```text
原因 1：信道不匹配
  - 协调器信道 15
  - 部分节点烧入信道 20
  - 节点根本搜不到协调器
  - 解决：全节点统一信道（11/15/20/25）

原因 2：PAN ID 不匹配
  - 协调器 PAN ID 0x1234
  - 部分节点出厂默认 0xFFFF
  - 节点 join 后协调器分配，但 join 流程会失败
  - 解决：节点出厂统一 PAN ID

原因 3：Install Code CRC 错
  - ZigBee 3.0 强制 Install Code
  - Install Code = 16 字节 + CRC
  - 现场烧入时 CRC 算错 → TCLK 失败
  - 解决：烧录器自动算 CRC

原因 4：父节点 LQI 差
  - 节点选父节点时 LQI < 100
  - 链路质量差 → 频繁掉线
  - 解决：节点选父时 LQI 必须 > 150

原因 5：堆栈溢出
  - 大型项目 + 多 service = 堆栈不够
  - 节点 join 时崩溃
  - 解决：堆栈扩到 4KB+
```

### 修复（200 节点 85% → 99.5%）

```text
Step 1：金属环境 RF 勘测
  - 频谱仪扫 2.4 GHz
  - 找出"信号岛"（-82dBm 盲区）
  - 加中继 / 路由填补

Step 2：节点出厂配置
  - 全节点统一信道 15
  - 全节点统一 PAN ID
  - 全节点烧入正确 Install Code（含 CRC）

Step 3：节点选父优化
  - LQI > 150 才能选为父
  - 否则选下一候选
  - 多路由节点 + 中继

Step 4：堆栈配置
  - 堆栈从 2KB 扩到 4KB
  - Heap 从 4KB 扩到 8KB

Step 5：入网后验证
  - 网络拓扑图（zigbee2mqtt networkmap）
  - 200 节点全部入网 = 99.5%
```

### 复盘

- **金属环境盲区 -82dBm 是物理硬伤**——必须 RF 勘测
- Install Code CRC 错 = 工厂烧录通病
- 父节点 LQI 阈值是"选邻居"的关键参数
- 堆栈 / Heap 扩 2x 是大型项目标配
- 200 节点项目 = RF 勘测 + 全节点统一配置 + 选父优化

### 来源

- _Inbox/ZigBee-2026-08-21-candidates.md 候选 4
- NSTL / 晓网科技工业项目复盘
- ZigBee 3.0 Install Code 规范

---

## 案例 18：涂鸦多网关离线 15-30%（闭源固件 + 多网关同频 CCA 失败）

### 现象

12 个商业项目实测：

- 涂鸦多网关部署
- 子设备离线率 15-30%
- 客户投诉率 30%+

### 抓包 / 根因

```text
实测数据（12 商业项目）：
  - 离线率 15-30%
  - 核心矛盾：3 个

矛盾 1：网关间无动态信道协商
  - 涂鸦 5 个网关都选信道 15
  - 同空间同信道 → CCA 失败
  - 多网关同频 RSSI 差 < 3dBm → CCA 频繁冲突

矛盾 2：涂鸦 AF_ACK_REQUEST 不开放
  - 涂鸦私有协议不开 ACK 机制
  - 用户无法强制 ACK
  - 关键包丢失无重传

矛盾 3：ED 阈值错抬 6-8dB
  - End Device 接收灵敏度阈值错抬
  - 实际信号 -85dBm 被判为无效
  - 节点频繁"被认为离线"
```

### 修复

```text
强制信道隔离（4 步）：
  Step 1：手动给每个网关分信道
    - 网关 1：信道 11
    - 网关 2：信道 15
    - 网关 3：信道 20
    - 网关 4：信道 25
    - 5 个网关分 5 个信道
    - 同空间不冲突

  Step 2：LQI 分级
    - LQI > 200：稳定
    - LQI 100-200：监控
    - LQI < 100：拒收
    - 多网关选最高 LQI

  Step 3：NWK 调参
    - 默认 NWK 帧间隔 200ms
    - 多网关环境改 120ms
    - 减少冲突等待

  Step 4：跨层衰减 > 12dB 改 Thread
    - Thread 协议栈原生支持多网关
    - Channel Hopping 算法自动避频
    - 适合多网关环境
```

### 复盘

- **多网关同频 RSSI 差 < 3dBm 时 CCA 失败激增**——必须信道隔离
- 跨层衰减 > 12dB = 多网关环境**应该选 Thread 而不是 ZigBee**
- 涂鸦 AF_ACK_REQUEST 不开放 = 厂商闭源是隐性约束
- ED 阈值错抬 6-8dB = 闭源固件无法自定义
- 12 商业项目 = 真实数据，多网关环境必须警惕

### 来源

- _Inbox/ZigBee-2026-08-21-candidates.md 候选 5
- CSDN aiot 实战
- Thread vs ZigBee 选型对比

---

## 案例 19：ZigBee Transport Key 失败 3 根因 + Install Code 派生

### 现象

ZigBee 3.0 设备入网后 Transport Key 阶段失败：

- Router 反复 Rejoin 循环
- 链路层 LQI 正常但 APS 层无响应
- 加密链路建立失败

### 抓包 / 3 根因

```text
根因 1：APS Counter 跳变
  - 中间设备丢特定长度加密帧
  - APS Counter 跳变 → 重传
  - 反复跳变 → Transport Key 阶段无 ACK
  - 解决：检查 MTU / Fragmentation 配置

根因 2：Key Type 错值
  - Transport Key 必须 Key Type = 0x01（Network Key）
  - 错用 Link Key → 全链路加密失败
  - Trust Center Link Key vs Network Key 区别：
    - 0x01 = Network Key（节点 join 后用）
    - 0x03 = Link Key（应用层加密）
  - 解决：Trust Center 端配 Network Key

根因 3：加密标志位缺失
  - APS 层加密标志位 APS_ENCRYPTION = 0
  - Transport Key 明文传输 → 接收端拒
  - 解决：APS 命令前 set APS_ENCRYPTION
```

### 修复

```c
// Install Code 派生 Link Key
// 16 字节 Install Code → SHA-256 → 取前 16 字节 = Link Key
void install_code_to_link_key(uint8_t install_code[18], 
                              uint8_t link_key[16]) {
    uint8_t hash[32];
    // Install Code = 16 字节 + 2 字节 CRC
    SHA256_CTX ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, install_code, 16);  // 只 hash 前 16 字节
    sha256_final(&ctx, hash);
    memcpy(link_key, hash, 16);  // 取前 16 字节
}

// 入网流程（带 Install Code）
void zigbee_join_with_install_code(uint8_t install_code[18]) {
    uint8_t link_key[16];
    install_code_to_link_key(install_code, link_key);
    
    // 1. 设 Link Key
    zb_set_link_key(link_key);
    
    // 2. 发起 Transport Key
    zb_transport_key_request(APS_KEY_TYPE_TCLK, link_key);
}
```

### 复盘

- **Transport Key 失败 80% = Key Type 错**（0x01 vs 0x03）
- APS Counter 跳变 = MTU / Fragmentation 配置错
- 加密标志位缺失 = APS 命令前必设
- Install Code 派生 Link Key = ZigBee 3.0 标准
- 16 字节 Install Code + SHA-256 → 取前 16 字节 = Link Key

### 来源

- _Inbox/ZigBee-2026-08-16-candidates.md 候选 1
- CSDN 实战博客
- ZigBee 3.0 Install Code 规范

---

## 案例 20：化工厂 ZigBee "自愈变自杀"——非线性射频环境协议栈崩溃

### 现象

化工厂无线传感器网关：

- 现场无微波炉 / 大电机
- 理论 RF 环境可控
- **凌晨 3 点网关频繁掉线**（夜间无人值守）
- 白天偶尔恢复
- 持续一周

### 抓包 / 根因

```text
频谱仪抓包：
  - 现场无明显干扰
  - 但金属罐体多径效应
  - 接收端信号微抖动（毫秒级）
  - 触发 MAC 层重传

雪崩链路：
  Step 1：信号微抖动 → 1-2 包丢
  Step 2：节点 CSMA/CA 退避 → 信道忙等待
  Step 3：父节点判定子节点丢失 → 离网广播
  Step 4：子节点收到离网广播 → 触发 rejoin
  Step 5：rejoin 风暴 → 父节点表满
  Step 6：父节点瘫痪 → 子节点全部瘫痪
  Step 7：几秒内整个子网瘫
  Step 8：协调器未受影响（孤岛）
```

### 关键工程认知

```text
1. CSMA/CA 在多径下"过度谦让"
   - 标准假设：信号稳定
   - 实际：信号抖动 → CSMA 退避 → 累积延迟
   - 修复：禁 LBT（Listen Before Talk）

2. Datasheet 的 +20 dBm / -100 dBm 是暗室数据
   - 产线要看 Dk 漂移 → VSWR 恶化 → PA 发热负反馈
   - 实际灵敏度：-95 dBm（-100 dBm 缩水 5 dB）

3. MAC 重传风暴 + 离网广播 = "鬼影"雪崩
   - 几秒内整个子网瘫
   - 协调器不知道（孤岛）
   - 凌晨值班 = 0 告警
```

### 选型决策矩阵（什么时候该抛弃 ZigBee）

```text
**ZigBee 适合**：
  - 节点密度：30-50 个 / 网关
  - 实时性：< 50ms
  - RF 环境：办公 / 家用
  - 工业：仓储 / 物流

**ZigBee 不适合**：
  - 节点密度：> 50 个 / 网关
  - 实时性：> 50ms
  - RF 环境：金属密集 / 多径 / 强电磁
  - 工业：化工厂 / 钢铁厂 / 高电磁

**替代方案**：
  - LoRaWAN：远距 + 抗干扰（但实时性差）
  - TSN 有线：实时 + 抗干扰（但布线成本）
  - RS-485 + Modbus：传统工控
```

### 修复（4 步）

```text
1. 禁 LBT
   - 默认 ZigBee 3.0 开 LBT
   - 多径下必须关
   - 改 NWK 配置

2. 限 rejoin 频率
   - 默认 rejoin 每 60s 一次
   - 改 3600s（1 小时）
   - 避免雪崩

3. 协调器 firmware 锁版
   - 锁版本避免 OTA 改 GP sink
   - 锁硬件（不要换模组）

4. 远程诊断
   - RSSI / 噪声底 / 动态协商 TX
   - 数据远程可查
```

### 复盘

- **"自愈"反向 = 雪崩瘫痪**——ZigBee 在非线性射频环境的硬伤
- 选型决策：节点密度 + 实时性 + RF 环境 = 三维判断
- 化工厂 / 钢铁厂应该直接放弃 ZigBee
- 修复 = 禁 LBT + 限 rejoin + 锁固件
- 关键：CSMA/CA 在多径下过度谦让

### 来源

- _Inbox/ZigBee-2026-08-27-candidates.md 候选 1
- _Inbox/ZigBee-2026-08-29-candidates.md 候选 1
- _Inbox/ZigBee-2026-08-31-candidates.md 候选 1
- TrueSight 实战

---

## 案例 21：晓网 5 大根因——2000 平米仓库 300 节点凌晨 3 点批量掉线

### 现象

晓网电子（ZigBee 厂商）实战案例：

- 2000 平米仓库
- 300 节点部署
- 凌晨 3 点批量掉线
- 在线率 92%

### 抓包 / 5 大根因

```text
根因 1：父节点失效
  现象：50% 子节点连不上协调器
  根因：父节点（路由器）自身失效
        子节点不知道切父节点
  解决：
    - 父节点 LQI 检测
    - 失败阈值切换（> 3 次失败）
    - 自动选新父

根因 2：WiFi 干扰
  现象：白天掉线少，凌晨掉线多
  根因：白天仓库工作 → WiFi 少
        凌晨无人 → WiFi AP 自动信道变化
        自动信道变 11 → 覆盖 ZigBee 11-15
  解决：固化协调器信道 20/25

根因 3：路由老化
  现象：节点路由表失效
  根因：节点移动 / 库存变化 → 路由失效
  解决：路由表 10 → 20 扩容
        定期 rejoin

根因 4：电源跌落
  现象：节点周期性离线
  根因：仓库电瓶车充电 → 电源污染
  解决：电池 + DC-DC 隔离

根因 5：NVM 密钥丢失
  现象：节点 join 后掉线
  根因：FALSH 写保护错
        加密 key 没存住
  解决：NV_RESTORE + 异常掉电测试
```

### 实战 3 步诊断

```text
Step 1：硬件排查
  - 节点 LED 状态（红/绿/灭）
  - 父节点路由表状态
  - 电源纹波

Step 2：现场勘测
  - 频谱仪扫 2.4 GHz
  - WiFi AP 信道列表
  - 仓库货物摆放（金属遮挡）

Step 3：日志分析
  - NS 后台看每个节点最后上行
  - 离网广播次数
  - rejoin 风暴
```

### 修复 4 步

```text
1. 父节点 LQI 检测 + 失败阈值切换
2. 信道 20/25（避 WiFi 11）
3. 路由表 10 → 20 扩容
4. NV_RESTORE + 异常掉电测试
```

### 实战数据

```text
修复前：
  - 在线率：92%
  - 凌晨掉线：50% 节点

修复后：
  - 在线率：99.8%
  - 凌晨掉线：< 1%
```

### 复盘

- **5 大根因典型**（父节点 / WiFi / 路由 / 电源 / NVM）
- 凌晨掉线 = 排查 WiFi 自动信道
- 父节点失效 = 切父阈值 + 自动选新
- 路由老化 = 路由表扩容 + 定期 rejoin
- 92% → 99.8% = 4 步全做

### 来源

- _Inbox/ZigBee-2026-08-23-candidates.md 候选 1
- 晓网电子（ZigBee 厂商实战）
- CSDN 实战

---

## 案例 22：ZigBee 安全实战——BlackHat 2015 + Aviatrix 2024 工业 IIoT 渗透

### 现象

ZigBee 协议被多次证明有重大安全风险：

- 2015 BlackHat：Cognosec 公开 3 大产品安全漏洞
- 2024 Aviatrix：工业 ZigBee 渗透 + 3 CVE

### BlackHat 2015 三大攻击

```text
攻击 1：Hue / SmartThings / 门锁默认 TC Link Key
  - 出厂默认 `ZigbeeAlliance09`
  - 攻击者嗅探 rejoin 报文
  - 弱 key 降级攻击
  - 拿到 Network Key

攻击 2：ZLL Touchlink 远距离劫持
  - ZLL 协议 inter-PAN 帧明文无认证
  - 2015 年 master key 泄露（reddit）
  - 攻击者用泄露 master key + 100m 外发命令
  - 实际 36m 距离可劫持
  - 设计 2m，实测 36m

攻击 3：11 月无 key rotation
  - ZigBee 默认不轮换 Network Key
  - 攻击者拿到一次 key = 长期有效
  - 工业部署 = 一年不轮换 = 永久被控
```

### Aviatrix 2024 工业 IIoT 渗透

```text
真实工控 ZigBee 渗透链：
  Step 1：嗅探
    - 抓取 rejoin 报文
    - 提取 APS 层加密数据
  Step 2：弱 key 攻击
    - 工业 ZigBee 仍大量默认 key
    - rejoin 窗口持续抓网络 key
  Step 3：协调器仿冒
    - 用拿到的 key 加入网络
    - 协调器无法区分
  Step 4：端点重绑
    - 重新绑定控制端点
    - 拿到控制权
  Step 5：继电器劫持
    - 控制工业设备
    - 物理破坏 / 数据篡改

3 CVE 公开：
  - CVE-2024-XXXX：默认 key
  - CVE-2024-XXXX：rejoin 弱认证
  - CVE-2024-XXXX：ZLL 远程劫持

完整 MITRE ATT&CK 映射：
  - Initial Access：默认 key 嗅探
  - Persistence：rejoin 持续攻击
  - Lateral Movement：协调器仿冒
  - Impact：继电器劫持
```

### 修复（ZigBee 出厂安全基线）

```text
1. 弃用默认 key
   - 出厂生成独立 Install Code
   - 每节点唯一 Network Key
   - 不共享 master key

2. 强制 LE-SC（Secure Connections）
   - LE-SC = LE Legacy 替换
   - 抗中间人
   - 但 ZigBee 3.0 之前不支持

3. 启用 key rotation
   - 每月轮换 Network Key
   - 或每周（高安全场景）
   - 强制 rejoin 重新分发

4. 禁用 ZLL Touchlink
   - ZLL 设计有 backward compatibility 漏洞
   - 工业产品禁用
   - 3.0 修复（但老产品仍受影响）

5. 监控异常 rejoin
   - 频繁 rejoin = 攻击信号
   - 监控网络异常
   - 自动告警
```

### ZigBee 3.0 安全演进时间线

```text
- ZigBee HA 1.2（2007）：
  - 默认 Trust Center Link Key
  - 明文传输
  - 漏洞：嗅探 + 仿冒

- BlackHat 2015（Cognosec）：
  - 公开 3 大攻击
  - Hue / SmartThings / 门锁

- ZigBee 3.0（2016）：
  - Install Code 派发 Link Key
  - 强制 LE-SC
  - Trust Center Rejoin 改 Secure Rejoin

- ZigBee PRO 2023：
  - 进一步强化加密
  - 修复 3.0 已知漏洞

- 2024 Aviatrix：
  - 工业 IIoT 仍有 3 CVE
  - 默认 key 仍被广泛使用
  - rejoin 攻击仍有效
```

### 复盘

- **ZigBee 安全 ≠ 默认安全**——必须显式配置
- 默认 key = 永久被控
- ZLL Touchlink = 远程劫持入口
- Install Code + LE-SC = 出厂基线
- **2024 工业 IIoT 仍大量用默认 key**——必须主动加固
- 3.0 不是终点，PRO 2023 才是现代基线

### 来源

- _Inbox/ZigBee-2026-08-25-candidates.md 候选 1 + 候选 2
- BlackHat 2015 / Cognosec
- Aviatrix threat-research 2024
- Silicon Labs Zigbee Security

---

## 案例 23：ZigBee Green Power 3.0 全栈 + GP 能量收集设备"失踪"5 根因

### 现象

ZigBee Green Power（GP）3.0 协议——超低功耗能量收集场景：

- 5 根因致 GP 设备"配对后掉线"
- 加路由器反而更糟
- 协调器 OTA 后 GP sink 改变 = 全部 GP 设备失联

### Green Power 3.0 协议栈

```text
四角色：
  - GP Source（GP 发射器，能量收集）
  - GP Proxy（GP 代理，转发到 ZigBee 网状）
  - GP Sink（GP 汇聚，接收 GP 数据）
  - GP Combo（GP + ZigBee 双功能）

三层地址：
  - Source IEEE（GP 设备唯一 ID）
  - Source Network（GP 网络内 ID）
  - Alias（GP Proxy 用）

三种配网模式：
  - Commissioning：传统配网
  - Push：配对后入网
  - Auto-commissioning：自动发现 + 配对
```

### 实战代码模板（NXP JN516x）

```c
// GP 初始化
void gp_init(void) {
    // 1. GP Sink
    GP_RegisterSink();
    
    // 2. GP Proxy
    GP_RegisterProxy();
    
    // 3. 去重表（**本地**）
    GP_InitDeduplicationTable(GP_DEDUP_SIZE);  // 家庭 5-10 / 工业 15-20
    
    // 4. 配对窗口
    GP_SetCommissioningWindow(GP_COMMISSIONING_TIMEOUT);  // 2-3s
    
    // 5. 配对超时
    GP_SetTimeout(GP_TIMEOUT);
    
    // 6. 翻译表（GP ID → ZigBee 端点）
    GP_InitTranslationTable();
}

// GP 发送
void gp_send_button_press(uint8_t button_id) {
    uint8_t gp_frame[10];
    gp_frame[0] = 0x01;  // 简化命令
    gp_frame[1] = button_id;
    
    GP_SendFrame(gp_frame, 10, GP_FRAME_LIGHTWEIGHT);
}
```

### GP 设备"失踪"5 根因

```text
根因 1：缺 GP Proxy
  现象：GP 设备发数据，Sink 收不到
  根因：网络中没有 GP Proxy 节点
  修复：每个 Router 节点必须开 GP Proxy

根因 2：加路由器改 link cost
  现象：加 Router 后 GP 设备"消失"
  根因：路由表变化导致 GP 转发路径错
  修复：锁定 Router 位置，避免动态调整

根因 3：协调器固件差异
  现象：协调器 OTA 后 GP 全部失联
  根因：OTA 改了 GP sink 行为
  修复：协调器固件锁版（重要：GP sink 跟协调器版本绑定）

根因 4：能量不足
  现象：GP 设备配对后立即掉线
  根因：能量收集（如按压机械能）供不上
  修复：储能电容 + 多次按压触发

根因 5：配网漏
  现象：GP 设备配对后没入网
  根因：配对窗口太短（< 1s）来不及入网
  修复：延窗口到 2-3s
```

### 关键限制

```text
1. "**更多路由器≠更好**"
   - GP 依赖特定 proxy 转发
   - 路由 churn 撞微焦耳
   - 协调器 → 1 个 GP proxy（不需多）

2. ZigBee 仅 1 broadcast/s
   - 多 GP 广播必丢
   - 必须 unicast

3. 双向"二次握手"省 GP 接收能量
   - GP Source 发 → GP Proxy 收
   - GP Proxy 应答（一次握手）
   - 节省 GP Source 接收能量
```

### 部署方法论

```text
playbook：
  1. 固件锁版
     - 协调器固件必须锁
     - 不能 OTA 改 GP sink
  2. 代理近端
     - GP Proxy 放在协调器附近
     - 不要远端 Router
  3. 20 次触发回归
     - GP 设备配对后按 20 次
     - 验证稳定入网
  4. 配网窗口
     - 默认 2-3s
     - 电池 + 多次触发
```

### 关键参数

```text
家庭 SIZE：5-10 个 GP 设备
工业 SIZE：15-20 个 GP 设备
TIMEOUT：2-3s（家庭 / 工业）
去重表本地：GP Proxy 缓存，GP Sink 再过一遍
GP 地址冲突：优先级高于 ZigBee
```

### 复盘

- **Green Power = 超低功耗协议栈**——能量收集供电
- 4 角色 + 3 模式 + 3 层地址 = 必须严格配置
- "**更多路由器≠更好**"——GP 代理近端
- 协调器固件锁版 = GP sink 不能变
- 配网窗口 2-3s = 关键时间窗
- 20 次触发回归 = 部署标准

### 来源

- _Inbox/ZigBee-2026-09-01-candidates.md 候选 2 + 候选 5
- CSDN NXP JN516x 实战
- futurion 实战博客

---

## 案例 24：EFR32 NCP 并发 OTA 阻塞 50ms 触发 host assert（buffer 0x19 耗尽）

### 现象

HOST + EFR32MG21 NCP 架构：

- 0~5 终端并发起 OTA 升级
- NCP 偶发阻塞 50ms+
- host 端报 assert 失败
- 平台：EFR32MG21 + SiSDK 2024.06

### 抓包 / 根因

```text
NCP 日志：
  - 错误：`NCP has run out of buffers, error 0x19`
  - 持续触发
  - Host 端感知：50ms+ 阻塞 → timeout

三重打爆 NCP 缓冲区：
  1. OTA 升级中：图像 / 文件传输占大量 NCP 帧
  2. 0.5s polling：NCP 持续响应 OTA 进度查询
  3. 主机小时级属性读：NCP 缓存控制属性请求

默认配置：
  - NCP 缓冲区数量 = 64 帧
  - 一次 OTA 同时有：image 块 / progress 报告 / 属性读
  - 100 帧 / 5s = 20 帧/s
  - NCP 处理 30 帧/s
  - 持续累积 → 缓冲区耗尽 → 0x19
```

### 修复（官方方案）

```text
1. 改 `EZSP_CONFIG_PACKET_BUFFER_COUNT` 为 0xFF
   - 默认 64（0x40）
   - 改 0xFF = 255 个缓冲区
   - 解决：OTA 期间缓冲区够用

2. 检查 OTA Bootload Cluster 配置
   - 必须 enable OTA Bootload Cluster
   - 必须配 image 校验
   - 必须 image size 校准

3. 禁用 Packet Handoff plugin
   - Packet Handoff 是 EFR32 早期版本兼容方案
   - 新版 SiSDK 不需要
   - 禁用 = 减少内存压力
```

### 配置代码

```c
// EFR32 NCP 配置
void ncp_config_packet_buffer(void) {
    ezspStatus status;
    
    // 1. 改 NCP 缓冲区数量
    status = ezspSetConfigurationValue(EZSP_CONFIG_PACKET_BUFFER_COUNT, 0xFF);
    if (status != EZSP_SUCCESS) {
        log_error("Set packet buffer failed: 0x%02X", status);
    }
    
    // 2. 检查 OTA cluster
    status = ezspSetConfigurationValue(EZSP_CONFIG_OTA_POLL_PERIOD, 50);
    // 0.5s = 50 × 10ms
    
    // 3. 禁用 Packet Handoff
    status = ezspEnablePacketHandoff(false);
    if (status != EZSP_SUCCESS) {
        log_error("Disable packet handoff failed: 0x%02X", status);
    }
}
```

### 50ms 周期任务隐患

```text
Host 端常见：50ms 周期任务（如传感器读、状态查询）
  - 每个 50ms 任务触发 NCP 帧
  - 1s 20 帧
  - 50ms 任务 + OTA = 缓冲区压力 +1 倍

修：
  - 合并 50ms 任务为 100ms / 200ms
  - 或用 batch 模式（一次多读）
  - 或调整 OTA 时段（不与 50ms 任务同时）
```

### 复盘

- **`EZSP_CONFIG_PACKET_BUFFER_COUNT=0xFF` = 量产必设**
- Packet Handoff = 老版本兼容，新版禁用
- 50ms 周期任务 = 隐性观察窗
- OTA + 高频查询 = 缓冲区耗尽
- 3 件套：buffer count / OTA cluster / 禁用 handoff
- SiSDK 升级到 2024.06+ 默认修

### 来源

- _Inbox/ZigBee-2026-09-01-candidates.md 候选 3
- Silicon Labs 社区（工程师 Jesse）
- EFR32 + SiSDK 2024.06 实战

---

## 案例 25：SmartSpace zigbee2mqtt + Wireshark 90 天 4.2h→8min ROI 7.5x

### 现象

某企业 SmartSpace（智能空间）3 楼层部署：

- 90 天调试 pipeline
- 诊断时间从 4.2h 降到 8min（-96.8%）
- 非计划停机 47h → 3.2h/月（-93.2%）
- 设备可靠率 91.3% → 99.4%
- ROI 7.5x

### 抓包 / 根因

```text
3 类主要问题（90 天发现）：

1. Wi-Fi 信道 11 与 ZigBee 信道 15 重叠
   - 现象：丢包 + 延迟
   - 根因：2.4 GHz 共存
   - 修复：协调器信道改 25

2. 2 楼路由器电源故障致 47 个终端掉线
   - 现象：47 终端失联
   - 根因：电源失效
   - 修复：换路由器 + 电源监控

3. 占用传感器 100ms 上报（应是 10s）致消息风暴
   - 现象：网络拥塞
   - 根因：参数错配
   - 修复：参数改 10s
```

### 4 指标告警阈值

```text
LQI（Link Quality Indicator）告警：
  - 80 = 告警
  - 40 = 危急
  - 路由决策

Retrans 重传率告警：
  - 5% = 警告
  - 15% = 危急
  - 立即处理

设备超时：
  - 15 min 默认
  - 调整看场景

诊断间隔：
  - 5 min = 实时
  - 15 min = 标准
  - 1 h = 趋势分析
```

### 实战 ROI

```text
投入：
  - $2,400 硬件（Wireshark dongle × 3 + 抓包 PC）
  - 80 h 集成（python 监控脚本）
  - 1 年维护

回报（第一年）：
  - 诊断时间：4.2h → 8min × 20 次 / 月 = 节省 78h / 月
  - 停机时间：47h → 3.2h × $5k/h = 节省 $220k / 年
  - ROI = 7.5x
```

### 实战 pipeline 3 件套

```text
1. 多楼层分布式抓包
   - 每层 1 个 Wireshark dongle
   - 抓包时间戳对齐

2. Python 监控脚本
   - 抓 LQI / Retrans / 设备超时
   - 阈值告警
   - 日报推送

3. 应急响应流程
   - 告警 → 自动派单
   - 现场带数据排查
   - 数据驱动根因
```

### 复盘

- **3 抓包点 + Python 监控** = L4 实战工具
- 4.2h → 8min = 90 天调试的 ROI
- LQI 80/40 阈值 = 实战标准
- 100ms vs 10s 错配 = 拥塞
- 2 楼路由器电源 = 单点故障
- ROI 7.5x = 数据驱动

### 来源

- _Inbox/ZigBee-2026-09-04-candidates.md 候选 2
- _Inbox/ZigBee-2026-09-06-candidates.md 候选 2
- Johal 工程博客 90 天实测

---

## 案例 26：JN5169 ZigBee 量产踩坑——回流焊温区 + 半孔钢网 + 工艺一致性

### 现象

NXP JN5169 ZigBee 模组量产：

- 模块不启动（30% 不良）
- 调试器不连（生产工具识别不到）
- 距离短（50% 案例）
- 无法入网（5-10% 案例）
- 批次性问题（5% 拒收率）

### 7 类故障 + 根因

```text
故障 1：模块不启动
  根因：回流焊峰值 > 260°C 或 TAL 超时
  解决：炉温曲线 ≤ 260°C，TAL 60-90s

故障 2：调试器不连
  根因：SWD 引脚虚焊
  解决：补焊 + 检查 PCB 焊盘

故障 3：距离短
  根因：天线选型错 / 金属外壳屏蔽
  解决：M00 外置天线 / 玻璃钢外壳

故障 4：无法入网
  根因：信道 / PANID 不匹配
  解决：统一烧录

故障 5：批次性不良
  根因：来料检验漏
  解决：AQL 检验 + 老化测试

故障 6：电池续航短
  根因：未用 GPIO 漏电
  解决：终端深睡前改输入态

故障 7：天线辐射效率低
  根因：M00 / M03 / M06 选型错
  解决：按场景选（M00 = 外置 / M03 = 陶瓷 / M06 = IPEX）
```

### 3 大回流焊实战点

```text
1. 峰值温度
   - 标准：≤ 260°C
   - 实际：240-250°C 更安全
   - 超温：模块内部焊点融化

2. TAL（Time Above Liquidus）
   - 60-90s 标准
   - 超出 = 焊点过烧
   - 不足 = 冷焊

3. 钢网设计（半孔）
   - "内切外延"设计
   - 外圈开窗
   - 内圈过孔填充
   - 半孔焊盘关键
```

### JN5169 模组选型

```text
JN5169 模组选型：
  M00：外置天线（吸盘 / 棒状）
        - 工业现场、距离优先
        - 玻璃钢外壳
  M03：陶瓷天线
        - 小型化产品
        - 距离 30-100m
  M06：IPEX 连接器
        - 外置天线可换
        - 设计灵活
```

### 复盘

- **7 类故障** = JN5169 量产常见
- 回流焊 260°C + TAL 60-90s = 硬规范
- 半孔钢网"内切外延" = 工业经验
- M00/M03/M06 选型 = 按距离/外壳/可换性决策
- 未用 GPIO 漏电 = 终端深度睡眠必查
- 工艺一致性 = 批次性不良主因

### 来源

- _Inbox/ZigBee-2026-09-04-candidates.md 候选 3
- _Inbox/ZigBee-2026-09-06-candidates.md 候选 4
- wmrh.cn 嵌入式工程师博客
- NXP JN5169 datasheet §2.3

---

## 案例 27：高雄工厂 20+ 酸洗吊挂 ZigBee 监控（Router 互转 + VxCOMM 0 改代码）

### 现象

高雄某工厂 20+ 移动酸洗吊挂设备：

- 设备在金属钢梁 / 天车下移动
- 障碍密集
- PLC 通信需求
- 移动 + 强遮挡工业场景

### 抓包 / 方案

```text
泓格（ICP DAS）方案：
  - 协调器：ZT-2570
  - Router 节点：ZT-2551（每台 1 个）
  - 主机侧：VxCOMM 虚拟串口驱动

3 大关键点：
  1. Router 互转 = 天然 repeater
     - 没有 Router 的地方 = 信号盲区
     - Router 之间互转 = 移动设备不断网
     - 20+ 设备 = 必须 Router 互转

  2. 短帧 PLC 轮询 = ZigBee 黄金场景
     - PLC 周期短帧（< 100 B）
     - ZigBee 短帧高效
     - 1 主多从 = 标准 ZigBee 拓扑

  3. 大封包多包重组防误判
     - ZigBee 单包 ≤ 127 B
     - 大包 = 多包
     - 重组逻辑要稳
```

### 拓扑

```text
移动酸洗吊挂（20+）：
  - 节点 1 移动到 A 区
  - 节点 1 移动到 B 区
  - Router 1（A 区） ↔ Router 2（B 区） ↔ 协调器
  - 移动过程 = Router 接力
  - 主机通过协调器 + VxCOMM 虚拟串口通信

优势：
  - 移动不丢包
  - 主机代码 0 改
  - 强遮挡穿透
```

### 实战要点

```text
1. Router 选型
   - 工业级 ZT-2551
   - 防水防尘 IP65
   - 宽温 -25 ~ +75°C

2. 协调器选型
   - 工业级 ZT-2570
   - Ethernet / RS-485
   - 24V 工业电源

3. VxCOMM 虚拟串口
   - 主机侧装驱动
   - 创建虚拟 COM 端口
   - PLC 通信不变
   - 0 代码改

4. 短帧优化
   - PLC 轮询周期 = 1s
   - 帧长 < 100 B
   - 不需要大包优化
```

### 复盘

- **移动 + 强遮挡 = Router 互转**（天然 repeater）
- VxCOMM = 0 代码改
- 短帧 PLC = ZigBee 黄金场景
- 工业级 Router/协调器 = 防水防尘宽温
- 大包重组 = 多包逻辑要稳
- 泓格 ZT-2570 / ZT-2551 = 工业 Mesh 实战

### 来源

- _Inbox/ZigBee-2026-09-04-candidates.md 候选 5
- 泓格科技 案例库
- asmag 全球安防科技网

---

## 案例 28：智能家居 ZigBee Mesh 5 条军规（消费级实战）

### 现象

智能家居 ZigBee Mesh 部署，常见 5 类问题：

- 设备频繁掉线
- 自动化场景执行失败
- 远程控制延迟
- 电池设备续航短
- 升级后变砖

### 5 条军规

```text
军规 1：协调器放中心 + USB 延长线
  原因：
    - 协调器一般用 USB 供电
    - USB 3.0 干扰 2.4 GHz（噪声大）
    - 直接插主机 USB 3.0 = 干扰
  解决：
    - USB 延长线（远离 USB 3.0）
    - 或 USB 2.0 延长
    - 或加磁环

军规 2：先买常供电路由器再买电池传感器
  原因：
    - 电池设备不能当 Mesh backbone
    - 电池设备频繁入网/离网
    - Mesh 自愈需要 Router
  解决：
    - 常供电设备配 Router 功能
    - 电池设备配 End Device 功能
    - 部署顺序：先 Router 后电池

军规 3：路由器放"强弱交界"中点
  原因：
    - 信号强弱交界 = Router 黄金位置
    - Router 转发效率最高
    - 盲区填缝
  解决：
    - 现场勘测 RSSI 热图
    - 放交界点
    - 重复 2-3 次直到信号均匀

军规 4：场景只配常供电设备
  原因：
    - 电池设备响应慢
    - 自动化延迟大
    - 用户体验差
  解决：
    - 触发器 = 常供电（开关 / 插座 / 灯）
    - 响应器 = 任何
    - 自动化 = 协调器发起

军规 5：升级先在协调器 OTA，节点 OTA 慎用
  原因：
    - 协调器升级 = 高风险
    - 节点 OTA 协调器辅助
    - 升级失败 = 节点变砖
  解决：
    - 协调器固件稳定后再升级节点
    - 节点 OTA 必有回滚
    - 升级前备份配置
```

### 与 R6-6 案例 20（自愈变自杀）的区别

```text
R6-6 案例 20（化工厂自愈变自杀）：
  - 工业场景 = 金属密集 + 节点多
  - 选型决策 = 弃用 ZigBee
  - 强金属 + 实时 > 50ms 必弃

R10-9 智能家居军规：
  - 消费级场景 = 家用 + 节点少（< 50）
  - 选型 = ZigBee 可用
  - 优化覆盖 + 路由器策略
```

### 复盘

- **5 条军规** = 消费级 ZigBee 实战清单
- 协调器 USB 3.0 干扰 = 隐性坑
- Router 顺序 = Mesh backbone 关键
- 电池设备 = 末端节点，不能 backbone
- 升级协调器 = 高风险
- 工业 vs 消费 = 选型决策树

### 来源

- _Inbox/ZigBee-2026-09-06-candidates.md 候选 5
- futurion.blog 智能家居 Mesh 实战
- 与 R6-6 案例 20（TrueSight 化工厂自愈变自杀）对比

---

## 案例 29：Kaspersky Securelist Zigbee 工业环境安全评估

### 现象

Kaspersky Securelist 团队 nRF52840 模拟协调器 + 真实 Z-Stack 设备：

- 评估 Zigbee 工业部署安全性
- 测试私有 profile 设备对抗
- Update ID 厂商未定义行为

### 抓包 / 根因

```text
3 大发现：

1. nRF52840 协调器对私有 profile 设备失效
   - 厂商自定 Stack Profile（0x00/0x02）
   - 标准协调器不识别
   - 直接拒入网
   - 解决：明确 profile 兼容性

2. Python Scapy 跟不上 MAC ACK 时序
   - 802.15.4 MAC auto-ACK 192μs
   - Python 软件层不可达
   - 必须 C 改写固件
   - 解决：硬件级实时 ACK

3. Stack Profile 0x00/0x02 不匹配直接拒入网
   - Zigbee 3.0 强制 Profile 0x02
   - 厂商自定 Profile 0x00
   - 协调器 → 设备 入网请求 → Profile 不匹配 → 拒
   - 解决：明确 Profile 编码
```

### 实战要点

```text
1. Profile 兼容表
   - Profile 0x00：Zigbee（已废弃）
   - Profile 0x01：Zigbee PRO（早期）
   - Profile 0x02：Zigbee（3.0 标准）
   - 厂商私有：Profile 0x40+
   - 协调器必须明确支持

2. MAC auto-ACK 硬件级
   - 192μs 超时
   - 软件层无法响应
   - 必须 PHY 层硬件 ACK
   - 解决：用 nRF52840 / EFR32 硬件 ACK

3. Update ID 字段
   - Beacon 帧中
   - 厂商未定义 = 攻击面
   - 必须显式填值
```

### 复盘

- **nRF52840 模拟协调器** = 安全评估金标准
- 私有 profile = 工业部署第一坑
- Profile 0x00/0x02 不匹配 = 拒入网
- MAC auto-ACK = 192μs 硬件实时
- Python Scapy = 跟不上 = C 改写
- 工业 Zigbee = 显式 Profile 兼容

### 来源

- _Inbox/ZigBee-2026-09-07-candidates.md 候选 1
- Kaspersky Securelist
- Z-Stack 3.0 Profile 规范

---

## 案例 30：ZigBee 3.0 BDB / ZCL / ZGP 核心 + Reporting + APS_BindReq 实战

### 现象

ZigBee 3.0 开发者必踩 5 类坑：

- 信道
- 密钥
- 角色
- 绑定
- 内存

### BDB / ZCL / ZGP 三层

```text
BDB（Base Device Behavior）：
  - 配网 / 入网 / 复位
  - 3 模式：
    - 触摸配网（Touchlink）
    - 入网（Network Steering）
    - 找网（Network Finding）
  - 必走流程

ZCL（ZigBee Cluster Library）：
  - 标准化 cluster（on/off / level / temperature）
  - Reporting 机制
  - 属性读 / 写 / 通知
  - 控制链核心

ZGP（ZigBee Green Power）：
  - 能量收集设备
  - 超低功耗
  - 见 R6-7 案例 23 Green Power
```

### 2 大核心机制

```text
机制 1：Reporting（属性自动上报）
  - Min Interval：最小上报间隔
  - Max Interval：最大上报间隔
  - Reportable Change：变化量触发
  - 实战：
    - 温度：Min=10s, Max=60s, Change=0.5°C
    - 湿度：Min=10s, Max=60s, Change=1% RH
    - 电池：Min=1h, Max=24h, Change=5%
  - 触发：时间 OR 变化

机制 2：APS_BindReq（绑定表）
  - Cluster ID + Endpoint 绑定
  - 控制端：协调器 / 开关
  - 响应端：灯 / 锁 / 风扇
  - 例：开关 S2 绑定灯 L1 的 on/off cluster
  - 实战：控制链高效关键
```

### 5 类坑实战

```text
坑 1：信道
  - 现象：找不到设备
  - 修：广播 / 扫描信道一致

坑 2：密钥
  - 现象：join 后无通信
  - 修：Install Code 正确 + SHA-256 → Link Key

坑 3：角色
  - 现象：路由失效
  - 修：Router / ED / Coordinator 配对

坑 4：绑定
  - 现象：控制无反应
  - 修：APS_BindReq 配对

坑 5：内存
  - 现象：节点 crash
  - 修：堆栈 / heap 加大 + 释放 BDB
```

### 实战代码（AppBuilder + Network Analyzer）

```c
// Reporting 配置
zclReportCfg_t reportCfg = {
    .direction = ZCL_SEND_TO_COORDINATOR,
    .pEndpoint = &zclEntity_ep,
    .clusterId = ZCL_CLUSTER_ID_MS_TEMPERATURE_MEASUREMENT,
    .attrId = ATTRID_MS_TEMPERATURE_MEASURED_VALUE,
    .minReportInt = 10,  // 10s
    .maxReportInt = 60,  // 60s
    .reportableChange = 50,  // 0.5°C
};
zcl_configureReporting(&reportCfg);
```

### 复盘

- **BDB / ZCL / ZGP 三层** = ZigBee 3.0 核心
- Reporting = 时间 OR 变化触发
- APS_BindReq = 控制链高效
- 5 类坑 = 量产常见
- 内存坑 = Z-Stack 3.0 Resource Pool 必看
- AppBuilder + Network Analyzer = L4 工具

### 来源

- _Inbox/ZigBee-2026-09-07-candidates.md 候选 4
- wmrh.cn BitCloud + EFR32MG24 实战

---

## 案例 31：Tuya Private vs Standard 3.0 30s 上报拥塞协调器 crash

### 现象

某 15+ 电表 / 配电箱项目：

- 触发 data storm
- 协调器 crash
- 现象：电表数据丢失 + 协调器重启

### 抓包 / 根因

```text
2 大根因：

根因 1：30s 固定上报 + Tuya Private
  - 现象：每 30s 上报一次
  - 对 Standard 3.0：合理（adaptive data packing）
  - 对 Tuya Private：每属性独立包
  - 后果：带宽爆炸
  - 解决：
    - 改 Standard 3.0
    - 或开 adaptive packing
    - 或拉长间隔

根因 2：高密度 + 协调器处理能力
  - 现象：协调器 crash
  - 根因：15+ 设备 + 30s 上报 + 多属性 = 高负载
  - 协调器 CPU / 内存不足
  - 解决：
    - 增加协调器资源
    - 分散到多协调器
    - 降低上报频率
```

### Tuya Private vs Standard 3.0 差异

```text
Tuya Private：
  - 每属性独立 ZCL 帧
  - 1 设备 5 属性 = 5 帧 / 上报
  - 15 设备 × 5 帧 = 75 帧 / 30s = 2.5 帧 / s
  - 协调器必须处理每帧

Standard 3.0：
  - adaptive data packing
  - 多属性合并
  - 1 设备 5 属性 = 1 帧
  - 15 设备 × 1 帧 = 15 帧 / 30s = 0.5 帧 / s
  - 协调器负载降 5x
```

### 实战修复

```text
Step 1：选 Standard 3.0
  - 不用 Tuya Private
  - 选标准 ZCL
  - 选 EFR32 / nRF52 / Silicon Labs
  - 高密度必选标准

Step 2：协调器升级
  - 旧：嵌入式协调器
  - 升级：x86 主机 + ChirpStack + 多 worker
  - 处理能力 10x

Step 3：上报间隔
  - 30s → 60s（电表场景够用）
  - 负载降一半

Step 4：多协调器
  - 15+ 设备分散到 2-3 协调器
  - 每协调器 5-7 设备
  - 单点故障消除
```

### 复盘

- **Tuya Private vs Standard 3.0** = 5x 带宽差异
- 30s 固定上报 = 电表场景够用
- 高密度必选 Standard 3.0
- 协调器升级 = 选 x86 主机
- 多协调器 = 单点故障消除
- 选型决策 = 优先 Standard 3.0

### 来源

- _Inbox/ZigBee-2026-09-07-candidates.md 候选 5
- Bituo-Technik 能源表厂商官方排障文档

---

## 案例 32：仓库 ZigBee mesh 40 跳怪拓扑——router 密度 ≠ robustness

### 现象

某仓库 ZigBee mesh 部署：

- 30 ED + 8 Router + 1 Coordinator
- 测试 OK
- 现场一周后延迟爬升 3 秒
- 最近 20 英尺设备绕 6 节点
- LQI-based 路由贪婪找"便宜路径"
- 怪拓扑 = 延迟爆增

### 抓包 / 根因

```text
LQI（Link Quality Indicator）cost：
  - 节点选"便宜路径"（LQI 高 = cost 低）
  - 算法找 6 跳"看似便宜"路径
  - 实际：每跳累加延迟
  - 6 跳 = 6 × 50ms = 300ms
  - 加上 CSMA/CA 退避 = 3s
  - 远超 1 跳直接路径（50ms）

节点密度 = 双刃剑：
  - 太少：覆盖差
  - 太多：路由选择坏
  - 最佳：1-2 跳内覆盖
```

### 修复

```text
Step 1：减半 Router
  - 8 Router → 4 Router
  - 网格化（不要散点）
  - 测试 1 周稳定

Step 2：限制跳数
  - 设置 max_hops = 2
  - Z-Stack 3.0：NWK_MAX_DEPTH = 2
  - 超过 2 跳不允许

Step 3：选 hop count 而非 LQI cost
  - 算法参数改
  - 优先"少跳"而非"高 LQI"
  - 减少怪拓扑

Step 4：监控拓扑变化
  - 定期看 zigbee2mqtt networkmap
  - 检测怪拓扑
  - 自动告警
```

### 拓扑实战

```text
修复前：
  - Coordinator → R1 → R2 → R3 → R4 → R5 → R6 → ED
  - 6 跳 = 3s 延迟

修复后：
  - Coordinator → R1 → ED（最近路由）
  - Coordinator → R2 → ED（备份路由）
  - 1-2 跳 = 50ms 延迟
```

### 复盘

- **router 密度 ≠ robustness** = 反直觉
- LQI cost 算法 = 找便宜路径 = 怪拓扑
- 减半 router = 改善
- 限制跳数 = 关键
- hop count 优先 > LQI cost
- 监控 topology = 长期维护
- 工业 mesh 部署 = 1-2 跳优先

### 来源

- _Inbox/ZigBee-2026-09-09-candidates.md 候选 1
- moltbook 仓库 mesh 实战

---

## 案例 33：Hubitat FF01 广播风暴冲崩协调器（reporting 间隔对齐定时炸弹）

### 现象

某 Hubitat 智能家居部署：

- 11:00:01.583 收到 4 thermostat + 3 I/O module
- 同毫秒发 FF01 cluster
- 协调器 radio buffer 满
- 协调器关机
- parent-child timeout
- 设备循环重启
- 唯一恢复 = 物理 power cycle

### 抓包 / 根因

```text
触发条件：
  - 多 endpoint 设备
  - 同步 reporting 间隔
  - 毫秒级同时发 FF01 cluster
  - 协调器 radio buffer 满

FF01 cluster：
  - 设备 + 协调器能力协商
  - 必须有
  - 但同时多发 = 拥塞

11:00:01.583 时间窗：
  - 7 设备同毫秒
  - 协调器无线 capacity 12 packets/s
  - 7 设备 × 1 帧 = 7 帧 / ms = 7000 帧 / s
  - 协调器 5 帧 = 5 帧满
  - 后续 2 帧 = radio buffer 满
  - 协调器 crash
```

### 修复

```text
Step 1：错开 reporting 间隔
  - 设备 1：reporting 5 min
  - 设备 2：reporting 7 min
  - 设备 3：reporting 9 min
  - 错开 = 不同时发

Step 2：物理 power cycle 唯一可靠恢复
  - 协调器恢复后
  - 设备重新入网
  - 配置错开间隔

Step 3：去任一设备仍复现 = 系统性问题
  - 不是单个设备问题
  - 是 reporting 同步问题
  - 修：必须错开
```

### 实战（4 步）

```text
1. 找同毫秒发包的设备
   抓包看时戳

2. 改 reporting 间隔
   - 设备 1：5 min
   - 设备 2：7 min
   - 设备 3：9 min
   - 错峰

3. 协调器配置
   - 提高 RF buffer
   - 增强调度

4. 监控告警
   - 协调器内存
   - 设备时戳集中度
```

### 复盘

- **多 endpoint + 同步 reporting = 定时炸弹** = 真实问题
- 同毫秒 7 设备 = 协调器 radio buffer 满
- 物理 power cycle 唯一恢复
- 错开 reporting = 必做
- 同步问题 = 系统性不是单设备
- 毫秒级时戳 = 必看

### 来源

- _Inbox/ZigBee-2026-09-09-candidates.md 候选 3
- Hubitat 社区

---

## 案例 34：Z-Stack 20240710 BUFFER_FULL 0x11 物理重插——固件回退案例

### 现象

某用户使用 ZBDongle-P + Z-Stack 20240710 固件：

- 网络跑几小时后日志报 `0x11 BUFFER_FULL`
- 软重启 z2m 不恢复
- 物理重插协调器才恢复
- 业务网络不可接受

### 抓包 / 根因

```text
0x11 BUFFER_FULL：
  - Zigbee 协议栈内部 buffer 满
  - 根因疑似：
    1. 缓冲区管理缺陷
    2. 内存泄漏
    3. 异常路径未释放

软重启不恢复：
  - 重启后 buffer 状态未清
  - 重新分配 = 同样问题
  - 必须物理重插（断电清状态）

物理重插恢复：
  - 断电清全部状态
  - buffer 完全释放
  - 协调器正常运行
```

### 修复

```text
短期方案（workaround）：
  1. 回退固件
     - Z-Stack 20240710 → Z-Stack 20221226
     - 20221226 测试稳定
     - 这是 manufacturer 验证过的稳定版
  2. 配合 zigbee2mqtt 老版本
     - 老版本 + 老固件 = 兼容

长期方案（root cause）：
  1. 等待官方 fix
     - TI 已知问题
     - 修复版本待发
  2. 关键业务网络保留稳定版
     - 不轻易升级
     - 新版本先小规模灰度
```

### 关键工程认知

```text
- 关键业务网络 = 保留已知工作版本
- 新版本 = 小规模灰度
- BUFFER_FULL 0x11 = 软重启不恢复
- 物理重插 = 唯一可靠恢复
- 固件升级 = 风险操作
- 协议栈升级 = 必测 1 周稳定性
```

### 实战

```bash
# 1. 查看当前固件版本
Z-Stack 3.0.2 (built 20240710)

# 2. 备份配置
cp /config/zigbee.db /config/zigbee.db.bak

# 3. 刷老固件
# 通过 web flasher 刷 20221226 固件

# 4. 启动协调器
systemctl restart zigbee2mqtt

# 5. 验证
- 设备重新入网
- 监控 1 周稳定
- 不再 BUFFER_FULL
```

### 复盘

- **Z-Stack 20240710 BUFFER_FULL 0x11** = 已知问题
- 软重启不恢复 = 状态未清
- 物理重插 = 唯一可靠恢复
- 回退 20221226 = 短期修复
- 关键业务 = 保留稳定版
- 灰度升级 = 必走流程
- 协议栈 bug = 等官方 fix

### 来源

- _Inbox/ZigBee-2026-09-09-candidates.md 候选 4
- GitCode 博客 Z-Stack 实战

---

## 案例 35：ESP32-C6 sniffer RSSI histogram 定位"loud neighbor" desense

### 现象

某 ZigBee 网络 sniffer 一周撞 3 故障：

- 车库 Tuya 设备 -96dBm 直连无 router 备援
- 整网 NWK_NO_ROUTE 误报，实际 Hue 桥前级 desense
- 配对停滞

### 抓包 / 根因

```text
desense（去敏）：
  - 强信号在空间近（≠频段冲突）压低接收灵敏度
  - 真实现象：RSSI 极高但 PER 也高
  - 容易被误判为 NWK_NO_ROUTE（路由问题）
  - 实际是 receiver 阻塞

Hackaday 实战发现：
  - 3 类故障混在一起
  - RSSI histogram 面板定位 loud neighbor
  - 高帧率 + RSSI 集中 = 物理近
```

### RSSI histogram 算法

```python
# sniffer 抓包 1 小时
# 统计每设备 RSSI 分布
# 高峰 = 信号源位置
# 多设备共享高峰 = loud neighbor

import collections
rssi_hist = collections.Counter()
for packet in sniffed_packets:
    rssi_hist[packet.rssi] += 1

# 找高峰
top_5_rssi = rssi_hist.most_common(5)
for rssi, count in top_5_rssi:
    print(f"RSSI {rssi} dBm: {count} packets")
# 输出：
# RSSI -45 dBm: 5000 packets  ← loud neighbor
# RSSI -75 dBm: 200 packets
# RSSI -96 dBm: 50 packets   ← 远端设备
```

### 修复

```text
1. RSSI histogram 定位
   - 找高峰设备
   - 物理近 = desense 元凶

2. 空间隔离
   - 把 loud neighbor 远离协调器
   - 加吸盘天线
   - 屏蔽金属反射

3. 加 router 备援
   - 远端 Tuya 设备加 router
   - 直连太弱 -96dBm
   - router 转发 = -75dBm 健康

4. 重置 + 重配
   - 配对停滞
   - 协调器重置
   - 设备重入
```

### 复盘

- **desense 空间近 ≠ 频段冲突** = 真实坑
- RSSI histogram = 定位 loud neighbor
- 高峰 + 高帧率 = 物理近
- Hue 桥 = 高功率 = 阻塞其他
- Tuya 远端 -96dBm = 无 router = 死区
- 修复 = 空间隔离 + router 备援
- 配对停滞 = 协调器重置

### 来源

- _Inbox/ZigBee-2026-09-10-candidates.md 候选 1
- Hackaday.io 项目日志

---

## 案例 36：ESP32-C6 遥控器 4 层叠加故障（3 周调试实战）

### 现象

某 ESP32-C6 ZigBee 遥控器：

- 3 周调试
- 4 层叠加故障
- 实际：C6 SDK 跨芯片 bug + 配对漏配

### 4 层叠加

```text
层 1：setReporting 缺配
  - 现象：sensor 数据不回传
  - 根因：setReporting 配置缺失
  - 修复：ZCL Configure Reporting 命令

层 2：C6 SDK 跨芯片 bug（time cluster 缺实现）
  - 现象：time cluster 调用 null pointer
  - 根因：C6 SDK 跨芯片移植不完整
  - 修复：禁用 time cluster 或打补丁

层 3：Z2M converter 编码须与固件一致
  - 现象：HA 收到乱码
  - 根因：zigbee2mqtt converter 编码与固件不一致
  - 修复：检查 converter 与固件 cluster 编码

层 4：GPIO0 浮空需 5MΩ 下拉
  - 现象：上电 boot 模式错乱
  - 根因：ESP32 GPIO0 浮空 → boot 模式不确定
  - 修复：5MΩ 下拉电阻
  - 注意：兼顾"防浮空" + "键盘弱电压触发"
```

### NVS 双阶段

```text
NVS（Non-Volatile Storage）：
  - 阶段 1：上电初始化
  - 阶段 2：用户配对后

双阶段重配：
  1. 配对后存 NVS
  2. 启动时读 NVS
  3. 失败 → 重新配对
  4. 不要：单阶段（容易丢配对）
```

### 实战代码

```c
// 1. 5MΩ 下拉 GPIO0
// hardware: GPIO0 → 5MΩ → GND

// 2. NVS 双阶段
typedef enum {
    NVS_PHASE_INIT,
    NVS_PHASE_PAIRED
} nvs_phase_t;

void nvs_init_check(void) {
    nvs_phase_t phase = nvs_read_phase();
    if (phase == NVS_PHASE_INIT) {
        // 重新配对
        start_pairing();
    } else {
        // 已配对，复位
        restore_pairing();
    }
}
```

### 复盘

- **4 层叠加** = 真实调试常态
- setReporting 缺配 = 头号坑
- 跨芯片 SDK bug = 必查
- converter 编码 = 必须一致
- GPIO0 5MΩ 下拉 = 兼顾防浮空 + 弱电压触发
- NVS 双阶段 = 配对不丢
- 3 周调试 = 工业调试真实时长

### 来源

- _Inbox/ZigBee-2026-09-10-candidates.md 候选 3
- dredyson.com 工程复盘

---

## 案例 37：SNZB-02DR2 Telink 0xf000 OTA 解析失败 + 晓网 WLT 380 节点 99.6%

### A. SNZB-02DR2 OTA 失败

```text
2025-09 SNZB-02DR2 在 SONOFF 网关 OK：
  - 升级正常
  - 控制正常

在 Home Assistant（Z2M + ZHA）三症：
  - 症状 1：check fail
  - 症状 2：100% 卡住
  - 症状 3：推送缺失

根因：
  - Telink 0xf000 sub-element 插 Tag Info
  - 导致标准 ZCL OTA offset 错位
  - 解析失败

修复：
  - Z2M issue #9963 + #9984
  - 兼容 Telink 私货 sub-element
```

### 3 类 OTA 失败

```text
失败 1：传输失败
  - 网络问题
  - 多包丢失
  - 重传不收敛

失败 2：解析失败
  - 私货 sub-element
  - ZCL length 语义破坏
  - 厂商兼容性

失败 3：版本失败
  - 固件版本不匹配
  - 硬件 revision 错
  - image type 不符
```

### B. 晓网 WLT 工业模组 380 节点 99.6%

```text
传统 ZigBee 160 节点：
  - 离线 9.1%
  - 延迟 600ms+
  - AT 无返回 = 工位报废

晓网 WLT 380 节点：
  - 72h 满载测试
  - 在线 99.6%
  - 延迟 < 10ms
  - 视距 3km
  - 休眠 < 4μA
```

### 6 大 AT 无返回原因 + 对策

```text
1. 上电 3s 内发指令
   - 模组未初始化完
   - 对策：上电后延时 3s 再发 AT

2. 信道 25 抗 450MHz 谐波
   - 现场对讲机谐波
   - 对策：选信道 15/20/25

3. 串口参数错
   - 波特率 / 校验位
   - 对策：固化 115200-8-N-1

4. AT 指令后无 \r\n
   - 模组要求
   - 对策：发完加回车换行

5. 协调器地址错
   - AT+COORD? 查
   - 对策：校准地址

6. 固件 bug
   - 旧版本
   - 对策：升级最新
```

### 4 硬指标

```text
工业 ZigBee 模组选型 4 硬指标：
  1. 节点数容量：> 380
  2. 延迟：< 10ms
  3. 视距：> 3km
  4. 休眠功耗：< 4μA
```

### 复盘

- **SNZB-02DR2 Telink 0xf000** = 厂商私货 sub-element 突破 length
- OTA 3 类失败 = 传输 / 解析 / 版本
- 晓网 WLT 380 节点 99.6% = 工业标杆
- 6 大 AT 无返回 = 必走清单
- 4 硬指标 = 选型标准
- 上电 3s 延时 = 实战经验
- 私货 sub-element = 适配 checklist

### 来源

- _Inbox/ZigBee-2026-09-10-candidates.md 候选 4 + 候选 5
- SONOFF 官方博客
- 电子工程网 晓网科技

---

## 案例 38：化工厂自愈变自杀——多径→重传→离网广播雪崩

### 现象

化工厂部署 80 节点 ZigBee 传感网（温度/压力/可燃气），**凌晨 3 点集中掉线**：
- 单次掉线 5-15 节点，5 分钟内自愈
- 每周 2-3 次频发，重启协调器后恢复
- 白天产线运行正常，**仅夜班低温时段（<10℃）触发**
- 现场误判为"软件 bug"，实际是物理层多径 + 工业环境 PCB Dk 漂移叠加

### 抓包 + 根因（3 大根因）

#### 根因 1：金属罐体多径 → MAC 重传风暴 → 雪崩

- 化工厂 80 节点 + 大量 5m 高金属储罐 + 不锈钢管道
- 2.4 GHz 电磁波在金属罐体间**多径反射**——同一信号经 3-5 路径到达接收端
- 各路径长度差异 5-20m，**时延展宽 50-200ns**（远超 802.15.4 chip 500ns）
- chip 模糊 → MAC 帧 CRC fail → 重传
- **重传 3 次仍 fail → 父节点判该子节点 lost** → 发离网广播（"device leave"）
- 全网 30+ 节点同时判 lost → **离网广播雪崩** → 协调器收 30+ leave 帧 → 路由表清空 → 整网瘫
- **自愈机制反而成了自杀触发器**——"device leave"广播本身又触发新一轮 lost 判定

#### 根因 2：工业高温 PCB Dk 漂移 → 天线谐振偏移 2 MHz+

- 化工厂白天 35℃ + 阳光直射 PCB = **局部 50℃+**
- 夜班温变 -25℃（冬季室外）/ +10℃（室内）
- FR4 基板 Dk（介电常数）温漂系数 **+200 ppm/℃**
- 35℃ → 50℃ 变化 15℃ → Dk 漂移 0.3% → 50Ω 微带线阻抗漂移 1.5Ω
- **chip 天线谐振频率偏移 2 MHz+**（chip 天线 Q 值高，1.5Ω 漂移就明显）
- 2.4 GHz ISM 中心频点偏 0.1% → 反射增加 3dB → 链路预算 -3dB
- 叠加根因 1 的多径 → CRC fail 概率从 0.5% 涨到 5%

#### 根因 3：节点 > 30-50 触发路由表溢出

- 单协调器 ZigBee 3.0 路由表典型 40-60 项
- 80 节点 + 多 router → 路由表请求查询拥塞
- **查询响应超 802.15.4 MAC ack 时序（典型 5ms）** → 协调器判通信失败
- 表现：节点随机"看起来"掉线（实际是路由查询拥塞）

### 定位（4 步法）

```text
Step 1：频谱 + 抓包联动
  - 频谱仪看 2.4 GHz 频段（多径场景往往有 3-5 个尖峰）
  - 同时 ZigBee sniffer 抓包
  - 抓 fail 帧时间戳和 fail 节点位置
  - 命中：fail 节点呈"金属罐体集中分布"

Step 2：温度相关性分析
  - 装温度传感器记录 PCB 实测温度
  - 与掉线时间聚类
  - 命中：凌晨 3-5 点 + 温度谷值 = 强相关

Step 3：VNA 天线谐振点扫
  - 50℃ vs 10℃ 测天线 S11
  - 看谐振点是否偏移 2 MHz+
  - 命中：Dk 漂移 = 根因 2

Step 4：路由表监控
  - 协调器日志看路由表 size
  - 满 80 节点时 size 60/60 满
  - 命中：路由表溢出 = 根因 3
```

### 修复

| 根因 | 修复 | 验证 |
| --- | --- | --- |
| 1 多径 | 罐体旁加 RF absorber foam + 节点移开金属 0.5m+ | 多径尖峰 -10dB |
| 2 Dk 漂移 | 换高频基板（Rogers RO4350B，Dk 温漂 +50 ppm/℃） | 50℃ vs 10℃ 谐振漂移 < 0.5 MHz |
| 3 路由表 | 加 2 个 router 做中继，拆 80 节点为 3 个子网（30+30+20） | 每协调器路由表 < 30 |
| 兜底 | 离网广播限速（每秒 ≤ 5 帧）+ 父节点 lost 判定加 hysteresis | 雪崩概率 < 0.1% |

### 复盘

- **自愈变自杀 = ZigBee 工业部署最戏剧性失败模式**——自愈机制本身被攻击
- 工业 80 节点规模**默认要拆子网**——单协调器路由表不够是硬约束
- FR4 Dk 温漂在消费级不显形，工业 50℃ 温变**必须考虑**——选 Rogers/Isola 高频基板
- 多径 + 温漂 + 路由表溢出 = 工业 ZigBee 三联坑——**只解决一个不能根治**

### 来源

- _Inbox/ZigBee-2026-09-13-candidates.md 候选 1
- tsight.io（工业 IoT 工程博客）

---

## 案例 39：工业 ZigBee 渗透——Python/Zephyr C 双轨 + Private (0x00) vs Pro (0x02) 不兼容

### 现象

工业 ZigBee 安全评估项目（化工厂内部红队），试图批量复现"加入流程 + 离网 + 重放攻击"：
- 用 Python 高层协议栈（zigpy / bellows）跑 association → **加入失败率 80%+**
- 同一硬件用 nRF52840 + Zephyr C 固件跑 MAC ACK 解时序 → **100% 复现**
- 现场发现某 OEM 网关仅接受 **ZigBee Pro profile (0x02)**，排斥 Private (0x00)
- Python 工具用 Private profile 关联 → 网关直接 reject

### 抓包 + 根因（3 大根因）

#### 根因 1：Python 协议栈慢到 MAC ACK 超时

- zigpy + bellows（Python high-level 协议栈）在 Linux user space 跑
- association request → 等 network response → 解密 → 回复 ACK
- 端到端处理时间 **50-200ms**（Python GIL + I/O scheduling）
- 802.15.4 MAC ack **超时典型 5ms**（aResponseWaitTime MAC PIB attribute）
- 50ms vs 5ms = **ACK 已超时 10 倍** → 发送方判"对方不应答" → 重传 → 雪崩
- 实际 Z-Stack/Zephyr 协调器**直接 reject 慢设备**——视为"恶意"

#### 根因 2：Private profile (0x00) vs ZigBee Pro (0x02) 跨厂商不兼容

ZigBee 3.0 spec 定义两种 stack profile：
- **0x00 = ZigBee Private**（早期 1.x 遗留）
- **0x02 = ZigBee Pro**（3.0 主流）

实际工业部署发现：
- 老 OEM（Honeywell / Schneider 旧设备）= 0x00
- 新 OEM（Tuya / Aqara 主流）= 0x02
- **0x00 设备申请加入 0x02 网络 = 100% reject**（profile mismatch）
- 0x02 设备申请加入 0x00 网络 = 部分设备能加入但 commissioning cluster 不识别
- **Update ID 跨厂商行为未定义**——0x00 网关 update ID 0x05 跟 0x02 网关 update ID 0x05 **逻辑不同**

#### 根因 3：nRF52840 + Zephyr C 跑 MAC 才是工业可行解

- nRF52840 + Zephyr 固件在 RTC + radio ISR 内完成 MAC ACK
- 端到端处理时间 **< 500µs**（远低于 5ms ack timeout）
- 可模拟任何 stack profile（0x00 / 0x02 / 自定义）
- **能复现任何 802.15.4 MAC 层攻击**——replay / ack spoofing / energy jamming
- Python 协议栈**做不到这一层**——只能做 high-level 协议分析

### 定位（4 步法）

```text
Step 1：复现 association 失败
  - Python zigpy 配 nRF52840 802.15.4 sniffer
  - 抓 association request → 期望 response → 实际无 response
  - 时间戳：request 发出 +180ms 才到 response 解析完成
  - 命中：Python 慢 = 根因 1

Step 2：profile 检查
  - sniffer 解 association request payload
  - 找 stack profile 字节 = 0x00
  - 协调器广播 commissioning signal profile = 0x02
  - 命中：profile 不兼容 = 根因 2

Step 3：Zephyr C 固件重试
  - 写 Zephyr app 模拟 association（profile 0x00 和 0x02 两种）
  - 0x00 profile：reject（命中）
  - 0x02 profile：加入成功（验证）
  - 确认根因 2 + 解决方案

Step 4：ACK 时序实测
  - GPIO 测 nRF52840 ISR 响应时间
  - request 收到 → ISR 触发 → 处理 → ack 发送
  - 实测 320µs（< 5ms timeout）
  - 验证根因 3
```

### 修复 / 实战方案

| 场景 | 修复 | 验证 |
| --- | --- | --- |
| 工业 ZigBee 渗透 | 用 Zephyr C 固件（nRF52840）不用 Python | association 100% 复现 |
| 多厂商设备混用 | 现场**先抓 commissioning signal 看 profile** | 匹配后才能加入 |
| 老设备 0x00 加入新 0x02 | 网关开 legacy compatibility（spec 模糊）| 不可靠，需实测 |
| 协议分析 | zigpy 看 high-level + Zephyr 看 MAC + sniffer 抓 802.15.4 | 三层联动 |

### 复盘

- **Python 协议栈 = 工业 ZigBee 渗透的伪工具**——只能做 high-level 抓包
- nRF52840 + Zephyr C 才是工业可行解——MAC 层 ACK 时序 < 500µs
- Private (0x00) vs Pro (0x02) 是 ZigBee 3.0 spec 盲区——**spec 没强制要求 backward compatible**
- **跨厂商混用是工业项目常见需求**——commissioning signal profile 检查必须入 checklist
- Update ID 跨厂商行为未定义 = 升级协调器**前要全网 audit**

### 来源

- _Inbox/ZigBee-2026-09-13-candidates.md 候选 2
- Cubex Group（工业安全研究博客）
- IEEE 802.15.4-2020 §7.5.6.2（MAC ack timing）
- ZigBee 3.0 spec §5.4.3（stack profile）

---

## 案例 40：贪 LQI 不贪跳数——仓库 mesh 40 跳怪拓扑（路由优化诡计）

### 现象

仓库部署 30 端点（sensor）+ 8 router + 1 协调器，**lab 测试全过**，**一周后现场偶发 3 秒延迟**：
- 抓包显示端到端路径**跳数 6+ 跳**
- 单跳理论延迟 < 50ms，6 跳理论 < 300ms
- 实际端到端 3 秒（**10x 理论**）
- 减 router + 网格化回 1-2 跳后稳定
- 现场复现：在节点间来回走 30 步，延迟从 50ms 跳到 3 秒

### 抓包 + 根因（3 大根因）

#### 根因 1：ZigBee 路由表优化"贪 LQI 不贪跳数"

- ZigBee 路由选择算法（Z-Stack / EmberZNet）**默认按 LQI（链路质量）选路**，不按跳数
- LQI 高 ≠ 跳数少
- 现场 6 跳路径 = 每个单跳 LQI 80-100（信号强） → 算法判定"这条路径综合 LQI 高"
- 但**6 跳 × 50ms 单跳 + 重传 = 300ms + 2.7s 累积延迟**
- 算法**忽略了端到端总成本**——只看局部 LQI

#### 根因 2："dense ≠ robust" 拓扑反直觉

- 8 router 看似 mesh 健壮
- 实际：router 数量多 = **路由表项多 = 路径搜索空间大**
- 30 端点 + 8 router = **38 个 mesh 节点**，组合路径 4 万+
- 路由更新广播**风暴**——单一节点掉线触发 N 次路由重算
- 路由表**频繁翻动** → 端点频繁切换父节点 → 上层应用感知"延迟抖动"

#### 根因 3：稀疏可推理拓扑 vs 密集但不可预测

- 修复方案：**减到 3 router + 网格化布局**
- 修复后：3 跳以内，端到端 < 150ms
- **稀疏可推理拓扑 = 节点少、路径少、状态可枚举**
- **密集不可预测拓扑 = router 多、组合爆炸、状态机爆炸**

### 定位（4 步法）

```text
Step 1：抓单跳延迟
  - sniffer 看每跳的 request → ack 间隔
  - 单跳典型 30-80ms（包含 MAC 重传 + 上层重试）
  - 6 跳 = 180-480ms 理论

Step 2：抓端到端延迟
  - app 层 ping 协调器
  - 实际 3000ms+
  - 比例 10x 异常

Step 3：路径追踪
  - sniffer 解 network 层 source route
  - 看实际走的跳数
  - 发现 6 跳路径（不是直接 1 跳）

Step 4：拓扑重画 + 减 router 验证
  - 关掉 5 个 router（保留 3 个）
  - 重启后路径变 2 跳
  - 延迟回到 80ms
  - 验证根因
```

### 修复

| 手段 | 实施 | 验证 |
| --- | --- | --- |
| 减 router 数 | 8 → 3，按**物理位置最远 3 点** | 跳数 < 3 |
| 网格化布局 | 节点按等边三角网格摆，避免 router 扎堆 | LQI 分布 < 30 偏差 |
| 路由算法 | 改 Z-Stack `ROUTE_DISCOVERY_MODE` 选 min hops | 路径按跳数优化 |
| 跳数限制 | `MAX_HOPS_NWK` 设 5 | 超 5 跳重算路径 |
| 父节点稳定 | `PARENT_LINK_QUIESCE_TIME` 加 5x | 避免频繁切换 |

### 复盘

- **贪 LQI 不贪跳数 = ZigBee 路由算法反直觉陷阱**——Z-Stack / EmberZNet 默认行为
- "dense ≠ robust"——**router 数量与稳定性负相关**（在小规模 mesh）
- 稀疏可推理拓扑是工业 / 仓库部署的**正确心智模型**——3-5 router 上限
- Z-Stack `ROUTE_DISCOVERY_MODE` 改 min hops 是隐藏优化点
- **R12-3 案例 32 写过 40 跳怪拓扑但从 router 密度讲，本案例从 LQI 路由优化诡计讲**——互补

### 来源

- _Inbox/ZigBee-2026-09-13-candidates.md 候选 3
- moltbook 工程师实战帖
- Z-Stack 3.0 developer's guide §8.4（route discovery）

---

## 案例 41：HDI 板厂焊后离子残留——ZigBee 休眠 2 µA 飙 20 µA+（PCB 漏电隐形陷阱）

### 现象

智能门锁 ZigBee 模组（JN5169 / CC2538），消费级产线出货 1 万件：
- 设计 spec 休眠功耗 2 µA（行业标杆）
- 实际产线抽测 **5% 件 = 20 µA+**（10x 偏大）
- 续航从 1 年降到 **< 2 个月**（电池 240 mAh）
- 7 天高温高湿（85℃/85% RH）测试后 → 90% 件漏电
- **回原板厂（换可信赖供应商）→ 100% 件 72h 湿度箱稳**

### 抓包 + 根因（3 大根因）

#### 根因 1：HDI 板厂焊后离子残留 → 湿度下 PCB 漏电

- 廉价 HDI 板厂**焊后清洗不充分**（或根本不洗）
- 残留：助焊剂（rosin flux）+ 离子（Na⁺/Cl⁻/Br⁻）
- 干燥环境（产线测试）**漏电不显形**（离子电导需要水）
- 湿度环境（85% RH）→ 离子水合 → **PCB 表面形成薄电解液层**
- 漏电路径：相邻 trace（间距 0.1mm）→ 离子电导
- 阻抗从 100 GΩ（干燥）降到 **1-10 MΩ**（潮湿）
- 漏电流 3.3V / 1 MΩ = 3.3 µA → 多条漏电路径 = 20 µA+ 总漏

#### 根因 2：LDO 动态响应 > 静态电流（被 datasheet 误导）

- 项目选 LDO 重点看 quiescent current（静态 Iq）
- 选 XC6206（Iq 1 µA，datasheet 标"超低功耗"）
- 实测 ZigBee 模组休眠瞬间（radio 关闭）→ 3.3V 跌到 3.1V（**200 mV 跌落**）
- XC6206 瞬态响应差 → 200 mV 跌落恢复要 5ms
- 期间**电流从 1 µA 飙到 100 µA**（datasheet 标瞬态峰值）
- 平均功耗涨 **2-3 µA**（看似小，但放大量级就是 50%）
- **datasheet 静态 Iq ≠ 实际动态 Iq**——必须实测 sleep → wake transition

#### 根因 3：32.768 kHz 晶振 ESR 高 + 负载电容失配

- 32.768 kHz 晶振起振慢（典型 1-3 秒）
- 廉价晶振 ESR 80 kΩ（spec 应 < 50 kΩ）
- 内部 inverter gain 不足 → 启动时间**延长 2-3 秒**
- 启动期间工作电流 5 µA（正常 1 µA）
- **负载电容失配**（layout 寄生 + 晶振标称 CL 失配）
- 振荡器工作点偏移 → 振幅不稳 → 频率偏移 → MCU 内核定时器校准重做 → 多耗 1 µA
- 三个 1 µA 叠加 = 2 µA spec 变 5 µA 实际

### 定位（4 步法）

```text
Step 1：漏电流路径定位
  - 拆下 ZigBee 模组 + 切断所有走线 + 单独测 VCC 漏电流
  - 设计 2 µA → 实际 20 µA → 确认漏电
  - 切断 radio 部分后 → 仍有 18 µA → 漏电不在 radio

Step 2：PCB 漏电验证
  - 整板 85℃/85% RH 72h 后测
  - 漏电从 1 µA 涨到 20 µA
  - 高倍显微镜看焊点 + PCB 表面
  - 命中：助焊剂残留 + 离子污染 = 根因 1

Step 3：LDO 动态测试
  - 示波器 + 电流探头测 LDO 输出
  - 看 sleep → wake 转换
  - 输出跌 200mV + 恢复 5ms
  - 命中：LDO 动态 = 根因 2

Step 4：晶振验证
  - 换低 ESR 晶振（Abracon 替代）
  - 启动时间从 3s 降到 0.8s
  - 实测功耗降 1.5 µA
  - 命中：晶振 = 根因 3
```

### 修复

| 根因 | 修复 | 验证 |
| --- | --- | --- |
| 1 离子残留 | 换可信赖板厂（焊后严格清洗）+ 离子污染度测试 ≤ 1.56 µg/cm² NaCl eq | 85/85 72h 后漏电 < 5 µA |
| 1 备选 | 加 conformal coating（三防漆）阻隔湿度 | 同上验证 |
| 2 LDO 动态 | 换 TPS782（Iq 0.5 µA + 动态响应快，5µs 恢复） | 跌落 < 50 mV |
| 3 晶振 | 换低 ESR 晶振 + 严格匹配 CL（实测 layout 寄生） | 启动 < 1.5s |
| 3 备选 | 用内部 RC 振荡器（精度差但低功耗稳） | 牺牲精度换功耗 |

### 复盘

- **离子残留 = 隐形寄生电阻**——干燥环境测不出，湿度下崩
- **datasheet 静态 Iq ≠ 实际动态 Iq**——必须测 sleep → wake 转换
- 晶振 ESR + CL 失配 = 启动功耗 1-3 µA 增量——**低功耗设计必测**
- 廉价 HDI 板厂是消费级 IoT 续航的**最大隐形威胁**
- **conformal coating 是性价比补救**——但**首选还是换可信赖板厂**

### 来源

- _Inbox/ZigBee-2026-09-13-candidates.md 候选 4
- SprintpcbGroup（PCB 厂博客）
- IPC-TM-650 §2.3.25（离子污染度测试标准）

---

## 案例 42：JN5169 量产工艺——M00/M03/M06 选型 + 邮票孔内切外延 + 回流焊 TAL 严控

### 现象

NXP JN5169 ZigBee 模组量产（消费级智能插座，10K 件/月）：
- 选型阶段纠结 M00（外置天线）/ M03（PCB 天线）/ M06（IPEX 连接器）
- 量产回流焊后**虚焊率 8%**（spec 应 < 0.5%）
- 客户退回件中 **70% 是半孔/邮票孔焊盘开裂**
- 改钢网 + 改回流焊曲线后虚焊率降到 0.3%
- 同期某 OEM 用同样 JN5169 走 2 年没出问题——**工艺差异是根因**

### 抓包 + 根因（3 大根因）

#### 根因 1：M00 / M03 / M06 选型反决策

JN5169 模组有 3 种天线封装：
- **M00 = 外置天线（SMA 连接器）**：金属外壳场景优（信号不被屏蔽）
- **M03 = PCB 天线**：成本低（省连接器），但**金属外壳场景不能用**
- **M06 = IPEX 连接器**：可换外置天线，**最灵活**但成本 +$0.5/件

实际项目选 M03（省 $0.3/件）→ 装入金属外壳智能插座 → **天线被屏蔽 → 链路预算 -8dB**
表现：lab 测试正常，**客户家里距离 5m 就失联**——误判为模组质量问题。

#### 根因 2：邮票孔半孔工艺 = 虚焊高发区

- JN5169 模组采用 **stamp hole（邮票孔/半孔）工艺** 做 PCB 边连接
- 邮票孔 = 模组边缘半镀铜孔，**焊盘宽度仅 0.4-0.5mm**
- 模组贴片到主板上时，**半孔焊盘的爬锡高度必须严格控制**
- 普通钢网开孔 1:1 → 锡膏量不足 → 半孔爬锡 < 50% → **开裂 / 虚焊**
- **正确工艺 = 钢网"内切外延"开孔**：
  - 内（靠近模组）：开孔缩 10% → 减少锡膏量
  - 外（远离模组）：开孔扩 15% → 增加爬锡面积
  - 总锡膏量适中 + 焊点面积足够 = **爬锡 > 80%**

#### 根因 3：回流焊峰值/TAL 不严控

JN5169 模组 + 主板 = 异型混装：
- 模组（已塑封）能耐温 < 245℃
- 主板其他元件（电感/晶振）能耐 260℃+
- **典型错配 = 主板 reflow profile 给 260℃ peak + TAL 90s**
- 模组**耐不住** → 内部芯片引线键合应力 → 长期可靠性降
- 短期表现：开裂、虚焊
- 长期表现：3-6 月后开裂

正确 reflow profile：
- **预热 150-180℃ 60-90s**（缓慢均匀）
- **TAL (Time Above Liquidus 217℃) = 60-75s**
- **峰值 240-245℃**（不要 260℃）
- **降温速率 ≤ 3℃/s**（避免热冲击）

### 定位（4 步法）

```text
Step 1：虚焊定位
  - X-ray 看半孔焊点
  - 发现 70% 退回件 = 半孔开裂 / 爬锡 < 50%
  - 命中：邮票孔工艺 = 根因 2

Step 2：天线选型验证
  - 把虚焊件的天线剪短
  - 测距离 vs 完整模组
  - 装金属外壳后距离从 30m 降到 5m
  - 命中：M03 + 金属外壳 = 根因 1

Step 3：reflow profile 审计
  - 量产回流焊曲线与 JN5169 datasheet spec 对比
  - peak 255℃（spec 240℃）+ TAL 85s（spec 60-75s）
  - 命中：reflow 超 spec = 根因 3

Step 4：同款 OEM 对比
  - 问 2 年没出过问题的同行 OEM
  - 人家用 M00（外置天线）+ 内切外延钢网 + 245℃ reflow
  - 全部工艺差异 = 三联坑
```

### 修复

| 根因 | 修复 | 验证 |
| --- | --- | --- |
| 1 天线选型 | 金属外壳场景**强制 M00 或 M06**（不用 M03） | 距离 > 20m |
| 2 邮票孔钢网 | 改"内切外延"钢网（内缩 10% + 外扩 15%） | 爬锡 > 80% |
| 2 备选 | 加 underfill（底部填充胶）补强 | 跌落测试通过 |
| 3 reflow | peak 245℃ + TAL 60-75s + 降温 ≤ 3℃/s | 炉温曲线实测 |

### 复盘

- **M00/M03/M06 选型 = JN5169 量产第一道坑**——金属外壳不能用 PCB 天线
- **邮票孔工艺**是 NXP 模组特有的高发虚焊区——必须用"内切外延"钢网
- **回流焊 TAL 严控 = 长期可靠性关键**——不是只看虚焊率
- **R9-2 案例 25 写过 JN5169 量产回流焊**（元器件侧）但**本案例新增**：
  1. 三种天线选型反决策
  2. 邮票孔"内切外延"钢网工艺
  3. 模组+主板异型 reflow profile

### 来源

- _Inbox/ZigBee-2026-09-13-candidates.md 候选 5
- wmrh.cn（无线模组技术博客）
- NXP JN5169 datasheet §13.1（reflow profile spec）
- IPC-7530（钢网设计指南）

---

## 案例汇总

| # | 现象 | 根因 | 难度 |
| --- | --- | --- | --- |
| 1 | CC2530 ReJoin 失败 | NLME 状态机 BUG + NV 残留 | 高 |
| 2 | zigbee2mqtt 50+ 掉线 | USB 适配器 / 配置错 | 中 |
| 3 | EFR32 NCP crash | 无 SWO 调试 | 中 |
| 4 | End Device 撑不过 1 周 | Poll Control 错配 | 低 |
| 5 | 多 Coordinator 冲突 | PAN ID 冲突 | 中 |
| 6 | 0x8A 误判 | 属性 vs Cluster 错 | 低 |
| 7 | 默认 Link Key | 量产用公开 key | 高 |
| 8 | Z-Stack 版本互操作 | 协议栈大版本 | 中 |

## 关联文档

- `bus/zigbee.md` 主题入口
- `bus/zigbee-practical.md` 调试流程速查
- `bus/zigbee-deep-dive.md` 协议栈深挖
- `bus/zigbee-index.md` 主题地图 + 导航
