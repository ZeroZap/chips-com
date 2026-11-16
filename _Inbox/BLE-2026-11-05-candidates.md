# BLE 候选素材 @ 2026-11-05 23:00

## 协议速览
- 是什么：2.4GHz 跳频 + GATT 分层的低功耗蓝牙协议
- 解决什么：手机/网关与电池节点间小包数据、信标广播与厘米级测距
- 跟 L4 主题的关联：BLE 是 L4 近距离低功耗主力，IoT/可穿戴第一优先

## 候选文章（5 条）

### 1. BLE 抓包实战：HCI 层 + 空口
- 链接：https://m3ng9e.github.io/2026/03/16/BLE-蓝牙协议：抓包实战-HCI-空口/
- 来源：技术博客 Hexo（2026-03-16）
- 摘要：HCI 抓包绕过硬件加密拿明文，空口抓包拿 PHY/LL 全包，两者互补。用 EBYTE E104（nRF52840，45 元）+ Wireshark 抓小米手环。
- 关键实战点：① nrfutil v4 与固件 nrfsniffer3.0 版本不符即失败，插件须同版 ② 不指定目标 MAC 只能在 3 个广播信道打转，须抓 CONNECT_IND 才跟得上跳频
- 推荐动作：扩 ble-practical.md 抓包章节

### 2. Channel Sounding：nRF52840 厘米级测距
- 链接：https://blog.csdn.net/weixin_32770423/article/details/166119897
- 来源：CSDN 实战（2026-09-19）
- 摘要：BLE 5.4 Channel Sounding 测距，RTT + PBR 相位测距双机制互校，含 SDK 配置、天线延迟校准、Sniffer 调试，视距误差 ±10-15cm。
- 关键实战点：① 天线延迟校准是厘米级精度前提 ② 精度明显优于 RSSI，对应防丢器/室内定位
- 推荐动作：新建 ble-channel-sounding.md（库内空白）

### 3. NCS/Zephyr 蓝牙 OTA：MCUboot 与 DFU 分区
- 链接：https://www.cnblogs.com/iini/p/16085811.html
- 来源：博客园 iini（更新至 2026-07，nRF54L15 / NCS v3.4）
- 摘要：MCUboot vs NSIB(B0)、SMP/CBOR、分区规划、压缩 DFU 与单区 DFU 实测，附 ED25519/ECDSA 验签选型。
- 关键实战点：① 压缩 DFU 实测 143kB vs 248kB = 57.7%，不支持 revert 且须 overwrite-only ② 单区 DFU app 空间 1368kB（压缩版仅 784kB），代价是失败只能反复刷
- 推荐动作：扩 ble-deep-dive.md OTA 章节

### 4. BLE RF 射频测试规范与 KW36 六大误区
- 链接：https://www.elecfans.com/d/1826989.html
- 来源：电子发烧友 / 恩智浦 MCU 加油站（2022-04）
- 摘要：BLE 射频测试项与 PASS/NG 条件（BQB/FCC/CE），结合 KW36 客户现场总结 6 个踩坑误区，含 DTM/HCI 模式与仪器差异。
- 关键实战点：① AN12076 默认 MXG，国内用 R&S CMW270/500 走标准 HCI，照文档烧 conn_test.bin 连不上 DUT ② 默认 pattern 码流 125K 太慢，带内功率波形不达标须改 1M
- 推荐动作：扩 ble-failure-cases.md

### 5. BES LE Audio：LC3、多流同步与功耗调优
- 链接：https://blog.csdn.net/weixin_29164843/article/details/168614746
- 来源：CSDN 实战（2026-10-20）
- 摘要：BES 平台 LE Audio 落地：LC3 在音质/码率/DSP 负载间的取舍，多流 CIS 重构 TWS 拓扑实现双耳同步低延迟，BIS 广播接收与加密。
- 关键实战点：① CIS 调度与 ANC 共存是功耗关键路径 ② 多流 CIS 改了 TWS 拓扑，不能沿用经典蓝牙假设
- 推荐动作：入 ble-deep-dive.md 新增 LE Audio 段

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
（备注：web_search 本轮报 MATRIX_TOOL_REQUEST_FAILED，改用 DuckDuckGo lite + 直抓正文；raybyte.cn 等洗稿站已排除）
