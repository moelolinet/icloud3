"""Generate custom_components/icloud3/i18n/event_log_zh.json from tools/i18n/ev_mt.json."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "tools/i18n/ev_mt.json"
OUT = ROOT / "custom_components/icloud3/i18n/event_log_zh.json"

table = json.loads(SRC.read_text(encoding="utf-8"))
OUT.write_text(
    json.dumps(table, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
    encoding="utf-8",
)
print(f"event_log_zh.json: {len(table)} entries")
