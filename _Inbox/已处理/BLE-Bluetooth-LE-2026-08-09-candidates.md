# BLE 候选素材 @ 2026-08-09 00:00

## 协议速览
- 是什么：低功耗短距无线（2.4 GHz），GATT/ATT 服务模型，SMP 安全配对
- 解决什么：IoT/可穿戴/手机的低功耗互联
- 跟 L4 主题的关联：IoT/可穿戴首选无线协议，配对/重连/掉线实战排错是高价值素材

## 候选文章（4 条）

### 1. RTL8762 低功耗蓝牙配对失败诊断
- 链接：https://ask.csdn.net/questions/9119395
- 来源：CSDN 问答（高赞采纳答案）
- 摘要：Realtek RTL8762 量产/调试高频问题——配对请求无响应、连接立即断、绑定写 NVDS 失败。围绕 SMP 状态机，覆盖 Security Level/IO Capability/MITM/Key Distribution/NVDS 异常，附诊断路径图。
- 实战点：7 项 SM 配置错误表；NVDS BD_ADDR 校验片段；4 个必须注册的 SMP 事件回调
- 推荐动作：**扩 deep-dive**——嵌入式 BLE 排错标准模板

### 2. BluetoothGatt DeadObjectException 重连实战
- 链接：https://blog.csdn.net/ming0gy/article/details/129835837
- 来源：CSDN 技术博客
- 摘要：Android BLE 典型坑——先连成功→断开→蓝牙重开后服务未绑定就 connect，触发 error 133。给出"断开→close→sleep 500→扫描→connectGatt"修复模板。
- 实战点：蓝牙重开后必须先扫描再 connect（顺序敏感）；error 133 根因是 service discovery 未完成；disconnect/close 顺序与 null 释放
- 推荐动作：**写实战案例**——Android BLE Host 重连标准范式

### 3. badgemagic-firmware 自定义 BLE 服务
- 链接：https://blog.csdn.net/gitblog_00062/article/details/153496821
- 来源：CSDN（开源 LED 徽章固件 badgemagic-firmware）
- 摘要：CH582（RISC-V + BLE + USB）固件实战——添加自定义 service UUID、注册 characteristic 读写回调；USB 复合设备（CDC + HID）描述符配置；BLE_DEBUG 宏日志；Charlieplexed LED 阵列。
- 实战点：自定义 service 文件结构（profile/setup.c 注册）；USB 复合设备描述符字段；BLE+USB 双协议 MCU 选型（CH582 国产替代）
- 推荐动作：**入主题笔记**——国产 RISC-V BLE+USB 实战参考

### 4. Dell 蓝牙省电导致断连
- 链接：http://www.dell.com/support/article/tw/zh/twdhs1/sln119257/zh/
- 来源：Dell 官方支持文章（000122996）
- 摘要：蓝牙装置随机与 Windows 断线——根因是 Windows 电源管理允许关蓝牙适配器省电。修复：设备管理器→蓝牙适配器属性→电源管理→取消勾选"允许计算机关闭此装置以节省电源"。
- 实战点：Win11 蓝牙电源管理路径；Host OS 电源策略对无线稳定性的隐性影响；跨平台调试需考虑 Host 电源
- 推荐动作：**扩 deep-dive**——"Host 电源策略影响 BLE 链路"反例

## 下一步
等你 review 后决定：激活 / 改写 / 丢弃
