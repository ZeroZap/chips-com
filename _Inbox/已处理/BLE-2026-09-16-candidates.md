# BLE / Bluetooth LE 候选素材 @ 2026-09-16 00:00

## 协议速览
低功耗短距无线（2.4 GHz ISM），GATT 服务发现 + Notify；IoT/可穿戴首选，产线 SPC/定位信标/医疗贴片核心承载。

## 候选文章（4 条）

### 1. Why Bluetooth Fails in Manufacturing
- 链接：https://www.microridge.com/why-bluetooth-fails-in-manufacturing/
- 来源：MicroRidge（工业 SPC 厂）blog
- 摘要：IMTS 2024（9 万人制造展）现场某竞品蓝牙 SPC demo 彻底失效。论证 AFH 在 Wi-Fi/蓝牙噪声下被迫"差中选不那么差"循环跳频→丢包/掉链。
- 关键实战点：
  - AFH 在 clean channel 池压垮后强制循环 → retry / latency 飙升
  - 金属多径 + 跳频比"固定信道 + 评估"更脆弱（反直觉）
- 推荐动作：扩 deep-dive → 入 BLE/工业主题笔记

### 2. Why Is Your Bluetooth Remote Control Dropping Connections
- 链接：https://ebyteiot.com/blogs/ebyte-iot-blog/why-is-your-bluetooth-remote-control-dropping-connections-and-how-can-you-fix-it
- 来源：EByte 亿佰特（工业 BLE 模块厂）blog
- 摘要：90% 蓝牙掉线根因在硬件层——LDO 瞬态差致 RF SoC brownout、2.4 GHz 共信道阻塞、VSWR > 3.0、连接间隔过激。配 DSO/频谱仪排查表。
- 关键实战点：
  - TX burst VCC drop < 50 mV 硬指标；10 µF 以下 bulk cap 不够
  - Wi-Fi 占满 → clean channel 不足 → supervision timeout
- 推荐动作：写实战案例（断电-纹波-掉线因果）→ 入笔记

### 3. 蓝牙无法连接外设：工业场景排查方案
- 链接：https://gutab.cn/news_industrial/899.html
- 来源：合亿 Gutab（工业平板厂）news
- 摘要：工业 4.0 四维排查——天线 VSWR/IPEX、AFH 信道映射、电源去耦 + USB selective suspend、固件状态机 + HCI 队列溢出。每步含可量化阈值。
- 关键实战点：
  - Adv Interval vs Scan Window 时间窗口必须重叠，否则主机错过广播
  - 工业 OS 对 USB 蓝牙适配器自动 suspend 直接切断射频
- 推荐动作：扩 deep-dive → 工业场景 BLE 笔记主框架

### 4. 从信号完整性视角重构蓝牙连接逻辑
- 链接：https://tsight.io/articles/15176126?lang=zh
- 来源：tsight.io（中文 blog，基于 Ellisys 抓包）
- 摘要：用 Ellisys 拆 BLE 跳频序列与 Channel Map 重协商；指出产线高负载下"固件把数据优先级置于 LL ACK 之上"致物理层超时释放链路。给天线去耦/单点接地/屏蔽 10-20 个最差信道 3 条建议。
- 关键实战点：
  - LL_CONNECTION_UPDATE_IND 超时 + MIC Failure 是产线典型签名
  - Channel Map 更新 T_IFS 级延迟跟不上干扰即断链
- 推荐动作：扩 deep-dive → 入 BLE/PHY 信号完整性笔记

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃