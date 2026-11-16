# CAN FD / CAN XL 候选素材 @ 2026-11-09 23:50

## 协议速览
- 是什么：CAN 第三代，FD 64B/5-8Mbps，XL 2048B/20Mbit/s，物理层 PWM+推挽。
- 解决什么：经典 CAN 8B/500k 带宽不够，需补一致性测试与 EMC 抗扰护栏。
- 跟 L4 主题的关联：补 can-fd-failure-cases.md 缺的 EMC、终端匹配、XL 判据三段。

## 候选文章（4 条）

### 1. CAN 接口 EMC 防护实战：从 BCI 测试失败到全频段通过
- 链接：https://blog.csdn.net/weixin_26854829/article/details/166168167
- 来源：CSDN 单篇
- 摘要：ISO 11452-4 BCI 200mA 下 80-120MHz 冒错误帧、超 200mA 直接 bus off；共模摆幅 ±25V 超 TJA1042 限值。
- 关键实战点：① 整改——TVS 换 SM712、CMC 300→600Ω@100MHz 且清空电感下方铺铜、接口地↔数字地 1nF/2kV 桥接、H/L 对地 47pF → 共模 ±8V、近场降 6-8dB；② TVS 距连接器 7cm 等于没防；CISPR 25 留 6dB 余量、BCI 加严 20%。
- 推荐动作：写实战案例（新增 EMC 抗扰度章节）

### 2. 同星 CAN XL 一致性测试方案（博世 IP 交流日）
- 链接：https://www.tosunai.com/bosch-ip-tech-exchange-day-tosun-can-xl-conformance-test-solution-debut/
- 来源：同星智能厂商技术演讲（TSMaster）
- 摘要：XL 2048B/20Mbit/s，CRC 升 PCRC+FCRC，新增 SDT/VCID/AF 字段。
- 关键实战点：① 1bit 仅 50ns，回环延迟上限 t_loop≤190ns，软件无法 1bit 内注入，须硬件触发干扰仪；② 数据相位不回采只能靠 CRC 确认；错误信令禁用时节点不发错误帧，判据改为"接收端是否记录到异常"。
- 推荐动作：入主题笔记（CAN XL 测试判据小节）

### 3. CAN FD 超时在 CCS 充电中的定位（ISO 15118-2）
- 链接：https://digitalflownet.com/ev-charging/diagnose-can-fd-timeout-errors-ccs-iso-15118-2
- 来源：英文技术站（数值待核）
- 摘要：PnC 握手静默失败 3.2s：SessionSetupRes 用 498.2ms（限 500ms），ServiceDiscoveryRes 用 1218.3ms（限 1200ms）。
- 关键实战点：① 丢帧不上报 DTC（5 家 OEM 73% 零 DTC 而 CANoe 见 >95% 丢帧），须绝对时间戳+状态机脚本判超时；② 根因在硬件邻域——MCU 唤醒 112µs、抖动 18-22ns、BMS 12ppm 漂移叠加，换 TJA1153 后 <5ns；压测 ±50ppm、>75% 负载、100+ 次。
- 推荐动作：写实战案例（静默超时诊断流程；抖动数值回 NXP 核）

### 4. 车载 CAN FD 信号完整性调试：终端电阻匹配与 EMI 抑制
- 链接：https://www.21ic.com/a/1008533.html
- 来源：21IC 电子网
- 摘要：PVC 双绞线 1MHz 实测 Z0 常 110-130Ω，硬配 120Ω 会反射致采样错。
- 关键实战点：① TDR 测 Z0 再配终端（±1%），不均匀时两端各串 2-5Ω 补偿，2Mbps 分支压到 0.3m 内；② CMC 100µH（DCR<0.5Ω）+ 对地电容 2Mbps 22pF、500k 47pF；眼图 2Mbps 眼高>1.5V、眼宽>400ns、抖动<50ns。
- 推荐动作：扩 deep-dive（终端电阻/特性阻抗章节）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
