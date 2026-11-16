# RTU 网关总体设计

## 定位

本文是 RTU 协议网关设计的总览文档。RTU 网关的核心任务是**多协议汇聚 + 北向上行**：

```text
现场设备/传感器/仪表（多种协议）
        |
        v
    RTU 网关（多协议转换 + 数据汇聚）
        |
        v
调度中心 / 行业云平台 / MES
```

## RTU 网关产品形态

```text
形态 1：嵌入式 RTU（MCU + 4G + 多协议接口）
形态 2：边缘网关（Linux + 4G + 工业接口 + 容器化）
形态 3：协议转换器（专用芯片 + 串口 / Ethernet）
形态 4：板卡式 RTU（PC + 多板卡）
```

## 网络拓扑

```text
现场层                                网关层                 上行层
--------                              --------              --------
仪表：Modbus RTU    ─┐
仪表：DL/T 645      ─┤
仪表：CJ/T 188      ─┤
仪表：M-Bus         ─┼─→  RTU 网关  ──→ IEC 104 (电力)
仪表：HART          ─┤                  ──→ DNP3 (出海)
设备：BACnet MS/TP  ─┤                  ──→ IEC 61850 (高端)
设备：OPC UA        ─┤                  ──→ MQTT (云)
设备：IEC 61850     ─┤                  ──→ HJ 212 (环保)
PLC: Modbus TCP    ─┤                  ──→ SL 651 (水文)
保护：GOOSE / SV    ─┘                  ──→ SZY 206 (水资源)
```

## 数据流模型

```text
1. 采集
   RTU 网关按配置轮询现场设备
   每个设备有独立的协议栈 + 缓存

2. 协议转换
   现场协议 A → 内部统一数据模型 → 上行协议 B
   例如：Modbus RTU（寄存器）→ 内部模型 → IEC 104（ASDU）

3. 数据汇聚
   多个现场设备的数据 → 同一上行协议的多个点
   例如：5 台电表 → IEC 104 的 5 个站点（公共地址）

4. 北向上行
   内部模型 → 调度中心协议
   例如：内部模型 → IEC 104 / DNP3 / MQTT
```

## 内部数据模型

RTU 网关核心是**内部统一数据模型**，屏蔽具体协议差异：

```text
测量点（Point）：
  - 唯一标识（Point ID）
  - 数据类型（AI / AO / DI / DO / 累计）
  - 工程值（如 23.5 kV）
  - 品质（Good / Bad / Substituted）
  - 时间戳
  - 来源（Modbus / DL/T 645 / IEC 61850）
  - 目标（IEC 104 / DNP3 / MQTT）

内部协议无关：
  - 所有协议都映射到 Point
  - 跨协议不直接转换，而是通过 Point
```

## 协议转换策略

### 策略 1：直接映射（适用于简单协议对）

```text
Modbus RTU（保持寄存器 0x0000） → IEC 104（ASDU M_ME_NC_1, IOA=1）

适用：单寄存器值
不适用：带时序、品质的数据
```

### 策略 2：内部模型中转（适用于复杂协议对）

```text
Modbus RTU（4 字节 float） → 内部模型（Point, type=Float）
                              ↓
                          IEC 104（ASDU M_ME_NC_1 + CP56Time2a）

适用：时序、品质、类型转换
不适用：实时性要求高
```

### 策略 3：代理转发（适用于同构协议）

```text
Modbus TCP（主站）→ Modbus RTU（从站）
                   网关做协议透明转发

适用：Modbus TCP 客户端无法直接访问 Modbus RTU 设备
```

## 数据类型映射

| 内部模型 | Modbus | IEC 104 | DNP3 | OPC UA |
| --- | --- | --- | --- | --- |
| AI (16-bit) | Holding Register | M_ME_NB_1 | g4v2 (16-bit AI) | AnalogValue |
| AI (32-bit) | Holding Register ×2 | M_ME_NC_1 | g4v1 (32-bit AI) | AnalogValue |
| DI | Coil / Discrete Input | M_SP_NA_1 | g1v1 (BI) | BooleanValue |
| Accumulator | Holding Register ×2 | M_IT_NA_1 | g3v1 (Counter) | AnalogValue |

## 时间戳处理

```text
1. 采集时：记录当前 RTC 时间
3. 转换时：保留采集时间
5. 上行时：使用采集时间（不覆盖）
7. 同协议转：CP56Time2g8 / g50v1 等
```

## 品质处理

```text
Modbus：无品质位 → 默认 Good
DL/T 645：无品质位 → 默认 Good
IEC 104：品质字节 → 直接映射
DNP3：Flags 字节 → 直接映射
BACnet：Status Flags → 直接映射
OPC UA：StatusCode → 直接映射
```

## 关键设计原则

### 1. 协议栈独立

```text
每个协议独立模块
模块间通过内部模型交互
协议升级不影响其他协议
```

### 2. 数据缓存

```text
现场采集缓存（防丢）
上行发送缓存（防堵塞）
断网缓存（自动补传）
```

### 3. 线程隔离

```text
采集线程（高优先级）
转换线程（中优先级）
上行线程（按调度）
```

### 4. 配置驱动

```text
JSON / YAML 配置文件
每个设备独立配置
支持热更新
```

## 网关架构图

```text
┌──────────────────────────────────────────────────────┐
│                   RTU 网关                              │
├──────────────────────────────────────────────────────┤
│ 上行协议层                                              │
│   IEC 104 / DNP3 / IEC 61850 / MQTT / OPC UA / ...   │
├──────────────────────────────────────────────────────┤
│ 内部统一模型                                          │
│   Point（ID, type, value, quality, timestamp）        │
├──────────────────────────────────────────────────────┤
│ 协议转换层                                            │
│   映射规则 / 类型转换 / 时间戳 / 品质处理              │
├──────────────────────────────────────────────────────┤
│ 现场协议层                                            │
│   Modbus RTU / DL/T 645 / CJ/T 188 / BACnet / ...    │
├──────────────────────────────────────────────────────┤
│ 物理层                                                │
│   RS485 / RS232 / Ethernet / 4G / 短信                │
└──────────────────────────────────────────────────────┘
```

## 关键性能指标

| 指标 | 典型值 | 工程经验 |
| --- | --- | --- |
| 采集周期 | 1-10 s | 越快越占 CPU |
| 上行延迟 | < 100 ms | 突发场景 |
| 断网缓存 | 10000 点 | 至少 24h 数据 |
| 上行并发 | 1-4 主站 | 多主站场景 |
| 协议转换 | < 10 ms | 每点 |
| 数据丢失率 | < 0.01% | 工程要求 |

## 选型建议

```text
小型项目（< 100 点）：
├── 嵌入式 RTU
├── 4G + RS485 × 4
├── 内部 MCU + RTOS
└── 配置：JSON

中型项目（100-1000 点）：
├── 边缘网关
├── 4G + RS485 × 8 + Ethernet × 2
├── Linux + 容器化
└── 配置：YAML

大型项目（> 1000 点）：
├── 板卡式 RTU / 工控机
├── 4G + Ethernet + 光纤
├── Linux + SCADA 软件
└── 配置：数据库
```

## 跨协议网关文档

```text
bus/modbus-rtu-iec104-gateway.md        # Modbus RTU ↔ IEC 104
bus/dlt645-iec104-gateway.md           # DL/T 645 ↔ IEC 104
bus/modbus-rtu-mqtt-gateway.md         # Modbus RTU ↔ MQTT
bus/hj212-mqtt-gateway.md              # HJ 212 ↔ MQTT
bus/dnp3-iec104-gateway.md             # DNP3 ↔ IEC 104
bus/bacnet-opcua-gateway.md            # BACnet ↔ OPC UA
bus/iec61850-iec104-gateway.md         # IEC 61850 ↔ IEC 104
```

## 延伸阅读

- `bus/power-rtu/rtu-protocols.md`：RTU 设备协议全集
- 各协议三件套：详见各协议 -index.md
- `MODBUS / IEC 104 / DNP3` 等具体协议文档

## 检查清单

```text
- 内部统一数据模型设计
- 各协议模块独立
- 协议转换策略明确
- 数据缓存机制
- 断网补传机制
- 多线程隔离
- 配置驱动
- 关键性能指标达标
- 协议栈独立可测试
- 异常处理
```