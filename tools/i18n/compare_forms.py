"""Round 3: compare the two render outputs.

    python tools/i18n/render_forms.py en
    python tools/i18n/render_forms.py zh
    python tools/i18n/compare_forms.py

English mode must be byte-identical to the original release; only labels may be
translated, never the values that get submitted back to iCloud3.
"""
import json
import pathlib
import sys

BASE = pathlib.Path("C:/tmp/ic3_render")
en = json.loads((BASE / "en.json").read_text(encoding="utf-8"))
zh = json.loads((BASE / "zh.json").read_text(encoding="utf-8"))

problems = []
for form in sorted(en):
    a, b = en[form], zh[form]
    if isinstance(a, str) or isinstance(b, str):
        problems.append(f"{form}: render error ({a if isinstance(a, str) else b})")
        continue
    if [f["name"] for f in a] != [f["name"] for f in b]:
        problems.append(f"{form}: field names differ")
        continue
    for field_en, field_zh in zip(a, b):
        if field_en["values"] != field_zh["values"]:
            problems.append(f"{form}.{field_en['name']}: option values differ")

print(f"forms: {len(en)}")
print(f"differences: {len(problems)}")
for problem in problems[:20]:
    print("  -", problem)
sys.exit(1 if problems else 0)
