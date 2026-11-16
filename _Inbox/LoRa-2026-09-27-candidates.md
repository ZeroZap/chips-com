# LoRa / LoRaWAN 候选素材 @ 2026-09-27 00:00

## 协议速览
- 是什么：1GHz 以下免许可频段的扩频（CSS）低功耗远距离无线，LoRaWAN 是其上的星型 MAC 协议
- 解决什么：电池供电 / 小数据量 / 广域分布 / 无人值守节点的远距离上报（水气表、农业传感、地磁、园区传感）
- 跟 L4 主题关联：实战排障同型（RSSI 好但丢包、SF/ADR 陷阱、网关硬件坑），"实验室 OK 产线挂"系列天然补集

## 候选文章（3 条）

### 1. LoRaWAN Gateway Troubleshooting: RSSI, SNR & Packet Loss（Robustel 工业 IoT blog）
- 链接：https://www.robustel.store/blogs/industrial-iot-blog/lorawan-gateway-troubleshooting-rssi-snr-packet-loss
- 来源：工业 IoT 网关厂商 blog
- 摘要：丢包按 pattern 分 3 类（Random/Periodic/Total Silence）反推根因；硬件列 4 大坑（电缆水侵、pigtail 折断、2.4GHz 误插 915MHz 端口）；信噪地板城市 -100 dBm / 农村 -120 dBm
- 关键实战点：① 健康阈值 RSSI > -115 dBm 且 SNR > -10 dB；② 多径导致 ±10 dB 抖动必须看 20 包平均；③ 周期性丢包先查 2-4 PM 邻近机械/卡车
- 推荐动作：**写实战案例**（与 ZigBee 仓库 RSSI 好但丢包主题打对仗）

### 2. Hot Take: LoRaWAN Is Overkill for Factory IoT — Use Sigfox（johal.in）
- 链接：https://johal.in/hot-take-lorawan-is-overkill-factory-iot-use
- 来源：工程师博客（含真实测试代码）
- 摘要：12 个工厂站点实测 ADR 陷阱——SF12 卡死后需手动复位，34% 节点 30 天被锁 SF12，电池寿命缩短 22%；关 ADR + 固定 SF7/8 后电池改善 41%、时延降 62%
- 关键实战点：① ADR 6x 功耗 / 10x 时延的具体数字；② disable_adr() C 代码片段；③ 工厂建议关 ADR（含 LoRaWAN_ADR_Utils 工具思路）
- 推荐动作：**写实战案例**（真实数字 + 代码片段，扩 deep-dive 也合适）

### 3. LoRa 无线通信技术详解：从扩频原理到 LoRaWAN 组网与低功耗实战（kwkr.cn 中文）
- 链接：https://kwkr.cn/news/418894
- 来源：中文工程师长文（偏经验向）
- 摘要：覆盖 LoRa 物理层、SF/BW/CR 联动、SX1276 vs SX1262/1268 选型、低功耗电流实测、链路预算与现场踩坑；含 6.4 节"常见问题速查表"
- 关键实战点：① RSSI 满格但丢包根因是 SNR（典型 -15 dB 失效）；② 休眠电流偏差 100x 的两类根因（DIO 浮空漏电 / 开发板 LED 静态电流）；③ ADR 判定逻辑（固定关 / 移开）；④ 中文链路预算与现场勘测方法
- 推荐动作：**入主题笔记**（中文 L4 主题素材源，含公式 + 现场排查清单）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃