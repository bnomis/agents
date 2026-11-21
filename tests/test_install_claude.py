"""Tests for bin/install-claude.py's status line registration."""

import importlib.util
import json
import pathlib

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / 'bin' / 'install-claude.py'


@pytest.fixture
def installer():
    spec = importlib.util.spec_from_file_location('install_claude', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def settings(tmp_path):
    return tmp_path / 'settings.json'


def test_main_exits_with_the_settings_error(installer, tmp_path, monkeypatch, capsys):
    home = tmp_path.resolve()
    monkeypatch.setenv('HOME', str(home))
    (home / '.claude').mkdir()
    (home / '.claude' / 'settings.json').write_text('{not json')
    with pytest.raises(SystemExit) as exc:
        installer.main([])
    assert exc.value.code != 0
    assert 'settings.json is not valid JSON' in str(exc.value.code)


def test_status_line_registered_when_absent(installer, settings):
    settings.write_text(json.dumps({'model': 'x'}))
    installer.register_status_line(None, settings)
    data = json.loads(settings.read_text())
    assert data['statusLine'] == installer.STATUS_LINE
    assert data['model'] == 'x'


def test_existing_status_line_is_kept(installer, settings):
    original = json.dumps({'statusLine': {'type': 'command', 'command': 'mine'}})
    settings.write_text(original)
    installer.register_status_line(None, settings)
    assert settings.read_text() == original
    assert not settings.with_name('settings.json.orig').exists()


def test_status_line_refuses_invalid_settings(installer, settings):
    settings.write_text('[]')
    with pytest.raises(installer.SettingsError, match='settings.json'):
        installer.register_status_line(None, settings)
    assert settings.read_text() == '[]'


def test_full_install_registers_the_status_line_once(installer, tmp_path, monkeypatch):
    home = tmp_path.resolve()
    monkeypatch.setenv('HOME', str(home))
    installer.install_claude(None)
    installer.install_claude(None)
    data = json.loads((home / '.claude' / 'settings.json').read_text())
    assert data['statusLine'] == installer.STATUS_LINE
    assert (home / '.claude' / 'statusline.py').exists()
