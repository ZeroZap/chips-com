# ZigBee 候选素材 @ 2026-08-11 00:00

## 速览
- 是什么：IEEE 802.15.4 + 联盟自组网 Mesh，2.4 GHz 免执照
- 解决什么：低功耗（电池年）+ Mesh 自愈（百节点）+ 工业/家居/集抄
- L4 关联：智能家居/工业传感/电表集抄/楼宇（与 BLE 互补）

## 候选（5 条）

### 1. 致远电子 ZigBee 损坏产线案例
- 链接：https://wenku.suwen.cn/p-567039.html
- 来源：致远电子（产线实战）
- 摘要：四路 ZigBee 模块批量烧板。失效根因：AC 浪涌经寄生参数耦合到 5V，ZigBee 上 LDO 最高 6.5V 应力不足被击穿；继电器反向浪涌加重。
- 实战点：LM1117 20V 替 LDO 扛浪涌；AC 入口加共模电感；5V 加 TVS；实测 ZigBee 40mA / ARM+ZigBee 200mA
- 动作：写实战案例（嵌入式产品浪涌防护速查表）

### 2. ZigBee 设备典型故障 4 例排查
- 链接：https://max.book118.com/html/2019/1012/5321122313002134.shtm
- 来源：原创力文档（智能家居产线 PPT）
- 摘要：UniSion 智能家居 8 页手册。故障：电源灯不亮、入网失败（默认密码 unisiot654321）、红外学习保持 5cm、GPRS 在线灯不亮（SIM/防火墙）。
- 实战点：默认调试密码遗漏是产线高频；红外学习 5cm 距离；GPRS TCP 被防火墙拦比硬件故障多
- 动作：入主题笔记（ZigBee 智能家居产线 QA 速查）

### 3. ZigBee 通信失败 5 大类速查
- 链接：https://blog.csdn.net/P_xiaojia/article/details/97690576
- 来源：CSDN（产线实战总结）
- 摘要：信号质量（距离/障碍物）、同频干扰（Wi-Fi/蓝牙 2.4G 噪声）、路由未恢复、节点移动、数据包过频拥堵。
- 实战点：读 RSSI/LQI 判定；产线 2.4G 频谱仪扫；路由发现期间数据丢；分包限速防拥堵
- 动作：扩 deep-dive（2.4G 共存 Wi-Fi/BLE 实战手册）

### 4. IAR/CC2530 编译调试 17 问
- 链接：https://blog.csdn.net/halsonhe/article/details/47087729
- 来源：CSDN（开发实战 17 错误清单）
- 摘要：XDATA_Z 段溢出（数组超 0x19A1）；CSTACK 不足；Fatal error #E1（IAR/TI Tools 不同盘）；lnk51ew_cc2530b.xcl 路径；release 必须 .hex。
- 实战点：数组改 __code / code 段；改 f8w2430.xcl -D_CODE_END；IAR 跟 SmartRF Tools 同盘；linker output format debug/release
- 动作：入主题笔记（CC2530/Z-Stack 调试错误码速查）

### 5. CC2530 Z-Stack 终端功耗 8mA→11μA
- 链接：https://blog.csdn.net/m0_38064214/article/details/78165056
- 来源：CSDN（Power Monitor 仪器实测）
- 摘要：EndDeviceEB 预编译去 xPOWER_SAVING 前缀。Monsoon 实测：普通 8.087mA / 32.4h；低功耗 11μA / 142.9h；HalKeyConfig 禁用中断再省 3μA。
- 实战点：xPOWER_SAVING 单一开关；2s 周期发数据测在网；HalKeyConfig 禁中断省 3μA；与产品要求仍有差距
- 动作：写实战案例（ZigBee 终端电池寿命优化 pipeline）

## 下一步
等你 review：激活 / 改写 / 丢弃
<mavis-progress>idle</mavis-progress>
