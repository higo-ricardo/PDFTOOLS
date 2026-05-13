"""Tab de Extração de Imagens de PDFs."""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from core.services.image_extractor import ImageExtractorService, ExtractionResult
from utils.helpers import format_file_size
from gui_tkinter.widgets.modern_widgets import ModernButton, DropZoneFrame, ProgressCard


class ImageExtractorTab(ctk.CTkFrame):
    """Tab de extração de imagens de PDFs."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.extractor = ImageExtractorService()
        self.selected_files: List[str] = []
        self.extraction_results: List[ExtractionResult] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface da tab de extração de imagens."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header com título
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🖼️ Extrair Imagens de PDF",
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
        self.select_btn.grid(row=0, column=0, padx=10, pady=5)
        
        self.extract_btn = ModernButton(
            btn_frame,
            text="✨ Extrair Imagens",
            command=self.start_extraction,
            width=160,
            height=45,
            corner_radius=12,
            state="disabled"
        )
        self.extract_btn.grid(row=0, column=1, padx=10, pady=5)
        
        self.open_folder_btn = ModernButton(
            btn_frame,
            text="📂 Abrir Pasta",
            command=self.open_output_folder,
            width=160,
            height=45,
            corner_radius=12,
            state="disabled"
        )
        self.open_folder_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Opções de extração
        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        options_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Formato de saída
        ctk.CTkLabel(options_frame, text="Formato:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.format_var = ctk.StringVar(value="png")
        format_menu = ctk.CTkOptionMenu(
            options_frame,
            values=["png", "jpg", "tiff"],
            variable=self.format_var,
            width=120
        )
        format_menu.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Redimensionamento
        ctk.CTkLabel(options_frame, text="Redimensionar:").grid(row=0, column=2, sticky="w", padx=10, pady=5)
        self.resize_var = ctk.StringVar(value="original")
        resize_menu = ctk.CTkOptionMenu(
            options_frame,
            values=["original", "800x600", "1920x1080"],
            variable=self.resize_var,
            width=120
        )
        resize_menu.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Lista de arquivos
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        ctk.CTkLabel(
            list_frame,
            text="Arquivos Selecionados:",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.files_listbox = ctk.CTkScrollableFrame(list_frame, height=150)
        self.files_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.files_listbox.grid_columnconfigure(0, weight=1)
        
        # Área de resultados
        self.results_frame = ctk.CTkFrame(self)
        self.results_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        self.results_label = ctk.CTkLabel(
            self.results_frame,
            text="",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        self.results_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Barra de progresso
        self.progress_card = ProgressCard(self, title="Extraindo imagens...", show_details=True)
        self.progress_card.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        self.progress_card.grid_remove()
    
    def _on_files_dropped(self, files: List[str]):
        """Handle files dropped na zona de drop."""
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        
        if pdf_files:
            self.selected_files.extend(pdf_files)
            self._update_files_list()
            self.drop_zone.set_active(True)
            self.after(1000, lambda: self.drop_zone.set_active(False))
    
    def select_files(self):
        """Abre diálogo para selecionar arquivos PDF."""
        files = filedialog.askopenfilenames(
            title="Selecionar PDFs para extrair imagens",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            self.selected_files.extend(list(files))
            self._update_files_list()
    
    def _update_files_list(self):
        """Atualiza lista visual de arquivos."""
        # Limpa lista atual
        for widget in self.files_listbox.winfo_children():
            widget.destroy()
        
        if not self.selected_files:
            ctk.CTkLabel(
                self.files_listbox,
                text="Nenhum arquivo selecionado",
                text_color="gray"
            ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
            self.extract_btn.configure(state="disabled")
        else:
            for idx, file_path in enumerate(self.selected_files):
                name = os.path.basename(file_path)
                size = format_file_size(os.path.getsize(file_path))
                
                file_frame = ctk.CTkFrame(self.files_listbox, fg_color="transparent")
                file_frame.grid(row=idx, column=0, sticky="ew", padx=5, pady=2)
                file_frame.grid_columnconfigure(0, weight=1)
                
                ctk.CTkLabel(
                    file_frame,
                    text=f"📄 {name} ({size})",
                    font=ctk.CTkFont(size=10),
                    justify="left"
                ).grid(row=0, column=0, sticky="w")
                
                remove_btn = ctk.CTkButton(
                    file_frame,
                    text="❌",
                    width=30,
                    height=25,
                    command=lambda fp=file_path: self._remove_file(fp)
                )
                remove_btn.grid(row=0, column=1, padx=5)
            
            self.extract_btn.configure(state="normal")
    
    def _remove_file(self, file_path: str):
        """Remove arquivo da lista."""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            self._update_files_list()
    
    def start_extraction(self):
        """Inicia extração de imagens em thread separada."""
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Selecione pelo menos um arquivo PDF.")
            return
        
        self.extract_btn.configure(state="disabled")
        self.progress_card.grid()
        self.progress_card.update_progress(0, "Preparando extração...")
        
        # Thread de extração
        thread = threading.Thread(target=self._run_extraction, daemon=True)
        thread.start()
    
    def _run_extraction(self):
        """Executa extração em background."""
        try:
            total_files = len(self.selected_files)
            output_format = self.format_var.get()
            resize_option = self.resize_var.get()
            
            resize_to = None
            if resize_option == "800x600":
                resize_to = (800, 600)
            elif resize_option == "1920x1080":
                resize_to = (1920, 1080)
            
            self.extraction_results = []
            
            for idx, file_path in enumerate(self.selected_files):
                progress = (idx + 1) / total_files
                self.after(0, lambda p=progress, f=file_path: 
                    self.progress_card.update_progress(p, f"Processando: {os.path.basename(f)}"))
                
                result = self.extractor.extract_images(
                    file_path,
                    output_format=output_format,
                    resize_to=resize_to
                )
                self.extraction_results.append(result)
            
            # Conclusão
            total_images = sum(r.images_extracted for r in self.extraction_results)
            self.after(0, lambda: self._on_extraction_complete(total_images))
            
        except Exception as e:
            self.after(0, lambda: self._on_extraction_error(str(e)))
    
    def _on_extraction_complete(self, total_images: int):
        """Callback quando extração completa."""
        self.progress_card.grid_remove()
        self.extract_btn.configure(state="normal")
        self.open_folder_btn.configure(state="normal")
        
        msg = f"✅ Extração concluída!\n\n"
        msg += f"📊 Total de imagens extraídas: {total_images}\n\n"
        
        for result in self.extraction_results:
            msg += f"• {os.path.basename(result.pdf_path)}: {result.images_extracted} imagens\n"
            msg += f"  → Pasta: {os.path.basename(result.output_folder)}\n"
        
        self.results_label.configure(text=msg)
        messagebox.showinfo("Sucesso", f"{total_images} imagens extraídas com sucesso!")
    
    def _on_extraction_error(self, error: str):
        """Callback quando ocorre erro."""
        self.progress_card.grid_remove()
        self.extract_btn.configure(state="normal")
        
        self.results_label.configure(text=f"❌ Erro: {error}")
        messagebox.showerror("Erro", f"Falha na extração: {error}")
    
    def open_output_folder(self):
        """Abre pasta de saída no explorador."""
        if self.extraction_results and len(self.extraction_results) > 0:
            folder = self.extraction_results[0].output_folder
            if os.path.exists(folder):
                os.startfile(folder) if os.name == 'nt' else os.system(f'xdg-open "{folder}"')
