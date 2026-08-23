# Automated Test Harness

## 目标

本文说明如何把通信调试经验、测量样例和回归测试矩阵落到自动化测试治具中，形成可执行、可判定、可追溯的测试系统。

适用范围：

- 新板 bring-up 自动化。
- 固件版本回归。
- 协议栈升级验证。
- 量产工位测试。
- 现场故障复现和关闭。
- 长时间稳定性和异常注入。

## 总体架构

推荐把测试系统分成五层：

```text
Test Runner
    |
Test Case Model
    |
Protocol Adapter
    |
Instrument Adapter
    |
Device Under Test
```

职责：

| 层级 | 职责 |
| --- | --- |
| Test Runner | 调度用例、超时、重试、结果汇总 |
| Test Case Model | 描述前置条件、步骤、期望、证据 |
| Protocol Adapter | 封装 UART/I2C/CAN/USB/Ethernet 等操作 |
| Instrument Adapter | 控制示波器、逻辑分析仪、电源、继电器、抓包工具 |
| DUT | 被测板卡、模块、传感器、PLC、ECU 或网关 |

测试脚本不应直接散写底层命令。协议和仪器都应通过 adapter 暴露稳定接口。

## 测试用例模型

建议用结构化格式描述测试。

示例：

```yaml
id: i2c_sensor_id_001
title: Read sensor chip ID
protocol: i2c
level: bringup
topology: mcu_i2c0_to_sensor0
precondition:
  power: 3.3V enabled
  reset: released
steps:
  - scan_address: 0x68
  - read_reg: { addr: 0x68, reg: 0x00, len: 1 }
expect:
  chip_id: 0x42
evidence:
  - i2c_trace
  - driver_log
timeout_ms: 1000
retry: 2
```

关键字段：

| 字段 | 说明 |
| --- | --- |
| id | 稳定唯一编号 |
| title | 简短可读标题 |
| protocol | 协议或接口 |
| level | bringup / parameter / negative / recovery / stress / production |
| topology | 被测连接关系 |
| precondition | 电源、复位、固件、线缆和工具状态 |
| steps | 可执行动作 |
| expect | 可机器判定的期望 |
| evidence | 必须采集的证据 |
| timeout_ms | 超时边界 |
| retry | 允许重试次数 |

## 结果日志 Schema

每个测试结果建议保存为 JSON Lines，便于追加和索引。

示例：

```json
{"time":"2026-06-21T10:15:30Z","test_id":"can_busoff_003","result":"fail","layer":"physical","error":"bus_off","dut":"board-a-001","hw":"revB","fw":"1.2.3","tool":"can-analyzer-2.1","evidence":["trace/can_busoff_003.asc","logs/board-a-001.txt"]}
```

推荐字段：

| 字段 | 说明 |
| --- | --- |
| time | UTC 时间 |
| test_id | 用例编号 |
| result | pass / fail / skip / blocked |
| layer | physical / link / transport / protocol / application / tool |
| error | 归一化错误码 |
| dut | 被测设备序列号 |
| hw | 硬件版本 |
| fw | 固件版本 |
| tool | 工具和治具版本 |
| duration_ms | 用例耗时 |
| evidence | 原始证据路径 |
| metrics | 关键数值，如延迟、错误计数、电压 |

## 错误分层

自动化系统必须给失败分层，而不是只输出 fail。

推荐层级：

| 层级 | 示例 |
| --- | --- |
| physical | 电源低、线缆断、终端错误、信号幅度异常 |
| link | ACK Error、USB 枚举失败、PHY Link down |
| transport | ISO-TP CF 超时、TCP 断连、USB transfer STALL |
| protocol | UDS NRC、Modbus exception、PMBus CML fault |
| application | DID 不存在、Flash 校验失败、Sensor ID 不匹配 |
| tool | 抓包工具未启动、串口被占用、治具继电器失败 |

分层失败的价值：

- 便于筛选同类问题。
- 便于决定责任边界。
- 便于生成趋势图。
- 便于现场复现和关闭。

## 证据归档规则

每次失败至少保存：

- 测试用例定义。
- 测试结果 JSON。
- DUT 日志。
- 工具日志。
- 原始抓包或波形。
- 关键寄存器 dump。
- 环境和版本信息。

建议目录：

```text
artifacts/
  run-20260621-101530/
    summary.json
    results.jsonl
    dut-log.txt
    tool-log.txt
    traces/
    waveforms/
    dumps/
    configs/
```

文件名应包含 `test_id`、DUT 序列号和时间，避免覆盖。

## 协议 Adapter 示例

I2C adapter 最小接口：

```text
i2c.scan(bus)
i2c.read(bus, addr, reg, len)
i2c.write(bus, addr, reg, data)
i2c.recover(bus)
i2c.capture(bus, duration_ms)
```

CAN / ISO-TP / UDS adapter 最小接口：

```text
can.send(id, data)
can.expect(id, timeout_ms)
isotp.request(payload, bs, stmin)
uds.service(sid, payload)
uds.read_did(did)
uds.security_access(level)
uds.transfer_data(block_no, data)
```

Ethernet / TSN adapter 最小接口：

```text
net.ping(ip)
net.capture(filter, duration_ms)
net.measure_latency(flow, duration_s)
ptp.status()
switch.read_queue_stats(port)
switch.apply_qbv(profile)
```

USB / DFU adapter 最小接口：

```text
usb.enumerate(vid, pid)
usb.read_descriptors()
dfu.enter()
dfu.download(image)
dfu.get_status()
dfu.verify_crc()
dfu.reset()
```

PMBus adapter 最小接口：

```text
pmbus.read_word(addr, command)
pmbus.write_word(addr, command, value)
pmbus.set_page(addr, page)
pmbus.read_status(addr)
pmbus.convert_linear11(raw)
pmbus.clear_faults(addr)
```

SerDes adapter 最小接口：

```text
serdes.read_local_id()
serdes.read_remote_id(port)
serdes.link_status(port)
serdes.dump_registers(port)
serdes.read_error_counters(port)
camera.read_sensor_id(port)
camera.capture_frame(port)
```

## 仪器 Adapter 示例

可编程电源：

```text
psu.set_voltage(channel, voltage)
psu.set_current_limit(channel, current)
psu.output_on(channel)
psu.output_off(channel)
psu.measure(channel)
```

继电器矩阵：

```text
relay.connect(path)
relay.disconnect(path)
relay.pulse(path, duration_ms)
```

示波器：

```text
scope.configure(channel, scale, offset)
scope.trigger(edge, channel, level)
scope.capture(duration)
scope.measure_rise_time(channel)
scope.save_waveform(path)
```

抓包工具：

```text
capture.start(interface, filter)
capture.stop()
capture.save(path)
capture.stats()
```

## 判定策略

测试应尽量机器判定。

常见判定：

- ID 等于期望值。
- 错误计数不增长。
- p99 延迟小于阈值。
- CRC/hash 匹配。
- 状态机进入目标状态。
- N 秒内自动恢复。
- 日志中不存在指定错误码。

不建议只判定：

- “肉眼看起来有图”。
- “工具显示 OK”。
- “没有明显报错”。
- “测试人员认为正常”。

主观判定可以存在，但必须附带图像、截图或视频，并标记为 manual evidence。

## 异常注入自动化

自动化治具应支持受控异常。

常见注入：

| 注入 | 治具方法 | 验证目标 |
| --- | --- | --- |
| 断电 | 可编程电源输出关闭 | 回滚、防变砖、状态恢复 |
| 掉线 | 继电器断开线缆 | 断线检测和重连 |
| 降压 | 电源阶跃降低 | 低电压保护和日志 |
| 高负载 | 背景流或满帧发送 | 缓冲区和尾延迟 |
| 错帧 | 协议工具发送非法帧 | 错误路径和 NRC/异常码 |
| 设备忙 | 插入延迟或阻塞响应 | 超时、重试、pending |

异常注入后必须验证恢复，而不是只验证能检测错误。

## 长稳测试

长稳测试建议输出周期性 metrics。

示例字段：

```text
uptime_s
tx_count
rx_count
timeout_count
crc_error_count
reset_count
recover_count
memory_free
temperature
voltage
last_error
```

判定建议：

- 错误计数不能无限增长。
- recover 后必须回到 READY/RUNNING。
- 内存不能持续下降。
- 断链重连次数要可解释。
- 日志不能刷爆存储寿命。

## CI 集成

CI 中适合分层执行：

| 阶段 | 内容 | 触发 |
| --- | --- | --- |
| Static | 配置、脚本、协议表、镜像 header 检查 | 每次提交 |
| Simulator | 协议状态机和解析器单元测试 | 每次提交 |
| HIL smoke | 最小通信和枚举 | 每日或关键提交 |
| HIL regression | 回归矩阵核心用例 | 夜间 |
| HIL stress | 长稳、异常注入、高低温 | 发布前 |

CI 失败输出必须包含 artifact 链接，不能只显示红绿状态。

## 量产集成

量产测试关注速度、稳定和可追溯。

建议：

- 测试项分为 must-pass 和 audit-only。
- 每台设备绑定序列号、硬件版本、固件版本和治具 ID。
- 失败项保存最小日志，不保存过大波形。
- 抽检工位保存完整波形和抓包。
- 治具自身定期自检。
- 量产阈值和研发阈值分开管理。

量产不适合执行所有复杂异常注入，但必须覆盖电源、接口连通性、设备 ID 和关键功能。

## 现场复现闭环

现场问题关闭应满足：

1. 能用自动化用例复现或近似复现。
2. 失败能归到明确层级。
3. 修复后同一用例通过。
4. 用例加入回归矩阵。
5. 证据归档到故障案例。

如果不能复现，至少要把现场日志转换成一个监控用例，确保同类问题再次出现时能被捕获。

## 最小落地路线

推荐分三步落地：

1. 先自动化最小通信和 ID 读取。
2. 再加入错误计数、日志和 artifact 归档。
3. 最后加入异常注入、长稳和 CI/HIL。

不要一开始追求全协议全自动化。先保证少量高价值用例稳定可靠，再逐步扩展。

## 延伸阅读

- `REGRESSION_TEST_MATRIX.md`
- `MEASUREMENT_EXAMPLES.md`
- `EXPERIMENT_TEMPLATE.md`
- `PRODUCTION_TEST.md`
- `RELIABILITY_GUIDE.md`
- `DRIVER_PATTERNS.md`
- `FAILURE_CASES.md`
