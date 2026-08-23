# LTE-IoT 产线实战案例库

## 目标

把产线常见的 LTE-IoT 通信失败、附着错、PDP 激活失败、DNS 解析失败、PSM/eDRX 配置错、SIM 卡不识别、瞬态电流塌陷等问题写成案例库。每个案例：

- 现象（现场）
- 抓包 / 抓 log（判断）
- 定位（根因）
- 修复（代码 / 硬件 / 配置）
- 复盘（如何预防）

案例来源：_Inbox/ 候选素材 + 实战复盘。

---

## 案例 1：NB-IoT 模组完全搜不到网（频段错配）

### 现象

某智能水表项目使用移远 BC26 模组（NB-IoT），中国移动 SIM 卡。产线 1000 台设备，800 台完全搜不到网。设备指示灯常亮（注册中），3 分钟后 5min、10min 仍未注册。

### 抓 log

```text
AT+CFUN?
+CFUN: 1

AT+CEREG?
+CEREG: 0,2  // 搜网中

AT+COPS=?
+COPS: (1,"CHINA MOBILE","CMCC","46000",7),(2,"CHINA MOBILE","CMCC","46000",9),...

AT+CSQ
+CSQ: 99,99  // 99 = 未知（搜不到信号）
```

CEREG 一直 stat=2 搜网中，CSQ 99 无信号。3 分钟后仍无进展。

### 定位

**BC26 默认频段**：

```c
// BC26 出厂默认仅 B1/B3/B5/B8 之一
AT+QBAND?
+QBAND: 1,3,5,8
```

实际上 NB-IoT 移动部署仅在 **B8（900 MHz）**，部分区域 B3 / B5。但 BC26 部分批次 firmware 仅支持 B3 / B5，**缺 B8**。

**根因**：

```text
产线 800 台都搜不到 → 不是单台问题
移动 NB-IoT 仅 B8（部分区域 B3/B5）
BC26 部分批次 firmware 不含 B8
```

**额外验证**：

```c
// 手动加 B8
AT+QBAND=8
// 重启后
AT+CFUN=0
AT+CFUN=1

// 3 秒后
AT+CSQ
+CSQ: 14,99  // 信号正常
AT+CEREG?
+CEREG: 0,1  // 已注册
```

### 修复

```c
// 方案 1：固件 AT 命令（产线统一烧入）
AT+QBAND=8            // 仅 B8
// 或
AT+QBAND=3,5,8        // B3/B5/B8 多频段
AT&W                   // 保存
AT+CFUN=0
AT+CFUN=1

// 方案 2：固件升级 BC26 全部支持 B8
// 移远 BC26 R02 以后版本支持全频段

// 方案 3：替换 BC28 / BC260Y
// BC28 / BC260Y 是 BC26 的替代品，全频段

// 方案 4：AT 命令在产线测试中验证搜网成功
// 产线自动测试脚本：
send_at("AT+CEREG?", 5);
parse_creg_response();  // 必须 stat=1 或 5 才算通过
```

### 复盘

- **NB-IoT 模组选频段必须看运营商部署白皮书**，不能凭 datasheet 默认配置
- **产线测试脚本必须验证搜网成功**，不能只看"上电 OK"
- **频段配置有版本差异**，锁批次采购，避免混入老 firmware 模组
- **CSQ=99 必须报警**，99 表示"无信号"，不是"弱信号"

---

## 案例 2：PDP 激活失败（APN 错配）

### 现象

某共享设备项目使用移远 EC200N（Cat 1），电信物联网卡。SIM 卡可识别、能搜网（`AT+CEREG?` 返回 stat=1），但激活 PDP 失败。

### 抓 log

```text
AT+CPIN?
+CPIN: READY                              // SIM OK

AT+CEREG?
+CEREG: 0,1                               // 已注册

AT+CSQ
+CSQ: 18,99                               // 信号良好

AT+QICSGP=1,1,"cmnet","","",0
OK

AT+QIACT=1
ERROR
+CME ERROR: 553

AT+QIACT?
+QIACT: 1,0                              // 1=cid, 0=未激活
```

### 定位

**+CME ERROR 553** 是 3GPP TS 27.007 未定义错误码，移远扩展。实际查询移远 AT 手册：

```text
+CME ERROR 553:
  Cause: Specified APN is invalid or empty
  Action: 检查 APN 设置
```

**根因**：

```text
电信 Cat 1 物联网卡：
  公网 APN = ctnet（不是 cmnet！）
  专网 APN = 自定义（平台分配）

EC200N 默认配置了 cmnet（中国移动）
但卡是电信 → APN 不匹配 → 拒绝激活
```

**额外验证**：

```c
// 改用 ctnet
AT+QICSGP=1,1,"ctnet","","",0
OK
AT+QIACT=1
OK                                   // 激活成功

AT+QIACT?
+QIACT: 1,1                          // 1=cid, 1=已激活
```

### 修复

```c
// 方案 1：按运营商设置 APN
// 中国移动：cmnet / cmwap
// 中国电信：ctnet
// 中国联通：uninet / 3gnet

AT+QICSGP=1,1,"ctnet","","",0
AT+QIACT=1

// 方案 2：多 APN 试错（产线自动测试）
const char *apns[] = {"cmnet", "ctnet", "uninet", "3gnet"};
for (int i = 0; i < 4; i++) {
    send_at("AT+QICSGP=1,1,\"%s\",\"\",\"\",0", apns[i]);
    if (qi_act_success()) return OK;
}

// 方案 3：从 USIM 读 APN
AT+CGDCONT?       // 查 USIM 中保存的 APN
// 但很多物联网卡不写 USIM APN，需手动配

// 方案 4：联系运营商确认 APN
```

### 复盘

- **APN 配错是 PDP 失败最常见原因**（80%）
- **产线测试必须按运营商**配 APN，不要用默认 APN 测
- **CME ERROR 553 一定是 APN 错**
- **建议：USIM 中预置 APN**，避免现场配置
- **建议：模组启动时读 USIM 中 MCC/MNC**，自动选 APN

---

## 案例 3：PSM 启用后下行数据收不到

### 现象

某智能锁项目使用 SIM7080（NB-IoT），启用 PSM 后锁端无法收到服务器下行指令。服务器发了 100 条指令，锁端全部丢失。

### 抓 log

```text
// 启用 PSM
AT+CPSMS=1,,,"10101010","00100001"
OK

// 配 APN + 激活 PDP
AT+CSTT="cmnb","",""
OK
AT+CIICR
OK
AT+CIFSR
10.123.45.67                              // 拿到 IP

// 上行数据
AT+CIPSTART="TCP","platform.com",8883
OK
AT+CIPSEND
> hello
SEND OK

// 上行完后，模组进入 PSM
// 30 分钟后
// 服务器下行 → 模组收不到
```

### 定位

**PSM 期间下行不可达**：

```text
PSM 行为：
  - 上行数据发完 → 启动 T3324（active timer）→ 进入 PSM
  - PSM 期间：模组完全关收发，仅 RTC
  - 网络寻呼：UE 不可达，寻呼失败
  - 下行数据：缓存在 MME / 服务器侧，UE TAU 唤醒时才下发
```

**根因**：

```text
产品需求："锁端能远程控制"
实际配置：PSM（不可达）
矛盾：PSM 不适合"需要下行"的场景

应选 eDRX（周期可达）或不用 PSM
```

### 修复

```c
// 方案 1：用 eDRX 代替 PSM（适合"偶尔下行"）
AT+CEDRXS=1,5,"0101"  // 20.48s 周期
// 服务器下行最坏 20.48s 到达

// 方案 2：短 T3412 + 短 T3324（适合"实时下行"）
AT+CPSMS=1,,,"00100001","00000101"
// T3412 = 1 min（频繁 TAU，醒来可达）
// T3324 = 6 sec（active 窗口短，省电）

// 方案 3：禁用 PSM
AT+CPSMS=0

// 方案 4：根据状态切换
typedef enum {
    LOCK_PSM_MODE,    // 闲时 PSM（无下行）
    LOCK_ACTIVE_MODE, // 激活时 RRC_IDLE（可达）
} lock_mode_t;

void lock_on_event(void) {
    // 触发后切换到 ACTIVE
    at_cmd("AT+CPSMS=0");
    // 上报服务器
    at_cmd("AT+CIPSTART=...");
}

void lock_idle(void) {
    // 5 min 无事件，进 PSM
    at_cmd("AT+CPSMS=1,,,\"10101010\",\"00100001\"");
}
```

### 复盘

- **PSM 期间不可达**，跟"远程控制"业务不兼容
- **选错省电模式** 比 不省电 更糟糕（业务不通）
- **产品需求 vs 省电策略** 必须在设计阶段对齐
- **eDRX** 是 PSM 与可达性的折中（周期可达 + 较省电）
- **场景化省电**：闲时 PSM + 激活时 RRC_IDLE 是常见组合

---

## 案例 4：DNS 解析失败（APN 没带 DNS）

### 现象

某环境监测项目使用 EC200N + 中国移动 NB-IoT 卡。设备能拿到 IP、TCP 连接超时。但用 IP 直连能通。

### 抓 log

```text
// 用 IP 通信
AT+QIOPEN=1,0,"TCP","139.196.108.221",8883,0,0
OK
+QIOPEN: 0,0                              // 连接成功

// 用域名通信
AT+QIOPEN=1,0,"TCP","platform.example.com",8883,0,0
OK
+QIOPEN: 0,563                            // 0=cid, 563=Connection time out

AT+QIDNSGIP=1,"platform.example.com"
ERROR
+CME ERROR: 564                           // DNS parse failed
```

### 定位

**+CME ERROR 564 = DNS parse failed**：

```text
DNS 解析失败原因：
  1. APN 没带 DNS（NB-IoT APN 经常不给 DNS）
  2. 平台域名错（写错 / 解析不到）
  3. DNS 服务器本身不可达

中国移动 NB-IoT APN = cmnb：
  默认不带 DNS（与普通 cmnet 不同）
  需手动配 DNS 或 走 IP
```

**根因**：

```text
物联网项目常用 NB-IoT 卡
NB-IoT 运营商 APN 常不带 DNS
开发时误以为 DNS 自动有
生产时直接用域名 → DNS 失败
```

### 修复

```c
// 方案 1：手动配 DNS
AT+QIDNSCFG="114.114.114.114","8.8.8.8"
// 或
AT+QIDNSCFG="211.136.17.107","211.136.20.203"  // 中国移动 DNS

// 方案 2：模组指定 DNS
// 移远 EC200N
AT+QIDNSCFG="primary.dns","secondary.dns"

// 芯讯通 SIM7080
AT+CDNSCFG="8.8.8.8","8.8.4.4"

// 方案 3：服务器端用 IP 直连（最稳）
// 但 IP 变更时 OTA 更新

// 方案 4：客户端用 mDNS / 域名 → IP 缓存
// 启动时解析一次，缓存 IP
```

### 复盘

- **NB-IoT APN 默认无 DNS**，不是常识错误
- **DNS 失败是 NB-IoT / 专网 APN 常见问题**
- **产线测试时必须用域名 + DNS 验证**，不能只看 IP 通
- **首选 IP 直连**，避免 DNS 依赖
- **如用域名，必须手动配 DNS 服务器**

---

## 案例 5：模组过温保护导致频繁掉线

### 现象

某车载 Cat 1 设备，夏天中午车内温度 60°C，设备频繁掉线。10 分钟内掉线 5 次。

### 抓 log

```text
// 正常工作
AT+CEREG?
+CEREG: 0,1                               // 已注册

// 过温后
AT+CEREG?
+CEREG: 0,0                               // 未注册
AT+CSQ
+CSQ: 99,99                               // 无信号

// 重启
AT+CFUN=0
AT+CFUN=1
// 几分钟后
AT+CEREG?
+CEREG: 0,1                               // 恢复
```

**示波器看 VBAT**：

```text
正常：3.8V 稳压
过温：VBAT 跌至 3.2V → 触发模组过压保护
       + 模组温度传感器触发 shutdown
```

### 定位

**模组过温保护**：

```text
移远 EC200N 工作温度：-35°C ~ +75°C
存储温度：          -40°C ~ +90°C
过温保护阈值：       ~85°C

车载场景夏天：
  阳光直射 → 车内 60°C
  模组 + 自发热 → 80°C+
  触发过温保护 → 模组自动关机或重启
```

**根因**：

```text
1. 模组没有散热设计
2. 模组靠近热源（CPU / 电源）
3. 密封外壳无通风
4. 阳光直射（黑色外壳吸热）
```

### 修复

```c
// 方案 1：加散热片
// 模组背面加铝散热片
// 增大与外壳的导热面积

// 方案 2：调整模组位置
// 远离热源（如 CPU、PMIC）
// 靠近金属外壳（导热）

// 方案 3：开模散热孔
// 外壳开孔或加金属片
// 注意 IP 防护等级（IP67 需密封）

// 方案 4：主动散热（极端场景）
// 加风扇 / 半导体制冷片

// 方案 5：降频使用
AT+QCFG="band",0x8,0x0  // 减少并发频段
AT+QCFG="pwrctrl",1     // 降功率（牺牲速率）

// 方案 6：温控阈值
// 模组过温保护阈值（部分模组可配）
AT+QTEMP              // 读温度
// 75°C 预警，80°C 主动降频，85°C 关机
```

### 复盘

- **工业 / 车载产品** 必须做温升测试（-40°C ~ +85°C）
- **过温保护阈值** 写入产品手册，提醒客户散热
- **模组选型** 注意工作温度范围（汽车级 -40~85°C）
- **外壳材质** 金属散热好但吸热（黑色金属暴晒 60°C+）
- **密封 + 散热** 矛盾时，优先加金属内壳 + 外壳通风

---

## 案例 6：Cat 1 模组瞬态电流塌陷导致重启

### 现象

某共享设备使用 EC200N（Cat 1），设备随机重启，1 天 5~10 次。

### 抓 log

```c
// 串口 log
[main] power on, firmware V1.0.3
[net] AT+CFUN=0
[net] AT+CFUN=1
[net] AT+CSQ
+CSQ: 18,99
[net] AT+CEREG? → stat=1
[net] AT+QICSGP=1,1,"cmnet",... → OK
[net] AT+QIACT=1 → OK
[app] HTTP POST → reset!
[main] power on, firmware V1.0.3    // 重启
```

**示波器看 VBAT**：

```text
稳态：3.85V
注册时：跌至 3.50V（瞬态）
HTTP POST 时：跌至 3.20V（瞬态，2A 电流）
              → 触发模组过压保护
              → 模组重启
```

### 定位

**Cat 1 模组瞬态电流**：

```text
EC200N 数据手册：
  峰值电流：2 A（典型 RB 满载时）
  平均电流：~700 mA

电源设计：
  用 3.8V 稳压
  但稳压芯片电流限 1.5A
  → 瞬态 2A 时电压跌落
  → 模组掉电重启
```

**根因**：

```text
1. 电源芯片选型余量不够（1.5A → 应选 3A）
2. 大容量电容不够（瞬态电流需大电容 buffer）
3. 走线阻抗高（VBAT 走线细 → 压降）
4. 散热差（电源芯片过温保护）
```

### 修复

```c
// 硬件修复
// 1. 换电源芯片：3A 输出（如 MP2145 / SY8089）
// 2. 加 bulk capacitor：220µF 钽电容 + 100µF 陶瓷
// 3. 加瞬态抑制：TVS 二极管（5V）
// 4. 加软启动：电源 IC 限流启动

// 电源设计参考
// 输入：5V / 3A
// 输出：3.8V / 3A
// bulk cap：220µF × 2 + 100nF × 2（高频去耦）
// 走线：VBAT 走线宽 0.5mm 以上，长度 < 20mm

// 软件修复
// 1. 错峰传输：HTTP 完 → 等待 5s → 下次 HTTP
// 2. 限速：用 AT+QSCLK=1 限速模式
// 3. 预热：上电后等 30s 再传输（电容充电）
```

### 复盘

- **Cat 1 模组瞬态电流 2A**，电源设计必须有 50% 余量
- **bulk 电容** 是关键（瞬态电流缓存）
- **VBAT 走线** 要宽、要短
- **量产前** 必须做电源压力测试（连续 1000 次 HTTP POST）
- **便宜的电源芯片是定时炸弹**，选大品牌（TI / MPS / Silergy）

---

## 案例 7：SIM 卡不识别（卡座污染）

### 现象

某量产项目出货 5000 台，售后返修 100 台，20% 问题是 "SIM 不识别"。

### 抓 log

```text
AT+CPIN?
+CME ERROR: 10                            // SIM not inserted

AT+CPIN?
+CME ERROR: 13                            // SIM busy
AT+CPIN?
+CME ERROR: 14                            // SIM wrong
```

### 定位

**SIM 卡座常见问题**：

```text
1. 卡座虚焊（回流焊温度不当）
2. 卡座氧化（长期暴露空气）
3. 卡座污染（助焊剂残留、汗渍）
4. SIM 卡方向反（用户插错）
5. SIM 卡损坏（卡芯片刮伤）
```

**根因**：

```text
1. 卡座选型：用了便宜的 push-push 卡座（容易坏）
2. 回流焊：手工补焊，焊盘虚焊
3. 防护：没有防水罩（IP 防护不达标）
4. 库存：卡座长期暴露空气（库房湿度）
```

**额外验证**：

```text
万用表量卡座引脚：
  VCC / GND / DATA / CLK / RST
  各引脚对地电阻、电压正常

示波器看 SIM 卡 IO：
  DATA 线无信号 → 可能是卡座问题
  有信号但错 → 可能是 SIM 卡问题
```

### 修复

```c
// 方案 1：硬件修复
// 1. 换卡座：自弹式（push-push）→ 掀盖式（hinge）或焊死
// 2. 加 ESD 防护：SIM 卡各引脚加 TVS
// 3. 卡座下方铺地：屏蔽干扰
// 4. 卡座补焊：补焊所有引脚

// 方案 2：软件容错
// 1. 开机检测 SIM 状态
// 2. SIM 不识别时重试 3 次
// 3. 失败后 log 详细错误码
// 4. 提示用户检查 SIM

void check_sim_with_retry(void) {
    int retry = 3;
    while (retry--) {
        if (send_at("AT+CPIN?", "READY", 1000) == 0) {
            return;  // 成功
        }
        delay_ms(500);
    }
    // 失败：log + 上报服务器 + 提示用户
    log("SIM not detected, please check SIM card");
}

// 方案 3：用 eSIM / iSIM
// 减少物理 SIM 卡座（可靠性提升 10x）
```

### 复盘

- **SIM 卡座** 是出货后前 3 个月返修率最高的部件
- **卡座选型** 选掀盖式或焊死的（不要 push-push）
- **量产前** 必须做卡座插拔测试（1000 次）
- **ESD 防护** 必加（人体静电可击穿 SIM）
- **eSIM / iSIM** 是未来方向（特别是可穿戴）

---

## 案例 8：移动 NB-IoT 卡被插入 4G 设备

### 现象

某客户把中国移动 NB-IoT 卡插入 4G 路由器（Cat 4 设备），设备能识别 SIM，但搜不到 4G 网络。

### 抓 log

```text
AT+CPIN?
+CPIN: READY                              // SIM OK

AT+COPS=?
+COPS: (3,"CHINA MOBILE","CMCC","46000",7),...
// AcT = 7 = LTE，仅有 LTE 列表

AT+CSQ
+CSQ: 99,99

AT+CEREG?
+CEREG: 0,3                               // 注册被拒
+CEREG: 0,3,,,7,15                        // cause_type=7, reject_cause=15
                                            // EPS services not allowed in this PLMN
```

### 定位

**reject_cause 15 = EPS services not allowed in this PLMN**（3GPP TS 24.301 §5.5.3.2）：

```text
移动 NB-IoT 卡：
  - 套餐仅限 NB-IoT 网络
  - 不允许使用普通 4G LTE
  - 网络侧（MME）返回 15 拒绝

4G Cat 4 设备：
  - 走普通 LTE / Cat 4 网络
  - 跟 NB-IoT 无关

矛盾：卡 vs 设备能力不匹配
```

**根因**：

```text
客户没分清 NB-IoT 卡 vs 普通 SIM 卡
NB-IoT 卡仅限 NB-IoT 模组
普通 4G 设备插 NB-IoT 卡 → 拒绝
```

**类似问题**：

```text
电信 NB-IoT 卡 → 只能插 NB-IoT 模组
联通 NB-IoT 卡 → 只能插 NB-IoT 模组
普通 SIM 卡 → 不能插 NB-IoT 模组（NB-IoT 套餐不识别）
```

### 修复

```c
// 方案 1：客户教育（最有效）
// 卡上有标识："NB-IoT 专用" / "物联网卡"
// 包装上写明适用设备

// 方案 2：设备侧兼容（不推荐）
// 4G 设备如果能识别 NB-IoT 网络 → 切换
// 但 NB-IoT 网络 vs LTE 物理层不兼容
// 4G Cat 4 设备硬件上无法解 NB-IoT 信号

// 方案 3：模组侧 + 网络侧协商
// 移动 NB-IoT 套餐支持 NB-IoT + Cat 1（部分套餐）
// 联系运营商确认

// 方案 4：换卡
// 用普通 4G 卡（不是物联网卡）插 4G 设备
// 或用 NB-IoT 卡插 NB-IoT 设备
```

### 复盘

- **NB-IoT 卡 ≠ 普通 SIM 卡**，要明确标识
- **NB-IoT 卡 物理形态相同**（mini / micro / nano），但套餐不同
- **硬件上**：NB-IoT 模组 / 4G 模组不能通用（基带不一样）
- **套餐上**：NB-IoT 卡只允许 NB-IoT 网络，普通 4G 卡不允许 NB-IoT 网络
- **客户教育** 必要（包装 + 说明 + 客服话术）

---

## 案例 9：RACH 失败导致 NB-IoT 设备完全注册不上

### 现象

某地下停车场项目使用 BC26（NB-IoT），覆盖增强（CE Level 2）。地下室深度 5 层，10% 设备注册不上。

### 抓 log

```text
// 尝试注册
AT+CEREG?
+CEREG: 0,2                               // 搜网中（长时间）
// 5 分钟后
+CEREG: 0,0                               // 仍未注册

// 高通 QXDM 详细 log
L1 RACH: 尝试次数 32（最多 32）
L1 RACH: 全部失败 → RRC 连接失败
NAS: RACH failure, 持续重试

AT+CSQ
+CSQ: 3,99                                // RSRP ~ -107 dBm
```

**详细信号**：

```c
AT+QENG="servingcell"
+QENG: "servingcell",...
  RSRP: -107 dBm                          // 弱
  RSRQ: -18 dB
  SINR: -3 dB
  CE Level: 2
 重复次数: 32                              // 满重复
```

### 定位

**CE Level 2 极端场景**：

```text
NB-IoT 覆盖增强：
  CE Level 0: 重复 1 次（普通覆盖）
  CE Level 1: 重复 8 次
  CE Level 2: 重复 32~128 次

地下室 5 层 + 距离基站远：
  RSRP ~ -107 dBm（边缘）
  RSRQ ~ -18 dB（极差）
  SINR ~ -3 dB（噪声大）
  → CE Level 2 都救不回来
  → RACH 32 次都失败
```

**根因**：

```text
1. 地下室无 NB-IoT 室内分布
2. 信号衰减超出 CE Level 2 极限（164 dB MCL）
3. 设备天线增益不足
4. 地下室有金属结构屏蔽
```

### 修复

```c
// 方案 1：加室内分布（运营商侧）
// 联系运营商部署 NB-IoT 室内分布
// 或自建 Pico 基站

// 方案 2：加外置天线
// 用高增益天线（5 dBi → 8 dBi）
// 天线拉到地下室入口

// 方案 3：换位置
// 设备安装位置靠近窗户 / 通风口
// 避开金属结构

// 方案 4：换 Cat M1（更广覆盖）
// Cat M1 移动性比 NB-IoT 好
// 室外 NB-IoT 失败场景，Cat M1 可能成功
// 但 Cat M1 模组更贵

// 方案 5：换 LoRa（更远距离）
// LoRa MCL 可达 157 dB
// NB-IoT 救不回来，LoRa 可能可以

// 方案 6：场景适配
// 地下室 5 层 NB-IoT 本来就难
// 现场勘测：地下室 1~2 层可装设备，3~5 层换方案
```

### 复盘

- **NB-IoT 覆盖极限 164 dB MCL**，超出后无解
- **部署前必须做现场勘测**（RSRP / RSRQ / SINR 全测）
- **CE Level 仅 32~128 次重复**，救不回来就彻底失败
- **设备安装位置** 对覆盖影响巨大（10cm 距离可能差 10 dB）
- **极端场景**（地下室 / 电梯 / 管道）需要多技术（NB-IoT + LoRa + 卫星）
- **客户预期管理**："NB-IoT 哪里都能用" 是营销话术，物理定律不能违反

---

## 案例汇总

| # | 现象 | 根因 | 难度 |
| --- | --- | --- | --- |
| 1 | NB-IoT 完全搜不到网 | 频段错配 / 固件版本 | 低 |
| 2 | PDP 激活失败 | APN 错 | 低 |
| 3 | PSM 启用后下行丢失 | PSM 不可达 | 中 |
| 4 | DNS 解析失败 | NB-IoT APN 无 DNS | 低 |
| 5 | 模组过温掉线 | 工作温度超限 | 中 |
| 6 | Cat 1 瞬态电流塌陷 | 电源设计余量不足 | 中 |
| 7 | SIM 不识别 | 卡座污染 / 虚焊 | 低 |
| 8 | NB-IoT 卡插 4G 设备 | 套餐 vs 设备能力不匹配 | 低 |
| 9 | NB-IoT RACH 失败 | 覆盖超出 CE Level 2 | 高 |

## 关联文档

- `bus/lte-iot.md` 主题入口
- `bus/lte-iot-practical.md` 调试流程速查
- `bus/lte-iot-deep-dive.md` 协议栈深挖
- `bus/lte-iot-index.md` 主题地图 + 导航
