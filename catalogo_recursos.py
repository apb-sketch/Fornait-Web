"""Explorador local de recursos y prototipo de edición por casillas."""

from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from queue import Empty, Queue
from threading import Thread
from tkinter import filedialog, messagebox, ttk
from zipfile import BadZipFile, ZipFile
import base64
import math
import os
import re
import shutil
import stat
import tkinter as tk
import unicodedata


DEMO_DIR = Path(__file__).resolve().parent / "recursos"
GRID_PATH = DEMO_DIR / "Rejilla_de_edicion_azul.png"

EXTENSIONS = {
    "Texturas": ".png .jpg .jpeg .webp .gif .bmp .tif .tiff .tga .dds .ktx2 .exr .psd .aseprite",
    "Materiales": ".mtl .material .tres .sbsar .mat",
    "Modelos y skins": ".fbx .glb .gltf .blend .obj .dae .usd .usdz .vrm",
    "Animaciones y emotes": ".anim .bvh .animset",
    "Audio": ".wav .mp3 .ogg .flac .opus .aac .m4a .aiff .wem .bnk .mid",
    "Lógica y shaders": ".gd .gdshader .verse .cs .cpp .h .lua .luau .js .ts .py .shader .glsl .hlsl .usf .ush",
}
TYPE_BY_EXT = {
    ext: category
    for category, extensions in EXTENSIONS.items()
    for ext in extensions.split()
}
UNREAL_PREFIXES = {
    "Texturas": ("t_", "hdr_"),
    "Materiales": ("m_", "mi_", "mf_"),
    "Modelos y skins": ("sk_", "sm_", "skel_"),
    "Animaciones y emotes": ("as_", "am_", "bs_", "abp_"),
    "Audio": ("sw_", "sc_", "sfx_", "ms_"),
    "Lógica y shaders": ("bp_", "ac_", "bi_", "wbp_"),
}
SEARCH_TERMS = {
    "Texturas": "textura 2d texture imagen image",
    "Materiales": "material shader",
    "Modelos y skins": "modelo model mesh skin personaje character",
    "Animaciones y emotes": "animacion animation emote gesto baile dance",
    "Audio": "audio musica music sonido sound",
    "Lógica y shaders": "codigo code logica script shader gameplay",
    "Paquetes Unreal": "paquete unreal",
}
NAMES = re.compile(r"^[^<>:\"/\\|?*\x00-\x1f]+$")
DEVICE_NAMES = re.compile(r"^(CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|COM[1-9¹²³]|LPT[1-9¹²³])$", re.I)
PAGE_SIZE = 250
PREVIEW_BYTES = 12 * 1024 * 1024


def normalize(text):
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(re.split(r"[\W_]+", text))


def category_for(path):
    ext = path.suffix.lower()
    if ext == ".uasset":
        for category, prefixes in UNREAL_PREFIXES.items():
            if path.name.lower().startswith(prefixes):
                return category
        return "Paquetes Unreal"
    if ext in {".uexp", ".ubulk", ".uptnl", ".umap"}:
        return "Paquetes Unreal"
    if ext in {".fbx", ".glb", ".gltf"} and re.search(
        r"\b(?:anim|animation|animations|animaciones|emote|emotes|gestos)\b",
        normalize(path.as_posix()),
    ):
        return "Animaciones y emotes"
    return TYPE_BY_EXT.get(ext, "Otros")


@dataclass(frozen=True, slots=True)
class Asset:
    source: Path
    path: PurePosixPath
    size: int
    zipped: bool = False
    category: str = field(init=False)
    searchable: str = field(init=False, repr=False)

    def __post_init__(self):
        category = category_for(self.path)
        object.__setattr__(self, "category", category)
        terms = SEARCH_TERMS.get(category, "")
        object.__setattr__(
            self, "searchable", normalize(f"{self.source.name} {self.path.as_posix()} {terms}")
        )


def safe_zip_member(name):
    parts = name.split("/")
    return all(
        NAMES.fullmatch(part)
        and part == part.rstrip(" .")
        and not DEVICE_NAMES.fullmatch(part.partition(".")[0].rstrip(" "))
        for part in parts
    )


def scan(sources):
    assets = {}
    errors = []
    skipped = 0
    for source, zipped in sources:
        try:
            if zipped:
                with ZipFile(source) as archive:
                    for info in archive.infolist():
                        if info.is_dir() or archive.getinfo(info.filename) is not info:
                            continue
                        if (
                            info.flag_bits & 1
                            or stat.S_ISLNK(info.external_attr >> 16)
                            or not safe_zip_member(info.orig_filename)
                        ):
                            skipped += 1
                            continue
                        path = PurePosixPath(info.filename)
                        assets[(source, path)] = Asset(source, path, info.file_size, zipped=True)
                continue
            if not source.is_dir():
                raise FileNotFoundError("La carpeta no está disponible.")
            for folder, subfolders, files in os.walk(source, onerror=lambda error: errors.append(str(error))):
                if hasattr(Path, "is_junction"):
                    subfolders[:] = [name for name in subfolders if not (Path(folder) / name).is_junction()]
                for filename in files:
                    full_path = Path(folder) / filename
                    try:
                        metadata = full_path.lstat()
                    except OSError:
                        skipped += 1
                        continue
                    if not stat.S_ISREG(metadata.st_mode):
                        continue
                    path = PurePosixPath(full_path.relative_to(source).as_posix())
                    assets[full_path] = Asset(source, path, metadata.st_size)
        except (OSError, BadZipFile, NotImplementedError, UnicodeError) as error:
            errors.append(f"{source.name} — {error}")
    return assets, skipped, errors


def numbered(base, index):
    return base if index == 1 else f"{base} ({index})"


def create_export_folder(parent):
    index = 1
    while True:
        output = parent / numbered("Recursos exportados", index)
        try:
            output.mkdir()
            return output
        except FileExistsError:
            index += 1


def copy_stream(stream, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    index = 1
    candidate = target
    while True:
        try:
            destination = candidate.open("xb")
            break
        except FileExistsError:
            index += 1
            candidate = target.with_name(numbered(target.stem, index) + target.suffix)
    try:
        with destination:
            shutil.copyfileobj(stream, destination)
    except Exception:
        candidate.unlink(missing_ok=True)
        raise


def export_assets(assets, parent):
    output = create_export_folder(parent)
    errors = []
    written = 0
    groups = {}
    used_names = set()
    for asset in assets:
        groups.setdefault(asset.source, []).append(asset)
    for source, group in groups.items():
        label = (source.stem if group[0].zipped else source.name) or "Carpeta"
        index = 1
        while numbered(label, index).casefold() in used_names:
            index += 1
        label = numbered(label, index)
        used_names.add(label.casefold())
        archive = None
        try:
            if group[0].zipped:
                archive = ZipFile(source)
            for asset in group:
                try:
                    target = output.joinpath(label, *asset.path.parts)
                    stream = archive.open(asset.path.as_posix()) if archive else (
                        source.joinpath(*asset.path.parts).open("rb")
                    )
                    with stream:
                        copy_stream(stream, target)
                    written += 1
                except (OSError, KeyError, BadZipFile, RuntimeError, NotImplementedError) as error:
                    errors.append(f"{asset.path} — {error}")
        except (OSError, BadZipFile, UnicodeError) as error:
            errors.append(f"{source.name} — {error}")
        finally:
            if archive is not None:
                archive.close()
    return output, written, errors


def readable_size(size):
    for suffix in ("B", "KB", "MB", "GB"):
        if size < 1024 or suffix == "GB":
            return f"{size} B" if suffix == "B" else f"{size:.1f} {suffix}"
        size /= 1024


def image_bytes(asset):
    if asset.path.suffix.lower() not in {".png", ".gif"} or asset.size > PREVIEW_BYTES:
        return None
    if asset.zipped:
        with ZipFile(asset.source) as archive, archive.open(asset.path.as_posix()) as stream:
            data = stream.read(PREVIEW_BYTES + 1)
    else:
        with asset.source.joinpath(*asset.path.parts).open("rb") as stream:
            data = stream.read(PREVIEW_BYTES + 1)
    if len(data) > PREVIEW_BYTES:
        return None
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
    elif data.startswith((b"GIF87a", b"GIF89a")) and len(data) >= 10:
        width = int.from_bytes(data[6:8], "little")
        height = int.from_bytes(data[8:10], "little")
    else:
        return None
    if 0 < width <= 8192 and 0 < height <= 8192 and width * height <= 20_000_000:
        return data
    return None


BG = "#101622"
PANEL = "#182234"
INPUT = "#202e43"
BORDER = "#3b4d66"
TEXT = "#edf4fe"
MUTED = "#acbed5"
BLUE = "#75d8ff"


def set_styles(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        ".", background=BG, foreground=TEXT, font=("Segoe UI", 10),
        bordercolor=BORDER, darkcolor=BORDER, lightcolor=BORDER,
    )
    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Title.TLabel", font=("Segoe UI", 25, "bold"))
    style.configure("PanelTitle.TLabel", background=PANEL, font=("Segoe UI", 13, "bold"))
    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("Panel.TLabel", background=PANEL, foreground=MUTED)
    style.configure("Count.TLabel", background=PANEL, foreground=BLUE, font=("Segoe UI", 15, "bold"))
    style.configure("TButton", padding=(12, 7), background=INPUT, bordercolor=INPUT)
    style.map("TButton", background=[("active", "#314661")], foreground=[("disabled", "#8191a6")])
    style.configure("Accent.TButton", background=BLUE, foreground=BG, bordercolor=BLUE)
    style.map("Accent.TButton", background=[("disabled", INPUT), ("active", "#a0e5ff")])
    style.configure("TEntry", fieldbackground=INPUT, foreground=TEXT, insertcolor=TEXT, padding=7)
    style.configure("TCombobox", padding=6, arrowcolor=TEXT)
    style.map("TCombobox", fieldbackground=[("readonly", INPUT)], selectbackground=[("readonly", INPUT)])
    root.option_add("*TCombobox*Listbox.background", PANEL)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    style.configure("TNotebook", borderwidth=0)
    style.configure("TNotebook.Tab", background=PANEL, foreground=MUTED, padding=(18, 9))
    style.map("TNotebook.Tab", background=[("selected", INPUT)], foreground=[("selected", TEXT)])
    style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=29)
    style.map("Treeview", background=[("selected", "#24476a")], foreground=[("selected", TEXT)])
    style.configure("Treeview.Heading", background=INPUT, foreground=TEXT, font=("Segoe UI", 9, "bold"))
    style.map("Treeview.Heading", background=[("active", INPUT)])
    style.configure("Vertical.TScrollbar", background=INPUT, troughcolor=PANEL, arrowcolor=MUTED)


class GridDemo(ttk.Frame):
    SIZE = 512

    def __init__(self, parent):
        super().__init__(parent, padding=(16, 18))
        self.selected = set()
        self.applied = set()
        self.visited = set()
        self.paint_value = True
        self.canvas = tk.Canvas(self, width=self.SIZE, height=self.SIZE, bg=BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="n", padx=(0, 20))
        self.image = tk.PhotoImage(file=GRID_PATH).subsample(2)
        self.canvas.bind("<Button-1>", self.start_paint)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.columnconfigure(1, weight=1)

        panel = ttk.Frame(self, padding=20, style="Panel.TFrame")
        panel.grid(row=0, column=1, sticky="nsew")
        ttk.Label(panel, text="Edición de una estructura", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(
            panel, text="Pulsa o arrastra sobre las casillas que quieras vaciar. Aplica los cambios para ver la abertura.",
            wraplength=315, style="Panel.TLabel",
        ).pack(anchor="w", pady=(8, 22))
        self.count = ttk.Label(panel, style="Count.TLabel")
        self.count.pack(anchor="w", pady=(0, 14))
        self.apply_button = ttk.Button(panel, text="Aplicar edición", style="Accent.TButton", command=self.apply)
        self.apply_button.pack(fill="x")
        ttk.Button(panel, text="Restablecer", command=self.reset).pack(fill="x", pady=8)
        ttk.Button(panel, text="Guardar PNG…", command=self.save).pack(fill="x")
        ttk.Label(
            panel, text="Textura original · 1024 × 1024 px · transparencia RGBA", style="Panel.TLabel",
            wraplength=315,
        ).pack(anchor="w", pady=(12, 0))
        self.draw()

    def cell(self, event):
        if 0 <= event.x < self.SIZE and 0 <= event.y < self.SIZE:
            return (event.y * 3 // self.SIZE) * 3 + event.x * 3 // self.SIZE
        return None

    def start_paint(self, event):
        self.visited.clear()
        self.paint_value = self.cell(event) not in self.selected
        self.paint(event)

    def paint(self, event):
        cell = self.cell(event)
        if cell is None or cell in self.visited:
            return
        self.visited.add(cell)
        if self.paint_value:
            self.selected.add(cell)
        else:
            self.selected.discard(cell)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.image)
        for cell in self.selected | self.applied:
            row, col = divmod(cell, 3)
            left, right = col * self.SIZE // 3, (col + 1) * self.SIZE // 3
            top, bottom = row * self.SIZE // 3, (row + 1) * self.SIZE // 3
            if cell in self.applied:
                self.canvas.create_rectangle(left, top, right, bottom, fill=BG, outline=BG)
            if (cell in self.selected) != (cell in self.applied):
                self.canvas.create_rectangle(
                    left + 18, top + 18, right - 18, bottom - 18,
                    fill="#184c55", outline="#9af9d8", width=2,
                )
                self.canvas.create_text(
                    (left + right) // 2, (top + bottom) // 2,
                    text="−" if cell in self.selected else "+", fill="#9af9d8", font=("Segoe UI", 22),
                )
        pending = len(self.selected ^ self.applied)
        self.apply_button.state(["!disabled"] if pending and len(self.selected) < 9 else ["disabled"])
        if len(self.selected) == 9:
            self.count.configure(text="Conserva al menos una casilla")
        elif pending:
            self.count.configure(text="1 cambio pendiente" if pending == 1 else f"{pending} cambios pendientes")
        else:
            count = len(self.applied)
            self.count.configure(text="1 casilla vacía" if count == 1 else f"{count} casillas vacías")

    def apply(self):
        self.applied = self.selected.copy()
        self.draw()

    def reset(self):
        self.selected.clear()
        self.applied.clear()
        self.draw()

    def save(self):
        target = filedialog.asksaveasfilename(
            parent=self, title="Guardar textura original", initialfile=GRID_PATH.name,
            defaultextension=".png", filetypes=[("PNG", "*.png")],
        )
        if not target or Path(target).resolve() == GRID_PATH:
            return
        try:
            shutil.copyfile(GRID_PATH, target)
        except OSError as error:
            messagebox.showerror("No se pudo guardar el PNG", str(error), parent=self)


class Catalog(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=(16, 16))
        self.sources = []
        self.assets = {}
        self.ordered_assets = []
        self.results = []
        self.visible = {}
        self.page = 0
        self.search_timer = None
        self.worker_results = Queue()
        self.preview = None
        self.last_export = None
        self.query = tk.StringVar()
        self.filter = tk.StringVar(value="Todos los tipos")
        self.status = tk.StringVar(value=" ")

        sources = ttk.Frame(self)
        sources.pack(fill="x")
        self.source_buttons = [
            ttk.Button(sources, text="Añadir carpeta…", command=self.add_folder),
            ttk.Button(sources, text="Añadir ZIP…", command=self.add_zip),
            ttk.Button(sources, text="Volver a escanear", command=self.rescan),
        ]
        for button in self.source_buttons:
            button.pack(side="left", padx=(0, 7))

        search_bar = ttk.Frame(self)
        search_bar.pack(fill="x", pady=(14, 10))
        ttk.Label(search_bar, text="Buscar").pack(side="left", padx=(0, 8))
        self.search = ttk.Entry(search_bar, textvariable=self.query)
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        combo = ttk.Combobox(
            search_bar, textvariable=self.filter, state="readonly", width=23,
            values=("Todos los tipos", *EXTENSIONS, "Paquetes Unreal", "Otros"),
        )
        combo.pack(side="left")
        self.query.trace_add("write", self.schedule_search)
        combo.bind("<<ComboboxSelected>>", lambda _: self.refresh())

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        result_panel = ttk.Frame(body)
        result_panel.grid(row=0, column=0, sticky="nsew")
        result_panel.columnconfigure(0, weight=1)
        result_panel.rowconfigure(0, weight=1)
        self.table = ttk.Treeview(result_panel, columns=("name", "kind", "origin"), show="headings")
        for key, title, width in (
            ("name", "Archivo", 270), ("kind", "Tipo", 132), ("origin", "Ruta en la fuente", 210),
        ):
            self.table.heading(key, text=title, anchor="w")
            self.table.column(key, width=width, minwidth=75, stretch=(key != "kind"))
        scroll = ttk.Scrollbar(result_panel, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.table.bind("<<TreeviewSelect>>", self.update_preview)
        self.table.bind("<Control-a>", self.select_page)

        detail = ttk.Frame(body, padding=12, style="Panel.TFrame")
        detail.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        ttk.Label(detail, text="Vista previa", style="PanelTitle.TLabel").pack(anchor="w")
        preview_panel = ttk.Frame(detail, width=208, height=157)
        preview_panel.pack(anchor="w", pady=(13, 8))
        preview_panel.pack_propagate(False)
        self.image_view = tk.Label(preview_panel, bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.image_view.pack(fill="both", expand=True)
        self.details = ttk.Label(detail, wraplength=206, style="Panel.TLabel")
        self.details.pack(anchor="w")
        detail.configure(width=232)
        detail.pack_propagate(False)

        footer = ttk.Frame(self)
        footer.pack(fill="x", pady=(12, 2))
        self.export_button = ttk.Button(
            footer, text="Exportar selección…", style="Accent.TButton", command=self.export_selection,
        )
        self.export_button.pack(side="left")
        self.open_button = ttk.Button(footer, text="Abrir exportación", command=self.open_export)
        self.open_button.pack(side="left", padx=(7, 0))
        self.open_button.state(["disabled"])
        self.next_button = ttk.Button(footer, text="Siguiente ›", command=lambda: self.move_page(1))
        self.next_button.pack(side="right")
        self.prev_button = ttk.Button(footer, text="‹ Anterior", command=lambda: self.move_page(-1))
        self.prev_button.pack(side="right", padx=6)
        self.count = ttk.Label(footer, style="Muted.TLabel")
        self.count.pack(side="right", padx=6)
        ttk.Label(self, textvariable=self.status, style="Muted.TLabel", wraplength=900).pack(anchor="w")

        self.busy = False
        self.render_page()
        if DEMO_DIR.is_dir():
            self.add_sources([(DEMO_DIR, False)])
        self.search.focus_set()

    def add_folder(self):
        folder = filedialog.askdirectory(parent=self, title="Añadir carpeta de recursos", mustexist=True)
        if folder:
            self.add_sources([(Path(folder).resolve(), False)])

    def add_zip(self):
        files = filedialog.askopenfilenames(
            parent=self, title="Añadir paquetes ZIP", filetypes=[("Archivos ZIP", "*.zip")],
        )
        self.add_sources([(Path(file).resolve(), True) for file in files])

    def add_sources(self, sources):
        additions = [source for source in sources if source not in self.sources]
        if not additions:
            return
        self.sources.extend(additions)
        self.run_worker("Indexando recursos…", lambda: scan(additions), self.scan_finished)

    def rescan(self):
        self.run_worker("Actualizando el índice…", lambda: scan(self.sources), self.replace_index)

    def replace_index(self, result):
        self.assets.clear()
        self.scan_finished(result)

    def scan_finished(self, result):
        assets, skipped, errors = result
        self.assets.update(assets)
        self.ordered_assets = sorted(
            self.assets.values(),
            key=lambda asset: (asset.path.name.casefold(), asset.source.name.casefold(), asset.path.as_posix()),
        )
        self.refresh()
        sources = "1 fuente" if len(self.sources) == 1 else f"{len(self.sources):,} fuentes"
        files = "1 archivo indexado" if len(self.assets) == 1 else f"{len(self.assets):,} archivos indexados"
        summary = f"{sources} · {files}"
        if skipped:
            summary += f" · {skipped:,} entradas omitidas en este escaneo"
        self.status.set(summary)
        if errors:
            self.show_errors("Incidencias del escaneo", errors)

    def schedule_search(self, *_):
        if self.search_timer is not None:
            self.after_cancel(self.search_timer)
        self.search_timer = self.after(130, self.refresh)

    def refresh(self):
        if self.search_timer is not None:
            self.after_cancel(self.search_timer)
            self.search_timer = None
        tokens = normalize(self.query.get()).split()
        category = self.filter.get()
        self.results = [
            asset for asset in self.ordered_assets
            if (category == "Todos los tipos" or asset.category == category)
            and all(token in asset.searchable for token in tokens)
        ]
        self.page = 0
        self.render_page()

    def move_page(self, offset):
        self.page += offset
        self.render_page()

    def render_page(self):
        self.table.delete(*self.table.get_children())
        self.visible.clear()
        start = self.page * PAGE_SIZE
        for asset in self.results[start:start + PAGE_SIZE]:
            origin = (PurePosixPath(asset.source.name) / asset.path.parent).as_posix()
            row = self.table.insert("", "end", values=(asset.path.name, asset.category, origin))
            self.visible[row] = asset
        total = len(self.results)
        end = min(start + PAGE_SIZE, total)
        self.count.configure(text=f"{start + 1:,}–{end:,} de {total:,}" if total else "0 resultados")
        self.prev_button.state(["!disabled"] if self.page else ["disabled"])
        self.next_button.state(["!disabled"] if end < total else ["disabled"])
        rows = self.table.get_children()
        if rows:
            self.table.selection_set(rows[0])
            self.table.focus(rows[0])
        self.update_preview()

    def select_page(self, _event):
        self.table.selection_set(self.table.get_children())
        return "break"

    def selected_assets(self):
        return [self.visible[row] for row in self.table.selection() if row in self.visible]

    def update_preview(self, _event=None):
        selection = self.selected_assets()
        self.export_button.state(["!disabled"] if selection and not self.busy else ["disabled"])
        self.image_view.configure(image="", text="Selecciona un archivo")
        self.details.configure(text="")
        self.preview = None
        if len(selection) > 1:
            self.image_view.configure(text=f"{len(selection):,} archivos seleccionados")
            return
        if not selection:
            return
        asset = selection[0]
        self.details.configure(text=f"{asset.path}\n\n{readable_size(asset.size)}\n{asset.source}")
        self.image_view.configure(text="Sin vista previa")
        try:
            data = image_bytes(asset)
            if data is None:
                return
            original = tk.PhotoImage(master=self, data=base64.b64encode(data))
            ratio = max(1, math.ceil(original.width() / 200), math.ceil(original.height() / 148))
            self.preview = original.subsample(ratio)
            self.image_view.configure(image=self.preview, text="")
        except (OSError, KeyError, BadZipFile, tk.TclError, RuntimeError, NotImplementedError):
            self.image_view.configure(text="Vista previa no disponible")

    def export_selection(self):
        selection = self.selected_assets()
        folder = filedialog.askdirectory(parent=self, title="Elegir destino de la exportación", mustexist=True)
        if selection and folder:
            self.run_worker(
                "Exportando archivos…",
                lambda: export_assets(selection, Path(folder)), self.export_finished,
            )

    def export_finished(self, result):
        output, written, errors = result
        self.last_export = output
        self.open_button.state(["!disabled"])
        files = "1 archivo exportado" if written == 1 else f"{written:,} archivos exportados"
        self.status.set(f"{files} a {output}")
        if errors:
            self.show_errors("Incidencias de la exportación", errors)

    def open_export(self):
        if self.last_export is not None:
            try:
                os.startfile(self.last_export)
            except OSError as error:
                messagebox.showerror("No se pudo abrir la carpeta", str(error), parent=self)

    def run_worker(self, action, operation, success):
        self.busy = True
        self.status.set(action)
        for button in self.source_buttons:
            button.state(["disabled"])
        self.export_button.state(["disabled"])

        def job():
            try:
                result = operation()
            except Exception as error:
                self.worker_results.put((False, str(error)))
            else:
                self.worker_results.put((True, result))

        Thread(target=job, daemon=True).start()
        self.after(60, self.finish_worker, success)

    def finish_worker(self, success):
        try:
            completed, value = self.worker_results.get_nowait()
        except Empty:
            self.after(60, self.finish_worker, success)
            return
        self.busy = False
        for button in self.source_buttons:
            button.state(["!disabled"])
        if completed:
            success(value)
        else:
            self.status.set("La operación no se pudo completar")
            messagebox.showerror("Error", value, parent=self)
        self.update_preview()

    def show_errors(self, title, errors):
        details = "\n".join(errors[:8])
        if len(errors) > 8:
            details += f"\n… y {len(errors) - 8} incidencias más."
        messagebox.showwarning(title, details, parent=self)


def main():
    root = tk.Tk()
    root.title("Catálogo de recursos")
    root.geometry("1150x750")
    root.minsize(945, 710)
    root.configure(background=BG)
    set_styles(root)
    shell = ttk.Frame(root, padding=(22, 16))
    shell.pack(fill="both", expand=True)
    ttk.Label(shell, text="Catálogo de recursos", style="Title.TLabel").pack(anchor="w", pady=(0, 14))
    notebook = ttk.Notebook(shell)
    notebook.pack(fill="both", expand=True)
    catalog = Catalog(notebook)
    notebook.add(catalog, text="Biblioteca")
    if GRID_PATH.is_file():
        notebook.add(GridDemo(notebook), text="Rejilla de edición")
    root.bind("<Control-f>", lambda _: (notebook.select(catalog), catalog.search.focus_set()))
    root.mainloop()


if __name__ == "__main__":
    main()
