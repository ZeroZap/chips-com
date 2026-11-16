# USB 3.x / Thunderbolt 候选素材 @ 2026-11-11 00:05

## 协议速览
- 是什么：5/10Gbps 差分对总线，USB4/TB4 共用 40Gbps 链路层。
- 解决什么：产线相机/存储采集稳定性，掉速复位吃节拍。
- 跟 L4 主题的关联：库内 USB 8 篇非 DFU 笔记，**Thunderbolt/USB4 为 0 篇**；failure-cases 无跨接口共因。

## 候选文章（5 条）

### 1. 无人机 GPS 被 USB3.0 相机噪声淹没
- 链接：https://blog.szobov.ru/2018/12/24/try-to-avoid-using-usb3.0-and-2.4hz-radio-like-gps/
- 来源：实战博客（PX4+oCam 相机）
- 摘要：QGC 显示 16+ 卫星正常，一开相机工作 GPS 全丢，换 USB2.0 线恢复。
- 关键实战点：①USB3.0 差分对辐射压垮 2.4GHz 前端，屏蔽无效；②2.4GHz 电台旁禁用 USB3.0 存储/相机。
- 推荐动作：写实战案例（补 failure-cases 第 21 例）

### 2. MLCC 去耦引发 USB3.0 掉速 + 千兆丢包 + I2S 爆音
- 链接：https://blog.csdn.net/weixin_29174013/article/details/164982764
- 来源：CSDN · 多接口 Debug 实录
- 摘要：USB3.0 从 5Gbps 掉到 480Mbps，千兆口高负载丢包爬升，I2S 间歇爆音。
- 关键实战点：①三接口同坏是全局劣化而非单接口 bug；②根因在 MLCC 去耦选型与布局。
- 推荐动作：写实战案例（跨接口共因，库内空白）

### 3. USB3.0 眼图压模板：电源正常但 SI 不合格
- 链接：http://www.ictest8.com/a/technology/2023/02/USB.html
- 来源：专业集成电路测试网 · 实测
- 摘要：先测电源再测 SI，电源无问题但眼图压到内模板。
- 关键实战点：①「电源 → 眼图」顺序快速切分问题域；②内模板违规即量产不合格。
- 推荐动作：入主题笔记（产线 SI 排查流程）

### 4. Thunderbolt 4 做 P2P 备份比旧机慢一倍：BER 定位
- 链接：https://www.allion.com.cn/tech_syst_thunderboltcab/
- 来源：百佳泰 Allion（Thunderbolt 认证实验室）
- 摘要：新购 TB4 笔电做 P2P 备份，耗时多一倍引发客诉，BER 测到位错误。
- 关键实战点：①性能投诉根因常在硬件 SI 而非软件；②BER 比体验指标更早暴露位错误。
- 推荐动作：扩 deep-dive（新建 thunderbolt-usb4.md，补 0 篇空白）

### 5. 工业相机 USB3.0 丢帧：>3m 线缆叠加变频器现场
- 链接：https://www.zytino.com/NewsDetail/8106452.html
- 来源：智云腾科技（厂商案例）
- 摘要：安防集成商用「工业级」USB3.0 线连 4K 相机，丢帧、未识别、日志报 USB 链路复位。
- 关键实战点：①线长 >3m 且现场有变频器/伺服电机 → EMI 耦合；②「USB 链路复位」= SI 失效日志特征。
- 推荐动作：写实战案例（厂商软文，需核实）

## 备选
- 8b/10b 在 USB3.0 的利用（link training/LFPS）https://umatechnology.org/taking-full-advantage-of-8b-10b-encoding-in-your-usb-3-0-design/
- Type-C 线缆致显示异常 https://www.allion.com.cn/tech_cabc_screen_abnormality/

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
