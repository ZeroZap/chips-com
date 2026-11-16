# OBD-II 产线与售后故障案例库

## 目标

把 OBD-II 读取、故障码、就绪状态相关的现场问题写成案例库。每个案例：

- 现象（现场）
- 抓包分析（判断）
- 定位（根因）
- 修复（代码 / 配置）
- 复盘（如何预防）

OBD-II 场景的特殊性：**法规要求数据稳定且可复现**。很多"偶发读数漂移"在法规检测项里就是判不合格。

## 案例 1: ELM327 适配器能连上但读不到任何数据

### 现象

某品牌 OBD 适配器插上后串口能打开、能执行 AT 指令，但发任何 OBD 请求都没响应。换一台车、换一台电脑都一样。

### 抓包分析

用 CAN 分析仪旁路监听：

```text
(总线上有正常流量)
(工具发出了请求吗? —— 抓包看不到任何请求帧)
```

### 定位

`ATDP` 返回 `AUTO` 或 `SAE J1850` —— 这个适配器**不支持 CAN 协议**。

市面上的"ELM327"绝大多数是国产克隆芯片，芯片型号可能是：

```text
- 实际是 ST 的 OBDLink 克隆，只支持 KWP2000 / J1850
- 宣传写 "支持 CAN"，实际靠一个外置 CAN 收发器做转换
```

**判断方法**：

```text
ATZ     -> 返回什么?
ATI     -> 应返回 ELM327 v1.4/v1.5
ATDP    -> 返回当前协议
ATSP6   -> 手动设 CAN 11/500, 然后 ATDP 应显示 ISO 15765-4
```

如果 `ATSP6` 之后 `ATDP` 仍然显示 `AUTO`，芯片不支持 CAN。

### 修复

换适配器。

**选型建议**：

| 需求 | 推荐 |
| --- | --- |
| 只读基础数据 | OBDLink MX+ / Vgate iCar Pro（确认支持 CAN） |
| 需要完整抓包 | PCAN-USB / CANable / USB-CAN（真协议设备） |
| 自己做工具 | PCAN-USB + Python SocketCAN |

**不要用**标称"ELM327 v1.5"的低价白牌。

### 复盘

- 工具链第一件事是**验证协议能力**，不是先试读数据。
- 批量采购时要用**已知车辆 + 已知 PID** 做来料验证，不能只看商品页。
- 产线用的适配器要**固定型号固定版本**，不要混用。

## 案例 2: 读到转速是实际值的 2 倍

### 现象

数据显示发动机转速 4000 rpm，实际怠速只有 2000 rpm。所有基于转速的逻辑（换挡、怠速控制）全乱。

### 抓包分析

```text
请求: 02 41 0C 00 00 00 00 00
响应: 03 41 0C 1A 00 00 00 00
```

响应数据 `0x1A00` = 6656。

### 定位

PID 0x0C（发动机转速）的编码是：

```text
value = (rpm * 4) / 2 = rpm * 2
```

所以：

```text
rpm = value * 2 / 4 = value / 2
    = 6656 / 2 = 3328 rpm
```

工具算成了 `value / 4 = 1664`（偏小）或者直接 `value`（偏大 2 倍）。实际值 3328 对应数据 `0x1A00` 是正确的。

**其他 PID 的编码各不相同**，一张表记不住：

| PID | 编码 |
| --- | --- |
| 0x04 冷却液温度 | value - 40 |
| 0x0C 转速 | value * 2 / 4 |
| 0x0D 车速 | value 直出 |
| 0x11 节气门 | value * 100 / 255 |
| 0x42 电压 | value / 1000 |
| 0x46 环境温度 | value - 40 |

### 修复

```python
def decode_rpm(data: bytes) -> float:
    """PID 0x0C: (rpm * 4) / 2"""
    value = (data[3] << 8) | data[4]
    return value * 2 / 4

def decode_coolant_temp(data: bytes) -> float:
    """PID 0x04: A - 40"""
    return ((data[3] << 8) | data[4]) - 40

def decode_throttle(data: bytes) -> float:
    """PID 0x11: 0-100%"""
    return ((data[3] << 8) | data[4]) * 100 / 255

# 统一解码表
OBD_DECODERS = {
    0x04: lambda v: v - 40,
    0x0C: lambda v: v * 2 / 4,
    0x0D: lambda v: v,
    0x0F: lambda v: v - 40,
    0x11: lambda v: v * 100 / 255,
    0x42: lambda v: v / 1000,
    0x46: lambda v: v - 40,
}
```

### 复盘

- **PID 编码公式必须建表管理**，不要散落在代码各处。
- 每个 PID 的解码都要有单元测试，用已知值验证。
- 团队内共享一份"OBD-II PID 编码表"，不要各自记忆。

## 案例 3: 车速 PID 读回来恒为 0

### 现象

读 Mode 01 PID 0x0D（车速），永远是 0。但车明明在动。

### 抓包分析

```text
请求: 02 41 0D 00 00 00 00 00   (0x7DF)
响应: 03 41 0D 00 00 00 00 00   (0x7E8, ECM)  -> 0
```

抓包发现总线上**另一个 ECU 也在响应**：

```text
响应: 03 41 0D 32 00 00 00 00   (0x7EA, ABS)  -> 50 km/h
```

### 定位

**OBD-II 的功能寻址请求会被所有 ECU 响应**，而不同 PID 由不同 ECU 负责：

```text
0x7E8 ECM  -> 转速, 水温, 负荷, 燃油
0x7E9 TCM  -> 变速箱
0x7E7 / 0x7EA ABS -> 车速 (很多车型由 ABS 提供)
```

工具只取了**第一个响应**（0x7E8 ECM），而 ECM 不提供车速，返回 0。

### 修复

**A. 工具侧：按 PID 绑定响应源 ECU**

```python
# PID -> 期望的响应 ECU
PID_SOURCE_ECU = {
    0x0D: {0x7EA, 0x7E7},      # 车速: ABS
    0x0C: {0x7E8},             # 转速: ECM
    0x04: {0x7E8},             # 水温: ECM
}

def read_pid(pid: int, timeout: float = 2.0) -> Optional[bytes]:
    req = bytes([0x02, 0x41, pid, 0, 0, 0, 0, 0])
    s.send(0x7DF, req)

    expected = PID_SOURCE_ECU.get(pid)
    deadline = time.time() + timeout
    while time.time() < deadline:
        can_id, data = s.recv_from(16)
        if can_id in expected or expected is None:
            return data
    return None
```

**B. 更稳妥：不绑定 ECU，取该 PID 的第一个有效响应**

很多工具的做法是：发出请求后，收集所有响应，**对每个 PID 保留最后一次（或第一个非零）有效值**。

```python
def read_pid_multi_source(pid, timeout=2.0):
    """收集所有 ECU 对该 PID 的响应"""
    req = bytes([0x02, 0x41, pid, 0, 0, 0, 0, 0])
    s.send(0x7DF, req)
    results = []
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            can_id, data = s.recv_from(16)
        except socket.timeout:
            break
        if len(data) >= 3 and data[1] == 0x41 and data[2] == pid:
            results.append((can_id, data))
    return results
```

**C. ECU 侧（可选）**

如果 ECU 侧能实现，在收到自己不提供的 PID 请求时**不响应**，减少总线流量。但法规对响应有强制要求（不支持的 PID 应回 `NOT SUPPORTED`），实现前要查目标市场的法规。

### 复盘

- **OBD-II 是广播多 ECU 响应**，和 UDS 的单播完全不同。工具设计时这是根本区别。
- 车速常由 ABS 提供，是最常见的"读不到"场景。
- 不要假设"响应顺序 = ECU 顺序"。

## 案例 4: 清码后故障码立刻回来

### 现象

用 Mode 04 清除了故障码，读回来是空的。但开一圈路（或原地怠速几十秒），故障码又出现了。

### 抓包分析

```text
>04          -> 04 44 00 00 00 00 00 00   (清码成功)
>03          -> 04 43 01 30 00 00 00 00   (P0130 回来了)
```

### 定位

**清码只清状态，不清故障原因**。

典型根因：

**A. 故障条件持续存在**

```text
氧传感器信号异常 -> 一直报 P0130
进气温度传感器短路 -> 一直报 P0118
```

**B. 清除后 ECU 的自检立即重新置位**

有些 ECU 在清码后立即跑一轮快速自检，发现问题立刻重新置码。

**C. 清码请求本身被部分 ECU 忽略**

```text
请求: 04 00 00 00 00 00 00 00
响应: 04 44 ...     (只有 ECM 回了)
(ABS / 变速箱的码没清)
```

### 修复

**A. 清码前先记录，清码后验证复现**

```text
1. 读 03 (Confirmed) + 07 (Pending) -> 记录
2. 读 02xx 冻结帧 -> 记录
3. 读 05 readiness -> 记录
4. 读相关动态 PID -> 记录故障时的实时数据
5. 执行 04
6. 再读 03 确认已清
7. 修故障 / 断开触发条件
8. 跑驾驶循环
9. 再读 03 确认未复现
```

**B. 判断故障是"持续"还是"间歇"**

```text
- 清码后立即复现 -> 持续故障, 必须修
- 清码后跑一段路才复现 -> 间歇故障, 重点抓 Pending 码和快照
- 清码后不复现 -> 可能已修复或只是触发条件未满足
```

**C. 多 ECU 清码要确认覆盖**

```text
请求后检查: 每个已知 ECU 都回了 0x44
没回的 ECU: 可能有权限要求 / 不支持 Mode 04 / 需要特定条件
```

### 复盘

- **清码是诊断手段，不是修复手段**。
- 每次清码前必须记录 DTC + 冻结帧 + readiness，否则关键证据丢失。
- 售后场景"直接清码交车"是反模式，会把故障线索全部销毁。

## 案例 5: Readiness 永远不全 1，尾气检测不过

### 现象

修完车做尾气检测，报告说"排放系统未就绪"。但已经开了很长距离，跑了多个驾驶循环。

### 抓包分析

```text
>05
01 41 00 24 00 00 00 00

readiness = 0x0024 = 0b0000000000100100
  bit2 = 1   综合 (Comprehensive) 已完成
  bit5 = 1   O2 Sensor 已完成
  其余 = 0
```

### 定位

readiness 位里 bit2（Comprehensive）和 bit5（O2 Sensor）已置位，但**催化器（bit3）、EVAP（bit4）、EGR（bit7）、二次空气（bit8）等都还是 0**。

常见原因：

**A. 监测循环所需的特定工况没跑到**

不同监测项需要不同工况：

```text
催化器监测:  需要车辆以一定速度巡航一段时间
EVAP 监测:    需要特定的燃油液位和加油动作
EGR 监测:     需要特定的负载和车速
失火监测:     需要一定的转速和负载变化
```

只跑市区短途无法满足所有监测项的条件。

**B. 某个监测项持续失败**

```text
EVAP 一直失败 -> EVAP readiness 永远不置位
（常见根因：加油嘴盖没拧紧、气泵故障、炭罐阀卡住）
```

**C. 某个 PID 不支持导致该监测项无法完成**

老车型或特殊配置下，某些监测项不适用。

### 修复

**A. 用 Mode 06 定位是哪个监测项**

```text
>06
08 46 00 81 00 65 00 00 00

监测项结果:
  monitor 1: 0x00  完成且通过
  monitor 2: 0x81  未完成 / 失败 (bit7 = 未通过)
  monitor 3: 0x00  完成
  monitor 4: 0x65  未完成 / 失败
  monitor 5: 0x00  完成
```

```text
0x81 -> 失败, 低 7 bit 是具体故障信息
0x65 -> 失败
```

**Mode 05 只告诉你"没就绪"，Mode 06 告诉你"哪个没就绪"** —— 这是两者配合的核心价值。

**B. 驱动循环（Drive Cycle）**

典型驾驶循环包含：

```text
1. 冷启动, 怠速到工作温度
2. 低速城市驾驶 (含减速)
3. 中速巡航 (50-80 km/h) 持续 5-10 分钟  <- 催化器监测的关键
4. 高速巡航 (80-120 km/h)
5. 减速到停车 (含 EVAP 泄压)
6. 加油 (触发 EVAP 监测)
7. 重新启动怠速
```

**C. 常见 EVAP 未就绪的物理原因**

```text
- 加油口盖没拧紧
- 炭罐通风阀 (purge valve) 卡住
- 炭罐清污电磁阀故障
- EVAP 泄漏检测泵故障
- 密封圈老化
```

### 复盘

- **Mode 05 和 Mode 06 必须配合**，只读 05 排查效率极低。
- readiness 不是"时间够了就置位"，需要**特定工况组合**。
- 售后交付前应主动跑一遍 Mode 06 确认，而不是等尾气检测报告。
- 记录车型对应的标准驾驶循环，作为交付检查项。

## 案例 6: VIN 读不全，只收到前半段

### 现象

读 Mode 09 PID 0x02（VIN，17 字节），只能读到 7 个字符左右就断了。

### 抓包分析

```text
请求: 02 49 02 00 00 00 00 00   (0x7DF)
响应: 07 49 02 56 49 4E 33 30 ...  (0x7E8, DLC=8)
(没有后续帧)
```

### 定位

**VIN 是 17 字节，装不进单帧 8 字节**，必须走 ISO-TP 多帧。但请求用的是 **11 位标准帧寻址**，而多帧传输在 OBD-II 里需要**扩展寻址**（29 位帧）。

两种情况：

**A. 工具只支持 11 位寻址**

```text
标准帧: 0x7DF 请求 / 0x7E8-0x7EB 响应
扩展帧: 0x18DAF110 请求 / 0x18DAF110+n 响应
```

Mode 09 的部分 PID 规范要求用扩展帧。

**B. 工具发的是扩展帧请求，但 ECU 侧的多帧响应没实现**

抓包能看到 FF（First Frame）但没有后续 CF。

### 修复

**A. 工具侧：Mode 09 用扩展寻址**

```python
def read_vin_extended():
    """29 位扩展帧寻址"""
    req = bytes([0x02, 0x49, 0x02, 0, 0, 0, 0, 0])
    # 扩展帧 CAN ID: 0x18DAF110
    s.send(0x18DAF110, req)

    # 收集多帧
    payload = b''
    ...
```

用 SocketCAN 时扩展帧要带 `CAN_EFF_FLAG`：

```python
CAN_EFF_FLAG = 0x80000000
s.send(0x18DAF110 | CAN_EFF_FLAG, req)
```

**B. ECU 侧：实现 ISO-TP 多帧响应**

```c
int obd_mode09_handler(uint8_t pid, uint8_t *resp) {
    switch (pid) {
        case 0x02: {                    /* VIN */
            const char *vin = vehicle_vin();
            /* 17 字节 -> 必须多帧 */
            return isotp_send_multiframe(resp_id, (uint8_t *)vin, 17);
        }
        case 0x04: {                    /* Calibration ID */
            return isotp_send_multiframe(resp_id, cal_id, strlen(cal_id));
        }
    }
    return -1;
}
```

### 复盘

- **Mode 09 的长数据（VIN）必须用扩展寻址 + 多帧**，这是 Mode 09 和其他 Mode 最大的差别。
- 工具要同时支持 11 位和 29 位两种寻址。
- 读到"半个 VIN"是典型的寻址方式错误信号，先查寻址再查 ECU。

## 案例 7: 同一 PID 连续两次读数不同，法规检测不通过

### 现象

工具连续读同一个 PID 10 次，数值每次都不同（转速在 ±20 rpm 范围内跳）。但这本来是正常数据波动。

### 抓包分析

```text
请求 03 41 0C ...
响应 03 41 0C 1A 00 ...
响应 03 41 0C 1A 02 ...   <- 不同
响应 03 41 0C 19 FE ...
```

### 定位

这不只是工具问题 —— **法规检测项明确要求同一 PID 的连续读数一致**。

OBD-II 的检测逻辑：

```text
对同一 PID 连续查询两次（或多次）:
  如果两次结果不一致 -> 判定该 ECU 的 OBD 功能不符合法规

这被称为 "data consistency" / "same PID different value" 检测
```

**根因在 ECU 侧**：PID 数据没有做滤波，直接返回原始捕获值。

```c
/* 错误: 直接返回原始捕获值 */
uint16_t obd_get_rpm(void) {
    return rpm_capture_raw;    /* 每次捕获都略有不同 */
}
```

### 修复

**ECU 侧：加滤波和量化**

```c
/* 低通滤波 */
uint16_t obd_get_rpm(void) {
    static uint16_t filtered = 0;
    uint16_t raw = rpm_capture_raw;

    /* 首帧直接取原值, 之后用 3:1 低通 */
    if (!filter_initialized) {
        filtered = raw;
        filter_initialized = 1;
    } else {
        filtered = (uint16_t)((filtered * 3 + raw) / 4);
    }
    return filtered;
}
```

**还要考虑量化**：某些 PID 需要对齐到规定精度。

```c
/* 车速: 法规要求 km/h 整数, 直接取整即可 */
/* 转速: 通常 0.25 rpm 精度, 但部分实现要求量化到 1 rpm */
uint16_t obd_get_speed(void) {
    return (uint16_t)(speed_kmh_float + 0.5f);   /* 四舍五入 */
}
```

**工具侧：不要把正常波动当故障**

```python
def read_stable_pid(pid, samples=3, tolerance=0):
    """多次采样取一致值, 用于一致性检查"""
    values = []
    for _ in range(samples):
        v = read_pid(pid)
        values.append(v)
    if len(set(values)) == 1:
        return values[0], True
    return values[0], False
```

### 复盘

- **OBD-II 的数据一致性是法规检测项**，ECU 侧必须滤波。
- 这是 ECU 移植时最容易漏的要求 —— 功能"能读出数据"不等于合规。
- 工具侧要做一致性检查，但同时不要因为正常波动就报警。
- 建议在 ECU 自测项里加一条"连续 10 次读数完全一致"的测试。

## 案例 8: 支持位图说支持，实际读不出来

### 现象

读 PID 0x00 支持位图，某一位是 1（表示支持），但实际去读那个 PID 却没响应。

### 抓包分析

```text
>0100
06 41 00 BF 3F B9 00 00 00 00

bit 20 位置: 0xB9 的 bit 5 = 1  -> PID 0x20 支持

>0120
(无响应)
```

### 定位

三种可能：

**A. 支持位图是 ECU 宣称的，但该 PID 由别的 ECU 提供**

ECM 声明支持 PID 0x20，实际响应来自另一个 ECU，而那个 ECU 此时不在线或响应被过滤。

**B. 位图解读错误**

支持位图是**大端 4 字节**，bit 顺序要仔细：

```text
PID 0x00 响应: byte3 byte4 byte5 byte6
  byte3 的 bit7 (0x80) -> PID 0x01
  byte3 的 bit0 (0x01) -> PID 0x08
  byte4 的 bit7 (0x80) -> PID 0x09
  ...
  byte6 的 bit0 (0x01) -> PID 0x20
```

映射关系：

```text
PID = 0x01 + (byte_index * 8) + (7 - bit_index)
```

byte_index = 0..3, bit_index = 0..7

**C. 支持位图覆盖范围有限**

```text
PID 0x00 -> 覆盖 PID 0x01 ~ 0x20
PID 0x20 -> 覆盖 PID 0x21 ~ 0x40
PID 0x40 -> 覆盖 PID 0x41 ~ 0x60
PID 0x60 -> 覆盖 PID 0x61 ~ 0x80
```

PID 0x41 之后的必须读 PID 0x40 的位图，不能只读 0x00 就以为全知道。

### 修复

**A. 工具侧：读到的位图是"该 ECU 声称支持"，不等于"总线一定读得到"**

```python
def discover_pids():
    """按规范逐块读支持位图"""
    supported = set()
    for block_pid, base in ((0x00, 0x01), (0x20, 0x21),
                            (0x40, 0x41), (0x60, 0x61)):
        resp = read_pid(block_pid)
        if resp is None:
            continue
        bitmap = resp[3:7]
        for byte_idx in range(4):
            b = bitmap[byte_idx]
            for bit_idx in range(8):
                if b & (0x80 >> bit_idx):
                    supported.add(base + byte_idx * 8 + bit_idx)
    return supported
```

**B. 位图解析必须用统一函数**

```python
def bitmap_to_pids(bitmap_bytes, base_pid):
    """bitmap_bytes 是 4 字节大端"""
    pids = []
    for byte_idx in range(4):
        b = bitmap_bytes[byte_idx]
        for bit_idx in range(8):
            if b & (0x80 >> bit_idx):
                pids.append(base_pid + byte_idx * 8 + bit_idx)
    return pids
```

### 复盘

- 支持位图是**分块**的，四个块都要读。
- 位序是 **MSB first**（bit7 对应块内第一个 PID）。
- 位图声明的是"本 ECU 支持"，实际可用性还要看总线和其他 ECU 状态。

## 案例 9: Mode 06 读不到，扩展帧没使能

### 现象

Mode 05 能读，Mode 06 读不到。抓包能看到请求发出去，但没响应。

### 抓包分析

```text
请求: 02 46 00 00 00 00 00 00   (0x7DF, 11 位)
(无响应)

请求: 02 46 00 00 00 00 00 00   (0x18DAF110, 29 位)
响应: 08 46 00 81 00 65 00 00 00   (0x18DAF110+1)
```

### 定位

**Mode 06（以及 Mode 09）在部分车型上要求扩展寻址**。

原因是 Mode 06 的响应可能比较长（多个监测项），单帧 8 字节不够；而且法规在某些版本里指定 Mode 06/08/09 用扩展帧传输。

**同一个 Mode 内也可能混用**：例如 Mode 06 的 PID 0x00（监测项数量）能用 11 位读，但完整列表需要 29 位。

### 修复

**工具侧：扩展寻址优先，标准寻址兜底**

```python
def request_obd(mode: int, pid: int, timeout: float = 2.0):
    """先试标准帧, 再试扩展帧"""
    payload = bytes([0x02, 0x40 | mode, pid, 0, 0, 0, 0, 0])

    # 1. 11 位标准帧
    s.send(0x7DF, payload)
    r = wait_response(0x7E8, timeout=timeout * 0.4)
    if r:
        return r

    # 2. 29 位扩展帧
    s.send(0x18DAF110 | CAN_EFF_FLAG, payload)
    r = wait_response_ext(0x18DAF110, timeout=timeout * 0.6)
    return r
```

**注意响应 ID**：扩展帧下响应可能是 `0x18DAF110 + n`，n 取决于哪个 ECU 响应。

### 复盘

- **Mode 06/08/09 优先用扩展帧**。
- 工具要同时支持两种寻址，并且要能处理"扩展帧响应 ID 带偏移"。
- 遇到"某个 Mode 读不到"先试寻址方式，再查 ECU 实现。

## 案例 10: 长时间未关引擎，Mode 04 清码后码又回来

### 现象

修完一个故障码，车主短时间试车没问题。过了两天故障码又回来了，而且这次是同一个码。

### 抓包分析

```text
第一次清码后: 03 43 00 00 00 00 00 00   (空)
两天后:       03 43 01 30 00 00 00 00   (P0130 回来了)
```

### 定位

**间歇性故障**，清码时故障条件恰好不成立，所以清掉了，但根因没解决。

P0130（进气温度传感器电路）的常见间歇根因：

```text
- 插接件接触不良（热插拔后氧化）
- 线束在振动部位磨破（间歇断路）
- 传感器内部间歇失效
- ECU 线束与高温件距离过近，热变形
```

**关键教训**：清码后"故障不再出现"不等于"故障已修复"。间歇故障需要靠 Pending 码 + 冻结帧 + 动态数据来定位。

### 修复

**A. 间歇故障的定位方法**

```text
1. 记录第一次出现的完整信息:
   - Mode 03 / 07 的码
   - Mode 02 冻结帧 (故障瞬间的转速/水温/负载)
   - 故障前后的动态 PID 波形

2. 冻结帧是金矿:
   - 故障时转速多少? 温度多少?
   - 对照故障模式推断触发条件

3. 高频采样关键 PID:
   - 连续记录进气温度 (PID 0x0F)
   - 看是否有跳变 (瞬间从正常值跳到 -40 或 255)

4. 物理检查:
   - 拉扯线束看是否复现
   - 加热插接件看是否复现
   - 检查连接器锁扣是否到位
```

**B. 冻结帧的利用**

```text
P0130 触发时冻结帧:
  转速 800 rpm, 水温 90C, 进气温度 -40C

-> 判断: 进气温度传感器在暖机后失效
-> 范围: 传感器本体或插接件热劣化
```

**C. 不要用"清码后不出现"结案**

```text
维修交付标准:
  - 故障码清除且在完整驾驶循环内不复现
  - 冻结帧已分析
  - 根因有物理解释, 不是"猜测已修复"
```

### 复盘

- **间歇性故障是售后最难的部分**，靠清码掩盖是最常见的错误处理。
- 冻结帧必须在下一次清码之前保存。
- 供应商层面，要向客户说明"已记录故障快照"，而不是"已清码"。
- 建议工具链自动归档每次清码前的 DTC + 冻结帧快照。

## 案例 11: 响应 DLC 不是 8，解析偏移全错

### 现象

工具解析响应时数据全错位。抓包发现收到的帧 DLC 只有 3，但解析代码按 8 字节读。

### 抓包分析

```text
candump 输出:
  can0  7E8  [3]  41 0C 1A
```

DLC = 3，实际数据只有 3 字节。

### 定位

两种情况：

**A. 这是 ISO-TP 单帧格式（CAN FD 或自定义实现）**

```text
Classic CAN 单帧（OBD-II 标准做法）:
  8 bytes: [len, 0x41, PID, d1, d2, d3, d4, d5]

ISO-TP 单帧:
  3 bytes: [0x03, 0x41, 0x0C]   <- 但 ISO-TP 的 PCI 会覆盖长度
```

**注意区分**：OBD-II 在 Classic CAN 上的标准格式是 **8 字节固定**，第 0 字节是数据长度。ISO-TP 是另一种封装。

看数据内容：

```text
8 字节 [03, 41, 0C, 1A, 00, 00, 00, 00]
  ^  ^   ^   ^
  |  |   |   └── 数据
  |  |   └────── PID
  |  └────────── 0x41 = 响应 Mode
  └───────────── 数据长度 = 3 (后续有 3 字节)

ISO-TP 单帧 [03, 41, 0C, ...]
  ^  ^
  |  └── 第一字节是 PCI (低 4 bit = 长度), 不是 Mode!
  └───── PCI
```

**ISO-TP 单帧的第一字节是 PCI（0x03），第二个字节才是 0x41** —— 但这正好和 OBD-II 的 `03 41 ...` 撞了！区别在于 ISO-TP 单帧只有 3 字节（PCI + 2 字节数据），而 OBD-II 是固定 8 字节。

**B. 工具的 DLC 处理写死了 8**

```python
# 错误
data = frame[0:8]     # DLC=3 时会读到垃圾

# 正确
dlc = frame.dlc if hasattr(frame, 'dlc') else len(frame)
data = frame[:dlc]
```

### 修复

**A. 正确解析 OBD-II 单帧**

```python
def parse_obd_response(data: bytes) -> Optional[dict]:
    """
    OBD-II Classic CAN 格式: 固定 8 字节
    byte0 = 数据长度 (不含自身)
    byte1 = 0x40 | Mode
    byte2 = PID
    """
    if len(data) < 3:
        return None

    # 判断是 OBD-II 8 字节格式还是 ISO-TP 单帧
    if len(data) == 8:
        length = data[0]
        if length > 7 or not (0x40 <= data[1] <= 0x49):
            return None
        mode = data[1] & 0xBF
        pid = data[2]
        payload = data[3:3 + length - 2]
        return {'mode': mode, 'pid': pid, 'data': payload}

    # ISO-TP 单帧
    if (data[0] & 0xF0) == 0x00:
        length = data[0] & 0x0F
        return {'mode': data[1] & 0xBF, 'pid': data[2],
                'data': data[3:3 + length]}

    return None
```

**B. 永远按实际 DLC 读**

```python
dlc = getattr(frame, 'dlc', len(frame))
payload = bytes(frame)[:dlc]
```

### 复盘

- **Classic CAN 上 OBD-II 是固定 8 字节**；CAN FD 或定制实现可能是 ISO-TP 变长。
- 解析代码要按 DLC 取数据，不能写死 8。
- 抓包看 DLC 是判断"格式对不对"的第一步。

## 案例 12: 工具发请求没设"单次响应"模式，响应刷屏

### 现象

用 Python SocketCAN 写 OBD 工具，每发一次请求，总线上返回好几帧一模一样的响应，日志刷屏。

### 抓包分析

```text
请求: 02 41 0C 00 00 00 00 00   (0x7DF)
响应: 03 41 0C 1A 00 00 00 00   (0x7E8)
响应: 03 41 0C 1A 00 00 00 00   (0x7E8)   <- 重复
响应: 03 41 0C 1A 00 00 00 00   (0x7E8)   <- 重复
```

### 定位

**CAN 控制器默认处于"自收自发"（loopback / 自回显）模式**，会把总线上的帧再回收到自己的接收 FIFO。

Python SocketCAN 默认也会收到自己发送的帧。

另外，ELM327 的 `ATCAF1`（关闭自动过滤）如果没设，适配器会过滤掉部分帧；反过来，如果 CAN 控制器的**回环模式**没关，会收到自己发的请求。

### 修复

**A. 关闭 SocketCAN 的本机回显**

```python
# Linux: 关闭 loopback
s.setsockopt(socket.SOL_CAN_RAW, CAN_RAW_LOOPBACK, 0)

# 关闭本机过滤 (只收 CAN ID, 不收自己发的)
s.setsockopt(socket.SOL_CAN_RAW, CAN_RAW_RECV_OWN_MSGS, 0)
```

**B. 过滤掉请求 ID**

```python
REQ_ID = 0x7DF
can_id, data = s.recv_from(16)
if can_id == REQ_ID:
    continue      # 跳过自己发的请求
```

**C. 每次请求只取第一个匹配响应**

```python
def read_pid_once(pid, timeout=2.0):
    req = bytes([0x02, 0x41, pid, 0, 0, 0, 0, 0])
    s.send(0x7DF, req)

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            can_id, data = s.recv_from(16)
        except socket.timeout:
            return None
        if can_id == REQ_ID:
            continue
        if len(data) >= 3 and data[1] == 0x41 and data[2] == pid:
            return data       # 只取第一个
    return None
```

**D. 用请求 ID 做同步屏障**

```python
def request_with_barrier(req_id, payload, resp_ids, timeout=2.0):
    """发请求前清空接收队列, 避免读到上一次的残留"""
    s.setblocking(False)
    try:
        while True:
            s.recv_from(16)
    except BlockingIOError:
        pass
    s.setblocking(True)
    s.settimeout(timeout)

    s.send(req_id, payload)
    ...
```

### 复盘

- **SocketCAN 要显式关 LOOPBACK 和 RECV_OWN_MSGS**，否则自己发的请求会被当成响应。
- 每次请求前**清空接收队列**，否则会读到上一条请求的延迟响应，解析串位。
- 用请求 ID 和 PID 双重过滤，定位问题时能快速分辨"响应串了"和"响应错了"。

## 根因清单

| 根因 | 典型症状 | 快速验证 |
| --- | --- | --- |
| 适配器不支持 CAN | 全部无响应 | `ATDP` 是否为 AUTO / J1850 |
| PID 解码公式错 | 转速 2 倍、温度高 40 度 | 对照编码表 |
| 响应源 ECU 选错 | 车速恒 0 | 看有没有 0x7EA 响应 |
| 故障条件未消除 | 清码后立刻复现 | 读冻结帧定位根因 |
| 监测工况未跑到 | readiness 永远不全 1 | Mode 06 定位失败项 |
| 寻址方式不对 | VIN 只读一半 | 试 29 位扩展帧 |
| ECU 无数据滤波 | 连续读数不一致 | 连读 10 次比对 |
| 位图解读错误 | 位图说有但读不到 | 四个块都读 + MSB first |
| DLC 处理写死 8 | 解析全错位 | 看抓包 DLC |
| 自回显未关 | 响应刷屏 | 关 LOOPBACK + 清队列 |
| 间歇故障被掩盖 | 几天后同码复现 | 冻结帧 + 动态波形 |
| 不支持 Mode 也响应 | 总线流量异常 | 检查 Mode 白名单 |

## 关联主题

- `bus/automotive/obd2.md` — OBD-II 概览、九个 Mode、PID 速查
- `bus/automotive/obd2-deep-dive.md` — PID 空间、I/M 监测模型、Mode 详解
- `bus/automotive/obd2-practical.md` — 工具链、调试流程、检查清单
- `bus/automotive/uds-failure-cases.md` — UDS 案例（OBD-II 的对照）
- `bus/automotive/iso-tp-failure-cases.md` — 传输层案例
- `basic/can-failure-cases.md` — CAN 物理层/链路层案例
- `bus/automotive/can-protocol-family.md` — CAN 家族全景

## 更新记录

- 2026-10-31: 初版，12 个案例。覆盖适配器能力、PID 解码、多 ECU 响应源、清码复现、I/M 就绪诊断、VIN 多帧、数据一致性、支持位图、扩展寻址、间歇故障定位、DLC 解析、自回显等高频坑。
