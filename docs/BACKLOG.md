# 📋 BACKLOG - PDF Tools v2.4

Controle de qualidade e evolução do produto.

**Última atualização:** 2024-05-13  
**Versão atual:** 2.3.0  
**Próxima release:** 2.4.0 (Fila de Processamento, Preview Inteligente e Componentização)

---

## 🎯 Roadmap

### Fase 1 ✅ - Fundação da Arquitetura (COMPLETO - v2.0.0)
- [x] Configuração centralizada (config.py)
- [x] Sistema de logging robusto (logger.py)
- [x] Validação de PDFs (core/validators/)
- [x] Arquitetura em camadas documentada
- [x] Documentação inicial (CHANGELOG, BACKLOG, PLANO_REFACTORY)

### Fase 2 ✅ - Core Services e GUI Moderna (COMPLETO - v2.1.0)
- [x] Implementar ExtractorService com streaming
- [x] Implementar CompressorService
- [x] Implementar SplitterService (DividirPDF)
- [x] Interfaces/protocols para injeção de dependência
- [x] Streaming para arquivos >50MB
- [x] Correção de lambdas em loops
- [x] Logger.exception() em todos os catches
- [x] Migração completa para CustomTkinter
- [x] Interface moderna com tema escuro premium
- [x] Botões arredondados e cards com sombra
- [x] Drop zones com drag-and-drop
- [x] Layout responsivo com tabs
- [x] Preview em todas funcionalidades
- [x] Funcionalidade DividirPDF completa
  - [x] Extrair páginas individuais
  - [x] Extrair intervalo de páginas
  - [x] Preview visual com thumbnails
  - [x] Seleção múltipla com checkboxes
- [x] Feedback visual mostrando arquivo/página sendo processada
- [x] Baixo acoplamento GUI ↔ Core

### Fase 3 ✅ - Widgets Reutilizáveis e ThemeManager (COMPLETO - v2.3.0)
- [x] Biblioteca de Widgets Reutilizáveis (W01-W12)
  - [x] W01 - NumericEntryPair: Entry numérico com botões +/- 
  - [x] W02 - TooltipCheckbox: Checkbox com tooltip
  - [x] W03 - FormatSelector: Seletor de formato (Combobox)
  - [x] W04 - FilePickerButton: Botão file picker
  - [x] W05 - SectionSeparator: Separador seccional
  - [x] W06 - DynamicStatusArea: Área de status dinâmico
  - [x] W07 - MetadataGrid: Grid de metadados
  - [x] W08 - ValueSlider: Slider com valor visível
  - [x] W09 - ClearListButton: Botão limpar lista
  - [x] W10 - ProcessingIndicator: Indicador de processamento
  - [x] W11 - SummaryCard: Card de resumo
  - [x] W12 - SmartIntervalInput: Input de intervalo inteligente
- [x] ThemeManager - Gerenciador de Temas Claro/Escuro
  - [x] Alternância instantânea entre temas
  - [x] Persistência de preferência em JSON
  - [x] Cobertura total de widgets CustomTkinter
  - [x] Paletas de cores configuráveis
  - [x] Registro de componentes para atualização automática
- [ ] Testes unitários com pytest (cobertura >80%)
  - [ ] Tests para ExtractorService
  - [ ] Tests para CompressorService
  - [ ] Tests para SplitterService
  - [ ] Tests para validators
  - [ ] Tests para widgets (W01-W12)
- [ ] Integração contínua (GitHub Actions)
  - [ ] Pipeline de testes
  - [ ] Build automatizado
  - [ ] Release automático
- [ ] Documentação Sphinx/API
- [ ] Pacote PyPI para distribuição

### Fase 4 🔄 - Em Desenvolvimento (v2.4.0)
- [ ] **Fila de Processamento Inteligente (TaskQueueService)**
  - [ ] Módulo `core/task_queue.py` com sistema de filas assíncronas
  - [ ] Suporte a prioridades (LOW, NORMAL, HIGH, CRITICAL)
  - [ ] Cancelamento seguro de tarefas
  - [ ] Callbacks para progresso em tempo real
  - [ ] Worker thread dedicado para processamento sequencial
  - [ ] Integração com todas as tabs de processamento
  
- [ ] **Pré-visualização Inteligente (PreviewEngine)**
  - [ ] Módulo `core/preview_engine.py` para estimativas detalhadas
  - [ ] Calcular tamanho estimado de arquivos antes da execução
  - [ ] Estimar tempo de processamento baseado no histórico
  - [ ] Preview de metadados completos (páginas, imagens, bookmarks)
  - [ ] Cálculo assíncrono sem bloquear UI
  - [ ] Componente `PreviewPanel` na interface
  
- [ ] **Classe BaseProcessTab**
  - [ ] Módulo `gui_tkinter/tabs/base_tab.py`
  - [ ] Centralizar ciclo de vida comum das tabs
  - [ ] Padronizar integração com TaskQueueService
  - [ ] Gerenciar estado e callbacks de forma uniforme
  - [ ] Reduzir código repetitivo em ~40%
  - [ ] Refatorar MergeTab, CompressTab, SplitTab para herdar da base
  
- [ ] **Correções de Drag-and-Drop e Ordenação**
  - [ ] Resolver problemas de detecção de drop no Linux
  - [ ] Corrigir botões de cancelar durante processamento
  - [ ] Melhorar ordenação na mesclagem de PDFs
  - [ ] Adicionar feedback visual aprimorado
  
- [ ] **Componentização de Elementos de Interface**
  - [x] Tabela de elementos candidatos à componentização definida
  - [ ] 🔴 Barra de Progresso com Status (Crítica) - Unificar estilos e integração com threading
  - [ ] 🟠 Painel de Configurações (Alta) - ConfigPanel genérico para campos
  - [ ] 🟠 Área de Logs/Console (Alta) - LogConsole com scroll e cores por nível
  - [ ] 🟡 Card de Estatísticas (Média) - StatsCard reutilizável
  - [ ] 🟡 Botão de Ação Principal (Média) - ActionButton com estados
  - [ ] 🟢 Seletor de Diretório (Baixa) - OutputPathSelector com validação
  - [ ] 🟠 Lista de Arquivos com Ações em Lote (Alta) - FileListManager completo
  - [ ] 🟡 Preview de Metadados do PDF (Média) - MetadataPreviewComponent

### Fase 5 📅 - Planejamento Futuro (v2.5.0+)
- [ ] OCR para PDFs escaneados (tesseract)
- [ ] Conversão PDF ↔ Word
- [ ] Merge de múltiplos PDFs avançado
- [ ] Adição de marca d'água
- [ ] Criptografia/descriptografia de PDFs
- [ ] Plugin system para extensões
- [ ] Modo batch avançado com filas prioritárias

---

## 🐛 Bugs Conhecidos

| ID | Severidade | Descrição | Status |
|----|------------|-----------|--------|
| BUG-001 | Baixa | Drop zone não detecta drop nativo no Linux | Aberto |
| BUG-002 | Média | Preview de PDFs >100 páginas lento | Em análise |

---

## 📖 Histórias de Usuário

### Épico: Extração de Texto

#### US-001 - Extrair texto de PDF único
**Como** usuário  
**Quero** extrair texto de um arquivo PDF  
**Para** usar o conteúdo em outros documentos  

**Critérios de Aceitação:**
- [ ] Selecionar arquivo via dialog ou drag-drop
- [ ] Visualizar progresso página por página
- [ ] Ver resultado formatado com numeração de páginas
- [ ] Salvar resultado em .txt

**Status:** ✅ Completo

---

#### US-002 - Extrair texto de múltiplos PDFs (batch)
**Como** usuário  
**Quero** processar vários PDFs de uma vez  
**Para** economizar tempo  

**Critérios de Aceitação:**
- [ ] Selecionar múltiplos arquivos
- [ ] Ver progresso individual por arquivo
- [ ] Resultado combinado em único arquivo
- [ ] Tratamento de erro por arquivo

**Status:** ✅ Completo

---

### Épico: Compressão

#### US-003 - Comprimir PDF
**Como** usuário  
**Quero** reduzir tamanho de um PDF  
**Para** facilitar envio por email  

**Critérios de Aceitação:**
- [ ] 3 níveis de compressão (Baixa, Média, Alta)
- [ ] Visualizar redução percentual
- [ ] Manter qualidade legível
- [ ] Escolher local de salvamento

**Status:** ✅ Completo

---

### Épico: Divisão de PDF

#### US-004 - Dividir PDF em páginas individuais
**Como** usuário  
**Quero** separar cada página em um arquivo PDF  
**Para** distribuir páginas individualmente  

**Critérios de Aceitação:**
- [ ] Visualizar thumbnails de todas as páginas
- [ ] Selecionar páginas específicas
- [ ] Extrair páginas selecionadas
- [ ] Nomear arquivos automaticamente conforme 

**Status:** ✅ Completo

---

#### US-005 - Extrair intervalo de páginas
**Como** usuário  
**Quero** extrair um intervalo contínuo de páginas  
**Para** criar um documento menor  

**Critérios de Aceitação:**
- [ ] Definir página inicial e final
- [ ] Preview do intervalo selecionado
- [ ] Extrair em único arquivo PDF
- [ ] Validar intervalo válido

**Status:** 🔄 Em desenvolvimento

---

## 🔧 Tarefas Técnicas

### Infraestrutura
- [ ] Setup pytest + coverage
- [ ] Configurar GitHub Actions CI/CD
- [ ] Dockerfile para containerização
- [ ] Scripts de build automatizado

### Qualidade de Código
- [ ] Type hints em todos os módulos
- [ ] Docstrings padronizadas (Google style)
- [ ] Linting com flake8/black
- [ ] Análise estática com mypy

### Performance
- [ ] Benchmark de operações
- [ ] Otimizar geração de thumbnails
- [ ] Cache de previews
- [ ] Processamento assíncrono avançado

---

## 📊 Métricas de Qualidade

| Métrica | Meta | Atual | Status |
|---------|------|-------|--------|
| Cobertura de testes | >80% | 0% | ❌ |
| Code smell | <10 | TBD | ⏳ |
| Dívida técnica | Baixa | Média | ⚠️ |
| Tempo de build | <2min | N/A | ⏳ |

---

## 📝 Notas de Release

### v2.0.0 - Refatoração Completa
**Data:** 2024  
**Foco:** Arquitetura, UX e Performance

**Destaques:**
- Nova interface CustomTkinter moderna
- Funcionalidade DividirPDF com preview visual
- Streaming para arquivos >50MB
- Logging robusto com rotação
- Configuração centralizada flexível

**Breaking Changes:**
- Migração de Kivy para CustomTkinter
- Mudança na estrutura de diretórios
- API de serviços reestruturada

---

## 🏷️ Labels

- `feature`: Nova funcionalidade
- `bug`: Correção de defeito
- `enhancement`: Melhoria
- `refactor`: Refatoração de código
- `docs`: Documentação
- `test`: Testes
- `performance`: Otimização
- `ui/ux`: Interface e experiência

---

*Última atualização: 2024*
