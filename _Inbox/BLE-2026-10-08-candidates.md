# BLE 候选素材 @ 2026-10-08 00:00

## 协议速览
- 是什么：蓝牙 4.0+ 的 LE 子集，低功耗短距无线
- 解决什么：纽扣电池 IoT 偶发数据/低带宽连接，与 Wi-Fi 共 2.4 GHz
- 跟 L4 主题的关联：产线配对失败/断连是 BLE 售后头号问题

## 候选文章（5 条）

### 1. BLE System-Level Design Mistakes
- 链接：https://www.eurthtech.com/post/ble-is-not-just-a-protocol-system-level-design-mistakes-engineers-make
- 来源：EurthTech 工程博客
- 摘要：脱敏部署 case——多年稳定产品因 BLE 被视为外设，跌进掉线/电池衰减。列 5 大架构盲区。
- 关键实战点：① prototype 近距 ≠ 现场边缘；② iOS/Android 后台策略改 BLE 行为；③ 半配对/脏 bond 需 factory reset
- 推荐动作：扩 deep-dive

### 2. Smart Dumbbell 12-Model BLE Audit
- 链接：https://telectronichub.com/sports/smart-dumbbell-bluetooth-pairing-issues-troubleshooting-connectivity-that-derails-progressive-overload-tracking
- 来源：telectronichub 评测
- 摘要：2023 年 12 款主流智能哑铃（SelectTech 560X、JAXJOX、iSelect）实测，67% 出现 ≥1 类失败，仅 2 款 BLE 5.2 + 自适应跳频保 99%。
- 关键实战点：① 金属外壳把距离压到 <1.8 m；② 90 s 闲置断连 + 3 s/15 s 广播窗降低发现率
- 推荐动作：写实战案例（消费品量产故障统计）

### 3. BLE Connection Issues Diagnosis Guide
- 链接：https://blefyi.com/tr/guide/ble-connection-issues
- 来源：blefyi 调试指南
- 摘要：三阶段诊断流程（discovery/establishment/maintenance）+ HCI 0x08/0x13/0x14/0x15/0x1A 错误码速查 + MTU/DLE 协商次序。
- 关键实战点：① ADV_NONCONN_IND 被手机 OS 过滤；② iOS bond 缓存，peripheral 新 LTK 静默加密失败；③ Android 12+ 需 BLUETOOTH_CONNECT/SCAN 运行时授权
- 推荐动作：入主题笔记（错误码 + 诊断流程图）

### 4. Dell Pro Headset — LE Audio OTA 后 Dongle 掉配
- 链接：https://www.dell.com/support/kbdoc/zh-cn/000248881/dell-wireless-headset-loses-connection-to-paired-dongle-after-firmware-update?lang=nl
- 来源：Dell 官方 KB
- 摘要：WL3024/WL5024/WL7024 启用 LE Audio 后 dongle 配对丢失，根因地址方案切换。
- 关键实战点：① Classic BT → LE Audio 切换 = 既有 bond 必丢；② 出货产品启用新 codec 前要规划"配对迁移工具"
- 推荐动作：扩 deep-dive（OTA 配对迁移 + Dongle Pairing Tool）

### 5. RTL8762 国产芯片配对失败诊断
- 链接：https://ask.csdn.net/questions/9119395
- 来源：CSDN 工程师问答
- 摘要：RTL8762 国产 Realtek 配对 6 大现象 + SM 配置错误表 + NVDS 脏地址排查 + Mermaid 决策图。
- 关键实战点：① LE Security Mode Level 不匹配直接拒配对；② smp_db_init() 必须 stack 启动前调用；③ NVDS 全 0/全 F = SM 拒绝启动
- 推荐动作：写实战案例（国产芯片 vs Nordic/TI）

## 下一步
等你 review。24h 去重：下次最早 2026-10-09 00:00 后