# LoRa / LoRaWAN 候选素材 @ 2026-09-08 00:00

## 协议速览
- 是什么：Semtech LoRa 调制 + LoRaWAN MAC 的 LPWAN，国内 470-510 MHz、Class A/B/C。
- 解决什么：电池供电、公里级、小数据量（≤250B/帧）、千级终端/网关的上行主导 IoT。
- 跟 L4 关联：网关/NS 部署、ADR 调优、下行可靠性、FUOTA、占空比与时钟同步——产线稳定运行核心。

## 候选文章（5 条）

1. **基于 LoRaWAN 的智能能源系统实践：从选型到踩坑全记录** — http://www.kwkd.cn/news/79492（拓冰网络）  
   420 节点三个月后 P0 全网延迟/丢失。根因三层：半信道网关并发打满 + ChirpStack PG 连接池溢出 + ADR 把近端全压 SF7 同秒撞车。修：8 通道 SX1302 + NS worker 调优 + 限 ADR 最低 SF9，吞吐涨 4×。  
   实战点：按终态预留网关/NS 余量；ADR 在移动/抖动场景反而致丢；SX1262 接收电流比 SX1276 低 1 数量级；FUOTA 先灰度、Class A↔C 切换省电。  
   **推荐：入主题笔记，可扩「ADR 边界 + 撞车复盘」deep-dive。**

2. **LoRaWAN 智能能源项目实战：300 节点从翻车到稳定** — http://www.wmrh.cn/news/1191354（尧图网络）  
   300 节点首日 10% 掉线。三类根因：金属配电箱内天线衰减（-95→-125 dBm）、RS485 反接、终端固件与网关信道不匹配。8 信道均布 + ADR SF 下限 + 网关天线升高 3m 换玻璃钢，到达率 93%→99.8%。  
   实战点：电池账面 9 年实测 3-5 年；Class A ACK 反增碰撞，业务层补采替代；去重必须「设备 ID+采集时间戳」否则倒序电量；占空比 1% 是 OTA 隐形瓶颈。  
   **推荐：入主题笔记（与 #1 互补，覆盖安装侧 + 数据正确性）。**

3. **LoRaWAN Repeater Fix: SF11+ Broadcasting Issue Solved** — https://talkin.icu/blog/lorawan-repeater-fix-sf11-broadcasting（talkin.icu）  
   pyMC_Repeater 在 SF≥11 时 repeater 不转发。根因 airtime.py 缺 `bandwidth_hz` 参数，低 SF 隐式默认不崩，SF11+ 空气时间精度高直接挂。远端高 SF 设备（农业/地下室/工业死角）整个静默死区，间歇丢包极难发现。  
   实战点：间歇丢包 + SF 升高才出现 = 90% 是配置/脚本边界 bug；ADR 灵活性破坏后运营成本反向增加。  
   **推荐：入主题笔记，可改写「边缘场景静默死区排查清单」。**

4. **踩过 LoRaWAN 的坑后，这家工厂把园区网络换成了私网 LoRa** — https://so.html5.qq.com/page/real/search_news?docid=70000021_3356a8e8e0413252（QQ 浏览器 / DreamLNK 客户案例）  
   精密制造厂老周 LoRaWAN 改造三次翻车：凌晨公网抖动看板卡 10+min、NS 升级开工单等半天、两车间却为"跨网接入"付费。改私网 LoRa（网关本地解析+边缘盒子）后联动秒级、运维自主、加节点零成本。  
   实战点：小规模封闭场景 LoRaWAN 公共 NS 是负资产；选型三问：数据去哪？谁运维？规模多大？  
   **推荐：入主题笔记（难得的"反 LoRaWAN"实战视角）。**

5. **LoRaWAN 通用网关技术拆解：从射频链路到智能门锁** — http://www.wmrh.cn/news/1194406（尧图网络）  
   LEXI 通用网关承载水电表/门锁/烟感三套系统。踩坑：① 下行开门失败 = 占空比锁频点 + NS 队列无重试上限；② 多网关重复上行看似丢包实则 NS 未去重，根因 NTP 未校 + 私有 NS 无 dedup；③ Class A 开门延迟解法 = 定时心跳 + 下行缓存。  
   实战点：边缘规则引擎断网执行关键联动；PoE 网关省弱电井找插座；网关台账必填位置/天线高/固件版本。  
   **推荐：入主题笔记，可扩「LoRaWAN 下行失败模式全景」deep-dive。**

## 下一步
review 后决定：激活（入 L4 LoRaWAN 章节）/ 改写 / 丢弃。5 条均经 web_search 真抓，国产实战（#1 #2 #5）+ 国际开源坑（#3）+ 决策反例（#4）覆盖建设期+运维期+选型期。24h 内未跑 LoRa，符合去重规则。
