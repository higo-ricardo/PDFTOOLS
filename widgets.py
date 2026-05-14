import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES

class DropZone(tk.Frame):
    """Componente visual para arraste de arquivos e seleção manual."""
    def __init__(self, master, on_drop_callback, on_click_callback, palette, fonts, **kwargs):
        super().__init__(master, **kwargs)
        self.on_drop_callback = on_drop_callback
        self.on_click_callback = on_click_callback
        self.palette = palette
        self.fonts = fonts
        
        self.configure(highlightthickness=2)
        
        self.label_icon = tk.Label(self, text="📂", font=("Segoe UI", 32))
        self.label_icon.pack(pady=(30, 5))
        
        self.label_text = tk.Label(self, text="Arraste e solte seus PDFs aqui\nou clique para selecionar", 
                                   font=self.fonts["body"])
        self.label_text.pack(pady=(0, 30))
        
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop_callback)
        self.bind("<Button-1>", lambda e: self.on_click_callback())
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.apply_theme(self.palette)
        
    def _on_enter(self, event):
        self.configure(highlightbackground=self.palette.accent, bg=self.palette.background)
        # Mais brilho no hover?
        self.label_icon.configure(bg=self.palette.background)
        self.label_text.configure(bg=self.palette.background)

    def _on_leave(self, event):
        self.configure(highlightbackground=self.palette.border, bg=self.palette.frame)
        self.label_icon.configure(bg=self.palette.frame)
        self.label_text.configure(bg=self.palette.frame)

    def apply_theme(self, palette):
        self.palette = palette
        self.configure(bg=palette.frame, highlightbackground=palette.border)
        self.label_icon.configure(bg=palette.frame, fg=palette.accent)
        self.label_text.configure(bg=palette.frame, fg=palette.secondary_text)

class FileCard(tk.Frame):
    """Card individual para arquivo na lista."""
    def __init__(self, master, filepath, on_remove, palette, fonts, **kwargs):
        super().__init__(master, **kwargs)
        self.palette = palette
        self.fonts = fonts
        self.filepath = filepath
        
        self.configure(padx=10, pady=8, highlightthickness=1)
        
        self.label_icon = tk.Label(self, text="📄", font=("Segoe UI Symbol", 14))
        self.label_icon.pack(side=tk.LEFT)
        
        self.info_frame = tk.Frame(self)
        self.info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        import os
        self.label_name = tk.Label(self.info_frame, text=os.path.basename(filepath), font=self.fonts["body"], anchor='w')
        self.label_name.pack(fill=tk.X)
        
        try: fsize = f"{os.path.getsize(filepath)/1024:.1f} KB"
        except Exception: fsize = "N/A"
        self.label_size = tk.Label(self.info_frame, text=fsize, font=self.fonts["small"], anchor='w')
        self.label_size.pack(fill=tk.X)
        
        self.btn_remove = tk.Button(self, text="✖", command=lambda: on_remove(filepath), 
                                   relief=tk.FLAT, font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.btn_remove.pack(side=tk.RIGHT)
        self.apply_theme(palette)

    def apply_theme(self, palette):
        self.palette = palette
        self.configure(bg=palette.card, highlightbackground=palette.border)
        self.label_icon.configure(bg=palette.card, fg=palette.accent)
        self.info_frame.configure(bg=palette.card)
        self.label_name.configure(bg=palette.card, fg=palette.text)
        self.label_size.configure(bg=palette.card, fg=palette.secondary_text)
        self.btn_remove.configure(bg=palette.card, fg=palette.secondary_text, activebackground=palette.card)

class ModernButton(tk.Button):
    """Botão com estilo customizado."""
    def __init__(self, master, **kwargs):
        self.palette = kwargs.pop('palette', None)
        # Define valores padrão se não fornecidos
        if 'relief' not in kwargs: kwargs['relief'] = tk.FLAT
        if 'pady' not in kwargs: kwargs['pady'] = 5
        if 'borderwidth' not in kwargs: kwargs['borderwidth'] = 0
        
        self.base_bg = kwargs.get('bg', "SystemButtonFace")
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        if self['state'] != tk.DISABLED:
            # Escurece um pouco no hover
            self.configure(bg=self._adjust_color(self.cget('bg'), -10))

    def _on_leave(self, event):
        self.configure(bg=self.base_bg)

    def _adjust_color(self, hex_color, amount):
        """Ajusta brilho de uma cor hex."""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            new_rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
            return '#%02x%02x%02x' % new_rgb
        return hex_color

    def apply_theme(self, bg, fg):
        self.base_bg = bg
        self.configure(bg=bg, fg=fg)
