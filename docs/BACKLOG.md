# 📋 BACKLOG - PDF Tools v2.1

Controle de qualidade e evolução do produto.

**Última atualização:** 2024-05-13  
**Versão atual:** 2.1.0  
**Próxima release:** 2.2.0 (Testes & CI/CD)

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

### Fase 3 🔄 - Em Desenvolvimento (v2.2.0)
- [ ] Testes unitários com pytest (cobertura >80%)
  - [ ] Tests para ExtractorService
  - [ ] Tests para CompressorService
  - [ ] Tests para SplitterService
  - [ ] Tests para validators
- [ ] Integração contínua (GitHub Actions)
  - [ ] Pipeline de testes
  - [ ] Build automatizado
  - [ ] Release automático
- [ ] Documentação Sphinx/API
- [ ] Pacote PyPI para distribuição

### Fase 4 📅 - Planejamento Futuro (v2.3.0+)
- [ ] OCR para PDFs escaneados (tesseract)
- [ ] Conversão PDF ↔ Word
- [ ] Merge de múltiplos PDFs
- [ ] Adição de marca d'água
- [ ] Criptografia/descriptografia de PDFs
- [ ] Plugin system para extensões
- [ ] Modo batch avançado com filas

### Fase 3 📅 - Planejamento Futuro
- [ ] OCR para PDFs escaneados
- [ ] Conversão PDF ↔ Word
- [ ] Merge de múltiplos PDFs
- [ ] Adição de marca d'água
- [ ] Criptografia/descriptografia
- [ ] Plugin system para extensões

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
- [ ] Nomear arquivos automaticamente

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
