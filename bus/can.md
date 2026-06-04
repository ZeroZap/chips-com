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

## 延伸阅读

- `basic/can-phy.md`
- `bus/can-canopen-practical.md`
- `bus/can-canopen-deep-dive.md`
