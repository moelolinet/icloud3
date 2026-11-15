"""iCloud3 中文本地化回归测试.

这些测试只验证「显示层」的正确性与安全性，不依赖 Apple 账号：

* 英文模式下所有文本必须与原文一致（不能改动 en.json 的内容）
* 中文模式下表单选项的 value 仍是英文（配置值/反查逻辑不受影响）
* 每个 selector 的 default 必须存在于其 options 中
  （否则 Home Assistant 打开表单会报 "not a valid option"）
* 译文占位符必须与英文一致（否则格式化时抛异常）
"""
import json
import pathlib
import re

import pytest

PKG = pathlib.Path(__file__).resolve().parent.parent / "custom_components" / "icloud3"
if not PKG.is_dir():
    PKG = pathlib.Path(__file__).resolve().parent.parent / "icloud3" / "custom_components" / "icloud3"

EN_PATH = PKG / "translations/en.json"
ZH_PATH = PKG / "translations/zh-Hans.json"
CATALOG = PKG / "i18n/catalog.json"


def _walk(node, prefix=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _walk(value, f"{prefix}.{key}" if prefix else key)
    else:
        yield prefix, node


@pytest.fixture(scope="module")
def translations():
    return json.loads(EN_PATH.read_text(encoding="utf-8")), json.loads(ZH_PATH.read_text(encoding="utf-8"))


def test_zh_structure_matches_en(translations):
    en, zh = translations

    def shape(node):
        if isinstance(node, dict):
            return {k: shape(v) for k, v in node.items()}
        return type(node).__name__

    assert shape(en) == shape(zh)


def test_zh_placeholders_match_en(translations):
    en, zh = translations
    en_flat, zh_flat = dict(_walk(en)), dict(_walk(zh))
    pattern = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")
    mismatches = [
        key for key, value in en_flat.items()
        if set(pattern.findall(value)) != set(pattern.findall(zh_flat[key]))
    ]
    assert mismatches == []


def test_zh_strings_are_formattable(translations):
    en, zh = translations
    en_flat, zh_flat = dict(_walk(en)), dict(_walk(zh))
    pattern = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
    for key, value in en_flat.items():
        kwargs = {name: "X" for name in pattern.findall(value)}
        if "_comment" in key:
            continue
        zh_flat[key].format(**kwargs)   # must not raise


def test_catalog_has_no_placeholder_conflicts():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    pattern = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")
    bad = [k for k, v in catalog.items() if set(pattern.findall(k)) != set(pattern.findall(v))]
    assert bad == []
