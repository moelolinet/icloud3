"""回归测试：中文界面下提交表单不能被拒.

Home Assistant 会用选项列表校验提交值，所以「选项文本」和「默认值」必须使用
同一套文本。这个测试复现过真实缺陷：选项译成中文、默认值仍是英文时，用户
不改任何内容直接提交会被 HA 拒绝（"… is not a valid option"）。
"""
import pytest
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from icloud3.i18n import core
from icloud3.i18n import display as i18n
from icloud3.configure_v1 import const_form_lists as T

HEADERS = [
    T.WAZE_USED_HEADER, T.WAZE_HISTORY_USED_HEADER, T.STAT_ZONE_HEADER,
    T.PASSTHRU_ZONE_HEADER, T.TRK_FROM_HOME_ZONE_HEADER, T.APPLE_ACCT_USED_HEADER,
    T.ANALYTICS_ENABLED_HDR,
]

TABLES = [
    T.TRACKING_MODE_OPTIONS, T.UNIT_OF_MEASUREMENT_OPTIONS, T.DATA_SOURCE_OPTIONS,
    T.TIME_FORMAT_OPTIONS, T.WAZE_SERVER_OPTIONS, T.WAZE_HISTORY_TRACK_DIRECTION_OPTIONS,
    T.DEVICE_TRACKER_STATE_SOURCE_OPTIONS, T.LOG_LEVEL_OPTIONS,
    T.APPLE_SERVER_LOCATION_OPTIONS, T.DASHBOARD_MAIN_VIEW_STYLE_OPTIONS,
]


@pytest.fixture(autouse=True)
def _zh():
    core.reset()
    core.set_language("zh")
    yield
    core.reset()


@pytest.mark.parametrize("header", HEADERS, ids=[h[:26] for h in HEADERS])
def test_header_checkbox_accepts_its_own_default(header):
    default = i18n.multi_select_default([header])
    schema = vol.Schema({vol.Optional("h", default=default): cv.multi_select(i18n.multi_select([header]))})
    assert schema({"h": default}) == {"h": default}


def test_sensor_multi_select_accepts_key_default():
    table = T.CONF_SENSORS_DEVICE_KEY_TEXT
    default = list(table)[:2]
    schema = vol.Schema({
        vol.Required("sensors", default=default): cv.multi_select(i18n.multi_select(table))
    })
    assert schema({"sensors": default}) == {"sensors": default}
    # labels are translated but the submitted values stay the internal keys
    assert all(v != k for k, v in i18n.multi_select(table).items())


@pytest.mark.parametrize("table", TABLES, ids=[t.get("track", t.get("mi", "t"))[:12] if False else str(i) for i, t in enumerate(TABLES)])
def test_dropdown_keeps_english_label_as_value(table):
    options = i18n.option_dict(table)
    values = {o["value"] for o in options}
    missing = [label for label in table.values() if label not in values]
    assert missing == []
