# BLE 候选素材 @ 2026-08-15 12:00

## 协议速览
- 是什么：低功耗蓝牙，2.4 GHz 跳频，IoT/可穿戴主流通信
- 解决什么：手机-外设低功耗数据通道（心率/位置/控制指令）
- 跟 L4 主题的关联：IoT/可穿戴的"基础连接层"，实战素材聚焦断连/参数协商/平台兼容性

## 候选文章（5 条）

### 1. BLE 连接异常断开原因深度解析与 0x3E 错误码实战
- 链接：https://blog.csdn.net/pytorch8learner/article/details/155528816
- 来源：CSDN 实战博客
- 摘要：聚焦 0x3E "Connection Failed / Sync Timeout" 错误码。真实案例：智能手环同时采数据+传数据时 CPU 资源不足触发 0x3E；办公 2.4 GHz 噪声比郊区高 20 dB；自定义信道选择算法把工业 IoT 项目连接稳定性提升 50%。
- 关键实战点：
  - 0x3E = 6 个广播事件内未建立连接（含物理层建立后高层协议失败）
  - Android 最多同时 6 个 BLE 外设（资源上限）
  - PCB 天线阻抗匹配+净空区 → 距离提升 30%
- 推荐动作：扩 deep-dive（写"BLE 0x3E 错误码排查手册"实战主题）

### 2. BLE 连接故障排查实战：错误码到诊断修复的完整指南
- 链接：https://blog.csdn.net/weixin_30621959/article/details/98727516
- 来源：CSDN 实战博客
- 摘要：智能手环项目踩坑 0x3B（连接参数不被接受）— 根因是 iOS 默认 7.5 ms 连接间隔 vs Android 默认 20 ms，某国产手机请求 10 ms 间隔但智能锁固件只接受 15 ms+。通过 Wireshark 抓包对比 + 改 gap_params_init() 修复。
- 关键实战点：
  - 0x3B（参数不接）vs 0x08（连接超时）vs 0x05（认证失败）— 三大高频码
  - nRF SDK gap_conn_params_t 正确配置示例
  - iOS / Android 默认连接间隔差异是踩坑重灾区
- 推荐动作：扩 deep-dive + 写入"参数协商"主题笔记

### 3. CC2340R5-Q1 BLE 堆栈 ICall abort 调试案例（TI E2E 论坛）
- 链接：https://e2e.ti.com/support/wireless-connectivity/bluetooth-group/bluetooth/f/bluetooth-forum/1463461/
- 来源：TI 官方 E2E 论坛（机器翻译版）
- 摘要：用户用 CC2340R53 (64KB) 替换 R52 (32KB) 后 BLE 初始化卡在 ICall abort()。根因：旧 SDK 8.10 的 linker 文件不适用于 64KB 部件，需迁移到 8.40 SDK 的 R53 专用项目；定制板无外部天线/PCB 天线也会导致异常。
- 关键实战点：
  - 芯片变体（RAM 容量）必须配套迁移 linker / SDK
  - EVM 板正常 ≠ 定制板正常（天线/RF 布局差异）
  - TI 官方工程师实战回复流程：复现 → 假设 → 验证 → SDK 升级
- 推荐动作：写实战案例（CC2340 平台"换芯片变体必看"清单）

### 4. Android BLE 断线重连 status=133 解决方案
- 链接：https://blog.csdn.net/biandang6/article/details/115386388
- 来源：CSDN 实战博客
- 摘要：开关蓝牙后自动重连失败，日志报 `onClientConnectionState() - status=133`。根因：GATT 资源未及时释放 + 缺少重连前扫描。修复模式：disconnect + close + nullify + Thread.sleep(500) + startLeScan 后再 connectGatt。
- 关键实战点：
  - status=133 = GATT 资源未释放的典型信号
  - 重连前必须先扫描（即使已经知道 MAC）
  - 关闭扫描避免资源浪费（连接成功后 stopLeScan）
- 推荐动作：入主题笔记（"Android BLE 资源生命周期"）

### 5. 华为机型 BLE 连接成功但不回调 discoverServices
- 链接：https://blog.csdn.net/qq_27465321/article/details/90544504
- 来源：CSDN 实战博客
- 摘要：连接已建立、广播显示成功，但 discoverServices() 不回调。解法：在 connectGatt 后手动调用 `mBluetoothGatt.connect()` 触发真正建链，再 `discoverServices()`。平台碎片化典型案例。
- 关键实战点：
  - 部分 Android 机型 connectGatt 不会真正建链，需手动补一次 connect()
  - discoverServices 必须在连接回调内触发，跨线程/延时不靠谱
  - 华为/小米/OPPO 在 GATT 行为上各有差异
- 推荐动作：入主题笔记（"国产手机 BLE GATT 兼容性踩坑"）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
- 候选 1+2 适合扩 deep-dive（错误码专题）
- 候选 3 适合做"换芯片变体"实战案例
- 候选 4+5 适合入主题笔记（Android BLE 资源/兼容性）
