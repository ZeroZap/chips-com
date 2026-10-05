# BACnet ↔ OPC UA 网关

## 定位

本文是 BACnet ↔ OPC UA 双向转换网关设计文档。这是楼宇 + 工业 4.0 集成场景：现场 BACnet 楼宇设备通过网关转 OPC UA 上 MES / 云平台。

## 场景

```text
现场设备（BACnet）：
  - HVAC、照明、传感器、控制器
  - BACnet/IP 或 BACnet MS/TP

上行（OPC UA）：
  - 工厂 MES / 数字孪生
  - 标准 OPC UA
```

或反向：

```text
工业 4.0（OPC UA）→ 楼宇设备（BACnet）
```

## 数据流

```text
1. BACnet 设备发现（Who-Is / I-Am）
   - 获取所有设备列表
   - 浏览对象树

3. BACnet → 内部 Point 模型
   - BACnet Object Identifier → Point ID
   - Object Name / Description

4. OPC UA Server（地址空间）
   - Object / Variable 节点
   - TypeDefinition 映射
   - 订阅 / 通知

5. 反向：OPC UA 写入 → BACnet WriteProperty
```

## BACnet 对象 ↔ OPC UA 节点

| BACnet 对象 | OPC UA Variable Type | 说明 |
| --- | --- | --- |
| Analog Input (AI) | AnalogItemType | 模拟量输入 |
| Analog Output (AO) | AnalogItemType | 模拟量输出 |
| Analog Value (AV) | AnalogItemType | 模拟量值 |
| Binary Input (BI) | TwoStateDiscreteType | 二态开关 |
| Binary Output (BO) | TwoStateDiscreteType | 二态输出 |
| Binary Value (BV) | TwoStateDiscreteType | 二态值 |
| Multi-state Input (MI) | MultiStateDiscreteType | 多态 |
| Multi-state Output (MO) | MultiStateDiscreteType | 多态 |
| Multi-state Value (MV) | MultiStateDiscreteType | 多态 |
| Schedule | Object | 调度 |
| Trend Log | Object | 历史 |

## 数据转换示例

```text
BACnet AI 1 Present_Value：
  Object Identifier: AI 1
  Property: Present_Value
  Value: REAL = 23.5
  Units: degrees-Celsius

OPC UA 节点：
  NodeId: ns=1;s=BACnet.AHU_01.Temperature
  TypeDefinition: AnalogItemType
  Value: Double = 23.5
  EngineeringUnits: degrees_Celsius
```

## 命令反向

```text
OPC UA 客户端：
  写入 AO 1 Present_Value = 50.0
  Call Method: BACnet.Device.AHU_01.Setpoint

网关转换：
  BACnet WriteProperty
    Object Identifier: AO 1
    Property Identifier: Present_Value
    Property Value: REAL = 50.0

BACnet 响应 → OPC UA 应答
```

## COV → OPC UA MonitoredItem

```text
BACnet COV 订阅：
  SubscribeCOV AI 1 (Lifetime 60s)
  → ConfirmedCOVNotification 变位时

OPC UA MonitoredItem：
  SamplingInterval 500ms
  → Publish DataChangeNotification
```

## 配置示例（JSON）

```json
{
  "bacnet": {
    "interface": "udp:47808",
    "scan_interval": 60
  },
  "opcua": {
    "server_url": "opc.tcp://localhost:4840",
    "namespace": 1,
    "security_policy": "Basic256Sha256"
  },
  "device_mapping": [
    {
      "bacnet_device_id": 100,
      "bacnet_device_name": "AHU_01",
      "opcua_node_path": "Devices/AHU_01",
      "objects": [
        {
          "bacnet_object": "AI 1",
          "name": "Temperature",
          "opcua_variable": "Temperature",
          "engineering_units": "degrees_Celsius"
        }
      ]
    }
  ]
}
```

## 实战代码片段

### BACnet 对象浏览

```python
# 伪代码（Python bacpypes）
from bacpypes.app import BIPSimpleApplication
from bacpypes.core import run

app = BIPSimpleApplication()
app.do WhoIs()

# 接收 I-Am
for device in discovered_devices:
    # 读 Object List
    obj_list = read_property(app, device, "objectList")
    
    # 读每个对象
    for obj in obj_list:
        present_value = read_property(app, obj, "presentValue")
        opcua_node = map_bacnet_to_opcua(obj)
        opcua_write_node(opcua_node, present_value)
```

### OPC UA 信息建模

```python
# 伪代码（Python opcua）
from opcua import Server

server = Server()
server.set_endpoint("opc.tcp://localhost:4840")

# 创建对象
objects = server.get_objects_node()
ns = server.register_namespace("BACnet")

# 设备对象
ahu = objects.add_object(ns, "AHU_01")

# 添加 AnalogItem
ai_temp = ahu.add_variable(ns, "Temperature", 0.0)
ai_temp.set_datatype(opcua.NodeId(opcua.ua.ObjectIds.AnalogItemType))
```

## 实战检查清单

```text
- BACnet 设备发现（Who-Is）
- BACnet 对象浏览
- BACnet → OPC UA 映射
- OPC UA Server 地址空间
- BACnet COV → OPC UA MonitoredItem
- 反向：OPC UA 写入 → BACnet WriteProperty
- 安全（OPC UA Sign / Encrypt）
- 设备自动发现
- 实时性
```

## 典型陷阱

```text
1. BACnet Object 命名不一致
   解决：统一命名规范

2. OPC UA NodeId 冲突
   解决：Namespace 区分

3. COV 不触发
   解决：COV_Increment 配置

4. MonitoredItems 堆积
   解决：定期清理

5. 时戳不一致
   解决：UTC 统一
```

## 适用场景

```text
- 楼宇集成：BACnet → OPC UA → MES
- 工业 4.0：工厂 OPC UA 集成楼宇设备
- 智慧城市：多个楼宇系统汇聚
- 数字孪生：楼宇 + 工厂联合建模
```

## 延伸阅读

- `bus/rtu-gateway-design.md`：RTU 网关总体设计
- `bus/bacnet.md`：BACnet 协议
- `bus/opcua.md`：OPC UA 协议