# BLE 候选素材 @ 2026-08-06 00:00

## 协议速览
- 是什么：低功耗蓝牙（BLE），4.0 起，2026 主流 5.4（LE Audio / PAwR / Channel Sounding）。
- 解决什么：低速率、低占空比、μA 级休眠的近场无线，IoT/可穿戴/资产追踪主战场。
- 跟 L4 关联：用户主做 IoT/可穿戴；0x13/0x16/0x22 断连、MTU、GATT 错误码是一线必修。

## 候选文章（5 条）

### 1. 低功耗BLE调试总结之0x13,0x16,0x22问题
- 链接：https://blog.csdn.net/zhuyonghou/article/details/119084343
- 来源：CSDN 实战博客
- 摘要：产品多次触发功能后断连，抓日志定位三类断连码；解释 LL 40s 超时、conn_param_update 频繁致从机无响应、鉴权失败主动断开根因。
- 实战点：0x13 手机未解消息断开；0x22 LL 握手 >40s；仅必要时接受 conn_param_update
- 推荐：扩 deep-dive（错误码 → ATT/LL 时序图）

### 2. 乐鑫 ESP-BLE-UART 方案（H4 / H21 SoC）
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_4446a48527052852
- 来源：企鹅号 / 乐鑫官宣
- 摘要：BLE 协议栈封装为 BLE UART 固件 + PC 工具链（Console/Daemon/Bridge），替代拆机接串口线，定位工厂调试 / 现场维护。H21 电池，H4 双核 HMI。
- 实战点：透明传输不绑协议；现场配参 + 无线日志采集
- 推荐：写实战案例（配网 / 现场维护对比）

### 3. BLE 产线测试方案盘点（LitePoint / NI / Agilent / R&S）
- 链接：http://www.eeskill.com/article/id/15786
- 来源：畅学电子网
- 摘要：四大仪表厂产线方案横评：LitePoint IQ2015 多协议并行、NI PXIe-5644R VST FPGA EVM -47dB、Agilent N4010A 选件 109、R&S CBT。覆盖 TX/RX 量产 + PER 4× + 并行 DUT。
- 实战点：单次插测多标准省 20%；并行测 100% 吞吐；BT 4.0 RF 是产线基线
- 推荐：入主题笔记（产线测试 / 验收章节）

### 4. FastBle Android BLE 框架 BleBluetooth 连接管理
- 链接：https://blog.csdn.net/gitblog_01178/article/details/153383020
- 来源：GitCode + CSDN 解读
- 摘要：开源 Android BLE 框架核心类：自动/手动连接 + 重试、Android M+ TRANSPORT_LE、LastState 状态机、MTU/RSSI、多设备 LruHashMap、destroy() 全释放防泄漏。
- 实战点：connect 重试 + TRANSPORT_LE；LruHashMap 限实例数；destroy 链 stop→refreshCache→closeGatt
- 推荐：跳具体项目再读，先收藏

### 5. CH9143 BLE/UART/USB 三通芯片无线串口调试
- 链接：https://blog.csdn.net/2301_80174350/article/details/146231222
- 来源：CSDN 实战博客
- 摘要：国产三通芯片 CH9143 替代物理串口，BLEDebug + COMTransmit 联动实现「蓝牙↔串口」双向透传。解台式机无串口、产线不便拆壳痛点。
- 实战点：国产芯片替代有线串口真实方案；BLEDebug + 串口工具联动；廉价 USB 适配器可能不支持 BLE
- 推荐：写实战案例（无串口场景无线替代）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
