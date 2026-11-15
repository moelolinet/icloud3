"""iCloud3 中文本地化核心（Chinese localisation core）.

本模块只负责把「显示用的英文字符串」换成中文。它不改变：

* 配置文件中保存的值（仍是英文键值，如 ``mi`` / ``track``）
* 字典的键、entity_id、unique_id
* 代码里用于比较的逻辑文本（如 ``'➤ ADD'`` 前缀判断）

所有查表都是容错的：

* 查不到 -> 原样返回英文
* 译文里的 ``{占位符}`` 与英文不一致 -> 拒绝该译文并返回英文
  （否则 Home Assistant 格式化时会抛 KeyError，界面直接报错）
* 内部任何异常都被吞掉并回退英文
"""

from __future__ import annotations

import json
import logging
import os
import re

_LOGGER = logging.getLogger(__name__)

_PLACEHOLDER_RE = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")

ZH_LANGUAGE_PREFIX = "zh"
ENGLISH = "en"
CHINESE = "zh"
AUTO = "auto"

_LANGUAGE = AUTO
_HASS_LANGUAGE = ""
_TABLE: dict[str, str] = {}
_LOADED = False


# ---------------------------------------------------------------------------
# 语言设置
# ---------------------------------------------------------------------------
def set_language(language):
    """设置语言：``zh``、``en`` 或 ``auto``（默认，跟随 Home Assistant）。"""
    global _LANGUAGE
    value = (language or AUTO).strip().lower()
    if value.startswith(ZH_LANGUAGE_PREFIX):
        _LANGUAGE = CHINESE
    elif value.startswith("en"):
        _LANGUAGE = ENGLISH
    else:
        _LANGUAGE = AUTO


def get_language_setting():
    return _LANGUAGE


def set_hass_language(language):
    """记录 Home Assistant 的语言（由 __init__.py 在 setup 时写入）。"""
    global _HASS_LANGUAGE
    _HASS_LANGUAGE = (language or "").strip().lower()


def is_chinese():
    """当前是否应该显示中文。"""
    if _LANGUAGE == CHINESE:
        return True
    if _LANGUAGE == ENGLISH:
        return False
    return _HASS_LANGUAGE.startswith(ZH_LANGUAGE_PREFIX)


def has_chinese_text(value):
    return isinstance(value, str) and any("\u4e00" <= ch <= "\u9fff" for ch in value)


def reset():
    """仅供测试使用。"""
    global _LANGUAGE, _HASS_LANGUAGE, _LOADED
    _LANGUAGE = AUTO
    _HASS_LANGUAGE = ""
    _LOADED = False
    _TABLE.clear()


# ---------------------------------------------------------------------------
# 查表
# ---------------------------------------------------------------------------
def _load():
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalog.json")
        with open(path, encoding="utf-8") as file:
            _TABLE.update(json.load(file))
    except Exception as err:          # 目录缺失/损坏时保持英文，绝不影响启动
        _LOGGER.warning("iCloud3 中文翻译表加载失败，将显示英文：%s", err)


def _placeholders(value):
    return set(_PLACEHOLDER_RE.findall(value or ""))


def _safe(english, translated):
    if not translated:
        return english
    if _placeholders(english) != _placeholders(translated):
        return english
    return translated


def text(english):
    """把一段显示文本翻译成中文；查不到时原样返回。"""
    if not english or not isinstance(english, str) or not is_chinese():
        return english
    _load()
    try:
        return _safe(english, _TABLE.get(english))
    except Exception:
        return english


def text_with_suffix(english, extra_prefix_symbols=()):
    """翻译 ``"前缀 → 说明"`` 这种运行期拼接文本。

    iCloud3 会在表格文本后面接上动态内容（例如
    ``'REVIEW INACTIVE DEVICES → ... ^add-text^'``），这里在找不到完全匹配时
    退回翻译 ``→`` 之前的部分，再接回原文的其余部分。
    """
    if not english or not is_chinese():
        return english
    translated = text(english)
    if translated != english:
        return translated
    for sep in (" → ", " > "):
        if sep in english:
            head, tail = english.split(sep, 1)
            head_zh = text(head)
            if head_zh != head:
                return f"{head_zh}{sep}{tail}"
    return english


def table(english_table):
    """翻译 ``{key: 显示文本}`` 表格，**键保持不变**（键是配置值）。"""
    if not english_table or not is_chinese():
        return english_table
    return {key: text(value) for key, value in english_table.items()}


def items(english_items):
    """翻译一个显示文本列表，跳过分隔线/装饰行。"""
    if not english_items or not is_chinese():
        return english_items
    return [text(value) for value in english_items]
