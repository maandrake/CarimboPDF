import argparse
import os
import json
import sys
from datetime import date, datetime
from pathlib import Path
from .stamper import StampOptions, stamp_pdf
import tkinter as tk
from tkinter import filedialog, messagebox
try:
    from tkinter import ttk  # type: ignore
except Exception:
    ttk = None

# Tentar importar tkcalendar para o widget de calendário
try:
    from tkcalendar import DateEntry  # type: ignore
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False


def _get_config_file() -> Path:
    """Retorna o caminho do arquivo de configuração."""
    config_dir = Path.home() / ".data_hora_pdf"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def _load_config() -> dict:
    """Carrega as configurações salvas."""
    config_file = _get_config_file()
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_config(config: dict) -> None:
    """Salva as configurações."""
    config_file = _get_config_file()
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _hide_console() -> None:
    """Oculta o console do Windows se estiver rodando em Windows."""
    try:
        import ctypes
        if sys.platform == "win32":
            # Obter o handle da janela do console
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd != 0:
                # Ocultar a janela do console
                ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass  # Se não conseguir ocultar, continua normalmente


def _center_window(root: tk.Tk) -> None:
    """Centraliza a janela na tela."""
    root.update_idletasks()  # Garante que as dimensões estejam corretas
    
    # Obter dimensões da janela
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    
    # Obter dimensões da tela
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calcular posição para centralizar
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    # Definir geometria da janela
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")


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
    # Proteção
    p.add_argument("--protection-password", help="Senha para proteção de edição do documento")
    p.add_argument("--restrict-editing", action="store_true", help="Restringir edição do documento")
    p.add_argument("--no-copy", action="store_true", help="Desativar cópia de texto e imagens")
    p.add_argument("--encrypt-content", action="store_true", help="Criptografar todo o conteúdo do documento")
    # Data personalizada
    p.add_argument("--date", help="Data personalizada no formato DD/MM/AAAA (não pode ser futura)")
    # VBA Integration
    p.add_argument("--vba-api", action="store_true", help="Iniciar servidor de API para integração VBA")
    p.add_argument("--vba-port", type=int, default=8080, help="Porta do servidor VBA (padrão: 8080)")
    return p


def _run_gui_with_form(args: argparse.Namespace) -> int:
    if tk is None or filedialog is None or messagebox is None:
        raise RuntimeError("Tkinter não disponível para o modo GUI.")

    # Ocultar console do Windows
    _hide_console()

    root = tk.Tk()
    root.title("Carimbar PDF - Formulário")
    
    # Configurar ícone da janela se possível
    try:
        # Tentar usar o logo como ícone se existir
        logo_path = Path("Logo.jpg")
        if logo_path.exists():
            # Converter para formato de ícone se necessário
            pass
    except Exception:
        pass

    # Carregar configurações salvas
    saved_config = _load_config()

    # Defaults a partir dos args e do dataclass
    defaults = StampOptions()
    cidade_default = args.cidade or os.environ.get("CIDADE_PADRAO") or saved_config.get("cidade", "Lages/SC.")

    # Tk variables (usando configurações salvas quando disponíveis)
    v_input = tk.StringVar(value=args.input or "")
    v_inplace = tk.BooleanVar(value=saved_config.get("inplace", True if not args.output else False))
    v_output = tk.StringVar(value=args.output or "")
    v_cidade = tk.StringVar(value=cidade_default)
    v_page = tk.IntVar(value=saved_config.get("page", args.page or 0))
    v_fontsize = tk.DoubleVar(value=saved_config.get("font_size", args.font_size or 12.0))
    v_font = tk.StringVar(value=saved_config.get("font", args.font or "helv"))
    v_color = tk.StringVar(value=saved_config.get("color", args.color or "#000000"))
    v_bold = tk.BooleanVar(value=saved_config.get("bold", bool(args.bold)))
    v_logo_path = tk.StringVar(value=saved_config.get("logo_path", args.logo_path or ""))
    v_logo_width = tk.DoubleVar(value=saved_config.get("logo_width_cm", args.logo_width_cm if args.logo_width_cm is not None else defaults.logo_width_cm))
    v_logo_margin = tk.DoubleVar(value=saved_config.get("logo_margin_cm", args.logo_margin_cm if args.logo_margin_cm is not None else defaults.logo_margin_cm))
    v_italic = tk.BooleanVar(value=saved_config.get("italic", bool(getattr(args, "italic", False))))
    # Proteção
    v_protection_password = tk.StringVar(value=saved_config.get("protection_password", getattr(args, "protection_password", "") or ""))
    v_restrict_editing = tk.BooleanVar(value=saved_config.get("restrict_editing", bool(getattr(args, "restrict_editing", False))))
    v_no_copy = tk.BooleanVar(value=saved_config.get("no_copy", bool(getattr(args, "no_copy", False))))
    v_encrypt_content = tk.BooleanVar(value=saved_config.get("encrypt_content", bool(getattr(args, "encrypt_content", False))))
    # Novas opções
    v_show_password = tk.BooleanVar(value=False)
    v_save_password = tk.BooleanVar(value=saved_config.get("save_password", False))
    # Data personalizada
    v_use_custom_date = tk.BooleanVar(value=saved_config.get("use_custom_date", False))
    
    # Carregar data salva ou usar hoje como padrão
    saved_date_str = saved_config.get("custom_date")
    if saved_date_str:
        try:
            saved_date = datetime.strptime(saved_date_str, "%Y-%m-%d").date()
            # Verificar se a data salva não é futura
            if saved_date <= date.today():
                default_date = saved_date
            else:
                default_date = date.today()
        except:
            default_date = date.today()
    else:
        default_date = date.today()

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

    def toggle_password_visibility():
        if v_show_password.get():
            password_entry.configure(show="")
        else:
            password_entry.configure(show="*")

    def toggle_custom_date():
        """Habilita/desabilita o seletor de data."""
        pass  # Será redefinido após criar os widgets

    def save_current_config():
        """Salva as configurações atuais."""
        config = {
            "inplace": v_inplace.get(),
            "cidade": v_cidade.get(),
            "page": v_page.get(),
            "font_size": v_fontsize.get(),
            "font": v_font.get(),
            "color": v_color.get(),
            "bold": v_bold.get(),
            "italic": v_italic.get(),
            "logo_path": v_logo_path.get(),
            "logo_width_cm": v_logo_width.get(),
            "logo_margin_cm": v_logo_margin.get(),
            "restrict_editing": v_restrict_editing.get(),
            "no_copy": v_no_copy.get(),
            "encrypt_content": v_encrypt_content.get(),
            "save_password": v_save_password.get(),
            "use_custom_date": v_use_custom_date.get(),
        }
        
        # Salvar senha apenas se a opção estiver marcada
        if v_save_password.get():
            config["protection_password"] = v_protection_password.get()
            
        # Salvar data personalizada se estiver sendo usada
        if v_use_custom_date.get():
            try:
                if HAS_CALENDAR and hasattr(date_entry, 'get_date'):
                    selected_date = date_entry.get_date()
                    config["custom_date"] = selected_date.strftime("%Y-%m-%d")
                else:
                    config["custom_date"] = default_date.strftime("%Y-%m-%d")
            except:
                pass
        
        _save_config(config)

    def on_closing():
        """Chamado quando a janela é fechada."""
        save_current_config()
        root.destroy()

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
                # Proteção
                protection_password=v_protection_password.get().strip() or None,
                restrict_editing=bool(v_restrict_editing.get()),
                allow_copy=not bool(v_no_copy.get()),  # Invertido: no_copy -> allow_copy
                encrypt_content=bool(v_encrypt_content.get()),
            )
            # aplicar parâmetros de logo se informados
            lw = float(v_logo_width.get())
            lm = float(v_logo_margin.get())
            if lw > 0:
                opts.logo_width_cm = lw
            if lm >= 0:
                opts.logo_margin_cm = lm

            cidade_val = v_cidade.get().strip() or cidade_default
            
            # Determinar qual data usar
            if v_use_custom_date.get():
                try:
                    if HAS_CALENDAR and hasattr(date_entry, 'get_date'):
                        selected_date = date_entry.get_date()
                    else:
                        # Fallback para campo de texto
                        date_str = v_date_string.get()
                        selected_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                        
                    # Verificar se a data não é futura
                    if selected_date > date.today():
                        messagebox.showwarning("Data inválida", "Não é possível usar uma data futura. Usando a data de hoje.", parent=root)
                        selected_date = date.today()
                except Exception:
                    messagebox.showwarning("Data inválida", "Formato de data inválido. Usando a data de hoje.", parent=root)
                    selected_date = date.today()
            else:
                selected_date = date.today()
                
            stamp_pdf(inp, outp, cidade_val, selected_date, opts)
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

    # Data personalizada
    date_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    use_custom_chk = (ttk.Checkbutton(date_row, text="Usar data personalizada:", variable=v_use_custom_date, command=toggle_custom_date) if ttk else tk.Checkbutton(date_row, text="Usar data personalizada:", variable=v_use_custom_date, command=toggle_custom_date))
    
    # Variável para data no formato string (para fallback)
    v_date_string = tk.StringVar(value=default_date.strftime("%d/%m/%Y"))
    
    # Criar widget de data baseado na disponibilidade do tkcalendar
    if HAS_CALENDAR:
        date_entry = DateEntry(date_row, 
                             width=12, 
                             background='darkblue',
                             foreground='white', 
                             borderwidth=2,
                             date_pattern='dd/mm/yyyy',
                             maxdate=date.today(),  # Não permite datas futuras
                             state="disabled")
        date_entry.set_date(default_date)
    else:
        # Fallback para Entry simples se tkcalendar não estiver disponível
        date_entry = (ttk.Entry(date_row, textvariable=v_date_string, width=12, state="disabled") if ttk else tk.Entry(date_row, textvariable=v_date_string, width=12, state="disabled"))
    
    use_custom_chk.pack(side=tk.LEFT, padx=(0, 5))
    date_entry.pack(side=tk.LEFT)
    add_row(5, "", date_row)
    
    # Redefinir a função toggle_custom_date agora que os widgets foram criados
    def toggle_custom_date():
        """Habilita/desabilita o seletor de data."""
        if v_use_custom_date.get():
            date_entry.configure(state="normal")
        else:
            date_entry.configure(state="disabled")

    fontsize_spin = (ttk.Spinbox(container, from_=6, to=72, increment=0.5, textvariable=v_fontsize, width=6) if ttk else tk.Spinbox(container, from_=6, to=72, increment=0.5, textvariable=v_fontsize, width=6))
    add_row(6, "Tamanho fonte:", fontsize_spin)

    font_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    font_entry = (ttk.Combobox(font_row, textvariable=v_font, values=["helv","times","cour"], width=10) if ttk else tk.Entry(font_row, textvariable=v_font, width=12))
    font_entry.pack(side=tk.LEFT)
    add_row(7, "Fonte:", font_row)

    color_entry = (ttk.Entry(container, textvariable=v_color) if ttk else tk.Entry(container, textvariable=v_color))
    add_row(8, "Cor (HEX):", color_entry)

    style_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    bold_chk = (ttk.Checkbutton(style_row, text="Negrito", variable=v_bold) if ttk else tk.Checkbutton(style_row, text="Negrito", variable=v_bold))
    italic_chk = (ttk.Checkbutton(style_row, text="Itálico", variable=v_italic) if ttk else tk.Checkbutton(style_row, text="Itálico", variable=v_italic))
    bold_chk.pack(side=tk.LEFT, padx=6)
    italic_chk.pack(side=tk.LEFT, padx=6)
    add_row(9, "Estilo:", style_row)

    # Logo
    logo_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    logo_entry = (ttk.Entry(logo_row, textvariable=v_logo_path, width=50) if ttk else tk.Entry(logo_row, textvariable=v_logo_path, width=50))
    logo_btn = (ttk.Button(logo_row, text="Selecionar...", command=browse_logo) if ttk else tk.Button(logo_row, text="Selecionar...", command=browse_logo))
    logo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    logo_btn.pack(side=tk.LEFT, padx=6)
    add_row(10, "Logo (opcional):", logo_row)

    logo_w_spin = (ttk.Spinbox(container, from_=0.5, to=20, increment=0.5, textvariable=v_logo_width, width=6) if ttk else tk.Spinbox(container, from_=0.5, to=20, increment=0.5, textvariable=v_logo_width, width=6))
    add_row(11, "Logo largura (cm):", logo_w_spin)

    logo_m_spin = (ttk.Spinbox(container, from_=0.0, to=20, increment=0.5, textvariable=v_logo_margin, width=6) if ttk else tk.Spinbox(container, from_=0.0, to=20, increment=0.5, textvariable=v_logo_margin, width=6))
    add_row(12, "Logo margem (cm):", logo_m_spin)

    # Separador para proteção
    sep_label = (ttk.Label(container, text="PROTEÇÃO DO DOCUMENTO", font=("TkDefaultFont", 9, "bold")) if ttk else tk.Label(container, text="PROTEÇÃO DO DOCUMENTO", font=("TkDefaultFont", 9, "bold")))
    add_row(13, "", sep_label)

    # Campos de proteção
    password_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    password_entry = (ttk.Entry(password_row, textvariable=v_protection_password, show="*", width=30) if ttk else tk.Entry(password_row, textvariable=v_protection_password, show="*", width=30))
    show_password_chk = (ttk.Checkbutton(password_row, text="Mostrar", variable=v_show_password, command=toggle_password_visibility) if ttk else tk.Checkbutton(password_row, text="Mostrar", variable=v_show_password, command=toggle_password_visibility))
    save_password_chk = (ttk.Checkbutton(password_row, text="Salvar como padrão", variable=v_save_password) if ttk else tk.Checkbutton(password_row, text="Salvar como padrão", variable=v_save_password))
    
    password_entry.pack(side=tk.LEFT, padx=(0, 5))
    show_password_chk.pack(side=tk.LEFT, padx=(0, 5))
    save_password_chk.pack(side=tk.LEFT)
    add_row(14, "Senha para edição:", password_row)

    protect_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    restrict_chk = (ttk.Checkbutton(protect_row, text="Restringir edição", variable=v_restrict_editing) if ttk else tk.Checkbutton(protect_row, text="Restringir edição", variable=v_restrict_editing))
    no_copy_chk = (ttk.Checkbutton(protect_row, text="Desativar cópia", variable=v_no_copy) if ttk else tk.Checkbutton(protect_row, text="Desativar cópia", variable=v_no_copy))
    restrict_chk.pack(side=tk.LEFT, padx=6)
    no_copy_chk.pack(side=tk.LEFT, padx=6)
    add_row(15, "Restrições:", protect_row)

    encrypt_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    encrypt_chk = (ttk.Checkbutton(encrypt_row, text="Criptografar todo o conteúdo", variable=v_encrypt_content) if ttk else tk.Checkbutton(encrypt_row, text="Criptografar todo o conteúdo", variable=v_encrypt_content))
    encrypt_chk.pack(side=tk.LEFT, padx=6)
    add_row(16, "Criptografia:", encrypt_row)

    # Botões
    btn_row = (ttk.Frame(container) if ttk else tk.Frame(container))
    run_btn = (ttk.Button(btn_row, text="Carimbar", command=do_stamp) if ttk else tk.Button(btn_row, text="Carimbar", command=do_stamp))
    quit_btn = (ttk.Button(btn_row, text="Sair", command=on_closing) if ttk else tk.Button(btn_row, text="Sair", command=on_closing))
    run_btn.pack(side=tk.LEFT)
    quit_btn.pack(side=tk.LEFT, padx=8)
    add_row(17, "", btn_row)

    # Ajustes finais
    container.columnconfigure(1, weight=1)
    on_toggle_inplace()
    toggle_custom_date()  # Aplicar estado inicial do seletor de data
    
    # Configurar protocolo de fechamento da janela
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Definir tamanho mínimo e centralizar
    root.minsize(580, 500)
    _center_window(root)
    
    # Focar na janela
    root.focus_force()
    root.lift()
    
    root.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # VBA API mode
    if getattr(args, 'vba_api', False):
        try:
            from .vba_integration import VBAIntegrationAPI
            print(f"Iniciando servidor de API VBA na porta {args.vba_port}")
            print("Para parar o servidor, pressione Ctrl+C")
            print("Teste de conectividade: curl http://127.0.0.1:{}/health".format(args.vba_port))
            api = VBAIntegrationAPI(args.vba_port)
            api.run(debug=False)
            return 0
        except ImportError:
            print("Erro: Flask não está instalado. Execute: pip install flask")
            return 1
        except KeyboardInterrupt:
            print("\nServidor VBA API encerrado pelo usuário.")
            return 0
        except Exception as e:
            print(f"Erro ao iniciar servidor VBA API: {e}")
            return 1

    # Modo GUI por padrão se nenhum argumento específico for fornecido
    # ou se --gui foi especificado explicitamente
    should_use_gui = (
        args.gui or 
        not args.input or 
        (not args.input and not args.output and not args.cidade and len([x for x in (argv or []) if not x.startswith('--')]) == 0)
    )
    
    if should_use_gui:
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
        # Proteção
        protection_password=getattr(args, "protection_password", None),
        restrict_editing=getattr(args, "restrict_editing", False),
        allow_copy=not getattr(args, "no_copy", False),  # Invertido
        encrypt_content=getattr(args, "encrypt_content", False),
    )
    if args.logo_width_cm is not None:
        opts.logo_width_cm = args.logo_width_cm
    if args.logo_margin_cm is not None:
        opts.logo_margin_cm = args.logo_margin_cm
    
    # Determinar a data a ser usada
    if getattr(args, 'date', None):
        try:
            custom_date = datetime.strptime(args.date, "%d/%m/%Y").date()
            if custom_date > date.today():
                parser.error("A data não pode ser futura.")
            use_date = custom_date
        except ValueError:
            parser.error("Formato de data inválido. Use DD/MM/AAAA")
    else:
        use_date = date.today()
    
    stamp_pdf(str(input_path), str(output_path), args.cidade, use_date, opts)
    print(f"PDF gerado: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
