"""
Serviço de divisão de PDFs.

Permite dividir um PDF em:
- Páginas individuais
- Intervalos específicos de páginas
- Por bookmarks existentes
- Páginas específicas (pares, ímpares, customizadas)

Com preview das páginas para seleção pelo usuário.

Autor: PDF Tools Team
Versão: 2.1.0
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Generator, Union
from dataclasses import dataclass
import logging
from io import BytesIO

logger = logging.getLogger(__name__)


@dataclass
class BookmarkInfo:
    """Informações de um bookmark."""
    title: str
    page: int
    level: int
    parent: Optional['BookmarkInfo'] = None
    children: List['BookmarkInfo'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


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
            output_dir: Diretório de saída (opcional, usa mesmo diretório do arquivo se None).
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
            
            # Define diretório de saída (padrão: mesmo diretório do arquivo original)
            if output_dir is None:
                output_dir = str(Path(file_path).parent)
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
            
            # Define caminho de saída (padrão: mesmo diretório do arquivo original)
            if output_path is None:
                base_name = Path(file_path).stem
                output_dir = Path(file_path).parent
                output_path = str(output_dir / f"{base_name}_paginas_{start_page}-{end_page}.pdf")
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
    
    def get_bookmarks(self, file_path: str) -> List[BookmarkInfo]:
        """
        Extrai bookmarks (índice) de um PDF.
        
        Args:
            file_path: Caminho do arquivo PDF.
            
        Returns:
            List[BookmarkInfo]: Lista de bookmarks com hierarquia.
        """
        try:
            doc = fitz.open(file_path)
            toc = doc.get_toc()  # Retorna lista de [level, title, page]
            
            if not toc:
                doc.close()
                return []
            
            bookmarks = []
            bookmark_stack = []  # Stack para controlar hierarquia
            
            for level, title, page in toc:
                bookmark = BookmarkInfo(
                    title=title,
                    page=page,
                    level=level
                )
                
                # Encontra o pai correto na hierarquia
                while bookmark_stack and bookmark_stack[-1].level >= level:
                    bookmark_stack.pop()
                
                if bookmark_stack:
                    parent = bookmark_stack[-1]
                    bookmark.parent = parent
                    parent.children.append(bookmark)
                else:
                    bookmarks.append(bookmark)
                
                bookmark_stack.append(bookmark)
            
            doc.close()
            logger.info(f"Extraídos {len(bookmarks)} bookmarks do PDF")
            return bookmarks
            
        except Exception as e:
            logger.exception(f"Erro ao extrair bookmarks: {e}")
            return []
    
    def split_by_bookmarks(
        self,
        file_path: str,
        output_dir: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> SplitResult:
        """
        Divide PDF por bookmarks, criando um arquivo por seção.
        
        Args:
            file_path: Caminho do arquivo PDF original.
            output_dir: Diretório de saída (padrão: mesmo diretório do arquivo).
            progress_callback: Callback para atualizar progresso.
            
        Returns:
            SplitResult: Resultado da operação.
        """
        try:
            doc = fitz.open(file_path)
            toc = doc.get_toc()
            
            if not toc:
                doc.close()
                return SplitResult(
                    output_files=[],
                    total_pages=0,
                    success=False,
                    message="PDF não possui bookmarks"
                )
            
            # Define diretório de saída (padrão: mesmo diretório do arquivo original)
            if output_dir is None:
                output_dir = str(Path(file_path).parent)
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            base_name = Path(file_path).stem
            output_files = []
            total_bookmarks = len(toc)
            
            logger.info(f"Dividindo PDF por bookmarks: {total_bookmarks} seções")
            
            for i, (level, title, page) in enumerate(toc):
                # Determina página final (próximo bookmark ou fim do documento)
                start_page = page - 1  # Converte para 0-based
                
                if i + 1 < total_bookmarks:
                    end_page = toc[i + 1][2] - 2  # Página anterior ao próximo bookmark
                else:
                    end_page = len(doc) - 1
                
                # Garante limites válidos
                end_page = max(start_page, min(end_page, len(doc) - 1))
                
                # Cria novo documento com a seção
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
                
                # Limpa nome do arquivo (remove caracteres inválidos)
                safe_title = "".join(c for c in title if c.isalnum() or c in ' _-').strip()[:50]
                if not safe_title:
                    safe_title = f"secao_{i+1}"
                
                output_filename = f"{base_name}_{safe_title}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                # Salva seção
                new_doc.save(output_path)
                new_doc.close()
                
                output_files.append(output_path)
                
                # Atualiza progresso
                if progress_callback:
                    progress = int(((i + 1) / total_bookmarks) * 100)
                    progress_callback(progress)
            
            doc.close()
            
            logger.info(f"PDF dividido por bookmarks: {len(output_files)} arquivos criados")
            
            return SplitResult(
                output_files=output_files,
                total_pages=len(output_files),
                success=True,
                message=f"{len(output_files)} seção(ões) extraída(s) por bookmarks"
            )
            
        except Exception as e:
            logger.exception(f"Erro ao dividir por bookmarks: {e}")
            return SplitResult(
                output_files=[],
                total_pages=0,
                success=False,
                message=f"Erro ao dividir por bookmarks: {str(e)}"
            )
    
    def extract_specific_pages(
        self,
        file_path: str,
        pages: Union[List[int], str],
        output_dir: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> SplitResult:
        """
        Extrai páginas específicas (pares, ímpares ou lista customizada).
        
        Args:
            file_path: Caminho do arquivo PDF original.
            pages: Lista de páginas OU string ('even', 'odd') para pares/ímpares.
            output_dir: Diretório de saída (padrão: mesmo diretório do arquivo).
            progress_callback: Callback para atualizar progresso.
            
        Returns:
            SplitResult: Resultado da operação.
        """
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Processa parâmetro pages
            if isinstance(pages, str):
                if pages.lower() == 'even':
                    # Páginas pares (2, 4, 6, ...)
                    page_numbers = list(range(2, total_pages + 1, 2))
                elif pages.lower() == 'odd':
                    # Páginas ímpares (1, 3, 5, ...)
                    page_numbers = list(range(1, total_pages + 1, 2))
                else:
                    doc.close()
                    return SplitResult(
                        output_files=[],
                        total_pages=0,
                        success=False,
                        message=f"Opção inválida: {pages}. Use 'even', 'odd' ou lista de números."
                    )
            elif isinstance(pages, list):
                # Lista de páginas (1-based)
                page_numbers = [p for p in pages if 1 <= p <= total_pages]
            else:
                doc.close()
                return SplitResult(
                    output_files=[],
                    total_pages=0,
                    success=False,
                    message="Parâmetro 'pages' deve ser lista ou string ('even'/'odd')"
                )
            
            if not page_numbers:
                doc.close()
                return SplitResult(
                    output_files=[],
                    total_pages=0,
                    success=False,
                    message="Nenhuma página válida encontrada"
                )
            
            # Define diretório de saída (padrão: mesmo diretório do arquivo original)
            if output_dir is None:
                output_dir = str(Path(file_path).parent)
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            # Cria documento com páginas selecionadas
            new_doc = fitz.open()
            
            for page_num in page_numbers:
                new_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)
            
            # Define nome do arquivo baseado no tipo de extração
            base_name = Path(file_path).stem
            if isinstance(pages, str):
                suffix = "pares" if pages.lower() == 'even' else "impares"
            else:
                suffix = "selecionadas"
            
            output_filename = f"{base_name}_{suffix}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            # Salva documento
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
            
            if progress_callback:
                progress_callback(100)
            
            logger.info(f"Páginas extraídas: {len(page_numbers)} páginas ({suffix})")
            
            return SplitResult(
                output_files=[output_path],
                total_pages=len(page_numbers),
                success=True,
                message=f"{len(page_numbers)} página(s) extraída(s) ({suffix})"
            )
            
        except Exception as e:
            logger.exception(f"Erro ao extrair páginas específicas: {e}")
            return SplitResult(
                output_files=[],
                total_pages=0,
                success=False,
                message=f"Erro ao extrair páginas: {str(e)}"
            )
    
    def split_by_ranges(
        self,
        file_path: str,
        ranges: List[Tuple[int, int]],
        output_dir: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> SplitResult:
        """
        Divide PDF em múltiplos arquivos por intervalos de páginas.
        
        Args:
            file_path: Caminho do arquivo PDF original.
            ranges: Lista de tuplas (start, end) definindo intervalos.
            output_dir: Diretório de saída (padrão: mesmo diretório do arquivo).
            progress_callback: Callback para atualizar progresso.
            
        Returns:
            SplitResult: Resultado da operação.
        """
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Define diretório de saída (padrão: mesmo diretório do arquivo original)
            if output_dir is None:
                output_dir = str(Path(file_path).parent)
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            base_name = Path(file_path).stem
            output_files = []
            total_ranges = len(ranges)
            
            logger.info(f"Dividindo PDF em {total_ranges} intervalos")
            
            for i, (start, end) in enumerate(ranges):
                # Valida intervalo
                start = max(1, min(start, total_pages))
                end = max(start, min(end, total_pages))
                
                # Cria novo documento
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start - 1, to_page=end - 1)
                
                output_filename = f"{base_name}_parte{i+1}_pag{start}-{end}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                new_doc.save(output_path)
                new_doc.close()
                
                output_files.append(output_path)
                
                # Atualiza progresso
                if progress_callback:
                    progress = int(((i + 1) / total_ranges) * 100)
                    progress_callback(progress)
            
            doc.close()
            
            logger.info(f"PDF dividido em {len(output_files)} arquivos por intervalos")
            
            return SplitResult(
                output_files=output_files,
                total_pages=sum(end - start + 1 for start, end in ranges),
                success=True,
                message=f"{len(output_files)} arquivo(s) criado(s) por intervalos"
            )
            
        except Exception as e:
            logger.exception(f"Erro ao dividir por intervalos: {e}")
            return SplitResult(
                output_files=[],
                total_pages=0,
                success=False,
                message=f"Erro ao dividir por intervalos: {str(e)}"
            )
