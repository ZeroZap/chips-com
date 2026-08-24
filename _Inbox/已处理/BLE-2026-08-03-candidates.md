# BLE 候选素材 @ 2026-08-03 00:00

## 协议速览
- 是什么：蓝牙低功耗(Bluetooth Low Energy)，2.4GHz 短距低功耗通信
- 解决什么：电池供电 IoT 设备的小数据间歇传输（手环/智能锁/传感器）
- 跟 L4 主题的关联：IoT 主流无线协议，连接参数/配对/抓包是嵌入式必修课

## 候选文章（4 条）

### 1. BLE连接故障排查实战：错误码到诊断修复
- 链接：https://blog.csdn.net/weixin_30621959/article/details/98727516
- 来源：CSDN 实战博客
- 摘要：从 HCI 层 Disconnect Reason（0x3B/0x08/0x05）反推连接层故障；真实案例：智能手环 0x3B（iOS 默认 7.5ms 间隔 vs 固件 20ms+）、智能锁连接间隔不匹配。
- 实战点：①连接参数四元组协商 ②Wireshark 抓包对比 ③0x3B 到 gap_params_init() 根因定位
- 推荐动作：扩 deep-dive 入 BLE 连接参数笔记

### 2. BLE配对绑定协议分析和抓包（Just Works）
- 链接：https://blog.csdn.net/dozenyaoyida/article/details/161661240
- 来源：CSDN 抓包实战
- 摘要：Just Works 配对四步流程（特性交换→STK→LTK→密钥分发）+ 链路层 Session Key 生成（SessionKey = AES(LTK, SKD)），附 HCI log + 空口抓包双视角。
- 实战点：①Rfcreations blueSpy 空口抓包链 ②LL ENC REQ/RSP 时序 ③重连时 Rand/EDIV 非零机制
- 推荐动作：写实战案例入 BLE 安全笔记

### 3. nRF52840+BLE 索尼相机自动地理标记（完整项目）
- 链接：https://blog.csdn.net/weixin_30460489/article/details/96149294
- 来源：CSDN 嵌入式项目实战
- 摘要：完整 nRF52840+Adafruit Feather+GPS+BLE 项目；逆向索尼私有 BLE 协议（Service 8000DD00...，Char 0xDD11），状态机管扫描/连接/定位/发送，6h 徒步实测+故障速查表。
- 实战点：①MicroPython 不支持配对（Pico W 弃用）②Adafruit 默认 100mA 充电→30h 充满 ③BLE 重连指数退避 1→2→4→10s
- 推荐动作：扩 deep-dive 入 BLE 项目实战笔记

### 4. Windows 10/11 BLE 调试：BLEDebug 工具指南
- 链接：https://blog.csdn.net/hp777/article/details/153005678
- 来源：CSDN Windows 调试实战
- 摘要：BLEDebug 替代 nRF Connect 跑 Windows BLE 调试，配合 CH9143（BLE/UART/USB 三通）做串口-蓝牙透传；含环境准备（Win10 1803+）、扫描过滤、GATT 树查看、特征值读写。
- 实战点：①Win 蓝牙 API 稳定性版本边界 ②廉价适配器不持 BLE 甄别 ③SmartScreen 签名绕过
- 推荐动作：入主题笔记（Windows BLE 调试工具集）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
