# LoRa / LoRaWAN 候选素材 @ 2026-10-01 12:00

## 协议速览
- 是什么：Semtech LoRa 调制 + LoRaWAN MAC，sub-GHz ISM，公里级 / mW 级 / 电池数年的 LPWAN
- 解决什么：远距离低功耗少数据免 SIM 的小数据广域物联（电表/烟感/定位/园区能耗）
- L4 关联：「实验室 OK 产线挂」实战排错。LoRa 产线故障（SX1262 vs SX1276 迁移、DIO2 射频开关、FUOTA、ADR SF7 扎堆、半信道网关）都是典型 L4 素材

## 候选文章（5 条）

### 1. SX126x LoRa 驱动移植实战：5 个烧板废时间的真实案例
- 链接：http://www.lpqz.cn/news/558014.html
- 来源：尧图网络科技
- 摘要：SX126x 命令状态机+Busy 握手+DIO2 射频开关范式差异；STM32 SPI Mode 0；5 个真实烧板案例
- 实战点：DIO2 必须 `SetDio2AsRfSwitchCtrl(true)` 否则 TX 功率掉 20dB；Hz 当寄存器写 433MHz 偏 400kHz
- 推荐：**入主题笔记+写实战案例**（中文圈最完整 SX126x 移植排错清单）

### 2. LoRaWAN 智能能源系统实践：420 点 P0 事故复盘+FUOTA
- 链接：https://www.sheratonhq.com/news/80827
- 来源：sheratonhq
- 摘要：2km² 园区 420 点（电表/水表/温湿度/漏水）；STM32L0+SX1262 实测 50uA（2 节 AA 续航 2 年）；第 3 月 P0 三叠加
- 实战点：限最小 SF=SF9→吞吐 +4 倍；上报 jitter 削高峰 60%
- 推荐：**扩 deep-dive+写实战案例**（国内少见 LoRaWAN 大规模故障复盘）

### 3. WiFi LoRa 32 V4 / ESP32-S3 SX1262 跑通 TTN US915 FSB2
- 链接：http://community.heltec.cn/t/wifi-lora-32-v4-esp32-s3-sx1262-cannot-get-ttn-us915-fsb2-uplinks-visible/26373
- 来源：Heltec 论坛
- 摘要：V4 ESP32-S3+SX1262 跑通 US915 FSB2 的 4 项关键：pin map（NSS=8/DIO1=14/RST=12/BUSY=13）+ PA/FEM（GPIO7/2/5）+ RF switch 表 + FSB2 信道 903.9–905.3MHz
- 实战点：V4 ≠ V3+新芯片，需显式 PA/FEM；DevEUI 字节序反向被 NS 忽略
- 推荐：**入主题笔记**（Heltec 板级差异+US915 频段实战）

### 4. Troubleshooting ESP32+LoRa: Fix SPI, Range & Power
- 链接：https://electricalflux.com/mcu-general/fix-esp32-lora-spi-range-issues
- 来源：electricalflux.com
- 摘要：VSWR>3 烧 RFOUT（433MHz 天线装 868MHz）；5V 直连 3.3V SPI 烧栅氧；RadioLib 替换旧库（SX126x 用 DIO1 非 DIO0）；DC-DC 需 47nH 否则 brownout
- 实战点：VSWR>3 RFOUT 永久烧毁；RG178 pigtail 900MHz 衰减大换 RG316
- 推荐：**扩 deep-dive**（英文 troubleshooting 跟中文互补）

### 5. LoRa 模块初始化失败：70% 硬件或 SPI/UART 错配
- 链接：https://ask.csdn.net/questions/9222679
- 来源：CSDN
- 摘要：70% 故障在硬件（SPI NSS 推挽缺失、上拉缺失、CPOL/CPHA 错）+ UART 偏差>3%；防御性初始化模板
- 实战点：70% 是链路未建立而非固件；STM32 APB 分频错是 UART 偏差源头
- 推荐：**入主题笔记**（可单立「SX127x/SX126x 初始化 checklist」）

## 下一步
review 后决定：激活/改写/丢弃