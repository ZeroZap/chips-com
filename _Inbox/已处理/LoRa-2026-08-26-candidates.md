# LoRa/LoRaWAN 候选素材 @ 2026-08-26

## 协议速览
- 是什么:Sub-GHz LPWAN(LoRa PHY + LoRaWAN MAC)
- 解决:Wi-Fi/BLE 够不到(距离/穿透/电池)+ 蜂窝太贵的"少量数据+远距离+多年电池"场景
- L4 关联:产线设备健康监测**首选物理层**,必谈 SF/ADR/占空比/私有 NS

## 候选(5 条)

### 1. 起重机 LoRaWAN 状态监测(EurthTech)
- 链接:https://www.eurthtech.com/post/industrial-crane-condition-monitoring-with-lorawan-the-vibration-and-temperature-sensor-stack-that
- 来源:嵌入式咨询 blog
- 摘要:起重机电机轴承预测全栈:边缘 FFT+duty-cycle+LoRa/蜂窝双链路+EMI 抑制+运行态感知阈值;**标定是 design-validate-refine 循环**
- 实战点:①MCU 提 RMS/峰值/频域特征再发(超 duty cycle) ②动态 baseline 替固定阈值 ③双链路防"最该报时掉链" ④标定反向触发固件修订
- 推荐:**扩 deep-dive** —— L4 必收"LoRa+振动+边缘计算"

### 2. Volvo Lyon AGV 监测
- 链接:https://www.volvogroup.com/en/news-and-media/news/2023/mar/volvo-group-implements-a-new-internet-of-things-iot-network-to-make-factories-smarter.html
- 来源:Volvo 官方
- 摘要:AGV 24V 电池<22V 趴窝,每停=损失 2 台发动机/周;LoRa 监测<23V 提前告警
- 实战点:①2.4GHz 被产线占满只能 Sub-GHz ②私有直连 Ethernet 拒云依赖 ③网关过 IT 审计 ④一网多用(温湿度+压差)撑 ROI
- 推荐:**入主题笔记** —— L4 重型制造 ROI 样板

### 3. SmartLumber:LoRaWAN+LSTM 孪生
- 链接:https://wiki.heltec.org/news/contest-content-template/SmartLumber
- 来源:Heltec 官方 wiki
- 摘要:粉尘+电磁噪声+500m 厂房,LoRaWAN+振动温度+Node-RED/InfluxDB/Grafana+Python LSTM 孪生;**无故障数据时孪生造数据**,7 天预测
- 实战点:①数据悖论→孪生造数据合法 ②2.4GHz 金属厂房失效 ③Docker Compose 一键复现 ④LSTM 仅仿真需数据回流
- 推荐:**写实战案例** —— L4 "LoRa+AI 边缘预测"教材

### 4. 晶圆厂 LoRaWAN 废液监测(研华)
- 链接:https://www.advantech.com/es-es/resources/case-study/20D00BB3-74F8-4292-9A64-D1D1B575A3D5
- 来源:研华官方
- 摘要:屋顶 20+ 排酸废气风机,以前人爬屋顶手提振动仪一天一次。WISE-2410+WISE-6610,Modbus 进 SCADA,**对标 ISO 10816**
- 实战点:①ISO 10816 立可信度 ②边缘 ARM M4 算 VRMS/kurtosis(非 raw) ②节 Li-SOCl2 撑 2 年 ④私有 LoRaWAN 免流量 ⑤穿透 15km
- 推荐:**入主题笔记** —— L4 "ISO 10816+LoRa"范本

### 5. Pilot→Production:70% 扩不了
- 链接:https://lorawan-consulting.com/articles/pilot-to-production
- 来源:LoRaWAN 咨询公司
- 摘要:**70% 企业 IoT 死在 pilot purgatory**;5 卡点:网关单点/树莓派 NS/IT 审计/采购/OTA
- 实战点:①ChirpStack 需 2-4 核+8GB RAM,不上 Pi ②N+1 网关冗余 ③FUOTA 硬约束 ④多租户/角色 pilot 期定义 ⑤€80 单件可能 €55 批量,lead time 8-16 周
- 推荐:**写实战案例** —— L4 失败模式反教材

## 下一步
等你 review 后决定:激活/改写/丢弃
