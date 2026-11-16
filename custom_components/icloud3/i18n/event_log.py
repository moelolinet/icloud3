"""Event Log 消息的中文显示层.

内部记录始终保留英文原文（去重、过滤、导出、Repairs 关联都依赖它），只在
「输出给 Event Log 卡片」时替换成中文。

实现要点（性能关键）：
    1. 先把模板按「字面片段」做**快速预筛**：消息里不含模板的全部字面片段就直接跳过，
       不做正则。这条把绝大多数模板的匹配成本降到一次 `in` 判断。
    2. 真正做正则时，动态段用 ``(.+?)`` 而**不是**多个连续的 ``(.*?)``；
       连续 ``(.*?)`` 在长文本上会指数级回溯（实测 20KB 文本可阻塞 10+ 秒）。
    3. 消息长度超过 ``MAX_TRANSLATE_LEN`` 时直接跳过翻译，避免异常长的日志卡住事件循环。
"""

from __future__ import annotations

import json
import logging
import os
import re

from .core import is_chinese

_LOGGER = logging.getLogger(__name__)

# 超长消息（异常日志、转储的 JSON 等）不翻译，直接原样显示
MAX_TRANSLATE_LEN = 4000

_LOADED = False
# (字面片段列表, 已编译正则, 中文模板)
_PATTERNS: list[tuple[list[str], re.Pattern, str]] = []


def _template_to_regex(template: str) -> re.Pattern:
    """把 ``"...{v}..."`` 模板编译成分组正则。

    动态段使用 ``(.+?)``；模板里的字面部分用 ``re.escape``。
    首尾锚定，``re.S`` 让 ``.`` 跨行（Event Log 里有多行消息）。
    """
    parts = template.split("{v}")
    body = "(.+?)".join(re.escape(part) for part in parts)
    return re.compile("^" + body + "$", re.S)


def _literal_parts(template: str) -> list[str]:
    """模板里的非空字面片段（用于快速预筛）。"""
    return [p for p in template.split("{v}") if p.strip()]


def _load() -> None:
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "event_log_zh.json")
        with open(path, encoding="utf-8") as file:
            table = json.load(file)
    except Exception as err:          # 缺文件时保持英文
        _LOGGER.debug("iCloud3 Event Log 中文表加载失败：%s", err)
        return

    # 长模板优先，避免短模板抢先匹配
    for english in sorted(table, key=len, reverse=True):
        try:
            pattern = _template_to_regex(english)
        except re.error:
            continue
        _PATTERNS.append((_literal_parts(english), pattern, table[english]))


# iCloud3 用 '^x^' 前缀给 Event Log 上色（^a^ 警报、^e^ 错误、^m^ 监视……）
_COLOR_PREFIX_RE = re.compile(r"^(?:\^[0-9a-zA-Z]\^)+")


def text(message: str) -> str:
    """把一条 Event Log 消息翻成中文；没有对应模板时原样返回。"""
    if not message or not is_chinese() or not isinstance(message, str):
        return message

    if len(message) > MAX_TRANSLATE_LEN:
        return message

    prefix = ""
    color = _COLOR_PREFIX_RE.match(message)
    if color:
        prefix = color.group(0)
        message = message[len(prefix):]

    _load()
    if not _PATTERNS:
        return prefix + message

    for literals, pattern, translated in _PATTERNS:
        # 快速预筛：字面片段必须全部出现，否则不可能匹配
        if any(part not in message for part in literals):
            continue
        found = pattern.match(message)
        if found is None:
            continue
        try:
            return prefix + translated.replace("{v}", "{}").format(*found.groups())
        except (IndexError, KeyError, ValueError):
            return prefix + message
    return prefix + message
