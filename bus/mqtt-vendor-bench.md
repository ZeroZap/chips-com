# MQTT 主流云厂商 / Broker 对标

## 定位

MQTT 是 IoT / 工业物联网通讯的事实标准。本文梳理 MQTT Broker（云厂商与开源版）+ 工业 MQTT 集成方案。

> 说明：本文档基于公开资料整理，**具体产品 / 规格 / 价格请以厂商官网为准**。

## 海外云厂商

### AWS IoT

| 能力 | 说明 |
| --- | --- |
| MQTT Broker | ✅ AWS IoT Core |
| 通信协议 | MQTT 3.1.1 + 5.0 |
| TLS | ✅ TLS 1.2 / 1.3 |
| X.509 证书 | ✅ |
| 身份认证 | X.509 / Cognito / IAM |
| 规则引擎 | ✅ SQL 规则 |
| Sparkplug B | ⚠️ 部分（需要第三方） |
| QoS 0/1/2 | ✅ |
| 消息保留 | ✅ |
| Session 持久化 | ✅ |

### Microsoft Azure IoT

| 能力 | 说明 |
| --- | --- |
| MQTT Broker | ✅ IoT Hub |
| 通信协议 | MQTT 3.1.1 |
| TLS | ✅ TLS 1.2 |
| SAS 令牌 | ✅ |
| X.509 证书 | ✅ |
| DPS（设备预配） | ✅ |
| 数字孪生（DTDL） | ✅ |
| 规则引擎 | ✅ Azure Stream Analytics |
| IoT Edge | ✅ 本地计算 |

### Google Cloud IoT（已停服）

```text
Google Cloud IoT Core 已于 2023 年停服。
替代方案：与合作伙伴（如 ClearBlade / HiveMQ）集成。
```

## 国内云厂商

### 阿里云 IoT 平台

| 能力 | 说明 |
| --- | --- |
| MQTT Broker | ✅ 物联网平台（LinkKit） |
| 通信协议 | MQTT 3.1.1 + 5.0 |
| TLS | ✅ TLS / DTLS |
| 设备认证 | 一机一密 / X.509 |
| 物模型 | ✅ TSML（类似 DTDL） |
| 规则引擎 | ✅ SQL 规则 |
| 阿里云 LinkEdge | ✅ 边缘计算 |

### 华为云 IoT

| 能力 | 说明 |
| --- | --- |
| MQTT Broker | ✅ IoTDA |
| 通信协议 | MQTT 3.1.1 + 5.0 |
| TLS | ✅ |
| 设备认证 | X.509 / 一机一密 |
| 物模型 | ✅ |
| 规则引擎 | ✅ |
| IoT Edge | ✅ 边缘计算 |

### 腾讯云 IoT Explorer

| 能力 | 说明 |
| --- | --- |
| MQTT Broker | ✅ IoT Explorer |
| 通信协议 | MQTT 3.1.1 + 5.0 |
| TLS | ✅ |
| 设备认证 | X.509 / 一机一密 |
| 物模型 | ✅ |
| 规则引擎 | ✅ |
| IoT Explorer Edge | ✅ |

### 百度云 IoT

| 能力 | 说明 |
| --- | --- |
| MQTT Broker | ✅ IoT Hub |
| 通信协议 | MQTT 3.1.1 |
| TLS | ✅ |
| 设备认证 | 一机一密 |
| 物模型 | ✅ |

## 开源 Broker

| 项目 | 特点 | 适用 |
| --- | --- | --- |
| **EMQX** | 高性能、企业级 | IoT 平台 |
| **HiveMQ** | 企业级、Java | 工业 MQTT |
| **Mosquitto** | 轻量、C | 小型 / 边缘 |
| **RabbitMQ MQTT** | 通用 | 中小型 |
| **VerneMQ** | 高可用、Elixir | 大规模 |
| **ActiveMQ Artemis** | 通用 | 中小型 |
| **Bevywise MQTT Broker** | 商业 | 工业 |

## 工业 MQTT 集成方案

### Sparkplug B

```text
Sparkplug B 优势：
- 工业标准定义
- 自动状态管理（NBIRTH / DBIRTH / NDATA / DDATA / NDEATH / DDEATH）
- 时戳 + 序列号
- 多客户端兼容

主流厂商支持：
- Inductive Automation（Ignition）
- Cirrus Link Solutions
- HiveMQ（插件）
- EMQX（插件）
- AWS IoT Core（Sparkplug B 适配）
- Azure IoT（第三方集成）

国内支持：
- 阿里云 IoT 平台：原生支持 Sparkplug B（2023+）
- 华为云 IoT：原生支持
- 腾讯云 IoT Explorer：原生支持
```

### MQTT 5.0 新特性

```text
新特性：
- Properties（用户属性 + 主题别名 + 响应主题）
- Reason Codes：响应请求码
- 流控（Receive Maximum）
- 消息过期
- 主题别名
- 共享订阅（Share Subscriptions）
- 离线消息队列优化

主流厂商支持：
- AWS IoT Core：✅ 完整
- 阿里云 IoT：✅
- 华为云 IoT：✅
- EMQX 5.x：✅ 完整
- HiveMQ 4.x：✅ 完整
- Mosquitto 2.x：✅ 完整
```

## MQTT + 工业协议集成

```text
Modbus RTU + MQTT：
- libmodbus + paho-mqtt
- 网关实现

OPC UA + MQTT：
- OPC UA Companion Specs
- 工业云平台对接

DNP3 + MQTT：
- 北美 SCADA + 工业云

IEC 104 + MQTT：
- 电力 + 工业云
```

## 选型决策

```text
MQTT Broker 选择
├── 国内 IoT 项目
│   ├── 阿里云 IoT 平台（首选）
│   ├── 华为云 IoT（首选）
│   ├── 腾讯云 IoT Explorer
│   └── 自建 EMQX（私有云）
├── 海外 IoT 项目
│   ├── AWS IoT Core（首选）
│   ├── Azure IoT Hub
│   └── 自建 HiveMQ / VerneMQ
├── 工业云（Sparkplug B）
│   ├── AWS IoT Core + Sparkplug
│   ├── EMQX + HiveMQ
│   └── Inductive Ignition（工业 SCADA）
├── 边缘计算
│   ├── AWS IoT Greengrass
│   ├── Azure IoT Edge
│   ├── 阿里云 LinkEdge
│   └── 华为云 IoT Edge
└── 小型 / 边缘
    └── Mosquitto
```

## 选型要点

```text
1. MQTT 5.0 支持（推荐）
3. TLS 加密（必备）
5. X.509 证书认证
7. QoS 0/1/2 支持
11. 规则引擎
13. Sparkplug B 工业支持（工业项目）
15. 私有化部署（数据本地化）
17. 一致性测试报告
```

## 行业大厂关键产品

```text
AWS IoT Core：
- 业界最成熟 IoT 平台
- 全球部署
- 与 AWS Lambda / S3 / DynamoDB 集成

EMQX：
- 企业级 MQTT Broker
- 私有化部署
- Sparkplug B 插件

Inductive Ignition：
- 工业 SCADA + MQTT
- Sparkplug B 原生支持
- MES / Historian 集成
```

## 延伸阅读

- `bus/mqtt.md`：MQTT 协议
- `bus/modbus-rtu-mqtt-gateway.md`：Modbus RTU ↔ MQTT 网关
- `bus/hj212-mqtt-gateway.md`：HJ 212 ↔ MQTT 网关