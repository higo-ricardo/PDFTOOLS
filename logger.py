"""
Módulo de logging do PDF Tools.

Sistema robusto de logging com rotação de arquivos, níveis configuráveis
e handlers separados para console e arquivo.

Autor: PDF Tools Team
Versão: 2.0.0
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union
import sys
import threading


class LoggerConfig:
    """
    Configuração centralizada do sistema de logging.
    
    Gerencia criação e configuração de loggers com rotação de arquivos.
    """
    
    # Singleton instance
    _instance: Optional['LoggerConfig'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implementa padrão singleton thread-safe."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa configuração de logging."""
        if self._initialized:
            return
        
        self._initialized = True
        self._configured_loggers = set()
    
    def setup(
        self,
        log_file: Union[str, Path] = "logs/pdf_tools.log",
        level: int = logging.INFO,
        max_bytes: int = 5 * 1024 * 1024,  # 5 MB
        backup_count: int = 3,
        console_level: int = logging.WARNING,
        include_timestamp: bool = True,
        include_module: bool = True,
    ) -> logging.Logger:
        """
        Configura o sistema de logging.
        
        Args:
            log_file: Caminho do arquivo de log.
            level: Nível de logging para arquivo (DEBUG, INFO, etc).
            max_bytes: Tamanho máximo do arquivo antes de rotacionar.
            backup_count: Número de arquivos de backup a manter.
            console_level: Nível de logging para console.
            include_timestamp: Incluir timestamp nos logs.
            include_module: Incluir nome do módulo nos logs.
        
        Returns:
            logging.Logger: Logger configurado para uso.
        """
        # Converte string para Path se necessário
        if isinstance(log_file, str):
            log_file = Path(log_file)
        
        # Garante que diretório existe
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Cria logger root
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Limpa handlers existentes
        root_logger.handlers.clear()
        
        # Formato do log
        if include_module:
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            log_format = "%(asctime)s - %(levelname)s - %(message)s"
        
        date_format = "%Y-%m-%d %H:%M:%S" if include_timestamp else None
        
        formatter = logging.Formatter(log_format, datefmt=date_format)
        
        # Handler para arquivo com rotação
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        
        # Adiciona handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Log inicial
        root_logger.info(f"Logging configurado: {log_file}")
        root_logger.debug(f"Nível: {logging.getLevelName(level)}, Max bytes: {max_bytes}, Backups: {backup_count}")
        
        return root_logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Obtém ou cria um logger com nome específico.
        
        Args:
            name: Nome do logger (geralmente __name__ do módulo).
        
        Returns:
            logging.Logger: Logger configurado.
        """
        logger = logging.getLogger(name)
        
        # Se ainda não foi configurado, garante nível adequado
        if name not in self._configured_loggers:
            logger.setLevel(logging.DEBUG)  # Herda do root
            self._configured_loggers.add(name)
        
        return logger


# Instância global singleton
_config: Optional[LoggerConfig] = None


def get_logger_config() -> LoggerConfig:
    """
    Retorna instância singleton da configuração de logging.
    
    Returns:
        LoggerConfig: Instância única de configuração.
    """
    global _config
    if _config is None:
        _config = LoggerConfig()
    return _config


def setup_logging(
    log_file: Union[str, Path] = "logs/pdf_tools.log",
    level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
    console_level: int = logging.WARNING,
) -> logging.Logger:
    """
    Função convenience para configurar logging.
    
    Args:
        log_file: Caminho do arquivo de log.
        level: Nível de logging para arquivo.
        max_bytes: Tamanho máximo do arquivo.
        backup_count: Número de backups.
        console_level: Nível de logging para console.
    
    Returns:
        logging.Logger: Logger root configurado.
    """
    config = get_logger_config()
    return config.setup(
        log_file=log_file,
        level=level,
        max_bytes=max_bytes,
        backup_count=backup_count,
        console_level=console_level,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Função convenience para obter um logger.
    
    Args:
        name: Nome do logger (__name__ do módulo).
    
    Returns:
        logging.Logger: Logger configurado.
    """
    config = get_logger_config()
    return config.get_logger(name)


def log_exception(logger: logging.Logger, message: str, exc_info: bool = True):
    """
    Logga uma exceção com stack trace completo.
    
    Esta função deve ser usada em blocos except para garantir
    que o stack trace completo seja registrado.
    
    Args:
        logger: Logger a ser usado.
        message: Mensagem de erro.
        exc_info: Se True, inclui informações da exceção atual.
    """
    logger.exception(message, exc_info=exc_info)


class LoggingContext:
    """
    Context manager para logging temporário.
    
    Útil para capturar logs de operações específicas.
    
    Exemplo:
        >>> with LoggingContext("processamento", level=logging.DEBUG) as logger:
        ...     logger.info("Iniciando processamento")
        ...     # logs serão capturados
    """
    
    def __init__(self, context_name: str, level: int = logging.DEBUG):
        """
        Inicializa contexto de logging.
        
        Args:
            context_name: Nome do contexto para identificação.
            level: Nível de logging para este contexto.
        """
        self.context_name = context_name
        self.level = level
        self.logger: Optional[logging.Logger] = None
        self._old_level: Optional[int] = None
    
    def __enter__(self) -> logging.Logger:
        """Entrada do contexto."""
        self.logger = get_logger(self.context_name)
        self._old_level = self.logger.level
        self.logger.setLevel(self.level)
        self.logger.info(f"[{self.context_name}] Contexto iniciado")
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Saída do contexto."""
        if exc_type is not None:
            self.logger.exception(
                f"[{self.context_name}] Erro no contexto: {exc_val}",
                exc_info=(exc_type, exc_val, exc_tb)
            )
        else:
            self.logger.info(f"[{self.context_name}] Contexto finalizado com sucesso")
        
        if self._old_level is not None:
            self.logger.setLevel(self._old_level)
        
        return False  # Não suprime exceptions


# Convenience exports
__all__ = [
    "LoggerConfig",
    "get_logger_config",
    "setup_logging",
    "get_logger",
    "log_exception",
    "LoggingContext",
]
