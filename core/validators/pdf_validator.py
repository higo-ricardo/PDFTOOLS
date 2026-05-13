"""
Módulo de validação de arquivos PDF.

Fornece validações robustas para garantir que arquivos PDF
são válidos antes do processamento.

Autor: PDF Tools Team
Versão: 2.0.0
"""

from pathlib import Path
from typing import Tuple, Union
import logging
import os

logger = logging.getLogger(__name__)


class PDFValidator:
    """
    Validador de arquivos PDF.
    
    Realiza múltiplas verificações para garantir que um arquivo
    é um PDF válido e pode ser processado com segurança.
    """
    
    # Assinatura mágica de arquivos PDF
    PDF_SIGNATURE = b"%PDF"
    
    # Versões mínimas/máximas suportadas
    SUPPORTED_VERSIONS = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "2.0"]
    
    @classmethod
    def validate(cls, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Valida se um arquivo é um PDF válido.
        
        Args:
            file_path: Caminho do arquivo a validar.
        
        Returns:
            Tuple[bool, str]: (True/False, mensagem de status)
        """
        file_path = Path(file_path)
        
        # Verificações básicas
        is_valid, message = cls._check_exists(file_path)
        if not is_valid:
            return is_valid, message
        
        is_valid, message = cls._check_extension(file_path)
        if not is_valid:
            logger.warning(f"Extensão inválida: {file_path}")
            # Não falhamos apenas pela extensão, continuamos
        
        is_valid, message = cls._check_signature(file_path)
        if not is_valid:
            return is_valid, message
        
        is_valid, message = cls._check_readable(file_path)
        if not is_valid:
            return is_valid, message
        
        is_valid, message = cls._check_pdf_structure(file_path)
        if not is_valid:
            return is_valid, message
        
        logger.info(f"PDF válido: {file_path}")
        return True, "PDF válido"
    
    @classmethod
    def _check_exists(cls, file_path: Path) -> Tuple[bool, str]:
        """Verifica se o arquivo existe."""
        if not file_path.exists():
            return False, f"Arquivo não encontrado: {file_path}"
        
        if not file_path.is_file():
            return False, f"Caminho não é um arquivo: {file_path}"
        
        return True, "Arquivo existe"
    
    @classmethod
    def _check_extension(cls, file_path: Path) -> Tuple[bool, str]:
        """Verifica se a extensão é .pdf (case-insensitive)."""
        if file_path.suffix.lower() != ".pdf":
            return False, f"Extensão inválida: {file_path.suffix} (esperado .pdf)"
        
        return True, "Extensão válida"
    
    @classmethod
    def _check_signature(cls, file_path: Path) -> Tuple[bool, str]:
        """
        Verifica a assinatura mágica do arquivo PDF.
        
        PDFs começam com "%PDF-" seguido da versão.
        """
        try:
            with open(file_path, "rb") as f:
                header = f.read(8)
                
                if len(header) < 5:
                    return False, "Arquivo muito pequeno para ser um PDF"
                
                if not header.startswith(cls.PDF_SIGNATURE):
                    return False, "Assinatura PDF não encontrada (não é um arquivo PDF válido)"
                
                # Extrai versão
                version_end = header.find(b"-", 4)
                if version_end != -1:
                    version = header[5:version_end].decode("ascii", errors="ignore")
                    logger.debug(f"Versão do PDF: {version}")
                    
                    if version not in cls.SUPPORTED_VERSIONS:
                        logger.warning(f"Versão do PDF não testada: {version}")
                
                return True, "Assinatura PDF válida"
                
        except PermissionError:
            return False, "Permissão negada para ler arquivo"
        except Exception as e:
            return False, f"Erro ao ler assinatura: {str(e)}"
    
    @classmethod
    def _check_readable(cls, file_path: Path) -> Tuple[bool, str]:
        """Verifica se o arquivo pode ser lido."""
        try:
            with open(file_path, "rb") as f:
                # Tenta ler alguns bytes
                f.read(1024)
            return True, "Arquivo legível"
        except PermissionError:
            return False, "Permissão negada para ler arquivo"
        except Exception as e:
            return False, f"Erro ao ler arquivo: {str(e)}"
    
    @classmethod
    def _check_pdf_structure(cls, file_path: Path) -> Tuple[bool, str]:
        """
        Verifica a estrutura interna do PDF usando bibliotecas.
        
        Tenta abrir o PDF com pdfplumber e fitz para validar estrutura.
        """
        # Tenta com pdfplumber
        try:
            import pdfplumber
            
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    return False, "PDF vazio (nenhuma página encontrada)"
                
                logger.debug(f"PDF válido (pdfplumber): {len(pdf.pages)} páginas")
                return True, f"Estrutura válida ({len(pdf.pages)} páginas)"
                
        except ImportError:
            logger.warning("pdfplumber não disponível, tentando fitz")
        except Exception as e:
            logger.warning(f"pdfplumber falhou: {str(e)}, tentando fitz")
        
        # Tenta com fitz (PyMuPDF)
        try:
            import fitz
            
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()
            
            if page_count == 0:
                return False, "PDF vazio (nenhuma página encontrada)"
            
            logger.debug(f"PDF válido (fitz): {page_count} páginas")
            return True, f"Estrutura válida ({page_count} páginas)"
            
        except ImportError:
            logger.error("Nenhuma biblioteca PDF disponível (pdfplumber ou fitz)")
            return False, "Bibliotecas PDF não disponíveis para validação completa"
        except Exception as e:
            error_msg = str(e).lower()
            
            # Mensagens de erro comuns
            if "corrupt" in error_msg or "damaged" in error_msg:
                return False, "PDF corrompido ou danificado"
            elif "password" in error_msg or "encrypted" in error_msg:
                return False, "PDF protegido por senha"
            elif "empty" in error_msg:
                return False, "PDF vazio"
            else:
                return False, f"Erro na estrutura do PDF: {str(e)}"
    
    @classmethod
    def get_file_info(cls, file_path: Union[str, Path]) -> dict:
        """
        Obtém informações detalhadas sobre um arquivo PDF.
        
        Args:
            file_path: Caminho do arquivo.
        
        Returns:
            dict: Informações do arquivo.
        """
        file_path = Path(file_path)
        info = {
            "path": str(file_path),
            "exists": file_path.exists(),
            "size_bytes": 0,
            "size_kb": 0,
            "size_mb": 0,
            "extension": file_path.suffix,
            "is_pdf": False,
            "pages": 0,
            "valid": False,
            "error": None,
        }
        
        if not info["exists"]:
            info["error"] = "Arquivo não encontrado"
            return info
        
        try:
            info["size_bytes"] = file_path.stat().st_size
            info["size_kb"] = info["size_bytes"] / 1024
            info["size_mb"] = info["size_kb"] / 1024
            
            # Verifica assinatura
            with open(file_path, "rb") as f:
                header = f.read(5)
                info["is_pdf"] = header.startswith(cls.PDF_SIGNATURE)
            
            # Conta páginas se for PDF válido
            if info["is_pdf"]:
                try:
                    import fitz
                    doc = fitz.open(file_path)
                    info["pages"] = len(doc)
                    doc.close()
                    info["valid"] = info["pages"] > 0
                except Exception as e:
                    info["error"] = str(e)
            
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    @classmethod
    def validate_batch(cls, file_paths: list) -> dict:
        """
        Valida múltiplos arquivos PDF.
        
        Args:
            file_paths: Lista de caminhos de arquivos.
        
        Returns:
            dict: Resultados da validação com estatísticas.
        """
        results = {
            "total": len(file_paths),
            "valid": 0,
            "invalid": 0,
            "files": [],
        }
        
        for file_path in file_paths:
            is_valid, message = cls.validate(file_path)
            
            result = {
                "path": str(file_path),
                "valid": is_valid,
                "message": message,
            }
            
            results["files"].append(result)
            
            if is_valid:
                results["valid"] += 1
            else:
                results["invalid"] += 1
        
        logger.info(
            f"Validação em lote: {results['valid']}/{results['total']} válidos"
        )
        
        return results


# Convenience function
def validate_pdf(file_path: Union[str, Path]) -> Tuple[bool, str]:
    """
    Função convenience para validar um arquivo PDF.
    
    Args:
        file_path: Caminho do arquivo.
    
    Returns:
        Tuple[bool, str]: (válido, mensagem)
    """
    return PDFValidator.validate(file_path)


__all__ = [
    "PDFValidator",
    "validate_pdf",
]
