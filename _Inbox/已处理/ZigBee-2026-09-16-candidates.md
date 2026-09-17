# ZigBee 候选素材 @ 2026-09-16 12:14

## 速览
IEEE 802.15.4 低功耗短距网状网，2.4 GHz / 250 kbps，单网关 30-50 节点上限。L4 关联：IoT 产线实战——多径/温漂、buffer 满、OTA 失败、SDK 回归。

## 候选（5 条）

### 1. Zigbee 工业组网：自愈变自杀（tsight.io）
- 链接：https://tsight.io/articles/12807223
- 来源：tsight.io 工业实测
- 摘要：化工厂网关凌晨掉线，频谱仪抓到金属罐体多径→MAC 重传→父节点判丢子节点→离网广播雪崩。
- 实战点：金属+温漂致 VSWR 恶化、PA 发热形成"越久越差"负反馈；单网关 30-50 节点真实极限，实时 >50ms 控制直接放弃 Zigbee。
- 推荐：**扩 deep-dive**——产线失败归因到物理层的中文实战稿。

### 2. Zigbee Module PCB: Stop Blaming the RF Chip First
- 链接：https://www.sprintpcbgroup.com/fi/blogs/zigbee-module-pcb-signal-integrity-hdi-stackup-antenna/
- 来源：SprintPCB 实战博客
- 摘要：量产模块 sleep current 2 µA 跳到几十 µA，追半月发现 HDI 板厂焊前清洗差→离子残留→高湿隐性导电通道。
- 实战点：LDO 看动态响应/压降别只看静态电流；32.768kHz 晶振 ESR 让同批模块功耗差 ~1 µA。
- 推荐：**扩 deep-dive**——"低功耗是系统工程而非芯片选型"。

### 3. Z-Stack 20240710 BUFFER_FULL 大网崩溃
- 链接：https://blog.gitcode.com/3f1089ec9a65cfe3818fcdd6c0d274ca.html
- 来源：GitCode 社区 issue 汇总
- 摘要：20240710 固件大网（60-120 设备）跑数小时崩溃，日志爆 `0x11: BUFFER_FULL`；回退 20221226 即恢复。
- 实战点：buffer 管理 + 疑似内存泄漏；升级前在模拟生产环境压测，关键业务网保持"已知工作版本"基线。
- 推荐：**写实战案例**——大规模组网 buffer 雪崩模板，L4 内存管理反面教材。

### 4. Inovelli VZM31-SN OTA 25% abort
- 链接：https://community.inovelli.com/t/recently-purchased-inovelli-blue-series-switches-3-and-canopy-modules-2-constantly-dropping-from-zigbee-network/21732
- 来源：Inovelli 官方社区
- 摘要：v1.01 固件 OTA 25% 反复 abort；根因旧 Zigbee 3.0 栈 + ZHA OTA 块过快撞 buffer；解决 air-gap 复位 + 降速 OTA + 跨代先升 2.18 再 3.0。
- 实战点：跨代 OTA 不直跳；`zha_ota_update_request_interval: 10` 是社区调速共识。
- 推荐：**写实战案例**——OTA 协议栈版本管理+节流调参配方。

### 5. Zigbee assessment in industrial environments（Cubex）
- 链接：https://cubexgroup.com/?p=8606/
- 来源：Cubex Group 安全团队博客
- 摘要：工业 Zigbee 渗透，Python responder 太慢连不上；改 nRF52840 dongle 又因 stack profile 不匹配被拒；最终 Zephyr C 跑 MAC/ACK + Python 上层 hybrid。
- 实战点：MAC/ACK 硬实时必须 C/Zephyr；stack profile 公开 vs 私有不互通。
- 推荐：**入主题笔记**——L4 协议栈混合调试少实战。

## 下一步
priority: 1>2>3>4>5；🚫 ebclinks（营销）、Bituo-Technik（产品手册）。