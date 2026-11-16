# ISO-TP 产线死机案例库

## 目标

把产线常见的 ISO-TP 多帧传输失败写成案例库。每个案例：

- 现象（现场）
- 抓包分析（判断）
- 定位（根因）
- 修复（代码 / 配置）
- 复盘（如何预防）

ISO-TP（ISO 15765-2）是 UDS 和 OBD-II 的公共传输底座。**单帧通、多帧不通**是这类故障最典型的特征，排查时不要一上来就怀疑 UDS 层。

## 案例 1: 单帧服务正常，读取长 DID 永远无响应

### 现象

诊断工具读短 DID（如 `0xF190` VIN）完全正常。读长 DID（超过 7 字节）时工具转圈直到超时，ECU 侧日志只有一条 `10 03` 会话请求，没有任何后续记录。

### 抓包分析

抓包显示只有请求帧，没有 First Frame：

```text
Tester -> ECU  0x7E8  02 22 F1 90      (Single Frame, 3 bytes payload)
ECU   -> Tester 0x7E8  06 62 F1 90 56 31 ...
```

长 DID 的请求根本没发出去。

### 定位

工具侧 ISO-TP 发送模块对长度判断用了 `> 8` 而不是 `> 7`。

经典 CAN 单帧最大数据载荷是 **8 字节**，但 ISO-TP 的 Single Frame 还要占用 **1 字节做 PCI**：

```text
SF 格式: [PCI][data...]
PCI 0x0N = 单帧, N = 数据长度, 最大 7

8 字节 payload -> 放不进 SF -> 必须走 FF/CF 多帧
```

工具用 `payload_len > 8` 判断，单帧 8 字节时判为"可以单帧"，实际发出的是 8 字节 SF。ECU 按 ISO-TP 解析，第 8 字节本应是 PCI，结果被当成数据 → 解析错误 → 静默丢弃。

### 修复

```c
/* 错误 */
if (payload_len > 8) {
    use_multiframe = true;
}

/* 正确: SF 最多带 7 字节数据 */
#define ISO_TP_SF_MAX_DATA   7
#define ISO_TP_FF_MAX_DATA   6   /* FF: 2 bytes PCI + 6 bytes data */

if (payload_len > ISO_TP_SF_MAX_DATA) {
    use_multiframe = true;
}
```

### 复盘

- Single Frame 的 7 字节上限是 ISO-TP 最容易搞错的边界值。
- **自测项**：构造 7 字节和 8 字节两种长度的请求各发一次，确认都走对路径。
- 工具和 ECU 两侧都要有这条断言，不要只靠工具侧。

## 案例 2: FF 发出去后 ECU 不回 Flow Control

### 现象

发送长数据，First Frame 发出后 ECU 毫无反应，没有 Flow Control。工具报"等待 FC 超时"。

### 抓包分析

```text
Tester -> ECU  0x7E8  10 14 01 00 00 00 00 00 00   (FF, 长度=0x0114=276)
(无后续帧)
```

ECU 收到了 FF，但没发 FC。

### 定位

三个可能，逐个排除：

**A. FF 的 CAN ID 用错（最常见）**

ISO-TP 的 FF 用**请求 ID**发，但 FC（接收方回）用**响应 ID**发。工具实现时把 FC 也发到请求 ID，ECU 的接收过滤器只认请求 ID，FC 根本进不了 ECU。

```text
Tester -> ECU   请求 ID (0x7E8)   FF / CF
ECU   -> Tester 响应 ID (0x7E8 另一对) FC
```

**B. 接收缓冲区不够**

ECU 收到 FF 后，声明长度 276 字节，但接收缓冲区只配了 256 字节。ECU 选择**不回 FC**（连 FC_OVFLW 都不发，直接放弃）。

**C. 长度字段解析错误**

FF 的长度是跨 2 字节的：

```text
FF 格式:
  byte0: 0x1X   (X = 高 4 位长度)
  byte1: XX XX  (低 8 位长度)
  byte2-7: 数据 (最多 6 字节)

总长度 = ((byte0 & 0x0F) << 8) | byte1
```

如果实现写成 `byte0 & 0xF0` 或只取 `byte1`，长度会算出完全不同的值。

### 修复

**A. ID 配对检查**

```c
typedef struct {
    uint32_t tx_id;      /* 我发的帧用这个 ID */
    uint32_t rx_id;      /* 收到的帧期望这个 ID */
} isotp_addr_t;

/* 发送 FC 时用 rx_id, 不是 tx_id */
isotp_send_flow_control(ctx, ctx->addr.rx_id, FC_CTS, bs, stmin);
```

**B. 缓冲区检查**

```c
/* FF 到达时先检查长度 */
uint16_t total = ff_total_length(ff);
if (total > ctx->rx_buf_size) {
    /* 发 FC_OVFLW (0x12) 明确告知对方溢出 */
    isotp_send_flow_control(ctx, ctx->addr.rx_id, FC_OVERFLOW, 0, 0);
    return ISO_TP_ERR_OVERFLOW;
}
```

**C. 长度解析**

```c
static uint16_t ff_total_length(const uint8_t *ff) {
    return (uint16_t)(((ff[0] & 0x0F) << 8) | ff[1]);
}
```

### 复盘

- ISO-TP 实现必须**同时**验证 FF 长度解析、缓冲区边界、TX/RX ID 配对三项，缺一项就会出现这个症状。
- 建议在收到 FF 时打一条日志：长度、可用缓冲区、期望 FC 的 CAN ID。这一条日志能省掉 80% 的排查时间。

## 案例 3: Flow Control 的 Block Size 理解反了

### 现象

ECU 发 FC 里 `BS = 0x10`（16），意思是"我每次让你发 16 个 CF"。工具实现按"我发 16 个就停"处理，但实际发到第 16 个 CF 时 ECU 不再发新 FC，工具一直等 FC 直到超时。

### 抓包分析

```text
ECU -> Tester  0x7E8  30 00 00 10 00 00 00 00 00   (FC: CTS, BS=0x10, STmin=0)
Tester -> ECU  0x7E8  21 00 ... (CF #1)
...
Tester -> ECU  0x7E8  21 10 ... (CF #16)
(无新 FC, 工具超时)
```

### 定位

BS 语义有两个方向，容易搞反：

```text
接收方在 FC 里声明 BS = N:
  含义 = "你最多可以连续发 N 个 CF, 然后停下来等我下一个 FC"

发送方视角:
  发出第 N 个 CF 后, 必须停下来等下一个 FC
```

错误实现：

```c
/* 错误: 把 BS 当成"我发满 BS 个才发 FC" */
if (cf_count == bs) {
    send_flow_control();
}
```

正确实现：

```c
/* 正确: 发完 BS 个 CF 后停下等对方给下一个 FC */
if (cf_count >= bs) {
    state = WAIT_FC;
    cf_count = 0;
    /* 不要自己发 FC, 等对端发 */
    return;
}
```

另外 **BS = 0 是特例**，表示"无限制"（不限制连续 CF 数量），不是"一个都不能发"。

### 修复

```c
#define FC_BS_UNLIMITED  0x00

/* 发送端 */
if (fc_bs != FC_BS_UNLIMITED && cf_count >= fc_bs) {
    state = ISOTP_STATE_WAIT_FC;
    cf_count = 0;
    return;  /* 等对端 FC */
}

/* 接收端发 FC 时 */
uint8_t bs = (ctx->rx_buf_size > 256) ? 0x00 : 0x20;  /* 0 = 不限 */
```

### 复盘

- BS 是**接收方给发送方的额度**，方向搞反就会出现"发着发着卡住"。
- 特别确认 BS=0 的语义，漏处理会直接卡死。
- 工具侧和 ECU 侧都要按同一份语义实现，建议在协议文档里明确写"BS 是接收方声明的发送额度"。

## 案例 4: STmin 单位搞错，CF 发得太快被丢弃

### 现象

ECU 发 FC 时 `STmin = 0x0A`（10）。按规范 10 表示 10 ms。工具实现按"10 微秒"处理，CF 间隔远小于 ECU 的 Flash/环形缓冲处理能力，ECU 收到 CF 后缓冲区还没腾空，CF 被丢弃，最终超时。

### 抓包分析

```text
ECU -> Tester  0x7E8  30 00 00 0A 00 00 00 00 00   (STmin = 0x0A = 10 ms)
Tester -> ECU  0x7E8  21 00 ...   (间隔约 0.5 ms)
Tester -> ECU  0x7E8  21 01 ...
```

抓包工具显示 CF 间隔只有几百微秒，远小于声明的 10 ms。

### 定位

STmin 的编码规则：

| STmin 值 | 实际间隔 |
| --- | --- |
| 0x00 | 0 ms（无延时） |
| 0x01–0x7F | 1–127 ms |
| 0xF1–0xF9 | 100–900 μs |
| 0xFA | 6 μs |
| 0xFB | 7 μs |
| 0xFC | 8 μs |
| 0xFD | 9 μs |
| 0xFE | 10 μs |
| 0xFF | 11 μs |

工具把 `0x0A` 直接当"10 微秒"用了。

### 修复

```c
static uint32_t stmin_to_us(uint8_t stmin) {
    if (stmin <= 0x7F) {
        return (uint32_t)stmin * 1000u;      /* ms -> us */
    } else if (stmin >= 0xF1 && stmin <= 0xF9) {
        return (uint32_t)(stmin - 0xF0) * 100u;
    } else {
        switch (stmin) {
            case 0xFA: return 6;
            case 0xFB: return 7;
            case 0xFC: return 8;
            case 0xFD: return 9;
            case 0xFE: return 10;
            case 0xFF: return 11;
            default:   return 0;
        }
    }
}

/* 用硬件定时器或忙等, 不要用浮点 */
void isotp_wait_stmin(uint32_t us) {
    uint32_t start = tick_get_us();
    while ((tick_get_us() - start) < us) {
        /* 让出 CPU */
    }
}
```

### 复盘

- STmin 是**非线性的编码表**，不能用"值 × 单位"线性换算。
- 不要用浮点延时，用 tick 差值。
- 建议在 FC 解析后 log 出换算后的实际 μs 值，和抓包实测间隔对照。

## 案例 5: CF 序号跳号，数据错位

### 现象

ECU 收到的重组数据在第 20 字节左右开始错乱，后续全是乱码。抓包显示 CF 序号是 0,1,2,...,19,**21**,22,... 跳过了 20。

### 抓包分析

```text
Tester -> ECU  0x7E8  21 13 ...   (CF SN = 0x13 = 19)
Tester -> ECU  0x7E8  21 15 ...   (CF SN = 0x15 = 21, 跳过了 0x14 = 20)
```

SN 是 4 bit 循环的：`0x0F` 之后回到 `0x00`。

### 定位

两个原因：

**A. 发送端跳号**

发送端在发第 20 个 CF 前发生了一次发送失败（仲裁失败重发、邮箱满），重试后 SN 计数器没有回退到正确值，直接发了 SN=21。

**B. 接收端序号检查用了错误比较**

接收端做连续性检查时写成：

```c
/* 错误: SN 是 4 bit 循环, 不能用普通整数比较 */
if (sn != expected_sn + 1) {
    error();
}
```

SN 从 `0x0F` 回到 `0x00` 时，`0x00 != 0x0F + 1`，会误判为跳号。

### 修复

**A. 发送端保证 SN 原子性**

```c
/* 在发送成功的路径上推进 SN, 不要在发起发送时就推进 */
if (can_send_success) {
    ctx->cf_sn = (ctx->cf_sn + 1) & 0x0F;
}
```

**B. 接收端用 4 bit 环绕比较**

```c
static int sn_is_next(uint8_t sn, uint8_t expected) {
    return ((sn + 1) & 0x0F) == expected;
}

if (!sn_is_next(rx_sn, ctx->expected_sn)) {
    ctx->error_count++;
    /* 策略: 严格模式直接中止, 宽容模式重新同步 */
    isotp_abort_rx(ctx);
    return;
}
```

### 复盘

- **4 bit 环绕**是 ISO-TP 的经典陷阱，`0x0F → 0x00` 的合法跳变必须处理。
- SN 检查的错误计数要记录，出现"偶尔错位"时先看错误计数再猜。
- 发送端 SN 推进必须在确认发送成功后，否则重发会污染序号。

## 案例 6: FF 之后直接发 CF，跳过 FC

### 现象

某些自定义上位机发长数据时，FF 之后不等 FC，直接连续发 CF。ECU 收到 FF 后发出 FC，但上位机已经开始发 CF，导致帧冲突（Bit Error），双方都进 Error Passive。

### 抓包分析

```text
Tester -> ECU  0x7E8  10 14 01 ...  (FF)
ECU   -> Tester 0x7E8  30 00 00 20 ...  (FC)   <- 同时刻
Tester -> ECU  0x7E8  21 00 ...        (CF 抢在 FC 生效前)
(错误帧, 双方 TEC 上升)
```

### 定位

上位机实现假设"接收方不需要确认"，直接连续发。但 ISO-TP 标准流程是：

```text
Sender -> FF
Receiver -> FC (CTS)      <- 必须等
Sender -> CF #1..N        <- 收到 FC 后才发
```

即使 BS=0（不限数量），也**必须先收到 FC**才能发第一个 CF。

### 修复

发送端状态机必须严格：

```text
IDLE
  -> 发送 FF
  -> 等待 FC (状态 = WAIT_FC)
  -> 收到 FC(CTS) -> 发送 CF (状态 = SEND_CF)
  -> 发满 BS 个 CF -> 回到 WAIT_FC
  -> 全部发完 -> IDLE
```

```c
/* 绝不能在发送 FF 的同一个调用里接着发 CF */
case ISOTP_STATE_IDLE:
    if (tx_len > ISO_TP_SF_MAX_DATA) {
        isotp_send_ff(ctx);
        ctx->state = ISOTP_STATE_WAIT_FC;   /* 必须切状态 */
        break;                                /* 必须 break, 不能 fall through */
    }
    /* ... */
```

同时注意总线仲裁：FC 发送和 CF 发送在总线上可能撞车。**发送方在等 FC 期间不应该占用总线**。

### 复盘

- 状态机里"发了 FF 还要继续往下走"是经典 bug，必须显式 `break`。
- 上下位机自研协议时，容易把自己的时序当成标准。**用第三方 ISO-TP 库做对拍测试**。
- 抓包里看到 FC 和 CF 时间戳重叠，基本可以确定是这个问题。

## 案例 7: 寻址方式不一致，CAN ID 全对仍然无响应

### 现象

CAN ID 和数据都核对无误，请求帧 ECU 确实收到了，但 ECU 完全不回应。工具侧日志显示发送成功。

### 抓包分析

```text
Tester -> ECU  0x7E8  10 03              (Normal Addressing, 单帧)
(ECU 收到, 无任何响应)
```

但规范要求 **Extended Addressing**：

```text
Extended Addressing 格式:
  byte0: 0x10 | (len-1)     PCI, 长度 1..7
  byte1: 0x00 | (addr>>8)   地址高字节
  byte2: addr & 0xFF        地址低字节
  byte3..: 实际数据
```

### 定位

ISO-TP 有三种寻址方式，数据格式完全不同：

| 方式 | 单帧格式 |
| --- | --- |
| Normal | `[PCI][data...]` |
| Extended | `[PCI][addr_hi][addr_lo][data...]` |
| Mixed | `[PCI][addr_hi][addr_lo][data...]`（数据从 byte2 开始，但地址只占 2 byte 的高 12 bit） |

ECU 按 Extended 解析，收到 Normal 格式的单帧时，把 `byte1`（本应是地址高字节，实际是 `0x03`）当成地址的一部分 → 目标地址错 → 丢弃。

**CAN ID 正确不代表 ISO-TP 层正确** —— 这是分层排障的关键点。

### 修复

```c
typedef enum {
    ISOTP_ADDR_NORMAL = 0,
    ISOTP_ADDR_EXTENDED,
    ISOTP_ADDR_MIXED
} isotp_addr_mode_t;

/* Extended 寻址的单帧长度要减去 2 个地址字节 */
if (mode == ISOTP_ADDR_EXTENDED) {
    header_len = 2;
} else {
    header_len = 0;
}

if (payload_len - header_len <= ISO_TP_SF_MAX_DATA) {
    send_sf(ctx, payload_len - header_len, &payload[header_len]);
}
```

### 复盘

- **寻址方式是规范的一部分**，必须从 ECU 诊断规范确认，不能猜。
- 产线工具要支持三种寻址方式可配置，并在日志里打出当前模式。
- 排障顺序：CAN ID → 帧类型 → **寻址方式** → PCI → UDS。跳步就会卡在"ID 全对却不响应"。

## 案例 8: 接收缓冲区被写越界，长数据把 RAM 打穿

### 现象

ECU 在接收长数据（>4 KB）时发生 HardFault。复位后 RAM 内容被破坏，堆上的其他数据结构全部错乱。

### 抓包分析

FF 声明长度正常（0x1000 = 4096），CF 数量也对得上。抓包无异常。

### 定位

接收缓冲区实际只有 1024 字节，但 FF 长度检查用的是 `>` 而不是 `>=`，或者检查了但写 CF 时没重新校验：

```c
/* 错误: 只在 FF 时检查一次, 或检查逻辑漏了 */
if (ff_len > rx_buf_size) {   /* rx_buf_size = 1024, ff_len = 4096 */
    return;                    /* 这行如果漏掉就完蛋 */
}

/* 错误写法: 写入时用 ff_len 但不检查 */
memcpy(&ctx->rx_buf[ctx->rx_offset], cf_data, cf_len);
```

更隐蔽的一种：**FF 长度合法，但多帧重组累计偏移算错**。

```c
/* 错误 */
ctx->rx_offset += cf_len;   /* cf_len 包含了 PCI 字节! */
```

CF 的 8 字节里有 1 字节是 PCI（SN），实际数据只有 7 字节。如果把 8 字节都拷进去并累加偏移，累计 15% 的膨胀，缓冲区迟早被写穿。

### 修复

```c
/* 每个 CF 严格校验 */
#define CF_MAX_DATA  7
uint8_t cf_data_len = 8;

/* SF 帧: 8 字节全是数据 */
if (frame_type == ISOTP_FRAME_SF) {
    cf_data_len = pci_len;      /* PCI 里声明的长度 */
} else {
    cf_data_len = 7;             /* CF: 1 byte PCI + 7 bytes data */
}

/* 写入前边界检查 */
if (ctx->rx_offset + cf_data_len > ctx->rx_buf_size) {
    isotp_send_flow_control(ctx, ctx->addr.rx_id, FC_OVERFLOW, 0, 0);
    isotp_abort_rx(ctx);
    return;
}

memcpy(&ctx->rx_buf[ctx->rx_offset], &frame[1], cf_data_len);
ctx->rx_offset += cf_data_len;
```

### 复盘

- **SF 的 PCI 声明长度**和 **CF 的固定 7 字节**是两个不同的数据长度来源，最容易混。
- 缓冲区写入前必须做边界检查，不能只在 FF 阶段查一次。
- 建议加编译期断言：`rx_buf_size` 至少等于 `ISOTP_MAX_MESSAGE_LEN`。
- HardFault 现场务必开栈溢出检测和看门狗，把栈顶写进备份寄存器。

## 案例 9: FC 超时时间过短，总线繁忙时误判失败

### 现象

产线上 20 个节点同时进行诊断，总线利用率高。单节点测试正常，批量测试时偶发"等待 FC 超时"，重测又好了。

### 抓包分析

```text
Tester -> ECU  0x7E8  10 14 01 ...   (FF)
(busy, 延迟 ~80 ms 后)
ECU   -> Tester 0x7E8  30 00 00 20 ...  (FC, 延迟 80 ms)
```

ECU 的 FC 响应延迟超过了工具的等待阈值。

### 定位

ISO-TP 超时分层：

| 超时 | 含义 | 典型值 |
| --- | --- | --- |
| N_As / N_Ar | FF 后等待 FC | 25–75 ms |
| N_Bs / N_Cr | FC 后等待下一个 FC | 20–1000 ms |
| N_Cs | 收到 FC 后等待对端反应 | 5–20 ms |

工具把 N_As 设成了 50 ms，而 ECU 侧因为要抢占总线（大量高优先级报文）实际延迟 80 ms。

**注意**：ISO-TP 超时和 UDS 的 P2/P2* 是两套独立计时器。工具超短了不能靠调 UDS P2 解决。

### 修复

```c
/* 工具侧超时配置, 按实际总线负载留余量 */
#define ISOTP_N_AS_TIMEOUT_MS   1000   /* 等 FC */
#define ISOTP_N_BS_TIMEOUT_MS   1000   /* 等下一个 FC */
#define ISOTP_N_CS_TIMEOUT_MS     50   /* 等对端响应 */

/* ECU 侧如果 FC 响应可能延迟, 优先降低 FC 延迟而不是调大对端超时 */
```

实测做法：把总线负载拉到目标值再测超时余量，不要在空总线（分析仪单节点）上定超时。

### 复盘

- **在真实总线负载下定超时**，空载测出来的值在产线必然不够。
- ISO-TP 超时和 UDS 超时是两套，改错地方会白折腾。
- 批量测试偶发失败要往"总线负载"方向想，不要第一反应怀疑协议实现。

## 案例 10: 多帧响应时 ECU 侧把 FC 发到了自己的 TX ID

### 现象

ECU 读长 DID 返回多帧。ECU 发完 FF 后等待 FC，工具发了 FC 但 ECU 没收到，工具报超时。反过来，工具能收到 ECU 的 FF，但收不到后续 CF。

### 抓包分析

```text
ECU   -> Tester 0x7E0  10 14 01 ...   (FF, 发到 0x7E0)
Tester -> ECU   0x7E8  30 00 00 20 ... (FC, 发到 0x7E8)   <- 错！应发 0x7E0
(ECU 等 FC 超时)
```

### 定位

ECU 侧 ISO-TP 上下文把 `tx_id` 和 `rx_id` 用成了同一个值：

```c
/* 错误 */
ctx.tx_id = 0x7E0;   /* 我发 */
ctx.rx_id = 0x7E0;   /* 我收 —— 应该是 0x7E8 */
```

或者初始化时传反了参数：

```c
isotp_init(&ctx, tx_id, rx_id);
/* 调用方写成 */
isotp_init(&ctx, rx_id, tx_id);
```

**诊断协议里请求 ID 和响应 ID 通常成对且不对称**（如 0x7E8 ↔ 0x7E0），最容易传反。

### 修复

```c
typedef struct {
    uint32_t req_id;    /* 对端 -> 我 */
    uint32_t resp_id;   /* 我 -> 对端 */
} diag_addr_t;

/* 每次收发都用对的方向 */
isotp_send_ff(ctx, ctx->resp_id, ...);
isotp_send_cf(ctx, ctx->resp_id, ...);
isotp_expect_fc(ctx, ctx->req_id, ...);
```

建议在初始化后立刻做一次自检：发一个 Single Frame 并检查是否收到对端的 FC 或 ACK。

### 复盘

- **TX/RX ID 方向**是自研 ISO-TP 栈最高频的错误。
- 建议把 ID 配置做成"请求 ID / 响应 ID"两个具名字段，不要用 `tx_id`/`rx_id` 这种容易混淆的命名。
- 产线测试加一条"多帧双向回环"用例。

## 案例 11: 长时间运行后 ISO-TP 状态机泄漏，重启才恢复

### 现象

设备连续运行几天后，开始出现偶发的多帧失败。重启后恢复正常，但过几天又复现。内存占用缓慢增长。

### 抓包分析

抓包无明显异常，是间歇性失败。

### 定位

每次发起多帧传输时动态分配缓冲区，但异常路径（超时、Abort、FC_OVFLW）没有释放：

```c
/* 每次传输都 malloc */
void isotp_send_multi(...) {
    ctx->tx_buf = malloc(len);      /* 泄漏点 */
    ...
}

/* 超时路径 */
void isotp_timeout_handler(...) {
    isotp_reset(ctx);
    return;                          /* 忘记 free(tx_buf) */
}
```

也可能是在收到新的 FF 时没有先清理上一次未完成的传输，导致同一个指针被赋值两次（泄漏 + 悬垂指针）。

### 修复

```c
/* 统一的清理入口, 所有异常路径都走它 */
void isotp_abort_tx(isotp_ctx_t *ctx) {
    if (ctx->tx_buf) {
        free(ctx->tx_buf);
        ctx->tx_buf = NULL;
    }
    ctx->tx_len = 0;
    ctx->tx_sent = 0;
    ctx->state = ISOTP_STATE_IDLE;
}

/* 所有错误出口统一调用 */
#define ISOTP_FAIL(ctx, err) do { \
    isotp_abort_tx(ctx);            \
    return (err);                   \
} while (0)
```

另外：接收侧在收到新的 FF 时，先 `isotp_abort_rx()` 清理上一轮，再开始新的重组。

### 复盘

- 状态机的**所有出口**（成功、超时、错误、重入）都要走同一个清理函数。
- 建议加"传输计数 / 分配计数 / 释放计数"三个运行时计数器，泄漏能被计数差直接暴露。
- 长时间稳定性测试是嵌入式协议的必测项，短测发现不了这类问题。

## 案例 12: CAN FD 下用 ISO-TP，PCI 解析没考虑 BRS 位

### 现象

CAN 总线升级到 CAN FD 后，ISO-TP 单帧正常，但多帧（FF/CF）失败。经典 CAN 上的同一套代码完全正常。

### 抓包分析

```text
CAN FD 帧:
  CAN ID 0x7E8, DLC=15, flags: BRS=1, ESI=0
  Data: 10 14 01 00 00 00 00 00 00 ...
```

CAN FD 的 `DLC` 是**编码值**，不是实际字节数：

```text
DLC 9  -> 12 字节
DLC 10 -> 16 字节
DLC 11 -> 20 字节
DLC 12 -> 24 字节
DLC 13 -> 32 字节
DLC 14 -> 48 字节
DLC 15 -> 64 字节
```

### 定位

两个叠加问题：

**A. 按 DLC 当长度用**

```c
/* 错误: DLC=15 实际是 64 字节 */
uint8_t len = frame->dlc;
```

解析 PCI 时，FC 帧在 64 字节 CAN FD 帧里只有前 3 字节有效，剩下 61 字节是填充。某些实现按 `dlc` 取长度会越界读。

**B. 忽略 BRS（Bit Rate Switch）**

CAN FD 帧可能在仲裁段和数据段用不同速率。BRS=1 表示数据段切换到更高速率。如果 CAN 控制器的过滤器只按 CAN ID 配置，**而某些驱动在 BRS 帧上走了不同的接收 FIFO**，就会出现"帧收到了但没进我的 FIFO"。

**C. CAN FD 单帧可以带更多数据**

CAN FD 下 SF 的 PCI 编码扩展了：`0x00` 仍然表示 SF 长度 0..7，但 CAN FD 允许单帧超过 7 字节（用 FF + SF 逃逸序列 `0x00` + `0x00` 格式）。

### 修复

```c
/* DLC -> 实际字节数 */
static const uint8_t fdi_dlc_to_len[16] = {
    0,1,2,3,4,5,6,7,8,12,16,20,24,32,48,64
};
uint8_t real_len = fdi_dlc_to_len[frame->dlc];

/* CAN FD 逃逸序列: 0x00 0x00 表示后面是 CAN FD 单帧 */
if (frame->data[0] == 0x00 && frame->data[1] == 0x00) {
    uint8_t fd_sf_len = frame->data[2] & 0x7F;   /* bit7 = escape */
    payload = &frame->data[3];
    payload_len = fd_sf_len;
}
```

**B 的处理**：确认 CAN 控制器支持 BRS 帧接收，必要时为 FD 帧单独配置 FIFO 或放宽过滤器掩码。

### 复盘

- CAN FD + ISO-TP 组合要单独测，不能用经典 CAN 的用例覆盖。
- **DLC 是编码值不是长度**，这条在 CAN FD 调试里踩坑率极高。
- 升级到 CAN FD 时，CAN ID 分配和过滤器配置要一起复核。

## 根因清单

| 根因 | 典型症状 | 快速验证 |
| --- | --- | --- |
| SF 上限用 8 而不是 7 | 8 字节请求无响应 | 看抓包有没有发出 FF |
| TX/RX ID 方向反 | FF 后无 FC | 核对 CAN ID 对 |
| 寻址方式不匹配 | 完全无响应 | 核对寻址模式 |
| BS 语义反 | 发满 N 个 CF 卡住 | 看 FC 的 BS 值 |
| STmin 单位错 | CF 被丢弃 | 对比声明间隔与实测间隔 |
| SN 4bit 环绕 | 周期性数据错位 | 看 SN 序列 |
| PCI 长度解析错 | FC 长度字段异常 | 手工算 FF 长度 |
| 缓冲区越界 | HardFault | 查写入边界检查 |
| 超时过短 | 批量测试偶发失败 | 加载真实总线负载 |
| 异常路径不释放 | 长时间后失效 | 看内存增长曲线 |
| DLC 当长度用 | 仅 CAN FD 失败 | 查 DLC 编码表 |

## 关联主题

- `bus/iso-tp.md` — ISO-TP 定位、帧类型、关键参数
- `bus/iso-tp-deep-dive.md` — 寻址方式、PCI 编码、超时、缓冲区
- `bus/iso-tp-practical.md` — 调试流程与检查清单
- `bus/uds-failure-cases.md` — UDS 层案例（ISO-TP 正常但 NRC 的场景）
- `bus/uds-deep-dive.md` — UDS 与传输层的分层边界
- `basic/can-failure-cases.md` — CAN 物理层/链路层案例
- `bus/can-protocol-family.md` — CAN 家族全景

## 更新记录

- 2026-10-31: 初版，12 个产线案例。覆盖 SF 长度边界、TX/RX ID 方向、寻址方式、BS 语义、STmin 编码、SN 环绕、缓冲区越界、超时分层、状态机泄漏、CAN FD DLC 编码等高频坑。
