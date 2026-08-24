# BLE / Bluetooth LE 候选素材 @ 2026-08-07 12:00

## 协议速览
- 是什么:蓝牙 4.0 起引入的低功耗短距离无线,2.4GHz ISM
- 解决什么:可穿戴/传感器/智能家居纽扣电池设备"小数据率+长续航"通信
- 跟 L4 主题的关联:IoT/可穿戴核心接入,产线稳定性/跨平台/真实故障对应 chips-com 实战库

## 候选(5 条)

### 1. BLE 连接不稳定的 4 大原因(产品设计实战)
- 链接:https://blog.csdn.net/liwei16611/article/details/90412480
- 来源:CSDN
- 摘要:IoT 设计 BLE 突然断开根因:天线/芯片兼容/连接参数/代码逻辑;nRF52832 发完未等 ACK 重发致看门狗复位、0x3E 6 步握手丢包
- 关键实战点:发送必须等 `BLE_GATTS_EVT_HVN_TX_COMPLETE`;6 次重发 vs supervision timeout 是两套机制;2.4G 拥挤应用层重连
- 推荐动作:写实战案例

### 2. BLE Core v5.3 错误码 5 类故障排查
- 链接:https://blog.csdn.net/weixin_30530339/article/details/96051118
- 来源:CSDN
- 摘要:5 类错误码(超时 0x08/0x28、安全 0x05/0x3D、资源 0x09/0x3A、参数 0x3E/0x3B、协议栈 0x12/0x22)逐类拆解,含参数建议表 + 密集 WiFi 0x22 案例
- 关键实战点:移动 Supervision Timeout ≥ 2s,固定 ≥ 6s;0x3B 99% 是连接间隔不匹配(7.5ms vs 15ms);0x3D MIC 错误常因 iOS 加密中插入参数更新
- 推荐动作:扩 deep-dive(协议栈行为)

### 3. 蓝牙协议栈差异致连接失败(跨平台实战)
- 链接:https://blog.csdn.net/weixin_42466857/article/details/155210573
- 来源:CSDN
- 摘要:同一标准在 Nordic/Apple/Google/小米差异,SM/L2CAP/GAP 三大雷区;nRF52832 心率带连三星 Reason 5、iOS L2CAP 请求被自研栈断链、广播 Flags 缺 Bit5 Android 搜不到
- 关键实战点:SM 强制 LE-SC + Legacy 回退的 `#ifdef` 模式;L2CAP 未知信令必须 Command Reject 不能断链;Flags 错设 0x06(漏 Bit5)→ non-discoverable
- 推荐动作:写实战案例(可直接入 L4 主题笔记)

### 4. ESP32-S3 蓝牙工程实践与故障诊断
- 链接:https://blog.csdn.net/weixin_35761094/article/details/158439575
- 来源:CSDN
- 摘要:ESP32-S3 蓝牙工程视角(电池门窗磁 vs USB 智能灯控);Bluedroid HCI 共享内存、L2CAP MTU、WiFi/BLE 共用 RF 前端互相降灵敏度 10dB
- 关键实战点:CR2032 场景广播 ≤31 字节、连接间隔 ≥1s;`l2cap_mtu` 需在 `esp_bt_controller_init()` 前显式设;WiFi/BLE 双开需 `esp_wifi_set_max_tx_power(78)` 让出射频余量
- 推荐动作:扩 deep-dive(芯片平台特定)

### 5. Zephyr BT: bond deleted on pairing failure(真实 issue)
- 链接:https://github.com/zephyrproject-rtos/zephyr/issues/24086
- 来源:GitHub Zephyr(已修复,新增 `BT_SMP_ALLOW_UNAUTH_OVERWRITE`)
- 摘要:Zephyr 外设已建绑定,中心无对应绑定时被静默删除,致可被低安全配对覆盖无需用户交互;含 bt_smp reason 0x3 复现
- 关键实战点:触发条件 = 中心 clear all + 重连 + security 失败;IoT 设备绑定被静默覆盖
- 推荐动作:入主题笔记(安全/绑定设计要点)

## 下一步
等你 review 后决定:激活 / 改写 / 丢弃
