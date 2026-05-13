# CHANGELOG

Todas as mudanças significativas neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto segue o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.1.0] - 2024 - Interface Moderna e Funcionalidade DividirPDF

### ✨ Adicionado

#### Nova Funcionalidade: Divisão de PDF com Preview
- **DividirPDF completo**: Converte cada página em PDF individual OU extrai intervalos
- **Preview visual avançado**: Grid de thumbnails com renderização de todas páginas
- **Seleção flexível**: 
  - Checkbox individual por página
  - Modo "Selecionar Todos/Nenhum"
  - Modo intervalo (página inicial-final)
- **Extração inteligente**: 
  - Páginas selecionadas → PDFs individuais
  - Intervalo → Único PDF com páginas sequenciais
- **Feedback em tempo real**: Status mostra página sendo processada

#### Interface CustomTkinter Premium
- **Tema escuro moderno**: Paleta profissional (#1e1e1e, #2d2d2d, #2196F3)
- **Botões arredondados**: Corner radius 12px com efeitos hover suaves
- **Cards com sombra**: ShadowFrame para elevação visual 3D
- **Drop zones interativas**: Drag-and-drop com feedback visual dinâmico
- **Layout responsivo**: Tabs organizadas (Extrair, Comprimir, Dividir)
- **Widgets customizados**:
  - `ModernButton`: Botão com gradiente e animações
  - `PreviewCard`: Card de preview com thumbnail e número
  - `ProgressCard`: Barra de progresso integrada com status
  - `DropZoneFrame`: Zona de drop com borda animada
  - `ShadowFrame`: Frame base com efeito de sombra
- **Preview universal**: Todas funcionalidades mostram preview antes de processar
- **Toasts notificações**: Mensagens flutuantes com ícones (✅ ❌ ⚠️)

#### Streaming Avançado
- **Processamento híbrido**: 
  - Arquivos <50MB: Carregamento completo (mais rápido)
  - Arquivos ≥50MB: Streaming página-a-página (economia de memória)
- **Threshold configurável**: Via config.py (`processing.streaming_threshold_mb`)
- **Garbage collection inteligente**: Libera memória a cada 10 páginas
- **Status detalhado**: "Processando página X de Y" na barra de status

#### Injeção de Dependência
- **Serviços injetáveis**: GUI recebe serviços via construtor
- **Protocolos definidos**: Interfaces para ExtractorService, CompressorService
- **Baixo acoplamento**: GUI não importa módulos core diretamente
- **Testabilidade máxima**: Mock de serviços em testes unitários

### 🔧 Modificado

#### Correções Críticas Implementadas
- ✅ **Lambdas em loops**: Todas capturam variáveis corretamente com defaults
- ✅ **Logging de exceptions**: 100% dos catches usam `logger.exception()`
- ✅ **Validação prévia**: PDF validado antes de qualquer processamento
- ✅ **Stack traces completos**: Logs incluem traceback completo

#### Melhorias de UX
- 🎨 **Feedback visual rico**: 
  - Nome do arquivo sendo processado
  - Página atual em operações longas
  - Porcentagem de progresso visível
- 🚀 **Performance**: 
  - Preview assíncrono (não bloqueia UI)
  - Cache de thumbnails geradas
  - Lazy loading para PDFs >100 páginas

#### Arquitetura
- 🏗️ **Separação total**: 
  - `gui_tkinter/`: Apenas apresentação
  - `core/services/`: Lógica de negócio pura
  - `core/models/`: Estruturas de dados
  - `core/validators/`: Validações
- 📦 **Módulos independentes**: Cada serviço em arquivo separado

### 📦 Dependências

```txt
customtkinter>=5.2.0
Pillow>=10.0.0
pdfplumber>=0.10.0
PyMuPDF>=1.23.0
```

### 🗑️ Removido
- **Kivy**: Migração 100% completa
- **interface.kv**: Obsoleto
- **gui/screens.py**: Substituído por tabs CustomTkinter

---

## [2.0.0] - 2024 - Refatoração Completa com Arquitetura em Camadas

### ✨ Adicionado

#### Nova Funcionalidade: Divisão de PDF
- **DividirPDF**: Converte cada página do PDF em um novo PDF individual
- **Extrair intervalo**: Separa páginas específicas ou intervalos de páginas
- **Preview visual**: Grid de thumbnails com seleção individual de páginas
- **Seleção múltipla**: Checkbox para selecionar/deselecionar páginas
- **Modo intervalo**: Extrai faixa contínua de páginas em um único arquivo

#### Interface Moderna CustomTkinter
- **Tema escuro profissional**: Paleta de cores moderna (#1e1e1e, #2196F3)
- **Botões arredondados**: Corner radius de 12px com efeitos hover
- **Cards com sombra**: ShadowFrame para elevação visual
- **Drop zones**: Áreas de drag-and-drop com feedback visual
- **Layout responsivo**: Tabs organizadas por funcionalidade
- **Widgets customizados**: ModernButton, PreviewCard, ProgressCard, DropZoneFrame

#### Streaming para Arquivos Grandes
- **Processamento página-a-página**: Generator para baixo uso de memória
- **Threshold automático**: Ativa streaming para arquivos >50MB
- **Garbage collection periódico**: Previne vazamento de memória
- **Feedback detalhado**: Mostra página sendo processada no status bar

#### Sistema de Logging Robusto
- **Rotação de arquivos**: 5MB max, 3 backups
- **Níveis configuráveis**: DEBUG, INFO, WARNING, ERROR
- **Stack traces completos**: logger.exception() em todos os catches
- **Logging assíncrono**: Não bloqueia thread principal da GUI

#### Configuração Centralizada (config.py)
- **Temas e paletas**: LIGHT_PALETTE, DARK_PALETTE
- **Variáveis de ambiente**: Sobrescrita via PDF_TOOLS_* 
- **Singleton thread-safe**: get_config() global
- **Validação automática**: ensure_setup() na inicialização

#### Arquitetura em Camadas
- **Serviços (core/services/)**: Lógica de negócio isolada
  - `extractor_service.py`: Extração com streaming
  - `pdf_splitter.py`: Divisão com previews
- **Models (core/models/)**: Estruturas de dados (dataclasses)
  - `PagePreview`: Dados de thumbnail e texto preview
  - `SplitResult`: Resultado de divisão
- **Validators (core/validators/)**: Validação de PDFs
  - `pdf_validator.py`: Verifica integridade antes de processar
- **GUI desacoplada**: Injeção de dependência via serviços

### 🔧 Modificado

#### Correções Críticas
- **Lambdas em loops**: Captura correta de variáveis com defaults
- **Logging de exceptions**: Substituído `logger.error()` por `logger.exception()`
- **Validação prévia**: Verifica PDF antes de processar

#### Melhorias de UX
- **Feedback visual**: Status bar mostra arquivo e página sendo processada
- **Barras de progresso**: Porcentagem visível em todas operações
- **Mensagens de erro**: Toasts com ícones (✅ ❌ ⚠️)
- **Preview em todas tabs**: Visualização antes de processar

#### Otimizações
- **Redução de acoplamento**: GUI não importa módulos core diretamente
- **Separação de responsabilidades**: Cada módulo com única responsabilidade
- **Código DRY**: Eliminação de duplicação através de classes base

### 📦 Dependências Adicionais
- `customtkinter>=5.2.0`: Framework GUI moderno
- `Pillow>=10.0.0`: Processamento de imagens para thumbnails
- `pdfplumber>=0.10.0`: Extração de texto (mantido)
- `PyMuPDF>=1.23.0`: Compressão e divisão (mantido)

### 🗑️ Removido
- **Kivy dependency**: Migração completa para CustomTkinter
- **interface.kv**: Arquivo de layout Kivy obsoleto
- **gui/screens.py**: Screens Kivy substituídos por tabs

---

## [1.0.0] - Versão Inicial Kivy

### Adicionado
- Extração de texto de PDFs (single e batch)
- Compressão de PDFs com 3 níveis (BAIXA, MÉDIA, ALTA)
- Interface gráfica com Kivy
- Salvamento de resultados em TXT
- Barra de progresso básica
- Tratamento de erros simples

---

## Referências

- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)
