# CAN

## 定位

CAN 是 Controller Area Network，常用于车载、工业控制、电机、BMS 和机器人。

核心特点：

- 多主。
- 广播。
- ID 仲裁。
- 差分信号。
- 强错误检测。
- 适合实时控制。

## ID 与仲裁

CAN ID 通常表示消息含义，不是简单设备地址。

ID 越小，优先级通常越高。

多个节点同时发送时，CAN 通过显性/隐性位完成非破坏性仲裁。

## 帧类型

常见：

```text
标准帧：11-bit ID
扩展帧：29-bit ID
CAN FD：数据区可到 64 字节
```

经典 CAN 单帧最多 8 字节数据。

## 物理层

CAN 需要 CAN 收发器连接 `CANH/CANL`。

总线两端通常各有 120Ω 终端。

## 相关规范

CAN 涉及的标准从物理层一直排到法规，完整总表见 `bus/automotive/can-standards-map.md`。核心几项：

| 层 | 标准 | 作用 |
| --- | --- | --- |
| 数据链路 | **ISO 11898-1** | 核心标准。经典 CAN / CAN FD / CAN XL 三代帧格式、仲裁、错误处理 |
| 数据链路 | Bosch CAN Spec 2.0 (1991) | 原始规范，业界引用基准 |
| 物理 | **ISO 11898-2** | 高速差分物理层、终端电阻、位时序电气特性、唤醒 |
| 物理 | ISO 11898-6 | 高速低功耗变体 |
| 物理 | ISO 11898-3 / ISO 11519 | 低速容错 CAN（线断可继续通信） |
| 物理 | ISO 14950-2 | 单线 CAN 兼容物理层（TJA1050） |
| 物理 | SAE J2284-1 ~ -4 | 北美体系下的 CAN 物理层 |
| 一致性 | ISO 16845-1 / -2 | 一致性测试方法学与测试计划 |
| 环境 | ISO 16750-1 ~ -5 | 环境条件与试验（电气/机械/气候/化学负荷） |
| EMC | ISO 7637-2、ISO 10605、CISPR 25、ISO 11452 | 瞬态干扰、ESD、发射、辐射抗扰度 |
| 安全 | ISO 26262、ISO/SAE 21434、UNECE R155/R156 | 功能安全、网络安全、软件更新合规 |

### 三代数据链路

| 代 | 数据场 | 速率 | 标准 |
| --- | --- | --- | --- |
| CAN CC | 1–8 字节 | ≤ 1 Mbit/s | ISO 11898-1 |
| CAN FD | 1–64 字节 | 数据段可加速 | ISO 11898-1（:2015 起） |
| CAN XL | 1–2048 字节 | > 10 Mbit/s | ISO 11898-1:2024 |

### 物理层选型

| 需求 | 物理层 | 典型收发器 |
| --- | --- | --- |
| 经典高速 | ISO 11898-2 | TJA1050、SN65HVD230、TCAN1042 |
| 低功耗 | ISO 11898-6 | TJA1051/T/3、TJA1041/T/3 |
| 5V 供电 | ISO 11898-2 | TJA1443 |
| CAN FD | ISO 11898-2 | TJA1044、TCAN1044 |
| 振铃抑制 | ISO 11898-2 + CiA 601-4 | SIC 收发器 |
| 低速容错 | ISO 11898-3 / ISO 11519 | TJA1021/T/3 |

终端电阻：总线两端各 120Ω，断电测 CANH-CANL 约 60Ω。

## 延伸阅读

- `basic/can-phy.md`
- `bus/automotive/canopen-practical.md`
- `bus/automotive/canopen-deep-dive.md`
- `bus/automotive/can-standards-map.md` — CAN 家族标准规范总表
- `bus/automotive/can-protocol-family.md` — CAN 家族协议全景
- `bus/automotive/can-fd-failure-cases.md`（CAN FD / CAN XL 产线实战案例：位定时 / 采样点 / BRS / TDC / CRC-17；2026 增 15 案例：装车 TDC / S32K SSP / Daimler 铰接巴士 / 50m 长距离 / 4 层定位 / VCC 跌落 / 400ns 边沿 $15K 幻影保修 / 4 大 killer lab 通产线崩 / Ford 438 万辆 ITRM 召回 / SN65HVD234 4% 失效率 RS pin silent mode / TDCO 指纹 bit 24/28 + 装车 / 模块化插卡 120Ω 并联 + 万用表 SOP / **STM32H5 FDCAN + 收发器 4 模式原子切换** / **TEC/REC 阈值 + REC↑=EMC/TEC↑=硬件 + FreeRTOS 监控模板** / **STM32 FDCAN 硬件 CRC 含位填充 vs 软件不含 + UDS 时序 + 量产 SOP 4 类验证清单**）
