"""Round 1 full-surface audit for the Chinese localisation.

Checks:
  1. every Python file still compiles
  2. the Event Log card still parses
  3. en.json / zh-Hans.json have identical keys and placeholders
  4. no form option *value* is Chinese (values must stay English)
  5. every option_dict value is one of the table's English labels

Usage:  python tools/i18n/audit_round1.py
"""
import compileall
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bootstrap  # noqa: F401,E402

ROOT = HERE.parents[2]
PKG = ROOT / "icloud3/custom_components/icloud3"
problems = []

if not compileall.compile_dir(str(PKG), quiet=1, force=True):
    problems.append("python compile failed")

card = PKG / "event_log_card/icloud3-event-log-card.js"
result = subprocess.run(["node", "--check", str(card)], capture_output=True, text=True)
if result.returncode != 0:
    problems.append("js syntax: " + result.stderr[:200])


def leaves(node, prefix=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from leaves(value, f"{prefix}.{key}" if prefix else key)
    else:
        yield prefix, node


en = dict(leaves(json.loads((PKG / "translations/en.json").read_text(encoding="utf-8"))))
zh = dict(leaves(json.loads((PKG / "translations/zh-Hans.json").read_text(encoding="utf-8"))))
if set(en) != set(zh):
    problems.append(f"key mismatch: only_en={len(set(en) - set(zh))} only_zh={len(set(zh) - set(en))}")

PLACEHOLDER = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")
for key, value in en.items():
    if key in zh and set(PLACEHOLDER.findall(value)) != set(PLACEHOLDER.findall(zh[key])):
        problems.append(f"placeholder mismatch: {key}")

from icloud3.i18n import core, display  # noqa: E402
from icloud3.configure_v1 import const_form_lists as tables  # noqa: E402

core.set_language("zh")
CJK = re.compile(r"[\u4e00-\u9fff]")
checked = 0
for name, table in vars(tables).items():
    if not isinstance(table, dict) or not table:
        continue
    if not all(isinstance(value, str) for value in table.values()):
        continue
    options = display.option_dict(table)
    if not isinstance(options, list) or not options:
        continue
    checked += 1
    values = [option["value"] for option in options if isinstance(option, dict)]
    for label in table.values():
        if label not in values:
            problems.append(f"option value is not the english label: {name}")
    for value in values:
        if CJK.search(str(value)):
            problems.append(f"chinese leaked into option value: {name}")

print(f"translation tables checked: {checked}")
print(f"problems: {len(problems)}")
for problem in problems[:20]:
    print("  -", problem)
sys.exit(1 if problems else 0)
