# Communication Observability

## 目标

本文定义通信系统的可观测性设计方法，帮助设备在实验室、量产、现场和远程维护阶段留下足够证据，让通信问题可定位、可复现、可回归。

核心目标：

- 让每个通信链路都有状态、计数器和最近错误。
- 让失败能定位到物理、链路、传输、协议、应用或工具层。
- 让现场日志能和实验室抓包、寄存器 dump、测试结果关联。
- 让长期运行问题有趋势数据，而不是只看到最后一次崩溃。
- 控制日志量、隐私和 Flash 写入寿命。

## 可观测性分层

推荐按以下层级记录：

| 层级 | 观测内容 |
| --- | --- |
| Physical | 电源、电平、Link、线缆、温度、reset 原因 |
| Link | ACK/NACK、CRC、错误帧、枚举状态、lock 状态 |
| Transport | ISO-TP、TCP、USB transfer、DoIP、分包和重组状态 |
| Protocol | UDS NRC、Modbus exception、PMBus status、CIP status |
| Driver | 状态机、超时、重试、恢复、buffer 水位、DMA 状态 |
| Application | DID、对象字典、业务状态、权限、版本、配置 |
| Tool | 测试脚本、治具、抓包工具、PLC/Host 工具版本 |

不要把所有错误都压缩成 `communication_failed`。这会让现场问题无法闭环。

## 通用状态模型

每个通信对象建议至少有：

```text
UNKNOWN
INIT
PROBING
CONFIGURING
READY
RUNNING
DEGRADED
RECOVERING
OFFLINE
FAILED
```

状态含义：

| 状态 | 含义 |
| --- | --- |
| UNKNOWN | 尚未初始化或没有数据 |
| INIT | 本地接口初始化中 |
| PROBING | 正在读取 ID、枚举或发现设备 |
| CONFIGURING | 正在写配置或协商参数 |
| READY | 最小通信已通过 |
| RUNNING | 正常业务通信中 |
| DEGRADED | 降级运行，例如降速、部分通道不可用 |
| RECOVERING | 正在执行恢复动作 |
| OFFLINE | 设备离线但可继续重试 |
| FAILED | 不可自动恢复，需要人工或重启 |

状态变化必须记录原因和时间。

## 通用计数器

每条链路建议维护：

```text
tx_count
rx_count
timeout_count
retry_count
crc_error_count
format_error_count
auth_error_count
nak_or_nrc_count
disconnect_count
recover_count
reset_count
last_success_time
last_error_time
last_error_code
last_error_layer
```

不同协议扩展专用计数器：

| 协议 | 专用计数器 |
| --- | --- |
| I2C/SMBus | address_nack、data_nack、bus_busy、bus_recovery |
| SPI/QSPI | cs_error、dummy_mismatch、verify_fail、wip_timeout |
| CAN | ack_error、bus_off、error_passive、rx_overrun |
| ISO-TP | fc_timeout、cf_timeout、sn_mismatch、reassembly_fail |
| UDS | nrc_count、security_fail、session_timeout、pending_count |
| Ethernet | link_down、arp_miss、tcp_reset、socket_timeout |
| TSN | ptp_offset_max、queue_drop、late_packet、gate_miss |
| USB | enum_fail、stall_count、reset_count、ep_timeout |
| DFU | block_fail、crc_fail、manifest_fail、rollback_count |
| PMBus | pec_error、cml_fault、status_word、page_switch_count |
| SerDes | lock_drop、back_channel_error、remote_i2c_fail、csi_error |
| MIPI | ecc_error、crc_error、frame_drop、line_error |
| PCIe | ltssm_fail、aer_error、link_retrain、dma_crc_fail |

计数器要有清零策略。建议支持“自上电以来”和“最近窗口”两种视图。

## 事件日志格式

建议每条事件包含：

```json
{"time_ms":123456,"if":"can0","dev":"motor2","state":"RECOVERING","layer":"link","event":"bus_off","detail":{"txerr":255,"rxerr":12,"action":"reinit"}}
```

字段建议：

| 字段 | 说明 |
| --- | --- |
| time_ms | 单调时间，便于排序 |
| wall_time | 可选，真实时间 |
| if | 接口名 |
| dev | 设备名或节点 |
| state | 当前状态 |
| layer | 失败层级 |
| event | 事件名 |
| detail | 协议相关字段 |
| seq | 日志序号，便于检测丢日志 |

事件名要稳定，不要频繁改字符串，否则不利于统计。

## 快照 Dump

错误发生时建议保存快照。

快照内容：

- 当前状态。
- 最近 N 条事件。
- 计数器。
- 当前配置参数。
- 关键寄存器。
- 最近一次请求和响应摘要。
- 电源、温度和 reset 原因。
- 固件、硬件和配置版本。

示例：

```text
dump_id=can0_motor2_20260621_101530
state=RECOVERING
last_error=heartbeat_timeout
can_bitrate=500000
node_id=2
tx_count=120340
rx_count=119992
recover_count=3
last_frames=...
```

快照应避免保存敏感密钥和完整用户数据。

## 环形日志和持久化

嵌入式设备不应无限写日志。

推荐策略：

- RAM 中维护环形事件日志。
- 关键错误触发持久化快照。
- 持久化频率限流。
- 重要计数器定期 checkpoint。
- Flash 日志区 wear leveling。
- 支持导出后清除。

不要在高频中断里直接写 Flash 或阻塞输出日志。

## 远程诊断接口

现场维护建议提供只读诊断接口。

至少支持：

- 读取版本。
- 读取通信状态。
- 读取错误计数器。
- 读取最近错误。
- 导出快照。
- 触发安全的重新初始化。
- 清除计数器，需权限控制。

接口形态可以是：

- CLI。
- Web API。
- UDS DID。
- Modbus register。
- MQTT topic。
- 文件导出。
- 产线治具命令。

远程诊断必须区分只读操作和会改变系统状态的操作。

## 协议状态页

建议产品提供通信状态页。

最小字段：

| 字段 | 示例 |
| --- | --- |
| Interface | can0 / i2c1 / eth0 |
| Device | motor2 / sensor0 / plc |
| State | RUNNING / DEGRADED / OFFLINE |
| Last success | 2026-06-21 10:15:30 |
| Last error | crc_error |
| Error layer | link |
| Recover count | 3 |
| Version | fw=1.2.3 cfg=4 |

状态页不应只显示“正常/异常”，否则无法定位。

## 告警设计

告警应基于状态和趋势，不只看单次错误。

建议分级：

| 等级 | 条件 | 动作 |
| --- | --- | --- |
| Info | 单次可恢复错误 | 记录事件 |
| Warning | 错误率升高或进入 DEGRADED | 上报和保留快照 |
| Error | 设备 OFFLINE 或服务失败 | 上报告警并尝试恢复 |
| Critical | 影响安全或升级失败 | 停止危险动作并要求人工介入 |

示例：

```text
I2C 单次 NACK -> Info
I2C 1 分钟内 NACK 超过 100 次 -> Warning
Sensor 连续 3 次恢复失败 -> Error
固件升级校验失败且无可回滚镜像 -> Critical
```

## 与测试系统关联

自动化测试应读取同一套状态和计数器。

测试前：

- 读取版本。
- 清零测试窗口计数器。
- 保存初始状态。

测试中：

- 采集事件日志。
- 采集协议 trace。
- 记录异常注入时间点。

测试后：

- 读取最终状态。
- 读取计数器增量。
- 导出快照。
- 生成 artifact 链接。

这样现场和实验室看到的是同一套语言。

## 协议观测示例

I2C 设备：

```text
state=RUNNING
addr=0x68
speed=400k
tx=102030
rx=102030
address_nack=0
data_nack=2
bus_recovery=1
last_error=data_nack reg=0x20
```

UDS 刷写：

```text
state=DOWNLOADING
session=programming
security=unlocked
block_seq=128
isotp_fc_timeout=0
isotp_sn_mismatch=0
uds_nrc_last=none
flash_program_max_ms=18
```

TSN：

```text
state=RUNNING
ptp_state=synchronized
ptp_offset_max_ns=420
rt_flow_p99_us=150
rt_flow_p999_us=240
queue_drop=0
gate_miss=0
```

SerDes 摄像头：

```text
state=RUNNING
port=2
link_lock=1
lock_drop=0
remote_i2c_ok=1
csi_crc_error=0
sensor_mode=1920x1080_30_raw12
```

PMBus：

```text
state=RUNNING
page=1
status_word=0x0000
read_iout_raw=0xe8c0
read_iout_a=18.2
pec_error=0
cml_fault=0
```

## 数据保留和隐私

日志可能包含敏感信息。

注意：

- 不记录明文密钥。
- 不长期保存 UDS SecurityAccess key。
- 不保存用户隐私 payload。
- 对远程导出的日志做脱敏。
- 记录日志版本，便于解析工具兼容。
- 对环形日志设置容量上限。

## 最小落地清单

优先实现：

- 每条链路一个状态。
- 每条链路一组计数器。
- 最近错误和错误层级。
- 可导出的快照。
- 自动化测试能读取计数器。
- 现场能导出日志。

后续增强：

- 事件日志结构化。
- 趋势和告警。
- 远程诊断接口。
- 与 CI/HIL artifact 自动关联。
- 量产工位日志上传。

## 延伸阅读

- `DEBUG_PLAYBOOK.md`
- `DRIVER_PATTERNS.md`
- `RELIABILITY_GUIDE.md`
- `AUTOMATED_TEST_HARNESS.md`
- `REGRESSION_TEST_MATRIX.md`
- `MEASUREMENT_EXAMPLES.md`
- `FAILURE_CASES.md`
