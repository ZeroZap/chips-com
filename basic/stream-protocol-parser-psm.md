# 流式协议解析器 PSM（Protocol State Machine）

## 目标

把 chips-com 里分散在 UART / TCP / CAN 上的「沾包 / 断帧 / 半包 / 重组」做法抽成一篇统一参考。

覆盖三个层级，从最薄的字节流到最厚的多包流控：

| 层级 | 物理 / 传输 | 协议 | 关键问题 |
| --- | --- | --- | --- |
| L1 字节流 | UART / SPI / I2C | 二进制 SOF+LEN+CRC | 断帧 / 半包 / 沾包（= 多帧） |
| L2 TCP 流 | TCP socket | Modbus TCP（MBAP）| 沾包 / 半包 / 多客户端 |
| L3 多包重组 | CAN（8B 帧） | J1939 TP（BAM / RTS-CTS）| 多包分片 + 流控 + 超时 + 重传 |

每层都是同一种状态机思想在不同物理层的复现：**有限状态机 + 缓冲 + 异常恢复**。本文把它收成一份"模式库"。

## 为什么必须用状态机（PSM）

- 串口是**字节流**（无消息边界），TCP 是**字节流**，CAN 是**帧流**——它们都不天然携带"这是一条消息的开始/结束"。
- 任何"假设一次 `read` / `recv` 收到完整消息"的代码都是错的。接收方可能出现：
  - 半包（一次 `read` 只收到半条消息）
  - 沾包（一次 `read` 收到多条消息）
  - 错帧（噪声、CRC 错、长度的字段对不上）
  - 假 SOF（数据里出现和 SOF 相同的字节）
- 正确做法：把接收过程建模成**有限状态机**，按"看到的字节 / 字段"决定下一步进哪个状态。任何"看上去不对劲"就**回到初始状态**等下一个 SOF。

## 模式库 1：L1 字节流分帧（UART）

**来源**：`basic/uart-failure-cases.md` 案例 7（协议分帧错，字节流错乱）。

### 5 状态机：SOF + LEN + DATA + CRC

```c
typedef enum {
    RX_SOF,     /* 等起始符 0xAA */
    RX_LEN_L,   /* 长度低字节 */
    RX_LEN_H,   /* 长度高字节 */
    RX_DATA,    /* 收 len 字节数据 */
    RX_CRC,     /* 收 CRC 字节 */
} rx_state_t;

typedef struct {
    rx_state_t  state;
    uint16_t    len;        /* LEN_L + LEN_H 解析出的长度 */
    uint16_t    pos;        /* 当前 DATA 已收字节数 */
    uint8_t     buf[256];   /* 帧缓冲 */
    uint8_t     crc;        /* 计算中的 CRC */
} rx_ctx_t;

void uart_rx_byte(rx_ctx_t *ctx, uint8_t byte) {
    switch (ctx->state) {
    case RX_SOF:
        if (byte == 0xAA) ctx->state = RX_LEN_L;
        /* 错帧字节一律丢弃, 保持 RX_SOF 等待下一个 SOF */
        break;
    case RX_LEN_L:
        ctx->len = byte;
        ctx->state = RX_LEN_H;
        break;
    case RX_LEN_H:
        ctx->len |= ((uint16_t)byte << 8);
        if (ctx->len > sizeof(ctx->buf)) {   /* 长度异常, 放弃 */
            ctx->state = RX_SOF;
            break;
        }
        ctx->pos = 0;
        ctx->crc = 0;
        ctx->state = RX_DATA;
        break;
    case RX_DATA:
        ctx->buf[ctx->pos++] = byte;
        ctx->crc = crc8_update(ctx->crc, byte);
        if (ctx->pos >= ctx->len) ctx->state = RX_CRC;
        break;
    case RX_CRC:
        if (ctx->crc == byte) {
            process_frame(ctx->buf, ctx->len);  /* 完整一帧 */
        }
        ctx->state = RX_SOF;  /* 任何情况下都回到 SOF */
        break;
    }
}
```

### 关键规则

1. **SOF 必须唯一**：选一个数据里几乎不可能出现的字节（0xAA 0x55 是常见选择）。
2. **长度字段做边界检查**：`len > buf_size` → 直接回 SOF，不读 DATA。
3. **任何状态遇错**（CRC 错、长度越界、超时）→ 强制回 SOF，**不要在当前状态继续硬扛**。
4. **`static` 状态变量** = 单接收口；多口用结构体（`rx_ctx_t`）每个口一份。

### 文本协议简化版（AT 命令、NMEA）

```c
void line_rx_byte(rx_ctx_t *ctx, uint8_t byte) {
    if (byte == '\n') {
        process_line(ctx->buf, ctx->pos);
        ctx->pos = 0;
    } else if (byte != '\r' && ctx->pos < sizeof(ctx->buf)) {
        ctx->buf[ctx->pos++] = byte;
    }
}
```

文本协议用 `\r\n` 分帧，**没有 SOF**——靠"行尾"定界。风险是数据里出现裸 `\n`，所以推荐用 **SOF+LEN+CRC** 形式。

## 模式库 2：L2 TCP 半包/沾包（Modbus TCP）

**来源**：`bus/ethernet-deep-dive.md` §TCP 粘包和半包 + `bus/ethernet-modbus-tcp-practical.md` + `bus/modbus-tcp-deep-dive.md`。

### 现象

```text
一次 recv 收到半个 MBAP 帧（半包）
一次 recv 收到多个 MBAP 帧（沾包）
一次 recv 收到一个半 MBAP 帧（半 + 沾混合）
```

不是 TCP 的错。**TCP 是字节流，没消息边界**——跟 UART 一模一样。

### 解决方案：MBAP Length 驱动的状态机

MBAP Header（7 字节）：

```text
| Transaction ID (2B) | Protocol ID (2B) | Length (2B) | Unit ID (1B) |
```

其中 `Length` 字段 = **Unit ID 之后的所有字节数**（Function + Data）。这是分帧的唯一依据。

```c
typedef enum {
    MBAP_TID_H, MBAP_TID_L,     /* Transaction ID */
    MBAP_PID_H, MBAP_PID_L,     /* Protocol ID, 必须 0x00 */
    MBAP_LEN_H, MBAP_LEN_L,     /* Length 字段 */
    MBAP_UID,                    /* Unit ID */
    MBAP_FUNC,                   /* Function Code */
    MBAP_DATA,                   /* Length-2 字节数据 */
} mbap_state_t;

typedef struct {
    mbap_state_t state;
    uint16_t     len;            /* 从 MBAP_LEN 解析得到 */
    uint16_t     pos;            /* 已收 DATA 字节数 */
    uint8_t      buf[260];       /* MBAP + Function + Data + CRC */
} mbap_ctx_t;

void mbap_rx_byte(mbap_ctx_t *ctx, uint8_t byte) {
    switch (ctx->state) {
    case MBAP_TID_H: ctx->buf[0] = byte; ctx->state = MBAP_TID_L; break;
    case MBAP_TID_L: ctx->buf[1] = byte; ctx->state = MBAP_PID_H; break;
    case MBAP_PID_H:
        if (byte != 0x00) { ctx->state = MBAP_TID_H; break; }  /* 协议错, 重置 */
        ctx->buf[2] = byte; ctx->state = MBAP_PID_L; break;
    case MBAP_PID_L:
        ctx->buf[3] = byte; ctx->state = MBAP_LEN_H; break;
    case MBAP_LEN_H: ctx->len = ((uint16_t)byte) << 8; ctx->state = MBAP_LEN_L; break;
    case MBAP_LEN_L:
        ctx->len |= byte;
        if (ctx->len < 2 || ctx->len > sizeof(ctx->buf) - 6) {
            ctx->state = MBAP_TID_H; break;  /* 长度异常, 重置 */
        }
        ctx->buf[4] = (ctx->len >> 8) & 0xFF;
        ctx->buf[5] = ctx->len & 0xFF;
        ctx->pos = 0;
        ctx->state = MBAP_UID;
        break;
    case MBAP_UID:
        ctx->buf[6] = byte;
        ctx->state = MBAP_FUNC;
        ctx->len -= 2;   /* 减 Unit ID + Function */
        break;
    case MBAP_FUNC:
        ctx->buf[7] = byte;
        if (ctx->len == 0) goto frame_done;
        ctx->state = MBAP_DATA;
        break;
    case MBAP_DATA:
        ctx->buf[8 + ctx->pos++] = byte;
        if (ctx->pos >= ctx->len) goto frame_done;
        break;
    }
    return;

frame_done:
    process_mbap(ctx->buf, ctx->len + 8);  /* buf[0..7+len] */
    ctx->state = MBAP_TID_H;                /* 等下一帧 */
}
```

### 关键规则

1. **TCP 上一个 ctx 一个 socket**——多客户端 = 多个 `mbap_ctx_t`。
2. **必须在 `recv` 循环里反复喂字节**给状态机，直到 ctx 回到 `MBAP_TID_H` 才说明"一帧"处理完。
3. **沾包自然解决**：一帧处理完后 ctx 回到 `MBAP_TID_H`，下一次 `recv` 拿到的字节会接着解析下一帧。
4. **半包自然解决**：ctx 状态停在 `MBAP_DATA`，下次 `recv` 续喂即可。
5. **长度合法性必查**：`len < 2`（至少 Func + UnitID 之后的 0 数据）或 `len > buf_size` 都要重置。

## 模式库 3：L3 多包流控重组（J1939 TP）

**来源**：`bus/j1939-transport-protocol.md`。

CAN 经典帧只能传 8 字节，> 8 字节的数据必须拆成多帧（TP，Transport Protocol）。这相当于"在帧流之上又叠了一层字节流"，所以有了**二级 PSM**：

- **外层 PSM**（TP 会话状态机）：Idle / Waiting-CTS / Sending / Receiving / Aborted
- **内层 PSM**（每包内的 8 字节解析）：控制字节 / 长度 / 包号

### TP 会话状态机（外层）

```text
            ┌──────────┐
            │   IDLE   │  无会话
            └────┬─────┘
                 │ 收 RTS / 启动发送
                 ▼
       ┌───────────────────┐
       │ WAITING_CTS       │  发送方等 CTS
       │ (T1=750ms 超时)   │  接收方等 DT
       └────┬─────────┬────┘
            │         │
   收 CTS   │         │  收 DT (num++/全部收完)
            ▼         ▼
       ┌─────────┐  ┌─────────────┐
       │SENDING  │  │RECEIVING    │
       │  DT     │  │  DT,重组数据│
       └────┬────┘  └─────┬───────┘
            │             │
            └──────┬──────┘
                   │ 全部包 ACK / EndOfMsgAck
                   ▼
              ┌─────────┐
              │  IDLE   │  (或 Conn_Abort → IDLE)
              └─────────┘
```

### 4 类超时

| 超时 | 含义 | 默认 | 触发方 |
| --- | --- | --- | --- |
| T1 | RTS → CTS | 750 ms | 发送方重发 RTS（最多 3 次） |
| T2 | CTS → DT | 50 ms | 接收方发 Conn_Abort |
| T3 | DT 包之间间隔 | 200 ms | 接收方发 Conn_Abort |
| T4 | 整个 TP 会话总时间 | 1050 ms | 任一方发 Conn_Abort |

### 接收 DT 重组（内层 PSM）

```c
void tp_rx_dt_handler(uint8_t src_addr, uint8_t *dt_data) {
    /* 1. 会话合法性检查 */
    if (!tp_session_active || tp_session.src_addr != src_addr) return;

    /* 2. 包号连续性检查（错位 = 重组失败）*/
    uint8_t packet_num = dt_data[0];
    if (packet_num != tp_session.next_packet) {
        tp_session_abort();  /* 发 Conn_Abort, 回 IDLE */
        return;
    }

    /* 3. 按包号偏移写入重组缓冲（每包 7 字节数据 + 1 字节包号）*/
    uint16_t offset = (uint16_t)(packet_num - 1) * 7;
    memcpy(&tp_session.buffer[offset], &dt_data[1], 7);
    tp_session.received_bytes = offset + 7;
    if (tp_session.received_bytes > tp_session.total_bytes) {
        tp_session.received_bytes = tp_session.total_bytes;  /* 最后一包裁剪 */
    }
    tp_session.next_packet++;

    /* 4. 全部收完 / 等下一批 */
    if (tp_session.next_packet > tp_session.num_packets) {
        tp_send_endofmsgack(src_addr);
        process_tp_message(tp_session.pgn, tp_session.buffer, tp_session.total_bytes);
        tp_session_active = false;  /* 回 IDLE */
    } else {
        tp_send_cts(src_addr, tp_session.next_packet);  /* 续发 CTS */
    }
}
```

### 关键规则

1. **T1/T2/T3/T4 四个定时器必须全开**——只开 T1 会在 CTS→DT 阶段死锁。
2. **包号从 1 开始**（不是 0），`next_packet` 严格递增，不连续就 Abort。
3. **最后一包可能不足 7 字节**——按 `received_bytes > total_bytes` 时裁剪。
4. **同时只允许一个 TP 会话**——新 RTS 来时如果 `tp_session_active` 已置位，发 Conn_Abort。
5. **Conn_Abort 任一方都可发**——协议错、超时、buffer 满、应用层要求终止。

## 模式库对比

| 维度 | L1 UART 5 状态机 | L2 TCP MBAP 状态机 | L3 J1939 TP 二级 PSM |
| --- | --- | --- | --- |
| 物理 | UART 字节流 | TCP 字节流 | CAN 8B 帧流 |
| 边界 | SOF+LEN+CRC | MBAP Length 字段 | RTS/CTS 协议 |
| 半包 | ✓（状态停在 RX_DATA） | ✓（状态停在 MBAP_DATA） | ✓（DT 包序号） |
| 沾包 | ✓（回 SOF 后续接） | ✓（回 MBAP_TID_H 续接） | ✗（TP 内每包独立） |
| 错帧 | CRC 错 / 长度越界 | Length 越界 / PID 错 | 包号错 / Abort |
| 超时 | 通常不需要 | TCP keepalive | T1/T2/T3/T4 必开 |
| 重传 | 否（应用层） | TCP 自动 | T1 重发 RTS，最多 3 次 |
| 缓冲 | 1 帧缓冲 | 1 帧缓冲 | **多帧重组缓冲** |
| 多客户端 | N/A | 每 socket 一 ctx | 同一总线，PGN 区分 |

## 通用设计清单

无论哪个层级，下面 7 件事必须做到：

1. **状态机有穷 + 必含 IDLE**——任何异常都能"回家"。
2. **长度字段必做边界检查**——`len > buf_size` 一律重置。
3. **CRC 必校验**——`len` 字段不可信（噪声可能产生任何值）。
4. **SOF 字节必须唯一**——选数据中几乎不出现的值。
5. **ctx 不可全局 static**——多客户端 / 多口必须结构体化。
6. **异常计数器要暴露**——`rx_crc_err / rx_overrun / rx_abort` 上报便于产线排障。
7. **"读完一帧"必须让 ctx 回到 IDLE**——不要让状态停在"半个 frame"等下次喂字节。

## 实战代码位置

- **UART 5 状态机完整代码**：`basic/uart-failure-cases.md` 案例 7（行 289-365）
- **UART Ring Buffer + DMA + Idle**：`basic/uart-dma-circular-and-rtos.md` §1-3
- **Modbus TCP 状态机**：`bus/modbus-tcp-deep-dive.md` §MBAP + `bus/ethernet-modbus-tcp-practical.md` §解析
- **J1939 TP 完整代码**：`bus/j1939-transport-protocol.md` §完整 RTS/CTS 示例 + §超时和重传
- **DRIVER_PATTERNS TCP 解析器 6 必修**：`bus/DRIVER_PATTERNS.md` §Ethernet TCP Server（行 132-154）

## 一句话总结

**UART 是字节流，TCP 是字节流，CAN 是帧流——都不天然携带消息边界。任何"流式协议"都必须用 PSM：5 状态机（UART） → MBAP 状态机（TCP） → TP 二级 PSM（CAN）三档复杂度，覆盖从最薄的字节流到最厚的多包流控。**

## 更新记录

- 2026-08-23：初版，从 `uart-failure-cases.md` 案例 7 + `ethernet-modbus-tcp-practical.md` + `j1939-transport-protocol.md` 反向抽象而成。
