# BLE/Bluetooth LE 候选素材 @ 2026-09-30 12:00

## 协议速览
- 是什么：2.4 GHz 低功耗短距无线（GATT/ATT 协议栈）
- L4 关联：「实验室 OK 一上线就掉」是 BLE 实战最高频命题（IoT/可穿戴方向尤突出）

## 候选文章（5 条）

### 1. 正基 AP6XXX 蓝牙调试全流程（HCI→产线射频）
- 链接：https://blog.csdn.net/weixin_31476015/article/details/164415722
- 来源：CSDN 工程师实战
- 摘要：HCI 验证 + 产线射频指标（信令/非信令）+ 5 个排查实录 + 自动化烧录脚本
- 实战点：①WiFi+BT 双模天线 BT_ACTIVE 与 WLAN_ACTIVE 配错周期性中断；②UART 3M 波特率不匹配 HCI 无响应；③固件版本混用（AD/AE）致射频指标异常不自知
- 推荐：扩 deep-dive（产线 RF 认证 + 双天线切换）

### 2. Zebra DS3678 西门子 PLC 集成断连修复
- 链接：https://industrialmonitordirect.com/zh-hans/blogs/knowledgebase/zebra-ds3678-stb3678-bluetooth-disconnection-industrial-fix
- 来源：Industrial Monitor Direct
- 摘要：四声蜂鸣断连根因在蓝牙层（非 Ethernet/IP）；123Scan 升级两端固件 + BTTIMEOUT 提高 + HID 应急备份
- 实战点：①EA3600→CP443-1 PLC，CP_CNTRL 无效因根因在配对层；②BTTIMEOUT（参数 623）拉高+PLC 主动查询；③HID 模式直连 HMI 应急
- 推荐：入主题笔记（工业 BLE 集成 + PLC 网关降级）

### 3. 斑马 LI4278 扫描枪产线断连排查（汽车零部件厂）
- 链接：http://www.xyschina.net/index.php?c=show&id=2604
- 来源：旭悦升科技（产线售后）
- 摘要：中午罢工扫描枪，根因是「断开超时 30s」+旧配对占底座槽位；三步调参恢复稳定
- 实战点：①省电策略是工业连续场景最大敌人（停线损失>>电池成本）；②底座只允 1 把枪配对，旧配对占槽位必须清理
- 推荐：扩 deep-dive（BLE 产线参数 + 省电策略权衡）

### 4. BLE5.2 1 主 10 从工厂传感器频繁断连案例
- 链接：https://www.dunling.com/17108.html
- 来源：盾灵导航（中文实战手册）
- 摘要：1 主 10 从 BLE5.2 工厂环境频繁断连/丢数据；连接建立从 7s 优化到 800ms
- 实战点：①多从机 BLE 工厂网络稳定性实战；②CI/SL/Supervision Timeout 调优；③工业频段拥塞致 Channel Map 频繁重协商
- 推荐：扩 deep-dive（多从机 BLE + 工厂 EMI + 连接参数）

### 5. 信号完整性视角重构 BLE 连接（工业跳频实战）
- 链接：https://tsight.io/articles/15176126?lang=zh
- 来源：tsight.io（信号完整性博客）
- 摘要：Ellisys 抓包解读 MIC Failure / Channel Map Update 延迟 / T_IFS 偏差；4 类系统集成优化
- 实战点：①ACK 优先级错排导致高频干扰下直接释放链路；②金属反射→PHY CRC 错误→必须 RF 地单点接地；③T_IFS 微偏差是断连元凶
- 推荐：入主题笔记（BLE 信号完整性 + 跳频 + Channel Map）

## 下一步
等你 review 决定：激活 / 改写 / 丢弃。优先级 1>3>2>4>5。