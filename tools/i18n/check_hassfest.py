"""hassfest 翻译规则自检（本地版）。

Home Assistant 的 hassfest 会拒收以下翻译，导致 HACS 校验失败、集成无法安装：

  * 译文首尾有空格
  * 译文里出现 URL（应改用 description placeholders）
  * step 内出现非法键（只允许 title/description/data/data_description/...）

用法：python tools/i18n/check_hassfest.py
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

# Locate the integration's translations directory without assuming the repo
# layout (the same scripts run inside both the upstream clone and this fork).
PKG = next(
    (parent / "custom_components" / "icloud3"
     for parent in HERE.parents
     if (parent / "custom_components" / "icloud3" / "translations").is_dir()),
    None,
)
if PKG is None:
    raise SystemExit("cannot locate custom_components/icloud3")

RE_URL = re.compile(
    r"(((ftp|ftps|scp|http|https|mqtt|mqtts|socket|socks5)://|www\.)"
    r"[a-z0-9]+([\-.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(/.*)?)",
    re.IGNORECASE,
)
STEP_KEYS = {
    "title", "description", "data", "data_description", "menu_options",
    "menu_option_descriptions", "submit", "sections",
}


def leaves(node, prefix=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from leaves(value, f"{prefix}.{key}" if prefix else key)
    else:
        yield prefix, node


def main():
    problems = []
    for name in ("en.json", "zh-Hans.json", "zh-Hant.json"):
        path = PKG / "translations" / name
        if not path.exists():
            problems.append(f"{name}: file missing")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))

        for key, value in leaves(data):
            if not isinstance(value, str):
                continue
            if value != value.strip():
                problems.append(f"{name}: leading/trailing space at {key}")
            if RE_URL.search(value):
                problems.append(f"{name}: URL at {key}")

        # step 内的键必须在白名单里
        for section in ("config", "options"):
            for step, body in data.get(section, {}).get("step", {}).items():
                if not isinstance(body, dict):
                    continue
                for key, value in body.items():
                    if key not in STEP_KEYS:
                        problems.append(f"{name}: invalid step key {section}.step.{step}.{key}")
                    # data_description 的每个键都必须有对应 data 字段
                    if key == "data_description" and isinstance(value, dict):
                        data_keys = set(body.get("data", {}))
                        for dd_key in value:
                            if dd_key not in data_keys:
                                problems.append(
                                    f"{name}: orphan data_description "
                                    f"{section}.step.{step}.{dd_key}"
                                )

        # issues.<id>.fix_flow.step 里同样检查
        for issue, body in data.get("issues", {}).items():
            for step, step_body in (body.get("fix_flow", {}).get("step", {}) or {}).items():
                if not isinstance(step_body, dict):
                    continue
                for key, value in step_body.items():
                    if key not in STEP_KEYS:
                        problems.append(f"{name}: invalid step key issues.{issue}.{step}.{key}")
                    if key == "data_description" and isinstance(value, dict):
                        data_keys = set(step_body.get("data", {}))
                        for dd_key in value:
                            if dd_key not in data_keys:
                                problems.append(
                                    f"{name}: orphan data_description "
                                    f"issues.{issue}.{step}.{dd_key}"
                                )

    print(f"checked 3 files, problems: {len(problems)}")
    for problem in problems[:40]:
        print("  -", problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
