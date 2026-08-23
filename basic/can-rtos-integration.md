# CAN RTOS 集成与 Linux SocketCAN

## 目标

把 CAN 驱动集成到 RTOS + Linux 系统中。覆盖:
- RT-Thread / Zephyr / FreeRTOS 三平台集成模式
- Linux SocketCAN 编程模型
- 多 task 共享 CAN 控制器
- 错误处理和重连
- 实战代码骨架

## 三个 RTOS 的 CAN 抽象

```text
RT-Thread
  rt_can_device
  client 调用: rt_can_send() / rt_can_recv()
  bus 持有: mutex

Zephyr
  can_dt_spec
  client 调用: can_send() / can_receive() / can_transmit() / can_add_rx_filter()
  支持 CAN FD

FreeRTOS
  无标准 CAN 抽象
  各家 SDK 自己实现 (STM32 HAL / NXP MCUXpresso / Nordic nrfx)
  通用做法: CAN_Adapter_t + xSemaphore
```

## RT-Thread 实现

### 总线结构

```c
struct rt_can_bus {
    struct rt_can_device *can_dev;
    enum {
        RT_CAN_BUS_NORMAL = 0,
        RT_CAN_BUS_XFER,
        RT_CAN_BUS_ERROR,
        RT_CAN_BUS_BUSOFF,
    } state;
    struct rt_mutex bus_lock;
    struct rt_semaphore tx_done_sem;
    struct rt_semaphore rx_done_sem;
    /* 统计 */
    atomic_t tx_count;
    atomic_t rx_count;
    atomic_t err_count;
    atomic_t bus_off_count;
};
```

### 客户端事务入口

```c
rt_size_t rt_can_send_with_lock(struct rt_can_device *dev,
                                 struct rt_can_msg *msg)
{
    struct rt_can_bus *bus = dev->priv;
    rt_size_t ret;

    rt_mutex_take(&bus->bus_lock, RT_WAITING_FOREVER);
    bus->state = RT_CAN_BUS_XFER;

    ret = rt_device_write(&dev->parent, 0, msg, sizeof(*msg));

    if (ret != sizeof(*msg)) {
        bus->state = RT_CAN_BUS_ERROR;
        atomic_fetch_add(&bus->err_count, 1);
    } else {
        bus->state = RT_CAN_BUS_NORMAL;
        atomic_fetch_add(&bus->tx_count, 1);
    }

    rt_mutex_release(&bus->bus_lock);
    return ret;
}
```

## Zephyr 实现

### 关键 API

```c
/* 同步 API */
int can_send(const struct device *dev, struct can_frame *frame, 
             can_tx_callback_t callback, void *user_data);
int can_receive(const struct device *dev, can_rx_callback_t callback, 
                void *user_data);
int can_add_rx_filter(const struct device *dev, can_rx_callback_t callback,
                      void *user_data, const struct can_filter *filter);

/* CAN FD */
int can_send_fd(const struct device *dev, struct canfd_frame *frame, ...);
```

### 客户端代码

```c
static const struct device *can_dev = DEVICE_DT_GET(DT_NODELABEL(can1));

/* 发送回调 */
static void can_tx_callback(const struct device *dev, int error, void *user_data) {
    if (error != 0) {
        LOG_WRN("CAN tx error: %d", error);
    }
}

static int send_can_frame(uint32_t can_id, uint8_t *data, uint8_t len) {
    struct can_frame frame = {0};
    frame.id = can_id;
    frame.dlc = len;
    memcpy(frame.data, data, len);
    
    return can_send(can_dev, &frame, can_tx_callback, NULL);
}

/* 接收回调 */
static void can_rx_callback(const struct device *dev, struct can_frame *frame,
                            void *user_data) {
    LOG_DBG("RX id=0x%03x dlc=%d", frame->id, frame->dlc);
    process_can_frame(frame);
}

/* 启动接收 */
int start_can_rx() {
    struct can_filter filter = {
        .flags = CAN_FILTER_DATA,
        .id = 0x123,
        .mask = CAN_STD_ID_MASK,
    };
    return can_add_rx_filter(can_dev, can_rx_callback, NULL, &filter);
}
```

## FreeRTOS 实现

### Adapter 模式

```c
typedef struct {
    CAN_HandleTypeDef *hcan;
    SemaphoreHandle_t bus_mutex;
    SemaphoreHandle_t tx_done_sem;
    QueueHandle_t rx_queue;
    volatile bool tx_busy;
    volatile uint32_t tx_count;
    volatile uint32_t rx_count;
    volatile uint32_t err_count;
} can_adapter_t;

int can_adapter_init(can_adapter_t *adap, CAN_HandleTypeDef *hcan) {
    adap->hcan = hcan;
    adap->bus_mutex = xSemaphoreCreateMutex();
    adap->tx_done_sem = xSemaphoreCreateBinary();
    adap->rx_queue = xQueueCreate(16, sizeof(struct can_frame));
    return 0;
}

int can_adapter_send(can_adapter_t *adap, uint32_t can_id, 
                     uint8_t *data, uint8_t len) {
    if (adap->tx_busy) return -EBUSY;
    
    xSemaphoreTake(adap->bus_mutex, portMAX_DELAY);
    adap->tx_busy = true;
    
    CAN_TxHeaderTypeDef tx_header;
    uint32_t mailbox;
    
    tx_header.StdId = can_id;
    tx_header.IDE = CAN_ID_STD;
    tx_header.RTR = CAN_RTR_DATA;
    tx_header.DLC = len;
    
    HAL_StatusTypeDef ret = HAL_CAN_AddTxMessage(adap->hcan, &tx_header, 
                                                  data, &mailbox);
    if (ret != HAL_OK) {
        adap->tx_busy = false;
        xSemaphoreGive(adap->bus_mutex);
        return -EIO;
    }
    
    /* 等发送完成 */
    if (xSemaphoreTake(adap->tx_done_sem, pdMS_TO_TICKS(1000)) != pdTRUE) {
        HAL_CAN_AbortTxRequest(adap->hcan, mailbox);
        adap->tx_busy = false;
        xSemaphoreGive(adap->bus_mutex);
        return -ETIMEDOUT;
    }
    
    adap->tx_busy = false;
    xSemaphoreGive(adap->bus_mutex);
    return 0;
}

int can_adapter_recv(can_adapter_t *adap, struct can_frame *frame, 
                     uint32_t timeout_ms) {
    if (xQueueReceive(adap->rx_queue, frame, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        return -ETIMEDOUT;
    }
    return 0;
}

/* 中断回调 */
void HAL_CAN_TxMailbox0CompleteCallback(CAN_HandleTypeDef *hcan) {
    BaseType_t hp_woken = pdFALSE;
    xSemaphoreGiveFromISR(g_can_adapter.tx_done_sem, &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
}

void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan) {
    CAN_RxHeaderTypeDef rx_header;
    uint8_t rx_data[8];
    
    HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &rx_header, rx_data);
    
    struct can_frame frame;
    frame.id = rx_header.StdId;
    frame.dlc = rx_header.DLC;
    memcpy(frame.data, rx_data, rx_header.DLC);
    
    BaseType_t hp_woken = pdFALSE;
    xQueueSendFromISR(g_can_adapter.rx_queue, &frame, &hp_woken);
    portYIELD_FROM_ISR(hp_woken);
}
```

## Linux SocketCAN

### SocketCAN 简介

Linux 内核自带的 CAN 协议栈, 把 CAN 当成 socket 接口。优势:
- 统一 BSD socket 编程模型
- 内置 CAN 字符设备
- 支持多协议 (CAN, CAN FD, CAN XL)
- 内核态网络协议 (CAN, CAN over IP)

### 基础编程: 打开 + 绑定

```c
#include <linux/can.h>
#include <linux/can/raw.h>
#include <sys/socket.h>
#include <net/if.h>
#include <string.h>
#include <unistd.h>

int can_open(const char *ifname) {
    int s;
    struct sockaddr_can addr;
    struct ifreq ifr;
    
    /* 1. 创建 socket */
    s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (s < 0) {
        perror("socket");
        return -1;
    }
    
    /* 2. 获取接口索引 */
    strcpy(ifr.ifr_name, ifname);
    ioctl(s, SIOCGIFINDEX, &ifr);
    
    /* 3. 绑定 */
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifr_ifindex;
    bind(s, (struct sockaddr *)&addr, sizeof(addr));
    
    return s;
}
```

### 发送 CAN 帧

```c
int can_send(int s, uint32_t can_id, uint8_t *data, uint8_t len) {
    struct can_frame frame;
    
    frame.can_id = can_id;        /* 11 bit ID, 标准帧 */
    /* frame.can_id = can_id | CAN_EFF_FLAG; */ /* 29 bit ID */
    frame.can_dlc = len;
    memcpy(frame.data, data, len);
    
    return write(s, &frame, sizeof(frame));
}
```

### 接收 CAN 帧

```c
int can_recv(int s, struct can_frame *frame) {
    int n = read(s, frame, sizeof(*frame));
    if (n < 0) {
        perror("read");
        return -1;
    }
    if (n < sizeof(*frame)) {
        return -1;
    }
    return 0;
}

/* 也可以用 select / poll 异步收 */
fd_set rfds;
FD_ZERO(&rfds);
FD_SET(s, &rfds);
struct timeval tv = { .tv_sec = 1, .tv_usec = 0 };
int ret = select(s + 1, &rfds, NULL, NULL, &tv);
if (ret > 0 && FD_ISSET(s, &rfds)) {
    can_recv(s, &frame);
}
```

### 过滤器

```c
/* 只接收 ID = 0x123 或 0x456 */
struct can_filter filter[2];
filter[0].can_id = 0x123;
filter[0].can_mask = CAN_SFF_MASK;  /* 11 bit 标准帧 */
filter[1].can_id = 0x456;
filter[1].can_mask = CAN_SFF_MASK;
setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, filter, sizeof(filter));

/* 不过滤, 接收所有帧 */
setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, NULL, 0);

/* 错误帧 (Linux 内核会接收错误) */
int recv_own_msgs = 1;
setsockopt(s, SOL_CAN_RAW, CAN_RAW_RECV_OWN_MSGS, &recv_own_msgs, sizeof(int));
```

### 错误处理

```c
/* SocketCAN 错误帧: can_id 有特殊位 */
if (frame.can_id & CAN_ERR_FLAG) {
    /* 错误帧 */
    if (frame.can_id & CAN_ERR_BUSOFF) {
        log_error("can bus off");
    }
    if (frame.can_id & CAN_ERR_CRTL) {
        log_warn("can controller error");
    }
    if (frame.can_id & CAN_ERR_PROT) {
        log_warn("can protocol error");
    }
}

/* 也可以订阅错误 */
struct can_filter err_filter = {
    .can_id = CAN_ERR_FLAG,
    .can_mask = CAN_ERR_FLAG,
};
setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, &err_filter, sizeof(err_filter));
```

### CAN FD

```c
#include <linux/canfd.h>

int can_fd_open(const char *ifname) {
    int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    /* ... bind ... */
    
    /* 启用 CAN FD */
    int enable_canfd = 1;
    setsockopt(s, SOL_CAN_RAW, CAN_RAW_FD_FRAMES, &enable_canfd, sizeof(int));
    
    return s;
}

int can_fd_send(int s, uint32_t can_id, uint8_t *data, uint8_t len) {
    struct canfd_frame frame;
    
    frame.can_id = can_id;
    frame.len = len;        /* CAN FD: 0-64 */
    frame.flags = CANFD_BRS | CANFD_ESI;  /* 数据段加速 + 错误状态 */
    memcpy(frame.data, data, len);
    
    return write(s, &frame, sizeof(frame));
}
```

## 多任务并发

### 场景

```text
Task A: 周期性发 0x100 报文 (10ms 周期)
Task B: 接收 0x200 报文, 处理业务
Task C: 发送 0x300 报文 (事件触发)
Task D: OBD 诊断请求 (0x7DF)
```

3 个 task 都用 CAN1, 需要 mutex 串行化。

### 单 mutex

```c
static SemaphoreHandle_t g_can1_mutex;

int can1_send_safe(...) {
    xSemaphoreTake(g_can1_mutex, portMAX_DELAY);
    /* HAL_CAN_AddTxMessage */
    /* 等发送完成 */
    xSemaphoreGive(g_can1_mutex);
    return 0;
}
```

**问题**: 任务 A 周期 10ms, 任务 D 诊断 100ms, 互斥阻塞会让 A 周期不准。

### 优化: 优先级反转

```c
/* 高优先级 task (A: 安全报文) 短事务 */
/* 低优先级 task (C: 事件) 长事务, 短可以等待 */

/* 用 mutex 加 timeout, 避免永久阻塞 */
if (xSemaphoreTake(g_can1_mutex, pdMS_TO_TICKS(5)) != pdTRUE) {
    return -ETIMEDOUT;  /* 短任务 timeout, 不影响系统 */
}
```

### 优化: 多 mailbox 优先级

```c
/* bxCAN 有 3 个发送 mailbox, 可用优先级调度 */
/* 高优先级报文放 mailbox 0, 低放 mailbox 1 */
/* 用 transmit priority 控制发送顺序 */
```

## Bus Off 恢复策略

### 策略 1: AutoBusOff (硬件)

```c
hcan1.Init.AutoBusOff = ENABLE;
/* 128 次 11 recessive 后自动恢复 */
/* 优点: 不需要软件干预 */
/* 缺点: 根因没解决, 反复 bus off */
```

### 策略 2: 软件监控 + 手动恢复

```c
void can_recovery_task(void *arg) {
    can_adapter_t *adap = (can_adapter_t *)arg;
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(100));
        
        uint32_t esr = adap->hcan->Instance->ESR;
        if (esr & CAN_ESR_BOFF) {
            /* Bus off, 强制恢复 */
            log_error("can: bus off, force reset");
            HAL_CAN_Stop(adap->hcan);
            HAL_Delay(1000);  /* 长时间等待 */
            HAL_CAN_Start(adap->hcan);
            adap->err_count++;
        }
    }
}
```

### 策略 3: 故障节点隔离

```c
/* Bus off 多次后, 节点主动脱离网络 */
/* 工业系统, 关键节点不能一直 "bus off - 恢复 - 再次 bus off" */

#define MAX_BUS_OFF 3
static uint32_t bus_off_count = 0;

void can_recovery_task(void *arg) {
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(100));
        if (esr & CAN_ESR_BOFF) {
            bus_off_count++;
            if (bus_off_count > MAX_BUS_OFF) {
                log_error("can: too many bus off, isolate");
                /* 报告应用层, 节点停用 CAN */
                can_isolated = true;
            } else {
                HAL_CAN_Stop(adap->hcan);
                HAL_Delay(5000);
                HAL_CAN_Start(adap->hcan);
            }
        }
    }
}
```

## 应用层任务设计

### 任务划分

```text
can_rx_task:   接收所有帧, 分发到对应处理 task
  - 用队列 (queue) 接收
  - 根据 ID 路由到不同处理 task
  - 高优先级帧优先处理

can_tx_task:   周期报文 / 事件报文发送
  - 周期报文用定时器触发
  - 事件报文用 queue 接收
  - 按优先级排序发送

can_monitor_task:  监控错误 / bus off
  - 周期性检查 TEC/REC
  - Bus off 恢复
  - 错误上报

can_diag_task:  诊断 (UDS)
  - 处理 0x7DF / 0x7E8 帧
  - 不影响其他任务
```

### 实战: 报文路由

```c
typedef enum {
    MSG_TYPE_SAFETY = 0,   /* 安全报文 (高优先级) */
    MSG_TYPE_CONTROL,      /* 控制报文 */
    MSG_TYPE_DIAG,         /* 诊断报文 */
    MSG_TYPE_INFO,         /* 信息报文 */
} msg_type_t;

typedef struct {
    msg_type_t type;
    can_frame_t frame;
} routed_msg_t;

QueueHandle_t g_can_rx_queue[4];

/* CAN 接收 ISR -> 路由 */
void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan) {
    CAN_RxHeaderTypeDef rx_header;
    uint8_t data[8];
    HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &rx_header, data);
    
    msg_type_t type;
    if (rx_header.StdId < 0x100) {
        type = MSG_TYPE_SAFETY;
    } else if (rx_header.StdId < 0x400) {
        type = MSG_TYPE_CONTROL;
    } else if (rx_header.StdId == 0x7DF || rx_header.StdId == 0x7E8) {
        type = MSG_TYPE_DIAG;
    } else {
        type = MSG_TYPE_INFO;
    }
    
    routed_msg_t msg = { .type = type };
    msg.frame.id = rx_header.StdId;
    msg.frame.dlc = rx_header.DLC;
    memcpy(msg.frame.data, data, rx_header.DLC);
    
    xQueueSendFromISR(g_can_rx_queue[type], &msg, NULL);
}
```

## Linux 完整实战

```c
/* can_node.c - Linux SocketCAN 完整实现 */

#include <linux/can.h>
#include <linux/can/raw.h>
#include <sys/socket.h>
#include <net/if.h>
#include <sys/select.h>
#include <unistd.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    int sock;
    pthread_t rx_thread;
    volatile int running;
    /* 用户回调 */
    void (*on_frame)(const struct can_frame *frame, void *user);
    void *user_data;
} can_node_t;

void *can_rx_thread(void *arg) {
    can_node_t *node = (can_node_t *)arg;
    struct can_frame frame;
    fd_set rfds;
    
    while (node->running) {
        FD_ZERO(&rfds);
        FD_SET(node->sock, &rfds);
        struct timeval tv = { .tv_sec = 1, .tv_usec = 0 };
        
        int ret = select(node->sock + 1, &rfds, NULL, NULL, &tv);
        if (ret < 0) {
            perror("select");
            break;
        }
        if (ret == 0) continue;  /* timeout */
        if (!FD_ISSET(node->sock, &rfds)) continue;
        
        int n = read(node->sock, &frame, sizeof(frame));
        if (n < (int)sizeof(frame)) continue;
        
        if (frame.can_id & CAN_ERR_FLAG) {
            /* 错误帧处理 */
            if (frame.can_id & CAN_ERR_BUSOFF) {
                printf("CAN bus off\n");
            }
            continue;
        }
        
        if (node->on_frame) {
            node->on_frame(&frame, node->user_data);
        }
    }
    return NULL;
}

int can_node_start(can_node_t *node, const char *ifname) {
    struct sockaddr_can addr;
    struct ifreq ifr;
    
    node->sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (node->sock < 0) return -1;
    
    strcpy(ifr.ifr_name, ifname);
    ioctl(node->sock, SIOCGIFINDEX, &ifr);
    
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;
    if (bind(node->sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(node->sock);
        return -1;
    }
    
    node->running = 1;
    pthread_create(&node->rx_thread, NULL, can_rx_thread, node);
    return 0;
}

int can_node_send(can_node_t *node, const struct can_frame *frame) {
    return write(node->sock, frame, sizeof(*frame));
}
```

## CAN 产线压力测试

```text
1. 总线负载测试
   - 多节点高频率发帧
   - 测总线利用率 < 70%
   - 测 TEC/REC 不持续增长

2. 干扰测试
   - 电机启停瞬间
   - 继电器切换
   - 静电放电
   - 测错误率是否可恢复

3. 长时间老化
   - 1000 小时连续运行
   - 监控 TEC/REC 趋势
   - 监控错误帧率

4. 错误注入
   - CANH 短路 CANL
   - 终端电阻断开
   - 收发器拔掉
   - 节点断电
```

## 关联文档

- `can-practical.md` 速查
- `can-deep-dive.md` 原理
- `can-failure-cases.md` 产线死机案例
- `can-multimaster-and-bus-off.md` 多 master + bus off
- `can-fd-and-can-xl.md` 演进
- `can-vs-other-bus.md` 跨总线对比
- `can-index.md` 导航
- `bus/can-canopen-deep-dive.md` CANopen (RT-Thread 集成)
- `i2c-rtos-integration.md` I2C RTOS 集成 (对比)
- `spi-rtos-integration.md` SPI RTOS 集成 (对比)
- `uart-dma-circular-and-rtos.md` UART RTOS 集成 (对比)
