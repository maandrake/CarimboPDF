from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import io

import fitz  # PyMuPDF


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
    if len(s) != 6:
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



def stamp_pdf(
    input_pdf: str,
    output_pdf: str,
    cidade: str,
    d: date | None = None,
    options: StampOptions | None = None,
) -> None:
    """Carimba o PDF com "Cidade, dia de mês de ano".

    - input_pdf: caminho do PDF de entrada
    - output_pdf: caminho do PDF de saída
    - cidade: nome da cidade
    - d: data (padrão = hoje)
    - options: configurações de página/posição/estilo
    """
    if options is None:
        options = StampOptions()
    if d is None:
        d = date.today()

    # Duas linhas: 1) cidade  2) data por extenso
    linha1 = f"{cidade}".upper()
    linha2 = f"{data_por_extenso(d)}.".upper()
    linhas_ativas: list[tuple[str, str]] = []
    if options.stamp_city:
        linhas_ativas.append(("city", linha1))
    if options.stamp_date:
        linhas_ativas.append(("date", linha2))

    doc = fitz.open(input_pdf)
    replace_plan: tuple[Path, Path] | None = None
    try:
        if options.page < 0 or options.page >= len(doc):
            raise IndexError(f"Página {options.page} não existe no PDF (total {len(doc)}).")
        page = doc[options.page]

        # Definir posição padrão/atributos
        fontname = _resolve_pdf_font_name(options.font or "helv", options.bold, options.italic)
        used_font = fontname
        fontsize = options.font_size
        color = _parse_hex_color(options.color)

        width, height = page.rect.width, page.rect.height
    # Cálculo de largura com fallback de fonte (usado só para leading)
        try:
            w1 = fitz.get_text_length(linha1, fontname=fontname, fontsize=fontsize)
            w2 = fitz.get_text_length(linha2, fontname=fontname, fontsize=fontsize)
        except Exception:
            fontname = _resolve_pdf_font_name("helv", options.bold, options.italic)
            used_font = fontname
            w1 = fitz.get_text_length(linha1, fontname=fontname, fontsize=fontsize)
            w2 = fitz.get_text_length(linha2, fontname=fontname, fontsize=fontsize)
        leading = fontsize * 1.2  # espaçamento entre linhas (aprox.)

    # Sistema de coordenadas simples:
    # - Origem (0,0) no canto superior esquerdo.
    # - X cresce para a direita; Y cresce para baixo.
    # - X é a posição absoluta do início do texto (alinhado à esquerda).

        # Padrão: posições fixas em pt se x/y não forem informados.
        lines_to_draw: list[tuple[str, float, float]] = []
        if options.x is None and options.y is None:
            default_coords = {
                "city": (337.0, 280.0),
                "date": (391.0, 307.0),
            }
            for kind, text in linhas_ativas:
                x_def, y_def = default_coords.get(kind, (337.0, 280.0))
                lines_to_draw.append((text, x_def, y_def))
        else:
            x_base = options.x if options.x is not None else options.margin
            y_base = options.y if options.y is not None else (height - options.margin)
            temp: list[tuple[str, float, float]] = []
            y_cursor = y_base
            for kind, text in reversed(linhas_ativas):
                temp.append((text, x_base, y_cursor))
                y_cursor -= leading
            lines_to_draw = list(reversed(temp))

        used_font = fontname
        if not lines_to_draw:
            try:
                print("[data-hora-pdf] Aviso: Nenhum texto carimbado (cidade/data desativadas).")
            except Exception:
                pass
        else:
            current_font = fontname
            for text, x_pos, y_pos in lines_to_draw:
                try:
                    page.insert_text((x_pos, y_pos), text, fontsize=fontsize, fontname=current_font, fill=color, render_mode=0)
                except Exception:
                    current_font = _resolve_pdf_font_name("helv", options.bold, options.italic)
                    used_font = current_font
                    page.insert_text((x_pos, y_pos), text, fontsize=fontsize, fontname=current_font, fill=color, render_mode=0)
            # Log simples para depuração
            try:
                print(f"[data-hora-pdf] Fonte efetiva: {used_font} | bold={options.bold} | italic={options.italic}")
            except Exception:
                pass

        # Inserir logo no canto inferior esquerdo, se disponível
        def _resolve_logo_path() -> Path | None:
            # prioridade: options.logo_path > arquivo padrão no CWD > diretório do PDF de entrada
            candidates: list[Path] = []
            if options.logo_path:
                candidates.append(Path(options.logo_path))
            # nomes comuns
            for name in ("Logo.jpg", "logo.jpg", "Logo.png", "logo.png"):
                candidates.append(Path.cwd() / name)
            for name in ("Logo.jpg", "logo.jpg", "Logo.png", "logo.png"):
                candidates.append(Path(input_pdf).resolve().parent / name)
            for p in candidates:
                try:
                    if p.exists():
                        return p
                except Exception:
                    continue
            return None

        logo_file = _resolve_logo_path()
        if logo_file is not None:
            # Inserir somente via Pillow para evitar avisos de ICC do MuPDF
            try:
                from PIL import Image  # type: ignore

                with Image.open(logo_file) as im:
                    im = im.convert("RGB")
                    w_img, h_img = im.size
                    bio = io.BytesIO()
                    # PNG RGB SEM perfil ICC para evitar mensagens do MuPDF
                    im.save(bio, format="PNG", icc_profile=None)
                    data = bio.getvalue()

                w_pt = options.logo_width_cm * 28.3465  # 1cm = 28.3465pt
                h_pt = w_pt * (h_img / w_img)
                left = options.logo_margin_cm * 28.3465
                bottom = height - options.logo_margin_cm * 28.3465
                rect = fitz.Rect(left, bottom - h_pt, left + w_pt, bottom)
                page.insert_image(rect, stream=data, keep_proportion=True)
            except Exception:
                # não interromper o carimbo se o logo falhar
                pass

        # Salvar: se for o mesmo arquivo, salvar em tmp e substituir após fechar
        try:
            same = Path(input_pdf).resolve() == Path(output_pdf).resolve()
        except Exception:
            same = False
        
        # Aplicar proteções se especificadas
        if options.protection_password or options.restrict_editing or not options.allow_copy or options.encrypt_content:
            # Configurar permissões
            permissions = -1  # Todas as permissões por padrão
            
            if options.restrict_editing:
                # Remove permissões de modificação
                permissions &= ~(fitz.PDF_PERM_MODIFY | fitz.PDF_PERM_ANNOTATE | fitz.PDF_PERM_FORM)
            
            if not options.allow_copy:
                # Remove permissões de cópia
                permissions &= ~(fitz.PDF_PERM_COPY | fitz.PDF_PERM_ACCESSIBILITY)
            
            # Definir senhas
            owner_password = options.protection_password or ""
            user_password = ""  # Sem senha para abrir o documento
            
            # Aplicar encriptação
            if options.encrypt_content:
                # Usar encriptação forte
                encrypt_method = fitz.PDF_ENCRYPT_AES_256
            else:
                # Usar encriptação padrão
                encrypt_method = fitz.PDF_ENCRYPT_RC4_128
            
            # Configurar a proteção do documento
            try:
                # O PyMuPDF usa a função save com parâmetros de encriptação
                if same:
                    target = Path(output_pdf)
                    tmp = target.with_name(f"{target.stem}__tmp__{target.suffix}")
                    doc.save(str(tmp), 
                            encryption=encrypt_method,
                            owner_pw=owner_password,
                            user_pw=user_password,
                            permissions=permissions)
                    replace_plan = (tmp, target)
                else:
                    doc.save(output_pdf,
                            encryption=encrypt_method,
                            owner_pw=owner_password,
                            user_pw=user_password,
                            permissions=permissions)
            except Exception as e:
                # Fallback: salvar sem proteção se der erro
                print(f"[data-hora-pdf] Aviso: Não foi possível aplicar proteção: {e}")
                if same:
                    target = Path(output_pdf)
                    tmp = target.with_name(f"{target.stem}__tmp__{target.suffix}")
                    doc.save(str(tmp))
                    replace_plan = (tmp, target)
                else:
                    doc.save(output_pdf)
        else:
            # Salvar normalmente sem proteção
            if same:
                target = Path(output_pdf)
                tmp = target.with_name(f"{target.stem}__tmp__{target.suffix}")
                doc.save(str(tmp))
                replace_plan = (tmp, target)
            else:
                doc.save(output_pdf)
    finally:
        doc.close()
        if replace_plan is not None:
            tmp, target = replace_plan
            try:
                tmp.replace(target)
            finally:
                if tmp.exists():
                    try:
                        tmp.unlink()
                    except Exception:
                        pass
