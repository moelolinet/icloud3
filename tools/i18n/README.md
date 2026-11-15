# iCloud3 中文支持构建工具（Chinese localisation build tools）

这些脚本生成随集成一起发布的翻译资源，以及验证脚本。

## 生成资源

| 文件 | 说明 |
|---|---|
| `mt.json` | `en.json` 叶子文本 → 中文（人工复核后的缓存） |
| `mt_ui.json` | 代码里写死的界面文本 → 中文（菜单/动作/下拉选项/传感器名） |
| `ev_mt.json` | Event Log 消息模板 → 中文（`{v}` 表示动态内容） |
| `ev_templates.json` | 从代码里提取出的 Event Log 消息模板清单 |
| `gen_catalog_json.py` | 由 `mt*.json` 生成 `i18n/catalog.json`（运行时查表） |
| `gen_event_log.py` | 由 `ev_mt.json` 生成 `i18n/event_log_zh.json` |
| `gen_zh.py` | 由 `en.json` + `mt.json` 生成 `translations/zh-Hans.json`、`zh-Hant.json` |

改翻译的标准流程：

```
# 1. 只改这三个「人工可复核」的文件
#    mt.json / mt_ui.json / ev_mt.json

# 2. 重新生成运行时资源
python tools/i18n/gen_catalog_json.py
python tools/i18n/gen_event_log.py
python tools/i18n/gen_zh.py

# 3. 回归测试
pytest tests -q
```

## 验证脚本

| 文件 | 用途 |
|---|---|
| `audit_round1.py` | 全量静态审计：编译、JS 语法、键/占位符一致性、选项值必须是英文 |
| `render_forms.py <en\|zh>` | 在真实 HomeAssistant 里渲染全部 20 个 Configure 表单 |
| `compare_forms.py` | 对比中英文两次渲染：字段名与提交值必须完全一致 |
| `bootstrap.py` | 给上述脚本准备 `sys.path` 与两个可选 HA 依赖的替身 |

## 三轮排查结果

| 轮次 | 内容 | 结果 |
|---|---|---|
| 第 1 轮 | 静态审计（编译 / JS / 键 / 占位符 / 选项值） | 53 张表、872 条文本，0 问题 |
| 第 2 轮 | 真实 HomeAssistant 渲染 20 个 Configure 表单 | 20/20 通过 |
| 第 3 轮 | 英文模式与原始版本（git HEAD）逐字段对比 | 0 差异 |

三轮中发现并修复的真实缺陷：

1. 英文模式下 `option_dict()` 返回 dict（原代码传的是 list）→ 表单无法渲染
2. `TRAVEL_TIME` 等多选默认值仍是英文、选项已变中文 → 不改动直接提交会被 HA 拒绝
3. Event Log 的 `^x^` 颜色前缀挡住消息匹配 → 警报/监视消息不翻译
4. 标题复选框（整段说明当成开关）被翻译后，提交值变成中文长句 → 保持英文
