# USB Deep Dive

## 目标

本文深入 USB 工程细节，重点覆盖标准请求、描述符层级、复合设备、CDC/HID/MSC、Endpoint 0、设备状态、Remote Wakeup、Type-C/PD 边界和枚举失败定位。

## USB 设备状态

USB Device 常见状态：

```text
Attached
Powered
Default
Addressed
Configured
Suspended
```

设备只有进入 Configured 后，非 EP0 的业务 Endpoint 才能正常工作。

## Endpoint 0

Endpoint 0 是默认控制端点。

负责：

- 读取描述符。
- 设置地址。
- 设置配置。
- 标准请求。
- 类请求。
- 厂商请求。

EP0 实现不稳定会导致所有 USB 类都不可靠。

## 标准请求

常见标准请求：

| 请求 | 含义 |
| --- | --- |
| GET_DESCRIPTOR | 读取描述符 |
| SET_ADDRESS | 设置设备地址 |
| SET_CONFIGURATION | 设置配置 |
| GET_CONFIGURATION | 获取配置 |
| GET_STATUS | 获取状态 |
| CLEAR_FEATURE | 清除特性 |
| SET_FEATURE | 设置特性 |

枚举抓包时重点看这些请求是否正确响应。

## 描述符层级

典型结构：

```text
Device Descriptor
Configuration Descriptor
  Interface Descriptor
    Endpoint Descriptor
    Class-specific Descriptor
```

复合设备会有多个 Interface。

Configuration 的总长度必须覆盖所有下级描述符。

## 复合设备

复合设备例如：

```text
CDC + HID
CDC + MSC
Audio + HID
```

要点：

- Interface 编号不能冲突。
- Endpoint 地址不能冲突。
- 类描述符要放在正确 Interface 下。
- Windows 可能需要 IAD 描述符识别 CDC 复合设备。

## CDC 深入注意

CDC ACM 常见接口：

```text
Communication Interface
Data Interface
Interrupt IN Endpoint
Bulk IN Endpoint
Bulk OUT Endpoint
```

常见问题：

- Host 未设置 DTR，设备不输出。
- Line Coding 请求未处理。
- Bulk 包长和缓冲区不匹配。
- 断开重连后状态未清理。

## HID 深入注意

HID 的核心是 Report Descriptor。

常见问题：

- Report 长度和 Endpoint 包长不匹配。
- Usage Page/Usage 写错。
- Input/Output/Feature 报告方向混乱。
- Host 轮询周期不符合预期。

## MSC 深入注意

MSC 常见协议栈：

```text
Bulk-Only Transport
SCSI 命令集
Block device
File system
```

常见风险：

- Host 缓存导致拔出前数据未写完。
- MCU 和 Host 同时改文件系统。
- 扇区读写没有对齐。
- 存储介质擦写寿命。

## Suspend 和 Remote Wakeup

USB Host 可让设备进入 suspend。

设备要注意：

- 降低功耗。
- 保持必要唤醒状态。
- Remote Wakeup 需要 Host 授权。
- resume 时恢复时钟和 Endpoint 状态。

## Type-C 和 PD 边界

Type-C 是连接器和角色检测体系。

USB PD 是电源协商协议。

普通 USB 2.0 Device 使用 Type-C 时也要正确处理 CC：

```text
Sink 侧 Rd 下拉
Source 侧 Rp 上拉
```

不要把 Type-C 当成只换了连接器。

## 枚举失败定位

| 阶段 | 可能问题 |
| --- | --- |
| 插入无反应 | VBUS、D+/D-、CC、上拉、时钟 |
| Default 失败 | Bus reset、EP0、时钟 |
| 读描述符失败 | 描述符长度、EP0 buffer |
| 设置地址失败 | USB 栈状态机 |
| 设置配置失败 | 配置总长度、Endpoint 冲突 |
| 类驱动失败 | 类描述符、VID/PID、驱动匹配 |

## 深度检查清单

- EP0 标准请求完整。
- 描述符长度和层级正确。
- Endpoint 地址唯一。
- 复合设备 IAD 处理正确。
- 类请求已实现。
- Suspend/Resume 状态正确。
- Type-C CC 角色正确。
- 枚举失败有抓包或系统日志。
