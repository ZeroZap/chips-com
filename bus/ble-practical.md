# BLE Practical Guide

## 目标

本文用于 BLE 工程调试：广播、扫描、连接、配对、MTU、PHY、错误码、产线常见故障的快速定位。

## 最小接线（以 nRF52832 为例）

```text
VDD ──── VDD (1.7~3.6V)
GND ──── GND
ANT ──── 2.4GHz 天线（PCB 走线天线 / 陶瓷天线 / IPEX 外接）
DEC1 ──── 100nF + 10µF 紧靠 VDD 引脚
DEC2 ──── 100nF 紧靠 DEC1 引脚
```

**关键约束**：

- 天线 50Ω 阻抗匹配到 RF 输出引脚
- 走线避开噪声源（DC-DC、晶振、时钟线）
- 地平面完整，天线下禁止铺地
- 馈线长度 < 5mm（推荐），阻抗连续
- 屏蔽罩（可选）减少外部干扰

## 关键参数

### 连接参数三件套

| 参数 | 范围 | 影响 |
| --- | --- | --- |
| Connection Interval | 7.5 ms ~ 4 s | 主从通信周期，越短吞吐越大功耗越高 |
| Slave Latency | 0 ~ 499 | 从机可跳过的连接事件数，>0 省电但增加延迟 |
| Supervision Timeout | 100 ms ~ 32 s | 超时未收到则断开，必须 > (1 + Slave Latency) × Connection Interval × 2 |

**典型档位**：

```text
低功耗档（纽扣电池）：
  Connection Interval  = 1000 ms
  Slave Latency        = 4
  Supervision Timeout  = 6000 ms

平衡档（可穿戴）：
  Connection Interval  = 100 ms
  Slave Latency        = 1
  Supervision Timeout  = 400 ms

高吞吐档（OTA / 音频）：
  Connection Interval  = 15 ms
  Slave Latency        = 0
  Supervision Timeout  = 200 ms
```

### 连接参数协商 SOP

主从建立连接后参数是「建议值」，从机可以请求更新，主机**可以拒绝**。真实产线里参数协商失败比"广播不亮"更难定位。

```text
Step 1: Slave 发 LL_CONNECTION_PARAM_REQ
        → Interval_Min / Interval_Max / Latency / Timeout
Step 2: Master 决定接受 / 拒绝 / 反提新参数
        → 接受：LL_CONNECTION_PARAM_RSP
        → 拒绝：LL_REJECT_IND (reason = 0x3A Unsupported)
        → 反提：LL_CONNECTION_PARAM_RSP 带新区间
Step 3: 双方生效，INSTANT 事件触发
        → 之后所有连接事件按新参数跑
```

**高频断连码（参数协商失败三件套）**：

| 错误码 | 名称 | 常见原因 | 解决方向 |
| --- | --- | --- | --- |
| 0x3B | UNACCEPTABLE_CONNECTION_PARAMETERS | Master 拒绝区间 | 从机放宽 Min/Max 边界 |
| 0x08 | INSTANT_PASSED | INSTANT 已过 | 从机避开发送窗口 |
| 0x05 | AUTHENTICATION_FAILURE | LTK 缺失 | 清除 bonding 重新配对 |

**真实产线坑：iOS vs Android 参数偏好冲突**

```text
iOS 默认：Interval = 30 ms，Latency = 0
Android 默认：Interval = 7.5 ms（部分机型） / 50 ms（其它）
国产智能锁固件：Interval 最低 15 ms（强制）

典型翻车：iPhone 连接后，Slave 请求 15 ms 失败（iOS 走 30ms 兜底）
         之后又反提 7.5 ms，Master 不接受 → 0x3B 反复触发
         用户体验：连接后几秒断连
对策：
  1. Slave 端 Interval_Min 设为 30 ms（兼容 iOS）
  2. Master 端写 reject 逻辑时返回 reason = 0x3A + LOG 记录
  3. 调试时抓 nRF Sniffer，对比 LL_CONNECTION_PARAM_REQ/RSP 时序
```

**调试思路**：

```text
1. nRF Sniffer 抓 LL_CONNECTION_PARAM_REQ/RSP
2. 对比 Reject / Accept 分布
3. 看 Master 拒绝时的 reason 码
4. 设备固件看是否有限速逻辑（节能 / 协议栈默认）
5. 多次握手失败 → 怀疑 bonding 残留，从机清 FDS 整片
```

### PHY 档位（BLE 5.x）

| PHY | 速率 | 灵敏度 | 范围 | 功耗 |
| --- | --- | --- | --- | --- |
| LE 1M | 1 Mbps | -94 dBm | 基准 | 基准 |
| LE 2M | 2 Mbps | -91 dBm | - | ↑↑ |
| LE Coded S2 | 500 kbps | -97 dBm | 2× | ↑ |
| LE Coded S8 | 125 kbps | -103 dBm | 4× | ↑↑ |

### 广播参数

| 参数 | 范围 | 典型 |
| --- | --- | --- |
| Advertising Interval | 20 ms ~ 10.485 s | 100 ms（快发现）/ 1 s（省电） |
| Advertising Type | ADV_IND / ADV_DIRECT_IND / ADV_SCAN_IND / ADV_NONCONN_IND | ADV_IND |
| Primary PHY | LE 1M / LE Coded | LE 1M（默认） |
| Secondary PHY | LE 1M / LE 2M / LE Coded | LE 1M（默认） |

### MTU

```text
默认 MTU  = 23 字节（ATT 默认）
协商 MTU  = 247 字节（ATT 最大）
有效载荷  = MTU - 3（L2CAP 头 + ATT 头）
```

**长包写入必须用 `prepare_write` + `execute_write`（分片）**，单包超 MTU 会返回 `ATT_ERR_INVALID_ATTR_VALUE_LEN (0x0D)`。

#### Android BLE MTU 实战（20 字节硬限）

Android 蓝牙协议栈对单包数据有一个**隐性硬限 20 字节**，跟 MTU 协商无关，是内核层 buffer size 限制：

```text
现象：MTU 协商到 247 成功，但发 50 字节 notify，Android 收到只 20 字节
根因：博通（Broadcom）Android 蓝牙协议栈 + 部分国产芯片（AP62XX 全志）
      内核层 ATT 收包 buffer = 20 byte，写再多也截断
      iOS 无此限制（Apple 协议栈直传全部）
      某些国产 BLE 模组（Allwinner + 博通组合）现象更明显

实测数据：
  iOS 15+: MTU=247，单包 notify 200 字节 → 全部收到 ✅
  Android 12 (Pixel 6): MTU=247，单包 notify 200 字节 → 收到 200 字节 ✅
  Android 10 (小米/红米部分): MTU=247，单包 notify 200 字节 → 收到 20 字节 ❌
  全志 Tina + AP62XX: MTU=247 → 20 字节截断（不论 Android 哪个版本）

跨平台安全值：
  MTU 协商到 244+（理论最大）但**实际单包 ≤ 20 字节**（分片到 < 20/包）
  接收端 buffer 累积合并
  用 prepare_write/execute_write 走 L2CAP 分片更稳（不依赖 ATT notify）
```

**修复方案**：

```text
固件侧：
  1. 单包 notify ≤ 20 字节（Android 兼容默认）
  2. 长数据走 GATT Write（分片 prepare_write + execute_write）
  3. 给 Android 端 demo 一个明显的"分片已合并"日志

产线侧：
  1. 测试矩阵：iOS + 主流 Android（至少 3 个品牌）跨平台测
  2. 写自动化测试：发 100 字节数据，看每个平台收到多少
  3. 测试用例要包含"全志 + 博通"这种已知坑平台
```

## 抓包工具

| 工具 | 平台 | 优势 | 限制 |
| --- | --- | --- | --- |
| nRF Sniffer + Wireshark | nRF52840 DK / 专用 dongle | 免费、协议解析全 | 仅支持 Nordic 芯片抓包 |
| Ellisys Bluetooth Tracker | USB 硬件 | 全协议 + 同步 2.4GHz 波形 | 贵（>10K 美元） |
| Teledyne LeCroy | USB 硬件 | 专业级 | 贵 |
| hci_dump + btsnoop | 软件抓 HCI log | 无需硬件 | 仅看 host 端，无法看空中 |
| nRF Connect / LightBlue | 手机 App | 现场快速验证 GATT | 浅层 |
| BLEDebug + CH9143 | Windows 10/11 PC | 替代 nRF Connect 跑 Windows 端 BLE 调试；CH9143 串口-蓝牙透传做桥接 | 需 Win10 1803+；廉价适配器可能不持 BLE |

**产线推荐组合**：

```text
研发调试：nRF Sniffer + Wireshark（看 ATT/GATT/SMP 全程）
产线批量：手机 nRF Connect 跑连接测试脚本（看 RSSI + 吞吐 + 断连率）
压测：btsnoop + 自动化脚本
```

### nRF52832 高数据率发送实战

nRF52832 跑官方 `ble_app_uart` 例程，发高数据率时最容易"看起来在跑但其实丢了"：

```c
// ❌ 错：未等 TX 完成就发下一包
void send_data(uint8_t *data, uint16_t len) {
    ble_nus_data_send(&m_nus, data, &len, m_conn_handle);
    // 直接发下一包 → 触发 0x3E + 看门狗复位
}

// ✅ 对：等 BLE_GATTS_EVT_HVN_TX_COMPLETE 事件
static bool tx_busy = false;
void send_data(uint8_t *data, uint16_t len) {
    if (tx_busy) return;  // 上一次还没发完
    tx_busy = true;
    ble_nus_data_send(&m_nus, data, &len, m_conn_handle);
}

void on_ble_evt(ble_evt_t *p_ble_evt) {
    switch (p_ble_evt->header.evt_id) {
        case BLE_GATTS_EVT_HVN_TX_COMPLETE:
            tx_busy = false;  // 释放锁，可发下一包
            break;
    }
}
```

**踩坑点**：
- 6 次重发 vs supervision timeout 是两套机制：重发由协议栈自动重试，断连由 supervision timeout 触发
- 2.4GHz 拥挤环境（办公区 / 路由器旁）建议加应用层重连逻辑
- 频偏必须匹配官方 DEMO 板，否则 PHY 层就丢

### Host 电源管理影响 BLE 链路（隐性坑）

蓝牙适配器在 Windows 上**被允许"省电休眠"**，但 BLE 长连接对实时性敏感，省电会引入断连：

```text
症状：
  Windows 笔记本上 BLE 设备随机断连（短时 30s ~ 数小时）
  Linux/macOS 上不出现
  重启后能恢复，但过一会又断

根因：
  Windows 默认允许 USB/内置蓝牙适配器进入省电模式
  → 适配器周期性掉电
  → BLE 长连接视为"链路丢失"
  → 触发 0x08 CONNECTION TIMEOUT

修复：
  控制面板 → 设备管理器 → 蓝牙适配器 → 属性 → 电源管理
  取消勾选「允许计算机关闭此设备以节省电源」

  PowerShell 一键（管理员）：
    powercfg /devicequery wake_armed
    powercfg /devicedisablewake "Bluetooth Device"

产线提醒：
  给客户的 Windows 笔记本预装"取消蓝牙省电"批处理
  否则客户现场 1 周后必然投诉
```

## 调试步骤

1. **量天线阻抗**：VNA 量 RF 输出端口，50Ω + 史密斯圆图落在中心
2. **看广播**：手机 nRF Connect 扫描，确认设备名 + Service UUID 可见
3. **看连接**：手机连接，触发读写，看 GATT 流程
4. **看错误码**：HCI log / Wireshark 解析错误事件
5. **看 RSSI**：连接后实时 RSSI，-80 dBm 以内稳定
6. **跑距离测试**：1m / 5m / 10m / 隔墙，逐档验证

### LightBlue 6 项外设产前 checklist

Punch Through（LightBlue 厂商）建议外设生产前必过 6 项检查 + LightBlue vs 自家 App 二分定位法：

```text
6 项外设 checklist（覆盖 90% 现场失败）：
  1. **广播**：nRF Connect / LightBlue 能看到设备 + Service UUID
  2. **连接**：能稳定建链，RSSI > -80dBm
  3. **服务发现**：discoverServices() 能列全所有 Service / Characteristic
  4. **读写**：Read / Write / Notify 三种类型各测 1 个 characteristic
  5. **配对**：能完成配对，绑定信息持久化
  6. **重连**：断电后能自动重连（NV 持久化）

LightBlue vs 自家 App 二分定位法：
  - 同一台外设
  - 用 LightBlue（标准 central）测 → 通过
    → 自家 App 失败 = App stack 配对 bug
  - 用 LightBlue 测 → 失败
    → 外设固件 bug
  - 二分定位**责任侧**，app bug 成本指数级上升
  - 6 项 checklist + LightBlue 二分 = 外设量产前必备工具

LightBlue 优势：
  - 跨平台（iOS / Android）
  - 标准 central 协议栈（接近 nRF Connect）
  - 配对流程标准（Just Works / Passkey / OOB）
```

## 常见问题速查

| 现象 | 优先检查 |
| --- | --- |
| 扫描不到设备 | 广播没启 / 广播间隔太长 / 天线没接 / 电池电压低 |
| 频繁断连 | 连接参数错 / 电源不稳 / 信号弱（RSSI < -90）/ 干扰 |
| 连接后几秒断连 | 参数协商失败（0x3B/0x08/0x05）→ 看「连接参数协商 SOP」段 |
| 配对失败 | IO 能力不匹配 / 配对码错 / bonding 信息残留 |
| 写入返回 0x0D | MTU 不够 / 数据超长没分片 |
| 通知收不到 | CCCD 没写 0x0001 / Service changed 事件没处理 |
| 功耗偏高 | 连接间隔太短 / Slave Latency 0 / 广播太频繁 |
| 距离近（< 5m） | 天线匹配差 / 走线错 / 净空区不足 / DC-DC 干扰 |
| 跨平台连接失败 | BLE 协议版本不一致（4.0 vs 5.x）/ 自定义 Service UUID |

## 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 完全扫不到 | 广播 / 天线 / 电源 | nRF Connect 扫，看设备名 |
| 配对失败 | IO 能力 / 配对码 | 检查 bonding flash 残留 |
| 写入超长失败 | MTU 不够 | `GATT_MTU exchange` 协商到 247 |
| 通知不来 | CCCD 没启用 | 写 `0x2902` CCCD = `0x0001` |
| 0x3E 断开 | 信道拥塞 | 改连接间隔到 50ms+ |
| 0x3D 断开 | MIC 校验失败 | 检查 LTK / 加密参数 |
| 0x08 断开 | 监控超时 | 调大 Supervision Timeout |
| 距离近 | 天线问题 | VNA 量阻抗，示波器看 RF |
| 跨平台不连 | 协议版本 | 统一 BLE 5.x |
| 功耗大 | 参数没省 | Slave Latency 调到 4+ |

## HCI STATUS 错误码速查（Core 5.0 Vol 2 Part D）

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x00 | SUCCESS | 正常 |
| 0x01 | UNKNOWN HCI COMMAND | 未知 HCI 命令 |
| 0x02 | UNKNOWN CONNECTION IDENTIFIER | 无效连接句柄 |
| 0x05 | AUTHENTICATION FAILURE | 认证失败（配对错） |
| 0x08 | CONNECTION TIMEOUT | 监控超时 |
| 0x0C | COMMAND DISALLOWED | 当前状态不允许 |
| 0x12 | PAIRING NOT ALLOWED | 不允许配对 |
| 0x13 | REMOTE USER TERMINATED | 远端主动断 |
| 0x16 | LOCAL HOST TERMINATED | 本地主动断 |
| 0x1A | UNSUPPORTED REMOTE FEATURE | 远端不支持特性 |
| 0x22 | LMP RESPONSE TIMEOUT / LL RESPONSE TIMEOUT | 链路层超时 |
| 0x28 | INSTANT PASSED | 加密 / PHY 更新时机过期 |
| 0x3A | CONTROLLER BUSY | 控制器忙 |
| 0x3D | MIC_FAILURE | MIC 校验失败 |
| 0x3E | CONNECTION FAILED TO BE ESTABLISHED | 连接失败（同步包丢失） |

## ATT Error 速查

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x01 | INVALID HANDLE | handle 无效 |
| 0x02 | READ NOT PERMITTED | 该 handle 不允许读 |
| 0x03 | WRITE NOT PERMITTED | 不允许写 |
| 0x05 | INSUFFICIENT AUTHENTICATION | 鉴权不够 |
| 0x06 | INSUFFICIENT AUTHORIZATION | 授权不够 |
| 0x07 | INSUFFICIENT ENCRYPTION | 加密不够 |
| 0x0D | INVALID ATTRIBUTE VALUE LENGTH | 数据超 MTU（没分片） |
| 0x0E | UNLIKELY ERROR | 服务器内部错误 |
| 0x13 | APPLICATION ERROR 0x80+ | 应用自定义 |

## nRF52832 实战注意

- **通知发送必须等 `BLE_GATTS_EVT_HVN_TX_COMPLETE`** 才能发下一包，否则 L2CAP 拥塞触发 0x3A BUSY
- **长包写入用 `sd_ble_gattc_write` + 分片**（`WRITE_REQ` → `PREPARE_WRITE_REQ` × N → `EXECUTE_WRITE_REQ`）
- **Service Changed**（0x2A05）必须实现，否则 OTA 后主机缓存失效
- **Bonding Flash 操作**：用 `fds`（Flash Data Storage），不要直接写 flash page
- **SoftDevice 错误码**：用 `nrf_error.h` 的 `NRF_ERROR_*`，不是 HCI 错误码
- **天线走线**：nRF52832 DK 的天线走线是 50Ω 参考，长度 < 5mm

## 检查清单

```text
□ 电源：稳压到 1.7~3.6V，纹波 < 50mV
□ 去耦：每个 VDD 引脚 100nF + 10µF 紧靠
□ 天线：50Ω 匹配，VNA 验证 S11 < -10dB
□ 晶振：32.768 kHz + 32 MHz（高频精度 ±40 ppm）
□ 固件：协议栈版本（SoftDevice S140 v7+）与 SDK 匹配
□ 广播：ADV_IND + 设备名 + Service UUID
□ 连接参数：按功耗档配（低功耗 / 平衡 / 高吞吐）
□ MTU：协商到 247
□ 配对：Just Works / Passkey / OOB 按场景选
□ Bonding：fds 持久化，重启可恢复
□ 安全：LE Secure Connections（ECDH P-256），不只用 LE Legacy
□ 错误码：HCI / ATT / SMP 三套错误码都要能解析
```

## 关联文档

- `bus/ble.md` 主题入口
- `bus/ble-deep-dive.md` 协议栈深挖
- `bus/ble-failure-cases.md` 产线实战案例
- `bus/ble-index.md` 主题地图 + 导航
