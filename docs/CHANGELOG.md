# CHANGELOG

Todas as mudanças significativas neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto segue o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.3.0] - 2024 - Extração de Imagens e Divisão Avançada de PDFs

### ✨ Adicionado

#### Nova Funcionalidade: Extração de Imagens de PDFs
- **Serviço ImageExtractorService completo**:
  - Opção específica para extrair apenas imagens do PDF
  - Salvamento em pasta organizada com nomes sequenciais (`imagem_0001.png`, `imagem_0002.png`, ...)
  - Formatos suportados: **PNG, JPG, TIFF** (configurável via parâmetro)
  - Manter resolução original ou redimensionar (opção `resize_to`)
  - Extração de metadados detalhados das imagens
- **Metadados extraídos**:
  - Dimensões originais (width, height)
  - Espaço de cores (colorspace)
  - DPI/resolução original
  - Página de origem no PDF
  - Formato original e formato de saída
  - Tamanho do arquivo em bytes
- **Arquivo de metadados**: `metadados_imagens.json` na pasta de saída
- **Salvamento automático**: Mesmo diretório do arquivo de entrada
  - Pasta padrão: `{nome}_imagens_{timestamp}/`
  - Nomes sequenciais: `imagem_{NNNN}.{ext}` (ex: `imagem_0001.png`)
- **Processamento profissional**:
  - Thread dedicada com barra de progresso
  - Contagem prévia de imagens por página
  - Tratamento de erros robusto com rollback seguro

#### Nova Funcionalidade: Divisão Avançada de PDFs
- **Serviço PDFSplitterService expandido**:
  - ✅ **Separar um PDF em múltiplos arquivos**: `split_to_individual_pages()`
    - Cada página vira um arquivo PDF individual
    - Nomeação: `{nome}_pagina_{N}.pdf`
  - ✅ **Dividir por intervalos de páginas específicos**: `split_by_ranges()`
    - Lista de tuplas [(start, end), ...]
    - Nomeação: `{nome}_parte{N}_pag{start}-{end}.pdf`
  - ✅ **Dividir por bookmarks existentes**: `split_by_bookmarks()`
    - Extração automática de bookmarks/toc
    - Cada bookmark vira um arquivo separado
    - Nomeação: `{nome}_{titulo_secao}.pdf`
    - Método auxiliar: `get_bookmarks()` para preview
  - ✅ **Extrair páginas específicas**: `extract_specific_pages()`
    - Páginas pares: `extract_specific_pages(pdf_path, "even")`
    - Páginas ímpares: `extract_specific_pages(pdf_path, "odd")`
    - Lista customizada: `extract_specific_pages(pdf_path, [1, 3, 5, 7])`
    - Nomeação: `{nome}_pares.pdf`, `{nome}_impares.pdf`, `{nome}_selecionadas.pdf`
- **Flexibilidade total**: Usuário escolhe estratégia de divisão
- **Preservação de qualidade**: Todas divisões mantêm qualidade original

### 🔧 Modificado

#### Padronização de Salvamento (Atualizado)
- **Política unificada reforçada**: Todos os serviços salvam no mesmo diretório do arquivo de entrada
  - Cleaner: `{diretorio}/{nome}_limpo.{ext}`
  - Merger: `{diretorio}/{primeiro_arquivo}_mesclado_{timestamp}.pdf`
  - Splitter (páginas individuais): `{diretorio}/{nome}_pagina_{N}.pdf`
  - Splitter (bookmarks): `{diretorio}/{nome}_{titulo_secao}.pdf`
  - Splitter (intervalos): `{diretorio}/{nome}_parte{N}_pag{start}-{end}.pdf`
  - Splitter (pares/ímpares): `{diretorio}/{nome}_pares.pdf` / `{nome}_impares.pdf`
  - Compressor: `{diretorio}/{nome}_comprimido.pdf`
  - Image Extractor: `{diretorio}/{nome}_imagens_{timestamp}/imagem_{NNNN}.{ext}`
- **Timestamp em operações batch**: Evita sobrescrita acidental
- **Pastas organizadas**: Extração de imagens cria subpasta dedicada

#### Interface GUI (Planejado)
- **Nova tab "🖼️ Extrair Imagens"** (implementação futura):
  - Drag-and-drop de PDFs
  - Seleção de formato (PNG, JPG, TIFF)
  - Opção de redimensionamento
  - Preview de quantas imagens serão extraídas
  - Barra de progresso com contagem
- **Nova tab "✂️ Dividir PDF (Avançado)"** (implementação futura):
  - Seleção de estratégia: páginas individuais, intervalos, bookmarks, pares/ímpares
  - Preview de bookmarks disponíveis
  - Configuração de intervalos customizados
  - Checkbox para páginas pares/ímpares

### ✅ Testes de Regressão

#### PDF Splitter Service
```
✅ Split por bookmarks: 4 seções extraídas com sucesso
   - Arquivos criados: {nome}_{titulo_secao}.pdf
   
✅ Páginas pares: 2 páginas extraídas
   - Arquivo: {nome}_pares.pdf
   
✅ Páginas ímpares: 2 páginas extraídas
   - Arquivo: {nome}_impares.pdf
   
✅ Intervalos [(1,2), (3,4)]: 2 arquivos criados
   - Arquivos: {nome}_parte1_pag1-2.pdf, {nome}_parte2_pag3-4.pdf
```

#### Image Extractor Service
```
✅ Extração PNG: 2/2 imagens extraídas
   - Pasta: {nome}_imagens_{timestamp}/
   - Arquivos: imagem_0001.png, imagem_0002.png
   - Metadados: metadados_imagens.json gerado
   
✅ Extração JPG: 2/2 imagens extraídas
   - Qualidade preservada
   
✅ Extração TIFF: 2/2 imagens extraídas
   - Formato sem perdas
   
✅ Redimensionamento: 2/2 imagens redimensionadas
   - Resolução ajustada conforme parâmetro resize_to
```

### 📦 Dependências Adicionais
- `PyMuPDF>=1.23.0`: Extração de imagens e divisão de PDFs (já existente)
- `Pillow>=10.0.0`: Processamento e conversão de formatos de imagem (já existente)

---

## [2.2.0] - 2024 - Limpeza de Arquivos e Mesclagem de PDFs

### ✨ Adicionado

#### Nova Funcionalidade: Limpeza de Arquivos de Texto (.txt, .md, .docx)
- **Serviço CleanerService completo**: Pipeline EncodingDetector + TextCleaner
- **EncodingDetector inteligente**: 
  - Detecção automática (utf-8, latin-1, cp1252, iso-8859-1)
  - Correção de caracteres pt-BR (acentos, cedilha, aspas inteligentes)
  - Fallback com substituição para arquivos corrompidos
- **TextCleaner com 12 técnicas**:
  1. Remoção de BOM (Byte Order Mark)
  2. Normalização CRLF → LF
  3. Espaços múltiplos (preservando code blocks)
  4. Trailing whitespace
  5. Linhas em branco excessivas (máx 2 consecutivas)
  6. Espaço antes de pontuação
  7. Headers Markdown normalizados (# espaço)
  8. Negrito/itálico sem espaços extras (**texto**)
  9. Detecção de links vazios
  10. Listas Markdown padronizadas
  11. Hífens/traços normalizados
  12. Newline final único
- **Interface GUI moderna**:
  - Drag-and-drop de múltiplos arquivos
  - Processamento em thread com barra de progresso
  - Resultados detalhados por arquivo
  - Salvamento automático no mesmo diretório: `{nome}_limpo.{ext}`
- **Degradação zero**: Preserva code blocks e formatação essencial
- **Intervenção mínima**: Apenas correções necessárias

#### Nova Funcionalidade: Mesclagem de PDFs
- **Serviço PDFMergerService completo**:
  - Seleção múltipla de PDFs (drag-and-drop + botão)
  - Preview visual com informações: nome, nº páginas, tamanho formatado
  - Reordenação flexível com botões ↑↓ (qualquer ordem)
  - Remoção individual de arquivos da lista
  - Opções configuráveis: bookmarks, compressão, separadores
- **Processamento profissional**:
  - Thread dedicada com barra de progresso
  - Preservação de bookmarks/navegação original
  - Compressão opcional para reduzir tamanho final
  - Separadores entre arquivos (páginas em branco)
- **Salvamento automático**: Mesmo diretório do primeiro arquivo
  - Nome padrão: `{primeiro_arquivo}_mesclado_{timestamp}.pdf`
  - Abertura automática da pasta após conclusão
- **Tratamento de erros robusto**: Mensagens claras e rollback seguro

### 🔧 Modificado

#### Padronização de Salvamento
- **Política unificada**: Todos os serviços salvam no mesmo diretório do arquivo de entrada
  - Cleaner: `{diretorio}/{nome}_limpo.{ext}`
  - Merger: `{diretorio}/{primeiro_arquivo}_mesclado_{timestamp}.pdf`
  - Splitter: `{diretorio}/{nome}_pagina_{N}.pdf`
  - Compressor: `{diretorio}/{nome}_comprimido.pdf`
- **Sem diálogos desnecessários**: Salvamento automático com opção de abrir pasta
- **Timestamp em operações batch**: Evita sobrescrita acidental

#### Interface GUI
- **Import datetime**: Adicionado suporte a timestamps
- **Fluxo simplificado**: Menos cliques, mais produtividade
- **Feedback consistente**: Mensagens padronizadas em todas tabs

### ✅ Testes de Regressão

#### Cleaner Service
```
✅ teste_encoding.txt - 7 limpezas aplicadas
   - Encoding detectado: latin-1
   - Linhas: 14 → 12, Chars: 270 → 255

✅ teste.md - 7 limpezas aplicadas
   - Encoding: utf-8
   - Linhas: 14 → 11, Chars: 184 → 169
```

#### PDF Merger Service
```
✅ Criação de PDFs de teste: 3 arquivos
✅ Obtenção de informações: nome, páginas, tamanho
✅ Mesclagem bem-sucedida: 3 páginas totais
✅ Reordenação funcional: move arquivos entre posições
```

### 📦 Dependências Adicionais
- `python-docx`: Suporte a arquivos .docx
- `PyPDF2`: Mesclagem de PDFs com bookmarks

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
