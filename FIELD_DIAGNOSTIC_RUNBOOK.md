# Field Diagnostic Runbook

## 目标

本文定义通信现场问题的标准处理流程，用于把“现场说不稳定”转成可定位、可复现、可修复、可回归的工程闭环。

适用场景：

- 客户现场通信异常。
- 量产返修通信问题。
- 路试、产线、实验室无法稳定复现的问题。
- 远程诊断、网关、升级和工业网络问题。
- 高风险链路的临时规避和正式修复。

## 总流程

推荐流程：

```text
接报
  -> 分级
  -> 保护现场
  -> 收集证据
  -> 分层定位
  -> 最小复现
  -> 临时规避
  -> 根因修复
  -> 回归验证
  -> 质量门禁更新
  -> 关闭
```

不要在证据收集前反复重启、清故障、升级固件或替换硬件，除非存在安全风险。

## 接报信息

第一时间收集：

| 字段 | 说明 |
| --- | --- |
| 产品序列号 | 追溯硬件和生产记录 |
| 硬件版本 | PCB、模组、线束、连接器版本 |
| 固件版本 | Bootloader、Application、协议栈、配置版本 |
| 环境 | 温度、电压、线缆长度、负载、网络拓扑 |
| 现象 | 无响应、偶发掉线、数据错、升级失败、黑屏 |
| 频率 | 必现、偶发、运行多久后出现 |
| 影响 | 单台、多台、单客户、批次性 |
| 最近变更 | 固件、线束、配置、外设、网络、工艺 |
| 临时恢复 | 重启、插拔、降速、换线、清故障是否有效 |

现场描述要尽量转换为可验证事实。

## 分级

按影响分级：

| 等级 | 条件 | 响应 |
| --- | --- | --- |
| P0 | 安全风险、批量变砖、产线停线 | 立即升级响应，冻结相关发布 |
| P1 | 核心功能不可用、客户现场停机 | 当日定位方向，提供规避方案 |
| P2 | 偶发异常、有恢复手段 | 收集证据，进入版本修复计划 |
| P3 | 轻微告警、日志噪声、体验问题 | 纳入维护队列 |

通信升级失败、运动控制异常、车载视频黑屏和远程诊断不可用通常不应低估。

## 保护现场

保护现场的目标是保留证据。

优先动作：

- 保存当前日志和快照。
- 拍照记录接线、线束、连接器和指示灯。
- 记录电源电压、温度和运行时长。
- 导出配置和版本。
- 保存抓包或总线 trace。
- 标记故障设备，避免混入正常样机。

避免动作：

- 未导出日志就清故障。
- 未记录版本就升级。
- 未拍照就换线。
- 未保存状态就断电。
- 同时改变多个变量。

如果必须恢复生产，应先保存最小证据集。

## 最小证据集

最小证据集：

```text
问题描述
时间和环境
硬件/固件/配置版本
通信状态和错误计数器
最近事件日志
关键抓包或波形
复位原因
临时恢复动作和结果
```

高风险问题额外需要：

- 电源波形或电压记录。
- 线缆、连接器和拓扑照片。
- 寄存器 dump。
- 量产测试记录。
- 同批次正常样机对比。
- 故障前后的完整日志。

## 分层定位

按层判断：

| 层级 | 典型证据 | 下一步 |
| --- | --- | --- |
| Physical | 电压异常、断线、终端错误、Link down | 查接线、电源、连接器、收发器 |
| Electrical | 上升沿慢、振铃、差分幅度不足 | 降速、换线、示波器测量 |
| Link | ACK Error、NACK、枚举失败、lock drop | 查地址、时钟、终端、链路参数 |
| Transport | ISO-TP 超时、TCP reset、USB STALL | 查分包、缓冲区、超时、Host |
| Protocol | NRC、异常码、状态位、格式错误 | 查协议状态机和配置 |
| Application | 权限、单位、PAGE、对象映射、业务条件 | 查数据库、标定、版本兼容 |
| Tool | 抓包点错、工具版本错、治具故障 | 复核工具和测试脚本 |

现场问题常常跨层。先找第一个明确异常层级。

## 最小复现

将复杂现场降级：

1. 单设备。
2. 最短线缆。
3. 最低速率。
4. 固定电源。
5. 固定版本。
6. 最简单命令。
7. 读取 ID 或状态。

逐步恢复现场变量：

- 线缆长度。
- 多设备数量。
- 高速参数。
- 背景负载。
- 温度。
- 真实业务流程。
- 长时间运行。

每次只改变一个变量，并记录结果。

## 临时规避

临时规避必须满足可回退。

常见措施：

| 问题 | 临时规避 |
| --- | --- |
| I2C NACK | 降低速率、增大超时、启用总线恢复 |
| RS485 丢字节 | 延迟关闭 DE、降低波特率 |
| CAN Bus Off | 自动恢复、降低负载、检查终端 |
| UDS 刷写失败 | 降低 block size、增大 STmin、限制低电压刷写 |
| PMBus 误报 | 关闭自动动作，只上报告警，保留 raw word |
| TSN 尾延迟 | 关闭背景流、修正队列映射、降低实时流负载 |
| SerDes 掉线 | 降速、换短线、禁用故障端口、增强日志 |
| USB DFU 风险 | 禁止远程升级，强制进入安全 Bootloader |

规避措施要记录适用版本、影响范围和撤销条件。

## 协议专项取证

I2C/SMBus/PMBus：

- SCL/SDA 波形。
- 上拉阻值和总线电容估算。
- 地址、命令码、ACK/NACK。
- `STATUS_WORD`、`STATUS_CML`、raw word、PAGE。
- PEC 开关和计算方式。

CAN/ISO-TP/UDS：

- CAN ID、DLC、错误帧。
- Flow Control、BS、STmin、CF 序号。
- UDS SID、NRC、P2/P2*。
- 会话、安全等级、Transfer Data block 序号。
- ECU reset reason 和 Bootloader 日志。

Ethernet/TSN：

- PHY Link、速率、双工。
- ARP、IP、TCP reset。
- VLAN PCP、PTP offset、队列统计。
- Qbv 配置和 p99/p999 延迟。
- 交换机端口配置和固件版本。

USB/DFU：

- 枚举日志和描述符。
- Endpoint、STALL、reset。
- DFU download block、getstatus、manifest。
- 镜像 header、load address、CRC/hash、metadata。
- Bootloader 和 Application 版本。

MIPI/SerDes/显示：

- 电源、reset、MCLK。
- Sensor ID 或 EDID/DPCD。
- Link Lock、lock drop、PoC 电压。
- CSI/DSI error counter、VC/DT、Lane。
- 背光、HPD、AUX、Link Training。

## 远程诊断包

建议一键导出远程诊断包。

目录建议：

```text
field-dump-<serial>-<time>/
  summary.txt
  versions.json
  topology.txt
  counters.json
  events.jsonl
  snapshots/
  traces/
  photos/
  configs/
  production-record.json
```

`summary.txt` 至少包含：

- 问题摘要。
- 影响范围。
- 最近变更。
- 临时恢复动作。
- 当前风险等级。
- 联系人和时间。

## 根因关闭标准

问题关闭必须满足：
```text
有可解释根因
有修复提交或配置变更
有复现用例
有回归用例
有现场验证结果
有风险评估
```

不能只以“现场暂时没再出现”作为关闭标准。

## 修复后回归

修复后至少执行：

- 原始复现步骤。
- 最小通信测试。
- 同类协议错误路径。
- 断线或重启恢复。
- 长时间运行。
- 量产最小测试，视影响范围。

高风险修复还要执行：

- 异常注入。
- 低电压或高低温。
- 固件升级和回滚。
- 多版本兼容。
- 现场日志导出验证。

## 经验沉淀

关闭后要更新：

- `FAILURE_CASES.md`：记录现象、排查、根因、修复。
- `TROUBLESHOOTING_QUICKREF.md`：补现场速查入口。
- `REGRESSION_TEST_MATRIX.md`：补回归用例。
- `AUTOMATED_TEST_HARNESS.md`：补 adapter 或测试脚本能力。
- `COMMUNICATION_OBSERVABILITY.md`：补计数器、状态或日志字段。
- `COMMUNICATION_QUALITY_GATE.md`：补门禁要求或风险接受规则。

## 现场沟通模板

建议对外沟通使用事实结构：

```text
当前现象：
影响范围：
已收集证据：
初步分层判断：
临时规避方案：
下一步验证：
预计更新时间：
风险和限制：
```

不要在根因未确认前承诺具体硬件或软件原因。

## 延伸阅读

- `DEBUG_PLAYBOOK.md`
- `TROUBLESHOOTING_QUICKREF.md`
- `FAILURE_CASES.md`
- `COMMUNICATION_OBSERVABILITY.md`
- `MEASUREMENT_EXAMPLES.md`
- `REGRESSION_TEST_MATRIX.md`
- `COMMUNICATION_QUALITY_GATE.md`
