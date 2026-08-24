# BLE 候选素材 @ 2026-08-14 00:00

## 协议速览
- 是什么：低功耗蓝牙（BLE），4.0 起分叉，2.4GHz，GATT/ATT 模型
- 解决什么：替代经典蓝牙在 IoT/可穿戴的功耗痛点（峰值 <15mA，休眠 <1µA）
- 跟 L4 关联：IoT/可穿戴 🥇 最高优先级；产线连接/MTU/重连/OTA 必踩坑

## 候选文章（5 条）

### 1. BLE HCI 断开原因对照表（全错误码速查）
- 链接：https://blog.csdn.net/xiaoshideyuxiang/article/details/115075257
- 来源：CSDN 实战专栏
- 摘要：BLE Core 5.0 Vol2 Part D 全 HCI 错误码 0x00~0x3E 速查
- 实战点：0x06 PIN 丢失；0x3B conn interval 多见 iOS 默认 30ms 协商失败；0x3D MIC 失败=加密链路/LTK 丢失
- 推荐：✅ 扩 deep-dive（做 L4 速查表，跟 CAN-FD 错误帧同级）

### 2. Nordic nRF52832 sd_power_system_off 间歇性 NRF_ERROR_NOT_SUPPORTED
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/30389/nrf_error_not_supported-returned-by-sd_power_system_off-sometimes-nrf52
- 来源：Nordic 官方 DevZone Q&A（Case 200496）
- 摘要：nRF52832 调 sd_power_system_off 偶发返回错误，只有物理断电能恢复
- 实战点：SPI/I2S DMA 未完成时进入 sleep；必须 nrfx_*_uninit 后再 sleep；用 Power Management poll DMA；间歇性但量产必踩
- 推荐：✅ 扩 deep-dive（入 nRF52 主题）

### 3. Android BLE requestMtu 断连 + BLUETOOTH_PRIVILEGED 报错
- 链接：https://www.cnblogs.com/developer-wang/p/18459969
- 来源：博客园
- 摘要：部分 Android 在 onConnectionStateChange 直接 requestMtu(512) 断连
- 实战点：反射 BluetoothGatt.refresh()（系统隐藏 API）清缓存；每次开扫前清；MTU 失败 -100 重试
- 推荐：✅ 写实战案例（Android 主机侧）

### 4. Android BLE DeadObjectException + 133 异常全套模板
- 链接：https://blog.csdn.net/ming0gy/article/details/129835837
- 来源：CSDN
- 摘要：连接→断开→重连时序错位导致 DeadObjectException
- 实战点：disconnect 后必须 close()；重连前 sleep(500) 等释放；失败回调置 null 防泄漏
- 推荐：✅ 写实战案例（Android 连接管理）

### 5. Nordic nRF52832 量产 OTA 工具链实战
- 链接：https://zhuanlan.zhihu.com/p/94625175
- 来源：知乎量产实践
- 摘要：工厂 OTA 全流程：micro-ecc → nrfutil 密钥 → mergehex 合并 → nrfjprog 一次烧 → OTA zip
- 实战点：wchar_t 16/32 位兼容（IAR/Keil/GCC 切换常见）；nrfutil 6.0.0a1 OTA 校验失败要 6.0.0；--sd-req 必须与 bootloader sd_config.h 一致
- 推荐：✅ 扩 deep-dive（产线脚本入 BLE 量产笔记）

## 下一步
等你 review：激活 / 改写 / 丢弃
- 必扩 deep-dive：#1 HCI 速查 / #2 Nordic 睡眠坑 / #5 量产工具链
- 写实战案例：#3 / #4 Android 主机侧
