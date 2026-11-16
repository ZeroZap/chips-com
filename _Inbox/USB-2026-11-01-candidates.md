# USB 3.x / Thunderbolt 候选素材 @ 2026-11-01 00:01

## 协议速览
- 是什么：5Gbps/10Gbps 差分对高速总线，与 USB 2.0 共存的双层架构。
- 解决什么：相机/存储/FPGA 产线采集，LTSSM 决定能否跑满速率。
- 跟 L4 主题的关联：TOPIC_MATRIX L140「USB 3.x / Thunderbolt」仍待新建；failure-cases 20 例无 LTSSM 逐段分析。

## 候选文章（5 条）

### 1. 工业相机频繁掉线：USB 供电不足
- 链接：https://ask.csdn.net/questions/9956064
- 来源：CSDN 问答 · 机器视觉
- 摘要：日志级定位，瞬时功耗实测超 1.3A，Windows 事件 201/219、dmesg 报 reset failed。
- 关键实战点：①无源延长线 >2m、无磁环或接扩展坞时掉线率升 3 倍；②解法：主动式延长 + 工业锁扣线 + PD 供电。
- 推荐动作：写实战案例（补 failure-cases 案例 16）

### 2. Wireshark 抓包实战分析 USB3.0 链路训练（LTSSM）
- 链接：https://blog.csdn.net/weixin_34194829/article/details/161553527
- 来源：CSDN · Beagle+Wireshark
- 摘要：Wireshark + 嗅探器把 LTSSM 变为可读状态数据，附扩展坞枚举失败与 SSD 降速案例。
- 关键实战点：①TS1 超限=CDR 失锁、TS2 中断=均衡不匹配、Idle 丢失=阻抗突变；②扩展坞 Polling.RxEQ 重试，根因 CTLE 过激。
- 推荐动作：扩 deep-dive（建 usb-ltssm.md）

### 3. USB compliance tests：USB 3.0 设备检测流程
- 链接：https://github.com/CrabCapital/apu2-documentation/blob/HEAD/docs/research/USB_compliance_test.md
- 来源：GitHub · apu2 文档库
- 摘要：逐阶段拆解 USB3 检测流程并标注 Spec 节号，RxDetect 到 U0 可查。
- 关键实战点：①RxDetect 连续 8 次未检出终端电阻即进 SS.Disabled，主机此后再不探测 USB3，转枚举 USB 2.0；②给出电气/链路层合规的仪器取舍。
- 推荐动作：入主题笔记（检测流程）

### 4. usb3_pipe：FPGA 开源 USB3 Device Core（LiteX）
- 链接：http://github.com/enjoy-digital/usb3_pipe
- 来源：GitHub · enjoy-digital（2026-10 活跃）
- 摘要：FPGA 内实现 USB3.2 Gen1/Gen2 PHY + Device Core，含完整 LTSSM 实现。
- 关键实战点：①实测 Gen1 446MB/s、139GB 全双工 0 错误 0 Recovery；②Gen2 10Gbps 在 UltraScale+ GTY 跑通，附 debugging-guide.md。
- 推荐动作：入主题笔记（LTSSM 参考）

### 5. FX3 USB3.0 Type-C 配置（KBA DOC-10403）
- 链接：https://community.infineon.com/t5/USB-superspeed-peripherals/USB3-0-configuration/m-p/77533
- 来源：英飞凌开发者社区
- 摘要：FX3 用 MUXSEL GPIO 控 2:1 SS 复用器做 Type-C 方向翻转，失败即换差分线重试。
- 关键实战点：①SS_COMP_ENTRY 与 USB3_LNKFAIL 任一触发即翻向；②加比较器接 CC 线免改固件。
- 推荐动作：入主题笔记（方向检测+降级）

## 备选
- 智云腾 3C 厂机器视觉线 USB3 花屏/降速案例（90Ω±5%，厂商软文需核实）https://zytino.com/NewsDetail/7428331.html

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
