# Driver State Machine Patterns

## 目标

本文整理通信驱动常见状态机和伪代码模式，帮助从“能通信”走向“可恢复、可测试、可维护”。

## 通用设备驱动状态

```text
RESET
POWER_ON
PROBE
CONFIGURE
READY
RUNNING
ERROR
RECOVERING
OFFLINE
```

推荐原则：

- 初始化失败要能回到可恢复状态。
- 通信错误要分类统计。
- 设备离线和协议错误要区分。
- 不能在中断里做复杂阻塞操作。

## I2C 寄存器设备

```text
power_on()
release_reset()
scan_address()
read_chip_id()
write_init_table()
verify_status()
enter_ready()
```

错误处理：

```text
address_nack -> retry -> mark_offline
bus_busy -> bus_recovery -> retry
data_nack -> report_command_error
timeout -> reset_controller_or_device
```

## SPI Flash

```text
read_jedec_id()
read_status()
write_enable()
page_program()
poll_wip_clear()
verify_data()
```

注意：
```text
DMA 完成不代表 Flash 内部写完成
必须轮询 WIP
```

## Modbus RTU 主站

```text
build_request()
enable_rs485_tx()
send_frame()
wait_uart_tc()
enable_rs485_rx()
wait_response_timeout()
check_crc()
parse_response_or_exception()
update_slave_state()
```

从站状态：

```text
ONLINE
TIMEOUT
OFFLINE
RECOVERING
```

## CANopen 节点控制

```text
wait_bootup()
read_identity()
configure_heartbeat()
configure_pdo()
nmt_start()
monitor_heartbeat()
process_emcy()
exchange_pdo()
```

电机驱动还需要 CiA 402 状态机：

```text
Fault Reset
Shutdown
Switch On
Enable Operation
Run
Disable / Fault Handling
```

## USB Device

```text
usb_stack_init()
connect_pullup()
handle_reset()
handle_setup_packet()
send_descriptors()
set_configuration()
start_class_endpoints()
process_class_data()
```

注意：

- 未配置前不要假设 Endpoint 可用。
- CDC 要关注 Host 是否打开端口。
- 断开重连要释放状态。

## Ethernet TCP Server

```text
phy_link_wait()
dhcp_or_static_ip()
listen_socket()
accept_client()
recv_stream()
frame_parser()
process_request()
send_response()
handle_disconnect()
```

TCP 解析器必须处理：

```text
半包
粘包
多客户端
超时
断线重连
```

## 通用错误统计

建议每个驱动维护：

```text
tx_count
rx_count
timeout_count
crc_error_count
nack_count
bus_recovery_count
reset_count
last_error
last_success_time
```

## 日志格式建议

```text
[bus][device][state][error][detail]
```

示例：

```text
i2c imu0 PROBE address_nack addr=0x68 retry=2
modbus meter1 RUNNING crc_error frame_len=9
can motor2 ERROR heartbeat_timeout node=2
```
