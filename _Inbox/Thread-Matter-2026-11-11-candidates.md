# Thread / Matter 候选素材 @ 2026-11-11 23:38

## 协议速览
- 是什么 / 解决什么：Thread = IPv6 低功耗 802.15.4 mesh，承载 Matter 应用
- 跟 L4 主题的关联：thread-*/matter-* 各 5 篇、FC 仅 9/8 例；本轮视角：排障 + 量产 + 共存

## 候选文章（5 条）

### 1. Diagnosing Thread BR Handshake Failures (Matter 1.4 Multi-Admin)
- 链接：https://larphof.de/?p=21658
- 来源：larphof.de / CRM Academy
- 摘要：BR 握手诊断：180ms 被 IPv6 ND 拖成 30s 超时。
- 关键实战点：
  ① EFR32MG24 每 fabric 槽 1,140 B NVS，上限 5
  ② RA Lifetime=0 → 主机 1800s 后丢前缀路由
  ③ `ip -6 neigh show` STALE >20s 即丢包
- 推荐动作：扩 deep-dive → thread-deep-dive.md 补 ND 排障

### 2. OpenThread BR 设备无法加入 Thread 网络,常见原因有哪些?
- 链接：https://ask.csdn.net/questions/9471013
- 来源：CSDN 问答
- 摘要：BR「静默不入网」八层定位法：ot-ctl → Wireshark。
- 关键实战点：
  ① otIp6SetEnabled 须先于 otThreadSetEnabled，否则无 fd 前缀
  ② CoAP 超时根因常是 RTC 漂移 >500ppm
  ③ forwarding=1、proxy_ndp=1、ip6tables 放行 wpan0↔eth0
- 推荐动作：写实战案例 → thread-failure-cases.md 补 4 例

### 3. ESP32-C6 开发 Matter 设备全指南：架构、环境与踩坑实录
- 链接：http://www.xxmr.cn/news/160937
- 来源：xxmr.cn 工程师原创
- 摘要：单核 RISC-V 160MHz 跑 Matter 落地记录，聚焦分区表/OTA。
- 关键实战点：
  ① OTA 改 nvs 分区 → Fabric 被顶掉，显示未配网
  ② Flash 加密开发模式漏切发布模式，量产被打回
  ③ BLE 配网卡「连接路由器」= AP 隔离/组播过滤
- 推荐动作：入主题笔记 → matter-practical.md 补分区表段

### 4. ESP32-C6 双频组网实测：WiFi6 与 802.15.4 共存抗干扰
- 链接：https://aiot.csdn.net/69e58a540a2f6a37c5a0f9f1.html
- 来源：CSDN AI硬件社区（实测表 + 产线指标）
- 摘要：单 WiFi6 78.2Mbps/0.1% 丢包，双模并发 41.5Mbps/12.4%。
- 关键实战点：
  ① 退避增 3-5 倍、LNA 饱和 15%、缓存溢出 200+/分
  ② 时分调度 7:3 拉回 67.8Mbps、CPU 负载 65%
  ③ 天线间距 ≥31.25mm、净空 ≥3mm；产线并发 ≥65Mbps
- 推荐动作：扩 deep-dive → matter-deep-dive.md 补共存指标

### 5. Matter commissioning on an ESP32: what happens during pairing?
- 链接：https://www.theengineeringprojects.com/forum/discussion/matter-commissioning-on-an-esp32-fails-or-times-out-what-actually-happens-during-pairing
- 来源：The Engineering Projects 论坛
- 摘要：配网拆五阶段定位失败点，多落在 stage 5。
- 关键实战点：
  ① BLE 发现 → PASE → attestation → credentials → DNS-SD + CASE
  ② VID 0xFFF1-0xFFF4、passcode 20202021、disc 3840
  ③ 多板同凭据会认错设备；配网窗口仅 15 分钟
- 推荐动作：写实战案例 → matter-failure-cases.md 补 4 例

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
