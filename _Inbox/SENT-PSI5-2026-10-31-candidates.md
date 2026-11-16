# SENT / PSI5 候选素材 @ 2026-10-31 12:00

## 协议速览
- 是什么：SENT（SAE J2716）单线脉冲宽度编码 + PSI5 两线电流调制，ECU 接传感器的低成本数字链路。
- 解决什么：把模拟/PWM 传感器的噪声与地偏置换成自时钟数字帧，只留 2-3 根线。
- 跟 L4 主题的关联：全库 0 篇 SENT/PSI5 笔记（TOPIC_MATRIX L138 待新建），矩阵点名、内容全空。

## 候选文章（3 条）

### 1. SENT 协议：单线的艺术——PWM 编码、CRC 校验与高精度传感器数据
- 链接：https://blog.csdn.net/qq_37619128/article/details/160369654
- 来源：CSDN · 发动机控制系统一线调试
- 摘要：节气门位置传感器整车环境"跳动"，实验室稳定、换件无效；示波器抓到同步脉冲从 56 tick 缩到 54 tick。
- 关键实战点：①根因是点火 EMI 耦合致边沿畸变，加 RC 滤波只缓解不根治；②脉冲宽度 =(12+数据值)×Tick，范围 12-27 tick，超界即判错；③Tick 由 56 tick 同步脉冲反推（168μs/56=3μs），1% 误差累积到 27 tick 脉冲即 0.27 tick。
- 推荐动作：入主题笔记（最硬，建议直接开 SENT 主题底稿）

### 2. sent-decoder：SAE J2716 (SENT) decoder for Sigrok
- 链接：https://github.com/enp6s0/sent-decoder
- 来源：GitHub · 开源实现（MIT）
- 摘要：少见的开源 SENT 解码器，支持 SPC 短 PWM 码，作者自陈 feature-incomplete，可作实现参照。
- 关键实战点：①三种 CRC 口径并存——J2716 Recommended（补零，仅数据 nibble）、J2716 Legacy（不补零）、Infineon TLE4998（数据+状态 nibble），选错必然校验不过；②SPC 脉冲目前直接跳过未解码；③帧边界靠时间间隔而非标志位，抗干扰弱。
- 推荐动作：入主题笔记（参考实现 + CRC 变体表）

### 3. 用 PSI5 低成本实现汽车传感器菊花链组网实战（含初始化与异常处理避坑）
- 链接：https://blog.csdn.net/weixin_30352191/article/details/97359645
- 来源：CSDN · 车身电子量产项目
- 摘要：PSI5 菊花链物理层参数、时隙规划、初始化三阶段与自检错误码，含低温轮速阵列失效定位。
- 关键实战点：①静态电流基准 7mA±10%，逻辑 1 增流 20mA（18-22mA），>2m 线缆末端须并 120Ω，否则曼彻斯特回波；②初始化 0x1F=CRC 错、0x1F4=自检失败，恢复为复位电源/降速/切冗余；③某车型轮速阵列低温通信失败，根因是电源调整管响应慢，加预充电解决。
- 推荐动作：写实战案例

## 备选（偏教程/工具向，未展开）
- 示波器解码 SENT（J2716-2016）接线与故障波形 — https://blog.csdn.net/weixin_29193259/article/details/158415679
- PSI5 vs SENT vs SPI 选型与调试工具对比 — https://www.toutiao.com/article/7701611965088678419
- CANoe .Sensor 分析/仿真 PSI5 与 SENT — https://cdn.eenewseurope.com/en/analysis-and-test-of-psi5-and-sent-sensor-protocols-3/

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
