# BLE 候选素材 @ 2026-08-27 00:00

## 协议速览
- 是什么：低功耗短距无线（2.4 GHz），间歇上报+纽扣电池数年续航
- 解决什么：替代有线/经典蓝牙的"小数据+省电"场景（可穿戴/工业传感/Beacon）
- 跟 L4 关联：IoT/可穿戴首选物理层；实战故障（共存/重传/功耗/连接抖动）是硬通货

## 候选文章（3 条）

### 1. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：DEWINE Labs（工业 BLE 厂商 blog）
- 摘要：工业 BLE 上线后 latency 10→200ms+ 抖动、随机断连、Wi-Fi 干扰吞吐崩塌。根因常不是 RF/PCB 而是消费级 stack 的 best-effort 调度；DEWINE 用对照实验推翻"硬件不行"误判，给出 deterministic stack 替换（<10ms 确定性、>700kbit/s under interference）。
- 关键点：① 故障不灾难化——latency spike/间歇断连/跟 Wi-Fi 时段相关 ② 90% 团队先怪 RF 浪费数月才发现是固件层 ③ 解决思路是换 deterministic stack 而非重做硬件
- 推荐：**扩 deep-dive**，入主题笔记做"工业为啥不能用手机外设同款 stack"

### 2. CH582 低功耗实战：1.2mA→5μA 排查全记录
- 链接：https://blog.csdn.net/weixin_27956639/article/details/161208920
- 来源：CSDN（沁恒 CH582 实战，温湿度信标项目）
- 摘要：CH582（BLE 5.3 + RISC-V）信标标称 6 月续航实测只撑 3 周。72h 排查锁定 3 漏电流陷阱：DEBUG 宏 UART 活跃 / 浮空 GPIO 单引脚 ~200μA 漏电 / 软件定时器泄漏持续唤醒。1.2mA→5μA。
- 关键点：① 工具 Keithley 2450（μA 静态）+ TCP0030A 电流探头 + Saleae ② **测量前必断 J-Link**（否则测的是调试器电流）③ 国产 RISC-V+BLE 5.3 真实量产踩坑，**不是** Nordic 教程
- 推荐：**写实战案例**——CH582 跟 user 国产 RISC-V+可穿戴方向契合，拆"国产 BLE MCU 量产功耗 3 陷阱"

### 3. 蓝牙功耗异常飙升？SPI/BLE 交互调试指南
- 链接：https://www.kuazhi.com/post/716533818.html
- 来源：夸智网长文（STM32 + nRF52840 案例）
- 摘要：STM32+nRF52840 通过 SPI 外挂，实测 3.2mA vs 理论 5μA（600 倍）。拆 3 类异常模式（持续高平台/周期尖峰/长时唤醒），给 ISR 三不原则、零拷贝环形缓冲、动态连接参数切换、Python+Monsoon 自动化测试平台。
- 关键点：① "假休眠"陷阱：CPU 睡了但 SPI/BLE_INT 还在工作 ② ISR 三不原则：不打印日志/不访问 SPI/不调阻塞 ③ 突发 vs 分散：3 条 SPI 180μs→1 条 burst 80μs（-55%）
- 推荐：**扩 deep-dive**——中文最系统化的 BLE 功耗实战文，拆"BLE 功耗 3 模式 + ISR 三不原则"

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
