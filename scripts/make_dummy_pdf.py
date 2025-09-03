from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF


def make_blank_pdf(path: str, width: float = 595.276, height: float = 841.89):
    # A4 in points (72dpi): 595.276 x 841.89
    doc = fitz.open()
    page = doc.new_page(width=width, height=height)
    # opcional: borda guia
    rect = page.rect
    page.draw_rect(rect, color=(0.8, 0.8, 0.8), width=0.5)
    doc.save(path)
    doc.close()


if __name__ == "__main__":
    out = Path("dummy.pdf")
    make_blank_pdf(str(out))
    print(f"PDF de teste criado em: {out.resolve()}")
