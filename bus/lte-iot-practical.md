# LTE-IoT Practical Guide

## 目标

本文用于 LTE-IoT 工程调试：模组选型、SIM/APN 配置、AT 命令、蜂窝注册、PSM/eDRX、错误码、产线常见故障的快速定位。

## 最小接线（以 EC200N 为例）

```text
VDD  ──── 3.4~4.3V（典型 3.8V，瞬态 2A 峰值）
GND  ──── GND（多个引脚全部接）
USB  ──── USB 2.0（调试 / 烧 firmware / log）
TX/RX ──── UART 115200 8N1（接 MCU 串口）
PWRKEY ──── 拉低 ≥ 100ms 上电
RESET  ──── 拉低 ≥ 200ms 复位
ANT   ──── 主天线 50Ω（IPEX / 焊接）
```

**关键约束**：

- 电源纹波 < 100 mVpp，瞬态电流 2 A（Cat 1 突发传输）
- 模组下方禁铺地（射频辐射）
- SIM 卡座信号线短而直（< 30 mm）
- 天线匹配到 50Ω，VSWR < 2（推荐 < 1.5）
- 模组需有完整地平面
- UART 1.8V/3.3V 注意电平匹配（移远新模组 1.8V）

## 关键参数

### 蜂窝模组选型三件套

| 参数 | 选项 | 影响 |
| --- | --- | --- |
| Category | Cat 1 / Cat M1 / Cat NB1/NB2 | 速率 / 功耗 / 移动性 |
| 频段 | 国内：B1/B3/B5/B8/B39/B40/B41 | 运营商部署匹配 |
| 封装 | LCC / Mini PCIe / M.2 | 尺寸 / 引脚兼容性 |

**典型选型**：

```text
高速 + 移动（POS / 车载）        → Cat 1  + B1/B3/B5/B8/B39/B40/B41
中速 + 中移动（车队 / 资产追踪） → Cat M1 + 全球多频段
低速 + 静态（抄表 / 烟雾）       → NB-IoT + B3/B5/B8
```

### APN 配置

| 场景 | APN | 用户名 / 密码 | 认证 |
| --- | --- | --- | --- |
| 中国移动公网 | cmnet / cmwap | 空 / 空 | 无 |
| 中国电信公网 | ctnet | 空 / 空 | 无 |
| 中国联通公网 | uninet / 3gnet | 空 / 空 | 无 |
| 中国移动 NB-IoT | cmnb | 空 / 空 | 无 |
| 中国电信 NB-IoT | ctnb | 空 / 空 | 无 |
| 中国联通 NB-IoT | nbiot | 空 / 空 | 无 |
| 专网 / 私有平台 | 自定义（如 abc.example.com） | 视平台 | PAP / CHAP |

**APN 设置命令**：

```c
// 设置 APN（移远 EC200N）
AT+QICSGP=1,1,"cmnet","","",0  // cid=1, IPV4, APN, user, pwd, auth
AT+QIACT=1                        // 激活 PDP
AT+QIACT?                         // 查询激活状态

// 设置 APN（SIM7080 / SIM7000）
AT+CNMP=38     // 选 LTE only
AT+CMNB=2      // NB-IoT
AT+CSTT="cmnb","",""
AT+CIICR
AT+CIFSR        // 拿 IP
AT+CIPSTART="TCP","example.com",80
```

### 蜂窝注册状态

```c
AT+CREG?        // CS 域注册（Cat 1 语音）
AT+CEREG?       // EPS 域注册（Cat M1 / NB-IoT 数据）
AT+CGREG?       // GPRS 域注册（GSM fallback）
```

返回格式：

```text
+CREG: <n>,<stat>[,[<lac>],[<ci>],[<AcT>],[<cause_type>],[<reject_cause>]]
+CEREG: <n>,<stat>[,[<tac>],[<ci>],[<AcT>],[[cause_type],[reject_cause]]]]

stat:
  0 = 未注册，未搜
  1 = 已注册，本地网
  2 = 搜网中
  3 = 拒绝
  4 = 未知
  5 = 已注册，漫游
```

### 关键状态码含义

| stat | 含义 | 行动 |
| --- | --- | --- |
| 0 | 未注册 | 等 30s 重查，确认天线 / SIM |
| 2 | 搜网中 | 正常，等待 |
| 3 | 拒绝 | 看 reject_cause（NAS EMM cause） |
| 5 | 漫游 | 检查漫游 APN |

### 信号质量

```c
AT+CSQ         // 通用 CSQ（0~31）
AT+QENG="servingcell"   // 移远：详细服务小区
AT+CESQ        // 3GPP TS 27.007 扩展
```

CSQ 换算：

```text
CSQ 0       = -113 dBm 或更差
CSQ 1       = -111 dBm
CSQ 2..30   = -109..-53 dBm（每 +1 约 +2 dBm）
CSQ 31      = -51 dBm 或更好
CSQ 99      = 未知
```

**经验阈值**：

```text
良好：    RSRP > -90 dBm  /  RSRQ > -10 dB  /  SINR > 10 dB
可用：    RSRP -90~-105  /  RSRQ -10~-15  /  SINR 0~10
边缘：    RSRP -105~-115  /  RSRQ -15~-20  /  SINR -5~0
不可用：  RSRP < -115    /  RSRQ < -20    /  SINR < -5
```

### 蜂窝模组抓包命令

```c
// 移远：开 log
AT+QLOG=1,3            // 1=开启，3=保存到 U 盘或 AP 侧
AT+QLOGCFG="usb",1     // log 输出到 USB

// 移远：信令 trace
AT+QENG="servingcell"  // 看服务小区
AT+QENG="neighbourcell" // 看邻区

// 高通平台：QXDM 抓 DM log
// nvlog 工具

// 芯讯通：
AT+CSIM=10
AT+CENG=1
```

## 调试步骤

1. **量电源**：上电瞬间电流 ~50 mA，注册时 200~500 mA，传输时 1~2 A 峰值
2. **看串口 log**：开机 log 是否正常（firmware 版本、IMEI、SIM 状态）
3. **看 SIM 状态**：`AT+CPIN?` 返回 `READY` 才正常
4. **看搜网**：`AT+COPS?` 返回运营商名，`AT+CEREG?` stat=1 或 5
5. **看信号**：`AT+CSQ` ≥ 10 才有数据可能
6. **配 APN**：`AT+QICSGP` 配对运营商
7. **激活 PDP**：`AT+QIACT` 成功返回 IP
8. **跑 TCP**：`AT+QIOPEN` → `AT+QISEND` → 收到 `SEND OK` + 服务器回包
9. **测 PSM / eDRX**：发 AT 命令配 T3412 / T3324 / PTW，看功耗下降
10. **看错误码**：`+CME ERROR: <num>` / `+CMS ERROR: <num>` / `+QCFG: error`

## 常见问题速查

| 现象 | 优先检查 |
| --- | --- |
| 模组不上电 | 电源纹波 / PWRKEY 时序 / 焊接 |
| AT 无响应 | UART 电平 / 波特率 / 串口反接 |
| SIM 不识别 | 卡座接触 / SIM 卡方向 / `AT+CPIN?` 返回值 |
| 搜不到网 | 天线 / 频段 / 运营商限制（NB-IoT 卡不能上 4G） |
| 附着失败 | APN 错 / PLMN 锁 / NAS reject cause |
| DNS 失败 | APN 没带 DNS（要查 APN 规则）/ 平台域名错 |
| TCP 超时 | RSRP 弱 / NAT 老化 / 防火墙 |
| 功耗高 | PSM / eDRX 没启用 / 连接态过长 |
| 频繁掉线 | 信号弱 / 模组过温 / 电源塌陷 |
| 数据上传丢 | 空口拥塞 / 服务器限流 / 串口 buffer 溢出 |

## 5 秒钟定位

| 现象 | 一句话定位 | 首选动作 |
| --- | --- | --- |
| 模组无反应 | 电源 / PWRKEY | 示波器量 VDD 波形 |
| AT 无响应 | UART 错 | 换线、调电平、查波特率 |
| SIM 不识别 | 卡 / 卡座 | `AT+CPIN?` 必返回 READY |
| 完全搜不到网 | 天线 / 频段 | `AT+CSQ` 是否 99 / `AT+COPS=?` |
| 搜网慢（>2min） | NB-IoT 频段窄 | 配 B3/B5/B8，禁用 TDD 频段 |
| 附着失败 | APN / SIM | 看 `+CEREG` reject_cause |
| DNS 失败 | APN 没带 DNS | 改用 IP 通信或换公网 APN |
| TCP 慢 / 失败 | 信号弱 | 调天线位置 / 加外置天线 |
| 掉线频繁 | 电源 / 信号 | 看 VBAT 波形、查 RSRP |
| 功耗大 | PSM 没开 | `AT+CPSMS=1` + 配 T3412/T3324 |
| eDRX 没生效 | 运营商未开通 | 联系运营商开通 eDRX 业务 |
| 模组过温 | 散热不足 | 加散热片、降环境温度 |

## 错误码速查

### +CME ERROR (Mobile Equipment Error, 3GPP TS 27.007 §9.2)

| 码 | 名称 | 触发 / 解决 |
| --- | --- | --- |
| 0 | Phone failure | 模组异常，复位 |
| 3 | Operation not allowed | 当前状态不允许 |
| 4 | Operation not supported | AT 命令不支持 |
| 10 | SIM not inserted | SIM 物理问题 |
| 11 | SIM PIN required | SIM 卡锁了 |
| 13 | SIM busy | SIM I/O 忙，等 |
| 14 | SIM wrong | SIM 烧了或失效 |
| 15 | SIM PUK required | SIM 锁死要 PUK |
| 16 | SIM PIN2 required | SIM 卡 PIN2 锁 |
| 30 | No network service | 搜不到网 |
| 31 | Network timeout | 搜网超时 |
| 32 | Network not allowed - emergency only | 仅紧急呼叫，PLMN 受限 |
| 33 | Network not allowed - roaming | 漫游不允许 |
| 50 | Incorrect parameters | AT 参数错 |
| 100 | Unknown | 看 log 详细 |
| 514 | Not registered, ME busy | 并发 AT 阻塞，加锁 |
| 515 | Not allowed, ME busy | 同一时间多个流程 |

### +CMS ERROR (Message Service Error, 3GPP TS 27.005)

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 30 | No network service | 搜不到网 |
| 38 | Network out of order | 网络掉线 |
| 41 | Temporary failure | 临时失败，重试 |
| 42 | Congestion | 网络拥塞 |
| 500 | Unknown | 内部错误 |
| 512 | User abort | 用户中止 |
| 513 | Not allowed, ME busy | 忙 |
| 514 | ME busy | 忙 |

### TCP / IP 错误（移远 +QISTATE / +QIERROR）

| 错误 | 含义 | 行动 |
| --- | --- | --- |
| 563 | Connection time out | 服务器无响应，查 RSRP / IP |
| 564 | DNS parse failed | DNS 失败，改 IP 或配 DNS |
| 565 | Socket closed | 服务器断，查心跳 |
| 566 | Socket error | socket 异常，重连 |
| 567 | Unknown | 看 +QIERROR 详细 |

### NAS EMM 拒绝原因（3GPP TS 24.301 §5.5.3.2）

| 码 | 名称 | 触发 |
| --- | --- | --- |
| 3 | Illegal UE | 设备非法（IMEI 黑名单） |
| 6 | Illegal ME | 设备非法（ESN/MEID 黑名单） |
| 7 | EPS services not allowed | 业务不允许 |
| 8 | EPS services and non-EPS services not allowed | 业务不允许 |
| 14 | EPS services not allowed in this PLMN | 本 PLMN 业务不允许 |
| 15 | No suitable cells in tracking area | TA 不允许 |
| 17 | Network failure | 网络失败 |
| 22 | Congestion | 拥塞 |
| 23 | User plane integrity failure | 用户面完整性失败 |
| 27 | EPS services not allowed in this PLMN | 同 14 |

### 模组扩展错误（移远 / 芯讯通）

```c
// 移远
+QCFG: "error"  → 详细错误
+QIND: "csq",<rssi>,<ber>  → 信号变化
+QIND: "pdpdeact",<cid>  → PDP 去激活
+QIND: "cered",<stat>     → 注册状态变化

// 芯讯通
+CENG: <cell info>  → 工程小区
+CSIM: <result>     → SIM 操作结果
```

## 实战注意

### 移远 EC200N

- **默认 APN** 经常是 `cmnet`，对接专网平台必须先 `AT+QICSGP`
- **开机 log 大量输出**，调试时建议关： `ATE0` 关回显，`AT+QLOG=0` 关 log
- **PWRKEY 拉低 ≥ 100ms**，否则可能半开机（典型死机）
- **VBAT 跌落 < 3.4V** 会触发掉线，特别是 Cat 1 传输 2A 瞬态
- **固件升级**：`AT+QFOTADL="http://..."` 或 USB DFU

### 芯讯通 SIM7080

- **默认 LTE 模式**，NB-IoT 用 `AT+CMNB=2` 切换
- **TCP 通信** 走 `AT+CIPSTART` / `AT+CIPSEND` 走老 API（多模组兼容）
- **GPS 模式**：`AT+CGNSPWR=1` 开启，但要确认模组有 GPS 硬件

### 广和通 L610

- **LCC 封装**，尺寸兼容 EC200N
- **内置协议栈** 跟移远类似，AT 命令相近
- **PSM 配置** 用 `AT+CPSMS=1` + 配 4 个定时器

### Nordic nRF9160

- **应用核 + 蜂窝核** 双核架构，蜂窝核跑 Modem firmware
- **应用侧控制**：用 nrf9160 SDK + LTE link control
- **注意**：nRF9160 不开放传统 AT 命令，要用 `nrf_modem_lib` API
- **PSM / eDRX**：直接调 `lte_lc_psm_req()` / `lte_lc_edrx_req()`

## 检查清单

```text
□ 模组选型：Category / 频段 / 封装 三件套
□ 电源：3.4~4.3V，瞬态 2A，纹波 < 100mVpp
□ SIM：USIM / eSIM / iSIM 匹配运营商
□ APN：公网 / 专网 / NB-IoT 专用 APN
□ 天线：50Ω 匹配，VSWR < 1.5
□ AT 命令：UART 1.8V/3.3V 匹配，波特率 115200
□ 蜂窝注册：CEREG stat=1 或 5
□ 信号：RSRP > -100 dBm 量产 / > -90 dBm 良好
□ PDP 激活：QIACT 拿到 IP
□ TCP / UDP：QIOPEN → QISEND → SEND OK
□ PSM：T3412 / T3324 / 定时器配对
□ eDRX：PTW / eDRX 周期配运营商
□ 错误码：CME / CMS / TCP / NAS EMM 全解析
□ OTA：远程 firmware 升级路径
□ 电源管理：过温保护 / 掉电保护
□ 安全性：IMEI / IMSI 加密存储
```

## 关联文档

- `bus/lte-iot.md` 主题入口
- `bus/lte-iot-deep-dive.md` 协议栈深挖 / 信令流程
- `bus/lte-iot-failure-cases.md` 产线实战案例
- `bus/lte-iot-index.md` 主题地图 + 导航
