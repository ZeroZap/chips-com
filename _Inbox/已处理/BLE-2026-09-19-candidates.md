# BLE / Bluetooth LE 候选素材 @ 2026-09-19 00:00

## 协议速览
- 是什么：2.4 GHz 低功耗短距无线协议，嵌入式 IoT/可穿戴主选
- 解决什么：纽扣电池级设备数据上报与控制链路
- L4 关联：射频实测 / GATT 属性表 / 产线掉线重连 / 与 Wi-Fi 共存

## 候选文章（5 条）

### 1. Why does your BLE work in the lab – then fail in production?
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：Dewine Labs 独立测试机构
- 摘要：实验室 vs 产线环境差异 + 多款 BLE 模块在受控 Wi-Fi 干扰下的实测数据
- 实战点：① 产线断连常是协议假设偏差非硬件；② 延迟与邻频 Wi-Fi 强相关
- 推荐：**扩 deep-dive**

### 2. 蓝牙无法连接外设：工业场景排查方案
- 链接：https://gutab.cn/news_industrial/899.html
- 来源：合亿 Gutab 工业平板方案商
- 摘要：射频物理层 / GAP-GATT / 电源管理 / 固件驱动 四维度工业级 SOP，覆盖天线驻波比、AFH 跳频映射、电源纹波、HCI 缓冲区溢出
- 实战点：① "物理-协议-应用"立体思维；② 蓝牙发射瞬时电流可致 MCU 复位
- 推荐：**入主题笔记**（中文工业 SOP）

### 3. 标签一致性检测系统 BLE 扫码枪接入实录
- 链接：https://sknp.top/posts/label-check-system-ble
- 来源：SKNP 个人博客（车间现场实测）
- 摘要：树莓派 3B + bleak + BlueZ 双扫码枪 7×24 长连接；8 类真实踩坑：SIGKILL 假连接、双枪 InProgress、Notify 分包截断、3 档退避
- 实战点：① 单 HCI 适配器必串行化握手；② "首帧 Notify"判定连接可用；③ SIGKILL 后必清残留
- 推荐：**扩 deep-dive**（BLE"工业现场"主轴）

### 4. BLE Data Integrity Failures — Nordic 官方 DevZone
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/125365/ble-data-integrity-failures-out-of-order-segments
- 来源：Nordic 官方 DevZone 真实工单
- 摘要：nRF52840 BLE→Wi-Fi 桥 800KB 传输出现包乱序（A1,A2,A2,A4）。官方明确"BLE fully acked 不可能跳过 A3"，怀疑 GATT 回调 buffer 指针受 Wi-Fi 干扰污染
- 实战点：① 异常先抓 sniffer log；② 串口 log 无硬件流控不可信；③ BLE+Wi-Fi 并发 buffer pointer corruption 真实风险
- 推荐：**入主题笔记**

### 5. 基于 Frontline 的 BLE 物理层时序异常诊断
- 链接：https://tsight.io/articles/19771077?lang=zh
- 来源：TrueSight 技术博客
- 摘要：BLE 5.x 2Mbps PHY 高吞吐场景下用 Frontline X240 做 μs 级时序还原，覆盖 T_IFS 偏移 / Anchor Point 漂移 / Connection Param Update 失败 / L2CAP 静默丢包
- 实战点：① 物理层时钟漂移根因常是晶振 ppm 超补偿；② 非 credit-based L2CAP 溢出即静默丢
- 推荐：**扩 deep-dive**（"高吞吐/物理层"子节）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃