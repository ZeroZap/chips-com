# ZigBee 候选素材 @ 2026-08-14 23:34

## 协议速览
- 是什么：IEEE 802.15.4 低功耗 Mesh 短距无线协议（2.4GHz/250kbps）
- 解决什么：IoT 大量低带宽节点（传感器/开关/灯）可靠组网与互操作
- 跟 L4 主题关联：IoT/可穿戴核心协议，产线老化、Mesh 掉线、commissioning 失败是真实痛点

## 候选（5 条）

### 1. 彻底解决 Zigbee2MQTT 连接中断
- 链接：https://blog.csdn.net/gitblog_01142/article/details/151414103
- 来源：CSDN 2025
- 摘要：拆解 7 大连接中断根因（USB/MQTT/干扰/兼容/资源/配置/版本），每条配症状+方案+代码
- 实战点：USB 屏蔽延长线+autoReconnect；协调器离 Wi-Fi/微波炉 1m+；networkmap 看 LQI；Docker 部署；availability 超时
- 推荐：**扩 deep-dive**（Mesh 自愈+LQI+干扰隔离可单写一篇）

### 2. Zigbee 照明产品产测流程（免开发）
- 链接：https://developer.tuya.com/cn/docs/iot/Zigbee-light?id=Kbyymu8ytier1
- 来源：涂鸦开发者平台 2024-03
- 摘要：免开发 Zigbee 灯具产测 SOP：老化前 1 次 + 老化后可重复，含信标产测、模组通信测试
- 实战点：老化前后分段工艺；信标产测进入条件；只有"新产测流程"固件才能做可重复老化后测试——固件选型决定产线能否闭环
- 推荐：**写实战案例**（产测流程可移植到 BLE/LoRa）

### 3. 小米多模网关 zigbee 设备全部掉线
- 链接：https://blog.csdn.net/weixin_33279554/article/details/112732147
- 来源：CSDN 用户真实吐槽 2020-12
- 摘要：两小米多模网关每周旗下 zigbee 全掉线，必须插拔电源；米家反馈无回复；两网关不同步掉线
- 实战点：网关级整体掉线 vs 单设备掉线的定位思路；网关 watchdog 失效场景
- 推荐：**入主题笔记**（"ZigBee 网关死机/全网掉线"故障类型归档）

### 4. 生产车间 Zigbee 网络可靠性评估方法
- 链接：https://www.docin.com/p-2281079227.html
- 来源：东南大学硕士论文 2019（54 页）
- 摘要：家电检测车间实测，量化机械遮挡/Wi-Fi 蓝牙/电磁脉冲对丢包率/时延/RSSI 的影响；AHP+模糊综合评判模型
- 实战点：车间三大干扰源定量分析；丢包率+时延+RSSI 三指标；mesh 拓扑车间选型依据
- 推荐：**入主题笔记**（"工业 ZigBee 可靠性评估"实战参考）

### 5. Zigbee 掉线问题排查步骤
- 链接：https://www.docin.com/p-1056855976.html
- 来源：winertech 厂商排查手册 2015
- 摘要：4 步定位掉线：①移动超距 ②障碍物/钢铁屏蔽 ③本地地址冲突 ④电源不足
- 实战点：地址冲突→反复重连特征；电源不足→通信模块隐性故障；外协快速排查 checklist
- 推荐：**入主题笔记**（"ZigBee 现场 4 步排查"短清单）

## 下一步
等你 review。优先 1（Mesh 实战）+ 2（产线），3/4/5 归档故障案例库。
