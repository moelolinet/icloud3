"""Test configuration for iCloud3.

``custom_components`` is added to sys.path so the integration can be imported as
``icloud3.*``. A few optional Home Assistant dependencies (native packages
without wheels on this platform, and HA's assist pipeline) are replaced by inert
stand-ins; iCloud3 only touches them indirectly through ``mobile_app.notify``.
"""
import pathlib
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parent.parent
for candidate in (ROOT / "custom_components", ROOT / "icloud3" / "custom_components"):
    if candidate.is_dir():
        sys.path.insert(0, str(candidate))
        break


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

# mobile_app -> HA assist/conversation stack; only notify is needed here
_module(
    "homeassistant.components.mobile_app",
    notify=types.SimpleNamespace(send_message=lambda *a, **k: None),
)
_module("homeassistant.components.mobile_app.notify")
