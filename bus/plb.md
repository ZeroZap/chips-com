# PLB（Personal Locator Beacon，个人定位信标）

## 定位

PLB 是 COSPAS-SARSAT 国际卫星搜救系统下的"个人"紧急定位信标，工作在 406 MHz 频段，配合 121.5 MHz 近场测向辅助信号，由 GNSS 提供位置。1982 年由前苏联、加拿大、法国、美国联合建成，目标是"按下按钮，全球救援力量可在 1 小时内收到求救信号和位置"。

PLB 跟 EPIRB（Emergency Position Indicating Radio Beacon，船用）、ELT（Emergency Locator Transmitter，航空）同源同标准，是 406 MHz 搜救信标家族里"陆地/个人"那一个分支。

```text
406 MHz 信标家族（按用途分）：
  EPIRB  → 船用（海洋救生），自动或手动释放
  ELT    → 航空（飞机坠落），自动触发
  PLB    → 个人（户外 / 登山 / 远洋 / 探险），手动触发
```

PLB 体积通常为手持大小（典型 12~15 cm 长、200~300 g 重），电池 5~7 年有效期，触发后持续发射 24~48 小时以上。是登山、远洋、沙漠、极地、远途航空等"失联即死亡"场景的最终求救手段。

## 跟 EPIRB / ELT 的关系

| 项 | PLB | EPIRB | ELT |
| --- | --- | --- | --- |
| 用途 | 个人 / 户外 | 船用 | 航空 |
| 触发 | 手动（部分支持自动） | 自动（船沉水压释放）+ 手动 | 自动（G 触发器）+ 手动 |
| 频段 | 406 MHz + 121.5 MHz + GNSS | 同 | 同 |
| 标准 | COSPAS-SARSAT T.007 | 同 | 同 |
| 注册 | 个人到国家救援中心 | 船舶到船籍国 | 飞机到民航局 |
| 功率 | 5 W（406 MHz） | 5 W（406 MHz） | 5 W（406 MHz） |
| 电池 | 5~7 年 | 5 年 | 5~6 年 |
| 价格 | 200~600 美元 | 800~3000 美元 | 1500~5000 美元 |

三者**协议层完全一致**（共用 COSPAS-SARSAT 系统），差异只在注册管理、触发机构、产品形态。

## 跟卫星通讯 / Garmin inReach 的关系

PLB 跟 inReach、SPOT、Iridium 卫星电话属于"户外紧急通讯"但工作模式完全不同：

```text
                PLB              inReach / SPOT / 卫星电话
信号方向        单向（上行为主）  双向
协议            COSPAS-SARSAT     Iridium / Globalstar 商用
覆盖            全球（LEO+GEO）    全球（LEO 商业）
主要用途        求救援            求救援 + 日常通讯
电池续航        5~7 年待命        数天到数周
位置            紧急信号内置      主动查询 / 定时回传
资费            无（救援免费）    订阅（30~100 美元/月）
误触成本        救援队出动        误触发短信
```

PLB 优势：**免月费、5 年待命、全球无盲区**。劣势：**只能发不能收**，发完不知道有没有人收。

实战经验：户外装备圈普遍"PLB + inReach 双带"。PLB 是"最后保险"（手机 / inReach 全失败才用），inReach 是"日常双向通讯"。两类产品**互补不互替**。

## 关键体系

PLB 涉及四个核心系统，必须同时理解：

1. **COSPAS-SARSAT 国际救援卫星系统**（俄罗斯 / 加拿大 / 法国 / 美国 1982 年起）
   - LEO 极轨道卫星（LEOSAR）+ GEO 静轨道卫星（GEOSAR）+ 中继（MEO 2024+）
   - 4 颗 SARR / 6 颗 SAR 仪器搭载在 NOAA / MetOp / Elektro 卫星上
   - 全球分布，406 MHz 上行 + 1544.5 MHz 下行到地面站 LUT / MEOLUT

2. **406 MHz 数字信号**（上行求救，PLB 主动发射）
   - 频段 406.0 ~ 406.1 MHz，5 W 功率
   - 每 50 秒发射一次，0.5 秒时长
   - 含 UIN（Unique Identification Number，全球唯一 15 字符 hex）、位置、协议标志

3. **121.5 MHz 模拟信号**（下行近场定位，PLB 主动发射，飞机 / 船舶测向接收）
   - 频段 121.5 MHz，50~100 mW 功率
   - 连续发射（PLB 触发后），用于 SAR 队伍抵近时的最后 5~10 km 测向

4. **GNSS 定位集成**（GPS / GLONASS / Galileo / 北斗多模）
   - PLB 内置 GNSS 接收机，首次定位后写入 406 MHz 报文
   - 定位精度典型 ±50 m（无 GNSS 时 ±5 km，多普勒定位）

## 关键协议

PLB 涉及的核心协议名词：

- **MID（Maritime Identification Digits，海事识别数字）**：3 位数字国家码（ITU 分配），例如中国 412、美国 366/367/368/369、加拿大 316、英国 232/233/236。PLB 编码进 UIN。
- **UIN（Unique Identification Number，唯一识别号）**：15 字符 hex 串（60 bit），结构 = 国家码 + 协议码 + 序列号，例 `ADCC00012345678`。全球唯一，注册到国家救援中心。
- **Beacon Type（信标类型）**：0 = PLB、1 = EPIRB（标准）、2 = ELT（标准）、3 = 其它。决定报文解析路径。
- **编码协议**：
  - **Long Form**（短消息 144 bit payload）：含位置（lat/lon） + 编码国家 + 协议标志
  - **Short Message**（短消息 112 bit payload）：仅含 UIN + beacon type，位置由多普勒解算
- **BCH 纠错**：BCH(250,144) 或 BCH(202,112)，最多纠 40 / 60 bit 突发错。Bit error rate 1e-5 仍能正确解析。

## 关键芯片 / 模块

PLB 整机里有 3 类关键器件：

| 器件 | 国外代表 | 国产代表 | 角色 |
| --- | --- | --- | --- |
| 模拟 121.5 MHz 发射 | RF Solutions DRF1215、Silicon Labs Si4063 | LKT4211（深圳）、瑞迪恩 RD1215 | 测向信号源 |
| 数字 406 MHz 发射 | Microsemi（Microchip）Syracuse 4 系列、Acmetech | 海积 HZB406、中电 54 所 CEP-1 | 主求救信号源 |
| GNSS 接收机 | u-blox MAX-M10、Quectel LG77L | 中科微 AT6558R、芯与物 CC4056P | 位置定位 |

**核心难点**：406 MHz 频率合成 + 5W PA + 频率稳定度 ±0.5 ppm（卫星多普勒解算基础）。Microsemi Syracuse 系列是行业事实标准（全球 70%+ PLB 用），国产海积 HZB406 在 2022 年起逐步量产。

## 认证

PLB 上市前必须过的认证（按市场分）：

- **COSPAS-SARSAT Type Approval**（C/S T.007）：强制。所有 PLB 必过，测试 406 MHz 频谱、报文格式、UIN 唯一性、电池续航、-40°C~+55°C 温区。
- **FCC Part 80 / 87**（美国）：强制。频谱 + 杂散。
- **CE / RED**（欧盟）：强制。
- **CCS / DNV**（船检）：仅船用配套才要。
- **国家入网**（中国型号核准 SRRC）：必须。
- **电池有效期**：5 年（消费级）/ 7 年（专业级），过期强制更换。

## 嵌入式产线典型故障

PLB 跟消费电子不同，**故障 = 人命**。产线必查项：

- 406 MHz 发射功率 < 5W ±1dB（COSPAS-SARSAT 必查项）
- 报文 BCH 校验失败（编码器固件 bug，1e-5 错误率上线）
- UIN 注册失败（重复分配、协议码错）
- 121.5 MHz 频率偏移 > ±50 Hz（飞机测向灵敏度不够）
- GNSS 首次定位时间 TTFF > 5 min（远洋场景不达标）
- 电池在 -40°C 容量下降 > 50%（极地场景）
- G 触发器误触发（航空 ELT 常见，PLB 较少但要测）

## 延伸阅读

- `bus/plb-practical.md` 调试流程速查 / 抓包 / 错误码
- `bus/plb-deep-dive.md` COSPAS-SARSAT / 406 MHz 编码 / BCH / UIN 解析深挖
- `bus/plb-failure-cases.md` 产线实战案例（编码错 / 触发错 / 认证失败等）
- `bus/plb-index.md` 主题地图 + 读者路径
