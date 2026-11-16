---
tags:
  - layer/guides
  - type/cheatsheet
  - topic/learning
---

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

## CAN FD / CAN XL

```text
nominal bitrate
data bitrate
sample point (arbitration/data)
SJW
termination
transceiver loop delay
BRS / ESI
DLC / payload
```

## J1939

```text
bitrate (250k/500k)
PGN
SPN
source address
NAME
address claim
TP.CM / TP.DT
```

## UDS / ISO-TP

```text
CAN ID (request/response)
ISO-TP BS / STmin
P2 / P2* timeout
session type
security level / Seed-Key
DID / DTC
NRC handling
```

## Modbus TCP

```text
IP / port 502
unit ID
MBAP length
function code
register address / quantity
byte order
poll interval / timeout
```

## IEC 60870-5-104 / 101

```text
IP / port 2404 (104)
link address / common address
ASDU type
cause of transmission
information object address
K / W window (104)
t1/t2/t3 timeout
```

## DNP3

```text
transport / link address
outstation address
object group / variation
class 0/1/2/3
unsolicited response
event buffer
time sync
```

## BACnet

```text
network number
device instance
object type / instance
property
service (ReadProperty/WriteProperty)
BBMD / foreign device
APDU timeout / retries
```

## OPC UA

```text
endpoint URL
security policy
security mode
certificate
session timeout
subscription interval
node ID
```

## BLE

```text
advertising interval
connection interval
slave latency
supervision timeout
MTU
GATT service / characteristic
TX power
```

## ZigBee / Thread / Matter

```text
PAN ID / channel
network key / security
coordinator / border router
router / end device
ZCL cluster / endpoint
Matter fabric / discriminator
```

## LoRaWAN

```text
region / frequency
SF / bandwidth
TX power
ADR
OTAA / ABP
duty cycle
join timeout / retries
```

## LTE / NB-IoT

```text
band / APN
SIM / IMSI
PSM / eDRX
RSRP / SINR
attach / PDN
retry / backoff
```

## TSN

```text
gPTP domain / sync interval
VLAN ID / PCP
Qbv gate control list
cycle time / guard band
Qav idle slope
frame preemption
```

## 卫星 / 应急

```text
satellite system / band
SBD / short message length
GNSS fix / TTFF
beacon registration
activation method
retry / acknowledgment
```
