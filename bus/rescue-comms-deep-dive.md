# Rescue Communications 协议深挖

## 目标

从协议栈、链路层、物理层、安全、加密、QoS、多模融合等维度深挖救援通讯的工程实现。适合做卫星模组、PLB、应急终端嵌入式固件的工程师。

## 1. 卫星 SOS 双向链路深挖

### 1.1 Iridium（铱星）LEO 星座

Iridium 是 66 颗低轨卫星（LEO, Low Earth Orbit）+ 9 颗在轨备份，轨道高度 780 km，覆盖全球（含南北极）。频段 1616~1626.5 MHz（L 频段），时分多址 TDMA + 频分多址 FDMA，每颗星 48 个波束。

```text
终端 ↔ 卫星（Ka/L 频段）↔ 地面关口站（K 频段）↔ 公网
       ↑             ↑
       1616-1626.5 MHz
       1.616 GHz 上下
```

关键参数：

- 端到端延迟：1.2 s（极地）~ 5 s（赤道）
- 切换频率：每 7~10 min 一次星间切换（LEO 高速运动）
- SBD 协议：基于 Iridium IX 协议 v2.0，单条消息 < 1960 字节
- MO (Mobile Originated) / MT (Mobile Terminated) 双方向

**Iridium 9602/9603 模组关键命令**：

```text
AT+CIER=1,1,1      # 启用 SBD 状态指示
AT+CSQ             # 信号强度（0~5，最后 99 = 未知）
AT+SBDWT=<b64>     # 写 SBD 消息缓冲
AT+SBDIX=A         # 发起 SBD 收发
AT+SBDRT           # 读收到的 SBD 消息
AT+SBDDST           # 清 SBD 缓冲
```

**SBD 状态寄存器**：

```text
+SBDIX: <MO_status>, <MOMSN>, <MT_status>, <MTMSN>, <RA>, <T>
MO_status:
  0  MO 消息发送成功
  1  MO 消息发送中
  2  MO 消息错（详见错误码）
MT_status:
  0  无新消息
  1  有新消息
```

### 1.2 北斗 RDSS（Beidou Radio Determination Satellite Service）

北斗-3 一大特色是**有源定位 + 短报文合一**。GEO（Geostationary Orbit，地球静止轨道）卫星 3 颗，IGSO（Inclined Geosynchronous Orbit，倾斜地球同步轨道）3 颗，MEO（Medium Earth Orbit，中圆地球轨道）24 颗。RDSS 用 GEO/IGSO 双星定位。

```text
用户 → 卫星（上行 L/S 频段）→ 主站（中国卫通）
    → 注入站 → 卫星 → 用户（下行）
```

关键参数：

- 工作频段：上行 1610~1626.5 MHz / 下行 2483.5~2500 MHz
- 定位原理：双星测距 + 高程数据库
- 短报文：1000 汉字 / 14 次/分钟 / 70 次/小时
- 入网延迟：< 5 s
- 抗干扰：BPSK（Binary Phase Shift Keying，二进制相移键控）扩频
- 加密：用户卡内置 SM4 算法

**RDSS 与 GPS 差异**：

```text
GPS     : 无源定位，仅下行，用户不上行
RDSS    : 有源定位 + 短报文，用户必须上行发射
GLONASS : 无源定位
Galileo : 无源定位
```

### 1.3 Apple Emergency SOS 卫星链路

iPhone 14 起内嵌 Globalstar 卫星调制解调器（S 频段上行 / L 频段下行），不依赖运营商。

```text
iPhone (S 频段 2483.5 MHz)
    ↓
Globalstar 第二代 24 颗 LEO 卫星
    ↓
地面站
    ↓
iPhone 紧急联系人 / 救援中心
```

**协议设计**：

- 自定义协议，不公开
- 消息压缩到 140 字符以内（含位置）
- 中继方式：卫星 → 地面站 → 公网 → Apple 紧急服务
- 仅在"完全无蜂窝"时自动激活
- 5 秒自动发送位置（无用户操作）

**预填问卷机制**：

- iOS Health App 填"医疗 ID"（血型、过敏、病史、紧急联系人）
- 触发 SOS 时一并发送，节省信道
- 中英文双语同步

### 1.4 Garmin inReach / Iridium SBD 双向

Garmin 用 Iridium 9602/9603 模组做嵌入式，整机功耗做到 30 天待命。inReach Messenger 通过蓝牙连手机 App，用户写消息 → 蓝牙 → inReach → Iridium。

**预设消息优化**：

```text
预设消息（presets）：
- "OK"（免费）→ 卫星 1 hop
- "Starting trek"（免费）→ 卫星 1 hop
- "Need help"（付费）→ 卫星 1 hop + ACK
- "SOS"（紧急）→ 卫星 1 hop + 救援中心
```

每条预设消息经过 Iridium 压缩到 20 字节以内，链路建立时间 < 30 s。

## 2. 短报文 SBD 协议深挖

### 2.1 Iridium SBD 协议栈

```text
应用层    : 业务数据（位置 / 状态 / 报警）
           ↓
传输层    : SBD 协议（基于 IX 协议 v2.0）
           - MO: Mobile Originated
           - MT: Mobile Terminated
           - MOMSN/MTMSN 消息序号
           ↓
链路层    : L 频段 TDMA/FDMA
           - 4 帧/突发 × 8.28 ms/帧 = 33 ms/突发
           - 50 kHz 信道 × 240 信道/星
           ↓
物理层    : QPSK（Quadrature Phase Shift Keying，四进制相移键控）/ DE-QPSK
           - 50 kbaud 符号率
           - 卷积码 FEC（Forward Error Correction，前向纠错） r=1/2, k=7
```

**关键设计权衡**：

- L 频段 1.6 GHz 是低频，路径损耗小，但带宽窄
- 50 kbaud × FEC 1/2 = 25 kbps 物理层，实际 SBD 协议 overhead 后 9.6 kbps
- 高仰角比低仰角 SNR（Signal-to-Noise Ratio，信噪比）好 10 dB

### 2.2 北斗短报文协议

```text
应用层    : 用户消息（最长 1000 汉字）
           ↓
编码层    : SM4 加密（用户卡内置密钥）
           ↓
链路层    : CDMA（Code Division Multiple Access，码分多址）扩频
           - 扩频码长 1024/2048 chips
           - 频度 1 Hz（1 次/秒）
           ↓
物理层    : L 频段 1.6 GHz 上行
           - BPSK 调制
           - 发射功率 5W~10W EIRP
```

**频度限制**：

- 1 Hz 是核心限制，避免信道拥塞
- 群发场景：14 次/分钟 = 4.3 s/次
- 长消息拆分后总频次需自验

### 2.3 Inmarsat IsatData Pro

Inmarsat 是 GEO 卫星（静地轨道，36 000 km 高度），3 颗主星 + 4 颗备份。IsatData Pro 是双向短报文协议。

```text
终端 (L 频段 1.5/1.6 GHz)
    ↕
Inmarsat I-4 GEO
    ↕
地面站（PSN，Packet Switching Node）
    ↕
公网 / 业务平台
```

关键参数：

- MO：6.4~16 KB
- MT：10~32 KB
- 延迟：15~60 s（LEO 模式 < 1 s）
- 终端：模组 + 卫星天线（碟形）
- 优势：单消息体积大，适合物流
- 劣势：终端贵（> 1000 USD），重量大

## 3. PLB 406 MHz 协议深挖

### 3.1 COSPAS-SARSAT 系统架构

```text
PLB 发射 406 MHz 短脉冲
    ↓
LEO 卫星（6 颗，800 km 高度）+ GEO 卫星（5 颗，36 000 km）
    ↓
数据下传到 LUT（Local User Terminal，本地用户终端）
    ↓
MCC（Mission Control Center，任务控制中心）分发
    ↓
RCC（Rescue Coordination Center，救援协调中心）→ 救援队
```

**LEO 卫星**：极轨，高度 800~850 km，能全球覆盖但有时间窗口
**GEO 卫星**：36 000 km，全球覆盖但定位精度低

**LEO + GEO 双模定位**：

- 仅 LEO：多普勒定位，精度 5 km
- 仅 GEO：频率 + 时间，精度 10 km
- LEO + GEO：精度 1~2 km
- GPS 集成：精度 < 100 m（现代 PLB 标配）

### 3.2 406 MHz 协议

```text
短脉冲：5 W 脉冲，520 ms / 周期
   - 短报文：112 bits（无 GPS）
   - 长报文：144 bits（含 GPS）
   - 长报文：含 30 字符 ASCII 自由文本
   - 编码：Biphase-L
   - 错误校验：BCH（255, 144）

时间窗口：50 s ± 5%（LEO 卫星可见时间）
频率稳定度：± 50 ppb（parts per billion，十亿分之一）
```

**406 MHz 协议字段**（长报文）：

```text
[Bit 0-15]    : 同步码（0001 1010 1100 1100）
[Bit 16-24]   : 协议标志（EPIRB / PLB / ELT）
[Bit 25-85]   : 国家码 + 用户 ID
[Bit 86-107]  : 位置（GPS 数据，22 bits）
[Bit 108-129] : 自由文本 / 国家特定
[Bit 130-143] : BCH 校验
[Bit 144]     : 同步码
```

**121.5 MHz 副载波**：

- 用于 SAR 直升机定向
- 模拟信号，连续发射
- 范围 5~10 km
- 飞机接近后才有意义

### 3.3 EPIRB vs PLB vs ELT

| 设备 | 用途 | 频率 | 触发 |
| --- | --- | --- | --- |
| PLB | 个人 | 406 MHz | 手动 |
| EPIRB | 船用 | 406 MHz | 浸水 / 手动 |
| ELT | 飞机 | 406 MHz | 撞击 / 手动 |

**EPIRB 自动释放**：

- 水银开关 + 海水电池
- 船沉时自动浮出水面 + 自动启动
- 船用 5 W，射程 800 km（LEO 可见）

## 4. 应急蜂窝深挖

### 4.1 VoLTE Emergency

3GPP TS 23.167 定义 IMS（IP Multimedia Subsystem，IP 多媒体子系统）紧急呼叫流程：

```text
UE (User Equipment，用户设备) → eNodeB (4G 基站) → EPC (Evolved Packet Core，演进分组核心网)
                                          ↓
                                    E-CSCF (Emergency CSCF，紧急呼叫会话控制功能)
                                          ↓
                                    PSAP (Public Safety Answering Point，公共安全应答点)
                                          ↓
                                    救援机构
```

**关键特性**：

- 优先 QoS：QCI（QoS Class Identifier，服务质量等级标识）= 5（IMS 信令） + QCI = 1（语音）
- 即使网络拥塞也会接通
- 携带 GPS / Cell-ID 位置（精度 50~500 m）
- 回落 2G/3G CS（电路交换） fallback

**E911 vs E112**：

- 美国 E911：必须有 GPS 或运营商位置
- 欧洲 E112：到 2024 已部分实现 AML（Advanced Mobile Location，先进移动定位）
- 中国 110/119/120/122：尚未完整 E911 实现

### 4.2 卫星 IoT 备份

3GPP Release 17 起把 NTN（Non-Terrestrial Network，非地面网络）纳入 5G 体系。手机直连卫星的标准化路径：

```text
R17 (2022) : NTN 基本框架（IoT）
R18 (2024) : NR-NTN（语音/数据）
R19 (2025) : 增强（多卫星、Ka 频段）
```

**当前卫星 IoT 平台**：

| 平台 | 频段 | 数据率 | 覆盖 |
| --- | --- | --- | --- |
| Astrocast | L 频段 | 0.5 kbps | 全球 |
| Swarm | VHF 频段 | 1 kbps | 全球 |
| Myriota | L 频段 | 0.1 kbps | 全球 |
| Iridium SBD | L 频段 | 9.6 kbps | 全球 |
| 北斗短报文 | L 频段 | 几 kbps | 亚太 |
| NB-IoT NTN | L/S 频段 | 26 kbps DL/62 kbps UL | 测试中 |

## 5. 户外对讲深挖

### 5.1 业余无线电 VHF/UHF

HAM 频段：

```text
2 m   : 144~148 MHz（VHF 段，城市/中等距离）
70 cm : 420~450 MHz（UHF 段，短距/中继）
6 m   : 50~54 MHz（VHF 段，DX 远距离）
1.25 m: 222~225 MHz（UHF 段）
23 cm : 1240~1300 MHz（UHF 段）
```

**关键协议**：

- FM 模拟：25 kHz 带宽
- C4FM（Continuous 4-level FM，连续 4 电平调频）：Yaesu System Fusion
- D-STAR：ICOM 数字
- DMR（Digital Mobile Radio，数字移动无线电）：业余 + 商业
- P25：APCO（Association of Public-Safety Communications Officials，公共安全通信官员协会）公共安全

**应急中继**：

- ARES（Amateur Radio Emergency Service，业余无线电应急服务）：美国 HAM 应急
- RACES：Radio Amateur Civil Emergency Service，业余无线电民事应急服务
- 中国 BY 应急：HAM 联盟救援

### 5.2 海上 VHF DSC

DSC（Digital Selective Calling）是 ITU-R M.493 标准，工作在 VHF 156 MHz：

```text
频道 70 (156.525 MHz) : DSC 专用
频道 16 (156.800 MHz) : 语音呼叫 + 紧急
频道 06 (156.300 MHz) : 船-船安全
```

**DSC 协议**：

```text
[同步 100 bits] [定址 5~9 位] [类别] [消息类型] [位置] [时间] [EOS]
```

**MMSI（Maritime Mobile Service Identity）**：

- 9 位数字，全球唯一
- 船台 MID（Maritime Identification Digits，海上识别数字） + 6 位 ID
- 岸台 MID + 0 + 4 位 ID
- 中国 MID 412~414

**DSC 测试**：

- 频道 70 发送测试帧
- 收到 ACK 即通过
- 不可在频道 16 长时间测试

### 5.3 卫星电话深挖

Iridium 9555 / 9575 Extreme 关键参数：

```text
工作频段 : 1616~1626.5 MHz
调制     : DE-QPSK
多址     : TDMA/FDMA
语音编码 : AMBE（Advanced Multi-Band Excitation，高级多带激励）2.4 kbps / MELPe 1.2 kbps
数据率   : 2.4 kbps 语音 / 9.6 kbps 数据
发射功率 : 1W 平均 / 7W 峰值
天线     : 折叠式全向 / 拉杆高增益
电池     : 2300 mAh，30 小时待命，4 小时通话
```

Thuraya XT-LITE 关键参数：

```text
工作频段 : L 频段 1525~1559 MHz / 1626.5~1660.5 MHz
覆盖     : 亚非欧 + 澳洲（无南北美）
卫星     : 2 颗 GEO
数据率   : 9.6 kbps 数据
电池     : 6 小时通话 / 80 小时待命
```

## 6. 端到端加密

### 6.1 加密要求

- 不依赖地面网络（卫星链路加密不经过公网）
- 抗截获：位置 + 内容不暴露
- 抗胁迫：被劫持时能秘密报警
- 抗重放：消息序号 + 时间戳
- 密钥周期：24h 更换

### 6.2 加密算法

| 协议 | 算法 | 密钥长度 | 备注 |
| --- | --- | --- | --- |
| 北斗 RDSS | SM4 | 128 bits | 国密 |
| Iridium SBD | AES-256 | 256 bits | 应用层 |
| PLB 406 MHz | 无 | - | 协议明文，靠 BCH 纠错 |
| Apple Emergency SOS | 私有 | 未知 | 不公开 |
| Garmin inReach | AES-256 | 256 bits | 应用层 |
| DSC | 无 | - | 明文，仅频段隔离 |

### 6.3 抗胁迫设计

```text
普通 SOS：求救信号 → 救援中心
抗胁迫 SOS：求救信号 + 隐含信号 → 救援中心识别
         例：发送"OK"时附带双击 → 实际是"SOS"
```

实际产品（如 inReach）通过"预设消息 + 隐含触发"实现，例：

- "I'm OK, please call my wife" → 实际被劫持，发短信给妻子
- 5 秒内连按 SOS 键 3 次 → 强制报警（即使 UI 被锁）

## 7. 电池续航设计

### 7.1 PLB 5 年待命

```text
PLB 待机电流 < 5 µA（GPS 模块关）
GPS 工作电流 < 50 mA（捕获）
406 MHz 发射电流 < 1 A × 520 ms / 50 s = 10 mA 平均
24h 发射电池容量 = 10 mA × 24 h = 240 mAh
5 年待机电池 = 5 µA × 5 × 365 × 24 = 219 mAh

总电池 = 240 + 219 = 459 mAh → 选 1000 mAh Li-SOCl2 留 2× 余量
```

**Li-SOCl2（锂亚硫酰氯电池）**：

- 自放电率 < 1%/年（业界最佳）
- 工作温度 -40°C ~ +85°C
- 能量密度 700 Wh/kg
- PLB 标配

### 7.2 inReach 14 天待命

```text
inReach Mini 2 跟踪模式（10 min 间隔）：
  GPS 锁定 : 30 mA × 5 s / 600 s = 0.25 mA 平均
  Iridium 发射 : 1 A × 1 s / 600 s = 1.67 mA 平均
  模组待机 : 35 µA ≈ 0
  MCU + BLE 待机 : 200 µA
  总平均 : 2.12 mA

电池 2200 mAh / 2.12 mA = 1037 h = 43 天（实测 14 天，余量给低温）
```

## 8. 多模融合

### 8.1 优先级架构

```text
启动顺序（户外终端）：
  1. 蜂窝（4G/5G）: 有则用
  2. Wi-Fi: 营地近距离
  3. BLE Mesh: 队友间（< 100 m）
  4. 卫星 SBD: 兜底 1
  5. 卫星短报文（北斗 RDSS）: 兜底 2
  6. PLB 406 MHz: 兜底 3（最后）

链路切换触发：
  - 链路质量（RSSI < -110 dBm）→ 切下一档
  - 链路超时（> 60 s）→ 切下一档
  - 用户手动：可强制选某一档
```

### 8.2 端到端 QoS

```text
优先级:
  P0: SOS 求救（1 s 内必发）
  P1: 位置追踪（10 s 内必发）
  P2: 状态消息（1 min 内）
  P3: 自由消息（5 min 内）

带宽分配:
  P0 → 100% 带宽（抢占）
  P1 → 30% 带宽
  P2 → 5% 带宽
  P3 → 1% 带宽
```

### 8.3 融合芯片

目前业界趋势：单芯片多模融合

- **Qualcomm 9205**：LTE-M + NB-IoT + GNSS（Global Navigation Satellite System，全球导航卫星系统）
- **MediaTek MT6825**：3GPP NTN（卫星 IoT）+ GNSS
- **Nordic nRF9151**：LTE-M + NB-IoT + GNSS（无卫星 IoT）
- **Astrocast ASIC**：L 频段卫星 IoT + GNSS
- **u-blox SARA-S528N3**：3GPP NTN
- **华为巴龙 700 / 麒麟 9000S**：蜂窝 + 北斗 RDSS

## 9. 抓包 / 协议分析

### 9.1 SDR 抓 406 MHz

RTL-SDR V3（30 USD）+ 406 MHz 带通滤波器（10 USD）：

```text
天线 → 滤波器 → LNA (Low Noise Amplifier，低噪声放大器) → RTL-SDR → PC
```

软件：

- SDR# (SDRSharp)
- SatDump（COSPAS-SARSAT 协议解析）
- 自写 Python 脚本（用 `pyrtlsdr`）

**关键帧**：

```text
[前导码 80 bits] [同步码 32 bits] [数据 144 bits] [BCH 校验] [结束]
```

### 9.2 Iridium SBD 抓 log

```python
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
# 启用 verbose SBD log
ser.write(b'AT+CIER=1,1,1\r\n')
print(ser.read(100))

# 发起 SBD
ser.write(b'AT+SBDWT=Ikdvcmtz\r\n')  # base64 "work"
print(ser.read(100))
ser.write(b'AT+SBDIX=A\r\n')
print(ser.read(200))  # 期待 +SBDIX: 0, 1, 1, 0, 0, 0
```

### 9.3 北斗 RDSS 抓 log

```text
命令 : $BDRDSS,<length>,<payload>*<checksum>\r\n
响应 : $BDRDSS,<length>,<payload>*<checksum>\r\n
```

抓 log 后看响应：

```text
发送位置：$BDRDSS,32,1122334455...*XX
接收位置：$BDRDSS,32,OK*XX
```

## 10. 应急链路设计模式

### 10.1 自动 SOS

```c
void emergency_sos_handler(void) {
    // 1. GPS 锁定
    if (!gps_lock()) {
        gps_warm_start();
        if (!gps_lock()) {
            // 2. 走蜂窝 Cell-ID
            cell_id = get_cell_id();
            location = cell_id_to_loc(cell_id);
        }
    }
    
    // 3. 链路优先级选路
    if (cell_available()) {
        send_sos_via_cell();
    } else if (sat_sbd_available()) {
        send_sos_via_sbd();
    } else if (beidou_available()) {
        send_sos_via_beidou();
    } else {
        activate_plb();  // 最后兜底
    }
}
```

### 10.2 抗误触

```c
// SOS 键防误触
bool sos_long_press_detect(void) {
    if (sos_pin_low_for_5s()) {
        return true;  // 真按
    }
    return false;  // 误触
}

// 二次确认
if (sos_long_press_detect()) {
    vibrate(1, 200);
    if (sos_long_press_detect_again()) {
        trigger_sos();
    }
}
```

### 10.3 抗误报

PLB 误报率 95%+ 是业界痛点，COSPAS-SARSAT 数据：

```text
每年全球 PLB 触发 : 1500+ 次
实际救援需求 : < 100 次
误报率 : > 90%
```

**抗误报设计**：

- 长按 5 s 启动
- 二次确认
- 倒计时 30 s 取消
- 防水 + 跌落 + 多传感器确认

## 11. 法规与认证

### 11.1 卫星频段许可

- Iridium：美国 FCC 许可，中国工信部限制使用
- 北斗：中国自主，无许可问题
- Globalstar：FCC 许可
- Inmarsat：英国/美国许可

### 11.2 PLB 注册

- 406registration.com（COSPAS-SARSAT 官方）
- 中国由交通运输部救援中心注册
- 必须登记用户信息 + 紧急联系人

### 11.3 DSC 船检

- 中国船检局（CCS）认证
- 国际海事组织（IMO）SOLAS（International Convention for the Safety of Life at Sea，国际海上人命安全公约）公约
- GMDSS（Global Maritime Distress and Safety System，全球海上遇险与安全系统）认证

## 12. 未来趋势

- **3GPP NTN 全面落地**：5G Release 19+ 全面支持手机直连卫星
- **LEO 巨型星座**：Starlink V2 + 华为 Mate 60 Pro + Apple Emergency SOS 推动消费级卫星
- **AI 边缘求救**：设备自动判断危险（加速度、心率、温度）后自动 SOS
- **量子加密**：未来 5~10 年救援链路可能用 QKD（Quantum Key Distribution，量子密钥分发）
- **太阳能 + 长续航**：户外终端集成太阳能，告别电池焦虑

## 关联文档

- `bus/rescue-comms.md` 主题入口
- `bus/rescue-comms-practical.md` 调试速查
- `bus/rescue-comms-failure-cases.md` 实战案例
- `bus/rescue-comms-index.md` 主题地图
