"""Shared bootstrap for the local verification scripts.

Adds the repository to sys.path and installs inert stand-ins for two optional
Home Assistant dependencies that have no Windows wheels.
"""
import pathlib
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "icloud3/custom_components"))


def _install(name, **attrs):
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


_install("pymicro_vad", MicroVad=_Inert)
_install("pyspeex_noise", AudioProcessor=_Inert)
