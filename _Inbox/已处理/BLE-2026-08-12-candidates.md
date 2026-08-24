# BLE / Bluetooth LE 候选素材 @ 2026-08-12 00:00

## 协议速览
- 是什么：低功耗短距无线（2.4 GHz, 40 信道, GFSK），手机/可穿戴/IoT 标配
- 解决什么：纽扣电池设备小数据量、低占空比、低成本无线连接
- 跟 L4 关联：IoT/可穿戴首选无线，连接参数 / GATT / 配对是工程高频坑

## 候选文章（5 条）

### 1. Ellisys 抓包器 BLE 调试实战
- 链接：https://blog.csdn.net/weixin_31842715/article/details/161468370
- 来源：CSDN 实战博客
- 摘要：智能手环间歇性断连、日志无异常，Ellisys 从 PHY 到 ATT/GATT 全栈抓包定位
- 实战点：广播间隔异常→超时；CRC 失败→随机丢包；电源不稳（紫灯）影响抓包；缓冲区 200MB 太小
- 推荐：**扩 deep-dive** —— Ellisys 工具链 + 典型故障模式清单

### 2. ZephyrOS BLE 心率计 GATT 服务
- 链接：https://blog.csdn.net/weixin_42542669/article/details/160140788
- 来源：CSDN 实战博客
- 摘要：剖析 peripheral_hr 示例的 GATT 服务定义、特征值声明、通知机制
- 实战点：Kconfig 模块化（`CONFIG_BT_HRS`/`CONFIG_BT_BAS`）；标准 UUID（SIG）+ `BT_GATT_SERVICE` 宏；Docker 镜像避 Python 依赖坑
- 推荐：**入主题笔记** —— GATT 服务模板，可套 XinYi/BareOS 心率/电池服务

### 3. CircuitPython 内存优化 + BLE 故障
- 链接：https://blog.csdn.net/weixin_28673669/article/details/161077925
- 来源：CSDN 实战博客
- 摘要：SAMD21（M0, 32KB RAM）MemoryError 排查、`.mpy` 预编译节省 RAM、蓝牙连接失踪
- 实战点：`.py` vs `.mpy` 体积差；列表/字符串失控→碎片化；REPL 实时监控可用内存
- 推荐：**扩 deep-dive** —— 小内存 MCU+BLE 内存预算模型，可联动 BareOS（N32L40X 128KB）

### 4. BLE L2CAP / HCI ACI 深度解析（BlueNRG NCP）
- 链接：https://blog.csdn.net/weixin_36311421/article/details/158911248
- 来源：CSDN 实战博客
- 摘要：BlueNRG-2/3 NCP 框架下 ACI 命令体系：连接参数协商 / LE CFC / EATT
- 实战点：Connection_Interval [7.5ms, 4000ms]；SPSM=0x0027=EATT（BLE 5.3）；NCP 模式下 `aci_*` 不可在 SoC 单芯片直接调用
- 推荐：**入主题笔记** —— L2CAP/ECFC 进阶图谱，对应 L4 协议深度维度

### 5. Android requestMtu 断连 + Need BLUETOOTH PRIVILEGED
- 链接：https://www.cnblogs.com/developer-wang/p/18459969
- 来源：博客园
- 摘要：连接 GATT 后立即 `requestMtu(512)` 在部分 Android 机上直接断链；重连时缓存残留
- 实战点：反射 `refresh()` 刷 GATT 缓存；断开时降 MTU 100 退避重连；正确顺序 onConnectionStateChange→onMtuChanged→discoverServices
- 推荐：**写实战案例** —— 手机-外设互通坑清单（MTU/缓存/时序），故障库必备

## 下一步
等你 review 后决定激活/改写/丢弃
- 候选 1+5：故障库方向，落地性最强
- 候选 2+4：协议深度方向，补 L4 进阶知识
- 候选 3：跨 BareOS 复用价值高
