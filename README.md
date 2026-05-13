# PDF Tools - Suite de Ferramentas para PDF

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Uma aplicação moderna e modular para manipulação de PDFs com interface gráfica CustomTkinter, oferecendo extração de texto, compressão e divisão de arquivos PDF com preview visual.

## ✨ Funcionalidades

- 📄 **Extrator de Texto**: Converta PDFs para TXT mantendo formatação
- 🗜️ **Compressor de PDF**: Reduza tamanho com 3 níveis de compressão
- ✂️ **Dividir PDF**: Extraia páginas individuais ou intervalos com preview visual
- 🎨 **Interface Moderna**: Tema escuro premium com widgets customizados
- 🚀 **Streaming**: Processa arquivos grandes (>50MB) sem vazamento de memória
- 📊 **Preview Universal**: Visualize conteúdo antes de processar
- 🔒 **Validação Robusta**: Verifica integridade do PDF antes de processar

## REQUISITOS

### Python
- **Versão mínima:** Python 3.8
- **Versão recomendada:** Python 3.10 ou superior

### Bibliotecas
Instale as dependências necessárias executando:

```bash
pip install customtkinter pdfplumber PyMuPDF Pillow
```

Ou, se preferir usar um arquivo de requisitos:
```text
customtkinter>=5.2.0
pdfplumber>=0.10.0
PyMuPDF>=1.23.0
Pillow>=10.0.0
```

**Descrição das bibliotecas:**
- **customtkinter**: Framework GUI moderno com temas automático claro/escuro
- **pdfplumber**: Extração precisa de texto de PDFs
- **PyMuPDF (fitz)**: Manipulação, compressão e divisão de PDFs
- **Pillow**: Processamento de imagens para thumbnails de preview

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

4. **A interface moderna será aberta** com 3 abas:
   - 📄 **Extrair**: Extração de texto de PDFs
   - 🗜️ **Comprimir**: Redução de tamanho de PDFs
   - ✂️ **Dividir**: Separação de páginas com preview

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

### ✂️ Dividir PDF (NOVO!)

1. Clique na aba **"✂️ Dividir"**
2. Selecione um PDF para dividir
3. **Preview automático**: Veja thumbnails de todas páginas
4. Escolha o modo de divisão:
   - **Páginas individuais**: Cada página vira um PDF separado
   - **Intervalo**: Extraia páginas X-Y em um único PDF
5. Selecione páginas com checkboxes OU defina intervalo
6. Clique em **"Dividir PDF"**
7. Arquivos salvos com numeração automática

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

### ✂️ Dividir PDF (NOVO!)
- **Preview Visual**: Thumbnails de todas páginas
- **Seleção Flexível**: Checkboxes individuais
- **Modo Intervalo**: Extraia páginas X-Y
- **Páginas Individuais**: Cada página = PDF separado
- **Nomeação Auto**: Arquivos numerados sequencialmente

### 🔜 Em Planejamento (v2.2+)
- **OCR Integrado**: Tesseract para PDFs escaneados
- **Merge**: Juntar múltiplos PDFs
- **Marca D'água**: Adicionar logos/textos
- **Criptografia**: Proteger com senha
- **PDF ↔ Word**: Conversão bidirecional

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
│   │   └── splitter_service.py     # Divisão de PDFs (NOVO)
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
