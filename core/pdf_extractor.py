"""
Módulo de extração de texto de PDFs.
Separa a lógica de negócio da interface gráfica.
"""

import pdfplumber
from io import BytesIO
from pathlib import Path
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class PDFTextExtractor:
    """Classe responsável pela extração de texto de arquivos PDF."""
    
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, str]:
        """
        Extrai texto de um PDF.
        
        Args:
            file_bytes: Bytes do arquivo PDF.
            
        Returns:
            Tuple[str, str]: Texto extraído e status ('sucesso' ou 'erro').
        """
        try:
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                text_content = []
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"\n--- Página {page_num} ---\n{page_text}")
                    else:
                        text_content.append(f"\n--- Página {page_num} [Sem texto extraível] ---\n")
                
                result = "\n".join(text_content)
                logger.info(f"Texto extraído com sucesso: {len(result)} caracteres")
                return result, "sucesso"
                
        except Exception as e:
            error_msg = f"Erro ao processar PDF: {str(e)}"
            logger.error(error_msg)
            return error_msg, "erro"
    
    @staticmethod
    def extract_from_file_path(file_path: str) -> Tuple[str, str]:
        """
        Extrai texto de um arquivo PDF pelo caminho.
        
        Args:
            file_path: Caminho do arquivo PDF.
            
        Returns:
            Tuple[str, str]: Texto extraído e status.
        """
        try:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            return PDFTextExtractor.extract_text_from_pdf(file_bytes)
        except Exception as e:
            error_msg = f"Erro ao ler arquivo: {str(e)}"
            logger.error(error_msg)
            return error_msg, "erro"
    
    @staticmethod
    def extract_batch(file_paths: List[str], progress_callback: Optional[callable] = None) -> Tuple[str, bool]:
        """
        Extrai texto de múltiplos PDFs.
        
        Args:
            file_paths: Lista de caminhos de arquivos PDF.
            progress_callback: Função de callback para atualizar progresso (recebe porcentagem).
            
        Returns:
            Tuple[str, bool]: Texto combinado de todos os PDFs e status de sucesso.
        """
        try:
            total_files = len(file_paths)
            processed_text = ""
            
            for i, file_path in enumerate(file_paths, 1):
                filename = Path(file_path).stem
                text, status = PDFTextExtractor.extract_from_file_path(file_path)
                
                if status == "erro":
                    logger.error(f"Falha ao processar {filename}: {text}")
                    return text, False
                
                processed_text += f"► {filename}\n{text}\n\n"
                
                # Atualiza progresso se callback fornecido
                if progress_callback:
                    progress = int((i / total_files) * 100)
                    progress_callback(progress)
            
            logger.info(f"Processamento em lote concluído: {total_files} arquivos")
            return processed_text, True
            
        except Exception as e:
            error_msg = f"Erro durante processamento em lote: {str(e)}"
            logger.error(error_msg)
            return error_msg, False
