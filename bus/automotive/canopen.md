---
tags:
  - layer/bus
  - type/overview
  - protocol/canopen
  - topic/automotive
---

# CANopen

## 定位

CANopen 是建立在 CAN 上的工业通信协议，常用于运动控制、IO 模块、编码器和工业设备。

它在 CAN 之上定义：

- 对象字典。
- Node ID。
- SDO。
- PDO。
- NMT。
- Heartbeat。
- Emergency。
- EDS。

## 对象字典

对象通过：

```text
Index + Sub-index
```

定位。

电机驱动常见对象：

```text
6040h Controlword
6041h Statusword
6060h Operation Mode
607Ah Target Position
6064h Actual Position
```

## SDO 和 PDO

SDO：

```text
配置和低频访问对象字典
一问一答
```

PDO：

```text
实时过程数据
无一问一答
需要预先映射
```

## 相关规范

CANopen 的标准全部由 **CiA（CAN in Automation）** 发布，不走 ISO：

| 标准 | 作用 |
| --- | --- |
| **CiA 301** | 核心标准。CANopen 应用层与通信 Profile（对应 EN 50325-4） |
| CiA 1301 | CANopen FD 应用层（USDO 替代 SDO，支持 64 字节） |
| CiA 1302-1 / -2 | CANopen FD 附加应用层（2026-08 CiA 公告已定稿） |
| CiA 402 | 驱动与运动控制设备 Profile（电机状态机） |
| CiA 401 | 通用 I/O 设备 Profile |
| CiA 404 ~ 434 | 各类设备接口 Profile（编码器、模拟量、数字量、限位、位置等） |
| CiA 302 | CANopen 附加应用层功能 |
| CiA 304 | CANopen Safety（对应 EN 50325-5） |
| CiA 305 | LSS（Layer Setting Services，节点地址与波特率自动配置） |
| CiA 306 | EDS 电子数据表格式 |
| CiA 1311 | XDD 描述文件格式 |
| CiA 510 | CANopen → J1939 PGN 映射 |

**下层依赖**：

```text
CANopen (CiA 301)
└── CAN FD / 经典 CAN  (ISO 11898-1, ISO 11898-2)
```

**环境与安全**（按场景选）：工业现场看 ISO 16750 / ISO 26262；车载场景还需 ISO/SAE 21434 与 UNECE R155/R156。

## 延伸阅读

- `bus/automotive/canopen-practical.md`
- `bus/automotive/canopen-deep-dive.md`
- `bus/automotive/canopen-failure-cases.md`
- `bus/automotive/canopen-safety.md` — CANopen Safety（CiA 304 / EN 50325-5，SRDO 功能安全扩展）
- `bus/automotive/can-standards-map.md` — CAN 家族标准规范总表
