# PDF Tools - Suite de Ferramentas para PDF

Uma aplicação modular desenvolvida em Python com interface gráfica em Kivy para extração de texto e compressão de arquivos PDF.

## REQUISITOS

### Python
- **Versão mínima:** Python 3.8
- **Versão recomendada:** Python 3.10 ou superior

### Bibliotecas
Instale as dependências necessárias executando:

```bash
pip install kivy pdfplumber PyMuPDF
```

Ou, se preferir usar um arquivo de requisitos (crie um arquivo `requirements.txt`):
```text
kivy>=2.2.0
pdfplumber>=0.10.0
PyMuPDF>=1.23.0
```

**Descrição das bibliotecas:**
- **kivy**: Framework para criação da interface gráfica multiplataforma
- **pdfplumber**: Biblioteca para extração precisa de texto de PDFs
- **PyMuPDF (fitz)**: Biblioteca para manipulação e compressão de PDFs

## COMO EXECUTAR

1. **Clone ou navegue até o diretório do projeto:**
   ```bash
   cd PDF
   ```

2. **Certifique-se de que todas as dependências estão instaladas:**
   ```bash
   pip install -r requirements.txt  # Se criou o arquivo
   # OU
   pip install kivy pdfplumber PyMuPDF
   ```

3. **Execute a aplicação:**
   ```bash
   python main.py
   ```

4. **A interface gráfica será aberta**, permitindo navegar entre as abas de "Extrator de Texto" e "Compressor de PDF".

## COMO USAR

### 📄 Extrator de Texto (PDF para TXT)

1. Na tela inicial, clique na aba **"Extrator de Texto"**.
2. Clique no botão **"Selecionar Arquivo(s) PDF"** para escolher um ou múltiplos arquivos PDF.
3. (Opcional) Selecione uma pasta de destino. Se não selecionada, os arquivos `.txt` serão salvos na mesma pasta dos originais.
4. Clique em **"Extrair Texto"**.
5. Acompanhe o progresso na barra de status e visualize os logs de sucesso ou erro.
6. Os arquivos de texto serão gerados com o mesmo nome do PDF original.

### 🗜️ Compressor de PDF

1. Na tela inicial, clique na aba **"Compressor de PDF"**.
2. Clique no botão **"Selecionar Arquivo(s) PDF"** para escolher os arquivos que deseja comprimir.
3. Escolha o **Nível de Compressão** no menu suspenso:
   - **Baixa:** Mantém alta qualidade, redução moderada de tamanho.
   - **Média:** Equilíbrio entre qualidade e tamanho (Recomendado).
   - **Alta:** Máxima redução de tamanho, pode haver perda visível de qualidade.
4. (Opcional) Selecione uma pasta de destino para os arquivos comprimidos.
5. Clique em **"Comprimir PDFs"**.
6. Acompanhe o progresso e verifique a economia de espaço nos logs.

## FUNCIONALIDADES

### Gerais
- **Interface Unificada:** Navegação simples entre ferramentas em uma única janela.
- **Processamento em Lote:** Capacidade de selecionar e processar múltiplos arquivos PDF de uma vez.
- **Logs Detalhados:** Painel de logs em tempo real mostrando o status de cada operação (sucesso, falha, detalhes de tamanho).
- **Validação de Arquivos:** Verificação automática se os arquivos selecionados são PDFs válidos antes do processamento.
- **Design Responsivo:** Interface adaptável a diferentes tamanhos de tela.

### Extrator de Texto
- **Extração de Alta Qualidade:** Utiliza `pdfplumber` para preservar a estrutura do texto sempre que possível.
- **Codificação UTF-8:** Garante compatibilidade com caracteres especiais e acentos.
- **Suporte a Múltiplas Páginas:** Concatena o texto de todas as páginas em um único arquivo.
- 🔄 **Extração de Imagens:** *(Planejado)* Opção específica para extrair apenas as imagens contidas no PDF e salvá-las em uma pasta organizada.

### Compressor de PDF
- **Níveis de Compressão Ajustáveis:** Controle sobre o trade-off entre qualidade e tamanho do arquivo.
- **Economia de Espaço:** Redução significativa do tamanho do arquivo para facilitar compartilhamento e armazenamento.
- **Preservação de Conteúdo:** Mantém o conteúdo textual e visual essencial, removendo metadados desnecessários e otimizando imagens.

### 🔜 Ferramentas Adicionais (Em Planejamento)
- **Mesclagem (Merge):** Juntar vários arquivos PDF em um único documento, aproveitando a biblioteca `PyMuPDF` ou `pypdf`.
- **Divisão (Split):** Separar um PDF em múltiplos arquivos baseados em intervalos de páginas específicos.
- **OCR Integrado:** Reconhecimento de texto em documentos digitalizados/escaneados usando Tesseract.

## ESTRUTURA DE ARQUIVOS

O projeto segue uma arquitetura modular para facilitar a manutenção e escalabilidade:

```
PDF/
├── main.py                 # Ponto de entrada da aplicação (instancia a App Kivy)
├── __init__.py             # Inicialização do pacote principal
├── README.md               # Este arquivo de documentação
│
├── core/                   # Módulo de Lógica de Negócios (Modelos)
│   ├── __init__.py
│   ├── pdf_extractor.py    # Classe PDFTextExtractor: Lógica de extração de texto
│   └── pdf_compressor.py   # Classes PDFCompressor e CompressionLevel: Lógica de compressão
│
├── gui/                    # Módulo de Interface Gráfica
│   ├── __init__.py
│   ├── screens.py          # Definição das telas (ExtractorScreen, CompressorScreen)
│   └── interface.kv        # Arquivo de linguagem KV para layout e estilização
│
└── utils/                  # Módulo de Utilitários
    ├── __init__.py
    └── helpers.py          # Funções auxiliares (formatação de tamanho, validações, etc.)
```

### Descrição dos Módulos

- **`main.py`**: Responsável por iniciar a aplicação Kivy e carregar o arquivo `.kv`.
- **`core/`**: Contém a lógica pura de negócios, independente de interface gráfica. Pode ser reutilizada em scripts CLI ou outros projetos.
  - `pdf_extractor.py`: Gerencia a abertura do PDF, extração de texto página por página e salvamento.
  - `pdf_compressor.py`: Gerencia a abertura, redefinição de streams de imagens e salvamento otimizado.
- **`gui/`**: Contém toda a lógica de apresentação e interação com o usuário.
  - `screens.py`: Define o comportamento das telas (callbacks, seleção de arquivos, atualização de UI).
  - `interface.kv`: Define a estrutura visual (layouts, botões, labels, cores).
- **`utils/`**: Funções de apoio usadas por vários módulos.
  - `helpers.py`: Contém funções como `format_file_size`, `is_valid_pdf`, e configuração de logging.

---

**Licença:** Uso livre para fins educacionais e pessoais.
**Autor:** Gerado via IA com base em solicitação de refatoração.
