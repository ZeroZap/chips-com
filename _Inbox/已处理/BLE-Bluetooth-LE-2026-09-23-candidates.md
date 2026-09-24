# BLE / Bluetooth LE 候选素材 @ 2026-09-23 12:00

## 协议速览
- 是什么：2.4 GHz 跳频低功耗短距无线，GATT/ATT 模型
- 解决什么：手机/网关 ↔ 电池嵌入式设备（穿戴/医疗/工业传感）点对点
- 跟 L4 关联：IoT/可穿戴"实验室 OK 一上产线就挂"最集中爆发在 BLE

## 候选文章（5 条）

### 1. 蓝牙产线 Fail 闭环流程
- 链接：https://www.hhins.cn/xingyedongtai/12-392.html
- 摘要：Fail 拆成"误测/参数偏移/硬故障"三类，三站式闭环，MES 用 SN 串联。
- 实战点：①Fail≠报废，先过复测站<br>②维修后必须重跑完整测试序列<br>③每天汇总复测/维修/报废率作产线晴雨表
- 动作：扩 deep-dive（产线 Fail 字典补到 BLE 笔记"产线工程"）

### 2. 蓝牙模块量产四大卡点
- 链接：https://blog.csdn.net/weixin_29173777/article/details/165143181
- 摘要：27 个量产项目里 19 个卡点在蓝牙——烧录一致性、射频漂移、SPP 老化丢包、EMC 传导。
- 实战点：①JLINK 烧 5000 片后 3000 校验错，治具 PCB 长 8 mm 致 SPI 上升沿 3.2 ns<br>②车壳铜箔距天线 1.2 mm 致谐振偏移 70 MHz，辐射效率掉 63%<br>③BLE 广播 30 ms 时 SPP 延迟从 18 ms 跳到 127 ms
- 动作：写实战案例（可量化数据，可转成 L4 笔记）

### 3. BLE 系统级设计错误
- 链接：https://www.eurthtech.com/post/ble-is-not-just-a-protocol-system-level-design-mistakes-engineers-make
- 摘要：5 个错误——BLE 当透明管道、忽略 Central 行为、功耗被忽略、状态爆炸、安全假设过期。
- 实战点：①iOS/Android 后台策略动态改变 BLE 行为<br>②BLE 不是"自动省电"，全栈耦合功耗<br>③Bonding 状态累积导致现场难复现
- 动作：扩 deep-dive（架构视角补到 BLE 笔记"陷阱"）

### 4. BLE 在 lab OK 在产线挂
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 摘要：受控 Wi-Fi 干扰下测多款主流 BLE 模块，"Lab 通过 ≠ 现场稳定"。工业现场金属/移动设备/反射面引入 Wi-Fi 共存压力。
- 实战点：①差距主因是 2.4 GHz 共存而非硬件缺陷<br>②失败呈"间歇性延迟漂移+偶发断连"，难复现<br>③先怀疑天线/硬件常浪费数月，真因是固件栈调度
- 动作：扩 deep-dive（与上条互补：架构错误 + 实证数据）

### 5. BLE 抓包分析实战
- 链接：https://blog.csdn.net/weixin_28273593/article/details/165072960
- 摘要：从零搭建 nRF52840 Dongle + Wireshark 抓包，覆盖驱动烧录、过滤器、三类典型场景。
- 实战点：①OTA 用 Write Command 传固件 + 总长度比对 = 高干扰下必翻车<br>②心率带 Android OK / iPhone 13 反复重连，根因 SM 层 Identity Address 字段<br>③睡醒后连接失效，看广播间隔异常比看代码日志快
- 动作：写实战案例（抓包工具链 + 故障字典落 BLE 笔记"调试"）

## 下一步
等你 review：激活 / 改写 / 丢弃