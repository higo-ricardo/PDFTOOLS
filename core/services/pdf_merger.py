#!/usr/bin/env python3
"""
Serviço de Mesclagem de PDFs
Permite unir múltiplos PDFs em qualquer ordem, com opções de bookmarks e compressão.

Usa PyMuPDF (fitz) como backend para consistência com demais serviços.
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass, field
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PDFFileInfo:
    """Informações sobre um arquivo PDF."""
    caminho: str
    nome: str
    num_paginas: int
    tamanho_bytes: int
    tamanho_formatado: str = ""
    
    def __post_init__(self):
        self.tamanho_formatado = self._format_size()
    
    def _format_size(self) -> str:
        """Formata tamanho do arquivo."""
        size = self.tamanho_bytes
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


@dataclass
class MergeResult:
    """Resultado da mesclagem de PDFs."""
    sucesso: bool
    caminho_saida: str
    arquivos_entrada: List[str]
    num_paginas_total: int
    tamanho_final: int
    erro: Optional[str] = None
    mensagens: List[str] = field(default_factory=list)


class PDFMergerService:
    """
    Serviço profissional para mesclar PDFs.
    Suporta reordenação, bookmarks, compressão e separadores.
    """
    
    def __init__(self):
        pass
    
    def get_pdf_info(self, filepath: str) -> Optional[PDFFileInfo]:
        """
        Obtém informações detalhadas de um PDF.
        
        Args:
            filepath: Caminho do arquivo PDF
            
        Returns:
            PDFFileInfo ou None se erro
        """
        try:
            path = Path(filepath)
            if not path.exists():
                logger.error(f"Arquivo não encontrado: {filepath}")
                return None
            
            if path.suffix.lower() != '.pdf':
                logger.error(f"Não é um PDF: {filepath}")
                return None
            
            doc = fitz.open(filepath)
            num_pages = len(doc)
            doc.close()
            file_size = path.stat().st_size
            
            return PDFFileInfo(
                caminho=filepath,
                nome=path.name,
                num_paginas=num_pages,
                tamanho_bytes=file_size
            )
        except Exception as e:
            logger.exception(f"Erro ao ler PDF {filepath}: {e}")
            return None
    
    def merge_pdfs(
        self,
        pdf_files: List[str],
        output_path: Optional[str] = None,
        keep_bookmarks: bool = True,
        add_separators: bool = False,
        compress: bool = True
    ) -> MergeResult:
        """
        Mescla múltiplos PDFs em um único arquivo.
        
        Args:
            pdf_files: Lista de caminhos dos PDFs (na ordem desejada)
            output_path: Caminho do arquivo de saída (opcional, gera no mesmo diretório do primeiro arquivo se None)
            keep_bookmarks: Manter bookmarks/navegação
            add_separators: Adicionar páginas separadoras entre arquivos
            compress: Aplicar compressão
            
        Returns:
            MergeResult: Resultado detalhado da operação
        """
        if not pdf_files:
            return MergeResult(
                sucesso=False,
                caminho_saida="",
                arquivos_entrada=[],
                num_paginas_total=0,
                tamanho_final=0,
                erro="Nenhum arquivo fornecido"
            )
        
        if len(pdf_files) < 2:
            return MergeResult(
                sucesso=False,
                caminho_saida="",
                arquivos_entrada=pdf_files,
                num_paginas_total=0,
                tamanho_final=0,
                erro="É necessário pelo menos 2 arquivos para mesclar"
            )
        
        # Define caminho de saída (padrão: mesmo diretório do primeiro arquivo)
        if output_path is None:
            first_file = Path(pdf_files[0])
            output_dir = first_file.parent
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(output_dir / f"{first_file.stem}_mesclado_{timestamp}.pdf")
        
        try:
            merged_doc = fitz.open()
            total_pages = 0
            messages = []
            toc_entries = []
            
            for i, pdf_path in enumerate(pdf_files):
                path = Path(pdf_path)
                if not path.exists():
                    merged_doc.close()
                    return MergeResult(
                        sucesso=False,
                        caminho_saida="",
                        arquivos_entrada=pdf_files,
                        num_paginas_total=0,
                        tamanho_final=0,
                        erro=f"Arquivo não encontrado: {path.name}"
                    )
                
                try:
                    src_doc = fitz.open(pdf_path)
                    num_pages = len(src_doc)
                    
                    # Bookmark de nível 1 apontando para a primeira página deste PDF
                    if keep_bookmarks:
                        toc_entries.append([1, path.stem, total_pages + 1])
                    
                    # Insere todas as páginas
                    merged_doc.insert_pdf(src_doc)
                    total_pages += num_pages
                    
                    src_doc.close()
                    
                    messages.append(f"✓ {path.name} ({num_pages} págs)")
                    
                    # Adiciona separador (página em branco) se solicitado
                    if add_separators and i < len(pdf_files) - 1:
                        # Usa dimensão da última página inserida
                        last_page = merged_doc[-1]
                        w = last_page.rect.width
                        h = last_page.rect.height
                        merged_doc.new_page(width=w, height=h)
                        total_pages += 1
                        messages.append("  → Separador adicionado")
                        
                except Exception as e:
                    merged_doc.close()
                    return MergeResult(
                        sucesso=False,
                        caminho_saida="",
                        arquivos_entrada=pdf_files,
                        num_paginas_total=0,
                        tamanho_final=0,
                        erro=f"Erro ao processar {path.name}: {str(e)}"
                    )
            
            # Aplica bookmarks (Table of Contents)
            if keep_bookmarks and toc_entries:
                merged_doc.set_toc(toc_entries)
            
            # Salva arquivo final
            save_kwargs = {}
            if compress:
                save_kwargs["deflate"] = True
                save_kwargs["garbage"] = 4
            
            merged_doc.save(output_path, **save_kwargs)
            merged_doc.close()
            
            # Obtém tamanho final
            final_size = Path(output_path).stat().st_size
            
            logger.info(f"PDFs mesclados com sucesso: {output_path}")
            logger.info(f"Total de páginas: {total_pages}, Tamanho: {final_size} bytes")
            
            return MergeResult(
                sucesso=True,
                caminho_saida=output_path,
                arquivos_entrada=pdf_files,
                num_paginas_total=total_pages,
                tamanho_final=final_size,
                mensagens=messages
            )
            
        except Exception as e:
            logger.exception(f"Erro ao mesclar PDFs: {e}")
            return MergeResult(
                sucesso=False,
                caminho_saida="",
                arquivos_entrada=pdf_files,
                num_paginas_total=0,
                tamanho_final=0,
                erro=str(e)
            )
    
    def reorder_files(
        self,
        files: List[PDFFileInfo],
        from_index: int,
        to_index: int
    ) -> List[PDFFileInfo]:
        """
        Reordena lista de arquivos movendo um item de uma posição para outra.
        
        Args:
            files: Lista original de arquivos
            from_index: Índice de origem
            to_index: Índice de destino
            
        Returns:
            List[PDFFileInfo]: Nova lista ordenada
        """
        if not files or from_index < 0 or to_index < 0:
            return files
        
        if from_index >= len(files) or to_index >= len(files):
            return files
        
        # Cria cópia da lista
        new_list = files.copy()
        
        # Move o item
        item = new_list.pop(from_index)
        new_list.insert(to_index, item)
        
        return new_list
    
    def remove_file(
        self,
        files: List[PDFFileInfo],
        index: int
    ) -> Tuple[List[PDFFileInfo], Optional[PDFFileInfo]]:
        """
        Remove um arquivo da lista.
        
        Args:
            files: Lista de arquivos
            index: Índice do arquivo a remover
            
        Returns:
            Tuple com nova lista e arquivo removido (ou None)
        """
        if not files or index < 0 or index >= len(files):
            return files, None
        
        new_list = files.copy()
        removed = new_list.pop(index)
        
        return new_list, removed
