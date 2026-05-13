# PDF Tools - Suite de Ferramentas para PDF

[![Version](https://img.shields.io/badge/version-2.3.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Uma aplicação moderna e modular para manipulação de PDFs com interface gráfica CustomTkinter, oferecendo extração de texto, compressão, divisão, mesclagem, limpeza de arquivos e extração de imagens.

## ✨ Funcionalidades

- 📄 **Extrator de Texto**: Converta PDFs para TXT mantendo formatação
- 🗜️ **Compressor de PDF**: Reduza tamanho com 3 níveis de compressão
- ✂️ **Dividir PDF**: Extraia páginas individuais ou intervalos com preview visual
- 📑 **Mesclar PDFs**: Junte múltiplos PDFs com reordenação e preview
- 🧹 **Limpar Arquivos**: Limpeza de .txt, .md, .docx com 12 técnicas + encoding
- 🖼️ **Extrair Imagens**: Extraia imagens em PNG, JPG, TIFF com metadados
- 🎨 **Interface Moderna**: Tema escuro premium com widgets customizados
- 🚀 **Streaming**: Processa arquivos grandes (>50MB) sem vazamento de memória
- 📊 **Preview Universal**: Visualize conteúdo antes de processar
- 🔒 **Validação Robusta**: Verifica integridade do PDF antes de processar
- 🎭 **ThemeManager**: Alternância instantânea entre temas claro/escuro com persistência
- 🧩 **Widgets Reutilizáveis**: 12 componentes padronizados (W01-W12) para consistência visual

## REQUISITOS

### Python
- **Versão mínima:** Python 3.8
- **Versão recomendada:** Python 3.10 ou superior

### Bibliotecas
Instale as dependências necessárias executando:

```bash
pip install customtkinter pdfplumber PyMuPDF Pillow python-docx PyPDF2
```

Ou, se preferir usar um arquivo de requisitos:
```text
customtkinter>=5.2.0
pdfplumber>=0.10.0
PyMuPDF>=1.23.0
Pillow>=10.0.0
python-docx>=0.8.11
PyPDF2>=3.0.0
```

**Descrição das bibliotecas:**
- **customtkinter**: Framework GUI moderno com temas automático claro/escuro
- **pdfplumber**: Extração precisa de texto de PDFs
- **PyMuPDF (fitz)**: Manipulação, compressão, divisão e extração de imagens de PDFs
- **Pillow**: Processamento de imagens para thumbnails e conversão de formatos
- **python-docx**: Leitura e manipulação de arquivos .docx (Word)
- **PyPDF2**: Mesclagem de PDFs com preservação de bookmarks

## 🧩 Widgets Reutilizáveis (W01-W12)

A partir da versão 2.3.0, o projeto inclui uma biblioteca de widgets reutilizáveis para acelerar o desenvolvimento de interfaces consistentes e manter a qualidade visual.

### Lista de Widgets

| ID | Widget | Descrição | Uso Principal |
|----|--------|-----------|---------------|
| **W01** | `NumericEntryPair` | Par Label + Entry Numérico com botões +/- | Configuração de valores numéricos (ex: nível de compressão) |
| **W02** | `TooltipCheckbox` | Checkbox com tooltip explicativo | Opções com descrição adicional |
| **W03** | `FormatSelector` | Seletor de Formato (Combobox) | Seleção de formatos de saída (PDF, TXT, PNG, etc.) |
| **W04** | `FilePickerButton` | Botão de Arquivo (File Picker) | Seleção de arquivos/diretórios com path display |
| **W05** | `SectionSeparator` | Separador Seccional com Título | Divisão visual de seções no layout |
| **W06** | `DynamicStatusArea` | Área de Status Dinâmico | Mensagens de status com ícone e cor dinâmica |
| **W07** | `MetadataGrid` | Grid de Metadados (Read-only) | Exibição de metadados chave-valor |
| **W08** | `ValueSlider` | Slider com Valor Visível | Controle deslizante com valor em tempo real |
| **W09** | `ClearListButton` | Botão de Limpar Lista | Limpeza de listas com confirmação opcional |
| **W10** | `ProcessingIndicator` | Indicador de "Processando..." | Feedback visual de processamento animado |
| **W11** | `SummaryCard` | Card de Resumo Final | Estatísticas de operação concluída |
| **W12** | `SmartIntervalInput` | Input de Intervalo Inteligente | Entrada de intervalos (ex: 1-10, 1,2,3) com validação |

### Como Usar os Widgets

```python
from gui_tkinter.widgets import (
    NumericEntryPair,      # W01
    TooltipCheckbox,       # W02
    FormatSelector,        # W03
    FilePickerButton,      # W04
    SectionSeparator,      # W05
    DynamicStatusArea,     # W06
    MetadataGrid,          # W07
    ValueSlider,           # W08
    ClearListButton,       # W09
    ProcessingIndicator,   # W10
    SummaryCard,           # W11
    SmartIntervalInput,    # W12
)

# Exemplo: W01 - Entry Numérico
numeric_input = NumericEntryPair(
    master=frame,
    label_text="Nível de Compressão",
    default_value=5,
    min_value=1,
    max_value=10,
    command=lambda v: print(f"Valor: {v}")
)

# Exemplo: W12 - Intervalo Inteligente
interval_input = SmartIntervalInput(
    master=frame,
    label_text="Páginas para Extrair",
    min_value=1,
    max_value=100,
    command=lambda pages: process_pages(pages)
)
```

### Benefícios da Componentização

✅ **Redução de Código Repetitivo**: Widgets prontos para uso em múltiplas tabs  
✅ **Consistência Visual**: Padrão estético uniforme em toda interface  
✅ **Manutenção Simplificada**: Mudanças em um widget refletem em todos usos  
✅ **Documentação Integrada**: Cada widget tem docstrings detalhadas  
✅ **Testabilidade**: Componentes isolados facilitam testes unitários

## 🎨 ThemeManager - Temas Claro/Escuro

A partir da versão 2.3.0, o projeto inclui um sistema completo de gerenciamento de temas com alternância instantânea entre modo claro e escuro.

### Recursos Principais

✅ **Alternância Instantânea**: Toggle entre temas sem reiniciar a aplicação  
✅ **Persistência Automática**: Preferência salva em `~/.pdf_tools/theme_config.json`  
✅ **Cobertura Total**: CustomTkinter + widgets nativos Tkinter  
✅ **Paletas Centralizadas**: 24+ cores configuráveis via `ColorPalette`  
✅ **Atualização Automática**: Componentes registrados são atualizados em tempo real  
✅ **Singleton Global**: Acesso via `get_theme_manager()`  

### Como Usar

```python
from gui_tkinter import (
    get_theme_manager,
    ThemeManager,
    DARK_PALETTE,
    LIGHT_PALETTE,
    apply_theme_to_widget,
)

# Obter instância singleton
theme_mgr = get_theme_manager()

# Alternar tema (claro <-> escuro)
novo_tema = theme_mgr.toggle_theme()
print(f"Tema atual: {novo_tema}")  # 'dark' ou 'light'

# Definir tema específico
theme_mgr.set_theme("dark")

# Acessar cores do tema atual
bg_color = theme_mgr.get_color("primary_bg")
accent = theme_mgr.get_color("accent_color")

# Registrar componente para atualização automática
theme_mgr.register_component(my_frame, callback=lambda t: print(f"Tema: {t}"))

# Criar botão de toggle pré-configurado
toggle_btn = theme_mgr.create_theme_toggle_button(
    master=header_frame,
    command=lambda: print("Tema alterado!")
)

# Aplicar tema manualmente a um widget
apply_theme_to_widget(my_widget, theme_mgr)
```

### Paletas de Cores

**Modo Escuro (`DARK_PALETTE`):**
- Fundo: `#1E1E1E` (cinza muito escuro)
- Frames: `#2D2D2D` (cinza escuro)
- Cards: `#383838` (cinza médio)
- Texto: `#FFFFFF` (branco)
- Accent: `#64B5F6` (azul claro)
- Borda: `#404040` (cinza escuro)

**Modo Claro (`LIGHT_PALETTE`):**
- Fundo: `#FFFFFF` (branco)
- Frames: `#F5F5F5` (cinza muito claro)
- Cards: `#FFFFFF` (branco)
- Texto: `#1A1A1A` (preto suave)
- Accent: `#2196F3` (azul Material Design)
- Borda: `#E0E0E0` (cinza claro)

### Integração na Interface

Para adicionar toggle de tema na sua aplicação:

```python
import customtkinter as ctk
from gui_tkinter import get_theme_manager

class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Obtém gerenciador de temas
        self.theme_mgr = get_theme_manager()
        
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=10, pady=5)
        
        # Título
        title = ctk.CTkLabel(header, text="PDF Tools")
        title.pack(side="left", padx=10)
        
        # Botão de toggle de tema
        theme_btn = self.theme_mgr.create_theme_toggle_button(
            master=header,
            command=self._on_theme_changed
        )
        theme_btn.pack(side="right", padx=10)
    
    def _on_theme_changed(self):
        print(f"Tema alterado para: {self.theme_mgr.current_theme}")

# Executar
app = MyApp()
app.mainloop()
```

### Persistência

O ThemeManager automaticamente:
- **Salva** preferência ao alternar temas
- **Carrega** preferência ao iniciar aplicação
- **Local**: `~/.pdf_tools/theme_config.json`
- **Formato**: JSON simples `{"theme": "dark"}`

### API Completa

| Método | Descrição | Retorna |
|--------|-----------|---------|
| `get_theme_manager()` | Singleton global | `ThemeManager` |
| `toggle_theme()` | Alterna claro/escuro | `str` (novo tema) |
| `set_theme(theme)` | Define tema específico | `None` |
| `get_color(name)` | Obtém cor por nome | `str` (hex) |
| `get_all_colors()` | Todas as cores | `Dict[str, str]` |
| `register_component(widget, cb)` | Registra componente | `None` |
| `unregister_component(widget)` | Remove componente | `None` |
| `create_theme_toggle_button(master, cmd)` | Cria botão toggle | `CTkButton` |

## COMO EXECUTAR

1. **Clone ou navegue até o diretório do projeto:**
   ```bash
   cd /workspace
   ```

2. **Instale as dependências:**
   ```bash
   pip install customtkinter pdfplumber PyMuPDF Pillow
   ```

3. **Execute a aplicação:**
   ```bash
   python gui_tkinter/app.py
   ```

4. **A interface moderna será aberta** com 6 abas:
   - 📄 **Extrair**: Extração de texto de PDFs
   - 🗜️ **Comprimir**: Redução de tamanho de PDFs
   - ✂️ **Dividir**: Separação de páginas com preview
   - 📑 **Mesclar**: Juntar múltiplos PDFs com reordenação
   - 🧹 **Limpar**: Limpeza de arquivos .txt, .md, .docx
   - 🖼️ **Extrair Imagens**: Extração de imagens do PDF

## COMO USAR

### 📄 Extrator de Texto (PDF → TXT)

1. Clique na aba **"📄 Extrair"**
2. Arraste PDFs para a drop zone OU clique em **"Selecionar Arquivos"**
3. Visualize o preview do conteúdo antes de processar
4. Escolha a pasta de destino (opcional)
5. Clique em **"Extrair Texto"**
6. Acompanhe o progresso página por página
7. Resultado salvo em UTF-8 com numeração de páginas

### 🗜️ Compressor de PDF

1. Clique na aba **"🗜️ Comprimir"**
2. Selecione os PDFs para comprimir
3. Escolha o nível de compressão:
   - **Baixa:** ~30% redução, qualidade máxima
   - **Média:** ~50% redução, equilíbrio ideal ⭐
   - **Alta:** ~70% redução, qualidade reduzida
4. Visualize preview antes de comprimir
5. Clique em **"Comprimir PDFs"**
6. Veja economia de espaço em tempo real

### ✂️ Dividir PDF (Avançado!)

**Modo Básico:**
1. Clique na aba **"✂️ Dividir"**
2. Selecione um PDF para dividir
3. **Preview automático**: Veja thumbnails de todas páginas
4. Escolha o modo de divisão:
   - **Páginas individuais**: Cada página vira um PDF separado
   - **Intervalo**: Extraia páginas X-Y em um único PDF
5. Selecione páginas com checkboxes OU defina intervalo
6. Clique em **"Dividir PDF"**
7. Arquivos salvos com numeração automática

**Modo Avançado (Backend Service):**
- **Split por bookmarks**: Divide automaticamente pelos bookmarks/TOC do PDF
- **Split por intervalos**: Lista customizada [(1,3), (5,7), ...]
- **Páginas pares/ímpares**: Extrai apenas páginas pares ou ímpares
- **Páginas específicas**: Lista customizada [1, 3, 5, 7, ...]

### 📑 Mesclar PDFs (NOVO!)

1. Clique na aba **"📑 Mesclar"**
2. Arraste múltiplos PDFs OU clique em **"Selecionar Arquivos"**
3. **Preview visual**: Veja nome, nº de páginas e tamanho de cada arquivo
4. **Reordene** com botões ↑↓ (qualquer ordem desejada)
5. Remova arquivos indesejados individualmente
6. Configure opções:
   - ✅ Manter bookmarks originais
   - ✅ Comprimir resultado final
   - ✅ Adicionar separadores entre arquivos
7. Clique em **"Mesclar PDFs"**
8. Resultado salvo como `{primeiro}_mesclado_{timestamp}.pdf`

### 🧹 Limpar Arquivos (NOVO!)

1. Clique na aba **"🧹 Limpar"**
2. Arraste arquivos .txt, .md ou .docx
3. Clique em **"✨ Limpar"**
4. **Processamento automático em 2 etapas**:
   - **Etapa 1**: `EncodingDetector` corrige encoding (utf-8, latin-1, cp1252)
   - **Etapa 2**: `TextCleaner` aplica 12 técnicas de limpeza
5. Resultado salvo como `{nome}_limpo.{ext}` no mesmo diretório

**Técnicas de limpeza aplicadas:**
1. Remoção de BOM (Byte Order Mark)
2. Normalização CRLF → LF
3. Espaços múltiplos (preservando code blocks)
4. Trailing whitespace
5. Linhas em branco excessivas (máx 2 consecutivas)
6. Espaço antes de pontuação
7. Headers Markdown normalizados
8. Negrito/itálico sem espaços extras
9. Detecção de links vazios
10. Listas Markdown padronizadas
11. Hífens/traços normalizados
12. Newline final único

### 🖼️ Extrair Imagens (NOVO!)

1. Clique na aba **"🖼️ Extrair Imagens"** (implementação futura)
2. Selecione um PDF contendo imagens
3. Escolha o formato de saída: PNG, JPG ou TIFF
4. Opcional: Configure redimensionamento
5. Clique em **"Extrair Imagens"**
6. Imagens salvas em pasta organizada: `{nome}_imagens_{timestamp}/`
7. Nomes sequenciais: `imagem_0001.png`, `imagem_0002.png`, ...
8. Metadados extraídos em `metadados_imagens.json`

## FUNCIONALIDADES

### Gerais
- **Interface Unificada**: 3 tabs organizadas em layout responsivo
- **Tema Escuro Moderno**: Paleta profissional com widgets customizados
- **Processamento em Lote**: Múltiplos arquivos simultaneamente
- **Logs Detalhados**: Painel com status de cada operação
- **Validação Automática**: Verifica PDFs antes de processar
- **Design Responsivo**: Adaptável a diferentes telas
- **Drop Zones**: Drag-and-drop intuitivo
- **Preview Universal**: Visualize antes de processar

### 📄 Extrator de Texto
- **Alta Qualidade**: `pdfplumber` preserva estrutura do texto
- **UTF-8**: Suporte completo a caracteres especiais
- **Múltiplas Páginas**: Concatenação automática
- **Numeração**: Indica página de origem no resultado
- **Streaming**: Processa arquivos >50MB sem travar

### 🗜️ Compressor de PDF
- **3 Níveis**: Baixa, Média (⭐), Alta compressão
- **Economia Visível**: Mostra % de redução
- **Qualidade Preservada**: Otimização inteligente
- **Metadados**: Remove dados desnecessários

### ✂️ Dividir PDF (Avançado!)
- **Preview Visual**: Thumbnails de todas páginas
- **Seleção Flexível**: Checkboxes individuais
- **Modo Intervalo**: Extraia páginas X-Y
- **Páginas Individuais**: Cada página = PDF separado
- **Nomeação Auto**: Arquivos numerados sequencialmente
- **Split por Bookmarks**: Divide automaticamente pelos bookmarks/TOC
- **Split por Intervalos**: Lista customizada [(1,3), (5,7), ...]
- **Páginas Pares/Ímpares**: Extrai apenas páginas pares ou ímpares

### 📑 Mesclar PDFs (NOVO!)
- **Seleção Múltipla**: Drag-and-drop de vários PDFs
- **Preview Visual**: Nome, nº páginas, tamanho de cada arquivo
- **Reordenação Flexível**: Botões ↑↓ para qualquer ordem
- **Remoção Individual**: Remove arquivos da lista
- **Opções Configuráveis**: Bookmarks, compressão, separadores
- **Processamento em Thread**: Barra de progresso com feedback
- **Salvamento Automático**: `{primeiro}_mesclado_{timestamp}.pdf`

### 🧹 Limpar Arquivos (NOVO!)
- **EncodingDetector Inteligente**: Detecta e corrige encoding automaticamente
- **TextCleaner com 12 Técnicas**: Limpeza completa de formatação
- **Suporte Multi-formato**: .txt, .md, .docx
- **Degradação Zero**: Preserva code blocks e formatação essencial
- **Intervenção Mínima**: Apenas correções necessárias
- **Pipeline Automático**: Encoding → Limpeza → Salvamento

### 🖼️ Extrair Imagens (NOVO!)
- **Extração Completa**: Todas imagens do PDF
- **Múltiplos Formatos**: PNG, JPG, TIFF
- **Nomes Sequenciais**: `imagem_0001.png`, `imagem_0002.png`, ...
- **Metadados Detalhados**: DPI, dimensões, página original, colorspace
- **Arquivo JSON**: `metadados_imagens.json` com informações completas
- **Redimensionamento Opcional**: Mantém resolução original ou ajusta
- **Pasta Organizada**: `{nome}_imagens_{timestamp}/`

### 🔜 Em Planejamento (v2.4+)

**Fila de Processamento e Componentização:**
- **TaskQueueService**: Fila de processamento inteligente com prioridades e cancelamento
- **PreviewEngine**: Pré-visualização inteligente com estimativas de tamanho e tempo
- **BaseProcessTab**: Classe base para padronizar ciclo de vida das tabs
- **Componentes de Interface**: Barra de progresso unificada, painel de configs, área de logs
- **Correções**: Melhorias no drag-and-drop e ordenação na mesclagem

**Funcionalidades Avançadas:**
- **Interface GUI**: Implementar tabs "Extrair Imagens" e "Dividir Avançado"
- **OCR Integrado**: Tesseract para PDFs escaneados
- **Marca D'água**: Adicionar logos/textos
- **Criptografia**: Proteger com senha
- **PDF ↔ Word**: Conversão bidirecional completa

## ESTRUTURA DE ARQUIVOS

Arquitetura em camadas para máxima manutenibilidade e testabilidade:

```
/workspace/
├── main.py                     # Legacy (Kivy) - manter para referência
├── README.md                   # Esta documentação
├── requirements.txt            # Dependências do projeto
│
├── config.py                   # Configuração centralizada (temas, cores, paths)
├── logger.py                   # Sistema de logging com rotação
│
├── gui_tkinter/                # Interface Moderna (CustomTkinter)
│   ├── app.py                  # Aplicação principal com tabs
│   ├── widgets.py              # Componentes customizados
│   └── dialogs.py              # Diálogos reutilizáveis
│
├── core/                       # Camada de Domínio
│   ├── services/               # Serviços de Negócio
│   │   ├── extractor_service.py    # Extração de texto
│   │   ├── compressor_service.py   # Compressão de PDFs
│   │   ├── pdf_splitter.py         # Divisão de PDFs (páginas, bookmarks, intervalos)
│   │   ├── pdf_merger.py           # Mesclagem de PDFs com reordenação
│   │   ├── cleaner_service.py      # Limpeza de .txt, .md, .docx (12 técnicas + encoding)
│   │   └── image_extractor.py      # Extração de imagens (PNG, JPG, TIFF)
│   ├── validators/             # Validações
│   │   └── pdf_validator.py        # Validação robusta de PDFs
│   └── models/                 # Modelos de Dados
│       └── __init__.py
│
├── docs/                       # Documentação Completa
│   ├── CHANGELOG.md            # Histórico de versões
│   ├── BACKLOG.md              # Backlog do produto
│   ├── PLANO_REFACTORY.md      # Plano de arquitetura
│   ├── RESUMO_REFACTORY.md     # Resumo executivo
│   └── AUDITORIA_COMPLETA.md   # Auditoria de código
│
└── logs/                       # Logs da aplicação (auto-criado)
    └── pdf_tools.log
```

### Camadas da Arquitetura

| Camada | Responsabilidade | Módulos |
|--------|-----------------|---------|
| **Apresentação** | UI/UX, eventos, feedback visual | `gui_tkinter/` |
| **Serviços** | Lógica de negócio, orquestração | `core/services/` |
| **Domínio** | Entidades, modelos, regras | `core/models/` |
| **Infraestrutura** | Validações, logging, config | `core/validators/`, `config.py`, `logger.py` |

### Princípios de Design

- ✅ **SOLID**: Separação clara de responsabilidades
- ✅ **Injeção de Dependência**: Serviços injetados na GUI
- ✅ **Baixo Acoplamento**: Core independente de GUI
- ✅ **Alta Coesão**: Módulos com propósito único
- ✅ **Streaming**: Processamento eficiente de grandes arquivos

---

**Licença:** Uso livre para fins educacionais e pessoais.
**Autor:** Gerado via IA com base em solicitação de refatoração.
