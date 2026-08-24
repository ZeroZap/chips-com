# LoRa / LoRaWAN 候选素材 @ 2026-08-10 00:00

## 速览
- 是什么：LoRa Alliance 低功耗广域网协议
- 解决什么：km 距离 + 5-10 年电池 + 大容量 IoT
- L4 关联：水气表/共享电单车/农业/户外传感

## 候选（5 条）

### 1. ESP32+LoRa 上电"抽风"血案
- 链接：https://blog.csdn.net/weixin_30514745/article/details/95472093
- 来源：CSDN（物联网实战）
- 摘要：智能农业项目 ESP32 单测正常，接 LoRa 后频繁重启；冷启动失败、热插拔正常。问题在 ESP32 Strapping 引脚（GPIO0/GPIO2）被 LoRa 接入瞬间拉偏，Bootloader 读错启动模式。
- 实战点：Strapping 上电时序冲突；Flash 读失败错误码；先断 LoRa 上电、连上后正常；硬件初始化是"定时炸弹"
- 动作：扩 deep-dive（ESP32+LoRa 并接时序陷阱）

### 2. SX1278 实战三大坑
- 链接：https://blog.csdn.net/wuhenyouyuyouyu/article/details/102675850
- 来源：CSDN（SX1278 调试）
- 摘要：SX1278 调试 3 大隐蔽问题：LDO 纹波 100mV 与发射频率耦合；打静电后 RSSI 锁死 -164/-155；FSK 长发灌饱和相邻 LoRa 接收机。
- 实战点：电源去耦 + 选大功率 LDO；连续 RSSI 异常自动复位；接收忙加 RSSI 阈值过滤 FSK；V2.1 驱动初始化两次会死机
- 动作：写实战案例（LoRa 射频 EMC 手册）

### 3. 50Ω 阻抗匹配：LoRa 天线避坑
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_0136a5625c262752
- 来源：企鹅号（射频工程）
- 摘要：射频通路偏离 50Ω 就反射。FR4 0.8mm 板线宽 1.7mm 接近 50Ω；天线高度每 +10m 视距 +5.5km。
- 实战点：π 型匹配 + 网络分析仪；增益 1km/2.15dBi、5km/5dBi、15km/7-9dBi；100mW 弹簧/500mW 棒状/2W+ 吸盘；高度 > 增益
- 动作：入主题笔记（LoRa 射频前端速查）

### 4. 纺织工厂 LoRa 振动监测
- 链接：https://www.iotrouter.com/case/229.html
- 来源：纵横智控（工厂案例）
- 摘要：纺织厂 24h 监测纺织机故障，LoRa 节点串口接转速脉冲传感器，集中器 4G MQTT 上云。减 70% 意外停机、降 35% 维护成本、提 10% 生产效率。
- 实战点：LoRa 节点 + 加速度计/陀螺仪/温/声学多传感；4G 上行；事后维修转事先预防
- 动作：扩 deep-dive（LoRa 工业预测性维护）

### 5. E78+E870 搭 LoRaWAN 实操
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_67768c232ef65052
- 来源：企鹅号（E78 节点 + E870 网关）
- 摘要：E870-L470LG12-O 网关 + E78-400TBL-02 节点 CN470 组网，出厂默认启动 ChirpStack，AT 配 DevEUI/AppKey/AppEUI + AT+CCLASS=2 + AT+CJOIN 入网。CLASS C +AT+DTRX 上行、Queue 下行。
- 实战点：CN470 默认 DevEUI/APPKEY 固化；gw.sh/cs.sh 快捷命令；CLASS C RX2 常开功耗 × 数倍；ChirpStack 8080 看日志
- 动作：入主题笔记（LoRaWAN AT 指令流 + ChirpStack 部署）

## 下一步
等你 review：激活 / 改写 / 丢弃
<mavis-progress>idle</mavis-progress>
