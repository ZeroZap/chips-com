# Thread 产线实战案例库

## 目标

把产线常见的 Thread 入网失败、PSKc 错、Channel Mask 错、RPL 路由震荡、Border Router 切换、Sleepy End Device 频繁唤醒等问题写成案例库。每个案例：

- 现象（现场）
- 抓 log / 抓包（判断）
- 定位（根因）
- 修复（代码 / 配置）
- 复盘（如何预防）

案例来源：实战复盘 + 已知问题库。

## 案例 1：PSKc 派生错，Joiner 找不到 Commissioner

### 现象

Thread 智能门锁量产 1000 台，30% 设备首次入网失败，App 提示"配对失败"。log 显示"Discovery Timeout"。

### 抓 log

```text
Joiner log:
  > joiner start J01NME
  Discovery Request
  ... 5 秒 ...
  Discovery Timeout
  > joiner stop

Commissioner log:
  > commissioner add 8c1fb5a1b2c3d4e5 J01NME 60
  Joiner added
  ... 60 秒 ...
  Joiner Not Joined (timeout)
```

### 定位

**PSKc 派生错**：

```c
// 错：Commissioner 端派生 PSKc
uint8_t pskc[16];
otCommissioningGeneratePskc(
    master_key,                    // 16 字节
    eui64,                         // Joiner EUI-64
    pskd,                          // 字符串
    ext_panid,                     // 8 字节
    pskc                           // 输出 16 字节
);

// Joiner 端派生 PSKc
uint8_t pskc[16];
otCommissioningGeneratePskc(
    master_key,
    eui64,
    pskd,
    ext_panid,
    pskc
);
// 必须保证双方 master_key 一致
// 必须保证 ext_panid 一致
// 必须保证 EUI-64 顺序一致（LE）
```

**根因**：

- Master Key 在两设备不一致
- Extended PAN ID 字节序错
- EUI-64 字节序错（Little-Endian / Big-Endian）

### 修复

```c
// 1. Master Key 必须统一
const uint8_t master_key[16] = {
    0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
    0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff
};

// 2. Extended PAN ID 字节序一致
const uint8_t ext_panid[8] = {
    0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77
};

// 3. EUI-64 字节序（厂商芯片有 LE/BE 之分）
// 工厂烧录用网络字节序
// 运行时转 LE（OpenThread 默认）

// 4. PSKd 字符串
const char *pskd = "J01NME";  // 6 字节
// 长度 6~32，建议 8+ 字节

// 5. 工厂烧录校验
void factory_verify_pskc(void) {
    uint8_t pskc[16];
    otCommissioningGeneratePskc(
        master_key, eui64, pskd, ext_panid, pskc);
    
    // 写入 KVS
    kvs_write("pskc", pskc, 16);
    
    // 验证
    uint8_t verify[16];
    kvs_read("pskc", verify, 16);
    if (memcmp(pskc, verify, 16) != 0) {
        log_error("PSKc write failed");
    }
}
```

### 复盘

- **PSKc 派生一致性** 是配对关键
- **Master Key 工厂统一**（建议 Master Key = 网络标识）
- **Extended PAN ID 字节序** 统一
- **EUI-64 字节序** 烧录前先确认
- **PSKd 长度** 至少 8 字节

---

## 案例 2：Channel Mask 全部清 0，设备找不到网络

### 现象

Thread 智能灯泡 500 台，40% 设备入网失败。log 显示"Discovery 阶段失败"。

### 抓 log

```text
> scan
|  11 |  26 |  0   |  0  |  -65  |  0    |
|  12 |  26 |  0   |  0  |  -68  |  0    |
|  ...                                                |

只显示信道，但没看到 Thread 网络
```

### 定位

**Channel Mask 被清空**：

```c
// 错：Channel Mask 0 = 全部禁用
otLinkSetChannelMask(0);
// 设备完全扫描不到

// 修复：Channel Mask 至少包含目标信道
uint32_t mask = 0x07FFE400;  // 避 Wi-Fi 1, 6, 11
otLinkSetChannelMask(mask);
```

**根因**：

- 工程师测试时为了节省时间 `otLinkSetChannelMask(0)` 限制信道
- 工厂批量烧录时忘记恢复默认
- 工厂烧录脚本错

### 修复

```c
// 1. 工厂烧录前必须设置
void factory_default_settings(void) {
    // 1. Channel Mask
    uint32_t mask = 0x07FFE400;  // 避 Wi-Fi 1, 6, 11
    otLinkSetChannelMask(mask);
    
    // 2. Master Key
    otLinkSetMasterKey(master_key, sizeof(master_key));
    
    // 3. Extended PAN ID
    otLinkSetExtendedPanId(ext_panid, sizeof(ext_panid));
    
    // 4. Network Name
    otLinkSetNetworkName("MyThreadNet");
    
    // 5. PAN ID
    otLinkSetPanId(0x1234);
    
    // 6. Channel
    otLinkSetChannel(15);
    
    // 7. 写入持久化
    otInstanceSaveToFile(instance);
}

// 2. 烧录后验证
void factory_verify_settings(void) {
    uint32_t mask = otLinkGetChannelMask();
    if (mask == 0) {
        log_error("Channel Mask is 0, scan will fail");
    }
    
    const char *name = otLinkGetNetworkName();
    if (strcmp(name, "MyThreadNet") != 0) {
        log_error("Network Name mismatch");
    }
}
```

### 复盘

- **Channel Mask 0 = 全部禁用**，配网必失败
- **工厂烧录必须有 verify 流程**
- **烧录脚本必须有 default settings 恢复**
- **每台设备出厂前必须能 scan 到主网络**

---

## 案例 3：多 Thread 网络共信道，邻居 PAN ID 干扰

### 现象

智能家居客户部署了 2 套 Thread 网络（A 和 B），都在 15 信道。设备掉线率 30%。

### 抓 log

```text
> scan
|  15 |  26 | 0x1234 | ... |  -65  |  my-thread   | ← A 网络
|  15 |  26 | 0x5678 | ... |  -62  |  other-thread | ← B 网络（邻居干扰）

Joiner 困惑：哪个是合法网络？
```

### 定位

**共信道干扰**：

- A 网络 0x1234
- B 网络 0x5678
- 都在 15 信道
- Joiner 选错网络概率高

**根因**：

- 客户买了两套 Thread 设备（不同品牌）
- 都没改默认配置
- 邻居 PAN 干扰

### 修复

```c
// 1. Channel Mask 严格限制（避邻居信道）
// 邻居用 15 → 我们改用 16
uint32_t mask = 0x07FE0400;
// bit 16 = 1，其他避

// 2. 改 PAN ID
otLinkSetPanId(0xABCD);  // 自定义，避免冲突

// 3. 改 Network Name
otLinkSetNetworkName("MyHomeThread");

// 4. 改 Extended PAN ID
uint8_t ext_panid[8] = { /* 自定义 */ };
otLinkSetExtendedPanId(ext_panid, 8);

// 5. Channel Selection 算法
// 优先选 RSSI 最强 + PAN ID 唯一
```

**Channel 实际选择策略**：

```c
// 自动选信道：扫 11-26，选 RSSI 最强 + 干扰最小
int select_best_channel(void) {
    int best_channel = 0;
    int best_score = -1000;
    
    for (int ch = 11; ch <= 26; ch++) {
        if (!(channel_mask & (1 << ch))) continue;
        
        // 算 score
        int rssi = scan_rssi[ch];
        int interference = scan_interference[ch];
        int score = rssi - interference * 2;
        
        if (score > best_score) {
            best_score = score;
            best_channel = ch;
        }
    }
    return best_channel;
}
```

### 复盘

- **多 Thread 网络共信道是常见踩坑**
- **Channel Mask + 自定义 PAN ID 双保险**
- **自动选信道**（避免手动配）
- **生产前扫信道** 必备

---

## 案例 4：REED 升级 Router 失败，子节点数限制

### 现象

智能灯 1000 台部署到大型商场。开始几天稳定，1 周后 30% 设备掉线。

### 抓 log

```text
> child table
| 001 | 8c1fb5a1... | 5 | r |    5 |  120 |  0 |  0 |
| 002 | 8c1fb5a2... | 5 | r |    5 |  120 |  0 |  0 |
...
| 010 | 8c1fb5aa... | 5 | r |    5 |  120 |  0 |  0 |

子节点已达 10（默认上限）
第 11 台请求加入 → 拒绝
```

### 定位

**子节点数限制**：

```c
// 默认 maxChildren = 10
otRouterSetMaxChildren(10);  // 默认

// 智能灯都 Router-capable，但选了 FTD (Router) 模式
// Router 数 = 16-64（依网络大小）
// 父节点数限制导致加入失败
```

**根因**：

- 网络内 Router 数不足
- 部分 Router 已被 10 个子节点占满
- 新设备找不到父节点

### 修复

```c
// 1. 提高 maxChildren（推荐 20-30）
otRouterSetMaxChildren(20);

// 2. 调整 Router 数（基于网络规模）
// 网络规模计算：
//   Router 数 = max(32, ceil(设备数 / maxChildren))
//   例如：1000 设备 / maxChildren=20 = 50 Router

// 3. REED 升级 Router
// REED 设备满足条件自动升级 Router
// 条件：网络 Router 数 < nwkRouterThreshold
// 默认 nwkRouterThreshold = 16 或 32

// 4. 监控
void monitor_router_count(void) {
    int routers = otRouterGetRouterIdSequence(instance);
    int leader_id = otRouterGetLeaderId(instance);
    int max_routers = otRouterGetRouterIdRange(instance);
    
    if (routers >= max_routers) {
        log_warn("Router table full");
    }
}
```

### 复盘

- **大规模 Thread 部署必须算 Router 数**
- **REED 自动升级** 是关键
- **maxChildren 配置** 根据设备密度调整
- **监控 Router 表** 避免满

---

## 案例 5：RPL 路由震荡，链路质量差

### 现象

Thread 智能灯部署到工厂车间，灯光闪烁。log 显示 RPL 父节点频繁切换。

### 抓 log

```text
20:30:01  RPL: Parent switch (Router1 → Router2)
20:30:03  RPL: Parent switch (Router2 → Router1)
20:30:05  RPL: Parent switch (Router1 → Router2)
...
20:30:30  RPL: Stable (Router2)
```

### 定位

**RPL 父节点震荡**：

```c
// 链路 ETX 边界值：
//   1 跳：ETX 1（极好）
//   2 跳：ETX 2（一般）
//   3 跳：ETX 3（差）

// 震荡场景：
//   Router1 RSSI = -75, ETX = 1.5
//   Router2 RSSI = -73, ETX = 1.4
//   边界值，频繁切
```

**根因**：

- 工厂车间 Wi-Fi 干扰大
- 2.4 GHz 频段拥塞
- Router 数量少，子节点依赖近场 RF

### 修复

```c
// 1. 启用 MRHOF + Hysteresis
otThreadSetRouterSelectionJitter(120);  // 120s 延迟切换
otThreadSetRouterSelectionThreshold(1);  // 切换阈值

// 2. 调高最小 ETX 差
otThreadSetMinParentSelectionImprovement(3);  // ETX 差 < 3 不切换

// 3. 减少 RSSI 边界
// 工厂车间建议 RSSI < -80 才考虑切

// 4. 加更多 Router
// 50 台设备 / Router = 10 Router

// 5. 改用 OF0 + 跳数优先
otThreadSetPreferredRouteCost(otRouteCostOfETX(1.5));
```

**Hysteresis 配置**：

```c
// OpenThread 配置
otRouteCostConfig config = {
    .mMinCost = 1,         // 最小 ETX
    .mMaxCost = 7,         // 最大 ETX
    .mHysteresis = 3,      // 切换需要 ETX 差 ≥ 3
    .mThreshold = 1,       // 切换触发阈值
};
otThreadSetRouteCostConfig(&config);
```

### 复盘

- **RPL 震荡是边界 ETX 值导致**
- **Hysteresis 必备**（避免频繁切换）
- **加 Router** 比调参有效
- **Wi-Fi 干扰大场景** 改用 5 GHz AP 让 2.4 GHz 干净

---

## 案例 6：Border Router 切换导致 Thread 网络重组

### 现象

智能家居客户，Home Assistant + OTBR 在树莓派上。树莓派重启后，所有 Thread 设备短暂掉线。

### 抓 log

```text
BR log:
  Border Router shutting down
  ... 30s ...
  Border Router starting up
  Network: New partition ID 0x12345678
  Leader: New RLOC16 = 0x0400

Thread devices:
  20s 全部 Detached
  30s 全部 Rejoined
  40s 全部 Operational
```

### 定位

**Border Router 切换触发网络重组**：

```c
// 树莓派断电 30s
//   ↓
// OTBR 进程退出
//   ↓
// Thread 失去 Border Router
//   ↓
// Leader 选举（原本 Border Router 是 Leader）
//   ↓
// 新 Leader 通知所有 Router
//   ↓
// Router 更新 Leader Data
//   ↓
// 子节点重新发现父节点
//   ↓
// ~30s 全部恢复
```

**根因**：

- 树莓派没 UPS，断电 30s
- 树莓派没 Watchdog
- Border Router 没冗余

### 修复

```c
// 1. 树莓派 UPS 备用电源
// 推荐：PiJuice / UPS HAT

// 2. Watchdog
// /etc/systemd/system/otbr-agent.service
[Service]
Type=simple
ExecStart=/usr/sbin/otbr-agent
Restart=always
RestartSec=10
WatchdogSec=300

// 3. Border Router 冗余
// 至少 2 个 Border Router
// 一个 Leader，一个 Backup
// Apple HomePod / Google Nest Hub 都可以做 BR

// 4. Thread 1.3 改进
// Thread 1.3+ 引入 "Keep-Alive" 模式
// BR 切换时保持网络稳定

// 5. 应用层容错
// 设备应用层缓存最近 60s 状态
// 网络恢复后不需要重新初始化
```

### 复盘

- **BR 切换不可避免**，但要尽量减少
- **UPS + Watchdog** 必备
- **多 BR 冗余** 是 Thread 1.3+ 推荐
- **应用层缓存** 降低 BR 切换影响

---

## 案例 7：Sleepy End Device 频繁唤醒，纽扣电池撑不过 1 周

### 现象

Thread 智能窗户传感器，CR2032 电池，宣称"撑 2 年"，实测 1 周。

### 抓 log

```text
功率分析仪（20s 窗口）：
  周期：~2 秒
  唤醒电流：~8 mA，~30ms
  睡眠电流：~3 µA
  平均：~800 µA
```

**问题**：唤醒频率比预期 6 倍。

### 定位

**Sleepy End Device 父节点丢失**：

```c
// SED 默认配置
#define SED_POLL_INTERVAL    3000    // 3s
// 父节点 Child Timeout 默认 240s（4 分钟）
// 子节点无活动 4 分钟 → 父节点认为子节点丢失

// 实际场景：
//   父节点 Router 掉线 30s
//   SED 醒来 poll 没响应 → 找新父节点
//   频繁重连 → 频繁唤醒
```

**根因**：

- 父节点 Router 偶发掉线（电源不稳）
- 父节点切换 → SED 重连 → 高唤醒

### 修复

```c
// 1. 加长 Poll Interval
#define SED_POLL_INTERVAL    30000   // 30s
// 默认 3s 太频繁，30s 合理

// 2. 配对 Keepalive
//   PollInterval < 父节点 Child Timeout
//   30s < 240s ✓

// 3. 加 RSSI 父节点选择
//   选 RSSI 强的父节点
//   避免频繁切换

// 4. 备用父节点
//   REED 升级 Router 作为备份

// 5. 实测功耗
//   唤醒 30ms / 周期 30s = 0.1% duty
//   平均 8 × 0.001 + 3e-3 = 11 µA
//   CR2032 (220 mAh) / 0.011 / 24 / 365 = 2.28 年 ✓
```

**SED 配置综合**：

```c
// SED 关键参数
#define SED_POLL_INTERVAL        30000   // 30s
#define SED_TIMEOUT              240     // 4 分钟（默认）
#define SED_KEEPALIVE            60000   // 60s

// 父节点 Router 配置
// Child Timeout 必须 > SED_TIMEOUT / 2
// 240s > 120s ✓

// Network Data
// 启用 "Parent Selection RSSI" 优先
```

### 复盘

- **SED 默认 3s Poll** 是开发值，量产必须改 30s+
- **Keepalive + Child Timeout 必须配对**
- **备用父节点** 避免单点故障
- **功率分析仪实测** 永远比 datasheet 准

---

## 案例 8：Joiner 入网后立即掉，Network Key 不匹配

### 现象

Thread 智能灯量产 500 台，60% 设备入网后 5 秒内掉线。

### 抓 log

```text
Joiner log:
  > joiner start J01NME
  Discovery Response
  DTLS 握手成功
  Network Key 接收
  > thread start
  Detached
  > state
  leader
  ...
  Detached  ← 反复
```

### 定位

**Network Key 派生错**：

```c
// 错：Joiner 接收 Network Key 后用 Master Key 派生
// 但 Master Key 派生 Network Key 算法有差异

// OpenThread 派生：
Network Key = HMAC-SHA256(Master Key, "ThreadMasterKey")

// 部分厂商派生（错误）：
Network Key = Master Key  // 直接用
```

**根因**：

- 厂商 SDK 实现不一致
- 部分老 SDK 不做派生
- 跨厂商 BR / Joiner 不兼容

### 修复

```c
// 1. 严格按 OpenThread 标准
Network Key = HMAC-SHA256(Master Key, "ThreadMasterKey")

// 2. 跨厂商验证
// 用官方 OpenThread CLI 测
> networkkey
00112233445566778899aabbccddeeff
> masterkey
00112233445566778899aabbccddeeff  // 错：应派生

// 3. 工厂烧录必须用 OpenThread CLI 派生
otMasterKeyToNetworkKey(master_key, network_key);

// 4. 多厂商设备统一测试
// OpenThread / nRF Connect / GSDK 设备互通
```

### 复盘

- **Network Key 必须派生自 Master Key**
- **多厂商互通测试** 必备
- **工厂烧录脚本必须用官方工具**
- **OpenThread CLI 是事实标准**

---

## 案例 9：IPv6 通信断，MLE 链路错

### 现象

Thread 智能灯部署后，ping 灯返回 "Request timeout for icmp_seq"。

### 抓 log

```text
> ipaddr
fdde:ad00:beef:0:fdad:beff:fe00:fc10  ← Leader ALOC
fdde:ad00:beef:0:fdad:beff:fe00:fc11  ← Commissioner ALOC
fdde:ad00:beef:0:ff:fe00:fc00  ← RLOC

> ping fdde:ad00:beef:0:fdad:beff:fe00:fc00
PING ... timeout
```

### 定位

**MLE 链路错**：

```c
// 检查 neighbor
> neighbor
[FF:FF:FF:FF:FF:00:00:00]  -30dBm  Router  ← 邻居
[8c:1f:b5:a1:b2:c3:d4:e5]  -45dBm  Router  ← 自身

// 检查路由
> router
0x0400  Leader  -25dBm  fdde:ad00:beef:0:ff:fe00:fc00
0x0800  Router  -30dBm  fdde:ad00:beef:0:ff:fe00:fc10

// 检查 Network Data
> networkdata
- Prefix fd00::/64
- Has Route fc00
```

**根因**：

- Network Data 缺失 prefix
- Router 表不完整
- MLE Counter 错乱

### 修复

```c
// 1. 重启 Thread
> thread stop
> thread start

// 2. 检查 Leader Data
> leaderdata
Partition ID: 0x12345678
Weighting: 64
Data Version: 1
Stable Data Version: 1
Leader Router ID: 0

// 3. 强制 Leader 选举
> leaderelection

// 4. 检查路由表
> route 1
fdde:ad00:beef:0:ff:fe00:fc10  via fdde:ad00:beef:0:ff:fe00:fc00  cost 1

// 5. 修复 Network Data
// Border Router 必须发 prefix
otBorderRouterAddOnMeshPrefix(
    prefix, prefix_len,
    flags, preference
);
```

### 复盘

- **MLE 链路错** 多由 Network Data 缺失 / 错乱导致
- **Border Router 必须发 prefix**
- **重启 Thread 经常解决**
- **route 1 验证路由** 必备

---

## 案例汇总

| # | 现象 | 根因 | 难度 |
| --- | --- | --- | --- |
| 1 | Joiner 找不到 Commissioner | PSKc 派生错 | 中 |
| 2 | Channel Mask 0 找不到网络 | 工厂烧录错 | 低 |
| 3 | 多 Thread 网络共信道 | 邻居 PAN 干扰 | 中 |
| 4 | REED 升级 Router 失败 | 子节点数限制 | 中 |
| 5 | RPL 路由震荡 | 边界 ETX 值 | 中 |
| 6 | BR 切换网络重组 | 单点 BR | 高 |
| 7 | SED 频繁唤醒 | 父节点丢失 / Poll 频繁 | 低 |
| 8 | Network Key 不匹配 | 派生算法错 | 中 |
| 9 | IPv6 通信断 | Network Data 缺失 | 中 |

## 关联文档

- `bus/thread.md` 主题入口
- `bus/thread-practical.md` 调试流程速查
- `bus/thread-deep-dive.md` 协议栈深挖
- `bus/thread-index.md` 主题地图 + 导航
- `bus/matter-*.md` Matter over Thread
- `bus/zigbee-*.md` 同源 PHY 对比
