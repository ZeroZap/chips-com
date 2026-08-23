# CAN 多 Master 仲裁与 Bus Off 专题

## 目标

CAN 是多 master 总线, 仲裁机制是核心。本文讲清楚:
- 多 master 仲裁的物理原理
- 应用层调度策略
- 错误计数器 (TEC/REC) 详细行为
- 节点状态机 (Active / Passive / Bus Off)
- Bus Off 后的恢复机制
- 实战代码骨架

## 多 Master 仲裁的物理原理

### 显性优先特性

```text
CAN 总线电气特性:
  显性 (dominant, 0): 主动拉低总线, 多设备同时拉低还是低
  隐性 (recessive, 1): 释放总线, 靠上拉电阻回高

多个设备同时发:
  - 一个发显性, 一个发隐性 -> 总线 = 显性
  - 这就是"显性优先"
```

**关键**: 这是 CAN 仲裁的物理基础。

### 仲裁过程 (逐位)

```text
时序: 所有节点同时开始发, 逐位听
1. SOF (显性位): 所有节点看到 dominant, 继续
2. ID bit 10 (MSB): 节点 A 发 0, 节点 B 发 1
   - 总线 = 0 (dominant)
   - 节点 A: 发 0, 听 0, 一致, 继续
   - 节点 B: 发 1, 听 0, 不一致! -> 仲裁失败, 立即退出
3. ID bit 9-0: 节点 A 继续, 节点 B 沉默
4. 节点 A 完成整帧发送
5. 节点 B 自动重试 (应用层不需要管)
```

**特点**:
- **非破坏性仲裁**: 失败的节点不破坏赢的节点的帧
- **ID 越小, 优先级越高**: 因为 ID 0 比 ID 1 更早出现显性位
- **应用层无感**: 失败节点自动重试, 上层 API 看到的就是成功

### 仲裁时序示例

```text
节点 A: 0x123 (优先级中)
节点 B: 0x456 (优先级低)
节点 C: 0x058 (优先级高)

bit 10: A=0, B=0, C=0  -> 总线 0, 全部继续
bit  9: A=0, B=1, C=1  -> 总线 0
         B 发 1 听 0 -> B 退出
         C 发 1 听 0 -> C 退出
bit  8-0: A 单独发, 完成

赢: A
```

## 节点状态机

### 3 个状态

```text
Error Active (主动错误):
  - TEC <= 127, REC <= 127
  - 正常状态
  - 发"主动错误帧" (6 dominant 位)
  - 强制其他节点看到错误

Error Passive (被动错误):
  - TEC > 127 或 REC > 127
  - 降级状态
  - 发"被动错误帧" (6 recessive 位)
  - 不影响其他节点
  - 发送后必须等待 8 bit 暂停时间 (挂起发送)

Bus Off (总线关闭):
  - TEC > 255
  - 节点完全脱离总线
  - 不再发任何帧
  - 必须软件 reset 重新加入
```

### 状态转移图

```text
Error Active
  |   ↑ 错误消失 (TEC/REC 减 1)
  |   |
  |   | TEC 或 REC > 127
  |   ↓
  | Error Passive
  |   |   ↑ 错误消失
  |   |   |
  |   |   | TEC > 255
  |   |   ↓
  |   | Bus Off
  |   |   |   ↑ 128 次 11 recessive 位
  |   |   |   | (AutoBusOff)
  |   |   |   ↓
  |   | Error Active
```

## 错误计数器 (TEC/REC) 规则

### 基础规则 (CAN 2.0)

```text
发送方:
  发送错误 -> TEC + 8
  发送成功 (ACK 收到) -> TEC - 1 (>= 0)
  错误时如果已经 passive -> TEC + 1 而不是 + 8

接收方:
  接收错误 -> REC + 8
  接收成功 (CRC 校验过) -> REC - 1 (>= 0)
  接收错误时如果已经 passive -> REC + 1 而不是 + 8

特殊规则 (CAN 2.0):
  - 发送方发送 1 bit 但听到 1 bit (隐性), 而应该是 0 (显性): TEC + 8
  - 但在仲裁阶段, 发送 1 听 0 是预期的, 不算错误
  - 在 ACK 阶段, 发送方不会算 ACK 错误
```

### 快速增加场景

```text
总线严重错 (波特率算错):
  节点发, 听不一致 -> TEC + 8
  持续几十次 -> TEC > 127 (passive)
  再持续几十次 -> TEC > 255 (bus off)

接收大量错误帧:
  别人发错误帧, 我方接收错误 -> REC + 8
  但 REC 增长慢于 TEC
  REC 达到 127 通常表示总线上有其他节点故障
```

### 减少规则 (谨慎)

```text
- 每成功发送 1 帧, TEC 减 1 (但 >= 0)
- 每成功接收 1 帧, REC 减 1 (但 >= 0)
- 减少速度很慢, 1 个成功帧 = 1 减
- 长期错误累积, 短期难以恢复
```

**关键**: 进入 passive / bus off 不容易, 但**恢复更慢**。

## 主动错误帧 vs 被动错误帧

### 主动错误帧 (Error Active)

```text
节点检测到错误:
  -> 中断当前帧
  -> 发 6 个 dominant 位 (主动错误标志)
  -> 8 bit recessive (错误定界符)
  -> 其他节点看到 dominant 也认为有错, 也会发错误帧
  -> 总线上看起来 6-12 个 dominant 位
```

### 被动错误帧 (Error Passive)

```text
节点 (在 passive 状态) 检测到错误:
  -> 中断当前帧
  -> 发 6 个 recessive 位 (被动错误标志)
  -> 等待其他节点 (active) 发 6 个 dominant
  -> 然后 8 bit recessive (错误定界符)
  -> 总线上至少 6 个 dominant (来自 active 节点)
```

**关键区别**:
- 主动错误帧: 6 个 dominant, 强制其他节点看到
- 被动错误帧: 6 个 recessive, 不影响其他节点

**后果**: 大量被动错误节点 = 总线上看不到错误, 但 REC 还在涨。

## Bus Off 恢复机制

### 3 种 Bus Off 恢复

#### 1. AutoBusOff (硬件自动)

```c
/* STM32 HAL */
hcan1.Init.AutoBusOff = ENABLE;
/* 进入 bus off 后:
   1. 控制器停止参与总线活动
   2. 检测 128 次 11 个 recessive 位 (约 0.2s @ 1M)
   3. 重新进入 Error Active
   4. 自动恢复
*/
```

**优点**: 不需要软件干预
**缺点**: 自动恢复, 但根因没解决, 可能再次 bus off

#### 2. 软件手动恢复

```c
/* 监控 bus off, 手动 reset */
void can_check_bus_off() {
    if (hcan1.Instance->ESR & CAN_ESR_BOFF) {
        HAL_CAN_Stop(&hcan1);
        HAL_Delay(100);
        /* 清除错误状态 */
        hcan1.Instance->MCR |= CAN_MCR_RESET;
        while (hcan1.Instance->MCR & CAN_MCR_RESET);
        /* 重新初始化 */
        HAL_CAN_Init(&hcan1);
        HAL_CAN_Start(&hcan1);
    }
}
```

**优点**: 恢复前可以记录错误状态, 上报
**缺点**: 需要周期性检查

#### 3. 完全离线 (不恢复)

某些关键场景 (汽车安全 ECU) 进 bus off 后**永远不再连**, 等待人工维护。

### 恢复时序

```text
Bus Off
  ↓
 等待 128 × 11 recessive 位
  (在 1 Mbaud 下: 128 × 11 × 1us = 1.4ms)
  ↓
 Error Active (但 TEC 仍较高)
  ↓
 继续发送, 错误计数慢慢恢复
  ↓
 正常
```

**关键**: 恢复后 TEC 不是 0, 是之前的数 (128), 需慢慢减回 0。

## 多 Master 调度的工程问题

### 问题 1: 高优先级报文垄断总线

```text
场景: ECU 发 0x100 (优先级最高), 周期 1ms
其他节点: 0x200, 0x300, 0x400

ECU 一直在发, 总线占用率 90%+
其他节点永远抢不到总线, 数据延迟 100ms+
```

**修复**:
```text
1. 限制最高优先级报文的发送频率
2. 应用层优先级反转 (周期报文用低 ID, 但发送周期长)
3. 用 CAN bridge / gateway 分段
```

### 问题 2: 报文雪崩, 总线饱和

```text
场景: 多个节点同时检测到事件, 都开始发报文
总线瞬间饱和, 错误率上升
```

**修复**:
```text
1. 应用层节流: 同一事件 N ms 内只发 1 次
2. 报文聚合: 多个事件打包成 1 个报文
3. 用周期报文替代事件报文
```

### 问题 3: 长时间未发送节点优先级反转

```text
场景: 节点 A 优先级高 (ID 小), 但平时不发
      节点 B 优先级低, 一直发
某时刻 A 需要发, 但 B 正在发, A 等 B 发完
A 的实时性降低
```

**修复**:
```text
1. 优先级分配: 高实时性 = 高优先级 (小 ID)
2. 不要给"不常发"的节点分配高优先级
3. 用 deadline scheduling
```

## 应用层优先级分配

### 优先级分配原则

```text
最高优先级 (ID 0x000-0x0FF):
  - 安全相关 (制动, 转向, 气囊)
  - 100Hz+ 高频报文
  - < 5ms 延迟要求

中优先级 (ID 0x100-0x3FF):
  - 动力总成 (发动机, 变速箱)
  - 50Hz 报文
  - < 10ms 延迟

低优先级 (ID 0x400-0x7FF):
  - 车身控制 (灯光, 雨刷, 门锁)
  - 10Hz 报文
  - < 50ms 延迟

最低优先级 (ID 0x700-0x7FF):
  - 诊断 (UDS)
  - 非实时
  - 100ms-1s 延迟可接受
```

### 真实 ID 分配示例 (DBC 文件)

```c
/* 假设 11 bit ID, 分配 16 个报文 */
BO_ 0x100 Steering_Angle: 8 Vector__XXX
BO_ 0x101 Steering_Torque: 6 Vector__XXX
BO_ 0x110 Engine_RPM: 8 Vector__XXX
BO_ 0x111 Vehicle_Speed: 6 Vector__XXX
BO_ 0x120 Brake_Pressure: 4 Vector__XXX
BO_ 0x121 ABS_Status: 2 Vector__XXX
BO_ 0x200 Battery_Voltage: 4 Vector__XXX
BO_ 0x201 Battery_Current: 4 Vector__XXX
BO_ 0x300 Light_Status: 3 Vector__XXX
BO_ 0x301 Door_Status: 2 Vector__XXX
BO_ 0x7DF UDS_Request: 8 Vector__XXX
BO_ 0x7E8 UDS_Response_ECU1: 8 Vector__XXX
```

**原则**:
- 安全报文 (制动, 转向) 最小 ID
- 动力次之
- 车身更小
- 诊断最大

## 接收过滤器配置

### 过滤器原理

```text
CAN 控制器有硬件 ID 过滤器, 减少 CPU 中断负担

每个过滤器:
  - ID + Mask 模式: (received_id & mask) == (filter_id & mask)
  - 或列表模式: received_id in [filter_id1, filter_id2, ...]

不匹配的 ID: 直接丢弃, 不进入 FIFO
```

### STM32 HAL 过滤器配置

```c
CAN_FilterTypeDef filter;

/* 例 1: 单 ID 过滤 */
filter.FilterBank = 0;
filter.FilterMode = CAN_FILTERMODE_IDMASK;
filter.FilterScale = CAN_FILTERSCALE_32BIT;
filter.FilterIdHigh = 0x100 << 5;        /* ID = 0x100 */
filter.FilterIdLow = 0x0000;
filter.FilterMaskIdHigh = 0x7FF << 5;    /* 11 bit ID */
filter.FilterMaskIdLow = 0x0000;
filter.FilterFIFOAssignment = CAN_RX_FIFO0;
filter.FilterActivation = ENABLE;
HAL_CAN_ConfigFilter(&hcan1, &filter);

/* 例 2: 多 ID 过滤 (用 2 个过滤器 bank) */
filter.FilterBank = 1;
filter.FilterIdHigh = 0x110 << 5;
HAL_CAN_ConfigFilter(&hcan1, &filter);

filter.FilterBank = 2;
filter.FilterIdHigh = 0x120 << 5;
HAL_CAN_ConfigFilter(&hcan1, &filter);

/* 例 3: 范围过滤 (0x100-0x1FF) */
filter.FilterIdHigh = 0x100 << 5;        /* 起始 ID */
filter.FilterMaskIdHigh = 0x700 << 5;    /* mask: 忽略 bit 8-10 */
HAL_CAN_ConfigFilter(&hcan1, &filter);
```

**关键**: 过滤器配错, 节点收不到任何帧。

## 监控错误计数器

### STM32 HAL 监控

```c
void can_monitor() {
    uint32_t esr = hcan1.Instance->ESR;
    uint8_t tec = (esr >> 24) & 0xFF;
    uint8_t rec = (esr >> 16) & 0xFF;
    uint8_t lec = (esr >> 0) & 0x7;     /* Last Error Code */
    
    if (tec > 0 || rec > 0) {
        log_warn("can: tec=%d rec=%d lec=%d", tec, rec, lec);
    }
    
    if (esr & CAN_ESR_BOFF) {
        log_error("can: bus off");
    }
    
    if (esr & CAN_ESR_EPVF) {
        log_warn("can: error passive");
    }
    
    /* Last Error Code 解码 */
    const char *lec_msg[] = {
        "no error", "stuff error", "form error", "ack error",
        "bit recessive error", "bit dominant error", "crc error",
        "set by software"
    };
    if (lec < 8) {
        log_debug("can: lec=%s", lec_msg[lec]);
    }
}
```

### 应用层响应

```c
void can_error_handler() {
    uint8_t tec = (hcan1.Instance->ESR >> 24) & 0xFF;
    uint8_t rec = (hcan1.Instance->ESR >> 16) & 0xFF;
    
    if (hcan1.Instance->ESR & CAN_ESR_BOFF) {
        /* 严重: 节点脱离总线 */
        log_error("CAN bus off, reset");
        HAL_CAN_Stop(&hcan1);
        HAL_Delay(1000);  /* 长时间等待 */
        HAL_CAN_Start(&hcan1);
        /* 上报应用层 */
        fault_report(CAN_FAULT_BUSOFF);
    } else if (tec > 200) {
        /* 接近 bus off, 主动停止发 */
        log_warn("CAN tec=%d, halt tx", tec);
        can_tx_enabled = false;
    } else if (tec < 50 && !can_tx_enabled) {
        /* 恢复, 重新允许发 */
        log_info("CAN tec=%d, resume tx", tec);
        can_tx_enabled = true;
    }
}
```

## 多 Master 调度的工程实践

### 周期报文 vs 事件报文

```text
周期报文:
  - 按固定周期发 (1ms / 10ms / 100ms)
  - 适合: 实时 sensor 数据 (速度, 温度)
  - 优点: 应用层处理简单
  - 缺点: 浪费总线带宽 (数据没变化也发)

事件报文:
  - 事件触发才发
  - 适合: 状态变化 (门开, 灯亮)
  - 优点: 节省带宽
  - 缺点: 多个事件可能雪崩, 需要应用层节流
```

### 报文聚合

```text
场景: 车身控制 10 个开关
  不用事件报文: 10 个独立报文
  聚合: 1 个 8 字节报文, bit 0-9 表示 10 个开关状态
```

**优点**: 减少总线负载, 减少仲裁次数
**缺点**: 单个 bit 变化也发整个报文 (可以加变化检测)

### 总线利用率上限

```text
推荐:
  - 正常运行: < 50% 利用率
  - 峰值瞬时: < 70% 利用率
  - 永远不超: > 80% 利用率

超过 70% 时:
  - 增加总线带宽 (1M -> CAN FD 2M / 5M)
  - 减少报文频率
  - 增加总线 (网关分段)
```

## 实战: 完整多 Master CAN 节点

```c
/* can_node.h */
typedef struct {
    CAN_HandleTypeDef *hcan;
    uint8_t node_id;
    volatile bool tx_enabled;
    volatile uint32_t tec;
    volatile uint32_t rec;
    volatile uint32_t bus_off_count;
    volatile uint32_t last_recovery_tick;
} can_node_t;

int can_node_init(can_node_t *node, CAN_HandleTypeDef *hcan, uint8_t node_id);
int can_node_send(can_node_t *node, uint32_t can_id, uint8_t *data, uint8_t len);
void can_node_monitor(can_node_t *node);
int can_node_recover(can_node_t *node);

/* can_node.c */
int can_node_init(can_node_t *node, CAN_HandleTypeDef *hcan, uint8_t node_id) {
    node->hcan = hcan;
    node->node_id = node_id;
    node->tx_enabled = true;
    node->bus_off_count = 0;
    
    hcan->Init.AutoBusOff = ENABLE;        /* 硬件自动恢复 */
    hcan->Init.AutoRetransmission = ENABLE; /* 自动重传 */
    hcan->Init.AutoWakeUp = DISABLE;       /* 不用 wake up */
    hcan->Init.ReceiveFifoLocked = DISABLE;
    hcan->Init.TransmitFifoPriority = ENABLE;
    HAL_CAN_Init(hcan);
    
    /* 启动 */
    HAL_CAN_Start(hcan);
    
    /* 启用接收 */
    HAL_CAN_ActivateNotification(hcan, CAN_IT_RX_FIFO0_MSG_PENDING | 
                                       CAN_IT_ERROR | 
                                       CAN_IT_BUSOFF);
    return 0;
}

int can_node_send(can_node_t *node, uint32_t can_id, uint8_t *data, uint8_t len) {
    if (!node->tx_enabled) {
        return -EBUSY;
    }
    
    CAN_TxHeaderTypeDef header;
    header.StdId = can_id;
    header.IDE = CAN_ID_STD;
    header.RTR = CAN_RTR_DATA;
    header.DLC = len;
    header.TransmitGlobalTime = DISABLE;
    
    uint32_t mailbox;
    HAL_StatusTypeDef ret = HAL_CAN_AddTxMessage(node->hcan, &header, data, &mailbox);
    return (ret == HAL_OK) ? 0 : -EIO;
}

void can_node_monitor(can_node_t *node) {
    uint32_t esr = node->hcan->Instance->ESR;
    node->tec = (esr >> 24) & 0xFF;
    node->rec = (esr >> 16) & 0xFF;
    
    /* 主动 / 被动 / Bus Off 状态 */
    if (esr & CAN_ESR_BOFF) {
        /* Bus Off */
        node->tx_enabled = false;
        node->bus_off_count++;
        node->last_recovery_tick = HAL_GetTick();
        log_error("node %d: CAN bus off (tec=%d rec=%d)",
                  node->node_id, node->tec, node->rec);
    } else if (esr & CAN_ESR_EPVF) {
        /* Error Passive */
        node->tx_enabled = false;
        log_warn("node %d: CAN error passive (tec=%d rec=%d)",
                 node->node_id, node->tec, node->rec);
    } else {
        /* Error Active */
        if (node->tec < 50 && !node->tx_enabled) {
            /* 恢复, 重新允许发 */
            node->tx_enabled = true;
            log_info("node %d: CAN recovered (tec=%d rec=%d)",
                     node->node_id, node->tec, node->rec);
        }
    }
}

int can_node_recover(can_node_t *node) {
    HAL_CAN_Stop(node->hcan);
    HAL_Delay(100);
    /* 清除错误状态 */
    node->hcan->Instance->MCR |= CAN_MCR_RESET;
    while (node->hcan->Instance->MCR & CAN_MCR_RESET);
    HAL_CAN_Init(node->hcan);
    HAL_CAN_Start(node->hcan);
    HAL_CAN_ActivateNotification(node->hcan, CAN_IT_RX_FIFO0_MSG_PENDING | 
                                            CAN_IT_ERROR | 
                                            CAN_IT_BUSOFF);
    return 0;
}

/* 中断回调 */
void HAL_CAN_ErrorCallback(CAN_HandleTypeDef *hcan) {
    uint32_t err = hcan->ErrorCode;
    if (err & HAL_CAN_ERROR_BOF) {
        /* Bus off */
        can_node_t *node = hcan_to_node(hcan);
        can_node_monitor(node);
    }
}
```

## Linux SocketCAN 的多 master

Linux 也有多 master 处理:

```c
/* SocketCAN 多 master 节点 */
#include <linux/can.h>
#include <linux/can/raw.h>

int s;
struct sockaddr_can addr;
struct ifreq ifr;

s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
strcpy(ifr.ifr_name, "can0");
ioctl(s, SIOCGIFINDEX, &ifr);
addr.can_family = AF_CAN;
addr.can_ifindex = ifr.ifr_ifindex;
bind(s, (struct sockaddr *)&addr, sizeof(addr));

/* 发送: 多 master 仲裁由硬件做, 软件无感 */
struct can_frame frame;
frame.can_id = 0x123;
frame.can_dlc = 8;
memcpy(frame.data, data, 8);
write(s, &frame, sizeof(frame));

/* 错误监控: 用 netlink CAN error */
#include <linux/can/error.h>
```

## 产线根因预防清单

```text
□ ID 分配用 DBC 文件管理, 工具检查冲突
□ 高优先级报文限制频率
□ 报文聚合减少总线负载
□ 总线利用率 < 50% (运行) / < 70% (峰值)
□ AutoBusOff 开启
□ 错误计数器周期性监控和上报
□ 关键节点有软件 bus off 恢复 + 故障上报
□ 接收过滤器严格配
□ 周期报文 + 事件报文混合使用, 事件报文节流
□ 报文优先级 + 应用层 deadline 调度匹配
□ 多 master 场景测试 (用 CAN stress 工具)
□ 老化测试监控 TEC/REC 趋势
```

## 关联文档

- `can-practical.md` 速查
- `can-deep-dive.md` 原理
- `can-failure-cases.md` 产线死机案例
- `can-fd-and-can-xl.md` 演进
- `can-rtos-integration.md` RTOS + SocketCAN
- `can-vs-other-bus.md` 跨总线对比
- `can-index.md` 导航
- `bus/uds-*.md` UDS (诊断优先级)
- `bus/j1939-*.md` J1939 (商用车主从)
- `i2c-bus-recovery-playbook.md` I2C recovery (对比)
