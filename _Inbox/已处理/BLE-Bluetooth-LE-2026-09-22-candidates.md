# BLE / Bluetooth LE 候选素材 @ 2026-09-22 00:00
> 2.4 GHz 低功耗短距 / 主从 GATT 栈 → IoT/可穿戴双向通信。"lab 通过即发货"翻车高发区。

### 1. Why does your BLE work in the lab – then fail in production?
- 来源/链接:dewinelabs(英国无线测试实验室) · https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 摘要:实测多款 BLE 模块在 Wi-Fi 干扰下的延迟/吞吐曲线,揭示"实验室通过 ≠ 产线能用"。环境复杂度是头号变量,硬件非根因;BLE 固件为消费类设计。
- 实战/动作:工厂 RF 干扰 latency spike + 随机 disconnect;翻车常先疑天线/PCB,实为 firmware 时序 → 入 L4-BLE"产线干扰基线"

### 2. Our BLE Connection Was a Ghost. I Rebuilt It From Scratch.
- 来源/链接:mohsin.xyz(Omi 可穿戴) · https://mohsin.xyz/blog/our-ble-connection-was-a-ghost
- 摘要:Omi BLE audio streaming "app 显示 connected 但音频断流"的 ghost connection,Flutter 补丁堆 4 层状态混乱。重构:Native BLE Transporter 替换 flutter_blue_plus,崩溃率显著下降。
- 实战/动作:4 个 connection state 真值源(provider/service/transport/plugin)冲突;15s 重连 timer in-pocket 持续开 radio → 入 BLE"可穿戴 audio streaming 选型"

### 3. BLE Is Not Just a Protocol: System-Level Design Mistakes
- 来源/链接:eurthtech(嵌入式工程咨询) · https://www.eurthtech.com/post/ble-is-not-just-a-protocol-system-level-design-mistakes-engineers-make
- 摘要:5 系统级错误:把 BLE 当透明管道、忽略中央设备、电源意识缺失、状态爆炸、安全假设不演进。Case:传感可靠但 BLE 连接/重连/电池全翻车。
- 实战/动作:Prototype illusion(原型 ≠ 部署);BLE 常占电池预算大头;bonding/MTU/CCCD 不显式管理 → fragile → 入 L4-BLE"系统级陷阱"

### 4. 蓝牙配对失败:40ms 间隔时序错位实战
- 来源/链接:CSDN RFCEO(nRF52 实测) · https://ruban.blog.csdn.net/article/details/156693172
- 摘要:40ms 广播偶发连接失败根因:主从时序窗口错位。给 nRF52 固件代码(interval 随机化、全信道、listen delay)+ 主从时序图。含故障对策表(配对/安全/射频/供电/时序)。
- 实战/动作:40ms ±10% 随机化 + 全 3 信道 + listen delay=1;配对 40ms / 成功 100ms 降功耗;主扫窗 ≥ 从广播间隔 → L4-BLE 配对时序优化

### 5. The 10 Most Common BLE Bugs and How to Find Them
- 来源/链接:hubble(BLE 社区 bug 库) · https://hubble.com/community/guides/the-10-most-common-ble-bugs-and-how-to-find-them/
- 摘要:10 BLE 高频 bug:连接参数算错、跨厂商配对不一致、MTU 静默失败、CCCD 未写、sleep 毫安级、Advertising 不可发现、字节序/buffer 失效、GATT 变更缓存、bonding 残留、debug print 阻塞 HCI。
- 实战/动作:CCCD 必须 central 写 0x0001,peripheral 不能代劳;MTU 必须 request + handle response,否则 fallback 23B;supervision timeout ≥ 6× connection interval → 作 BLE troubleshooting checklist 永久参考