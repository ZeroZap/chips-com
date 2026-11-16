# CANopen 产线死机案例库

## 目标

把产线常见的 CANopen 通信失败、SDO 读写异常、PDO 不发、NMT 状态机卡住写成案例库。每个案例：

- 现象（现场）
- 抓包分析（判断）
- 定位（根因）
- 修复（代码 / 配置）
- 复盘（如何预防）

CANopen 排障第一原则：**先确认节点状态，再确认数据通路**。Node ID 唯一、NMT 进入 Operational、PDO 映射一致，这三条任何一条不满足，现象都会表现为"数据不来"。

## 案例 1: 两个设备 Node ID 相同，互相顶掉

### 现象

两个相同型号的伺服驱动器接上总线后，只有第一个能正常工作。第二个上电后第一个的通信就乱了。拔掉第二个，第一个恢复正常。

### 抓包分析

```text
Node A (Node ID=1) 上电
Node A -> Bus  0x701  00                    (Boot-up)
Node A -> Bus  0x180+1 0x181  ...           (TPDO1)

Node B (Node ID=1) 上电
Node B -> Bus  0x701  00                    (Boot-up, 同 ID!)
Node B -> Bus  0x181  ...                   (和 Node A 撞 ID)
```

### 定位

CANopen 的 Node ID 是**节点在网络中的唯一标识**，编码在所有 COB-ID 里。Node ID 重复会导致：

- 同一个 COB-ID 上出现两个不同节点的数据帧 → 主控无法区分来源。
- 两个节点同时响应同一个 SDO 请求 → SDO 应答冲突。
- NMT 指令同时作用于两个节点。

**为什么常见**：CANopen 的 Node ID 通常由拨码开关、EEPROM 或设备序号设置。批量生产时如果默认值都是 1 而现场又没改，就会撞。

### 修复

**A. 生产流程强制分配唯一 Node ID**

```c
/* 方案 1: 从芯片唯一 ID 派生 (推荐, 天然唯一) */
uint8_t derive_node_id(void) {
    uint32_t uid = HAL_GetUIDw0();          /* 芯片 96bit UID 的低 32 bit */
    return (uint8_t)((uid >> 16) & 0x7F) + 1;   /* 1..127, 避开 0 */
}

/* 方案 2: 拨码开关 + 冲突检测 */
uint8_t node_id = read_dip_switch();
if (node_id == 0 || node_id > 127) {
    node_id = 1;   /* 非法值兜底 */
}
```

**B. 启动时做地址冲突检测**

```c
/* 上电后监听一段时间, 发现同 ID 的 Boot-up 就报警 */
void check_node_id_conflict(void) {
    uint8_t seen[128] = {0};
    uint32_t start = tick_get_ms();

    while (tick_elapsed_ms(start) < 1000) {
        can_frame_t f;
        if (can_receive(&f) && (f.id & 0x7F8) == 0x700) {
            uint8_t id = f.id & 0x7F;
            if (id == my_node_id) {
                /* 收到自己的 Boot-up 回声 = 有冲突 */
                node_id_conflict_flag = 1;
                emcy_send(EMCY_CAN_ERROR, 0x00, 0x00);   /* 上报 EMCY */
                return;
            }
            seen[id] = 1;
        }
    }
}
```

**C. 主控侧也要防呆**

主控在下发 NMT Start 前，先确认目标 Node ID 的 Heartbeat 状态是它期望的那台设备。

### 复盘

- **Node ID 唯一性是产线第一道检查**，配置表和实物必须一一对应。
- 优先用芯片 UID 派生，避免人工设置出错。
- 启动冲突检测 + EMCY 上报，让问题在设备级别可见，而不是等主控侧排查。

## 案例 2: SDO 读设备类型返回 Abort 0x06020000

### 现象

用 CANopen 主站工具读取设备信息（`1000h` 设备类型），返回 SDO Abort。

### 抓包分析

```text
Master -> Node  0x601  02 40 00 10 00 00 00 00   (SDO Upload Request, Index 0x1000)
Node  -> Master 0x581  05 80 00 00 06 02        (SDO Abort)
```

Abort code `0x06020000` = **Object does not exist**。

### 定位

几种可能：

**A. 对象确实不存在**

设备不是标准 CANopen 设备，或只实现了部分对象字典。

**B. 字节序搞反（最常见）**

SDO 的 Index 和 Sub-index 在 CAN 帧里是**小端**：

```text
Index    0x1000 -> 字节序 00 10
Sub-index 0x00  -> 字节序 00
```

正确的请求帧：

```text
40 00 10 00 00 00 00 00
  │  └──┬─┘ └──┬──┘
  │     │      └── Sub-index (小端)
  │     └───────── Index (小端)
  └─────────────── command specifier
```

发成 `40 10 00 00 ...`（大端）会读到 Index 0x0010，那是不同的对象。

**C. 用了 expedited 格式但设备只支持 segmented**

有些设备（尤其带 Bootloader 或大对象字典的）只支持分块传输。

### 修复

```c
/* 主机侧: 始终用小端编码 */
uint8_t build_sdo_upload_req(uint16_t index, uint8_t subindex, uint8_t *buf) {
    buf[0] = 0x40;                 /* command specifier */
    buf[1] = index & 0xFF;         /* Index 小端: 低字节先 */
    buf[2] = index >> 8;
    buf[3] = subindex;
    buf[4] = buf[5] = buf[6] = buf[7] = 0x00;
    return 8;
}

/* 从设备侧: 处理 Upload Request */
int sdo_handle_upload_req(uint16_t index, uint8_t subindex, uint8_t *resp) {
    od_entry_t *e = od_find(index, subindex);
    if (!e) {
        resp[0] = 0x80;                       /* abort */
        resp[1] = 0x00;
        resp[2] = 0x00;
        resp[3] = 0x06;                       /* 0x06020000 */
        resp[4] = 0x02;
        return 4;
    }
    ...
}
```

**关于小端**：CANopen 规范里对象字典的 Index/Sub-index 用小端，但**对象的数据内容字节序由设备定义**（CiA 402 的 32 bit 参数通常也是小端，但厂商设备可能有差异，必须查对象字典文档）。

### 复盘

- **SDO Index/Sub-index 是小端** —— 这是 CANopen 新手最高频的错误。
- 工具应有"对象不存在"和"字节序错误"的区分提示。
- 从设备侧要能返回准确的 Abort code，别一律返回通用 abort。

## 案例 3: SDO 写参数后设备不生效

### 现象

通过 SDO 写入参数（如 `6060h` 操作模式、`6071h` 目标转矩），返回正响应，但电机行为没变化。

### 抓包分析

```text
Master -> Node  0x601  06 23 60 60 01 00 00 00   (SDO Download, expedited 4 bytes)
Node  -> Master 0x581  02 60 60 00                (SDO Download Response)
```

协议层面完全正常 —— `0x60` 就是标准的下载确认。

### 定位

**SDO 写成功 ≠ 参数生效**。CANopen 有两类对象：

```text
可存储对象 (persistent):
  - 写入后掉电保持, 下次上电生效

易失对象 (ram):
  - 写入后立即在 RAM 生效, 掉电丢失
```

常见根因：

**A. 写的是易失对象，但驱动只在启动时读一次**

```c
/* 错误: 只在初始化时读 */
void drive_init(void) {
    op_mode = od_get_u8(0x6060, 0);     /* 启动时读一次 */
}

/* 之后主控改了 6060, 驱动完全不知道 */
```

**B. CiA 402 状态机不允许立即切换**

在 `Operation Enabled` 状态下写 `6060h` 操作模式，CiA 402 规范要求设备先回到 `Ready to Switch On`，模式切换才生效。驱动实现如果没检查状态，会静默忽略。

**C. 参数有生效条件**

很多参数需要复位（`11 01`）后才生效，或者需要走 `Routine Control`。

### 修复

**A. 关键参数用 PDO 映射，或提供专门的"应用"例程**

```c
/* 模式切换通过 CiA 402 标准流程, 而不是裸写 6060 */
int set_op_mode(uint8_t mode) {
    uint16_t status;

    /* 1. 确认当前状态允许切换 */
    sdo_read_u16(0x6041, 0, &status);
    uint8_t state = status & 0x6F;
    if (state != STATE_READY_TO_SWITCH_ON) {
        /* 2. 走 Disable Voltage -> Ready to Switch On */
        write_controlword(0x0007);
        wait_for_state(STATE_READY_TO_SWITCH_ON, 1000);
    }

    /* 3. 写操作模式 */
    sdo_write_u8(0x6060, 0, mode);

    /* 4. 用 6061 确认生效 */
    uint8_t displayed;
    sdo_read_u8(0x6061, 0, &displayed);
    return (displayed == mode) ? 0 : -1;
}
```

**B. 参数写入后主动读取 6061 验证**

```c
/* 设备侧: 收到 6060 写入后, 真正切换并更新 6061 */
void od_write_hook_6060(uint8_t new_mode) {
    if (cia402_state_allows_mode_change()) {
        actual_mode = new_mode;
        od_set_u8(0x6061, 0, actual_mode);   /* 同步显示值 */
    }
    /* 不允许时保持旧值, 由主控通过 6061 发现 */
}
```

### 复盘

- **写完参数一定要读回来验证**（对 6060 读 6061，对 6061 读 6064）。
- CiA 402 的模式切换有状态机前置条件，不是自由写。
- 区分"可存储"和"易失"对象，在对象字典文档里标注。
- 主控工具在写关键参数后要有"生效确认"步骤。

## 案例 4: PDO 配好了但一直收不到数据

### 现象

PDO 映射参数全部写成功（`1400h`、`1600h`、`1A00h` 等），COB-ID 也确认无误，但总线上就是看不到 TPDO 帧。

### 抓包分析

```text
(总线上只有 SDO 帧和 Heartbeat, 没有任何 0x181/0x182 帧)
```

### 定位

**PDO 发送的前置条件**，按 CANopen 标准，缺一个都不发：

```text
1. 节点处于 Operational 状态
2. PDO 有效 (Communication Parameter 的 bit31 = 0)
3. 映射数量 > 0
4. 传输类型正确 (同步 / 异步 / 周期)
5. 同步型 PDO 还需要收到 SYNC 帧
```

逐个排查后发现根因是**第 2 条：bit31 被误置 1，PDO 处于禁用状态**。

标准的 PDO 配置顺序是：

```text
1. 禁用 PDO       (bit31 = 1)
2. 清空映射数量   (映射数量 = 0)
3. 写映射对象
4. 写映射数量
5. 配 COB-ID 和传输类型 (bit31 = 0)
6. 启用 PDO       (确认 bit31 = 0)
```

很多实现只做了 3、4 两步，忘了 1 和 6 —— 或者做了 6 但顺序在 3 之前，导致写映射时被拒绝。

### 修复

```c
/* 完整的 PDO 配置流程 */
int configure_tpdo1(uint32_t cob_id, uint8_t trans_type, uint16_t period_ms) {
    /* 1. 禁用 TPDO1: 置 bit31 = 1 */
    od_write_u32(0x1800, 0, 0x80000000u);      /* bit31 = 1 -> PDO 禁用 */

    /* 2. 清空映射数量 */
    od_write_u8(0x1A00, 0, 0);

    /* 3. 写映射: 状态字 + 实际位置 + 实际速度 */
    od_write_u8 (0x1A00, 1, 8);            /* 4 bytes */
    od_write_u32(0x1A00, 2, 0x6041);       /* Statusword */
    od_write_u32(0x1A00, 3, 0x6064);       /* Position actual value */
    od_write_u32(0x1A00, 4, 0x606C);       /* Velocity actual value */

    /* 4. 写映射数量 = 3 */
    od_write_u8(0x1A00, 0, 3);

    /* 5. 配 COB-ID + 传输类型 + 周期 */
    uint32_t comm = cob_id;                /* bit31 = 0 (PDO 有效), bit30 = 0 (保留) */
    comm |= (uint32_t)(trans_type & 0xFE) << 16;  /* bit16-19: transmission type */
    /* bit29 = 0 -> 11 bit 标准帧; 置 1 才是 29 bit 扩展帧 */
    od_write_u32(0x1800, 0, comm);

    /* 6. 写事件定时器 (周期模式下) */
    if (period_ms > 0) {
        od_write_u16(0x1800, 1, period_ms);
    }

    return 0;
}
```

### PDO COB-ID 的四个控制位（CiA 301）

```text
bit 31 (0x80000000)  有效性:  0 = PDO 有效/激活,  1 = PDO 禁用
bit 30 (0x40000000)  保留:    必须为 0
bit 29 (0x20000000)  帧格式:  0 = 11 bit 标准帧,   1 = 29 bit 扩展帧
bit 16-19            传输类型: 0 = 同步非周期, 1 = 同步周期, 0xFE/0xFF = 事件驱动
```

**最容易搞反的是 bit 31**：它是「**禁用**」位，不是「有效」位。所以：

```text
禁用 PDO (重配置映射前):  写 bit31 = 1
启用 PDO (配置完成后):    写 bit31 = 0
```

很多实现（和网上流传的示例代码）把 bit31 当成「有效位」，配置时置 1，结果 PDO 永远不生效 —— 表现就是「进了 Operational 但没有 TPDO 流量」，且总线错误计数器完全干净。

**传输类型不需要额外置 bit29**：事件驱动（0xFE/0xFF）靠传输类型字段表达，不是靠 bit29。bit29 只管帧格式。

**关于同步型 PDO**：如果传输类型是 0x01（同步非周期）或 0x02（同步周期），设备**只在收到 SYNC 帧后才发**。SYNC 帧 COB-ID 是 `0x080`，由主控周期发送。没发 SYNC → 永远收不到 PDO。

```c
/* 同步型 PDO 必须等 SYNC */
if (pdo_is_synchronous() && !sync_received) {
    return;   /* 等 SYNC 触发 */
}
```

### 复盘

- **PDO 配置的 6 步顺序是强制的**，少一步或顺序错就静默失败。
- 调试时优先确认节点在不在 Operational，再看传输类型，最后才查映射内容。
- 同步型 PDO 一定要确认 SYNC 帧在发。
- 建议设备提供"PDO 配置自检"接口，一键检查这 5 个条件。

## 案例 5: PDO 数据长度对不上，解析全是错位

### 现象

主控能收到 TPDO 帧，但解析出来的数据全是错位值。位置值读出来是数量级不对的数字。

### 抓包分析

```text
Node -> Bus  0x181  08 0F 00 00 00 00 00 00   (8 bytes)
```

主控按"状态字(2) + 位置(4) + 速度(4) = 10 字节"解析，但帧只有 8 字节。

### 定位

**CANopen 允许在对象字典里给每个对象指定位数（bit length），实际字节数由位长累加后向上取整。**

比如主控期望的映射是：

```text
0x6041 Statusword       16 bit
0x6064 Position actual  32 bit
0x606C Velocity actual  16 bit
总计 64 bit = 8 bytes
```

但设备实际配的是：

```text
0x6041 Statusword       16 bit
0x6064 Position actual  32 bit
0x606C Velocity actual  32 bit
总计 80 bit = 10 bytes
```

CANopen 规则：**最后一帧如果放不下，剩余字节用填充（0x00）补齐，不跨帧传输**。

所以设备发的是 8 字节（装不下 10 字节就截断或分两帧，取决于实现），主控按 10 字节解析就错位。

### 修复

**A. 双方约定固定的 PDO 布局**

最稳妥的做法是**双方都用 EDS 文件**定义映射，或者在项目文档里明确写出每个 PDO 的字节布局表：

```text
TPDO1 (COB-ID 0x181), 8 bytes:
  byte 0-1 : Statusword        (0x6041)  uint16 LE
  byte 2-5 : Position actual   (0x6064)  int32  LE
  byte 6-7 : Velocity actual   (0x606C)  int16  LE
```

**B. 主控侧按实际接收长度做校验**

```c
int parse_tpdo1(const uint8_t *data, uint8_t len, tpdo1_t *out) {
    if (len < 8) {
        return -1;      /* 长度不足, 丢弃 */
    }
    out->status  = (uint16_t)(data[0] | (data[1] << 8));
    out->pos     = (int32_t)(data[2] | (data[3] << 8) |
                            (data[4] << 16) | (data[5] << 24));
    out->vel     = (int16_t)(data[6] | (data[7] << 8));
    return 0;
}
```

**C. 设备侧确保映射长度和实际发送长度一致**

```c
/* 设备侧: 按映射表计算发送长度 */
uint8_t tpdo1_payload_len(void) {
    uint32_t bits = 0;
    for (int i = 1; i <= od_get_u8(0x1A00, 0); i++) {
        bits += od_entry_bit_len(od_get_u32(0x1A00, i));
    }
    return (bits + 7) / 8;      /* 向上取整到字节 */
}
```

### 复盘

- **CANopen 对象的位长由设备定义**，主控必须知道每个对象的实际位长。
- 主控侧一定要做长度校验，不要盲目按期望长度解析。
- 优先用 EDS 文件统一双方定义。
- PDO 布局要在项目文档里固定成表格，不要靠"大家都知道"。

## 案例 6: NMT Start 发了但节点不进 Operational

### 现象

主控发送 NMT Start（`0x000` 广播或 `0x000` + Node ID），节点 Heartbeat 状态一直是 `0x7F`（Pre-operational），不进 `0x05`（Operational）。

### 抓包分析

```text
Master -> Node  0x000  02 01 01        (NMT: Start Remote Node, Node ID = 1)
Node  -> Bus   0x701  00               (Boot-up, 不是 0x05)
Master -> Node  0x000  02 01 01        (再发一次)
Node  -> Bus   0x701  7F               (Pre-operational)
```

### 定位

**NMT 命令的目标节点 ID 位置错误**，或者 **Node ID 不匹配**。

NMT 命令格式：

```text
byte0: 0x00          (COB-ID = 0x000)
byte1: command       0x01 = Start Remote Node
byte2: node ID      0x00 = 广播到所有节点, 0x01..0x7F = 指定节点
```

上面抓包是 `01 01`，表示启动 Node 1。如果实际设备的 Node ID 是 3，这条命令对它是无效的。

另一种根因：NMT 命令的 **COB-ID 必须是 0x000**。有些实现用了 `0x080`（SYNC 的 ID）或别的 ID，节点收不到。

第三种：**节点自己拒绝进入 Operational**，比如有硬件使能输入未满足，或者启动自检失败。

### 修复

**A. 广播启动 + 检查 Heartbeat**

```c
/* 广播启动所有节点 */
can_send(0x000, 0x01, 0x00, NULL, 0);

/* 然后轮询 Heartbeat 确认状态 */
uint8_t wait_operational(uint8_t node_id, uint32_t timeout_ms) {
    uint32_t start = tick_get_ms();
    while (tick_elapsed_ms(start) < timeout_ms) {
        uint8_t state = heartbeat_state_cache[node_id];
        if (state == 0x05) return 0;         /* Operational */
        if (state == 0x04) return -2;        /* Stopped */
        delay_ms(10);
    }
    return -1;                               /* 超时 */
}
```

**B. 设备侧必须处理 NMT Start**

```c
void nmt_handler(uint8_t cmd, uint8_t node_id) {
    if (node_id != 0 && node_id != my_node_id) {
        return;      /* 不是给我的 */
    }

    switch (cmd) {
        case 0x01:                       /* Start Remote Node */
            if (startup_check_ok()) {
                nmt_state = NMT_OPERATIONAL;
                pdo_start();             /* 启动 PDO 发送 */
            } else {
                nmt_state = NMT_PRE_OPERATIONAL;
                emcy_send(EMCY_GENERIC, 0x00, 0x00);
            }
            break;
        case 0x02:                       /* Stop Remote Node */
            nmt_state = NMT_STOPPED;
            pdo_stop();
            break;
        case 0x80:                       /* Enter Pre-operational */
            nmt_state = NMT_PRE_OPERATIONAL;
            pdo_stop();
            break;
        case 0x81:                       /* Reset Node */
            nmt_state = NMT_RESET;
            do_reset();
            break;
    }
    heartbeat_send();                    /* 立即回报新状态 */
}
```

**C. 心跳是唯一可靠的状态来源**

不要假设"NMT Start 发出去了节点就 Operational 了"，必须等 Heartbeat 回报 `0x05`。

### 复盘

- **NMT 命令格式是 `0x000` + cmd + nodeID**，nodeID 在第 2 字节。
- **状态确认靠 Heartbeat，不靠"我发了命令"**。
- 节点启动自检失败时要给 EMCY，不能静默留在 Pre-operational。
- 主控要有超时和失败处理，不能无限等。

## 案例 7: Heartbeat 超时误判，节点其实在线

### 现象

主控监控显示某节点掉线，但用 CAN 分析仪看，那个节点一直在正常发数据。

### 抓包分析

```text
Node -> Bus  0x702  05      (Heartbeat, Operational, 周期 100ms)
```

Heartbeat 帧完全正常，但主控报超时。

### 定位

**主控侧 Heartbeat 接收过滤器配置错误**。

CANopen 的 Heartbeat COB-ID 是 `0x700 + Node ID`，即一个范围 `0x700 ~ 0x77F`。主控如果要监控所有节点，过滤器必须覆盖这个**范围**，而不是只配具体某个 ID。

```c
/* 错误: 只配了目标节点的 ID */
can_filter_config(FILTER_ID_EXACT, 0x702);

/* 正确: 用 mask 覆盖整个 Heartbeat 范围 */
can_filter_config(FILTER_ID_MASK, 0x700, 0x7F);
```

> **mask 怎么算**：Heartbeat COB-ID = `0x700 + Node ID`，Node ID 是 1–127，所以范围是 `0x701 ~ 0x77F`。要让 `(id & mask) == 0x700` 成立，mask 必须只盖住 bit0–bit6，也就是 **`0x7F`**。
>
> 写成 `0x780`（盖住 bit0–bit7）会连 `0x780` 以上（保留区）一起收进来，虽然实际总线上不会有这些 ID，但属于配置不严谨；写成 `0x7F8` 则只匹配 `0x700` 一个 ID，覆盖不到所有节点。

其他常见根因：

**A. 标准帧/扩展帧类型不匹配**

Heartbeat 用 11 位标准帧。如果过滤器只配了扩展帧，收不到。

**B. FIFO 满被丢弃**

总线上流量大时，FIFO 满会丢帧。Heartbeat 优先级低，容易被丢。

**C. 接收中断没开，或回调里做了阻塞操作**

```c
/* 错误: 在接收中断里做耗时操作, 导致后续帧丢失 */
void CAN_RX_IRQHandler(void) {
    can_frame_t f;
    while (can_receive(&f)) {
        if (is_heartbeat(&f)) {
            process_heartbeat_slowly();   /* 阻塞! */
        }
    }
}
```

### 修复

```c
/* 1. 过滤器覆盖整个 Heartbeat 范围 (0x701 ~ 0x77F) */
can_filter_add(FILTER_ID_MASK, 0x700, 0x7F, FIFO0);

/* 2. 接收中断只做入队, 处理放到任务里 */
typedef struct {
    uint8_t  node_id;
    uint8_t  state;
    uint32_t timestamp_ms;
} hb_entry_t;

static hb_entry_t hb_queue[16];
static volatile uint8_t hb_head, hb_tail;

void CAN_RX_IRQHandler(void) {
    can_frame_t f;
    while (can_receive(&f)) {
        if ((f.id & 0x7F8) == 0x700) {
            uint8_t next = (hb_head + 1) % 16;
            if (next != hb_tail) {           /* 队列满则丢弃, 不阻塞 */
                hb_queue[hb_head].node_id = f.id & 0x7F;
                hb_queue[hb_head].state = f.data[0];
                hb_queue[hb_head].timestamp_ms = tick_get_ms();
                hb_head = next;
            }
        }
    }
}

/* 3. 任务里做超时判定 */
void heartbeat_monitor_task(void *arg) {
    for (;;) {
        uint32_t now = tick_get_ms();
        for (int i = 0; i < NODE_COUNT; i++) {
            if (node_online[i] &&
                (now - last_hb_ms[i]) > (hb_period_ms[i] * 3)) {
                node_online[i] = 0;
                on_node_offline(i);
            }
        }
        task_delay_ms(50);
    }
}
```

### 复盘

- **Heartbeat 是范围 ID（0x700-0x77F）**，过滤器要用 mask。
- 超时阈值建议是周期的 3 倍，避免边界抖动误判。
- **接收中断里绝不做耗时处理**，入队 + 任务处理。
- 队列满时的策略（丢弃最旧 / 丢弃最新）要明确。

## 案例 8: EMCY 上报了但主控解析出错误码

### 现象

设备报了 EMCY，主控显示的错误码和实际故障对不上。

### 抓包分析

```text
Node -> Bus  0x081  08 10 00 21 00 00 00 00
```

主控显示 "0x0021"，但设备实际报的可能是别的。

### 定位

**EMCY 报文的数据格式**：

```text
byte0-1: Error Code (小端 uint16)   0x0010 = Generic Error
        0x0020 = Current
        0x0021 = Current + Device
        0x0030 = Exceeded
        0x0031 = Exceeded + Device
        0x0080 = Monitor
        0x0081 = Monitor + Device
        0x1000 = Device

byte2:   Error Register
byte3-7: Manufacturer Specific
```

问题在于 **Error Code 的低 2 bit 是"故障域"标志，不是错误码的一部分**：

```text
bit0 = 0: 不需要重启 / reset
bit1 = 1: 设备特定 (Device) 错误
```

有些实现把 16 bit 全当错误码显示，有些把 bit1 掩掉，工具和设备对不上。

另一个根因：**Error Register 的位定义**没对上：

```text
bit0: 通用错误
bit1: 电流
bit2: 电压
bit3: 温度
bit4: 设备参数
bit5: 设备厂商特定
bit6: 设备厂商特定
bit7: 附加模块
```

### 修复

```c
/* 设备侧: 正确编码 EMCY */
void emcy_send(uint16_t err_code, uint8_t err_reg, const uint8_t *vendor, uint8_t vendor_len) {
    uint8_t buf[8];
    buf[0] = err_code & 0xFF;        /* 小端 */
    buf[1] = err_code >> 8;
    buf[2] = err_reg;
    memcpy(&buf[3], vendor, vendor_len);
    can_send(0x080 + my_node_id, buf, 8);
}

/* 主控侧: 解析时分离故障域标志 */
typedef struct {
    uint16_t error_code;     /* 原始 16 bit */
    uint16_t base_code;      /* 掩掉 bit0/bit1 后的基础码 */
    uint8_t  needs_reset;    /* bit0 */
    uint8_t  is_device_specific; /* bit1 */
    uint8_t  error_register;
} emcy_info_t;

void parse_emcy(const uint8_t *data, emcy_info_t *out) {
    out->error_code = data[0] | (data[1] << 8);
    out->needs_reset = out->error_code & 0x01;
    out->is_device_specific = (out->error_code >> 1) & 0x01;
    out->base_code = out->error_code & 0xFFFC;
    out->error_register = data[2];
}
```

### 复盘

- **EMCY Error Code 的 bit0/bit1 是标志位**，显示时要说清楚是否掩掉。
- Error Code 和 Error Register 是两个维度，不能混为一谈。
- 设备应实现标准的 Error Register 位定义（至少 bit0/bit2/bit3）。

## 案例 9: SDO 写超时，节点一直不回 Abort

### 现象

写某个 SDO 对象，主控等响应超时。抓包显示请求已发出，节点**完全没有任何响应帧**（不是 Abort，是没回）。

### 抓包分析

```text
Master -> Node  0x601  06 23 60 60 01 00 00 00
(无任何响应)
```

### 定位

节点的 SDO 处理函数在写这个对象时**卡住或崩溃**。

常见根因：

**A. 写 handler 里做了阻塞 Flash 写，没返回**

```c
/* 错误: 直接在 SDO 上下文里写 Flash, 耗时几十 ms 甚至更长 */
int did_write_0x6060(uint8_t val) {
    flash_erase_page(CONFIG_PAGE);
    flash_program(CONFIG_PAGE, &val, 1);
    flash_wait_ready();          /* 可能几秒! */
    return 0;
}
```

UDS 的 P2 超时是 50 ms，CANopen 没有 ISO-TP 层的流控，SDO 请求**必须快速应答**。长操作应该返回 Abort 或用分段传输。

**B. 写 handler 越界崩溃**

```c
/* 错误: 没检查长度 */
int did_write_0xF190(const uint8_t *data, uint8_t len) {
    memcpy(g_vin, data, len);    /* len 可以是 255, g_vin 只有 17 字节! */
    return 0;
}
```

这会触发 HardFault，节点直接挂掉 —— 表现就是"完全无响应"。

**C. SDO 通道被占用未释放**

上一次 SDO 事务因为异常没有释放通道，后续请求被忽略。

### 修复

**A. 长操作不能阻塞 SDO 上下文**

```c
/* 方案 1: 拒绝不支持的长操作 */
int did_write_0x6060(uint8_t val) {
    if (!is_in_operational()) {
        return ABORT_CONDITION_NOT_CORRECT;   /* 0x08000021 */
    }
    od_set_u8(0x6060, 0, val);      /* 只写 RAM, 立即返回 */
    return 0;
}

/* 方案 2: 需要写 Flash 的对象用分段传输 (segmented SDO) */
```

**B. 严格检查长度**

```c
int did_write_0xF190(const uint8_t *data, uint8_t len) {
    if (len != 17) {
        return ABORT_LENGTH_NOT_CORRECT;    /* 0x06070012 */
    }
    memcpy(g_vin, data, 17);
    return 0;
}
```

**C. SDO 通道状态机 + 看门狗**

```c
/* 请求到达时重置超时 */
void sdo_rx_isr(const can_frame_t *f) {
    sdo_ctx.last_req_ms = tick_get_ms();
    sdo_ctx.state = SDO_BUSY;
}

/* 周期任务检查 */
void sdo_timeout_task(void *arg) {
    if (sdo_ctx.state == SDO_BUSY &&
        tick_elapsed_ms(sdo_ctx.last_req_ms) > SDO_TIMEOUT_MS) {
        sdo_ctx.state = SDO_IDLE;       /* 释放通道 */
    }
}
```

**D. 加看门狗兜底**

```c
/* SDO 处理前后喂狗, 处理中崩溃能恢复 */
int sdo_process(const can_frame_t *f) {
    watchdog_feed();
    int r = sdo_dispatch(f);
    watchdog_feed();
    return r;
}
```

### 复盘

- **SDO 响应必须是毫秒级的**，任何耗时操作要挪出 SDO 上下文。
- 所有写 handler 必须做长度检查 —— 这是最直接的节点挂死原因。
- 节点必须有看门狗，SDO 处理崩溃能自动恢复。
- SDO 通道要有超时释放机制，避免一次异常卡死后续所有通信。

## 案例 10: 总线负载高时低优先级 PDO 被饿死

### 现象

总线节点增多后，某些 PDO 帧开始周期性丢失。但单独测试每个节点都正常。

### 抓包分析

```text
(高优先级诊断 / 节点管理帧密集)
0x000 (NMT)      每次广播
0x080 (SYNC)     周期 10ms
0x180-0x1FF      周期 PDO, 多节点
0x580/0x600      SDO 大量
0x700-0x77F      Heartbeat

低优先级 PDO (COB-ID 0x281, 节点 5) 长时间不出现
```

### 定位

CAN 的非破坏性仲裁机制决定了：**CAN ID 小的优先级高，低优先级帧在总线忙时必须等待**。

CANopen 默认 COB-ID 分配：

```text
0x000  NMT          最高
0x080  SYNC
0x081-0x0FF EMCY
0x100-0x17F TPDO1   (0x180 + NodeID 的前 0x80 个)
0x180-0x1FF TPDO1
0x200-0x27F RPDO1
0x280-0x2FF TPDO2
0x300-0x37F RPDO2
0x380-0x3FF TPDO3
0x400-0x47F TPDO4
0x480-0x4FF SDO Tx
0x500-0x57F RPDO4
0x580-0x5FF SDO Tx (标准)
0x600-0x67F SDO Rx (标准)
0x700-0x77F Heartbeat
```

**Node ID 越大，COB-ID 越大，优先级越低**。Node ID = 127 的节点用 `0x700 + 127 = 0x77F`，是全网最低优先级。

当总线利用率超过一定阈值，低优先级帧会持续被推迟，导致接收方**超时判定为掉线**。

### 修复

**A. 缩短周期 + 合理错峰**

```c
/* 不要所有节点同一时刻发送, 加随机化偏移 */
void pdo_send_task(void *arg) {
    uint32_t period = pdo_period_ms;
    uint32_t offset = (my_node_id * 7) % period;   /* 按 Node ID 错峰 */

    task_delay_ms(offset);
    for (;;) {
        pdo_send();
        task_delay_ms(period);
    }
}
```

**B. 降低非必要帧的优先级消耗**

```c
/* 减少 SYNC 频率, 或只让需要的节点订阅 SYNC */
/* 心跳周期按重要性分级: 关键节点 100ms, 普通节点 500ms 或 1s */
```

**C. 收紧总线负载指标**

```text
设计目标: 稳态负载 < 40%, 峰值 < 70%

测量:
  candump -n 1000 can0 | 计算总位数 / (总线速率 × 时间)
```

**D. 必要时用 CAN FD**

CAN FD 保持仲裁段速率不变，但数据段速率可提高，吞吐翻倍而仲裁行为不变。

### 复盘

- **COB-ID 越大优先级越低**，Node ID 大的节点天然吃亏。
- 周期帧必须错峰，否则会形成周期性总线峰值。
- 总线负载要留足余量，30% 以下才安全。
- 丢帧排查先看总线负载，再看节点实现。

## 案例 11: 同步 PDO 偶发丢一帧，SYNC 抖动

### 现象

同步型 PDO 数据偶尔丢一帧或延迟一帧，但 SYNC 帧抓包看是正常的。

### 抓包分析

```text
Master -> Bus  0x080  08 00 00 00 00 00 00 00   (SYNC, 周期 10ms)
Node  -> Bus  0x181  ...                          (TPDO, 应该在 SYNC 后立即)
Node  -> Bus  0x181  ...                          (下一帧)
(中间有一帧 PDO 缺失)
```

### 定位

**SYNC 帧序号（Sync Counter）处理有问题**。

CANopen 的 SYNC 帧第 0 字节是**同步计数器**（SYNC COUNTER）：

```text
byte0: SYNC counter (0..255 循环)
byte1-7: 保留
```

接收方应该检查这个计数器**是否连续**。如果跳号，说明丢了一次 SYNC。

常见根因是**发送方没做 SYNC 计数器检查**，或者**收到 SYNC 后没有立即触发 PDO，而是等下一个周期定时器**。

另一种情况：SYNC 的**发送时刻不稳定**。SYNC 通常由主控在固定周期（如 10 ms）发出，如果 SYNC 是由某个事件触发而不是定时器触发，抖动会传导到所有同步 PDO。

### 修复

**A. 检查 SYNC 计数器连续性**

```c
void sync_received(const uint8_t *data) {
    uint8_t counter = data[0];
    uint8_t expected = (last_sync_counter + 1) & 0xFF;

    if (sync_counter_valid && counter != expected) {
        sync_lost_count++;      /* 丢了一次 SYNC */
    }
    last_sync_counter = counter;
    sync_counter_valid = 1;

    /* 立即触发同步 PDO 发送 */
    send_sync_pdos();
}
```

**B. 收到 SYNC 立即发送，不要等周期定时器**

```c
/* 错误: 定时器周期 = 10ms, SYNC 到达时刻抖动, 两个触发源打架 */
void pdo_timer_cb(void) {
    if (pdo_type == SYNC) {
        pdo_send();      /* 和 SYNC 触发的发送重复了! */
    }
}

/* 正确: 同步型只在 SYNC 到达时发送 */
void pdo_send_dispatch(void) {
    if (pdo_type == SYNC) {
        if (sync_received_flag) {
            pdo_send();
            sync_received_flag = 0;
        }
    } else {
        pdo_send();      /* 事件驱动 / 周期型不受 SYNC 控制 */
    }
}
```

**C. SYNC 必须由硬件定时器产生**

```c
/* 主控: 用硬件定时器触发 SYNC, 不受业务负载影响 */
void TIM_IRQHandler(void) {
    if (sync_timer_expired()) {
        uint8_t data[8] = {0};
        data[0] = sync_counter++;     /* 计数器在每次发送时递增 */
        can_send(0x080, data, 8);
    }
}
```

### 复盘

- **SYNC 帧第 0 字节是计数器**，必须检查连续性才能发现丢 SYNC。
- 同步型 PDO 只能由 SYNC 触发，不能同时有定时器触发源。
- SYNC 必须用硬件定时器，抖动会传导给全网同步 PDO。
- 抓包时把 SYNC 和 PDO 画在同一时间轴上对比，最直观。

## 案例 12: 设备更换后行为不同，EDS 与实际实现不符

### 现象

用主站工具加载 EDS 后能正常工作；换成另一个厂商的同类设备，EDS 加载成功但通信异常。手动读取对象字典发现对象布局不同。

### 抓包分析

```text
Master -> Node  0x601  02 40 00 10 00 00 00 00
Node  -> Master 0x581  06 43 00 10 00 00 00 00   (设备类型 = 0x00000000)

(但 EDS 里写的是 Drive)
```

设备类型对象 `1000h` 的值不对。

### 定位

**EDS（Electronic Data Sheet）描述的是设备宣称支持的对象字典，但实际固件实现可能不一致**。

常见原因：

- 固件版本和 EDS 版本不匹配。
- EDS 是通用模板，实际设备只实现了子集。
- 同一型号不同批次固件实现有差异。
- 厂商的 EDS 本身有错误。

CANopen 规范定义了 `1018h` Identity Object 里的 **Supported Modules**（支持的模块列表）和 `1019h` **All Supported Objects**，设备应该如实上报自己实现了哪些对象。

### 修复

**A. 设备侧：用 1019h 如实上报支持的对象**

```c
/* 启动时扫描并生成支持对象列表 */
void build_supported_objects_list(void) {
    uint16_t count = 0;
    for (uint16_t idx = 0x1000; idx <= 0x1FFF; idx++) {
        if (od_entry_exists(idx, 0)) {
            od_set_u16(0x1019, count + 1, idx);
            count++;
        }
    }
    od_set_u8(0x1019, 0, (uint8_t)count);
}
```

**B. 主控侧：不盲信 EDS，运行时探测**

```c
/* 用 SDO 实际探测关键对象是否存在 */
int probe_node(uint8_t node_id, uint16_t index, uint8_t subindex) {
    uint8_t req[8];
    build_sdo_upload_req(index, subindex, req);
    can_send(0x600 + node_id, req, 8);

    /* 等待响应, 区分 Abort(对象不存在) 和超时 */
    uint8_t resp[8];
    if (!sdo_wait_response(node_id, resp, 1000)) {
        return PROBE_TIMEOUT;
    }
    if (resp[0] == 0x80) {
        return PROBE_NOT_SUPPORTED;
    }
    return PROBE_OK;
}
```

**C. 主控侧：对关键对象做能力协商**

```c
typedef struct {
    uint8_t has_cia402;
    uint8_t has_sdo_uds;
    uint8_t max_pdo_channels;
} node_caps_t;

void detect_caps(uint8_t node_id, node_caps_t *caps) {
    caps->has_cia402      = (probe_node(node_id, 0x6041, 0) == PROBE_OK);
    caps->has_max_torque  = (probe_node(node_id, 0x6073, 0) == PROBE_OK);
    caps->max_pdo_channels = 4;   /* 保守默认 */
}
```

### 复盘

- **EDS 是声明，不是事实** —— 主控侧必须做运行时探测。
- 设备侧应通过 `1019h` 如实上报支持的对象。
- 产线要维护"设备型号 × 固件版本 × 实际能力"的对照表。
- 换厂商设备时，这个案例 100% 会复现。

## 根因清单

| 根因 | 典型症状 | 快速验证 |
| --- | --- | --- |
| Node ID 重复 | 两设备互相顶掉 | 抓 Boot-up 帧 ID |
| SDO Index 大端 | 读对象返回 0x06020000 | 核对字节序 |
| 参数未生效 | 写成功但行为不变 | 读 6061 验证 |
| PDO 有效位误置 | 配好了但不发 PDO | 查 1800h bit31（=0 才有效） |
| PDO 位长不一致 | 解析全错位 | 核对映射字节数 |
| NMT nodeID 位置错 | 不进 Operational | 看 Heartbeat 状态 |
| Heartbeat 过滤器错 | 误报掉线 | 查过滤器 mask |
| EMCY 标志位混淆 | 错误码对不上 | 分离 bit0/bit1 |
| SDO handler 越界 | 节点完全无响应 | 加长度检查 |
| 总线负载过高 | 低优先级 PDO 丢帧 | 测总线利用率 |
| SYNC 计数器不检查 | 同步 PDO 丢帧 | 检查计数器连续性 |
| EDS 与实现不符 | 换设备行为不同 | 运行时探测对象 |

## 关联主题

- `bus/canopen.md` — CANopen 定位、对象字典、SDO/PDO
- `bus/can-canopen-deep-dive.md` — COB-ID 规则、SDO 命令字、PDO 映射、NMT、CiA 402
- `bus/can-canopen-practical.md` — CAN 物理层 + COB-ID + 电机调试流程
- `basic/can-failure-cases.md` — CAN 物理层/链路层案例
- `basic/can-multimaster-and-bus-off.md` — 仲裁与 Bus Off
- `bus/uds-failure-cases.md` — UDS 诊断案例对比
- `bus/can-protocol-family.md` — CAN 家族全景

## 更新记录

- 2026-10-31: 初版，12 个产线案例。覆盖 Node ID 冲突、SDO 字节序、参数生效、PDO 有效位与位长、NMT 启动、Heartbeat 过滤、EMCY 编码、SDO 越界挂死、总线负载饿死、SYNC 计数器、EDS 与实现不符等高频坑。
