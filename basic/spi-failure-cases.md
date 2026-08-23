# SPI 产线死机案例库

## 目标

把产线常见的 SPI 死机 / 通信失败 / 信号完整性问题写成案例库。每个案例:
- 现象 (现场)
- 抓波形 (判断)
- 定位 (根因)
- 修复 (代码 / 硬件)
- 复盘 (如何预防)

按主题分类, 配 `spi-deep-dive.md` / `spi-practical.md` 使用。

---

## 案例 1: 读 Flash JEDEC ID 失败, 0xFF

### 现象

新板第一次跑, 读 SPI Flash 的 JEDEC ID:
```text
[flash] read JEDEC ID: 0xFF 0xFF 0xFF
[flash] err: unknown manufacturer
```

### 抓波形

- CS 拉低了
- SCLK 有输出
- MOSI 有数据
- MISO 一直高 (0xFF)

### 定位

MISO 浮空。可能是:
1. MISO 引脚没接 (焊接漏)
2. MISO pinmux 配错
3. Flash 没上电
4. CS 极性反 (CS 高有效, 但软件配成低有效)

### 修复

1. 量 MISO 对地电阻, 应该有上拉 (10k~100k)
2. 量 Flash VCC, 应该 3.3V
3. 改 CS 极性配置

```c
/* HAL 改 CS 极性 */
hspi1.Init.NSS = SPI_NSS_SOFT;  /* 软件 CS, 自己控制 GPIO */
```

### 复盘

- 0xFF 永远先查硬件
- 写代码前, 示波器看 4 根线 (CS, SCLK, MOSI, MISO)
- 90% 的 0xFF 是硬件问题

---

## 案例 2: 写 Flash 不生效, 数据仍是 0xFF

### 现象

```text
[flash] erase sector 0x1000
[flash] write 256 bytes at 0x1000
[flash] read back: 0xFF 0xFF 0xFF ...
[flash] err: write failed
```

### 抓波形

- 写命令序列正常
- Write Enable 命令发出
- 但是写后读数据是 0xFF, 写没生效

### 定位

没有发 Write Enable (0x06) 命令, 或者 Write Enable 之后做了其他操作导致状态清除。

```c
/* 错: 写前没 Write Enable */
HAL_SPI_Transmit(&hspi1, &cmd_page_program, 4, 100);

/* 对: 写前先 Write Enable */
uint8_t cmd_we = 0x06;
HAL_SPI_Transmit(&hspi1, &cmd_we, 1, 100);
HAL_SPI_Transmit(&hspi1, &cmd_page_program, 4, 100);
```

### 复盘

- SPI Flash 几乎所有写操作前都要 Write Enable
- 写完后必须轮询 WIP (Write In Progress)
- 把 Write Enable / WIP 封装成 helper, 不要每次手写

---

## 案例 3: 多设备总线冲突, 读到错数据

### 现象

板子上有 2 个 SPI 设备: Flash 和 LCD。读 Flash 时, 偶尔读到的数据是 LCD 寄存器值。

### 抓波形

读 Flash 时, CS_Flash 拉低, 但 LCD 的 CS_LCD 也意外拉低, MISO 上两个设备都驱动, 数据混乱。

### 定位

LCD 的 CS 极性反了, 或者 LCD 的 CS GPIO 没配成输出, 高阻输入时被 Flash 拉低。

### 修复

1. 检查所有 CS GPIO, 必须配成推挽输出, 默认高
2. 改 LCD CS 软件拉低前, 先确认其他 CS 都是高
3. 用 `hspi1.Init.NSS = SPI_NSS_SOFT` 手动控制

```c
/* 关键: 切设备前 CS 默认高, 然后只拉目标 CS */
HAL_GPIO_WritePin(CS_LCD_PORT, CS_LCD_PIN, GPIO_PIN_SET);  /* 先关 LCD */
HAL_GPIO_WritePin(CS_FLASH_PORT, CS_FLASH_PIN, GPIO_PIN_RESET);  /* 开 Flash */
/* 操作 Flash */
HAL_GPIO_WritePin(CS_FLASH_PORT, CS_FLASH_PIN, GPIO_PIN_SET);
```

### 复盘

- 多 SPI 设备, CS 极性必须一致 (都低有效或都高有效)
- 切设备前显式关所有 CS, 避免瞬时多设备选中
- MISO 必须三态, 否则会拉低

---

## 案例 4: 速度提到 10 MHz, 数据全错

### 现象

1 MHz 跑通, 提到 10 MHz 失败, 读出来数据是预期值的移位版本。

### 抓波形

10 MHz 下 SCLK 边沿有振铃, MISO 上升沿慢, 数据建立时间不足。

### 定位

信号完整性问题:
1. MISO 上拉太弱 (10k + 长走线, 上升时间 200ns)
2. 时钟周期 100ns, MISO 还没拉到高就读

### 修复

```text
方案 1: 改 MISO 上拉电阻到 1k~2.2k
方案 2: 降速到 5 MHz
方案 3: 改 CPHA 采样边沿
方案 4: 加 series 电阻 (33 ohm) 在 SCLK 上
方案 5: 短走线, 远离干扰
```

### 复盘

- 速度每提升一档, 都要重新验证信号完整性
- MISO 是最慢的信号, 因为有内部上拉 + 设备驱动能力限制
- 示波器是唯一可信工具, datasheet 数字不够

---

## 案例 5: SPI Flash 写后读数据正确, 复位后变 0xFF

### 现象

写 Flash, 读回来正确。但是 MCU 复位后, 读 Flash, 数据变 0xFF, 写丢了。

### 抓波形

写命令和数据正常, 写完后 WIP 变 0, 但 MCU 复位后读是 0xFF。

### 定位

Flash 写完后, **没有等待内部编程完成**。MCU 在 WIP 仍为 1 时复位, 写丢失。

```c
/* 错: 写完不轮询 WIP */
HAL_SPI_Transmit(&hspi1, &cmd_we, 1, 100);
HAL_SPI_Transmit(&hspi1, &cmd_page_program, 256+4, 1000);
/* 此时 WIP = 1, 数据还在编程, 不可读 */

/* 对: 写后轮询 WIP */
HAL_SPI_Transmit(&hspi1, &cmd_we, 1, 100);
HAL_SPI_Transmit(&hspi1, &cmd_page_program, 256+4, 1000);
HAL_SPI_Transmit(&hspi1, &cmd_read_sr1, 1, 100);
HAL_SPI_Transmit(&hspi1, &sr1, 1, 100);
while (sr1[0] & 0x01) {  /* WIP = 1 */
    HAL_SPI_Transmit(&hspi1, &cmd_read_sr1, 1, 100);
    HAL_SPI_Transmit(&hspi1, &sr1, 1, 100);
}
```

### 复盘

- SPI Flash 写操作是非阻塞的, 写命令发出后内部还在编程
- 必须轮询 WIP = 0 才能继续
- 关键数据写完应做 read-back 校验

---

## 案例 6: 跨地电位差, 高速 SPI 偶发失败

### 现象

板子 A 和板子 B 通过 SPI 连接 (板对板线缆), 1 MHz 跑通, 5 MHz 偶发失败。

### 抓波形

5 MHz 下, 数据波形在 0x80 附近抖动, 像被地电位差干扰。

### 定位

板对板线缆, GND 走线太细, 大电流经过时两端 GND 有 0.3V 电位差。SPI 是单端信号, 0.3V 足够让接收端误判。

### 修复

```text
1. 加粗 GND 线, 单独走
2. 降速到 1 MHz
3. 改用差分 SPI (少见)
4. 加隔离芯片
```

### 复盘

- 板对板 SPI 受 GND 电位差影响
- 关键信号 + GND 必须绑在一起走
- 长距离 (>10cm) 不要用 SPI, 改 RS485 / 差分

---

## 案例 7: DMA 跑到一半挂, 数据错乱

### 现象

用 DMA 接收 1KB 数据, 偶发只收到 500 字节, 后面的数据是 0。

### 抓波形

DMA 传输中, CS 提前拉高 (在 DMA 完成前), 从设备没继续驱动 MISO。

### 定位

CS 拉高在 DMA 回调里, 但是 DMA 完成回调触发比数据传输完成早 (某些 MCU 的 DMA bug)。

### 修复

```c
/* 错: 在 DMA 完成回调立刻拉高 CS */
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi == &hspi1) {
        HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);  /* 错! */
    }
}

/* 对: 在 DMA 完成回调里, 等几个 byte 时间再拉高 CS */
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi == &hspi1) {
        delay_us(5);  /* 等最后字节锁存 */
        HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);
    }
}
```

或者改用 IT 模式 (字节中断), 而不是 DMA。

### 复盘

- DMA 完成 ≠ 设备锁存完毕
- 高速 + DMA + 多设备, 边界情况多
- 改用 IT 模式 debug 容易

---

## 案例 8: SPI 中断优先级和 DMA 冲突

### 现象

用 DMA 收发, 偶发 overrun / underrun 错误, 数据丢失。

### 抓波形

正常, 但软件报告 OVR / UDR 错误。

### 定位

SPI EV 中断优先级 < DMA 中断优先级。DMA 完成触发, 抢占 SPI EV 中断, 导致 SPI 状态寄存器被覆盖。

### 修复

```c
/* 调高 SPI EV 中断优先级 */
HAL_NVIC_SetPriority(SPI1_IRQn, 2, 0);
HAL_NVIC_SetPriority(DMA1_Stream0_IRQn, 3, 0);
```

### 复盘

- 中断优先级数字小 = 高 (NVIC)
- SPI EV 中断不能比 DMA 中断低
- 详细见 `i2c-state-machine.md` 同类问题

---

## 案例 9: 3-Wire SPI 模式配错

### 现象

用 3-Wire SPI (单线双向), 读传感器失败。

### 抓波形

SCLK 有, 但 MOSI/MISO 都没数据。

### 定位

3-Wire SPI 用同一根线 (SIO) 双向传输, 但 SPI 控制器配成标准 4-Wire (MOSI+MISO 分开)。

### 修复

```c
/* 3-Wire SPI 配置: 单线双向 */
hspi1.Init.Direction = SPI_DIRECTION_1LINE;  /* 单线 */
/* 数据方向: TX 或 RX, 切换用 */
hspi1.Init.Mode = SPI_MODE_MASTER;
```

代码里需要切换方向:

```c
/* 写 */
HAL_SPI_Transmit(&hspi1, tx, len, 100);
/* 读 */
HAL_SPIEx_FlushRxFifo(&hspi1);
HAL_SPIEx_EnableHalfDuplexRx(&hspi1);
HAL_SPI_Receive(&hspi1, rx, len, 100);
```

### 复盘

- 3-Wire SPI 在 sensor 中常见
- 配错会完全没数据
- 4-Wire 和 3-Wire 不兼容, 切换要小心

---

## 案例 10: 菊花链设备链路错位

### 现象

用菊花链连接 4 个 LED 驱动 (TLC5947), 期望看到 4 个 LED 都亮, 但只有第 1 个亮, 其他 3 个错乱。

### 抓波形

菊花链的数据流: Controller -> LED1 -> LED2 -> LED3 -> LED4。数据移位是单向的, 必须从后往前填。

### 定位

数据发送顺序错: 应该是 LED4 数据先发 (因为链尾先收到, 逐级移位), LED1 数据最后发 (链头最后收到)。

```c
/* 错: LED1 数据先发 */
tx[0] = led1_data;
tx[1] = led2_data;
tx[2] = led3_data;
tx[3] = led4_data;
HAL_SPI_Transmit(&hspi1, tx, 4*12, 1000);

/* 对: LED4 数据先发 (链尾先收) */
tx[0] = led4_data;
tx[1] = led3_data;
tx[2] = led2_data;
tx[3] = led1_data;
HAL_SPI_Transmit(&hspi1, tx, 4*12, 1000);
```

### 复盘

- 菊花链数据从链尾开始发
- 不同芯片 datasheet 写的不一样, 看图确认
- 调试: 先只发 1 字节, 看哪个 LED 响应

---

## 案例 11: SPI Flash 跨页写, 数据错乱

### 现象

写 256 字节到 Flash, 跨了页边界, 后半部分数据错乱。

### 抓波形

写命令和地址正确, 但数据写到下一个页的起始, 把前一个页的数据覆盖了。

### 定位

SPI Flash 页大小通常是 256 字节, 跨页写会回卷到页首。

```c
/* 错: 跨页写 */
addr = 0x100;  /* 在页边界 0x100 处 */
HAL_SPI_Transmit(&hspi1, &cmd_page_program, 256+4, 1000);
/* 写 256 字节: 0x100 ~ 0x200, 但 Flash 把后半段回卷到 0x000 */

/* 对: 跨页分两次写 */
if (addr + len > page_end) {
    /* 第一次: 写到页尾 */
    HAL_SPI_Transmit(&hspi1, &cmd_pp1, page_end-addr+4, 1000);
    /* 第二次: 从下一页开始 */
    addr = page_end;
    HAL_SPI_Transmit(&hspi1, &cmd_pp2, len-(page_end-addr_old)+4, 1000);
}
```

### 复盘

- SPI Flash 页写有 page boundary 限制
- 跨页必须分多次写
- 先 erase 再写, 不能只 write

---

## 案例 12: SPI 设备上电时序错乱

### 现象

板子断电后立刻上电, SPI 设备通信失败, 重新上下电后正常。

### 抓波形

上电后第一次 SPI 通信, 数据错乱, 但后面恢复正常。

### 定位

设备 POR 未完成, 内部状态机未初始化完。MCU 已经开始 SPI 通信。

### 修复

1. 上电后延时 100ms 再 init SPI
2. 关键设备 reset 接 MCU GPIO, 上电时拉 reset
3. SPI init 前先读一次 JEDEC ID, 失败重试

```c
void spi_init_after_power_on() {
    HAL_Delay(100);  /* 等设备 POR 完成 */
    /* 试读 ID, 失败重试 */
    for (int i = 0; i < 5; i++) {
        if (spi_read_id() == 0xEF4018) {  /* 期望的 JEDEC ID */
            return;  /* 成功 */
        }
        HAL_Delay(10);
    }
    /* 失败, 上报 */
    log_error("SPI Flash not responding");
}
```

### 复盘

- 设备 POR 时间 datasheet 会写, 通常 1-100ms
- 高速系统也要尊重设备时序
- 复位 / 重新 init 是兜底

---

## 案例 13: 高速 SPI 干扰低速 sensor

### 现象

板子有 1 MHz 的 SPI sensor 和 20 MHz 的 SPI Flash。两个不同时使用, 但 sensor 通信偶发失败。

### 抓波形

示波器在 sensor 通信期间, SCLK 边沿有抖动, 像被 Flash 的 SCLK 干扰。

### 定位

两根 SCLK 走线平行, 高速信号耦合到低速信号。

### 修复

```text
1. 走线垂直, 避免平行
2. 加地线隔离
3. 降速 Flash 到 5 MHz
4. 物理上分开 SPI controller, 用不同 SPI 外设
```

### 复盘

- 高速 SPI 是 EMC 干扰源
- 多 SPI 设备, 走线要小心
- 干扰难查, 预防 > 修复

---

## 案例 14: SPI 中断里跑过长时间操作

### 现象

SPI EV 中断里跑 printf 调试, 通信失败。

### 抓波形

正常, 但日志显示 SPI 状态卡住。

### 定位

printf 在中断里跑 1-2 ms, 期间 SPI EV 中断持续触发 (DMA 完成的回调), 优先级反转。

### 修复

1. 中断里只做最少动作 (set flag, give semaphore)
2. printf / log 移到线程里
3. 用 ITM / SWO 替代 printf 做实时日志

```c
/* 错 */
void SPI1_IRQHandler(void) {
    HAL_SPI_IRQHandler(&hspi1);
    /* HAL 回调里 */
    printf("SPI done\n");  /* 错! 中断里跑 printf */
}

/* 对 */
volatile bool spi_done_flag = false;
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi == &hspi1) {
        spi_done_flag = true;  /* 简短 */
    }
}

void spi_thread() {
    while (1) {
        if (spi_done_flag) {
            spi_done_flag = false;
            printf("SPI done\n");  /* 线程里 */
        }
    }
}
```

### 复盘

- 中断里只做最少动作
- printf / log / 上报都应该在线程
- 实时日志用 ITM / SWO, 不阻塞

---

## 案例 15: SPI Flash 写保护没解除

### 现象

新板 Flash 写不进去, 读 ID 正常。

### 抓波形

写命令正常, 但 status register 显示 BP (Block Protect) 位被置位。

### 定位

Flash 出厂默认带写保护, 或者上次写的状态没清。

### 修复

```c
/* 写前解除写保护 */
uint8_t cmd_wrsr[2] = { 0x01, 0x00 };  /* Write Status Register, 全部清 0 */
HAL_SPI_Transmit(&hspi1, cmd_wrsr, 2, 1000);
HAL_Delay(10);
/* 验证 SR1 = 0 */
uint8_t cmd_rdsr = 0x05;
uint8_t sr1 = 0;
HAL_SPI_Transmit(&hspi1, &cmd_rdsr, 1, 100);
HAL_SPI_Transmit(&hspi1, &sr1, 1, 100);
```

### 复盘

- Flash 出厂默认有 BP 位
- 新板首次用, 要清 SR
- 关键数据写完后, 重新 enable BP 防误写

---

## 案例 16: 同一 SPI 控制器多设备时, 速度配置冲突

### 现象

SPI 控制器上挂 2 个设备, 1 MHz 和 10 MHz。代码里来回切速度, 偶发某次切的速度不对。

### 抓波形

某次访问 1 MHz 设备时, 实际跑 10 MHz, 数据错。

### 定位

速度切换时, SPI 控制器的 BR 寄存器没及时更新, 或者时钟分频器没稳定。

### 修复

```c
/* 切速度时, 先 disable 再 enable */
HAL_SPI_DeInit(&hspi1);
hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_64;  /* 1 MHz @ 64 MHz clock */
HAL_SPI_Init(&hspi1);
```

或者用软件切换 (不同 SPI 实例, 每个设备一个 SPI 外设, 互不干扰)。

### 复盘

- 速度配置切换需要 disable + init
- 多速度设备, 优先用多 SPI 外设
- 切换前确认切换成功 (读回 BR 寄存器)

---

## 案例 17: 高速 SPI 读 Flash 漏 dummy cycle

### 现象

普通 Read 命令 (0x03) 跑通, Fast Read (0x0B) 失败。

### 抓波形

Fast Read 命令发完后, 第一个 dummy cycle 期间 MISO 没数据, 后面数据错位。

### 定位

Fast Read 需要 dummy cycle (通常是 8 个 SCLK), 时钟产生但数据还没准备好, 采样错位。

### 修复

```c
/* Fast Read 流程: 1 字节命令 + 3 字节地址 + 1 字节 dummy + 数据 */
uint8_t cmd[5] = { 0x0B, addr>>16, addr>>8, addr, 0xFF };  /* 0xFF 是 dummy byte */
HAL_SPI_Transmit(&hspi1, cmd, 5, 100);
HAL_SPI_Receive(&hspi1, rx, len, 1000);
```

### 复盘

- Fast Read 必须有 dummy cycle
- Dummy 数量查手册, 不同 Flash 不同
- QSPI 模式下 dummy 是 cycle 数, 不是 byte

---

## 案例 18: SPI 时序违反设备 setup time

### 现象

设备要求 CS 拉低后等 100ns 再发 SCLK, 但代码立刻发, 设备不响应。

### 抓波形

CS 拉低和 SCLK 第一个边沿间隔 20ns, 设备识别不到。

### 定位

SPI 控制器的 NSS 管理不当, 软件 CS 拉低后立刻进 TX, 没等 tCSS (CS setup time)。

### 修复

```c
/* 软件拉 CS 后, 延时 */
HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_RESET);
delay_ns(200);  /* 满足 setup time */
HAL_SPI_Transmit(&hspi1, tx, len, 1000);
```

或者用硬件 NSS, SPI 控制器自动管理时序。

### 复盘

- CS 到 SCLK 有时序要求 (tCSS, tCSH)
- 高速 (>10 MHz) 时这些 ns 级时序重要
- 示波器量, 不靠 datasheet 估算

---

## 案例 19: 板子被 ESD 打坏后 SPI 偶发失败

### 现象

板子经过 ESD 测试 (空气放电 8kV) 后, SPI 通信偶发失败。

### 抓波形

SPI 波形正常, 但数据值错位, 像被噪声干扰。

### 定位

ESD 损伤了 SPI 引脚的 IO 电路, 没完全坏, 但驱动能力下降。

### 修复

```text
1. 硬件: 加 TVS 二极管, 加 series 电阻
2. 硬件: 走线远离板边
3. 软件: 降速, 加重试
4. 验证: ESD 测试必须做, 不能省
```

### 复盘

- ESD 损伤是隐性死因
- SPI 高速 (10MHz+) 引脚对 ESD 敏感
- 产线每块板子应做 ESD 测试

---

## 案例 20: 多任务同时调 SPI 阻塞

### 现象

RTOS 2 个 task 都调 `HAL_SPI_Transmit`, 1 个能跑通, 1 个永远失败。

### 抓波形

逻辑分析仪看, 2 个 task 的 SPI 时序交叠, MISO 数据错。

### 定位

HAL_SPI_Transmit 阻塞, 但不是 thread-safe。2 个 task 共享 hspi1, 状态被覆盖。

### 修复

```c
static SemaphoreHandle_t g_spi1_mutex;

int spi1_xfer(uint8_t *tx, uint8_t *rx, int len, uint32_t timeout) {
    xSemaphoreTake(g_spi1_mutex, portMAX_DELAY);
    HAL_StatusTypeDef ret;
    if (rx) ret = HAL_SPI_TransmitReceive(&hspi1, tx, rx, len, timeout);
    else     ret = HAL_SPI_Transmit(&hspi1, tx, len, timeout);
    xSemaphoreGive(g_spi1_mutex);
    return ret;
}
```

### 复盘

- HAL 库不是 thread-safe
- 任何被多 task 访问的 SPI 控制器, 必须 mutex
- 详细见 `spi-rtos-integration.md`

---

## 案例汇总: 产线 SPI 死机根因分布

```text
Mode / CS / 接线错    25%
信号完整性 (高速)      20%
Flash 时序错 (WE/WIP)  15%
DMA / 中断 race       12%
电源 / 上电时序        10%
多设备冲突              8%
EMC / ESD              5%
其他                   5%
```

Mode/CS/接线 + 信号完整性加起来 45%, 是产线 SPI 死机的主要根因区。

## 产线 SPI 根因预防清单

```text
□ SPI Mode 在 boot 阶段就锁定, 不动态改
□ 100 kHz 跑通后再提速, 每档都验证
□ 写 Flash 前 Write Enable, 写后轮询 WIP
□ 多设备 MISO 三态, CS 默认高
□ 关键设备 reset 由 MCU 控制
□ 高速 (10MHz+) 验证信号完整性
□ DMA + 中断优先级明确文档
□ 上下电时序文档化
□ 产线 fault injection (CS 抖动, 速度, EMC)
□ 老化测试 1000+ 小时
□ 跨页 / 跨块操作封装成 helper
□ 多 task 访问 SPI 必须 mutex
```

## 关联文档

- `spi-deep-dive.md` 原理 + 故障树
- `spi-practical.md` 速查
- `spi-multislave-and-dma.md` 多从 / 菊花链 / DMA
- `spi-rtos-integration.md` RTOS 集成
- `spi-index.md` 导航
- `qspi-ospi.md` 高速 SPI Flash
