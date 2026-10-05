# BACnet 主题总览

## 目标

BACnet 是楼宇自动化国际标准。本文是**总览导航**，围绕 BACnet 已经形成 3 篇专题笔记 + 1 篇实战案例。

## 主题地图

```text
chips-com/bus/bacnet-*.md
│
├── 速查层
│   ├── bacnet.md                1 页概念：对象、服务、BACnet/IP
│   └── bacnet-practical.md      报文示例 + 调试步骤
│
├── 原理层
│   └── bacnet-deep-dive.md      BVLC/NPDU/APDU 编码、MS/TP、BBMD
│
└── 实战层
    └── bacnet-failure-cases.md  20 个产线死机案例
```

## 5 种读者路径

### 路径 1：刚接触 BACnet

```text
1. bacnet.md            概念 + 对象 + 服务
2. bacnet-practical.md  Who-Is / Read / COV
3. bacnet-failure-cases.md 第 1-5 案例  UDP / APDU
```

### 路径 2：要做楼宇 BACS

```text
1. bacnet.md            协议定位
2. bacnet-practical.md  Who-Is / Browse / Read
3. bacnet-deep-dive.md  BVLC/NPDU/APDU + COV
4. bacnet-failure-cases.md 第 6-15 案例  COV / MS/TP
```

### 路径 3：要做 MS/TP 控制器

```text
1. bacnet-deep-dive.md  MS/TP 令牌环
2. bacnet-practical.md  MS/TP 调试
3. bacnet-failure-cases.md MS/TP 案例
```

### 路径 4：要做 BBMD 跨子网

```text
1. bacnet-deep-dive.md  BBMD 配置
2. bacnet-practical.md  Foreign Device
3. bacnet-failure-cases.md BBMD 案例
```

### 路径 5：要做 BACnet 设备发现

```text
1. bacnet-practical.md  Who-Is / I-Am
2. bacnet-deep-dive.md  NPDU 编码
3. bacnet-failure-cases.md 设备发现案例
```

## 主题速查矩阵

| 你想知道的事 | 文档位置 |
| --- | --- |
| BACnet 是啥 | bacnet.md §定位 |
| BACnet/IP | bacnet.md §BACnet/IP |
| BACnet MS/TP | bacnet.md §BACnet MS/TP |
| 对象模型 | bacnet.md §BACnet 对象模型 |
| 服务 | bacnet.md §BACnet 服务 |
| APDU 编码 | bacnet-deep-dive.md §APDU 详解 |
| COV 订阅 | bacnet-deep-dive.md §COV 订阅机制 |
| MS/TP 令牌环 | bacnet-deep-dive.md §MS/TP 详解 |
| BBMD | bacnet-deep-dive.md §BBMD 跨子网 |
| 主站实现 | bacnet-deep-dive.md §工程实现 |
| 16 个常见故障 | bacnet-deep-dive.md §现场常见故障 |
| 20 个产线死机案例 | bacnet-failure-cases.md |

## BACnet vs Modbus vs OPC UA

| 维度 | BACnet | Modbus | OPC UA |
| --- | --- | --- | --- |
| 应用 | 楼宇 | 工业 | 工业 4.0 |
| 物理 | UDP / RS485 | TCP / 串行 | TCP / HTTPS |
| 数据模型 | 对象 | 寄存器 | 地址空间 |
| 信息建模 | 标准 LN | 无 | 行业 Companion |
| 安全 | BACnet/SC | 无 | Sign + Encrypt |
| 国内 | 不支持 | 通用 | 拓展中 |

## 选型决策树

```text
楼宇 / 智慧城市立项
├── 楼宇 HVAC / 照明
│   └── BACnet（首选）
├── 工业 IoT
│   └── OPC UA / MQTT
└── 楼宇边缘网关
    └── BACnet + MQTT
```

## 实战检查清单

```text
- UDP 端口 47808 已开（BACnet/IP）
- BVLC 编码正确
- NPDU 编码正确
- APDU 编码正确
- Device 对象存在
- AI/AO/BI/BO 对象模型完整
- ReadProperty / ReadPropertyMultiple 支持
- WriteProperty 支持
- SubscribeCOV 支持
- COV_Increment 配置
- Who-Is / I-Am 支持
- BBMD 配置（如跨子网）
- MS/TP 令牌环（RS485 场景）
```

## 延伸阅读

- `bus/rtu-protocols.md`：RTU 设备协议全集
- `bus/modbus.md`：与 Modbus 对比
- `bus/opcua.md`：与 OPC UA 对比
- `bus/bacnet-failure-cases.md`：20 个产线死机案例库

## 版本演进

```text
BACnet 1.0: 1995
BACnet 2016: 当前
ISO 16484-5: 国际标准
```