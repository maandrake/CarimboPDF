"""GUI integration tests use a hidden window and isolated preferences."""

import time
from datetime import date

import pymupdf as fitz
import pytest

from data_hora_pdf.cli import build_parser


@pytest.fixture
def app(monkeypatch):
    tk = pytest.importorskip("tkinter")
    from data_hora_pdf import gui

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk/display unavailable: {exc}")
    root.withdraw()
    monkeypatch.setattr(gui, "load_config", lambda: gui.DEFAULTS.copy())
    monkeypatch.setattr(gui, "save_config", lambda config: None)
    instance = None
    try:
        instance = gui.StampApp(root, build_parser().parse_args([]))
        yield instance
    finally:
        if instance is not None and instance.executor:
            instance.executor.shutdown(wait=True)
        root.destroy()


def test_gui_layout_and_defaults(app):
    app.root.update_idletasks()
    assert app.vars["inplace"].get() is False
    assert app.root.winfo_reqwidth() <= 900
    assert app.root.winfo_reqheight() <= 800
    app.vars["input"].set("documento.pdf")
    assert app.vars["output"].get() == "documento_carimbado.pdf"
    app.vars["inplace"].set(True)
    app.update_output()
    assert app.vars["output"].get() == "documento.pdf"


def test_window_and_header_icon(app):
    import os

    app.root.update_idletasks()
    assert app.title_label.cget("image")
    assert 48 <= app.header_icon.width() <= 64
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        # Query the native window: Tk's getter does not return ICO filenames.
        send_message = ctypes.windll.user32.SendMessageW
        send_message.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        send_message.restype = ctypes.c_void_p
        hwnd = int(app.root.frame(), 16)
        assert send_message(hwnd, 0x007F, 0, 0)  # WM_GETICON, ICON_SMALL
        assert send_message(hwnd, 0x007F, 1, 0)  # WM_GETICON, ICON_BIG


def test_gui_processes_pdf_and_restores_button(app, tmp_path, monkeypatch):
    from data_hora_pdf import gui

    messages = []
    monkeypatch.setattr(gui.messagebox, "showinfo", lambda *a, **kw: messages.append(a))
    monkeypatch.setattr(gui.messagebox, "showerror", lambda *a, **kw: pytest.fail(str(a)))
    source = tmp_path / "source.pdf"
    with fitz.open() as doc:
        doc.new_page()
        doc.save(source)
    app.vars["input"].set(str(source))
    app.vars["cidade"].set("Teste")
    app.vars["auto_logo"].set(False)
    app.submit()
    assert app.future is not None
    deadline = time.monotonic() + 20
    while app.future is not None and time.monotonic() < deadline:
        app.root.update()
        time.sleep(0.01)
    assert app.future is None
    assert messages
    assert "disabled" not in app.run_button.state()
    with fitz.open(app.vars["output"].get()) as doc:
        assert "TESTE" in doc[0].get_text()


def test_gui_plain_date_fallback(app, monkeypatch):
    import tkinter as tk
    from tkinter import ttk

    app.date_entry.destroy()
    text = tk.StringVar(app.root, value="02/01/2025")
    app.date_entry = ttk.Entry(app.root, textvariable=text)
    app.vars["use_custom_date"].set(True)
    assert app.selected_date() == date(2025, 1, 2)
    assert app.preferences()["custom_date"] == "2025-01-02"
    text.set("31/02/2025")
    with pytest.raises(ValueError):
        app.selected_date()
    app.vars["font_size"].set("")
    assert app.preferences()["font_size"] == 12.0
