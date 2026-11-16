# LoRa / LoRaWAN 候选素材 @ 2026-10-07 12:01

## 协议速览
- 是什么：1GHz 以下免授权 LPWAN，Chirp 扩频
- 解决什么：电池节点公里级通信、私有自建网关
- L4 关联：IoT/可穿戴远距低功耗主力；实战 = 现场 ≠ 实验室

## 候选文章（3 条）

### 1. LoRaWAN工业温控器从代码到量产
- 链接：http://www.rrmt.cn/news/96507
- 来源：荣润铭拓（国产技术博客）
- 摘要：LoRaWAN 工业温控器样机到小批量交付大半年实战。Class A/C 选型、FreeRTOS 任务拆分、TLV 帧格式、EEPROM 双备份、产测网隔离、两点校准。
- 实战点：
  1. 服务器把 Class C 配成 Class A → 下行延迟 10 分钟
  2. 继电器/可控硅开关瞬间干扰 RX1 → 必须做"通信保护窗口"
  3. 产测网与正式网必须隔离，否则量产设备 Join 进客户生产网
  4. "办公室正常、厂房失败" = 默认信道列表没跟现场网关对齐
- 推荐动作：**入主题笔记**（deep-dive 主源，最完整工业级实战）

### 2. Resolving LoRaWAN Downlinks Scheduled But Not Sent
- 链接：https://industrialmonitordirect.com/de/blogs/knowledgebase/troubleshooting-lorawan-downlinks-scheduled-but-not-sent
- 来源：Industrial Monitor Direct
- 摘要：下行"已排队但未下发"4 类故障域（encoder / NS scheduler / 单通道 forwarder / RX2 错配）+ Root Cause 矩阵 + MQTT 诊断。
- 实战点：
  1. encoder 抛异常 → 控制台 UI 仍显示 "scheduled"（异步静默失败）
  2. 单通道 forwarder（ESP32 LoRa32）TTN 不支持 → 8 通道 + SF7-SF12 合规底线
  3. RX2 频率/速率与区域 spec 不匹配 → RX1 OK RX2 never
  4. Class A + 上行 10 分钟 = 下行被动跟随；调试时强制 Class C
- 推荐动作：**写实战案例**（4 类故障域 + MQTT 诊断脚本可复用）

### 3. Troubleshooting Common LoRaWAN Gateway Issues
- 链接：https://www.uniconvergetech.in/blog/troubleshooting-lorawan-gateway-issues/
- 来源：Uniconverge Technologies（印度 IIoT 集成商）
- 摘要：网关运维 + 5 网关农场土壤监测真案：1 个网关每隔几小时 offline 又自愈。
- 实战点：
  1. **真凶是 EMI**：网关与灌溉泵共电源 → 泵启停 EMI + 电压跌落 → 网关崩溃重启（"幽灵问题"远程难定位）
  2. RSSI/SNR 是预测性维护关键指标（-110 dBm 弱，SNR 负值噪声压制）
  3. Wireshark 抓包过滤网关 UDP 端口定位 gateway↔NS 链路
  4. 多网关冗余 + NS 自动去重是终极方案
- 推荐动作：**写实战案例**（"EMI 诱发网关 reboot"是 L4 经典反模式彩蛋）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃