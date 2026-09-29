"""Smoke tests: el paquete instalado debe ser importable."""

import zoria


def test_version_is_set():
    assert isinstance(zoria.__version__, str)
    assert zoria.__version__


def test_lib_is_importable():
    from zoria.lib import ADMX2001, SweepType, SweepScale  # noqa: F401

    assert ADMX2001 is not None
