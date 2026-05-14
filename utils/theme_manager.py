import json
import os
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Callable, Any

logger = logging.getLogger(__name__)

@dataclass
class ColorPalette:
    background: str
    frame: str
    card: str
    text: str
    accent: str
    border: str
    go: str = "#28a745"
    stop: str = "#dc3545"
    secondary_text: str = "#888888"

DARK_PALETTE = ColorPalette(
    background="#1E1E1E",
    frame="#2D2D2D",
    card="#383838",
    text="#FFFFFF",
    accent="#64B5F6",
    border="#404040",
    go="#28a745",
    stop="#dc3545",
    secondary_text="#AAAAAA"
)

LIGHT_PALETTE = ColorPalette(
    background="#FFFFFF",
    frame="#F5F5F5",
    card="#FFFFFF",
    text="#1A1A1A",
    accent="#2196F3",
    border="#E0E0E0",
    go="#28a745",
    stop="#dc3545",
    secondary_text="#666666"
)

class ThemeManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path: str = "theme_config.json"):
        if self._initialized:
            return
        self.config_path = config_path
        self.current_theme = self._load_preference()
        self.listeners: list[Callable[[str, ColorPalette], None]] = []
        self._initialized = True

    def _load_preference(self) -> str:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    return data.get("theme", "light")
            except Exception as e:
                logger.error(f"Erro ao carregar preferência de tema: {e}")
        return "light"

    def _save_preference(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception as e:
            logger.error(f"Erro ao salvar preferência de tema: {e}")

    def get_palette(self) -> ColorPalette:
        return DARK_PALETTE if self.current_theme == "dark" else LIGHT_PALETTE

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self._save_preference()
        palette = self.get_palette()
        for listener in self.listeners:
            listener(self.current_theme, palette)

    def subscribe(self, listener: Callable[[str, ColorPalette], None]):
        self.listeners.append(listener)
        # Envia o estado atual imediatamente
        listener(self.current_theme, self.get_palette())

def get_theme_manager() -> ThemeManager:
    return ThemeManager()
