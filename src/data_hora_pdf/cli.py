import argparse
import os
from datetime import date
from pathlib import Path
from .stamper import StampOptions, stamp_pdf
import tkinter as tk
from tkinter import filedialog, messagebox
try:
    from tkinter import ttk  # type: ignore
except Exception:
    ttk = None


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
    p.add_argument("--font", default=None, help="Família/nome da fonte (helv|times|cour ou nome base do MuPDF)")
    p.add_argument("--color", default="#000000", help="Cor do texto em HEX, ex: #000000")
    p.add_argument("--bold", action="store_true", help="Usar fonte em negrito")
    p.add_argument("--italic", action="store_true", help="Usar fonte em itálico")
    p.add_argument("--gui", action="store_true", help="Abrir seletor de arquivo e salvar automaticamente")
    p.add_argument("--in-place", action="store_true", help="Sobrescrever o arquivo de entrada")
    # Logo
    p.add_argument("--logo-path", help="Caminho do arquivo de logo (jpg/png). Padrão: Logo.jpg ao lado do PDF.")
    p.add_argument("--logo-width-cm", type=float, default=None, help="Largura do logo em centímetros (se omitido, usa o padrão do código)")
    p.add_argument("--logo-margin-cm", type=float, default=None, help="Margem do logo em cm a partir da borda (se omitido, usa o padrão do código)")
    return p


def _run_gui_with_form(args: argparse.Namespace) -> int:
    if tk is None or filedialog is None or messagebox is None:
        raise RuntimeError("Tkinter não disponível para o modo GUI.")

    root = tk.Tk()
    root.title("Carimbar PDF - Formulário")

    # Defaults a partir dos args e do dataclass
    defaults = StampOptions()
    cidade_default = args.cidade or os.environ.get("CIDADE_PADRAO") or "Lages/SC."

    # Tk variables
    v_input = tk.StringVar(value=args.input or "")
    v_inplace = tk.BooleanVar(value=True if not args.output else False)
    v_output = tk.StringVar(value=args.output or "")
    v_cidade = tk.StringVar(value=cidade_default)
    v_page = tk.IntVar(value=args.page or 0)
    v_fontsize = tk.DoubleVar(value=args.font_size or 12.0)
    v_font = tk.StringVar(value=(args.font or "helv"))
    v_color = tk.StringVar(value=args.color or "#000000")
    v_bold = tk.BooleanVar(value=bool(args.bold))
    v_logo_path = tk.StringVar(value=args.logo_path or "")
    v_logo_width = tk.DoubleVar(value=(args.logo_width_cm if args.logo_width_cm is not None else defaults.logo_width_cm))
    v_logo_margin = tk.DoubleVar(value=(args.logo_margin_cm if args.logo_margin_cm is not None else defaults.logo_margin_cm))
    v_italic = tk.BooleanVar(value=bool(getattr(args, "italic", False)))

    # Helpers
    def browse_input():
        sel = filedialog.askopenfilename(title="Selecione um PDF", filetypes=[("Arquivos PDF", "*.pdf"), ("Todos", "*.*")])
        if sel:
            v_input.set(sel)
            if v_inplace.get():
                v_output.set(sel)

    def browse_output():
        sel = filedialog.asksaveasfilename(title="Salvar como", defaultextension=".pdf", filetypes=[("Arquivos PDF", "*.pdf")])
        if sel:
            v_output.set(sel)

    def browse_logo():
        sel = filedialog.askopenfilename(title="Selecione o logo", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg"), ("Todos", "*.*")])
        if sel:
            v_logo_path.set(sel)

    def on_toggle_inplace():
        if v_inplace.get():
            v_output.set(v_input.get())
            out_entry.configure(state="disabled")
            out_btn.configure(state="disabled")
        else:
            out_entry.configure(state="normal")
            out_btn.configure(state="normal")

    def do_stamp():
        inp = v_input.get().strip()
        outp = v_output.get().strip()
        if not inp:
            messagebox.showerror("Erro", "Selecione um arquivo PDF de entrada.", parent=root)
            return
        if not os.path.exists(inp):
            messagebox.showerror("Erro", f"Arquivo não encontrado:\n{inp}", parent=root)
            return
        if v_inplace.get():
            outp = inp
        elif not outp:
            messagebox.showerror("Erro", "Informe o caminho de saída ou marque 'Salvar no mesmo arquivo'.", parent=root)
            return

        try:
            opts = StampOptions(
                page=v_page.get(),
                font_size=float(v_fontsize.get()),
                font=v_font.get().strip() or "helv",
                color=v_color.get(),
                bold=bool(v_bold.get()),
                italic=bool(v_italic.get()),
                logo_path=v_logo_path.get() or None,
            )
            # aplicar parâmetros de logo se informados
            lw = float(v_logo_width.get())
            lm = float(v_logo_margin.get())
            if lw > 0:
                opts.logo_width_cm = lw
            if lm >= 0:
                opts.logo_margin_cm = lm

            cidade_val = v_cidade.get().strip() or cidade_default
            stamp_pdf(inp, outp, cidade_val, date.today(), opts)
            messagebox.showinfo("Concluído", f"PDF atualizado com sucesso:\n{outp}", parent=root)
        except Exception as e:
            messagebox.showerror("Falha", f"Erro ao processar o PDF:\n{e}", parent=root)

    # Layout
    container = ttk.Frame(root) if ttk else tk.Frame(root)
    container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    def add_row(row, label_text, widget):
        lbl = (ttk.Label(container, text=label_text) if ttk else tk.Label(container, text=label_text))
        lbl.grid(row=row, column=0, sticky="w", pady=4)
        widget.grid(row=row, column=1, sticky="we", pady=4)

    # Input/output
    in_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    in_entry = (ttk.Entry(in_row, textvariable=v_input, width=50) if ttk else tk.Entry(in_row, textvariable=v_input, width=50))
    in_btn = (ttk.Button(in_row, text="Selecionar...", command=browse_input) if ttk else tk.Button(in_row, text="Selecionar...", command=browse_input))
    in_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    in_btn.pack(side=tk.LEFT, padx=6)
    add_row(0, "PDF de entrada:", in_row)

    out_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    out_entry = (ttk.Entry(out_row, textvariable=v_output, width=50) if ttk else tk.Entry(out_row, textvariable=v_output, width=50))
    out_btn = (ttk.Button(out_row, text="Salvar como...", command=browse_output) if ttk else tk.Button(out_row, text="Salvar como...", command=browse_output))
    out_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    out_btn.pack(side=tk.LEFT, padx=6)
    add_row(1, "PDF de saída:", out_row)

    inplace_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    inplace_chk = (ttk.Checkbutton(inplace_row, text="Salvar no mesmo arquivo", variable=v_inplace, command=on_toggle_inplace) if ttk else tk.Checkbutton(inplace_row, text="Salvar no mesmo arquivo", variable=v_inplace, command=on_toggle_inplace))
    inplace_chk.pack(side=tk.LEFT)
    add_row(2, "", inplace_row)

    # Campos básicos
    cidade_entry = (ttk.Entry(container, textvariable=v_cidade) if ttk else tk.Entry(container, textvariable=v_cidade))
    add_row(3, "Cidade:", cidade_entry)

    page_spin = (ttk.Spinbox(container, from_=0, to=9999, textvariable=v_page, width=6) if ttk else tk.Spinbox(container, from_=0, to=9999, textvariable=v_page, width=6))
    add_row(4, "Página (0=1ª):", page_spin)

    fontsize_spin = (ttk.Spinbox(container, from_=6, to=72, increment=0.5, textvariable=v_fontsize, width=6) if ttk else tk.Spinbox(container, from_=6, to=72, increment=0.5, textvariable=v_fontsize, width=6))
    add_row(5, "Tamanho fonte:", fontsize_spin)

    font_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    font_entry = (ttk.Combobox(font_row, textvariable=v_font, values=["helv","times","cour"], width=10) if ttk else tk.Entry(font_row, textvariable=v_font, width=12))
    font_entry.pack(side=tk.LEFT)
    add_row(6, "Fonte:", font_row)

    color_entry = (ttk.Entry(container, textvariable=v_color) if ttk else tk.Entry(container, textvariable=v_color))
    add_row(7, "Cor (HEX):", color_entry)

    style_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    bold_chk = (ttk.Checkbutton(style_row, text="Negrito", variable=v_bold) if ttk else tk.Checkbutton(style_row, text="Negrito", variable=v_bold))
    italic_chk = (ttk.Checkbutton(style_row, text="Itálico", variable=v_italic) if ttk else tk.Checkbutton(style_row, text="Itálico", variable=v_italic))
    bold_chk.pack(side=tk.LEFT, padx=6)
    italic_chk.pack(side=tk.LEFT, padx=6)
    add_row(8, "Estilo:", style_row)

    # Logo
    logo_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    logo_entry = (ttk.Entry(logo_row, textvariable=v_logo_path, width=50) if ttk else tk.Entry(logo_row, textvariable=v_logo_path, width=50))
    logo_btn = (ttk.Button(logo_row, text="Selecionar...", command=browse_logo) if ttk else tk.Button(logo_row, text="Selecionar...", command=browse_logo))
    logo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    logo_btn.pack(side=tk.LEFT, padx=6)
    add_row(9, "Logo (opcional):", logo_row)

    logo_w_spin = (ttk.Spinbox(container, from_=0.5, to=20, increment=0.5, textvariable=v_logo_width, width=6) if ttk else tk.Spinbox(container, from_=0.5, to=20, increment=0.5, textvariable=v_logo_width, width=6))
    add_row(10, "Logo largura (cm):", logo_w_spin)

    logo_m_spin = (ttk.Spinbox(container, from_=0.0, to=20, increment=0.5, textvariable=v_logo_margin, width=6) if ttk else tk.Spinbox(container, from_=0.0, to=20, increment=0.5, textvariable=v_logo_margin, width=6))
    add_row(11, "Logo margem (cm):", logo_m_spin)

    # Botões
    btn_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    run_btn = (ttk.Button(btn_row, text="Carimbar", command=do_stamp) if ttk else tk.Button(btn_row, text="Carimbar", command=do_stamp))
    quit_btn = (ttk.Button(btn_row, text="Sair", command=root.destroy) if ttk else tk.Button(btn_row, text="Sair", command=root.destroy))
    run_btn.pack(side=tk.LEFT)
    quit_btn.pack(side=tk.LEFT, padx=8)
    add_row(12, "", btn_row)

    # Ajustes finais
    container.columnconfigure(1, weight=1)
    on_toggle_inplace()
    root.minsize(520, 0)
    root.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Modo GUI: escolher arquivo de entrada e salvar automaticamente
    if args.gui or not args.input:
        return _run_gui_with_form(args)

    # Modo CLI tradicional (sem GUI)
    if not args.input or (not args.output and not args.in_place) or not args.cidade:
        parser.error("Parâmetros obrigatórios ausentes: --input, (--output ou --in-place) e --cidade.")

    input_path = Path(args.input)
    output_path = Path(args.input) if args.in_place else Path(args.output)
    if not input_path.exists():
        parser.error(f"Arquivo de entrada não encontrado: {input_path}")

    opts = StampOptions(
        page=args.page,
        x=args.x,
        y=args.y,
        font_size=args.font_size,
        font=(args.font or "helv"),
        color=args.color,
        bold=args.bold,
        italic=args.italic,
        logo_path=args.logo_path,
    )
    if args.logo_width_cm is not None:
        opts.logo_width_cm = args.logo_width_cm
    if args.logo_margin_cm is not None:
        opts.logo_margin_cm = args.logo_margin_cm
    stamp_pdf(str(input_path), str(output_path), args.cidade, date.today(), opts)
    print(f"PDF gerado: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
