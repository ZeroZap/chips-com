# DNP3 ↔ IEC 104 网关

## 定位

本文是 DNP3 ↔ IEC 104 双向转换网关设计文档。这是国内出海电力 RTU + 国内调度双栈场景的常用网关。

## 场景

```text
现场设备（DNP3）：
  - 北美 / 出海 RTU
  - 标准 DNP3（IEEE 1815）
  - TCP 或串行

上行调度中心（IEC 104）：
  - 国内调度主站
  - 标准 IEC 104
```

或反向：

```text
现场设备（IEC 104）：
  - 国内 RTU
  - 标准 IEC 104
  - TCP

上行（DNP3）：
  - 北美 SCADA 主站
  - 标准 DNP3
```

## 数据流（IEC 104 → DNP3）

```text
1. IEC 104 接收主站召唤
   - 总召唤 C_IC_NA_1
   - 时钟同步 C_CS_NA_1
   - 命令下行 C_SC_NA_1

2. IEC 104 → 内部 Point 模型
   - ASDU Type → Point type
   - IOA → Point ID

3. 上行 DNP3
   - 完整性轮询响应（Class 0）
   - 事件轮询响应（Class 1/2/3）
   - 命令响应
```

## 内部模型映射

| IEC 104 ASDU | 内部 Point | DNP3 Object |
| --- | --- | --- |
| M_SP_NA_1 (Type 1) | DI | g1v1 (Binary Input Static) |
| M_DP_NA_1 (Type 3) | DI (双点) | g1v1 |
| M_ME_NB_1 (Type 11) | AI_16 | g4v2 (16-bit Analog Input Static) |
| M_ME_NC_1 (Type 13) | AI_Float | g4v1 (32-bit Analog Input Static) |
| M_IT_NA_1 (Type 15) | Counter | g3v1 (Counter Static) |
| C_SC_NA_1 (Type 45) | Command | g10v1 (Binary Output) |
| C_SE_NC_1 (Type 50) | Setpoint | g41v1 (Analog Output Command) |

## 数据转换示例

```text
IEC 104 ASDU M_ME_NC_1：
  Type 13, IOA=1, Value=23.5 (IEEE 754 float)

内部 Point：
  ID 1, type=AI_Float, value=23.5

DNP3 g4v1：
  Group 4, Variation 1
  Point Index 1
  Flags = ONLINE (0x01)
  Value = 23.5 (32-bit float IEEE 754)
```

## DNP3 Class 报告转换：

```text
IEC 104 总召唤（突发 + 静态）→ DNP3 完整性轮询响应（Class 0 全部）
IEC 104 突发上报 → DNP3 Class 1/2/3 事件轮询响应
IEC 104 时钟同步 → DNP3 Record Current Time (0x14)
```

## 命令链

```text
调度中心（IEC 104）：
  C_SC_NA_1 单点命令（开关）
  选择 SE=1 → 执行 SE=0

网关转换（DNP3）：
  Select + Operate（两步）

  IEC 104 Select → DNP3 Select
  IEC 104 Operate → DNP3 Operate
  DNP3 响应 → IEC 104 响应

  或 Direct Operate：
  IEC 104 命令 → DNP3 Direct Operate
```

## 配置示例（JSON）

```json
{
  "direction": "iec104_to_dnp3",
  "iec104": {
    "listen_port": 2404,
    "common_address": 1
  },
  "dnp3": {
    "outstation_id": 100,
    "master_ip": "scada.example.com",
    "master_port": 20000,
    "unsolicited_enabled": true,
    "class_1_class_2_class_3_mapping": {
      "iec104_event_priority_high": "Class1",
      "iec104_event_priority_medium": "Class2",
      "iec104_event_priority_low": "Class3"
    }
  },
  "point_mapping": [
    {
      "iec104_ioa": 1,
      "iec104_type": 13,
      "dnp3_group": 4,
      "dnp3_variation": 1,
      "dnp3_point": 1
    }
  ]
}
```

## 实战代码片段

### IEC 104 → DNP3 转换

```c
/* 伪代码 */
void on_iec104_general_interrogation(iec104_server_t *srv) {
    /* 触发 DNP3 完整性轮询响应 */
    dnp3_send_integrity_response(dnp3_master);
    
    /* DNP3 Class 0 全部点 */
    for (point in all_points) {
        dnp3_send_g4v1(dnp3_master, point.index, point.value, point.flags);
    }
    
    /* IEC 104 总召唤结束 */
    iec104_send_c_ic_na_1_end(srv);
}
```

### DNP3 → IEC 104 突发

```c
/* DNP3 未确认报告触发 */
void on_dnp3_event(point_t *point) {
    /* 触发 IEC 104 突发 */
    switch (point->type) {
        case AI_Float:
            iec104_send_m_me_nc_1(iec104_server, point->ioa, point->value);
            break;
        case DI:
            iec104_send_m_sp_na_1(iec104_server, point->ioa, point->value);
            break;
        case Counter:
            iec104_send_m_it_na_1(iec104_server, point->ioa, point->value);
            break;
    }
}
```

## 实战检查清单

```text
- IEC 104 总召唤响应
- DNP3 Class 0 完整性轮询
- DNP3 Class 1/2/3 事件轮询
- DNP3 未确认报告
- 命令链（Select → Operate）
- 时戳一致
- 品质映射
- 异常响应
```

## 典型陷阱

```text
1. DNP3 Class 分配混乱
   解决：明确 Class 0/1/2/3 对应 IEC 104 优先级

2. IEC 104 突发堆积
   解决：限速 + 合并

3. DNP3 未确认报告不响应
   解决：Enable Unsolicited 正确配置

4. 命令链超时
   解决：Select → Operate 紧接

5. 时区不一致
   解决：UTC 统一
```

## 适用场景

```text
- 出海电力 RTU：DNP3 上行 IEC 104 主站
- 国内电力 RTU：IEC 104 上行 DNF 主站
- 双栈 RTU：同时支持国内 + 出海
- 调度双备份：主 DNP3 + 备 IEC 104
```

## 延伸阅读

- `bus/rtu-gateway-design.md`：RTU 网关总体设计
- `bus/dnp3.md`：DNP3 协议
- `bus/iec104.md`：IEC 104 协议