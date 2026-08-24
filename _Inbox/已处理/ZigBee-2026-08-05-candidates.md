# ZigBee 候选素材 @ 2026-08-05 12:00

## 协议速览
- 是什么：基于 IEEE 802.15.4 的低功耗短距离 Mesh 无线协议
- 解决什么：智能家居/工业传感网中多设备、低带宽、长电池寿命的组网通信
- 跟 L4 主题的关联：IoT/可穿戴核心协议之一，与 BLE/Thread 互补

## 候选文章（5 条）

### 1. Zigbee Debugging NCP（Silicon Labs 知乎）
- 链接：https://zhuanlan.zhihu.com/p/339588055
- 来源：知乎 / Silicon Labs 官方号
- 摘要：NCP 固件崩溃无 crash info 输出问题。方案：SWO 引脚+虚拟 UART 打印 Reset info 0x07/CRS 等寄存器内容反推调用栈；提供 ncp-debug-print plugin 路径与硬件配置步骤。
- 关键实战点：NCP vs SoC 调试差异；SWO/VUART 硬件配置；plugin 安装路径 `protocol\zigbee\app\ncp\plugin\ncp-debug-print`；crash info 解码方法
- 推荐动作：扩 deep-dive（NCP/Host 架构 + crash 解析模板）

### 2. Zigbee 光源产品产测流程说明（涂鸦）
- 链接：https://developer.tuya.com/cn/docs/iot/zigbee-production-test-process-description?id=K9s9rhitjpf87
- 来源：涂鸦开发者平台
- 摘要：单色/RGB/RGBW/RGBWC 灯具产测 SOP。USB Dongle 拨码 4 置 ON、放距测架 2m 内、配网设备必须先 App 移除再断电。分老化前/老化后两次测试。
- 实战点：产测 USB Dongle 准备；老化前/后测试差异；多通道产测矩阵
- 推荐动作：写实战案例（产测 SOP 模板）

### 3. ZIGBEE调试总结（holle_kitty / CSDN）
- 链接：https://blog.csdn.net/holle_kitty/article/details/80161804
- 来源：CSDN 实战博客
- 摘要：ch340 不能为 zigbee 供电需用 pl2303；WiFi 1/6/11 下 zigbee 选 11/15/20/26 避让；ZED 串口唤醒只保 3s 同步窗口，3 次接收后不再接收导致同步广播丢 2~3 字节。
- 实战点：USB 转串口芯片选型；WiFi/Zigbee 信道共存表；ZED 同步广播丢数据
- 推荐动作：入主题笔记（信道规划 + 终端节点限制）

### 4. Simplicity Studio v5 配置 ZigBee 调试打印（世强）
- 链接：https://www.sekorm.com/news/11273429.html
- 来源：世强
- 摘要：EFR32MG21 串口打 ZigBee 调试信息流程：Z3Light → SOFTWARE COMPONENTS 搜 debug → 勾选 Debug Printf → Configure → 生成代码。
- 实战点：调试组件宏开关；AppBuilder 工程结构
- 推荐动作：跳过（#1 已覆盖 NCP 调试核心）

### 5. Zigbee 网络故障诊断与排除（豆丁）
- 链接：https://www.docin.com/p-4714102065.html
- 来源：技术文档（2024-08）
- 摘要：系统分类 zigbee 故障：设备无法连接、信号强度低、网络性能下降、ZED 休眠协调。配 zigpy 库 Python 示例，含网络 ID/通道匹配、信号盲区排查流程。
- 实战点：故障分类清单；zigpy 工具链；PAN ID 匹配检查
- 推荐动作：入主题笔记（故障分类清单 + zigpy 入门）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
