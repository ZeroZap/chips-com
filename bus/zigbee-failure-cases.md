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
