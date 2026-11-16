"""由 en.json + 翻译缓存生成 translations/zh-Hans.json（以及 zh-Hant.json）.

结构严格复制 en.json，只替换叶子文本，所以键、层级、占位符天然保持一致。
"""
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
EN = ROOT / "custom_components/icloud3/translations/en.json"
MT = ROOT / "tools/i18n/mt.json"
TR = ROOT / "custom_components/icloud3/translations"


def build(node, path, table):
    if isinstance(node, dict):
        return {key: build(value, f"{path}.{key}" if path else key, table)
                for key, value in node.items()}
    if "_comment" in path or path.endswith("translation_file_by"):
        return node
    return table.get(node, node)


def main():
    en = json.loads(EN.read_text(encoding="utf-8"))
    table = json.loads(MT.read_text(encoding="utf-8"))
    zh = build(en, "", table)
    for name in ("zh-Hans.json", "zh-Hant.json"):
        (TR / name).write_text(
            json.dumps(zh, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print("wrote", name)


if __name__ == "__main__":
    main()
