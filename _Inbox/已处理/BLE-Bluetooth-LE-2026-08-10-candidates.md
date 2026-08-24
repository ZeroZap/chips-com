# BLE / Bluetooth LE 候选素材 @ 2026-08-10 12:00

## 协议速览
- 是什么：低功耗短距离无线协议，2.4GHz / 40 频道（3 广播+37 数据）/ GATT 模型
- 解决什么：纽扣电池设备（手环/传感器/门锁）的间歇性小数据上报
- 跟 L4 主题的关联：IoT/可穿戴首选协议，量产阶段连接失败/配对异常/丢包都是高频故障

## 候选文章（4 条）

### 1. 用 Ellisys 精准诊断 BLE 连接失败五大场景
- 链接：https://blog.csdn.net/jjfatjjfat/article/details/84158159  来源：CSDN
- 摘要：智能锁 OTA 在小米机型 20% 失败，Ellisys 抓到 transmitWindowOffset 超从设备能力；医疗血压计华为 P50 首次连接仅 60%
- 实战点：① Ellisys 协议层抓包定位 LL 参数 ② GATT 错误码 133/257 真实根因
- 推荐动作：扩 deep-dive（往 ble-failure-cases.md 补 Ellisys 案例+错误码速查表）

### 2. 蓝牙协议栈差异导致连接失败排查
- 链接：https://blog.csdn.net/weixin_42466857/article/details/155210573  来源：CSDN（nRF52832 实战）
- 摘要：nRF52832 心率带强制 LE SC，连 iPhone 稳、连三星 A 系列报 SM Reason 5；广播 Flags=0x06 被 Android 判 non-discoverable
- 实战点：① SM 安全策略动态适配 ② L2CAP 未知命令必须 Command Reject 而非断链 ③ Flags 必须含 Bit5（0x1A）
- 推荐动作：扩 deep-dive（往 ble-failure-cases.md 补"协议栈差异三大雷区"+多平台测试矩阵）

### 3. BLE 连接异常断开原因深度解析
- 链接：https://blog.csdn.net/pytorch8learner/article/details/155528816  来源：CSDN（工业 IoT）
- 摘要：0x3E 错误码深度解析（连接 6 个广播事件内未成功）；自定义信道选择算法 +50% 稳定性；Android 同时只能连 6 个 BLE
- 实战点：① 0x3E = LL 同步超时 ② PCB 天线阻抗匹配 +30% 距离 ③ 开关电源噪声耦合滤波
- 推荐动作：扩 deep-dive（往 ble-failure-cases.md 补"0x3E 错误码家族"+抗干扰硬件设计）

### 4. 蓝牙智能硬件常见报错处理（产线 SOP）
- 链接：https://www.cnblogs.com/yangykaifa/p/19558941  来源：博客园（.NET MAUI 跨平台 BLE 实战）
- 摘要：三大报错（搜索不到/连接失败/丢包）配分步方案；Nordic nRF52840 固件 GATT 注册顺序；BLE MTU 默认 20B
- 实战点：① Nordic 固件初始化顺序（nrf_sdh→gatt_init→adv_start） ② 协议帧最大 20B（DATA 14B） ③ 10 分钟快速排查流程
- 推荐动作：写实战案例（合并到 ble-practical.md 当"产线标准化排查 SOP"）

## 下一步
- 重点推荐 #2（协议栈差异）和 #3（0x3E 错误码），跟 chips-com "故障实战"方向最贴
- 等你 review 后决定：激活/改写/丢弃
