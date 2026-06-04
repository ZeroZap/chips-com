# USB

## 定位

USB 是通用串行总线，用于主机和外设之间的热插拔通信。

常见设备：

- 键盘鼠标。
- U 盘。
- 摄像头。
- 声卡。
- USB 转串口。
- MCU CDC/HID/MSC 设备。

## Host 和 Device

USB 是 Host 控制 Device 的体系。

Host 负责枚举、供电、调度传输和加载驱动。

Device 负责上报描述符并响应 Host 请求。

## 核心概念

- 枚举。
- 描述符。
- Endpoint。
- Control/Bulk/Interrupt/Isochronous。
- VID/PID。
- CDC/HID/MSC。

## 延伸阅读

- `bus/usb-practical.md`
