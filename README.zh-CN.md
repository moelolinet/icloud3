# <img width="32" height="32" src="https://brands.home-assistant.io/icloud3/icon.png"> iCloud3 Apple 设备追踪

[![HACS](https://img.shields.io/badge/HACS-%E8%87%AA%E5%AE%9A%E4%B9%89%E5%AE%89%E8%A3%85-steelblue.svg)](https://github.com/hacs/integration) ![Type](https://img.shields.io/badge/%E7%B1%BB%E5%9E%8B-%E8%87%AA%E5%AE%9A%E4%B9%89%E7%BB%84%E4%BB%B6-steelblue.svg)

[English](README.md) | **简体中文**

本仓库基于上游 iCloud3 v3.8.0-beta.4.1，增加了完整的中文界面。当 Home Assistant 使用中文
（`zh-Hans` / `zh-CN` …）时，iCloud3 会自动显示中文；切回英文后立即恢复英文界面。

已翻译：安装向导、Apple 账户认证、Configure 全部 20 个配置画面（含字段说明与下拉选项）、
HA Repairs 修复流程、Actions 服务、传感器名称、Event Log 卡片按钮、Event Log 运行消息。

不翻译（有意保留英文）：`entity_id`、`unique_id`、配置键、设备名/区域名/账户等用户数据、
服务 `command` 取值，以及导出的日志（便于排查问题）。

实现方式与维护方法见 [`custom_components/icloud3/i18n/README.md`](custom_components/icloud3/i18n/README.md)
与 [`tools/i18n/README.md`](tools/i18n/README.md)。翻译只作用于「显示」，不会改动配置文件内容
或已存在的实体。

---

iCloud3 是一个设备追踪自定义组件，用于追踪 iPhone、iPad 与 Apple Watch。家人共享列表中的设备
以及通过 Home Assistant 移动端 App 接入的设备都可以被追踪。设备会向 Apple iCloud 定位服务请求
位置数据，同时监控移动端 App 的各类传感器与触发器，从而得出设备的电量、位置、距离、行程时间
以及到家状态。

---

## iCloud3 的组成部分

iCloud3 自定义组件由 4 个主要部分构成，分别负责配置、追踪与呈现设备位置信息：

- **iCloud3 设备追踪器** —— 监控设备位置，决定下一次定位的时机，并更新全部传感器。
- **Event Log（事件日志）** —— 显示设备位置、位置变化是如何处理的、定位结果、错误以及启动信息。
- **Configure 设置** —— 配置已追踪设备、Apple 账户、iCloud3 仪表板、传感器及其它参数。
- **Dashboard Builder（仪表板生成器）** —— 以多种版式生成包含追踪结果、电量信息和 Event Log 的
  iCloud3 仪表板。生成后可用 Home Assistant 仪表板编辑器自定义，其中的条目与视图也可以复制粘贴到
  其它仪表板。Dashboard Builder 本身就是 *Configure 设置* 中的一个画面。

## iCloud3 文档

- 介绍 iCloud3 的众多功能与组件
- 重点说明各配置画面与参数
- 提供示例画面、自动化与脚本
- 完整的用户手册见 [此处](https://gcobb321.github.io/icloud3_docs/#/)

---

## 首次配置 iCloud3

整套流程已经尽量自动化，步骤是：安装 iCloud3 → 添加 Apple 账户 → 完成 Apple 账户登录认证 →
导入 Apple 设备 → 生成 iCloud3 仪表板 → 结束 Configure 会话 → 开始追踪设备。

![](https://gcobb321.github.io/icloud3_docs/screens/apple_acct/apple-acct-auth-import-devices-steps.png)

1. 在 *HA 设置 → 设备与服务 → 添加集成* 中添加 iCloud3，选择 *iCloud3 Apple Device Tracker*
2. 在 iCloud3 集成卡片上点击「配置」齿轮图标
3. 在 *更新 Apple 账户* 画面输入用户名（邮箱）与密码，登录 Apple 账户；受信任设备会收到登录通知
4. 在 *Apple 账户登录认证* 画面按提示输入 6 位验证码，或开始安全密钥认证流程
5. 在 *导入 Apple 设备* 画面，用第 3 步下载的设备信息创建 iCloud3 设备
6. 在 *iCloud3 设备* 画面检查并修改需要调整的配置（名称、头像、移动端 App 绑定等）
7. 退出 *iCloud3 Configure 会话* 后，会以你的设备生成 *iCloud3 仪表板*，它被加入 *HA 侧边栏*
   并显示为云朵图标
8. 打开 *iCloud3 仪表板*。若一切正常，应能看到设备与 Event Log

![](https://gcobb321.github.io/icloud3_docs/screens/dashboard-allinfo-summary.png)

> 该流程的详细说明见 [iCloud3 文档](https://gcobb321.github.io/icloud3_docs/#/chapters/1_installing?id=configure-icloud3-for-the-first-time)。

---

## iCloud3 主要特性

Home Assistant 自带官方的 iCloud 组件，但 iCloud3 的能力远超于它。以下为主要特性。

### 通用

- **HA 集成** —— iCloud3 是 Home Assistant 自定义集成，在 *HA 设置 → 设备与服务 → 集成* 中完成
  搭建与配置。
- **配置即时生效** —— 各类配置画面在线修改参数，无需重启 HA 即可生效。
- **更新与重启** —— iCloud3 可以独立重启，无需重启整个 Home Assistant。
- **重启后恢复状态值** —— 重启后当前的 device_tracker 与传感器实体状态会被恢复。属性不会恢复，
  而是在第一次追踪事件时重新生成。
- **device_tracker 与传感器实体** —— iCloud3 设备与传感器都是 Home Assistant 实体，可在
  *更新 iCloud3 设备* 与 *传感器* 配置画面中新增、删除和修改。
- **Dashboard Builder** —— 首次安装 iCloud3 集成时，会自动把多种版式的 iCloud3 仪表板加入
  Home Assistant。

### 设备追踪

- **追踪 iPhone、iPad 与 Apple Watch** —— 对 iDevice 进行主动追踪或被动监控。
- **位置数据来源** —— 位置数据来自 iCloud 账户与 HA 移动端 App。
- **多个 Apple 账户** —— 可以同时追踪多个 Apple 账户下的设备（你自己的、配偶的、孩子的、
  朋友的、亲属的等）。
- **监控移动端 App 活动** —— 每 5 秒检查一次位置与触发器变化。
- **改善 GPS 精度** —— 消除 GPS 漂移导致的错误离开区域判定。
- **主动追踪设备** —— 根据设备距离家或其它区域的距离，按一定间隔请求位置。
- **被动监控设备** —— 设备自身不请求位置，而是在其它被追踪设备请求位置时一并更新。

### 特殊区域追踪

- **静止区域** —— 设备一段时间未移动（医院、商店、朋友家）时会创建动态 *静止区域*，有助于省电。
- **区域监控** —— 设备更新时会显示各区域内的设备数量。
- **区域距离传感器属性** —— 显示到家区域中心与边界的距离、到其它区域的距离以及到其它设备的距离。
- **从多个区域追踪** —— 追踪结果（位置、行程时间、距离、预计到达时间等）可以基于家区域或其它
  区域（公司、第二住处、父母家等）报告。
- **进入区域延迟** —— 延迟处理「进入区域」触发器，避免只是路过就被判定。
- **未使用移动端 App 设备的离开区域** —— 不使用（或无法使用，如 Apple Watch）移动端 App 的设备，
  在检测到附近另一台设备离开区域时也会响应离开事件。
- **主家区域** —— 可以为设备指定另一个区域作为主区域，并据此报告追踪结果。适用于有两个住处、
  在外地度假、在父母家触发自动化等场景。

### 高级功能

- **电量状态** —— 追踪事件中从 iCloud 数据更新电量与充电状态，移动端 App 则每 5 秒更新一次。
- **Waze 路线服务** —— 到家或到其它被追踪区域的行程时间与距离由 Waze 提供。
- **Waze 路线历史数据库** —— Waze 返回的行程时间与距离会保存到本地数据库，设备回到曾去过的位置时
  直接复用。
- **区域活动日志** —— 可以为每次进入区域记录日志。日志文件为 CSV 格式，可导入表格软件，用于
  报销、行程回顾、设备位置监控等。
- **附近设备** —— 显示与其它设备的距离，并参与追踪结果的计算。
- **本地时区** —— 事件时间默认使用 HA 服务器所在时区；身处其它时区时，也可以按所在时区显示。
- **丰富的传感器** —— 会创建并更新大量传感器，涵盖距离、行程时间、轮询数据、电量状态、区域属性等。
  只需勾选你要用的那些。

### 以及……

- **Event Log** —— 每台被追踪与监控设备的当前状态和历史事件都显示在 iCloud3 Event Log 自定义
  Lovelace 卡片上，包括设备配置、错误与告警、附近设备、追踪结果、调试信息以及定位请求结果。
- **详尽的文档** —— iCloud3 用户手册介绍了三大组成部分、如何上手、如何从 v2 迁移、如何安装集成、
  每个画面与特殊功能、用于请求更新/定位 iPhone/发送通知告警的服务调用，以及「到家自动开车库门」
  等自动化示例。
- **更多** —— 查阅下列文档，了解它们能否帮助你追踪与监控 iPhone、iPad 与 Apple Watch 的位置。

---

## 重要链接

- **iCloud3 用户手册** —— 内容非常详尽，见 [此处](https://gcobb321.github.io/icloud3_docs/#/)

- **iCloud3 GitHub 仓库** —— 上游主仓库见 [此处](https://github.com/gcobb321/icloud3)

- **iCloud3 开发版 GitHub 仓库** —— 用于尚未发布的 beta 变更，见 [此处](https://github.com/gcobb321/icloud3_v3)

<a href="https://www.buymeacoffee.com/gcobb321" target="_blank"><img src="https://gcobb321.github.io/icloud3_docs/images/buymeacoffee-docs-button.png"/></a>

---

*Gary Cobb，即 GeeksterGary（上游作者）；本仓库仅在其基础上增加中文本地化。*
