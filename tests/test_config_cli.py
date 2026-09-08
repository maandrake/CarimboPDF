import json
import subprocess
import sys
from datetime import date, timedelta

import pytest

from data_hora_pdf.cli import main
from data_hora_pdf.config import DEFAULTS, load_config, save_config
from data_hora_pdf.dates import parse_date


@pytest.mark.parametrize("content", ["[]", "null", "{broken", '{"page": "bad", "font_size": -1}'])
def test_corrupt_config_uses_defaults(tmp_path, content):
    config = tmp_path / "config.json"
    config.write_text(content)
    assert load_config(config) == DEFAULTS


def test_config_atomic_and_does_not_save_secrets(tmp_path):
    path = tmp_path / "settings" / "config.json"
    save_config(
        {
            "cidade": "São Paulo",
            "protection_password": "secret",
            "save_password": True,
            "input_password": "also secret",
            "custom_date": "2025-01-02",
        },
        path,
    )
    assert load_config(path)["cidade"] == "São Paulo"
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert "protection_password" not in raw
    assert "save_password" not in raw
    assert "input_password" not in raw
    assert raw["custom_date"] == "2025-01-02"
    assert len(list(path.parent.iterdir())) == 1


def test_config_write_failure_keeps_previous(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    save_config({"cidade": "Original"}, path)
    before = path.read_bytes()

    def fail(*_):
        raise OSError("disk error")

    monkeypatch.setattr("data_hora_pdf.config.os.replace", fail)
    with pytest.raises(OSError):
        save_config({"cidade": "New"}, path)
    assert path.read_bytes() == before
    assert len(list(tmp_path.iterdir())) == 1


@pytest.mark.parametrize(
    "value", ["31/02/2025", "wrong", (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")]
)
def test_invalid_date_is_not_silently_replaced(value):
    with pytest.raises(ValueError):
        parse_date(value)


def test_cli_does_not_import_tkinter():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.modules['tkinter'] = None; from data_hora_pdf.cli import main; main(['--help'])",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_partial_arguments_do_not_open_gui():
    with pytest.raises(SystemExit) as exc:
        main(["--cidade", "Cidade"])
    assert exc.value.code == 2


def test_runtime_error_has_nonzero_exit(capsys):
    assert main(["--input", "missing.pdf", "--output", "out.pdf", "--cidade", "Cidade"]) == 1
    assert "Erro:" in capsys.readouterr().err


def test_conflicting_output_arguments():
    with pytest.raises(SystemExit) as exc:
        main(["--input", "a.pdf", "--output", "b.pdf", "--in-place"])
    assert exc.value.code == 2
