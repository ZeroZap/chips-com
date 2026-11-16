# CANopen 候选素材 @ 2026-11-16 00:00

## 协议速览
- 是什么 / 解决什么：CAN 之上的工业应用层协议（CiA 301），统一对象字典与 SDO/PDO/NMT 语义
- L4 关联：库内 CANopen 5 篇（safety + 12 例 failure-cases），认证/一致性 0 命中，FD 与 CiA 402 近乎空白

## 候选文章（5 条）

### 1. CANopen 认证级测试：一致性认证完整路径
- 链接：http://www.gpio.com.cn/theory/canopen/11-canopen-certification-test.html
- 来源：gpio.com.cn CANopen 专题
- 摘要：四层认证 + CTT 到证书路径，附 SocketCAN 自测代码。
- 关键实战点：
  ① 送测首因：EDS 与固件不一致，缺 0x1001/0x1018 判失败
  ② bus-off 时序：256 次错误→128×11 隐性位后恢复
  ③ 物理层：显性差分 1.5–3.0 V、隐性 ≤0.5 V、采样点 70–90%
- 推荐动作：写实战案例 + 扩 deep-dive

### 2. CANopen FD device conformance testing
- 链接：https://www.can-cia.org/services/cia-test-center/canopen-fd-device-conformance-testing
- 来源：CiA 官方测试中心（CiA 1310-1）
- 摘要：FD 一致性 29 步流程 + 错误清单。
- 关键实战点：
  ① 必须带与实物一致的 XDD 才送测
  ② 用对象字典调 Node-ID/波特率基本必挂
  ③ 含 USDO 分段传输、SYNC 计数、隐藏对象扫描
- 推荐动作：扩 deep-dive → 新建 bus/canopen-fd.md

### 3. Resolving CANopen Bus-Off Errors Between VFDs and PLC Systems
- 链接：https://industrialmonitordirect.com/blogs/knowledgebase/resolving-canopen-bus-off-errors-between-vfds-and-plc-systems
- 来源：Industrial Monitor Direct
- 摘要：AC VFD 并入电池组 CANopen 网，加速即 Bus-Off。
- 关键实战点：
  ① 差分探头看不出，须单端探 CAN_GND（~60 Vpp，规格 -2~+7 V）
  ② 三点接地 + 屏蔽两端 360° 夹持，禁 pigtail
  ③ 断电测 PE↔BAT- 应 <0.1 Ω
- 推荐动作：写实战案例 → 入 failure-cases

### 4. Troubleshooting CODESYS CiA 402 Axis Not Running on ASDA-A2E
- 链接：https://industrialmonitordirect.com/blogs/knowledgebase/troubleshooting-codesys-cia-402-axis-not-running-on-asda-a2e
- 来源：Industrial Monitor Direct（EtherCAT 载波）
- 摘要：DS402 状态机全表 + 8 条根因矩阵。
- 关键实战点：
  ① Operation Enabled 判据 = Statusword 0x0237，控制字 0x06→07→0F
  ② 0x1C32:0x02 单位纳秒，1 ms 主站写 1000000
  ③ 固件 1.005 改 0x60B8 类型，旧 ESI 致 PDO 全空
- 推荐动作：写实战案例 → 建 canopen-drive-profile.md

### 5. CANopen 对象字典工程化实践：从建模到 STM32 集成
- 链接：https://blog.csdn.net/root9/article/details/155737343
- 来源：CSDN 量产复盘
- 摘要：OD Editor 建模→导出 C 头文件→STM32 集成。
- 关键实战点：
  ① CO_OD_ArraySize 漏计子索引→读未初始化内存 HardFault
  ② OD 变量未初始化→上电状态字随机非零被主站误判
- 推荐动作：写实战案例 + 扩 practical

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
