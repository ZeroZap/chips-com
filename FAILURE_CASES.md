# Failure Cases

## 目标

本文收集典型通信故障案例，用“现象 -> 排查 -> 根因 -> 修复”的方式沉淀经验。

## I2C 高速偶发 NACK

现象：

```text
100 kHz 稳定，400 kHz 偶发 NACK
```

排查：

- 示波器观察 SCL/SDA 上升沿。
- 检查上拉电阻和挂载设备数量。
- 检查电平转换器型号。

根因：

```text
总线电容较大，上拉过弱，上升沿不满足 Fast-mode 时序。
```

修复：

- 将上拉从 10k 调整到 2.2k/4.7k。
- 降低速率。
- 减少总线电容或分段。

## SPI Flash Fast Read 数据偏移

现象：

```text
0x03 普通读正常，0x0B Fast Read 数据错位
```

排查：

- 逻辑分析仪检查 command/address/dummy。
- 对比 Flash 手册 dummy cycle 要求。

根因：

```text
Fast Read 少发送 8 个 dummy clocks。
```

修复：

- 按手册补足 dummy cycle。
- 不同频率下确认 dummy cycle 配置。

## RS485 最后字节丢失

现象：

```text
Modbus RTU 响应 CRC 偶发错误，最后字节异常
```

排查：

- 逻辑分析仪同时观察 UART TX 和 DE。
- 检查发送完成判断条件。

根因：

```text
软件等待 TXE 后关闭 DE，移位寄存器最后停止位未发完。
```

修复：

- 等待 UART TC 标志后再关闭 DE。

## CAN 单节点一直 ACK Error

现象：

```text
CAN 控制器发送失败，错误计数增加
```

排查：

- 检查总线上是否有其他正常节点。
- 用 CAN 分析仪接入并开启 ACK。

根因：

```text
总线上只有一个发送节点，没有任何节点应答 ACK。
```

修复：

- 接入第二个 CAN 节点或 CAN 分析仪。
- 确认波特率一致。

## USB CDC 枚举成功但无输出

现象：

```text
设备管理器显示虚拟串口，但串口工具无日志
```

排查：

- 检查 Host 是否打开端口。
- 检查 DTR 状态。
- 检查 CDC Bulk IN 是否发送。

根因：

```text
固件等待 DTR 后才输出，串口工具未拉起 DTR。
```

修复：

- 修改串口工具设置。
- 固件区分调试日志和 DTR 控制策略。

## Ethernet ping 不通但 Link 正常

现象：

```text
网口 Link LED 亮，ping 不通
```

排查：

- Wireshark 看 ARP。
- 检查 IP/Mask。
- 检查 MAC 地址是否重复。

根因：

```text
静态 IP 与 PC 不在同一网段。
```

修复：

- 修正 IP 和子网掩码。
- 或配置正确网关。

## MIPI 屏背光亮但黑屏

现象：

```text
背光亮，屏幕无图
```

排查：

- 检查 DSI 初始化命令。
- 检查 Sleep Out 和 Display On。
- 检查 Video Mode 时序。

根因：

```text
只打开了背光，Panel 未完成 DSI 初始化。
```

修复：

- 按屏厂初始化表发送完整命令。
- 确认延时满足手册。

## PCIe 枚举不到设备

现象：

```text
lspci 看不到 Endpoint
```

排查：

- 查看 LTSSM 状态。
- 检查 PERST# 和 REFCLK。
- 检查 Lane TX/RX 方向。

根因：

```text
PERST# 释放过早，Endpoint 电源尚未稳定。
```

修复：

- 调整复位时序。
- 确保 REFCLK 和电源稳定后释放 PERST#。
