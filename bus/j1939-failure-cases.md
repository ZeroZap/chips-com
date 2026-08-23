# J1939 产线死机案例库

## 目标

把产线常见的 J1939 通信失败、地址冲突、DM1 报错、传输协议错误等问题写成案例库。每个案例:
- 现象 (现场)
- 抓波形 / DBC 分析 (判断)
- 定位 (根因)
- 修复 (代码 / 硬件 / DBC)
- 复盘 (如何预防)

## 案例 1: ECU 上电后 1s 反复地址声明, 网络瘫

### 现象

商用车 (卡车) 启动, 多块 ECU 同时启动, 反复地址声明 (Address Claimed, PGN 60928), 总线频繁错误帧。

### 抓 DBC

CAN 分析仪抓 PGN 60928 (0x18EEFF**), NAME 字段相同地址竞争。

### 定位

两个 ECU 的 NAME 字段中**地址相同**, 但 NAME 唯一性没有保证, J1939 地址冲突协议无法解决。

```text
J1939 NAME (8 byte) 结构:
  比特 63-49: 身份号 (21 bit)
  比特 48-41: 厂商代码 (11 bit)
  比特 40-34: ECU 实例 (6 bit)
  比特 33-29: 功能实例 (5 bit)
  比特 28-11: 功能 (18 bit)
  比特 10-8:  保留 (3 bit)
  比特 7-0:   地址 (8 bit)

NAME 的 8 bit 地址相同时:
  -> 不能用 NAME 仲裁
  -> 必须修改 NAME (身份号或厂商代码) 或改地址
```

### 修复

```c
/* 每个 ECU 用唯一身份号 */
/* 例如: 身份号 = 芯片 UID 后 21 bit */
uint64_t get_unique_name() {
    uint32_t uid[3] = {0};
    HAL_GetUIDw0(&uid[0]);  /* STM32 96 bit UID */
    HAL_GetUIDw1(&uid[1]);
    HAL_GetUIDw2(&uid[2]);
    
    uint64_t name = 0;
    name |= ((uint64_t)(uid[2] & 0x1FFFFF) << 43);  /* 身份号 21 bit */
    name |= ((uint64_t)MY_MANUFACTURER_CODE << 35);  /* 厂商代码 11 bit */
    /* ... 其他字段 */
    return name;
}

/* 优先用 NAME 仲裁 */
/* NAME 小的 (身份号小) 优先 */
```

### 复盘

- J1939 地址冲突的标准解决: 比较 NAME, 小的赢
- 同一型号 ECU 必须用不同身份号 (UID / 烧写编号)
- 产线必须用唯一身份号烧录

---

## 案例 2: DM1 误报, 实际硬件正常

### 现象

DTC (Diagnostic Trouble Code) 报告 SPN 100, FMI 1 (发动机机油压力低), 实际机油压力正常。

### 抓 DBC

PGN 65226 (DM1) 显示 SPN 100, FMI 1, CM (发生次数) = 1。

### 定位

DM1 上报规则出错。DM1 应该在 DTC **主动** (active) 时上报, CM 表示发生次数, 但 OEM 应在 DTC **清除** (历史) 时停止上报。

```c
/* 错: DTC 触发后一直上报, 即使已清 */
void dm1_report() {
    if (spn100_fmi1_active) {
        can_send(PGN_DM1, dtc_data, 8);
    }
    /* 没有清除逻辑 */
}

/* 对: 区分 active / previously active */
void dm1_report() {
    if (spn100_fmi1_active) {
        dtc_data[0] = 0xFF;  /* lamp status */
        dtc_data[1] = 0xFF;
        dtc_data[2] = 0x01;  /* SPN 100 low byte */
        dtc_data[3] = 0x00;  /* SPN high */
        dtc_data[4] = 0x01;  /* SPN 100, FMI 1 */
        dtc_data[5] = 0x01;  /* CM = 1 */
        can_send(PGN_DM1, dtc_data, 8);
    } else if (spn100_fmi1_history) {
        /* 历史 DTC, 不上报 (或用 DM2) */
    }
}
```

### 复盘

- DM1 报 active DTC, DM2 报历史 DTC
- 清除 DTC 时, CM 重置
- 详细见 `bus/uds-*.md`

---

## 案例 3: BAM (Broadcast Announce Message) 多帧传输数据丢失

### 现象

ECU 用 BAM 发 1500 字节固件, 接收方偶尔少 1-2 字节, CRC 校验失败。

### 抓 DBC

PGN 60416 (TP.CM_BAM) 发出, 后续 TP.DT (PGN 60160) 帧到, 但偶尔有 TP.DT 丢失。

### 定位

BAM 协议是"广播 + 不应答", 接收方无重传机制, 任何 TP.DT 帧丢失都会导致数据不全。

```text
TP 协议:
  - RTS/CTS (点对点, 1 对 1): 接收方有 ACK, 可以重传
  - BAM (广播, 1 对多): 接收方无 ACK, 丢包不能恢复
```

### 修复

```c
/* 固件下载用 RTS/CTS, 不用 BAM */
int send_firmware_ecu(uint8_t *firmware, int len) {
    /* RTS (Request To Send) */
    can_send_tp_cm(PGN_TP_CM, RTS_MSG, total_bytes, total_packets, ...);
    
    /* 等 CTS (Clear To Send) */
    wait_for_cts();
    
    /* 按 CTS 指示的包数发 */
    for (packet = 0; packet < total_packets; packet++) {
        can_send_tp_dt(packet_num, data[packet]);
        /* 等下一 CTS */
        if (need_more_cts) wait_for_cts();
    }
    
    /* EndOfMsgAck */
    wait_for_eoma();
    return 0;
}
```

### 复盘

- 固件下载必须用 RTS/CTS (有重传)
- BAM 只用于"广播" 场景 (e.g. 全网同步配置)
- 详细见 `j1939-transport-protocol.md`

---

## 案例 4: PGN 请求 (Request PGN) 应答超时

### 现象

诊断工具发 Request PGN (PGN 59904) 请求 0xFEEE (DM1), 但 ECU 不应答。

### 抓 DBC

总线上看到 Request PGN, 但没有 DM1 响应。

### 定位

DM1 的 PGN 是 PGN 65226 (0x00FECA, 高字节 0xFE, 低字节 0xCA)。请求时需要按 PGN 规则编码, 一些代码错误地按"原始 ID" 请求。

```c
/* 错: 直接用 ID 而非 PGN */
can_send(0x18FECA00, ...);  /* 这是 DM1 的 ID, 不是 Request */

/* 对: Request PGN 格式 */
can_send_request(0x00FECA);  /* PGN = 65226 */
```

### 修复

```c
/* 用 J1939 库, 不要手动组装 ID */
/* 或用 CAN ID = 0x18EAFF + target_address, 数据 = requested_PGN */
can_send_ext_id(0x18EAFFFE, pgn, 3);
```

### 复盘

- J1939 PGN 请求格式: ID 0x18EA** (PF=234, PS=255, target=0xFE)
- 详细见 `j1939-deep-dive.md` "## Request PGN"

---

## 案例 5: 多 ECU 同一 SPN 来源不同, 报告冲突

### 现象

诊断工具收到同一 SPN (e.g. SPN 110 发动机温度) 报告, 但来源 ECU 多个, 数据不一致。

### 抓 DBC

PGN 65262 (ET1 - Engine Temperature 1) 多个 ECU 都发, SA (Source Address) 不同。

### 定位

SPN 不是全局唯一, 是"在某个 PGN 里有特定含义"。多个 ECU 报告同一 SPN 是正常的 (e.g. ECU1 和 ECU2 都报告发动机温度, 用 SA 区分)。

诊断工具要按 SA 区分数据源, 不要把同名 SPN 当成同一数据。

### 修复

```c
/* 诊断工具按 SA + PGN + SPN 组合索引 */
struct spn_data {
    uint8_t source_address;
    uint32_t pgn;
    uint32_t spn;
    uint8_t fmi;
    float value;
    uint32_t timestamp;
};

/* 索引: (SA, PGN, SPN) -> spn_data */
```

### 复盘

- SPN 是局部编号, 跨 PGN 才有意义
- 诊断工具必须按 (SA, PGN, SPN) 索引数据
- 详细见 `j1939-deep-dive.md` "## SPN 编号"

---

## 案例 6: Transport Protocol 流控 (CTS) 错误, 数据错位

### 现象

ECU 用 RTS/CTS 接收固件, 接收到的数据顺序错乱。

### 抓 DBC

TP.CM_RTS, 后续 TP.CM_CTS 包的包数 / 下一包号错。

### 定位

CTS 包的数据格式错, "下一包号" 字段填错, "可发包数" 字段填错。

```text
TP.CM_CTS (PGN 60416) 8 字节:
  字节 0: 控制字节 = 0x10 (CTS)
  字节 1: 可发包数 (0xFF = 剩下的全部)
  字节 2: 下一包号
  字节 3-7: 保留
```

### 修复

```c
/* 对: 严格按 J1939-21 协议 */
void send_cts(uint8_t next_packet, uint8_t max_packets) {
    uint8_t data[8] = {
        0x10,                    /* 控制字节 = CTS */
        max_packets,             /* 可发包数 */
        next_packet,             /* 下一包号 */
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF
    };
    can_send_pgn(PGN_TP_CM, data, 8);
}
```

### 复盘

- J1939-21 协议格式严格
- 字节序和字段位置错, 整批数据错乱
- 详细见 `j1939-transport-protocol.md`

---

## 案例 7: BAM 广播速率过快, 接收方来不及

### 现象

发动机 ECU 用 BAM 周期 10ms 广播 PGN 61444 (EEC1), 50ms 广播 PGN 65262 (ET1)。某些节点接收丢帧。

### 抓 DBC

BAM TP.DT 帧连续, 接收方每 10ms 进一次中断, 业务处理不过来。

### 定位

接收方处理速度跟不上广播速率, RTOS 任务优先级不够, 接收 buffer 溢出。

```c
/* 错: 接收方优先级低 */
void can_rx_task(void *arg) {
    /* 优先级 5, 低 */
    process_can_frame();
}

/* 对: 高优先级 + 批量处理 */
void can_rx_isr(void) {
    /* ISR 写入环形 buffer */
    ring_buf_put(&rx_ring, frame);
    /* 不在 ISR 处理 */
}

void can_process_task(void *arg) {
    /* 优先级 4, 高 */
    while (ring_buf_available(&rx_ring)) {
        ring_buf_get(&rx_ring, &frame);
        process_frame(&frame);
    }
}
```

### 复盘

- 高频广播需要接收方有专用处理任务
- 不能用低优先级循环处理
- 详细见 `can-rtos-integration.md`

---

## 案例 8: NAME 配置错, 地址声明失败

### 现象

ECU 启动后地址声明 (PGN 60928) 发出, 但 250ms 后还没收到 CAN 帧被其他 ECU 接受。

### 抓 DBC

PGN 60928 (Address Claimed) 反复发, SA 不停在 0x00-0xFF 之间跳。

### 定位

NAME 字段非法 (e.g. 厂商代码 0, 保留位非 0), 协议栈拒绝。

```c
/* 错: NAME 没填好 */
uint64_t name = 0;  /* 全 0, 不合法 */

/* 对: NAME 严格按 J1939-81 规定 */
uint64_t build_name(
    uint32_t identity_number,    /* 21 bit */
    uint16_t manufacturer_code,   /* 11 bit */
    uint8_t  ecu_instance,        /* 6 bit (实例 0-3, 4-7 保留) */
    uint8_t  function_instance,   /* 5 bit */
    uint32_t function,            /* 18 bit */
    uint8_t  reserved,            /* 3 bit (必须 0) */
    uint8_t  address              /* 8 bit (0-253, 254-255 保留) */
) {
    uint64_t name = 0;
    name |= ((uint64_t)(identity_number & 0x1FFFFF) << 43);
    name |= ((uint64_t)(manufacturer_code & 0x7FF) << 35);
    name |= ((uint64_t)(ecu_instance & 0x3F) << 29);  /* 0-3 */
    name |= ((uint64_t)(function_instance & 0x1F) << 24);
    name |= ((uint64_t)(function & 0x3FFFF) << 6);
    name |= ((uint64_t)(reserved & 0x7) << 3);
    name |= ((uint64_t)(address & 0xFF));
    return name;
}
```

### 复盘

- NAME 字段是 J1939 身份核心
- 厂商代码必须从 SAE 申请, 不能用 0
- 详细见 `j1939-network-management.md`

---

## 案例 9: DM14/DM15 (DM Active) 应答错误

### 现象

诊断工具发 DM14 (DM Clear), ECU 错误地清除所有 DTC, 包括不想清的。

### 抓 DBC

PGN 65235 (DM14) 请求清除, 接收方错误地清除了所有 DTC, 包括历史 DTC。

### 定位

DM14 处理逻辑错。DM14 应该只清除 active DTC, 保留历史 DTC (DM2); 或者按 OEM 策略部分清除。

```c
/* 错: DM14 清所有 DTC */
void dm14_handler(uint8_t *data, int len) {
    clear_all_dtcs();  /* 错! */
}

/* 对: 按 SAE J1939-73 规定 */
void dm14_handler(uint8_t *data, int len) {
    /* DM14 是 4 字节:
       字节 0-1: 保留 (0xFF)
       字节 2-3: 第一个 SPN (specific SPN)
       字节 4-5: 第一个 FMI
       字节 6-7: 第二个 SPN
       ...
       如果特定 SPN: 只清匹配的
       如果全 0xFF: 清所有 (谨慎!)
    */
    
    if (specific_spn_requested) {
        clear_specific_dtc(spn, fmi);
    } else {
        /* 全 0xFF 表示"清所有", 但只清 active, 不清 historical */
        clear_all_active_dtcs();
    }
}
```

### 复盘

- DM14 清除有标准规则, 严格按 J1939-73
- 产线测试 DM14 应保留历史 DTC

---

## 案例 10: J1939 网桥 (Bridge) 过滤规则错

### 现象

卡车有 2 路 CAN (发动机 / 车身), 网桥过滤规则错, 关键报文没转发。

### 抓 DBC

网桥进有数据, 出没数据, 过滤规则误把发动机关键报文过滤掉。

### 定位

网桥过滤规则配置错, 应该在 DBC 阶段确定, 不是写代码时确定。

```c
/* 错: 硬编码过滤规则 */
void bridge_filter(uint32_t can_id) {
    if (can_id == 0x18FEF100) return;  /* EEC1, 错! 这是关键报文 */
    forward_to_other_bus(can_id);
}

/* 对: DBC 驱动的过滤规则 */
struct j1939_pgn_filter {
    uint32_t pgn;
    bool forward;
};

const struct j1939_pgn_filter bridge_rules[] = {
    { 0xFECA, true },   /* DM1 转发 */
    { 0xFEEF, true },   /* DM2 转发 */
    { 0xFEE5, true },   /* DM14 转发 */
    { 0xFEF1, false },  /* 不转发某些 */
    /* ... */
};
```

### 复盘

- J1939 网桥过滤必须 DBC 驱动
- 关键报文 (DM, EEC1, CCVS) 必须转发
- 网桥配置应该有版本控制和回滚

---

## 案例 11: PGN 库版本不一致, 解析错乱

### 现象

不同供应商的 ECU 用不同版本 PGN 库, 同一 PGN (e.g. 0xFEEE) 解析出不同数据。

### 抓 DBC

PGN 0xFEEE 长度 8 字节, 但 OEM A 解析为"扩展诊断", OEM B 解析为"DM1"。

### 定位

PGN 0xFEEE 是 SAE 保留的, 不同 OEM 自己定义。**0xFEEE 不是公共 PGN**, 各家自定义。

### 修复

```text
- 用 SAE 公共 PGN (e.g. DM1=0xFECA, EEC1=0xF004)
- 不用 SAE 保留 PGN (0xFEE0-0xFEFF) 跨厂商
- 跨厂商通信用 UDS (ISO 14229) 而非 J1939
```

### 复盘

- PGN 0xFEE0-0xFEFF 是 SAE 保留
- 各厂商自定义会造成冲突
- 详细见 `j1939-deep-dive.md` "## PGN 分类"

---

## 案例 12: 终端电阻错, J1939 通信失败

### 现象

J1939 总线 (250 kbaud) 错误帧, 重启 ECU 后好一段时间, 然后又错。

### 抓波形

J1939 总线终端电阻没接或错接。

### 定位

J1939 总线 (商用车) 通常终端电阻位置在诊断接口 (OBD) 上, 不是 ECU 上。如果诊断接口没接或坏了, 总线缺终端。

```text
J1939-11 物理层 (250 kbaud):
  终端电阻 120 ohm 在诊断接口 (OBD J1939 pin 6 和 pin 14)

J1939-14 物理层 (500 kbaud):
  终端电阻在每个 ECU 内
```

### 修复

```text
1. 检查 OBD 接口终端电阻 (J1939-11)
2. 检查每个 ECU 终端电阻使能 (J1939-14)
3. 量 CAN_H / CAN_L 之间电阻: 60 ohm
```

### 复盘

- J1939-11 和 J1939-14 终端电阻位置不同
- 产线必须验证 OBD 接口
- 详细见 `can-failure-cases.md` 案例 2

---

## 案例 13: 报文优先级 (PRIO) 配错, 实时性差

### 现象

发动机 ECU 报 PGN 61444 (EEC1) 用 PRIO 6 (低优先级), 高负载下响应慢。

### 抓 DBC

CAN ID = 0x18F6F104, PRIO 字段 (bit 26-28) = 6。

### 定位

PGN 61444 (EEC1) 是发动机关键报文, 应该用最高优先级 (0-2)。

```c
/* 错: 默认优先级 */
can_send_id(0x18F6F104, data, 8);
/* 0x18F = PRIO 6, bit 26-28 */

/* 对: 高优先级 */
can_send_id(0x0CF6F104, data, 8);
/* 0x0C = PRIO 3 (发动机关键) */

/* 最高优先级 (P = 0): 0x04F6F104 */
```

### 复盘

- J1939 PGN 优先级 (0-7) 由 CAN ID bit 26-28 决定
- 0 = 最高, 7 = 最低
- 关键报文 (发动机, 制动) 用 0-2
- 详细见 `j1939-deep-dive.md` "## CAN ID 编码"

---

## 案例 14: DM 报文格式错, 诊断工具拒绝

### 现象

ECU 上报 DM1, 但诊断工具 (J1939 兼容) 不识别。

### 抓 DBC

DM1 格式错, 字节序或字段长度错。

```text
DM1 格式 (PGN 65226, 8 字节):
字节 0: 第一个 DTC 的 lamp status (MIL/RSL/AWL/PL)
字节 1: 第一个 DTC 的 lamp status + reserved
字节 2-3: SPN 低 16 bit (byte 2 = bit 7-0, byte 3 = bit 15-8)
字节 4-5: SPN 高 5 bit (byte 4 bit 0-4) + FMI (byte 4 bit 5-7) + ...
```

### 定位

SPN 是 19 bit, FMI 是 5 bit, 编码方式不直观, 容易错。

```c
/* 错: 直接赋值 */
data[2] = spn & 0xFF;        /* 错 */
data[3] = (spn >> 8) & 0xFF;
data[4] = (fmi & 0x1F) | ((spn >> 16) << 5);  /* 错 */

/* 对: 严格按 SAE J1939-73 编码 */
void encode_dtc(uint32_t spn, uint8_t fmi, uint8_t occurrence_count, uint8_t *data) {
    /* data 是 4 字节: data[0]=lamp, data[1]=reserved/lamp, data[2-3]=SPN+encoded FMI */
    
    uint32_t spn_low = spn & 0xFFFF;           /* 低 16 bit */
    uint8_t  spn_high = (spn >> 16) & 0x1F;     /* 高 5 bit */
    uint8_t  fmi_5bit = fmi & 0x1F;             /* 5 bit */
    
    /* SAE 编码 */
    data[3] = spn_low & 0xFF;                   /* 字节 3 = SPN bit 7-0 */
    data[4] = ((spn_low >> 8) & 0xFF) |          /* 字节 4 = SPN bit 15-8 */
              ((spn_high & 0x07) << 5) |        /* 字节 4 bit 5-7 = SPN bit 16-18 */
              (fmi_5bit & 0x1F);                 /* 字节 4 bit 0-4 = FMI */
    /* 注: 具体编码因 OEM 而异, 严格按 J1939-73 */
}
```

### 复盘

- DM 格式是 SAE 规定的, 严格按 J1939-73
- SPN/FMI/CM 编码容易错
- 用专业 J1939 库, 不要手写

---

## 案例 15: J1939 网桥循环转发, 死循环

### 现象

J1939 网桥把报文从 CAN1 转到 CAN2, 又从 CAN2 转回 CAN1, 总线爆。

### 抓波形

同一帧在总线上反复出现, 每次转发副本。

### 定位

网桥过滤规则没排除"已转发" 的帧, 形成循环。

```c
/* 错: 简单转发, 不过滤 */
void can1_to_can2(uint32_t id, uint8_t *data, int len) {
    can_send(CAN2, id, data, len);  /* 错: 会被 can2_to_can1 转回 */
}

void can2_to_can1(uint32_t id, uint8_t *data, int len) {
    can_send(CAN1, id, data, len);  /* 错: 会被 can1_to_can2 转回 */
}

/* 对: 标记已转发, 过滤已转发 */
void can1_to_can2(uint32_t id, uint8_t *data, int len) {
    if (already_forwarded(id)) return;
    mark_forwarded(id);
    can_send(CAN2, id, data, len);
}
```

### 复盘

- J1939 网桥必须有防循环机制
- 用 CAN ID 标记已转发, 或用 PGN 黑白名单

---

## 案例 16: 命令地址 (DA) 错, 多个 ECU 响应

### 现象

诊断工具发 Request PGN (PGN 59904) 给特定 ECU (DA=0x28), 但多个 ECU 响应。

### 抓 DBC

DA = 0x28 的 Request PGN, 但多个 ECU 都发 DM1 响应。

### 定位

**多个 ECU 用了相同的地址 0x28**。J1939 地址声明 (PGN 60928) 时, NAME 仲裁失败, 多个 ECU 占用同一地址。

```c
/* 解决: 严格分配地址 */
/* 地址分配表 (OEM 文档) */
const uint8_t ecu_address_map[] = {
    0x00,  /* Engine #1 */
    0x01,  /* Engine #2 (双发动机) */
    0x10,  /* Transmission */
    0x18,  /* Brakes */
    /* ... */
};

/* 启动时检查地址是否已占用 */
if (address_in_use(assigned_address)) {
    request_new_address();
}
```

### 复盘

- J1939 地址分配必须 OEM 严格管理
- 同一地址被多个 ECU 占用, 整个网络混乱
- 详细见 `j1939-network-management.md`

---

## 案例 17: 心跳报文 (Heartbeat) 丢失, 误判 ECU 离线

### 现象

监控工具检测到 ECU "离线", 实际 ECU 正常运行, 报文正常发。

### 抓 DBC

ECU 发 1Hz 心跳 (PGN 65260), 监控工具 5s 没收到就报离线。

### 定位

监控工具的判定时间过短, 或 ECU 心跳被网关过滤。

```c
/* 错: 5s 超时太短 */
if (heartbeat_lost_timeout(5s)) {
    report_offline();
}

/* 对: 至少 3-5 倍心跳周期 */
if (heartbeat_lost_timeout(30s)) {  /* 1Hz 心跳, 30s 阈值 */
    report_offline();
}
```

### 复盘

- 心跳超时时间必须 > 3 倍心跳周期
- 考虑网络延迟 + 网关过滤
- 详细见 `j1939-network-management.md`

---

## 案例 18: PGN 0x00 (Torque/Speed) 解析错, 仪表显示异常

### 现象

仪表盘显示的车速不对, 实际车速正常。

### 抓 DBC

PGN 65265 (CCVS - Cruise Control/Vehicle Speed) 解析错。

### 定位

PGN 65265 字段定义:
```text
字节 0-1:  车速 (1/256 km/h)
字节 2-3:  巡航控制车速 (1/256 km/h)
字节 4:    巡航控制状态
字节 5-6:  巡航控制设定速度 (1/256 km/h)
字节 7:    其他
```

代码解析时把字节序错, 或分辨率用错。

```c
/* 错 */
uint16_t speed_raw = (data[0] << 8) | data[1];  /* 大端, 错? */
float speed = speed_raw * 0.01;  /* 分辨率错, 应该是 1/256 */

/* 对: 小端 + 正确分辨率 */
uint16_t speed_raw = (data[1] << 8) | data[0];  /* 小端 */
float speed = speed_raw / 256.0;  /* 1/256 km/h */
```

### 复盘

- J1939 字段严格按 SAE J1939-71
- 字节序 + 分辨率是常见错误
- 用专业 DBC 工具生成代码, 不要手写

---

## 案例 19: J1939-73 DTC 数量溢出

### 现象

ECU 报 DM1, 但诊断工具只能看到前 2 个 DTC, 实际 ECU 有 10 个 active DTC。

### 抓 DBC

DM1 (PGN 65226) 8 字节, 1 个 DTC 占 4 字节, 8 字节最多 2 个 DTC。

### 定位

DM1 一帧只能报 2 个 DTC (8 字节), 超过需要多帧 (TP 协议)。

```c
/* 错: 把所有 DTC 塞进 DM1 */
void dm1_send() {
    uint8_t data[8];
    /* 1 个 DTC 4 字节, 8 字节只能 2 个 */
    encode_dtc(&all_dtcs[0], &data[0]);
    encode_dtc(&all_dtcs[1], &data[4]);
    can_send(PGN_DM1, data, 8);  /* 其他 8 个 DTC 丢了 */
}

/* 对: 多帧用 TP 协议 */
void dm1_send() {
    if (active_dtc_count <= 2) {
        /* 单帧 */
        send_dm1_single();
    } else {
        /* 多帧用 TP.BAM */
        send_dm1_bam();
    }
}
```

### 复盘

- DM1 单帧最多 2 个 DTC
- 多 DTC 用 TP 协议 (BAM 或 RTS/CTS)
- 详细见 `j1939-transport-protocol.md`

---

## 案例 20: 产线 J1939 一致性测试不通过

### 现象

新 ECU 跑 SAE J1939-84 一致性测试, 几十项测试中部分失败。

### 抓 DBC

测试工具报: "PGN 60928 应答超时", "DM1 格式错" 等。

### 定位

J1939-84 一致性测试覆盖:
- 地址声明
- 关键 PGN 应答
- DM 格式
- TP 协议
- 心跳
- 等

每项测试有严格标准, 任何不符合就是 fail。

### 修复

```text
1. 跑 J1939-84 完整测试
2. 逐项修复 fail 项
3. 重新测试
4. 记录通过的 OEM 测试报告
```

### 复盘

- J1939-84 一致性测试是商用车 ECU 量产标准
- 产线必须 100% 通过
- 推荐用 Vector / Softing 等专业工具

---

## 案例汇总: 产线 J1939 死机根因分布

```text
地址声明 / 冲突             18%
TP 协议 (BAM / RTS/CTS)    15%
DM 格式错 / 解析错          15%
PGN 库版本不一致            12%
心跳 / 离线判定             10%
CAN 物理层 (终端 / EMC)      10%
优先级 / 实时性              8%
多 ECU 协同                 7%
其他                         5%
```

地址 + TP + DM 三类加起来近 50%, 是产线 J1939 死机的主要根因区。

## 产线 J1939 根因预防清单

```text
□ NAME 字段严格按 SAE J1939-81, 身份号唯一
□ 地址分配 OEM 统一管理, 避免冲突
□ PGN 库版本一致, 跨厂商用公共 PGN
□ 关键报文用高优先级 (0-2)
□ TP 协议: 固件用 RTS/CTS, 广播用 BAM
□ DM 格式严格按 SAE J1939-73, 用专业库
□ J1939-84 一致性测试 100% 通过
□ 网桥过滤规则 DBC 驱动, 防循环
□ 心跳超时 > 3 倍心跳周期
□ 终端电阻按 J1939-11 / 14 标准放置
□ 多 DTC 用 TP 协议
□ 终端电阻验证 (J1939-11 60 ohm, J1939-14 单 ECU)
□ 老化测试 1000+ 小时
□ 跨 OEM 通信用 UDS (ISO 14229) 而非 J1939
```

## 关联文档

- `j1939-deep-dive.md` 原理
- `j1939-practical.md` 速查
- `j1939-transport-protocol.md` TP 多帧传输
- `j1939-network-management.md` 地址声明 / 网络管理
- `j1939-index.md` 导航
- `can-deep-dive.md` CAN 基础
- `can-failure-cases.md` CAN 产线案例
- `can-multimaster-and-bus-off.md` CAN 多 master / Bus Off
- `bus/uds-*.md` UDS 诊断
- `bus/iso-tp-*.md` ISO-TP
