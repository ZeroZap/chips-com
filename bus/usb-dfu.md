# USB DFU

## 定位

DFU 是 Device Firmware Upgrade，用于通过 USB 对设备进行固件升级。

常见于：

- MCU bootloader。
- USB 设备固件升级。
- 工厂烧录。
- 现场维护。

## 核心概念

DFU 设备通常有：

- Runtime 模式。
- DFU 模式。
- DFU 描述符。
- 下载固件请求。
- 状态查询。
- 退出和重启。

## 典型流程

```text
Host 识别设备
进入 DFU 模式
分块下载固件
设备写入 Flash
Host 查询状态
下载完成
设备校验并重启
```

## 工程注意

- 固件完整性校验。
- 防止升级中断变砖。
- Bootloader 区域保护。
- 版本和硬件兼容检查。
- 必要时支持回滚。

## 常见错误

| 现象 | 优先检查 |
| --- | --- |
| 进不了 DFU | 描述符、触发条件、boot pin |
| 下载失败 | block size、Flash 写入、状态机 |
| 升级后不启动 | vector、校验、地址、硬件版本 |
| 设备变砖 | bootloader 保护、回滚策略 |

## 延伸阅读

- `bus/usb-practical.md`
- `bus/usb-deep-dive.md`
- `PRODUCTION_TEST.md`
