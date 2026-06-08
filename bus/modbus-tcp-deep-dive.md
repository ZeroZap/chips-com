# Modbus TCP Deep Dive

## 目标

本文深入 Modbus TCP 工程细节，重点覆盖 MBAP、TCP 字节流、并发客户端、网关转换、事务 ID、Unit ID、异常响应、连接管理和 Wireshark 排障。

## Modbus TCP 帧结构

Modbus TCP 使用 MBAP Header：

```text
Transaction ID | Protocol ID | Length | Unit ID | Function | Data
```

字段：

- Transaction ID：事务 ID，用于匹配请求和响应。
- Protocol ID：通常为 0。
- Length：后续 Unit ID + PDU 长度。
- Unit ID：单元 ID，网关场景常用。
- Function/Data：Modbus PDU。

Modbus TCP 没有 RTU CRC。

## TCP 字节流

TCP 不保留应用帧边界。

接收端必须根据 MBAP 的 Length 解析完整帧。

不能假设：

```text
一次 recv == 一帧 Modbus TCP
```

必须支持：

- 半包。
- 粘包。
- 多帧连续。
- 异常断开。

## Transaction ID

Transaction ID 用于匹配请求和响应。

在简单同步客户端中，它可能递增即可。

在并发请求或网关中，它很重要。

服务端通常应原样返回请求中的 Transaction ID。

## Unit ID

Unit ID 在纯 TCP 设备中可能固定为 1 或忽略。

在 Modbus TCP 到 RTU 网关中，Unit ID 常映射为 RTU 从站地址。

例如：

```text
TCP Unit ID 5 -> RS485 从站地址 5
```

## 并发客户端

设备作为 Modbus TCP Server 时要定义：

- 最大连接数。
- 同一客户端超时时间。
- 多客户端同时写寄存器的仲裁。
- 连接异常断开后的资源释放。

简单嵌入式设备可限制单客户端。

## 网关转换

Modbus TCP -> RTU 网关流程：

```text
接收 TCP 请求
解析 MBAP
取 Unit ID 作为 RTU 地址
生成 RTU 帧并加 CRC
等待 RTU 响应
校验 CRC
转换为 TCP 响应
保留 Transaction ID
```

注意：

- RTU 总线一次只能处理一个请求。
- TCP 多客户端请求需要排队。
- RTU 超时要转换为 TCP 异常或连接层错误策略。

## 异常响应

异常响应和 Modbus RTU 类似：

```text
Exception Function = Function + 0x80
Exception Code
```

常见异常：

- 01 非法功能。
- 02 非法数据地址。
- 03 非法数据值。
- 04 从站设备故障。

## 连接管理

嵌入式 Server 应处理：

- TCP keepalive。
- 空闲超时。
- 半开连接。
- 客户端异常断开。
- 资源耗尽。
- 重复连接。

不要让断开的 socket 永久占用连接槽。

## Wireshark 排查

常用过滤：

```text
tcp.port == 502
modbus
ip.addr == 192.168.1.50
```

重点看：

- TCP 三次握手。
- MBAP Length 是否正确。
- Transaction ID 是否匹配。
- Unit ID 是否正确。
- 是否出现 TCP Retransmission。
- 是否有 Reset。

## 常见故障定位

| 现象 | 优先检查 |
| --- | --- |
| TCP 连不上 | IP、端口、防火墙、服务监听 |
| 收到但解析错 | MBAP Length、半包/粘包 |
| 网关响应慢 | RTU 波特率、轮询队列、超时 |
| 多客户端异常 | 连接数、写冲突、资源释放 |
| 地址不对 | Unit ID、寄存器偏移 |

## 检查清单

- MBAP 解析使用状态机。
- Transaction ID 原样返回。
- Unit ID 语义明确。
- 支持半包和粘包。
- 连接超时和资源释放正确。
- 网关场景有请求队列。
- Wireshark 可解码请求和响应。
