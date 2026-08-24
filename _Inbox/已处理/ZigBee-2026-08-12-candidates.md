# ZigBee 候选素材 @ 2026-08-12 22:30

## 协议速览
- 是什么：IEEE 802.15.4 低功耗 Mesh 局域网（2.4GHz / 16 通道）
- 解决什么：电池 IoT 节点自组网（智能家居 / 工业 / 表计）
- 跟 L4 主题的关联：无线协议选型与掉线恢复经典样本

## 候选文章（5 条）

### 1. Zigbee 疑难问题定位（三）—— 掉线 + CC2530 坑 + 串网关
- 链接：https://blog.csdn.net/moonlinux20704/article/details/95624716
- 来源：CSDN（工程师复盘）
- 摘要：两类掉线——部分一晚才重连、极少永远自恢复。抓包定位：(a) 重入网被 5s 定时位卡死 (b) CC2530 NLME_ReJoinRequest 概率返错。还有"设备串到别的网关"——flash NV 被污染。
- 关键实战点：
  - `OrphanJoin` → `ReJoin` 在 TI Z-Stack 有 BUG，fallback `ZDO_MultipleJoinReq`
  - 重新入网必须只 join 之前 PAN ID
  - 长期跑换 Silicon Labs EFR32
- 推荐动作：扩 deep-dive

### 2. zigbee 编译 17 个 IAR/CC2530 错误
- 链接：https://blog.csdn.net/halsonhe/article/details/47087729
- 来源：CSDN（error code 实战集）
- 摘要：IAR + Z-Stack 编译 CC2530 的 17 个错误——XDATA 溢出、`__program_start` 找不到、license 失效、烧写 breakpoint 失败。
- 关键实战点：
  - 数组撑爆 XDATA：`unsigned char code shuzi[5100]` 强制 CODE 段
  - IAR 6.0 64 位 Win7 改 `lnk51ew_cc2530F256.xcl` 路径
  - Programmer 只认 release `.hex`
- 推荐动作：入 L4 笔记

### 3. ZigBee 设备典型故障分析与排查（PPT）
- 链接：https://www.docin.com/p-2187907391.html
- 来源：豆丁（产线培训 PPT）
- 摘要：产线 ZigBee 四大故障——电源灯不亮、手机入不了网、红外学习失败、GPRS DTU 不在线。
- 关键实战点：
  - "手机入不了网"= 没开工程调试 + 默认密码 `unisiot654321`
  - 红外学习"灯亮→灭→再亮"瞬间对准遥控器（5cm）
  - DTU 在线灯 = 登录网络才亮
- 推荐动作：入主题笔记

### 4. EWD181-Z20 ZigBee 3.0 工业级网关
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_60868c7b98742252
- 来源：企鹅号（工业 IoT 厂商新品）
- 摘要：ZigBee 3.0 工业网关——ModBus TCP/RTU 自动转换、MQTT 接阿里/华为/OneNET、断网 5s 自愈。-40~+85℃。
- 关键实战点：
  - 实战基线：AES-128、AT+HEX 双指令、485/232 双串口
  - 协议转换在网关内完成
- 推荐动作：跳过（产品 spec 偏营销）

### 5. zigbee2mqtt OTA 不走系统代理
- 链接：https://github.com/Koenkk/zigbee2mqtt/issues/3588
- 来源：GitHub Issue（IoT 隔离网络真实问题）
- 摘要：RasPi 跑 z2m 在 IoT 隔离网段过 squid 代理，系统能正常更新，但 OTA 固件检查**不走代理**超时。
- 关键实战点：
  - z2m OTA 默认不读系统代理环境变量
  - 隔离网段 OTA 是部署"最后一公里"
- 推荐动作：扩 deep-dive

## 下一步
- 优先 #1 #5
- #2 #3 入 L4 笔记
- #4 偏营销可暂搁
