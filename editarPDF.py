# main.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import os
from datetime import datetime

class PDFManipulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Manipulador de PDF")
        self.root.geometry("600x400")
        
        # Variáveis
        self.selected_files = []
        self.output_folder = os.path.join(os.path.expanduser("~"), "Documents", "PDF_Manipulator")
        
        # Criar pasta de saída se não existir
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Notebook para as abas
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Aba de juntar PDFs
        merge_frame = ttk.Frame(notebook)
        notebook.add(merge_frame, text='Juntar PDFs')
        self.setup_merge_tab(merge_frame)
        
        # Aba de dividir PDF
        split_frame = ttk.Frame(notebook)
        notebook.add(split_frame, text='Dividir PDF')
        self.setup_split_tab(split_frame)
        
    def setup_merge_tab(self, parent):
        # Frame para lista de arquivos
        list_frame = ttk.LabelFrame(parent, text="Arquivos Selecionados")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Listbox para arquivos
        self.files_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.files_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Frame para botões
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        # Botões
        ttk.Button(button_frame, text="ADICIONAR", command=self.add_files).pack(side='left', padx=10)
        ttk.Button(button_frame, text="REMOVER", command=self.remove_files).pack(side='left', padx=105)
        ttk.Button(button_frame, text="MESCLAR", command=self.merge_pdfs).pack(side='right', padx=10)
        
    def setup_split_tab(self, parent):
        # Frame para seleção de arquivo
        file_frame = ttk.LabelFrame(parent, text="Arquivo Selecionado")
        file_frame.pack(fill='x', padx=10, pady=10)
        
        self.split_file_var = tk.StringVar()
        ttk.Label(file_frame, textvariable=self.split_file_var).pack(fill='x', padx=5, pady=5)
        
        # Frame para botões
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        # Botões
        ttk.Button(button_frame, text="SELECIONAR", command=self.select_split_file).pack(side='left', padx=10)
        ttk.Button(button_frame, text="DIVIDIR", command=self.split_pdf).pack(side='left', padx=10)
        
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Selecionar PDFs",
            filetypes=[("PDF files", "*.pdf")]
        )
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.files_listbox.insert(tk.END, os.path.basename(file))
                
    def remove_files(self):
        selection = self.files_listbox.curselection()
        for index in reversed(selection):
            self.files_listbox.delete(index)
            self.selected_files.pop(index)
            
    def merge_pdfs(self):
        if len(self.selected_files) < 2:
            messagebox.showerror("Erro", "Selecione pelo menos 2 arquivos PDF para juntar!")
            return
            
        try:
            # Gerar nome do arquivo de saída
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_folder, f"riko_{timestamp}.pdf")
            
            merger = PdfMerger()
            for pdf in self.selected_files:
                merger.append(pdf)
                
            merger.write(output_file)
            merger.close()
            
            messagebox.showinfo("Parabéns", f"O arquivo foi criado com sucesso!\nSalvo em: {output_file}")
            
            # Abrir a pasta com o arquivo
            os.startfile(self.output_folder)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao mesclar PDFs: {str(e)}")
            
    def select_split_file(self):
        file = filedialog.askopenfilename(
            title="Selecionar PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file:
            self.split_file_var.set(os.path.basename(file))
            self.split_file_path = file
            
    def split_pdf(self):
        if not hasattr(self, 'split_file_path'):
            messagebox.showerror("Erro", "Selecione um arquivo PDF para dividir!")
            return
            
        try:
            # Criar pasta para páginas
            timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
            output_dir = os.path.join(self.output_folder, f"dividido_{timestamp}")
            os.makedirs(output_dir)
            
            # Dividir PDF
            pdf = PdfReader(self.split_file_path)
            for page_num in range(len(pdf.pages)):
                writer = PdfWriter()
                writer.add_page(pdf.pages[page_num])
                
                output_path = os.path.join(output_dir, f"pagina_{page_num + 1}.pdf")
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)
                    
            messagebox.showinfo("Parabéns", f"Os arquivos foram criados com sucesso!\nSalvo em: {output_dir}")
            
            # Abrir a pasta com os arquivos
            os.startfile(output_dir)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao dividir PDF: {str(e)}")

def main():
    root = tk.Tk()
    app = PDFManipulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
