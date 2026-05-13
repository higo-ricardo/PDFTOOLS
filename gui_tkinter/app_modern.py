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
        
        # Configurar conteúdo das abas
        self.extractor_frame = ExtractorTab(self.extractor_tab)
        self.extractor_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        self.compressor_frame = CompressorTab(self.compressor_tab)
        self.compressor_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        self.splitter_frame = SplitterTab(self.splitter_tab)
        self.splitter_frame.pack(fill="both", expand=True, padx=12, pady=12)
    
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
