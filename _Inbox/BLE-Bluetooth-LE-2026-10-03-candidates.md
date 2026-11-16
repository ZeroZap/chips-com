# BLE 候选素材 @ 2026-10-03 12:00

## 协议速览
BLE 短距低功耗无线，GAP/GATT/ATT/L2CAP 分层；解决手机-外设最后 10 米；L4 关联 = 「实验室 OK 产线挂」是 BLE 最大痛点。

## 候选（5 条按优先级）

### 1. E-Rickshaw BMS 蓝牙劫持（视频复现·真实出行）
- 链接：https://www.linkedin.com/pulse/app-can-kill-e-rickshaw-mid-traffic-technical-binit-varghese-l2vhc
- 摘要：印度 150 万辆 e-rickshaw 用 Grenergy BMS，APP 走 BLE Level 1 Just Works 配对——任何人 15m 内接管切断输出。Rony Das（Google $5000 bounty 研究员）发视频复现并艾特 Assam Police；同款 BMS 还用于高尔夫车。Just Works = CWE-306，单 SoC 漏洞跨产品传导。

### 2. Nordic NRF52832 量产「Loop of Death」（官方 DevZone 5 年未解）
- 链接：https://devzone.nordicsemi.com/thread/321147?ContentTypeID=1
- 摘要：NRF52832 + SDK v15.3 + S132 6.1，连接 10–25min 后 peripheral 不响应，23–24 包重传后掉；最常失败在 empty PDU，也死在 LL_FEATURE_REQ/PHY_REQ/MTU 交换。pinreset 才能恢复。缩周期复现（20min→30s→几秒）= 状态机毒性积累；iPhone 比 Android 敏感。

### 3. CSDN 工程师 NRF52832+ESP32 量产 4 类故障 + 6 步排查
- 链接：https://blog.csdn.net/weixin_32496547/article/details/164598478
- 摘要：把 BLE 不稳定归 3 类（连不上/掉线/丢包）→ 3 排查方向。覆盖连接参数/广播/白名单+绑定+私有地址/MTU+DLE/CCCD 持久化/晶振频偏/天线 S11。附「智能水表欠费关阀无法蓝牙唤醒」完整案例：MCU 低功耗唤醒源未覆盖 BLE 中断。

### 4. EurthTech「BLE Is Not Just a Protocol」5 mistake + 5 年 case
- 链接：https://www.eurthtech.com/post/ble-is-not-just-a-protocol-system-level-design-mistakes-engineers-make
- 摘要：5 mistake：(1) 当 transport 不用当 system；(2) 忽略 central 不可靠；(3) Power 后置；(4) State 爆炸；(5) Security 不演进。真实案例：传感+处理稳定运行数年，但 BLE 不可预测掉线、电池加速衰减——根因不是 stack，是 firmware 把 BLE 当 peripheral interface。

### 5. EBYTE 工业 BLE 遥控器掉线 4 物理层根因 + 4 步现场排查
- 链接：https://ebyteiot.com/fr/blogs/ebyte-iot-blog/why-is-your-bluetooth-remote-control-dropping-connections-and-how-can-you-fix-it
- 摘要：工业/商业 90% 掉线根因在硬件：电源纹波（TX 15–25mA 峰值致 LDO brownout）、2.4GHz 拥塞（AFH 失效）、天线 VSWR>3.0（人体/金属 detune）、连接间隔不当。附现场排查 Matrix。

## 推荐动作
- 写实战案例：1（与 Frontier X CVE-2026-5768 合并「BLE 信任边界缺失」集）
- 入主题笔记：2（nrf52-known-bugs.md）+ 4（架构方法论）
- 扩 deep-dive：3（实验室 vs 产线首选）+ 5（物理层/电源/天线补强）

下一步：P1=1+2+3 强实战，P2=4 架构，P3=5 物理层；下个协议 = **CAN FD / CAN XL**。
