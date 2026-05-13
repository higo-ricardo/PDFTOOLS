"""
Módulo de utilitários para o projeto PDF Tools.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging(log_file: str = "pdf_tools.log", level: int = logging.INFO):
    """
    Configura o sistema de logging.
    
    Args:
        log_file: Nome do arquivo de log.
        level: Nível de logging.
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Cria handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Cria handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Configura logging root
    logging.basicConfig(
        level=level,
        handlers=[file_handler, console_handler]
    )
    
    logging.info("Logging configurado com sucesso")


def get_timestamp() -> str:
    """
    Retorna timestamp formatado para uso em nomes de arquivo.
    
    Returns:
        str: Timestamp no formato YYYYMMDD_HHMMSS.
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_directory(directory: str) -> bool:
    """
    Garante que um diretório existe, criando se necessário.
    
    Args:
        directory: Caminho do diretório.
        
    Returns:
        bool: True se sucesso, False se erro.
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:
        logging.error(f"Erro ao criar diretório {directory}: {str(e)}")
        return False


def format_file_size(size_bytes: int) -> str:
    """
    Formata tamanho de arquivo em KB, MB ou GB.
    
    Args:
        size_bytes: Tamanho em bytes.
        
    Returns:
        str: Tamanho formatado.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def is_pdf_file(file_path: str) -> bool:
    """
    Verifica se um arquivo é um PDF válido.
    
    Args:
        file_path: Caminho do arquivo.
        
    Returns:
        bool: True se for PDF válido.
    """
    try:
        if not os.path.exists(file_path):
            return False
        
        if not file_path.lower().endswith('.pdf'):
            return False
        
        # Verifica assinatura do arquivo PDF
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
            
    except Exception:
        return False


def get_safe_filename(filename: str) -> str:
    """
    Retorna um nome de arquivo seguro, removendo caracteres inválidos.
    
    Args:
        filename: Nome do arquivo original.
        
    Returns:
        str: Nome de arquivo seguro.
    """
    # Remove extensão
    name = Path(filename).stem
    
    # Caracteres permitidos
    safe_chars = []
    for char in name:
        if char.isalnum() or char in (' ', '-', '_'):
            safe_chars.append(char)
        else:
            safe_chars.append('_')
    
    return ''.join(safe_chars).strip()
