# BLE/Bluetooth LE 候选素材 @ 2026-09-26 00:00

## 协议速览
- 是什么 / 解决:2.4 GHz 跳频低功耗短距无线,GATT/ATT;手机/网关 ↔ 电池嵌入式设备点对点
- 跟 L4 关联:"实验室 OK 一上产线就挂"在 BLE 最集中

## 候选文章(5 条)

### 1. Why does your BLE work in the lab – then fail in production?
- 链接:https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源:Dewine Labs
- 摘要:6 款 BLE 模块在可控 Wi-Fi 干扰实测。产线真实失效:Wi-Fi/金属/反射面叠加 → latency 抖动 + "链路未断但控制回路已超时"的隐性断链
- 实战点:①硬件通常不是瓶颈,根因在 BLE 协议栈假设"偶发延迟可接受";②产线几十个 2.4G 设备+金属结构在实验室不可复现
- 推荐:扩 deep-dive(产线 RF 干扰)

### 2. 蓝牙 5.2 工业级:453-00145R + R7KA8D2KFLCAC 协同实战
- 链接:https://blog.csdn.net/weixin_42570484/article/details/165530822
- 来源:CSDN(7 款网关量产)
- 摘要:Broadcom 453-00145R 前端 + Silicon Labs EFR32BG22 (PSA L3) 协同。产线 bug:`sl_bt_advertiser_set_radio_channels(0x07)` 误写 `0x01` → iOS 扫不到
- 实战点:①量产网关要解决 20 节点同上报+0.3s 本地响应+防 MITM;②广播信道掩码错一位 = iOS 兼容炸
- 推荐:入主题笔记(BLE 工业选型 + 烧录坑)

### 3. A short story about Android BLE timeouts and GATT internal errors
- 链接:https://blog.classycode.com/a-short-story-about-android-ble-connection-timeouts-and-gatt-internal-errors-fa89e3f6a456
- 来源:Classy Code Blog
- 摘要:Android BLE 二次连不上,三星卡 10-20s、Pixel 触发 GATT 129。HCI snoop log + Logcat TRC_L2CAP/TRC_GATT=6 + Ubertooth 嗅探三层锁住 disconnect() 19s 后才真释放
- 实战点:①Bluedroid GATT 状态机存在隐性 stuck,业务代码调不出来;②Ubertooth 2015-10-R1 有 bug,需回退 09-R2 才能 follow 连接
- 推荐:写实战案例(Android BLE 调试三件套)

### 4. ESP32 Bluetooth Connection Drops: Error Diagnosis & Fixes
- 链接:https://electricalflux.com/mcu-general/esp32-bluetooth-connection-error-diagnosis
- 来源:electricalflux
- 摘要:Bluedroid 启动吃 110-140 KB SRAM → OOM。0x103/0x106/0x3008/0x102/0x2002 错误码-失效域-修复映射,MTU 协商触发 Guru Meditation 硬修复(`onMtuChanged` 必挂)
- 实战点:①BLE-only 必须 `esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT)` 回收 ~30 KB;②MTU 硬编 23 B 是 silently truncate 根因
- 推荐:扩 deep-dive(ESP32 BLE 内存预算)

### 5. Robust BLE on Android 12+: Foreground Services + Auto-Reconnect
- 链接:https://dev.to/ble_advertiser/robust-ble-preventing-disconnections-and-implementing-auto-reconnect-on-android-12-with-in8
- 来源:DEV Community
- 摘要:Android 12+ 后台进程激进回收,普通 Service 几秒就死。`connectedDevice` 类型 Foreground Service 唯一稳定;`connectGatt(autoConnect=true)` 是被动慢重连,工业场景要主动循环
- 实战点:①必须 `FOREGROUND_SERVICE_CONNECTED_DEVICE` 保活 BLE;②`BLUETOOTH_SCAN` 加 `neverForLocation` 绕过位置权限
- 推荐:入主题笔记(Android BLE 后台保活)

## 下一步
等你 review:激活 / 改写 / 丢弃。优先级 1>2>3>4>5