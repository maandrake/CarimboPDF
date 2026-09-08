"""Run each GUI scenario in a fresh process, as with a real application launch.

Tcl/Tk native image state can fail intermittently when several app instances are
created and destroyed in one process on Windows. Do not retry or suppress errors:
each scenario must pass once in its own interpreter, including native icon checks.
"""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "scenario",
    [
        "test_gui_layout_and_defaults",
        "test_window_and_header_icon",
        "test_gui_processes_pdf_and_restores_button",
        "test_gui_plain_date_fallback",
    ],
)
def test_gui_scenario(scenario, tmp_path):
    script = Path(__file__).with_name("gui_scenarios.py")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            f"{script}::{scenario}",
            "-q",
            "-rs",
            "--tb=short",
            "--basetemp",
            str(tmp_path / "child"),
            "-p",
            "no:cacheprovider",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    if "1 skipped" in result.stdout:
        pytest.skip(output)
    assert "1 passed" in result.stdout, output
