# SENT / PSI5 候选素材 @ 2026-11-10 16:55

## 协议速览
- 是什么：SENT（SAE J2716）单线脉宽编码 + PSI5 双线电流调制，ECU 直连传感器低成本链路。
- 解决什么：把模拟/PWM 噪声与地偏置换成自时钟数字帧，只留 2-3 线。
- 关联：全库 0 篇 SENT/PSI5，本轮补协议底座/产线 EOL/实现选型。

## 候选文章（5 条）

### 1. SENT protocol decoding & diagnosis guide
- 链接：https://www.picoauto.com/library/product-news/sent-protocol-decoding-and-diagnosis-guide
- 来源：Pico Automotive 文档
- 摘要：PicoScope 解 SAE J2716 帧，给 tick 反推与 nibble 换算算例。
- 实战点：①tick = 最宽脉冲间隔 ÷ 56（168 µs → 3 µs），nibble = tick 数 − 12；②SENT Slow 取状态 nibble 2 bit，跨 16/18 帧拼厂商码与错码。
- 动作：扩 deep-dive（底稿首选）

### 2. TDK HAC 3930 SENT → S7-1200 PLC
- 链接：https://industrialmonitordirect.com/pl/blogs/knowledgebase/interfacing-tdk-hac-3930-sent-sensor-to-siemens-s7-1200-plc
- 来源：Industrial Monitor Direct（波兰语）
- 摘要：霍尔传感器 SENT 输出接入 S7-1200 PLC，附帧预算表。
- 实战点：①sync 56 tick=168 µs，数据 nibble 12+n=36-81 µs，pause 12-768 tick≤2.3 ms，整帧 264 µs-2.7 ms；②4-bit CRC seed 0x05、发送端取反，正确帧满足 calc_CRC XOR recv_CRC = 0x0F；③S7-1200 无 SENT 块，S32K144 FlexIO 无 input capture，收 SENT 须定时器测脉宽。
- 动作：写实战案例（工业侧接入）

### 3. What Is SENT SPC?
- 链接：https://www.teledynelecroy.com/oscilloscope/blog/what-is-sent-spc/
- 来源：Teledyne LeCroy 技术博客
- 摘要：Infineon 的 SENT SPC 半双工变体，MTP 长度当地址，一线最多 4 从机。
- 实战点：①MTP 长度即地址，传感器 0 为 7-15 tick，顺序任意（0,1,0,2,0,3）；②电平 Low <0.5 V / High >4.1 V，MTP 后留 response time 再回 SYNC。
- 动作：入主题笔记（库内空白）

### 4. SENT protocol (SAE J2716) practical use
- 链接：https://www.peak-system.com/fr/know-how/blog/the-sent-protocol-sae-j2716-explained-basics-application-and-practical-use-1/
- 来源：PEAK-System know-how
- 摘要：SENT 协议全貌与测试集成方法，含帧率数据率、变体演进与 EOL 链。
- 实战点：①tick 3-90 µs，3 µs 时帧频 1.5 kHz、净数据率约 37 kbps；②硬伤：无反向通道、仅点对点；SENT-B 修订中速度约翻倍。
- 动作：入主题笔记（底稿+选型）

### 5. PSI5-based pedestrian sensor testing
- 链接：https://www.add2.co.uk/?p=635
- 来源：add2（英国设备商）
- 摘要：PSI5 行人保护传感器产线 EOL 方案，讲节拍、PLC 集成与失效诊断。
- 实战点：①PSI5 V1.3 由 Autoliv/Bosch/Continental/TRW 联合制定，气囊传感器已量产；②产线由 PLC 编排、节拍优先，典型失效属装配类：压断/接触不良/制造不良。
- 动作：入主题笔记（PSI5 产线）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
