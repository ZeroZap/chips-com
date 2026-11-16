# DNP3 产线死机案例库

## 目标

把产线常见的 DNP3 通信失败、CRC 错、对象变体错、Class 报告错、SA 认证错等写成案例库。

## 案例 1：CRC16 多项式错

### 现象

主站发请求，RTU CRC 校验失败。

### 排查

```text
主站 CRC 多项式：0xA001（Modbus）
RTU CRC 多项式：0xA6BC（DNP3）
```

### 修复

主站 CRC 算法切换为 DNP3 CRC16。

### 复盘

```text
1. DNP3 CRC16 是 0xA6BC，不是 Modbus 0xA001
2. 不同协议 CRC 不同
3. 测试用例必须验证 CRC
```

## 案例 2：[0x05 0x64] 启动符未识别

### 现象

主站 / RTU 完全不通信。

### 排查

```text
TCP 三次握手成功
但应用层无数据
```

### 定位

Wireshark 看 TCP 流，没有 [0x05 0x64] 启动字符。

### 修复

检查应用层发送逻辑。

### 复盘

```text
1. DNP3 启动字符是 [0x05 0x64]
2. 必须先发启动字符
3. 测试用例必须验证报文格式
```

## 案例 3：控制字节解析错

### 现象

主站请求链路状态，RTU 不响应。

### 排查

```text
主站控制字节：0xC9 (DIR=0, PRM=1, FC=9)
RTU 解析：0x89 (DIR=0, PRM=1, FC=9)  # 错
```

### 修复

控制字节按位掩码纠正。

### 复盘

```text
1. DIR/PRM/FCB/FCV/DFC 必须按位解析
2. 不同实现易错
3. 测试用例必须验证控制字节
```

## 案例 4：对象变体错

### 现象

主站读 g1v1 Binary Input Static，RTU 回 g1v2 Binary Input Event（错）。

### 排查

```text
主站请求：g1v1
RTU 响应：g1v2（错配）
```

### 修复

RTU 对象变体映射纠正。

### 复盘

```text
1. 主站 / RTU 对象变体必须一致
2. 测试用例必须验证对象变体
3. 部署前必须确认
```

## 案例 5：Class 报告混乱

### 现象

RTU Class 1/2/3 分配错，导致主站报告混乱。

### 排查

```text
Class 1 分配了低优先级数据
Class 3 分配了高优先级数据
```

### 修复

RTU Class 分配纠正。

### 复盘

```text
1. DNP3 Class 0/1/2/3 必须合理分配
2. Class 1 优先级最高
3. 测试用例必须验证 Class
```

## 案例 6：完整性轮询无响应

### 现象

主站发 Class 0 完整性轮询，RTU 不响应。

### 排查

```text
主站：Read + g60v1 + Range=0x00 (Class 0)
RTU：不识别 g60v1
```

### 修复

主站请求格式纠正（用 g60v2）。

### 复盘

```text
1. DNP3 Class 0 完整性轮询用 g60v2 Range=0x00
2. 部分 RTU 只支持特定变体
3. 测试用例必须验证
```

## 案例 7：事件轮询失败

### 现象

主站发 Class 1 事件轮询，RTU 偶发不响应。

### 排查

```text
Class 1 事件：缓冲未清空
```

### 修复

RTU 事件缓冲管理纠正。

### 复盘

```text
1. Class 1 事件必须定期清除
2. RTU 缓冲管理是关键
3. 测试用例必须验证事件轮询
```

## 案例 8：未确认报告不触发

### 现象

主站发 Enable Unsolicited，RTU 不主动上报。

### 排查

```text
主站：Enable Unsolicited
RTU：未实现
```

### 修复

RTU 实现未确认报告主动上报。

### 复盘

```text
1. 未确认报告 RTU 必须实现
2. 测试用例必须验证 Enable Unsolicited
```

## 案例 9：命令 Select → Operate 失败

### 现象

主站发 Select 命令，RTU 不响应。

### 排查

```text
主站：Select + g10v1 + Point 5
RTU：未实现 Select
```

### 修复

RTU 实现 Select 处理。

### 复盘

```text
1. Select → Operate 是标准流程
2. RTU 必须实现两步
3. 测试用例必须验证命令链
```

## 案例 10：Direct Operate 无 Select 错

### 现象

主站发 Direct Operate，RTU 执行但主站期待 Select → Operate。

### 修复

主站必须按 RTU 配置选择流程。

### 复盘

```text
1. Direct Operate 单步，无 Select
2. 必须 RTU 配置支持
3. 测试用例必须区分
```

## 案例 11：时间戳错

### 现象

主站解析 RTU 上报时间错。

### 排查

```text
RTU g50v1：6 字节时间
主站解析：错（多读 / 少读字节）
```

### 修复

主站按 g50v1 字节数解析。

### 复盘

```text
1. DNP3 时间字节数固定
2. g50v1 = 6 字节，g50v4 = 10 字节
3. 测试用例必须验证时间格式
```

## 案例 12：SA v5 认证失败

### 现象

主站发 Command + HMAC，RTU 认证失败。

### 排查

```text
主站 HMAC：SHA-1
RTU HMAC：SHA-256（错配）
```

### 修复

主站 / RTU 统一 HMAC 算法。

### 复盘

```text
1. SA v5 用 SHA-1
2. SA v6 用 SHA-256
3. 测试用例必须验证 SA
```

## 案例 13：Aggressive Mode vs Normal Mode

### 现象

主站发 Aggressive Mode 命令，RTU 不支持。

### 修复

主站切换 Normal Mode（先 Request Challenge）。

### 复盘

```text
1. Aggressive Mode = 单向认证（风险）
2. Normal Mode = 双向认证（推荐）
3. 关键基础设施必须 Normal Mode
```

## 案例 14：密钥更新失败

### 现象

主站发 Update Key，RTU 密钥未更新。

### 排查

```text
主站：Update Key + KeyChangeData
RTU：未实现 Update Key
```

### 修复

RTU 实现 Update Key。

### 复盘

```text
1. SA v5/v6 必须支持密钥更新
2. 定期更新密钥
3. 测试用例必须验证密钥更新
```

## 案例 15：传输层分片错

### 现象

主站收到分片帧，序号错乱。

### 排查

```text
RTU：分片 SEQ=1, 2, 3
主站：按 SEQ=0, 1, 2 重组（错）
```

### 修复

主站按 FIR/FIN + SEQ 重组。

### 复盘

```text
1. DNP3 传输层分片 FIR/FIN + SEQ
2. 测试用例必须验证分片
```

## 案例 16：链路层 FCB 不同步

### 现象

主站发请求，RTU 偶发不响应。

### 排查

```text
主站 FCB：0, 1, 0, 1
RTU FCB：未正确翻转
```

### 修复

RTU FCB 状态机纠正。

### 复盘

```text
1. DNP3 链路层 FCB 必须翻转
2. 测试用例必须验证 FCB
```

## 案例 17：Class 0 响应数据不全

### 现象

主站发 Class 0 完整性轮询，RTU 响应不全。

### 排查

```text
RTU：Class 0 部分点未配置
```

### 修复

RTU 配置 Class 0 全部点。

### 复盘

```text
1. Class 0 必须完整
2. 测试用例必须验证完整性
```

## 案例 18：文件操作失败

### 现象

主站发 File Open，RTU 不响应。

### 排查

```text
RTU：未实现 File Open
```

### 修复

RTU 实现文件操作。

### 复盘

```text
1. DNP3 文件操作用于配置 / 固件下载
2. 必须 RTU 实现
```

## 案例 19：设备重启命令执行

### 现象

主站发 Cold Restart（0x1D），RTU 实际重启但没准备好。

### 修复

主站用 Warm Restart（0x1E）替代。

### 复盘

```text
1. Cold Restart 是断电重启
2. Warm Restart 是软重启
3. 工程实践：Warm Restart 优先
```

## 案例 20：VPN / 专网断

### 现象

主站与 RTU VPN 断开，所有通信中断。

### 修复

VPN 重连机制 / 备用网络。

### 复盘

```text
1. DNP3 关键基础设施必须 VPN / 专网
2. 网络不能断 / 必须有备份
3. 测试用例必须验证网络异常
```