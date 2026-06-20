# Ethernet TSN Practical Guide

## 目标

本文面向第一次调试 TSN 网络的工程场景，重点覆盖时间同步、队列调度、交换机配置、端系统配置、Linux 工具入口、抓包验证和常见不确定延迟问题定位。

TSN 不是单一协议，也不是打开一个开关就能得到确定性实时网络。TSN 调试必须同时确认端系统、交换机、时间同步、队列、调度表、流量分类和测量方法。

## 先明确边界

开始前先回答：

- 需要多低的端到端延迟。
- 允许多大的抖动。
- 是周期控制流、音视频流还是普通优先级流。
- 网络中哪些交换机和端系统支持 TSN。
- 使用哪些 TSN 特性，而不是笼统说“支持 TSN”。
- 是否需要与 PROFINET、EtherNet/IP、OPC UA PubSub 或自定义 UDP 联合使用。

常见误区：

```text
普通千兆以太网低延迟 != TSN 确定性
PTP 时间同步正常 != 调度确定性正常
交换机支持 TSN != 端系统驱动已正确配置
实验室单跳成功 != 现场多跳一定稳定
```

## 常见 TSN 能力

工程中常见能力方向：

| 能力 | 常见标准方向 | 作用 |
| --- | --- | --- |
| 时间同步 | 802.1AS / gPTP | 全网统一时间基准 |
| 时间感知调度 | 802.1Qbv | 按时间窗口开关队列门控 |
| 信用整形 | 802.1Qav | 平滑音视频或周期流量 |
| 帧抢占 | 802.1Qbu / 802.3br | 允许高优先级帧打断低优先级大帧 |
| 流过滤监管 | 802.1Qci | 限制异常流量影响确定性流 |
| 冗余 | 802.1CB | 复制和消除帧，提高可靠性 |

不是每个项目都需要全部能力。先从时间同步和队列分类做起，再逐步引入 Qbv、Qav 或 Qbu。

## 最小实验拓扑

建议先用最小拓扑：

```text
Talker ---- TSN Switch ---- Listener
```

准备：

- Talker 支持硬件时间戳或至少支持稳定发包。
- Listener 支持硬件时间戳或高精度收包时间记录。
- Switch 明确支持所需 TSN 特性。
- 三端的网口速率和双工固定或协商稳定。
- 使用独立测试网络，避免 IT 网络广播和未知流量干扰。

第一阶段不要一上来多交换机、多流、多协议混跑。先验证单流、单跳、固定周期。

## 时间同步

TSN 的基础是统一时间。

常见路径：

```text
Grandmaster Clock
        |
TSN Switch / Boundary / Transparent behavior
        |
Talker / Listener
```

检查项：

- 是否选出正确 Grandmaster。
- 每个节点是否进入同步状态。
- Offset 是否稳定。
- Path Delay 是否稳定。
- 网卡或交换机是否使用硬件时间戳。
- PTP domain、profile、priority 是否一致。

Linux 常用工具入口：

```text
ptp4l
phc2sys
pmc
ethtool -T
```

调试顺序：

1. 用 `ethtool -T` 确认网卡时间戳能力。
2. 启动 `ptp4l`，确认端口状态。
3. 用 `pmc` 查看 Grandmaster 和 offset。
4. 用 `phc2sys` 同步系统时钟和 PHC，按需求配置方向。
5. 记录 offset 长时间稳定性，而不是只看某一瞬间。

如果时间同步不稳定，先不要调 Qbv 调度表。

## 流量分类

TSN 调度依赖流量分类。

常见分类依据：

- VLAN PCP。
- 目的 MAC。
- 源 MAC。
- EtherType。
- IP DSCP。
- UDP 端口。
- Stream ID，取决于设备和交换机能力。

建议：

- 为实时流使用独立 VLAN 或明确 PCP。
- 普通流和实时流分开队列。
- 所有交换机端口映射一致。
- 文档记录每条流的分类规则。

常见问题：
- Talker 没打 VLAN tag。
- PCP 值被中间设备改写。
- 交换机入口队列映射和出口队列映射不一致。
- 测试工具发出的帧和实际应用帧分类不同。

## Qbv 时间感知调度

Qbv 通过 Gate Control List 控制队列在不同时间窗口是否允许发送。

简化模型：

```text
周期 T
窗口 A：只允许实时队列发送
窗口 B：允许普通队列发送
窗口 C：保护带或其他队列
```

关键参数：

- Base Time。
- Cycle Time。
- Gate Control List。
- 队列到 gate 的映射。
- 每个窗口时长。
- Guard Band。

调试步骤：

1. 确认全网时间同步稳定。
2. 确认实时流进入预期队列。
3. 配置简单两窗口调度表。
4. 设置 Base Time 在未来时间点。
5. 观察实时流延迟和抖动。
6. 增加背景流量，确认实时流不被明显影响。
7. 多跳场景逐跳调整调度窗口和传播延迟预算。

常见错误：

| 现象 | 优先检查 |
| --- | --- |
| 调度表不生效 | Base Time、队列映射、端口方向、硬件支持 |
| 周期性丢包 | 窗口太短、帧长度超预算、Guard Band 不够 |
| 多跳后抖动变大 | 各交换机时间同步、窗口偏移、路径延迟预算 |
| 普通流饿死 | 调度表不给普通队列足够窗口 |

## Qav 信用整形

Qav 适合平滑特定优先级流量，常见于音视频或周期流。

关注参数：

- Idle Slope。
- Send Slope。
- Hi Credit。
- Lo Credit。
- 队列带宽分配。

工程直觉：

- Qav 不是严格按时间窗口发送。
- 它更像带宽和突发控制。
- 适合降低抖动和避免突发影响。
- 不等同于 Qbv 的时间确定性调度。

如果项目要求严格固定发送时刻，优先看 Qbv；如果项目主要要求平滑和带宽保障，可以评估 Qav。

## Qbu / 帧抢占

帧抢占允许高优先级 express frame 打断低优先级 preemptable frame。

工程意义：

- 减少高优先级帧等待低优先级大帧发送完成的时间。
- 降低 Guard Band 需求。
- 提升高优先级流的最坏延迟表现。

检查项：

- MAC 是否支持帧抢占。
- PHY / 交换机是否支持相关能力。
- 链路两端是否协商成功。
- 哪些队列是 express，哪些是 preemptable。
- 抢占统计计数是否变化。

帧抢占是链路两端协同能力，不是单端配置即可生效。

## Linux 端系统配置入口

不同内核、网卡和驱动支持差异很大。

常见入口：

```text
tc qdisc taprio
tc qdisc cbs
tc qdisc mqprio
tc filter
ethtool -T
ethtool -S
ip link
ptp4l / phc2sys / pmc
```

典型思路：

1. 用 `mqprio` 或驱动配置队列数量和优先级映射。
2. 用 VLAN PCP 或 filter 把实时流映射到目标队列。
3. 用 `taprio` 配置 Qbv 调度。
4. 用 `cbs` 配置 Qav 信用整形，视项目需要。
5. 用 `ethtool -S` 查看网卡队列和错误计数。
6. 用硬件时间戳或应用日志测端到端延迟。

注意：

- 命令能执行不代表硬件真的 offload。
- software qdisc 只能验证概念，确定性能力通常需要硬件支持。
- 驱动、网卡、内核版本和交换机固件都要纳入版本记录。

## 交换机配置

TSN 交换机配置要记录：

- 端口角色。
- VLAN 和 PCP 映射。
- 队列数量和优先级映射。
- PTP / gPTP 角色。
- Qbv 调度表。
- Qav 参数。
- 帧抢占配置。
- 流过滤规则。
- 固件版本。

多交换机场景额外关注：

- 每跳传播延迟。
- 每跳调度窗口偏移。
- 时间同步路径。
- 链路故障恢复时间。
- 冗余路径是否影响时延。

## 测试流设计

至少准备三类流：

| 流量 | 目的 |
| --- | --- |
| 实时流 | 验证目标延迟和抖动 |
| 背景流 | 制造拥塞和干扰 |
| 管理流 | 验证 PTP、配置和监控不被误伤 |

测试维度：

- 无背景流时延迟。
- 满背景流时延迟。
- 单跳和多跳差异。
- Qbv 开关前后差异。
- 时间同步异常时表现。
- 链路断开恢复后表现。

不要只测平均延迟。TSN 更关注最坏延迟、抖动和异常恢复。

## 抓包和测量

Wireshark 可观察：

```text
ptp
eth.type == 0x88f7
vlan
eth.addr == <talker-mac>
udp.port == <test-port>
```

重点看：

- PTP 报文是否稳定。
- VLAN tag 和 PCP 是否正确。
- 实时流周期是否稳定。
- 背景流是否进入普通队列。
- 是否出现突发和周期性丢帧。

测量建议：

- 优先使用硬件时间戳。
- Talker 和 Listener 记录同一时钟域下时间戳。
- 统计 min、max、p99、p999 和丢包率。
- 长时间运行，至少覆盖温度、负载和链路恢复场景。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| 时间同步不稳定 | Grandmaster、PTP profile、硬件时间戳、交换机支持 |
| Qbv 不生效 | Base Time、Cycle Time、队列映射、offload、端口方向 |
| 延迟偶发尖峰 | 背景流分类、Guard Band、帧抢占、交换机队列 |
| 多跳后抖动变大 | 每跳调度偏移、路径延迟、时钟同步、链路速率 |
| 配置重启后丢失 | 交换机保存配置、Linux 启动脚本、驱动初始化顺序 |
| 实时流被普通流影响 | PCP/DSCP 映射、VLAN、队列调度、入口过滤 |
| 抓包看不到关键流 | 抓包点错误、端口镜像、硬件卸载、VLAN 过滤 |

## 实战检查清单

- Talker、Listener、Switch 都明确支持所需 TSN 特性。
- `ethtool -T` 或厂商工具确认时间戳能力。
- PTP/gPTP offset 长时间稳定。
- 实时流 VLAN/PCP/队列映射正确。
- Qbv Base Time 设置在未来，Cycle Time 和窗口正确。
- 背景流不会进入实时队列。
- 多跳路径每跳窗口和延迟预算明确。
- 使用硬件时间戳或可信测量方法统计最坏延迟。
- 配置、固件、驱动、内核和交换机版本已记录。
- 断链、重启、Grandmaster 切换后能恢复到预期状态。

## 与工业以太网协议的关系

TSN 提供确定性以太网能力，但不直接定义设备对象模型。

PROFINET、EtherNet/IP、OPC UA PubSub 或自定义 UDP 可以利用 TSN 网络能力，但仍需要各自的应用协议、工程模型和诊断体系。

调试时要分清：

```text
TSN 问题：时间同步、队列、调度、流量分类
应用协议问题：设备模型、连接、数据映射、诊断状态
```

## 延伸阅读

- `bus/ethernet-tsn.md`
- `bus/ethernet-deep-dive.md`
- `basic/ethernet-phy.md`
- `bus/profinet-deep-dive.md`
- `bus/ethernet-ip-deep-dive.md`
- `bus/industrial-ethernet-comparison.md`
