# Satellite-IoT Practical Guide

## 目标

本文用于卫星物联网工程调试：NB-IoT NTN、北斗短报文、Iridium SBD、Starlink IoT、Garmin inReach 五路线的最小系统、关键参数、抓包工具、错误码、5 秒定位、产线常见故障的快速定位。

## 最小接线（以移远 BG95-M3 NB-IoT NTN 为例）

```text
VDD ──── VDD (3.3V ~ 4.3V，NB-IoT 峰值电流 ~500 mA)
GND ──── GND
ANT ──── L 频段天线（1626.5 ~ 1660.5 MHz 下行，1525 ~ 1559 MHz 上行）
       ─ 或 GPS L1（1575.42 MHz）有源天线
DEC1 ──── 100nF + 10µF 紧靠 VDD 引脚
RESET ── 拉低 100ms 复位
USIM ──── SIM 卡座（NB-IoT NTN 专用 USIM）
```

**关键约束**：

- 电源峰值电流 500 mA，电源纹波 < 200 mV，电池建议 1500 mAh+
- L 频段天线 VSWR < 2.0（NTN 链路预算紧张，不容许失配）
- 卫星仰角选 20°+（避免多径、链路余量至少 3 dB）
- 模组与 MCU UART 走线 < 100 mm，波特率 115200 起步
- GNSS 有源天线供电 3.3V，电流 < 50 mA

## NB-IoT NTN 关键参数

### NTN 时序参数（3GPP R17）

| 参数 | 典型值 | 影响 |
| --- | --- | --- |
| GSE（GNSS 星历）有效性 | < 3 小时 | 过期后搜星失败 |
| 服务链路时延（LEO） | 20~50 ms | TCP 应用需调超时 |
| 多普勒频偏（400 MHz LEO） | ±10 kHz | 模组需预补偿 |
| Doppler rate | ±0.5 Hz/s | 终端需跟踪 |
| 最大路径损耗（MCL） | 164 dB（NTN 终端） | 链路预算基准 |
| 接入时延（LEO 单跳） | 5~15 s | 含 PRACH（Physical Random Access Channel，物理随机接入信道）/ RACH（Random Access Channel，随机接入信道）排队 |
| eDRX（Extended DRX，扩展非连续接收）周期 | 10.24 s ~ ~41 min | NTN 允许更长 |
| 短报文 payload | 1000 字节级 | 适合应用层分包 |

### NTN 接入流程

```text
1. 终端开机
2. 扫频：扫 NTN 频段（运营商分配）
3. 读 SIB（System Information Block，系统信息块）拿到 GSE / Doppler 预补偿
4. PRACH 接入：带 Doppler pre-compensation
5. RRC Connection Setup
6. Attach / PDU Session Establishment
7. 数据传输
8. 进入 eDRX / PSM（Power Saving Mode，省电模式）
```

### NTN 频段（3GPP 定义）

| 频段 | 频率 | 运营商 / 国家 | 状态 |
| --- | --- | --- | --- |
| L-band n255 | 1525 ~ 1660 MHz | Inmarsat / 欧洲 | 商用 |
| S-band n256 | 1980 ~ 2010 / 2170 ~ 2200 MHz | 欧洲 / 中国 | 试点 |
| n254 | 1610 ~ 1626.5 MHz | 韩国 | 试点 |
| 2 GHz 频段（国内） | 待分配 | 亚太卫星合作 | 2025+ 试商用 |

## 北斗短报文关键参数

### 北斗三号 RDSS（Radio Determination Satellite Service，卫星无线电测定业务）参数

| 参数 | 典型值 | 备注 |
| --- | --- | --- |
| 入站频点（L 频段） | 1610 ~ 1626.5 MHz | 用户 → 卫星 |
| 出站频点（S 频段） | 2483.5 ~ 2500 MHz | 卫星 → 用户 |
| 短报文长度 | 1000 汉字（普通卡） | 单次上行 |
| 定位精度 | 水平 10 m，高程 10 m | 民用级 |
| 首次定位 TTFF | 冷启动 < 60 s | 需星历有效 |
| 电文加密 | AES-128 / SM4 | 国产化支持 |
| 卡类型 | 北斗 RDSS 卡（专用） | 与普通 SIM 不通用 |

### 北斗短报文通信流程

```text
1. RDSS 模组上电，读取北斗卡信息
2. 申请入网注册（提交用户 ID + 加密因子）
3. 等待中心站确认（地面信关站回执）
4. 定位（同时接收 RNSS（Radio Navigation Satellite Service，卫星无线电导航业务）信号）
5. 编码短报文（用户 ID + 电文内容 + 校验）
6. 入站发射（按 1/2/3 颗 GEO 卫星波束）
7. 地面中心站接收并广播
8. 目标用户接收出站信号
9. 收到 ACK 回执（可选）

电文长度限制：
  普通卡    → 1000 汉字 / 1 次
  升级卡    → 1680 汉字 / 1 次（部分）
  集团卡    → 更大容量
  频度限制  → 1 次 / 1 min（普通卡）
```

## Iridium SBD 关键参数

| 参数 | 典型值 | 备注 |
| --- | --- | --- |
| 上行 / 下行频段 | 1616 ~ 1626.5 MHz（L 频段） | 66 颗 LEO 卫星 |
| SBD 消息大小 | MO 340 B / MT 270 B | 单次 payload |
| MO 成功率 | > 95%（开阔天空） | 仰角 > 8° |
| 卫星过顶窗口 | ~10 min / 单颗 | 66 颗近乎全时覆盖 |
| 接入时延 | 5~30 s | 含多普勒同步 |
| 时延（LEO 单跳） | 20~50 ms | 信号传播 |
| 资费 | ~$0.05~$0.50 / 消息 | 套餐另算 |
| 激活要求 | IMEI 注册 + IMEI 入网 | 必须先注册 |

### Iridium SBD 通信流程

```text
1. 模组上电，AT 命令初始化（AT+CIER=1,1,1,1）
2. 扫星：搜 SBD 波束
3. 附着 Iridium 网络（attach）
4. 检查信号强度（AT+CSQ → +CSQ:5）
5. 发送 MO（Mobile Originated）：
   - AT+SBDWB=<len>  → 写 buffer
   - AT+SBDI → 触发发送
   - 等待 +SBDI: <MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MT queued>
6. 接收 MT（Mobile Terminated）：
   - AT+SBDRT → 读 buffer
   - AT+SBDD → 清理 buffer
7. 短报文回执：返回 MOMSN（Mobile Originated Message Sequence Number）
```

## Starlink IoT 关键参数（2024 公布）

| 参数 | 典型值 | 备注 |
| --- | --- | --- |
| 工作频段 | 1.9 GHz T-Mobile 段 | 美国主导 |
| 速率 | 数十 kbps（IoT 模式） | 初期非高速 |
| 时延 | 20~40 ms | LEO 优势 |
| 覆盖 | 美国 + 部分海外 | 国内未开放 |
| 终端要求 | LTE 模组固件升级 | 需 Starlink 认证 |
| Direct to Cell | 2024 起短信 + 通话 | 2025+ IoT 模式 |

## Garmin inReach / SPOT 关键参数

| 参数 | Garmin inReach | SPOT |
| --- | --- | --- |
| 网络 | Iridium | Globalstar |
| 短报文 | 160 字符 | 41~110 字符 |
| 双向通信 | 是 | 否（仅 SOS 单向） |
| 定位精度 | 5 m | 5~10 m |
| 续航 | 14 天（10 min 跟踪） | 14 天 |
| 资费 | $14.95 ~ $64.95 / 月 | $14.95 / 月起 |

## 抓包工具

| 工具 | 路线 | 优势 | 限制 |
| --- | --- | --- | --- |
| QLog / QXDM | NB-IoT NTN | 完整 RRC / NAS / NAS-MM 信令 | 需高通平台 |
| Iridium Analyzer（RockBLOCK / SBD log） | Iridium SBD | 解析 MO/MT SBD 信令 | 需 Iridium 设备 |
| 北斗 RDSS log（中斗微星 / 华力创通） | 北斗短报文 | 解析 RDSS 帧格式 + 入网注册流程 | 需北斗模组 |
| 串口 log + AT 回显 | 通用 | 必备、最快 | 浅层 |
| MobileInsight | NB-IoT NTN | 解析 Android logcat NTN 信令 | 仅 Android |
| Wireshark + 自定义 dissector | NB-IoT NTN | 解析 S1AP / NAS | 需 pcap 源 |
| SDR（HackRF / LimeSDR） | L/S 频段 | 看空中 RF | 需射频经验 |
| CMW500 + NTN 选件 | NB-IoT NTN | 模拟卫星信道（含 Doppler） | 贵（>30K 美元） |

**产线推荐组合**：

```text
研发调试：QLog + 北斗 RDSS log + 串口 AT log（多线程抓）
产线批量：串口 log 跑 AT 自动化脚本（看搜星成功率 + 短报文成功率）
压测：CMW500 模拟卫星弱信号 + Doppler
户外测试：实际开阔天空 + 时间窗（卫星过顶预测）
```

## 调试步骤

### NB-IoT NTN 调试流程

1. **确认 USIM 卡**：插入 NB-IoT NTN 专用卡（普通 NB-IoT 卡不通用）
2. **配置 APN**：通过 AT+CGDCONT 配置 NTN APN（运营商下发）
3. **搜星**：AT+COPS=? + AT+CEREG?，看是否注册到 PLMN
4. **检查 GSE / Doppler**：模组 log 应有 GSE 接收 + Doppler pre-compensation
5. **PRACH 接入**：看 +CEREG: 5（registered, roaming）/ 1（home）
6. **PDU session**：AT+CGACT=1,1 激活
7. **数据传输**：TCP / UDP / MQTT 测试
8. **看错误码**：+CME ERROR / +CEREG 状态

### 北斗短报文调试流程

1. **插入北斗 RDSS 卡**：特殊卡座（与 SIM 物理上同尺寸但电气不同）
2. **模组初始化**：读卡 → 申请入网（用户 ID + 密钥）
3. **检查入网状态**：AT 命令查询 / 模组状态字
4. **定位**：RNSS 通道搜星，10 颗+ 即可
5. **发送短报文**：AT 命令编码 + 发射
6. **等待 ACK**：地面中心站回执
7. **接收短报文**：出站频点监听，ACK 回执
8. **看 log**：RDSS 帧格式 + 入网时延

### Iridium SBD 调试流程

1. **IMEI 注册**：先在 Iridium 官网注册 IMEI（不可跳）
2. **插入 SBD 卡**：或写 SIM 卡（Iridium SBD 服务）
3. **AT 初始化**：AT+CIER=1,1,1,1 启用错误回显
4. **检查信号**：AT+CSQ → 信号 0~5，3 以上合格
5. **附网**：AT+SBDDET / AT+SBDREG
6. **发送 MO**：AT+SBDWB 写 buffer + AT+SBDI 触发
7. **接收 MT**：AT+SBDRT + AT+SBDD
8. **看 log**：+SBDI 返回 MO status / MOMSN / MT status

## 常见问题速查

| 现象 | 优先检查 |
| --- | --- |
| NTN 搜不到卫星 | GSE 过期 / 频段错 / 仰角不够 / USIM 卡错 |
| NTN 附着失败 | Doppler 未预补偿 / 卫星未对准 / PLMN 错 |
| 北斗入网失败 | 卡未授权 / 密钥错 / 频点未对准 |
| 北斗电文发送失败 | 长度超 1000 汉字 / 频度超限 / 中心站不可达 |
| Iridium SBD 失败 | IMEI 未注册 / 信号差 / MO 通道关闭 |
| Iridium +SBDI: 4, x, 0, 0, 0, 0 | 网络未注册 / 重新 attach |
| Starlink 无信号 | 不在美国 / 频段未授权 / 模组固件版本不对 |
| 链路预算差 | 天线增益低 / 仰角低 / 多径 |
| 短报文丢失 | LEO 过顶窗口短 / 数据超容量 |
| 定位漂移 | GNSS 卫星数 < 4 / 城市峡谷 |

## 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| NTN 搜不到星 | GSE / 频段 / 卡 | 查 AT+CEREG 状态 |
| NTN 附着失败 | Doppler / 卫星 | 看 PRACH 失败原因 |
| 北斗入网失败 | 卡 / 密钥 / 频点 | 查模组入网状态字 |
| 北斗电文失败 | 长度 / 频度 | 切小电文 + 错开发送 |
| Iridium SBD 失败 | IMEI / 信号 | 查 +SBDI 返回码 |
| +SBDI: 4 | 网络未注册 | AT+SBDREG 重附网 |
| 链路预算差 | 天线 / 仰角 | 选 20°+ 仰角天线 |
| 短报文丢失 | 容量 / 窗口 | 分包 + 监控窗口期 |
| 定位漂移 | 卫星数 < 4 | 移到开阔天空 |
| 资费暴涨 | 计费策略 | 加计费预警 + 限速 |

## 错误码速查

### NB-IoT NTN 常见 +CME ERROR

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 30 | NO NETWORK | 搜不到网络 |
| 514 | BUSY | 并发 AT 命令阻塞 |
| 515 | ABORTED | 流程被中止 |
| 100 | INVALID SIM | USIM 卡无效 |
| 103 | ILLEGAL MS | 移动台非法 |
| 106 | ILLEGAL ME | 移动设备非法 |
| 107 | GPRS NOT ALLOWED | GPRS 不允许 |
| 111 | PLMN NOT ALLOWED | PLMN 不允许 |
| 112 | LOCATION NOT ALLOWED | 位置区不允许 |
| 133 | SERVICE NOT SUBSCRIBED | 服务未订阅 |
| 149 | PDP AUTH FAILURE | PDP 鉴权失败 |

### 北斗短报文常见错误

| 错误 | 触发 |
| --- | --- |
| 入网失败 | 卡未授权 / 频点错 |
| 发射功率不足 | 模组供电不足 / 天线失配 |
| 电文长度超限 | 超过 1000 汉字 |
| 频度超限 | 1 min 内重复发 |
| 中心站拒收 | 加密因子错 / 协议版本不匹配 |
| 收不到 ACK | 出站链路问题 / 卡未激活接收 |

### Iridium SBD 错误码（+SBDI 返回）

| MO status | 含义 | 处理 |
| --- | --- | --- |
| 0 | Success | 正常 |
| 1 | Timeout waiting for response | 网络超时，重发 |
| 2 | MO message has too few bytes | 消息太短 |
| 3 | MO message has too many bytes | 消息太长（>340 B） |
| 4 | Gateway not available | 地面网关不可达 |
| 5 | Link lost during transmit | 发送过程链路丢失 |
| 6 | MO message has unsupported CRC | CRC 错 |
| 7 | Sequence number out of range | MOMSN 越界 |
| 8 | MT message has too few bytes | MT 长度错 |
| 9 | MT message has too many bytes | MT 长度错 |
| 10 | Gateway response timeout | 网关响应超时 |
| 11 | Iridium protocol fatal error | 协议错 |
| 12 | IMEI not provisioned | IMEI 未注册 |

## 实战注意

### NB-IoT NTN 实战

- **GSE 是关键**：3 小时过期，必须周期性重读 SIB-NTN
- **Doppler 预补偿**：LEO 多普勒 ±10 kHz，模组需支持
- **APN 必须是 NTN 专用**：与地面 NB-IoT APN 不同
- **eDRX 必须开**：避免频繁寻呼（卫星功耗大）
- **认证卡用专用 USIM**：与 NB-IoT 卡不同
- **天线 VSWR < 1.5**：链路预算紧

### 北斗短报文实战

- **入网注册必须做**：第一次开机注册后保存
- **频度限制**：1 min / 1 条（普通卡）
- **电文长度**：1000 汉字 / 1 次（超长需分包）
- **加密卡**：国产化必须 SM4
- **天线方向**：仰角 20°~70° 最佳
- **ACK 回执**：发送后 30 s 内收不到为失败
- **量产测试**：户外开阔天空 + 实际卫星过顶时段

### Iridium SBD 实战

- **IMEI 必须先注册**：注册后 24 h 生效
- **SBD 模组卡 vs SBD 服务卡**：硬件相同，服务开通方式不同
- **短报文长度**：MO 340 B / MT 270 B（严格限制）
- **MOMSN 必须单调递增**：防重放
- **MT 收不到**：检查 SBD 服务中心 URL（某些场景需指定）
- **量产计费预警**：$0.05/条，1000 台 1 天 1000 条 = $50
- **户外天线**：全向天线（4 dBi）+ 仰角 8°+

### Starlink IoT 实战

- **频段限制**：仅 1.9 GHz（T-Mobile 美国段）
- **认证模组**：必须 Starlink 认证通过
- **覆盖**：美国 + 部分海外，国内暂无
- **2025+ IoT 模式**：尚未全开放

## 检查清单

```text
□ 电源：3.3V ~ 4.3V，峰值电流 500 mA 余量
□ 去耦：100nF + 10µF 紧靠 VDD
□ 天线：L 频段 VSWR < 1.5，仰角 20°+
□ 模组：固件版本（移远 BG95-M3 R17 NTN 固件）
□ USIM：NTN 专用卡（与 NB-IoT 卡区分）
□ APN：NTN 专用 APN
□ GSE：SIB-NTN 星历下载成功
□ Doppler：模组支持 pre-compensation
□ 短报文长度：按路线限制
□ 频度限制：1 min / 1 条（北斗）
□ IMEI：Iridium 必须先注册
□ 户外测试：开阔天空 + 卫星过顶时段
□ 资费：监控用量 + 计费预警
□ 错误码：+CME / +CEREG / +SBDI 三套都要解析
```

## 关联文档

- `bus/satellite-iot.md` 主题入口
- `bus/satellite-iot-deep-dive.md` 协议栈 / 卫星注册 / 链路预算深挖
- `bus/satellite-iot-failure-cases.md` 产线实战案例
- `bus/satellite-iot-index.md` 主题地图 + 导航
