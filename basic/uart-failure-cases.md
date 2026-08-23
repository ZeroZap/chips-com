# UART 产线死机案例库

## 目标

把产线常见的 UART 通信失败、丢包、RS485 冲突、协议错位等写成案例库。每个案例:
- 现象 (现场)
- 抓波形 (判断)
- 定位 (根因)
- 修复 (代码 / 硬件)
- 复盘 (如何预防)

按主题分类, 配 `uart-deep-dive.md` / `uart-practical.md` 使用。

---

## 案例 1: 串口工具收不到 MCU 输出

### 现象

新板第一次跑, printf 输出的调试信息, 串口工具完全没收到。

### 抓波形

TX 引脚没有波形, 一直是高电平 (idle)。

### 定位

1. printf 根本没执行 (代码路径没走)
2. printf 走的是 ITM / SWO, 不是 UART
3. UART TX 引脚配错
4. UART 波特率配错 (虽然没数据, 但可能是初始化失败)

### 修复

```c
/* 1. 确认 printf 实际走的是 UART */
int fputc(int ch, FILE *f) {
    HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, 10);
    return ch;
}

/* 2. 确认 UART 引脚对 */
huart1.Instance = USART1;
huart1.Init.BaudRate = 115200;
huart1.Init.WordLength = UART_WORDLENGTH_8B;
huart1.Init.StopBits = UART_STOPBITS_1;
huart1.Init.Parity = UART_PARITY_NONE;
huart1.Init.Mode = UART_MODE_TX_RX;
HAL_UART_Init(&huart1);

/* 3. 确认 GPIO AF 配对 */
GPIO_InitStruct.Alternate = GPIO_AF7_USART1;
```

### 复盘

- printf 没数据, 90% 是初始化错
- 用示波器量 TX, 排查是软件问题还是硬件问题
- 串口工具先简单测 (回环测试)

---

## 案例 2: 收到的全是乱码, 像随机字符

### 现象

115200 8N1, 收到的是 "ÿþ" 或随机字符, 不是预期输出。

### 抓波形

TX 波形正常 (115200 baud), 但串口工具显示乱码。

### 定位

**最常见 3 个原因**:

1. **串口工具波特率配错** (115200 vs 9600 容易混)
2. **晶振不准** (内部 RC 振荡器误差太大)
3. **UART 时钟源配错** (PCLK 频率错)

### 修复

```c
/* 1. 用示波器量实际 baud */
/* TX 波形 1 bit 时长 = 1/baud */
/* 8.68us @ 115200, 104us @ 9600 */

/* 2. 确认晶振是外部 */
/* HSE_VALUE = 8000000 (8 MHz) */
/* 不能用内部 HSI (RC, 误差大) */

/* 3. 确认 UART 时钟源 */
huart1.ClockPrescaler = UART_PRESCALER_DIV1;
HAL_RCCEx_GetPeriphCLKConfig(&periph_clk_config);
```

### 复盘

- 乱码永远先查 baud
- 内部 RC 振荡器不能用于产线产品
- 用示波器量 TX 波形, 算实际 baud

---

## 案例 3: 偶发丢字节, 高速时严重

### 现象

9600 baud 不丢, 115200 baud 偶尔丢字节, 921600 baud 严重丢。

### 抓波形

接收波形正常, 但应用层读到的字节数比实际少。

### 定位

CPU 来不及读 RX FIFO, 溢出 (overrun error) 触发, 字节丢失。

```c
/* 错: 阻塞接收, 没开中断或 DMA */
uint8_t buf[100];
HAL_UART_Receive(&huart1, buf, 100, 1000);  /* 100ms 阻塞等待 100 字节 */
```

### 修复

```c
/* 对: DMA + 环形缓冲 */
HAL_UART_Receive_DMA(&huart1, rx_buf, RX_BUF_SIZE);

/* 中断里处理 DMA 完成 + idle 中断 */
void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size) {
    if (huart->Instance == USART1) {
        /* 处理 Size 字节 */
        process(rx_buf, Size);
        /* 重启 DMA */
        HAL_UARTEx_ReceiveToIdle_DMA(&huart1, rx_buf, RX_BUF_SIZE);
    }
}
```

### 复盘

- 高速 (>= 115200) 必须用 DMA
- 阻塞 HAL_UART_Receive 在 RTOS 里是大忌
- 开 idle 中断, 实现"不定长"接收

---

## 案例 4: RS485 方向控制时序错, 数据丢失

### 现象

RS485 总线挂 5 个从设备, 主站能发, 但从站响应有时收到有时收不到。

### 抓波形

主站 TX 时, DIR 引脚拉高 (发送模式), 数据发完, DIR 拉低 (接收模式), 但从站响应已经在 DIR 拉低前发完, 主站收不到。

### 定位

RS485 收发器 DIR 切换时序错, 应该**等发送完成 (TC) 后再切回接收**, 但代码用 TXE 切 (TXE 在最后一字节写入时立即触发, 数据还没发完)。

```c
/* 错: TXE 切回接收 (太早) */
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
    /* 实际是 TXE callback, 不是 TC */
    HAL_GPIO_WritePin(RS485_DIR_PORT, RS485_DIR_PIN, GPIO_PIN_RESET);  /* 错! */
}
```

### 修复

```c
/* 对: TC (Transmission Complete) 切回接收 */
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        /* 关键: 等 TC 标志, 最后一字节真正从移位寄存器发出 */
        while (!__HAL_UART_GET_FLAG(huart, UART_FLAG_TC));
        HAL_GPIO_WritePin(RS485_DIR_PORT, RS485_DIR_PIN, GPIO_PIN_RESET);
    }
}
```

或用 HAL 库 TC 中断:

```c
HAL_UART_Transmit_IT(&huart1, tx, len);
/* 在 TC callback 里切回接收 */
```

### 复盘

- RS485 DIR 切换必须用 TC, 不用 TXE
- 切回接收前, 留几个 bit 时间的 guard time
- 高波特率 + 长距离, 方向切换时序更敏感

---

## 案例 5: 多任务并发访问 UART, 发送错乱

### 现象

RTOS 2 个 task 都调 printf, 偶尔输出交错混乱, "Hello World" 变成 "HeWllo orld"。

### 抓波形

逻辑分析仪看, 2 个 task 的 TX 时序交叠, 数据混在一起。

### 定位

HAL_UART_Transmit 不是 thread-safe, 多个 task 共享 huart1, 状态被覆盖。

### 修复

```c
static SemaphoreHandle_t g_uart1_mutex;

int uart1_printf(const char *fmt, ...) {
    xSemaphoreTake(g_uart1_mutex, portMAX_DELAY);
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
    xSemaphoreGive(g_uart1_mutex);
    return 0;
}
```

### 复盘

- HAL 库不是 thread-safe
- 任何被多 task 访问的 UART, 必须 mutex
- printf 包装函数加 mutex

---

## 案例 6: 串口工具能收, MCU 收不到

### 现象

串口工具发 "AT\r\n", 期待 MCU 回 "OK\r\n", 但没收到。

### 抓波形

RX 波形正常, 串口工具发出来了, 但 MCU 的 RX 接收缓冲区没有数据。

### 定位

1. RX 引脚配错
2. UART 没开接收
3. 中断没开
4. 协议分帧错 (没识别到 \r\n)

```c
/* 错: 只开了 TX, 没开 RX */
HAL_UART_Init(&huart1);  /* Mode 默认是 TX_RX, 但是某些 HAL 配错 */

/* 错: 阻塞等待, 但超时太短 */
HAL_UART_Receive(&huart1, buf, 4, 10);  /* 10ms 超时, 串口工具发完 4 字节可能更慢 */
```

### 修复

```c
/* 对: 开 RX 中断 + 环形缓冲 */
HAL_UART_Receive_IT(&huart1, rx_buf, 1);  /* 字节中断 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    /* 处理 rx_buf[0] */
    /* 重新启动接收 */
    HAL_UART_Receive_IT(&huart1, rx_buf, 1);
}
```

或用 DMA + idle:

```c
HAL_UARTEx_ReceiveToIdle_DMA(&huart1, rx_buf, RX_BUF_SIZE);
```

### 复盘

- 接收必须用中断或 DMA
- 阻塞等待在不确定对方何时发的情况下不可靠
- 协议分帧是另一个层次的问题 (见案例 7)

---

## 案例 7: 协议分帧错, 字节流错乱

### 现象

串口收到 "Hello World", 应用层收到的却是 "lo World" 或 " Wor" 等不完整。

### 抓波形

接收数据正常, 但应用层解析错。

### 定位

UART 是字节流, **不天然保留消息边界**。应用层必须自己定义分帧规则:
- 固定长度
- 起始符 + 长度
- 文本协议 (\r\n)
- 超时分帧

**错做法**: 假设一次 read 能收到一个完整消息。

```c
/* 错: 假设一次 read 收到一个完整 AT 命令 */
HAL_UART_Receive(&huart1, buf, 4, 100);
/* 实际: 4 字节分 2 次到达, buf 只有前 2 字节 */
```

### 修复

```c
/* 对 1: 文本协议, 按 \r\n 分帧 */
void uart_rx_byte(uint8_t byte) {
    if (byte == '\n') {
        /* 一帧完成 */
        process_line(rx_buf, rx_pos);
        rx_pos = 0;
    } else if (byte != '\r') {
        rx_buf[rx_pos++] = byte;
    }
}

/* 对 2: 二进制协议, 按 SOF + LEN 分帧 */
void uart_rx_byte(uint8_t byte) {
    static uint8_t state = RX_SOF;
    static uint16_t len = 0;
    switch (state) {
    case RX_SOF:
        if (byte == 0xAA) state = RX_LEN_L;
        break;
    case RX_LEN_L:
        len = byte;
        state = RX_LEN_H;
        break;
    case RX_LEN_H:
        len |= (byte << 8);
        state = RX_DATA;
        rx_pos = 0;
        break;
    case RX_DATA:
        rx_buf[rx_pos++] = byte;
        if (rx_pos >= len) state = RX_CRC;
        break;
    case RX_CRC:
        /* 验证 CRC */
        if (verify_crc(rx_buf, len, byte)) {
            process_frame(rx_buf, len);
        }
        state = RX_SOF;
        break;
    }
}
```

### 复盘

- UART 是字节流, 协议必须自己分帧
- 任何"假设一次 read 收到完整消息"的代码都是错的
- 推荐: SOF + LEN + CMD + DATA + CRC 格式

---

## 案例 8: 内部 RC 振荡器导致 baud 漂移

### 现象

冷启动时通信正常, 板子工作 10 分钟后开始乱码。

### 抓波形

量 TX 波形, 早期 115200 baud 准确, 后期 114500 baud 漂移。

### 定位

MCU 用内部 RC 振荡器 (HSI), 温度上升时频率漂移。115200 baud 计算出错。

```c
/* 错: 内部 RC 振荡器 */
RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
RCC_OscInitStruct.HSIState = RCC_HSI_ON;
/* HSI 误差 1-2%, 温度漂移大 */
```

### 修复

```c
/* 对: 外部晶振 */
RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
RCC_OscInitStruct.HSEState = RCC_HSE_ON;
RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
/* HSE 8 MHz 误差 20 ppm */
```

### 复盘

- 产线产品必须用外部晶振
- 内部 RC 振荡器只能用于 boot 阶段或非关键通信
- 看温度曲线: 工业级 (-40~85°C) 晶振漂移 < 50 ppm

---

## 案例 9: 长距离 RS485 通信失败, 距离 > 1km

### 现象

100 m 正常, 500 m 偶尔失败, 1 km 频繁失败。

### 抓波形

500m 后波形畸变, 边沿变慢, 反射明显。

### 定位

长距离 RS485 信号完整性问题:
1. 线缆电容大, 边沿慢
2. 阻抗不匹配, 反射
3. 终端电阻缺失或错位

### 修复

```text
1. 加终端电阻 (120 ohm) 在总线两端
2. 降低 baud: 115200 改 9600
3. 用屏蔽双绞线, 屏蔽层单点接地
4. 加中继器 / 隔离器
5. 检查总线拓扑, 避免星形 / 分支
```

```c
/* STM32 RS485 终端电阻 (有些收发器内置) */
HAL_GPIO_WritePin(TERM_EN_PORT, TERM_EN_PIN, GPIO_PIN_SET);  /* 仅总线两端开启 */
```

### 复盘

- RS485 距离 = baud 反比
- 1200m @ 9600 baud
- 10m @ 10M baud
- 终端电阻关键, 缺了反射严重

---

## 案例 10: RS485 总线冲突, 多个设备同时发

### 现象

总线上 5 个设备, 偶发两个设备同时发, 数据被破坏。

### 抓波形

总线上同时出现两个设备的波形叠加, 看起来像噪声。

### 定位

总线上没有 master 仲裁, 多个设备抢总线。

**这是 RS485 的根本限制**: 物理层是半双工, 但协议层必须有 master。

```c
/* 错: 多从设备"自由"发 */
void slave_send() {
    HAL_UART_Transmit(&huart1, tx, 10, 100);  /* 没等 master 允许 */
}

/* 对: 严格主从, 只有 master 轮询 */
void master_poll_slave(uint8_t slave_addr) {
    send_request(slave_addr);
    wait_response_with_timeout();
}
```

### 修复

```text
1. 严格主从协议 (Modbus RTU 等)
2. 任何从设备只能在 master 询问后响应
3. 加 token / 地址机制防冲突
4. 业务层增加"我没在等响应"的检查
```

### 复盘

- RS485 物理层不能阻止冲突, 必须协议层防
- Modbus RTU 的"沉默间隔 3.5 字符"就是防冲突机制
- 详细见 `modbus-rs485-deep-dive.md`

---

## 案例 11: UART 中断里调 printf, 系统卡死

### 现象

UART 中断里调 printf, 系统卡死 1-2 秒, 期间其他中断进不来。

### 抓波形

正常, 但软件延迟大。

### 定位

printf 在中断里跑 1-2 ms, 阻塞了高优先级中断。

```c
/* 错 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    uint8_t byte = rx_buf[0];
    printf("RX: 0x%02X\n", byte);  /* 错! printf 跑 1-2 ms */
}
```

### 修复

```c
/* 对 1: 简单数据用 flag, 复杂数据用队列 */
volatile uint8_t g_last_byte;
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    g_last_byte = rx_buf[0];  /* 简短 */
}

/* 对 2: 用环形缓冲 + 业务 task 处理 */
typedef struct {
    uint8_t buf[256];
    uint16_t head, tail;
} ring_buf_t;

void uart_rx_byte(uint8_t byte) {
    ring_buf_put(&g_rx_buf, byte);  /* 简短 */
}

void uart_thread() {
    while (1) {
        uint8_t byte;
        if (ring_buf_get(&g_rx_buf, &byte)) {
            process(byte);
            log("RX: 0x%02X", byte);
        }
    }
}
```

### 复盘

- 中断里只做最少动作
- printf / log 移到线程
- 实时日志用 ITM / SWO

---

## 案例 12: 硬件流控 (RTS/CTS) 没接, 高速丢包

### 现象

1M baud 高速传输, 偶发丢字节。降速到 115200 不丢。

### 抓波形

TX 波形密集, 接收方 RXNE 来不及读, FIFO 溢出。

### 定位

高速场景必须用硬件流控, 否则接收方处理慢会丢字节。

```c
/* 错: 不用流控 */
huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;

/* 对: 用硬件流控 */
huart1.Init.HwFlowCtl = UART_HWCONTROL_RTS_CTS;
```

### 修复

```text
1. 硬件: 接 RTS/CTS 线
2. 软件: huart1.Init.HwFlowCtl = UART_HWCONTROL_RTS_CTS
3. 软件流控 (XON/XOFF) 不推荐, 因为占用 2 字节
```

### 复盘

- 1M baud+ 强烈建议用 RTS/CTS
- 接收 buffer 必须足够大 (>= 1024 字节)
- 配合 DMA 更稳

---

## 案例 13: 串口工具和 MCU 电平不兼容, 烧毁引脚

### 现象

3.3V MCU 接 5V 串口工具 (老式 RS232 转 USB), 偶尔烧毁 MCU。

### 抓波形

MCU RX 引脚电压 4.5V, 超过 MCU 3.6V 耐压。

### 定位

5V 设备 (老式 USB-TTL 工具) 直接输出 5V, 3.3V MCU 接收端没保护。

### 修复

```text
1. 用 3.3V 兼容的 USB-TTL 工具 (CP2102, CH340 等)
2. 加电平转换 (电阻分压 / TXS0108E / MOS)
3. MCU 选 5V 耐压型号
4. 加 TVS 二极管
```

### 复盘

- 调试口接错电平是产线烧片常见原因
- 必须看两端电平
- 加电平转换 / 保护电路

---

## 案例 14: 串口工具显示正常, 上位机收不到

### 现象

串口工具 (PC) 能正常收发, 但上位机 (其他系统) 收不到。

### 抓波形

正常。

### 定位

1. 上位机串口参数配错 (baud, parity, stop)
2. 上位机串口号错
3. 上位机软件没打开串口
4. 串口被其他程序占用

### 修复

```text
1. 确认串口参数一致
2. 关闭其他占用串口的程序
3. 用示波器 / 逻辑分析仪看 TX 是否有数据
4. 用串口工具的"回环"功能测线路
```

### 复盘

- 串口工具能收不代表上位机能收
- 串口资源可能被其他进程占用
- 用 dmesg / ls -l /dev/ttyUSB* 排查

---

## 案例 15: 调试日志太多, 系统卡

### 现象

加 debug 日志后, 系统响应变慢, 某些任务超时。

### 抓波形

正常, 但软件延迟大。

### 定位

printf 阻塞 UART 发送, 大量日志阻塞系统。

```c
/* 错: 业务循环里大量 printf */
while (1) {
    process_data();
    log("data: %d %d %d %d", a, b, c, d);  /* 每秒 1000 次, 阻塞 */
}
```

### 修复

```c
/* 对 1: 日志限频 */
static uint32_t last_log_tick = 0;
if (HAL_GetTick() - last_log_tick > 1000) {
    log("data: %d %d", a, b);
    last_log_tick = HAL_GetTick();
}

/* 对 2: 异步日志 */
typedef struct {
    char buf[4096];
    uint16_t pos;
} log_buf_t;

void log_async(const char *fmt, ...) {
    /* 写入环形缓冲, 单独 task 异步输出 */
}

/* 对 3: 等级控制 */
#define LOG_LEVEL  LOG_LEVEL_WARN  /* 生产用 WARN, 调试用 DEBUG */
```

### 复盘

- 日志是隐性死因
- 异步日志 + 限频 + 等级控制
- 产线 RELEASE 版本用 LOG_LEVEL_INFO, 不用 DEBUG

---

## 案例 16: 串口 (RS232) 电平冲突, 通信失败

### 现象

板子用 MAX232 转换到 RS232 (+/-12V), 接到 PC 串口, 通信失败。

### 抓波形

RS232 TX 引脚电压 ±5V, 不是标准 ±12V, PC 识别不到。

### 定位

MAX232 实际输出电压是 ±5V~±10V, 不是规范 ±12V。某些老 PC 串口识别阈值高, 接收不到。

### 修复

```text
1. 用 MAX3232 (3.3V 供电, 兼容 5V 逻辑)
2. 用 SP3232 / ICL3232 等
3. 加 ±12V 升压芯片 (如果必须 RS232 规范)
4. 改用 USB 转 UART (CH340, CP2102)
```

### 复盘

- RS232 电平标准是 ±12V, 但实际 ±5V 多数设备能识别
- 强烈推荐用 USB 转 UART, 不走 RS232
- 老 PC 串口越来越少

---

## 案例 17: 串口被 boot loader 占用, 应用层用不了

### 现象

boot 阶段串口有输出 (boot loader), 但应用层用 printf 没反应。

### 抓波形

boot 阶段正常, 应用阶段没 TX 波形。

### 定位

boot loader 配置了 UART (e.g. 115200 8N1), 但应用层用了不同参数 (e.g. 9600 7E1), UART 控制器没正确 reset。

### 修复

```c
/* 应用层: 先 DeInit 再 Init */
HAL_UART_DeInit(&huart1);
HAL_UART_Init(&huart1);
/* 重新配参数 */
```

### 复盘

- boot loader 和应用层用同一 UART, 必须 reset
- 用 boot loader 升级后, 重新 init 是关键
- 推荐: boot loader 不用同一个 UART, 避免冲突

---

## 案例 18: 中断优先级倒置, UART 中断进不去

### 现象

UART 中断配优先级 5, 但某个高频中断 (e.g. timer) 优先级 0, 持续抢占。

### 抓波形

正常, 但 UART 中断响应延迟大。

### 定位

高优先级中断持续执行, 阻塞 UART 中断响应, RXNE 标志累积导致 overrun。

### 修复

```c
/* 调高 UART 中断优先级 */
HAL_NVIC_SetPriority(USART1_IRQn, 2, 0);  /* 数字小 = 高 */
/* 调低高频中断优先级 */
HAL_NVIC_SetPriority(TIM2_IRQn, 5, 0);
```

### 复盘

- 中断优先级数字小 = 高
- UART 中断必须能及时响应, 否则丢数据
- 详细见 `i2c-state-machine.md` 类似问题

---

## 案例 19: 多串口工具打开同一 COM 口, 数据错乱

### 现象

PC 端开两个串口工具 (XCOM, SecureCRT), 都连 COM3, 偶尔收到错乱数据。

### 抓波形

正常, 但软件层错乱。

### 定位

两个程序抢同一 COM 口, USB 串口驱动无法决定给谁。

### 修复

```text
1. 一次只开一个串口工具
2. 用串口转发器 (虚拟串口 + 共享)
3. 用 TCP 串口服务器 (网络化)
```

### 复盘

- PC 端 COM 口是排他资源
- 调试时只开一个工具
- 多人协同调试用 TCP 串口服务器

---

## 案例 20: 产线老化工 UART 通信失败

### 现象

新板 100% pass, 老化 1000 小时后, 3% UART 通信失败。

### 抓波形

UART 波形正常, 但数据偶尔错位 (1 bit 错)。

### 定位

焊点疲劳 (BGA 焊球), UART 引脚接触电阻增大, 上升沿变慢, 接收方采样错位。

### 修复

```text
1. 硬件: 改用更大焊盘, 加 underfill
2. 硬件: 加外部 buffer 隔离
3. 软件: 降速, 加重试
4. 老化测试必须做
```

### 复盘

- 老化测试是产线良率的保证
- UART 高速 (1M+) 引脚对焊点质量敏感
- 详细见 `i2c-failure-cases.md` 案例 16

---

## 案例汇总: 产线 UART 死机根因分布

```text
波特率 / 晶振错        25%
RS485 方向控制错        20%
协议分帧错              15%
DMA / 中断 race         12%
电平 / 接线错          10%
多任务并发               8%
EMC / ESD               5%
其他                     5%
```

波特率/RS485/分帧加起来 60%, 是产线 UART 死机的主要根因区。

## 产线 UART 根因预防清单

```text
□ 外部晶振 (误差 < 50 ppm)
□ 波特率匹配, 误差 < 1%
□ TX/RX 方向对, GND 共地
□ 电平兼容或加转换
□ RS485 方向控制用 TC 不用 TXE
□ 接收用 DMA + 环形缓冲
□ 协议有帧边界 (SOF + LEN + CRC)
□ 缓冲区足够 (>= 256 字节)
□ 多任务访问 UART 必须 mutex
□ 高速 (>= 1M) 开硬件流控
□ 日志限频 + 等级控制
□ 产线 fault injection (baud 漂移, 干扰, 断线)
□ 老化测试 1000+ 小时
```

## 关联文档

- `uart-deep-dive.md` 原理 + 故障树
- `uart-practical.md` 速查
- `uart-rs485-and-flow-control.md` RS485 / 流控专题
- `uart-dma-circular-and-rtos.md` DMA + 环形缓冲 + RTOS
- `uart-index.md` 导航
- `rs232-rs485.md` 物理层基础
- `modbus-rs485-deep-dive.md` Modbus RTU
- `i2c-failure-cases.md` 类似产线案例
