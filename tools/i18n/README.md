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

## 三轮排查结果（首次交付）

| 轮次 | 内容 | 结果 |
|---|---|---|
| 第 1 轮 | 静态审计（编译 / JS / 键 / 占位符 / 选项值） | 53 张表、872 条文本，0 问题 |
| 第 2 轮 | 真实 HomeAssistant 渲染 20 个 Configure 表单 | 20/20 通过 |
| 第 3 轮 | 英文模式与原始版本（git HEAD）逐字段对比 | 0 差异 |

首轮发现并修复的真实缺陷：

1. 英文模式下 `option_dict()` 返回 dict（原代码传的是 list）→ 表单无法渲染
2. `TRAVEL_TIME` 等多选默认值仍是英文、选项已变中文 → 不改动直接提交会被 HA 拒绝
3. Event Log 的 `^x^` 颜色前缀挡住消息匹配 → 警报/监视消息不翻译
4. 标题复选框（整段说明当成开关）被翻译后，提交值变成中文长句 → 保持英文

## 第二轮排查（deep review）

在真实 HomeAssistant（HA 2025.9）中逐表单比对「选项值 / 默认值」，并检查
Event Log 匹配器的边界与性能。结果：

| 检查 | 结果 |
|---|---|
| 20 个表单 × 71 个下拉字段，中英文默认值/选项值 | 完全一致（无中文特有缺陷） |
| 197 条带 `{v}` 的 Event Log 模板 | 全部翻译且动态值保留 |
| 239 条模板的占位符数量 | 全部一致 |
| 模板歧义（同一消息匹配多条） | 0 条错配 |
| `action_fname` 回传后端 | 始终英文 |

本轮发现并修复的真实缺陷：

1. **仪表板「主视图设备」默认值被翻译**
   `all-devices` / `result-summary` / `track-details` 等**提交值**被误收进翻译表，
   中文模式下默认值变成「所有设备」，与选项键不匹配 → 表单提交被拒。
   已在 `gen_catalog_json.py` 增加 `CODE_VALUES` 防护名单，避免再次误收。

2. **Event Log 正则灾难性回溯**
   模板里连续多个 `(.*?)` 在长文本上指数级回溯：20KB 未匹配消息耗时 **14 秒**，
   会阻塞 HA 事件循环。改为 `(.+?)` + 字面片段预筛 + 4000 字符上限，
   同一场景降到 **0.00 ms**。

3. **Event Log 卡片回传中文标签**
   卡片把 `option.innerText` 当 `action_fname` 传给后端。中文界面下会传中文，
   而后端按英文常量比较。现在每个 option 记录英文 `dataset.label`，
   回传用 `ic3EnglishLabel()`。

4. **两条 Event Log 模板占位符数量不匹配**（译文多插 `{v}`）→ `.format()` 抛异常、
   消息回退英文。已修正。

5. **一处修复流程说明残留整句英文**（`issues.device_reassigned`）→ 已补全翻译。

## 第三轮排查（回归）

| 检查 | 结果 |
|---|---|
| `pytest tests` | 48 passed |
| `ruff check i18n`（F/B/B9/SIM/RET/C4/PIE） | 全部通过 |
| `audit_round1.py` 静态审计 | 53 张表，0 问题 |
| 翻译数据完整性（872 条 + 879 词条 + 239 模板） | 0 条残留英文句、0 条占位符不一致 |
| 传感器中文名重名冲突 | 与英文完全相同的 9 组（entity_id 不受影响） |
| Event Log 卡片 JS 语法与边界 | `node --check` 通过；null/undefined/无 language 均安全 |
