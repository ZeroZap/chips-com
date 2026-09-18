# LoRa / LoRaWAN 候选素材 @ 2026-09-02 00:00

## 协议速览
Sub-GHz 扩频调制 + LoRaWAN MAC 协议栈，远距离低功耗广域网（LPWAN）。与 BLE/Zigbee 互补形成短中长三段覆盖。

## 候选文章（4 条）

### 1. 踩过 LoRaWAN 的坑后，这家工厂把园区网络换成了私网 LoRa
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_3356a8e8e0413252
- 来源：腾讯企鹅号 / 骏晔科技 DreamLNK
- 摘要：精密制造厂老周接手园区智能化第一版选 LoRaWAN——凌晨网络抖动致能耗看板卡 10+ 分钟、NS 升级要开工单一等大半天、500 节点只覆盖两个车间却要为"跨网络接入"持续付费。最后改用私网 LoRa（网关本地解析+边缘盒子），联动从"绕一圈公网"压到秒级。
- 实战点：公网 NS 升级 = 工单等半天运维命脉不可控；小规模园区私网 LoRa 比 LoRaWAN 实在；选型先问数据去哪/谁运维/规模多大
- 推荐动作：**入主题笔记（"选型边界"专章）**

### 2. the LoRa packet that arrived 45 minutes late
- 链接：https://moltbook.com/post/5e59d97b-36ba-456e-bb53-43c48e2a77bf
- 来源：moltbook 实战帖
- 摘要：SX1276+SF12+125kHz 农场部署 bench 一切正常，上线后传感器读数"来自 45 分钟前"。根因不是 RTC 漂移而是邻居 LoRa 设备同频冲突致 ACK 延迟，节点重传逻辑忠实重发老包。修法：丢包前 packet age check > 2 duty cycle 直接丢。
- 实战点：confirmed uplink + 同频冲突 → ACK 延迟 → 节点重传 + 原时间戳 → 数据"穿越"；bench≠field，上线前必做邻居频谱占用勘测
- 推荐动作：**扩 deep-dive（LoRaWAN confirmed frame 死循环）**

### 3. LoRa Network Failure Story: Debugging in the Field
- 链接：https://www.linkedin.com/posts/mashuk-e-lahi_iot-embeddedsystems-fieldengineering-activity-7471360772607021057-nVoH
- 来源：LinkedIn / Mashuk E Lahi（World Bank IoT 项目）
- 摘要：城市空气质量传感器网络 day-1 40 节点全在线，day-2 16 节点沉默。两天系统排查定位 4 个根因：城市 RF 干扰吃掉 60% LoRa 距离、GSM 信号同栋楼地面和顶楼差 3 格、2 个传感器运输温差冲击致校准漂移、1 块 PCB 振动下冷焊点失效。
- 实战点：多模故障并发——RF+蜂窝+传感器校准+硬件焊接 4 维同时炸；"无 Stack Overflow 答案"= 实战
- 推荐动作：**写实战案例（多根因并发故障典型样本）**

### 4. LoRaWAN智能能源项目实战：从选型调优到300节点稳定运行
- 链接：http://www.wmrh.cn/news/1191354
- 来源：尧图网络
- 摘要：300 节点园区能耗管理首日 30 设备入网失败（金属配电箱/RS485 极性反/固件版本老），数据到达率 93%→99.8% 走三步：8 信道均匀分布 + ADR 限 SF 下限 + 网关天线升高 3m 换高增益玻璃钢（86%→99%）。5 条可复用清单：前期勘测/安装规范/网关宁多勿少/平台分层+设备ID+时间戳去重/OTAA+每台唯一密钥。
- 实战点：10% 首日掉线=终端安装+固件版本不是网络层；99.8% 需"业务层 24h 补采"兜底不能只靠 ACK 重传；OTAA+唯一 DevEUI/AppKey 是硬底线
- 推荐动作：**入主题笔记（"300 节点规模"实战模板）**——最完整中文 LoRaWAN 工程复盘

## 下一步
等你 review：激活 / 改写 / 丢弃。4 篇互不重叠，覆盖选型边界/频谱冲突/多根因排查/规模工程化 4 类缺口，建议全收。
