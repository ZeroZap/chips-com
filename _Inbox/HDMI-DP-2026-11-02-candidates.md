# HDMI 2.1 / DP 2.0 候选素材 @ 2026-11-02 00:00

## 协议速览
- 是什么：HDMI 2.1 用 FRL（4 lane 并行、时钟嵌入）达 48Gbps；DP 2.0 用 UHBR20 达 20Gbps/lane
- 解决什么：8K/4K120+ 高刷传输；瓶颈转向链路训练与信号完整性
- 关联：hdmi-edp-deep-dive 427 行但 FRL/SCDC 全空，且无 failure-cases

## 候选文章（5 条）

### 1. NVIDIA 论坛：DPMS 后 FRL 训练失败致 5K 消失
- 链接：https://forums.developer.nvidia.com/t/nvidia-driver-fails-to-detect-5120x2160-resolution-after-display-power-events-on-samsung-odyssey-g75f-via-hdmi-2-1/360651
- 来源：NVIDIA 开发者论坛
- 摘要：DPMS 后 FRL 训练失败回退 TMDS，5K 模式消失。
- 关键实战点：① 内核日志 "HDMI FRL link training failed" 是根因线索 ② 失败即回退 TMDS，2.0 带宽撑不住 5K ③ 重插显示器可恢复
- 推荐动作：写实战案例 → 新建 hdmi-failure-cases.md

### 2. Intel KB：FPGA Sink IP 间歇性 FRL 训练失败
- 链接：https://www.intel.com/content/www/us/en/support/programmable/articles/000075660.html
- 来源：Intel 官方支持文档
- 摘要：Quartus 19.4/20.4 起偶发 Rx 训练失败，根因是 FRL lock 抖动后未重做符号对齐。
- 关键实战点：① 根因=FRL lock 不稳后未正确 symbol re-alignment ② 修复版本 Quartus 21.1 ③ 间歇性难复现，先查工具版本
- 推荐动作：入主题笔记 → hdmi-edp-deep-dive 补 IP 缺陷型失败

### 3. CSDN：HDMI 2.1 FRL Link Training 状态机与 16b18b
- 链接：https://blog.csdn.net/ypcan/article/details/163700060
- 来源：CSDN FPGA 工程师原创
- 摘要：逐节拆 LTS 状态机与编码，含 Sink 侧寄存器级排障表。
- 关键实战点：① LTS:1→2→3→4→P/L，失败退路只有降速或回 TMDS ② 卡 FLT_ready 查 +5V/HPD（SCDC 寄存器清零）③ 200ms 超时先降一档速率验线缆
- 推荐动作：扩 deep-dive → 补 FRL 状态机与 SCDC 寄存器

### 4. CSDN：8K 终端 HDMI 2.1 认证连续三次失败
- 链接：https://blog.csdn.net/weixin_30700095/article/details/157777508
- 来源：CSDN 硬件实战手记
- 摘要：四个工程断层叠加致 6GHz 眼图闭合、CDR 失锁。
- 关键实战点：① 蚀刻因子 0.85 使线宽 5.2→4.4mil，Z₀ 抬升 6.5Ω ② 参考平面被掏 35mil 槽 ③ USB 3.2 以 0.8mm 间距掠过 TX1
- 推荐动作：写实战案例 → hdmi-failure-cases.md SI/产线类

### 5. UniGraf：把 HDMI/DP 问题拆成可复现的产线测试流程
- 链接：https://saniffer.cn/4/2/2226487
- 来源：Saniffer/UniGraf FAE
- 摘要：UCD500 覆盖 DP 2.1 CTS 与 UHBR20，含 DPCD/EDID 在线编辑。
- 关键实战点：① 切 8.1G→5.4G 编码在 128b/132b 与 8b/10b 间切换 ② RX 侧改能力写回 DPCD 可模拟各种 Sink ③ 车载非标时序需自定义 Timing
- 推荐动作：入主题笔记 → 补 DP 2.0/UHBR20 产线验证

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
