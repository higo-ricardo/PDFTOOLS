"""
Serviço de extração de texto com streaming para arquivos grandes.

Implementa processamento com baixo uso de memória usando generators
e streaming para arquivos acima de 50MB.

Autor: PDF Tools Team
Versão: 2.0.0
"""

import pdfplumber
from io import BytesIO
from pathlib import Path
from typing import Tuple, List, Optional, Generator, Dict
import logging
import gc

logger = logging.getLogger(__name__)


class StreamingPDFExtractor:
    """
    Extrator de texto com suporte a streaming para arquivos grandes.
    
    Usa generators para processar páginas individualmente sem carregar
    todo o arquivo em memória.
    """
    
    STREAMING_THRESHOLD_BYTES = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def extract_text_streaming(
        file_path: str,
        progress_callback: Optional[callable] = None
    ) -> Generator[Tuple[int, str, bool], None, None]:
        """
        Extrai texto página por página usando streaming.
        
        Args:
            file_path: Caminho do arquivo PDF.
            progress_callback: Callback recebindo (pagina_atual, total_paginas).
            
        Yields:
            Tuple[int, str, bool]: (número_página, texto_extraído, sucesso)
        """
        try:
            file_size = Path(file_path).stat().st_size
            use_streaming = file_size > StreamingPDFExtractor.STREAMING_THRESHOLD_BYTES
            
            logger.info(f"Extração {'streaming' if use_streaming else 'normal'}: {file_path}")
            
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text() or ""
                        success = True
                        
                        if not page_text:
                            page_text = "[Sem texto extraível nesta página]"
                            success = True
                        
                        yield (page_num, page_text, success)
                        
                        # Callback de progresso
                        if progress_callback:
                            progress_callback(page_num, total_pages)
                        
                        # Garbage collection periódico para arquivos grandes
                        if use_streaming and page_num % 5 == 0:
                            gc.collect()
                    
                    except Exception as page_error:
                        error_msg = f"Erro na página {page_num}: {str(page_error)}"
                        logger.exception(error_msg)
                        yield (page_num, error_msg, False)
            
            logger.info(f"Extração concluída: {total_pages} páginas")
            
        except Exception as e:
            logger.exception(f"Erro na extração streaming: {e}")
            yield (-1, f"Erro fatal: {str(e)}", False)
    
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, str]:
        """
        Extrai texto de um PDF (método tradicional para compatibilidade).
        
        Args:
            file_bytes: Bytes do arquivo PDF.
            
        Returns:
            Tuple[str, str]: Texto extraído e status.
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
            logger.exception(error_msg)
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
            return StreamingPDFExtractor.extract_text_from_pdf(file_bytes)
        except Exception as e:
            error_msg = f"Erro ao ler arquivo: {str(e)}"
            logger.exception(error_msg)
            return error_msg, "erro"
    
    @staticmethod
    def extract_batch(
        file_paths: List[str],
        progress_callback: Optional[callable] = None
    ) -> Tuple[str, bool]:
        """
        Extrai texto de múltiplos PDFs.
        
        Args:
            file_paths: Lista de caminhos de arquivos PDF.
            progress_callback: Callback recebendo porcentagem de conclusão.
            
        Returns:
            Tuple[str, bool]: Texto combinado e status de sucesso.
        """
        try:
            total_files = len(file_paths)
            processed_text = ""
            
            for i, file_path in enumerate(file_paths, 1):
                filename = Path(file_path).stem
                text, status = StreamingPDFExtractor.extract_from_file_path(file_path)
                
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
            logger.exception(error_msg)
            return error_msg, False
    
    @staticmethod
    def get_pdf_info(file_path: str) -> Dict:
        """
        Obtém informações sobre um PDF.
        
        Args:
            file_path: Caminho do arquivo PDF.
            
        Returns:
            Dict: Informações do PDF.
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                info = {
                    "total_pages": len(pdf.pages),
                    "filename": os.path.basename(file_path),
                    "file_size": Path(file_path).stat().st_size,
                }
            return info
        except Exception as e:
            logger.exception(f"Erro ao obter informações: {e}")
            return {"error": str(e)}


# Alias para compatibilidade
PDFTextExtractor = StreamingPDFExtractor
