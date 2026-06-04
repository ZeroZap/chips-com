# Ethernet PHY

## 定位

Ethernet PHY 是以太网物理层芯片，用于把 MAC 的数字接口转换为网线上的差分信号。

典型结构：

```text
MCU/SoC MAC <-> PHY <-> Magnetics <-> RJ45 <-> Cable
```

很多 MCU 只有 MAC，没有内置 PHY。

## MAC-PHY 接口

常见接口：

```text
MII
RMII
RGMII
SGMII
```

MCU 10/100M 常见 `RMII`。

千兆常见 `RGMII`。

## MDIO / MDC

MAC 通过 MDIO/MDC 管理 PHY。

可读取：

- PHY ID。
- Link 状态。
- 协商速率。
- 双工模式。

MDIO 不通时，软件通常识别不到 PHY。

## 磁性器件

RJ45 接口通常需要网络变压器或 MagJack。

注意：

```text
RJ45 不是 PHY
MagJack 也不是 PHY
```

## 常见错误

| 现象 | 优先检查 |
| --- | --- |
| Link 不亮 | PHY 电源、复位、时钟、磁性器件、网线 |
| MDIO 读不到 | PHY 地址、MDC、MDIO 上拉、复位 |
| 速率异常 | 自协商、线缆、PHY 配置 |
| 千兆不稳定 | RGMII delay、阻抗、PCB 时序 |

## 延伸阅读

- `bus/ethernet-deep-dive.md`
- `bus/ethernet-modbus-tcp-practical.md`
