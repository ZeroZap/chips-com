# BLE / Bluetooth LE 候选素材 @ 2026-08-02 00:00

## 协议速览
- 是什么：蓝牙 4.0+ 引入的低功耗短距无线协议，Central/Peripheral/Broadcaster/Observer 四种角色
- 解决什么：IoT/可穿戴场景下纽扣电池续航数月到数年的间歇性小数据通信
- 跟 L4 主题的关联：XinLink（数据连接器）双模产品线主力承载；产线配网/OTA/产测都跑这条

## 候选文章（5 条）

### 1. BLE 连接故障排查实战：从错误码到诊断修复
- 链接：https://blog.csdn.net/weixin_30621959/article/details/98727516
- 来源：CSDN 实战帖
- 摘要：拆解 0x3B/0x08/0x05 三个高频 HCI 断连码；nRF Connect 抓包对比 iOS 默认 7.5ms 间隔请求 vs 国产智能锁固件最低 15ms 不兼容的真实产线故障
- 实战点：连接参数协商矩阵、MTU 23 字节默认陷阱、Android 机型兼容性
- 推荐动作：**扩 deep-dive**（连接参数 SOP 值得立主题笔记）

### 2. BLE 4.2 Controller 加密流程与实现（Cordio 源码级）
- 链接：https://www.cnblogs.com/ixbwer/p/19393586
- 来源：博客园 + Cordio 协议栈源码
- 摘要：完整 LL_ENC_REQ/RSP/START_ENC 三步握手时序；附 PalCryptoAesCcmEncrypt/Decrypt 真实代码，0x1A/0x06/0x3D 异常码处理路径
- 实战点：MIC 失败立即断连、加密暂停 LL_PAUSE_ENC_REQ 流程、Nonce 39-bit PacketCounter 重传不递增
- 推荐动作：**入主题笔记**（Bonding/LTK 持久化是 XinLink 量产必踩的坑）

### 3. Kali Linux 实战：BLE 配对漏洞与安全防御
- 链接：https://blog.csdn.net/weixin_30410119/article/details/98352988
- 来源：CSDN 安全攻防
- 摘要：演示 Just Works / Passkey Entry / Numeric Comparison / OOB 四种配对攻击面，TWS 耳机默认 Just Works 的 MitM + 重放攻击完整利用链
- 实战点：Ubertooth 抓包 + GATT 注入 + OTA 签名绕过
- 推荐动作：**写实战案例**（反面教材入安全笔记）

### 4. Winform BLE 蓝牙通信全流程解析
- 链接：https://blog.csdn.net/weixin_29213827/article/details/157415471
- 来源：CSDN .NET 平台实战
- 摘要：Windows.Devices.Bluetooth 下 DeviceWatcher 扫描，首次拿不到设备名称需等 Updated 事件；-70dBm 稳定/-80dBm 频繁断连的实测阈值
- 推荐动作：**跳过**（PC 端 SDK，对嵌入式/IoT 复用度低）

### 5. GitHub - zwack：BLE 传感器模拟室内自行车训练器
- 链接：https://github.com/perillo/zwack
- 来源：GitHub 开源项目（Node.js + bleno）
- 摘要：bleno 实现 CSP/RSC/FTMS 三种 Profile 广播，跨 macOS/Linux/RPi/Windows；"MacOS 蓝牙失败换 @abandonware/bleno" 的真实坑
- 推荐动作：**跳过**（运动特定 Profile，跟主方向距离略远）

## 下一步
等你 review。优先吃下 #1（连接参数）和 #2（加密流程）—— XinLink 量产最深的两个坑。
