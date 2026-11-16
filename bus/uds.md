# UDS

## 定位

UDS 是 Unified Diagnostic Services，统一诊断服务，常用于汽车 ECU 诊断、刷写和维护。

UDS 可运行在 CAN、CAN FD、DoIP 等传输之上。

## 常见用途

- 读取故障码。
- 清除故障码。
- 读取数据标识 DID。
- 安全访问。
- ECU 编程刷写。
- 例程控制。
- 诊断会话管理。

## 常见服务

| SID | 服务 |
| --- | --- |
| 0x10 | Diagnostic Session Control |
| 0x11 | ECU Reset |
| 0x22 | Read Data By Identifier |
| 0x27 | Security Access |
| 0x28 | Communication Control |
| 0x2E | Write Data By Identifier |
| 0x31 | Routine Control |
| 0x34 | Request Download |
| 0x36 | Transfer Data |
| 0x37 | Request Transfer Exit |
| 0x3E | Tester Present |

## ISO-TP

UDS over CAN 通常使用 ISO-TP 做多帧传输。

它解决经典 CAN 单帧数据少的问题。

## 工程注意

- 诊断会话状态机。
- 安全访问种子密钥。
- 多帧流控。
- 超时参数。
- 负响应 NRC。
- 刷写失败恢复。

## 相关规范

UDS 是**一个总纲 + 多个承载变体**的结构，这点常被忽略：

| 标准 | 作用 |
| --- | --- |
| **ISO 14229-1** | UDS 规范与要求的**总纲**。SID 集、NRC、DID、DTC、Routine、刷写流程 |
| ISO 14229-2 | 会话层服务（与传输层解耦） |
| ISO 14229-3 | UDS on CAN |
| ISO 14229-4 | UDS on FlexRay |
| ISO 14229-5 | UDS on IP（与 DoIP 配套） |
| ISO 14229-6 | UDS on K-Line（老平台） |
| ISO 14229-7 | UDS on LIN |
| ISO 15765-2 | DoCAN 传输协议（UDS over CAN 的承载层） |
| ISO 13400-2 / -3 / -4 | DoIP 传输层 / 数据链路层 / 连接器 |
| ISO 20794-3 | 以太网上的传输与网络层 |
| ISO 26262 | 功能安全（诊断覆盖率、ASIL 分级） |
| ISO/SAE 21434 | 网络安全（TARA、CAN 注入攻击防护） |
| ISO 24089 / UNECE R155 / R156 | 软件更新与网络安全合规 |

**前代标准**（新设计不建议再用，但老平台会遇到）：

```text
ISO 14230 (KWP2000)  ── ISO 14229 和 ISO 15765 的前身
SAE J1850 / J2178    ── GM / Ford 的 VPW / PWM
SAE J2818 (K-Line)   ── VAG 的 KW1281
SAE J2819 (TP2.0)    ── VAG 的传输协议，UDS 的前身
SAE J3054 (TP1.6)    ── VAG 的 CAN 11 bit 数据链路
```

数据字典（ODX / CDD / Excel）不属于 ISO 强制部分，由 OEM 自定义格式。

## 延伸阅读

- `bus/can.md`
- `bus/j1939.md`
- `bus/uds-deep-dive.md`
- `bus/uds-practical.md`
- `bus/uds-failure-cases.md`
- `bus/iso-tp.md`
- `bus/obd2.md` — OBD-II 与 UDS 的规范边界
- `bus/can-standards-map.md` — CAN 家族标准规范总表
