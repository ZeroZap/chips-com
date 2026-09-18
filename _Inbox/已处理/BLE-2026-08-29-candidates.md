# BLE / Bluetooth LE 候选素材 @ 2026-08-29 07:17

## 候选（5 条）

### 1. Why does your BLE work in the lab – then fail in production?
- https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/ — DEWINE Labs
- 多款 BLE 模块受控 Wi-Fi 干扰对比，**lab 通过 ≠ 产线能用**——根因不是硬件，是 BLE 固件为消费场景设计
- 实战：① RF 复杂度 lab 复现不了；② 团队错怪硬件→改板浪费数月；③ 间歇性 latency 才是真信号
- → 扩 deep-dive / 写 L4 笔记 "BLE lab vs prod 5 维诊断矩阵"

### 2. TI EXT_EP-11442 — CC2340R5 PHY 切换 Connection Timeout
- https://sir.ext.ti.com/jira/browse/EXT_EP-11442 — TI Jira
- CC2340R5（Peripheral）+ CC2652R1（Central）长稳**反复切 PHY**（1M↔2M↔Coded）偶发 0x08 Timeout，最短 24min；其他 Peripheral 芯片不复现——**芯片级差异**（已修 BLE5-3.2.2）
- 实战：① PHY 切换 BLE 5 高频坑；② 不换 PHY 只 GATT 读写→不复现（隔离法）
- → **入主题笔记**（PHY 切换 long-term 稳定性 = L4 产线级案例）

### 3. STM32WB HCI_HARDWARE_ERROR_EVENT (0x02) 单元差异
- https://community.st.com/topic/show?tid=165647 — ST Community
- 批量 STM32WB 0x02 BlueCore time overrun，**只部分单元**出问题。stack v1.11.0→v1.24.0 + FUS v1.2.0→v2.2.0 后**问题消失**
- 实战：① 同 PCB 同固件"部分单元"= HSE/LSE 精度/RF 匹配/电源边界；② BLE stack 大版本升级直接 fix 产线良率
- → **入主题笔记**（与 #2 一起作"BLE stack 升级解决产线"双案例）

### 4. ESP32-C3 BLE 每 30s 掉线，凶手是 mDNS
- https://moltbook.com/post/9ab7ff6d-7e73-4f5e-b65d-e891a0f23edf — moltbook 工程师实战 post
- ESP32-C3 + NimBLE + 同芯片 WiFi（OTA），mDNS announce 抢 2.4GHz 时隙，BLE connection event 6 次 miss → supervision timeout → ~30s 准时断
- 实战：① 单 2.4GHz 射频（WiFi+BLE）coex 是 ESP32 核心坑；② BLE 日志只 0x08，**不告诉你 coex**；③ 三参数组合修复：sup_timeout=4s + interval=50ms + `esp_coex_preference_set(ESP_COEX_PREFER_BT)`
- → 扩 deep-dive（**IoT/可穿戴必经坑**，单芯片多 radio 普遍）

### 5. Abbott FreeStyle Libre 3 — FDA Warning Letter + 3M 召回
- https://manufacturingchemist.com/abbott-hit-with-multiple-fda-complaints-warning-letter — Manufacturing Chemist
- 2025-10 FDA 检查 Abbott 厂 4 项 GMP 违规：未传精度、无验收测试、抽样无依据、release 未对齐。**letter 指 BLE connectivity testing 替代了 glucose accuracy 测试**。3M Libre 3/3+ 召回（伪低血糖），Class I，860 重伤 + 7 死
- 实战：① 量产 IoT 医疗的**BLE 验收 ≠ 传感器精度验收**；② iCGM 21 CFR 862.1355 要求端到端精度；③ 设计 transfer + 成品 acceptance + 统计抽样 = 三大失守点
- → **入主题笔记**（最高优——IoT 医疗 + 量产 + BLE 验收三维交叉）

🟢 #2/#3/#5 入主题笔记；🟡 #1/#4 扩 deep-dive；等 review
