from __future__ import annotations

import io
import math
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pymupdf as fitz


def _positive(value: float, name: str, *, zero: bool = False) -> None:
    if not math.isfinite(value) or value < 0 or (value == 0 and not zero):
        raise ValueError(f"{name} deve ser um número {'não negativo' if zero else 'positivo'} e finito.")


@dataclass
class StampOptions:
    page: int = 0
    x: float | None = None
    y: float | None = None
    font_size: float = 12.0
    font: str = "helv"  # família base: helv|times|cour (ou nome completo se desejar)
    color: str = "#000000"
    bold: bool = False
    italic: bool = False
    margin: float = 36.0  # 0.5in
    # Logo
    logo_path: str | None = None
    logo_width_cm: float = 2.0
    logo_margin_cm: float = 0.5
    # Proteção com senha
    protection_password: str | None = None  # Senha para proteção (edição)
    restrict_editing: bool = False  # Restringir edição do documento
    allow_copy: bool = True  # Permitir copiar texto
    encrypt_content: bool = False  # Criptografar todo o conteúdo
    # Controle de carimbo
    input_password: str | None = None
    auto_logo: bool = True
    stamp_city: bool = True
    stamp_date: bool = True


def _month_name_pt(month: int) -> str:
    nomes = [
        "janeiro",
        "fevereiro",
        "março",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro",
    ]
    return nomes[month - 1]


def data_por_extenso(d: date) -> str:
    return f"{d.day} de {_month_name_pt(d.month)} de {d.year}"


def _parse_hex_color(hex_color: str):
    s = hex_color.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", s):
        raise ValueError(f"Cor inválida: {hex_color}")
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    return (r, g, b)


def _resolve_pdf_font_name(base: str, bold: bool, italic: bool) -> str:
    base_normalized = base.lower().strip() or "helv"
    font_map = {
        "helv": {
            (False, False): "Helvetica",
            (True, False): "Helvetica-Bold",
            (False, True): "Helvetica-Oblique",
            (True, True): "Helvetica-BoldOblique",
        },
        "times": {
            (False, False): "Times-Roman",
            (True, False): "Times-Bold",
            (False, True): "Times-Italic",
            (True, True): "Times-BoldItalic",
        },
        "cour": {
            (False, False): "Courier",
            (True, False): "Courier-Bold",
            (False, True): "Courier-Oblique",
            (True, True): "Courier-BoldOblique",
        },
    }
    font_name = font_map.get(base_normalized, {}).get((bold, italic))
    if font_name:
        return font_name
    return base_normalized


def _validate(options: StampOptions, cidade: str) -> None:
    _positive(options.font_size, "Tamanho da fonte")
    _positive(options.margin, "Margem", zero=True)
    _positive(options.logo_width_cm, "Largura do logo")
    _positive(options.logo_margin_cm, "Margem do logo", zero=True)
    for name in ("x", "y"):
        value = getattr(options, name)
        if value is not None:
            _positive(value, name.upper(), zero=True)
    _parse_hex_color(options.color)
    if options.stamp_city and not cidade.strip():
        raise ValueError("Informe a cidade ou desative o carimbo da cidade.")
    if options.protection_password and len(options.protection_password.encode("utf-8")) > 40:
        raise ValueError("A senha de edição deve ter no máximo 40 bytes em UTF-8.")
    if (
        options.restrict_editing or not options.allow_copy or options.encrypt_content
    ) and not options.protection_password:
        raise ValueError("Informe uma senha de edição para aplicar a proteção.")


def _resolve_logo(input_pdf: Path, options: StampOptions) -> Path | None:
    if options.logo_path:
        logo = Path(options.logo_path).expanduser()
        if not logo.is_file():
            raise FileNotFoundError(f"Logo não encontrado: {logo}")
        return logo
    if options.auto_logo:
        locations = [Path.cwd(), input_pdf.parent]
        if getattr(sys, "frozen", False):
            locations.extend([Path(sys.executable).parent, Path(getattr(sys, "_MEIPASS", "."))])
        for folder in locations:
            for name in ("Logo.jpg", "logo.jpg", "Logo.png", "logo.png"):
                candidate = folder / name
                if candidate.is_file():
                    return candidate
    return None


def _insert_logo(page: fitz.Page, logo: Path, options: StampOptions) -> None:
    from PIL import Image

    with Image.open(logo) as original:
        # Preserve transparency while removing incompatible ICC profiles.
        im = original.convert("RGBA")
        width, height = im.size
        data = io.BytesIO()
        im.save(data, format="PNG", icc_profile=None)
    w = options.logo_width_cm * 72 / 2.54
    h = w * height / width
    margin = options.logo_margin_cm * 72 / 2.54
    bounds = page.cropbox
    rect = fitz.Rect(margin, bounds.height - margin - h, margin + w, bounds.height - margin)
    if not fitz.Rect(0, 0, bounds.width, bounds.height).contains(rect):
        raise ValueError("O logo não cabe na página com a largura e margem informadas.")
    page.insert_image(rect, stream=data.getvalue(), keep_proportion=True)


def _insert_text(page: fitz.Page, cidade: str, d: date, options: StampOptions) -> None:
    lines = []
    if options.stamp_city:
        lines.append(("city", cidade.strip().upper()))
    if options.stamp_date:
        lines.append(("date", f"{data_por_extenso(d)}.".upper()))
    fontname = _resolve_pdf_font_name(options.font, options.bold, options.italic)
    try:
        fitz.Font(fontname)
    except Exception:
        fontname = _resolve_pdf_font_name("helv", options.bold, options.italic)
    color = _parse_hex_color(options.color)
    for index, (kind, text) in enumerate(lines):
        # Preserve the coordinates of the existing document template.
        if options.x is None and options.y is None:
            x, y = {"city": (337.0, 280.0), "date": (391.0, 307.0)}[kind]
        else:
            x = options.x if options.x is not None else options.margin
            baseline = options.y if options.y is not None else page.cropbox.height - options.margin
            y = baseline - (len(lines) - index - 1) * options.font_size * 1.2
        page.insert_text((x, y), text, fontsize=options.font_size, fontname=fontname, fill=color)


def _save_options(options: StampOptions) -> dict:
    if not options.protection_password:
        return {"encryption": fitz.PDF_ENCRYPT_KEEP}
    permissions = -1
    if options.restrict_editing:
        permissions &= ~(
            fitz.PDF_PERM_MODIFY | fitz.PDF_PERM_ANNOTATE | fitz.PDF_PERM_FORM | fitz.PDF_PERM_ASSEMBLE
        )
    if not options.allow_copy:
        permissions &= ~fitz.PDF_PERM_COPY
    return dict(
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw=options.protection_password,
        user_pw="",
        permissions=permissions,
    )


def stamp_pdf(
    input_pdf: str, output_pdf: str, cidade: str, d: date | None = None, options: StampOptions | None = None
) -> None:
    """Apply a stamp and atomically replace the output only after a successful save.

    Default coordinates are retained for compatibility with existing templates.
    Existing encryption is kept unless new protection is explicitly requested.
    """
    options = options or StampOptions()
    _validate(options, cidade)
    source = Path(input_pdf).expanduser().resolve()
    target = Path(output_pdf).expanduser().resolve()
    logo = _resolve_logo(source, options)
    temporary: Path | None = None
    try:
        with fitz.open(source) as doc:
            if not doc.is_pdf:
                raise ValueError("O arquivo de entrada deve ser um PDF.")
            if doc.needs_pass and not doc.authenticate(options.input_password or ""):
                raise ValueError("PDF protegido: informe a senha de entrada correta.")
            if options.page < 0 or options.page >= len(doc):
                raise IndexError(f"Página {options.page} não existe no PDF (total {len(doc)}).")
            page = doc[options.page]
            _insert_text(page, cidade, d or date.today(), options)
            if logo is not None:
                _insert_logo(page, logo, options)
            fd, name = tempfile.mkstemp(prefix=f".{target.stem}-", suffix=".pdf", dir=target.parent)
            os.close(fd)
            temporary = Path(name)
            # A failed encryption or write must never fall back to an unprotected PDF.
            doc.save(str(temporary), deflate=True, **_save_options(options))
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
