# LoRa / LoRaWAN 候选素材 @ 2026-08-22 00:00

## 协议速览
Semtech CSS 物理层 + LoRaWAN MAC（OTAA/ABP/A/B/C）的 Sub-GHz LPWAN；L4 关联：IoT 户外/表计首选，chirp + 占空比 + ADR 是三大坑

## 候选文章（5 条）

### 1. Resolving LoRaWAN Join-Storms · 商业案例
- 链接：https://www.concept13.co.uk/news/lorawan-join-storm/
- 来源：Concept13
- 摘要：欧洲物业数千节点+几台网关 → 1/5 节点日重 join、丢包 80%。根因 = 共享 AppKey + 网关各自当 LNS（Islands）+ Node Red 抢占；25 项整改最关键是迁集中云 LNS。
- 要点：Join Storm 自激；Gateway-as-LNS 同空间互抢；先砍根因再修边角
- 动作：实战案例 + deep-dive（Join Storm + ADR 抗振荡）

### 2. 14 LoRaWAN Common Pitfalls · 调试方法论
- 链接：https://iotclass.org/lorawan/lorawan-common-pitfalls.html
- 来源：IoTClass
- 摘要：从症状反推 14 类坑（missing uplinks / rejected frames / missed downlinks / release surprises），核心"symptom → evidence gap → correction → 复检条件"四件套 review rule。
- 要点：60 设备 × 4 上行/h = 240/h 基线，弱 SF 触顶占空比；ADR 启用无后继 = 失效
- 动作：deep-dive（ADR 工程化 / payload / 复检 SOP），L4 release evidence 范例

### 3. LoRaWAN Communication Debug · 14 步 checklist
- 链接：https://wiki.dragino.com/docs/Configuration/end-node/lorawan-debug
- 来源：Dragino Wiki
- 摘要：14 个生产故障 SOP：OTAA sub-band 不匹配（US915/AU915/CN470 8 个）、ABP Frame Counter 重启归零、payload 0x00（MAC 拆分）、MIC Mismatch（AppKey 误填 APPSKEY）、32MHz ppm 漂移致 LDRO 失效。
- 要点：US915 默认 8/16 信道 ≠ TTN 全 72 频；MIC Mismatch 90% = AppKey 误填 APPSKEY
- 动作：实战案例（对照表 + AT 速查），入量产排错

### 4. LoRa 低功耗三大设计陷阱 · 2000 节点年实测
- 链接：https://aiot.csdn.net/69fb2d0354b52172bc720e3e.html
- 来源：CSDN aiot
- 摘要：3 年实地：Class A 41% 时间漂移（32MHz 晶振 ±234ppm，唤醒 >2h 累积超窗口）、38% 首包失败；"伪发送成功"= SX1262 射频储能 <15ms。给两级储能 + rampTime + GPS 驯服。
- 要点：载荷 50B+ 必须预热 ≥15ms；唤醒 >2h 必须 TCXO；Class B 卡死 31% > Class A 17%
- 动作：deep-dive（SX126x rampTime + Class + TCXO）

### 5. LoRa 深层解构 · 物理层 + 三个翻车坑
- 链接：http://lfdjt.com/info_32_7953.html
- 来源：廊坊大讲堂
- 摘要：chirp 物理 + EU 868 占空比 1% 下 SF12/125kHz 单报 1.3s 直接限流 + 三坑：天线金属腔失效、SF 正交仅同步完美时成立、ADR 振荡（移动遮挡 SF7↔SF12 横跳）。
- 要点：SF 迷信 = 触法；3000 水表凌晨拥塞 = 晶振漂移 + 纯 ALOHA；ADR 迟滞补丁降抖动 80%
- 动作：deep-dive（chirp + 占空比 + ADR）

## 下一步
review：激活 / 改写 / 丢弃（_Inbox 仅此文件，未动 bus/basic/TOPIC_MATRIX.md）
