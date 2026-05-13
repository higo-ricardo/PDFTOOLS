"""
ThemeManager - Gerenciador de Temas para PDF Tools

Funcionalidades:
- Alternância instantânea entre modo claro/escuro
- Persistência de preferência em arquivo JSON
- Cobertura total da interface (CustomTkinter + widgets nativos)
- Definição de paletas de cores centralizadas
- Notificação de mudança de tema para componentes registrados

Autor: PDF Tools Team
Versão: 2.3.0
"""

from __future__ import annotations

import json
import os
import tkinter as tk
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

import customtkinter as ctk


@dataclass
class ColorPalette:
    """Paleta de cores para um tema."""
    
    # Cores primárias
    primary_bg: str = "#FFFFFF"
    primary_fg: str = "#1A1A1A"
    
    # Cores de fundo
    frame_bg: str = "#F5F5F5"
    card_bg: str = "#FFFFFF"
    
    # Cores de texto
    text_primary: str = "#1A1A1A"
    text_secondary: str = "#666666"
    text_disabled: str = "#999999"
    
    # Cores de borda
    border_color: str = "#E0E0E0"
    border_focus: str = "#2196F3"
    
    # Cores de destaque
    accent_color: str = "#2196F3"
    accent_hover: str = "#1976D2"
    
    # Cores de status
    success_color: str = "#4CAF50"
    warning_color: str = "#FF9800"
    error_color: str = "#F44336"
    info_color: str = "#2196F3"
    
    # Cores específicas para widgets
    button_fg: str = "#2196F3"
    button_hover: str = "#1976D2"
    button_text: str = "#FFFFFF"
    
    entry_bg: str = "#FFFFFF"
    entry_border: str = "#E0E0E0"
    
    progress_bar_color: str = "#2196F3"
    
    # Cores para drop area
    drop_area_bg: str = "#FAFAFA"
    drop_area_border: str = "#E0E0E0"
    drop_area_hover: str = "#E3F2FD"


# Paleta Modo Escuro
DARK_PALETTE = ColorPalette(
    primary_bg="#1E1E1E",
    primary_fg="#FFFFFF",
    frame_bg="#2D2D2D",
    card_bg="#383838",
    text_primary="#FFFFFF",
    text_secondary="#B0B0B0",
    text_disabled="#666666",
    border_color="#404040",
    border_focus="#64B5F6",
    accent_color="#64B5F6",
    accent_hover="#42A5F5",
    success_color="#81C784",
    warning_color="#FFB74D",
    error_color="#E57373",
    info_color="#64B5F6",
    button_fg="#64B5F6",
    button_hover="#42A5F5",
    button_text="#1E1E1E",
    entry_bg="#2D2D2D",
    entry_border="#404040",
    progress_bar_color="#64B5F6",
    drop_area_bg="#252525",
    drop_area_border="#404040",
    drop_area_hover="#1E3A5F",
)

# Paleta Modo Claro
LIGHT_PALETTE = ColorPalette()


class ThemeManager:
    """
    Gerenciador centralizado de temas para a aplicação PDF Tools.
    
    Responsabilidades:
    - Armazenar e alternar entre temas claro/escuro
    - Persistir preferência do usuário em arquivo JSON
    - Aplicar temas a todos os componentes da interface
    - Notificar componentes registrados sobre mudanças de tema
    - Fornecer acesso centralizado às cores do tema atual
    
    Uso:
        manager = ThemeManager()
        manager.set_theme("dark")  # ou "light"
        manager.toggle_theme()  # alterna entre temas
        
        # Acessar cores
        bg_color = manager.get_color("primary_bg")
        
        # Registrar componente para atualização automática
        manager.register_component(my_frame, on_theme_change_callback)
    """
    
    # Chaves de configuração
    THEME_KEY = "theme"
    DARK_THEME = "dark"
    LIGHT_THEME = "light"
    
    # Arquivo de persistência
    CONFIG_DIR = Path.home() / ".pdf_tools"
    CONFIG_FILE = CONFIG_DIR / "theme_config.json"
    
    def __init__(self) -> None:
        """Inicializa o gerenciador de temas."""
        self._current_theme: str = self.LIGHT_THEME
        self._palette: ColorPalette = LIGHT_PALETTE
        self._components: List[tuple[tk.Widget, Callable[[str], None]]] = []
        self._custom_colors: Dict[str, Dict[str, Any]] = {}
        
        # Carrega preferência salva
        self._load_preference()
        
        # Aplica tema inicial
        self._apply_theme(self._current_theme)
    
    @property
    def current_theme(self) -> str:
        """Retorna o tema atual ('light' ou 'dark')."""
        return self._current_theme
    
    @property
    def palette(self) -> ColorPalette:
        """Retorna a paleta de cores atual."""
        return self._palette
    
    def _get_config_path(self) -> Path:
        """Retorna o caminho do arquivo de configuração."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        return self.CONFIG_FILE
    
    def _load_preference(self) -> None:
        """Carrega preferência de tema do arquivo de configuração."""
        try:
            config_path = self._get_config_path()
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    theme = config.get(self.THEME_KEY, self.LIGHT_THEME)
                    if theme in (self.DARK_THEME, self.LIGHT_THEME):
                        self._current_theme = theme
                        self._palette = DARK_PALETTE if theme == self.DARK_THEME else LIGHT_PALETTE
        except (json.JSONDecodeError, IOError) as e:
            # Em caso de erro, usa tema claro como default
            print(f"Aviso: Não foi possível carregar preferência de tema: {e}")
    
    def _save_preference(self) -> None:
        """Salva preferência de tema no arquivo de configuração."""
        try:
            config_path = self._get_config_path()
            config = {self.THEME_KEY: self._current_theme}
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Aviso: Não foi possível salvar preferência de tema: {e}")
    
    def set_theme(self, theme: str) -> None:
        """
        Define o tema da aplicação.
        
        Args:
            theme: 'light' ou 'dark'
        
        Raises:
            ValueError: Se o tema não for 'light' ou 'dark'
        """
        if theme not in (self.DARK_THEME, self.LIGHT_THEME):
            raise ValueError(f"Tema inválido: {theme}. Use 'light' ou 'dark'.")
        
        if theme == self._current_theme:
            return
        
        self._current_theme = theme
        self._palette = DARK_PALETTE if theme == self.DARK_THEME else LIGHT_PALETTE
        self._apply_theme(theme)
        self._save_preference()
        self._notify_components(theme)
    
    def toggle_theme(self) -> str:
        """
        Alterna entre tema claro e escuro.
        
        Returns:
            O novo tema aplicado ('light' ou 'dark')
        """
        new_theme = self.DARK_THEME if self._current_theme == self.LIGHT_THEME else self.LIGHT_THEME
        self.set_theme(new_theme)
        return new_theme
    
    def get_color(self, color_name: str) -> str:
        """
        Retorna a cor especificada do tema atual.
        
        Args:
            color_name: Nome da cor (ex: 'primary_bg', 'accent_color')
        
        Returns:
            Código hexadecimal da cor
        
        Raises:
            AttributeError: Se a cor não existir na paleta
        """
        if not hasattr(self._palette, color_name):
            raise AttributeError(f"Cor '{color_name}' não encontrada na paleta.")
        return getattr(self._palette, color_name)
    
    def get_all_colors(self) -> Dict[str, str]:
        """Retorna todas as cores do tema atual como dicionário."""
        return {
            key: value for key, value in self._palette.__dict__.items()
            if not key.startswith('_')
        }
    
    def _apply_theme(self, theme: str) -> None:
        """
        Aplica o tema a todos os componentes CustomTkinter e configurações globais.
        
        Args:
            theme: 'light' ou 'dark'
        """
        # Configura tema base do CustomTkinter
        ctk.set_appearance_mode(theme)
        
        # Configura cores do tema CustomTkinter
        self._configure_ctk_theme(theme)
        
        # Atualiza cores customizadas registradas
        self._update_custom_colors()
    
    def _configure_ctk_theme(self, theme: str) -> None:
        """Configura o tema do CustomTkinter com cores personalizadas."""
        p = self._palette
        
        # Tema escuro
        if theme == self.DARK_THEME:
            ctk.ThemeManager.theme["CTkFrame"] = {
                "fg_color": p.frame_bg,
                "border_color": p.border_color,
                "top_fg_color": p.card_bg,
                "corner_radius": 12,
            }
            ctk.ThemeManager.theme["CTkLabel"] = {
                "text_color": p.text_primary,
                "corner_radius": 0,
            }
            ctk.ThemeManager.theme["CTkButton"] = {
                "fg_color": p.button_fg,
                "hover_color": p.button_hover,
                "text_color": p.button_text,
                "border_color": p.border_color,
                "corner_radius": 12,
                "border_width": 0,
            }
            ctk.ThemeManager.theme["CTkEntry"] = {
                "fg_color": p.entry_bg,
                "border_color": p.entry_border,
                "text_color": p.text_primary,
                "corner_radius": 8,
                "border_width": 1,
            }
            ctk.ThemeManager.theme["CTkTextbox"] = {
                "fg_color": p.entry_bg,
                "border_color": p.entry_border,
                "text_color": p.text_primary,
                "corner_radius": 8,
                "border_width": 1,
            }
            ctk.ThemeManager.theme["CTkProgressBar"] = {
                "progress_color": p.progress_bar_color,
                "fg_color": p.frame_bg,
                "border_color": p.border_color,
                "corner_radius": 6,
                "border_width": 0,
            }
            ctk.ThemeManager.theme["CTkSwitch"] = {
                "progress_color": p.accent_color,
                "fg_color": p.border_color,
                "border_color": p.border_color,
                "corner_radius": 16,
                "border_width": 0,
            }
            ctk.ThemeManager.theme["CTkCheckBox"] = {
                "fg_color": p.accent_color,
                "border_color": p.border_color,
                "hover_color": p.accent_hover,
                "checkmark_color": p.button_text,
                "corner_radius": 4,
                "border_width": 1,
            }
            ctk.ThemeManager.theme["CTkRadioButton"] = {
                "fg_color": p.accent_color,
                "border_color": p.border_color,
                "hover_color": p.accent_hover,
                "corner_radius": 10,
                "border_width": 1,
            }
            ctk.ThemeManager.theme["CTkOptionMenu"] = {
                "fg_color": p.button_fg,
                "button_color": p.button_hover,
                "text_color": p.button_text,
                "corner_radius": 12,
            }
            ctk.ThemeManager.theme["CTkComboBox"] = {
                "fg_color": p.entry_bg,
                "border_color": p.entry_border,
                "text_color": p.text_primary,
                "button_color": p.border_color,
                "corner_radius": 8,
                "border_width": 1,
            }
            ctk.ThemeManager.theme["CTkTabview"] = {
                "fg_color": p.frame_bg,
                "border_color": p.border_color,
                "selected_color": p.accent_color,
            }
            ctk.ThemeManager.theme["CTkScrollableFrame"] = {
                "fg_color": p.frame_bg,
                "label_fg_color": p.card_bg,
            }
        
        # Tema claro
        else:
            # Reseta para defaults do CustomTkinter com ajustes
            ctk.ThemeManager.theme["CTkFrame"] = {
                "fg_color": "#F5F5F5",
                "border_color": "#E0E0E0",
                "top_fg_color": "#FFFFFF",
                "corner_radius": 12,
            }
            ctk.ThemeManager.theme["CTkLabel"] = {
                "text_color": "#1A1A1A",
                "corner_radius": 0,
            }
            ctk.ThemeManager.theme["CTkButton"] = {
                "fg_color": "#2196F3",
                "hover_color": "#1976D2",
                "text_color": "#FFFFFF",
                "border_color": "#E0E0E0",
                "corner_radius": 12,
                "border_width": 0,
            }
            ctk.ThemeManager.theme["CTkEntry"] = {
                "fg_color": "#FFFFFF",
                "border_color": "#E0E0E0",
                "text_color": "#1A1A1A",
                "corner_radius": 8,
                "border_width": 1,
            }
            ctk.ThemeManager.theme["CTkTextbox"] = {
                "fg_color": "#FFFFFF",
                "border_color": "#E0E0E0",
                "text_color": "#1A1A1A",
                "corner_radius": 8,
                "border_width": 1,
            }
            ctk.ThemeManager.theme["CTkProgressBar"] = {
                "progress_color": "#2196F3",
                "fg_color": "#F5F5F5",
                "border_color": "#E0E0E0",
                "corner_radius": 6,
                "border_width": 0,
            }
            ctk.ThemeManager.theme["CTkSwitch"] = {
                "progress_color": "#2196F3",
                "fg_color": "#E0E0E0",
                "border_color": "#E0E0E0",
                "corner_radius": 16,
                "border_width": 0,
            }
            ctk.ThemeManager.theme["CTkCheckBox"] = {
                "fg_color": "#2196F3",
                "border_color": "#E0E0E0",
                "hover_color": "#1976D2",
                "checkmark_color": "#FFFFFF",
                "corner_radius": 4,
                "border_width": 1,
            }
            ctk.ThemeManager.theme["CTkRadioButton"] = {
                "fg_color": "#2196F3",
                "border_color": "#E0E0E0",
                "hover_color": "#1976D2",
                "corner_radius": 10,
                "border_width": 1,
            }
            ctk.ThemeManager.theme["CTkOptionMenu"] = {
                "fg_color": "#2196F3",
                "button_color": "#1976D2",
                "text_color": "#FFFFFF",
                "corner_radius": 12,
            }
            ctk.ThemeManager.theme["CTkComboBox"] = {
                "fg_color": "#FFFFFF",
                "border_color": "#E0E0E0",
                "text_color": "#1A1A1A",
                "button_color": "#E0E0E0",
                "corner_radius": 8,
                "border_width": 1,
            }
            ctk.ThemeManager.theme["CTkTabview"] = {
                "fg_color": "#F5F5F5",
                "border_color": "#E0E0E0",
                "selected_color": "#2196F3",
            }
            ctk.ThemeManager.theme["CTkScrollableFrame"] = {
                "fg_color": "#F5F5F5",
                "label_fg_color": "#FFFFFF",
            }
    
    def register_component(
        self, 
        component: tk.Widget, 
        callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        Registra um componente para receber notificações de mudança de tema.
        
        Args:
            component: Widget Tkinter/CustomTkinter a ser registrado
            callback: Função opcional para ser chamada quando o tema mudar.
                     Recebe o nome do novo tema como argumento.
        """
        if callback is None:
            # Callback padrão que tenta atualizar cores automaticamente
            callback = lambda theme: self._default_update_callback(component, theme)
        
        self._components.append((component, callback))
    
    def unregister_component(self, component: tk.Widget) -> None:
        """Remove um componente da lista de notificações."""
        self._components = [
            (comp, cb) for comp, cb in self._components if comp != component
        ]
    
    def _default_update_callback(self, component: tk.Widget, theme: str) -> None:
        """
        Callback padrão para atualização de componentes.
        Tenta atualizar cores básicas automaticamente.
        """
        p = self._palette
        
        try:
            # Tenta atualizar cores comuns
            if hasattr(component, 'configure'):
                # Frame backgrounds
                if isinstance(component, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                    component.configure(fg_color=p.frame_bg)
                
                # Label text colors
                elif isinstance(component, ctk.CTkLabel):
                    component.configure(text_color=p.text_primary)
                
                # Button colors
                elif isinstance(component, ctk.CTkButton):
                    component.configure(
                        fg_color=p.button_fg,
                        hover_color=p.button_hover,
                        text_color=p.button_text
                    )
        except Exception:
            # Ignora erros em componentes que não suportam certas configurações
            pass
    
    def _notify_components(self, theme: str) -> None:
        """Notifica todos os componentes registrados sobre mudança de tema."""
        for component, callback in self._components:
            try:
                callback(theme)
            except Exception as e:
                print(f"Aviso: Erro ao notificar componente: {e}")
    
    def register_custom_color(
        self, 
        widget_type: str, 
        color_name: str, 
        light_value: str, 
        dark_value: str
    ) -> None:
        """
        Registra uma cor customizada para um tipo específico de widget.
        
        Args:
            widget_type: Tipo do widget (ex: 'CTkFrame', 'CTkButton')
            color_name: Nome da propriedade de cor (ex: 'fg_color')
            light_value: Valor da cor no tema claro
            dark_value: Valor da cor no tema escuro
        """
        if widget_type not in self._custom_colors:
            self._custom_colors[widget_type] = {}
        
        self._custom_colors[widget_type][color_name] = {
            self.LIGHT_THEME: light_value,
            self.DARK_THEME: dark_value
        }
        
        # Aplica imediatamente se o tema atual corresponder
        if self._current_theme in (self.LIGHT_THEME, self.DARK_THEME):
            self._update_custom_colors()
    
    def _update_custom_colors(self) -> None:
        """Atualiza cores customizadas registradas baseado no tema atual."""
        for widget_type, colors in self._custom_colors.items():
            for color_name, values in colors.items():
                color_value = values.get(self._current_theme)
                if color_value and widget_type in ctk.ThemeManager.theme:
                    ctk.ThemeManager.theme[widget_type][color_name] = color_value
    
    def create_theme_toggle_button(
        self, 
        master: tk.Widget,
        command: Optional[Callable[[], None]] = None,
        **kwargs
    ) -> ctk.CTkButton:
        """
        Cria um botão de alternância de tema pré-configurado.
        
        Args:
            master: Widget pai
            command: Comando adicional para executar após alternar tema
            **kwargs: Argumentos adicionais para CTkButton
        
        Returns:
            CTkButton configurado
        """
        def toggle_and_notify():
            self.toggle_theme()
            if command:
                command()
        
        # Ícone baseado no tema atual
        icon = "🌙" if self._current_theme == self.LIGHT_THEME else "☀️"
        text = f"{icon} Tema"
        
        button = ctk.CTkButton(
            master,
            text=text,
            command=toggle_and_notify,
            width=120,
            height=40,
            **kwargs
        )
        
        return button


# Instância global singleton
_theme_manager_instance: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """
    Retorna a instância singleton do ThemeManager.
    
    Returns:
        Instância do ThemeManager
    """
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance


def apply_theme_to_widget(widget: tk.Widget, theme_manager: ThemeManager) -> None:
    """
    Aplica cores do tema atual a um widget específico.
    
    Função utilitária para aplicar manualmente temas a widgets.
    
    Args:
        widget: Widget para aplicar o tema
        theme_manager: Instância do ThemeManager
    """
    p = theme_manager.palette
    
    try:
        if hasattr(widget, 'configure'):
            # Aplica cores básicas
            if isinstance(widget, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                widget.configure(fg_color=p.frame_bg, border_color=p.border_color)
            elif isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=p.text_primary)
            elif isinstance(widget, ctk.CTkButton):
                widget.configure(
                    fg_color=p.button_fg,
                    hover_color=p.button_hover,
                    text_color=p.button_text
                )
            elif isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                widget.configure(
                    fg_color=p.entry_bg,
                    border_color=p.entry_border,
                    text_color=p.text_primary
                )
    except Exception:
        pass


__all__ = [
    "ThemeManager",
    "ColorPalette",
    "DARK_PALETTE",
    "LIGHT_PALETTE",
    "get_theme_manager",
    "apply_theme_to_widget",
]
