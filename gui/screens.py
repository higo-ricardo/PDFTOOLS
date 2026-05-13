"""
Telas da interface gráfica Kivy para PDF Tools.
"""

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import BooleanProperty
import logging

logger = logging.getLogger(__name__)


class ExtractorScreen(Screen):
    """Tela de extração de texto de PDFs."""
    
    has_text = BooleanProperty(False)
    selected_files = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extractor = None  # Será injetado
    
    def select_files(self):
        """Abre diálogo para seleção de arquivos."""
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.popup import Popup
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical')
        
        file_chooser = FileChooserListView(
            path='/',
            filters=['*.pdf'],
            multiselect=True
        )
        
        button_layout = BoxLayout(size_hint_y=None, height=50)
        
        select_btn = Button(text='Selecionar')
        cancel_btn = Button(text='Cancelar')
        
        def do_select(instance):
            self.selected_files = file_chooser.selection
            popup.dismiss()
            
            if self.selected_files:
                self.ids.process_btn.disabled = False
                self.ids.status_label.text = f'{len(self.selected_files)} arquivo(s) selecionado(s)'
                logger.info(f'{len(self.selected_files)} arquivos selecionados')
        
        def do_cancel(instance):
            popup.dismiss()
        
        select_btn.bind(on_release=do_select)
        cancel_btn.bind(on_release=do_cancel)
        
        button_layout.add_widget(select_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(file_chooser)
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Selecione os PDFs',
            content=content,
            size_hint=(0.9, 0.9)
        )
        popup.open()
    
    def start_extraction(self):
        """Inicia a extração de texto."""
        if not self.selected_files:
            self.ids.status_label.text = 'Nenhum arquivo selecionado'
            return
        
        self.ids.process_btn.disabled = True
        self.ids.select_btn.disabled = True
        self.ids.progress_bar.value = 0
        self.ids.result_text.text = ''
        self.ids.status_label.text = 'Processando...'
        
        # Processa em thread separada
        from threading import Thread
        Thread(target=self._process_files, daemon=True).start()
    
    def _process_files(self):
        """Processa os arquivos em segundo plano."""
        try:
            if not self.extractor:
                raise Exception("Extrator não configurado")
            
            total = len(self.selected_files)
            processed_text = ""
            
            for i, file_path in enumerate(self.selected_files, 1):
                text, status = self.extractor.extract_from_file_path(file_path)
                
                if status == "erro":
                    Clock.schedule_once(
                        lambda dt: self._show_error(text), 0
                    )
                    return
                
                from pathlib import Path
                filename = Path(file_path).stem
                processed_text += f"► {filename}\n{text}\n\n"
                
                # Atualiza progresso
                progress = int((i / total) * 100)
                Clock.schedule_once(
                    lambda dt, p=progress: self._update_progress(p), 0
                )
            
            # Atualiza UI com resultado
            Clock.schedule_once(
                lambda dt: self._finish_extraction(processed_text), 0
            )
            
        except Exception as e:
            Clock.schedule_once(
                lambda dt: self._show_error(f'Erro: {str(e)}'), 0
            )
    
    def _update_progress(self, value):
        """Atualiza barra de progresso."""
        self.ids.progress_bar.value = value
    
    def _finish_extraction(self, text):
        """Finaliza extração e mostra resultado."""
        self.ids.result_text.text = text
        self.ids.status_label.text = 'Processamento concluído!'
        self.ids.process_btn.disabled = False
        self.ids.select_btn.disabled = False
        self.has_text = True
        logger.info('Extração concluída com sucesso')
    
    def _show_error(self, message):
        """Mostra mensagem de erro."""
        self.ids.status_label.text = f'Erro: {message}'
        self.ids.process_btn.disabled = False
        self.ids.select_btn.disabled = False
        self.ids.progress_bar.value = 0
        logger.error(message)
    
    def save_results(self):
        """Salva resultados em arquivo."""
        if not self.has_text:
            return
        
        from kivy.uix.popup import Popup
        from kivy.uix.filechooser import FileChooserSaveDialog
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical')
        
        file_chooser = FileChooserSaveDialog(
            path='/',
            filters=['*.txt']
        )
        
        button_layout = BoxLayout(size_hint_y=None, height=50)
        save_btn = Button(text='Salvar')
        cancel_btn = Button(text='Cancelar')
        
        def do_save(instance):
            save_path = file_chooser.selection[0] if file_chooser.selection else None
            
            if save_path:
                if not save_path.endswith('.txt'):
                    save_path += '.txt'
                
                try:
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(self.ids.result_text.text)
                    
                    popup.dismiss()
                    self.ids.status_label.text = f'Arquivo salvo: {save_path}'
                    logger.info(f'Resultado salvo em {save_path}')
                except Exception as e:
                    self.ids.status_label.text = f'Erro ao salvar: {str(e)}'
                    logger.error(f'Erro ao salvar: {str(e)}')
            else:
                popup.dismiss()
        
        def do_cancel(instance):
            popup.dismiss()
        
        save_btn.bind(on_release=do_save)
        cancel_btn.bind(on_release=do_cancel)
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(file_chooser)
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Salvar resultado',
            content=content,
            size_hint=(0.9, 0.9)
        )
        popup.open()


class CompressorScreen(Screen):
    """Tela de compressão de PDFs."""
    
    file_selected = BooleanProperty(False)
    file_path = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.compressor = None  # Será injetado
    
    def select_file(self):
        """Abre diálogo para seleção de arquivo."""
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.popup import Popup
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical')
        
        file_chooser = FileChooserListView(
            path='/',
            filters=['*.pdf'],
            multiselect=False
        )
        
        button_layout = BoxLayout(size_hint_y=None, height=50)
        select_btn = Button(text='Selecionar')
        cancel_btn = Button(text='Cancelar')
        
        def do_select(instance):
            selection = file_chooser.selection
            popup.dismiss()
            
            if selection:
                self.file_path = selection[0]
                self.file_selected = True
                self._update_file_info()
                logger.info(f'Arquivo selecionado: {self.file_path}')
        
        def do_cancel(instance):
            popup.dismiss()
        
        select_btn.bind(on_release=do_select)
        cancel_btn.bind(on_release=do_cancel)
        
        button_layout.add_widget(select_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(file_chooser)
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Selecione um PDF',
            content=content,
            size_hint=(0.9, 0.9)
        )
        popup.open()
    
    def _update_file_info(self):
        """Atualiza informações do arquivo selecionado."""
        if not self.file_path or not self.compressor:
            return
        
        info = self.compressor.get_file_info(self.file_path)
        
        if 'error' in info:
            self.ids.file_info_label.text = '[color=ff3333]Erro ao ler arquivo[/color]'
            self.file_selected = False
        else:
            from utils.helpers import format_file_size
            self.ids.file_info_label.text = (
                f"[b]📄 Arquivo:[/b] {info['filename']}\n"
                f"[b]📊 Tamanho:[/b] {format_file_size(int(info['size_bytes']))} | "
                f"[b]📑 Páginas:[/b] {info['pages']}"
            )
            self.file_selected = True
    
    def compress_pdf(self):
        """Inicia compressão do PDF."""
        if not self.file_path:
            self.ids.status_label.text = '[color=ff3333]⚠️ Selecione um arquivo primeiro![/color]'
            return
        
        self.ids.compress_btn.disabled = True
        self.ids.progress_bar.value = 0
        self.ids.status_label.text = 'Comprimindo...'
        
        compression_level = self.ids.compression_spinner.text
        
        from threading import Thread
        Thread(
            target=self._do_compress,
            args=(compression_level,),
            daemon=True
        ).start()
    
    def _do_compress(self, compression_level):
        """Executa compressão em segundo plano."""
        try:
            if not self.compressor:
                raise Exception("Compressor não configurado")
            
            result_path, status = self.compressor.compress_pdf(
                self.file_path,
                compression_level
            )
            
            if status == "sucesso":
                # Calcula redução
                original_size = os.path.getsize(self.file_path)
                compressed_size = os.path.getsize(result_path)
                reduction = ((original_size - compressed_size) / original_size) * 100
                
                Clock.schedule_once(
                    lambda dt: self._finish_compress(result_path, reduction), 0
                )
            else:
                Clock.schedule_once(
                    lambda dt: self._show_error(result_path), 0
                )
                
        except Exception as e:
            Clock.schedule_once(
                lambda dt: self._show_error(f'Erro: {str(e)}'), 0
            )
    
    def _finish_compress(self, result_path, reduction):
        """Finaliza compressão e mostra resultado."""
        self.ids.result_label.text = (
            f"[color=33ff33][b]✅ PDF comprimido com sucesso![/b][/color]\n\n"
            f"[b]📁 Salvo em:[/b] {result_path}\n"
            f"[b]📉 Redução:[/b] {reduction:.1f}%"
        )
        self.ids.status_label.text = '[color=33ff33]Concluído![/color]'
        self.ids.compress_btn.disabled = False
        self.ids.progress_bar.value = 100
        logger.info(f'Compressão concluída: {reduction:.1f}% de redução')
    
    def _show_error(self, message):
        """Mostra mensagem de erro."""
        self.ids.status_label.text = f'[color=ff3333]❌ {message}[/color]'
        self.ids.compress_btn.disabled = False
        self.ids.progress_bar.value = 0
        logger.error(message)


# Import necessário para _do_compress
import os
