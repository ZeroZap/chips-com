# Interface Parameter Cheatsheet

## 目标

本文整理常见通信接口调试时必须确认的关键参数。

## UART

```text
baud rate
data bits
parity
stop bits
flow control
voltage level
```

常见：

```text
115200 8N1
```

## I2C

```text
7-bit address
bus speed
pull-up resistor
voltage domain
Repeated START
Clock Stretching
```

常见速度：

```text
100 kHz
400 kHz
1 MHz
```

## SPI

```text
frequency
CPOL
CPHA
bit order
CS polarity
word length
dummy cycles
```

常见模式：

```text
Mode 0
Mode 3
```

## RS485 + Modbus RTU

```text
baud rate
parity
stop bits
slave address
function code
register offset
CRC byte order
DE/RE timing
```

## CAN

```text
bitrate
sample point
SJW
standard/extended ID
termination
filter
```

常见速率：

```text
125 kbps
250 kbps
500 kbps
1 Mbps
```

## CANopen

```text
Node ID
COB-ID
NMT state
SDO/PDO mapping
Heartbeat time
Object Dictionary
```

## USB

```text
role: Host/Device/OTG
speed
VID/PID
class
configuration
interface
endpoint
max packet size
```

## Ethernet

```text
MAC address
IP address
subnet mask
gateway
port
PHY address
link speed
duplex
```

## PCIe

```text
RC/EP role
Gen
Lane width
REFCLK
PERST#
BAR
MSI/MSI-X
DMA mapping
```

## MIPI CSI/DSI

```text
lane count
lane rate
pixel format
resolution
frame rate
MCLK
reset timing
power sequence
```
