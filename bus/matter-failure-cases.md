# Matter 产线实战案例库

## 目标

把产线常见的 Matter 配网失败、CASE 失败、跨生态不同步、多 Fabric 持久化、OTA 失败、认证测试 fail 等问题写成案例库。每个案例：

- 现象（现场）
- 抓包 / 抓 log（判断）
- 定位（根因）
- 修复（代码 / 配置）
- 复盘（如何预防）

案例来源：实战复盘 + 已知问题库。

## 案例 1：Commissioning 失败，Passcode 不匹配

### 现象

智能插座产线量产 1000 台，5% 设备用户首次配网失败。App 显示"配网失败，请重试"。

### 抓包

```text
nRF Connect 抓 BLE 广播：
  0xFEAF Service Data 正确
  Discriminator 0xF00 正确

手机 App 扫描后尝试配网：
  App 输入 Manual Pairing Code: 12345 67890 123
  实际 QR 码 Passcode: 20202021
  → 配网失败

App log：
  PASE: Received error 0x12 InvalidProvisioningData
```

### 定位

**Passcode 不匹配**：

- QR 码由工厂批量打印
- 固件 Passcode 默认 20202021
- App 配对码读错（生产环境误改为 12345 67890 123）

**根因**：

```c
// 错：硬编码不同 Passcode
static const uint32_t DEFAULT_PASSCODES[] = {
    12345678901,
    12345678902,
    ...
};
// 实际测试用 12345 67890 123 (11 位)
// 量产用 20202021 (8 位数字)

// 修复：统一 Passcode
#define DEFAULT_PASSCODE 20202021
```

### 修复

```c
// 1. 统一 Passcode
#define DEFAULT_PASSCODE 20202021
#define DEFAULT_DISCRIMINATOR 3840

// 2. 工厂烧录校验
void factory_test_passcode(void) {
    uint32_t read_passcode;
    if (KVS_Read("passcode", &read_passcode, sizeof(read_passcode))
        != KVS_OK || read_passcode != DEFAULT_PASSCODE) {
        // 烧录失败
        log_error("Passcode mismatch");
        factory_burn_passcode();
    }
}

// 3. App 引导用户用 QR 码
// QR 码内容:
// matter://<vid>/<pid>/<discriminator>/<passcode>
// 扫码自动填充

// 4. Production Mode 限定
// CommissionableWindow 模式 1 (KVS)
// Mode 2 (SetupPasscode) 留给工厂测试
```

### 复盘

- **Passcode / Discriminator 必须在生产前定版**
- **QR 码 vs Manual Pairing Code 必须匹配**
- **工厂测试 vs 量产模式分开**
- **CommissioningWindow 默认 15 分钟太长 / 太短都要调**
- **App 必须引导用户用 QR 码，输错率低**

---

## 案例 2：CASE 失败，NOC 写入错

### 现象

智能灯量产 500 台，配网 80% 在 PASE 通过，卡在 CASE 阶段。Log 报"NOC 写入失败"。

### 抓 log

```text
PASE: success
Attestation: success
NOC 生成: success
NOC 写入: failure
  → 设备返回 0x02 InvalidData
CASE: not started
```

### 定位

**NOC 写入错**：

```c
// 错：NOC 写入流程不完整
void write_noc_to_device(const NOC &noc) {
    if (noc.size > MAX_NOC_SIZE) {
        // 没 fall back
        return -1;  // 错
    }
    kvs_write("noc", noc.data, noc.size);  // 写错位置
}

// 修复
void write_noc_to_device(const NOC &noc) {
    // 1. 校验 NOC
    if (noc.size > MAX_NOC_SIZE || noc.size < MIN_NOC_SIZE) {
        return ERROR_INVALID_SIZE;
    }
    // 2. 写入 NOCSR（带 Fabric ID）
    NOCSR nocsr;
    nocsr.noc = noc;
    nocsr.fabric_id = current_fabric_id;
    // 3. 写持久化（带 CRC）
    kvs_write_with_crc("nocsr", &nocsr, sizeof(nocsr));
    // 4. 验证
    if (kvs_read_with_crc("nocsr", &verify, sizeof(verify)) != KVS_OK) {
        return ERROR_VERIFY_FAIL;
    }
    if (memcmp(&nocsr, &verify, sizeof(nocsr)) != 0) {
        return ERROR_VERIFY_FAIL;
    }
    return OK;
}
```

**根因**：

- NOC 长度超设备 KVS 限制
- NOC 写入路径选错
- 写后未做 CRC 校验
- KVS 磨损不均

### 修复

```c
// 1. 限制 NOC 长度（最大 4 KB）
#define MAX_NOC_SIZE 4096
#define MIN_NOC_SIZE 200  // 至少含 NOC + ICAC

// 2. KVS 分区独立 + 大小限制
KVS_Partition_t fabric_partition = {
    .name = "fabric",
    .start = 0x6F000,
    .size = 16 * 1024,  // 16 KB 存 5+ fabric
    .wear_leveling = true,
    .crc = true,
};

// 3. NOC 写前 commit
// 4. 失败回滚
// 5. 周期性 fabric 健康检查
void fabric_health_check(void) {
    for (int i = 0; i < MAX_FABRICS; i++) {
        NOC n;
        if (kvs_read_fabric_noc(i, &n) != KVS_OK) {
            log_error("Fabric %d NOC broken", i);
            // 修复或清
        }
    }
}
```

### 复盘

- **NOC 写入是 commissioning 关键路径**，必须有 CRC + 验证
- **KVS 分区独立** + wear leveling 必要
- **Fabric 数量限制**（典型 5+），超限处理策略
- **持久化失败 → 重试 N 次** → fabric 重建

---

## 案例 3：iOS 写 / Android 读，跨生态不同步

### 现象

智能灯加入 Apple Home 和 Google Home 两个 fabric。iOS 用户开灯，Android 用户看不到状态。Android 用户开灯，iOS 用户看不到。

### 抓包

```text
iOS HomeKit Hub → 灯:
  On/Off On (1)
  ReportData → 0x0006 OnOff=1

Android → 灯:
  ReadAttribute 0x0006 OnOff
  Response: 0x0006 OnOff=0  ← 错！
```

### 定位

**跨 Fabric 状态不同步**：

```text
iOS 用户开灯：
  1. iOS Hub → 灯: On/Off On
  2. 灯 Server: 状态变更 OnOff=1
  3. 灯 Server 推 Report 给所有订阅者
  4. iOS Hub 收到 → 显示开
  5. Android Hub 没订阅 → 不知道
  6. Android Hub 主动 Read → 拿到真实状态 = 0（灯离线 / 状态错）
```

**根因**：

- Android Hub 没有订阅该灯的 Attribute
- 灯只推 Report 给订阅者，没推给所有 fabric
- 多 Fabric 同步逻辑不完整

**正确行为**：

```text
iOS 用户开灯：
  1. iOS Hub → 灯: On/Off On
  2. 灯 Server: 状态变更 OnOff=1
  3. 灯 Server 推 Report 给所有订阅者
  4. iOS Hub 收到 → 显示开
  5. Android Hub 没订阅 → 状态还是旧
  6. Android Hub 下次 Read → 拿最新 = 1
```

### 修复

**修复 1：App 端订阅**

```swift
// iOS
chipController.readAttribute(.OnOff) { result in
    // 订阅
    chipController.subscribeAttribute(.OnOff, minInterval: 0, maxInterval: 60) { event in
        // 处理状态变化
    }
}
```

```kotlin
// Android
matterController.subscribe(Cluster.ON_OFF, Attribute.ON_OFF) {
    minInterval = 0
    maxInterval = 60
}
```

**修复 2：设备端多 Fabric Report**

```c
// Matter 协议：Server 推 Report 给所有订阅者
// 已经是标准行为，设备无需改
// 但要保证订阅者列表正确

void on_attribute_change(uint16_t endpoint, uint32_t cluster, uint16_t attribute) {
    // 找所有 fabric 的订阅者
    for (int fabric = 0; fabric < MAX_FABRICS; fabric++) {
        for (int sub = 0; sub < MAX_SUBSCRIBERS; sub++) {
            if (subscription[fabric][sub].active) {
                send_report(fabric, sub, endpoint, cluster, attribute);
            }
        }
    }
}
```

**修复 3：iOS / Android 都订阅**

```text
iOS / Android 配网成功后：
  1. 自动订阅所有受控设备 Attribute
  2. 周期性 refresh（每 60s）
  3. Read on app start
```

### 复盘

- **多 Fabric 状态同步是 App 责任**，不是设备责任
- **App 必须主动订阅**，不能只 Read
- **状态同步周期 60s** 是常用档位
- **App 启动时 Refresh** 必备

---

## 案例 4：多 Fabric KVS 分区错，fabric 互相覆盖

### 现象

设备加入 Apple Home 后，再加 Google Home，Apple Home fabric 丢失。反之亦然。

### 抓 log

```text
加 Apple Home:
  Fabric 0: Apple Home (写入 NOC)
  NOC OK, fabric OK

加 Google Home:
  Fabric 0: Google Home (覆盖！)
  NOC OK, 但 Apple Home NOC 丢失

iOS 端: 设备离线 / 配对丢失
```

### 定位

**KVS 分区错**：

```c
// 错：所有 fabric 共享同一存储 key
void write_fabric(int fabric_index, const Fabric &fabric) {
    kvs_write("fabric", &fabric, sizeof(fabric));
    // fabric 0 永远覆盖 fabric 1
}

// 修复：按 fabric_index 索引
void write_fabric(int fabric_index, const Fabric &fabric) {
    char key[16];
    snprintf(key, sizeof(key), "fabric_%d", fabric_index);
    kvs_write(key, &fabric, sizeof(fabric));
}
```

**根因**：

- KVS key 设计错
- 没考虑 Multi-Fabric 场景
- KVS 容量规划错（多 fabric 需 1-2 KB/fabric × 5 = 5-10 KB）

### 修复

```c
// 1. KVS 分区独立 + 大小足够
#define MAX_FABRICS 8
#define FABRIC_DATA_SIZE 1024  // 1 KB / fabric
#define FABRIC_PARTITION_SIZE (MAX_FABRICS * FABRIC_DATA_SIZE + 4)  // 8 KB + 4

// 2. KVS 索引存储
struct {
    int fabric_count;
    Fabric fabrics[MAX_FABRICS];
} fabric_table;

// 3. 写前查空
int find_empty_fabric_slot(void) {
    for (int i = 0; i < MAX_FABRICS; i++) {
        if (kvs_read_fabric(i).size == 0) {
            return i;
        }
    }
    return -1;  // fabric 已满
}

// 4. 写后校验
int write_fabric(int idx, const Fabric &fabric) {
    if (idx < 0 || idx >= MAX_FABRICS) {
        return ERROR_INVALID_INDEX;
    }
    if (kvs_write_fabric(idx, &fabric, sizeof(fabric)) != KVS_OK) {
        return ERROR_KVS;
    }
    Fabric verify;
    if (kvs_read_fabric(idx, &verify) != KVS_OK) {
        return ERROR_VERIFY;
    }
    if (memcmp(&verify, &fabric, sizeof(fabric)) != 0) {
        return ERROR_VERIFY_MISMATCH;
    }
    return OK;
}
```

### 复盘

- **Multi-Fabric 是 Matter 基础能力**，必须在产品设计阶段就支持
- **KVS key 索引设计**是基础
- **分区大小预估**：1-2 KB / fabric × 5+
- **持久化后必须做 verify**

---

## 案例 5：OTA 升级失败，镜像签名错

### 现象

Matter 智能灯，OTA 升级 1000 台，30% 失败。Log 报"InvalidImageSignature"。

### 抓 log

```text
OTA Requestor → OTA Provider:
  QueryImage → version 1.2.3
OTA Provider:
  Response: Image available, signature 0xABC...

OTA Requestor:
  Verify signature → InvalidImageSignature
  0x02 InvalidArgument
```

### 定位

**镜像签名错**：

```text
CSA 签名链：
  CSA Root → Vendor Intermediate → Image Signature

  设备验证：
  1. 解出 Image Public Key（厂商签发）
  2. 用厂商 Intermediate 验证 Image Public Key
  3. 用 Image Public Key 验证 Image Signature
```

**根因**：

- 厂商 Intermediate 没写进设备
- Image Signature 用错的私钥签
- Image 签名前 hash 错（SHA-256 没做）

### 修复

```c
// 1. 厂商 Intermediate 烧录
void factory_burn_intermediate(const uint8_t *intermediate, size_t size) {
    if (size != INTERMEDIATE_SIZE) {
        log_error("Intermediate size mismatch");
        return;
    }
    kvs_write("vendor_intermediate", intermediate, size);
}

// 2. OTA 镜像生成流程
// step 1: 编译固件
// step 2: 计算 SHA-256
// step 3: 用厂商私钥签（chip-tool otasign 或厂商自研）
// step 4: 输出 .ota 镜像

# chip-tool 签名
./chip-tool ota sign \
    --vendor-id 0xFFF1 \
    --product-id 0x8000 \
    --software-version 0x00010002 \
    --firmware-info "v1.2.3" \
    --signing-key vendor_priv.key \
    --intermediate-key vendor_inter.key \
    --input firmware.bin \
    --output firmware.ota

# step 5: OTA Provider 加载
./chip-tool ota load-firmware firmware.ota

// 3. 设备端验证
bool verify_image(const uint8_t *image, size_t size) {
    // 1. 解析镜像头
    OTAImageHeader hdr;
    parse_header(image, &hdr);
    // 2. SHA-256
    uint8_t hash[32];
    sha256(image + hdr.payload_offset, hdr.payload_size, hash);
    // 3. 用厂商公钥验证签名
    if (ecdsa_verify(hash, hdr.signature, vendor_public_key) != 0) {
        return false;
    }
    // 4. 防回滚
    if (hdr.software_version <= current_version) {
        return false;
    }
    return true;
}
```

### 复盘

- **OTA 签名链不能错** —— 厂商 Intermediate 必须烧录
- **Image Signature 用对的私钥签** —— 私钥管理严格
- **设备 SHA-256 算法** —— 用硬件加速或软件实现，性能不是瓶颈
- **防回滚检查** —— 软件版本号比较

---

## 案例 6：Wi-Fi 切换 fabric 路由失效

### 现象

智能灯加入 Apple Home 后，用户改 Wi-Fi 密码或切换 Wi-Fi，灯 fabric 掉线。

### 抓 log

```text
Wi-Fi 切换前：
  Wi-Fi: SSID HomeWiFi
  IP: 192.168.1.100
  Fabric 路由表: 192.168.1.100 → IPv6

Wi-Fi 切换后：
  Wi-Fi: SSID NewWiFi
  IP: 192.168.1.200
  Fabric 路由表: 192.168.1.100 → IPv6  ← 错！
  → iOS Hub 找不到灯
```

### 定位

**fabric 路由表未更新**：

```c
// 错：fabric 路由表硬编码 IP
typedef struct {
    uint8_t ipv6[16];
    uint16_t port;
} FabricRoute;

FabricRoute fabric_routes[MAX_FABRICS];

// 修复：fabric 路由通过 mDNS / DNS-SD 重新发现
```

**根因**：

- fabric 路由表绑死 IP
- Wi-Fi 切换后 IP 变化
- mDNS 没触发更新

### 修复

```c
// 1. mDNS 持续工作
void mdns_advertise(void) {
    // Matter 服务发现
    mdns_add_service("_matter._tcp", "_local", 5540);
    // 持续广播
}

// 2. mDNS 监听
void mdns_resolve(const char *name) {
    // 解析 fabric 内的其他节点
}

// 3. Wi-Fi 切换时触发 mDNS 重新广播
void on_wifi_event(WiFiEvent event) {
    if (event == WIFI_CONNECTED) {
        // 重启 mDNS
        mdns_restart();
        // 通知所有 fabric
        notify_fabric_routes_changed();
    }
}

// 4. Operational Discovery 周期性重试
void operational_discovery_periodic(void) {
    for (int i = 0; i < MAX_FABRICS; i++) {
        // 重发 NOC 广播
        re_advertise_fabric(i);
    }
}
```

### 复盘

- **fabric 路由不能绑死 IP**，必须 mDNS 发现
- **Wi-Fi 切换**触发 mDNS 重新广播
- **mDNS 必须常驻**，不能关
- **Border Router 切换**同样问题

---

## 案例 7：CSA 认证测试 fail，Cluster 顺序错

### 现象

智能灯提交 CSA 认证，CSA Test Harness 报"Cluster 顺序不符合 Matter Device Library"。

### 抓 log

```text
Test Harness:
  Test: Dimmable Light Cluster Order Verification
  Expected order: Descriptor → Identify → On/Off → Level
  Actual order: On/Off → Descriptor → Identify → Level
  Result: FAIL
```

### 定位

**Cluster 顺序错**：

```c
// 错：Cluster 顺序随意
static const Cluster clusters[] = {
    OnOff,       // Cluster 0
    Descriptor,  // Cluster 1
    Identify,    // Cluster 2
    Level,       // Cluster 3
};

// 修复：按 Matter Device Library 顺序
static const Cluster clusters[] = {
    Descriptor,  // Cluster 0 - 必须是第一个
    Identify,    // Cluster 1
    OnOff,       // Cluster 2
    Level,       // Cluster 3
};
```

**Matter Device Library Cluster 顺序规则**：

```text
Dimmable Light (0x0101):
  Cluster 顺序（固定）：
    0. Descriptor (0x001D)
    1. Identify (0x0003)
    2. On/Off (0x0006)
    3. Level (0x0008)
  
  Cluster 顺序错 → 认证测试 fail
```

### 修复

```c
// 严格按 Matter Device Library 顺序
typedef struct {
    uint16_t cluster_id;
    void *instance;
} ClusterEntry;

static ClusterEntry endpoint_1_clusters[] = {
    { 0x001D, &descriptor_server },
    { 0x0003, &identify_server },
    { 0x0006, &onoff_server },
    { 0x0008, &level_server },
};

// 检查工具
void verify_cluster_order(int endpoint_id, int device_type_id) {
    ClusterEntry *expected = get_expected_clusters(device_type_id);
    ClusterEntry *actual = endpoint_clusters[endpoint_id];
    
    for (int i = 0; i < expected->count; i++) {
        if (actual[i].cluster_id != expected[i].cluster_id) {
            log_error("Cluster %d mismatch: expected 0x%04X, actual 0x%04X",
                      i, expected[i].cluster_id, actual[i].cluster_id);
        }
    }
}
```

### 复盘

- **Cluster 顺序必须严格按 Matter Device Library** —— 认证测试必查
- **Descriptor 永远 Cluster 0**
- **认证前用 chip-all-clusters 跑测试** —— 提前发现
- **PICS 文档** —— 写明所有 Cluster + 顺序

---

## 案例 8：跨生态 Cluster Attribute 不通用

### 现象

智能门锁在 Apple HomeKit 中能用 PIN 码开锁，在 Google Home 中 PIN 码开锁失败。

### 抓包

```text
Apple Home → 锁:
  DoorLock Cluster: LockDoor (PinCode=1234)
  Response: SUCCESS

Google Home → 锁:
  DoorLock Cluster: LockDoor (PinCode=1234)
  Response: 0x0015 InvalidStateChange
```

### 定位

**跨生态 Attribute 权限错**：

```c
// 错：PIN 验证逻辑只走 iOS
bool verify_pin(const char *pin) {
    if (current_fabric == APPLE_HOME) {
        return check_pin(pin);  // iOS 走这个
    } else {
        return false;  // 其他走这个
    }
}

// 修复：所有 fabric 统一验证
bool verify_pin(const char *pin) {
    // 1. 检查 PIN 长度
    if (strlen(pin) < 4 || strlen(pin) > 8) {
        return false;
    }
    // 2. 检查 PIN 在合法列表
    for (int i = 0; i < pin_count; i++) {
        if (strcmp(pin_table[i], pin) == 0) {
            // 3. 检查权限
            if (has_pin_access(pin, current_fabric)) {
                return true;
            }
        }
    }
    return false;
}
```

**根因**：

- 跨 fabric 权限检查不一致
- ACL 配置只针对一个 fabric
- 厂商实现只测了 Apple 生态

### 修复

```c
// 1. ACL 统一管理
void init_acl(void) {
    for (int fabric = 0; fabric < MAX_FABRICS; fabric++) {
        acl[fabric].privilege = OPERATE;
    }
}

// 2. PIN 验证跨 fabric 一致
bool verify_pin_across_fabric(const char *pin, int fabric_index) {
    return (check_pin_length(pin) && 
            check_pin_in_table(pin) && 
            has_fabric_access(fabric_index));
}

// 3. 跨生态测试（必须）
void cross_ecosystem_test(void) {
    // Apple Home
    matter_test_pairing_apple();
    matter_test_control_apple();
    
    // Google Home
    matter_test_pairing_google();
    matter_test_control_google();
    
    // Amazon Alexa
    matter_test_pairing_alexa();
    matter_test_control_alexa();
    
    // Samsung SmartThings
    matter_test_pairing_samsung();
    matter_test_control_samsung();
}
```

### 复盘

- **跨生态测试是 Matter 认证必做** —— 至少 5 个生态
- **ACL 必须跨 fabric 一致** —— 不允许特殊处理
- **App + Device 双端验证** —— 任何一端错都失败

---

## 案例汇总

| # | 现象 | 根因 | 难度 |
| --- | --- | --- | --- |
| 1 | Commissioning 失败 | Passcode 不匹配 | 低 |
| 2 | CASE 失败 | NOC 写入错 | 中 |
| 3 | 跨生态不同步 | 订阅没开 | 中 |
| 4 | Multi-Fabric 丢失 | KVS 分区错 | 中 |
| 5 | OTA 失败 | 镜像签名错 | 中 |
| 6 | Wi-Fi 切换掉线 | fabric 路由绑死 | 中 |
| 7 | 认证测试 fail | Cluster 顺序错 | 低 |
| 8 | 跨生态 PIN 失败 | 跨 fabric 权限不一致 | 中 |

## 关联文档

- `bus/matter.md` 主题入口
- `bus/matter-practical.md` 调试流程速查
- `bus/matter-deep-dive.md` 协议栈深挖
- `bus/matter-index.md` 主题地图 + 导航
- `bus/thread-*.md` Matter over Thread
- `bus/ble-deep-dive.md` BLE 配网通道
- `bus/zigbee-*.md` Cluster 沿用参考
