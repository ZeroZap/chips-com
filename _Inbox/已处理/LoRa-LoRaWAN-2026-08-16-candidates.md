# LoRa / LoRaWAN 候选素材 @ 2026-08-16 12:00

## 协议速览
- 是什么：Sub-1GHz LoRa 调制的 LPWAN，节点-网关-NS 三层星型
- 解决什么：电池终端 km 级低速率上行（表计/资产追踪/园区）
- 跟 L4 关联：频偏/入网/天线/功耗四大坑全是"产线一跑就翻车"型

## 候选文章（5 条）

### 1. 浅谈 LoRaWAN 调试心得（多频段产线实录）
- 链接：https://blog.csdn.net/zhufeng88/article/details/76651858
- 来源：CSDN（CLAA 中兴基站一线工程师）
- 摘要：跑过 470/433/868/915 四频段。晶振旁匹配电容选错使发射频率比频谱仪高 0.1MHz，ABP 直连不上；DR4 以上 BW 默认 500K 而基站 125K，致 915 上行 OK 下行断。
- 关键点：① 频偏 0.1M=加不上网 ② ABP 绕开 Join 调 ③ 上下行 BW 必须对齐 ④ 频谱仪必备
- 推荐：扩 deep-dive（频偏定位 + 寄存器 0x06/0x07 校准）

### 2. 50Ω 阻抗匹配：LoRa 天线调试避坑
- 链接：https://so.html5.qq.com/page/real/search_news?docid=70000021_0136a5625c262752
- 来源：企鹅号（射频实战）
- 摘要：π 型 LC 匹配电路；FR4 板材微带线宽 1.7mm（双面板 0.8mm）；天线每升 10m 视距+5.5km。
- 关键点：① 25mil 线宽<20mm 可接受 ② 增益 3dB 翻倍但波束收窄 ③ 频段误配>增益误判
- 推荐：入主题笔记（L4「射频前端」补充）

### 3. LoRaWAN 同频 vs 异频 + CN470 避坑
- 链接：https://blog.csdn.net/weixin_27697385/article/details/160646632
- 来源：CSDN
- 摘要：网关灯正常、节点回 Join Accept 但数据传不上去——根因是 RX1/RX2 同频（AT+BAND=7）/异频（AT+BAND=8）配错。CN470 频段宽 470-510MHz，节点随机信道易撞不同子带。
- 关键点：① 同频小网络/私部署 ② 异频是联盟推荐 ③ CN470 子带规划是国产第一关
- 推荐：扩 deep-dive（CN470 频段计划+8 通道子带映射表）

### 4. LoRaWAN 入网失败全攻略（利尔达 WB25 OTAA/ABP）
- 链接：https://blog.csdn.net/weixin_26899659/article/details/160848329
- 来源：CSDN（模组厂背景）
- 摘要：以利尔达 WB25 拆 OTAA/ABP 差异。AppKey 烧录、Join Accept 加密、DevNonce 防重放。给"Join Failed"排错清单。
- 关键点：① OTAA 走 AppKey 加密 ② ABP 跳 Join 但需手管 FCnt ③ AT+APPEUI/APPKEY 顺序
- 推荐：写实战案例（入网失败→逐项排查→恢复时间线）

### 5. LoRaWAN stack 移植笔记（五）· STM32L151→L051
- 链接：https://www.cnblogs.com/answerinthewind/p/6272349.html
- 来源：博客园（LoRaMac-node 移植实战）
- 摘要：移植到 L051C8T6 踩四坑——JLink SWD 选错；BOOT0 悬空不进入 main；RTC 局部变量失效（改全局解决，根因未明）；M3/M0 GPIO 中断入口差异致 Default_handler 死循环。
- 关键点：① BOOT0 必须接地 ② RTC 变量作用域坑 ③ M0/M3 中断向量需改
- 推荐：入主题笔记（L4「MCU 移植」补充）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
