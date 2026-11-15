"""Event Log 消息的中文显示层.

Event Log 的内部记录始终保留英文原文（去重、过滤、导出、Repairs 关联都依赖它），
只在「输出给 Event Log 卡片」时替换成中文。

做法：
    把 ``"Apple Acct > {v}, Login Failed"`` 这样的模板编译成正则，
    匹配实际消息并保留 {v} 对应的动态内容（设备名、时间、距离……）。

匹配不到的消息原样显示英文——这也保证了新加的日志不会因为没翻译而丢内容。
"""

from __future__ import annotations

import json
import logging
import os
import re

from .core import is_chinese

_LOGGER = logging.getLogger(__name__)

SPLIT = "\x00"          # 模板里 {v} 的位置
_LOADED = False
_PATTERNS: list[tuple[re.Pattern, str]] = []


def _template_to_regex(template: str) -> re.Pattern:
    parts = template.split("{v}")
    body = r"(.+?)".join(re.escape(part) for part in parts)
    # 整条匹配：动态部分允许为空，首尾锚定
    return re.compile("^" + body.replace(r"(.+?)", r"(.*?)") + "$", re.S)


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
            _PATTERNS.append((_template_to_regex(english), table[english]))
        except re.error:
            continue


# iCloud3 用 '^x^' 前缀给 Event Log 上色（^a^ 警报、^e^ 错误、^m^ 监视……）
_COLOR_PREFIX_RE = re.compile(r"^(?:\^[0-9a-zA-Z]\^)+")


def text(message: str) -> str:
    """把一条 Event Log 消息翻成中文；没有对应模板时原样返回。

    ``^x^`` 颜色前缀会先剥离、翻译后再原样接回去，卡片仍能正确着色。
    """
    if not message or not is_chinese() or not isinstance(message, str):
        return message

    prefix = ""
    color = _COLOR_PREFIX_RE.match(message)
    if color:
        prefix = color.group(0)
        message = message[len(prefix):]

    _load()
    if not _PATTERNS:
        return prefix + message

    for pattern, translated in _PATTERNS:
        found = pattern.match(message)
        if found is None:
            continue
        try:
            return prefix + translated.replace("{v}", "{}").format(*found.groups())
        except (IndexError, KeyError, ValueError):
            return prefix + message
    return prefix + message
