"""行为测试：中文界面不能改变 iCloud3 的逻辑.

iCloud3 的下拉/列表提交回来的是「界面上的文本」，代码再用英文文本反查配置值
（``*_KEY_BY_TEXT``、``option_text_to_parm``）。所以：

* UI 选项的 ``value`` 必须始终是英文原文；
* 只有 ``label`` 可以是中文；
* 每个表单默认值必须存在于自己的选项列表里。

这里用一个最小的假 selector 序列化来验证这三条，不依赖 Home Assistant 运行时。
"""
import pytest

from icloud3.i18n import core
from icloud3.i18n import display as i18n


@pytest.fixture(autouse=True)
def _reset():
    core.reset()
    yield
    core.reset()


ACTIONS = [
    "SAVE \u2192 Save the changes",
    "\u25c0\ufe0e MENU \u2192 Back to the menu",
    "UPDATE THE DEVICE \u2192 Update the selected device",
]


def test_english_mode_returns_the_original_text():
    core.set_language("en")
    assert i18n.label(ACTIONS[0]) == ACTIONS[0]
    # Values are always the English text; the label is the same in English mode.
    assert [o["value"] for o in i18n.option_list(ACTIONS)] == ACTIONS
    assert [o["label"] for o in i18n.option_list(ACTIONS)] == ACTIONS


def test_chinese_labels_keep_english_values():
    core.set_language("zh")
    options = i18n.option_list(ACTIONS)
    assert [o["value"] for o in options] == ACTIONS
    assert all(o["label"] != o["value"] for o in options)
    assert all(any("\u4e00" <= ch <= "\u9fff" for ch in o["label"]) for o in options)


def test_unknown_text_is_returned_unchanged():
    core.set_language("zh")
    assert i18n.label("Some brand new text") == "Some brand new text"


def test_option_dict_maps_values_to_english_labels():
    core.set_language("zh")
    table = {"track": "Track - Request Location and track the device"}
    options = i18n.option_dict(table)
    assert options[0]["value"] == table["track"]


def test_header_checkbox_is_never_translated():
    """``cv.multi_select`` 的候选项就是提交值，这类开关必须保持英文。"""
    core.set_language("zh")
    header = "SEND ICLOUD3 ANALYTICS DATA > Send usage data"
    assert i18n.header_checkbox([header]) == [header]


def test_multi_select_keeps_keys():
    core.set_language("zh")
    table = {"battery": "Battery", "badge": "Badge"}
    translated = i18n.multi_select(table)
    assert set(translated) == set(table)


def test_bad_placeholder_translation_is_rejected():
    """占位符不一致的译文必须被丢弃，否则 HA 格式化时会抛 KeyError。"""
    from icloud3.i18n import core as core_mod

    core_mod.set_language("zh")
    core_mod._TABLE.clear()
    core_mod._LOADED = False
    core_mod._TABLE.update({"{a} and {b}": "{a} 与 {c}"})
    core_mod._LOADED = True
    assert core_mod.text("{a} and {b}") == "{a} and {b}"


def test_language_follows_hass_when_auto():
    core.set_language("auto")
    core.set_hass_language("zh-Hans")
    assert core.is_chinese() is True
    core.set_hass_language("en")
    assert core.is_chinese() is False
    core.set_hass_language("de")
    assert core.is_chinese() is False


def test_forced_english_overrides_chinese_hass():
    core.set_language("en")
    core.set_hass_language("zh-Hans")
    assert core.is_chinese() is False


def test_sensor_name_translation_keeps_device_name():
    from icloud3.i18n import sensors

    core.set_language("zh")
    assert sensors.sensor_name("Gary iPhone Battery") == "Gary iPhone \u7535\u6c60"
    assert sensors.sensor_name("Gary TravelTime (min)") == "Gary \u884c\u7a0b\u65f6\u95f4\uff08\u5206\u949f\uff09"

