# OBD-II Practical Guide

## 目标

本文面向用 OBD-II 做实测、排障和工具开发的人，覆盖：

- 工具链选型和 ELM327 命令。
- candump / cansniffer 抓包方法。
- 手写 OBD 请求的调试步骤。
- 常见读数异常的定位顺序。
- 产线 / 售后场景的具体操作。

## 最小前提

先确认裸 CAN 正常：

- 车辆点火 ON（ON 不必打火，但需要给 ECU 供电）。
- 诊断口 16 针 J1962 的 CAN 相关针脚通。
- 车辆总线负载正常（关窗、关空调等大负载设备可减少干扰）。
- 至少有 CAN 分析仪或可用的 OBD 适配器。

OBD-II 是应用层协议，不解决物理层问题。

## 工具链

### 三类工具

| 类型 | 代表 | 用途 | 局限 |
| --- | --- | --- | --- |
| OBD 适配器 | ELM327 / OBDLink / Vgate iCar Pro | 车机连接、读基础数据 | 协议兼容性差，多为串口透传 |
| CAN 分析仪 | PCAN-USB / CANable / USB-CAN | 全量抓包、协议分析 | 需要自己解析报文 |
| 诊断仪 | 专用诊断设备 | 完整功能 | 贵，且常按车型收费 |

**ELM327 的坑**：市面绝大多数 ELM327 是**克隆芯片**，芯片只支持 KWP2000 / J1850 / ISO 9141，**不支持 CAN**。上 CAN 前先用 AT 指令确认。

```text
ATZ      -> 应返回 OK 或 ELM327 v1.5
ATDP     -> 应显示当前协议, 正常是 ISO 15765-4 (CAN 11/500)
ATSP6    -> 手动设 CAN 11 位 500k
ATSP7    -> 手动设 CAN 29 位 500k
ATSP8    -> 手动设 CAN 11 位 250k
ATSP9    -> 手动设 CAN 29 位 250k
ATSPa    -> 手动设 CAN 11 位 1000k
```

看到 `ATDP` 返回 `AUTO` 或 `SAE J1850` → 这个适配器**不支持 CAN**，必须换。

### ELM327 常用指令

```text
ATZ      复位
ATI      芯片版本 (识别克隆)
ATE0     关闭回显 (必须, 否则收到自己的命令)
ATH0     关闭标题 (不显示 CAN ID, 更清爽)
ATS0     关闭空格
ATL0     关闭换行
ATM0     关闭单色字符
ATAT1    自适应时序 (自动适配 ECU 响应时间)
ATDP     当前协议
ATRV     读取 ECU 电压
ATCAF1   关闭自动过滤 (否则会过滤掉部分帧)
```

**注意 `ATE0`**：不回显关闭时，工具收到的每一行前面都带着自己发的命令，解析会全错。

### 发送 OBD 请求

```text
>010C          读发动机转速 (Mode 01 PID 0C)
41 0C 1A 00    响应
```

多 PID 合并查询（法规允许，但 ECU 实现差异大）：

```text
>010C          读转速 + PID 1F (运行时间)
41 0C 1A 00
41 1F 87 1E
```

**建议**：一次只读一个 PID。多 PID 合并在很多车系上返回不完整，调试时容易误判。

## 抓包分析

### 用 candump

```bash
# 抓全部 CAN 帧
candump -t z can0

# 只看 OBD 相关 ID
candump -t z can0,7DF:7DF

# 抓 10 秒写文件
candump -t z -l 10000 can0 > obd.log
```

### 用 cansniffer

```bash
cansniffer -c 3 -i 1 can0     # 3 通道, 1 秒刷新
```

### 用 SocketCAN + Python

```python
import socket

s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
s.bind(('can0',))
s.settimeout(1.0)

# 发 OBD 请求: 0x7DF 广播
req = bytes([0x02, 0x41, 0x0C, 0x00, 0x00, 0x00, 0x00, 0x00])
s.send(0x7DF, req)

# 收响应
while True:
    try:
        can_id, data = s.recv_from(16)
        if can_id in (0x7E8, 0x7E9, 0x7EA, 0x7EB):
            print(f"0x{can_id:03X}: {data.hex(' ')}")
            break
    except socket.timeout:
        print("timeout")
        break
```

### 抓包该看什么

```text
1. 有没有请求帧发出去 (0x7DF)
2. 有没有响应帧回来 (0x7E8/7E9/7EA/7EB)
3. 响应帧的 DLC 是不是 8
4. 响应内容是不是 [len, 0x4X, PID, data...]
5. 有没有错误帧 (can_id & 0x40000000)
```

**DLC 检查**：OBD 响应通常固定 8 字节。如果收到 DLC=3，说明用了 ISO-TP 单帧（这是 CAN FD 场景或自定义实现），要相应调整解析。

## 调试步骤

### 标准流程

```text
1. 点火 ON
2. 确认适配器支持 CAN (ATDP)
3. ATCAF1 + ATE0 + ATH0
4. 抓包看总线是否有流量
5. 发 010C (转速) 验证基本链路
6. 发 0100 拿支持位图
7. 按位图逐个读 PID
8. 发 03 读故障码
9. 发 05 / 06 读就绪状态
10. 发 09 02 读 VIN
```

### 定位"读不到数据"

```text
抓包确认请求帧发出去了吗?
  |
  +-- 没发出 -> 工具问题 (串口 / 适配器 / 指令)
  |
  +-- 发出去了, 有响应吗?
        |
        +-- 无响应 -> 查: 寻址方式 / 波特率 / ECU 是否在线 / 车辆条件
        |
        +-- 有响应但内容不对 -> 查: 解码公式 / 支持位图 / 响应来源 ECU
```

## 各 Mode 实操

### 读实时数据

```text
>010C        转速
>0104        冷却液温度
>010D        车速
>010F        进气温度
>0111        节气门
>0142        模块电压
>0100        PID 01-20 支持位图
>0120        PID 21-40 支持位图
>0140        PID 41-60 支持位图
>0160        PID 61-80 支持位图
```

### 读故障码

```text
>03          排放相关故障码 (Confirmed)
>07          待定故障码 (Pending)
```

**两者都要读**。只读 Mode 03 会漏掉间歇性故障。

### 读冻结帧

```text
>0200        Mode 02 支持位图 (注意是 02 不是 01)
>0204        冻结帧里的冷却液温度
```

**必须在清码之前读**。

### 读就绪状态

```text
>05          就绪位图 (4 字节)
>06          各监测项结果
>08 05       指定监测项
```

### 读车辆信息

```text
>0902        VIN
>0904        标定 ID
```

VIN 是 17 字节，**一定走多帧**。如果只收到一部分，检查 ISO-TP 和寻址方式。

### 清码

```text
>04          清除故障码 / 冻结帧 / MIL / readiness
```

清码前后的标准动作：

```text
1. 读 03 / 07 记录故障码
2. 读 02xx 记录冻结帧
3. 读 05 记录 readiness 初始状态
4. 执行 04
5. 再读 03 确认已清
6. 读 05 确认 readiness 被重置
7. 跑一个完整驾驶循环
8. 再读 05 确认全部就绪
```

**清码不等于修好**。故障条件还在，码会立刻回来。

## 常见读数异常定位

| 现象 | 优先检查 |
| --- | --- |
| 转速读数是实际值 2 倍 | PID 0C 编码是 rpm×4/2，解码公式 |
| 温度值偏高 40 度 | 温度 = A - 40 忘了减 |
| 车速恒为 0 | 车速多由 ABS 提供 (0x7EA)，检查是不是读了 ECM 的空 PID |
| 电压读数不对 | PID 0x42 编码，电压 = value/1000 |
| 同一 PID 两次读数不同 | ECU 侧滤波缺失（法规检测项） |
| 支持位图说支持但读不到 | 响应来自别的 ECU，检查响应 ID |
| 扩展 PID (0x41+) 读不到 | 可能需要 29 位扩展帧寻址 |
| VIN 只有 17 字节但收不全 | ISO-TP 多帧 / 寻址方式 |

## 产线与售后场景

### 产线下线检测

```text
1. 确认 VIN 正确 (Mode 09 02)
2. 确认无排放故障码 (Mode 03 空)
3. 确认无待定码 (Mode 07 空)
4. 确认 readiness 符合该车型要求
5. 确认关键 PID 读数在合理范围
6. 确认模块电压正常 (PID 0x42, 典型 12.0-14.5V)
```

### 售后故障复现

```text
1. 读全部故障码 (03 + 07 + UDS 19)
2. 记录全部快照和扩展数据
3. 读 Mode 06 定位是哪个监测项失败
4. 读关键 PID 观察动态数据
5. 对比冻结帧和当前值的差异
```

### 间歇性故障捕捉

```text
- 持续高频轮询关键 PID
- 记录每次读数和时间戳
- 故障出现时立即抓冻结帧
- 用 Pending 码 (Mode 07) 判断是否是间歇性
```

## 工具建议

- **PCAN-USB** 或 **CANable**：性价比高，需要自己写解析。
- **OBDLink MX+**：商业级 OBD 适配器，协议覆盖全，比 ELM327 靠谱。
- **USB-CAN + Python**：做自动化测试和批量下线时最灵活。
- **示波器**：查物理层问题时（终端电阻、信号完整性）。

调试时建议保存：

- 原始抓包文件（`.log` / `.blf`）。
- ECU 型号和软件版本（Mode 09 07 / 09 08）。
- 支持位图（Mode 01 的 00/20/40/60）。
- 故障码 + 冻结帧 + readiness。

## 检查清单

- 适配器确认支持 CAN（`ATDP` 不是 AUTO / J1850）。
- `ATE0` 已关闭回显。
- 抓包确认请求帧真的发出去了。
- 响应 ID 区分清楚（0x7E8/7E9/7EA/7EB）。
- 支持位图已读，PID 范围确认。
- 解码公式逐个核对（温度 -40、转速 ×2/4、百分比 ×100/255）。
- Mode 01 和 Mode 02 的支持集分别读。
- Mode 03 和 Mode 07 都读了。
- Mode 05 和 Mode 06 配合读。
- 冻结帧在清码之前读。
- 清码后确认 readiness 被重置。
- 记录 ECU 型号和版本。

## 延伸阅读

- `bus/obd2.md` — OBD-II 概览
- `bus/obd2-deep-dive.md` — PID 空间、监测模型、Mode 详解
- `bus/obd2-failure-cases.md` — 故障案例
- `bus/uds-practical.md` — UDS 实战（对照）
- `bus/iso-tp-practical.md` — ISO-TP 实战
- `basic/can-practical.md` — CAN 调试基础
- `bus/can-protocol-family.md` — CAN 家族全景
