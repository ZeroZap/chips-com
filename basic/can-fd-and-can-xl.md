# CAN FD 与 CAN XL 演进

## 目标

CAN FD (CAN with Flexible Data-Rate) 和 CAN XL (CAN with eXtended data-field Length) 是 CAN 协议的演进版本。本文讲清楚:
- 为什么要演进 (经典 CAN 的局限)
- CAN FD 的关键改进
- CAN FD 与经典 CAN 的兼容
- CAN XL 的进一步演进
- 收发器和控制器选型
- 实战配置代码

## 经典 CAN 的局限

### 带宽不够

```text
经典 CAN 最高 1 Mbaud
现代 ECU 越来越多, 总线利用率经常 > 80%
部分应用 (如 ADAS 摄像头) 需要 > 1 Mbaud
```

### 数据长度不够

```text
经典 CAN 数据段最多 8 字节
多帧传输需要协议层分段 (ISO-TP, UDS)
传输 4KB 数据需要 ~500 帧
```

### 帧格式固定

```text
经典 CAN 帧格式严格
不能根据应用调整
```

## CAN FD 关键改进

### 3 大改进

```text
1. 数据段速率可变 (BRS 位)
   仲裁段: 1 Mbaud (保持)
   数据段: 可达 2 / 5 Mbaud

2. 数据长度扩展
   经典 CAN: 0-8 字节
   CAN FD:   0-64 字节

3. 帧格式扩展
   FDF 位区分经典 CAN 和 CAN FD
```

### 帧格式对比

```text
经典 CAN:
  SOF | ID | RTR | IDE | r0 | DLC | Data | CRC | ACK | EOF

CAN FD:
  SOF | ID | RRS | FDF | res | DLC | BRS | ESI | Data | CRC | ACK | EOF

差异:
  RRS (Remote Request Substitution) - 替代经典 RTR
  FDF (FD Format) - 0=经典, 1=FD
  res (reserved) - 保留位
  BRS (Bit Rate Switch) - 0=速率不变, 1=数据段加速
  ESI (Error State Indicator) - 0=主动, 1=被动
```

### DLC vs 实际数据长度

| DLC | 经典 CAN | CAN FD |
| --- | --- | --- |
| 0-8 | 0-8 字节 | 0-8 字节 |
| 9 | 8 字节 | 12 字节 |
| 10 | 8 字节 | 16 字节 |
| 11 | 8 字节 | 20 字节 |
| 12 | 8 字节 | 24 字节 |
| 13 | 8 字节 | 32 字节 |
| 14 | 8 字节 | 48 字节 |
| 15 | 8 字节 | 64 字节 |

**关键**: 经典 CAN 的 DLC 9-15 实际都只发 8 字节; CAN FD 利用了所有 DLC 值。

## CAN FD 兼容设计

### 3 个兼容要求

```text
1. 物理层兼容
   - 经典 CAN 和 CAN FD 收发器可以混用 (CAN FD 收发器向下兼容)
   - 但经典 CAN 收发器不能跑 CAN FD 数据段 > 1 Mbaud

2. 协议层兼容
   - FDF = 0: 经典 CAN 节点收到 CAN FD 帧 -> 错误
   - FDF = 1: 经典 CAN 节点不知道这个格式 -> 错误
   - 因此总线上的所有节点必须"都懂"CAN FD, 或按经典 CAN 走

3. 控制器兼容
   - 现代 MCU (STM32F4+, GD32F4, ESP32) bxCAN 支持 CAN FD 模式
   - 老款 MCU 只能跑经典 CAN
```

### 兼容混用的"陷阱"

```text
场景: 总线上 5 个节点, 1 个用经典 CAN, 4 个用 CAN FD
  - 经典 CAN 节点发 0x123 (经典帧), CAN FD 节点能正常接收
  - CAN FD 节点发 0x456 (FD 帧), 经典 CAN 节点检测到 FDF=1, 报错
  - 经典 CAN 节点的错误帧也会影响其他 CAN FD 节点

结论: 总线要"都 FD"或"都经典", 不能混
```

### 推荐路径

```text
1. 新设计: 全部用 CAN FD
2. 老网络升级: 逐步替换所有节点
3. 混用网络: 用 CAN bridge / gateway 隔离
```

## CAN FD 物理层

### 收发器要求

```text
经典 CAN 收发器 (e.g. TJA1050):
  - 支持 1 Mbaud
  - 不能跑 CAN FD 数据段 > 1M

CAN FD 收发器 (e.g. TJA1443):
  - 支持 1 Mbaud 仲裁段 + 2-5 Mbaud 数据段
  - 物理层优化 (对称性, 上升时间, 抖动)
```

### 物理层差异

| 维度 | 经典 CAN | CAN FD |
| --- | --- | --- |
| 仲裁段速率 | 1 Mbaud | 1 Mbaud (不变) |
| 数据段速率 | 1 Mbaud | 2 / 5 Mbaud |
| 上升时间 | 慢速 OK | 需要更快 |
| 收发器对称性 | 普通 | 严格 |
| 传输延迟 | 普通 | 严格 (跨时钟域) |
| 总线电容 | 常规 | 需优化 |

### 收发器选型 (CAN FD)

| 型号 | 最大数据速率 | 隔离 | 备注 |
| --- | --- | --- | --- |
| TJA1443 | 5 Mbaud | 无 | NXP 经典 |
| TJA1145 | 5 Mbaud | 无 | 带 sleep / wake |
| SN65HVD257 | 5 Mbaud | 无 | TI 工业级 |
| ISO1042 | 5 Mbaud | 数字隔离 | TI 隔离 |
| ADM3055 | 5 Mbaud | 数字隔离 | ADI 隔离 |
| TLE9251W | 5 Mbaud | 无 | Infineon 车规 |

## CAN FD 控制器配置

### STM32 bxCAN 模式切换

```c
/* STM32F4/H7 等有 bxCAN, 支持经典 CAN + CAN FD */

/* 经典 CAN 模式 */
hcan1.Init.FrameFormat = CAN_FRAME_CLASSIC;

/* CAN FD 模式 */
hcan1.Init.FrameFormat = CAN_FRAME_FD;
hcan1.Init.Mode = CAN_MODE_NORMAL;
hcan1.Init.AutoRetransmission = ENABLE;
hcan1.Init.TransmitPause = DISABLE;  /* CAN FD 推荐 DISABLE */
hcan1.Init.ProtocolException = DISABLE;
```

### 仲裁段 + 数据段双波特率

```c
/* CAN FD 仲裁段 (固定 1 Mbaud) */
hcan1.Init.NominalPrescaler = 4;
hcan1.Init.NominalSyncJumpWidth = 1;
hcan1.Init.NominalTimeSeg1 = 6;
hcan1.Init.NominalTimeSeg2 = 1;
/* Bit = (1 + 6 + 1) * 4 / 36M = 8 * 0.111us = 0.889us -> 1.125 Mbaud (略偏) */
/* 实际用 Prescaler=4, BS1=6, BS2=1 在 36 MHz 下, baud = 1.125M */
/* 严格 1M 需要: Prescaler=4, BS1=6, BS2=1 在 32 MHz 下, baud = 1M */

/* CAN FD 数据段 (2-5 Mbaud) */
hcan1.Init.DataPrescaler = 2;
hcan1.Init.DataSyncJumpWidth = 1;
hcan1.Init.DataTimeSeg1 = 5;
hcan1.Init.DataTimeSeg2 = 1;
/* Bit = (1 + 5 + 1) * 2 / 36M = 7 * 0.055us = 0.389us -> 2.57 Mbaud */
```

### 发送 CAN FD 帧

```c
CAN_TxHeaderTypeDef tx_header;
uint8_t tx_data[64];

tx_header.StdId = 0x123;
tx_header.ExtId = 0;
tx_header.IDE = CAN_ID_STD;
tx_header.RTR = CAN_RTR_DATA;
tx_header.DLC = 32;  /* CAN FD 最多 64 字节 */
tx_header.FDF = CAN_FDF;     /* 1 = CAN FD 帧 */
tx_header.BRS = CAN_BRS;     /* 1 = 数据段加速 */
tx_header.ESI = CAN_ESI_ACTIVE;  /* 错误状态 (这里 0 = 主动) */
tx_header.TransmitGlobalTime = DISABLE;

HAL_CAN_AddTxMessage(&hcan1, &tx_header, tx_data, &mailbox);
```

### 接收 CAN FD 帧

```c
/* 接收回调 */
void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan) {
    CAN_RxHeaderTypeDef rx_header;
    uint8_t rx_data[64];
    
    HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &rx_header, rx_data);
    
    /* 区分经典 CAN / CAN FD */
    if (rx_header.FDF == CAN_FDF) {
        /* CAN FD 帧 */
        log_debug("RX CAN FD: id=0x%03X dlc=%d BRS=%d",
                  rx_header.StdId, rx_header.DLC, rx_header.BRS);
    } else {
        /* 经典 CAN 帧 */
        log_debug("RX CAN: id=0x%03X dlc=%d",
                  rx_header.StdId, rx_header.DLC);
    }
    
    process_can_frame(&rx_header, rx_data);
}
```

## CAN FD 错误处理

### 收发器物理层错误

```text
CAN FD 数据段高速传输 (5 Mbaud):
  - 边沿快, 反射更明显
  - 走线 / 终端必须优化
  - 收发器对称性差 = 位错误率上升
```

### CRC 计算复杂度

```text
经典 CAN CRC: 15 位
CAN FD CRC: 17 位 (数据 0-16 字节) 或 21 位 (数据 17-64 字节)
  - 更强错误检测
  - 但计算更复杂
  - 部分老控制器硬件不支持
```

### 错误计数器在 CAN FD

```text
CAN FD 错误计数器和经典 CAN 一样 (TEC/REC)
但 CAN FD 高速数据段瞬时错误率可能更高
需要:
  - 更严格的物理层
  - 监控 TEC/REC
  - 必要时降速
```

## CAN XL 进一步演进

### CAN FD 的局限

```text
1. 数据长度虽然到 64 字节, 但仍不够 (例如 ADAS 摄像头原始数据)
2. 速率 5 Mbaud 仍偏慢 (车载主干网需求 > 10M)
3. 不支持时间同步 (TSN)
```

### CAN XL 关键改进

| 维度 | CAN FD | CAN XL |
| --- | --- | --- |
| 数据长度 | 0-64 字节 | 1-2048 字节 |
| 最大速率 | 5 Mbaud | 10+ Mbaud |
| 虚拟通道 (VC) | 无 | 支持 |
| 加速 (SDT) | 无 | 支持 |
| 安全 (SEC) | 无 | 支持 |
| 时间同步 | 无 | 部分支持 |
| 标准化 | ISO 11898-1:2015 | ISO 11898-1:2024 |

### CAN XL 帧格式

```text
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ SOF │  ID │ SDT │  VC │  AD │SADL │ SEC │ Data│ CRC │EOF│
│     │     │     │     │     │     │     │     │     │   │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
                        ↑     ↑     ↑
                        虚拟通道 加速  安全
```

关键字段:
- **SDT** (Service Data Unit Type): 帧类型 (数据/管理)
- **VC** (Virtual Channel): 虚拟通道 ID (类似 TSN 流 ID)
- **AD** (Acceptance Field): 接收过滤
- **SADL** (Source Address Destination Address Length): 地址长度
- **SEC** (Security): 安全等级

### CAN XL 应用场景

```text
车载主干网 (Ethernet 替代):
  - ADAS 摄像头: 多路 4K 视频
  - 智能座舱: 多屏显示
  - 域控制器: 跨域通信

工业骨干:
  - 高速工业控制
  - 大数据量 sensor

替代车载 Ethernet:
  - 比 Ethernet 简单
  - 比 CAN FD 强大
  - 100% CAN 兼容性
```

### CAN XL 状态 (2026)

```text
标准化: 完成 (ISO 11898-1:2024)
芯片: Bosch / NXP / 国产部分厂商有 IP
量产: 仍较少, 多数还在评估
价格: 比 CAN FD 收发器贵 2-3 倍
```

**结论**: 2026 年 CAN XL 仍在早期, 大规模量产预计 2027+。

## CAN FD 选型决策

### 什么时候用经典 CAN

```text
- 现有网络已部署经典 CAN
- 节点数 < 10, 报文不长 (< 8 字节)
- 总线利用率 < 30%
- 收发器成本敏感
- 速度 <= 1 Mbaud 足够
```

### 什么时候用 CAN FD

```text
- 新设计, 想保留升级空间
- 数据长度 > 8 字节 (e.g. 固件下载, 大数据 sensor)
- 总线利用率 > 50%, 需要加速
- ADAS / 域控制器等现代应用
- 收发器成本可接受
```

### 什么时候用 CAN XL

```text
- 车载主干网 (替代 Ethernet)
- 高速大流量 (> 5 Mbaud, > 64 字节)
- 时间敏感网络需求
- 长期演进目标
- 2026 年仍建议作为 "评估选项" 而非 "量产选项"
```

## CAN FD 实战配置 (STM32)

```c
/* 完整 CAN FD 初始化 (STM32H7 例) */
CAN_HandleTypeDef hcan1;

void can_fd_init() {
    hcan1.Instance = CAN1;
    
    /* 仲裁段: 1 Mbaud @ 64 MHz APB1 */
    hcan1.Init.NominalPrescaler = 8;
    hcan1.Init.NominalSyncJumpWidth = 1;
    hcan1.Init.NominalTimeSeg1 = 6;
    hcan1.Init.NominalTimeSeg2 = 1;
    
    /* 数据段: 5 Mbaud @ 64 MHz APB1 */
    hcan1.Init.DataPrescaler = 1;
    hcan1.Init.DataSyncJumpWidth = 1;
    hcan1.Init.DataTimeSeg1 = 11;  /* 13 Tq */
    hcan1.Init.DataTimeSeg2 = 1;
    /* Bit = 13 Tq * (1/64M) = 13 * 15.625ns = 203ns -> 4.9 Mbaud (接近 5M) */
    
    hcan1.Init.Mode = CAN_MODE_NORMAL;
    hcan1.Init.FrameFormat = CAN_FRAME_FD;
    hcan1.Init.AutoRetransmission = ENABLE;
    hcan1.Init.TransmitPause = DISABLE;
    hcan1.Init.ProtocolException = DISABLE;
    
    HAL_CAN_Init(&hcan1);
    
    /* 过滤器 */
    CAN_FilterTypeDef filter;
    filter.FilterBank = 0;
    filter.FilterMode = CAN_FILTERMODE_IDMASK;
    filter.FilterScale = CAN_FILTERSCALE_32BIT;
    filter.FilterIdHigh = 0x123 << 5;
    filter.FilterMaskIdHigh = 0x7FF << 5;
    filter.FilterFIFOAssignment = CAN_RX_FIFO0;
    filter.FilterActivation = ENABLE;
    HAL_CAN_ConfigFilter(&hcan1, &filter);
    
    HAL_CAN_Start(&hcan1);
    HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);
}

void can_fd_send(uint32_t can_id, uint8_t *data, uint8_t len) {
    CAN_TxHeaderTypeDef tx_header;
    uint32_t mailbox;
    
    tx_header.StdId = can_id;
    tx_header.IDE = CAN_ID_STD;
    tx_header.RTR = CAN_RTR_DATA;
    tx_header.DLC = len;  /* 0-64 */
    tx_header.FDF = 1;   /* CAN FD */
    tx_header.BRS = 1;   /* 数据段加速 */
    tx_header.ESI = 0;
    tx_header.TransmitGlobalTime = DISABLE;
    
    HAL_CAN_AddTxMessage(&hcan1, &tx_header, data, &mailbox);
}
```

## CAN FD 产线验证

### 验证项

```text
□ 物理层: 收发器型号支持 CAN FD
□ 物理层: 终端电阻 120 ohm 两端各 1
□ 物理层: 走线对称, 阻抗匹配
□ 控制器: bxCAN 配置正确
□ 控制器: 仲裁段 / 数据段双波特率配置
□ 协议层: FDF / BRS 位正确
□ 协议层: DLC 编码正确
□ 协议层: CRC 计算正确
□ 错误处理: TEC/REC 监控
□ 老化测试: 1000+ 小时, 监控错误率
```

### 产线 fault injection

```text
- 用 CAN FD 节点 + 经典 CAN 节点混用
  期望: 总线报错误, 隔离故障段
- 收发器拔掉
  期望: 节点 error passive
- 终端电阻短路
  期望: 节点 bus off
- 物理层干扰 (电机)
  期望: 错误率上升但功能正常
```

## CAN FD 与 SMBus 之类协议的对比 (跨总线视角)

| 维度 | CAN FD | I2C | SPI | UART/RS485 |
| --- | --- | --- | --- | --- |
| 速率 | 1M-5M | < 3.4M | 10M-200M | < 6M / RS485 1M |
| 多 master | 硬件仲裁 | 软件地址 | CS 选主 | 无 |
| 数据长度 | 0-64 B | 任意 | 任意 | 任意 |
| 错误检测 | 强 (CRC + 5 类) | 弱 (ACK) | 无 | 弱 (parity) |
| 距离 | 1km (低速) | 短 | 短 | RS485 1km |
| 节点数 | 32-256 | 多个 | 多个 (CS) | 32 (RS485) |
| 实时性 | 高 (仲裁) | 中 | 高 | 低 |
| 成本 | 中 | 低 | 低 | 低 |
| 演进 | CAN XL | I3C | QSPI | USB CDC |

**选型**:
- 实时 + 多节点 + 强可靠 → **CAN / CAN FD**
- 大数据 + 短距离 → SPI / QSPI
- 板内管理 + 多设备 → I2C / I3C
- 异步 + 长距离 → UART / RS485

## 关联文档

- `can-practical.md` 速查
- `can-deep-dive.md` 原理
- `can-failure-cases.md` 产线死机案例
- `can-multimaster-and-bus-off.md` 多 master + bus off
- `can-rtos-integration.md` RTOS + SocketCAN
- `can-vs-other-bus.md` 跨总线对比
- `can-index.md` 导航
- `bus/can-canopen-deep-dive.md` CANopen
- `i2c-vs-smbus-recovery.md` 跨协议对比参考
