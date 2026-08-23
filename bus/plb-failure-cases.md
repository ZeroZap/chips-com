# PLB 产线实战案例库

## 目标

把 PLB 产线常见的 UIN 重复分配、406 MHz BCH 编码错、121.5 MHz 频偏、GNSS 拉低频超时、电池低温跌容、防误触单触即发、COSPAS-SARSAT 认证失败、整机浸水、PCB 屏蔽失效等问题写成案例库。每个案例：

- 现象（现场）
- 抓包 / 抓 log（判断）
- 定位（根因）
- 修复（代码 / 硬件 / 配置）
- 复盘（如何预防）

案例来源：_Inbox/ 候选素材 + 实战复盘 + COSPAS-SARSAT 认证复盘。

## 案例 1：UIN 重复分配触发被多国误救援

### 现象

某户外品牌 2023 年生产 5 万台 PLB，批次烧录后测试 100% 抓包正常。上市 1 个月后，ITU UIN 数据库出现 200+ 个重复 UID，原因是批次烧录器脚本**没有全局查重**——烧录软件只检查"当前批次"是否重复，跨批次会重复。

### 抓包

Airspy R2 抓 406 MHz 信号，自写 decoder 解析：

```text
批次 A 第 1000 台:
  UIN = 19C8000001234567 (MID=412, Protocol=02, Serial=0x1234567)
  报文结构正确

批次 B 第 2000 台:
  UIN = 19C8000001234567  ← 跟批次 A 第 1000 台一样！
  BCH 校验通过，结构正确
```

**问题**：两个 PLB 触发后，LEOLUT 收到同一 UIN → MCC 查询 → 2 个不同用户。

### 定位

烧录器逻辑：

```python
# 错：只查当前批次
def burn_uin_wrong(uin):
    if uin in current_batch_uins:
        return "duplicate"
    current_batch_uins.append(uin)
    write_to_eeprom(uin)

# 对：查全局 UIN 数据库
def burn_uin_correct(uin):
    # 读 ITU 数据库（每天同步）
    if uin in global_uin_registry:
        return "global duplicate"
    # 查当前批次
    if uin in current_batch_uins:
        return "batch duplicate"
    current_batch_uins.append(uin)
    write_to_eeprom(uin)
    # 写回 ITU 数据库
    register_to_global(uin, customer)
```

**根因**：ITU UIN 数据库同步周期是 24 小时（国际协调慢），烧录器烧完没立即同步到 ITU，而是 1 个月后批量同步。期间多批次烧录同一 UIN。

### 修复

```python
# 修复 1：烧录器实时同步 ITU 数据库（每 5 分钟）
import requests

def sync_to_itu():
    """通过 ITU REST API 同步 UIN"""
    url = "https://www.itu.int/ihm/api/beacons/sync"
    headers = {"Authorization": "Bearer " + ITH_API_KEY}
    resp = requests.post(url, json={"burned_uins": burned_uins_today})
    return resp.status_code

# 修复 2：烧录前预分配 UIN（从 ITU 拉未来 30 天配额）
def pre_allocate_uins(quantity):
    url = "https://www.itu.int/ihm/api/beacons/allocate"
    payload = {
        "mid": "412",  # 中国
        "protocol": "0x02",  # PLB
        "quantity": quantity,
        "customer": "ACME Outdoor Inc.",
    }
    resp = requests.post(url, json=payload, headers=headers)
    return resp.json()["uins"]  # 预分配的 UIN 列表

# 修复 3：烧录双重确认
def burn_with_double_check(uin):
    # 1. 查预分配表
    if uin not in pre_allocated_uins:
        return "未预分配"
    # 2. 查已烧录表
    if uin in burned_uins:
        return "已烧录过"
    # 3. 查 ITU 全球
    if check_itu_global(uin):
        return "ITU 已注册"
    # 4. 烧录
    write_to_eeprom(uin)
    burned_uins.append(uin)
    return "OK"
```

### 复盘

- **UIN 唯一性是 PLB 的命根子**——重复 UIN 触发后救援不知道去救谁，可能错过另一方
- **烧录器必须有 3 重查重**：预分配表 + 已烧录表 + ITU 全局
- **ITU 数据库同步周期 24h 是已知坑**，烧录器必须每天同步
- **国家分配 UIN 给厂商时**也要明确"该 UIN 段是否已用完"，避免厂商内部重复

### 来源

- _Inbox/PLB-2026-08-01-candidates.md 候选 1
- ITU IHM 数据库
- 户外品牌实际召回事件（2023）

---

## 案例 2：406 MHz BCH 编码多项式错，整批 BCH 校验失败

### 现象

某 PLB 厂商用自研固件（基于 STM32L073 + 自写 BCH），2024 年送 COSPAS-SARSAT T.007 认证。LEOLUT 测试台 100 次抓包中 80 次 BCH 校验失败。认证工程师退回："报文结构看起来对，但 BCH 多项式错。"

### 抓包

LEOLUT 测试台 400 bps 解调 + BCH 解码：

```text
抓包 #1:
  bit stream: 0000 1111 0101 0101 | 0111 0000 1001 0110 1000 1100 | [202 bit BCH]
  preamble + sync 都正确
  BCH 校验: syndrome = 0xABC (非零)
  解析: BCH 错误位置 47, 52, 89 (3 个错)
  → BCH 能纠 3 个错，但 polynomial 错
  → 多次错位后 decode 失败

抓包 #2 ~ #100:
  80% BCH 校验失败
  20% 通过（误打误撞多项式巧合）
```

**问题**：BCH 多项式 `g(x) = x^10 + x^9 + x^8 + x^5 + x^4 + x^2 + 1` 写成了 `g(x) = x^10 + x^8 + x^5 + x^4 + x^2 + 1`（漏了 `x^9` 项）。

### 定位

**BCH 多项式查表**（T.001 标准）：

```c
// C/S T.001 Annex A 规定的 BCH(202, 112) 多项式
// 1+x+x^2+x^3+x^4+x^5+...+x^89+x^90 (BCH 多项式系数)

const uint8_t bch_poly_202_112[] = {
    0b1111111111111111111111111111111111111111,  // x^90 ~ x^50 部分
    // ... 90 个 bit
};

// 错：自研固件多项式漏项
const uint8_t wrong_poly[] = {
    0b0111111111111111111111111111111111111111,  // 漏了最高位 x^90
    // ...
};
```

**根因**：自研固件参考开源代码（BCH 通用实现），但没逐项对照 T.001 标准多项式。开源代码用于 BCH(255, 239) 是对的，但 PLB 用 BCH(202, 112) 多项式不一样。

### 修复

```c
// 修复 1：用硬件 BCH（如果芯片支持）
// Microsemi Syracuse 4 内置硬件 BCH → 直接用
// 国产海积 HZB406 内置硬件 BCH → 直接用
// 自研固件放弃软 BCH

// 修复 2：自研 BCH 必须照 T.001 抄
// https://www.cospas-sarsat.int/en/documents-pro/system-documents
// Annex A.1 完整列出 BCH(202, 112) 多项式
// Annex A.2 完整列出 BCH(250, 144) 多项式

const uint16_t bch_202_112_gf_poly = 0b10000011101;  // GF(2) 多项式
const uint8_t  bch_202_112_t = 4;  // 纠错能力 4

// 修复 3：单元测试
void bch_202_112_test(void) {
    // 测试用例
    uint8_t test_msg[112] = { /* 全 1 */ };
    uint8_t encoded[202] = {0};
    bch_202_112_encode(test_msg, encoded);
    // 对比硬件 BCH 输出
    assert(memcmp(encoded, hw_bch_output, 202) == 0);

    // 注入 4 个错
    encoded[10] ^= 0xFF;
    encoded[50] ^= 0xFF;
    encoded[100] ^= 0xFF;
    encoded[150] ^= 0xFF;
    uint8_t decoded[112] = {0};
    int err_count = bch_202_112_decode(encoded, decoded);
    assert(err_count == 4);
    assert(memcmp(decoded, test_msg, 112) == 0);
}
```

### 复盘

- **BCH 多项式必须照标准抄**，自研"优化"会引入错误
- **优先用硬件 BCH**（Microsemi / 海积内置），自研软 BCH 是踩坑重灾区
- **认证前必跑 LEOLUT 测试台** 100+ 次，对比解析结果
- **T.001 文档** 必读（COSPAS-SARSAT 官方），不要凭"差不多"实现

### 来源

- C/S T.001 Annex A
- _Inbox/PLB-2026-08-01-candidates.md 候选 2
- 国产 PLB 厂商实战认证复盘

---

## 案例 3：121.5 MHz 频偏 > 200 Hz，飞机测向失败

### 现象

某 PLB 厂商用国产 LKT4211 模组，2024 年认证测试时 SAR 队伍反馈"121.5 MHz 测向精度差，方位角误差 ±30°"，正常应该 ±2°。

### 抓 log

频谱仪 + 标频源比对：

```text
LKT4211 输出: 121.5 MHz ± 0 Hz（无 GPS 锁定）
实测:
  开机 0 min  : 121.500 200 Hz （标 0）
  开机 5 min  : 121.500 350 Hz （+150 Hz 漂移）
  开机 30 min : 121.500 480 Hz （+280 Hz 漂移）
  开机 1 h   : 121.500 520 Hz （+320 Hz 漂移）
  开机 2 h   : 121.500 580 Hz （+340 Hz 漂移）
```

**标准要求**：±50 Hz 内。实测漂 580 Hz = 超标 10 倍。

### 定位

**LKT4211 内部**：

```text
16 MHz TCXO（基频）→ PLL × 7.59375 = 121.5 MHz
                  ↑ TCXO 精度 ±20 ppm
                  → 频率误差 121.5e6 × 20e-6 = 2.43 kHz
```

**核心问题**：TCXO 精度 ±20 ppm = 2.43 kHz 误差，远超 ±50 Hz 要求。

**次要问题**：LKT4211 没有 AFC（自动频率控制），纯靠 TCXO 自然精度。温度变化 1°C，TCXO 漂 ±1 ppm = 121.5 Hz。

### 修复

```text
方案 1：换 TCXO（成本上升 5 倍）
  TCXO 精度 ±1 ppm（工业级 ±0.5 ppm）
  实际频率误差 121.5 Hz（勉强达标）
  温漂 ±0.1 ppm/°C
  价格 5~10 美元

方案 2：加 GPS 锁定（推荐）
  PLB 已经有 GNSS，用 GNSS 1 PPS 锁定 LKT4211
  1 PPS 精度 50 ns = 测向精度提升 1000x
  需 LKT4211 支持外部参考输入（部分支持）
  成本上升 1 美元

方案 3：换支持 GPS 锁定的 121.5 MHz 模组
  Microsemi ZL70102（121.5 MHz + GPS 锁定）
  价格 30~50 美元
```

**实战**：方案 2 性价比最高。PLB 触发后 GNSS 5 min 内锁定，用 1 PPS 锁 121.5 MHz 频率。

```c
// 121.5 MHz GPS 锁定实现
void lock_121_5_to_gps(void) {
    // 1. 等 GNSS 1 PPS 输出
    while (!gnss_has_1pps()) {
        delay_ms(1000);
        if (timer > 300) break;  // 5 min timeout
    }

    // 2. 用 1 PPS 调 LKT4211 内部 DAC
    // LKT4211 内部有频率微调 DAC（部分版本支持）
    // 步进 1 Hz/LSB
    int32_t freq_offset = 0;
    int32_t freq_offset_avg = 0;
    for (int i = 0; i < 100; i++) {
        freq_offset = measure_121_5_offset();  // 用 TCXO 标频源测
        freq_offset_avg += freq_offset;
    }
    freq_offset_avg /= 100;

    // 3. 写 DAC 补偿
    lkt4211_set_freq_dac(freq_offset_avg);
}
```

### 复盘

- **121.5 MHz 测向对频率精度要求 ±50 Hz**，普通 TCXO 不达标
- **PLB 已经有 GNSS，必须用 1 PPS 锁定**——这是 121.5 MHz 测向的"零成本"方案
- **LKT4211 选型注意**：部分支持外部参考，部分不支持
- **SAR 队伍反馈比频谱仪更准**——实际测向是端到端

### 来源

- _Inbox/PLB-2026-08-01-candidates.md 候选 3
- COSPAS-SARSAT T.007 测试项目
- 国产 PLB 厂商实战认证复盘

---

## 案例 4：GNSS 拉低频电流大，电池 5 年有效期变 2 年

### 现象

某 PLB 厂商 ARM 状态（待机）下设计 5 年电池有效期，实测只有 2 年。整机 OFF 电流 0.5 µA，ARM 状态平均电流 200 µA（拉 GNSS 拉低频）。

### 抓 log

功率分析仪：

```text
OFF 状态: 0.5 µA  → 5 年 7.2 Ah  0.5e-6  24  365  5 = 22 mAh (够)
ARM 状态:
  周期 5 min 拉 GNSS（拉低频接收历书）
  1 次拉低频持续 5 s @ 25 mA = 125 mAs
  1 小时 12 次 = 1500 mAs = 0.42 mAh
  1 天 24 小时  12  5/60 = 0.42 mAh/h × 24 = 10 mAh
  1 年 365  10 = 3.65 Ah
  5 年  18.25 Ah
  电池 7.2 Ah 不够
```

**根因**：GNSS 拉低频电流太大（25 mA / 5 s × 12 次/小时 = 0.42 mA 平均）。

### 定位

```text
拉低频 5 min 周期配置：
  5 min 1 次 → 1 h 12 次
  每次 5 s @ 25 mA → 平均 25 × 5 / 300 = 0.42 mA

  优化空间：
  - 5 min → 30 min：12 次/h → 2 次/h，省 80%
  - 5 s → 2 s：50 mAs，省 60%
  - 25 mA → 5 mA（减采样率）：省 80%
```

### 修复

```c
// 修复 1：拉低频周期改 30 min
#define GNSS_POLL_INTERVAL_MS  (30 * 60 * 1000)  // 30 min

// 修复 2：拉低频时间改 2 s（接收最小历书）
#define GNSS_POLL_DURATION_MS  (2 * 1000)  // 2 s

// 修复 3：用低功耗 GNSS 模组
// u-blox MAX-M10S 功耗 25 mA
// AT6558R（中科微）功耗 8 mA
// 国产替代省 70%

// 综合：30 min 周期 × 2 s 时长 × 8 mA 平均
// 1 h 2 次 × 2 s × 8 mA = 32 mAs/h = 0.0089 mA 平均
// 1 年 365  24  0.0089 = 78 mAh
// 5 年 390 mAh，远 < 7.2 Ah
// 实际可撑 20+ 年（电池自放电限 5 年）

// 修复 4：拉低频时关闭非必要模块
void gnss_poll_low_power(void) {
    // 关闭 MCU 外设
    uart_disable();
    adc_disable();
    pwm_disable();
    // 只留低功耗 timer
    gnss_power_on();
    delay_ms(2000);
    gnss_power_off();
    uart_enable();
}
```

### 复盘

- **PLB 电池 5 年有效期 = 营销标配**——拉低频电流必须算到毫安级
- **GNSS 拉低频周期 30 min 通常够用**（定位精度 ±50 m 不需要 1 min 更新）
- **国产 GNSS 模组功耗省 70%**（AT6558R 8 mA vs u-blox 25 mA）
- **拉低频时关闭所有外设**，单 GNSS 工作

### 来源

- _Inbox/PLB-2026-08-01-candidates.md 候选 4
- 国产 PLB 厂商实战设计复盘

---

## 案例 5：防误触三段开关单触即发，登山客误触发

### 现象

某品牌 PLB 用拨动式三段开关（OFF / ARM / ON），登山客把 PLB 放背包里，登山杖碰一下，ON 段被滑到，PLB 立即发射。救援队出动 1 次成本 5 万 +。事后发现"登山杖碰"事件 1 年 50+ 起。

### 抓 log

事件回放 + 用户访谈：

```text
登山客 A:  "我把 PLB 放背包侧袋，登山杖顶端滑过，刚好按到 ON"
登山客 B:  "我拿 PLB 倒水时，手指滑过开关"
户外领队: "我们 12 人队 1 年误触发 1 次算好的"
```

### 定位

**三段开关机械设计问题**：

```text
拨动式三段开关：
  OFF ← 5 mm → ARM ← 5 mm → ON
  滑动力 100 g 左右
  任何"水平力" 50 g 以上都可能导致滑动

问题：
  1. 滑动距离短（5 mm）
  2. 滑动力小（100 g）
  3. 没锁定机构
  4. 翻盖缺失
```

### 修复

```text
方案 1：翻盖 + 拨动开关（推荐）
  翻盖盖住 ON 段
  必须先翻盖（拇指 + 食指）才能拨到 ON
  误触概率 < 0.1%

方案 2：长按 3 秒 + 拨动
  拨到 ON 后必须长按 3 秒
  才发射
  短按 < 3 秒不发射

方案 3：组合（最安全）
  翻盖 + 拨到 ON + 长按 3 秒
  三动作全做完才发射
  误触概率 < 0.001%
```

**实战代码**：

```c
// 防误触三动作
typedef enum {
    TRIGGER_IDLE = 0,
    TRIGGER_COVER_OPEN,     // 翻盖打开
    TRIGGER_SWITCH_ON,      // 拨到 ON
    TRIGGER_BTN_HOLD_3S,    // 长按 3 秒
} trigger_state_t;

void trigger_check(void) {
    static uint32_t switch_on_time = 0;
    static trigger_state_t state = TRIGGER_IDLE;

    // 1. 翻盖状态
    if (gpio_read(COVER_OPEN_PIN) == 1) {
        state = TRIGGER_COVER_OPEN;
    } else {
        state = TRIGGER_IDLE;
        switch_on_time = 0;
        return;
    }

    // 2. 拨到 ON
    if (gpio_read(SWITCH_ON_PIN) == 1) {
        if (switch_on_time == 0) {
            switch_on_time = millis();
        }
        state = TRIGGER_SWITCH_ON;
    } else {
        switch_on_time = 0;
        return;
    }

    // 3. 长按 3 秒
    if (millis() - switch_on_time >= 3000) {
        state = TRIGGER_BTN_HOLD_3S;
        // 触发！
        start_beacon_transmit();
        log("PLB TRIGGERED");
    }
}
```

### 复盘

- **PLB 误触发的代价是救援队出动 5 万 + 1 次**——设计上必须多动作
- **翻盖 + 长按 3 秒 + 拨动开关** 三动作必选
- **触发后必须强提示**（LED 长亮 + 蜂鸣器 + 振动），让用户知道已触发
- **误触发后支持 24 小时内取消**——发射 1 次后，用户可以拨回 OFF，但 SAR 队伍已经收到了

### 来源

- _Inbox/PLB-2026-08-01-candidates.md 候选 5
- 户外品牌 PLB 误触发现场报告
- 国产 PLB 厂商实战设计复盘

---

## 案例 6：整机浸水后开机，密封圈失效

### 现象

某 PLB 厂商宣传"IP67 防水 1 米 30 min"，实测用户在户外 0.5 米水深 20 min 后开机，PLB 短路不工作。

### 拆机

```text
拆开外壳：
  PCB 上有水珠多处
  MCU 引脚有水渍
  GNSS 模组引脚腐蚀
  电池极柱生锈

  密封圈：
  表面有裂纹
  切口不均匀
  装入外壳时扭转
```

### 定位

**密封圈材质问题**：

```text
原装：硅胶（Silicone）邵氏硬度 50
      温区 -40°C ~ +200°C
      弹性好
      抗 UV 老化

实际：EPDM 橡胶（材料错）
      温区 -30°C ~ +120°C
      弹性差
      抗 UV 老化差
      切口 1 mm 偏
```

**根因**：

1. 密封圈材料错（EPDM 替硅胶）——成本省 30%
2. 切口偏 1 mm —— 自动化产线没 100% 视觉检测
3. 装入时扭转 —— 工人装配没培训

### 修复

```text
修复 1：换回硅胶密封圈（成本上升 0.5 美元 / 套）
修复 2：切口视觉检测（机器视觉 100%）
修复 3：装配扭力扳手（0.5 N·m 标定）
修复 4：浸水测试 100% 产线抽测（1 米 30 min）
修复 5：干燥剂包（每台 1 包）
修复 6：通气阀（带 Gore-Tex 膜，平衡内外气压）
```

**视觉检测脚本**（参考）：

```python
# seal_inspect.py
import cv2
import numpy as np

def inspect_seal(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. 找密封圈轮廓
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 2. 找最大圆环轮廓
    seal_contour = None
    max_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            seal_contour = c

    # 3. 检查完整性（用圆形度）
    perimeter = cv2.arcLength(seal_contour, True)
    circularity = 4 * np.pi * max_area / (perimeter * perimeter)
    if circularity < 0.85:
        return f"FAIL: 圆形度 {circularity} < 0.85, 密封圈不完整"

    # 4. 检查切口（找轮廓中的不连续点）
    seal_contour = seal_contour.reshape(-1, 2)
    gaps = []
    for i in range(1, len(seal_contour)):
        dist = np.linalg.norm(seal_contour[i] - seal_contour[i-1])
        if dist > 5:  # 5 px 间隔 = 切口
            gaps.append(i)

    if len(gaps) > 1:
        return f"FAIL: 切口 {len(gaps)} 个, 应 1 个"

    return "PASS"
```

### 复盘

- **密封圈是 PLB 防水第一防线**——材质必选硅胶
- **切口必检**（机器视觉 100%）
- **浸水测试不能省**（每批次抽测 5%）
- **干燥剂 + Gore-Tex 通气阀** 是双重保险
- **IP67 真实场景 vs 实验室**——户外真实场景温度变化会让橡胶收缩

### 来源

- _Inbox/PLB-2026-08-01-candidates.md 候选 6
- 国产 PLB 厂商实战设计复盘

---

## 案例 7：GNSS 拉低频天线被 PCB 屏蔽遮挡，TTFF > 5 min

### 现象

某 PLB 设计 GNSS 拉低频天线放 PCB 中间，PCB 顶层地平面覆盖天线。认证测试时 TTFF > 5 min，不达标（要求 < 5 min）。

### 抓 log

GNSS 模组 NMEA 输出：

```text
冷启动：
  $GPGSA,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*30
  卫星数：0
  5 min 后：6 颗
  10 min 后：9 颗
  15 min 后：12 颗
```

**问题**：5 min 内只看到 6 颗卫星（不达 9 颗），TTFF 实际 10 min。

### 定位

**PCB 布局问题**：

```text
PCB 顶层（Top Layer）：
  ┌──────────────────────────────────────┐
  │   地平面（GND Plane）                │
  │   ┌──────────────────────┐          │
  │   │   GNSS 天线 25×25mm │  ← 在 GND 中央！
  │   │   （被屏蔽）          │          │
  │   └──────────────────────┘          │
  │                                      │
  └──────────────────────────────────────┘

后果：
  GNSS 信号 -1575.42 MHz 极化 RHCP
  穿透 GND 平面损耗 -20 dB
  天线增益 -20 dB
  灵敏度从 -167 dBm 降到 -147 dBm
  卫星数从 12 颗降到 6 颗
```

### 修复

```text
方案 1：GNSS 天线移出 GND 平面（最简）
  顶层挖空（Keep-Out Area）5 mm 半径
  天线下不放地
  增益恢复 -167 dBm

方案 2：GNSS 天线放 PCB 边缘
  净空区 ≥ 5 mm
  实际增益 -163 dBm（足够）

方案 3：GNSS 用 active 天线
  内置 LNA，增益 +20 dB
  整机能补偿 -10 dB
  成本上升 1 美元
```

**PCB 改板实战**：

```text
改前：
  Top Layer: 整面地平面
  GNSS 天线位置: PCB 中间
  GNSS 模组位置: PCB 边角

改后：
  Top Layer: 地平面 + 5 mm 挖空
  GNSS 天线位置: PCB 边角 + 5 mm 净空
  GNSS 模组位置: GNSS 天线下方
  走线: 50Ω 阻抗匹配，长度 < 5 mm
```

### 复盘

- **GNSS 天线下绝不能铺地**——这是第一原则
- **净空区 5 mm 半径**是行业标准
- **GNSS 天线 50Ω 阻抗走线**到模组，长度 < 5 mm
- **GNSS 信号 -1575.42 MHz 比 2.4 GHz 敏感**，地平面影响更大
- **改板前 PCB review**必看 GNSS 净空区

### 来源

- _Inbox/PLB-2026-08-01-candidates.md 候选 7
- 国产 PLB 厂商实战 PCB 设计复盘

---

## 案例 8：UIN 协议码写错 (0x10 写 0x02)，整个批次 MCC 解析失败

### 现象

某 PLB 厂商固件工程师把 0x10 (ELT ICAO) 错写成 0x02 (PLB Serial)。但 UIN 字符是正确的 15 字符 hex。MCC 收到 UIN 后按 0x02 (PLB) 协议解析，但 ELT 报文格式跟 PLB 略不同，导致解析错。

### 抓 log

LEOLUT 测试台：

```text
抓包 #1:
  UIN = 19C80000E0A12345
  Protocol = 0x02 (PLB)
  报文: 0xFF FF FF FF FF (位置全填 0xFF)
  解析: country_id=0xE0A1, serial=0x2345
  实际: 应该是 ELT 24-bit ICAO 协议 (0x10)

问题：
  0x02 协议要求 position data 在位 86-105
  0x10 协议要求 aircraft 24-bit address 在位 86-109
  同样位 86-105 数据，0x02 解析为位置，0x10 解析为 ICAO address
  → 错位
```

### 定位

**协议码错位问题**：

```c
// 错：硬编码 0x02
const uint8_t BEACON_TYPE_PLB = 0x02;
// 实际应该是 0x10 (ELT)

// 修复：跟产品类型强关联
typedef enum {
    BEACON_TYPE_EPIRB_MMSI = 0x01,
    BEACON_TYPE_PLB_SERIAL = 0x02,
    BEACON_TYPE_ELT_24BIT  = 0x03,
    BEACON_TYPE_ELT_ICAO   = 0x10,
    BEACON_TYPE_PLB_TEST   = 0x20,
} beacon_protocol_t;

// 编译时检查
_Static_assert(BEACON_TYPE_PLB_SERIAL == 0x02, "PLB 协议码必须 0x02");
_Static_assert(BEACON_TYPE_ELT_ICAO == 0x10, "ELT 协议码必须 0x10");

// 运行时检查
void check_beacon_type(beacon_protocol_t p) {
    switch (p) {
        case BEACON_TYPE_EPIRB_MMSI:
        case BEACON_TYPE_PLB_SERIAL:
        case BEACON_TYPE_ELT_24BIT:
        case BEACON_TYPE_ELT_ICAO:
        case BEACON_TYPE_PLB_TEST:
            break;
        default:
            log("ERROR: 未知协议码 0x%02X", p);
            // 不发射
            while(1);
    }
}
```

### 修复

```text
方案 1：编译时 _Static_assert 检查
方案 2：固件版本号烧录到 UIN aux 字段
方案 3：批量测试时每台都跑协议码自检
方案 4：LEOLUT 测试台对每个 UIN 强制解析测试
```

**自检脚本**：

```python
# protocol_check.py
import csv

# 读烧录器日志
beacons = []
with open('burn_log.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        uin = row['uin_hex']
        protocol = int(uin[4:6], 16)  # 取协议码
        product_type = row['product_type']  # 'PLB' / 'EPIRB' / 'ELT'
        beacons.append((uin, protocol, product_type))

# 检查
for uin, protocol, product_type in beacons:
    expected_protocol = {
        'PLB': 0x02,
        'EPIRB': 0x01,
        'ELT_24BIT': 0x03,
        'ELT_ICAO': 0x10,
    }.get(product_type, None)

    if expected_protocol is None:
        print(f"未知产品类型 {product_type}: {uin}")
        continue

    if protocol != expected_protocol:
        print(f"协议码错 {uin}: 烧 {protocol:#04x} 期望 {expected_protocol:#04x}")
```

### 复盘

- **协议码是产品类型核心标志**——错一个 bit 全错
- **烧录器跟产品类型必须强绑定**，不能手动选协议码
- **LEOLUT 测试台 100% 协议码解析测试**
- **批量出货前 100% 抓包对协议码**

### 来源

- _Inbox/PLB-2026-08-01-candidates.md 候选 8
- 国产 PLB 厂商实战固件 bug 复盘

---

## 案例 9：电池在 -40°C 跌容 70%，极地场景不合格

### 现象

某 PLB 厂商用国产 Li-SOCl2 电池，标称 -40°C ~ +85°C 工作。极地客户实测 -40°C 持续发射只能撑 8 小时（要求 24 小时）。

### 抓 log

低温试验箱 + 功率分析仪：

```text
25°C: 持续发射 36 小时
 0°C: 持续发射 30 小时
-20°C: 持续发射 18 小时
-30°C: 持续发射 12 小时
-40°C: 持续发射 8 小时
```

**问题**：-40°C 跌容 70%，极地场景不合格（COSPAS-SARSAT 要求 5°C 下 24 h）。

### 定位

**电池电化学问题**：

```text
Li-SOCl2 电池：
  25°C 容量: 7.2 Ah
  -40°C 容量: 7.2 × 0.3 = 2.16 Ah  (跌 70%)

原因：
  -40°C 电解液粘度上升
  Li+ 离子扩散速度下降
  内阻从 50 mΩ 升到 800 mΩ
  5W PA 持续发射，电流 1.5A @ 5V
  5°C 下 1.5A 不难
  -40°C 下 1.5A 几乎抽不出来
```

### 修复

```text
方案 1：换电芯（推荐）
  Li-SOCl2 工业级电芯：-40°C 跌容 30%
  Li-SOCl2 军用级电芯：-40°C 跌容 10%
  价格 3 倍

方案 2：自加热电池
  电池内部加热膜
  触发时先加热 30 s（功耗 500 mA × 30 s = 15 mAs）
  加热后温度升到 0°C
  之后正常发射
  成本上升 2 美元

方案 3：双电池
  主电池 7.2 Ah + 备用电池 2 Ah
  低温下自动切到备用电池
  备用电池有自加热
  成本上升 5 美元
```

**实战**：

```c
// 电池自加热控制
void battery_heat_control(void) {
    static uint32_t heat_start = 0;

    if (temperature < -10) {
        if (heat_start == 0) {
            heat_start = millis();
            // 启动加热
            heater_enable();
        }

        if (millis() - heat_start < 30000) {
            // 加热中
            log("电池加热中: 温度 %d°C", temperature);
        } else {
            // 加热完成
            heater_disable();
            // 启动发射
            beacon_transmit_406();
        }
    } else {
        // 温度够，直接发射
        beacon_transmit_406();
    }
}
```

### 复盘

- **电池低温特性 = 极地 PLB 生死线**
- **Li-SOCl2 普通级 -40°C 跌容 70%**——工业级跌 30%，军用级跌 10%
- **自加热电池是性价比最高方案**（成本 +2 美元）
- **极地客户必查电池工作温度**
- **批量出货前低温试验 100%**

### 来源

- _Inbox/PLB-2026-08-01-candidates.md 候选 9
- 国产 PLB 厂商实战电池选型复盘

---

## 案例汇总

| # | 现象 | 根因 | 难度 |
| --- | --- | --- | --- |
| 1 | UIN 重复分配 | 烧录器无全局查重 | 中 |
| 2 | BCH 校验失败 | 编码多项式错 | 中 |
| 3 | 121.5 MHz 测向差 | TCXO 精度不够 | 中 |
| 4 | 5 年电池变 2 年 | GNSS 拉低频电流大 | 低 |
| 5 | 防误触单触即发 | 拨动开关无锁定 | 低 |
| 6 | 浸水后短路 | 密封圈材质错 + 切口偏 | 中 |
| 7 | TTFF > 5 min | GNSS 天线被 GND 屏蔽 | 低 |
| 8 | 协议码错位 | 固件硬编码错 | 低 |
| 9 | 电池 -40°C 跌容 70% | Li-SOCl2 普通级 | 中 |

## 关联文档

- `bus/plb.md` 主题入口
- `bus/plb-practical.md` 调试流程速查
- `bus/plb-deep-dive.md` 协议栈 / 编码 / BCH / GNSS 深挖
- `bus/plb-index.md` 主题地图 + 导航
