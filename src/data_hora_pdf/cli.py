"""Interface de linha de comando; Tkinter é carregado apenas no modo gráfico."""

import argparse
import sys
from pathlib import Path

from .dates import parse_date
from .stamper import StampOptions, stamp_pdf


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="data-hora-pdf",
        description="Carimba PDFs com 'Cidade, dia de mês de ano' em um local definido.",
    )
    # No modo --gui, os parâmetros podem ser omitidos
    p.add_argument("--input", help="Caminho do PDF de entrada")
    p.add_argument("--output", help="Caminho do PDF de saída")
    p.add_argument("--cidade", help="Nome da cidade a ser inserida")
    p.add_argument("--page", type=int, default=0, help="Índice da página (0 = primeira)")
    p.add_argument("--x", type=float, help="Posição X em pontos (72pt = 1 polegada)")
    p.add_argument("--y", type=float, help="Posição Y em pontos (72pt = 1 polegada)")
    p.add_argument("--font-size", type=float, default=12.0, help="Tamanho da fonte em pt")
    p.add_argument(
        "--font", default=None, help="Família/nome da fonte (helv|times|cour ou nome base do MuPDF)"
    )
    p.add_argument("--color", default="#000000", help="Cor do texto em HEX, ex: #000000")
    p.add_argument("--bold", action="store_true", help="Usar fonte em negrito")
    p.add_argument("--italic", action="store_true", help="Usar fonte em itálico")
    p.add_argument("--gui", action="store_true", help="Abrir seletor de arquivo e salvar automaticamente")
    p.add_argument("--in-place", action="store_true", help="Sobrescrever o arquivo de entrada")
    # Logo
    p.add_argument(
        "--logo-path", help="Caminho do arquivo de logo (jpg/png). Padrão: Logo.jpg ao lado do PDF."
    )
    p.add_argument(
        "--logo-width-cm",
        type=float,
        default=None,
        help="Largura do logo em centímetros (se omitido, usa o padrão do código)",
    )
    p.add_argument(
        "--logo-margin-cm",
        type=float,
        default=None,
        help="Margem do logo em cm a partir da borda (se omitido, usa o padrão do código)",
    )
    # Proteção
    p.add_argument("--protection-password", help="Senha para proteção de edição do documento")
    p.add_argument("--restrict-editing", action="store_true", help="Restringir edição do documento")
    p.add_argument("--no-copy", action="store_true", help="Desativar cópia de texto e imagens")
    p.add_argument("--encrypt-content", action="store_true", help="Criptografar todo o conteúdo do documento")
    # Data personalizada
    p.add_argument("--date", help="Data personalizada no formato DD/MM/AAAA (não pode ser futura)")
    # Controle de carimbo
    p.add_argument("--no-city", action="store_true", help="Não carimbar a linha da cidade")
    p.add_argument("--no-date", action="store_true", help="Não carimbar a linha da data")
    p.add_argument("--input-password", help="Senha do PDF de entrada")
    p.add_argument("--no-auto-logo", action="store_true", help="Desativar busca automática de logo")
    return p


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    args = parser.parse_args(arguments)
    if args.gui or not arguments:
        from .gui import run_gui

        return run_gui(args)
    if not args.input or (not args.output and not args.in_place):
        parser.error("Informe --input e (--output ou --in-place).")
    if args.output and args.in_place:
        parser.error("Use apenas --output ou --in-place.")
    output = Path(args.input if args.in_place else args.output)
    opts = StampOptions(
        page=args.page,
        x=args.x,
        y=args.y,
        font_size=args.font_size,
        font=args.font or "helv",
        color=args.color,
        bold=args.bold,
        italic=args.italic,
        logo_path=args.logo_path,
        logo_width_cm=2.0 if args.logo_width_cm is None else args.logo_width_cm,
        logo_margin_cm=0.5 if args.logo_margin_cm is None else args.logo_margin_cm,
        protection_password=args.protection_password,
        input_password=args.input_password,
        restrict_editing=args.restrict_editing,
        allow_copy=not args.no_copy,
        encrypt_content=args.encrypt_content,
        stamp_city=not args.no_city,
        stamp_date=not args.no_date,
        auto_logo=not args.no_auto_logo,
    )
    try:
        stamp_pdf(args.input, str(output), args.cidade or "", parse_date(args.date), opts)
    except Exception as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    print(f"PDF gerado: {output}")
    return 0


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()
    raise SystemExit(main())
