# LoRa 候选素材 @ 2026-10-21 12:00

## 协议速览
- 是什么：Chirp 扩频 ULP PHY（SX127x/SX126x）+ LoRaWAN MAC（OTAA/ADR/Class A-C）
- 解决什么：非授权频段 2-5km 广覆盖、µA 级静态功耗、几十字节小包
- 跟 L4 主题的关联：本批全是"实验室 OK、现场必现挂"，正合 L4 闭环口径

## 候选文章（3 条）

### 1. STM32WL55JC 在 ChirpStack 上失联：AU915 信道掩码解析 bug
- 链接：http://www.sheratonhq.com/news/83757
- 来源：技术博客（客户工单复盘）
- 摘要：同固件在 TTN 跑 14 天成功率 >99%，搬自建 ChirpStack v4 后入网 30-60 秒必冻结。ChirpStack 的 ADR 下发 ChMask=0x00FF/ChMaskCntl=0，MW 2.5.0 的 `RegionAU915LinkAdrReq` 把这个合法掩码解析成"启用通道数=0"，且未校验空集合就返回成功。
- 关键实战点：
  - "TTN 正常 / ChirpStack 挂"不是服务器不兼容，是**服务器参数组合触发固件边界 bug**
  - 失败链：通道清零 → `LORAMAC_STATUS_NO_CHANNEL_FOUND` → RTOS 封装不发 Confirm → 应用层永久等待，MCU 不死机而是"半死"
  - LoRaWAN 认证不覆盖全禁掩码这类边界用例，过认证≠对所有合法参数健壮
- 推荐动作：**扩 deep-dive**，可进 lora-failure-cases

### 2. SX1302 网关容量估算：真实带机量解析
- 链接：http://www.hqwc.cn/news/1883913.html
- 来源：工程博客（智慧农业）
- 摘要：ToA → ALOHA 18.4% → 设备数三步推算。实测郊区网关 800+ 设备，SF7 仅 15%、SF12 仅 3%，加权 ToA≈500ms，比理想 SF7 差一倍多。
- 关键实战点：
  - **500 台分批上电入网，Join 请求瞬间占满信道，在线设备轮询大面积超时**；加随机入网延时才缓解
  - 20km² 农业项目理论 2000 台，实际 500 台就掉线，最终 600 台稳定
  - "8 通道≠同时收 8 包"：同频点同 SF 是硬冲突；扩到 16 频点是时分复用，**不翻倍**
- 推荐动作：**写实战案例**，估算模板可复用

### 3. LoRaWAN 智能能源系统：420 点位 P0 复盘
- 链接：https://kwkr.cn/news/272465
- 来源：项目复盘博客
- 摘要：上线 3 个月点位扩到 420，8:00 起全网数据延迟 1 小时、部分节点不更新。三因素叠加，修复后吞吐提升约 4 倍。
- 关键实战点：
  - 半信道网关 UDP 转发队列堆积——标称 8 解调路径 ≠ NS 侧转发无上限
  - ChirpStack PostgreSQL 连接池打满 → 超时重试 → 压力二次放大
  - **ADR 无边界限制**：强信号节点全压到 SF7、并发窗口集中 → 队列溢出；修法是 NS 侧锁最小 SF9
- 推荐动作：**写实战案例**，三因素叠加结构可复用

## 备选（偏教程向，未展开）
- SXXL1276 低温 -20℃ TX 电流 120→158mA 致 MCU 复位 https://shuma.taobao.com/topic/RFmokuai_1105/2fb3b840171af6ab04f46cbfdd0740e6.html
- ESP32+LoRa brownout 与 PA_Boost/RFO 选脚 https://electricalflux.com/mcu-general/fix-esp32-lora-spi-range-issues

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃