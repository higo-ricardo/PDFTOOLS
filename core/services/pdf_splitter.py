"""
Serviço de divisão de PDFs.

Permite dividir um PDF em páginas individuais ou extrair intervalos específicos.
Com preview das páginas para seleção pelo usuário.

Autor: PDF Tools Team
Versão: 2.0.0
"""

import fitz  # PyMuPDF
import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Generator
from dataclasses import dataclass
import logging
from io import BytesIO

logger = logging.getLogger(__name__)


@dataclass
class PagePreview:
    """Dados de preview de uma página."""
    page_number: int
    thumbnail_data: bytes  # Imagem em bytes
    width: int
    height: int
    text_preview: str  # Primeiros caracteres de texto


@dataclass
class SplitResult:
    """Resultado de operação de divisão."""
    output_files: List[str]
    total_pages: int
    success: bool
    message: str


class PDFSplitterService:
    """
    Serviço para divisão de PDFs.
    
    Responsável por:
    - Gerar previews de páginas
    - Dividir PDF em páginas individuais
    - Extrair intervalos de páginas
    """
    
    def __init__(self):
        """Inicializa o serviço de divisão."""
        pass
    
    def get_page_previews(
        self, 
        file_path: str, 
        max_pages: int = 100,
        thumbnail_size: tuple = (150, 200)
    ) -> Generator[PagePreview, None, None]:
        """
        Gera previews de todas as páginas do PDF.
        
        Args:
            file_path: Caminho do arquivo PDF.
            max_pages: Número máximo de páginas para processar.
            thumbnail_size: Tamanho da miniatura (largura, altura).
            
        Yields:
            PagePreview: Dados de preview de cada página.
        """
        try:
            doc = fitz.open(file_path)
            total_pages = min(len(doc), max_pages)
            
            logger.info(f"Gerando previews de {total_pages} páginas")
            
            for page_num in range(total_pages):
                page = doc[page_num]
                
                # Gera thumbnail
                zoom_x = thumbnail_size[0] / page.rect.width
                zoom_y = thumbnail_size[1] / page.rect.height
                zoom = min(zoom_x, zoom_y)
                
                matrix = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=matrix)
                thumbnail_data = pix.tobytes("png")
                
                # Extrai texto preview (primeiros 100 caracteres)
                text = page.extract_text() or ""
                text_preview = text[:100].replace("\n", " ").strip()
                if len(text) > 100:
                    text_preview += "..."
                
                yield PagePreview(
                    page_number=page_num + 1,
                    thumbnail_data=thumbnail_data,
                    width=pix.width,
                    height=pix.height,
                    text_preview=text_preview
                )
                
                # Garbage collection para arquivos grandes
                if (page_num + 1) % 10 == 0:
                    import gc
                    gc.collect()
            
            doc.close()
            logger.info(f"Previews gerados com sucesso: {total_pages} páginas")
            
        except Exception as e:
            logger.exception(f"Erro ao gerar previews: {e}")
            raise
    
    def split_to_individual_pages(
        self,
        file_path: str,
        output_dir: Optional[str] = None,
        page_range: Optional[Tuple[int, int]] = None,
        progress_callback: Optional[callable] = None
    ) -> SplitResult:
        """
        Divide PDF em páginas individuais.
        
        Args:
            file_path: Caminho do arquivo PDF original.
            output_dir: Diretório de saída (opcional, usa temp se None).
            page_range: Intervalo de páginas (start, end) ou None para todas.
            progress_callback: Callback para atualizar progresso (recebe porcentagem).
            
        Returns:
            SplitResult: Resultado da operação.
        """
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Define intervalo de páginas
            if page_range:
                start, end = page_range
                start = max(1, min(start, total_pages))
                end = max(start, min(end, total_pages))
                pages_to_process = range(start - 1, end)
            else:
                pages_to_process = range(total_pages)
            
            num_pages = len(pages_to_process)
            
            # Define diretório de saída
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="pdf_split_")
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            output_files = []
            base_name = Path(file_path).stem
            
            logger.info(f"Dividindo PDF: {total_pages} páginas, intervalo: {page_range}")
            
            for i, page_num in enumerate(pages_to_process, 1):
                # Cria novo documento com uma página
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                # Define caminho de saída
                output_filename = f"{base_name}_pagina_{page_num + 1}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                # Salva página individual
                new_doc.save(output_path)
                new_doc.close()
                
                output_files.append(output_path)
                
                # Atualiza progresso
                if progress_callback:
                    progress = int((i / num_pages) * 100)
                    progress_callback(progress)
                
                # Garbage collection para arquivos grandes
                if i % 10 == 0:
                    import gc
                    gc.collect()
            
            doc.close()
            
            logger.info(f"PDF dividido com sucesso: {len(output_files)} arquivos criados")
            
            return SplitResult(
                output_files=output_files,
                total_pages=len(output_files),
                success=True,
                message=f"{len(output_files)} página(s) extraída(s) com sucesso"
            )
            
        except Exception as e:
            logger.exception(f"Erro ao dividir PDF: {e}")
            return SplitResult(
                output_files=[],
                total_pages=0,
                success=False,
                message=f"Erro ao dividir PDF: {str(e)}"
            )
    
    def extract_page_range(
        self,
        file_path: str,
        start_page: int,
        end_page: int,
        output_path: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Tuple[str, bool, str]:
        """
        Extrai um intervalo de páginas para um novo PDF.
        
        Args:
            file_path: Caminho do arquivo PDF original.
            start_page: Página inicial (1-based).
            end_page: Página final (1-based).
            output_path: Caminho de saída (opcional).
            progress_callback: Callback de progresso.
            
        Returns:
            Tuple[str, bool, str]: (caminho_saida, sucesso, mensagem)
        """
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Valida intervalo
            start_page = max(1, min(start_page, total_pages))
            end_page = max(start_page, min(end_page, total_pages))
            
            # Cria novo documento
            new_doc = fitz.open()
            
            # Insere páginas do intervalo
            new_doc.insert_pdf(
                doc,
                from_page=start_page - 1,
                to_page=end_page - 1
            )
            
            # Define caminho de saída
            if output_path is None:
                output_dir = tempfile.mkdtemp(prefix="pdf_extract_")
                base_name = Path(file_path).stem
                output_path = os.path.join(
                    output_dir,
                    f"{base_name}_paginas_{start_page}-{end_page}.pdf"
                )
            else:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Salva documento
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
            
            if progress_callback:
                progress_callback(100)
            
            logger.info(f"Intervalo extraído: páginas {start_page}-{end_page}")
            
            return output_path, True, f"Páginas {start_page}-{end_page} extraídas com sucesso"
            
        except Exception as e:
            logger.exception(f"Erro ao extrair intervalo: {e}")
            return "", False, f"Erro ao extrair intervalo: {str(e)}"
    
    def get_pdf_info(self, file_path: str) -> Dict:
        """
        Obtém informações sobre um PDF.
        
        Args:
            file_path: Caminho do arquivo PDF.
            
        Returns:
            Dict: Informações do PDF.
        """
        try:
            doc = fitz.open(file_path)
            info = {
                "total_pages": len(doc),
                "filename": os.path.basename(file_path),
                "file_size": os.path.getsize(file_path),
                "is_encrypted": doc.is_encrypted,
                "metadata": doc.metadata
            }
            doc.close()
            return info
        except Exception as e:
            logger.exception(f"Erro ao obter informações do PDF: {e}")
            return {"error": str(e)}
