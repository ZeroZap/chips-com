---
tags:
  - layer/bus
  - type/gateway-design
  - protocol/hj212
  - topic/power-rtu
---

# HJ 212 ↔ MQTT 网关

## 定位

本文是 HJ 212（环保联网协议）转 MQTT 的网关设计文档。这是环保 RTU 场景：现场 HJ 212 设备通过 RTU 网关转 MQTT 上云。

## 场景

```text
现场设备（HJ 212）：
  - 排污口 / 空气站 / 噪声 / 地表水
  - 标准 HJ 212-2017
  - TCP 长连接

上行云平台（MQTT）：
  - 环保云平台 / IoT 平台
  - 标准 MQTT
```

## 数据流

```text
1. HJ 212 现场数据采集
   - 实时数据 CN=2011
   - 分钟数据 CN=2021
   - 超标数据 CN=2051
   - 事件上报 CN=1011

2. HJ 212 → 内部 Point 模型
   - 因子编码 → Point ID
   - 数据值 + Flag-N + 时间戳

4. MQTT 上行
   - Topic：device/{mn}/data/{cn}
   - Payload：JSON

5. 反向：MQTT 命令 → HJ 212 命令
   - MQTT 命令 → HJ 212 CN=3021 命令请求
```

## HJ 212 ↔ 内部模型

| HJ 212 因子 | 内部 Point | MQTT Topic |
| --- | --- | --- |
| a21026 (流量) | AI_FlowRate | device/MN/point/flow |
| a21002 (SO2) | AI_SO2 | device/MN/point/so2 |
| w01014 (氨氮) | AI_NH3N | device/MN/point/nh3n |
| w01016 (COD) | AI_COD | device/MN/point/cod |
| a21026-Rtd | real-time-data | device/MN/data/realtime |

## MQTT Topic 设计

```text
上行（HJ 212 → MQTT）：
  device/{MN}/data/realtime        # 实时数据
  device/{MN}/data/minute          # 分钟数据
  device/{MN}/data/hour            # 小时数据
  device/{MN}/data/day             # 日数据
  device/{MN}/data/exceed          # 超标数据
  device/{MN}/event                # 事件
  device/{MN}/status               # 设备状态
  device/{MN}/heartbeat            # 心跳

下行（MQTT → HJ 212）：
  device/{MN}/cmd/set_threshold    # 设置阈值
  device/{MN}/cmd/calibrate        # 校准
  device/{MN}/cmd/sample           # 即时采样
  device/{MN}/cmd/reboot           # 重启
  device/{MN}/config/params        # 参数更新
```

## Payload 格式（JSON）

```json
{
  "mn": "ABC1234567890",
  "cn": "2011",
  "qn": "20260928153045123",
  "timestamp": 1728000000,
  "data": {
    "a21026-Rtd": 123.45,
    "a21026-Flag": "N",
    "a21002-Rtd": 15.32,
    "a21002-Flag": "N",
    "w01014-Rtd": 2.34,
    "w01014-Flag": "F"
  }
}
```

## 数据转换

```text
HJ 212 数据段：
  a21026-Rtd=123.45,a21026-Flag=N;
  a21002-Rtd=15.32,a21002-Flag=N;

内部 Point：
  Point ID 1, name="a21026", value=123.45, unit="m³/h", quality=Good
  Point ID 2, name="a21002", value=15.32, unit="mg/L", quality=Good

MQTT Payload：
  device/ABC1234567890/data/realtime
  {
    "timestamp": 1728000000,
    "data": [
      {"id": "a21026", "value": 123.45, "unit": "m³/h", "flag": "N"},
      {"id": "a21002", "value": 15.32, "unit": "mg/L", "flag": "N"}
    ]
  }
```

## 命令下行

```text
MQTT 命令：
  Topic: device/ABC1234567890/cmd/calibrate
  Payload: {"timestamp": 1728000000, "command": "calibrate"}

网关转换 HJ 212：
  CN=3021 命令请求
  DataTime=202609281530;Pol-a:123456;

HJ 212 应答 → MQTT：
  Topic: device/ABC1234567890/cmd/calibrate/ack
  Payload: {"result": "OK"}
```

## 配置示例（YAML）

```yaml
hj212:
  mn: ABC1234567890
  pw: 123456
  server_ip: platform.example.com
  server_port: 8000
  heartbeat_interval: 60

mqtt:
  broker: tls://broker.example.com:8883
  client_id: hj212_gateway_001
  
factor_mapping:
  a21026:
    name: "流量"
    unit: "m³/h"
    mqtt_topic_suffix: "flow"
  a21002:
    name: "SO2"
    unit: "mg/L"
    mqtt_topic_suffix: "so2"
```

## 实战代码片段

### HJ 212 数据接收

```python
# 伪代码
def on_hj212_data_received(cn, qn, data_section):
    payload = {
        "mn": mn,
        "cn": cn,
        "qn": qn,
        "timestamp": int(time.time()),
        "data": []
    }
    for item in parse_data_section(data_section):
        payload["data"].append({
            "id": item.factor,
            "value": item.value,
            "flag": item.flag
        })
    
    topic = f"device/{mn}/data/{cn_to_topic(cn)}"
    mqtt_client.publish(topic, json.dumps(payload), qos=1)
```

### MQTT 命令 → HJ 212

```python
def on_mqtt_command(client, userdata, msg):
    payload = json.loads(msg.payload)
    
    if msg.topic.endswith("/calibrate"):
        hj212_cmd = build_cn_3021("calibrate")
        hj212_send(hj212_cmd)
        
        ack = {"result": "OK"}
        client.publish(msg.topic + "/ack", json.dumps(ack))
```

## 实战检查清单

```text
- HJ 212 TCP 长连接
- MN / PW 配置
- 因子编码字典
- 心跳周期
- 实时 / 分钟 / 小时数据按周期上报
- 超标数据标识
- MQTT TLS 加密
- Topic 规范化
- 命令下行
- 应答机制
```

## 典型陷阱

```text
1. 因子编码不在字典
   解决：扩展字典 + 文档

2. 超标数据未触发
   解决：阈值配置

3. MN 未注册到平台
   解决：先注册再上线

4. 心跳周期不匹配
   解决：按省级要求配置

5. MQTT Topic 命名冲突
   解决：规范化 + 文档
```

## 适用场景

```text
- 排污口 RTU：HJ 212 → MQTT → 环保云
- 空气站：HJ 212 → MQTT → 城市 IoT
- 地表水监测：HJ 212 → MQTT
- 噪声监测：HJ 212 → MQTT
```

## 延伸阅读

- `bus/power-rtu/rtu-gateway-design.md`：RTU 网关总体设计
- `bus/power-rtu/hj212.md`：HJ 212 协议
- `bus/industrial/mqtt.md`：MQTT 协议