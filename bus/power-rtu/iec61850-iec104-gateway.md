# IEC 61850 ↔ IEC 104 网关

## 定位

本文是 IEC 61850 ↔ IEC 104 双向转换网关设计文档。这是变电站双栈场景：站内 IEC 61850 IED 通过网关转 IEC 104 上调度中心。

## 场景

```text
站内 IED（IEC 61850）：
  - 保护装置、测控装置、智能终端
  - 标准 IEC 61850（MMS + GOOSE + SV）

上行调度中心（IEC 104）：
  - 电力主站
  - 标准 IEC 104
```

或反向：

```text
站控（IEC 104）→ 站内（IEC 61850）
```

## 数据流

```text
1. IEC 61850 MMS 接入 IED
   - Initiate / Activate
   - Browse / Read / Write
   - SubscribeCOV / InformationReport

2. IEC 61850 → 内部 Point 模型
   - LN/DO/DA → Point ID
   - Functional Constraint 分类
   - 数据对象实例名

3. IEC 104 Server
   - 总召唤响应
   - 时钟同步响应
   - 突发上报
   - 命令下行

4. 反向：IEC 104 命令 → IEC 61850 命令
```

## IEC 61850 LN ↔ IEC 104 ASDU

| IEC 61850 LN | DO | IEC 104 ASDU |
| --- | --- | --- |
| XCBR | Pos.stVal | M_DP_NA_1 (Type 3) |
| XSWI | Pos.stVal | M_DP_NA_1 |
| CSWI | Pos.stVal / Loc.stVal | M_DP_NA_1 / M_SP_NA_1 |
| MMXU | TotW.mag.f | M_ME_NC_1 (Type 13) |
| MMXU | PhV.phsA.cVal.mag.f | M_ME_NC_1 |
| TCTR | Amp.instMag.f | M_ME_NC_1 |
| PIOC | Str.general | M_SP_NA_1 |
| CILO | EnaOpn.stVal | M_SP_NA_1 |

## 数据转换示例

```text
IEC 61850 LD0/MMXU1.TotW.mag.f：
  Functional Constraint: MX
  Value: Double = 1234.5 (kW)

内部 Point：
  ID 1, type=AI_Float, unit=kW, value=1234.5

IEC 104 ASDU M_ME_NC_1：
  Type 13, IOA=1
  ASDU body: 4 字节 IEEE 754 float
  0x449A4000 = 1234.5
```

## 命令反向

```text
调度中心 IEC 104：
  C_DC_NA_1 双点命令（开关合闸）

网关转换 IEC 61850：
  Object: LD0/XCBR1.Pos
  ctlModel: SBO
  Control:
    SelectWithValue ctlVal=true
    Operate ctlVal=true
  或 Direct Operate

IEC 61850 响应 → IEC 104 应答
```

## GOOSE / SV 处理

```text
GOOSE（站内）：
  - 保护跳闸事件
  - 多播接收
  - 转换为 IEC 104 突发：
    M_SP_NA_1 (保护动作)
    M_DP_NA_1 (开关变位)

SV（站内）：
  - 采样值（4.8 kHz）
  - IEC 104 不支持原始 SV
  - 转换为 IEC 104 短浮点：
    M_ME_NC_1 (电流 / 电压瞬时)
```

## 配置示例（JSON）

```json
{
  "iec61850": {
    "ied_ip": "192.168.1.100",
    "ied_ap_name": "AP1",
    "ied_ld": "LD0",
    "mms_port": 102
  },
  "iec104": {
    "listen_port": 2404,
    "common_address": 1
  },
  "point_mapping": [
    {
      "iec61850_path": "LD0/XCBR1.Pos.stVal",
      "iec104_ioa": 1,
      "iec104_type": 3,
      "fc": "ST"
    },
    {
      "iec61850_path": "LD0/MMXU1.TotW.mag.f",
      "iec104_ioa": 2,
      "iec104_type": 13,
      "fc": "MX"
    }
  ],
  "command_mapping": [
    {
      "iec104_ioa": 100,
      "iec61850_path": "LD0/XCBR1.Pos",
      "control_model": "SBO"
    }
  ]
}
```

## 实战代码片段

### IEC 61850 → IEC 104 突发

```c
/* 伪代码：IEC 61850 Report → IEC 104 */
void on_iec61850_information_report(BRCB brcb, DataSet dataSet) {
    for (da in dataSet.values) {
        point_t *point = lookup_point_by_ln_da_da(da.path);
        
        if (point == NULL) continue;
        
        /* 更新内部 Point */
        point_update(point, da.value, da.quality, da.timestamp);
        
        /* IEC 104 突发 */
        switch (point->type) {
            case AI_Float:
                iec104_send_m_me_nc_1(server, point->ioa, da.value);
                break;
            case DI:
                iec104_send_m_sp_na_1(server, point->ioa, da.value);
                break;
        }
    }
}
```

### IEC 104 命令 → IEC 61850

```c
/* 伪代码：IEC 104 命令 → IEC 61850 MMS */
void on_iec104_command_c_dc_na_1(uint32_t ioa, uint8_t dcmd) {
    point_t *point = lookup_point_by_ioa(ioa);
    
    /* IEC 61850 MMS Command */
    if (point->control_model == SBO) {
        iec61850_select(point->path, dcmd);
        iec61850_operate(point->path, dcmd);
    } else {
        iec61850_direct_operate(point->path, dcmd);
    }
    
    /* IEC 104 应答 */
    iec104_send_operate_response(server, ioa, OK);
}
```

## 实战检查清单

```text
- IEC 61850 MMS Initiate / Activate
- IEC 61850 Browse / Read / Write
- IEC 61850 SubscribeCOV / InformationReport
- IEC 61850 命令链（Select / Operate）
- IEC 104 总召唤响应
- IEC 104 时钟同步
- IEC 104 突发上报
- GOOSE 多播接收（如保护）
- SV 采样值转换
- 数据映射表
- 时戳统一
- 品质映射
```

## 典型陷阱

```text
1. IEC 61850 Reference 错
   解决：精确匹配 LN/DO/DA

2. IEC 61850 控制模型错
   解决：识别 SBO / Direct / EnhancedSecurity

3. GOOSE 多播不通
   解决：网卡加入多播组

4. IEC 104 时戳不一致
   解决：UTC 统一

5. 数据精度丢失
   解决：IEC 61850 用 IEEE 754 float
```

## 适用场景

```text
- 智能变电站：IEC 61850 → IEC 104 上行调度
- 数字化变电站双栈
- IEC 61850 测试工具 → IEC 104 主站
- IEC 61850 保护 + IEC 104 SCADA 联合
```

## 延伸阅读

- `bus/power-rtu/rtu-gateway-design.md`：RTU 网关总体设计
- `bus/power-rtu/iec61850.md`：IEC 61850 协议
- `bus/power-rtu/iec104.md`：IEC 104 协议