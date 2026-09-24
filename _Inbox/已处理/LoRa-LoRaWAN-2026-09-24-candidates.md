# LoRa / LoRaWAN 候选素材 @ 2026-09-24 11:12

## 协议速览
- 是什么：sub-GHz 扩频 LPWAN，节点电池数年
- 解决什么：km 级远距/低速率/深穿透工业传感回传
- 跟 L4 关联：IoT/可穿戴低功耗远距离主力

## 候选（5 条）

### 1. Resolving LoRaWAN Join-Storms | Case study
- 链接：https://www.concept13.co.uk/news/lorawan-join-storm/
- 来源：Concept13（英国方案商，欧企设施管理真实案例）
- 摘要：欧洲设施管理部署，几千传感器挤一栋小楼+几个网关，每日 1/5 节点 join，丢包严重，硬件投入数十万英镑失败
- 实战点：join-storm（反复入网+duty cycle 耗尽+RX1/RX2 漏接）；配置错（DevEUI/AppKey）级联放大；"配置基线+流量画像"诊断
- 推荐：**扩 deep-dive**（几千节点真实故障，深度匹配 L4）

### 2. LoRaWAN Gateway Duty Cycle Lock-up in EU868
- 链接：https://tech-champion.com/computer-networks/lorawan-gateway-duty-cycle-lock-up-in-eu868-causes-and-fixes
- 来源：Tech Champion（个人博客，含可运行脚本）
- 摘要：EU868 1% duty cycle 触发后网关 HAL `lgw_send failed` 永久 Busy 锁死；Python 日志解析+注入高下行流量复现
- 实战点：监管引擎 Wait→Busy 不可逆锁死根因；tshark 批量定位"突发下行后立刻报错"
- 推荐：**写实战案例**（含代码）

### 3. 深度排障笔记：工业环境 LoRaWAN 链路失效的非线性物理根因
- 链接：https://tsight.io/articles/13242120?lang=zh
- 来源：TrueSight（中文，物理层排障）
- 摘要：多径/时间同步漂移/天线极化三维度复盘；冷库 EM300-TH 挂上铁门后 -110dBm → -120dBm
- 实战点：金属格栅门+电机+钢缆桥架多径；"空旷 km"在反射环境失效；时间同步对双向窗隐性影响
- 推荐：**入主题笔记**（中文+物理层，IoT 互补）

### 4. LoRaWAN 智能电表项目实战：选型到 100 节点稳定运行
- 链接：http://www.hqwc.cn/news/1392472.html
- 来源：hqwc.cn（智能电网站点）
- 摘要：30+ 栋楼电表/水表/空调/温湿度统一接入 LoRaWAN，对比 Wi-Fi/NB-IoT/Zigbee 后定 LoRaWAN
- 实战点：300 节点"散列 ID 随机化"防碰撞；电源踩坑（LoRa 发射拉低 3.3V 干扰计量 ADC，钽电容+Layout 分割）；精简 MAC Payload 取代 DL/T 645
- 推荐：**扩 deep-dive**（硬件电源设计踩坑，IoT 稀缺实战）

### 5. LoRaWAN 数据包分析实战：空中抓包到 Wireshark 故障排查
- 链接：http://www.wmrh.cn/news/11388
- 来源：wmrh.cn（无线/物联网站）
- 摘要："不亲自看一眼空中原始数据包排查永远都在猜"。五件套（空中帧+负载+MIC+时间戳+duty cycle），含 Join Request 三次重试案例
- 实战点：入网失败根因（DevEUI/AppKey、RX 窗口下行、ABP session 残留）；tshark 全量帧回放验收
- 推荐：**入主题笔记**（LoRaWAN 调试手册，可作 L4"协议分析"方法论）

## 下一步
等你 review：激活 / 改写 / 丢弃