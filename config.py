"""
Módulo de configuração centralizada do PDF Tools.

Gerencia temas, aparência, paletas de cores, caminhos e parâmetros da aplicação.
Permite sobrescrita via variáveis de ambiente para facilitar deployment.

Autor: PDF Tools Team
Versão: 2.0.0
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
import os


class ThemeMode(Enum):
    """Modos de tema disponíveis."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class CompressionLevel(Enum):
    """Níveis de compressão de PDF."""
    LOW = "BAIXA"
    MEDIUM = "MÉDIA"
    HIGH = "ALTA"


@dataclass
class ColorPalette:
    """Paleta de cores para temas da interface."""
    
    # Cores primárias
    primary: str = "#2196F3"  # Azul Material Design
    primary_variant: str = "#1976D2"
    
    # Cores secundárias
    secondary: str = "#03DAC6"  # Turquesa
    secondary_variant: str = "#018786"
    
    # Cores de fundo
    background: str = "#FFFFFF"
    surface: str = "#F5F5F5"
    
    # Cores de erro
    error: str = "#B00020"
    
    # Cores de texto
    on_primary: str = "#FFFFFF"
    on_secondary: str = "#000000"
    on_background: str = "#000000"
    on_surface: str = "#000000"
    on_error: str = "#FFFFFF"
    
    # Cores específicas para PDF Tools
    success: str = "#4CAF50"  # Verde
    warning: str = "#FF9800"  # Laranja
    info: str = "#2196F3"  # Azul
    
    # Cores de status
    processing: str = "#FFC107"  # Amarelo
    completed: str = "#4CAF50"  # Verde
    failed: str = "#F44336"  # Vermelho


# Paleta para tema escuro
DARK_PALETTE = ColorPalette(
    primary="#90CAF9",
    primary_variant="#42A5F5",
    secondary="#80CBC4",
    secondary_variant="#4DB6AC",
    background="#121212",
    surface="#1E1E1E",
    on_background="#FFFFFF",
    on_surface="#FFFFFF",
    on_primary="#000000",
    on_secondary="#000000",
    success="#81C784",
    warning="#FFB74D",
    info="#64B5F6",
    processing="#FFE082",
    completed="#81C784",
    failed="#E57373"
)


# Paleta para tema claro (default)
LIGHT_PALETTE = ColorPalette()


@dataclass
class PathConfig:
    """Configuração de caminhos do sistema."""
    
    # Caminho base (raiz do projeto)
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    
    # Diretórios
    logs_dir: Path = field(init=False)
    temp_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    config_dir: Path = field(init=False)
    
    # Arquivos
    log_file: Path = field(init=False)
    config_file: Path = field(init=False)
    
    def __post_init__(self):
        """Inicializa caminhos derivados após criação do objeto."""
        self.logs_dir = self.base_dir / "logs"
        self.temp_dir = self.base_dir / "temp"
        self.output_dir = self.base_dir / "output"
        self.config_dir = self.base_dir / "config"
        
        self.log_file = self.logs_dir / "pdf_tools.log"
        self.config_file = self.config_dir / "settings.json"
    
    def ensure_directories(self) -> bool:
        """
        Garante que todos os diretórios necessários existam.
        
        Returns:
            bool: True se todos os diretórios foram criados com sucesso.
        """
        try:
            for directory in [self.logs_dir, self.temp_dir, self.output_dir, self.config_dir]:
                directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Erro ao criar diretórios: {e}")
            return False


@dataclass
class LoggingConfig:
    """Configuração do sistema de logging."""
    
    # Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    level: str = "INFO"
    
    # Arquivo de log
    file: Path = field(default_factory=lambda: PathConfig().log_file)
    
    # Rotação de arquivos
    max_bytes: int = 5 * 1024 * 1024  # 5 MB
    backup_count: int = 3
    
    # Formato do log
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # Console logging
    console_enabled: bool = True
    console_level: str = "WARNING"  # Apenas WARNING+ no console
    
    # Log de exceptions
    log_exceptions: bool = True
    include_stack_trace: bool = True


@dataclass
class UIConfig:
    """Configuração da interface gráfica."""
    
    # Tema
    theme_mode: ThemeMode = ThemeMode.DARK
    color_palette: ColorPalette = field(default_factory=lambda: LIGHT_PALETTE)
    
    # Janela
    window_width: int = 900
    window_height: int = 700
    min_width: int = 800
    min_height: int = 600
    title: str = "PDF Tools - Extrator & Compressor"
    
    # Fonte
    font_family: str = "Arial"
    font_size_base: int = 12
    font_size_title: int = 24
    font_size_small: int = 10
    
    # Widgets
    button_width: int = 150
    button_height: int = 40
    padding: int = 20
    spacing: int = 10
    
    # Feedback visual
    show_progress_details: bool = True
    show_file_being_processed: bool = True
    animation_enabled: bool = True
    
    # Idioma
    language: str = "pt_BR"


@dataclass
class ProcessingConfig:
    """Configuração de processamento de PDFs."""
    
    # Limites de arquivo
    max_file_size_mb: int = 500
    max_batch_size: int = 20
    
    # Streaming para arquivos grandes
    enable_streaming: bool = True
    streaming_threshold_mb: int = 50  # Ativa streaming para arquivos >50MB
    
    # Garbage collection
    gc_every_n_pages: int = 10  # Força GC a cada N páginas
    
    # Timeout
    operation_timeout_seconds: int = 300  # 5 minutos
    
    # Validação
    validate_pdf_before_process: bool = True
    check_pdf_signature: bool = True
    
    # Compressão
    default_compression_level: CompressionLevel = CompressionLevel.MEDIUM
    compression_zoom_levels: Dict[str, float] = field(default_factory=lambda: {
        "BAIXA": 0.25,
        "MÉDIA": 0.50,
        "ALTA": 0.75
    })


@dataclass
class Config:
    """
    Configuração principal da aplicação.
    
    Agrega todas as configurações em um único local e permite
    sobrescrita via variáveis de ambiente.
    
    Exemplo de uso:
        >>> config = Config()
        >>> config.ensure_setup()
        >>> print(config.ui.window_width)
        900
        >>> print(config.paths.logs_dir)
        /path/to/project/logs
    """
    
    # Sub-configurações
    paths: PathConfig = field(default_factory=PathConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    
    # Versão da aplicação
    version: str = "2.0.0"
    app_name: str = "PDF Tools"
    
    # Debug mode
    debug: bool = False
    
    def __post_init__(self):
        """Aplica configurações de ambiente após inicialização."""
        self._apply_environment_overrides()
    
    def _apply_environment_overrides(self):
        """
        Sobrescreve configurações baseado em variáveis de ambiente.
        
        Variáveis suportadas:
            PDF_TOOLS_DEBUG: true/false
            PDF_TOOLS_THEME: light/dark
            PDF_TOOLS_LOG_LEVEL: DEBUG/INFO/WARNING/ERROR/CRITICAL
            PDF_TOOLS_MAX_FILE_SIZE: tamanho em MB
        """
        if os.getenv("PDF_TOOLS_DEBUG", "").lower() == "true":
            self.debug = True
            self.logging.level = "DEBUG"
        
        theme_env = os.getenv("PDF_TOOLS_THEME", "").lower()
        if theme_env == "light":
            self.ui.theme_mode = ThemeMode.LIGHT
            self.ui.color_palette = LIGHT_PALETTE
        elif theme_env == "dark":
            self.ui.theme_mode = ThemeMode.DARK
            self.ui.color_palette = DARK_PALETTE
        
        log_level = os.getenv("PDF_TOOLS_LOG_LEVEL", "").upper()
        if log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            self.logging.level = log_level
        
        max_size = os.getenv("PDF_TOOLS_MAX_FILE_SIZE", "")
        if max_size.isdigit():
            self.processing.max_file_size_mb = int(max_size)
    
    def ensure_setup(self) -> bool:
        """
        Configura o ambiente da aplicação.
        
        Cria diretórios necessários e valida configurações.
        
        Returns:
            bool: True se setup foi bem sucedido.
        """
        # Cria diretórios
        if not self.paths.ensure_directories():
            return False
        
        # Valida configurações
        if not self._validate():
            return False
        
        return True
    
    def _validate(self) -> bool:
        """
        Valida configurações críticas.
        
        Returns:
            bool: True se todas as configurações são válidas.
        """
        # Valida tamanhos
        if self.processing.max_file_size_mb <= 0:
            print("Erro: max_file_size_mb deve ser positivo")
            return False
        
        if self.processing.max_batch_size <= 0:
            print("Erro: max_batch_size deve ser positivo")
            return False
        
        # Valida dimensões da janela
        if self.ui.window_width < self.ui.min_width:
            print(f"Erro: window_width ({self.ui.window_width}) < min_width ({self.ui.min_width})")
            return False
        
        if self.ui.window_height < self.ui.min_height:
            print(f"Erro: window_height ({self.ui.window_height}) < min_height ({self.ui.min_height})")
            return False
        
        return True
    
    def get_compression_zoom(self, level: str) -> float:
        """
        Retorna o fator de zoom para um nível de compressão.
        
        Args:
            level: Nível de compressão (BAIXA, MÉDIA, ALTA).
            
        Returns:
            float: Fator de zoom (0.25, 0.50, 0.75).
        """
        return self.processing.compression_zoom_levels.get(level, 0.50)
    
    def to_dict(self) -> Dict:
        """
        Converte configuração para dicionário.
        
        Returns:
            Dict: Dicionário com todas as configurações.
        """
        return {
            "version": self.version,
            "app_name": self.app_name,
            "debug": self.debug,
            "paths": {
                "base_dir": str(self.paths.base_dir),
                "logs_dir": str(self.paths.logs_dir),
                "temp_dir": str(self.paths.temp_dir),
                "output_dir": str(self.paths.output_dir),
                "log_file": str(self.paths.log_file),
            },
            "logging": {
                "level": self.logging.level,
                "max_bytes": self.logging.max_bytes,
                "backup_count": self.logging.backup_count,
                "console_enabled": self.logging.console_enabled,
            },
            "ui": {
                "theme_mode": self.ui.theme_mode.value,
                "window_width": self.ui.window_width,
                "window_height": self.ui.window_height,
                "language": self.ui.language,
            },
            "processing": {
                "max_file_size_mb": self.processing.max_file_size_mb,
                "max_batch_size": self.processing.max_batch_size,
                "enable_streaming": self.processing.enable_streaming,
                "streaming_threshold_mb": self.processing.streaming_threshold_mb,
                "default_compression_level": self.processing.default_compression_level.value,
            }
        }
    
    def __str__(self) -> str:
        """Retorna representação legível da configuração."""
        lines = [
            f"{self.app_name} v{self.version}",
            f"{'=' * 40}",
            f"Debug: {self.debug}",
            f"Tema: {self.ui.theme_mode.value}",
            f"Janela: {self.ui.window_width}x{self.ui.window_height}",
            f"Log: {self.logging.level}",
            f"Max arquivo: {self.processing.max_file_size_mb}MB",
            f"Max batch: {self.processing.max_batch_size}",
        ]
        return "\n".join(lines)


# Instância global singleton
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Retorna instância singleton da configuração.
    
    Returns:
        Config: Instância única de configuração.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
        _config_instance.ensure_setup()
    return _config_instance


def reload_config() -> Config:
    """
    Recarrega a configuração do zero.
    
    Útil quando configurações de ambiente mudam.
    
    Returns:
        Config: Nova instância de configuração.
    """
    global _config_instance
    _config_instance = Config()
    _config_instance.ensure_setup()
    return _config_instance


# Convenience exports
__all__ = [
    "Config",
    "PathConfig",
    "LoggingConfig",
    "UIConfig",
    "ProcessingConfig",
    "ColorPalette",
    "ThemeMode",
    "CompressionLevel",
    "LIGHT_PALETTE",
    "DARK_PALETTE",
    "get_config",
    "reload_config",
]
