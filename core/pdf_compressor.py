"""
Módulo de compressão de PDFs.
Separa a lógica de negócio da interface gráfica.
"""

import fitz  # PyMuPDF
import os
import tempfile
from pathlib import Path
from typing import Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class CompressionLevel:
    """Níveis de compressão disponíveis."""
    LOW = "BAIXA"
    MEDIUM = "MÉDIA"
    HIGH = "ALTA"
    
    @staticmethod
    def get_zoom(level: str) -> float:
        """
        Retorna o fator de zoom para o nível de compressão.
        
        Args:
            level: Nível de compressão (BAIXA, MÉDIA, ALTA).
            
        Returns:
            float: Fator de zoom (0.25, 0.50, 0.75).
        """
        zoom_levels = {
            "BAIXA": 0.25,
            "MÉDIA": 0.50,
            "ALTA": 0.75
        }
        return zoom_levels.get(level, 0.50)


class PDFCompressor:
    """Classe responsável pela compressão de arquivos PDF."""
    
    @staticmethod
    def compress_pdf(file_path: str, compression_level: str = "MÉDIA", 
                     output_path: Optional[str] = None) -> Tuple[str, str]:
        """
        Comprime um arquivo PDF.
        
        Args:
            file_path: Caminho do arquivo PDF original.
            compression_level: Nível de compressão (BAIXA, MÉDIA, ALTA).
            output_path: Caminho opcional para salvar o arquivo comprimido.
                        Se None, salva em diretório temporário.
                        
        Returns:
            Tuple[str, str]: Caminho do arquivo comprimido e status ('sucesso' ou 'erro').
        """
        try:
            if not os.path.exists(file_path):
                error_msg = f"Arquivo não encontrado: {file_path}"
                logger.error(error_msg)
                return "", error_msg
            
            # Abre o documento original
            doc = fitz.open(file_path)
            
            # Define caminho de saída
            if output_path is None:
                temp_dir = tempfile.mkdtemp()
                output_path = os.path.join(temp_dir, "pdf_comprimido.pdf")
            else:
                # Garante que o diretório de saída existe
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            
            # Obtém fator de zoom baseado no nível de compressão
            zoom = CompressionLevel.get_zoom(compression_level)
            
            # Cria novo documento
            new_doc = fitz.open()
            
            for page_num, page in enumerate(doc):
                # Renderiza página como imagem com zoom reduzido
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                
                # Cria nova página no documento de saída
                new_page = new_doc.new_page(width=pix.width, height=pix.height)
                
                # Insere imagem na página
                new_page.insert_image(new_page.rect, pixmap=pix)
                
                logger.debug(f"Página {page_num + 1} processada")
            
            # Salva o documento comprimido
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
            
            # Calcula redução de tamanho
            original_size = os.path.getsize(file_path)
            compressed_size = os.path.getsize(output_path)
            reduction = ((original_size - compressed_size) / original_size) * 100
            
            logger.info(f"PDF comprimido com sucesso: {reduction:.1f}% de redução")
            logger.info(f"Tamanho original: {original_size/1024:.1f} KB, Comprimido: {compressed_size/1024:.1f} KB")
            
            return output_path, "sucesso"
            
        except Exception as e:
            error_msg = f"Erro ao comprimir PDF: {str(e)}"
            logger.error(error_msg)
            return "", error_msg
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict:
        """
        Obtém informações sobre um arquivo PDF.
        
        Args:
            file_path: Caminho do arquivo PDF.
            
        Returns:
            Dict: Informações do arquivo (tamanho, páginas, etc.).
        """
        try:
            doc = fitz.open(file_path)
            info = {
                "pages": len(doc),
                "size_bytes": os.path.getsize(file_path),
                "size_kb": os.path.getsize(file_path) / 1024,
                "size_mb": os.path.getsize(file_path) / (1024 * 1024),
                "filename": os.path.basename(file_path)
            }
            doc.close()
            return info
        except Exception as e:
            logger.error(f"Erro ao obter informações do arquivo: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def compress_batch(file_paths: list, compression_level: str = "MÉDIA",
                       output_dir: Optional[str] = None,
                       progress_callback: Optional[callable] = None) -> Tuple[list, bool]:
        """
        Comprime múltiplos arquivos PDF.
        
        Args:
            file_paths: Lista de caminhos de arquivos PDF.
            compression_level: Nível de compressão.
            output_dir: Diretório de saída opcional.
            progress_callback: Callback para atualizar progresso.
            
        Returns:
            Tuple[list, bool]: Lista de resultados e status de sucesso.
        """
        try:
            results = []
            total_files = len(file_paths)
            
            for i, file_path in enumerate(file_paths, 1):
                filename = Path(file_path).stem
                
                if output_dir:
                    output_path = os.path.join(output_dir, f"{filename}_comprimido.pdf")
                else:
                    output_path = None
                
                result_path, status = PDFCompressor.compress_pdf(
                    file_path, compression_level, output_path
                )
                
                results.append({
                    "original": file_path,
                    "compressed": result_path,
                    "status": status
                })
                
                if progress_callback:
                    progress = int((i / total_files) * 100)
                    progress_callback(progress)
            
            logger.info(f"Compressão em lote concluída: {total_files} arquivos")
            return results, True
            
        except Exception as e:
            error_msg = f"Erro durante compressão em lote: {str(e)}"
            logger.error(error_msg)
            return [], False
