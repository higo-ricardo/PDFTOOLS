"""
Pacote GUI do PDF Tools - CustomTkinter.

Módulos:
- app_modern: Aplicação principal com interface moderna
- widgets: Widgets customizados reutilizáveis (W01-W12)
- dialogs: Componentes de diálogo (ProgressDialog, ResultDialog, etc.)
- theme_manager: Gerenciador de temas claro/escuro com persistência

Versão: 2.3.0
"""

__version__ = "2.3.0"

from gui_tkinter.theme_manager import (
    ThemeManager,
    ColorPalette,
    DARK_PALETTE,
    LIGHT_PALETTE,
    get_theme_manager,
    apply_theme_to_widget,
)

__all__ = [
    "ThemeManager",
    "ColorPalette",
    "DARK_PALETTE",
    "LIGHT_PALETTE",
    "get_theme_manager",
    "apply_theme_to_widget",
]
