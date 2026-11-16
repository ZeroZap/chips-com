# Thread / Matter 候选素材 @ 2026-11-01 12:00

## 协议速览
- 是什么 / 解决什么：Thread = IPv6 低功耗 mesh，承载 Matter 应用，低功耗设备跨生态互联
- 关联：thread-*/matter-* 各 5 篇已有，FC 仅 9/8 例（无线最薄）

## 候选文章（5 条）

### 1. Nordic DevZone：nRF54L15 Matter 1.4.2 认证失败
- 链接：https://devzone.nordicsemi.com/f/nordic-q-a/125863/assistance-required-multiple-matter-certification-failures-on-nrf54l15-ncs-v3-1-1-matter-1-4-2/556309
- 来源：Nordic 官方 Q&A（xiongwei.wang）
- 摘要：真机自测套件失败，定位为 PICS 与实现不符。
- 关键实战点：① TC_IDM_10_4=PICS 有 BINFO.S.A0018 但设备缺 ConfigurationVersion ② TC_IDM_10_5=端点5 device type ID 非法 ③ TC_ACL_2_6=AccessControlEntryChanged 未进 read 响应
- 推荐动作：写实战案例 → matter-failure-cases.md 补 4 例

### 2. Allion Labs：智能家居互操作测试方法论
- 链接：https://www.allion.com/?p=45515
- 来源：CSA 首批 Matter 授权实验室
- 摘要：124 设备 / 443 手机 / 453 AP 实物库，9 测试域。
- 关键实战点：① 认证≠互操作 ② 现场故障五分类：配网失败 / 单生态行多生态不行 / multi-admin 加 fabric 后只能恢复出厂 / router 静默拦截 / OTA 后回归 ③ 缺陷归属：设备/生态/网络/规范
- 推荐动作：扩 deep-dive → matter-deep-dive.md 补「认证 vs 互操作」判据

### 3. Matter 1.4 UK 实测：12 台设备仍失败
- 链接：https://ocentrum.com/matter-14-uk-compatibility
- 来源：Smart Home Tech UK（6 周 34 台实测）
- 摘要：真实住宅实测，12/34 台不过关，多不标认证版本。
- 关键实战点：① Tapo L630 停在 1.1，加第二 admin 48h 内掉线 ② Meross MSS315 停在 1.2，能量上报空白 ③ SmartThings Station 重启后 Thread 凭证失效
- 推荐动作：入主题笔记 → matter-practical.md 补版本矩阵实证段

### 4. CSDN：Thread 实战（Mesh + BR）
- 链接：https://blog.csdn.net/weixin_34025051/article/details/93070336
- 来源：CSDN 工程师原创（含 BOM 与踩坑）
- 摘要：RPi 4B + nRF52840 dongle 跑 OTBR，双 DK 当端节点。
- 关键实战点：① 拔中继节点 mesh 自愈、端节点几乎无感 ② OpenThread 版本须匹配工具链，submodule 未更新会怪错 ③ Windows 开发需 WSL
- 推荐动作：扩 deep-dive → thread-deep-dive.md 补 OTBR 自建 + 抓包

### 5. connectedhomeip：Joint Fabric Guide（JCM）
- 链接：https://raw.githubusercontent.com/project-chip/connectedhomeip/master/docs/guides/joint_fabric_guide.md
- 来源：project-chip 官方仓库
- 摘要：双生态联合配网，含命令与校验点。
- 关键实战点：① 首个被配网者须是 jf-admin-app（pairing 加 --anchor true）② chip-cert 看 Subject 校验 Anchor/Admin CAT ③ ACL 校验：Subjects 应为 FFFFFFFDFFFF0001
- 推荐动作：入主题笔记 → 对照 matter-failure-cases.md 案例 4 补证

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
