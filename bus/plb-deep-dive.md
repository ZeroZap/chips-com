# PLB Deep Dive

## 目标

深入 PLB 技术体系：COSPAS-SARSAT 卫星系统架构、406 MHz 信号物理层、BCH 纠错、UIN 编码规则、GNSS 集成、多普勒定位原理、121.5 MHz 测向原理。目标读者：PLB 固件 / 硬件 / 协议工程师、卫星通讯 / 应急救援设备认证工程师。

## COSPAS-SARSAT 系统架构

COSPAS-SARSAT（COSPAS 是俄语 Cosmicheskaya Sistema Poiska Avariynyh Sudov 的缩写，意为"搜救卫星系统"；SARSAT 是 Search And Rescue Satellite Aided Tracking）是由 4 个国家（俄罗斯、加拿大、法国、美国）和 30+ 国家组织联合运行的国际人道救援卫星系统。

### 整体架构

```text
        ┌─────────────────────────────────────────────┐
        │  Space Segment 卫星段                        │
        │  ┌─────────────┐  ┌─────────────┐            │
        │  │ LEOSAR      │  │ GEOSAR      │            │
        │  │ 低轨道 850km │  │ 静轨 36000km│            │
        │  │ SARR 仪器   │  │ SARR 仪器   │            │
        │  │ 6 颗现役    │  │ 8 颗现役    │            │
        │  └──────┬──────┘  └──────┬──────┘            │
        └─────────┼────────────────┼───────────────────┘
                  │ 406 MHz (PLB 上行)
                  │ 1544.5 MHz (LEO 转发到 LUT)
                  │ 1544.5 MHz (GEO 直接到 LUT)
        ┌─────────┼────────────────┼───────────────────┐
        │ Ground Segment 地面段                         │
        │  ┌──────────────┐  ┌──────────────┐           │
        │  │ LEOLUT        │  │ GEOLUT        │          │
        │  │ 接收 SARR     │  │ 接收 SARR     │          │
        │  │ 解 BCH + 多普 │  │ 解 BCH        │          │
        │  │ 勒定位        │  │ 时间标签      │          │
        │  └──────┬───────┘  └──────┬───────┘           │
        │         └──────┬───────────┘                  │
        │                ↓                              │
        │         ┌──────────────┐                      │
        │         │ MCC 任务控制 │                      │
        │         │ 全球 30+ 节点│                      │
        │         └──────┬───────┘                      │
        │                ↓                              │
        │         ┌──────────────┐                      │
        │         │ RCC 救援协调 │                      │
        │         │ → SAR 队伍   │                      │
        │         └──────────────┘                      │
        └─────────────────────────────────────────────┘
                  ↑                        ↑
                  │ 121.5 MHz 测向         │
                  │  (最后 5~10 km)        │
            ┌─────┴──────┐           ┌─────┴──────┐
            │ 飞机       │           │ 船舶       │
            │ 救援队     │           │ 救援队     │
            └────────────┘           └────────────┘
```

### LEO 卫星

- **轨道高度**：850~1000 km 极轨道
- **周期**：~100 分钟
- **现役卫星**（截至 2026）：6 颗搭载 SARR 仪器
- **覆盖**：每颗过顶时延 < 1 小时（最坏 4 小时，极地 < 30 min）
- **特点**：可多普勒定位（PLB 静止时，卫星相对运动导致频率偏移）

### GEO 卫星

- **轨道高度**：35,786 km 赤道静轨道
- **现役卫星**：8 颗（GOES 系列、MSG 系列、Elektro 系列、Louch 系列）
- **覆盖**：除极地外全球无缝
- **特点**：立即接收（无多普勒），但极地盲区
- **PLB 报告内容**：UIN + GNSS 位置（PLB 自带 GNSS 时）

### 中轨道 MEOSAR（2024+）

- **轨道高度**：19,000~23,000 km 中轨
- **代表**：Galileo SAR 服务（欧盟，全球 24 颗）
- **GLONASS SAR**（俄罗斯）
- **GPS SAR**（美国）
- **优势**：LEO + GEO 优势合并，全球无缝 + 多普勒定位 + 即时接收

### LEOLUT / GEOLUT

**LEOLUT (LEO Local User Terminal)**：

- 全球部署 50+ 个
- 接收 SARR 卫星转发的 1544.5 MHz 信号
- 计算 PLB 报文 + 多普勒频移 → 经度纬度（无 GNSS 时定位精度 ±5 km）
- 数据送到 MCC

**GEOLUT (GEO Local User Terminal)**：

- 全球部署 30+ 个
- 接收 GEO SARR 直接下行的 1544.5 MHz
- 解析 PLB 报文 + GNSS 位置（PLB 自带 GNSS）
- 数据送到 MCC

### MCC / RCC

- **MCC (Mission Control Center)**：全球 30+ 个国家各 1 个，节点互联
- **RCC (Rescue Coordination Center)**：救援协调中心，1 国家 1 个（中国由交通运输部南海救助局负责）
- **数据流**：LUT → MCC → MCC（根据 UIN 查注册国）→ RCC → SAR 队伍

## 406 MHz 物理层

### 频段与功率

```text
频段    ：406.0 ~ 406.1 MHz（10 kHz 带宽，每 PLB 配一段）
功率    ：5 W ±1 dB（37 dBm）
极化    ：RHCP（右旋圆极化）或线极化
调制    ：BPSK（Binary Phase Shift Keying）
比特率  ：400 bps
周期    ：50 s ±2.5%（T.007 强制）
单次时长：0.5 s（短消息）/ 0.44 s（长消息）
```

### 信号结构

```text
[Preamble 16 bit] [Sync 24 bit] [BCH encoded 202 / 250 bit] = 总 250 / 300 bit
位时长 = 1/400 bps = 2.5 ms
总时长 = 250 × 2.5 ms = 625 ms = 0.625 s
```

**Preamble（16 bit）**：`0000111101010101`（BPSK 同步头）

**Sync 24 bit**：`011100001001011010001100`（T.001 规定的位同步序列）

**BCH 编码**（112 bit 信息 → 202 bit）：

```text
BCH(202, 112):
  信息位    : 112 bit（短消息：UIN + beacon type + 国家码 + 协议码）
  校验位    : 90 bit（BCH 校验）
  纠错能力  : 最多纠 4 个错（突发错可纠 40 bit）
  生成多项式: g(x) = x^90 + x^89 + ... + 1 (T.001 详细给出)
```

**BCH(250, 144) 长消息**：

```text
  信息位    : 144 bit（长消息：含位置 lat/lon）
  校验位    : 106 bit
  纠错能力  : 最多纠 6 个错
```

### 报文内容（短消息 112 bit）

```text
位 1-30:   Bit Synchronization
位 31-85:   Unique Identifier (55 bit):
              MID (10 bit) + Protocol Code (6 bit) + ID (30 bit) + Flag (9 bit)
位 86-105:  Position / Encoded Position（短消息无位置填 0xFF）
位 106-112: Emergency Code / Protocol Flag
BCH(202, 112) → 202 bit
```

### 报文内容（长消息 144 bit）

```text
位 1-30:   Bit Synchronization
位 31-85:   Unique Identifier (55 bit)
位 86-105:  Position（20 bit）:
              位置 lat（9 bit）+ lon（10 bit）+ 编码类型（1 bit）
              编码精度: 4 秒（~120 m） lat + 8 秒（~240 m） lon
位 106-129: 辅助位置 / 国家码扩展
位 130-144: Emergency Code / Protocol Flag
BCH(250, 144) → 250 bit
```

### 编码到 400 bps BPSK

```text
编码流程：
1. 信源: 112 bit 短消息
2. BCH 编码: 202 bit
3. Preamble 16 bit + Sync 24 bit = 240 bit 头
4. 整体: 240 + 202 = 442 bit
5. 调制: BPSK 400 bps → 1.1 s 发射
注：标准 0.5 s 是 0.5 / 0.0025 = 200 bit，加上 preamble
     实际 T.007 规定 0.5 s 发射 = 200 bit 长
     短消息总长 200 bit, 长消息 250 bit
```

## UIN 编码

UIN（Unique Identification Number，15 字符 hex 串 = 60 bit）是 PLB 全球唯一身份。

### 结构

```text
位 1-10:   MID  Maritime Identification Digits (10 bit)
位 11-16:  Protocol Code (6 bit)
位 17-26:  Country Code / ID (10 bit)
位 27-40:  Serial Number (14 bit)
位 41-50:  Auxiliary (10 bit)
位 51-60:  CRC / Checksum (10 bit)
```

### MID 分配（ITU 管理）

| MID | 国家 |
| --- | --- |
| 201 / 202 / 203 | 阿尔巴尼亚 / 安道尔 / 奥地利 |
| 232 / 233 / 234 / 235 | 英国 |
| 257 / 258 / 259 | 挪威 / 瑞典 / 芬兰 |
| 316 | 加拿大 |
| 366 / 367 / 368 / 369 | 美国 |
| 412 | 中国 |
| 413 / 414 | 斯里兰卡 / 印度 |
| 461 / 462 / 463 / 464 / 465 / 466 | 越南 / 老挝 / 柬埔寨 / 泰国 / 缅甸 / 马来西亚 |
| 503 | 澳大利亚 |
| 538 / 539 / 540 | 巴布亚新几内亚 / 瑙鲁 / 汤加 |

完整列表见 ITU M.585（2024 年版本分配到 999）。

### Protocol Code

| 码 | 含义 |
| --- | --- |
| 0x00 | EPIRB / ELT / PLB 标准协议 |
| 0x01 | EPIRB MMSI |
| 0x02 | PLB Serial |
| 0x03 | ELT 24-bit Address |
| 0x10 | ELT Aircraft 24-bit ICAO |
| 0x20 | PLB 测试 |
| 0x30~0x3F | 国家专用 |

PLB 最常用 **0x02**（PLB Serial Protocol）。

### UIN 字符串示例

```text
PLB 中国 MID 412, Protocol 0x02, Serial 0x12345:
  10 bit MID       = 000110011100 (412 decimal)
  6 bit Protocol   = 000010
  10 bit Country   = 0000000000
  14 bit Serial    = 00000000000000 → 0x00012345 hex
  → 60 bit UIN     = 000110011100 000010 0000000000 00000000000000 0000000000 0000000000
  → 15 hex 字符    = 19 C8 00 00 00 00 00 00  → 19C800000000000
  注：实际计算由 ITU 工具: https://www.itu.int/mmsapp/ShipStation/land/forms
```

**注**：上例是简化版。实际 UIN 字符串分国家分配段，ITU 官方工具计算。

## 121.5 MHz 测向原理

### 频段与功率

```text
频段  : 121.5 MHz（国际航空 / 海事应急频段）
功率  : 50~100 mW（17~20 dBm）
调制  : AM / 等幅载波（A3E）
频偏  : ±50 Hz（测向精度基础）
覆盖  : 5~10 km（飞机 / 船载测向）
```

### 测向原理

**测向接收机**（飞机 / 救援船）：

```text
PLB 121.5 MHz 信号 → 测向天线（4 单元环形天线阵）
                    → 4 路信号相位差
                    → 测向算法（Watson-Watt / Doppler）
                    → 方位角
                    → 多机交汇 → 位置
```

**Watson-Watt 测向**（最常用）：

```text
4 个天线（N/S/E/W 方向）
每个天线接收信号强度差 → 测向

测向精度：±2°（开阔地）
测向距离：10~30 km（空中）/ 5~10 km（地面）
```

### 121.5 MHz 信号发射

PLB 触发后，121.5 MHz 持续发射（跟 406 MHz 同步持续 24~48 h）：

```text
触发 ON → MCU 启动 LKT4211 模组
        → 121.5 MHz 载波 + AM 调制（音频 1 kHz + 1.3 kHz 锯齿）
        → 50~100 mW 输出
        → 50Ω 弹簧天线
        → 测向接收机可锁定方位
```

**LKT4211 内部**：

```text
┌──────────────────────────────────────┐
│ 16 MHz TCXO（基频）                   │
│   ↓ × 7.59375 = 121.5 MHz            │
│ PLL + VCO                            │
│   ↓                                  │
│ PA (Class AB) → 50~100 mW            │
│   ↓                                  │
│ T/R Switch → ANT                    │
└──────────────────────────────────────┘
```

## GNSS 集成

### 系统选择

PLB 选 GNSS 考虑：

```text
必选：
  GPS L1 (1575.42 MHz)  → 全球覆盖，70% 时间可见 6+ 颗
  GLONASS L1 (1602 MHz) → 高纬度 / 极地增强

可选：
  Galileo E1 (1575.42 MHz) → 与 GPS 同频，欧盟 SAR 优先
  北斗 B1 (1561 MHz)       → 亚洲增强，中国 PLB 必选

不选：
  L5 / E5a / B2a          → 高精度但功耗大，PLB 不需要
  SBAS / RTK              → 增强到米级，PLB 不需要 ±50 m 够用
```

### 报文位置编码

GNSS 位置编码进 406 MHz 报文（长消息）：

```text
lat (9 bit)  + lon (10 bit) = 19 bit
编码精度: 4 秒 lat (120 m) + 8 秒 lon (240 m) at equator
          极地 lat 4 秒 → 4 m（更精确）

编码方式: lat 范围 -90° ~ +90°, 4 秒精度 → 4 × 60 × 60 = 14400 个值
          9 bit = 512 个值 → 不够
          实际用 4 秒 / 8 秒混合编码（详细 T.001 给出）

PLB 实际不主动算 lat/lon bit，依赖 GNSS 模组输出
u-blox MAX-M10:
  → UBX protocol 输出 lat/lon (4 byte float)
  → MCU 读 lat/lon + 编码成 19 bit
```

### TTFF 优化

PLB 触发后要尽快定位（最长 5 min）：

```text
冷启动 (Cold Start):
  无历书 (almanac) → TTFF < 35 s
  无星历 (ephemeris) → TTFF < 35 s
  拉低频 5 min 接收历书 (almanac) → 之后秒定

热启动 (Hot Start):
  保留历书 / 星历 → TTFF < 5 s
  PLB OFF 状态保留历书 (低功耗 SRAM)
```

**实战优化**：

```python
# gnss_init.c
# PLB 触发后 MCU 工作
void gnss_init_after_trigger(void) {
    // 1. 唤醒 GNSS 模组
    gnss_power_on();
    delay_ms(100);

    // 2. 拉低频 (1 Hz)
    gnss_set_update_rate(1);

    // 3. 看 CN 值 (carrier-to-noise)
    while (gnss_get_cn_max() < 35) {
        delay_ms(1000);  // 等信号稳定
        if (timer > 300) break;  // 5 min timeout
    }

    // 4. 触发单次定位
    gnss_single_fix();

    // 5. 读 NMEA / UBX
    while (!gnss_has_fix()) {
        delay_ms(1000);
        if (timer > 300) break;
    }

    if (gnss_has_fix()) {
        lat = gnss_get_lat();
        lon = gnss_get_lon();
        // 编码到 406 MHz 报文
        encode_position_to_beacon(lat, lon);
    } else {
        // 无定位 → 改用多普勒定位
        // 报文位置段填 0xFF
    }
}
```

## 多普勒定位原理（无 GNSS 时）

当 PLB 没有 GNSS 或 GNSS 故障时，COSPAS-SARSAT LEOSAR 用多普勒频移定位。

### 原理

```text
PLB 静止 → 发射 406.0 MHz 固定频率
LEO 卫星以 7.5 km/s 速度过顶
相对速度在 -7.5 ~ +7.5 km/s 之间
多普勒频移: Δf = f × v / c
  = 406 MHz × 7500 / 3×10^8
  = ±10.15 kHz

PLB 实际接收频率（卫星视角）: 406.0 MHz ± 10.15 kHz
```

### 定位过程

```text
1. LEO 卫星过顶，约 10 分钟可见
2. 期间 PLB 发射 4~12 次 406 MHz 信号
3. 卫星接收 + SARR 处理 → 1544.5 MHz 转发 LUT
4. LUT 测量每次发射的多普勒频移 + 时间
5. 反向拟合 PLB 位置（卫星位置已知）
6. 定位精度 ±5 km（COSPAS-SARSAT 官方）
```

### 实战意义

- 没有 GNSS 的老 PLB 也能被定位（但精度低）
- 有 GNSS 的 PLB 优先用 GNSS 位置
- 报文位置段如果填 0xFF 标记"无 GNSS"，LEOLUT 主动多普勒定位
- 如果填了乱码位置（编码 bug），LEOLUT 会按多普勒定位，丢弃错位置

## 整机架构

### 硬件框图

```text
                  ┌─────────────────┐
                  │ 一次性锂电池    │
                  │ Li-SOCl2 3.6V   │
                  │ 7.2 Ah / 25.9Wh │
                  │ (5~7 年)        │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
         ┌─────────┐  ┌─────────┐  ┌─────────┐
         │ MCU     │  │ 406 MHz │  │ 121.5   │
         │ STM32L  │  │ PA +    │  │ MHz     │
         │ 073     │  │ 滤波    │  │ LKT4211 │
         └────┬────┘  └────┬────┘  └────┬────┘
              │            │            │
              ↓            ↓            ↓
         ┌─────────┐  ┌─────────┐  ┌─────────┐
         │ GNSS    │  │ 406 MHz │  │ 121.5   │
         │ u-blox  │  │ 天线    │  │ 天线    │
         │ MAX-M10 │  │ 弹簧    │  │ 弹簧    │
         └────┬────┘  └─────────┘  └─────────┘
              ↓
         ┌─────────┐
         │ GNSS    │
         │ 天线    │
         │ 陶瓷    │
         └─────────┘
```

### 固件模块

```c
// plb_firmware.c
// 主循环
void main_loop(void) {
    switch (state) {
        case STATE_OFF:
            // 电流 < 1 µA
            low_power_sleep();
            break;

        case STATE_ARM:
            // 自检：电池电压、GNSS 模块、406 MHz PA、121.5 MHz 模组
            // 周期 5 min 拉 GNSS 拉低频
            self_test();
            gnss_poll_low_power();
            break;

        case STATE_ON:
            // 触发，发射
            beacon_transmit_406();
            beacon_transmit_121_5();
            wait_50s();
            repeat();
            break;
    }
}

// 406 MHz 发射
void beacon_transmit_406(void) {
    // 1. 读 GNSS 位置
    fix = gnss_get_fix();
    if (fix) {
        encode_long_message(uin, beacon_type, lat, lon);
    } else {
        encode_short_message(uin, beacon_type);  // 0xFF 位置
    }

    // 2. BCH 编码
    bch_encoded = bch_encode(message, len);

    // 3. 加 preamble + sync
    bitstream = concat(preamble, sync, bch_encoded);

    // 4. BPSK 调制
    bpsk_modulated = bpsk_modulate(bitstream);

    // 5. 上变频到 406 MHz
    rf_406_send(bpsk_modulated, 5W, 0.5s);
}

// 121.5 MHz 发射（同时）
void beacon_transmit_121_5(void) {
    // LKT4211 模组直接使能
    pin_121_5_enable();
    // 持续发射
}
```

## 关键芯片深度

### Microsemi（Microchip）Syracuse 4 系列

行业事实标准，全球 70%+ PLB 用。

```text
Syracuse 4 主要参数：
  频率: 406.0~406.1 MHz
  功率: 5W ±1dB
  调制: BPSK 400 bps
  BCH: 硬件 BCH(202,112) / BCH(250,144)
  UART: 配置 UIN + 报文 + 发射控制
  电流: 发射时 1.5A @ 5V（5W PA + 滤波）
  接口: SPI / UART / GPIO
  封装: 32-pin QFN
  价格: 50~100 美元
```

**Syracuse 4 vs Syracuse 3 差异**：

```text
Syracuse 3:
  只能短消息 112 bit
  无内置 GNSS 接口
  外置 MCU 控制

Syracuse 4:
  支持长消息 144 bit（含位置）
  内置 GNSS 接口（直接接 u-blox）
  内置 BCH 硬件
  集成度更高
```

### 国产海积 HZB406

```text
HZB406 主要参数：
  频率: 406.0~406.1 MHz
  功率: 5W ±1dB
  调制: BPSK 400 bps
  BCH: 硬件 BCH
  接口: SPI / UART
  价格: 80~150 人民币（2024 年）
  国产替代: 通过 COSPAS-SARSAT T.007 认证（2023）
```

### LKT4211（121.5 MHz 模组）

```text
LKT4211 主要参数：
  频率: 121.5 MHz ± 50 Hz
  功率: 50~100 mW
  调制: AM 1 kHz + 1.3 kHz 锯齿
  接口: SPI
  电流: 25 mA @ 50 mW
  价格: 30~60 人民币
```

### u-blox MAX-M10

```text
MAX-M10 主要参数：
  卫星: GPS + GLONASS + Galileo + 北斗（B1）
  灵敏度: -167 dBm
  TTFF: 冷启动 26 s, 热启动 2 s
  功耗: 25 mA @ 1.8V
  接口: UART / SPI / I2C
  封装: 12-pin LCC
  价格: 15~25 美元
```

## 认证深挖

### COSPAS-SARSAT T.007 测试项目

```text
发射机测试（406 MHz）:
  □ 频率范围 406.0~406.1 MHz ±1 kHz
  □ 功率 5W ±1dB 全温度稳定
  □ 频率稳定度 ±0.5 ppm（-40°C ~ +55°C）
  □ BPSK 调制 400 bps ±0.5%
  □ 杂散辐射 < -30 dBc
  □ 谐波 < -40 dBc
  □ 占用带宽 < 5 kHz（99% 功率）

发射机测试（121.5 MHz）:
  □ 频率 121.5 MHz ±50 Hz
  □ 功率 50~100 mW
  □ AM 调制深度 > 70%
  □ 音频 1 kHz + 1.3 kHz 锯齿

报文测试:
  □ BCH(202,112) 编码正确
  □ BCH(250,144) 编码正确
  □ 纠错能力 4 / 6 个错
  □ UIN 唯一（ITU 数据库查重）
  □ 报文结构符合 T.001

环境测试:
  □ 温度 -40°C ~ +55°C
  □ 振动 IEC 60945
  □ 冲击 IEC 60945
  □ 浸水 IP67（30 min, 1 m）
  □ 盐雾 IEC 60068-2-52
  □ 高度 16000 m（航空 ELT 适用）

电池测试:
  □ 24h 持续发射（5°C 下）
  □ 5 年 / 7 年有效期（自放电 < 1%/年）
  □ 短路 / 反接保护

标签:
  □ UIN（15 hex）
  □ 电池有效期
  □ 厂商信息
  □ 注册说明
```

### 国家认证

**中国**：

```text
- SRRC 型号核准（工信部）
- CCC 强制（部分场景）
- COSPAS-SARSAT 通过
- 船检：CCS（中国船级社，PLB 配套船才要）
- 户外用品：无强制 CCC，但部分省份要求入网
```

**美国**：

```text
- FCC Part 80 / 87（强制）
- COSPAS-SARSAT 通过
- NOAA 注册（用户）
- 户外用品：UL 913 防爆（可选）
```

**欧盟**：

```text
- CE / RED（强制）
- COSPAS-SARSAT 通过
- 国家海事局注册（用户）
```

## 协议解析实战（自写 decoder）

```python
# beacon_decoder.py
# 抓包 406 MHz 信号后，BPSK 解调 + bit stream 解析

import numpy as np

def bpsk_demodulate(iq_samples, sample_rate=240000):
    """
    IQ 采样 → bit stream
    sample_rate: 240 kHz (Airspy R2 默认)
    """
    # 1. 滤到 406 MHz ±5 kHz
    # 实际下变频到基带
    # ...

    # 2. 找载波
    carrier_freq = detect_carrier(iq_samples)  # Hz 偏移

    # 3. 下变频
    t = np.arange(len(iq_samples)) / sample_rate
    baseband = iq_samples * np.exp(-1j * 2 * np.pi * carrier_freq * t)

    # 4. 匹配滤波
    symbol_rate = 400  # bps
    samples_per_symbol = sample_rate / symbol_rate
    matched = np.convolve(baseband, np.ones(int(samples_per_symbol))/np.sqrt(samples_per_symbol))

    # 5. 采样
    symbols = matched[::int(samples_per_symbol)]
    bits = (np.real(symbols) > 0).astype(int)

    return bits

def parse_beacon(bits):
    """
    解析 BCH(202, 112) 短消息
    """
    if len(bits) < 200:
        return None

    # 1. 找 preamble
    preamble = [0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    if not bits[:16].tolist() == preamble:
        return None

    # 2. 找 sync (24 bit)
    sync = [0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0]
    if not bits[16:40].tolist() == sync:
        return None

    # 3. BCH(202, 112) 解码
    bch_block = bits[40:40+202]
    decoded = bch_decode_short(bch_block)
    if decoded is None:
        return None

    # 4. 解析 112 bit
    mid = int(''.join(map(str, decoded[0:10])), 2)
    protocol = int(''.join(map(str, decoded[10:16])), 2)
    country_id = int(''.join(map(str, decoded[16:26])), 2)
    serial = int(''.join(map(str, decoded[26:40])), 2)
    aux = int(''.join(map(str, decoded[40:50])), 2)
    crc = int(''.join(map(str, decoded[50:60])), 2)

    # beacon type
    if protocol == 0x02:
        beacon_type = "PLB"
    elif protocol == 0x01:
        beacon_type = "EPIRB MMSI"
    elif protocol == 0x10:
        beacon_type = "ELT ICAO"
    else:
        beacon_type = f"Unknown (0x{protocol:02X})"

    # CRC 校验
    if not verify_crc(decoded[:50], decoded[50:60]):
        return {"error": "CRC fail", "raw": decoded}

    return {
        "beacon_type": beacon_type,
        "mid": mid,
        "protocol": protocol,
        "country_id": country_id,
        "serial": serial,
        "aux": aux,
        "uin_hex": f"{mid:04X}{protocol:02X}{country_id:04X}{serial:04X}",
    }
```

## 性能数据参考

| 参数 | 典型值 | COSPAS-SARSAT 要求 |
| --- | --- | --- |
| 406 MHz 功率 | 5 W ±1 dB | 5 W ±1 dB |
| 频率稳定度 | ±0.5 ppm | ±0.5 ppm |
| 卫星可视性 | 95%（LEO + GEO 合并） | < 1 h 定位 |
| 多普勒定位精度 | ±5 km | < 5 km 90% |
| GNSS 定位精度 | ±50 m CEP | < 5 km（无 GNSS） |
| 121.5 MHz 测向距离 | 5~10 km | 不强制 |
| 电池续航（5°C） | 30 h | ≥ 24 h |
| TTFF（冷启动） | 26 s | < 5 min |
| 整机重量 | 200~300 g | 不强制 |
| 价格 | 200~600 美元 | 不强制 |

## 关联文档

- `bus/plb.md` 主题入口
- `bus/plb-practical.md` 调试流程速查
- `bus/plb-failure-cases.md` 产线实战案例
- `bus/plb-index.md` 主题地图 + 导航
