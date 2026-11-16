---
tags:
  - layer/bus
  - type/gateway-design
  - protocol/dlt645
  - topic/power-rtu
---

# DL/T 645 ↔ IEC 104 网关

## 定位

本文是 DL/T 645（电表协议）转 IEC 104（电力调度协议）的网关设计文档。这是国内电力 RTU 接入电表场景的常用网关。

## 场景

```text
现场设备（DL/T 645）：
  - 单相 / 三相电能表
  - 标准 DL/T 645-2007
  - RS485 总线

上行调度中心（IEC 104）：
  - 电力主站 / 配电主站
  - 标准 IEC 104 协议
  - TCP 长连接
```

## 数据流

```text
1. 网关按配置轮询电表（DL/T 645 Master）
   - 读 DI=00000000 总电能
   - 读 DI=02010100 A 相电压
   - 读 DI=02010300 A 相有功功率

2. 解析 DL/T 645 响应（BCD 解码）→ 内部 Point 模型
   - 总电能 → Point ID 1, type=Accumulator, value=12345.67 kWh
   - A 相电压 → Point ID 2, type=AI, value=220.1 V
   - 有功功率 → Point ID 3, type=AI, value=500.0 W

3. 上行 IEC 104
   - 累积量 M_IT_NA_1（电能）
   - 短浮点 M_ME_NC_1（电压、功率）
   - 时钟同步
```

## 内部模型映射

| DL/T 645 DI | 内部 Point | IEC 104 |
| --- | --- | --- |
| 00000000 (总电能) | Accumulator (BCD 4 字节) | M_IT_NA_1 (Type 15) |
| 00010000 (正向有功总电能) | Accumulator | M_IT_NA_1 |
| 02010100 (A 相电压) | AI (10 位小数 V) | M_ME_NC_1 (Type 13) |
| 02010200 (A 相电流) | AI (100 位小数 A) | M_ME_NC_1 |
| 02010300 (A 相有功) | AI (1000 位小数 kW) | M_ME_NC_1 |
| 04000100 (功率因数) | AI (1000 位小数) | M_ME_NC_1 |
| 05000100 (电池电压) | AI (10 位小数 V) | M_ME_NC_1 |
| 06000100 (阀门状态) | DI | M_SP_NA_1 (Type 1) |

## BCD 解码

```c
/* DL/T 645 BCD 解码示例：总电能 */
uint32_t bcd_decode(uint8_t *data, int len) {
    uint32_t val = 0;
    for (int i = 0; i < len; i++) {
        val = val * 100 + ((data[i] >> 4) * 10) + (data[i] & 0x0F);
    }
    return val;
}

/* 总电能 0000 0000 → 4 字节 BCD */
uint32_t raw_energy = bcd_decode(buf, 4);  // 例：0x12345678 → 12345678
float energy = raw_energy / 1000.0;       // 4 位小数 → kWh
```

## 数据转换示例

```text
DL/T 645 DATA = 0x12345678（4 字节 BCD）
BCD 解码：12345678
总电能：12345.67 kWh

内部 Point：
  ID 1, type=Accumulator, value=12345.67 kWh

IEC 104 ASDU M_IT_NA_1：
  Type 15 (M_IT_NA_1)
  ASDU body: 4 字节 binary counter (BSI = 1)
  0x00BC614E (= 12345.67 × 100 = 1234567 → 0x12D687)

实际工程中按 IEC 104 标准编码 BCD 或 32-bit binary。
```

## 命令下行

```text
调度中心 IEC 104：
  C_SC_NA_1 开关
  C_SE_NC_1 短浮点设定（电表参数）

网关转换：
  IEC 104 命令 → DL/T 645 写命令
  - C_SE_NC_1 (设定最大需量 10.0) → DL/T 645 Write DI=01000000 10.0
  - C_SC_NA_1 (合闸) → DL/T 645 Write DI=06000100 (特殊）

写入流程：
  1. IEC 104 Select → 内部命令缓存
  2. IEC 104 DL/T 645 修改密码（写数据前）
  3. IEC 104 Operate → DL/T 645 写入
  4. IEC 104 应答 ← DL/T 645 响应
```

## 配置示例（JSON）

```json
{
  "devices": [
    {
      "device_id": "Meter_1",
      "protocol": "dlt645",
      "interface": "/dev/ttyS0",
      "baud_rate": 2400,
      "parity": "E",
      "address": "123456789012",
      "points": [
        {
          "point_id": 1,
          "dlt645_di": "00000000",
          "type": "Accumulator",
          "unit": "kWh",
          "iec104_type": 15,
          "iec104_ioa": 1
        },
        {
          "point_id": 2,
          "dlt645_di": "02010100",
          "type": "AI_Voltage",
          "unit": "V",
          "iec104_type": 13,
          "iec104_ioa": 2
        }
      ]
    }
  ],
  "iec104": {
    "listen_port": 2404,
    "common_address": 1
  }
}
```

## 实战代码片段

### DL/T 645 读电表

```c
/* 伪代码 */
uint8_t read_dlt645_data(int fd, uint8_t *addr_7byte,
                         uint32_t di, uint8_t *value, int *len) {
    uint8_t frame[64];
    int frame_len = build_dlt645_read_frame(addr_7byte, di, frame);
    rs485_send(fd, frame, frame_len);
    
    uint8_t resp[64];
    int n = rs485_recv(fd, resp, sizeof(resp), 3.5 * 10 / baud_rate_ms);
    
    if (n > 0 && verify_cs(resp, n)) {
        extract_dlt645_data(resp, n, value, len);
        return OK;
    }
    return ERR;
}
```

### BCD 解码 + IEC 104 上行

```c
/* 伪代码 */
void on_total_energy_change(uint8_t *bcd_data, int len) {
    uint32_t raw = bcd_decode(bcd_data, 4);
    float energy = raw / 1000.0;  // 3 位小数 → kWh
    
    /* 更新内部 Point */
    point_update(1, energy);
    
    /* IEC 104 突发 */
    iec104_send_m_it_na_1(server, ioa=1, value=raw, bsi=1);
}
```

## 实战检查清单

```text
- DL/T 645 多电表轮询（地址 + DI）
- BCD 解码正确（按 DI 字典）
- 字节序 / 单位转换正确
- IEC 104 ASDU 类型映射（M_IT_NA_1 / M_ME_NC_1 / M_SP_NA_1）
- DL/T 645 写数据密码流程
- IEC 104 命令链（Select → Operate → DL/T 645 写）
- DL/T 645 多帧协议（块读）支持
- 异常处理（DL/T 645 ERR / IEC 104 异常）
```

## 典型陷阱

```text
1. BCD 解码按二进制搞反
   解决：必须 BCD 解码

2. DL/T 645 写数据未先改密码
   解决：流程固化

3. DL/T 645 多电表地址冲突
   解决：地址分配表 + 严格分时

4. 电表 DI 字典错位
   解决：DI 字典表 + 实测

5. IEC 104 累积量类型与 DL/T 645 不匹配
   解决：BSI / SQU 字段调整
```

## 适用场景

```text
- 配电房 RTU：电表 + 开关 + 传感器上行 IEC 104
- 工业能耗监测：工厂电表 → IEC 104 上行电力调度
- 楼宇能源：商业楼宇电表 → IEC 104
- 新能源场站：储能 / 逆变器 / 电表 → IEC 104
```

## 延伸阅读

- `bus/power-rtu/rtu-gateway-design.md`：RTU 网关总体设计
- `bus/power-rtu/dlt645.md`：DL/T 645 协议
- `bus/power-rtu/iec104.md`：IEC 104 协议
- `bus/industrial/modbus-rtu-iec104-gateway.md`：相关 Modbus 网关