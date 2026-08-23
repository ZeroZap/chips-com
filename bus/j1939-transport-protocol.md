# J1939 传输协议 (TP) 详解

## 目标

J1939 经典 CAN 数据帧只能传 8 字节, 但很多应用 (固件下载, 大数据块) 需要传输 > 8 字节。本文讲清楚:
- BAM (Broadcast Announce Message) 协议
- RTS/CTS (点对点) 协议
- 多帧传输完整流程
- 超时和重传
- 实战代码骨架

## 背景: 为什么需要 TP

```text
经典 CAN 数据帧: 0-8 字节
J1939 大多数 PGN: 0-8 字节
但有些场景需要 > 8 字节:
  - 固件下载 (几十 KB - 几 MB)
  - 诊断 (DM1 多个 DTC, 可能 > 2 个)
  - 大数据块 (e.g. 整车配置)
  - 多帧诊断响应

J1939 TP 协议:
  - 把大数据包拆成多个 8 字节 CAN 帧
  - 加流控和重传
  - 接收方重组
```

## TP 协议分类

### 两种协议

```text
BAM (Broadcast Announce Message):
  - 1 对多 (广播)
  - 无流控, 无重传
  - 适用: 整车配置同步, 简单广播
  - 不适用: 固件下载, 关键数据传输

RTS/CTS (点对点):
  - 1 对 1
  - 有流控, 有重传
  - 适用: 固件下载, 诊断大数据
```

### PGN 编号

```text
TP 协议用 2 个 PGN:
  TP.CM (Connection Mode): PGN 60416 (0x00EC00)
  TP.DT (Data Transfer):   PGN 60160 (0x00EB00)
  
CM 包的 8 字节包含"控制字节" 决定协议类型
```

## BAM (广播) 协议

### 协议流程

```text
发送方:
  1. 发 TP.CM_BAM (1 帧)
     - 包含总字节数, 总包数, 保留字节, PGN
  2. 等待 50-200ms (BAM 间隔)
  3. 发 TP.DT (1 帧 = 7 字节数据 + 1 字节包号)
  4. 重复 (3) 直到所有包发完
  5. 总耗时: 1785 ms 内必须发完 (256 包 * 7 字节 / 50ms 间隔)

接收方:
  1. 收 TP.CM_BAM, 记录总包数, PGN
  2. 收 TP.DT, 重组数据
  3. 全部收完后, 解析 PGN 数据
```

### TP.CM_BAM 格式 (PGN 60416, 8 字节)

```text
字节 0: 控制字节 = 0x20 (BAM)
字节 1: 保留 = 0xFF
字节 2-3: 总字节数 (LE, e.g. 0x0120 = 288 字节)
字节 4:  总包数 (e.g. 0x30 = 48 包)
字节 5:  保留 = 0xFF
字节 6-7: PGN (LE, 16 bit)
字节 7: 保留
```

### TP.DT 格式 (PGN 60160, 8 字节)

```text
字节 0:  包号 (1-255, 第 1 包 = 0x01)
字节 1-7: 数据 (7 字节/包)
```

### 完整示例

```c
/* 发送 BAM 广播 100 字节 PGN 0xFECA (DM1) */
void send_dm1_bam(uint8_t *data, int len) {
    if (len > 1785) return;  /* BAM 上限 */
    
    int num_packets = (len + 6) / 7;
    
    /* 1. 发 BAM */
    uint8_t cm_data[8] = {
        0x20,                              /* 控制字节 = BAM */
        0xFF,                              /* 保留 */
        (uint8_t)(len & 0xFF),             /* 总字节数低 */
        (uint8_t)((len >> 8) & 0xFF),      /* 总字节数高 */
        num_packets,                       /* 总包数 */
        0xFF,                              /* 保留 */
        0xCA,                              /* PGN 0xFECA 低 */
        0xFE,                              /* PGN 0xFECA 高 */
    };
    can_send_pgn(PGN_TP_CM, cm_data, 8);
    
    /* 2. 发 DT 包 */
    for (int i = 0; i < num_packets; i++) {
        uint8_t dt_data[8] = {
            i + 1,                          /* 包号 1-N */
            data[i*7 + 0],
            data[i*7 + 1],
            data[i*7 + 2],
            data[i*7 + 3],
            data[i*7 + 4],
            data[i*7 + 5],
            data[i*7 + 6],
        };
        can_send_pgn(PGN_TP_DT, dt_data, 8);
        
        /* BAM 间隔 50-200ms */
        HAL_Delay(75);
    }
}
```

## RTS/CTS (点对点) 协议

### 协议流程

```text
发送方 (源):
  1. 发 TP.CM_RTS
     - 总字节数, 总包数, 最大包数, PGN
  2. 等待 TP.CM_CTS
  3. 按 CTS 指示的包数发 TP.DT
  4. 等待下一个 TP.CM_CTS
  5. 重复 (3-4) 直到所有包发完
  6. 等待 TP.CM_EndOfMsgAck

接收方 (目标):
  1. 收 TP.CM_RTS
  2. 检查是否能接收 (buffer, 协议等)
  3. 发 TP.CM_CTS
     - 下一包号, 可发包数 (1-255, 0xFF = 全部)
  4. 收 TP.DT
  5. 收齐后发 TP.CM_EndOfMsgAck
  6. 异常时发 TP.CM_Conn_Abort
```

### TP.CM 控制字节

```text
0x10: CTS (Clear To Send) - 接收方发给发送方
0x11: EndOfMsgAck - 接收方发给发送方
0x12: RTS (Request To Send) - 发送方发给接收方
0x13: Conn_Abort - 任何一方发, 终止连接
0x14: BAM - 发送方广播
0xFF: DTS (Data Transfer Offset, 备用)
```

### TP.CM_RTS 格式 (控制字节 0x12)

```text
字节 0: 控制字节 = 0x12
字节 1-2: 总字节数 (LE, 16 bit)
字节 3:   总包数
字节 4:   最大包数 (本次连接最大可发的包数, 0xFF = 全部)
字节 5:   保留 = 0xFF
字节 6-7: PGN (LE, 16 bit)
```

### TP.CM_CTS 格式 (控制字节 0x10)

```text
字节 0: 控制字节 = 0x10
字节 1:   可发包数 (1-255, 0xFF = 全部)
字节 2:   下一包号 (1-N)
字节 3-7: 保留 = 0xFF
```

### TP.CM_EndOfMsgAck 格式 (控制字节 0x11)

```text
字节 0: 控制字节 = 0x11
字节 1-2: 总字节数 (LE, 16 bit)
字节 3:   总包数
字节 4-7: 保留 = 0xFF
```

### TP.CM_Conn_Abort 格式 (控制字节 0x13)

```text
字节 0: 控制字节 = 0x13
字节 1-7: 任意 (通常保留 0xFF)
```

## 完整 RTS/CTS 示例 (固件下载)

### 发送方 (源 ECU)

```c
int tp_send_firmware(uint8_t dest_addr, uint8_t *firmware, int len) {
    if (len > 1785) {
        /* 超过单连接上限, 分批 */
        /* 这里简化, 假设 <= 1785 */
    }
    
    int num_packets = (len + 6) / 7;
    
    /* 1. 发 RTS */
    uint8_t rts_data[8] = {
        0x12,                              /* 控制字节 = RTS */
        (uint8_t)(len & 0xFF),
        (uint8_t)((len >> 8) & 0xFF),
        num_packets,                       /* 总包数 */
        0xFF,                              /* 最大包数 = 全部 */
        0xFF,
        0xCA,                              /* PGN 0xFECA (DM1 举例) */
        0xFE,
    };
    can_send_dest_pgn(dest_addr, PGN_TP_CM, rts_data, 8);
    
    int sent_packets = 0;
    while (sent_packets < num_packets) {
        /* 2. 等 CTS */
        tp_cm_t cm;
        if (!wait_for_tp_cm(dest_addr, PGN_TP_CM, 0x10, &cm, 750)) {
            return -ETIMEDOUT;  /* CTS 超时 */
        }
        
        uint8_t next_packet = cm.next_packet;
        uint8_t max_packets = cm.max_packets;
        if (max_packets == 0) max_packets = num_packets - sent_packets;
        
        /* 3. 按 CTS 指示的包数发 DT */
        for (int i = 0; i < max_packets && sent_packets < num_packets; i++) {
            uint8_t dt_data[8] = {
                sent_packets + 1,         /* 包号 */
                firmware[sent_packets*7 + 0],
                firmware[sent_packets*7 + 1],
                firmware[sent_packets*7 + 2],
                firmware[sent_packets*7 + 3],
                firmware[sent_packets*7 + 4],
                firmware[sent_packets*7 + 5],
                firmware[sent_packets*7 + 6],
            };
            can_send_dest_pgn(dest_addr, PGN_TP_DT, dt_data, 8);
            sent_packets++;
            
            /* DT 间隔 0-200ms */
            HAL_Delay(10);
        }
    }
    
    /* 4. 等 EndOfMsgAck */
    tp_cm_t eoma;
    if (!wait_for_tp_cm(dest_addr, PGN_TP_CM, 0x11, &eoma, 750)) {
        return -ETIMEDOUT;
    }
    
    return 0;
}
```

### 接收方 (目标 ECU)

```c
/* 接收 RTS, 触发 TP 会话 */
void tp_rx_rts_handler(uint8_t src_addr, uint8_t *cm_data) {
    if (cm_data[0] != 0x12) return;  /* 不是 RTS */
    
    uint16_t total_bytes = cm_data[1] | (cm_data[2] << 8);
    uint8_t  num_packets = cm_data[3];
    uint8_t  max_packets = cm_data[4];
    uint16_t pgn = cm_data[6] | (cm_data[7] << 8);
    
    /* 检查是否能接收 */
    if (tp_session_active) {
        /* 已经有会话, 发 Conn_Abort */
        uint8_t abort[8] = { 0x13, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };
        can_send_dest_pgn(src_addr, PGN_TP_CM, abort, 8);
        return;
    }
    
    /* 启动新 TP 会话 */
    tp_session_active = true;
    tp_session.src_addr = src_addr;
    tp_session.total_bytes = total_bytes;
    tp_session.num_packets = num_packets;
    tp_session.next_packet = 1;
    tp_session.received_bytes = 0;
    tp_session.pgn = pgn;
    
    /* 发 CTS, 请求下一包 (1) */
    uint8_t cts_data[8] = {
        0x10,                              /* 控制字节 = CTS */
        num_packets,                       /* 一次全发 */
        1,                                  /* 下一包 = 1 */
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    };
    can_send_dest_pgn(src_addr, PGN_TP_CM, cts_data, 8);
}

/* 接收 DT, 重组 */
void tp_rx_dt_handler(uint8_t src_addr, uint8_t *dt_data) {
    if (!tp_session_active || tp_session.src_addr != src_addr) return;
    
    uint8_t packet_num = dt_data[0];
    if (packet_num != tp_session.next_packet) {
        /* 包号错, 发 Conn_Abort */
        uint8_t abort[8] = { 0x13, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };
        can_send_dest_pgn(src_addr, PGN_TP_CM, abort, 8);
        tp_session_active = false;
        return;
    }
    
    /* 存数据 */
    memcpy(&tp_session.buffer[(packet_num - 1) * 7], &dt_data[1], 7);
    tp_session.received_bytes += 7;
    if (tp_session.received_bytes > tp_session.total_bytes) {
        tp_session.received_bytes = tp_session.total_bytes;
    }
    tp_session.next_packet++;
    
    /* 全部收完, 发 EndOfMsgAck */
    if (tp_session.next_packet > tp_session.num_packets) {
        uint8_t eoma[8] = {
            0x11,                              /* 控制字节 = EndOfMsgAck */
            (uint8_t)(tp_session.total_bytes & 0xFF),
            (uint8_t)((tp_session.total_bytes >> 8) & 0xFF),
            tp_session.num_packets,
            0xFF, 0xFF, 0xFF, 0xFF,
        };
        can_send_dest_pgn(src_addr, PGN_TP_CM, eoma, 8);
        
        /* 处理完整数据 */
        process_tp_message(tp_session.pgn, tp_session.buffer, tp_session.total_bytes);
        
        tp_session_active = false;
    } else {
        /* 发下一个 CTS */
        uint8_t cts_data[8] = {
            0x10,
            tp_session.num_packets - tp_session.next_packet + 1,
            tp_session.next_packet,
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        };
        can_send_dest_pgn(src_addr, PGN_TP_CM, cts_data, 8);
    }
}
```

## 超时和重传

### 4 类超时

```text
T1: RTS 到 CTS 的响应时间
  默认 750ms
  超时: 发送方重发 RTS, 最多 3 次

T2: CTS 到 DT 的响应时间
  默认 50ms
  超时: 接收方发 Conn_Abort

T3: DT 包之间间隔
  默认 200ms
  超时: 接收方发 Conn_Abort

T4: 总传输时间
  默认 1050ms
  超时: 任何一方发 Conn_Abort
```

### Conn_Abort 处理

```c
/* 任何一方发 Conn_Abort, 双方结束会话 */
/* 异常情况:
   - buffer 满
   - 协议错
   - 超时
   - 应用层要求终止
*/
```

## TP 工具和库

### 开源库

```text
- Canard (C++, 嵌入式)
- libj1939 (Linux, C)
- SocketCAN J1939 (Linux 内核)
- cantools (Python, 解析 DBC + TP)
```

### Linux SocketCAN J1939

```c
/* Linux 4.6+ 内核支持 J1939 协议族 */
/* 像 SocketCAN 一样, 但 J1939 直接调用 */

#include <linux/can/j1939.h>

int s = socket(PF_CAN, SOCK_DGRAM, CAN_J1939);

/* 绑定 (类似 SocketCAN) */
struct sockaddr_can addr = {
    .can_family = AF_CAN,
    .can_ifindex = ifr.ifr_ifindex,
    .can_addr.j1939 = {
        .name = 0x1234567890ABCDEFULL,
        .pgn = J1939_PGN_TP_CM,
        .addr = 0x28,  /* 自己的地址 */
    },
};
bind(s, (struct sockaddr *)&addr, sizeof(addr));

/* 发送 TP.DT (需要内核支持) */
struct j1939_sk_buff jsk = {
    .skb = skb,  /* CAN 帧数据 */
    .addr = {
        .src_name = 0x1234567890ABCDEFULL,
        .dst_name = 0xFEDCBA0987654321ULL,
        .pgn = pgn,
        .addr = dst_addr,
    },
};
sendmsg(s, ...);
```

## 实战注意事项

### 1. 多 TP 会话管理

```text
每个地址对 (src, dst) 只能有 1 个 TP 会话
全局或按 (src, dst) 索引的会话表
新会话来时, 看是否有冲突
```

### 2. 大数据传输 ( > 1785 字节)

```text
1785 = 255 包 * 7 字节/包
超过 1785 字节, 必须分多个 TP 会话
每会话 1785 字节, 收方重组
```

### 3. TP 期间其他报文处理

```text
TP 传输期间, 普通 PGN 报文照常处理
但不能并发多个 TP 会话 (同一对 src+dst)
```

### 4. 心跳与 TP 配合

```text
TP 传输期间, ECU 心跳 (PGN 65260) 仍要发
不能用 TP 占住整个 ECU
```

## 7 条 TP 常见错误

| # | 错误 | 后果 |
| --- | --- | --- |
| 1 | 用 BAM 发固件 | 丢包不能恢复 |
| 2 | 包号错乱 | 数据错位 |
| 3 | CTS 字段填错 | 传输错乱 |
| 4 | 不等 CTS 就发 DT | 接收方不收 |
| 5 | 多个 TP 会话冲突 | 会话混乱 |
| 6 | 超时不处理 | 永久卡住 |
| 7 | Conn_Abort 不处理 | 重试无果 |

## 关联文档

- `j1939-deep-dive.md` 原理
- `j1939-practical.md` 速查
- `j1939-failure-cases.md` 产线案例
- `j1939-network-management.md` 地址声明 / 网络管理
- `j1939-index.md` 导航
- `bus/iso-tp-deep-dive.md` ISO-TP (类似, 但用于 UDS)
- `can-failure-cases.md` CAN 基础
- `can-multimaster-and-bus-off.md` CAN 多 master
