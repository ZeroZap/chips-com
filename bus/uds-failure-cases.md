# UDS 产线死机案例库

## 目标

把产线常见的 UDS 诊断失败、权限错乱、刷写变砖写成案例库。每个案例：

- 现象（现场）
- 抓包分析（判断）
- 定位（根因）
- 修复（代码 / 配置）
- 复盘（如何预防）

UDS 排障的第一原则：**分层定位**。CAN 层、ISO-TP 层、UDS 层、ECU 业务层的问题不要混在一起看。

## 案例 1: 单帧服务正常，长 DID 读取无响应

### 现象

诊断工具读短 DID（`0xF190` VIN）完全正常。读长 DID（如 `0xF186`  Active Diagnostic Session 或长配置块）永远超时。

### 抓包分析

```text
Tester -> ECU  0x7E8  03 22 F1 90        (SF, 短 DID 正常)
ECU   -> Tester 0x7E8  06 62 F1 90 ...   (正常响应)

Tester -> ECU  0x7E8  03 22 F1 86        (SF, 3 字节 payload)
ECU   -> Tester (无响应)
```

注意：长 DID 的请求**根本没变成多帧**。短 DID 是 3 字节 payload，能塞进 SF；长 DID 同样只发 3 字节（只是 DID 本身是 2 字节），响应才是长的。

### 定位

请求确实是短 DID，**问题在响应侧**。ECU 需要返回超过 7 字节的数据，必须走 FF/CF/FC 多帧。

ECU 的多帧发送实现有缺陷：发完 FF 后等待 FC，但 FC 用错了 CAN ID（发到了自己的 TX ID 而非请求 ID），或者 FC 之后没有正确发送 CF。

### 修复

参照 `bus/iso-tp-failure-cases.md` 案例 2 和案例 10。核心是：

```c
/* ECU 侧: 发 FC 必须用接收方的 ID (请求 ID) */
isotp_send_flow_control(ctx, ctx->req_id, FC_CTS, bs, stmin);
```

**排查顺序**：看到"单帧通多帧不通"先确认是**哪一侧**的多帧有问题 —— 看抓包有没有 FF。有 FF 没 FC = ECU 侧问题；有 FC 没 CF = 发送侧问题。

### 复盘

- "长 DID 读不到"是 ISO-TP 问题还是 UDS 问题，要看 FF 有没有发出去。
- 产线测试要同时覆盖"短请求短响应"和"短请求长响应"两种形态。

## 案例 2: 进入扩展会话后所有服务返回 NRC 0x7F

### 现象

发送 `10 03`（进入扩展会话）成功，响应 `50 03`。随后发任何服务都返回 `7F <SID> 7F`（服务不支持）。

### 抓包分析

```text
Tester -> ECU  0x7E8  02 10 03
ECU   -> Tester 0x7E8  03 50 03 00 32 01 F4
Tester -> ECU  0x7E8  02 22 F1 90
ECU   -> Tester 0x7E8  03 7F 22 7F
```

### 定位

`0x7F` 是 **Service Not Supported**。但同一个服务在默认会话下是能用的，所以不是真的不支持。

常见根因：**服务分发表是按会话索引的，进入扩展会话后索引指向了空表项**。

```c
/* 错误: 扩展会话下服务表指针没切换 */
typedef struct {
    const u8 *session_services[3];   /* [0]=default [1]=extended [2]=programming */
    u8 current_session;
} diag_ctx_t;

u8 lookup_service(diag_ctx_t *c, u8 sid) {
    const u8 *tbl = c->session_services[0];   /* 写死了 [0], 没用 current_session */
    ...
}
```

另一种根因：会话状态变量被复位。`10 03` 处理完把 `current_session` 写成 0，或者会话结构体定义在栈上/被栈上的其他变量覆盖。

### 修复

```c
const u8 *lookup_service(diag_ctx_t *c, u8 sid) {
    if (c->current_session >= SESSION_COUNT) {
        return NULL;
    }
    const u8 *tbl = c->session_services[c->current_session];
    for (u32 i = 0; tbl[i] != 0xFF; i++) {
        if (tbl[i] == sid) return &tbl[i];
    }
    return NULL;
}
```

会话变量必须是 `static` 或挂在上下文结构体上，**不能是局部变量**。

### 复盘

- 服务表按会话索引是标准做法，实现时必须用 `current_session` 而不是写死。
- **负响应 NRC 0x7F 在"某些会话下出现"时，要先怀疑会话状态，而不是服务实现**。
- 建议每个会话都跑一遍全服务遍历测试。

## 案例 3: 写 DID 返回成功，但重启后数据丢失

### 现象

用 `2E` 写配置 DID，ECU 返回 `6E`（正响应），显示写入成功。重启设备后配置恢复成旧值。

### 抓包分析

```text
Tester -> ECU  0x7E8  08 2E F1 99 01 02 03 04
ECU   -> Tester 0x7E8  02 6E F1 99
```

抓包完全正常，无任何异常。

### 定位

响应 `6E F1 99` 只表示"数据已接收并通过校验"，**不表示已落盘**。

常见根因是写 DID 时只改了 RAM 镜像，没写非易失存储：

```c
/* 错误: 只改 RAM, 没写 Flash/EEPROM */
int did_f199_write(diag_ctx_t *c, const u8 *data, u8 len) {
    memcpy(c->config.f199, data, len);
    return DID_OK;    /* 直接返回成功! */
}
```

另一种根因：写入了 Flash 但**没等写完成**就返回正响应。NOR Flash 编程期间读回的是旧值，此时读回校验必然失败，但代码忽略了校验失败仍然返回成功。

### 修复

```c
int did_f199_write(diag_ctx_t *c, const u8 *data, u8 len) {
    /* 1. 参数校验 */
    if (len != 4) return DID_ERR_LENGTH;

    /* 2. 写 RAM 镜像 */
    memcpy(c->config.f199, data, len);

    /* 3. 写 NVM, 必须阻塞等待完成并读回校验 */
    if (nvm_write(CONFIG_F199_OFFSET, data, len) != NVM_OK) {
        memcpy(c->config.f199, c->config.f199_backup, len);  /* 回滚 */
        return DID_ERR_NVM;
    }

    /* 4. 读回校验 */
    u8 verify[4];
    nvm_read(CONFIG_F199_OFFSET, verify, 4);
    if (memcmp(verify, data, 4) != 0) {
        return DID_ERR_VERIFY;
    }

    return DID_OK;   /* 只有真正落盘后才返回成功 */
}
```

**关键**：NVM 写入必须同步等待完成。异步写入时，DID 服务要返回 `0x78 Response Pending`，等写完再给最终响应。

### 复盘

- **`6E` 只代表接收成功，不代表落盘成功** —— 这条要在团队内统一认知。
- 所有写 DID 的服务都要有"写入 + 读回校验"两步。
- NVM 写入耗时超过 P2 时，必须走 Response Pending 流程。
- 产线测试要有"写 DID → 断电重启 → 读回比对"用例。

## 案例 4: Security Access 种子密钥偶发失败

### 现象

产线用固定 Key 解锁，绝大多数成功，偶发返回 `7F 27 35`（Invalid Key）。重试一次又好了。

### 抓包分析

```text
Tester -> ECU  0x7E8  02 27 01
ECU   -> Tester 0x7E8  06 67 01 A3 F1 2C 88 09
Tester -> ECU  0x7E8  06 27 02 <key>
ECU   -> Tester 0x7E8  03 7F 27 35
```

失败的几次里，对比 Seed 和 Key 的关系发现：**同样的 Key 对不同的 Seed 计算结果应该不同**，但工具在某些情况下复用了旧的 Key。

### 定位

工具端的问题：种子密钥算法实现有缓存或复用。

更常见的一种是**端序问题**：Seed 是多字节的，算法规定按大端还是小端参与运算，实现搞反时，**大部分 Seed 恰好也能算对**（因为某些 Seed 的字节有对称性），只在特定 Seed 值下失败。

另一种根因在 ECU 侧：Seed 缓冲区在发出后被覆盖（比如异步任务里又写了一次），而工具是拿**收到的 Seed** 算的 Key，ECU 校验时却用了**内存里被覆盖后的新 Seed**。

```c
/* 错误: 发出 seed 后, 缓冲区被其他代码覆盖 */
void send_seed(diag_ctx_t *c) {
    c->seed[0] = hw_rng();
    c->seed[1] = hw_rng();
    can_send(0x7E8, 0x67, 0x01, c->seed, 4);
    /* c->seed 之后没保护, 可能被中断或其他服务改掉 */
}
```

### 修复

**ECU 侧**：发出 Seed 后锁定缓冲区，直到收到对应 Key 才解锁。

```c
/* 用状态机保护 seed */
typedef enum { SEED_IDLE, SEED_ISSUED, SEED_KEYED } seed_state_t;

if (c->seed_state == SEED_IDLE) {
    fill_rng(c->seed, 4);
    c->seed_state = SEED_ISSUED;
    send_seed(c);
    return;
}

/* 收到 Key 时: 用当前 seed 校验, 校验后立即清除 */
if (c->seed_state == SEED_ISSUED) {
    int ok = verify_key(c->seed, key);
    wipe(c->seed, 4);              /* 用完即焚 */
    c->seed_state = SEED_IDLE;
    return ok ? OK : NRC_INVALID_KEY;
}
```

**工具侧**：端序和拼接必须严格按 ECU 规范文档实现，并写单元测试覆盖全部 256 个单字节 Seed 值。

### 复盘

- 种子密钥"偶发失败"通常是**边界值触发**，不是随机性问题。用全 Seed 空间遍历测试能一次定位。
- Seed 发出后必须锁定，用完立即清除。
- 种子密钥算法要版本化，算法版本和固件版本绑定。

## 案例 5: 安全访问尝试次数超限后永久锁死

### 现象

调试时连续输错几次 Key，之后即使输对也一直返回 `7F 27 37`（Required Time Delay Not Expired），等了很久也不恢复。

### 抓包分析

```text
(前几次 27 02 <wrong key>)
ECU   -> Tester 0x7E8  03 7F 27 35   (Invalid Key)
...
ECU   -> Tester 0x7E8  03 7F 27 36   (Exceed Number Of Attempts)
(等待 30 分钟后仍然)
ECU   -> Tester 0x7E8  03 7F 27 37   (Required Time Delay)
```

### 定位

延时计时器实现有问题，常见两种：

**A. 用 `while` 忙等，导致时间基准错乱**

```c
/* 错误: 忙等期间系统 tick 仍在走, 但复位延时计算用的是被延长后的时间 */
```

**B. 延时状态只在 RAM，ECU 复位后丢失 —— 但反过来更糟：有些实现把延时状态持久化到 Flash，每次读取都做 Flash 擦写，Flash 磨损且逻辑混乱。**

真正的问题通常是：**延时到期判断用了单调递增计数，但计数器在延时期间被其他代码复位**（比如另一个服务流程调用了状态机重置函数）。

### 修复

用单调时钟 + 绝对到期时间点：

```c
typedef struct {
    u8 state;            /* LOCKED / SEED_ISSUED / UNLOCKED / DELAY_ACTIVE */
    u8 attempt_count;
    uint32_t delay_until_ms;   /* 绝对到期时刻 */
} sec_ctx_t;

#define SEC_MAX_ATTEMPTS  5
#define SEC_DELAY_MS      30000

int sec_check_delay(sec_ctx_t *c) {
    if (c->state != DELAY_ACTIVE) return 0;
    if (tick_get_ms() >= c->delay_until_ms) {
        c->state = LOCKED;
        c->attempt_count = 0;
        return 0;                       /* 延时结束 */
    }
    return 1;                           /* 仍在延时 */
}

void sec_on_bad_key(sec_ctx_t *c) {
    c->attempt_count++;
    if (c->attempt_count >= SEC_MAX_ATTEMPTS) {
        c->state = DELAY_ACTIVE;
        c->delay_until_ms = tick_get_ms() + SEC_DELAY_MS;
    }
}
```

**关键**：所有会重置安全状态的路径（会话切换、ECU Reset）都要明确决策 —— 是保留延时（更安全）还是清除（更好用）。

### 复盘

- 延时状态机必须用**绝对到期时间**而不是相对累加。
- 产线调试要提供"安全访问解锁"的工程旁路机制（编译期开关 + 量产关闭），否则调试一次锁死一台设备。
- 尝试次数、延时时长、断电是否保持，都要在诊断规范里写清楚。

## 案例 6: 刷写过程中 ECU 断电，设备变砖

### 现象

刷写固件到 60% 时产线工装断电。重新上电后 ECU 无法启动，也无法进入诊断会话 —— 设备变砖。

### 抓包分析

```text
(刷写中断时的最后几帧)
Tester -> ECU  0x7E8  10 14 01 ...  (Transfer Data block N)
(断电)
```

重新上电后：

```text
Tester -> ECU  0x7E8  02 10 03
(无任何响应)
```

### 定位

Bootloader 在擦除 Application 区之前，**没有把"待写入的固件"保存到任何持久化位置**。擦除完成后断电，Application 区是空的，Bootloader 跳转到空区 → HardFault → 死循环。

更隐蔽的一种：Bootloader 有"启动失败自动回退"逻辑，但回退的镜像**从未下载过**（旧版本在第一次刷写时就已被擦除）。

### 修复

**A/B 分区 + 原子切换**

```text
Flash 布局:
  Slot A:  当前运行的应用
  Slot B:  正在写入的新应用
  Meta:    切换元数据 (独立扇区, 双备份)

流程:
  1. Request Download 声明写入 Slot B
  2. Transfer Data 全部写入 Slot B
  3. Request Transfer Exit
  4. 校验 Slot B (CRC + 签名)
  5. 写 Meta: pending_slot = B, state = TRYING   (原子写, 双备份)
  6. ECU Reset
  7. 从 B 启动, 自检通过 -> 写 Meta: state = CONFIRMED
  8. 自检失败 / 启动失败 -> 回退到 A
```

**B. 元数据写入必须原子**

```c
/* 双备份 + 校验: 写 A 失败还能从 B 恢复 */
typedef struct {
    u32 magic;
    u8  state;          /* IDLE / TRYING / CONFIRMED */
    u8  active_slot;
    u16 crc;
} boot_meta_t;

int meta_write(const boot_meta_t *m) {
    boot_meta_t tmp = *m;
    tmp.crc = crc16((u8*)&tmp, sizeof(tmp) - 2);
    return nvm_write(META_SLOT_A, &tmp, sizeof(tmp));
}

int meta_read(boot_meta_t *out) {
    if (nvm_read(META_SLOT_A, out, sizeof(*out)) == NVM_OK &&
        out->crc == crc16((u8*)out, sizeof(*out) - 2)) {
        return META_OK;
    }
    if (nvm_read(META_SLOT_B, out, sizeof(*out)) == NVM_OK &&
        out->crc == crc16((u8*)out, sizeof(*out) - 2)) {
        return META_OK;
    }
    return META_ERR;
}
```

**C. Bootloader 启动时必须有兜底**

```c
void bootloader_main(void) {
    boot_meta_t meta;
    if (meta_read(&meta) != META_OK) {
        /* 元数据坏了, 尝试启动已 CONFIRMED 的槽 */
        goto try_rollback;
    }

    if (meta.state == TRYING) {
        /* 上次没走完, 启动带计数保护的镜像 */
        if (!boot_slot_valid(meta.active_slot)) {
            goto try_rollback;
        }
        if (boot_slot_try_count(meta.active_slot) >= MAX_TRIES) {
            goto try_rollback;
        }
        boot_try_count_inc(meta.active_slot);
    }

    boot_jump(meta.active_slot);

try_rollback:
    boot_jump(other_slot);
}
```

### 复盘

- **刷写场景必须按"随时可能断电"设计**，不能假设流程能走完。
- "先擦除再下载"是变砖的根源 —— 应该"先下载到备用区，校验通过再切换"。
- 元数据要双备份 + CRC，启动计数要限制重试次数防止无限回退循环。
- 产线必须有"刷写中断"专项测试：在每个阶段随机断电，验证设备始终可恢复。

## 案例 7: Transfer Data 序号不连续被拒，刷写反复重试

### 现象

刷写大固件，前几十个块正常，第 200 块左右开始返回 `7F 36 13`（长度或格式错误）。工具重试该块仍失败。

### 抓包分析

```text
Tester -> ECU  0x7E8  10 14 03 ...  (Transfer Data, block counter = 0xC8)
ECU   -> Tester 0x7E8  03 7F 36 13
```

对比前后：
```text
前一块: ... 14 00 ...
本块:   ... 14 03 ...
```

### 定位

**Transfer Data 的块序号（Block Sequence Counter, BSC）必须从 1 开始连续递增**。抓包里前面是 `00`，但有些工具的 BSC 编码是"块序号 - 1"，而部分实现从 0 开始 —— 规范要求第一个块的 BSC 是 **1**。

另一种根因：BSC 是 4 bit 循环的（0x0F 之后回 0x00），但**只在 Request Download 和 Request Transfer Exit 之间循环**。如果工具在一次下载过程中重新发起（发了第二个 Request Download），BSC 归 1 是对的；但如果工具在传输中途重新发起而不重置 ECU 侧计数器，就会对不上。

### 修复

```c
/* ECU 侧校验 */
int handle_transfer_data(diag_ctx_t *c, const u8 *data, u8 len) {
    u8 bsc = data[0];

    if (c->bsc_expected == 0) {
        return NRC_REQUEST_SEQUENCE_ERROR;   /* 必须先 Request Download */
    }
    if (bsc != c->bsc_expected) {
        c->bsc_error_count++;
        return NRC_INVALID_FORMAT;
    }

    flash_write(c->download_addr, &data[1], len - 1);
    c->download_addr += (len - 1);
    c->downloaded += (len - 1);

    /* BSC 4 bit 循环 */
    c->bsc_expected = (bsc + 1) & 0x0F;

    return OK;
}
```

**关键**：BSC 是 4 bit 循环（1..15, 然后 0），**不是 8 bit**。超过 15 个块后必须回绕。如果工具用 8 bit 计数器，第 16 块就会对不上。

### 复盘

- **BSC 是 4 bit 循环**是刷写调试的高频坑，很多工具实现用了 8 bit 计数器。
- ECU 侧必须在 Request Download 时初始化 `bsc_expected = 1`。
- 产线测试要包含"超过 15 个块的大文件刷写"用例。

## 案例 8: 一直返回 0x78 Response Pending，工具挂死

### 现象

执行擦除 Flash 的例程（Routine），ECU 返回 `7F 31 78` 后就再也没动静了。工具按 P2* 等待，最终超时。

### 抓包分析

```text
Tester -> ECU  0x7E8  04 31 01 FF 02
ECU   -> Tester 0x7E8  03 7F 31 78       (Response Pending)
(之后再无任何帧)
```

### 定位

例程的执行任务**卡死或死循环**，导致 Pending 定时器无法再次触发。

常见根因：

**A. Flash 擦除等待循环里 tick 不走**

```c
/* 错误: 擦除等待里用了阻塞延时, 且等待条件永远不满足 */
while (flash_status() != FLASH_READY) {
    delay_ms(10);
    /* 如果 flash_status() 因为电压低或写保护一直返回 BUSY, 这里死等 */
}
```

**B. 例程在 RTOS 里用了阻塞式等待**

在 RTOS 中 `while(!done) delay()` 会占用整个任务时间片，且如果例程任务优先级高于负责发送 Pending 的任务，就形成**优先级反转 + 饿死**。

**C. Pending 发送任务被例程占满**

如果例程在同一个任务里跑，而 Pending 由另一个任务发送，例程的忙等让 Pending 任务拿不到 CPU。

### 修复

**A. 擦除等待必须有超时和失败处理**

```c
int flash_erase_wait(uint32_t timeout_ms) {
    uint32_t start = tick_get_ms();
    while (flash_status() == FLASH_BUSY) {
        if ((tick_get_ms() - start) > timeout_ms) {
            return FLASH_ERR_TIMEOUT;
        }
        task_yield();     /* RTOS 下让出 CPU, 让 Pending 任务能跑 */
    }
    return (flash_status() == FLASH_READY) ? FLASH_OK : FLASH_ERR;
}
```

**B. 长时间任务必须异步化**

```c
/* 例程启动后立即返回, 工作在后台任务里做 */
int routine_start(diag_ctx_t *c, u16 routine_id) {
    c->routine_state = ROUTINE_RUNNING;
    c->routine_result = ROUTINE_PENDING;
    xTaskCreate(routine_task, "rout", 1024, c, 3, NULL);  /* 异步 */
    return OK;   /* 主循环里按周期发 Pending */
}

/* 主循环里 */
if (c->routine_state == ROUTINE_RUNNING) {
    if (tick_elapsed(c->last_pending_ms) >= PENDING_INTERVAL_MS) {
        send_negative_response(c, 0x31, 0x78);   /* 0x78 */
        c->last_pending_ms = tick_get_ms();
    }
}
```

**C. Pending 发送必须有最大次数保护**

```c
#define MAX_PENDING_COUNT  200
#define PENDING_INTERVAL_MS  50

if (++c->pending_count > MAX_PENDING_COUNT) {
    /* 超时保护: 终止例程并返回最终 NRC */
    routine_abort(c);
    send_negative_response(c, 0x31, 0x72);   /* General Failure */
    c->pending_count = 0;
}
```

### 复盘

- **长时间任务必须异步化**，不能在诊断处理上下文里忙等。
- RTOS 下例程任务和诊断任务要有明确的优先级关系，Pending 发送路径不能被饿死。
- Pending 间隔和最大次数都要有规范依据，不要凭感觉。

## 案例 9: Tester Present 周期太长，会话中途掉回默认

### 现象

工具进入扩展会话后开始执行一个耗时较长的操作（读大量 DTC），操作到一半，后续服务全部返回 `7F 22 7F`（服务不支持，因为会话已回退到默认）。

### 抓包分析

```text
Tester -> ECU  0x7E8  02 10 03
ECU   -> Tester 0x7E8  03 50 03 00 32 01 F4
(中间 12 秒没有任何帧)
Tester -> ECU  0x7E8  02 22 F1 90
ECU   -> Tester 0x7E8  03 7F 22 7F
```

### 定位

UDS 的 S3 定时器（会话保持超时）到期，ECU 自动回落到默认会话。S3 典型值 5000 ms，工具的 Tester Present 间隔设为 3000 ms，但**工具在这一轮操作期间被阻塞**（比如同步等待读数据），没能按时发 Tester Present。

更隐蔽的一种：ECU 在执行长时间服务时**阻塞了 CAN 接收处理**，Tester Present 帧进了邮箱但没被处理，S3 定时器照样超时。

### 修复

**A. 工具侧：Tester Present 必须有独立发送线程**

```c
/* 不能在等待响应的阻塞路径里发 Tester Present */
void tp_task(void *arg) {
    while (1) {
        can_send(REQ_ID, 0x3E, 0x00, NULL, 0);
        vTaskDelay(pdMS_TO_TICKS(TP_PERIOD_MS));   /* TP_PERIOD_MS < S3 */
    }
}
```

**B. ECU 侧：长时间服务期间不能停止处理 Tester Present**

```c
/* 诊断处理循环里, 即使在忙, 也要持续检查 TP */
void diag_main_loop(void) {
    for (;;) {
        process_can_rx();          /* 始终处理, 包括 3E */
        handle_pending_response();
        service_watchdogs();
        task_yield();
    }
}
```

**C. 明确 Tester Present 的会话保持语义**

```c
void handle_tester_present(diag_ctx_t *c) {
    /* 注意: 不要因为收到 TP 就刷新"业务忙碌"超时, 只刷新 S3 */
    c->s3_deadline = tick_get_ms() + S3_TIMEOUT_MS;
}
```

### 复盘

- **S3 定时器只在收到 Tester Present 时刷新**，不是"有任何请求就刷新"。
- 工具侧 Tester Present 应该是独立定时任务，不受业务阻塞影响。
- ECU 侧长时间服务要保证接收路径不被饿死。
- 产线测试要模拟"长时间静默后继续操作"场景。

## 案例 10: DTC 清除后立刻重新出现

### 现象

用 `14 00 FF FF FF` 清除全部 DTC，返回正响应 `54`。立刻重新读取 DTC，故障码还在。

### 抓包分析

```text
Tester -> ECU  0x7E8  04 14 00 FF FF FF
ECU   -> Tester 0x7E8  02 54
Tester -> ECU  0x7E8  03 19 02 01
ECU   -> Tester 0x7E8  07 59 02 01 00 34 P1 01
```

### 定位

清除 DTC 只是清除了"已存储"状态，但**故障的触发条件仍然存在**，诊断监控下一轮就把 DTC 重新置位。

典型场景：

- 传感器线路短路，监控每 100 ms 检测一次 → 清除后 100 ms 内立刻复现。
- 清除 DTC 时车辆仍在运行，故障条件持续存在。
- 清除指令的 DTC 掩码不对（`FF FF FF` 只覆盖 2 字节，DTC 掩码实际是 3 字节）。

### 修复

**A. 清除后必须验证复现情况**

```c
/* 清除流程 */
1. 读取当前 DTC + 状态 + 快照
2. 记录快照 (供复现分析)
3. 修复故障或断开触发条件
4. 执行 Clear Diagnostic Information (0x14)
5. 重新读取 DTC 确认
6. 跑一轮完整诊断条件, 确认不再复现
```

**B. 掩码长度要按规范**

```text
0x14 Request:
  byte0: SID 0x14
  byte1: DTC 高字节 (0xFF = 全部)
  byte2: DTC 中字节 (0xFF = 全部)
  byte3: DTC 低字节 (0xFF = 全部)
```

发送时 3 字节掩码要全 0xFF。有些工具只发 2 字节 → 长度错误。

**C. 区分"当前故障"和"历史故障"**

```c
/* 只清历史, 不清当前 */
if (dtc_status & DTC_STATUS_CURRENT) {
    /* 当前故障还在, 清除必然复现, 应先修故障 */
    return ERR_CURRENT_FAULT_ACTIVE;
}
```

### 复盘

- 清 DTC 前先读快照，这是**故障分析的关键数据**，清了就拿不到了。
- 掩码长度按规范，是 `14` 服务的固定 3 字节。
- 产线测试要有"故障未修复时清 DTC"的预期行为定义。

## 案例 11: 整车网络中多个 ECU 同时响应，功能寻址冲突

### 现象

用功能寻址发送 `10 03`（全网络进入扩展会话），抓包看到 5 个 ECU 同时响应，响应帧同时上总线，产生 Bit Error，多个 ECU 进 Error Passive。

### 抓包分析

```text
Tester -> ECU  0x7DF  02 10 03        (功能寻址, 广播)
ECU1  -> ?     0x7E8  03 50 03 ...    (同时)
ECU2  -> ?     0x7E8  03 50 03 ...    (同时)
ECU3  -> ?     0x7E8  03 50 03 ...    (同时)
(位冲突, 错误帧)
```

### 定位

功能寻址（广播）请求要求**所有 ECU 抑制正响应**，只允许一个 ECU 以负响应形式应答（通常由网关汇总）。

ECU 实现没做这个判断：

```c
/* 错误: 任何地址都回正响应 */
int handle_session_control(diag_ctx_t *c, const u8 *data, u8 len) {
    c->session = data[1];
    send_positive_response(c, 0x50, ...);   /* 功能寻址也回了! */
}
```

### 修复

```c
/* 区分物理寻址和功能寻址 */
typedef struct {
    u32 req_id;
    u8  is_functional;   /* 1 = 功能寻址 (广播) */
} diag_addr_t;

int handle_session_control(diag_ctx_t *c, const u8 *data, u8 len) {
    c->session = data[1];

    if (c->addr.is_functional) {
        /* 功能寻址: 抑制正响应, 仅在拒绝时回 NRC */
        if (session_not_allowed(c->session)) {
            send_negative_response(c, 0x10, NRC_CONDITIONS_NOT_CORRECT);
        }
        /* 正常情况不回任何响应 */
        return OK;
    }

    send_positive_response(c, 0x50, ...);
    return OK;
}
```

**工程注意**：广播抑制正响应后，工具会等不到响应。功能寻址工具需要靠"总线上没有响应"来判定成功，或靠网关的汇总响应。

### 复盘

- 功能寻址下**只有拒绝才响应**，这条规则违反会导致总线冲突和节点掉线。
- 功能寻址的 CAN ID 通常是 `0x7DF`（11 位标准帧）。
- 产线测试必须覆盖"功能寻址广播"场景，确认多 ECU 网络不会冲突。

## 案例 12: 诊断服务影响正常业务，产线整条线卡住

### 现象

刷写某个 ECU 时，整车的其他 ECU（空调、仪表）也停止工作。刷写完成后恢复。

### 抓包分析

```text
刷写过程中, 整车上 CAN 总线被大量诊断流量占满
Tester -> ECU  0x7E8  ... (Transfer Data 连续高频)
(其他节点的周期报文被延迟, 甚至出现 Error Passive)
```

### 定位

两个问题叠加：

**A. 诊断流量挤占周期报文**

刷写大文件时，Transfer Data 高频发送，占满了总线带宽。CAN 是优先级仲裁，低优先级的周期报文（仪表、空调）被饿死。

**B. 通信控制（0x28）被误用**

如果工具在刷写前发了 `28 83`（关闭 Rx 和 Tx 通信），那不只是关闭诊断通信，**是关闭所有应用报文收发**：

```text
0x28 03 = disableRxAndTx       <- 全关
0x28 01 = enableRxAndTx
0x28 02 = enableRxAndDisableTx
0x28 03 = disableRxAndEnableTx
0x28 04 = disableRxAndDisableTx
```

### 修复

**A. 限制诊断流量占用**

```c
/* 工具侧: 控制 Transfer Data 速率, 给周期报文留带宽 */
#define TP_STMIN_MIN_US   1000   /* CAN FD 下可放宽 */
#define TP_BS_MAX         0x10

/* 典型配置: BS=8, STmin=1ms, 在 500kbps 总线上约占 30% 带宽 */
```

刷写前先测总线利用率：

```text
can_utils: candump -n 100 can0 | 计算帧数 × 帧长 / 总时间
```

**B. 明确 0x28 的使用边界**

```c
/* 通信控制只在必要时使用, 且必须恢复 */
int handle_communication_control(diag_ctx_t *c, u8 subfunc, u8 control_type) {
    switch (control_type) {
        case 0x01: c->comm_enabled = 1; break;   /* enableRxAndTx */
        case 0x02: c->tx_enabled = 0; break;
        case 0x03: c->rx_enabled = 0; break;
        case 0x04: c->comm_enabled = 0; break;
        default: return NRC_SUBFUNCTION_NOT_SUPPORTED;
    }
    /* 记录原状态, 便于恢复 */
    c->comm_state_saved = 1;
    return OK;
}

/* 会话切换 / 复位时恢复 */
void diag_reset_comm_state(diag_ctx_t *c) {
    if (c->comm_state_saved) {
        c->comm_enabled = 1;
        c->tx_enabled = 1;
        c->rx_enabled = 1;
        c->comm_state_saved = 0;
    }
}
```

### 复盘

- **刷写时必须监控总线利用率**，别把整条产线拖垮。
- `0x28` 的子功能编码容易混淆（`0x01` 是 enableRxAndTx，不是 disable），上表要背下来。
- 通信控制状态必须在会话切换和 ECU Reset 时恢复，否则设备会"通信瘫痪"到下次重启。

## 根因清单

| 根因 | 典型症状 | 快速验证 |
| --- | --- | --- |
| 多帧响应发错 CAN ID | 短 DID 通、长 DID 超时 | 看有没有 FF |
| 服务表按会话索引写死 | 扩展会话全部 0x7F | 对比默认会话行为 |
| 写 DID 没落盘 | 返回 6E 但重启丢失 | 断电重启读回 |
| NVM 写入未等待完成 | 写 DID 偶发丢数据 | 加读回校验 |
| Seed 缓冲区被覆盖 | 种子密钥偶发失败 | 全 Seed 空间遍历 |
| 延时计时用相对累加 | 安全访问永久锁死 | 换绝对到期时间 |
| 先擦除后下载 | 刷写断电变砖 | 改 A/B 分区 |
| BSC 用 8 bit 计数器 | 第 16 块开始失败 | 改 4 bit 循环 |
| 长时间任务同步阻塞 | 一直 0x78 | 改异步 + Pending |
| Tester Present 被阻塞 | 会话中途掉回默认 | 独立发送线程 |
| 故障条件未消除 | 清 DTC 立刻复现 | 先读快照再清 |
| 功能寻址未抑制响应 | 多 ECU 响应冲突 | 检查 is_functional |
| 诊断流量挤占总线 | 其他节点停摆 | 测总线利用率 |
| 通信控制未恢复 | 设备通信瘫痪 | 检查 0x28 状态 |

## 关联主题

- `bus/uds.md` — UDS 定位、服务表、ISO-TP 关系
- `bus/uds-deep-dive.md` — 状态机、NRC 决策顺序、刷写事务、DoIP
- `bus/uds-practical.md` — 调试流程、检查清单
- `bus/iso-tp-failure-cases.md` — 传输层案例（多帧问题的根因常在 ISO-TP）
- `bus/j1939-failure-cases.md` — J1939 诊断（DM1/DM2）案例对比
- `basic/can-failure-cases.md` — CAN 物理层/链路层案例
- `bus/can-protocol-family.md` — CAN 家族全景

## 更新记录

- 2026-10-31: 初版，12 个产线案例。覆盖多帧响应、会话服务表、DID 落盘、种子密钥、访问延时、刷写变砖、BSC 4bit 循环、Response Pending 死锁、S3 会话保持、DTC 复现、功能寻址冲突、诊断流量挤占等高频坑。
