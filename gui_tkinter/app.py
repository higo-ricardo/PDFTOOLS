"""
Aplicação principal PDF Tools com CustomTkinter.
Interface moderna, nativa e mais leve que Kivy.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pdf_extractor import PDFTextExtractor
from core.pdf_compressor import PDFCompressor
from utils.helpers import format_file_size


class ExtractorFrame(ctk.CTkFrame):
    """Frame de extração de texto de PDFs."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.extractor = PDFTextExtractor()
        self.selected_files = []
        self.has_text = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a interface do extrator."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Frame de botões superiores
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.select_btn = ctk.CTkButton(
            btn_frame, 
            text="📁 Selecionar PDF(s)",
            command=self.select_files,
            width=150
        )
        self.select_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.process_btn = ctk.CTkButton(
            btn_frame,
            text="▶️ Processar",
            command=self.start_extraction,
            state="disabled",
            width=150
        )
        self.process_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Salvar",
            command=self.save_results,
            state="disabled",
            width=150
        )
        self.save_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Área de texto
        self.result_text = ctk.CTkTextbox(self, wrap="word", state="disabled")
        self.result_text.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        # Frame de status
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Pronto - Selecione um arquivo PDF",
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=5)
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="right", padx=5)
    
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
        """Inicia a extração em thread separada."""
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
        """Processa os arquivos em segundo plano."""
        try:
            total = len(self.selected_files)
            processed_text = ""
            
            for i, file_path in enumerate(self.selected_files, 1):
                text, status = self.extractor.extract_from_file_path(file_path)
                
                if status == "erro":
                    self.after(0, lambda: self._show_error(text))
                    return
                
                filename = Path(file_path).stem
                processed_text += f"► {filename}\n{text}\n\n"
                
                # Atualiza progresso
                progress = i / total
                self.after(0, lambda p=progress: self.progress_bar.set(p))
            
            # Atualiza UI com resultado
            self.after(0, lambda: self._finish_extraction(processed_text))
            
        except Exception as e:
            self.after(0, lambda: self._show_error(f'Erro: {str(e)}'))
    
    def _finish_extraction(self, text):
        """Finaliza extração e mostra resultado."""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")
        
        self.status_label.configure(text="Processamento concluído!")
        self.process_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.has_text = True
    
    def _show_error(self, message):
        """Mostra mensagem de erro."""
        self.status_label.configure(text=f'Erro: {message}')
        self.process_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.progress_bar.set(0)
        messagebox.showerror("Erro", message)
    
    def save_results(self):
        """Salva resultados em arquivo."""
        if not self.has_text:
            return
        
        save_path = filedialog.asksaveasfilename(
            title="Salvar resultado",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.get("1.0", "end-1c"))
                
                self.status_label.configure(text=f'Arquivo salvo: {save_path}')
            except Exception as e:
                self.status_label.configure(text=f'Erro ao salvar: {str(e)}')
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")


class CompressorFrame(ctk.CTkFrame):
    """Frame de compressão de PDFs."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.compressor = PDFCompressor()
        self.file_path = None
        self.file_selected = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a interface do compressor."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Frame de controles
        ctrl_frame = ctk.CTkFrame(self)
        ctrl_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        ctrl_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.select_btn = ctk.CTkButton(
            ctrl_frame,
            text="📁 Selecionar PDF",
            command=self.select_file,
            width=150
        )
        self.select_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.compression_var = ctk.StringVar(value="MÉDIA")
        self.compression_menu = ctk.CTkOptionMenu(
            ctrl_frame,
            variable=self.compression_var,
            values=["BAIXA", "MÉDIA", "ALTA"],
            width=150
        )
        self.compression_menu.grid(row=0, column=1, padx=5, pady=5)
        
        self.compress_btn = ctk.CTkButton(
            ctrl_frame,
            text="⚡ Comprimir",
            command=self.compress_pdf,
            state="disabled",
            width=150
        )
        self.compress_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Informações do arquivo
        self.file_info_label = ctk.CTkLabel(
            self,
            text="Nenhum arquivo selecionado",
            justify="left",
            anchor="w"
        )
        self.file_info_label.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        # Área de resultado
        self.result_label = ctk.CTkLabel(
            self,
            text="",
            justify="center"
        )
        self.result_label.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        # Frame de status
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Pronto",
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=5)
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="right", padx=5)
    
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
        """Atualiza informações do arquivo selecionado."""
        if not self.file_path:
            return
        
        info = self.compressor.get_file_info(self.file_path)
        
        if 'error' in info:
            self.file_info_label.configure(
                text="Erro ao ler arquivo",
                text_color="red"
            )
            self.file_selected = False
            self.compress_btn.configure(state="disabled")
        else:
            self.file_info_label.configure(
                text=(
                    f"📄 Arquivo: {info['filename']}\n"
                    f"📊 Tamanho: {format_file_size(int(info['size_bytes']))} | "
                    f"📑 Páginas: {info['pages']}"
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
    
    def _do_compress(self, compression_level):
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
            self.after(0, lambda: self._show_error(f'Erro: {str(e)}'))
    
    def _finish_compress(self, result_path, reduction):
        """Finaliza compressão e mostra resultado."""
        self.result_label.configure(
            text=(
                f"✅ PDF comprimido com sucesso!\n\n"
                f"📁 Salvo em: {result_path}\n"
                f"📉 Redução: {reduction:.1f}%"
            )
        )
        self.status_label.configure(text="Concluído!", text_color="green")
        self.compress_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.progress_bar.set(1)
    
    def _show_error(self, message):
        """Mostra mensagem de erro."""
        self.status_label.configure(text=f"❌ {message}", text_color="red")
        self.compress_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.progress_bar.set(0)
        messagebox.showerror("Erro", message)


class PDFToolsApp(ctk.CTk):
    """Aplicação principal PDF Tools com CustomTkinter."""
    
    def __init__(self):
        super().__init__()
        
        self.title("PDF Tools - Extrator & Compressor")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a interface principal."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, height=60)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📄 PDF Tools - Extrator & Compressor",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, sticky="w")
        
        # Tabview para navegação
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Adicionar abas
        self.extractor_tab = self.tabview.add("Extrair Texto")
        self.compressor_tab = self.tabview.add("Comprimir PDF")
        
        # Configurar frames das abas
        self.extractor_frame = ExtractorFrame(self.extractor_tab)
        self.extractor_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.compressor_frame = CompressorFrame(self.compressor_tab)
        self.compressor_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def on_closing(self):
        """Executado ao fechar a aplicação."""
        import logging
        logging.info('PDF Tools fechado')
        self.destroy()


def main():
    """Função principal para executar a aplicação."""
    app = PDFToolsApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == '__main__':
    main()
