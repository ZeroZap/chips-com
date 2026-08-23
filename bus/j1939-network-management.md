# J1939 网络管理 (NM) 详解

## 目标

J1939 网络管理是商用车 ECU 的核心, 涉及:
- 64 bit NAME 字段
- 地址声明协议 (Address Claimed, PGN 60928)
- 命令地址 (Commanded Address, PGN 65240)
- 心跳 (Heartbeat, PGN 65260)
- 多 ECU 协同

本文讲清楚原理、协议和实战代码。

## NAME 字段 (64 bit)

### NAME 完整结构

```text
┌─────────────────────┬──────────────────┬────────┬─────────┬─────────────┬──────┬─────┐
│  身份号 (21 bit)     │ 厂商代码 (11 bit)│ECU 实例│功能实例 │  功能 (18)   │保留  │地址 │
│  Identity Number     │ Manufacturer Code │(6 bit) │(5 bit)  │ Function    │(3 b) │(8 b)│
└─────────────────────┴──────────────────┴────────┴─────────┴─────────────┴──────┴─────┘
   bit 63-43              bit 42-32         bit 31-26  bit 25-21  bit 20-3    bit 2-0  bit 7-0 (LSB)
```

**关键**:
- **身份号 (21 bit)**: 唯一标识, 多数用芯片 UID
- **厂商代码 (11 bit)**: SAE 分配, 不可自定义
- **ECU 实例 (6 bit, 但只有 0-3 有效, 4-7 保留)**: 同一 NAME 中区分
- **功能实例 (5 bit)**: 同一 NAME 同一功能中区分
- **功能 (18 bit)**: 设备功能编号 (e.g. 发动机=0, 变速箱=1, ABS=2)
- **保留 (3 bit)**: 必须 0
- **地址 (8 bit)**: 0-253 有效, 254 (NACK) 和 255 (全局) 保留

### NAME 编码

```c
typedef struct {
    uint32_t identity_number;   /* 21 bit */
    uint16_t manufacturer_code;  /* 11 bit */
    uint8_t  ecu_instance;       /* 6 bit (用 0-3) */
    uint8_t  function_instance;  /* 5 bit */
    uint32_t function;           /* 18 bit */
    uint8_t  reserved;           /* 3 bit, must 0 */
    uint8_t  address;            /* 8 bit (0-253) */
} j1939_name_t;

uint64_t encode_name(j1939_name_t *name) {
    uint64_t nm = 0;
    nm |= ((uint64_t)(name->identity_number & 0x1FFFFF) << 43);
    nm |= ((uint64_t)(name->manufacturer_code & 0x7FF) << 35);
    nm |= ((uint64_t)(name->ecu_instance & 0x3F) << 29);
    nm |= ((uint64_t)(name->function_instance & 0x1F) << 24);
    nm |= ((uint64_t)(name->function & 0x3FFFF) << 6);
    nm |= ((uint64_t)(name->reserved & 0x7) << 3);
    nm |= ((uint64_t)(name->address & 0xFF));
    return nm;
}

void decode_name(uint64_t nm, j1939_name_t *name) {
    name->identity_number    = (nm >> 43) & 0x1FFFFF;
    name->manufacturer_code  = (nm >> 35) & 0x7FF;
    name->ecu_instance       = (nm >> 29) & 0x3F;
    name->function_instance  = (nm >> 24) & 0x1F;
    name->function           = (nm >> 6)  & 0x3FFFF;
    name->reserved           = (nm >> 3)  & 0x7;
    name->address            = nm & 0xFF;
}
```

### NAME 优先级

```text
NAME 数值越小, 优先级越高

按位比较, 从 MSB 开始:
  身份号小的优先 (bit 63-43)
  相同身份号 -> 厂商代码小的优先
  相同厂商代码 -> ECU 实例小的优先
  ...
  
仲裁失败 (NAME 大的 ECU 输了) -> 不能用该地址, 必须换地址或 NAME
```

## 地址声明 (Address Claimed)

### 协议流程

```text
ECU 启动:
  1. 发 Address Claimed (PGN 60928), 用自己的 NAME
  2. 等 250ms
  3. 期间收其他 ECU 的 Address Claimed:
     - 如果其他 NAME 小 (优先级高) -> 我输了, 不能用该地址
     - 如果我 NAME 小 -> 别人输了
     - 如果 NAME 相同 -> 看 ECU 实例, 实例小的赢
     - 如果完全相同 -> 完全冲突, 不能用

如果输了:
  - 必须换地址 (从 0-253 找一个空闲的)
  - 或换 NAME (身份号 / 厂商代码)
  - 重新 Address Claimed

如果赢了:
  - 用该地址, 继续发其他报文
```

### PGN 60928 格式 (Address Claimed)

```text
CAN ID: 0x18EEFF + SA (Source Address)
  PGN = 0x00EEFF (60928)
  PF = 238 (0xEE)
  PS = 0xFF (255, 全局, 因为是 Address Claimed)
  SA = 0-253 (自己的地址)
  
数据 (8 字节): NAME 字段 (LSB 在前)
```

### 完整流程图

```text
ECU 上电
  |
  +-- 发 Address Claimed (NAME A, 地址 0x28)
  |
  +-- 等 250ms
  |
  +-- 期间收其他 ECU 的 Address Claimed
        |
        +-- 别人 NAME 小, 我输了
        |     -> 换地址 (找空闲)
        |     -> 或换 NAME
        |     -> 重发 Address Claimed
        |
        +-- 别人 NAME 大, 我赢了
        |     -> 继续, 用 0x28
        |
        +-- 别人 NAME 相同, ECU 实例小
        |     -> 我输了
        |     -> 换 ECU 实例或地址
        |
        +-- 完全相同
        |     -> 严重冲突, 必须改 NAME (身份号)
        |
        +-- 没有冲突
              -> 用 0x28
```

### 实战代码

```c
/* Address Claimed 处理 */
typedef struct {
    uint8_t  my_address;        /* 自己期望的地址 */
    uint64_t my_name;            /* 自己的 NAME */
    uint64_t peer_names[256];   /* 已知其他 ECU 的 NAME (按地址索引) */
    bool     address_conflict;
} j1939_nm_t;

void j1939_nm_init(j1939_nm_t *nm, uint8_t address, uint64_t name) {
    nm->my_address = address;
    nm->my_name = name;
    nm->address_conflict = false;
    memset(nm->peer_names, 0, sizeof(nm->peer_names));
}

/* 发 Address Claimed */
void j1939_nm_send_claim(j1939_nm_t *nm) {
    uint8_t data[8];
    for (int i = 0; i < 8; i++) {
        data[i] = (nm->my_name >> (i * 8)) & 0xFF;  /* LSB 在前 */
    }
    can_send_pgn_with_sa(0x00EEFF, nm->my_address, data, 8);
}

/* 收 Address Claimed 处理 */
void j1939_nm_on_claim(j1939_nm_t *nm, uint8_t src_addr, uint8_t *data) {
    uint64_t peer_name = 0;
    for (int i = 0; i < 8; i++) {
        peer_name |= ((uint64_t)data[i] << (i * 8));
    }
    
    nm->peer_names[src_addr] = peer_name;
    
    /* 检查是否和我冲突 */
    if (src_addr == nm->my_address) {
        if (peer_name == nm->my_name) {
            /* 完全相同, 严重冲突 */
            log_error("J1939 NAME 完全冲突");
            nm->address_conflict = true;
            /* 策略: 修改身份号 (UID 最后几位) */
        } else if (peer_name < nm->my_name) {
            /* 别人 NAME 小, 我输了 */
            log_warn("J1939 地址冲突: 别人 NAME=0x%llx 比我小", peer_name);
            nm->address_conflict = true;
            /* 策略: 换地址 (找下一个空闲的) */
        } else {
            /* 我 NAME 小, 别人输 */
            log_info("J1939 我赢: NAME=0x%llx", nm->my_name);
        }
    }
}

/* 找空闲地址 */
uint8_t j1939_nm_find_free_address(j1939_nm_t *nm) {
    /* 从 my_address + 1 开始找, 跳过 254 (NACK) 和 255 (全局) */
    for (int addr = 0; addr < 254; addr++) {
        if (addr == 254 || addr == 255) continue;  /* 保留 */
        if (nm->peer_names[addr] == 0) {
            return addr;
        }
    }
    return 0xFE;  /* NACK, 找不到 */
}

/* 周期发 Address Claimed (250ms) */
void j1939_nm_periodic(j1939_nm_t *nm) {
    static uint32_t last_claim = 0;
    if (HAL_GetTick() - last_claim > 250) {
        j1939_nm_send_claim(nm);
        last_claim = HAL_GetTick();
    }
    
    /* 检查冲突后处理 */
    if (nm->address_conflict) {
        uint8_t new_addr = j1939_nm_find_free_address(nm);
        if (new_addr != 0xFE) {
            log_info("J1939 换地址 0x%02x -> 0x%02x", nm->my_address, new_addr);
            nm->my_address = new_addr;
            nm->address_conflict = false;
            j1939_nm_send_claim(nm);
        }
    }
}
```

## 命令地址 (Commanded Address, PGN 65240)

### 协议

```text
外部工具 (诊断 / 配置) 发 Commanded Address:
  - 指定目标地址
  - ECU 收到后必须:
    1. 不能继续使用原地址
    2. 用新地址发 Address Claimed
    3. 或不发 Address Claimed, 进入不可用状态

典型场景:
  - 产线烧录, 临时改地址
  - 故障 ECU 强制更换地址
```

### PGN 65240 格式

```text
CAN ID: 0x18ED + DA + SA (目标地址)
  PGN = 0x00FED00 (65240)
  PF = 237 (0xED)
  PS = DA (Destination Address, 目标)
  SA = 0xFE (NACK / 诊断工具)

数据 (8 字节):
  字节 0: 新地址
  字节 1-7: NAME 字段
```

### 处理 Commanded Address

```c
void j1939_nm_on_commanded_addr(j1939_nm_t *nm, uint8_t *data) {
    uint8_t new_addr = data[0];
    uint64_t new_name = 0;
    for (int i = 0; i < 7; i++) {
        new_name |= ((uint64_t)data[i+1] << (i * 8));
    }
    
    if (new_name == nm->my_name) {
        log_info("J1939 收到命令地址 0x%02x -> 0x%02x", nm->my_address, new_addr);
        nm->my_address = new_addr;
        j1939_nm_send_claim(nm);
    }
}
```

## 心跳 (Heartbeat, PGN 65260)

### 协议

```text
PGN 65260 (0x00FECC):
  - 周期 50ms-1s
  - 数据 (8 字节): 状态信息
  - 接收方 3-5 倍心跳周期没收到, 判定 ECU 离线

格式:
  字节 0-3: 信号 (按 OEM 定义)
  字节 4-7: 信号
```

### 实战

```c
void j1939_heartbeat_send(j1939_nm_t *nm) {
    static uint32_t last_beat = 0;
    if (HAL_GetTick() - last_beat > 1000) {  /* 1s 心跳 */
        uint8_t data[8] = { 0 };
        /* 状态信息按 OEM 填 */
        data[0] = 0x01;  /* e.g. 运行中 */
        data[1] = 0xFF;
        can_send_pgn_with_sa(0x00FECC, nm->my_address, data, 8);
        last_beat = HAL_GetTick();
    }
}
```

## 多 ECU 协同

### 地址分配表 (OEM 文档)

```c
/* 商用车典型地址分配 */
const uint8_t j1939_address_map[256] = {
    /* Engine */
    [0x00] = ECU_ENGINE_1,
    [0x01] = ECU_ENGINE_2,
    /* Transmission */
    [0x03] = ECU_TRANSMISSION_1,
    /* Brakes */
    [0x0B] = ECU_ABS,
    /* Body */
    [0x10] = ECU_CAB,
    [0x11] = ECU_BODY,
    /* Telematics */
    [0x20] = ECU_TCU,
    /* Diagnostic */
    [0xF9] = ECU_DIAG_TOOL,
    /* NACK / Global */
    [0xFE] = ADDR_NACK,
    [0xFF] = ADDR_GLOBAL,
    /* 其他未分配地址: 0x00-0xF7 任意 */
};
```

### 启动顺序

```text
典型商用车启动顺序:
1. 钥匙打开, 主 ECU (e.g. 发动机) 上电, 先 Address Claimed
2. 其他 ECU 依次上电, 每个都 Address Claimed
3. 全部 Address Claimed 完成后, 才开始正常业务报文

如果顺序错 (e.g. 同时上电):
  - 多个 ECU 可能同时 Address Claimed
  - NAME 仲裁自然解决
  - 但 OEM 应该按启动顺序确保唯一
```

## NAME 设计最佳实践

### 身份号 (21 bit) 来源

```text
推荐用 MCU 唯一 ID (UID):
  - STM32: 96 bit UID, 取低 21 bit
  - NXP: 128 bit UID
  - ESP32: 64 bit EFUSE MAC
  - 国产 MCU: 大多有 96 bit UID

生产前烧录:
  - 工厂烧录器读 UID, 写入 ECU 固件
  - 或用 OTP / EEPROM 存身份号
  - 保证每台 ECU 身份号不同
```

### 厂商代码 (11 bit) 申请

```text
SAE 厂商代码 (MFC) 必须申请:
  https://www.sae.org/standards/content/j1924/
  
  申请后获得 11 bit 数字, 例如 0x4F1 (Altera 厂商代码)
  
  不可自定义, 否则冲突
```

### 避免常见错误

```text
错误 1: 厂商代码 0
  - 不合法, 协议栈拒绝

错误 2: 保留位非 0
  - 必须 0

错误 3: 身份号全 0 或全 1
  - 协议栈拒绝

错误 4: 同一型号 ECU 身份号相同
  - 地址冲突
  - 产线必须每台烧录不同身份号

错误 5: 身份号用固定值 (e.g. 1)
  - 同型号 ECU 全部冲突
```

## 心跳超时判定

### 监控 ECU 离线

```c
typedef struct {
    uint8_t  addr;
    uint32_t last_heartbeat;
    bool     online;
} j1939_peer_t;

j1939_peer_t peers[256];

void j1939_check_peers() {
    uint32_t now = HAL_GetTick();
    for (int i = 0; i < 256; i++) {
        if (peers[i].addr == 0xFF) continue;
        if (now - peers[i].last_heartbeat > 5000) {  /* 5s 超时 */
            if (peers[i].online) {
                log_warn("J1939 ECU 0x%02x 离线", peers[i].addr);
                peers[i].online = false;
            }
        }
    }
}
```

### 心跳超时时间选择

```text
心跳 1Hz:  超时 3-5s (考虑网络延迟)
心跳 100ms: 超时 1-2s
心跳 50ms: 超时 500ms-1s

经验: 超时时间 = 5-10 倍心跳周期
```

## Linux 内核 J1939 支持

### 内核模块

```bash
# 加载 J1939 模块
modprobe can
modprobe can_j1939

# 配置 J1939
ip link set can0 type can bitrate 250000
ip link set can0 up

# 查看 J1939 设备
ip -details link show can0

# 工具
j1939acd  # 监听 J1939 流量
j1939cat  # 解析 J1939 帧
```

### 用户态 J1939

```c
/* Linux J1939 socket 编程 */

/* 1. 创建 socket */
int s = socket(PF_CAN, SOCK_DGRAM, CAN_J1939);

/* 2. 绑定自己的地址 */
struct sockaddr_can addr = {
    .can_family = AF_CAN,
    .can_ifindex = ifr.ifr_ifindex,
    .can_addr.j1939 = {
        .name = 0x1234567890ABCDEFULL,
        .pgn = J1939_NO_PGN_FILTER,
        .addr = MY_ADDR,
    },
};
bind(s, (struct sockaddr *)&addr, sizeof(addr));

/* 3. 发送 PGN (地址声明) */
struct j1939_sk_buff jsk;
jsk.addr.dst.name = J1939_NO_NAME;
jsk.addr.dst.addr = J1939_NO_ADDR;  /* 全局 */
jsk.addr.pgn = PGN_ADDRESS_CLAIMED;
jsk.buf = my_name;  /* NAME 8 字节 */
sendmsg(s, &msg, ...);

/* 4. 接收 (异步) */
recvmsg(s, &msg, ...);
```

## 产线 J1939 NM 验收清单

```text
□ NAME 字段严格按 SAE J1939-81
□ 身份号 21 bit 来自芯片 UID, 唯一
□ 厂商代码 11 bit 来自 SAE 申请
□ ECU 实例 0-3, 保留位 0
□ 地址 0-253, 254/255 不用
□ Address Claimed 250ms 周期发
□ 冲突处理: 换地址, 不无限重试
□ Commanded Address 接收并处理
□ 心跳 50ms-1s, 监控其他 ECU
□ 地址分配表 OEM 文档化
□ J1939-84 一致性测试 100% 通过
□ 多 ECU 启动顺序验证
```

## 关联文档

- `j1939-deep-dive.md` 原理
- `j1939-practical.md` 速查
- `j1939-failure-cases.md` 产线案例
- `j1939-transport-protocol.md` TP 多帧
- `j1939-index.md` 导航
- `can-deep-dive.md` CAN 基础
- `can-multimaster-and-bus-off.md` CAN 多 master
- `bus/uds-*.md` UDS (诊断)
- `bus/iso-tp-*.md` ISO-TP
