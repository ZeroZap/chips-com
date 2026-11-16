# CANopen 候选素材 @ 2026-11-03 00:00

## 协议速览
- 是什么：CAN 之上的工业应用层协议（CiA 301 / EN 50325-4）
- 解决什么：统一对象字典与 COB-ID 语义
- 关联：canopen-failure-cases.md 仅 12 例，缺 FD 与认证类实战

## 候选文章（5 条）

### 1. CiA 1301 (CANopen FD) 对 CiA 301 的权威差异
- 链接：http://cannewsletter.org/engineering/standardization/201207_injector-and-scanner-communication_bayer_cnlm/
- 来源：CAN Newsletter 杂志（Bayer 撰，2020-12）
- 摘要：CiA 1301 于 2017 发布；USDO 取代 SDO，PDO 扩到 64 B，EMCY 8→20 B。
- 关键实战点：① 不兼容 CiA 301，换 CAN FD 必须换协议栈 ② USDO ID 固定 600h+客户端 / 580h+服务端 ③ PDO 映射粒度由 1 bit 改 1 byte
- 推荐动作：扩 deep-dive（新建 bus/canopen-fd.md）

### 2. CANopen FD 设备必须过 CiA 一致性测试
- 链接：https://can-cia.org/s/vgt7S
- 来源：CiA 官方
- 摘要：PEAK PCAN-MicroMod FD DR-1 双栈 IO，旋钮选 Node-ID 与位定时。
- 关键实战点：① CANopen FD 须过 CiA 一致性测试，经典 CANopen 免 ② 同设备可跑 CiA 1301 或 301 ③ XDD 按 CiA 1311 生成
- 推荐动作：入主题笔记 + 写实战案例

### 3. Beckhoff EL6751 网关 SDO 写 0x06020000 失败
- 链接：https://industrialmonitordirect.com/nl/blogs/knowledgebase/el6751-canopen-gateway-resolving-0x06020000-sdo-filter-error
- 来源：Industrial Monitor Direct 知识库
- 摘要：EL6751-0010 挂 CODESYS Control for Linux，EtherCAT 全绿但网关收不到 CAN 帧，转 PASSIVE。
- 关键实战点：① 根因缺 CAN Rx filter table（CoE 0x8001）② 受影响 fw≥17/Rev≥0022，3.5SP15 前用 inline ST 绕 ③ 与本库案例 2 同码不同根因
- 推荐动作：写实战案例（入 failure-cases 第 13 例）

### 4. NMT 与心跳实战：汇川 IS620P / 步科
- 链接：https://blog.csdn.net/weixin_34241036/article/details/93389615
- 来源：CSDN
- 摘要：NMT 命令发十几遍仍卡 Initialization(0x01)；或设备在线心跳却断，量电阻电压正常。
- 关键实战点：① 心跳消费超时须按周期 3 倍设，覆盖 PLC 重启窗口 ② 卡 0x01 时查 0x1017/0x1005 而非线缆 ③ 物理层→链路层→应用层逐层定位
- 推荐动作：写实战案例 + 扩 deep-dive

### 5. 工业现场避坑：对象字典配置 5 个错误
- 链接：https://blog.csdn.net/time3/article/details/154806177
- 来源：CSDN
- 摘要：焊接产线 PDO 映射错致机械臂停滞 6 小时；TPDO1 误配 0x182（应 0x183）。
- 关键实战点：① 映射项 32bit=索引/子索引/长度，0x60640120 写错错位 4 字节 ② EDS 跨厂商单位不一（0x607A 1/100mm vs 1/1000mm）③ pre-op 漏配 Inhibit Time 负载瞬时 95%
- 推荐动作：写实战案例（数字需核实后再入）

## 排除/待核
- 排除：tsight.io（AI 农场）、boardor.com（编号不可查）、kaifayun.com、hqwc.cn；待核：FD 波特率 5/8 Mbit/s

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
