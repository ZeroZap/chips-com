# BLE 候选素材 @ 2026-10-10 00:00

## 协议速览
- 是什么：低功耗短距无线，2.4 GHz ISM，广播+连接+GATT
- 解决什么：手机-外设可发现/可连接/可加密通道，IoT/可穿戴事实标配
- 跟 L4 关联："实验室 OK 产线挂"高发——配对/重连/缓存/广播拥塞全是 L4 坑

## 候选文章（5 条）

### 1. Hubble — Debug BLE with Sniffer
- 链接：https://hubble.com/community/guides/how-to-debug-ble-connection-failures-with-a-sniffer/
- 来源：Hubble Network 工程 blog
- 摘要：nRF Sniffer+Wireshark 5 阶段（Adv/Initiate/Param/Pair/Svc）定位失败，每阶段过滤+染色规则
- 实战点：① LL_REJECT/TERMINATE/SMP Failed 红染色秒定位失败点；② Sniffer 必开 Follow mode 跨广告→数据信道不丢
- 推荐：扩 deep-dive（5 阶段方法论适合 BLE 笔记骨架）

### 2. Hubble — 10 Most Common BLE Bugs
- 链接：http://hubble.com/community/guides/the-10-most-common-ble-bugs-and-how-to-find-them
- 来源：Hubble Network 工程 blog
- 摘要：10 bug 速查：连接秒断/phone 配对/MTU/CCCD/电流/可见/腐蚀/吞吐/参数/重连
- 实战点：① Bonding 仅 RAM 掉电必失败；② iPhone RPA 每 15 min 换地址，没 IRK 不认；③ CCCD 必须 client write 后 server 才 notify
- 推荐：入主题笔记（BLE-Common-Bugs.md 骨架可用）

### 3. BeaconZone — Poor Beacon Signals（100+ 同址）
- 链接：https://www.beaconzone.co.uk/blog/category/detectiontime
- 来源：BeaconZone blog + Samsung 资助论文
- 摘要：同址 100+ beacon 检测延迟指数增长。TX 0→+4 dBm 续航腰斩，adv ≤600 ms iOS 才稳
- 实战点：① 同频广播同信道相撞只能等下个 scan window；② adv 内置随机抖动降持续碰撞；③ 多 scanner×多 advertiser latency 与参数强相关
- 推荐：写实战案例（产线/仓储 BLE 部署 L4 痛点）

### 4. CSDN — 蓝牙配对连接：协议栈到实战
- 链接：https://blog.csdn.net/weixin_29240343/article/details/158636799
- 来源：CSDN 工程师长文（7 节深度）
- 摘要：经典+BLE 协议栈讲 Android Bluedroid btm_sec.c 状态机，9 个 tBTM_PAIRING_STATE 追踪三大故障日志路径
- 实战点：① btm_sec_change_pairing_state 日志追流转=国产安卓调试利器；② HCI_ERR_CONNECTION_TIMEOUT=19 vs HCI_ERR_PEER_USER=19 易混
- 推荐：入主题笔记（中文素材补 Hubble 协议栈视角空缺）

### 5. CSDN — STM32 BLE 配对/不稳定（HW-FW-Env）
- 链接：https://ask.csdn.net/questions/9233434
- 来源：CSDN 问答（采纳，2026-01）
- 摘要：HW（天线 S11≤-10dB、晶振≤±20ppm）+ FW（间隔/MTU/白名单）+ SW（GAP/GATT FSM、SysTick 抢 HCI）+ Env（2.4G 拥塞）
- 实战点：① STM32WB 晶振 ±25ppm 直接 CRC 批量失败，AN5289 Rev 4 是底线；② SysTick 优先于 HCI_TL → 事件丢
- 推荐：扩 deep-dive（硬件视角补 Hubble 软件盲区）

## 下一步
等 review：激活 / 改写 / 丢弃
