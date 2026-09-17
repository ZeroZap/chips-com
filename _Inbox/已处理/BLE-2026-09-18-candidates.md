# BLE 候选素材 @ 2026-09-18 00:00

## 协议速览
- 是什么：低功耗蓝牙（Bluetooth Low Energy），2.4 GHz 短距无线个人域网协议。
- 解决什么：可穿戴/IoT 设备低功耗周期上报与近距离连接，移动端 OS 主导连接参数。

## 候选文章（5 条）

### 1. nRF52 实测：400 ms 延迟是 central 决定的
- 链接：https://moltbook.com/post/09ee2ea3-0a02-4b26-b274-a0923bef87b6
- 来源：moltbook
- 摘要：固件请求 15ms 间隔，iOS 给 30ms、Android 48ms；逻辑分析仪证代码 <2ms。`sd_ble_gap_conn_param_update()` 是协商不是 setter。
- 关键实战点：central 持卡（iOS 15ms 起步、BlueZ 唯一肯给请求值）；批量化多次传感数据到一个 notify 修吞吐 ×4。
- 推荐动作：扩 deep-dive → 连接参数协商章节

### 2. nRF52840 iPhone 每 30 秒断连
- 链接：https://moltbook.com/post/03115e3c-f56c-4983-ad65-e2bfa4791902
- 来源：moltbook
- 摘要：同固件 Android 数小时稳，iPhone 30s 断；sniffer 抓 reason 0x08 timeout。固件请求 7.5/0/400ms 被静默拒，housekeeping 阻塞 radio。
- 关键实战点：iOS 硬规则（interval 15ms 倍数、timeout > (1+latency)*interval*2）；修 2 行——读回协商参数、选 30/0/6000ms。
- 推荐动作：入主题笔记 → supervision timeout 公式 + iOS 硬规则

### 3. nRF52 OTA 限速 8 KB/s，三旋钮解锁 80 KB/s
- 链接：https://moltbook.com/post/77190cec-49a1-465c-ac2f-036a1adbd719
- 来源：moltbook
- 摘要：1 Mbps PHY 推 OTA 实际 8 KB/s；启用 MTU=247 + DLE + interval=15ms 后到 80 KB/s，10×。同固件 iOS/Android 速度差异巨大。
- 关键实战点：三联调不可少（MTU + DLE + interval）；真实公式 = MTU × packets-per-event ÷ interval，central 握牌。
- 推荐动作：扩 deep-dive → BLE 吞吐量公式 + OTA 实战

### 4. Nordic DevZone 智能可穿戴产线 Notify 间歇丢失
- 链接：https://devzone.nordicsemi.com/thread/542561?ContentTypeID=1
- 来源：Nordic 官方 DevZone
- 摘要：1Hz sensor/IMU + event status 推送中，Sensor/IMU/Battery 间歇丢失而 Status 正常；现场能复现 lab 不行。问题缩到：是否真断、API 是否真调、错误码。
- 关键实战点：timer-driven 与 event-driven notify 在不同 work queue，可能互锁；现场加 log 验"API 真发出 + 返回值"。
- 推荐动作：入主题笔记 → 产线 Notify 间歇丢失排查流程

### 5. 稀土掘金：Android 连上了却收不到数据
- 链接：https://juejin.cn/post/7632298339148660776
- 来源：稀土掘金
- 摘要：连上 ≠ 链路通。GATT 只建通道不打开 Notify、不保证监听的就是上报 characteristic；需写 CCCD=0x0001 + 等 `onDescriptorWrite` 成功。
- 关键实战点：五状态 Disconnected→Connected→ServicesReady→NotificationReady→ProtocolReady；CCC 写完前不抢跑；"BLE 不稳定"很多是太早当 ready。
- 推荐动作：写实战案例 → Android Client 侧 BLE Ready 状态机样板

## 下一步
等你决定：激活 / 改写 / 丢弃