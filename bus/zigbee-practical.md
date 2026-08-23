# ZigBee Practical Guide

## 目标

本文用于 ZigBee 工程调试：信道、PAN ID、入网、ZCL 调试、抓包、产线常见故障（ReJoinRequest 失败、OrphanJoin 卡死、End Device 不睡眠、NCP crash）的快速定位。

## 最小接线（以 EFR32MG21 为例）

```text
VDD ──── VDD (1.71~3.8V)
GND ──── GND
ANT ──── 2.4GHz 天线（PCB 走线 / 陶瓷 / IPEX）
DEC1 ──── 100nF + 10µF 紧靠 VDD
RESETn ─ 10kΩ 上拉（必须）
JTAG/SWD ─ 调试口
```

**关键约束**：

- 2.4 GHz 天线 50Ω 匹配
- DC-DC 模式（默认 EFR32）需外置 L/C 滤波器
- Reset 引脚必须上拉，否则偶发不复位
- 晶振 38.4 MHz（HFXO）+ 32.768 kHz（LFXO），匹配电容精准

## 关键参数

### 信道

```text
IEEE 802.15.4 2.4 GHz:
  Channel 11 ~ 26 (中心频率 2405 ~ 2480 MHz)
  间隔 5 MHz
  16 个信道
```

**信道选择 vs Wi-Fi 干扰**：

| ZigBee 信道 | 中心频率 (MHz) | Wi-Fi 重叠 |
| --- | --- | --- |
| 11 | 2405 | Wi-Fi 1（最差） |
| 15 | 2425 | Wi-Fi 1~4 |
| 20 | 2450 | **Wi-Fi 6**（最差） |
| 25 | 2475 | Wi-Fi 11+ |
| 26 | 2480 | Wi-Fi 14（部分国家禁用） |

**推荐避开 11、15、20、25、26**——选 12~14、16~19、21~24。

**实战**：用 `Channel Mask` 限制扫描和入网：

```c
// 避开 Wi-Fi 1, 6, 11
uint32_t channel_mask = 0x07FFF800;
// bit 11~26 = 1，bit 0~10 = 0
// 实际：避 11/20/25（Wi-Fi 1/6/11）
uint32_t safe_mask = 0x07FFE400;
// bit 11=0, 20=0, 25=0, 其余 1
```

### PAN ID

```text
0x0000 ~ 0x3FFF（用户可用）
0xFFFF = 广播 PAN
0xFFFE = 选最优 PAN（ZigBee 3.0）
冲突 → 节点选另一个 PAN，可能掉网
```

**最佳实践**：

```text
小规模网络：选 0x0001 ~ 0x3FFF 固定值
大规模 / 楼宇：选随机 PAN + Coordinator 检测冲突后切换
ZigBee 3.0：用 0xFFFE 让 Coordinator 选
```

### 网络地址

```text
16-bit NWK 地址（短地址）：
  Coordinator: 0x0000
  Router / End Device: 由 Coordinator 分配
  0xFFFC = 路由器广播
  0xFFFD = 终端广播
  0xFFFE = 全节点广播
  0xFFFF = reserved
```

### TX Power

| 厂商 | 范围 | 默认 | 典型设置 |
| --- | --- | --- | --- |
| EFR32MG21 | -30 ~ +20 dBm | +8 dBm | 楼宇 8 dBm，户外 14 dBm |
| CC2652 | -25 ~ +5 dBm（boosted） | +5 dBm | 楼宇 5 dBm |
| nRF52840 | -20 ~ +8 dBm | 0 dBm | 楼宇 0 dBm |

### 路由深度

```text
最大跳数：默认 30（协议规定）
推荐深度：<= 5（mesh 太深延迟大）
每跳延迟：~10~30 ms
```

## 抓包工具

| 工具 | 平台 | 优势 | 限制 |
| --- | --- | --- | --- |
| Ubiqua Packet Sniffer | Windows | 协议解析全，TI/Silicon Labs dongle 支持 | 付费（>500 美元） |
| TI Packet Sniffer | Windows | CC2531 / CC2652 dongle 免费 | 仅 TI 协议栈 |
| Wireshark + ZigBee dissector | 全平台 | 开源，需配合 USB dongle | 配置复杂 |
| Ember Desktop / Network Analyzer | Windows | Silicon Labs 官方，能改 NCP 固件 | 仅 EFR32 |
| zigbee2mqtt + Mosquitto + Wireshark | Linux | 真实流量，含 MQTT 关联 | 仅 zigbee2mqtt 网关 |
| nRF Sniffer for 802.15.4 | nRF52840 DK | Nordic 出品，免费 | 仅 nRF 系列 |
| Daintree SNA (Network Analyzer) | Windows + 专用 dongle | 业内老牌抓包，从 PHY 到 ZCL 全栈解码；复杂环境抗扰强 | 商业授权；需刷 CC2531 Sniffer 固件 |

**产线推荐组合**：

```text
研发调试：Ubiqua + CC2652STK dongle（看 APS / ZCL / NWK 全程）
产线批量：nRF Sniffer + 自动化脚本（看入网 / 配对）
客户支持：zigbee2mqtt + Wireshark（看完整 IoT 流量）
NCP 调试：Ember Desktop + SWO 抓 log
```

### USB-TTL 串口电平匹配（DL-20 经典坑）

ZigBee 模块（如 DL-20 / E180 系列）通过串口接 MCU 时，**电平不匹配**是产线第一坑。模块电平只有 TTL（0~3.3V），但 USB-TTL 适配器种类繁多，乱接就废。

```text
典型翻车现场：
  DL-20 经 USB-TTL（CH340）自发自收正常（PC 端）
  接入 STM32 后：模块收不到 MCU 发的 AT 指令，但 MCU 能收到模块发的回显
  表现：抓包显示只发不收，节点永远入不了网

根因：串口电平不匹配
  ① DL-20 TX/RX 是 TTL 3.3V
  ② CH340 默认 5V 输出（可配置 3.3V）
  ③ STM32 USART1/2 走 VCC（5V 容差或 3.3V，取决于板子）
  ④ 5V 灌进 DL-20 RX → 长期高电平应力 → 端口逐渐失效

排查顺序（不要先怀疑固件）：
  1. 单独测试：DL-20 ↔ USB-TTL（直连 PC），AT 指令正常 → 模块 OK
  2. 单独测试：USB-TTL ↔ STM32 USART3（直连，绕开 USART1/2）→ 正常
  3. 测试 USART1/2 走 CH340/485 转换芯片：电平可能被拉偏
  4. 万用表量 DL-20 RX 脚：电压 > 3.6V → 立即停，问题确认

修复方案：
  ① 硬件：MCU 和模块之间加电平转换芯片（如 TXS0108E / MAX3232）
  ② 硬件：直接用 USART3（板载 3.3V TTL 直连）
  ③ 软件：USART 配低波特率（9600）减少电平边沿抖动
  ④ 长期：模块选型时**直接用 3.3V TTL 串口**的模组，避开 RS232 变体
```

**为什么不在抓包工具表里写**：电平匹配属于"硬件调试"，不是抓包本身。但和调试紧密相关，所以放在抓包工具段后做过渡。

### ZigBee 晶振选型实战（频偏 / 起振 / 隔离布局）

ZigBee 是 IEEE 802.15.4 协议，**频偏决定入网成功率**。晶振选错 = 节点入网成功率 50% 不到，从晶振视角看 ZigBee 实战：

```text
时钟架构：
  - 16 MHz RF 晶振：决定 RF 频率精度
    - 频偏 ±25 ppm（典型）→ IEEE 802.15.4 兼容
    - 频偏 ±10 ppm（好）→ 长距 / 工业
  - 32.768 kHz RTC 晶振：决定电池寿命
    - 睡眠电流 0.5-2 uA 取决于 RTC 精度
    - 频偏 ±20 ppm（典型）→ 计时准确
  - 内置 RC 振荡器：辅助
    - 启动快但精度差
    - 仅作 backup

频偏门限（实测）：
  - 综合频偏（RF + RTC）< ±40 ppm
    → 入网成功率 > 99%
  - 综合频偏 ±40-60 ppm
    → 入网成功率 95%（偶发失败）
  - 综合频偏 > ±60 ppm
    → 入网成功率 < 80%（频繁掉线）

排查入网失败（频偏 vs 链路）：
  Step 1：先查 LQI（Link Quality Index）
    LQI > 100 → 链路好，入网失败 = 频偏问题
    LQI < 100 → 链路差，先看 RSSI / 阻挡
  Step 2：测晶振实际频偏
    用频率计测 16 MHz 输出
    算 ppm = (实测 - 16e6) / 16e6 * 1e6
  Step 3：查温区
    -40 ~ +85°C 工业温区晶振：freq vs temp 漂移 < ±10 ppm
    0 ~ +70°C 商业温区：< ±5 ppm
    选型时看 datasheet "Frequency Stability vs Temperature"
```

**低温起振**：

```text
-40°C 低温起振时间 > 5ms → 偶发死机
固件解决：上电后等 10ms 再初始化 RF
  HAL_BOARD_INIT();          // 硬件 init
  delay_us(10000);           // 等 10ms 让晶振稳
  emberInit();                // 再 init RF stack

协调器 vs 终端晶振：
  协调器：±15 ppm（可选用 TCXO 温补晶振）
  终端：±25 ppm（普通晶振即可）
  路由：±20 ppm（介于两者之间）

RF / RTC 时钟隔离布局：
  - 16 MHz 晶振走线 < 5mm
  - 32.768 kHz 走线避开 RF 走线 > 3mm
  - 晶振地走线直接到 GND 焊盘（不走公共地）
  - 晶振外壳接 GND（屏蔽）
```

### CH582 RISC-V 自定义 BLE Service 实战（国产替代参考）

CH582（RISC-V + BLE + USB）开源项目 badgemagic-firmware 是国产 RISC-V BLE+USB 实战参考：

```text
硬件：CH582（青稞 V4 内核）+ BLE 5.0 + USB 2.0
      国产 RISC-V 替代 nRF52840 的可行方案

自定义 Service 文件结构：
  profile/
  ├── ble_custom_svc.c
  ├── ble_custom_svc.h
  └── setup.c     ← 注册 service + characteristic 读写回调

关键代码片段：
  // 1. 注册自定义 Service UUID
  uint8_t custom_svc_uuid[16] = { 0x12, 0x34, ... };
  GATT_AddService(GATT_PRIMARY_SERVICE_UUID, custom_svc_uuid, 0x0010);
  
  // 2. 添加 Characteristic
  uint8_t char_uuid[16] = { 0x12, 0x35, ... };
  GATT_AddCharacteristic(char_uuid, GATT_PROPERTY_READ | GATT_PROPERTY_WRITE,
                          0x0020, NULL, on_read_callback, on_write_callback);
  
  // 3. USB 复合设备（CDC + HID）
  //   - CDC：虚拟串口
  //   - HID：键盘 / 鼠标 / 自定义设备
  //   - 描述符：interface class 0x02 (CDC) + 0x03 (HID)
  
  // 4. BLE_DEBUG 宏日志
  #define BLE_DEBUG 1
  #ifdef BLE_DEBUG
    PRINT("BLE TX: %d bytes\n", len);
  #endif

Charlieplexed LED 阵列（特殊应用）：
  - 6 pin 控 30 LED
  - 适合 LED 徽章 / 矩阵显示
  - 不需要专用 LED driver
```

## 调试步骤

1. **量天线阻抗**：VNA 验证 S11 < -10 dB
2. **看 Coordinator**：手机 / PC 找 Coordinator 节点，看 PAN ID
3. **End Device 入网**：触发入网，看 Beacon Request → Association Response
4. **看 NWK 路由**：抓包看 NWK 帧 src/dst 地址，理解路径
5. **看 ZCL 流量**：On/Off Cluster 读写是否成功
6. **看 End Device 睡眠**：功率分析仪看睡眠周期是否符合预期
7. **看 Trust Center**：是否有 APS Encrypt Transport Key 流程

## 常见问题速查

| 现象 | 优先检查 |
| --- | --- |
| End Device 不入网 | Coordinator 信道 / Channel Mask / 距离 |
| 入网后掉线 | PAN ID 冲突 / 路由断开 / 睡眠参数错 |
| ZCL 命令无响应 | Bind 失败 / Cluster ID 错 / End Point 错 |
| End Device 撑不过 1 周 | Poll Control 错配 / 一直唤醒 |
| Coordinator 看不到 | 信道错 / TX Power 0 / 固件崩溃 |
| 多 Coordinator 冲突 | Channel Mask 没限 / 邻居 PAN 干扰 |
| OTA 失败 | 镜像签名错 / OTA Cluster 没配 |
| 配对 / 鉴权失败 | Trust Center Link Key / Install Code |
| CC2530 P0_4 端口异常 | 硬件 bug：P0_4 不能用作 GPIO，I2C 也不稳 → 换 P0_5/P0_6 |
| 改 PANID 后老节点不重连 | 协调器改 PANID 后**必须 AT+RESET**，老终端 NV_RESTORE 才生效 |
| NV_RESTORE 行为异常 | 三种断电场景下短地址变化：电源波动 / 软复位 / 硬复位，分情况查 |
| 串口接 DL-20 收不到数据 | USB-TTL 电平不匹配（CH340 是 3.3V/5V，DL-20 是 TTL），换直连串口 |
| 协调器断电后终端 ORPHAN 回调触发 | 在 ORPHAN_Indication 里强制复位终端重新入网（zgWriteStartupOptions） |
| 终端改 Beacon 周期 | 改 zgDefaultStartingScanDuration（默认 5）→ 8 减少漏入网 |
| ZED 串口唤醒只保 3s 同步窗口 | 3 次接收后不再接收，Zigbee 同步广播丢 2-3 字节 → 业务层加 buffer 累积 |
| WiFi 1/6/11 干扰 Zigbee | WiFi 信道避让：Zigbee 选 11/15/20/26（避开 WiFi 1/6/11 谐波） |
| ch340 不能给 Zigbee 模组供电 | 用 pl2303 / FTDI 替代（ch340 电流 100mA 不足，Zigbee 模组峰值 200mA） |
| CH582 RISC-V 自定义 Service | profile/setup.c 注册 service + 读写回调，BLE+USB 复合设备描述符 |

## 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 设备不入网 | Coordinator 找不到 / 信道错 | Channel Mask + 距离 |
| 反复掉线 | ReJoin 失败 | 看 APS Trust Center 流程 |
| 路由跳数大 | 拓扑差 | 减少物理距离 / 加 Router |
| 设备一直醒 | Poll Control 错 | 设 End Device Poll Interval |
| ZCL 命令无响应 | Bind 错 | Active EP + Bind Table |
| NCP crash | assert / 看门狗 | SWO 抓 log |
| End Device 频繁 Orphan | 父节点 Router 掉线 | 加 Router 备份 |
| 配对失败 | Install Code 错 | 检查 Trust Center 配置 |
| 距离近 | TX Power 限 | 检查 dBm 设置 + 天线 |

## NWK Status 速查

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x00 | SUCCESS | 正常 |
| 0x01 | INV_REQUESTTYPE | 错误的请求类型 |
| 0x02 | DEVICE_NOT_FOUND | 找不到目标设备 |
| 0x03 | INVALID_EP | End Point 无效 |
| 0x04 | NOT_ACTIVE | 节点不活跃 |
| 0x05 | NOT_SUPPORTED | 不支持 |
| 0x06 | TIMEOUT | 超时（典型：APS ACK 未收到） |
| 0x07 | NO_MATCH | 不匹配 |
| 0x08 | NO_ENTRY | 无 entry（Bind 缺失） |
| 0x09 | NO_DESCRIPTOR | 无 descriptor |
| 0x0A | INSUFFICIENT_SPACE | 空间不足 |
| 0x0B | NOT_PERMITTED | 不允许 |
| 0x0C | PARENT_LINK_FAILURE | 父节点链路失败（Orphan 触发） |
| 0x0D | PARENT_NOT_SUPPORTING | 父节点不支持入网请求 |
| 0x0E | NONSELF_ADDRESSED | 不是发给自己的 |
| 0xC1 | NWK_TABLE_FULL | 路由表满 |
| 0xC2 | DISCOVERY_TIMEOUT | 路由发现超时 |
| 0xC3 | BUFFER_FULL | 队列满 |
| 0xD0 | ROUTE_ERROR | 路由错误 |
| 0xD1 | SOURCE_ROUTE_FAILURE | 源路由失败 |

## APS Status 速查

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x00 | SUCCESS | 正常 |
| 0xA0 | ASDU_TOO_LONG | APS SDU 太长 |
| 0xA1 | DEFRAG_DEFERRED | 分片延迟 |
| 0xA2 | DEFRAG_UNSUPPORTED | 不支持分片 |
| 0xA3 | ILLEGAL_REQUEST | 非法请求 |
| 0xA4 | INVALID_BINDING | Bind 无效 |
| 0xA5 | INVALID_GROUP | Group 无效 |
| 0xA6 | INVALID_PARAMETER | 参数错 |
| 0xA7 | NO_ACK | 没收 ACK |
| 0xA8 | NO_BOUND_DEVICE | 设备未 Bind |
| 0xA9 | NO_SHORT_ADDRESS | 短地址无效 |
| 0xAA | NOT_SUPPORTED | 不支持 |
| 0xAB | SECURED_LINK_KEY | 安全 Link Key 错 |
| 0xAC | SECURED_NWK_KEY | 安全 Network Key 错 |
| 0xAD | SECURITY_FAIL | 安全失败 |
| 0xAE | TABLE_FULL | Bind 表满 |
| 0xAF | UNSECURED | 不安全请求 |
| 0xB0 | UNSUPPORTED_ATTRIBUTE | 属性不支持 |

## ZCL Status 速查

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 0x00 | SUCCESS | 正常 |
| 0x01 | FAILURE | 通用失败 |
| 0x70 | NOT_AUTHORIZED | 未授权 |
| 0x7E | RESERVED_FIELD_NOT_ZERO | 保留字段非 0 |
| 0x7F | MALFORMED_COMMAND | 命令格式错 |
| 0x80 | UNSUP_GENERAL_COMMAND | 不支持的通用命令 |
| 0x81 | UNSUP_MANUF_CLUSTER_COMMAND | 不支持的厂商特定命令 |
| 0x82 | UNSUP_MANUF_GENERAL_COMMAND | 不支持的厂商通用命令 |
| 0x83 | INVALID_FIELD | 字段无效 |
| 0x84 | UNSUPPORTED_ATTRIBUTE | 属性不存在 |
| 0x85 | INVALID_VALUE | 值无效 |
| 0x86 | READ_ONLY | 只读 |
| 0x87 | INSUFFICIENT_SPACE | 空间不足 |
| 0x88 | DUPLICATE_EXISTS | 重复（建 Group） |
| 0x8A | NOT_FOUND | 找不到（读属性） |
| 0x8B | UNREPORTABLE_ATTRIBUTE | 不可报告属性 |
| 0x8C | INVALID_DATA_TYPE | 数据类型错 |

## End Device 睡眠参数

```c
// Z-Stack / EmberZNet 关键参数
#define ZG_END_DEV_POLL_INTERVAL    3000    // 3s（典型）
#define ZG_END_DEV_KEEPALIVE        7000    // 7s
#define ZG_END_DEV_REJOIN_ATTEMPTS  3
#define ZG_END_DEV_REJOIN_INTERVAL  30      // 30s
#define ZG_END_DEV_MAX_PARENT_THRSH 3       // 父节点失败 3 次换父

// 实际功耗估算：
// 3s 唤醒 + 30ms 通信 = 1% duty
// 平均 30 µA（纽扣电池可撑 1 年）
```

**关键约束**：

- End Device 必须 **PollInterval < Parent NWK Link Status Timeout**（默认 16s）
- End Device 必须 **Keepalive < Rejoin Interval × Rejoin Attempts**（默认 7 < 30×3）
- 父节点 Router 掉线触发 Orphan → ReJoin → ReJoin 失败 N 次后 Network Discovery

## Trust Center 与安全

```text
TC Link Key（Default Well-Known）：
  5A 69 67 42 65 65 41 6C 6C 69 61 6E 63 65 30 39（"ZigBeeAlliance09"）
  仅生产阶段使用，量产前必须改

Install Code：
  16 字节唯一码 + 16 字节 CRC
  入网时由 Trust Center 验证
  量产推荐用 Install Code + Dynamic Link Key
```

**实际配置**：

```c
// Z-Stack: 启用 Install Code
#define TC_LINKKEY_JOIN  1
#define SECURE_LINK_KEY  1  // 每设备独立 Link Key

// EmberZNet: 启用 Install Code
// 1. 写 install code 到 NV
// 2. 调 emberTrustCenterAddInstallCode(ieee, installCode, installCodeSize)
// 3. 设备入网时自动用 install code 派生 link key
```

## EFR32 NCP 调试专项

**EFR32 跑 NCP 模式（不是 SoC）**：

```c
// NCP 跑协议栈，主机 MCU 跑应用
// 主机通过 UART 调 EZSP / CPC 命令
// 协议栈 crash 时，NCP 重启但主机不感知
```

**必备调试准备**：

1. **保留 SWO 引脚**（10-pin Simplicity Connector 至少留 SWO / SWDIO / SWCLK / GND）
2. **启用 ncp-debug-print 插件**：在 Simplicity Studio 中 `emberMinimal` + `printf` + `serial` 三个插件必须同开
3. **崩启用看门狗**：NCP 模式 assert/CRS/SW 重启必须靠 SWO 抓 log

**AN958 推荐的 10-pin Simplicity Connector**：

```text
Pin 1: VDD       Pin 2: GND
Pin 3: SWDIO     Pin 4: SWCLK
Pin 5: SWO       Pin 6: NC
Pin 7: NC        Pin 8: GND
Pin 9: RST       Pin 10: GND
```

## 调试检查清单

```text
□ 电源：1.7~3.8V 稳压，纹波 < 50mV
□ 去耦：每个 VDD 引脚 100nF + 10µF 紧靠
□ 天线：50Ω 匹配，VNA 验证 S11 < -10dB
□ 晶振：38.4 MHz + 32.768 kHz，匹配电容精准
□ Reset：10kΩ 上拉
□ DC-DC：EFR32 需 L/C 滤波器
□ 协议栈：Z-Stack 3.0+ / EmberZNet 7+（支持 ZigBee 3.0）
□ 信道：避 Wi-Fi 1, 6, 11（11, 20, 25）
□ PAN ID：固定值 + 不与邻居冲突
□ Channel Mask：限制可用信道
□ Trust Center：Link Key 改 + Install Code 验证
□ End Device 睡眠：PollInterval 配对 Keepalive
□ 抓包：Ubiqua / nRF Sniffer / Wireshark
□ 错误码：NWK / APS / ZCL 三套错误码都要能解析
□ NCP：留 SWO + 启用 ncp-debug-print
```

## 关联文档

- `bus/zigbee.md` 主题入口
- `bus/zigbee-deep-dive.md` 协议栈深挖
- `bus/zigbee-failure-cases.md` 产线实战案例
- `bus/zigbee-index.md` 主题地图 + 导航
