# BLE 候选素材 @ 2026-08-20 12:00

2.4 GHz GFSK 跳频低功耗短距无线，纽扣电池级 IoT/可穿戴首选；高频踩坑在产线 2.4 GHz 拥堵、烧录自检、配对失败

## 候选文章（5 条）

### 1. Why does your BLE work in the lab then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：DEWINE Labs 工业 BLE blog
- 摘要：工业/医疗/机器人 BLE 现场延迟抖动、莫名断连，多不是天线/硬件，而是 best-effort 调度被真实 RF 打穿。
- 实战点：①实验室无法复现现场 RF 拥堵；②平均延迟掩盖 P99 抖动；③多数团队误归因天线/PCB，先 firmware 调度优化
- 推荐动作：扩 deep-dive（"工业落地避坑"）

### 2. Fast Production Screening based upon Bluetooth DTM
- 链接：https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/fast-production-screening-based-upon-bluetooth-dtm
- 来源：Nordic 官方 devzone
- 摘要：产线 DTM 快速筛片，2 块 nRF51 DK + 屏蔽盒 + UART，日产能 10 万级，5s 判冷焊/物料错误/RF 性能。
- 实战点：①筛片 ≠ 功能测试只查 PER + 可启动；②DTM 是 SIG 强制认证环节可直接复用；③屏蔽盒 + 同轴衰减器，2 板扩 N 工位
- 推荐动作：写实战案例（绑定 BareOS/XinYi 板测）

### 3. How I Debugged a BLE Connectivity Bug in 10 Minutes
- 链接：https://dev.to/ble_advertiser/how-i-debugged-a-ble-connectivity-bug-in-10-minutes-using-real-time-logs-2ieh
- 来源：dev.to 工程实战
- 摘要：实时日志把 BLE 间歇性 bug 排查从天压到 10 分钟，覆盖 Write Without Response 丢包、参数协商、多 Central 竞争。
- 实战点：①Write Without Response 必须等 buffer 空；②连接参数被任一方拒绝 = 立即不稳；③多 Central 共享写顺序错乱 = 状态损坏
- 推荐动作：扩 deep-dive（"调试方法学"）

### 4. BLE 常见断连原因分析（Goodix GR551x/5525/5526）
- 链接：https://developers.goodix.com/zh/bbs/detail/c649c96ac97a4959a855b326b9b11f8b
- 来源：Goodix 官方开发者社区
- 摘要：把 BLE Spec 0x08/0x28/0x22/0x13/0x3D 映射到 Goodix 私有码 0x98/0xB8/0xB2/0xA3/0xCD，给 GPIO Diagnostic + 钩子两套基带抓信号方案。
- 实战点：①0x98（超时）= 先查射频再查中断；②0xB8（指令错过）= 调度不同步看 ISR/start 规律；③0xCD（加密失败）= 配对加密中插 LLCP 是根因
- 推荐动作：入主题笔记（错误码速查表）

### 5. Debugging BLE Peripherals with LightBlue
- 链接：https://punchthrough.com/debug-ble-peripheral-lightblue
- 来源：Punch Through（LightBlue 厂商）
- 摘要：外设生产前 6 项 checklist。LightBlue vs 自家 App 配对结果 = 一招定位责任侧。
- 实战点：①标准 central 二分定位责任侧；②app stack 配对 bug 成本指数级上升；③6 项 checklist 覆盖 90% 现场失败
- 推荐动作：写实战案例（wearable SOP）

## 下一步
review 后决定：激活 / 改写 / 丢弃
