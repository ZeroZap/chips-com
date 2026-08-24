# LoRa / LoRaWAN 候选素材 @ 2026-08-08 00:00

## 协议速览
- 是什么：LoRa 联盟定义的低功耗广域网协议
- 解决什么：km 远距 + 5-10 年电池 + 大容量 IoT 通信
- 跟 L4 关联：水表 / 共享单车 / 农业 / 户外传感首选

## 候选文章（5 条）

### 1. LoRaWAN 帧计数机制及典型问题分析
- 链接：https://blog.csdn.net/iotisan/article/details/109121378
- 来源：CSDN（IoT小能手 twowinter，LoRaWAN 中文译作者）
- 摘要：从 ABP 设备掉线切入，深挖 FCnt 机制三大隐藏 bug：ABP 重启归零、Disable 帧计数校验不灵、FCnt 跨 65535 的 MIC 校验绕过
- 实战点：MAX_FCNT_GAP=16384 边界实测；ChirpStack `SkipFCntValidation` 在 FCnt 超 65535 时隐性 bug；NS 手动配 SessionFCntUp 解决设备 105007 不上报
- 推荐动作：扩 deep-dive（LoRaWAN 帧计数陷阱实战笔记）

### 2. 共享电单车 LoRaWAN 移动场景 ADR 失效
- 链接：https://blog.csdn.net/weixin_30296405/article/details/98211593
- 来源：CSDN
- 摘要：深圳某头部运营商 20km/h 共享电单车终端集体掉线；剖析 ADR 在移动节点 5 类失效：环境稳定性谬误、命令时延陷阱、Class A 窗口限制
- 实战点：实测 1 分钟内 RSSI 波动 6-8dB；18s 延迟设备已移 300m；百万级设备验证的 5 种回退机制
- 推荐动作：写实战案例（移动 IoT 场景 ADR 优化笔记）

### 3. LoRaWAN 智能水表掉线问题处理方法
- 链接：https://www.sohu.com/a/808083022_120468846
- 来源：搜狐（水务行业实战）
- 摘要：水务远程抄表场景 7 大掉线原因排查路径：信号覆盖 / 基站故障 / 参数 / 电池 / 硬件 / 软件固件 / 安全
- 实战点：电池电量隐性排查（LoRa 耗电低，故障常在传感端）；固件 OTA 升级对掉线率影响
- 推荐动作：入主题笔记（IoT 远程抄表 L4 闭环参考）

### 4. 单通道 LoRaWAN 网关项目常见问题解决方案
- 链接：https://blog.csdn.net/gitblog_00600/article/details/143681456
- 来源：GitHub（single_chan_pkt_fwd 镜像 + 实战）
- 摘要：树莓派 + SX1276/SX1278 单通道网关部署三大坑：wiringPi 依赖、配置陷阱、硬件接线
- 实战点：完整引脚对照表（3.3V/GND/MISO/MOSI/SCK/NSS/DIO0/RST）；配置 4 关键项；单通道 vs 8 通道丢包率权衡
- 推荐动作：跳过

### 5. LoRaWAN 网关与常见网络服务器协议
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_053650172d949952
- 来源：企鹅号（LoRaWAN 实战汇总）
- 摘要：网关与 ChirpStack / TTN 之间三层协议：Packet Forwarder、Gateway Bridge、LoRaWAN MAC；含 ABP/OTAA 激活流程
- 实战点：ChirpStack Gateway Bridge 支持 UDP/MQTT 双协议；TTN 设备激活四步（JoinRequest→JoinAccept→DataComm→Security）
- 推荐动作：扩 deep-dive（LoRaWAN 网络架构选型笔记）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
<mavis-progress>idle</mavis-progress>
