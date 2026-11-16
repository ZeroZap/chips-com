# BLE 候选素材 @ 2026-11-02 12:00

## 协议速览
- 是什么：2.4GHz 跳频 + GATT 分层的低功耗蓝牙连接协议
- 解决什么：手机/网关与电池节点间的小包数据、信标广播与定位
- 跟 L4 主题的关联：BLE 是 L4 近距离低功耗主力，直接映射 L4 主题

## 候选文章（5 条）

### 1. TWI 室外必失效、室内必正常
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/77859/twi-always-fails-outdoors-and-never-fails-indoors-on-a-ble-enabled-nrf52
- 来源：Nordic DevZone 官方工程师答复
- 摘要：10% 产线板室外几十秒内 TWI 失败，室内正常；挂 10pF 阻抗分析仪即消失。
- 关键实战点：① 微波炉屏蔽箱内不复现，走出即复现 ② 怀疑 BLE 射频与 TWI 时序互扰 ③ 现场板只能软件绕开
- 推荐动作：扩 ble-failure-cases.md

### 2. Android 手机反复重连独占设备
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/71110/weird-connection-blocking-behavior---nrf52
- 来源：Nordic DevZone 官方工程师答复
- 摘要：Redmi Note 8 Pro 断连后主动重连，占死设备他人无法用；改 GAP 地址类型为 PUBLIC 后解决。
- 关键实战点：① 仅对手机最后连过的设备发生 ② 随机静态地址被记住 ③ 官方给出 sd_ble_gap_addr_set 改公开地址
- 推荐动作：扩 ble-failure-cases.md

### 3. 连上 BLE 后传感器采样率掉到 1/15
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/118052/data-loss-in-ble-when-sending-the-accelerometer-values
- 来源：Nordic DevZone 官方工程师答复
- 摘要：nRF52 单核上连 BLE 后采样从 3000/s 掉到 200/s，协议栈抢占 MCU；拉大连接间隔可摊平。
- 关键实战点：① 单核 MCU 被 BLE 实时事件抢占 ② 调连接间隔摊平每连接事件延迟 ③ 采样与发送须分任务
- 推荐动作：扩 ble-practical.md

### 4. 量产机 gatt error 133 与连接中途断开
- 链接：https://devzone.nordicsemi.com/thread/382020
- 来源：Nordic DevZone 官方工程师答复
- 摘要：三星 S22 连接报 error 133；安全请求延时 400ms 太小导致 iOS 侧响应不完整，改 1000–4000ms。
- 关键实战点：① 断开后须在 BLE_GAP_EVT_DISCONNECTED 重启广播 ② 安全延时改 PM_HANDLER_SEC_DELAY_MS ③ 低频晶振精度需复核
- 推荐动作：扩 ble-failure-cases.md

### 5. 英飞凌社区：AIROC B0/B1 硅片与 BSP 版本错配
- 链接：https://community.infineon.com/t5/AIROC-%E8%97%8D%E7%89%99/Bluetooth-LE-%E7%99%BC%E7%8F%BE%E7%84%A1%E6%B3%95%E5%9C%A8%E6%9F%90%E4%BA%9B%E6%9D%BF%E4%B8%8A%E5%9F%B7%E8%A1%8C/td-p/1106613
- 来源：英飞凌开发者社区（官方已结帖）
- 摘要：Find Me 例程栈初始化成功却无输出；根因 BSP 按 B1 硅片配，实板为 B0，需按官方 KB 转换。
- 关键实战点：① 3 款 EVK 同症状、另一款正常 ② 官方给 B0 转换 KB ③ 换 BSP 后工程师复现通过
- 推荐动作：扩 ble-failure-cases.md

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
