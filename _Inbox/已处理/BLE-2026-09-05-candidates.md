# BLE / Bluetooth LE 候选素材 @ 2026-09-05 12:00

## 协议速览
- 是什么：2.4 GHz 低功耗短距无线，1M/2M PHY + LE Coded
- 解决什么：电池月级寿命 + 手机直连 + mesh（IoT/可穿戴/产线 RTLS 主力）
- L4 关联：IoT/可穿戴首选；解"低功耗 + 实时性 + 共存(Wi-Fi/产线干扰)"三难

## 候选（4 条）

### 1. 4 款 BLE 模块 Wi-Fi 干扰实战对比
- 链接：https://dewinelabs.com/we-tested-4-popular-ble-modules-under-real-wi-fi-interference-and-heres-what-we-found/
- 来源：DEWINE Labs 行业 blog
- 摘要：100 B/100 ms 控制环 ≤30 ms 时延硬指标。干净 RF 4 款都过；2.4 GHz 干扰下标准 BLE 全崩——根因 firmware best-effort 调度而非硬件。LinkBlu RT 双通道隔离 + 干扰自适应给出 bounded latency 范式。
- 实战点：①瓶颈是 scheduling 不是 RF；②控制/日志分队列；③late packet = invalid packet
- 推荐动作：扩 deep-dive

### 2. CC254x BLE 4.0 OSAL 调度死锁复盘
- 链接：https://tsight.io/articles/11664458
- 来源：TrueSight 中文技术站
- 摘要：CC254x 8 KB RAM、7.5 ms 连接间隔下 OSAL 单线程遇死亡临界点。LL 层硬实时 ISR 被应用任务长期占用 → LL Timeout → 断链。GPIO 翻转 + 逻辑分析仪调试法。结论反直觉：禁用自动连接参数更新 + 绕过 GATT 直透传 LL 层。
- 实战点：①OSAL 入口/出口 GPIO 翻转对 LL ISR；②7.5 ms 是高负载分水岭；③主动放弃部分标准换稳定
- 推荐动作：入主题笔记

### 3. T20i 产线蓝牙待机死机根因（A2 线 19.2% 不良）
- 链接：https://www.renrendoc.com:9089/paper/532770742.html
- 来源：人人文库（专项攻关 PPT）
- 摘要：新开 A2 线蓝牙 19.2% 不良（行业 <1%）。待机 20 mA vs 良品 3 mA，看门狗 4 s 不复位=深度死锁。锁定 KT6368A DMA 异常 + 电压 2.4 V + TX/RX 倒灌三因子。串 100 Ω + 改料件检验 + 测试延至 20 s。
- 实战点：①QC 6 s vs 触发 15 s=测试盲区；②倒灌电流破坏上电时序；③热风枪复现=微裂纹
- 推荐动作：写实战案例

### 4. 仓库 BLE 网关 RTL8852BU 失效（Opcode 0xfcf0:-16）
- 链接：https://dredyson.com/optimizing-supply-chain-software-a-complete-step-by-step-guide-to-resolving-hardware-level-device-conflicts-in-warehouse-management-systems-and-fleet-management-iot-deployments
- 来源：Dre Dyson 物流技术 blog（12 年 IoT 顾问）
- 摘要：Fedora 44 RTL8852BU combo Wi-Fi/BT 芯片 `Opcode 0xfcf0 failed: -16` (=EBUSY)，单芯片故障致 WMS 全线瘫 48 h 损失 $47 k。日志 pattern：bluetoothd 初始化→22 s 后自终止→systemd 停服务。根因 firmware 初始化失败 + 共存资源争抢。
- 实战点：①combo 芯片单点故障放大；②dmesg pattern 比单行错误码更值钱；③仓库 throughput ≠ WMS bug
- 推荐动作：写实战案例

## 下一步
review 后决定: 激活/改写/丢弃
