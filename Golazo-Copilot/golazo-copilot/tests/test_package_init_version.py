"""Tests for golazo_copilot.__init__ version resolution paths."""

import importlib


def test_init_uses_installed_package_version(monkeypatch):
    import golazo_copilot

    monkeypatch.setattr("importlib.metadata.version", lambda _: "9.9.9")
    reloaded = importlib.reload(golazo_copilot)
    assert reloaded.__version__ == "9.9.9"


def test_init_falls_back_when_package_missing(monkeypatch):
    import golazo_copilot
    from importlib.metadata import PackageNotFoundError

    def raise_missing(_):
        raise PackageNotFoundError

    monkeypatch.setattr("importlib.metadata.version", raise_missing)
    reloaded = importlib.reload(golazo_copilot)
    assert reloaded.__version__ == "0.0.0+local"
