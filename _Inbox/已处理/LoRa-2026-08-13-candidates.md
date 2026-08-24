# LoRa / LoRaWAN 候选素材 @ 2026-08-13 00:00

## 协议速览
- 是什么：Semtech CSS 扩频 + LoRa Alliance 的 MAC 协议，Sub-GHz 远距低功耗
- 解决什么：电池 IoT 节点数~10km 小数据上行（水表/农业/物流）
- L4 关联：IoT 主流 LPWAN；user IoT/可穿戴方向资产追踪备选

## 候选文章（5 条）

### 1. 打造自己的 LoRaWAN 网关·进阶 2:处理异常
- 链接：https://blog.csdn.net/jiangjunjie_2005/article/details/80073820
- 来源：CSDN 实战
- 摘要：长期稳定性测试踩出 SX1301 网关 5 个真实故障（停机/CRC_FAIL 100%/丢包率大增/DNS 失败/网络安全），每条带"现象-原因-处理-验证"四段式
- 实战点：① SX1301 裸露易受 LoRa 噪声停机→加屏蔽盒；② `CRC_FAIL 100%` 连续 3 次触发 systemd 重启；③ 节点网关<2m 主频谐波灌相邻信道，丢包>20%
- 推荐：**扩 deep-dive**（教科书级产线问题）

### 2. 移动场景下 ADR 失效的 5 种解决方案
- 链接：https://blog.csdn.net/weixin_30296405/article/details/98211593
- 来源：CSDN 移动物联网实战
- 摘要：深圳运营商共享电单车试点，20km/h 移动场景 ADR 集体失效。含 RSSI 波动实测（静态±2/低速±6/高速±12dB）和 Class A 18s 延迟陷阱
- 实战点：① 1min RSSI 波动 6-8dB 颠覆传统 ADR 假设；② 60km/h 车辆 NS→设备 ADR 命令 18s 延迟，设备位移 300m
- 推荐：**写实战案例**（可穿戴/资产追踪直接相关）

### 3. Lora1278 使用中遇到的问题总结
- 链接：https://blog.csdn.net/wuhenyouyuyouyu/article/details/102675850
- 来源：CSDN 硬件实战
- 摘要：SX1278 调试 3 类硬件故障：电源纹波（LDO vs DC/DC）、静电后 RSSI 锁死 -164/-155、FSK 长发污染同板 Lora 接收
- 实战点：① LDO 旁用 DC-DC 时 Lora 不工作→电源裕量要够；② 静电后 RSSI 锁死，驱动需加"连续 N 次异常即复位"
- 推荐：**扩 deep-dive**（硬件+驱动+验证闭环）

### 4. Lora 模块同频干扰 3 种工程方案
- 链接：https://blog.csdn.net/manageruser/article/details/127099902
- 来源：CSDN 厂商技术
- 摘要：LoRa 一对多通信三种方案：主机轮询、从机定时上传、主动上传+RSSI 检测
- 实战点：① 轮询稳定但慢；② 定时上传广播同步时钟后错时上报；③ 主动上传+RSSI 适合突发但需模块带 RSSI
- 推荐：**写实战案例**（LPWAN 同频干扰通病）

### 5. 基于 Lora 通信的电表采集终端实现
- 链接：https://blog.csdn.net/asdmfb/article/details/137195071
- 来源：CSDN 产品实战
- 摘要：产品级 LoRa 电表（国网 645 协议 97/07 兼容+自动搜表+停电上报），含 SX1278 vs SX1262 选型对比+完整 Radio 抽象层
- 实战点：① SX1262 DC-DC 模式接收 5mA（vs SX1278 12mA），最大 22dBm；② 停电上报大电容+110-130s 随机定时防同时启动
- 推荐：**入主题笔记**（完整产品级代码+选型对比表）

## 下一步
review 后决定：激活/改写/丢弃
</content>
</invoke>
