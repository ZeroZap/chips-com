# USB DFU Practical Guide

## 目标

本文用于 USB DFU 固件升级工程实践，重点覆盖进入 DFU、描述符、分块下载、Flash 写入、校验、回滚和防变砖。

## DFU 模式入口

常见进入方式：

- 按键上电。
- 应用命令跳转。
- USB Runtime 请求。
- 固件校验失败自动进入。
- 工厂测试模式。

入口设计要确保现场可恢复。

## 典型流程

```text
Host 枚举 Runtime 设备
请求进入 DFU
设备重枚举为 DFU 模式
Host 分块下载固件
设备写 Flash
Host 查询状态
下载完成后校验
设备重启到新固件
```

## 分区建议

推荐至少区分：

```text
Bootloader
Application
Metadata
Optional backup slot
```

Bootloader 不应被普通升级覆盖。

## 固件校验

建议包含：

- 长度。
- 版本。
- 硬件兼容信息。
- CRC 或 Hash。
- 签名，视安全需求。

升级完成后必须校验再启动。

## 防变砖策略

常见策略：

- Bootloader 区域写保护。
- 双分区 A/B。
- 断电续传或失败回滚。
- 固件头校验。
- 启动后应用确认标志。

## 常见故障

| 现象 | 优先检查 |
| --- | --- |
| 进不了 DFU | 入口条件、描述符、Runtime 请求 |
| 下载中断 | block size、USB 超时、Flash busy |
| 升级后不启动 | 向量表、地址、校验、硬件版本 |
| 变砖 | Bootloader 被覆盖、无回滚、校验缺失 |

## 检查清单

- DFU 入口可控。
- Bootloader 受保护。
- Flash 写入按页/扇区处理。
- 固件完整性校验。
- 升级失败可恢复。
- Host 工具和设备状态机兼容。
