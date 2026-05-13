"""
Componentes reutilizaveis de dialogos e listagens para Tkinter.

Inclui:
- ProgressDialog: Janela modal de progresso.
- ResultDialog: Janela de sucesso/erro com detalhes.
- DropAreaFrame: Frame com eventos de Drag-and-Drop.
- ThumbnailViewer: Grid scrollavel para previews.
- FileListItem: Widget composto para listagem de arquivos.
"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable, Iterable, Optional


class ProgressDialog(tk.Toplevel):
    """Janela modal para operacoes em progresso."""

    def __init__(
        self,
        master: tk.Misc,
        title: str = "Processando",
        message: str = "Aguarde...",
        allow_cancel: bool = False,
        on_cancel: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self._on_cancel = on_cancel
        self._canceled = False

        container = ttk.Frame(self, padding=14)
        container.pack(fill="both", expand=True)

        self.message_var = tk.StringVar(value=message)
        self.detail_var = tk.StringVar(value="")
        self.progress_var = tk.DoubleVar(value=0.0)

        ttk.Label(container, textvariable=self.message_var).pack(anchor="w")

        self.progressbar = ttk.Progressbar(
            container,
            orient="horizontal",
            mode="determinate",
            variable=self.progress_var,
            maximum=100,
            length=300,
        )
        self.progressbar.pack(fill="x", pady=(10, 6))

        self.percent_label = ttk.Label(container, text="0%")
        self.percent_label.pack(anchor="e")

        self.detail_label = ttk.Label(container, textvariable=self.detail_var, foreground="#555555")
        self.detail_label.pack(anchor="w", pady=(6, 0))

        if allow_cancel:
            btns = ttk.Frame(container)
            btns.pack(fill="x", pady=(10, 0))
            ttk.Button(btns, text="Cancelar", command=self.cancel).pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self.cancel if allow_cancel else self._noop)
        self.update_idletasks()
        self._center(master)

    @property
    def canceled(self) -> bool:
        return self._canceled

    def _center(self, master: tk.Misc) -> None:
        self.update_idletasks()
        if isinstance(master, (tk.Tk, tk.Toplevel)):
            x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.winfo_width() // 2)
            y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _noop(self) -> None:
        return

    def cancel(self) -> None:
        self._canceled = True
        if self._on_cancel:
            self._on_cancel()

    def set_message(self, message: str) -> None:
        self.message_var.set(message)

    def set_detail(self, detail: str) -> None:
        self.detail_var.set(detail)

    def set_progress(self, percent: float, detail: Optional[str] = None) -> None:
        clamped = max(0.0, min(100.0, percent))
        self.progress_var.set(clamped)
        self.percent_label.configure(text=f"{clamped:.0f}%")
        if detail is not None:
            self.detail_var.set(detail)
        self.update_idletasks()

    def start_indeterminate(self) -> None:
        self.progressbar.configure(mode="indeterminate")
        self.progressbar.start(10)

    def stop_indeterminate(self) -> None:
        self.progressbar.stop()
        self.progressbar.configure(mode="determinate")

    def close(self) -> None:
        self.grab_release()
        self.destroy()


class ResultDialog(tk.Toplevel):
    """Dialogo modal para exibir sucesso/erro com detalhes."""

    def __init__(
        self,
        master: tk.Misc,
        title: str,
        message: str,
        success: bool = True,
        details: str = "",
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.resizable(True, True)
        self.transient(master)
        self.grab_set()
        self.minsize(430, 260)

        container = ttk.Frame(self, padding=14)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        icon = "✓" if success else "✗"
        icon_color = "#137333" if success else "#b3261e"
        ttk.Label(container, text=f"{icon} {message}", foreground=icon_color).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        ttk.Separator(container, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.details_text = tk.Text(container, wrap="word", height=10)
        self.details_text.grid(row=2, column=0, sticky="nsew")
        self.details_text.insert("1.0", details.strip() or "Sem detalhes adicionais.")
        self.details_text.configure(state="disabled")

        btns = ttk.Frame(container)
        btns.grid(row=3, column=0, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Fechar", command=self.close).pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.update_idletasks()
        self._center(master)

    def _center(self, master: tk.Misc) -> None:
        self.update_idletasks()
        if isinstance(master, (tk.Tk, tk.Toplevel)):
            x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.winfo_width() // 2)
            y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def close(self) -> None:
        self.grab_release()
        self.destroy()


class DropAreaFrame(ttk.Frame):
    """Frame reutilizavel com suporte a Drag-and-Drop de arquivos."""

    def __init__(
        self,
        master: tk.Misc,
        text: str = "Arraste arquivos aqui",
        on_drop: Optional[Callable[[list[str]], None]] = None,
        filetypes: Optional[list[tuple[str, str]]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, padding=10, **kwargs)
        self.on_drop = on_drop
        self.filetypes = filetypes or [("Todos os arquivos", "*.*")]

        self.configure(style="DropArea.TFrame")

        self.label = ttk.Label(self, text=text, anchor="center", justify="center")
        self.label.pack(fill="both", expand=True, padx=8, pady=8)

        self.bind("<Button-1>", self._select_files)
        self.label.bind("<Button-1>", self._select_files)
        self.bind("<Enter>", lambda _: self.configure(style="DropAreaHover.TFrame"))
        self.bind("<Leave>", lambda _: self.configure(style="DropArea.TFrame"))

        self._configure_styles()
        self._enable_native_dnd_if_available()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.configure("DropArea.TFrame", relief="ridge", borderwidth=2)
        style.configure("DropAreaHover.TFrame", relief="ridge", borderwidth=2)

    def _enable_native_dnd_if_available(self) -> None:
        if hasattr(self, "drop_target_register") and hasattr(self, "dnd_bind"):
            # Suporte para TkinterDnD2 (quando o app raiz for TkinterDnD.Tk)
            self.drop_target_register("DND_Files")
            self.dnd_bind("<<Drop>>", self._on_native_drop)

    def _normalize_dnd_payload(self, payload: str) -> list[str]:
        raw_parts = self.tk.splitlist(payload)
        files = [p.strip("{}") for p in raw_parts if p]
        return [f for f in files if os.path.exists(f)]

    def _on_native_drop(self, event) -> None:
        files = self._normalize_dnd_payload(getattr(event, "data", ""))
        if files and self.on_drop:
            self.on_drop(files)

    def _select_files(self, _event=None) -> None:
        files = filedialog.askopenfilenames(title="Selecionar arquivos", filetypes=self.filetypes)
        if files and self.on_drop:
            self.on_drop(list(files))


class ThumbnailViewer(ttk.Frame):
    """Visualizador de thumbnails em grid com scroll vertical."""

    def __init__(
        self,
        master: tk.Misc,
        columns: int = 4,
        thumbnail_size: tuple[int, int] = (150, 200),
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.columns = max(1, columns)
        self.thumbnail_size = thumbnail_size
        self._items: list[ttk.Frame] = []
        self._image_refs: list[tk.PhotoImage] = []

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind("<Configure>", self._on_frame_configure)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def _on_frame_configure(self, _event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def clear(self) -> None:
        for child in self.inner.winfo_children():
            child.destroy()
        self._items.clear()
        self._image_refs.clear()
        self._on_frame_configure()

    def set_items(self, items: Iterable[dict]) -> None:
        """
        Renderiza thumbnails no grid.

        Cada item pode conter:
        - image: PhotoImage opcional
        - title: str opcional
        - subtitle: str opcional
        - on_click: callback opcional
        """
        self.clear()
        for idx, item in enumerate(items):
            self.add_item(
                image=item.get("image"),
                title=item.get("title", f"Item {idx + 1}"),
                subtitle=item.get("subtitle", ""),
                on_click=item.get("on_click"),
            )

    def add_item(
        self,
        image: Optional[tk.PhotoImage],
        title: str,
        subtitle: str = "",
        on_click: Optional[Callable[[], None]] = None,
    ) -> None:
        idx = len(self._items)
        row = idx // self.columns
        col = idx % self.columns

        card = ttk.Frame(self.inner, padding=8, relief="ridge", borderwidth=1)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="n")

        img_label = ttk.Label(card)
        img_label.pack()
        if image is not None:
            img_label.configure(image=image)
            self._image_refs.append(image)
        else:
            w, h = self.thumbnail_size
            img_label.configure(text="Sem preview", width=max(10, w // 10), anchor="center")

        ttk.Label(card, text=title).pack(anchor="w", pady=(6, 0))
        if subtitle:
            ttk.Label(card, text=subtitle, foreground="#666666").pack(anchor="w")

        if on_click:
            for widget in (card, img_label):
                widget.bind("<Button-1>", lambda _e, cb=on_click: cb())

        self._items.append(card)


class FileListItem(ttk.Frame):
    """Widget composto para item de lista de arquivos."""

    def __init__(
        self,
        master: tk.Misc,
        file_name: str,
        file_path: str,
        size_text: str = "",
        on_remove: Optional[Callable[[str], None]] = None,
        on_open: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, padding=8, **kwargs)
        self.file_path = file_path
        self.on_remove = on_remove
        self.on_open = on_open

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="📄").grid(row=0, column=0, rowspan=2, padx=(0, 8), sticky="n")
        ttk.Label(self, text=file_name).grid(row=0, column=1, sticky="w")
        ttk.Label(self, text=file_path, foreground="#666666").grid(row=1, column=1, sticky="w")

        right = ttk.Frame(self)
        right.grid(row=0, column=2, rowspan=2, padx=(8, 0), sticky="e")

        if size_text:
            ttk.Label(right, text=size_text).pack(side="left", padx=(0, 8))

        ttk.Button(right, text="Abrir", command=self._handle_open).pack(side="left", padx=(0, 4))
        ttk.Button(right, text="Remover", command=self._handle_remove).pack(side="left")

    def _handle_open(self) -> None:
        if self.on_open:
            self.on_open(self.file_path)

    def _handle_remove(self) -> None:
        if self.on_remove:
            self.on_remove(self.file_path)


__all__ = [
    "ProgressDialog",
    "ResultDialog",
    "DropAreaFrame",
    "ThumbnailViewer",
    "FileListItem",
]
