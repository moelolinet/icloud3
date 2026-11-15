"""Render every iCloud3 Configure form inside a live HomeAssistant.

    python tools/i18n/render_forms.py zh
    python tools/i18n/render_forms.py en

Writes /tmp/ic3_render_out/<lang>.json with, for every form, each field name and
its option values. English and Chinese must agree on names and values; only the
displayed labels may differ.
"""
import asyncio
import io
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bootstrap  # noqa: F401,E402
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from homeassistant import core as ha_core, config_entries
from homeassistant.helpers import device_registry as dr, entity_registry as er, area_registry as ar
import homeassistant.helpers.config_validation as cv
import probatio

LANG = sys.argv[1] if len(sys.argv) > 1 else "zh"
HASS_LANG = "zh-Hans" if LANG == "zh" else "en"

FORMS = [
    ("form_config_flow", "form_config_option_user", ()),
    ("form_config_flow", "form_menu", ()),
    ("form_apple_acct", "form_apple_accounts", ()),
    ("form_apple_acct", "form_other_apple_acct_parameters", ()),
    ("form_icloud3_device", "form_device_list", ()),
    ("form_icloud3_device", "form_update_device", ()),
    ("form_icloud3_device", "form_update_other_device_parameters", ()),
    ("form_sensors", "form_sensors", ()),
    ("form_sensors", "form_exclude_sensors", ()),
    ("form_parameters", "form_tracking_parameters", ()),
    ("form_parameters", "form_format_settings", ()),
    ("form_parameters", "form_waze_main", ()),
    ("form_parameters", "form_special_zones", ()),
    ("form_parameters", "form_away_time_zone", ()),
    ("form_parameters", "form_inzone_intervals", ()),
    ("form_parameters", "form_display_text_as", ()),
    ("form_tools", "form_tools", (None,)),
    ("form_tools", "form_log_level", ()),
    ("form_dashboard_builder", "form_dashboard_builder", ()),
    ("form_analytics", "form_analytics", (None,)),
]

DEVICE = {
    "ic3_devicename": "gary_iphone", "fname": "Gary", "device_type": "iphone",
    "inzone_interval": 60, "fixed_interval": 0, "log_zones": ["none"],
    "track_from_zones": [], "track_from_base_zone": "home",
    "apple_device_name": "Gary-iPhone", "mobile_app_device": "None",
    "picture": "None", "icon": "mdi:account", "tracking_mode": "track",
    "apple_account": "", "aadev_name": "None",
}


class Flow:
    def __init__(self):
        self.errors = {}
        self.errors_user_input = {}
        self.multi_form_user_input = {}
        self.menu_item_selected = ["device_list", "tracking_parameters"]
        self.menu_page_no = 0
        self.menu_item = "device_list"
        self.apple_id = ""
        self.password = ""
        self.actions_list = []
        self.actions_list_default = ""
        self.conf_device = dict(DEVICE)
        self.conf_apple_acct = {}
        self.zone_name_key_text = {"home": "Home (home)"}
        self.icloud_list_text_by_fname = {"None": "None"}
        self.mobapp_list_text_by_entity_id = {".unknown": "The Mobile App is not installed"}
        self.picture_by_filename = {"None": "Icon"}
        self.log_level_devices_key_text = {"all": "All Devices"}
        self.analytic_reports_by_name = {"locations": "Locations Report"}
        self.away_time_zone_hours_key_text = {0: "0-hours", 1: "1-hour"}
        self.away_time_zone_devices_key_text = {"all": "All Devices"}
        self.dbf_dashboard_key_text = {"add": "➤ CREATE A NEW ICLOUD3 DASHBOARD"}
        self.ui_selected_dbname = "add"
        self.dbf_main_view_devices_key_text = {}
        self.ic3db_Dashboards_by_dbname = {}
        self.excluded_sensors = []
        self.sensors_fname_list = []
        self.sensors_list_filter = "?"
        self.device_items_by_devicename = {}
        self.device_items_displayed = []
        self.apple_acct_items_by_apple_id = {}
        self.apple_acct_items_displayed = []
        self.applyle_acct_auth_items_by_apple_id = {}
        self.aa_auth_methods_by_auth_method = {}
        self.www_directory_list = []
        self.dev_page_no = 0
        self.dev_page_last_selected_devicename = ["", ""]
        self.aa_page_no = 0
        self.aa_page_item = [""] * 5
        self.dta_selected_idx = -1
        self.dta_selected_idx_page = [0, 5]
        self.dta_page_no = 0
        self.dta_working_copy = {i: "" for i in range(10)}
        self.confirm_action = {"action_desc": "Confirm Action"}
        self.is_repair_flow = False
        self.is_deleting_device = False
        self.create_device_tracker_sensor_enities_on_exit = False
        self.rebuild_ic3db_dashboards = False

    def set_default_sensors(self, *a, **k):
        pass

    def __getattr__(self, name):
        return lambda *a, **k: None


def summarize(schema):
    out = probatio.to_field_list(schema.schema, custom_serializer=cv.custom_serializer)
    fields = []
    for field in out:
        selector = field.get("selector", {})
        options = None
        if "select" in selector:
            options = selector["select"]["options"]
        elif field.get("type") == "multi_select":
            options = field["options"]
        values = None
        if isinstance(options, list):
            values = [o if isinstance(o, str) else o["value"] for o in options]
        elif isinstance(options, dict):
            values = list(options)
        fields.append({"name": field.get("name"), "values": values})
    return fields


async def main():
    cfg = pathlib.Path("/tmp/ic3_render"); cfg.mkdir(parents=True, exist_ok=True)
    hass = ha_core.HomeAssistant(str(cfg))
    hass.config.config_dir = str(cfg)
    await hass.async_start()
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    dr.async_setup(hass)
    await dr.async_load(hass)
    await er.async_load(hass)
    await ar.async_load(hass)
    hass.config.language = HASS_LANG
    hass.data["lovelace"] = {}

    from icloud3.global_variables import GlobalVariables as Gb
    Gb.hass = hass
    from icloud3.i18n import core
    core.set_hass_language(HASS_LANG)
    from icloud3.startup import config_file, start_ic3
    start_ic3.initialize_directory_filenames()
    await config_file.async_load_icloud3_configuration_file()

    result = {}
    for module, func, args in FORMS:
        try:
            mod = __import__(f"icloud3.configure_v1.screens.{module}", fromlist=[func])
            result[f"{module}.{func}"] = summarize(getattr(mod, func)(Flow(), *args))
        except Exception as err:
            result[f"{module}.{func}"] = f"ERROR {type(err).__name__}: {err}"

    pathlib.Path(f"/tmp/ic3_render/{LANG}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    for name, value in result.items():
        if isinstance(value, str):
            print(f"FAIL {name}: {value}")
        else:
            print(f"OK   {name}: fields={len(value)}")
    await hass.async_stop()


asyncio.run(main())
