"""Event Log 显示层翻译测试.

内部记录保留英文，只在输出给卡片时翻译；颜色前缀必须原样保留。
"""
import pytest

from icloud3.i18n import core
from icloud3.i18n import event_log as ev


@pytest.fixture(autouse=True)
def _zh():
    core.reset(); core.set_language("zh")
    yield
    core.reset()


def test_known_message_translated():
    assert ev.text("HA Shutting Down") == "HA 关闭"


def test_dynamic_values_preserved():
    out = ev.text("Apple Acct > me@example.com, Login Failed, Error-9/0, Code-503")
    assert "me@example.com" in out
    assert "9/0" in out and "503" in out
    assert "\u767b\u5f55\u5931\u8d25" in out


def test_color_prefix_preserved():
    out = ev.text("^m^Tracking parameters updated")
    assert out.startswith("^m^")
    assert out != "^m^Tracking parameters updated"


def test_unknown_message_unchanged():
    msg = "A brand new message with no template"
    assert ev.text(msg) == msg


def test_english_mode_unchanged():
    core.set_language("en")
    msg = "HA Shutting Down"
    assert ev.text(msg) == msg


def test_message_containing_braces_is_safe():
    # 动态内容里带花括号时不能抛异常
    out = ev.text("Data Sources > {weird} value")
    assert isinstance(out, str)
