# EtherCAT 候选素材 @ 2026-11-16 12:00

## 协议速览
- 是什么 / 解决什么：以太网帧飞过式处理 + DC 分布式时钟，μs 级周期多轴同步
- L4 关联：库内 ethercat-deep-dive.md 仅 4.3 KB，缺 failure-cases / practical、认证 / 冗余 / FSoE

## 候选文章（5 条）

### 1. LAN9252+STM32 从站硬件与 SPI 驱动实战
- 链接：https://blog.csdn.net/weixin_29188043/article/details/166354502
- 来源：CSDN（调试实录）
- 摘要：坑在物理层与驱动层，非协议栈。
- 关键实战点：
  ① 必须 SPI Mode 3，误设 Mode 0 读值全 0/0xFFFF
  ② CS# 拉低后等 100ns；建议 ≤12MHz，低于 1MHz 失步
- 推荐动作：扩 deep-dive + 写实战案例

### 2. 从站掉线与 Hot Connect 拓扑恢复 ETG.1020
- 链接：https://industrialmonitordirect.com/blogs/knowledgebase/ethercat-slave-disconnection-hot-connect-and-topology-recovery
- 来源：Industrial Monitor Direct
- 摘要：摘一个节点整段 WKC 归零降级。
- 关键实战点：
  ① 拔一个从站即整段失效，帧回不到主站
  ② 扫描式恢复 200–800 ms，期间保持安全态输出
  ③ TwinCAT 3 build 4020 起才支持 Hot Connect；NI 不支持
- 推荐动作：新建 ethercat-failure-cases

### 3. ETG.7010 一致性指南与 CTT 认证
- 链接：https://ethercat.org/download/documents/ETG.7010_V1i2i0_EtherCATConformanceGuide.pdf
- 来源：ETG 官方 PDF
- 摘要：厂内自测与官方证书是两件事。
- 关键实战点：
  ① 厂商须持 Vendor ID 并订阅 CTT，上市前须过测
  ② Plug Fest 不发证，仅 ETC 官方测试发 Conformance Certificate
  ③ 证书不过期，新版本仍须自行回归；国内 ETC 在北航 LNC
- 推荐动作：扩 deep-dive（认证一节）+ 入主题笔记

### 4. 主站冗余与环网线缆冗余叠加
- 链接：https://industrialmonitordirect.com/blogs/knowledgebase/configuring-codesys-master-redundancy-with-ethercat-ring-topology
- 来源：Industrial Monitor Direct
- 摘要：两套冗余机制叠加有交互副作用。
- 关键实战点：
  ① 双主同时 ACTIVE 约 30 ms，从站掉 SAFE-OP，报 0xEA04
  ② 非对称心跳防误切：主机 6×周期+HoldDown 50 ms，备机 10×周期+Confirm 100 ms
- 推荐动作：扩 deep-dive（冗余一节）+ 写实战案例

### 5. FSoE 黑色通道与锂电涂布线定位实录
- 链接：https://blog.csdn.net/weixin_29326909/article/details/165287544
- 来源：CSDN（RK3568+Linux 6.6.119）
- 摘要：时间戳+WC 双校验 SIL2/SIL3，30 分钟定位。
- 关键实战点：
  ① CRC-0x1021 三重校验，字节序与初始值最易错
  ② 用 IGC 驱动替代 SOEM 做实时内核配置
  ③ FSoE.xml 超时参数须按现场调优
- 推荐动作：入 deep-dive（安全一节）+ 写实战案例

## 排除/待核
- 排除：tsight.io、hqwc.cn（AI 农场）、rorosafe.in、fixfaults.com
- 备选：国产 ESC LY-E252 替 LAN9252（CSDN 521）
- 待核：候选 3 比对 ETG.7010 修订号

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
