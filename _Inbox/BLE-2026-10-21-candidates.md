# BLE 候选素材 @ 2026-10-21 00:05

## 协议速览
- 是什么：2.4GHz 低功耗无线协议，nRF52/ESP32 上做手机—设备连接与 OTA 的主通道
- 解决什么：电池节点能被手机直连、升级固件、读诊断数据，不用拆机
- 跟 L4 的关联：本轮全是「BLE 广播正常、产线 DFU 却挂」的量产典型形态

## 候选文章（4 条）

### 1. DFU Failure - seems to be a hardware issue
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/127944/dfu-failure---seems-to-be-a-hardware-issue/565615
- 来源：Nordic DevZone（产线方提问）
- 摘要：BMD-350(nrf52832) 量产一年，产线自动 DFU 抓到 1 台收不到固件、秒退，但主应用和 BLE 都正常。换台面电源供电后 DFU 成功，换回原纽扣电池后续也成功。
- 关键实战点：
  - 产线才发现、客户侧复现不了 → DFU 不能只在上线前测
  - 官方判断：非永久失效，是切入 update mode 瞬间的临时掉压/复位
- 推荐动作：**写实战案例**（产线 DFU 掉压根因，可扩 failure-cases）

### 2. Adafruit nRF52 Bootloader OTAFIX（排障 FAQ + 调参矩阵）
- 链接：https://github.com/oltaco/Adafruit_nRF52_Bootloader_OTAFIX
- 来源：GitHub（nRF52 bootloader 增强版）
- 摘要：`Error: Operation Failed` 的根因是开了 Request High MTU 后与部分 Android BLE 栈不兼容；给出 PRN=30、pkt=30、reboot 0ms、scan 2000ms 实测值，并实现 lazy flash erase 与小包聚合。
- 关键实战点：
  - High-MTU 不兼容 → 关掉即可，是主机栈差异不是协议 bug
  - <64B 小包在传输层攒到 ≤240B 再写 flash，专治 iOS 端
- 推荐动作：**扩 deep-dive**（PRN/MTU/包长三维调参表）

### 3. Meshtastic 蓝牙 OTA 升级踩坑指南
- 链接：https://www.keepteen.com/blog-Solar-Lora/Updating-nRF-Firmware-Over-the-Air-The-Meshtastic-Bluetooth-OTA-Guide-11938290.html
- 来源：Meshtastic 中文社区博客
- 摘要：实测 BLE OTA 约 1 KB/s，150KB 固件需数分钟。归纳三类中断：传输卡住（iOS 包长 23→5 + 开 PRN）、更新后起不来（版本/格式错、文件损坏）、手机息屏断链（auto-lock 设 Never）。
- 关键实战点：
  - USB 20 秒 vs BLE 几分钟——量产选型的实际耗时差
  - 息屏断链是移动端特有失败模式，产线脚本要防
- 推荐动作：**写实战案例**（iOS 侧三大失败模式）

### 4. nRF52840 time to reboot after BLE OTA（swap vs direct-xip）
- 链接：https://devzone.nordicsemi.com/thread/516136
- 来源：Nordic DevZone
- 摘要：OTA 传完 20 秒才重启，根因是 dual-bank 的 swap 流程。Nordic 确认大应用 swap 耗时长，可改 direct-xip，代价是 DFU 前须自行判定活动 slot。
- 关键实战点：
  - swap 默认启用是「防变砖」换来的延迟，不是 bug
  - direct-xip 提速代价 = bootloader 自己管 slot 判定
- 推荐动作：**扩 deep-dive**（bank 取舍同 SimCardReader Bootloader）

## 下一步
等你 review：激活 / 改写 / 丢弃。下一站轮询 LoRa。