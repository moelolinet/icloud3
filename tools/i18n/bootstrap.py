"""Shared bootstrap for the local verification scripts.

Adds the repository to sys.path and installs inert stand-ins for optional Home
Assistant dependencies that are unavailable in this sandbox (native packages
without wheels, and HA's assist/conversation stack, which iCloud3 only reaches
through ``mobile_app.notify``).
"""
import pathlib
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "icloud3/custom_components"))


def _module(name, **attrs):
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        sys.modules[name] = module
    for key, value in attrs.items():
        if not hasattr(module, key):
            setattr(module, key, value)
    return module


class _Inert:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return _Inert()


for _name, _attr in (
    ("pymicro_vad", "MicroVad"),
    ("pyspeex_noise", "AudioProcessor"),
    ("hassil.fuzzy", "FuzzyNgramMatcher"),
    ("gazetteer_matcher", "GazetteerMatcher"),
):
    _module(_name, **{_attr: _Inert})

_module("homeassistant.components.mobile_app",
        notify=types.SimpleNamespace(send_message=lambda *a, **k: None))
_module("homeassistant.components.mobile_app.notify")
