"""Test configuration for iCloud3.

The Home Assistant pytest plugin needs POSIX-only modules (fcntl), so it is not
used here. These tests validate the translation layer and the Configure screens'
option tables.

``custom_components`` is added to sys.path so the integration's ``i18n`` package
can be imported as ``icloud3.i18n``. Two optional Home Assistant dependencies
have no Windows wheels and are replaced by inert stand-ins.
"""
import pathlib
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parent.parent

for candidate in (ROOT / "custom_components", ROOT / "icloud3" / "custom_components"):
    if candidate.is_dir():
        sys.path.insert(0, str(candidate))
        break


def _stub(name, **attrs):
    if name in sys.modules:
        return
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module


class _Inert:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return _Inert()


_stub("pymicro_vad", MicroVad=_Inert)
_stub("pyspeex_noise", AudioProcessor=_Inert)
