# Communication Traceability

## 目标

本文定义通信需求、风险、设计、测试、可观测性、故障案例和发布门禁之间的追踪关系，确保每个高风险通信项都有明确证据链。

追踪矩阵用于回答：

- 这个通信需求来自哪里。
- 它的主要风险是什么。
- 哪个设计项降低了风险。
- 哪些测试覆盖了风险。
- 失败时能看到哪些日志和计数器。
- 现场问题是否已经进入回归。
- 发布时是否满足质量门禁。

## 追踪对象

建议为以下对象分配稳定 ID：

| 对象 | ID 前缀 | 示例 |
| --- | --- | --- |
| Requirement | REQ | REQ-CAN-001 |
| Risk | RISK | RISK-UDS-DFU-001 |
| Design | DES | DES-PMBUS-PAGE-001 |
| Test | TEST | TEST-TSN-QBV-003 |
| Observable | OBS | OBS-SERDES-LOCK-001 |
| Failure Case | CASE | CASE-USBDFU-BOOT-001 |
| Quality Gate | GATE | GATE-R4-RELEASE-001 |
| Artifact | ART | ART-CANTRACE-20260621-001 |

ID 应稳定，不随文档标题变化。

## 最小追踪表

每个高风险项至少记录：

| 字段 | 说明 |
| --- | --- |
| Requirement ID | 需求编号 |
| Risk ID | 风险编号 |
| Design Control | 设计控制措施 |
| Test ID | 覆盖测试 |
| Observable ID | 状态、计数器、日志或 dump |
| Gate | 对应质量门禁 |
| Owner | 负责人 |
| Status | open / covered / verified / accepted |

`accepted` 必须有风险接受人和有效期。

## 状态定义

| 状态 | 含义 |
| --- | --- |
| open | 已识别但未覆盖 |
| designed | 有设计措施但未验证 |
| covered | 有测试覆盖但未完成验证 |
| verified | 测试通过且证据归档 |
| accepted | 风险被正式接受 |
| obsolete | 需求或风险已废弃 |

高风险发布项不能长期停留在 `open` 或 `designed`。

## 需求到风险

示例：

| Requirement | 风险 | 说明 |
| --- | --- | --- |
| REQ-UDS-001 支持固件刷写 | RISK-UDS-001 刷写中断变砖 | 断电、传输超时、镜像错误都可能导致不可启动 |
| REQ-TSN-001 实时流 p999 < 500 us | RISK-TSN-001 背景流导致尾延迟尖峰 | 队列映射或 Qbv 配置错误会破坏确定性 |
| REQ-SERDES-001 四路摄像头稳定运行 | RISK-SERDES-001 线束或 PoC 导致 lock drop | 现场振动和温度会降低链路裕量 |
| REQ-PMBUS-001 BMC 上报电源遥测 | RISK-PMBUS-001 数据格式误报过流 | Linear11、PAGE 和字节序错误会产生假告警 |
| REQ-USBDFU-001 支持现场 USB 升级 | RISK-USBDFU-001 镜像地址错误导致不启动 | 裸 bin 和缺少 metadata 会破坏回退 |

## 风险到设计控制

| Risk | Design Control |
| --- | --- |
| RISK-UDS-001 | Bootloader 防回滚、镜像校验、ISO-TP Flow Control 限速、断电恢复 |
| RISK-TSN-001 | VLAN PCP 到队列映射固定、Qbv GCL 版本化、PTP offset 监控 |
| RISK-SERDES-001 | PoC 网络按参考设计、lock drop 计数、线束裕量验证 |
| RISK-PMBUS-001 | raw word 和换算值同时记录、PAGE 显式传参、STATUS_WORD 联合判定 |
| RISK-USBDFU-001 | 镜像 header、Bootloader 写保护、应用确认标志、失败回退 DFU |

设计控制必须能被测试或观测，不可只写原则。

## 风险到测试

| Risk | Test | Evidence |
| --- | --- | --- |
| RISK-UDS-001 | TEST-UDS-TRANSFER-001 多 block Transfer Data | CAN trace、Bootloader flash log |
| RISK-UDS-001 | TEST-UDS-POWERLOSS-001 刷写中断电 | metadata dump、回退结果 |
| RISK-TSN-001 | TEST-TSN-QBV-001 背景满载 p999 延迟 | pcap、PTP offset、队列统计 |
| RISK-SERDES-001 | TEST-SERDES-CABLE-001 长线高温 lock drop | SerDes dump、PoC 波形、CSI error |
| RISK-PMBUS-001 | TEST-PMBUS-LINEAR-001 Linear11 换算对比 | raw word、外部仪表、STATUS_WORD |
| RISK-USBDFU-001 | TEST-DFU-HEADER-001 错地址镜像拒绝 | DFU log、metadata、Flash dump |

测试必须包含失败判定，而不只是成功路径。

## 风险到可观测性

| Risk | Observable | 字段 |
| --- | --- | --- |
| RISK-UDS-001 | OBS-UDS-TRANSFER | block_seq、fc_timeout、cf_timeout、flash_program_ms、last_nrc |
| RISK-TSN-001 | OBS-TSN-LATENCY | ptp_offset_max、p99_us、p999_us、queue_drop、gate_miss |
| RISK-SERDES-001 | OBS-SERDES-LINK | link_lock、lock_drop、remote_i2c_ok、csi_crc_error、poc_voltage |
| RISK-PMBUS-001 | OBS-PMBUS-TELEMETRY | page、status_word、read_iout_raw、read_iout_a、pec_error |
| RISK-USBDFU-001 | OBS-DFU-BOOT | image_addr、image_crc、boot_flag、confirm_flag、rollback_count |

没有可观测字段的风险很难在现场闭环。

## 故障案例到回归

每个故障案例关闭后必须补追踪。

| Failure Case | Root Cause | Regression Test | Observable |
| --- | --- | --- | --- |
| CASE-SERDES-LOCKDROP | PoC 和线束裕量不足 | TEST-SERDES-CABLE-001 | OBS-SERDES-LINK |
| CASE-TSN-LATENCY | 队列映射错误 | TEST-TSN-QBV-001 | OBS-TSN-LATENCY |
| CASE-UDS-TRANSFER | 工具忽略 STmin | TEST-UDS-TRANSFER-001 | OBS-UDS-TRANSFER |
| CASE-PMBUS-IOUT | Linear11 和 PAGE 错 | TEST-PMBUS-LINEAR-001 | OBS-PMBUS-TELEMETRY |
| CASE-USBDFU-BOOT | 镜像地址错误 | TEST-DFU-HEADER-001 | OBS-DFU-BOOT |

如果故障没有回归测试，后续版本很容易复发。

## 门禁追踪

| Gate | 必须覆盖 | 输入文档 | 输出证据 |
| --- | --- | --- | --- |
| G0 | 需求和风险 | `PROTOCOL_SELECTION.md` | 需求表、风险表 |
| G1 | 设计控制 | `REVIEW_CHECKLIST.md` | 评审记录、设计问题关闭 |
| G2 | 最小通信 | `MEASUREMENT_EXAMPLES.md` | 波形、抓包、bring-up log |
| G3 | 集成和错误路径 | `DEBUG_PLAYBOOK.md` | 协议 trace、错误计数 |
| G4 | 回归 | `REGRESSION_TEST_MATRIX.md` | 自动化结果、artifact |
| G5 | 量产 | `PRODUCTION_TEST.md` | 工位测试记录 |
| G6 | 发布 | `COMMUNICATION_QUALITY_GATE.md` | 发布报告、风险接受 |

每个 R3/R4 风险都应至少出现在 G3、G4 和 G6。

## 追踪矩阵模板

```markdown
| Req | Risk | Design | Test | Observable | Gate | Status | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-UDS-001 | RISK-UDS-001 | DES-UDS-BOOT-001 | TEST-UDS-TRANSFER-001 | OBS-UDS-TRANSFER | G4/G6 | verified | bootloader |
```

字段要求：

- `Req` 必须能追到需求来源。
- `Risk` 必须有影响和触发条件。
- `Design` 必须能被检查。
- `Test` 必须能自动或半自动执行。
- `Observable` 必须能在现场导出。
- `Gate` 必须说明在哪个阶段拦截。
- `Status` 必须定期更新。
- `Owner` 必须是具体团队或角色。

## 版本变更追踪

每次涉及通信的变更都要标记影响。

| 变更类型 | 需要更新 |
| --- | --- |
| 硬件改版 | Design、Test、Measurement、Production |
| 协议栈升级 | Risk、Test、Observable、Gate |
| 参数变更 | Requirement、Test、Production |
| 修复现场故障 | Failure Case、Regression Test、Observable |
| 添加新协议 | Requirement、Risk、Design、Test、Docs |
| 更换供应商 | Risk、Measurement、Production、Reliability |

没有更新追踪矩阵的通信变更，应视为发布风险。

## 审计检查清单

发布前抽查：

- 每个 R3/R4 风险是否有测试。
- 每个测试是否有证据 artifact。
- 每个现场故障是否有回归用例。
- 每个关键观测字段是否能远程导出。
- 每个风险接受是否有 owner 和有效期。
- 每个量产关键接口是否有工位测试。
- 每个升级链路是否有回滚和断电恢复验证。

## 最小落地路线

建议分阶段落地：

1. 先为 R4 风险建立追踪矩阵。
2. 再覆盖 R3 协议和现场故障。
3. 最后扩展到所有外部通信接口。

不要试图一次追踪所有细节。先把关键风险闭环做实。

## 延伸阅读

- `COMMUNICATION_QUALITY_GATE.md`
- `REGRESSION_TEST_MATRIX.md`
- `AUTOMATED_TEST_HARNESS.md`
- `COMMUNICATION_OBSERVABILITY.md`
- `FIELD_DIAGNOSTIC_RUNBOOK.md`
- `FAILURE_CASES.md`
