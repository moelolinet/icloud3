"""iCloud3 中文本地化（Chinese localisation）.

显示文本的中文翻译层。设计说明见 :mod:`core`。
"""

from .core import (AUTO, CHINESE, ENGLISH, get_language_setting, has_chinese_text,
                   is_chinese, items, reset, set_hass_language, set_language,
                   table, text, text_with_suffix)
from .display import label, multi_select, option_dict, option_list
from .sensors import sensor_name

__all__ = [
    "AUTO", "CHINESE", "ENGLISH", "get_language_setting", "has_chinese_text",
    "is_chinese", "items", "label", "multi_select",
    "option_dict", "option_list", "reset", "sensor_name", "set_hass_language",
    "set_language",
    "table", "text", "text_with_suffix",
]
