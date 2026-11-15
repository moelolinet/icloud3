# iCloud3 中文本地化（Chinese localisation）

iCloud3 原本只有英文界面。这里加了一层**显示层翻译**：界面显示中文，但配置值、
实体 ID、内部比较用的文本全部保持英文。

## 目录

| 文件 | 说明 |
|---|---|
| `core.py` | 查表核心：语言判定、文本查表、占位符校验、容错回退 |
| `display.py` | 表单显示助手：`option_list` / `option_dict` / `multi_select` / `header_checkbox` |
| `sensors.py` | 传感器友好名称翻译（`Gary iPhone Battery` → `Gary iPhone 电池`） |
| `event_log.py` | Event Log 消息翻译（模板匹配 + 颜色前缀保留） |
| `catalog.json` | 英文原文 → 中文（890 条，自动生成，勿手改） |
| `event_log_zh.json` | Event Log 模板 → 中文（239 条，自动生成，勿手改） |

`translations/zh-Hans.json`、`translations/zh-Hant.json` 由 `en.json` 生成，
供 Home Assistant 自己渲染的标题/描述/错误提示使用。

## 语言如何决定

```
1. 配置项 language（zh / en / auto）
2. auto（默认）时跟随 Home Assistant 自身的语言设置
```

只要 HA 是中文（`zh-Hans` / `zh-CN` …），iCloud3 就显示中文；把 HA 切回英文，
iCloud3 立刻恢复英文。所有查表都是容错的：找不到译文、占位符不一致、文件缺失，
都会安静地回退成英文，不会影响启动。

## 覆盖范围

**已翻译**

* 安装向导（添加集成）、重新认证流程
* 左侧 Configure 菜单的两个页面（菜单项 + 操作项）
* 全部 20 个 Configure 表单：标题、说明、字段名、字段说明、下拉选项、多选项
* HA Repairs 修复流程（`issues.*`）
* 服务（Actions）的名称、说明与字段
* 传感器友好名称
* Event Log 卡片上的按钮/操作菜单
* Event Log 消息（239 个模板）

**有意保留英文**

| 内容 | 原因 |
|---|---|
| `entity_id`、`unique_id`、配置文件名/键 | 改了会破坏已有的实体与自动化 |
| 设备名、区域名、Apple 账户、图片路径 | 用户自己的数据 |
| 服务 `command` 取值、Event Log 内部记录 | 代码按英文比较；导出日志保持英文便于排查 |
| 少数「整段说明当开关」的复选项 | `cv.multi_select` 无 label/value 分离，提交值就是文字 |
| 配置参数说明里出现的技术标识 | 保持与官方文档一致 |

## 维护

翻译源在 `tools/i18n/*.json`，改完用 `tools/i18n/gen_*.py` 重新生成，
再跑 `pytest tests` 与 `tools/i18n/audit_round1.py`。详见 `tools/i18n/README.md`。
