"""Validated, atomic persistence of non-sensitive user preferences."""

import json
import math
import os
import tempfile
from pathlib import Path

DEFAULTS = {
    "inplace": False,
    "cidade": "Lages/SC.",
    "page": 0,
    "font_size": 12.0,
    "font": "helv",
    "color": "#000000",
    "bold": False,
    "italic": False,
    "logo_path": "",
    "logo_width_cm": 2.0,
    "logo_margin_cm": 0.5,
    "restrict_editing": False,
    "no_copy": False,
    "encrypt_content": False,
    "stamp_city": True,
    "stamp_date": True,
    "use_custom_date": False,
    "custom_date": "",
    "auto_logo": True,
    "x": "",
    "y": "",
}


def config_path() -> Path:
    return Path.home() / ".data_hora_pdf" / "config.json"


def sanitize(raw: object) -> dict:
    result = DEFAULTS.copy()
    if not isinstance(raw, dict):
        return result
    for key, default in DEFAULTS.items():
        value = raw.get(key, default)
        if isinstance(default, bool):
            valid = type(value) is bool
        elif isinstance(default, (int, float)):
            valid = type(value) in (int, float) and math.isfinite(value) and value >= 0
            if key in ("font_size", "logo_width_cm"):
                valid = valid and value > 0
            if key == "page":
                valid = valid and type(value) is int
        else:
            valid = isinstance(value, str)
        if valid:
            result[key] = value
    return result


def load_config(path: Path | None = None) -> dict:
    try:
        return sanitize(json.loads((path or config_path()).read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return DEFAULTS.copy()


def save_config(config: dict, path: Path | None = None) -> None:
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".config-", suffix=".json", dir=target.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(sanitize(config), stream, ensure_ascii=False, indent=2)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
