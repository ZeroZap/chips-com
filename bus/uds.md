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

## 延伸阅读

- `bus/can.md`
- `bus/j1939.md`
