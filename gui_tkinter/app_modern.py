"""
Aplicação PDF Tools v2.0 - Interface Moderna CustomTkinter

Funcionalidades:
- Extração de texto com preview e streaming
- Compressão de PDFs com 3 níveis
- Divisão de PDF em páginas individuais ou intervalos
- Preview visual de todas as páginas
- Drag-and-drop de arquivos
- Tema escuro moderno com widgets customizados

Autor: PDF Tools Team
Versão: 2.0.0
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from PIL import Image
from io import BytesIO

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuração inicial
from config import get_config, DARK_PALETTE
from logger import setup_logging, get_logger

# Setup logging
setup_logging(level=10)  # DEBUG
logger = get_logger(__name__)

# Imports dos serviços
from core.services.extractor_service import StreamingPDFExtractor
from core.services.pdf_splitter import PDFSplitterService, PagePreview
from core.pdf_compressor import PDFCompressor
from core.services.cleaner_service import FileCleanerService, CleaningResult
from core.services.pdf_merger import PDFMergerService, PDFFileInfo, MergeResult
from utils.helpers import format_file_size

# Widgets customizados
from gui_tkinter.widgets.modern_widgets import (
    ModernButton, ShadowFrame, PreviewCard, ProgressCard, DropZoneFrame
)


class ExtractorTab(ctk.CTkFrame):
    """Tab de extração de texto com preview."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.extractor = StreamingPDFExtractor()
        self.selected_files: List[str] = []
        self.extracted_text = ""
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface da tab de extração."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header com título
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📄 Extrair Texto de PDF",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Área de drop zone
        self.drop_zone = DropZoneFrame(
            self,
            on_drop=self._on_files_dropped,
            text="Arraste PDFs aqui ou clique em Selecionar"
        )
        self.drop_zone.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Botões de ação
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.select_btn = ModernButton(
            btn_frame,
            text="📁 Selecionar PDF(s)",
            command=self.select_files,
            width=160,
            height=45,
            corner_radius=12
        )
        self.select_btn.grid(row=0, column=0, padx=8, pady=5)
        
        self.process_btn = ModernButton(
            btn_frame,
            text="▶️ Processar",
            command=self.start_extraction,
            state="disabled",
            width=160,
            height=45,
            corner_radius=12,
            fg_color="#2196F3"
        )
        self.process_btn.grid(row=0, column=1, padx=8, pady=5)
        
        self.save_btn = ModernButton(
            btn_frame,
            text="💾 Salvar",
            command=self.save_results,
            state="disabled",
            width=160,
            height=45,
            corner_radius=12,
            fg_color="#4CAF50"
        )
        self.save_btn.grid(row=0, column=2, padx=8, pady=5)
        
        # Área de resultado
        result_frame = ShadowFrame(self, corner_radius=12)
        result_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)
        
        self.result_text = ctk.CTkTextbox(
            result_frame,
            wrap="word",
            state="disabled",
            corner_radius=8,
            border_width=1
        )
        self.result_text.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        
        # Status bar
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Pronto - Selecione um arquivo PDF",
            anchor="w",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=250, corner_radius=6)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=1, padx=10)
        
        self.percent_label = ctk.CTkLabel(
            status_frame,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.percent_label.grid(row=0, column=2)
    
    def _on_files_dropped(self, files: list):
        """Handle files dropped."""
        if files:
            self.selected_files = files
            self.process_btn.configure(state="normal")
            self.status_label.configure(
                text=f"{len(self.selected_files)} arquivo(s) selecionado(s)"
            )
    
    def select_files(self):
        """Abre diálogo para seleção de arquivos."""
        files = filedialog.askopenfilenames(
            title="Selecione os PDFs",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            self.selected_files = list(files)
            self.process_btn.configure(state="normal")
            self.status_label.configure(
                text=f"{len(self.selected_files)} arquivo(s) selecionado(s)"
            )
    
    def start_extraction(self):
        """Inicia extração em thread separada."""
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado")
            return
        
        self.process_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.configure(state="disabled")
        self.status_label.configure(text="Processando...")
        
        # Processa em thread separada
        thread = threading.Thread(target=self._process_files, daemon=True)
        thread.start()
    
    def _process_files(self):
        """Processa arquivos em segundo plano."""
        try:
            total = len(self.selected_files)
            processed_text = ""
            
            for i, file_path in enumerate(self.selected_files, 1):
                filename = Path(file_path).stem
                
                # Usa streaming para arquivos grandes
                file_size = Path(file_path).stat().st_size
                use_streaming = file_size > 50 * 1024 * 1024
                
                if use_streaming:
                    # Processamento streaming página por página
                    page_texts = []
                    for page_num, text, success in self.extractor.extract_text_streaming(
                        file_path,
                        progress_callback=lambda curr, total_p: self._update_progress(curr, total_p, filename)
                    ):
                        if success:
                            page_texts.append(f"\n--- Página {page_num} ---\n{text}")
                        else:
                            page_texts.append(f"\n--- Página {page_num} [ERRO] ---\n{text}")
                    
                    text = "\n".join(page_texts)
                    status = "sucesso"
                else:
                    # Método tradicional
                    text, status = self.extractor.extract_from_file_path(file_path)
                
                if status == "erro":
                    self.after(0, lambda t=text: self._show_error(t))
                    return
                
                processed_text += f"► {filename}\n{text}\n\n"
                
                # Atualiza progresso
                progress = i / total
                self.after(0, lambda p=progress: self._update_progress_bar(p))
            
            self.after(0, lambda: self._finish_extraction(processed_text))
            
        except Exception as e:
            logger.exception(f"Erro na extração: {e}")
            self.after(0, lambda: self._show_error(f'Erro: {str(e)}'))
    
    def _update_progress(self, current: int, total: int, filename: str):
        """Atualiza label de progresso detalhado."""
        percent = int((current / total) * 100)
        self.after(0, lambda: self.status_label.configure(
            text=f"Processando: {filename} - Página {current}/{total} ({percent}%)"
        ))
        self.after(0, lambda p=current/total: self._update_progress_bar(p))
    
    def _update_progress_bar(self, value: float):
        """Atualiza barra de progresso."""
        self.progress_bar.set(value)
        self.percent_label.configure(text=f"{int(value * 100)}%")
    
    def _finish_extraction(self, text: str):
        """Finaliza extração e mostra resultado."""
        self.extracted_text = text
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")
        
        self.status_label.configure(text="✅ Processamento concluído!")
        self.process_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
    
    def _show_error(self, message: str):
        """Mostra mensagem de erro."""
        self.status_label.configure(text=f"❌ Erro: {message}")
        self.process_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.percent_label.configure(text="0%")
        messagebox.showerror("Erro", message)
    
    def save_results(self):
        """Salva resultados em arquivo."""
        if not self.extracted_text:
            return
        
        save_path = filedialog.asksaveasfilename(
            title="Salvar resultado",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(self.extracted_text)
                
                self.status_label.configure(text=f"✅ Arquivo salvo: {Path(save_path).name}")
                logger.info(f"Resultados salvos em: {save_path}")
            except Exception as e:
                logger.exception(f"Erro ao salvar: {e}")
                self.status_label.configure(text=f"❌ Erro ao salvar: {str(e)}")
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")


class CompressorTab(ctk.CTkFrame):
    """Tab de compressão de PDFs."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.compressor = PDFCompressor()
        self.file_path: Optional[str] = None
        self.file_selected = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface da tab de compressão."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ Comprimir PDF",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Drop zone
        self.drop_zone = DropZoneFrame(
            self,
            on_drop=self._on_file_dropped,
            text="Arraste um PDF aqui"
        )
        self.drop_zone.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Controles
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        ctrl_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.select_btn = ModernButton(
            ctrl_frame,
            text="📁 Selecionar PDF",
            command=self.select_file,
            width=160,
            height=45,
            corner_radius=12
        )
        self.select_btn.grid(row=0, column=0, padx=8, pady=5)
        
        self.compression_var = ctk.StringVar(value="MÉDIA")
        self.compression_menu = ctk.CTkOptionMenu(
            ctrl_frame,
            variable=self.compression_var,
            values=["BAIXA", "MÉDIA", "ALTA"],
            width=160,
            height=45,
            corner_radius=12
        )
        self.compression_menu.grid(row=0, column=1, padx=8, pady=5)
        
        self.compress_btn = ModernButton(
            ctrl_frame,
            text="⚡ Comprimir",
            command=self.compress_pdf,
            state="disabled",
            width=160,
            height=45,
            corner_radius=12,
            fg_color="#FF9800"
        )
        self.compress_btn.grid(row=0, column=2, padx=8, pady=5)
        
        # Informações do arquivo
        self.file_info_label = ctk.CTkLabel(
            self,
            text="Nenhum arquivo selecionado",
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.file_info_label.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        # Resultado
        result_frame = ShadowFrame(self, corner_radius=12)
        result_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)
        
        self.result_label = ctk.CTkLabel(
            result_frame,
            text="",
            justify="center",
            font=ctk.CTkFont(size=13)
        )
        self.result_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Status bar
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Pronto",
            anchor="w",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=250, corner_radius=6)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=1, padx=10)
    
    def _on_file_dropped(self, files: list):
        """Handle file dropped."""
        if files and len(files) == 1:
            self.file_path = files[0]
            self._update_file_info()
    
    def select_file(self):
        """Abre diálogo para seleção de arquivo."""
        file_path = filedialog.askopenfilename(
            title="Selecione um PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            self._update_file_info()
    
    def _update_file_info(self):
        """Atualiza informações do arquivo."""
        if not self.file_path:
            return
        
        info = self.compressor.get_file_info(self.file_path)
        
        if 'error' in info:
            self.file_info_label.configure(
                text="❌ Erro ao ler arquivo",
                text_color="#F44336"
            )
            self.file_selected = False
            self.compress_btn.configure(state="disabled")
        else:
            self.file_info_label.configure(
                text=(
                    f"📄 {info['filename']} | "
                    f"📊 {format_file_size(int(info['size_bytes']))} | "
                    f"📑 {info['pages']} páginas"
                ),
                text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"]
            )
            self.file_selected = True
            self.compress_btn.configure(state="normal")
    
    def compress_pdf(self):
        """Inicia compressão em thread separada."""
        if not self.file_path:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return
        
        self.compress_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Comprimindo...")
        
        compression_level = self.compression_var.get()
        
        thread = threading.Thread(
            target=self._do_compress,
            args=(compression_level,),
            daemon=True
        )
        thread.start()
    
    def _do_compress(self, compression_level: str):
        """Executa compressão em segundo plano."""
        try:
            result_path, status = self.compressor.compress_pdf(
                self.file_path,
                compression_level
            )
            
            if status == "sucesso":
                original_size = os.path.getsize(self.file_path)
                compressed_size = os.path.getsize(result_path)
                reduction = ((original_size - compressed_size) / original_size) * 100
                
                self.after(0, lambda: self._finish_compress(result_path, reduction))
            else:
                self.after(0, lambda: self._show_error(result_path))
                
        except Exception as e:
            logger.exception(f"Erro na compressão: {e}")
            self.after(0, lambda: self._show_error(f'Erro: {str(e)}'))
    
    def _finish_compress(self, result_path: str, reduction: float):
        """Finaliza compressão e mostra resultado."""
        self.result_label.configure(
            text=(
                f"✅ PDF comprimido com sucesso!\n\n"
                f"📁 {Path(result_path).name}\n"
                f"📉 Redução: {reduction:.1f}%\n"
                f"💾 Tamanho: {format_file_size(os.path.getsize(result_path))}"
            )
        )
        self.status_label.configure(text="✅ Concluído!", text_color="#4CAF50")
        self.compress_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.progress_bar.set(1)
    
    def _show_error(self, message: str):
        """Mostra mensagem de erro."""
        self.status_label.configure(text=f"❌ {message}", text_color="#F44336")
        self.compress_btn.configure(state="normal")
        self.select_btn.configure(state="disabled" if self.file_path else "normal")
        self.progress_bar.set(0)
        messagebox.showerror("Erro", message)


class SplitterTab(ctk.CTkFrame):
    """Tab de divisão de PDF com preview de páginas."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.splitter = PDFSplitterService()
        self.file_path: Optional[str] = None
        self.total_pages = 0
        self.previews_loaded = False
        self.selected_pages: set = set()
        self.preview_cards = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface da tab de divisão."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="✂️ Dividir PDF",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Drop zone
        self.drop_zone = DropZoneFrame(
            self,
            on_drop=self._on_file_dropped,
            text="Arraste um PDF para visualizar páginas"
        )
        self.drop_zone.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Controles superiores
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        ctrl_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.select_btn = ModernButton(
            ctrl_frame,
            text="📁 Selecionar PDF",
            command=self.select_file,
            width=140,
            height=40,
            corner_radius=10
        )
        self.select_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.select_all_btn = ModernButton(
            ctrl_frame,
            text="✓ Selecionar Todas",
            command=self.select_all_pages,
            state="disabled",
            width=140,
            height=40,
            corner_radius=10,
            fg_color="#2196F3"
        )
        self.select_all_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.mode_var = ctk.StringVar(value="individual")
        self.mode_menu = ctk.CTkOptionMenu(
            ctrl_frame,
            variable=self.mode_var,
            values=["individual", "intervalo"],
            width=140,
            height=40,
            corner_radius=10,
            command=self._on_mode_change
        )
        self.mode_menu.grid(row=0, column=2, padx=5, pady=5)
        
        self.split_btn = ModernButton(
            ctrl_frame,
            text="✂️ Dividir",
            command=self.start_split,
            state="disabled",
            width=140,
            height=40,
            corner_radius=10,
            fg_color="#FF9800"
        )
        self.split_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Frame de intervalo (oculto por padrão)
        self.range_frame = ctk.CTkFrame(self, fg_color="transparent")
        # Será mostrado quando modo = "intervalo"
        
        # Área de previews (scrollable)
        preview_container = ctk.CTkScrollableFrame(self, corner_radius=10)
        preview_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        preview_container.grid_columnconfigure(0, weight=1)
        
        self.preview_grid = ctk.CTkFrame(preview_container, fg_color="transparent")
        self.preview_grid.pack(fill="both", expand=True)
        
        # Status bar
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Pronto - Selecione um PDF",
            anchor="w",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=250, corner_radius=6)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=1, padx=10)
    
    def _on_file_dropped(self, files: list):
        """Handle file dropped."""
        if files and len(files) == 1:
            self.file_path = files[0]
            self._load_previews()
    
    def select_file(self):
        """Seleciona arquivo PDF."""
        file_path = filedialog.askopenfilename(
            title="Selecione um PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            self._load_previews()
    
    def _load_previews(self):
        """Carrega previews das páginas."""
        if not self.file_path:
            return
        
        try:
            self.status_label.configure(text="Carregando previews...")
            self.progress_bar.set(0)
            
            # Thread para carregar previews
            thread = threading.Thread(target=self._do_load_previews, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.exception(f"Erro ao carregar previews: {e}")
            self._show_error(f"Erro: {str(e)}")
    
    def _do_load_previews(self):
        """Carrega previews em background."""
        try:
            # Limpa previews anteriores
            self.after(0, lambda: self.preview_grid.destroy())
            self.after(0, lambda: setattr(self, 'preview_grid', ctk.CTkFrame(ctk.CTkScrollableFrame(self), fg_color="transparent")))
            
            previews = list(self.splitter.get_page_previews(self.file_path, max_pages=50))
            self.total_pages = len(previews)
            
            # Atualiza UI na thread principal
            self.after(0, lambda: self._display_previews(previews))
            
        except Exception as e:
            logger.exception(f"Erro ao gerar previews: {e}")
            self.after(0, lambda: self._show_error(f"Erro: {str(e)}"))
    
    def _display_previews(self, previews: List[PagePreview]):
        """Exibe previews na grid."""
        # Recria grid
        for widget in self.preview_grid.winfo_children():
            widget.destroy()
        
        self.preview_cards = []
        cols = 6
        rows = (len(previews) + cols - 1) // cols
        
        for i, preview in enumerate(previews):
            row = i // cols
            col = i % cols
            
            # Converte bytes da thumbnail para imagem
            try:
                img = Image.open(BytesIO(preview.thumbnail_data))
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 130))
            except:
                photo = None
            
            card = PreviewCard(
                self.preview_grid,
                page_number=preview.page_number,
                thumbnail_data=preview.thumbnail_data,
                text_preview=preview.text_preview,
                selected=False,
                on_toggle=self._on_page_toggle
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky="n")
            
            if photo:
                card.set_thumbnail(photo)
            
            self.preview_cards.append(card)
        
        self.preview_grid.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        
        self.select_all_btn.configure(state="normal")
        self.split_btn.configure(state="normal")
        self.status_label.configure(text=f"✅ {self.total_pages} páginas carregadas")
        self.progress_bar.set(1)
        self.previews_loaded = True
    
    def _on_page_toggle(self, page_num: int, selected: bool):
        """Handle toggle de página."""
        if selected:
            self.selected_pages.add(page_num)
        else:
            self.selected_pages.discard(page_num)
    
    def select_all_pages(self):
        """Seleciona todas as páginas."""
        for card in self.preview_cards:
            card.update_selection(True)
            self.selected_pages.add(card.page_number)
    
    def _on_mode_change(self, mode: str):
        """Handle mudança de modo."""
        if mode == "intervalo":
            # Mostrar controles de intervalo
            pass
        else:
            # Modo individual
            pass
    
    def start_split(self):
        """Inicia divisão do PDF."""
        if not self.file_path or not self.selected_pages:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma página")
            return
        
        self.split_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Dividindo PDF...")
        
        thread = threading.Thread(target=self._do_split, daemon=True)
        thread.start()
    
    def _do_split(self):
        """Executa divisão em background."""
        try:
            pages_list = sorted(list(self.selected_pages))
            
            # Converte para formato 0-based
            result = self.splitter.split_to_individual_pages(
                self.file_path,
                page_range=(min(pages_list), max(pages_list)),
                progress_callback=lambda p: self.after(0, lambda v=p/100: self.progress_bar.set(v))
            )
            
            if result.success:
                self.after(0, lambda: self._finish_split(result))
            else:
                self.after(0, lambda: self._show_error(result.message))
                
        except Exception as e:
            logger.exception(f"Erro na divisão: {e}")
            self.after(0, lambda: self._show_error(f"Erro: {str(e)}"))
    
    def _finish_split(self, result):
        """Finaliza divisão."""
        self.status_label.configure(text=f"✅ {result.total_pages} páginas extraídas")
        self.split_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.progress_bar.set(1)
        
        messagebox.showinfo(
            "Sucesso",
            f"{result.total_pages} páginas extraídas com sucesso!\n\n"
            f"Diretório: {Path(result.output_files[0]).parent if result.output_files else 'N/A'}"
        )
    
    def _show_error(self, message: str):
        """Mostra erro."""
        self.status_label.configure(text=f"❌ {message}", text_color="#F44336")
        self.split_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.progress_bar.set(0)
        messagebox.showerror("Erro", message)


class CleanerTab(ctk.CTkFrame):
    """Tab de limpeza de arquivos TXT, DOCX, MD com 12 criterios."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.cleaner = FileCleanerService()
        self.selected_files: List[str] = []
        self.cleaning_results: List[CleaningResult] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface da tab de limpeza."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🧹 Limpar Arquivos (TXT, DOCX, MD)",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        desc_label = ctk.CTkLabel(
            header_frame,
            text="Encoding automático + 12 limpezas: BOM, CRLF, espaços, headers, pontuação...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Drop zone
        self.drop_zone = DropZoneFrame(
            self,
            on_drop=self._on_files_dropped,
            text="Arraste arquivos .txt, .docx ou .md"
        )
        self.drop_zone.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Botões
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.select_btn = ModernButton(
            btn_frame,
            text="📁 Selecionar Arquivo(s)",
            command=self.select_files,
            width=160,
            height=45,
            corner_radius=12
        )
        self.select_btn.grid(row=0, column=0, padx=8, pady=5)
        
        self.clean_btn = ModernButton(
            btn_frame,
            text="✨ Limpar",
            command=self.start_cleaning,
            state="disabled",
            width=160,
            height=45,
            corner_radius=12,
            fg_color="#9C27B0"
        )
        self.clean_btn.grid(row=0, column=1, padx=8, pady=5)
        
        self.save_btn = ModernButton(
            btn_frame,
            text="💾 Salvar Todos",
            command=self.save_results,
            state="disabled",
            width=160,
            height=45,
            corner_radius=12,
            fg_color="#4CAF50"
        )
        self.save_btn.grid(row=0, column=2, padx=8, pady=5)
        
        # Lista de arquivos
        list_frame = ShadowFrame(self, corner_radius=12)
        list_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.file_listbox = ctk.CTkTextbox(
            list_frame,
            wrap="word",
            state="disabled",
            corner_radius=8,
            border_width=1,
            height=120
        )
        self.file_listbox.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        
        # Resultado
        result_frame = ShadowFrame(self, corner_radius=12)
        result_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)
        
        self.result_text = ctk.CTkTextbox(
            result_frame,
            wrap="word",
            state="disabled",
            corner_radius=8,
            border_width=1
        )
        self.result_text.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        
        # Status bar
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Pronto - Selecione arquivos para limpar",
            anchor="w",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=250, corner_radius=6)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=1, padx=10)
        
        self.percent_label = ctk.CTkLabel(
            status_frame,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.percent_label.grid(row=0, column=2)
    
    def _on_files_dropped(self, files: list):
        """Handle files dropped."""
        if files:
            self.selected_files = [f for f in files if Path(f).suffix.lower() in self.cleaner.SUPPORTED_EXTENSIONS]
            if len(self.selected_files) != len(files):
                messagebox.showwarning(
                    "Aviso",
                    f"Apenas arquivos .txt, .docx, .md são suportados.\n{len(files) - len(self.selected_files)} arquivo(s) ignorado(s)."
                )
            self._update_file_list()
    
    def select_files(self):
        """Abre diálogo para seleção de arquivos."""
        files = filedialog.askopenfilenames(
            title="Selecione os arquivos",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("Word documents", "*.docx"),
                ("All supported", "*.txt *.md *.docx")
            ]
        )
        
        if files:
            self.selected_files = list(files)
            self._update_file_list()
    
    def _update_file_list(self):
        """Atualiza lista de arquivos selecionados."""
        if not self.selected_files:
            return
        
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        
        for i, filepath in enumerate(self.selected_files, 1):
            path = Path(filepath)
            size = format_file_size(path.stat().st_size)
            self.file_listbox.insert("end", f"{i}. {path.name} ({size})\n")
        
        self.file_listbox.configure(state="disabled")
        self.clean_btn.configure(state="normal")
        self.status_label.configure(text=f"{len(self.selected_files)} arquivo(s) selecionado(s)")
    
    def start_cleaning(self):
        """Inicia limpeza em thread separada."""
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado")
            return
        
        self.clean_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.configure(state="disabled")
        self.status_label.configure(text="Processando...")
        
        # Processa em thread separada
        thread = threading.Thread(target=self._process_files, daemon=True)
        thread.start()
    
    def _process_files(self):
        """Processa arquivos em segundo plano."""
        try:
            total = len(self.selected_files)
            self.cleaning_results = []
            
            for i, file_path in enumerate(self.selected_files, 1):
                filename = Path(file_path).stem
                
                # Executa limpeza
                result = self.cleaner.clean_file(file_path)
                self.cleaning_results.append(result)
                
                # Atualiza UI
                if result.sucesso:
                    msg = f"✅ {result.arquivo}: {len(result.limpezas_aplicadas)} limpezas aplicadas"
                else:
                    msg = f"❌ {result.arquivo}: {result.erro}"
                
                self.after(0, lambda m=msg: self._append_result(m))
                
                progress = i / total
                self.after(0, lambda p=progress: self._update_progress_bar(p))
            
            self.after(0, lambda: self._finish_cleaning())
            
        except Exception as e:
            logger.exception(f"Erro na limpeza: {e}")
            self.after(0, lambda: self._show_error(f'Erro: {str(e)}'))
    
    def _append_result(self, message: str):
        """Adiciona mensagem ao resultado."""
        self.result_text.configure(state="normal")
        self.result_text.insert("end", message + "\n")
        self.result_text.configure(state="disabled")
    
    def _update_progress_bar(self, value: float):
        """Atualiza barra de progresso."""
        self.progress_bar.set(value)
        self.percent_label.configure(text=f"{int(value * 100)}%")
    
    def _finish_cleaning(self):
        """Finaliza limpeza."""
        success_count = sum(1 for r in self.cleaning_results if r.sucesso)
        self.status_label.configure(text=f"✅ Conclusão: {success_count}/{len(self.cleaning_results)} arquivos limpos")
        self.clean_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        
        if success_count > 0:
            self.save_btn.configure(state="normal")
    
    def _show_error(self, message: str):
        """Mostra mensagem de erro."""
        self.status_label.configure(text=f"❌ Erro: {message}")
        self.clean_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.percent_label.configure(text="0%")
        messagebox.showerror("Erro", message)
    
    def save_results(self):
        """Salva todos os resultados."""
        if not self.cleaning_results:
            return
        
        saved_count = 0
        for result in self.cleaning_results:
            if result.sucesso and result.caminho_saida:
                saved_count += 1
        
        self.status_label.configure(text=f"✅ {saved_count} arquivo(s) salvos")
        logger.info(f"{saved_count} arquivos limpos salvos")


class MergerTab(ctk.CTkFrame):
    """Tab de mesclagem de PDFs com preview e reordenação."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.merger_service = PDFMergerService()
        self.pdf_files: List[PDFFileInfo] = []
        self.output_path: Optional[str] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface da tab de mesclagem."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📑 Mesclar PDFs",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Selecione múltiplos PDFs, reordene e una em um único arquivo",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_label.grid(row=1, column=0, sticky="w")
        
        # Drop zone
        self.drop_zone = DropZoneFrame(
            self,
            on_drop=self._on_files_dropped,
            text="Arraste PDFs aqui ou clique em Adicionar"
        )
        self.drop_zone.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Botões de ação
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.add_btn = ModernButton(
            btn_frame,
            text="📁 Adicionar PDFs",
            command=self.add_files,
            width=160,
            height=40,
            corner_radius=10
        )
        self.add_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.remove_btn = ModernButton(
            btn_frame,
            text="🗑️ Remover",
            command=self.remove_selected,
            state="disabled",
            width=140,
            height=40,
            corner_radius=10,
            fg_color="#F44336"
        )
        self.remove_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.up_btn = ModernButton(
            btn_frame,
            text="⬆️ Subir",
            command=self.move_up,
            state="disabled",
            width=120,
            height=40,
            corner_radius=10,
            fg_color="#2196F3"
        )
        self.up_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.down_btn = ModernButton(
            btn_frame,
            text="⬇️ Descer",
            command=self.move_down,
            state="disabled",
            width=120,
            height=40,
            corner_radius=10,
            fg_color="#2196F3"
        )
        self.down_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Lista de arquivos com scroll
        list_frame = ShadowFrame(self, corner_radius=12)
        list_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Canvas com scrollbar
        self.canvas = ctk.CTkCanvas(list_frame, highlightthickness=0, bg="#2a2a2a")
        scrollbar = ctk.CTkScrollbar(list_frame, orientation="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=12)
        
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        
        # Opções de mesclagem
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        options_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.bookmarks_var = ctk.BooleanVar(value=True)
        self.bookmarks_check = ctk.CTkCheckBox(
            options_frame,
            text="Manter Bookmarks",
            variable=self.bookmarks_var,
            width=150
        )
        self.bookmarks_check.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.compress_var = ctk.BooleanVar(value=True)
        self.compress_check = ctk.CTkCheckBox(
            options_frame,
            text="Comprimir Resultado",
            variable=self.compress_var,
            width=150
        )
        self.compress_check.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        self.separators_var = ctk.BooleanVar(value=False)
        self.separators_check = ctk.CTkCheckBox(
            options_frame,
            text="Adicionar Separadores",
            variable=self.separators_var,
            width=150
        )
        self.separators_check.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        # Botão de mesclar
        merge_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        merge_btn_frame.grid(row=5, column=0, sticky="e", padx=20, pady=15)
        
        self.merge_btn = ModernButton(
            merge_btn_frame,
            text="🔗 Mesclar PDFs",
            command=self.start_merge,
            state="disabled",
            width=180,
            height=50,
            corner_radius=12,
            fg_color="#4CAF50"
        )
        self.merge_btn.pack(side="right")
        
        # Status bar
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Pronto - Adicione pelo menos 2 PDFs",
            anchor="w",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=250, corner_radius=6)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=1, padx=10)
        
        self.percent_label = ctk.CTkLabel(
            status_frame,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.percent_label.grid(row=0, column=2)
        
        # Bind para seleção
        self.selected_index: Optional[int] = None
    
    def _on_canvas_configure(self, event):
        """Ajusta largura do frame interno."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_frame_configure(self, event):
        """Atualiza região de scroll."""
        pass
    
    def _on_files_dropped(self, files: list):
        """Handle files dropped."""
        if files:
            self.add_pdf_files(files)
    
    def add_files(self):
        """Abre diálogo para seleção de arquivos."""
        files = filedialog.askopenfilenames(
            title="Selecionar PDFs para mesclar",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            self.add_pdf_files(list(files))
    
    def add_pdf_files(self, files: List[str]):
        """Adiciona arquivos PDF à lista."""
        for filepath in files:
            info = self.merger_service.get_pdf_info(filepath)
            if info and info not in self.pdf_files:
                self.pdf_files.append(info)
        
        self.refresh_file_list()
        self.update_buttons()
    
    def refresh_file_list(self):
        """Atualiza visualização da lista de arquivos."""
        # Limpa frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.pdf_files:
            label = ctk.CTkLabel(
                self.scrollable_frame,
                text="Nenhum arquivo adicionado\nArraste PDFs ou clique em 'Adicionar PDFs'",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            )
            label.pack(pady=40)
            return
        
        # Cria cards para cada arquivo
        for idx, pdf_info in enumerate(self.pdf_files):
            card = ctk.CTkFrame(self.scrollable_frame, corner_radius=8, fg_color="#2a2a2a")
            card.pack(fill="x", padx=10, pady=5, ipadx=10, ipady=8)
            
            # Seleção
            radio = ctk.CTkRadioButton(
                card,
                text="",
                command=lambda i=idx: self.select_file(i),
                width=20
            )
            radio.pack(side="left", padx=(5, 10))
            
            # Informações
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)
            
            name_label = ctk.CTkLabel(
                info_frame,
                text=f"📄 {pdf_info.nome}",
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            name_label.pack(anchor="w")
            
            details_label = ctk.CTkLabel(
                info_frame,
                text=f"{pdf_info.num_paginas} páginas • {pdf_info.tamanho_formatado}",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            details_label.pack(anchor="w")
            
            # Ordem
            order_label = ctk.CTkLabel(
                card,
                text=f"#{idx + 1}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#2196F3",
                width=40
            )
            order_label.pack(side="right", padx=10)
        
        self.status_label.configure(text=f"{len(self.pdf_files)} arquivo(s) na fila")
    
    def select_file(self, index: int):
        """Seleciona um arquivo da lista."""
        self.selected_index = index
        self.update_buttons()
    
    def update_buttons(self):
        """Atualiza estado dos botões."""
        has_files = len(self.pdf_files) >= 2
        has_selection = self.selected_index is not None
        
        self.merge_btn.configure(state="normal" if has_files else "disabled")
        self.remove_btn.configure(state="normal" if has_selection else "disabled")
        self.up_btn.configure(state="normal" if has_selection and self.selected_index > 0 else "disabled")
        self.down_btn.configure(state="normal" if has_selection and self.selected_index < len(self.pdf_files) - 1 else "disabled")
    
    def remove_selected(self):
        """Remove arquivo selecionado."""
        if self.selected_index is None or not self.pdf_files:
            return
        
        self.pdf_files.pop(self.selected_index)
        self.selected_index = None
        self.refresh_file_list()
        self.update_buttons()
    
    def move_up(self):
        """Move arquivo selecionado para cima."""
        if self.selected_index is None or self.selected_index <= 0:
            return
        
        self.pdf_files = self.merger_service.reorder_files(
            self.pdf_files,
            self.selected_index,
            self.selected_index - 1
        )
        self.selected_index -= 1
        self.refresh_file_list()
        self.update_buttons()
    
    def move_down(self):
        """Move arquivo selecionado para baixo."""
        if self.selected_index is None or self.selected_index >= len(self.pdf_files) - 1:
            return
        
        self.pdf_files = self.merger_service.reorder_files(
            self.pdf_files,
            self.selected_index,
            self.selected_index + 1
        )
        self.selected_index += 1
        self.refresh_file_list()
        self.update_buttons()
    
    def start_merge(self):
        """Inicia mesclagem em thread separada."""
        if len(self.pdf_files) < 2:
            messagebox.showwarning("Aviso", "Adicione pelo menos 2 PDFs para mesclar")
            return
        
        self.merge_btn.configure(state="disabled")
        self.add_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Mesclando PDFs...")
        
        # Processa em thread separada
        thread = threading.Thread(target=self._merge_pdfs, daemon=True)
        thread.start()
    
    def _merge_pdfs(self):
        """Executa mesclagem em segundo plano."""
        try:
            # Prepara lista de caminhos
            pdf_paths = [f.caminho for f in self.pdf_files]
            
            # Define caminho de saída automático (mesmo diretório do primeiro arquivo)
            first_file = Path(pdf_paths[0])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_output = str(first_file.parent / f"{first_file.stem}_mesclado_{timestamp}.pdf")
            
            # Atualiza progresso inicial
            self.after(0, lambda: self._update_progress(0.3))
            
            # Executa mesclagem (sem diálogo - salvamento automático)
            result = self.merger_service.merge_pdfs(
                pdf_files=pdf_paths,
                output_path=default_output,
                keep_bookmarks=self.bookmarks_var.get(),
                add_separators=self.separators_var.get(),
                compress=self.compress_var.get()
            )
            
            if result.sucesso:
                self.output_path = result.caminho_saida
                self.after(0, lambda: self._finish_merge(result))
            else:
                self.after(0, lambda: self._show_error(result.erro))
                
        except Exception as e:
            logger.exception(f"Erro na mesclagem: {e}")
            self.after(0, lambda: self._show_error(str(e)))
    
    def _update_progress(self, value: float):
        """Atualiza barra de progresso."""
        self.progress_bar.set(value)
        self.percent_label.configure(text=f"{int(value * 100)}%")
    
    def _finish_merge(self, result: MergeResult):
        """Finaliza mesclagem com sucesso."""
        self._update_progress(1.0)
        
        self.status_label.configure(
            text=f"✅ Sucesso! {result.num_paginas_total} páginas mescladas"
        )
        
        self.merge_btn.configure(state="normal")
        self.add_btn.configure(state="normal")
        
        # Mostra resultado
        msg = f"PDF mesclado com sucesso!\n\n"
        msg += f"Arquivo: {Path(self.output_path).name}\n"
        msg += f"Páginas totais: {result.num_paginas_total}\n"
        msg += f"Tamanho: {format_file_size(result.tamanho_final)}\n\n"
        msg += "Arquivos processados:\n"
        for m in result.mensagens:
            msg += f"  {m}\n"
        
        messagebox.showinfo("Mesclagem Concluída", msg)
        
        # Abre pasta
        os.startfile(str(Path(self.output_path).parent)) if os.name == 'nt' else None
    
    def _cancel_merge(self):
        """Cancela operação de mesclagem."""
        self.merge_btn.configure(state="normal")
        self.add_btn.configure(state="normal")
        self.status_label.configure(text="Operação cancelada")
        self._update_progress(0)
    
    def _show_error(self, message: str):
        """Mostra mensagem de erro."""
        self.status_label.configure(text=f"❌ Erro: {message}")
        self.merge_btn.configure(state="normal")
        self.add_btn.configure(state="normal")
        self._update_progress(0)
        messagebox.showerror("Erro", message)


class PDFToolsApp(ctk.CTk):
    """Aplicação principal PDF Tools v2.0."""
    
    def __init__(self):
        super().__init__()
        
        self.title("PDF Tools v2.0 - Profissional")
        self.geometry("1100x750")
        self.minsize(900, 650)
        
        # Configurar tema escuro moderno
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Cores customizadas
        self._configure_colors()
        
        self._setup_ui()
        
        logger.info("PDF Tools v2.0 iniciado")
    
    def _configure_colors(self):
        """Configura paleta de cores personalizada."""
        # Configura cores do tema
        ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = "#1e1e1e"
        ctk.ThemeManager.theme["CTkFrame"]["border_color"] = "#333333"
        ctk.ThemeManager.theme["CTkLabel"]["text_color"] = "#ffffff"
    
    def _setup_ui(self):
        """Configura interface principal."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header estilizado
        header_frame = ctk.CTkFrame(self, height=70, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📄 PDF Tools Professional v2.0",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=25, sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Extração • Compressão • Divisão",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        subtitle_label.grid(row=1, column=0, padx=25, sticky="w", pady=(0, 10))
        
        # Tabview moderno
        self.tabview = ctk.CTkTabview(self, corner_radius=12)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        
        # Adicionar abas
        self.extractor_tab = self.tabview.add("📝 Extrair Texto")
        self.compressor_tab = self.tabview.add("⚡ Comprimir")
        self.splitter_tab = self.tabview.add("✂️ Dividir PDF")
        self.cleaner_tab = self.tabview.add("🧹 Limpar Arquivos")
        self.merger_tab = self.tabview.add("📑 Mesclar PDFs")
        
        # Configurar conteúdo das abas
        self.extractor_frame = ExtractorTab(self.extractor_tab)
        self.extractor_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        self.compressor_frame = CompressorTab(self.compressor_tab)
        self.compressor_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        self.splitter_frame = SplitterTab(self.splitter_tab)
        self.splitter_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        self.cleaner_frame = CleanerTab(self.cleaner_tab)
        self.cleaner_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        self.merger_frame = MergerTab(self.merger_tab)
        self.merger_frame.pack(fill="both", expand=True, padx=12, pady=12)
    
    def on_closing(self):
        """Handle fechamento da aplicação."""
        logger.info('PDF Tools fechado')
        self.destroy()


def main():
    """Função principal."""
    # Garante setup da configuração
    config = get_config()
    config.ensure_setup()
    
    app = PDFToolsApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == '__main__':
    main()
