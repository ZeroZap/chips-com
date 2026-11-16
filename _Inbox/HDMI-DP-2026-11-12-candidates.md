# HDMI 2.1 / DP 2.0 候选素材 @ 2026-11-12 00:00

## 协议速览
- 是什么 / 解决什么：HDMI 2.1 FRL 48Gbps、DP 2.0 UHBR20 ~77.6Gbps；瓶颈转向 EDID/DPCD 协商与 DRM 读取
- 跟 L4 主题的关联：hdmi-edp 仅 3 篇笔记（12.4 KB，6 月停更）、无 failure-cases；本轮补 DP2.0/MST/内核 EDID

## 候选文章（5 条）

### 1. 嵌入式显示模组集成实战：从 HDMI/Type-C 接口到 Linux 驱动调试全解析
- 链接：https://blog.csdn.net/weixin_30363285/article/details/163387086
- 来源：CSDN（嵌入式 / RK3588）
- 摘要：模组选型到点屏，EDID 非标靠设备树强刷。
- 关键实战点：
  ① EDID 缺失 → 设备树强刷屏参绕过 DDC
  ② HPD 时序不稳 → 内核刷 ddc i2c transfer failed
  ③ "接口齐"≠能点亮，先拆供电/触摸/视频
- 推荐动作：扩 deep-dive → 补模组集成 + HPD 时序

### 2. DisplayPort 2.0 协议深度解析：链路训练与工程实现要点
- 链接：https://blog.csdn.net/weixin_27014595/article/details/164418244
- 来源：CSDN（DP2.0 规范 + FPGA 视角）
- 摘要：以 FPGA 视角倒推 1143 页规范怎么读。
- 关键实战点：
  ① 128b/132b、UHBR10/13.5/20 三档速率 + DSC/Panel Replay
  ② sink 的 I2C 地址当 DPCD 地址 → EDID 正常但训练恒失败
  ③ 以 DPCD 寄存器为索引倒查，换档连带 FEC/均衡
- 推荐动作：扩 deep-dive → 补 DP2.0 段（库内全空）

### 3. watch_displays blocks in DRM EDID read and prevents suspend with EVDI
- 链接：https://github.com/rockowitz/ddcutil/issues/659
- 来源：GitHub（ddcutil #659）
- 摘要：EDID 读线程卡死，连带挂起失败。
- 关键实战点：
  ① watch_displays 卡 D 态读 EDID sysfs，冻不住 → 挂起超时
  ② 栈顶 drm_edid_connector_property_show → __mutex_lock
  ③ 深睡失败回退 s2idle，三次复现
- 推荐动作：写实战案例 → 新建 hdmi-edp-failure-cases.md 首发

### 4. [PATCH v3] drm/i915/hdmi: preserve cached EDID on DDC failure
- 链接：https://lkml.iu.edu/2610.3/05729.html
- 来源：LKML（dri-devel，Jani Nikula 评审）
- 摘要：DPMS 下读失败清缓存，画面回落 1024x768。
- 关键实战点：
  ① 显示器待机关 DDC/I2C 控制器，EDID 读回 -ENXIO
  ② 根因是"读失败即清缓存"而非读失败
  ③ connector 被 force 时无热插拔沿，需手动 probe
- 推荐动作：入主题笔记 → 补 EDID 缓存语义 + fallback 模式

### 5. DP MST 菊花链第二台不亮或睡醒掉线：接口、开关与上电时序
- 链接：https://www.renrendaima.com/article/16421.html
- 来源：人人代码
- 摘要：多屏串联：第二台不亮与睡醒掉线。
- 关键实战点：
  ① 两个 DP 口常都是输入，只有 DP OUT 能下串
  ② OSD 的 MST/DP1.2 默认关闭 → 下游不枚举
  ③ 上电序：扩展坞→第一台→第二台→主机；HDR 抢带宽
- 推荐动作：入主题笔记 → 补 MST 拓扑与上电时序（库内全空）

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
