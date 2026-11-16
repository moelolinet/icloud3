"""Generate custom_components/icloud3/i18n/event_log_zh.json from tools/i18n/ev_mt.json."""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

# Locate the repository root without assuming the checkout layout: the same
# tools run inside the upstream clone and inside this fork.
ROOT = next(
    (parent for parent in HERE.parents
     if (parent / "custom_components" / "icloud3").is_dir()),
    None,
)
if ROOT is None:
    raise SystemExit("cannot locate custom_components/icloud3")
SRC = ROOT / "tools/i18n/ev_mt.json"
OUT = ROOT / "custom_components/icloud3/i18n/event_log_zh.json"

table = json.loads(SRC.read_text(encoding="utf-8"))
OUT.write_text(
    json.dumps(table, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
    encoding="utf-8",
)
print(f"event_log_zh.json: {len(table)} entries")
