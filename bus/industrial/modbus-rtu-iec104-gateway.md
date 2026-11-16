---
tags:
  - layer/bus
  - type/gateway-design
  - protocol/modbus
  - topic/industrial
---

# Modbus RTU ↔ IEC 104 网关

## 定位

本文是 Modbus RTU（RS485 现场协议）转 IEC 104（电力调度协议）的网关设计文档。这是 RTU 设备最常见的协议转换场景：现场 Modbus RTU 设备通过 RTU 网关转 IEC 104 上行调度中心。

## 场景

```text
现场设备（Modbus RTU）：
  - 变频器、PLC、传感器、IO 模块、智能仪表
  - 标准 Modbus RTU 协议
  - RS485 总线

上行调度中心（IEC 104）：
  - 电力主站 / 配电主站 / 新能源场站监控
  - 标准 IEC 104 协议
  - TCP 长连接
```

## 数据流

```text
1. 网关按配置轮询现场设备（Modbus Master）
   - 保持寄存器 0x0000 ~ 0x00FF：测量值
   - 线圈 0x0000 ~ 0x000F：开关状态
   - 输入寄存器：原始测量值

2. 解析 Modbus 响应 → 内部 Point 模型
   - 寄存器 0x0000 → Point ID 1, type=AI
   - 寄存器 0x0001 → Point ID 2, type=AI
   - 线圈 0x0000 → Point ID 100, type=DI

3. 上行 IEC 104（IEC 104 Outstation）
   - 总召唤响应
   - 突发上报（值变化）
   - 时钟同步响应
   - 命令下行（选择 → 执行）
```

## 内部模型映射

| Modbus RTU | 内部 Point | IEC 104 |
| --- | --- | --- |
| Holding Register (16-bit) | AI_16 | M_ME_NB_1 (Type 11) |
| Holding Register (32-bit, ×2) | AI_32 | M_ME_NC_1 (Type 13) |
| Holding Register (Float, ×2) | AI_Float | M_ME_NC_1 (Type 13) |
| Input Register (16-bit) | AI_16_RO | M_ME_NB_1 + ReadOnly |
| Coil | DI | M_SP_NA_1 (Type 1) |
| Discrete Input | DI_RO | M_SP_NA_1 + ReadOnly |

## 数据转换

### Float 转换

```text
Modbus RTU Holding Register × 2：
  寄存器 0x0010 = 0x4248（高字节）
  寄存器 0x0011 = 0x0000（低字节）
  
字节序：ABCD（Big-Endian Word Order）
  0x42480000 = IEEE 754 float = 50.0

内部 Point：
  Point ID 5, type=AI_Float, value=50.0

IEC 104 ASDU：
  Type 13 (M_ME_NC_1)
  ASDU body: 4 字节 float（IEEE 754）
  0x42480000
```

### 32-bit 数据

```text
Modbus RTU Holding Register × 2：
  寄存器 0x0020 = 0x1234
  寄存器 0x0021 = 0x5678
  
字节序：ABCD
  0x12345678 = 305419896

内部 Point：
  Point ID 6, type=AI_32, value=305419896

IEC 104 ASDU：
  Type 11 (M_ME_NB_1) 但仅 16-bit
  
方案 1：用 M_ME_NC_1 (32-bit float 但精度可能丢)
方案 2：拆分两个 16-bit 上行
方案 3：归一化（按工程值缩放）
```

## 命令下行

```text
调度中心 IEC 104：
  C_SC_NA_1 单点命令（开关合闸）
  C_DC_NA_1 双点命令
  C_SE_NC_1 短浮点设定

网关转换：
  IEC 104 命令 → Modbus 写命令
  - C_SC_NA_1 (合) → Modbus Write Coil 0x0001 = 1
  - C_SC_NA_1 (分) → Modbus Write Coil 0x0001 = 0
  - C_SE_NC_1 (设定 50.0) → Modbus Write Holding Register 0x0010 = 50.0

命令链：
  IEC 104 Select → 内部命令队列
  IEC 104 Operate → Modbus 写入
  IEC 104 应答 ← Modbus 响应
```

## 配置示例（JSON）

```json
{
  "devices": [
    {
      "device_id": "PLC_1",
      "protocol": "modbus_rtu",
      "interface": "/dev/ttyS0",
      "baud_rate": 9600,
      "parity": "E",
      "slave_id": 1,
      "points": [
        {
          "point_id": 1,
          "modbus_function": 3,
          "modbus_address": 0,
          "type": "AI_16",
          "iec104_type": 11,
          "iec104_ioa": 1
        },
        {
          "point_id": 2,
          "modbus_function": 3,
          "modbus_address": 16,
          "type": "AI_Float",
          "iec104_type": 13,
          "iec104_ioa": 2
        }
      ]
    }
  ],
  "iec104": {
    "listen_port": 2404,
    "common_address": 1,
    "k": 12,
    "w": 8,
    "t1": 15,
    "t2": 10,
    "t3": 20
  }
}
```

## 实战代码片段

### Modbus RTU 主站

```c
/* 伪代码：轮询 Modbus 设备 */
void poll_modbus_device(device_t *dev) {
    for (point in dev->points) {
        uint16_t raw[4];
        modbus_read_registers(dev->fd, dev->slave_id,
                              point.modbus_function,
                              point.modbus_address,
                              point.modbus_length,
                              raw);
        if (modbus_response_ok) {
            update_point(point.point_id, raw);
        }
    }
}
```

### IEC 104 Server

```c
/* 伪代码：IEC 104 总召唤响应 */
void on_general_interrogation(iec104_server_t *srv) {
    for (point in all_points) {
        if (point.type == AI_16) {
            send_m_ms_e_11(srv, point.ioa, point.value_16bit, point.quality);
        } else if (point.type == AI_Float) {
            send_m_me_nc_1(srv, point.ioa, point.value_float, point.quality);
        } else if (point.type == DI) {
            send_m_sp_na_1(srv, point.ioa, point.value_bool, point.quality);
        }
    }
    send_c_ic_na_1_end(srv);
}
```

## 实战检查清单

```text
- 内部 Point 模型与 Modbus / IEC 104 映射表
- Modbus 轮询任务（多设备 / 多寄存器）
- IEC 104 总召唤响应 / 突发上报 / 时钟同步
- IEC 104 命令下行到 Modbus 写入
- Float / 32-bit 数据字节序处理
- 时间戳 / 品质处理
- 多设备冲突避免（同一 IOA 不同来源）
- 异常处理（Modbus 错 / IEC 104 错）
```

## 典型陷阱

```text
1. Modbus 字节序错（ABCD vs CDAB）
   解决：实测 + 文档确认

2. IEC 104 时戳不一致
   解决：统一 RTC + 上行时带时间戳

3. Modbus 异常（无响应 / CRC 错）
   解决：超时重试 + 离线缓存

4. IEC 104 命令链超时
   解决：Select → Operate 紧接

5. 多设备冲突
   解决：轮询队列严格分时
```

## 性能指标

| 指标 | 典型值 | 说明 |
| --- | --- | --- |
| Modbus 轮询周期 | 1-5 s | 设备数 |
| IEC 104 总召唤时间 | < 5 s | 100 点 |
| 命令延迟 | < 100 ms | Select → Operate → Modbus 写 |
| 数据吞吐量 | 100 点/s | 突发场景 |
| 缓存能力 | 10000 点 | 24h 离线 |

## 适用场景

```text
- 工业侧：通用 Modbus RTU 设备接入 IEC 104 主站
- 配电侧：配电房测控终端上行
- 新能源：风电 / 光伏场站监控
- 电厂：辅机设备上行
- 储能：储能 EMS 上行
```

## 延伸阅读

- `bus/power-rtu/rtu-gateway-design.md`：RTU 网关总体设计
- `bus/industrial/modbus.md`：Modbus 协议
- `bus/power-rtu/iec104.md`：IEC 104 协议
- `bus/industrial/modbus-rtu-iec104-gateway.md`（本文）