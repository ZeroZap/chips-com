---
tags:
  - layer/bus
  - type/gateway-design
  - protocol/modbus
  - topic/industrial
---

# Modbus RTU ↔ MQTT 网关

## 定位

本文是 Modbus RTU 转 MQTT（IoT 云协议）的网关设计文档。这是工业 IoT 场景的常用网关：现场 Modbus RTU 设备通过 RTU 网关转 MQTT 上云。

## 场景

```text
现场设备（Modbus RTU）：
  - PLC、变频器、传感器、智能仪表
  - 标准 Modbus RTU
  - RS485 总线

上行云平台（MQTT）：
  - AWS IoT / Azure IoT / 阿里云 IoT / 自建 EMQX
  - 标准 MQTT 3.1.1 或 5.0
  - TLS 加密
```

## 数据流

```text
1. 网关按配置轮询现场设备（Modbus Master）
   - 保持寄存器、线圈、输入寄存器

2. 解析 → 内部 Point 模型
   - 时戳、品质、单位

3. 上行 MQTT（JSON / Sparkplug B / 自定义）
   - Topic：device/{device_id}/point/{point_id}
   - Payload：{"value": 23.5, "unit": "V", "ts": 1728000000}

4. 下行 MQTT
   - Topic：device/{device_id}/cmd/{cmd_id}
   - Payload：{"command": "set", "point_id": 1, "value": 50.0}
   - 网关解析 → Modbus 写入
```

## MQTT Topic 设计

```text
上行数据（设备 → 云）：
  device/{device_id}/point/{point_id}        # 单点数据
  device/{device_id}/telemetry               # 批量遥测
  device/{device_id}/event                   # 事件（告警 / 故障）
  device/{device_id}/status                  # 设备状态

下行命令（云 →设备）：
  device/{device_id}/cmd/{cmd_id}            # 单命令
  device/{device_id}/config                   # 配置更新
  device/{device_id}/firmware                # 固件升级

下行响应（设备 → 云）：
  device/{device_id}/cmd/{cmd_id}/ack        # 命令应答
  device/{device_id}/config/ack              # 配置应答
```

## Payload 格式（JSON）

```json
{
  "device_id": "PLC_1",
  "point_id": 5,
  "name": "voltage_a",
  "value": 220.1,
  "quality": "Good",
  "timestamp": 1728000000,
  "unit": "V"
}
```

## 数据转换

```text
Modbus 寄存器：
  保持寄存器 0x0001 = 0x4248（16-bit）
  实际为 float 高 16-bit
  寄存器 0x0002 = 0x0000（低 16-bit）
  float = 0x42480000 = 50.0

内部 Point：
  ID 5, type=AI_Float, value=50.0, unit=V

MQTT Payload：
  {"value": 50.0, "unit": "V", "quality": "Good", "ts": 1728000000}
```

## 命令下行

```text
云平台下发（MQTT）：
  Topic：device/PLC_1/cmd/set_voltage
  Payload：{"command": "write", "point_id": 5, "value": 75.0}

网关转换：
  Modbus Write Holding Register 0x0001 = 50.0（IEEE 754）
  
  字节序转换：75.0 = 0x42960000
    寄存器 0x0001 = 0x4296
    寄存器 0x0002 = 0x0000

MQTT 应答：
  Topic：device/PLC_1/cmd/set_voltage/ack
  Payload：{"result": "OK"}
```

## TLS 安全

```text
TLS 双向认证：
  - 客户端证书（设备）
  - 服务器证书（MQTT broker）

TLS 服务器认证：
  - 设备只认证 broker 证书（简化）

证书管理：
  - CA 证书预置
  - 客户端证书烧录
  - 定期更新
```

## Sparkplug B（工业 MQTT 标准）

```text
Sparkplug B 优势：
  - 工业标准定义
  - 自动状态管理（NBIRTH / DBIRTH / NDATA / DDATA / NDEATH / DDEATH）
  - 时戳 + 序列号
  - 多客户端兼容

Topic 结构：
  spBv1 / <group_id> / <message_type> / <edge_node_id> / <device_id>

消息类型：
  NBIRTH：节点出生
  DBIRTH：设备出生
  NDATA：节点数据
  DDATA：设备数据
  NDEATH：节点死亡
  DDEATH：设备死亡
```

## 配置示例（YAML）

```yaml
mqtt:
  broker: tls://broker.example.com:8883
  client_id: gateway_001
  username: gateway
  password: ${SECRET}
  keepalive: 60
  qos: 1
  
tls:
  ca_cert: /etc/certs/ca.pem
  client_cert: /etc/certs/client.pem
  client_key: /etc/certs/client.key

devices:
  - id: PLC_1
    protocol: modbus_rtu
    interface: /dev/ttyS0
    baud_rate: 9600
    slave_id: 1
    points:
      - id: 1
        function: 3
        address: 0
        type: AI_Float
        mqtt_topic: device/PLC_1/point/1
        unit: V
      - id: 2
        function: 1
        address: 0
        type: DI
        mqtt_topic: device/PLC_1/point/2
```

## 实战代码片段

### MQTT 上行

```python
# 伪代码（Python paho-mqtt）
import paho.mqtt.client as mqtt
import json

def on_modbus_data_received(point_id, value, unit, quality, ts):
    payload = {
        "value": value,
        "unit": unit,
        "quality": quality,
        "ts": ts
    }
    topic = f"device/{device_id}/point/{point_id}"
    client.publish(topic, json.dumps(payload), qos=1)

client = mqtt.Client(client_id="gateway_001")
client.tls_set(ca_certs="ca.pem", certfile="client.pem", keyfile="client.key")
client.connect("broker.example.com", 8883, 60)
client.loop_start()
```

### MQTT 下行命令

```python
def on_command_received(client, userdata, msg):
    payload = json.loads(msg.payload)
    if payload["command"] == "write":
        point_id = payload["point_id"]
        value = payload["value"]
        # 转换为 Modbus 写入
        modbus_write_register(slave_id, point_id, value)
        
        # 应答
        ack_topic = msg.topic + "/ack"
        client.publish(ack_topic, json.dumps({"result": "OK"}))

client.subscribe("device/+/cmd/+")
client.on_message = on_command_received
```

## 实战检查清单

```text
- Modbus 多设备轮询
- MQTT 客户端实现（paho / mosquitto）
- TLS 双向认证
- Topic 规范化
- Payload JSON 格式化
- 时戳 / 品质处理
- 命令下行解析
- 命令超时
- QoS 1/2 处理
- 离线缓存补传
```

## 典型陷阱

```text
1. TLS 证书验证失败
   解决：CA 证书 + 系统时间

2. MQTT Topic 设计混乱
   解决：统一规范 + 文档

3. Payload 格式不兼容
   解决：JSON Schema 验证

5. 离线数据丢失
   解决：缓存 + 重连补传
```

## 适用场景

```text
- 工厂 IoT：PLC / 仪表 → 云平台
- 智慧城市：设备 → 城市 IoT 平台
- 楼宇：HVAC / 电表 → 云
- 能源管理：储能 / 充电桩 → 云
```

## 延伸阅读

- [[bus/power-rtu/rtu-gateway-design|rtu-gateway-design]]：RTU 网关总体设计
- [[bus/industrial/modbus|modbus]]：Modbus 协议
- [[bus/industrial/mqtt|mqtt]]：MQTT 协议