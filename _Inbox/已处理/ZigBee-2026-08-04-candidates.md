# ZigBee 候选素材 @ 2026-08-04 00:00

## 速览
- 是什么：IEEE 802.15.4 低功耗 Mesh，2.4 GHz / ≤250 kbps
- 解决什么：多节点稳定组网 + 长电池寿命
- L4 关联：IoT/可穿戴 ✅ 优先

## 候选文章（5 条）

### 1. Zigbee 损坏原因分析（广州致远电子产线案例）
- 链接：https://wenku.suwen.cn/p-567039.html
- 来源：大厂产线故障分析
- 摘要：Zigbee 模块产线失效，定位 3.3V LDO 输入电压应力过低（5V 轨经继电器/互感器浪涌耦合），最终烧毁。
- 实战点：浪涌路径 1=AC→5V→LDO；路径 2=继电器反灌；修复=TVS+共模电感+改 LM1117
- 推荐：扩 deep-dive（产线 EMC/浪涌设计）

### 2. zigbee 模块常见故障分析（才茂 CM210 工业级）
- 链接：https://jingyan.baidu.com/article/2fb0ba4053015a00f2ec5f1e.html
- 来源：工业 Zigbee 厂商 FAQ
- 摘要：4 类典型故障：电源灯不亮 / 配置态进不去 / 终端路由灯不亮 / 收不到数据；每类有明确排查路径。
- 实战点：进配置态需 38400-8-N-1 无流控+按 S 键；CAIMORE 模式必须 HEX 发送；PANID 不一致是入网失败 #1
- 推荐：写实战案例（Zigbee 现场调试 SOP）

### 3. ZigBee 技术问答 30+ 题（CC2530/Z-Stack 实战集）
- 链接：https://blog.csdn.net/NBE999/article/details/70858271
- 来源：CSDN 老帖（中文 ZigBee 社区高频问题）
- 摘要：30+ 真实工程问答：协调器断电→短地址变化/PANID 漂移、CC2530 P0_4 硬件 bug、休眠唤醒高功耗、Z-Stack 版本差异、ZigBee 认证流程（CESI/TRAC）。
- 实战点：NV_RESTORE 开启后 PANID 锁死→需 zgWriteStartupOptions 清；CC2530 P0_4 有硬件 bug；End Device 改 Beacon 周期改 zgDefaultStartingScanDuration；协调器断电后终端在 ORPHAN 回调里强制复位
- 推荐：入主题笔记（最有价值的实战集合）

### 4. zigbee 终端无法重连问题解决
- 链接：https://www.cnblogs.com/yelin/archive/2016/11/11.html
- 来源：博客园 Z-Stack 实战笔记
- 摘要：终端掉线两种主因（信号差 / 协调器重启），掉线后进 ZDO_SyncIndicationCB 回调；给出完整重连流程。
- 实战点：ORPHAN 状态判断；协调器重启导致 PANID 变化→终端找原 ID 失败
- 推荐：入主题笔记（与 #3 互补，代码层更细）

### 5. WSN 节点晶振：IEEE 802.15.4/ZigBee 时钟方案（含 FAQ）
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_9076a20d02873752
- 来源：晶振厂商技术 blog（晶友嘉）
- 摘要：从晶振视角看 ZigBee 实战：16 MHz RF ±25 ppm 决定入网、32.768 kHz RTC 决定电池寿命、温区对起振时间影响、RF/RTC 时钟隔离布局。
- 实战点：综合频偏 <±40 ppm；排查入网失败先看 LQI，<100 才查晶振；低温起振 >5ms 偶发死机→固件等 10ms；协调器需 ±15 ppm 可选 TCXO
- 推荐：扩 deep-dive（ZigBee 硬件设计：从晶振/Layout 看可靠性）

## 下一步
review 后决定：激活 / 改写 / 丢弃
