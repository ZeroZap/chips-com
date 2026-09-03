# BLE / Bluetooth LE 候选素材 @ 2026-09-03 00:00

**协议速览**：2.4 GHz 跳频低功耗短距无线协议栈，IoT/可穿戴核心；产线"实验室 OK 出货挂"是头号实战问题。

## 候选文章（5 条）

### 1. 工业现场 BLE 跳频与时序物理真相
- https://tsight.io/articles/15176126 · tsight.io（中文）
- 摘要：Ellisys 抓包解构工业车间断连——高金属反射+变频器干扰下 Channel Map 未更新→ACK 在受损信道无效握手→T_IFS 偏移致 LL_CONNECTION_UPDATE_IND 超时与 MIC Failure。
- 实战：天线去耦/单点接地降 CRC 错；强制屏蔽 Wi-Fi 拥堵 10-20 信道；T_ACK 偏差定位中断嵌套。
- 动作：**入主题笔记**（跳频+ACK 时序）

### 2. Why does your BLE work in the lab – then fail in production?
- https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/ · Dewine Labs
- 摘要：BLE 模组在 Wi-Fi 干扰受控测试下延迟/吞吐/断连横向对比；揭露"lab 通过≠现场可用"——根因是环境复杂度、central 端 OS 策略、生产 RF 而非硬件。
- 实战：工厂/医院 RF 密度远大于 lab；先改参数/调固件别先换硬件；症状时有时无=RF 环境变化。
- 动作：**扩 deep-dive**（工业 BLE 验证方法论）

### 3. BLE Data Integrity Failures — Nordic 真实调试
- https://devzone.nordicsemi.com/f/nordic-q-a/125365/ble-data-integrity-failures-out-of-order-segments · Nordic DevZone
- 摘要：BLE-WiFi 桥接 800 KB 大文件时，高负载并发下 GATT notification 出现 (A1,A2,A2,A4) 重包；CRC fail→SAR 重排序崩→重传雪崩。三方日志时间戳对位是定位关键。
- 实战：SFP Nack/Timeout/tcp_window_full/dup_ack 时间关联=金标准；SAR 须显式处理 CRC fail 后序号空洞；双 radio 并发=调度雷区。
- 动作：**写实战案例**（三方日志对位时间轴，L4 价值最高）

### 4. BLE Is Not Just a Protocol: System-Level Design Mistakes
- https://www.eurthtech.com/post/ble-is-not-just-a-protocol-system-level-design-mistakes-engineers-make · EurthTech
- 摘要：5 大系统级错误——①BLE 当 transparent pipe；②忽略 central 端 OS 后台策略；③功耗 afterthought；④状态爆炸/老 bond；⑤安全配置一次定终身。附部署产品案例。
- 实战：BLE 当事件驱动子系统设计；central 端视为不可信；状态转换必须显式管理。
- 动作：**入主题笔记**（BLE 系统级陷阱）

### 5. 40 万台安全产品 BLE 重设计
- https://needcode.io/?p=11693/ · needCode（产线出货级实战）
- 摘要：40 万台天花板安全产品——把"持久连接+keepalive"反转为"按需广播+控制端常扫"，能量预算从"维持链路"挪到"传数据"；配 Boot POST+周期 self-test+失败 loud 不 silent。
- 实战：连接/扫描/广播/参数按场景重设计别照抄 SDK 默认；安全产品 silent fail 比 crash 更致命；build system 隔离驱动与报警逻辑。
- 动作：**入主题笔记**（连接架构+L4 IoT 电源预算+安全 fault 模型）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃

---
跳过 24h 内跑过的 CAN-FD/CAN-XL（9/2 12:03）；本轮=BLE（轮询表第 1 位）；5 条全部满足"实战/产线/真实故障"标准。
</content>
</invoke>