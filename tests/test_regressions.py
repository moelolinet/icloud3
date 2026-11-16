"""回归测试：本轮排查发现的两个真实缺陷。

1. 仪表板 `main_view_devices` 的提交值是内部键 `all-devices`，曾被误翻译成
   「所有设备」，导致中文模式下默认值与选项不匹配、表单提交被拒。
2. Event Log 模板里连续多个 `(.*?)` 造成指数级回溯：20KB 未匹配消息耗时 14 秒，
   会阻塞 Home Assistant 事件循环。
"""
import json
import pathlib
import sys
import time

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".." / "custom_components"))

from icloud3.i18n import core, display  # noqa: E402
from icloud3.i18n import event_log as ev  # noqa: E402

PKG = HERE.parent / "custom_components" / "icloud3"
if not PKG.is_dir():
    PKG = HERE.parent / "icloud3" / "custom_components" / "icloud3"


@pytest.fixture(autouse=True)
def _zh():
    core.reset()
    core.set_language("zh")
    yield
    core.reset()


# --- 1. 内部键不能被翻译 -------------------------------------------------
@pytest.mark.parametrize("key", ["all-devices", "iphone-first-2", "result-summary", "track-details"])
def test_dashboard_value_keys_are_never_translated(key):
    catalog = json.loads((PKG / "i18n" / "catalog.json").read_text(encoding="utf-8"))
    assert key not in catalog, f"{key} is a submitted value and must not be translated"


def test_dashboard_multi_select_default_stays_a_key():
    """默认值必须仍是内部键，才能与 cv.multi_select 的选项匹配。"""
    assert display.multi_select_default(["all-devices"]) == ["all-devices"]


def test_dashboard_labels_still_translated():
    """键不翻译，但用户看到的标签仍应是中文。"""
    assert display.label("All Devices") != "All Devices"


# --- 2. Event Log 不能有灾难性回溯 --------------------------------------
def test_long_unmatched_message_is_fast():
    msg = "X" * 20000
    started = time.perf_counter()
    assert ev.text(msg) == msg
    assert time.perf_counter() - started < 0.5


def test_near_miss_message_is_fast():
    msg = "Apple Acct > " + ("a," * 2000) + " NOT-A-TEMPLATE-END"
    started = time.perf_counter()
    ev.text(msg)
    assert time.perf_counter() - started < 0.5


def test_template_placeholders_match_translation():
    table = json.loads((PKG / "i18n" / "event_log_zh.json").read_text(encoding="utf-8"))
    bad = [k for k, v in table.items() if k.count("{v}") != v.count("{v}")]
    assert bad == []


def test_every_templated_message_translates_and_keeps_values():
    table = json.loads((PKG / "i18n" / "event_log_zh.json").read_text(encoding="utf-8"))
    for english in table:
        if "{v}" not in english:
            continue
        markers = [f"V{i}" for i in range(english.count("{v}"))]
        filled = english
        for marker in markers:
            filled = filled.replace("{v}", marker, 1)
        out = ev.text(filled)
        assert out != filled, f"not translated: {english[:60]}"
        assert all(m in out for m in markers), f"value lost: {english[:60]}"
