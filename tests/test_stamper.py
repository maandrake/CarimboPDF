from datetime import date
from pathlib import Path

import pymupdf as fitz
import pytest
from PIL import Image

from data_hora_pdf.stamper import StampOptions, stamp_pdf


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "input.pdf"
    with fitz.open() as doc:
        doc.new_page(width=842, height=842).insert_text((50, 50), "ORIGINAL")
        doc.new_page(width=842, height=842)
        doc.save(path)
    return path


def options(**kwargs):
    return StampOptions(auto_logo=False, **kwargs)


def test_stamp_preserves_content_and_default_coordinates(source, tmp_path):
    output = tmp_path / "out.pdf"
    stamp_pdf(str(source), str(output), "São Paulo", date(2025, 9, 3), options())
    with fitz.open(output) as doc:
        assert len(doc) == 2
        text = doc[0].get_text()
        assert "ORIGINAL" in text
        assert "SÃO PAULO" in text
        assert "3 DE SETEMBRO DE 2025." in text
        spans = [
            s for b in doc[0].get_text("dict")["blocks"] for line in b.get("lines", []) for s in line["spans"]
        ]
        assert next(s["origin"] for s in spans if s["text"] == "SÃO PAULO") == (337, 280)
        assert not doc[1].get_text()


def test_in_place(source):
    stamp_pdf(str(source), str(source), "Rio de Janeiro", options=options())
    with fitz.open(source) as doc:
        assert "RIO DE JANEIRO" in doc[0].get_text()
    assert not list(source.parent.glob(".input-*.pdf"))


@pytest.mark.parametrize(
    "overrides",
    [
        {"font_size": 0},
        {"font_size": float("nan")},
        {"logo_width_cm": -1},
        {"logo_margin_cm": -1},
        {"x": float("inf")},
        {"color": "#xyz"},
        {"page": 8},
        {"page": -1},
        {"restrict_editing": True},
        {"allow_copy": False},
        {"encrypt_content": True},
        {"logo_path": "does-not-exist.png"},
    ],
)
def test_invalid_options_leave_original_untouched(source, overrides):
    before = source.read_bytes()
    with pytest.raises((ValueError, IndexError, FileNotFoundError)):
        stamp_pdf(str(source), str(source), "Cidade", options=options(**overrides))
    assert source.read_bytes() == before


@pytest.mark.parametrize("existing", [False, True])
def test_save_failure_never_replaces_output(source, tmp_path, monkeypatch, existing):
    output = tmp_path / "output.pdf"
    if existing:
        output.write_bytes(b"KEEP ME")

    def fail_save(self, target, **kwargs):
        Path(target).write_bytes(b"PARTIAL")
        raise RuntimeError("simulated write/encryption failure")

    monkeypatch.setattr(fitz.Document, "save", fail_save)
    with pytest.raises(RuntimeError):
        stamp_pdf(str(source), str(output), "Cidade", options=options(protection_password="test"))
    assert output.read_bytes() == b"KEEP ME" if existing else not output.exists()
    assert not list(tmp_path.glob(".output-*.pdf"))


def test_aes_permissions_and_preservation(source, tmp_path):
    output = tmp_path / "protected.pdf"
    stamp_pdf(
        str(source),
        str(output),
        "Brasília",
        options=options(
            protection_password="test123",
            restrict_editing=True,
            allow_copy=False,
            bold=True,
            italic=True,
            color="#f00",
            font_size=16,
        ),
    )
    with fitz.open(output) as doc:
        assert not doc.needs_pass
        assert "AES" in doc.metadata["encryption"]
        for permission in (
            fitz.PDF_PERM_MODIFY,
            fitz.PDF_PERM_ANNOTATE,
            fitz.PDF_PERM_FORM,
            fitz.PDF_PERM_ASSEMBLE,
            fitz.PDF_PERM_COPY,
        ):
            assert not doc.permissions & permission
        assert doc.permissions & fitz.PDF_PERM_PRINT
        assert doc.permissions & fitz.PDF_PERM_ACCESSIBILITY
        assert doc.authenticate("test123") & 4
    stamp_pdf(str(output), str(output), "Outra cidade", options=options())
    with fitz.open(output) as doc:
        assert "AES" in doc.metadata["encryption"]
        assert not doc.permissions & fitz.PDF_PERM_COPY


def test_input_password(source, tmp_path):
    locked = tmp_path / "locked.pdf"
    with fitz.open(source) as doc:
        doc.save(locked, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="open", owner_pw="owner")
    before = locked.read_bytes()
    with pytest.raises(ValueError, match="senha"):
        stamp_pdf(str(locked), str(locked), "Cidade", options=options())
    assert locked.read_bytes() == before
    stamp_pdf(str(locked), str(locked), "Cidade", options=options(input_password="open"))
    with fitz.open(locked) as doc:
        assert doc.needs_pass
        assert doc.authenticate("open")
        assert "CIDADE" in doc[0].get_text()


def test_transparent_logo_and_selected_page(source, tmp_path):
    logo = tmp_path / "logo.png"
    Image.new("RGBA", (20, 10), (255, 0, 0, 120)).save(logo)
    stamp_pdf(
        str(source),
        str(source),
        "",
        options=options(logo_path=str(logo), page=1, stamp_city=False, stamp_date=False),
    )
    with fitz.open(source) as doc:
        assert not doc[0].get_images()
        assert len(doc[1].get_images()) == 1
        assert doc[1].get_images()[0][1] != 0  # alpha mask


def test_logo_errors_are_visible(source, tmp_path):
    logo = tmp_path / "bad.png"
    logo.write_bytes(b"not an image")
    before = source.read_bytes()
    with pytest.raises(OSError):
        stamp_pdf(str(source), str(source), "Cidade", options=options(logo_path=str(logo)))
    assert source.read_bytes() == before


@pytest.mark.parametrize("city,dated", [(True, False), (False, True), (False, False)])
def test_optional_lines(source, city, dated):
    stamp_pdf(
        str(source),
        str(source),
        "Cidade",
        date(2025, 1, 2),
        options(stamp_city=city, stamp_date=dated, x=50, y=100),
    )
    with fitz.open(source) as doc:
        text = doc[0].get_text()
        assert ("CIDADE" in text) == city
        assert ("2 DE JANEIRO DE 2025." in text) == dated


def test_unsupported_font_falls_back(source):
    stamp_pdf(str(source), str(source), "Cidade", options=options(font="unknown-font"))
    with fitz.open(source) as doc:
        assert "CIDADE" in doc[0].get_text()
