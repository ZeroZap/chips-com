# CANopen Safety（CiA 304 / EN 50325-5）

> CANopen 的功能安全扩展：在同一条 CAN 总线上，用 **SRDO（Safety Related Data Object）** 传输安全相关数据，达到 SIL-3 级别的通信可靠性。
>
> 与标准 CANopen **并行运行**——普通 PDO / SDO 不受影响，安全设备和非安全设备可以共线。

## 标准定位

| 项 | 内容 |
| --- | --- |
| CiA 编号 | **CiA 304**（原始规范编号） |
| 欧洲标准 | **EN 50325-5:2010**，全称 *Industrial communications subsystem based on ISO 11898 (CAN) for controller-device interfaces — Part 5: Functional safety communication based on EN 50325-4* |
| 基础标准 | **EN 50325-4**（= CANopen 主体，对应 CiA 301） |
| 安全生命周期标准 | **IEC/EN 61508**（功能安全） |
| 认证 | TÜV 认证可达 **SIL 3** |
| 发布时间 | CiA 304 先出，2010-07 CENELEC 发布 EN 50325-5，2023-05 复审确认 |

> **关键点**：EN 50325-5 **不覆盖**安全相关系统的配置流程与搭建流程，只定义**通信层**。系统级安全论证（安全手册、诊断覆盖率、PFD 计算）另由 IEC 61508 / ISO 13849 体系负责。

## 核心机制：SRDO

SRDO 的配置方式与 PDO 类似，但多了 4 项安全属性：

| 机制 | 说明 |
| --- | --- |
| **1-out-of-2 冗余传输** | 同一份数据发两帧：一帧正常值，一帧**逐位取反**（bitwise inverted） |
| **时间监控** | SCT（Safety Cycle Time）+ SRVT（Safety Related Validation Time）双重超时检测 |
| **配置完整性保护** | SRDO 参数用 **CRC-16-CCITT** 签名，配置被改 → CRC 不符 → 拒绝生效 |
| **GFC（Global Failsafe Command）** | 可选机制：广播一条 CAN ID = 0x001、DLC = 0 的帧，所有消费者进入安全状态 |

### 为什么「取反」而不是「CRC」

取反冗余极高效：**接收端只需判断两帧是否互为反码**，不需要 CRC 计算，也不需要在数据里附带校验字段。代价是占用两倍带宽。

- COB-ID 1（正常）：**奇数**，范围 `0x101` ~ `0x17F`
- COB-ID 2（取反）：**偶数**，范围 `0x102` ~ `0x180`

> 标准预留 SRDO 的 COB-ID 在 **0x100 ~ 0x180** 区间。这保证 SRDO 帧的**仲裁优先级高于 PDO**（ID 更小），同时不与任何标准 CANopen 服务（SDO/EMCY/Heartbeat/NMT）冲突。

### SCT 与 SRVT 的区别

```
        ┌─────── SCT = 100ms（安全周期时间）────────┐
        │                                          │
   ┌────┴────┐                              ┌──────┴──────┐
   │ 正常帧   │  ──── SRVT = 10ms ────►     │  正常帧     │
   └────┬────┘   （两帧允许的最大间隔）      └──────┬──────┘
        │                                          │
        ▼                                          ▼
   ┌─────────┐                             ┌─────────┐
   │ 取反帧   │                             │ 取反帧   │
   └─────────┘                             └─────────┘

超时判定：
  SRVT 超时 → 两帧没配对     → 视为安全事件（数据不可信）
  SCT  超时 → 整个周期没数据  → 视为安全事件（通信中断）
```

- **SCT** = 安全周期时间，同时也是**发送周期**（Refresh Time）。超时 = 通信断了。
- **SRVT** = 安全相关确认时间，规定同一对「正常帧 + 取反帧」之间的最大允许间隔。超时 = 两帧没配上。

> **最容易搞错的点**：SCT 和 SRVT **不是同一个东西**。SCT 管「周期」，SRVT 管「配对」。生产端 SRVT 通常填 0（不适用），消费端才需要填实际值。

## 对象字典布局

| Index | 名称 | 说明 |
| --- | --- | --- |
| **0x1300** | GFC Parameter | Bit 0：GFC 有效/无效 |
| **0x1301 ~ 0x1340** | SRDO 通信参数 | 每个 SRDO 一个 |
| **0x1381 ~ 0x13C0** | SRDO 映射参数 | 每个 SRDO 一个 |
| **0x13FE** | Configuration Valid | 写 **0xA5** 表示配置有效 |
| **0x13FF** | Safety Configuration Signature | 每个 SRDO 的 CRC 签名 |

> ⚠️ 注意 **0x13FE / 0x13FF 落在 0x1301~0x1340 与 0x1381~0x13C0 的区间尾部之外**——0x1301~0x1340 是 64 个 index，0x1381~0x13C0 也是 64 个，0x13FE/0x13FF 在其后，不冲突。

### 0x13xx — SRDO 通信参数

| Sub | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| 0 | Highest sub-index | UNSIGNED8 | 通常 = 6 |
| 1 | Information Direction | UNSIGNED8 | **0=不存在/无效，1=发送(tx)，2=接收(rx)** |
| 2 | Refresh Time / SCT | UNSIGNED16 | 周期，毫秒 |
| 3 | SRVT | UNSIGNED8 | 毫秒；tx 侧通常填 0 |
| 4 | Transmission Type | UNSIGNED8 | 一般固定 = 254 |
| 5 | COB-ID 1（正常） | UNSIGNED32 | 默认 `0xFF + 2 × NodeID`（奇数） |
| 6 | COB-ID 2（取反） | UNSIGNED32 | 默认 `0x100 + 2 × NodeID`（偶数） |

> **默认值公式**：NodeID = 0x40 时 → COB-ID1 = 0xFF + 0x80 = 0x17F，COB-ID2 = 0x100 + 0x80 = 0x180。这与 Temposonics MH-Series 安全传感器的实测文档一致。
>
> **发送/接收方向由 OD 运行时决定**（PDO 是编译期决定）——这是 SRDO 与 PDO 的关键实现差异。

### 0x13xx（配对）— SRDO 映射参数

| Sub | 名称 | 类型 |
| --- | --- | --- |
| 0 | Highest sub-index supported | UNSIGNED8 |
| 1 | 映射项 1（正常数据） | UNSIGNED32 |
| 2 | 映射项 1（取反数据） | UNSIGNED32 |
| 3 | 映射项 2（正常数据） | UNSIGNED32 |
| 4 | 映射项 2（取反数据） | UNSIGNED32 |
| … | 成对递增 | … |

> **映射必须成对**：同一份应用数据，要同时映射「正常副本」和「取反副本」两个 OD 对象。标准允许理论最多 64 个应用对象，但**通常按字节/字映射，实际最多 8 个**（CAN 8 字节上限）。
>
> 实现上：OD 属性必须打上 `ODA_RSRDO` / `ODA_TRSRDO` 标志（由 CANopenEditor 配置）。

## 安全配置签名（CRC）

**CRC-16-CCITT**，多项式 **0x1021**，**小端（little-endian）** 字节序计算。

计算范围（顺序固定，seed 逐段传递）：

| 顺序 | 对象 | Sub | 字节数 |
| --- | --- | --- | --- |
| 1 | 0x1301 SRDO 通信参数 | 01 Information Direction | 1 |
| 2 | 0x1301 | 02 Refresh Time / SCT | 2 |
| 3 | 0x1301 | 03 SRVT | 1 |
| 4 | 0x1301 | 05 COB-ID 1 | 4 |
| 5 | 0x1301 | 06 COB-ID 2 | 4 |
| 6 | 0x1381 SRDO 映射参数 | 00 映射数量 | 1 |
| 7+ | 0x1381 | 01,02,03… 逐项 | 每项 1(sub) + 4(mapping) |

> **注意**：Sub 04（Transmission Type）**不参与** CRC 计算。
>
> **注意**：安全配置签名是**唯一规定为小端**的 CRC —— 与其他 CANopen CRC 习惯相反，别照搬常规 CRC 工具的字节序。

CRC 计算完成后：

1. 写 `0x13FF`（按 SRDO 序号，sub 1 = SRDO1，sub 2 = SRDO2…）
2. 写 `0x13FE` = **0xA5** → 配置生效

## 配置流程（SDO 实操序列）

```
① 节点进 Pre-Operational（NMT 0x80）
② 读回所有安全相关参数（用于算 CRC）
③ SDO 写 0x13FF sub N = 计算好的 CRC
④ SDO 写 0x13FE sub 0 = 0xA5      ← 配置生效
⑤ NMT Start（0x01）→ 进 Operational → SRDO 开始收发
```

### 完整抓包示例（NodeID = 0x01，Refresh = 10 ms）

```
COB-ID   Dir  DLC  D0 D1 D2 D3 D4 D5 D6 D7   说明
0x701    Tx   1   00                             Boot-up
0x601    Rx   8   2B 01 13 02 0A 00 00 00      写 Refresh Time = 10 ms
0x581    Tx   8   60 01 13 02 00 00 00 00      响应
0x601    Rx   8   2B FF 13 01 AF C4 00 00      写 Safety config CRC = 0xC4AF
0x581    Tx   8   60 FF 13 01 00 00 00 00      响应
0x601    Rx   8   23 10 10 01 73 61 76 65      Store parameters ("save")
0x581    Tx   8   60 10 10 01 00 00 00 00      响应
0x601    Rx   8   40 01 13 05 00 00 00 00      读 COB-ID1
0x581    Tx   8   42 01 13 05 01 01 00 00      响应 = 0x101
0x601    Rx   8   40 01 13 06 00 00 00 00      读 COB-ID2
0x581    Tx   8   42 01 13 06 02 01 00 00      响应 = 0x102
0x601    Rx   8   2F FE 13 00 A5 00 00 00      Configuration valid = 0xA5
0x581    Tx   8   60 FE 13 00 00 00 00 00      响应
0x000    Rx   1   01                             NMT Start Remote Node
0x101    Tx   8   <Pos Pos Pos Pos Vel Vel Stat Cnt>    SRDO 正常帧
0x102    Tx   8   <反码>                                SRDO 取反帧
```

### CRC-16-CCITT 参考实现

```c
/* CRC-16-CCITT, poly = 0x1021, 小端字节序, init = 0x0000
 * 注意：安全配置签名专用，与其他 CANopen CRC 的字节序相反 */

/* 单字节喂入 */
static uint16_t crc16_ccitt_byte(uint16_t crc, uint8_t data)
{
    crc ^= (uint16_t)data << 8;
    for (int i = 0; i < 8; i++) {
        if (crc & 0x8000u) {
            crc = (uint16_t)((crc << 1) ^ 0x1021u);
        } else {
            crc = (uint16_t)(crc << 1);
        }
    }
    return crc;
}

/* 多字节喂入（little-endian：低字节先） */
static uint16_t crc16_ccitt_le(uint16_t crc, const uint8_t *data, size_t len)
{
    for (size_t i = 0; i < len; i++) {
        crc = crc16_ccitt_byte(crc, data[i]);
    }
    return crc;
}

/* 算单个 SRDO 的安全配置签名 */
uint16_t calc_srdo_signature(uint8_t info_dir,
                              uint16_t sct_ms,
                              uint8_t  srvt_ms,
                              uint32_t cob_id1,
                              uint32_t cob_id2,
                              uint8_t  map_count,
                              const uint8_t *mapping /* 成对映射表原始字节 */)
{
    uint16_t crc = 0x0000u;

    /* ① 0x1301: sub 01 Info Direction (1 byte) */
    crc = crc16_ccitt_byte(crc, info_dir);

    /* ② 0x1301: sub 02 Refresh/SCT (2 bytes, LE) */
    crc = crc16_ccitt_le(crc, (const uint8_t *)&sct_ms, 2);

    /* ③ 0x1301: sub 03 SRVT (1 byte) */
    crc = crc16_ccitt_byte(crc, srvt_ms);

    /* ④ 0x1301: sub 05 COB-ID 1 (4 bytes, LE) */
    crc = crc16_ccitt_le(crc, (const uint8_t *)&cob_id1, 4);

    /* ⑤ 0x1301: sub 06 COB-ID 2 (4 bytes, LE) */
    crc = crc16_ccitt_le(crc, (const uint8_t *)&cob_id2, 4);

    /* ⑥ 0x1381: sub 00 映射数量 (1 byte) */
    crc = crc16_ccitt_byte(crc, map_count);

    /* ⑦ 0x1381: 每项 = sub 序号(1 byte) + mapping 值(4 bytes, LE)
     *    注意成对顺序：1=正常1, 2=取反1, 3=正常2, 4=取反2 ... */
    crc = crc16_ccitt_le(crc, mapping, (size_t)map_count * 5u);

    /* sub 04 Transmission Type 不参与 CRC */
    return crc;
}
```

## 接收端校验逻辑

```c
typedef enum {
    SRDO_OK = 0,
    SRDO_ERR_RX_SHORT,          /* 收到的帧长度不足 */
    SRDO_ERR_RX_NOT_INVERTED,   /* 两帧不是互为反码 */
    SRDO_ERR_RX_TIMEOUT_SRVT,   /* 取反帧没在 SRVT 内到达 */
    SRDO_ERR_RX_TIMEOUT_SCT,    /* 下一组正常帧没在 SCT 内到达 */
    SRDO_ERR_TX_NOT_INVERTED,   /* 本机发出去的取反帧错了 */
    SRDO_ERR_TX_FAIL,           /* CAN 发送失败 */
    SRDO_ERR_CONFIGURATION,     /* CRC 不符 / 配置无效 */
} srdo_error_t;

/* 收到一帧时调用。is_inverted 决定按哪套期望值校验 */
void srdo_on_frame(srdo_ctx_t *ctx, uint8_t is_inverted,
                   const uint8_t *data, uint8_t len)
{
    if (len < ctx->expect_len) {
        ctx->err = SRDO_ERR_RX_SHORT;
        return;
    }

    if (!is_inverted) {
        /* 存正常帧快照，等取反帧来配对 */
        memcpy(ctx->normal_buf, data, len);
        ctx->have_normal = 1;
        ctx->t_normal_us = now_us();
        return;
    }

    /* 取反帧：必须与正常帧逐位互反 */
    if (!ctx->have_normal) {
        ctx->err = SRDO_ERR_RX_TIMEOUT_SRVT;
        return;
    }

    for (uint8_t i = 0; i < len; i++) {
        if ((uint8_t)(data[i] ^ ctx->normal_buf[i]) != 0xFFu) {
            ctx->err = SRDO_ERR_RX_NOT_INVERTED;
            return;
        }
    }

    /* SRVT 检查：两帧间隔不能超 */
    if ((uint32_t)(now_us() - ctx->t_normal_us) > (uint32_t)ctx->srvt_ms * 1000u) {
        ctx->err = SRDO_ERR_RX_TIMEOUT_SRVT;
        return;
    }

    /* 配对成功 → 数据可用 */
    ctx->err = SRDO_OK;
    ctx->have_normal = 0;
    memcpy(ctx->value, ctx->normal_buf, len);
    ctx->value_valid = 1;
}
```

### 安全状态机

所有 SRDO 都必须处于「通信已建立」状态，设备才允许进入正常工作态。**任一 SRDO 出错 → 整机进入安全状态**。

```
  NMT 非 Operational
        ↓
  initializing（刚进 Operational，尚未收/发过）
        ↓  收到并配对成功一对帧
  communicationEstablished   ← 只有到这里才允许正常工作
        ↓
  任何超时/取反不符 → error_* → 安全状态
```

## GFC（Global Failsafe Command）

最简单的失效安全机制：

- **CAN ID = 0x001**，**DLC = 0**（无数据）
- 发送方置 `0x1300` Bit 0 = 有效后广播
- 所有接收方收到即触发安全回调

```c
/* 发送 GFC */
can_frame_t f = {0};
f.id  = 0x001;
f.dlc = 0;
can_send(&f);

/* 接收 GFC → 进安全状态 */
void gfc_rx_cb(const can_frame_t *f) {
    if (f->id == 0x001 && f->dlc == 0) {
        enter_safe_state();
    }
}
```

## 产线调试要点

| 症状 | 排查方向 |
| --- | --- |
| 设备进 Operational 但不发 SRDO 帧 | `0x1301` sub1（Information Direction）是否为 1（tx）；`0x13FE` 是否已写 0xA5 |
| 收到的数据是乱的 | 取反帧没配对 → 检查 COB-ID1 是奇数、COB-ID2 是偶数 |
| 消费端一直报超时 | ① SRVT 填太小（生产端两帧间隔 > SRVT）② SCT 填太小 ③ 总线负载过高导致帧延迟 |
| CRC 校验总是不通过 | ① 字节序搞反（安全签名是**小端**）② 漏算 sub 04（**不**参与）③ 映射项顺序不是「正常/取反」成对 |
| 改了参数就失效 | 正常行为：写 `0x13FE`/`0x13FF` 或改 SRDO 参数会让配置失效，需**重算 CRC 并重写 0x13FE = 0xA5** |
| 一个节点能收不能发 | 检查 SRDO 的 Information Direction（1=tx / 2=rx），以及 `0x13FE` 状态 |

### 关键顺序陷阱

**修改任何 SRDO 参数后，必须重算 CRC 并重新写 `0x13FE = 0xA5`，否则配置立即失效。** 很多实现里，SDO 写 `0x13FE`/`0x13FF` 会**自动清除配置有效标志**（置 0），强制设备退回非安全态直到重新校验通过。

## 与相关标准的关系

| 标准 | 关系 |
| --- | --- |
| **EN 50325-4** | CANopen 主体（= CiA 301），SRDO 建立在它之上 |
| **ISO 11898-1/-2** | CAN 数据链路层 / 物理层 |
| **IEC/EN 61508** | 功能安全生命周期标准（SRDO 只解决通信层） |
| **ISO 13849** | 机械安全（PL d/e），与 SIL 对应关系用于设备选型 |
| **CiA 306** | CANopen 设备描述（EDS/DCF），安全设备需在 EDS 中声明安全相关对象 |
| **EN 50325-5** | 本标准本身 |

## 相关文档

- `bus/automotive/canopen.md` — CANopen 定位、对象字典、SDO/PDO/NMT
- `bus/automotive/canopen-failure-cases.md` — CANopen 产线案例（Node ID 冲突 / SDO 字节序 / PDO 映射 / NMT）
- `bus/automotive/can-standards-map.md` — CAN 家族标准规范总表（按层 + 按协议）
- `bus/automotive/can-protocol-family.md` — CAN 协议全景与覆盖缺口
