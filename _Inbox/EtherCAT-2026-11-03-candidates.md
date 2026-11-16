# EtherCAT 候选素材 @ 2026-11-03 22:00

## 协议速览
- 是什么：以太网物理层 + 帧「飞过」式处理
- 解决什么：μs 级确定周期 + DC 时钟，多轴对齐
- 关联：deep-dive 仅 4.3 KB（同库 10–25 KB），无 failure-cases

## 候选文章（5 条）

### 1. 主站丢周期：IRQ、中断亲和性到 CPU 隔离
- 链接：https://blog.csdn.net/whh_bjqy/article/details/167371815
- 来源：CSDN（IgH/Linux RT）
- 摘要：PDO/WKC 正常仍偶发周期超时，分四类：唤醒晚/算法超时/收发/同步异常
- 关键实战点：① CLOCK_MONOTONIC 量实际周期，看最大值不看均值 ② /proc/interrupts 查网卡 IRQ 是否与控制线程同核
- 推荐动作：扩 deep-dive + 新建 practical.md

### 2. IgH 主站 DC 同步与实时周期
- 链接：https://bbs.plcjs.com/forum.php?mod=viewthread&tid=650394
- 来源：PLC 论坛（IgH 第八篇）
- 摘要：DC 非配置项，而是「从站时钟+主站调度+application time+周期维护」组合，只调 config_dc 不同步
- 关键实战点：① sync0_cycle 单位 ns，填 us 差 1000 倍 ② assign_activate 须来自 ESI/手册 ③ 周期须含 application_time + sync_slave_clocks
- 推荐动作：扩 deep-dive 的 DC 章节

### 3. NI PXIe-8880 + 9144 环网间歇 -66460 根因链
- 链接：https://industrialmonitordirect.com/fr/blogs/knowledgebase/resolving-pxie-8880-scan-engine-error-66460-in-ethercat-systems
- 来源：Industrial Monitor Direct
- 摘要：数月后间歇 -66460，周期放宽非根因；故障时 CPU <30%
- 关键实战点：① 低 CPU 报错 = 时序问题非吞吐 ② BIOS 超线程/Turbo/C-States 退出唤醒 30–100 µs 击穿看门狗 ③ 9144 滤网/空槽封板致风道偏流→DC 失稳
- 推荐动作：写实战案例（新建 ethercat-failure-cases）

### 4. 汇川 InoProShop 组态与 SV660F 伺服调试
- 链接：https://blog.csdn.net/weixin_28285943/article/details/164582602
- 来源：CSDN（国产主站+伺服）
- 摘要：扫不到从站/一片红/伺服使能失败的排查表（汇川 H5U+SV660F）
- 关键实战点：① XML 版本须配固件版本，否则设备名带「?」 ② 导入 XML 后要重新添加从站才生效 ③ 周期别贪 0.25 ms
- 推荐动作：写实战案例 + 入主题笔记

### 5. EtherCAT 架构、DC 与运动控制（69 KB 长文）
- 链接：https://automationhub24.com/blog/ethercat-architecture-distributed-clocks-motion-control-opc-ua
- 来源：第三方技术站（对照 ETG/Beckhoff）
- 摘要：30+ 节：帧处理/PDO-SDO/CiA 402/DC/状态机/OPC UA
- 关键实战点：① DC 三项：offset 对齐时基、drift 持续校正、jitter 残余波动 ② 区分规范值与实测值
- 推荐动作：入主题笔记（仅作索引，数字回 ETG 核）

## 排除/待核
- 排除：hqwc.cn、kaifayun.com、tsight.io（AI 农场）；bitcoinversus.tech（科普转载）；bjdmk.com.cn
- 待核：候选 5 的 DC 抖动实测值是否与 ETG 一致

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
