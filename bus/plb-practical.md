# PLB Practical Guide

## 目标

PLB 工程调试速查：406 MHz 信号抓取、UIN 编码、协议解析、GNSS 集成、电池测试、认证测试。覆盖产线最常见的编码错、频率偏移、触发错、UIN 重复分配等故障的快速定位。

## 最小系统（以 Microsemi Syracuse 4 + u-blox MAX-M10 + 国产 LKT4211 为例）

```text
UIN 配置     ──── 烧录器（PC + 烧录软件） ──── MCU 内部 EEPROM
GNSS 天线    ──── 25×25 mm 陶瓷天线（GPS L1 + GLONASS L1）
GNSS 模块    ──── u-blox MAX-M10，UART 9600 bps 报 NMEA
406 MHz 功放 ──── 5W PA + 谐波滤波器
406 MHz 天线 ──── 螺旋弹簧天线（405~407 MHz，VSWR < 1.5）
121.5 MHz    ──── LKT4211 模组 + 50Ω 短天线
MCU          ──── STM32L073（Cortex-M0+，低功耗）
电源         ──── 一次性锂电池 Li-SOCl2 3.6V 7.2 Ah
按键         ──── 防误触三段开关（OFF / ARM / ON）
G 触发器     ──── 仅航空 ELT 配套要
```

**关键约束**：

- 406 MHz 频率稳定度 ±0.5 ppm（卫星多普勒定位基础，TCXO 必选）
- 电池能量 ≥ 7.2 Wh（保 24 小时持续发射，5 年自放电极小）
- 工作温度 -40°C ~ +55°C（COSPAS-SARSAT 必过）
- 整机密封 IP67（户外 / 落水场景）
- 防误触必须双动作（按键 + 解锁 / 翻盖）

## 关键参数

### 406 MHz 发射参数

| 参数 | 范围 / 典型 | 影响 |
| --- | --- | --- |
| 频段 | 406.0 ~ 406.1 MHz | COSPAS-SARSAT 强制 |
| 功率 | 5 W ±1 dB | 卫星可见性，越高越远 |
| 频率稳定度 | ±0.5 ppm（短期） | 多普勒定位精度 |
| 发射时长 | 0.5 s / 次 | 单次占用时间 |
| 发射周期 | 50 s ±2.5% | LEO 卫星过顶时间 |
| 报文长度 | 112 bit（短）或 144 bit（长） | 信息量 |
| BCH 纠错 | BCH(250,144) 或 BCH(202,112) | 抗突发错 |
| 数据调制 | BPSK 400 bps | 调制方式 |

### 121.5 MHz 近场信号参数

| 参数 | 范围 / 典型 | 影响 |
| --- | --- | --- |
| 频段 | 121.5 MHz | 民航 / 海事测向国际频段 |
| 功率 | 50~100 mW | 测向距离 5~10 km |
| 调制 | AM / 等幅载波 | 测向接收机解调 |
| 频偏 | ±50 Hz 内 | 测向精度 |
| 持续时间 | 跟 406 MHz 同步持续 | 24~48 小时 |

### GNSS 集成参数

| 参数 | 范围 / 典型 | 影响 |
| --- | --- |
| 卫星系统 | GPS L1 + GLONASS L1（必选） | 定位可用率 |
| | + Galileo / 北斗（可选） | 极地 / 山地增强 |
| 冷启动 TTFF | < 35 s | 首次定位时间 |
| 热启动 TTFF | < 5 s | 触发后首次发位置 |
| 定位精度 | ±50 m CEP（开天空） | COSPAS-SARSAT 接受 |
| 坐标格式 | WGS84 坐标，度分秒 / 度小数 | 报文编码 |

### 报文协议（短消息 112 bit）

```text
位  1-30:   Bit Synchronization（位同步）
位 31-85:   Unique Identifier（55 bit，含 MID + 协议码 + ID）
位 86-105:  Position Data（短消息无位置时填充）
位 106-112: Emergency Code / Protocol Flag
BCH(202, 112) 纠错扩展到 202 bit
最终 202 bit + 16 bit preamble
```

## 抓包工具

PLB 抓包主要分两类：406 MHz 卫星下行 / 121.5 MHz 测向 / 自检报文回传。

| 工具 | 平台 | 频段 | 优势 | 限制 |
| --- | --- | --- | --- | --- |
| RTL-SDR v3 | USB | 24~1766 MHz | 廉价、SDR# / GQRX 全平台 | 406 MHz 灵敏度弱 |
| Airspy R2 / Mini | USB | 24~1800 MHz | 406 MHz 灵敏度高 | 贵（150~300 美元） |
| SDRplay RSP1A | USB | 1 kHz ~ 2 GHz | 宽频段 | 贵 |
| 国产 SDR | USB | 多种 | 便宜 | 性能一般 |
| Funcube Dongle Pro+ | USB | 150 kHz ~ 2.6 GHz | 406 MHz 优化 | 贵、停产 |
| COSPAS-SARSAT LUT | 地面站 | 1544.5 MHz 下行 | 官方抓 | 不可携带 |
| MEOLUT | 多星地面 | 1544.5 MHz | 官方多星定位 | 不可携带 |

**产线推荐组合**：

```text
研发调试：
  Airspy R2 + SDR# + 自写 decoder（解析 BCH + UIN）
  产线自检：拉杆天线 + RTL-SDR + 脚本验证

认证测试：
  送 COSPAS-SARSAT 官方 / 授权实验室
  户外场测：NARDA / ETS-Lindgren 频谱仪 + 喇叭天线

生产批量：
  屏蔽箱 + 406 MHz 测试天线 + 自检脚本
  1 天 100 台吞吐量
```

## 调试步骤

1. **烧录 UIN**：用烧录器把 15 字符 hex 写入 MCU EEPROM（UIN 全局唯一，注册到国家中心）
2. **看 GNSS 报位置**：NMEA 输出到串口，确认 lat/lon 正确
3. **拉 406 MHz 测试天线 + 频谱仪**：看 406.0~406.1 MHz 频段信号
4. **抓 406 MHz 报文**：SDR# + 录音 + 自写 decoder 解析
5. **验证 BCH 校验**：用 `beacon_decoder.py` 校验 BCH(202,112) 或 BCH(250,144)
6. **验证 UIN 一致性**：烧录值 = 抓包解析值 = 标签印的值（三处一致）
7. **测电池电压**：接 50Ω 假负载连续发射，看电压跌落 < 0.3V
8. **测温度循环**：-40°C / +25°C / +55°C 各放 1 小时，看频率稳定度
9. **测防误触**：按 OFF / ARM / ON 三段开关，看触发时序
10. **测外壳密封**：浸水 1 米 30 分钟，看内部干燥

## 常见问题速查

| 现象 | 优先检查 |
| --- | --- |
| 406 MHz 频谱仪看不到 | PA 没供电 / 频段错 / 天线坏 / 烧录器覆盖了发射使能 |
| 抓到报文但 BCH 错 | 编码器固件错 / 时钟频率偏移 / 信号被反射叠加 |
| 抓包位置与 GNSS 实际不符 | 报文位置段编码错 / lat/lon 字节序错 / NMEA 解析错 |
| UIN 重复 | 烧录器没全局查重 / 协议码分配错 / 序列号循环溢出 |
| 121.5 MHz 测向距离 < 1 km | 频率偏移 > 100 Hz / 功率 < 30 mW / 调制方式错 |
| 触发后只发 406 MHz 不发 121.5 | LKT4211 模组供电断 / 121.5 MHz 频段错配 |
| 电池在 -40°C 容量跌 50% | 电池低温特性差 / 自加热电路没启 |
| TTFF > 5 min | GNSS 天线方向错 / 卫星数据过期 / 冷启动算法错 |
| 防误触单按就触发 | 翻盖开关没接 / 软件去抖没做 / 三段开关没锁 |
| 整机浸水后开机 | 密封圈老化 / 螺丝扭矩不够 / 通气孔漏 |

## 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 整机没信号 | 烧录 / 电源 / 天线 | 看 PA 供电、看频谱仪 |
| BCH 错 | 编码器 / 时钟 | 换 TCXO 验证 |
| UIN 重复 | 烧录器逻辑 | 加全局查重脚本 |
| 位置错 | 报文编码 / NMEA | 看 NMEA 原文 + 报文解码 |
| 121.5 没信号 | 模组供电 / 频段 | 万用表量 LKT4211 VCC |
| 电池低温差 | 电池 / 自加热 | 低温箱验证 |
| 防误触 | 硬件 / 软件 | 看翻盖开关接线 |
| 浸水 | 密封 / 通气 | 拆机看干燥剂 |
| TTFF 慢 | GNSS 天线 / 算法 | 看卫星数 + CN 值 |
| 触发后只 24h | 电池容量 | 假负载测电流积分 |

## 烧录 UIN 实战

UIN 格式（15 字符 hex = 60 bit）：

```text
位 1-10:   MID  国家码（10 bit 编码 MID）
位 11-16:  Protocol Code 协议码
位 17-26:  Country Code 备用国家码
位 27-40:  Serial Number 序列号
位 41-50:  Auxiliary / Test 标志
位 51-60:  CRC / 校验
```

**烧录器脚本示例**（Python）：

```python
# burn_uin.py
# UIN 分配从国家救援中心 CSV 拉
import csv
import serial

uin_table = []
with open('uin_registry.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        uin_table.append({
            'hex': row['uin_hex'],
            'serial': row['serial_no'],
            'assigned_to': row['customer'],
            'burned': False,
        })

def check_global_unique(uin_hex):
    """全局查重"""
    count = sum(1 for u in uin_table if u['hex'] == uin_hex)
    return count == 0

def burn_one(ser_port, uin_hex):
    """通过 UART 烧录 UIN 到 MCU EEPROM"""
    cmd = f"UIN:BURN:{uin_hex}\n".encode()
    ser_port.write(cmd)
    resp = ser_port.readline()
    if b"OK" in resp:
        return True
    return False

# 烧录流程
ser = serial.Serial('COM3', 115200)
for u in uin_table:
    if not check_global_unique(u['hex']):
        print(f"UIN 重复 {u['hex']}, 跳过")
        continue
    if burn_one(ser, u['hex']):
        u['burned'] = True
        print(f"已烧录 {u['hex']} -> {u['assigned_to']}")
    else:
        print(f"烧录失败 {u['hex']}")

# 写回 CSV 标记
with open('uin_registry.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['uin_hex', 'serial_no', 'customer', 'burned'])
    writer.writeheader()
    for u in uin_table:
        writer.writerow({
            'uin_hex': u['hex'],
            'serial_no': u['serial'],
            'customer': u['assigned_to'],
            'burned': u['burned'],
        })
```

**烧录前必查**：

1. UIN 库表里没有这个 hex
2. 中间 4 位协议码匹配产品类型（PLB = 0x2 / EPIRB = 0x1 / ELT = 0x3）
3. 序列号在 MID 范围内不冲突
4. 国家码 + 协议码 + 序列号三段加起来 = 60 bit
5. CRC 校验通过

## BCH 校验

406 MHz 报文 BCH 纠错验证：

```python
# bch_check.py
# BCH(202, 112) 短消息
# BCH(250, 144) 长消息

def bch_decode_short(bit_stream):
    """BCH(202, 112) 解码，返回 112 bit 有效信息或 None"""
    # 多项式: g(x) = x^10 + x^9 + x^8 + x^5 + x^4 + x^2 + 1
    syndrome = compute_syndrome(bit_stream, poly)
    if syndrome == 0:
        return bit_stream[:112]  # 无错
    # 纠错算法（BM / PGZ）
    corrected, err = berlekamp_massey_decode(bit_stream, syndrome)
    if err is None:
        return None
    return corrected[:112]

def bch_decode_long(bit_stream):
    """BCH(250, 144) 解码，返回 144 bit 有效信息或 None"""
    # 多项式: g(x) = x^21 + ...
    # 类似上面
    ...
```

**BCH 错位的常见原因**：

- 编码器固件用错多项式（最常见 BUG）
- 时钟漂移导致位错位（频率稳定度差）
- 多径反射导致位翻转（户外场地反射）
- 信噪比 < 6 dB 时错误率飙升（PA 功率低）

## 触发测试（防误触）

PLB 防误触三段开关：

```text
OFF  ──── 关机态，电池不供电
ARM ──── 待机态，自检 + GNSS 拉低频（每 5 分钟看一次）
ON  ──── 触发态，发射 406 MHz + 121.5 MHz
        必须先拨到 ARM 再拨到 ON（双动作）
        拨到 ON 时长按 3 秒（防误触）
```

**测试步骤**：

```text
1. 拨到 OFF → 整机电流 < 1 µA
2. 拨到 ARM → 自检 LED 闪一次，电池电压读回 MCU
3. 长按 ON 3 秒 → LED 长亮，开始 406 MHz 发射
4. 看频谱仪 → 406.0~406.1 MHz 出现信号
5. 持续发射 30 分钟 → 电池电压跌 < 0.3V
6. 拨回 OFF → 整机电流 < 1 µA
```

**生产测试**：

```python
# trigger_test.py
import time
import pyvisa

rm = pyvisa.ResourceManager()
sa = rm.open_resource('USB0::0x0957::0x2018::INSTR')  # 频谱仪

def test_trigger(port):
    # 1. OFF 测电流
    current_off = measure_current(port)
    assert current_off < 1e-6, f"OFF 态漏电 {current_off}A"

    # 2. ARM 测自检
    set_switch(port, 'ARM')
    time.sleep(2)
    self_test = read_self_test(port)
    assert self_test == 'OK', f"自检失败 {self_test}"

    # 3. 长按 ON 3s
    set_switch(port, 'ON')
    press_and_hold(port, 3)

    # 4. 频谱仪看信号
    sa.write('FREQ:CENT 406.05 MHz')
    sa.write('BAND 10 kHz')
    sa.write('POW:PEAK')
    time.sleep(2)
    power = float(sa.query('POW?'))

    assert 3.16 < power < 7.94, f"功率 {power}W 异常"  # 5W ±2dB

    # 5. 持续 30 分钟测电压
    start_v = read_battery_voltage(port)
    time.sleep(1800)
    end_v = read_battery_voltage(port)
    assert (start_v - end_v) < 0.3, f"电压跌 {start_v - end_v}V"

    # 6. OFF
    set_switch(port, 'OFF')
    current_off2 = measure_current(port)
    assert current_off2 < 1e-6, f"OFF 态漏电 {current_off2}A"

    return "PASS"
```

## 认证检查清单

COSPAS-SARSAT T.007 必过项（部分）：

```text
□ 406 MHz 频率范围 406.0~406.1 MHz
□ 功率 5W ±1dB 稳定（50 秒一个周期）
□ 频率稳定度 ±0.5 ppm（短期）
□ BPSK 调制 400 bps
□ BCH(202,112) 或 BCH(250,144) 编码
□ 报文结构符合 C/S T.001
□ UIN 全球唯一（注册到国家中心）
□ 121.5 MHz 频率 121.5 ± 50 Hz
□ 121.5 MHz 功率 50~100 mW
□ GNSS 定位（首次定位时间 < 5 min）
□ 报文含 lat/lon 位置
□ 电池续航 24 小时（5°C 下）
□ 电池有效期 5 年 / 7 年（标在标签上）
□ 工作温度 -40°C ~ +55°C
□ 振动 / 冲击（IEC 60945）
□ 浸水 IP67
□ 防误触三段开关
□ 自检功能（按 ARM 触发自检）
□ 标签含 UIN + 电池有效期 + 注册说明
```

## 配网流程（注册 UIN）

PLB 出厂后**必须注册**才能被救援中心识别：

```text
1. 用户购入 PLB
2. 填表（UIN + 姓名 + 紧急联系人 + 户外活动范围）
3. 寄到国家救援中心
4. 中心录入数据库（ITU 共享）
5. PLB 触发 → 卫星收到 UIN → 中心查 UIN → 联系紧急联系人
```

**各国注册方式**：

| 国家 | 注册中心 | 网址 |
| --- | --- | --- |
| 中国 | 中国交通部南海救助局 / 中国船舶检验 | cospas-sarsat.cn |
| 美国 | NOAA SARSAT | beaconregistration.noaa.gov |
| 加拿大 | Canadian Beacon Registry | cbr-rcb.ca |
| 英国 | HM Coastguard | mca.gov.uk |
| 澳大利亚 | AMSA | amsa.gov.au |

**注意**：中国 PLB 注册有特殊流程，需要通过"中信安"代理。户外爱好者买前必看。

## 检查清单

```text
□ UIN 烧录：全球唯一 + 烧录值 = 标签值 = 抓包解析值
□ 协议码：PLB = 0x2（写错最常见）
□ MID：中国 = 412
□ 406 MHz 频段：406.0~406.1 MHz
□ 406 MHz 功率：5W ±1dB
□ BCH 校验通过
□ 121.5 MHz 频段：121.5 ± 50 Hz
□ 121.5 MHz 功率：50~100 mW
□ GNSS 首次定位：< 5 min
□ 报文位置：lat/lon 正确编码
□ 电池电压：3.6V ±0.1V（出货）
□ 电池有效期：5/7 年
□ 防误触三段开关
□ 自检：LED 闪 + 电压读回
□ 外壳密封：IP67
□ 工作温度：-40°C ~ +55°C
□ 认证：COSPAS-SARSAT T.007 通过
□ 注册：国家中心已录入
```

## 关联文档

- `bus/plb.md` 主题入口
- `bus/plb-deep-dive.md` COSPAS-SARSAT / 406 MHz 编码 / BCH / UIN 解析深挖
- `bus/plb-failure-cases.md` 产线实战案例
- `bus/plb-index.md` 主题地图 + 导航
