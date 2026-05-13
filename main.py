"""
Aplicação principal do PDF Tools.
Interface unificada em Kivy para extração de texto e compressão de PDFs.
"""

import sys
import os

# Adiciona o diretório raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

# Importa módulos do core
from PDF.core.pdf_extractor import PDFTextExtractor
from PDF.core.pdf_compressor import PDFCompressor

# Importa telas
from PDF.gui.screens import ExtractorScreen, CompressorScreen

# Carrega arquivo KV
Builder.load_file(os.path.join(os.path.dirname(__file__), 'gui', 'interface.kv'))


class MainScreen(BoxLayout):
    """Tela principal com navegação entre extrator e compressor."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extractor = PDFTextExtractor()
        self.compressor = PDFCompressor()
    
    def show_extractor(self):
        """Mostra tela de extração."""
        self.ids.screen_manager.current = 'extractor'
    
    def show_compressor(self):
        """Mostra tela de compressão."""
        self.ids.screen_manager.current = 'compressor'


class PDFToolsApp(App):
    """Aplicação principal PDF Tools."""
    
    def build(self):
        """Configura e retorna a aplicação."""
        self.title = 'PDF Tools - Extrator & Compressor'
        
        # Configura ScreenManager
        sm = ScreenManager(transition=SlideTransition())
        
        # Cria tela principal
        main_screen = MainScreen()
        sm.add_widget(main_screen)
        
        # Configura injeção de dependências nas telas
        extractor_screen = sm.get_screen('extractor')
        compressor_screen = sm.get_screen('compressor')
        
        extractor_screen.extractor = self.extractor
        compressor_screen.compressor = self.compressor
        
        return sm
    
    def on_start(self):
        """Executado quando a aplicação inicia."""
        import logging
        logging.info('PDF Tools iniciado')


def main():
    """Função principal para executar a aplicação."""
    PDFToolsApp().run()


if __name__ == '__main__':
    main()
