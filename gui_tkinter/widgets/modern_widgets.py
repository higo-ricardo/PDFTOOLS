"""
Widgets customizados para CustomTkinter.

Implementa botões arredondados, cards com sombra, e outros elementos
estéticos para interface moderna.

Autor: PDF Tools Team
Versão: 2.0.0
"""

import customtkinter as ctk
from tkinter import Canvas
from typing import Optional, Callable, Tuple
import math


class ModernButton(ctk.CTkButton):
    """
    Botão moderno com cantos arredondados e efeitos hover.
    
    Estende CTkButton com melhorias estéticas.
    """
    
    def __init__(
        self,
        master=None,
        text: str = "",
        command: Optional[Callable] = None,
        width: int = 150,
        height: int = 45,
        corner_radius: int = 12,
        icon: str = "",
        **kwargs
    ):
        super().__init__(
            master,
            text=f"{icon} {text}" if icon else text,
            command=command,
            width=width,
            height=height,
            corner_radius=corner_radius,
            **kwargs
        )
        
        # Configurações padrão modernas
        self.configure(
            font=ctk.CTkFont(size=13, weight="bold"),
            hover_color=self._hover_color if hasattr(self, '_hover_color') else None
        )


class ShadowFrame(ctk.CTkFrame):
    """
    Frame com efeito de sombra simulada.
    
    Cria ilusão de elevação usando bordas sutis.
    """
    
    def __init__(
        self,
        master=None,
        shadow_color: str = "#000000",
        shadow_intensity: float = 0.1,
        corner_radius: int = 15,
        **kwargs
    ):
        super().__init__(master, corner_radius=corner_radius, **kwargs)
        
        self.shadow_color = shadow_color
        self.shadow_intensity = shadow_intensity
        self.corner_radius = corner_radius
        
        # Configura aparência elevada
        self.configure(
            fg_color=self._apply_alpha(kwargs.get("fg_color", "#2b2b2b"), 0.95)
        )
    
    def _apply_alpha(self, color: str, alpha: float) -> str:
        """Aplica transparência a uma cor hex."""
        # Implementação simplificada - retorna cor original
        return color


class PreviewCard(ctk.CTkFrame):
    """
    Card para exibição de preview de página PDF.
    
    Mostra thumbnail, número da página e texto preview.
    """
    
    def __init__(
        self,
        master=None,
        page_number: int = 1,
        thumbnail_data: Optional[bytes] = None,
        text_preview: str = "",
        selected: bool = False,
        on_toggle: Optional[Callable[[int, bool], None]] = None,
        **kwargs
    ):
        super().__init__(master, corner_radius=10, **kwargs)
        
        self.page_number = page_number
        self.thumbnail_data = thumbnail_data
        self.text_preview = text_preview
        self.selected = selected
        self.on_toggle = on_toggle
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura UI do card."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header com número da página e checkbox
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        header_frame.grid_columnconfigure(1, weight=1)
        
        self.checkbox_var = ctk.BooleanVar(value=self.selected)
        self.checkbox = ctk.CTkCheckBox(
            header_frame,
            text="",
            variable=self.checkbox_var,
            command=self._on_toggle,
            width=20,
            height=20
        )
        self.checkbox.grid(row=0, column=0, padx=(0, 5))
        
        self.page_label = ctk.CTkLabel(
            header_frame,
            text=f"Página {self.page_number}",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.page_label.grid(row=0, column=1, sticky="w")
        
        # Área da thumbnail
        self.thumbnail_label = ctk.CTkLabel(
            self,
            text="",
            width=120,
            height=160
        )
        self.thumbnail_label.grid(row=1, column=0, padx=8, pady=4)
        
        # Texto preview
        if self.text_preview:
            self.preview_label = ctk.CTkLabel(
                self,
                text=self.text_preview[:80] + ("..." if len(self.text_preview) > 80 else ""),
                font=ctk.CTkFont(size=9),
                wraplength=120,
                justify="left"
            )
            self.preview_label.grid(row=2, column=0, padx=8, pady=(0, 8))
    
    def _on_toggle(self):
        """Handle toggle do checkbox."""
        self.selected = self.checkbox_var.get()
        if self.on_toggle:
            self.on_toggle(self.page_number, self.selected)
    
    def set_thumbnail(self, photo_image):
        """Define imagem da thumbnail."""
        if photo_image:
            self.thumbnail_label.configure(image=photo_image, text="")
    
    def update_selection(self, selected: bool):
        """Atualiza estado de seleção."""
        self.selected = selected
        self.checkbox_var.set(selected)


class ProgressCard(ctk.CTkFrame):
    """
    Card mostrando progresso de operação com detalhes.
    """
    
    def __init__(
        self,
        master=None,
        title: str = "Processando...",
        show_details: bool = True,
        **kwargs
    ):
        super().__init__(master, corner_radius=10, **kwargs)
        
        self.title = title
        self.show_details = show_details
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura UI do card de progresso."""
        self.grid_columnconfigure(0, weight=1)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(self, corner_radius=6)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        
        # Label de porcentagem
        self.percent_label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.percent_label.grid(row=2, column=0, padx=15, pady=(0, 5), sticky="w")
        
        # Detalhes (opcional)
        if self.show_details:
            self.details_label = ctk.CTkLabel(
                self,
                text="",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            self.details_label.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="w")
    
    def update_progress(self, value: float, details: str = ""):
        """
        Atualiza progresso.
        
        Args:
            value: Valor entre 0.0 e 1.0
            details: Texto descritivo opcional
        """
        self.progress_bar.set(value)
        self.percent_label.configure(text=f"{int(value * 100)}%")
        if details:
            self.details_label.configure(text=details)


class DropZoneFrame(ctk.CTkFrame):
    """
    Área de drop para arrastar e soltar arquivos.
    
    Detecta drag-and-drop de arquivos do sistema.
    """
    
    def __init__(
        self,
        master=None,
        on_drop: Optional[Callable[[list], None]] = None,
        text: str = "Arraste e solte PDFs aqui",
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.on_drop = on_drop
        self.text = text
        self.is_hovering = False
        
        self._setup_ui()
        self._setup_drag_drop()
    
    def _setup_ui(self):
        """Configura UI da zona de drop."""
        self.configure(
            corner_radius=15,
            border_width=2,
            border_color="gray",
            fg_color="transparent"
        )
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Ícone e texto
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure((0, 1), weight=1)
        
        self.icon_label = ctk.CTkLabel(
            content_frame,
            text="📁",
            font=ctk.CTkFont(size=48)
        )
        self.icon_label.grid(row=0, column=0, pady=(0, 10))
        
        self.text_label = ctk.CTkLabel(
            content_frame,
            text=self.text,
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.text_label.grid(row=1, column=0)
    
    def _setup_drag_drop(self):
        """Configura handlers de drag-and-drop."""
        # Eventos de enter/leave para highlight
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Nota: Tkinter puro não suporta drop nativo de arquivos
        # Para suporte completo, usar biblioteca tkdnd ou customtkinter com extensão
        # Esta é uma implementação básica visual
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        if not self.is_hovering:
            self.is_hovering = True
            self.configure(border_color="#2196F3", fg_color="#2196F308")
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        if self.is_hovering:
            self.is_hovering = False
            self.configure(border_color="gray", fg_color="transparent")
    
    def set_active(self, active: bool):
        """Ativa/desativa estado visual."""
        if active:
            self.configure(border_color="#4CAF50", fg_color="#4CAF5008")
        else:
            self.configure(border_color="gray", fg_color="transparent")
