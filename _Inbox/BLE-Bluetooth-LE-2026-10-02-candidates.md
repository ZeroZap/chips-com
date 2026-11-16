# BLE/Bluetooth LE 候选素材 @ 2026-10-02 00:00

## 协议速览
- 是什么：2.4 GHz 低功耗短距无线协议，常嵌于 MCU SoC
- 解决什么：电池供电节点的短距低吞吐连接（穿戴/传感器/资产追踪）
- 跟 L4 关联：「环境差异型」故障第一大类，跟 Wi-Fi/ZigBee/Thread 同 2.4 GHz 拥塞

## 候选文章（5 条）

### 1. BLE 5.0 从实验室到量产的生存指南
- 链接：https://tsight.io/articles/17495642?lang=zh
- 来源：tsight.io 实战博客
- 摘要：nRF52840 手环项目实验室完美、量产后频繁掉线。根因 PCB 廉价材料 + 布线密集。覆盖「功耗谎言」「连接玄学」「协议栈陷阱」三章，每章含工业级解决。
- 实战点：① PCB 4 层板 + 地平面 + 差分走线；② 协议栈优先级抢占导致 HardFault
- 推荐动作：**扩 deep-dive**

### 2. nRF52833 量产失败 20% 案例
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/117429/nrf52833-ble-not-working
- 来源：Nordic 官方 DevZone QA 实战
- 摘要：批量产 3000 颗 nRF52833，前 500 OK，之后 ~20% 失败品 RADIO state=0 不广播。终极根因 = SMT 后的 PCB 分板工艺产生应力损伤 RF 区。
- 实战点：① NRF_RADIO->STATE / NRF_FICR 自检；② 分板对 RF bond wire 损伤；③ 同型号替换可证伪
- 推荐动作：**写实战案例**

### 3. 蓝牙遥控器丢连 4 类硬件层根因
- 链接：https://ebyteiot.com/fr/blogs/ebyte-iot-blog/why-is-your-bluetooth-remote-control-dropping-connections-and-how-can-you-fix-it
- 来源：EBYTE IoT Blog 工业 IoT 厂商
- 摘要：90% 根因在硬件/RF 环境。四类故障：① 电源纹波 brownout reset；② 2.4 GHz 拥塞耗尽 AFH 干净信道；③ 天线 VSWR>3.0；④ 连接间隔+从机延迟配错触发 watchdog。
- 实战点：① DSO AC 耦合 VCC ripple < 50 mV；② +4 dBm 补偿穿墙
- 推荐动作：**入主题笔记**

### 4. BLE 实验室 vs 产线：失败为何难 debug
- 链接：https://dewinelabs.com/why-does-your-ble-work-in-the-lab-then-fail-in-production/
- 来源：dewinelabs 专业无线测试实验室
- 摘要：失败非灾难性而是间歇性，依赖时间/Wi-Fi 流量/RF 条件。团队常花数月排查硬件，根因却在 firmware 假设 BLE = 透明管道而非事件子系统。
- 推荐动作：**扩 deep-dive**（跟 ZigBee/Thread 同主题可比照）

### 5. BLE 5 大系统级设计错误
- 链接：https://www.eurthtech.com/post/ble-is-not-just-a-protocol-system-level-design-mistakes-engineers-make
- 来源：EurthTech 嵌入式咨询
- 摘要：5 类错误 = ① 当透明管道；② 假设 central 设备可靠（iOS/Android 后台策略）；③ 电源事后调；④ BLE 状态爆炸；⑤ 安全策略不演进。
- 推荐动作：**入主题笔记**

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃

—— 优先级：2 (Nordic DevZone 真实失败案例) > 1 (tsight 量产 PCB/电源) > 3 (EBYTE 4 类硬件根因) > 4 (dewinelabs 失败哲学) > 5 (eurthtech 系统错误)。