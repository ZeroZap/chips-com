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

## 延伸阅读

- `bus/can-canopen-practical.md`
- `bus/can-canopen-deep-dive.md`
