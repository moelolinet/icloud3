"""由翻译缓存生成 runtime 查表文件 i18n/catalog.json.

输入（都是人工可复核的纯文本）:
    tools/i18n/mt.json     en.json 叶子文本 -> 中文
    tools/i18n/mt_ui.json  代码内界面文本 -> 中文

输出:
    custom_components/icloud3/i18n/catalog.json   英文原文 -> 中文
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EN = ROOT / "custom_components/icloud3/translations/en.json"
MT = ROOT / "tools/i18n/mt.json"
MT_UI = ROOT / "tools/i18n/mt_ui.json"
OUT = ROOT / "custom_components/icloud3/i18n/catalog.json"


def leaves(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from leaves(value)
    else:
        yield node


# 代码里当作「值」用的键（配置值、字典键、内部常量）。
# 它们绝不能出现在翻译表里，否则默认值/提交值会被翻译成中文。
CODE_VALUES = {
    "all-devices", "iphone-first-2", "result-summary", "track-details",
    "prerelease_switch_failed", "prerelease_switch_not_found", "prerelease_repo_not_installed",
    "rarely_updated_parms", "config", "data", "items", "path", "title", "views",
}


def is_code_value(text):
    return text in CODE_VALUES


def main():
    en = json.loads(EN.read_text(encoding="utf-8"))
    mt = json.loads(MT.read_text(encoding="utf-8"))
    mt_ui = json.loads(MT_UI.read_text(encoding="utf-8"))

    table = {}
    for english in leaves(en):
        if not isinstance(english, str):
            continue
        zh = mt.get(english)
        if zh and zh != english and not is_code_value(english):
            table.setdefault(english, zh)
    for english, zh in mt_ui.items():
        if zh and zh != english and not is_code_value(english):
            table.setdefault(english, zh)

    OUT.write_text(
        json.dumps(table, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"{OUT.name}: {len(table)} entries")


if __name__ == "__main__":
    main()
