"""
Widgets reutilizaveis para interface Tkinter/CustomTkinter.

Objetivo: Resolver repetição de código, inconsistência visual e facilitar manutenção.

Lista de Widgets:
- W01: Par Label + Entry Numérico
- W02: Checkbox com Tooltip
- W03: Seletor de Formato (Combobox)
- W04: Botão de Arquivo (File Picker)
- W05: Separador Seccional com Título
- W06: Área de Status Dinâmico
- W07: Grid de Metadados (Read-only)
- W08: Slider com Valor Visível
- W09: Botão de Limpar Lista
- W10: Indicador de "Processando..."
- W11: Card de Resumo Final
- W12: Input de Intervalo Inteligente
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional, Callable, Tuple, List, Dict, Any
import customtkinter as ctk
from pathlib import Path


class NumericEntryPair(ctk.CTkFrame):
    """
    W01 - Par Label + Entry Numérico
    
    Widget composto para entrada de valores numéricos com label descritivo.
    """
    
    def __init__(
        self,
        master: Any,
        label_text: str = "Valor",
        default_value: int | float = 0,
        min_value: Optional[int | float] = None,
        max_value: Optional[int | float] = None,
        step: int | float = 1,
        is_integer: bool = True,
        width: int = 120,
        height: int = 40,
        command: Optional[Callable[[int | float], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.label_text = label_text
        self.value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.is_integer = is_integer
        self.command = command
        
        self._setup_ui(width, height)
    
    def _setup_ui(self, width: int, height: int):
        """Configura UI do widget."""
        self.grid_columnconfigure(1, weight=1)
        
        # Label descritivo
        self.label = ctk.CTkLabel(
            self,
            text=self.label_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # Frame para entry e botões
        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.grid(row=0, column=1, sticky="ew")
        entry_frame.grid_columnconfigure(1, weight=1)
        
        # Botão diminuir
        self.btn_decrease = ctk.CTkButton(
            entry_frame,
            text="-",
            width=35,
            height=height,
            corner_radius=8,
            command=self._decrease
        )
        self.btn_decrease.grid(row=0, column=0, padx=(0, 5))
        
        # Entry numérico
        self.var = tk.StringVar(value=str(self.value))
        self.entry = ctk.CTkEntry(
            entry_frame,
            textvariable=self.var,
            width=width,
            height=height,
            corner_radius=8,
            validate="key",
            validatecommand=(self.register(self._validate_input), "%P")
        )
        self.entry.grid(row=0, column=1, padx=5)
        self.entry.bind("<Return>", lambda e: self._on_enter())
        self.entry.bind("<FocusOut>", lambda e: self._on_focus_out())
        
        # Botão aumentar
        self.btn_increase = ctk.CTkButton(
            entry_frame,
            text="+",
            width=35,
            height=height,
            corner_radius=8,
            command=self._increase
        )
        self.btn_increase.grid(row=0, column=2, padx=(5, 0))
    
    def _validate_input(self, new_value: str) -> bool:
        """Valida entrada do usuário."""
        if new_value == "":
            return True
        try:
            val = float(new_value)
            if self.min_value is not None and val < self.min_value:
                return False
            if self.max_value is not None and val > self.max_value:
                return False
            return True
        except ValueError:
            return False
    
    def _on_enter(self):
        """Handle Enter key."""
        self._update_value()
    
    def _on_focus_out(self):
        """Handle focus out."""
        self._update_value()
    
    def _update_value(self):
        """Atualiza valor a partir do entry."""
        try:
            val = float(self.var.get())
            if self.min_value is not None:
                val = max(self.min_value, val)
            if self.max_value is not None:
                val = min(self.max_value, val)
            if self.is_integer:
                val = int(val)
            self.value = val
            self.var.set(str(val))
            if self.command:
                self.command(val)
        except ValueError:
            self.var.set(str(self.value))
    
    def _increase(self):
        """Aumenta valor."""
        new_val = self.value + self.step
        if self.max_value is None or new_val <= self.max_value:
            if self.is_integer:
                new_val = int(new_val)
            self.value = new_val
            self.var.set(str(new_val))
            if self.command:
                self.command(new_val)
    
    def _decrease(self):
        """Diminui valor."""
        new_val = self.value - self.step
        if self.min_value is None or new_val >= self.min_value:
            if self.is_integer:
                new_val = int(new_val)
            self.value = new_val
            self.var.set(str(new_val))
            if self.command:
                self.command(new_val)
    
    def get_value(self) -> int | float:
        """Retorna valor atual."""
        return self.value
    
    def set_value(self, value: int | float):
        """Define novo valor."""
        if self.min_value is not None:
            value = max(self.min_value, value)
        if self.max_value is not None:
            value = min(self.max_value, value)
        if self.is_integer:
            value = int(value)
        self.value = value
        self.var.set(str(value))
    
    def set_enabled(self, enabled: bool):
        """Habilita/desabilita widget."""
        state = "normal" if enabled else "disabled"
        self.entry.configure(state=state)
        self.btn_increase.configure(state=state)
        self.btn_decrease.configure(state=state)


class TooltipCheckbox(ctk.CTkFrame):
    """
    W02 - Checkbox com Tooltip
    
    Checkbox que exibe tooltip explicativo ao passar o mouse.
    """
    
    def __init__(
        self,
        master: Any,
        text: str = "Opção",
        tooltip_text: str = "",
        variable: Optional[ctk.BooleanVar] = None,
        command: Optional[Callable[[bool], None]] = None,
        width: int = 200,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.text = text
        self.tooltip_text = tooltip_text
        self.command = command
        self.tooltip_window = None
        
        self.var = variable if variable else ctk.BooleanVar(value=False)
        self.var.trace_add("write", self._on_var_change)
        
        self._setup_ui(width)
    
    def _setup_ui(self, width: int):
        """Configura UI do widget."""
        self.checkbox = ctk.CTkCheckBox(
            self,
            text=self.text,
            variable=self.var,
            width=width,
            command=self._on_click
        )
        self.checkbox.pack(anchor="w")
        
        # Bind events para tooltip
        self.checkbox.bind("<Enter>", self._show_tooltip)
        self.checkbox.bind("<Leave>", self._hide_tooltip)
    
    def _on_click(self):
        """Handle click no checkbox."""
        if self.command:
            self.command(self.var.get())
    
    def _on_var_change(self, *args):
        """Handle mudança na variável."""
        if self.command:
            self.command(self.var.get())
    
    def _show_tooltip(self, event=None):
        """Exibe tooltip."""
        if not self.tooltip_text:
            return
        
        self.tooltip_window = ctk.CTkToplevel(self)
        self.tooltip_window.withdraw()
        self.tooltip_window.overrideredirect(True)
        
        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.tooltip_text,
            font=ctk.CTkFont(size=11),
            justify="left",
            wraplength=200
        )
        label.pack(padx=8, pady=4)
        
        # Posiciona tooltip acima do checkbox
        x = self.checkbox.winfo_rootx()
        y = self.checkbox.winfo_rooty() - label.winfo_reqheight() - 5
        self.tooltip_window.geometry(f"+{x}+{y}")
        self.tooltip_window.deiconify()
        self.tooltip_window.attributes("-topmost", True)
    
    def _hide_tooltip(self, event=None):
        """Esconde tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def get_value(self) -> bool:
        """Retorna estado do checkbox."""
        return self.var.get()
    
    def set_value(self, value: bool):
        """Define estado do checkbox."""
        self.var.set(value)


class FormatSelector(ctk.CTkFrame):
    """
    W03 - Seletor de Formato (Combobox)
    
    Combobox para seleção de formatos com opções pré-definidas.
    """
    
    def __init__(
        self,
        master: Any,
        label_text: str = "Formato",
        options: Optional[List[str]] = None,
        default: Optional[str] = None,
        width: int = 180,
        height: int = 40,
        command: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.label_text = label_text
        self.options = options or ["PDF", "TXT", "PNG", "JPG"]
        self.default = default or self.options[0]
        self.command = command
        
        self._setup_ui(width, height)
    
    def _setup_ui(self, width: int, height: int):
        """Configura UI do widget."""
        self.grid_columnconfigure(0, weight=1)
        
        # Label
        self.label = ctk.CTkLabel(
            self,
            text=self.label_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Combobox
        self.var = ctk.StringVar(value=self.default)
        self.combobox = ctk.CTkOptionMenu(
            self,
            variable=self.var,
            values=self.options,
            width=width,
            height=height,
            corner_radius=8,
            command=self._on_select
        )
        self.combobox.grid(row=1, column=0, sticky="w")
    
    def _on_select(self, value: str):
        """Handle seleção."""
        if self.command:
            self.command(value)
    
    def get_value(self) -> str:
        """Retorna valor selecionado."""
        return self.var.get()
    
    def set_value(self, value: str):
        """Define valor selecionado."""
        if value in self.options:
            self.var.set(value)
    
    def add_option(self, option: str):
        """Adiciona nova opção."""
        if option not in self.options:
            self.options.append(option)
            self.combobox.configure(values=self.options)
    
    def set_options(self, options: List[str]):
        """Redefine todas as opções."""
        self.options = options
        self.combobox.configure(values=options)


class FilePickerButton(ctk.CTkFrame):
    """
    W04 - Botão de Arquivo (File Picker)
    
    Botão que abre diálogo de seleção de arquivo com path display.
    """
    
    def __init__(
        self,
        master: Any,
        label_text: str = "Arquivo",
        button_text: str = "Selecionar...",
        filetypes: Optional[List[Tuple[str, str]]] = None,
        multiple: bool = False,
        mode: str = "open",  # open, save, directory
        width: int = 300,
        height: int = 40,
        command: Optional[Callable[[List[str]], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.label_text = label_text
        self.button_text = button_text
        self.filetypes = filetypes or [("All files", "*.*")]
        self.multiple = multiple
        self.mode = mode
        self.command = command
        self.selected_files: List[str] = []
        
        self._setup_ui(width, height)
    
    def _setup_ui(self, width: int, height: int):
        """Configura UI do widget."""
        self.grid_columnconfigure(0, weight=1)
        
        # Label
        self.label = ctk.CTkLabel(
            self,
            text=self.label_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Frame para entry e botão
        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.grid(row=1, column=0, sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)
        
        # Entry para mostrar path
        self.var = tk.StringVar(value="")
        self.entry = ctk.CTkEntry(
            entry_frame,
            textvariable=self.var,
            width=width - 100,
            height=height,
            corner_radius=8,
            state="readonly"
        )
        self.entry.grid(row=0, column=0, padx=(0, 5))
        
        # Botão de seleção
        self.btn = ctk.CTkButton(
            entry_frame,
            text=self.button_text,
            width=95,
            height=height,
            corner_radius=8,
            command=self._select_file
        )
        self.btn.grid(row=0, column=1)
    
    def _select_file(self):
        """Abre diálogo de seleção."""
        if self.mode == "open":
            if self.multiple:
                files = filedialog.askopenfilenames(
                    title="Selecionar arquivos",
                    filetypes=self.filetypes
                )
                self.selected_files = list(files)
            else:
                file_path = filedialog.askopenfilename(
                    title="Selecionar arquivo",
                    filetypes=self.filetypes
                )
                self.selected_files = [file_path] if file_path else []
        elif self.mode == "save":
            file_path = filedialog.asksaveasfilename(
                title="Salvar como",
                filetypes=self.filetypes
            )
            self.selected_files = [file_path] if file_path else []
        elif self.mode == "directory":
            dir_path = filedialog.askdirectory(
                title="Selecionar diretório"
            )
            self.selected_files = [dir_path] if dir_path else []
        
        if self.selected_files:
            display_text = ", ".join(Path(f).name for f in self.selected_files[:3])
            if len(self.selected_files) > 3:
                display_text += f" (+{len(self.selected_files) - 3})"
            self.var.set(display_text)
        else:
            self.var.set("")
        
        if self.command:
            self.command(self.selected_files)
    
    def get_files(self) -> List[str]:
        """Retorna arquivos selecionados."""
        return self.selected_files
    
    def clear(self):
        """Limpa seleção."""
        self.selected_files = []
        self.var.set("")
    
    def set_enabled(self, enabled: bool):
        """Habilita/desabilita widget."""
        state = "normal" if enabled else "disabled"
        self.entry.configure(state=state)
        self.btn.configure(state=state)


class SectionSeparator(ctk.CTkFrame):
    """
    W05 - Separador Seccional com Título
    
    Separador horizontal com título centralizado para dividir seções.
    """
    
    def __init__(
        self,
        master: Any,
        title: str = "Seção",
        width: int = 400,
        height: int = 40,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.title = title
        
        self._setup_ui(width, height)
    
    def _setup_ui(self, width: int, height: int):
        """Configura UI do widget."""
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Linha esquerda
        line_left = ctk.CTkFrame(
            self,
            fg_color="#555555",
            width=(width - 100) // 2,
            height=1
        )
        line_left.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#888888"
        )
        self.title_label.grid(row=0, column=1, padx=5)
        
        # Linha direita
        line_right = ctk.CTkFrame(
            self,
            fg_color="#555555",
            width=(width - 100) // 2,
            height=1
        )
        line_right.grid(row=0, column=2, sticky="ew", padx=(5, 0))


class DynamicStatusArea(ctk.CTkFrame):
    """
    W06 - Área de Status Dinâmico
    
    Área para exibição de mensagens de status com ícone e cor dinâmica.
    """
    
    def __init__(
        self,
        master: Any,
        default_message: str = "Pronto",
        width: int = 400,
        height: int = 50,
        **kwargs
    ):
        super().__init__(master, corner_radius=8, **kwargs)
        
        self.default_message = default_message
        
        self._setup_ui(width, height)
    
    def _setup_ui(self, width: int, height: int):
        """Configura UI do widget."""
        self.grid_columnconfigure(1, weight=1)
        self.configure(fg_color="#2b2b2b")
        
        # Ícone de status
        self.icon_label = ctk.CTkLabel(
            self,
            text="✓",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        )
        self.icon_label.grid(row=0, column=0, padx=(12, 8), sticky="w")
        
        # Mensagem de status
        self.message_var = tk.StringVar(value=self.default_message)
        self.message_label = ctk.CTkLabel(
            self,
            textvariable=self.message_var,
            font=ctk.CTkFont(size=12),
            wraplength=width - 80
        )
        self.message_label.grid(row=0, column=1, sticky="w", pady=12)
    
    def set_status(self, message: str, status_type: str = "info"):
        """
        Define status com tipo.
        
        Tipos: info, success, warning, error, processing
        """
        self.message_var.set(message)
        
        icons = {
            "info": ("ℹ", "#2196F3"),
            "success": ("✓", "#4CAF50"),
            "warning": ("⚠", "#FF9800"),
            "error": ("✗", "#f44336"),
            "processing": ("⟳", "#9E9E9E")
        }
        
        icon, color = icons.get(status_type, icons["info"])
        self.icon_label.configure(text=icon, text_color=color)
    
    def clear(self):
        """Limpa status."""
        self.message_var.set(self.default_message)
        self.icon_label.configure(text="✓", text_color="#4CAF50")


class MetadataGrid(ctk.CTkFrame):
    """
    W07 - Grid de Metadados (Read-only)
    
    Exibe metadados em formato de grid chave-valor somente leitura.
    """
    
    def __init__(
        self,
        master: Any,
        metadata: Optional[Dict[str, Any]] = None,
        columns: int = 2,
        width: int = 350,
        **kwargs
    ):
        super().__init__(master, corner_radius=8, **kwargs)
        
        self.metadata = metadata or {}
        self.columns = columns
        
        self._setup_ui(width)
    
    def _setup_ui(self, width: int):
        """Configura UI do widget."""
        self.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame para metadados
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=width,
            height=200,
            corner_radius=0,
            fg_color="transparent"
        )
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.scroll_frame.grid_columnconfigure((0, 1), weight=1)
        
        self._render_metadata()
    
    def _render_metadata(self):
        """Renderiza metadados no grid."""
        # Limpa conteúdo anterior
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        row = 0
        for key, value in self.metadata.items():
            # Chave
            key_label = ctk.CTkLabel(
                self.scroll_frame,
                text=f"{key}:",
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w"
            )
            key_label.grid(row=row, column=0, sticky="w", padx=8, pady=4)
            
            # Valor
            value_label = ctk.CTkLabel(
                self.scroll_frame,
                text=str(value),
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            value_label.grid(row=row, column=1, sticky="w", padx=8, pady=4)
            
            row += 1
    
    def set_metadata(self, metadata: Dict[str, Any]):
        """Atualiza metadados."""
        self.metadata = metadata
        self._render_metadata()
    
    def add_metadata(self, key: str, value: Any):
        """Adiciona um item de metadado."""
        self.metadata[key] = value
        self._render_metadata()
    
    def clear(self):
        """Limpa metadados."""
        self.metadata = {}
        self._render_metadata()


class ValueSlider(ctk.CTkFrame):
    """
    W08 - Slider com Valor Visível
    
    Slider horizontal que exibe o valor atual em tempo real.
    """
    
    def __init__(
        self,
        master: Any,
        label_text: str = "Valor",
        from_: int = 0,
        to: int = 100,
        initial_value: int = 50,
        step: int = 1,
        show_entry: bool = True,
        width: int = 250,
        height: int = 50,
        command: Optional[Callable[[int | float], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.label_text = label_text
        self.from_ = from_
        self.to = to
        self.value = initial_value
        self.step = step
        self.show_entry = show_entry
        self.command = command
        
        self._setup_ui(width, height)
    
    def _setup_ui(self, width: int, height: int):
        """Configura UI do widget."""
        self.grid_columnconfigure(0, weight=1)
        
        # Label e valor
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        self.label = ctk.CTkLabel(
            header_frame,
            text=self.label_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.label.grid(row=0, column=0, sticky="w")
        
        self.value_var = tk.StringVar(value=str(self.value))
        self.value_label = ctk.CTkLabel(
            header_frame,
            textvariable=self.value_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=40,
            anchor="e"
        )
        self.value_label.grid(row=0, column=1, sticky="e")
        
        # Slider
        self.slider = ctk.CTkSlider(
            self,
            from_=self.from_,
            to=self.to,
            number_of_steps=int((self.to - self.from_) / self.step) if self.step > 0 else None,
            width=width,
            height=20,
            command=self._on_slide
        )
        self.slider.set(self.value)
        self.slider.grid(row=1, column=0, sticky="ew")
        
        # Entry opcional
        if self.show_entry:
            self.entry = ctk.CTkEntry(
                self,
                textvariable=self.value_var,
                width=60,
                height=30,
                corner_radius=6
            )
            self.entry.grid(row=2, column=0, sticky="e", pady=(5, 0))
            self.entry.bind("<Return>", lambda e: self._on_entry_submit())
    
    def _on_slide(self, value: float):
        """Handle slide."""
        if self.step > 0:
            value = round(value / self.step) * self.step
        self.value = value
        self.value_var.set(str(int(value) if isinstance(value, float) and value.is_integer() else value))
        if self.command:
            self.command(value)
    
    def _on_entry_submit(self):
        """Handle submit do entry."""
        try:
            val = float(self.value_var.get())
            val = max(self.from_, min(self.to, val))
            if self.step > 0:
                val = round(val / self.step) * self.step
            self.value = val
            self.slider.set(val)
            if self.command:
                self.command(val)
        except ValueError:
            self.value_var.set(str(self.value))
    
    def get_value(self) -> int | float:
        """Retorna valor atual."""
        return self.value
    
    def set_value(self, value: int | float):
        """Define novo valor."""
        val = max(self.from_, min(self.to, value))
        self.value = val
        self.slider.set(val)
        self.value_var.set(str(val))
    
    def set_enabled(self, enabled: bool):
        """Habilita/desabilita widget."""
        state = "normal" if enabled else "disabled"
        self.slider.configure(state=state)
        if self.show_entry:
            self.entry.configure(state=state)


class ClearListButton(ctk.CTkButton):
    """
    W09 - Botão de Limpar Lista
    
    Botão especializado para limpar listas de arquivos/itens.
    """
    
    def __init__(
        self,
        master: Any,
        text: str = "🗑️ Limpar Lista",
        command: Optional[Callable[[], None]] = None,
        confirm: bool = True,
        confirm_message: str = "Tem certeza que deseja limpar a lista?",
        width: int = 140,
        height: int = 40,
        **kwargs
    ):
        self.confirm = confirm
        self.confirm_message = confirm_message
        self.custom_command = command
        
        super().__init__(
            master,
            text=text,
            width=width,
            height=height,
            corner_radius=8,
            fg_color="#f44336",
            hover_color="#d32f2f",
            command=self._on_click,
            **kwargs
        )
    
    def _on_click(self):
        """Handle click com confirmação opcional."""
        if self.confirm:
            from tkinter import messagebox
            if not messagebox.askyesno("Confirmar", self.confirm_message):
                return
        
        if self.custom_command:
            self.custom_command()


class ProcessingIndicator(ctk.CTkFrame):
    """
    W10 - Indicador de "Processando..."
    
    Widget animado que indica processamento em andamento.
    """
    
    def __init__(
        self,
        master: Any,
        message: str = "Processando...",
        width: int = 300,
        height: int = 60,
        **kwargs
    ):
        super().__init__(master, corner_radius=10, **kwargs)
        
        self.message = message
        self.animation_id = None
        
        self._setup_ui(width, height)
    
    def _setup_ui(self, width: int, height: int):
        """Configura UI do widget."""
        self.grid_columnconfigure(1, weight=1)
        self.configure(fg_color="#2b2b2b")
        
        # Spinner animado
        self.spinner_label = ctk.CTkLabel(
            self,
            text="⟳",
            font=ctk.CTkFont(size=20),
            text_color="#2196F3"
        )
        self.spinner_label.grid(row=0, column=0, padx=(15, 10), sticky="w")
        
        # Mensagem
        self.message_var = tk.StringVar(value=self.message)
        self.message_label = ctk.CTkLabel(
            self,
            textvariable=self.message_var,
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        self.message_label.grid(row=0, column=1, sticky="w", pady=15)
        
        # Barra de progresso indeterminada
        self.progress_bar = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            width=width - 60,
            corner_radius=6
        )
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 15))
    
    def start(self, message: Optional[str] = None):
        """Inicia animação."""
        if message:
            self.message_var.set(message)
        self.progress_bar.start()
        self._animate_spinner()
    
    def stop(self):
        """Para animação."""
        self.progress_bar.stop()
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        self.spinner_label.configure(text="⟳")
    
    def _animate_spinner(self):
        """Anima spinner."""
        frames = ["⟳", "⟲"]
        current = self.spinner_label.cget("text")
        next_frame = frames[1] if current == frames[0] else frames[0]
        self.spinner_label.configure(text=next_frame)
        self.animation_id = self.after(500, self._animate_spinner)
    
    def set_message(self, message: str):
        """Atualiza mensagem."""
        self.message_var.set(message)
    
    def is_visible(self) -> bool:
        """Verifica se está visível."""
        return self.winfo_viewable()


class SummaryCard(ctk.CTkFrame):
    """
    W11 - Card de Resumo Final
    
    Card exibindo resumo de operação concluída com estatísticas.
    """
    
    def __init__(
        self,
        master: Any,
        title: str = "Resumo",
        success: bool = True,
        stats: Optional[Dict[str, Any]] = None,
        width: int = 350,
        **kwargs
    ):
        super().__init__(master, corner_radius=12, **kwargs)
        
        self.title = title
        self.success = success
        self.stats = stats or {}
        
        self._setup_ui(width)
    
    def _setup_ui(self, width: int):
        """Configura UI do widget."""
        self.grid_columnconfigure(0, weight=1)
        
        # Header com ícone e título
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        icon = "✓" if self.success else "✗"
        color = "#4CAF50" if self.success else "#f44336"
        
        self.icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=color
        )
        self.icon_label.grid(row=0, column=0, padx=(0, 10))
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=self.title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=1, sticky="w")
        
        # Separador
        separator = ctk.CTkFrame(
            self,
            fg_color="#555555",
            height=1
        )
        separator.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        # Estatísticas
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.stats_frame.grid_columnconfigure((0, 1), weight=1)
        
        self._render_stats()
    
    def _render_stats(self):
        """Renderiza estatísticas."""
        # Limpa conteúdo anterior
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        row = 0
        col = 0
        for key, value in self.stats.items():
            # Chave
            key_label = ctk.CTkLabel(
                self.stats_frame,
                text=f"{key}:",
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            key_label.grid(row=row, column=col, sticky="w", padx=8, pady=4)
            
            # Valor
            value_label = ctk.CTkLabel(
                self.stats_frame,
                text=str(value),
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="e"
            )
            value_label.grid(row=row, column=col + 1, sticky="e", padx=8, pady=4)
            
            col += 2
            if col >= 4:
                col = 0
                row += 1
    
    def update_stats(self, stats: Dict[str, Any]):
        """Atualiza estatísticas."""
        self.stats = stats
        self._render_stats()
    
    def set_success(self, success: bool):
        """Define status de sucesso/erro."""
        self.success = success
        icon = "✓" if success else "✗"
        color = "#4CAF50" if success else "#f44336"
        self.icon_label.configure(text=icon, text_color=color)


class SmartIntervalInput(ctk.CTkFrame):
    """
    W12 - Input de Intervalo Inteligente
    
    Widget para entrada de intervalos com validação e formatação automática.
    Suporta formatos: "1-10", "1,2,3", "1-5,7,9-12"
    """
    
    def __init__(
        self,
        master: Any,
        label_text: str = "Intervalo de Páginas",
        min_value: int = 1,
        max_value: int = 999,
        placeholder: str = "Ex: 1-10 ou 1,2,3 ou 1-5,7,9-12",
        width: int = 350,
        height: int = 80,
        command: Optional[Callable[[List[int]], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.label_text = label_text
        self.min_value = min_value
        self.max_value = max_value
        self.placeholder = placeholder
        self.command = command
        self.parsed_values: List[int] = []
        
        self._setup_ui(width, height)
    
    def _setup_ui(self, width: int, height: int):
        """Configura UI do widget."""
        self.grid_columnconfigure(0, weight=1)
        
        # Label
        self.label = ctk.CTkLabel(
            self,
            text=self.label_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Entry
        self.var = tk.StringVar()
        self.entry = ctk.CTkEntry(
            self,
            textvariable=self.var,
            width=width,
            height=40,
            corner_radius=8,
            placeholder_text=self.placeholder
        )
        self.entry.grid(row=1, column=0, sticky="ew")
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Label de validação
        self.validation_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="#4CAF50"
        )
        self.validation_label.grid(row=2, column=0, sticky="w", pady=(5, 0))
        
        # Chips de preview
        self.chips_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chips_frame.grid(row=3, column=0, sticky="w", pady=(5, 0))
    
    def _on_key_release(self, event=None):
        """Handle tecla pressionada."""
        self._parse_and_validate()
    
    def _on_focus_out(self, event=None):
        """Handle foco perdido."""
        self._parse_and_validate()
    
    def _parse_and_validate(self):
        """Parse e valida entrada."""
        text = self.var.get().strip()
        
        if not text:
            self.parsed_values = []
            self.validation_label.configure(text="", text_color="#4CAF50")
            self._clear_chips()
            return
        
        try:
            values = self._parse_interval(text)
            
            # Valida range
            invalid = [v for v in values if v < self.min_value or v > self.max_value]
            
            if invalid:
                self.validation_label.configure(
                    text=f"Valores fora do range ({self.min_value}-{self.max_value}): {invalid[:3]}",
                    text_color="#f44336"
                )
                self.parsed_values = []
                self._clear_chips()
            else:
                count = len(values)
                self.validation_label.configure(
                    text=f"✓ {count} página(s) selecionada(s)",
                    text_color="#4CAF50"
                )
                self.parsed_values = sorted(set(values))
                self._render_chips()
                
                if self.command:
                    self.command(self.parsed_values)
        
        except Exception as e:
            self.validation_label.configure(
                text=f"✗ Formato inválido: {str(e)}",
                text_color="#f44336"
            )
            self.parsed_values = []
            self._clear_chips()
    
    def _parse_interval(self, text: str) -> List[int]:
        """
        Parse texto de intervalo para lista de inteiros.
        
        Formatos suportados:
        - "1-10" → [1,2,3,4,5,6,7,8,9,10]
        - "1,2,3" → [1,2,3]
        - "1-5,7,9-12" → [1,2,3,4,5,7,9,10,11,12]
        """
        values = []
        parts = text.split(",")
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            if "-" in part:
                # Intervalo
                range_parts = part.split("-")
                if len(range_parts) != 2:
                    raise ValueError(f"Intervalo inválido: {part}")
                
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
                
                if start > end:
                    raise ValueError(f"Início maior que fim: {part}")
                
                values.extend(range(start, end + 1))
            else:
                # Valor único
                values.append(int(part))
        
        return values
    
    def _render_chips(self):
        """Renderiza chips de preview."""
        self._clear_chips()
        
        # Mostra até 10 chips
        for i, val in enumerate(self.parsed_values[:10]):
            chip = ctk.CTkLabel(
                self.chips_frame,
                text=str(val),
                font=ctk.CTkFont(size=10, weight="bold"),
                corner_radius=4,
                fg_color="#2196F3",
                text_color="white",
                padx=6,
                pady=2
            )
            chip.grid(row=0, column=i, padx=2, sticky="w")
        
        # Indicador de mais
        if len(self.parsed_values) > 10:
            more_label = ctk.CTkLabel(
                self.chips_frame,
                text=f"+{len(self.parsed_values) - 10}",
                font=ctk.CTkFont(size=10),
                text_color="#888888"
            )
            more_label.grid(row=0, column=10, padx=2, sticky="w")
    
    def _clear_chips(self):
        """Limpa chips."""
        for widget in self.chips_frame.winfo_children():
            widget.destroy()
    
    def get_values(self) -> List[int]:
        """Retorna valores parseados."""
        return self.parsed_values
    
    def set_values(self, values: List[int]):
        """Define valores diretamente."""
        text = ",".join(str(v) for v in values)
        self.var.set(text)
        self._parse_and_validate()
    
    def clear(self):
        """Limpa entrada."""
        self.var.set("")
        self.parsed_values = []
        self.validation_label.configure(text="", text_color="#4CAF50")
        self._clear_chips()
    
    def set_enabled(self, enabled: bool):
        """Habilita/desabilita widget."""
        state = "normal" if enabled else "disabled"
        self.entry.configure(state=state)


# Exportações
__all__ = [
    "NumericEntryPair",      # W01
    "TooltipCheckbox",       # W02
    "FormatSelector",        # W03
    "FilePickerButton",      # W04
    "SectionSeparator",      # W05
    "DynamicStatusArea",     # W06
    "MetadataGrid",          # W07
    "ValueSlider",           # W08
    "ClearListButton",       # W09
    "ProcessingIndicator",   # W10
    "SummaryCard",           # W11
    "SmartIntervalInput",    # W12
]
