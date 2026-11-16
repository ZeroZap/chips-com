---
tags:
  - layer/bus
  - type/failure-cases
  - protocol/wwh-obd
  - topic/automotive
---

# WWH-OBD 商用车诊断故障案例库

## 目标

把 WWH-OBD（ISO 27145）商用车诊断相关的现场问题写成案例库。每个案例：

- 现象（现场）
- 抓包分析（判断）
- 定位（根因）
- 修复（代码 / 配置）
- 复盘（如何预防）

WWH-OBD 场景的特殊性：**商用车 ECU 多、网关路由、DoCAN/DoIP 双链路、3 字节 DTC**。乘用车 OBD-II 的经验在这里经常不适用。

## 案例 1: 诊断仪插上完全连不上，只支持 CAN 的设备连不了新车

### 现象

一批商用车（2023 年后车型，带以太网诊断口）用原有的 CAN 诊断仪完全读不到任何东西。换到另一台带以太网接口的设备，一插就通。

### 抓包分析

CAN 侧：

```text
(总线上有正常流量, 其他节点在通信)
(诊断仪的请求帧发不出去 / 发了没回应)
```

以太网侧：

```text
UDP 13400 -> 收到 Vehicle announcement (类型 0x0004)
TCP 13400 -> 路由激活成功 (响应码 0x10)
```

### 定位

**不是故障，是链路架构变了**。

新一代商用车（重卡、客车）大量改用 **DoIP**（ISO 13400）承载诊断，不再走纯 CAN 诊断。

```text
老架构:  诊断口 (OBD-II 16 针) -> CAN -> 网关 -> J1939
新架构:  诊断口 (含以太网)   -> 以太网 DoIP -> 网关 -> J1939
```

ISO 27145-4 从设计之初就要求测试设备支持**两条链路**，并做 **plug and play** 的链路识别。

### 修复

**采购层面**：换**双链路**诊断设备（CAN + 以太网）。

**工具层面**：实现 ISO 27145-4 的初始化流程，先探 UDP 13400 再探 CAN。

```python
def detect_link(iface):
    """plug and play 链路识别"""
    # 1. 先探 DoIP
    if doip_vehicle_identification(iface, timeout=2.0):
        return 'DoIP'
    # 2. 再探 DoCAN (11 位优先)
    if verify_11bit(iface):
        return 'DoCAN-11bit'
    if verify_29bit(iface):
        return 'DoCAN-29bit'
    return None
```

### 复盘

- **车队/检测站采购必须明确要求双链路**，否则新车批量上线后设备全部报废。
- 工具实现要把「链路识别」作为**第一等能力**，而不是硬编码某种链路。
- 不要把「连不上」直接当设备坏了——先分诊是链路、寻址、还是协议层。

## 案例 2: 只试 11 位寻址，长寻址车型全部连不上

### 现象

同款重卡，一部分车能连，一部分车连不上。抓包发现连不上的那批车总线上有流量，但工具的请求帧发出去就是没响应。

### 抓包分析

```text
(工具发请求: 11 位 CAN ID, 0x7DF)
(无响应)

(改用 29 位 CAN ID: 0x18DAF110)
响应: 04 50 03 00 20 01 F4 ...
```

### 定位

ISO 27145-4 §7.1 把初始化拆成**两个独立的验证程序**：

```text
7.1.2  11 bit CAN identifier verification procedure
7.1.3  29 bit CAN identifier verification procedure
```

**两个都要跑**。工具只实现了 11 位，长寻址车型就全灭。

根因通常是工具框架默认短寻址，没有暴露寻址模式配置。

### 修复

```python
def initialize_can(sock):
    """ISO 27145-4 初始化: 11 位和 29 位都验证"""
    result = {'11bit': False, '29bit': False}

    can_id, ok = verify_11bit(sock)
    if ok:
        result['11bit'] = True
        result['addr11'] = can_id

    can_id, ok = verify_29bit(sock)
    if ok:
        result['29bit'] = True
        result['addr29'] = can_id

    if not (result['11bit'] or result['29bit']):
        raise LinkNotEstablished('11/29 位寻址均失败')

    # 优先短寻址, 长寻址作为回退
    result['mode'] = '11bit' if result['11bit'] else '29bit'
    return result
```

**注意**：SocketCAN 发 29 位帧必须带 `CAN_EFF_FLAG`：

```python
CAN_EFF_FLAG = 0x80000000
sock.send(0x18DAF110 | CAN_EFF_FLAG, req)
```

### 复盘

- **11 位 / 29 位必须都验证**，这是标准规定步骤，不是可选优化。
- 工具要**暴露寻址模式**，不要硬编码。
- 长寻址的报文要记得 `CAN_EFF_FLAG`，漏了会发出一个 29 位 ID 数值但按标准帧发出——症状是「地址不对」而非「没发出去」，更难查。

## 案例 3: DTC 读出来是乱码，SPN 解出天文数字

### 现象

同一台车，两台诊断仪读同一个故障码：一台显示 `P0234`（OBD-II 风格），另一台显示 `SPN 3251 FMI 4`。研发怀疑其中一个工具错了。

### 抓包分析

```text
请求: 19 01 FF FF FF
响应: 59 01 04 01 23 45 67 12 34 56
              │  └──┬─┘
              │     └── DTC 1: 3 字节 = 01 23 45
              └──────── DTC 数量 = 4
```

### 定位

**两个工具都没错**——它们用的 DTC 格式不同。

```text
OBD-II:        2 字节 DTC (P/C/B/U + 3 位数字)
WWH-OBD:       3 字节 DTC (24 bit)
                 ├─ BaseDTC (16 bit)  ← SAE J2012-DA
                 └─ FTB (8 bit)
                 等价于 J1939 的 SPN(19) + FMI(5)
```

ISO 27145-2 定义 3 字节 DTC 格式的目的，就是**向后兼容 SAE J2012-DA 和 J1939 SPN/FMI 两套既有体系**。

那台按 OBD-II 解析的工具，**把 3 字节的码按 2 字节读了**，把 FTB 当成了下一个 DTC 的字节 —— 所以显示成乱码。

### 修复

工具侧必须**先协商 DTC 格式，再解析**：

```python
def read_dtc(sock, dtc_format=0x01):
    """按指定 DTCFormatIdentifier 读故障码"""
    req = bytes([0x19, dtc_format, 0xFF, 0xFF, 0xFF])
    sock.send(req)
    resp = recv(sock)
    if resp[0] == 0x59:
        count = resp[2]
        dtcs = []
        off = 3
        for _ in range(count):
            dtcs.append(parse_wwh_dtc(resp[off:off + 3]))
            off += 3
            # 快照长度随格式变化, 不能硬编码
            off += snapshot_len(dtc_format, resp, off)
        return dtcs
    return []
```

**同时**，工具要**显示格式标识**，让使用者知道这个码是按什么解释的。

### 复盘

- **WWH-OBD 的 DTC 是 3 字节**，拿乘用车的解析器一定会错。
- DTC 解析前**先确定格式标识**——同一套 UDS 服务能按不同格式读出不同编码。
- 快照（DTCExtendedDataRecord）长度**随格式变化**，硬编码长度会在某些车型上错位。
- 「两台工具显示不一致」时，先确认**格式标识**是否一致，再判断谁错。

## 案例 4: DoIP 路由激活返回 0x03

### 现象

DoIP 设备能建 TCP 连接，发路由激活请求，收到的响应码是 0x03。换一台同型号车，正常。

### 抓包分析

```text
请求: 02 FD 00 05 00 00 00 07 0E 00 00 00 00 00 00
      │  │  │     │     └──┬─┘
      │  │  │     │        └─ activation type = 0x00 (standard)
      │  │  │     └────────── 源地址 0x0E00
      │  │  └──────────────── payload type 0x0005
      │  └─────────────────── 反向版本
      └────────────────────── 版本 0x02

响应: 02 FD 00 06 00 00 00 07 00 00 03 ...
                        │  └──┬─┘
                        │     └── 响应码 0x03
                        └──────── 逻辑地址 0x0000
```

### 定位

**DoIP 路由激活响应码 0x03 = 该 activation type 未被车辆使能**。

| 响应码 | 含义 |
| --- | --- |
| 0x00 | 一般错误 |
| 0x01 | 激活类型不支持 |
| 0x02 | 已激活（重复激活） |
| 0x03 | **诊断会话不支持** |
| 0x04 | 需要鉴权 |

工具用了 `activation type = 0x00`（标准激活），但这辆车要求 **OEM 特定 activation type**（常见 0xE0 或厂商自定义值）。

这通常**不是车坏了**，而是这批车需要额外的 OEM 诊断授权流程——很多商用车（尤其后处理 SCR / 尿素系统相关）的法规诊断有额外门槛。

### 修复

**工具侧**：让 activation type 可配置，不要写死。

```python
ACTIVATION_TYPES = [0x00, 0xE0]   # 按品牌配置

def try_routing_activation(sock, addr=0x0E00):
    for act in ACTIVATION_TYPES:
        s = open_doip_tcp()
        code = do_routing_activation(s, addr, act)
        if code == 0x10:
            return s, act
        s.close()
    raise RoutingActivationFailed()
```

**流程侧**：如果需要 OEM activation，说明该车的诊断**有授权要求**，工具侧要有对应的凭据处理（种子密钥 / 令牌），不是重试能解决的。

### 复盘

- **路由激活 0x03 是 DoIP 最常见的失败点**，别往网络层乱查。
- activation type **必须做成配置项**。
- 路由激活成功 ≠ 认证通过。DoIP 默认**没有**认证和加密，除非启用 OEM 激活检查或 TLS。

## 案例 5: DoIP 连上了，读 VIN 却拿不到

### 现象

路由激活成功（响应码 0x10），发 0x22 F1 90 读 VIN，ECU 回了，但 payload 是空的。

### 抓包分析

```text
请求: 02 FD 80 01 00 00 00 07 10 01 22 F1 90
                        │  └──┬─┘
                        │     └─ UDS: 22 F1 90 (ReadDataByIdentifier, DID 0xF190)
                        └────── 目标逻辑地址 0x1001

响应: 02 FD 80 01 00 00 00 07 10 01 7F 22 31
                        │  └──┬─┘ └──┬──┘
                        │     │     └─ NRC 0x31 = requestOutOfRange
                        │     └─────── 否定响应 0x7F
                        └───────────── 逻辑地址 0x1001
```

### 定位

**NRC 0x31 = requestOutOfRange**。ECU 收到了请求，但**这个 DID 在该 ECU 上不存在或超出范围**。

关键：**DoIP 用逻辑地址寻址 ECU**（0x1001），不是 CAN ID。逻辑地址 → 具体 ECU 的映射表由 OEM 提供，工具**加载错了地址**就会把请求发给一个不该收这个 DID 的 ECU。

```text
典型逻辑地址:
  0x1001  发动机 EMS / ECM
  0x1002  变速箱 TCM
  0x1101  网关
  0x1201  ABS/ESC
  ...
```

VIN 在很多车型上由**网关或中央 ECU** 提供，不在发动机 ECU 上。

### 修复

加载正确的 OEM 路由配置（CID 文件 / ODX / 配置文件），并**先做 ECU 枚举**：

```python
def find_vin_provider(sock, logical_addrs):
    """遍历候选逻辑地址, 找到能读 F190 的 ECU"""
    for addr in logical_addrs:
        try:
            resp = send_uds(sock, addr, bytes([0x22, 0xF1, 0x90]))
        except (TimeoutError, ConnectionError):
            continue
        if resp and len(resp) > 3 and resp[0] == 0x62:
            return addr, resp[3:20].decode('ascii', errors='replace')
    return None, None
```

> **不要硬编码「VIN 一定在 0x1001」** —— 这是 OEM 相关的事实，工具必须走配置。

### 复盘

- DoIP 的**逻辑地址 ≠ CAN ID**，且是 OEM 相关配置，不是标准常量。
- 读不到某个 DID 时，先确认**发给谁**了，再确认**要什么**。
- 工具应内置「按 DID 找 ECU」的能力，而不是把地址写死。

## 案例 6: 工具把 PID 当 DID 发，读不到任何数据

### 现象

同一个工具在乘用车上能读转速，换到商用车读不到。但商用车用别的工具能正常读。

### 抓包分析

```text
请求: 03 22 0C 00 00 00 00 00
        │  └──┬─┘
        │     └── DID 0x0C?? -> 工具把 OBD-II 的 PID 0x0C 当成了 DID
        └──────── ReadDataByIdentifier

响应: 03 7F 22 31 00 00 00 00
           │  └──┬─┘
           │     └── NRC 0x31 requestOutOfRange
```

### 定位

工具在**复用乘用车 OBD-II 的 PID 表**，直接把它当 DID 发出去。

但 WWH-OBD 的数据模型是：

```text
PID 0x0C (发动机转速)  ──映射──→  DID 0xF190 之类的另一个编号
```

ISO 27145-2 的核心工作就是这个映射表（Annex A），以及强制 DID 清单（Annex B）。

**PID 空间和 DID 空间是独立的**，正如 OBD-II 的 PID 不能当 UDS 的 DID 用。

### 修复

工具侧维护 **PID/MID/ITID → DID/RID 映射表**，用 ODX / CDD / 配置文件加载：

```python
# 概念示意
PID_TO_DID = {
    0x0C: 0xF190,   # 发动机转速
    0x0D: 0xF18D,   # 车速
    0x04: 0xF195,   # 冷却液温度
}

def read_param(sock, addr, pid):
    did = PID_TO_DID.get(pid)
    if did is None:
        raise MappingError(f'PID 0x{pid:02X} 无 DID 映射')
    did_bytes = did.to_bytes(2, 'big')
    return send_uds(sock, addr, bytes([0x22]) + did_bytes)
```

### 复盘

- **PID 和 DID 是两套编号空间**，跨协议复用工具参数是典型的隐性 bug。
- 映射表必须**外置可更新**（ODX / CDD），不能写死在代码里。
- 映射缺失时应**明确报错**，而不是发出去等 NRC 0x31。

## 案例 7: 偶发超时，重试就好，但总也读不全

### 现象

读一组动态数据（约 20 个 DID），每次总有 2-3 个超时。手动重试那几项就读出来了。慢速加载的 ECU 尤其明显。

### 抓包分析

```text
请求: 03 22 F1 90 00 00 00 00
(1000 ms 后)
响应: 03 7F 22 78 00 00 00 00
           │  └──┬─┘
           │     └── NRC 0x78 = responsePending
```

但工具**在收到 0x78 之前就已经超时放弃了**。

### 定位

**客户端超时没有给 P2\* 留余量**。

```text
P2      ≈ 50 ms      Server 首次响应的默认上限
P2*     ≈ 5000 ms    需要 NRC 0x78 延长时的上限
P2_CAN_Client_Max    客户端最大等待 (ISO 15765-4:2021 的参数名)
```

商用车 ECU（尤其是后处理 SCR、变速箱）负载重，处理一个请求可能要几百 ms，**必须先回 NRC 0x78 表示「还在处理」**。

工具超时设成 100 ms → 收到 0x78 前就断了 → 表现为「偶发超时」。

> 这在乘用车上少见（ECU 轻），在商用车上很常见。

### 修复

```python
P2_DEFAULT   = 0.050   # 50 ms
P2_EXTENDED  = 5.000   # 5 s

def request_with_pending(sock, can_id, req, p2=P2_DEFAULT, p2_star=P2_EXTENDED):
    deadline = time.time() + p2_star
    sock.send(can_id, req)

    while True:
        remaining = deadline - time.time()
        if remaining <= 0:
            raise TimeoutError('超出 P2* 窗口')
        sock.settimeout(remaining)

        resp_id, data = sock.recv_from(16)
        # 否定响应且 NRC = 0x78 (responsePending)
        if len(data) >= 3 and data[1] == 0x7F and data[2] == 0x78:
            continue        # 继续等, 不放弃
        return resp_id, data
```

### 复盘

- **NRC 0x78 是「请继续等」，不是错误**。工具必须显式处理它。
- 客户端超时**至少覆盖 P2\***，否则重负载 ECU 永远读不到。
- 「偶发超时、重试就好」的现象要警惕——它可能不是网络抖动，而是时序配置不足。

## 案例 8: 网关后面能读到诊断信息，但读不到发动机转速

### 现象

诊断口接上能连上网关，也能读到网关自己的 DID，但读发动机转速（EMS 提供的参数）没数据。J1939 侧同一时间 EMS 是活的。

### 抓包分析

```text
(诊断口 CAN 总线上有流量)
(诊断仪发的请求帧)
(网关回了路由应答, 但没有 EMS 的数据)
```

### 定位

**商用车诊断网络是双层的**：

```text
诊断口 -> 网关 (CGW) -> J1939 网络 -> EMS / TCM / ABS
```

J1939 网络上的 ECU **不在诊断口的 CAN 总线上**，物理上隔离。必须由**网关做路由转发**。

网关要转发，需要知道：

```text
1. 目标 ECU 的物理寻址 ID (OEM 相关)
2. 请求的路由规则 (OEM 路由表)
3. 目标 ECU 支持该服务
```

工具没加载路由配置 → 网关收到请求但不知道往哪转 → 不回数据。

### 修复

加载 OEM 路由配置（CID / ODX），并**用网关的诊断服务确认路由表**：

```text
常见做法:
1. 读网关的「路由激活」类 DID / RID
2. 按 OEM 规范激活目标 ECU 的路由
3. 或在配置里预置「DID -> 目标 ECU」映射
```

```python
DID_TO_TARGET = {
    0xF190: 0x01,   # VIN -> 网关自己
    0xF195: 0x02,   # 发动机参数 -> EMS (需路由)
    0xF186: 0x04,   # 变速箱参数 -> TCM (需路由)
}

def read_did(sock, did):
    target = DID_TO_TARGET[did]
    if target != 0x00:
        activate_route(sock, target)   # 按 OEM 规范激活路由
    return send_uds(sock, 0x1001, bytes([0x22]) + did.to_bytes(2, 'big'))
```

### 复盘

- 商用车「读不到 ECU 数据」**先判断是不是物理隔离**，不是工具能力问题。
- OEM 路由配置是商用车诊断工具的**必备资产**，没有就做不了跨网段访问。
- 这条坑在乘用车不存在——乘用车 ECU 基本都在同一条 CAN 上。

## 案例 9: 清码后 DTC 立刻回来，readiness 永远不全 1

### 现象

执行 0x14（ClearDiagnosticInformation）清码成功，但开一段路故障码就回来了，监测器状态（readiness）怎么跑都跑不全。

### 抓包分析

```text
请求: 04 14 FF FF FF
响应: 04 54 00 00 00 00 00 00
           │  └──┬─┘
           │     └── 清除结果掩码: 哪些 DTC 类型真的被清了
(几分钟后)
请求: 03 19 01 FF FF FF
响应: 03 59 01 04 01 23 45 ...
              └── 故障码又回来了
```

### 定位

三个叠加原因。

**A. 清除掩码（clear mask）不对**

0x14 的请求里带**清除掩码**，只清掩码覆盖到的 DTC 组。清错了组，码当然还在。

**B. 故障条件持续存在**

清码只清状态，不清原因。后处理 SCR 相关故障（NOx 传感器、催化器、DPF 再生）在故障没修之前必然复现。

**C. readiness 被重置且跑不完**

商用车监测器需要**特定工况组合**才能置位：

```text
SCR 再生监测:  需要特定的排温和行驶里程
DPF 监测:      需要特定的再生周期
NOx 传感器:    需要特定的负载窗口
EGR/DPF:       需要特定的车速区间
```

只跑市区短途**永远跑不完**。

### 修复

**清码前完整留证**：

```text
1. 读全部 DTC (含 pending / permanent)
2. 读快照 (DTCExtendedDataRecord)
3. 读 readiness / 监测器状态
4. 读关键动态数据
5. 执行 0x14 (确认清除掩码正确)
6. 读回验证
```

**按 OEM 驾驶循环跑监测器**：每个 OEM 有标准驾驶循环（包含特定的加速、巡航、减速、静止再生段），必须按标准跑，不能自己瞎开。

### 复盘

- **清码前必须留证**，否则 DTC + 快照 + readiness 一次性丢失。
- 清除掩码要按 OEM 定义，不能用通配。
- 商用车监测循环对工况要求比乘用车苛刻得多，要用**标准驾驶循环**而不是「跑够里程」。
- 「清码不等于修好」在商用车尤其致命——后处理系统故障码反复会让车辆直接进跛行模式。

## 案例 10: 同一故障码，两个工具显示完全不同，判定也矛盾

### 现象

车队反馈同一台车，工具 A 显示 `SPN 3251 FMI 4`（电压低），工具 B 显示 `P0087`（燃油轨压力低）。两个技师各修各的，都没修好。

### 抓包分析

两边抓到的**原始字节其实一样**：

```text
59 01 01 01 23 45
         └──┬─┘
            └── 3 字节 DTC = 01 23 45
```

### 定位

两个工具用了**不同的 DTC 格式标识**和**不同的显示字典**。

```text
工具 A: DTCFormatIdentifier = 0x02 (J1939 格式) -> SPN/FMI 视图
工具 B: DTCFormatIdentifier = 0x01 (SAE J2012-DA) -> BaseDTC/FTB 视图
```

ISO 27145-2 的 24 bit 格式**同时承载两套语义**，而 DTCFormatIdentifier 决定怎么解读。

更麻烦的是：**同一组字节在不同 DTC 格式下指向完全不同的故障**。这不是显示差异，是**语义差异**。

### 修复

**协议层**：请求时**显式指定 DTC 格式**，不要让 ECU 用默认格式：

```python
# 明确请求 J1939 格式 (sub-function 0x02)
req = bytes([0x19, 0x02, 0xFF, 0xFF, 0xFF])
```

**工具层**：
- 读码时把**格式标识一起显示**
- 导出报告时**同时给出原始 3 字节和两种解释**
- 车队台账按**原始字节**存，不按显示文本存

### 复盘

- **DTCFormatIdentifier 是跨工具一致性问题的根源**，必须显式管理。
- 车队台账要存**原始字节 + 格式标识**，不要存显示文本。
- 「两台工具显示不一样」时，**不要急着判断谁错**——先比格式标识，再比原始字节。

## 案例 11: 产线检测全过，交付后一周报后处理故障

### 现象

整车厂下线检测全部通过，客户提车一周后报后处理（SCR）故障，P0087 / P0088 之类。回溯产线记录：无故障码。

### 抓包分析

产线检测时的记录：

```text
点火 ON -> 初始化 -> 读 DTC (空) -> 读 readiness -> 判定通过
```

但产线检测时的车辆状态：

```text
- 发动机可能刚启动, 后处理系统温度还没上来
- NOx 传感器还在自热
- SCR 尿素泵可能还没开始工作
- 监测循环一个都没跑
```

### 定位

**检测时机不对**，测的是「还没开始工作」的后处理系统。

SCR / DPF 相关的故障码与故障监测需要：

```text
- 后处理温度达到阈值 (通常 200-300°C)
- 行驶达到一定里程 / 触发一定次数的再生
- 氮氧化物传感器达到工作温度
```

在**热机**状态或**刚启动**状态测，读到的空码没有意义。

反过来，**冷机**检测对监测器状态（readiness）才有意义——因为要验证监测循环**没有**被违规跳过。

**产线检测的真正目的**是查「装配缺陷导致的立即报码」，而不是查「运行一段时间后的老化故障」。

### 修复

产线检测 SOP 应明确：

```text
1. 车辆状态: 冷机 (记录环境温度 / 冷却液温度)
2. 记录 DTC (空) + readiness (未置位)
3. 记录关键动态数据
4. 验证强制 DID (Annex B) 全部可读
5. 记录 ECU 软件 / 标定版本
6. 交付前提醒: 首箱燃油需走完整监测循环, 否则可能报后处理故障
```

**关键动作**：交付时**给客户说明监测循环要求**。

```text
"首次添加尿素并行驶满 X 公里后, 若报后处理故障码, 属于监测器自检未完成,
 请完成一次完整高速巡航 (含再生) 后再读码。"
```

### 复盘

- **检测时机和检测目的是绑定的**，SOP 要写清楚「在什么状态下测、测什么」。
- 产线检测**不该**声称能验证后处理系统——那需要热机和完整驾驶循环。
- 交付说明里**主动告知监测循环要求**，能消掉大量「新车就有故障」的客诉。

## 案例 12: 商用车 OBD-II 诊断仪能连上，读到的却是 Mode 格式

### 现象

维修站拿一台乘用车 OBD-II 扫描仪去读一辆商用车。连上了，能读转速——但读到的故障码格式不对，和商用车专用工具显示的完全不同。

### 抓包分析

```text
请求: 02 41 0C 00 00 00 00 00    <- OBD-II Mode 01 PID 0C
响应: 03 41 0C 1A 00 00 00 00    <- 0x41 = 0x40 + Mode 01

(商用车工具)
请求: 03 22 F1 90 00 00 00 00   <- UDS ReadDataByIdentifier
响应: 03 62 F1 90 56 49 4E ...
```

### 定位

**这辆车同时支持 OBD-II（ISO 15031）和 WWH-OBD（ISO 27145）**。这正是 ISO 27145-4 初始化序列要解决的问题。

回想 ISO 27145-4 的判定逻辑——基于初始化结果，测试设备判定车辆的排放相关系统支持哪种协议：

```text
- legislated OBD:      ISO 15031 (all parts)
- legislated WWH-OBD:  ISO 27145 (all parts)
```

```text
响应首字节快速判别:
  0x40 | Mode  (0x41/0x43/0x44/0x45...)  -> OBD-II 风格
  0x40 | SID   (0x50/0x59/0x62/0x67...)  -> UDS 风格 (WWH-OBD)
```

**注意**：ISO 27145-3 本身「包含支持 SAE J1979-DA 和 SAE J2012-DA WWH-OBD 数据集的规定」——WWH-OBD 体系**能承载 OBD-II 的数据集**。所以在商用车读到 OBD-II 格式响应不一定是「工具错了」，也可能是**这辆车合法地同时提供两套**。

### 修复

**不要用乘用车扫描仪做商用车诊断**：

```text
乘用车 OBD-II 扫描仪:
  - Mode 01-09 只覆盖基础 PID
  - DTC 是 2 字节, 读不了 3 字节 WWH-OBD DTC
  - 读不了 Annex B 强制 DID
  - 读不了监测器详细结果 (Mode 06 语义)
  - 后处理 / 尿素系统完全覆盖不到
```

**正确做法**：用商用车专用工具（支持 UDS + WWH-OBD + J1939），并在初始化阶段**记录判定结果**：

```text
1. 初始化, 记录协议判定 (OBD-II / WWH-OBD / 两者)
2. 记录链路 (DoCAN-11bit / DoCAN-29bit / DoIP)
3. 用对应格式读码 (3 字节 + 格式标识)
4. 报告中记录判定结果
```

### 复盘

- 商用车**可能同时支持两套协议**，工具必须在初始化时判定并记录。
- **故障码字节数是协议归属的最快判据**：2 字节 OBD-II vs 3 字节 WWH-OBD。
- 维修站采购工具要明确「**支持 WWH-OBD（ISO 27145）+ J1939**」，只写「支持 OBD」会买到乘用车工具。
- 诊断报告里要写清**用了哪个协议、哪种 DTC 格式**——否则跨厂商比对必然扯皮。

## 附录：案例速查表

| # | 症状 | 根因 | 关键判据 |
| --- | --- | --- | --- |
| 1 | 只支持 CAN 的设备连不了新车 | 新车用 DoIP | UDP 13400 有车辆公告 |
| 2 | 部分车连不上 | 只试了 11 位寻址 | 29 位有响应 |
| 3 | DTC 显示乱码 | 2 字节解析器读 3 字节 DTC | 响应长度 / DTC 字节数 |
| 4 | DoIP 路由激活 0x03 | activation type 未使能 | 响应码 0x03 |
| 5 | DoIP 读不到 VIN | 逻辑地址错 / DID 不在该 ECU | NRC 0x31 |
| 6 | PID 读不到 | PID 当 DID 发了 | 请求字节是 0x0C 还是 0xF1xx |
| 7 | 偶发超时 | 超时未留 P2* 余量 | 收到过 NRC 0x78 |
| 8 | 读不到发动机数据 | 网关未路由到 J1939 域 | 网关应答但无 ECU 数据 |
| 9 | 清码后码立刻回来 | 掩码错 / 故障未修 / 监测循环 | 清除掩码 + readiness |
| 10 | 两工具显示不同 | DTCFormatIdentifier 不同 | 原始字节是否一致 |
| 11 | 产线全过交付后报故障 | 检测时机（热机/刚启动） | 温度 / 监测循环状态 |
| 12 | OBD-II 扫描仪读到 Mode 格式 | 車同时支持两套协议 | 响应首字节 0x41 vs 0x62 |
