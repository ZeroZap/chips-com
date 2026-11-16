# USB DFU Deep Dive

## 目标

本文深入 USB DFU 设计，重点覆盖 bootloader 架构、镜像格式、Flash 布局、状态机、安全校验、回滚和量产升级。

## Bootloader 架构

推荐将 bootloader 与 application 分离：

```text
Bootloader：负责升级、校验、启动应用
Application：业务固件
Metadata：版本、大小、校验、状态
```

Bootloader 应尽量小、稳定、受写保护。

## 镜像格式

固件镜像建议包含：

- Magic。
- Header version。
- Hardware version。
- Firmware version。
- Image size。
- Load address。
- CRC/Hash。
- Signature，视安全需求。

不要只传裸 bin 而没有元数据。

## Flash 布局

常见布局：

```text
Bootloader
Application Slot A
Application Slot B，可选
Metadata
Config
```

A/B 双分区可支持回滚，但占用更多 Flash。

## 状态机

升级状态建议：

```text
IDLE
ERASING
DOWNLOADING
VERIFYING
READY_TO_BOOT
FAILED
ROLLBACK
```

每个状态都应可查询。

## 安全和可靠性

建议：

- Bootloader 写保护。
- 镜像完整性校验。
- 防回滚版本策略，视安全需求。
- 断电恢复。
- 应用启动确认。
- 升级失败自动回退 DFU。

## 量产升级

量产工具应记录：

- 设备序列号。
- 固件版本。
- 升级时间。
- 校验结果。
- 失败原因。

## 常见问题

| 问题 | 根因方向 |
| --- | --- |
| 设备升级后无响应 | vector/address/校验/复位流程 |
| 升级中断变砖 | bootloader 未保护，无回滚 |
| Host 工具不兼容 | DFU 描述符或状态机差异 |
| 偶发写失败 | Flash 擦写粒度、电源、超时 |

## 检查清单

- Bootloader 不可被普通升级覆盖。
- 镜像头完整。
- Flash 擦写粒度正确。
- DFU 状态机可查询。
- 失败可恢复。
- 量产日志可追溯。
