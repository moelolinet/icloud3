"""显示层助手（display helpers）.

要点：**值保持英文，只翻译显示标签**。

Home Assistant 的下拉/列表选择框支持 ``[{"value": "SAVE", "label": "保存"}]``，
前端显示 ``label``、提交回来的是 ``value``。这样 iCloud3 里所有
``*_KEY_BY_TEXT`` 反查、``startswith('➤ ADD')`` 前缀判断、配置文件里的英文键值
都不受影响，只需要改「显示」这一层。

例外：``cv.multi_select`` 的候选项本身就是「提交值」，无法分离 label 与 value
（见 :func:`header_checkbox`）。这类「整段说明文字当开关」的复选项保持英文，
否则提交内容会变成中文长句。
"""

from __future__ import annotations

from .core import is_chinese, text

RARROW = " → "


def label(value):
    """把一个选项文本转成显示用文本。

    iCloud3 的选项文本是 ``"标题 → 说明"``。标题用专门的词表（短、出现频率最高、
    必须与界面其他位置措辞一致），说明部分沿用整句译文；整句查不到时再按段拼接。
    """
    if not is_chinese() or not isinstance(value, str):
        return value

    whole = text(value)

    if RARROW in value:
        head, tail = value.split(RARROW, 1)
        head_zh = text(head)
        if head_zh != head:
            if whole != value and RARROW in whole:
                tail_zh = whole.split(RARROW, 1)[1]
            else:
                tail_zh = text(tail)
            return f"{head_zh}{RARROW}{tail_zh}"

    return whole


def option_list(values):
    """``[英文, ...]`` -> ``[{"value": 英文, "label": 中文}, ...]``。"""
    return [{"value": value, "label": label(value)} for value in values]


def option_dict(values):
    """``{内部键: 英文标签}`` -> ``[{"value": 英文标签, "label": 中文}, ...]``。

    ``value`` 必须是**英文标签**（不是内部键）：iCloud3 的 ``default=`` 与
    ``option_text_to_parm()`` 都是拿界面上的英文标签去比对的。
    """
    return [{"value": value, "label": label(value)} for value in values.values()]


def multi_select(values):
    """``cv.multi_select`` 的候选项：只翻译标签。

    支持 ``{键: 标签}`` 与 ``[标签, ...]`` 两种形态；键/值保持不变。
    """
    if not is_chinese():
        return values
    if isinstance(values, dict):
        return {key: label(value) for key, value in values.items()}
    if isinstance(values, (list, tuple)):
        return [label(value) for value in values]
    return values


def multi_select_default(default):
    """``cv.multi_select`` 的 default 必须与其选项文本一致，否则提交会校验失败。"""
    if not is_chinese():
        return default
    if isinstance(default, list):
        return [label(value) for value in default]
    if isinstance(default, str):
        return label(default)
    return default


def header_checkbox(values):
    """「整段说明文字当作开关」的复选项：**不翻译**。

    ``cv.multi_select`` 没有 label/value 分离，候选项文字就是提交内容；iCloud3
    只判断它是否为空（``!= []``）。保持英文可以确保提交值与其它逻辑完全一致。
    """
    return values
