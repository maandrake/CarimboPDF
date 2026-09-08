"""Tkinter interface. PDF processing runs in a separate process."""

import argparse
import os
import tkinter as tk
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from multiprocessing import get_context
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, ttk

from .config import DEFAULTS, load_config, save_config
from .dates import parse_date
from .stamper import StampOptions, data_por_extenso, stamp_pdf

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


class StampApp:
    def __init__(self, root: tk.Tk, args: argparse.Namespace):
        self.root = root
        self.future = None
        self.executor = None
        root.title("CarimboPDF")
        assets = Path(__file__).parent / "assets"
        self.icon_image = tk.PhotoImage(master=root, file=str(assets / "carimbopdf.png"))
        root.iconphoto(True, self.icon_image)
        if os.name == "nt":
            root.iconbitmap(default=str(assets / "carimbopdf.ico"))
        root.minsize(680, 600)
        style = ttk.Style(root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TButton", padding=(12, 7))
        style.configure("TNotebook.Tab", padding=(16, 9))
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", foreground="#536176")
        style.configure("Primary.TButton", foreground="white", background="#2159bc")
        style.map("Primary.TButton", background=[("active", "#194695")])
        values = load_config()
        if args.cidade or os.getenv("CIDADE_PADRAO"):
            values["cidade"] = args.cidade or os.environ["CIDADE_PADRAO"]
        for key in ("font", "logo_path", "logo_width_cm", "logo_margin_cm", "x", "y"):
            value = getattr(args, key, None)
            if value is not None:
                values[key] = value
        # argparse defaults remain compatible with existing CLI invocations.
        for key in ("page", "font_size", "color"):
            value = getattr(args, key)
            if value != DEFAULTS[key]:
                values[key] = value
        for key in ("bold", "italic", "restrict_editing", "no_copy", "encrypt_content"):
            if getattr(args, key):
                values[key] = True
        if args.no_city:
            values["stamp_city"] = False
        if args.no_date:
            values["stamp_date"] = False
        if args.no_auto_logo:
            values["auto_logo"] = False
        if args.in_place or args.output:
            values["inplace"] = bool(args.in_place)
        if args.date:
            values["custom_date"] = parse_date(args.date).isoformat()
            values["use_custom_date"] = True
        self.vars = {
            key: (
                tk.BooleanVar(root, value=value)
                if isinstance(value, bool)
                else tk.StringVar(root, value=value)
            )
            for key, value in values.items()
        }
        for key, value in dict(
            input=args.input or "",
            output=args.output or "",
            protection_password=args.protection_password or "",
            input_password=args.input_password or "",
        ).items():
            self.vars[key] = tk.StringVar(root, value=value)
        try:
            initial_date = date.fromisoformat(values["custom_date"])
        except ValueError:
            initial_date = date.today()
        self.date_text = tk.StringVar(root, value=initial_date.strftime("%d/%m/%Y"))
        self.status = tk.StringVar(root, value="Selecione um PDF para começar.")
        self.preview = tk.StringVar(root)
        shell = ttk.Frame(root, padding=20)
        shell.pack(fill="both", expand=True)
        ttk.Label(shell, text="CarimboPDF", style="Title.TLabel").pack(anchor="w")
        ttk.Label(shell, text="Cidade, data e identidade nos seus documentos.", style="Subtitle.TLabel").pack(
            anchor="w", pady=(2, 16)
        )
        notebook = ttk.Notebook(shell)
        notebook.pack(fill="both", expand=True)
        tabs = {}
        for name in ("Documento", "Carimbo", "Logo", "Proteção"):
            tab = ttk.Frame(notebook, padding=16)
            tab.columnconfigure(1, weight=1)
            notebook.add(tab, text=name)
            tabs[name] = tab
        doc = tabs["Documento"]
        self.entry(doc, 0, "PDF de entrada", "input", lambda: self.browse("input"))
        self.entry(doc, 1, "PDF de saída", "output", lambda: self.browse("output"))
        self.check(doc, 2, "Substituir o PDF original", "inplace", self.update_output)
        self.entry(doc, 3, "Página (0 = primeira)", "page")
        self.entry(doc, 4, "Senha do PDF de entrada", "input_password", secret=True)
        ttk.Label(
            doc,
            text="Por padrão, uma cópia com sufixo _carimbado é criada.",
            wraplength=520,
            style="Subtitle.TLabel",
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=16)
        stamp = tabs["Carimbo"]
        self.entry(stamp, 0, "Cidade", "cidade")
        self.check(stamp, 1, "Carimbar cidade", "stamp_city")
        self.check(stamp, 2, "Carimbar data", "stamp_date", self.update_date)
        self.check(stamp, 3, "Usar data personalizada", "use_custom_date", self.update_date)
        ttk.Label(stamp, text="Data").grid(row=4, column=0, sticky="w")
        if DateEntry:
            self.date_entry = DateEntry(
                stamp, date_pattern="dd/mm/yyyy", maxdate=date.today(), locale="pt_BR"
            )
            self.date_entry.set_date(min(initial_date, date.today()))
        else:
            self.date_entry = ttk.Entry(stamp, textvariable=self.date_text)
        self.date_entry.grid(row=4, column=1, sticky="ew", pady=5)
        ttk.Label(stamp, text="Fonte").grid(row=5, column=0, sticky="w")
        ttk.Combobox(
            stamp, textvariable=self.vars["font"], values=("helv", "times", "cour"), state="readonly"
        ).grid(row=5, column=1, sticky="ew", pady=5)
        self.entry(stamp, 6, "Tamanho (pt)", "font_size")
        self.entry(stamp, 7, "Cor (HEX)", "color", self.choose_color)
        styles = ttk.Frame(stamp)
        styles.grid(row=8, column=1, sticky="w")
        for key, label in (("bold", "Negrito"), ("italic", "Itálico")):
            ttk.Checkbutton(styles, text=label, variable=self.vars[key]).pack(side="left", padx=(0, 12))
        positions = ttk.Frame(stamp)
        positions.grid(row=9, column=1, sticky="ew", pady=5)
        ttk.Label(stamp, text="Posição (pt)").grid(row=9, column=0, sticky="w")
        for key in ("x", "y"):
            ttk.Label(positions, text=key.upper()).pack(side="left", padx=(0, 6))
            ttk.Entry(positions, textvariable=self.vars[key], width=10).pack(side="left", padx=(0, 12))
        ttk.Label(
            stamp, text="X e Y vazios mantêm as posições do modelo original.", style="Subtitle.TLabel"
        ).grid(row=10, column=0, columnspan=2, sticky="w", pady=5)
        logo = tabs["Logo"]
        self.entry(logo, 0, "Imagem", "logo_path", lambda: self.browse("logo_path"))
        self.entry(logo, 1, "Largura (cm)", "logo_width_cm")
        self.entry(logo, 2, "Margem (cm)", "logo_margin_cm")
        self.check(logo, 3, "Buscar logo automaticamente quando o campo estiver vazio", "auto_logo")
        ttk.Label(
            logo,
            text="O logo aparece no canto inferior esquerdo. PNG transparente é preservado.",
            wraplength=520,
            style="Subtitle.TLabel",
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=16)
        protect = tabs["Proteção"]
        password = self.entry(protect, 0, "Senha para edição", "protection_password", secret=True)
        show = tk.BooleanVar(root, value=False)
        ttk.Checkbutton(
            protect,
            text="Mostrar senha",
            variable=show,
            command=lambda: password.configure(show="" if show.get() else "•"),
        ).grid(row=1, column=1, sticky="w")
        self.check(protect, 2, "Restringir edição, anotações e montagem", "restrict_editing")
        self.check(protect, 3, "Desativar cópia", "no_copy")
        self.check(protect, 4, "Aplicar criptografia", "encrypt_content")
        ttk.Label(
            protect,
            text="A proteção usa AES-256 e exige senha de edição. O PDF abre sem senha. "
            "As restrições dependem do leitor de PDF. As senhas não são salvas nas preferências.",
            wraplength=510,
            style="Subtitle.TLabel",
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=16)
        ttk.Label(shell, textvariable=self.preview, style="Subtitle.TLabel", wraplength=610).pack(
            anchor="w", pady=(12, 6)
        )
        self.progress = ttk.Progressbar(shell, mode="indeterminate")
        self.progress.pack(fill="x", pady=4)
        bottom = ttk.Frame(shell)
        bottom.pack(fill="x", pady=(8, 0))
        ttk.Label(bottom, textvariable=self.status, wraplength=390).pack(side="left")
        self.run_button = ttk.Button(
            bottom, text="Carimbar PDF", style="Primary.TButton", command=self.submit
        )
        self.run_button.pack(side="right")
        for key in ("cidade", "stamp_city", "stamp_date", "use_custom_date"):
            self.vars[key].trace_add("write", self.update_preview)
        self.date_text.trace_add("write", self.update_preview)
        self.date_entry.bind("<<DateEntrySelected>>", self.update_preview)
        self.vars["input"].trace_add("write", lambda *_: self.update_output())
        self.update_date()
        if not args.output:
            self.update_output()
        self.update_preview()
        root.protocol("WM_DELETE_WINDOW", self.close)

    def entry(self, parent, row, label, key, browse=None, secret=False):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=5)
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=1, sticky="ew", pady=5)
        field = ttk.Entry(frame, textvariable=self.vars[key], show="•" if secret else "")
        field.pack(side="left", fill="x", expand=True)
        if browse:
            ttk.Button(frame, text="Selecionar", command=browse).pack(side="left", padx=(8, 0))
        return field

    def check(self, parent, row, label, key, command=None):
        ttk.Checkbutton(parent, text=label, variable=self.vars[key], command=command).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=6
        )

    def browse(self, key):
        if key == "output":
            path = filedialog.asksaveasfilename(
                parent=self.root, defaultextension=".pdf", filetypes=[("PDF", "*.pdf")]
            )
        else:
            types = [("PDF", "*.pdf")] if key == "input" else [("Imagens", "*.png *.jpg *.jpeg")]
            path = filedialog.askopenfilename(parent=self.root, filetypes=types)
        if path:
            self.vars[key].set(path)

    def choose_color(self):
        color = colorchooser.askcolor(parent=self.root)[1]
        if color:
            self.vars["color"].set(color)

    def update_output(self):
        source = self.vars["input"].get().strip()
        if source:
            path = Path(source)
            self.vars["output"].set(
                source if self.vars["inplace"].get() else str(path.with_stem(path.stem + "_carimbado"))
            )

    def update_date(self):
        enabled = self.vars["stamp_date"].get() and self.vars["use_custom_date"].get()
        self.date_entry.configure(state="normal" if enabled else "disabled")
        self.update_preview()

    def selected_date(self):
        if not (self.vars["stamp_date"].get() and self.vars["use_custom_date"].get()):
            return date.today()
        text = self.date_entry.get()
        return parse_date(text)

    def update_preview(self, *_):
        lines = []
        if self.vars["stamp_city"].get():
            lines.append(self.vars["cidade"].get().upper())
        if self.vars["stamp_date"].get():
            try:
                lines.append(data_por_extenso(self.selected_date()).upper() + ".")
            except ValueError:
                lines.append("DATA INVÁLIDA")
        self.preview.set(" • ".join(lines) or "Cidade e data desativadas.")

    def preferences(self):
        values = {key: self.vars[key].get() for key in DEFAULTS}
        for key in ("page", "font_size", "logo_width_cm", "logo_margin_cm"):
            try:
                values[key] = int(values[key]) if key == "page" else float(values[key])
            except ValueError:
                values[key] = DEFAULTS[key]
        if values["use_custom_date"] and values["stamp_date"]:
            try:
                values["custom_date"] = self.selected_date().isoformat()
            except ValueError:
                values["custom_date"] = ""
        return values

    def submit(self):
        if self.future is not None:
            return
        try:
            raw = {key: variable.get() for key, variable in self.vars.items()}
            source = raw["input"].strip()
            output = source if raw["inplace"] else raw["output"].strip()
            if not source or not output:
                raise ValueError("Informe os arquivos de entrada e saída.")
            selected = self.selected_date()
            options = StampOptions(
                page=int(raw["page"]),
                font_size=float(raw["font_size"]),
                font=raw["font"],
                color=raw["color"],
                bold=raw["bold"],
                italic=raw["italic"],
                stamp_city=raw["stamp_city"],
                stamp_date=raw["stamp_date"],
                x=float(raw["x"]) if str(raw["x"]).strip() else None,
                y=float(raw["y"]) if str(raw["y"]).strip() else None,
                logo_path=raw["logo_path"] or None,
                auto_logo=raw["auto_logo"],
                logo_width_cm=float(raw["logo_width_cm"]),
                logo_margin_cm=float(raw["logo_margin_cm"]),
                protection_password=raw["protection_password"] or None,
                input_password=raw["input_password"] or None,
                restrict_editing=raw["restrict_editing"],
                allow_copy=not raw["no_copy"],
                encrypt_content=raw["encrypt_content"],
            )
            if self.executor is None:
                self.executor = ProcessPoolExecutor(max_workers=1, mp_context=get_context("spawn"))
            self.future = self.executor.submit(stamp_pdf, source, output, raw["cidade"], selected, options)
            self.result_path = output
            self.run_button.configure(state="disabled")
            self.progress.start(12)
            self.status.set("Processando PDF…")
            self.root.after(100, self.poll)
        except Exception as exc:
            messagebox.showerror("Não foi possível iniciar", str(exc), parent=self.root)

    def poll(self):
        if not self.future.done():
            self.root.after(100, self.poll)
            return
        self.progress.stop()
        self.run_button.configure(state="normal")
        future, self.future = self.future, None
        try:
            future.result()
        except Exception as exc:
            self.status.set("Falha no processamento.")
            messagebox.showerror("Falha ao carimbar", str(exc), parent=self.root)
        else:
            self.status.set("PDF gerado com sucesso.")
            messagebox.showinfo("Concluído", f"PDF gerado:\n{self.result_path}", parent=self.root)

    def close(self):
        if self.future is not None:
            self.status.set("Aguarde o processamento terminar para sair.")
            return
        try:
            save_config(self.preferences())
        except OSError as exc:
            messagebox.showwarning("Preferências não salvas", str(exc), parent=self.root)
        if self.executor is not None:
            self.executor.shutdown(wait=False)
        self.root.destroy()


def run_gui(args: argparse.Namespace) -> int:
    root = tk.Tk()
    StampApp(root, args)
    root.mainloop()
    return 0
