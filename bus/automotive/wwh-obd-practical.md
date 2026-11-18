---
tags:
  - layer/bus
  - type/practical
  - protocol/wwh-obd
  - topic/automotive
---

# WWH-OBD Practical Guide

## 目标

本文面向用 WWH-OBD 做实测、排障和工具开发的人，覆盖：

- 测试设备选型（DoCAN / DoIP / 双链路）。
- ISO 27145-4 初始化序列的实际执行步骤。
- 11 位 / 29 位 CAN ID 验证程序怎么做。
- DoIP 抓包与路由激活实操。
- 24 位 DTC 的解析与 SPN/FMI 换算。
- 商用车特有的现场场景（冷启动、网关、多 ECU）。

## 最小前提

先确认物理层和供电：

- 车辆**点火 ON 或发动机已启动** —— 商用车很多 ECU 在钥匙 OFF 时不供电，诊断口有电但 ECU 不在线。
- 诊断口连接器就位，CAN 与以太网线序正确。
- 车辆总线负载正常（商用车气路/液压负载大，注意气泵、除霜）。
- 至少一台 CAN 分析仪 + 一台以太网抓包工具。

> **商用车与乘用车的关键差异**：商用车 ECU 数量多（10-30+）、冷启动慢、经常有总线休眠唤醒逻辑。**刚插上就发请求必然失败**，要走唤醒序列。

## 工具链

### 三类设备

| 类型 | 代表 | 用途 | 局限 |
| --- | --- | --- | --- |
| 通用诊断仪 | 商用车专用扫描仪、OBDLink MX+ | 快速读码、产线检测 | 车型覆盖有限，黑盒化 |
| CAN + 以太网分析仪 | PCAN-USB / VN5640 / CANoe | 全量抓包、协议分析 | 需要自己解析 |
| 台架设备 | 转鼓 + 排放测试台 | 法规认证、OBD 一致性验证 | 贵，场地要求高 |

> **选型关键**：现在的新一代商用车越来越多用 **DoIP**。只支持 CAN 的设备在新车上会**完全连不上**——这不是故障，是车型架构变了。

### 双链路设备的价值

ISO 27145-4 的核心诉求是 **plug and play**。一台理想测试设备应该：

```text
1. UDP 13400 发车辆识别请求 → 探测 DoIP
2. 若无应答 → 尝试 CAN 11 位验证程序
3. 若 11 位不通 → 尝试 CAN 29 位验证程序
4. 依据结果选定链路, 开始协议初始化
```

**只有 CAN 的设备**：能连老车，连不了新 DoIP 车。
**只有 DoIP 的设备**：能连新车，连不了纯 CAN 的老车和绝大多数未装以太网诊断口的商用车。

> 商用车队（fleet）两种都有——**采购双链路设备**。

## 初始化序列（ISO 27145-4）

### 标准流程

```text
1. 车辆上电 / 唤醒总线
2. 物理层确认:
   - CAN 波特率探测 (500 kbps / 250 kbps)
   - 或以太网链路确认
3. 链路选择:
   - DoIP: UDP 13400 车辆识别
   - DoCAN: 进入 11/29 位验证
4. 11 位 CAN ID 验证程序 (7.1.2)
5. 29 位 CAN ID 验证程序 (7.1.3)
6. 网络层初始化 (7.5)
7. 会话层: 诊断会话 (ISO 14229-2)
8. 应用层: ISO 27145-3 的 UDS 服务子集
```

### 11 位 / 29 位验证程序怎么做

标准把两者规定为**独立的验证程序**，实际工程做法：

**11 位（短寻址）验证**：

```text
1. 在候选 CAN ID 上发一个轻量请求
2. 观察是否有响应, 且响应内容符合 ISO 27145-3 格式
3. 记录该 ID 有效
```

**29 位（长寻址）验证**：

```text
1. 在 29 位 ID 空间 (0x18DAF1xx 段) 重复同样的探测
2. 响应必须来自对应的 29 位响应 ID
3. 记录该寻址方式有效
```

**判断结果**：

| 11 位 | 29 位 | 判定 |
| --- | --- | --- |
| ✓ | ✓ | 支持两种，按服务选择（通常短寻址优先） |
| ✓ | ✗ | 短寻址车型 |
| ✗ | ✓ | 长寻址车型，工具必须切到 29 位 |
| ✗ | ✗ | 寻址不匹配 / 链路错 / ECU 未唤醒 |

> **最容易踩的坑**：工具默认 11 位，长寻址车型就「连不上」。反过来工具强行用 29 位，短寻址车型也不通。**两种都要试，不能只试一种**。

### 探测脚本示例

```python
def verify_11bit(sock):
    """ISO 27145-4 7.1.2: 11 位 CAN ID 验证"""
    for can_id in (0x7DF, 0x7E0, 0x7E1):
        req = bytes([0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
        sock.send(can_id, req)
        try:
            resp_id, data = sock.recv_from(16)
            if data[1] in (0x50, 0x7F):   # 肯定或否定响应
                return can_id, True
        except socket.timeout:
            continue
    return None, False

def verify_29bit(sock):
    """ISO 27145-4 7.1.3: 29 位 CAN ID 验证"""
    CAN_EFF_FLAG = 0x80000000
    for can_id in (0x18DAF110, 0x18DA10F1):
        req = bytes([0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
        sock.send(can_id | CAN_EFF_FLAG, req)
        try:
            resp_id, data = sock.recv_from(16)
            if data[1] in (0x50, 0x7F):
                return can_id, True
        except socket.timeout:
            continue
    return None, False
```

## DoIP 实操

### 车辆识别（UDP 13400）

```bash
# 发送车辆识别请求 (DoIP 通用头 8 字节 + payload)
# 版本 02, 反向 FD, 类型 0x0001, 长度 0
printf '\x02\xfd\x00\x01\x00\x00\x00\x00' | nc -u -w1 192.168.0.10 13400
```

响应（类型 0x0004 Vehicle identification response）包含 VIN、GID、逻辑地址等。

**更简单的方式**：直接等**车辆公告**。车辆上电后会主动广播类型 0x0004 的 Vehicle announcement 到 UDP 13400。抓这个广播能直接拿到 VIN 和 DoIP 实体地址。

```python
import socket

def listen_vehicle_announcement(timeout=10):
    """监听车辆主动公告 (UDP 13400)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(timeout)
    s.bind(('', 13400))

    try:
        data, addr = s.recvfrom(4096)
        # 通用头: [0:2]=版本/反向 [2:4]=类型 [4:8]=长度
        ver, inv = data[0], data[1]
        ptype = (data[2] << 8) | data[3]
        plen = int.from_bytes(data[4:8], 'big')
        if ver ^ inv == 0xFF and ptype == 0x0004:
            return addr, data[8:8 + plen]
    except socket.timeout:
        return None, None
    finally:
        s.close()
    return None, None
```

### 路由激活

```python
def routing_activation(tester_addr=0x0E00, activation_type=0x00):
    """DoIP 路由激活 (payload type 0x0005)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.0.10', 13400))

    # 通用头: 版本 02, 反向 FD, 类型 0x0005, 长度 7
    # payload: 源地址(2) + activation type(1) + 4 字节保留
    payload = tester_addr.to_bytes(2, 'big') + bytes([activation_type]) + b'\x00' * 4
    header = b'\x02\xfd' + (0x0005).to_bytes(2, 'big') + len(payload).to_bytes(4, 'big')
    s.send(header + payload)

    resp = s.recv(4096)
    rtype = (resp[2] << 8) | resp[3]
    # 响应 payload: 逻辑地址(2) + 响应码(1) + 4 字节保留
    rc = resp[9] if len(resp) > 9 else None
    return s, rtype, rc
```

**路由激活响应码**：

| 响应码 | 含义 | 排查方向 |
| --- | --- | --- |
| 0x00 | 一般错误 | 看车辆状态 |
| 0x01 | 激活类型不支持 | 工具用了该车不支持的 activation type |
| 0x02 | 已激活（重复激活） | 无害 |
| 0x03 | **诊断会话不支持** | OEM activation type 未使能，工具侧要改 activation type |
| 0x04 | **需要鉴权** | 车辆要求 OEM 特定激活流程 |

> 响应码 0x03 是 DoIP 最常见的失败原因：**工具侧 activation type 与车辆要求不匹配**。先确认车辆要求的 activation type 再改工具。

### 发诊断消息

```python
def send_uds(sock, ecu_addr, uds_payload):
    """经 DoIP 发送 UDS 诊断消息 (payload type 0x8001)"""
    payload = ecu_addr.to_bytes(2, 'big') + uds_payload
    header = (b'\x02\xfd'
              + (0x8001).to_bytes(2, 'big')
              + len(payload).to_bytes(4, 'big'))
    sock.send(header + payload)
```

读 VIN（DID 0xF190）：

```python
s, _, rc = routing_activation()
if rc == 0x10:   # 路由激活成功
    send_uds(s, 0x1001, bytes([0x22, 0xF1, 0x90]))
    resp = s.recv(4096)
    # 解析: 去掉 DoIP 头, 取 UDS 响应
    uds = resp[8:]
    if uds[0] == 0x62:      # ReadDataByIdentifier 肯定响应
        vin = uds[3:3 + 17].decode('ascii')
        print(f"VIN: {vin}")
```

> **逻辑地址**：DoIP 用逻辑地址（0x1001 等）寻址 ECU，不像 CAN 用 CAN ID。这个映射表由 OEM 提供，工具需要加载。

### DoIP 抓包检查清单

```text
1. UDP 13400 有没有车辆识别响应 / 公告?
2. TCP 13400 能不能建连?
3. 路由激活请求发了没有?
4. 响应码是多少? (0x10 = 成功)
5. 诊断消息发出去, ECU 回不回?
6. 有没有 0x8003 负确认 (NACK)?
```

**NACK 常见码**：

| NACK | 含义 |
| --- | --- |
| 0x00 | 通用否定应答 |
| 0x01 | 消息长度不对 |
| 0x02 | 消息太大 |
| 0x03 | 未激活就发诊断消息 |
| 0x04 | 目标 ECU 地址无效 |

## DoCAN 实操

### 抓包

```bash
# 抓全部 CAN 帧
candump -t z can0

# 只看诊断相关 ID
candump -t z can0,7DF:7DF

# 抓 30 秒写文件
candump -t z -l 30000 can0 > wwh.log
```

### 抓包该看什么

```text
1. 总线上有没有流量? (唤醒成功没有)
2. 请求帧用 11 位还是 29 位?
3. 响应 ID 是否在预期范围?
4. 响应内容是 0x50/0x7F (UDS) 还是 0x41/0x43 (OBD-II)?
5. 有没有错误帧 (can_id & 0x40000000)?
6. 有没有 NRC 0x78 (response pending)?
```

**第 4 点是识别 WWH-OBD 还是 OBD-II 的最快方法**：响应首字节 `0x40|Mode`（0x41/0x43/0x44）是 OBD-II 风格；`0x40|SID`（0x50/0x59/0x62）是 UDS 风格。

### NRC 0x78 与超时设置

商用车重负载 ECU 经常需要更长时间：

```python
def request_with_retry(sock, can_id, req, timeout=6.0):
    """处理 NRC 0x78 response pending"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        sock.send(can_id, req)
        resp_id, data = sock.recv_from(16)
        # UDS 负响应: 7F <SID> <NRC>
        if len(data) >= 3 and data[1] == 0x7F and data[2] == 0x78:
            continue    # response pending, 继续等
        return resp_id, data
    return None, None
```

> **P2 vs P2\***：P2（首次响应）约 50 ms，P2\*（需要 NRC 0x78 延长）可达 5000 ms。**客户端超时必须留足余量**，否则重负载 ECU 会被误判超时。这在商用车上比乘用车常见得多。

## 24 位 DTC 解析

### 读 DTC

```text
请求: 19 01 FF FF FF    (ReadDTCInformation, sub-function 0x01)
响应: 59 01 04 01 23 45 67 12 34 56 ...
      │  │  │  └──┬─┘ └──┬──┘
      │  │  │     │       └── DTC 2 (3 byte)
      │  │  │     └────────── DTC 1 (3 byte)
      │  │  └──────────────── 0x59 = 0x40 + 0x19
      │  └─────────────────── sub-function 0x01
      └────────────────────── 0x19 ReadDTCInformation
```

### 格式：先协商，再解析

```python
def parse_wwh_dtc(three_bytes):
    """解析 24 bit WWH-OBD DTC → SPN / FMI"""
    b0, b1, b2 = three_bytes
    dtc = (b0 << 16) | (b1 << 8) | b2

    # BaseDTC = 高 16 bit
    base_dtc = (b0 << 8) | b1
    ftb = b2 & 0xFF

    # J1939 视图: SPN(19) + FMI(5)
    spn = (dtc & 0xFF) | ((dtc >> 13) << 8)
    fmi = (dtc >> 8) & 0x1F

    return {
        'raw': dtc,
        'base_dtc': base_dtc,
        'ftb': ftb,
        'spn': spn,
        'fmi': fmi,
    }

# 示例
d = parse_wwh_dtc(bytes([0x01, 0x23, 0x45]))
print(d['base_dtc'], d['ftb'], d['spn'], d['fmi'])
```

> ⚠️ **位域必须用标准 Figure 5 复核**。上面是「SPN/FMI 能无损装进 24 bit」这一结构的示意实现，实际 bit 布局以 ISO 27145-2 为准。

### 工具侧的关键纪律

```text
1. 读 DTC 前先确定 DTCFormatIdentifier
2. 不要用 2 字节 OBD-II 解析器读 WWH-OBD 的 DTC
3. 快照 (DTCExtendedDataRecord) 长度随格式变化, 不能硬编码
4. 同一 DTC 在不同工具里显示不同, 先确认两边用的同一格式
```

## 商用车特有场景

### 冷启动 vs 热机

```text
1. 钥匙 OFF 插诊断仪 -> 大多读不到
2. 钥匙 ON (不启动) -> 部分 ECU 唤醒
3. 启动发动机 -> 全部 ECU 在线, 但可能清掉部分 DTC 状态
4. 冷机数据 vs 热机数据含义不同
```

> **产线检测注意**：下线检测通常要求**冷机**状态（确保监测器未运行、readiness 未置位）。热机检测会读到已跑完的监测循环，反而**掩盖**问题。

### 网关与多 ECU

```text
商用车 ECU 数量可达 10-30+

典型布局:
  发动机 EMS (ECM)
  后处理 SCR / 尿素 (ACM)
  变速箱 TCM
  ABS/ESC
  车身控制器
  网关 (CGW)  <- 诊断与 J1939 的交汇点
```

**关键**：J1939 网络上的 ECU（EMS / TCM / ABS）通常**不能被 OBD 诊断口直接访问**，需要经过**网关路由**。

```text
诊断口 -> 网关 -> J1939 网络 -> EMS / TCM / ABS
```

这解释了为什么商用车诊断工具需要 OEM 路由配置——不是工具做得差，是物理拓扑决定的。

### 网关路由不生效

```text
症状: 读不到发动机转速, 但网关本身能应答

排查:
1. 抓包看请求帧去了哪个 CAN ID
2. 看网关有没有回路由帧
3. 确认路由表配置 (OEM 工具配置 / CID 文件)
4. 确认目标 ECU 的物理寻址 ID
```

## 常见读数异常定位

| 现象 | 优先检查 |
| --- | --- |
| 初始化就没任何响应 | 车辆唤醒、总线有流量、寻址模式（11/29 位） |
| DoIP 路由激活返回 0x03 | OEM activation type 不匹配 |
| DoIP 能连但读不到 ECU | 逻辑地址错、ECU 未实现该 UDS 服务 |
| DTC 读出来是乱码 | 按 2 字节解析了 3 字节 DTC，或 DTC 格式标识没协商 |
| SPN/FMI 解出来数值离谱 | bit 域映射错，用标准 Figure 5 复核 |
| PID 读不到但 DID 能读 | PID→DID 映射表缺失 |
| 偶发超时，重试就好 | ECU 负载高，需要 NRC 0x78 延长；客户端超时留足 P2* |
| 只有 DoCAN 能连，DoIP 不通 | 车型无以太网诊断口 / 网关未开 DoIP / UDP 13400 被拦 |
| 同一故障码两台工具显示不同 | 一套按 J1939 SPN/FMI，一套按 J2012-DA BaseDTC/FTB |

## 产线与检测站场景

### 下线检测

```text
1. 确认车辆冷机状态
2. 完成 ISO 27145-4 初始化, 记录链路类型 (DoCAN / DoIP)
3. 读 DTC (含 pending) -> 必须为空
4. 读 readiness / 监测器状态 -> 符合该车型要求
5. 读强制 DID (Annex B) -> 全部可读
6. 读关键动态数据 -> 在合理范围
7. 记录 ECU 型号、标定 ID、软件版本
```

### 年检 / 排放检测

```text
1. 初始化 + 链路确认
2. 读 DTC -> 记录全部（含 3 字节原始值）
3. 读 readiness 位图 -> 与车型要求比对
4. 读监测器结果 -> 定位未通过项
5. 导出报告: 需含 DTC 原值 + 格式标识
```

> **报告要求**：法规检测报告里的 DTC 必须带**格式标识**，否则跨地区比对会出错。

## 工具建议

- **双链路诊断仪**（CAN + 以太网）：商用车队刚需，避免新车连不上。
- **VN5640 / CANoe**：要抓 DoIP 就需要以太网接口，VN 系列同时支持 CAN/FD/以太网。
- **PCAN-USB + Python**：做自动化测试最灵活。
- **ODX / CDD 数据库**：做多品牌车队必须有，映射表靠它。

调试时建议保存：

- 原始抓包文件（`.blf` / `.log` / pcap）。
- 初始化过程记录（链路类型、寻址模式、验证结果）。
- DTC 原始字节 + 格式标识。
- Annex B 强制 DID 的读取结果。

## 检查清单

- 车辆已上电 / 已唤醒（冷机或热机状态明确记录）。
- 链路类型已确定（DoCAN 或 DoIP）。
- 11 位与 29 位验证程序都执行过。
- 会话已建立（诊断会话类型已记录）。
- DTCFormatIdentifier 已确定。
- DTC 按 3 字节解析，未混用 OBD-II 解析器。
- 快照长度按格式处理，未硬编码。
- PID→DID 映射表可用。
- 客户端超时留足 P2* 余量，NRC 0x78 已处理。
- Annex B 强制 DID 全部可读。
- 网关路由配置已加载（需要跨网段访问时）。
- 报告包含 DTC 原值与格式标识。

## 延伸阅读

- [[bus/automotive/wwh-obd|wwh-obd]] — WWH-OBD 专篇
- [[bus/automotive/wwh-obd-deep-dive|wwh-obd-deep-dive]] — 数据模型、24 位 DTC、初始化、DoIP 协议
- [[bus/automotive/wwh-obd-failure-cases|wwh-obd-failure-cases]] — 故障案例
- [[bus/automotive/obd2-practical|obd2-practical]] — 乘用车 OBD-II 实战（对照）
- [[bus/automotive/uds-practical|uds-practical]] — UDS 实战（WWH-OBD 的服务底座）
- [[bus/automotive/iso-tp-practical|iso-tp-practical]] — ISO-TP 实战（DoCAN 传输层）
- [[bus/automotive/j1939-index|j1939-index]] — J1939 导航（商用车网络地基）
- [[basic/can-practical|can-practical]] — CAN 调试基础
- [[bus/automotive/can-protocol-family|can-protocol-family]] — CAN 家族全景
