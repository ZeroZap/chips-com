# BLE 候选素材 @ 2026-09-20 12:00

## 协议速览
- 是什么：低功耗蓝牙（BLE），2.4 GHz ISM 短距无线
- 解决什么：电池供电 IoT / 可穿戴（数月~数年）短距低带宽数据/控制
- 跟 L4 的关联：IoT/可穿戴第一连网；Matter/Thread 配网第一公里走 BLE

## 候选文章（4 条）

### 1. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：Dewine Labs
- 摘要：实测多家 BLE 模组在 Wi-Fi 同频干扰下的延迟/丢包——"实验室通过≠生产可靠"；硬件一般不是瓶颈，BLE 协议原生为可容忍延迟的消费场景设计，搬到工业/医疗/机器人等时延敏感场景立刻暴露。
- 关键实战点：真实多模块对比；失败模式是"延迟尖刺+间歇断连"；盲目换芯片/协议是错误路径
- 推荐动作：**深读 + 扩主题笔记「BLE lab-vs-field gap」**（高价值骨架）

### 2. Optimizing Bluetooth Receivers in Industrial IoT
- 链接：https://ebyteiot.com/it/blogs/ebyte-iot-blog/optimizing-bluetooth-receivers-in-industrial-iot-a-field-engineer-s-troubleshooting-and-hardened-hardware-guide
- 来源：EBYTE 工业 IoT
- 摘要：工业 BLE 接收机四大硬件根因（电源纹波/天线失配/2.4 GHz 共信道/温漂晶振），每步给量化门限。
- 关键实战点：VCC 纹波 < 50 mVpp、RSSI > -85 dBm；温漂晶振 ±40 ppm 在 -40~+85 °C 可致符号同步失败；示波器→频谱→抓包 三段隔离
- 推荐动作：扩 deep-dive「BLE 工业接收机硬件鲁棒性」

### 3. BLE connection stability — Nordic DevZone 多连接掉线
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/66424/ble-connection-stability/272163
- 来源：Nordic 官方 DevZone
- 摘要：9 外设/3 iOS 中心实测，掉线与人数/距离正相关；HCI 错误 0x08/0x3E/0x28 全归丢包/重传；最终 2 Mbps → 1 Mbps PHY + LFXTAL Cpin 重算修复。
- 关键实战点：HCI 错误码字典；2 Mbps PHY 长距多连缺陷；LFXTAL 公式 C = 2·Cl − Cpin − Cpcb
- 推荐动作：写实战「nRF52 多连掉线 → PHY/晶振双修」

### 4. STM32WBA65 Matter 设备 BLE 配网失败全链路排查
- 链接：https://blog.csdn.net/weixin_34194829/article/details/164166068
- 来源：CSDN 实战博客
- 摘要：Matter commissioning 必经 BLE；从"Alexa 扫不到"倒推广播/连接/App 三层根因，附 Python bleak 验证脚本。
- 关键实战点：Matter commissioning = BLE 必经；Service UUID 0xFFF6 识别锚；Android/iOS BLE 权限/隐私差异
- 推荐动作：入主题笔记「Matter 配网 = BLE commissioning」补全概念边界

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
