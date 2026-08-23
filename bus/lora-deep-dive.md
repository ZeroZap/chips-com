# LoRa Deep Dive

## 目标

深入 LoRa / LoRaWAN 协议栈各层：物理层调制（chirp spread spectrum）、MAC 帧结构、Class A/B/C 状态机、OTAA/ABP 配网、ADR 算法、安全机制、Network Server 架构、GW 网关实现。目标读者：协议栈移植、驱动调试、安全加固、大规模部署的工程师。

## 协议栈分层

```text
┌─────────────────────────────────────────────────────┐
│ Application Layer（用户私有 / LoRaWAN App）           │
├─────────────────────────────────────────────────────┤
│ LoRaWAN MAC（MAC 命令 / Frame Counter / MIC）       │
├─────────────────────────────────────────────────────┤
│ MAC Frame（FOpts / FPort / FRMPayload）             │
├─────────────────────────────────────────────────────┤
│ Regional Parameters（频段 / 信道 / DR 映射）         │
├─────────────────────────────────────────────────────┤
│ LoRa Modem（SX1262 / SX1278 / SX1302）              │
│  → 调制 (Chirp Spread Spectrum) + FEC + CRC        │
├─────────────────────────────────────────────────────┤
│ RF Frontend（PA / LNA / TCXO / Antenna）            │
└─────────────────────────────────────────────────────┘
```

**两层解耦**：

- 物理层（PHY）：chirp 扩频 + FEC + CRC，由 Semtech 芯片硬件实现
- MAC 层（LoRaWAN）：NS + 终端固件协同实现
- 区域参数（Regional Parameters）：由频段 / DR / 信道映射决定，TS001 附录

## 物理层（PHY）

### Chirp Spread Spectrum（啁啾扩频）

```text
基础波形：频率随时间线性变化的正弦波
  f(t) = f0 + (BW / T) × t  (上行)
  f(t) = f1 - (BW / T) × t  (下行)
  T = 2^SF / BW  （一个 chirp 周期）
```

**关键特性**：

- 带宽 BW 决定 chirp 频率变化率
- 扩频因子 SF 决定 chirp 周期和符号持续时间
- 整个 BW 都用上 → 抗窄带干扰强
- 每个符号 = 一个完整 chirp → 解调看 chirp 起点位置

### SF / BW / 符号周期

```text
符号周期 Ts = 2^SF / BW
  SF7 / BW125kHz  → Ts = 1.024 ms
  SF8 / BW125kHz  → Ts = 2.048 ms
  SF12 / BW125kHz → Ts = 32.768 ms  （慢 32 倍）
```

**接收灵敏度**：

```text
SF7  → -123 dBm
SF8  → -126 dBm
SF9  → -129 dBm
SF10 → -132 dBm
SF11 → -134.5 dBm
SF12 → -137 dBm
每 +1 SF 提升 2.5~3 dB
```

**比特率**：

```text
Rb = SF × (BW / 2^SF) × CR
  SF7/BW125/CR4/5 → 5470 bps
  SF12/BW125/CR4/8 → 250 bps
```

### 前向纠错（FEC）

```text
LoRa 用 Hamming 码 + 交织（interleaver）
  CR 4/5 → 1 bit 冗余
  CR 4/6 → 2 bit 冗余
  CR 4/7 → 3 bit 冗余
  CR 4/8 → 4 bit 冗余

交织深度：
  SF7/8   → 4
  SF9/10  → 4 (low rate) / 4 (default)
  SF11    → 4 (low rate) / 4 (default)
  SF12    → 8 (low rate) / 4 (default)
```

**实战**：干扰强场景下，CR 4/8 + SF12 可把 BER 降低几个数量级，但代价是 2 倍空中时间。

### 数据 whitening（白化）

```text
目的：避免长串 0/1（影响时钟恢复）
算法：PRNG（CCITT 初始值 0xFF），对 payload 异或
所有 LoRaWAN payload 必走 whitening（除 FHDR 头部外）
```

### IQ 翻转（IQ Inversion）

```text
下行链路用 IQ 翻转区分上行
上行：chirp 从 BW 低端到高端
下行：chirp 从 BW 高端到低端
终端可识别方向，自动同步
```

### LoRa CSS 工业抗干扰（金属密集 / 频率选择性衰落）

LoRa 啁啾扩频（CSS）在金属密集、强电磁工业环境相对 Wi-Fi/ZigBee 有结构性优势：

```text
链路预算（CSS 物理层极限）：
  SF7 / BW125：灵敏度 -123 dBm
  SF10 / BW125：灵敏度 -132 dBm
  SF12 / BW125：灵敏度 -137 dBm
  SF12 / BW500：灵敏度 -120 dBm（宽带换灵敏度）
  最大预算：+14 dBm TX - (-137 dBm) = 151 dB（实测可达 156-170 dB）

抗多径（chirp 结构天然免疫）：
  ① 单 chirp 跨整个 BW（125kHz ~ 500kHz）
  ② 接收端匹配滤波器（match filter）做相关解调
  ③ 短时脉冲干扰只破坏 chirp 一小段，匹配滤波能容忍
  ④ 频率选择性衰落：chirp 占满信道，不存在"被某个频点衰落打到"的问题

实测对比（钢厂/电机车间）：
  Wi-Fi：2.4GHz 全频被工厂电机谐波干扰 → 通信距离 < 5m
  ZigBee：2.4GHz 同 Wi-Fi → 距离 < 3m
  LoRa：Sub-GHz 470MHz 工厂谐波覆盖不到 → 距离 4-6 km
  LoRa + 8dBi 定向天线：距离 8-10 km

关键参数：
  SF12 = 4096 码片冗余 → 单符号传输 12 bit
  啁啾信号对频偏容忍 ±25 ppm（普通晶振即稳）
  普通 16 MHz 晶振 ±20 ppm 已可稳定运行
  不需要 TCXO（温补晶振）→ 成本降低
```

**为什么不在"抗扰"段写：工业环境抗扰是 LoRa 物理层最被低估的特性**——很多选型文章只讲距离不讲抗扰，工程师实际部署钢厂/电机车间才发现 Wi-Fi/ZigBee 不工作，临时换 LoRa。

## 帧结构

### PHY 帧（LoRa Modem 层）

```text
┌──────────┬─────────┬─────────────┬─────────┬──────┐
│ Preamble │  Sync   │  SFD/Header │ Payload │ CRC  │
│ 8+ symb  │ 2 symb  │ 0.25~1 symb │ 1~256 B │ 2 B  │
└──────────┴─────────┴─────────────┴─────────┴──────┘
```

- Preamble：8 个 upchirks + 4.25 符号（默认）
- SFD（Start Frame Delimiter）：标记 preamble 结束
- Header（implicit/explicit）：显示头带 payload length，隐式头长度固定
- CRC：2 字节（CRC-16/CCITT）

**显式头 vs 隐式头**：

```text
显式头（默认）：含 payload length + CR + has-crc
  → 灵活，适合变长 payload
隐式头：固定长度（4~255 字节）
  → 空中时间短 ~5%
  → 适合固定场景
```

### LoRaWAN MAC 帧

```text
┌────────┬──────┬─────────┬────────┬────────┬─────────┬────────┬────────┬────────┬──────┬──────┐
│ Preamb │ PHDR │ PHDR_CRC│  MHDR  │  FHDR  │ FPort   │FRMPayload│Payload│ MIC   │ CRC  │
│   8+   │ 1 B  │  2 B    │  1 B   │  7~22 B│  1 B    │ 0~N B   │ 0~N B  │  4 B  │ 2 B  │
└────────┴──────┴─────────┴────────┴────────┴─────────┴────────┴────────┴────────┴──────┴──────┘
```

**MHDR（MAC Header）**：

```text
b7~b5  → MType（消息类型）
b4~b2  → RFU（保留）
b1~b0  → Major（LoRaWAN R1 = 00）

MType 编码：
  000  → Join Request
  001  → Join Accept
  010  → Unconfirmed Data Up
  011  → Unconfirmed Data Down
  100  → Confirmed Data Up
  101  → Confirmed Data Down
  110  → Rejoin Request
  111  → Proprietary
```

**FHDR（Frame Header）**：

```text
┌────────┬──────┬─────────────┬─────────┐
│ DevAddr│FCtrl │  FCnt (2B)  │ FOpts   │
│  4 B   │ 1 B  │             │ 0~15 B  │
└────────┴──────┴─────────────┴─────────┘

FCtrl：
  b7    → ADR
  b6    → ADRACKReq
  b5    → ACK
  b4    → FPending（Class B/C 下行）
  b3~b0 → FOptsLen（0~15 字节）
```

**FRMPayload**：

```text
FPort 0x00     → FRMPayload 仅含 MAC 命令（无应用数据）
FPort 1~223    → 用户应用层 payload
FPort 224~255  → 保留（LoRaWAN 规范）
```

**MIC（Message Integrity Code）**：

```text
4 字节 CMAC/AES-128
计算范围：MHDR + FHDR + FPort + FRMPayload
上行用 NwkSKey 计算 MIC（仅 MAC 完整性）
下行用 NwkSKey 计算 MIC
payload 加密用 AppSKey（AES-128 CTR 模式）
```

### Frame Counter（FCnt）实战

LoRaWAN 帧计数是防重放的核心机制，但 3 个隐藏 bug 在 ABP 设备上高发：

```text
正常机制（防重放）：
  每个上行包 FCntUp 自增 1
  NS 端记录（DevAddr, FCntUp）二元组
  收到新包时校验：new_fcnt - last_fcnt < MAX_FCNT_GAP（默认 16384）
  超出门限 → 视为重放 → 拒收
  防重放：攻击者无法用旧包重发

Bug 1：ABP 设备重启归零
  设备 ABP 入网后 NS 记录 last_fcnt = 1000
  设备断电 → 重启 → FCntUp 仍按 ABP 初始值（0）发
  NS 收到 fcnt=1，差值 999 < 16384 通过
  → 重启后所有包都被 NS 当"未来包"处理
  → 设备仍能正常上行，**但安全机制已破**
  修复：ABP 设备必须把 last_fcnt 存到 NV（EEPROM/Flash），重启恢复

Bug 2：Disable 帧计数校验不灵
  某些 NS（ChirpStack 老版本）配置 `SkipFCntValidation=true`
  → 设备 FCnt 乱发也接收
  → 防重放机制完全失效
  修复：生产环境必须 SkipFCntValidation=false，仅开发调试用

Bug 3：FCnt 跨 65535 的 MIC 校验绕过
  FCnt 字段是 16-bit，溢出后归 0
  但 16-bit FCnt + 32-bit DevAddr 拼接的 MIC 计算
  在跨 65535 时包序号跳跃 65535 → 0
  攻击者可构造：fcnt=65535 和 fcnt=0 两个包同时发出
  接收端 MIC 校验通过（值算对）但实际是"重放 + 伪造"
  修复：
    LoRaWAN 1.1+ 改 32-bit FCnt
    LoRaWAN 1.0.x 升级到 LoRaWAN 1.1 或加应用层序号
```

**实战故障案例**（ChirpStack + ABP 设备 105007 不上报）：

```text
症状：某 ABP 设备（dev_addr=105007）有数据但 NS 不收
定位：NS 端配置 last_fcnt=60000 → 设备实测 fcnt=1000
      差值 60000-1000 = 59000 < 16384？→ 实际是 1000-60000 模 65536
      差值落在 [40000, 65535] → 被判为重放 → 拒收
修复：ChirpStack 手动配 SessionFCntUp=设备实测 fcnt
      或 设备端把 last_fcnt 写 NV（不依赖 NS）
```

## Class A / B / C 状态机

### Class A（必实现）

```text
时间线：
  T0          T1       T2        T3
  │           │        │         │
  └─ 终端 TX ─┴ RX1 开窗 ┴ RX2 开窗 ┘
              （默认 1s 后） （默认 2s 后）

RX1 / RX2：
  RX1 频率 = 上行频率（同行）
  RX1 SF = 上行 SF（同行）
  RX2 频率 = 频段固定下行频率（RX2 通道）
  RX2 SF = 频段固定（默认 DR0 = SF12/BW125）
  RX1/RX2 之间间隔 = 1s（默认，可配置）
```

**Class A 限制**：

- 终端只能在上行后两个短窗口收下行
- NS 想下行必须等终端先上行
- 适合电池供电（RX2 窗口外完全睡眠）

### Class B（同步下行）

```text
额外机制：
  1. 网关定期发 Beacon（每 128s）
  2. 终端监听 Beacon 同步时钟
  3. NS 按调度在指定 ping slot 开 RX 窗口
  4. 终端在 ping slot 醒来接收

Beacon 频率：CN470 = 485.3 MHz（固定）
ping slot 数：2^12 / 2^PingNb（PingNb 0~7）
ping period：30s / 1min / 2min / 4min / 8min / 16min / 32min / 64min
```

**Class B 实战**：

- 网关必须有 GPS 同步（否则 beacon 不准）
- 终端需要更复杂的同步机制（信标漂移补偿）
- 功耗比 Class A 高（按 ping period 醒）

### Class C（持续下行）

```text
时间线：
  终端不发包时 → 一直打开 RX2
  终端发包时   → TX 完成后立即回 RX2

限制：
  - 功耗最高（RX 持续耗电 ~10 mA）
  - 仅适合有外供电场景
  - 必须支持立即下行（远程控制 / 紧急停机）
```

## OTAA 配网流程

```text
终端                          NS
  │                            │
  │ ① Join Request            │
  │ (DevEUI + AppEUI +         │
  │  DevNonce)                 │
  ├───────────────────────────→│
  │                            │ ② 校验 DevNonce
  │                            │ ③ 生成 NwkSKey
  │                            │    = AES(AppKey, 0x01 | AppNonce | NetID | DevNonce | pad)
  │                            │ ④ 生成 AppSKey
  │                            │    = AES(AppKey, 0x02 | AppNonce | NetID | DevNonce | pad)
  │                            │ ⑤ 生成 Join Accept
  │ ⑥ Join Accept             │    (AppNonce + NetID + DevAddr + DLSettings + RxDelay + CFList + MIC)
  │ (NwkSKey / AppSKey 派生)   │
  │←───────────────────────────┤
  │ ⑦ 启用会话                │
  │ ⑧ 业务帧 (上行)           │
  ├───────────────────────────→│
```

**关键参数**：

```text
DevEUI   → 64-bit 终端唯一 ID（IEEE OUI 段或自建）
AppEUI   → 64-bit 应用 ID（类似子网 ID）
DevNonce → 16-bit 随机数（每次 Join 必新）
AppKey   → 128-bit 应用根密钥（终端与 NS 各持一份）
AppNonce → 24-bit NS 生成，每次 Join +1
NetID    → 24-bit 网络 ID（多 NS 共享时区分）
DevAddr  → 32-bit 终端网络地址（Join 后分配）
```

**DevNonce 重放**：

- NS 收到 DevNonce 后存 24h 缓存
- 重启后用同一 DevNonce → NS 拒
- 终端必须保证每次 Join 的 DevNonce 唯一（用 RTC + 启动计数）

## ABP 配网流程

```text
生产测试时：直接烧 NwkSKey + AppSKey + DevAddr
终端开机：直接用烧录密钥发业务帧（不 Join）
NS 端：直接创建设备 profile，绑定密钥

风险：
  1. Frame Counter 重启后从 0 → NS 端认为重放 → 拒
  2. 密钥泄露永久（无 Join Accept 加密）
  3. 烧录参数不匹配 → 永久故障
```

**实战**：

- ABP 仅生产测试用（自动化 Join 测试 + 跳过密钥协商）
- 量产固件必用 OTAA
- ABP 模式下 Frame Counter 需每次烧录 +1（避免重放）

## ADR（Adaptive Data Rate）

```text
NS 端算法：
  1. 收集最近 20 帧的 RSSI + SNR
  2. 计算链路余量 = (当前 SF 解调所需 SNR) - 实际 SNR
  3. 余量 > 0 → 可降 SF 提速
  4. 余量 < 0 → 升 SF 降速
  5. NS 发 LinkADRReq 终端切 DR / TX Power

终端：
  1. 收到 LinkADRReq 切到指定 DR
  2. 之后 N 帧发包统计成功
  3. 如果 N 帧内丢包 > X% → 发 LinkADRAnsReq 拒绝
  4. NS 重新评估
```

**实战**：

```text
默认 DR（入网时）：
  CN470：DR5 = SF7/BW125
  EU868：DR0 = SF12/BW125（默认最远档）
  US915：DR0 = SF10/BW125

ADR 收敛：
  DR0（SF12）起步 → 几十分钟收敛到 DR3~DR5
  慢的原因：NS 保守策略 + 20 帧窗口
```

## 安全

### 密钥体系

```text
AppKey    → 128-bit 根密钥
  ├─ 派生 NwkSKey = AES(AppKey, 0x01 | ...)
  └─ 派生 AppSKey = AES(AppKey, 0x02 | ...)

NwkSKey   → 网络层密钥
  ├─ 计算 MIC（上行 + 下行）
  └─ 加密 MAC 命令

AppSKey   → 应用层密钥
  └─ 加密 FRMPayload

每次 Join / Reset：
  1. NS 端 AppNonce +1
  2. 重新派生 NwkSKey + AppSKey
  3. Frame Counter 重置为 0
  4. NS 端保存旧 session（用于下行）
```

### MIC 校验失败原因

```text
1. AppKey 错配（90% 概率）
   → 终端烧录 AppKey 与 NS 不一致
2. NwkSKey 派生错
   → 厂商 SDK 实现 bug
3. payload whitening 错
   → 字节序或 PRNG 错
4. Frame Counter 不连续
   → 终端丢帧 / NS 缓存清理
5. 硬件问题（罕见）
   → Flash 翻转 / 内存损坏
```

### 防重放

```text
上行：
  FCnt (16-bit) 每次 +1
  NS 端保存 (DevAddr, FCnt) 映射
  收到 < 已存 FCnt → 拒

下行：
  NS 端发下行带 FCntDown
  终端校验 FCntDown > 之前

风险：
  16-bit FCnt 最多 65535
  高频终端（如 1 min/帧）跑 45 天溢出
  LoRaWAN 1.1 引入 32-bit FCnt
```

## Network Server 架构

### ChirpStack 组件

```text
┌─────────────┐
│ GW Bridge   │ ← 接收 GW 上行 UDP 包（Semtech UDP 协议）
│ (gRPC)      │
└──────┬──────┘
       ↓
┌─────────────┐
│ ChirpStack  │ ← LoRaWAN MAC + 应用层解码
│ Server      │   Frame Counter / MIC 校验
│             │   ADR 计算 / MAC 命令
└──────┬──────┘
       ↓
┌─────────────┐
│ Application │ ← 应用层 payload 解码（Codec）
│ Server      │   MQTT 推送到客户后台
└──────┬──────┘
       ↓
┌─────────────┐
│ Storage     │ ← PostgreSQL（设备 / 多租户 / 统计）
│ (Postgres)  │   Redis（Frame Counter / 实时）
└─────────────┘
```

### TTN v3 架构

```text
NS（networkserver）→ 处理 LoRaWAN MAC
AS（applicationserver）→ 应用层解码 + Webhook
IS（identityserver）→ 用户 / 租户 / 设备
JS（join server）→ OTAA 密钥管理
DCS（device claim server）→ 设备所有权转移
```

### GW ↔ NS 协议（Semtech UDP）

```text
GW 上行 → NS（UDP port 1700）：
  PUSH_DATA (token + JSON: rxpk[])
  rxpk：时间戳 + 频率 + SF + BW + RSSI + SNR + payload (base64)

NS 下行 → GW（UDP port 1700）：
  PULL_RESP (txpk：时间戳 + 频率 + SF + BW + power + payload)
  GW 在指定时间发包
```

### LoRa 天线设计实战（50Ω 匹配 / 增益 / 视距）

LoRa 距离 5km → 500m，**90% 是天线问题**。从阻抗匹配到增益选型到安装规范，3 步决定产线效果：

```text
Step 1：50Ω 阻抗匹配（底线）
  ① VNA 量 RF 输出端口 S11
  ② 目标 S11 < -10 dB（驻波比 < 2）
  ③ 匹配网络：π 型 LC（常用结构）
     - C1（源端）：2.2pF ~ 10pF
     - L1（中间）：3.3nH ~ 33nH
     - C2（负载端）：2.2pF ~ 10pF
  ④ 频段误配是常见雷区：
     - 470MHz 模组用了 433MHz 天线 → S11 失谐
     - 模组是 Sub-GHz 但天线是 2.4GHz → 距离缩到 1/10
  ⑤ 微带线 ≤ 20mm 时，阻抗 25-75Ω 都可接受
     长走线必须 50Ω 控阻抗（4 层板 + 完整地平面）

Step 2：增益选型（核心）
  100mW 模组（+20dBm）：
    配 2dBi 全向棒状天线 → 视距 3-5km
    配 5dBi 定向天线 → 视距 6-8km
  500mW 模组（+27dBm）：
    配 5dBi 定向天线 → 视距 10-12km
    配 8dBi 定向八木 → 视距 15km+
  2W 模组（+33dBm）：
    仅供室外固定点 → 配 10dBi 板状天线 → 视距 20km+
  
  增益 vs 覆盖角：增益 +3dB 覆盖角收窄一半
  移动节点（车 / 资产）必须全向天线
  固定节点（水表 / 电表）首选定向

Step 3：安装规范
  ① 天线垂直朝天（不要贴地 / 贴墙）
  ② 30cm 范围内禁金属（金属会反射/吸收）
  ③ 视距：天线 + 10m 视距 → 5.5km（典型实测）
  ④ 多径环境：避开大型金属反射体
  ⑤ 防水：接头必须 IP67 防水胶带 + 自固化胶
```

**实战坑**：

```text
坑 1：模组焊上天线，PCB 调好匹配，但装机后距离缩一半
      → 金属外壳屏蔽：天线必须伸出壳外 5cm+
      
坑 2：模组用 433MHz 但卖给中国客户
      → 频段违法（中国 470-510MHz）
      → 法规风险 + 实际可能干扰其它设备

坑 3：天线选型只看增益不看方向图
      → 8dBi 八木用在移动节点 → 信号灯一直闪
      → 移动节点必须全向天线

坑 4：室内装天线，距离 50m 但 RSSI -110
      → 频段误配（用 868 天线在 470 频段）
      → 接头虚焊（接触电阻大）
      → 天线方向图错（垂直极化 vs 水平极化）
```

## 物理层芯片实现

### SX1262 关键 API

```c
// Semtech LoRaMac-node 标准 API
Radio.SetTxConfig(MODEM_LORA, TX_OUTPUT_POWER, 0, LORA_BANDWIDTH,
                  LORA_SPREADING_FACTOR, LORA_CODINGRATE,
                  LORA_PREAMBLE_LENGTH, LORA_FIX_LENGTH_PAYLOAD_ON,
                  true, 0, 0, LORA_IQ_INVERSION_ON, 3000);

Radio.SetRxConfig(MODEM_LORA, LORA_BANDWIDTH, LORA_SPREADING_FACTOR,
                  LORA_CODINGRATE, 0, LORA_PREAMBLE_LENGTH,
                  LORA_SYMBOL_TIMEOUT, LORA_FIX_LENGTH_PAYLOAD_ON,
                  0, true, 0, 0, LORA_IQ_INVERSION_ON, true);

Radio.Send(buffer, size);
Radio.Rx(0);  // 0 = 持续 RX
Radio.Rx(max_rx_time);  // 限时 RX
```

### SX1302 关键特性

```text
8 信道并发：
  - 8 个独立 LoRa 解调器
  - 1 个 FSK 解调器
  - 每信道独立 SF / BW 配置
  - 信道 0~7 固定 125 kHz
  - 信道 8（可选）支持 250/500 kHz

并发能力：
  - 8 个 LoRa 包可同时解调
  - 单信道 1 包/秒，8 信道理论 8 包/秒
  - 实际 ADR + 重传 → 2~4 包/秒

GPS 同步：
  - PPS 输入 → beacon 精度 ±100 µs
  - 失钟 1 小时 → Class B 完全不可用
```

## LoRaMac-node 协议栈移植实战

Semtech 官方 [LoRaMac-node](https://github.com/Lora-net/LoRaMac-node) 是 LoRaWAN 协议栈的事实标准实现，移植到 STM32 + SX1276/SX1262 是产线最常见需求。Semtech 协议栈是分层结构：

```text
┌─────────────────────────────────────┐
│  Application  (你的业务代码)            │
├─────────────────────────────────────┤
│  LoRaMac       (MAC 层 + Key 管理)     │
├─────────────────────────────────────┤
│  Region        (CN470/EU868/US915)    │
├─────────────────────────────────────┤
│  Boards        (板级 BSP / SPI / GPIO) │
├─────────────────────────────────────┤
│  Mac/Phy       (Radio HAL + Crypto)    │
├─────────────────────────────────────┤
│  Utils         (定时器 / 队列)          │
└─────────────────────────────────────┘
```

### 移植关键点（CN470 案例）

```text
1. Region 选型（必做，且必须做对）：
     默认 #define REGION_CN470 启用
     LoRaMacRegionNvmUpdate(CN470) 在 OTAA 成功后调用
     错把 EU868 固件烧到 CN470 板 → 频段违法，无数据
     错把 US915 固件烧到 EU868 板 → 占用错频段，半年后被查
     参见 failure-cases 案例 6 / 案例 9

2. Radio HAL 移植（SX1276 ↔ SX1262）：
     两者 SPI 命令集差异极大：
       SX1276: Radio.SetTxConfig() 直接传 SF/BW/CR
       SX1262: Radio.SetTxConfig() 走 SetPaConfig() + SetTxParams()
     切换模组时必须改 boards/<your-board>/radio_board_iface.h
     不能只改 .c 不改 .h → RadioEvents 回调全部失效

3. NV 持久化（最常踩坑）：
     LoRaMac 需要存 DevNonce / FrameCounter / Session keys
     移植到 STM32 + 内部 Flash：写之前必须 fds init
     移植到外部 EEPROM / SE 芯片：用 AT24Cxx / ATECC608B
     写失败处理：写完 verify read，不一致则 +1 重试 N 次
     否则：节点重启后 DevNonce 重复 → Join Fail

4. 加密硬件加速：
     默认软件 AES-128 慢（~50ms / 包）
     STM32L4 启用 CRYP 外设 → 降到 ~1ms / 包
     SX1262 内部有硬件 AES，但只用于 payload；MAC 层 MIC 仍用软件
```

### 移动设备关 ADR 锁 DR_5

```text
移动节点（车载 / 资产追踪）禁用 ADR：
  1. 移动场景下 SF 频繁变化，ADR 算法跟不上
  2. 默认 ADR 起步 SF12，节点一直用低速率，耗电
  3. 锁死 DataRate = DR_5（CN470 = SF7/125kHz）
  4. 路径：LoRaMacSetTxDataRate() 在每次发送前调用
  5. 副作用：移动节点对网络变化自适应差，距离近时浪费带宽
```

## 性能数据参考

```text
覆盖（视距）：
  SF7 / BW125  → ~2 km
  SF9 / BW125  → ~5 km
  SF12 / BW125 → ~15 km

覆盖（城区）：
  SF12 / BW125 → 2~5 km

电池寿命（AA 锂亚硫酰氯 2400 mAh）：
  Class A + DR0 + 1 帧/小时 → 10 年
  Class A + DR3 + 1 帧/小时 → 5 年
  Class B + 30s ping period → 1~2 年
  Class C + 持续 RX → 数天

空中时间（11B payload）：
  DR0 (SF12) → 1.5 s
  DR5 (SF7)  → 56 ms

网关容量：
  SX1302（8 信道 + ADR）：
    100 终端 × 1 帧/min ≈ 1.6 帧/秒 → 良好
    1000 终端 × 1 帧/min ≈ 16 帧/秒 → 打满
```

## 实战经验

- **Join 慢 99% 是 SF 起步太高**：默认 DR0 = SF12，入门起步要花 30~60s
- **MIC Failure 90% 是 AppKey 错配**：终端烧录与 NS 必须 byte-by-byte 一致
- **EU868 Duty Cycle 触发限流**：1% 真的就是 1%，节点 1 帧/30s 都不行
- **ADR 不收敛**：终端移动场景下永远 SF12，省电逻辑反成耗电
- **GW 容量打满的征兆**：Join Request 排队 5~10s，latency 抖动大
- **频段错配是新人最常见坑**：CN470 固件烧到 US915 板，半年都没数据
- **Class B 不可靠**：实际部署 GPS 失锁频发，谨慎用 Class B
- **ChirpStack 集群**：>10k 终端必须用 Redis Cluster + 多个 NS 实例

## 关联文档

- `bus/lora.md` 主题入口
- `bus/lora-practical.md` 调试流程速查
- `bus/lora-failure-cases.md` 产线实战案例
- `bus/lora-index.md` 主题地图 + 导航
