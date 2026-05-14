import tkinter as tk
from tkinter import filedialog, messagebox, font, ttk, scrolledtext
import os
import threading
from tkinterdnd2 import DND_FILES, TkinterDnD
from abc import ABC, abstractmethod
import functools
from typing import List, Optional

# --- Importação dos Módulos Core ---
from core.services.pdf_merger import PDFMergerService
from core.services.pdf_splitter import PDFSplitterService
from core.pdf_compressor import PDFCompressor
from core.services.extractor_service import StreamingPDFExtractor
from core.task_queue import get_task_queue, Priority, TaskStatus

# --- Importação de UI e Widgets ---
from utils.theme_manager import get_theme_manager, ColorPalette
from widgets import DropZone, FileCard, ModernButton

# =============================================================================
# CLASSES ABSTRATAS PARA AS OPERAÇÕES DE PDF
# =============================================================================
class PDFOperation(ABC):
    """Classe base abstrata para todas as operações de PDF."""
    def __init__(self, app_instance):
        self.app = app_instance

    @property
    @abstractmethod
    def name(self) -> str: pass

    @property
    @abstractmethod
    def icon(self) -> str: pass

    @abstractmethod
    def is_valid(self, file_count: int) -> bool: pass

    @abstractmethod
    def configure_and_execute(self): pass

    def _enqueue_task(self, func, args=(), kwargs=None, priority=Priority.NORMAL):
        """Adiciona a operação à fila de tarefas global e desativa a UI."""
        self.app.disable_ui()
        self.app.log(f"Agendando tarefa: {self.name}...")
        
        task_id = self.app.task_queue.add_task(
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            callbacks={
                'on_start': lambda: self.app.after(0, self.app.log, f"Em execução: {self.name}..."),
                'on_complete': lambda res: self.app.after(0, self.app.on_operation_result, True, self.name, str(res)),
                'on_error': lambda err: self.app.after(0, self.app.on_operation_result, False, self.name, err)
            }
        )
        self.app.log(f"Tarefa {self.name} na fila (ID: {task_id[:8]})")

# --- Implementações Concretas usando TaskQueue ---

class MergeOperation(PDFOperation):
    name = "Juntar"
    icon = "➕"
    def is_valid(self, count): return count >= 2
    
    def configure_and_execute(self):
        output = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="merged.pdf", filetypes=[("PDF", "*.pdf")])
        if not output: return
        
        self._enqueue_task(
            func=self.app.services['merger'].merge_pdfs,
            args=(self.app.selected_files, output),
            priority=Priority.HIGH
        )

class SplitOperation(PDFOperation):
    name = "Dividir"
    icon = "✂️"
    def is_valid(self, count): return count == 1
    
    def configure_and_execute(self):
        output_dir = filedialog.askdirectory(title="Salvar arquivos divididos em...")
        if not output_dir: return
        
        self._enqueue_task(
            func=self.app.services['splitter'].split_to_individual_pages,
            args=(self.app.selected_files[0], output_dir),
            priority=Priority.NORMAL
        )

class CompressOperation(PDFOperation):
    name = "Comprimir"
    icon = "📦"
    def is_valid(self, count): return count >= 1
    
    def configure_and_execute(self):
        output_dir = filedialog.askdirectory(title="Salvar arquivos comprimidos em...")
        if not output_dir: return
        
        def run_compression(files, out_dir):
            results, success = self.app.services['compressor'].compress_batch(files, output_dir=out_dir)
            if not success:
                raise Exception("Falha na compressão em lote.")
            return f"{len(results)} arquivos comprimidos com sucesso."

        self._enqueue_task(
            func=run_compression,
            args=(self.app.selected_files, output_dir),
            priority=Priority.LOW
        )

class ExtractOperation(PDFOperation):
    name = "Extrair Texto"
    icon = "📝"
    def is_valid(self, count): return count >= 1
    
    def configure_and_execute(self):
        output_file = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="extracao.txt", filetypes=[("Texto", "*.txt")])
        if not output_file: return
        
        def process_extraction(files, out_path):
            full_text = ""
            for f in files:
                text, status = self.app.services['extractor'].extract_from_file_path(f)
                if status == "sucesso":
                    full_text += f"\n--- {os.path.basename(f)} ---\n{text}\n"
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(full_text)
            return f"Texto salvo em {os.path.basename(out_path)}"

        self._enqueue_task(
            func=process_extraction,
            args=(self.app.selected_files, output_file),
            priority=Priority.NORMAL
        )

# =============================================================================
# CLASSE PRINCIPAL DA APLICAÇÃO
# =============================================================================
class PDFToolApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Pro Suite v4.0")
        self.geometry("850x850")
        
        # Inicialização dos Serviços
        self.services = {
            'merger': PDFMergerService(),
            'splitter': PDFSplitterService(),
            'compressor': PDFCompressor(),
            'extractor': StreamingPDFExtractor()
        }
        self.task_queue = get_task_queue()
        self.theme_manager = get_theme_manager()
        
        self._selected_files = []
        self.current_operation = None
        
        self._setup_styles()
        self._create_widgets()
        
        # Subscreve ao tema para atualizações dinâmicas
        self.theme_manager.subscribe(self.apply_theme)

    @property
    def selected_files(self): return self._selected_files

    @selected_files.setter
    def selected_files(self, value):
        self._selected_files = value
        self._update_file_display()
        self._update_ui_state()
        
    def _setup_styles(self):
        self.fonts = {"h1": ("Segoe UI", 11, "bold"), "body": ("Segoe UI", 10), "small": ("Segoe UI", 8)}

    def _create_widgets(self):
        # 0. HEADER COM TEMA
        self.header_frame = tk.Frame(self, pady=10)
        self.header_frame.pack(fill=tk.X)
        
        self.title_label = tk.Label(self.header_frame, text="PDF PRO SUITE", font=("Segoe UI", 14, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=20)
        
        self.btn_theme = tk.Button(self.header_frame, text="🌓 Alternar Tema", command=self.theme_manager.toggle_theme,
                                  relief=tk.FLAT, font=self.fonts["small"], padx=10)
        self.btn_theme.pack(side=tk.RIGHT, padx=20)

        # 1. BARRA DE OPERAÇÕES
        self.operations = [op(self) for op in [MergeOperation, SplitOperation, CompressOperation, ExtractOperation]]
        self.action_buttons = {}
        self.action_bar = tk.Frame(self, pady=15)
        self.action_bar.pack(fill=tk.X)
        for op in self.operations:
            btn = ModernButton(self.action_bar, text=f" {op.icon} {op.name}", command=lambda o=op: self._select_operation(o),
                               font=self.fonts["h1"])
            btn.pack(side=tk.LEFT, expand=True, padx=10)
            self.action_buttons[op.name] = btn

        # 2. ÁREA DE ARRASTAR E SOLTAR
        self.drop_zone = DropZone(self, on_drop_callback=self._on_drop, on_click_callback=self.select_files_dialog,
                                 palette=self.theme_manager.get_palette(), fonts=self.fonts)
        self.drop_zone.pack(fill=tk.X, padx=20, pady=20)

        # 3. ÁREA DOS CARDS DE ARQUIVOS (Scrollable)
        self.files_container = tk.Frame(self)
        self.canvas = tk.Canvas(self.files_container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.files_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 4. LOG DE ATIVIDADE
        self.log_frame = tk.LabelFrame(self, text="Log de Atividade", font=self.fonts["h1"], padx=10, pady=5)
        self.log_frame.pack(fill=tk.BOTH, expand=False, padx=20, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=6, state='disabled', wrap=tk.WORD, 
                                                 relief=tk.FLAT, font=self.fonts["body"])
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 5. BARRA DE AÇÃO FINAL
        self.final_action_bar = tk.Frame(self, pady=10)
        self.btn_execute = ModernButton(self.final_action_bar, text="🚀 Executar Ação", command=self._execute_current_operation,
                                        font=self.fonts["h1"], fg="white", padx=20, pady=8)
        self.btn_cancel = ModernButton(self.final_action_bar, text="✖ Cancelar", command=self._cancel_operation,
                                       font=self.fonts["h1"], fg="white", padx=20, pady=8)
        
        # 6. STATUS BAR
        self.status_bar = tk.Frame(self, height=25, relief=tk.SUNKEN, borderwidth=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.label_queue_status = tk.Label(self.status_bar, text="Fila: 0 tarefas", font=self.fonts["small"])
        self.label_queue_status.pack(side=tk.LEFT, padx=10)
        
        self._update_queue_display()
        self._update_ui_state()

    def apply_theme(self, theme_name, palette: ColorPalette):
        """Aplica cores do tema a todos os widgets."""
        self.configure(bg=palette.background)
        self.header_frame.configure(bg=palette.background)
        self.title_label.configure(bg=palette.background, fg=palette.text)
        self.btn_theme.configure(bg=palette.frame, fg=palette.text, activebackground=palette.frame)
        
        self.action_bar.configure(bg=palette.frame)
        for op_name, btn in self.action_buttons.items():
            btn.apply_theme(palette.frame, palette.text)
            
        self.drop_zone.apply_theme(palette)
        
        self.files_container.configure(bg=palette.background)
        self.canvas.configure(bg=palette.background)
        self.scrollable_frame.configure(bg=palette.background)
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, FileCard):
                widget.apply_theme(palette)
                
        self.log_frame.configure(bg=palette.frame, fg=palette.text)
        self.log_text.configure(bg=palette.background, fg=palette.text, insertbackground=palette.text)
        
        self.final_action_bar.configure(bg=palette.background)
        self.btn_execute.apply_theme(palette.go, "white")
        self.btn_cancel.apply_theme(palette.stop, "white")
        
        self.status_bar.configure(bg=palette.frame)
        self.label_queue_status.configure(bg=palette.frame, fg=palette.text)

    def _update_queue_display(self):
        count = self.task_queue.get_queue_size()
        status = "Processando..." if self.task_queue.is_processing() else "Ocioso"
        self.label_queue_status.config(text=f"Fila: {count} tarefas | {status}")
        self.after(1000, self._update_queue_display)

    def _on_drop(self, event):
        new_files = [path for path in self.tk.splitlist(event.data) if path.lower().endswith('.pdf')]
        if new_files:
            self.selected_files = self.selected_files + new_files
            self.log(f"Adicionados {len(new_files)} arquivos via Drag & Drop.")

    def select_files_dialog(self):
        new_files = filedialog.askopenfilenames(title="Selecione os PDFs", filetypes=[("PDF", "*.pdf")])
        if new_files:
            self.selected_files = self.selected_files + list(new_files)
            self.log(f"Adicionados {len(new_files)} arquivos via diálogo.")

    def _remove_file(self, filepath):
        temp_list = list(self.selected_files)
        temp_list.remove(filepath)
        self.selected_files = temp_list

    def _update_file_display(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        palette = self.theme_manager.get_palette()
        if not self.selected_files:
            self.drop_zone.pack(fill=tk.X, padx=20, pady=20)
            self.files_container.pack_forget()
        else:
            self.drop_zone.pack_forget()
            self.files_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            for f in self.selected_files: 
                card = FileCard(self.scrollable_frame, f, self._remove_file, palette, self.fonts)
                card.pack(fill=tk.X, padx=5, pady=3)

    def _update_ui_state(self):
        count = len(self.selected_files)
        palette = self.theme_manager.get_palette()
        for op in self.operations:
            btn = self.action_buttons[op.name]
            is_valid = op.is_valid(count)
            btn.config(state=tk.NORMAL if is_valid else tk.DISABLED)
            if not is_valid:
                btn.configure(fg=palette.secondary_text)
            else:
                btn.configure(fg=palette.text)
        
        if self.current_operation and not self.current_operation.is_valid(count):
            self._cancel_operation()

    def _select_operation(self, operation):
        self.current_operation = operation
        palette = self.theme_manager.get_palette()
        self.final_action_bar.pack(fill=tk.X, padx=20, pady=(0,10))
        self.btn_execute.pack(side=tk.RIGHT)
        self.btn_cancel.pack(side=tk.RIGHT, padx=10)
        self.btn_execute.config(text=f"🚀 Executar {operation.name}")
        for btn in self.action_buttons.values(): btn.config(borderwidth=0)
        self.action_buttons[operation.name].config(borderwidth=2, highlightbackground=palette.accent)
        
    def _cancel_operation(self):
        self.current_operation = None
        for btn in self.action_buttons.values(): btn.config(borderwidth=0)
        self.final_action_bar.pack_forget()

    def _execute_current_operation(self):
        if self.current_operation:
            self.current_operation.configure_and_execute()

    def on_operation_result(self, success, op_name, message):
        self.enable_ui()
        if success:
            self.log(f"SUCESSO: '{op_name}' concluído. {message}")
            messagebox.showinfo("Sucesso", f"Operação '{op_name}' concluída com sucesso!")
            self._cancel_operation()
            self.selected_files = [] 
        else:
            self.log(f"ERRO em '{op_name}': {message}")
            messagebox.showerror("Erro", f"Falha na operação '{op_name}':\n{message}")

    def disable_ui(self):
        # Desativa apenas botões de operação e execução
        for btn in self.action_buttons.values(): btn.config(state=tk.DISABLED)
        self.btn_execute.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.DISABLED)

    def enable_ui(self):
        self._update_ui_state()
        self.btn_execute.config(state=tk.NORMAL)
        self.btn_cancel.config(state=tk.NORMAL)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

if __name__ == "__main__":
    app = PDFToolApp()
    app.mainloop()
