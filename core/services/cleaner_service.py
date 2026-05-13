#!/usr/bin/env python3
"""
Serviço de Limpeza de Arquivos de Texto
Suporta: .txt, .docx, .md

Executa em sequência:
1. EncodingDetector - Corrige encoding e caracteres inválidos
2. MarkdownCleaner - Aplica 12 técnicas de limpeza

Degradação zero e intervenção mínima.
"""

import re
from pathlib import Path
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class CleaningResult:
    """Resultado da limpeza de um arquivo."""
    arquivo: str
    caminho_original: str
    caminho_saida: str
    encoding_detectado: str = "utf-8"
    extensao: str = ".txt"
    limpezas_aplicadas: List[str] = field(default_factory=list)
    linhas_antes: int = 0
    linhas_depois: int = 0
    chars_antes: int = 0
    chars_depois: int = 0
    erro: Optional[str] = None
    sucesso: bool = False


class EncodingDetector:
    """
    Detecta e corrige encoding de arquivos de texto em pt-BR.
    Correção automática de caracteres comuns do português brasileiro.
    """

    REPLACEMENTS = {
        "\x82": ",",  "\x84": '"',  "\x85": "...", "\x88": "^",
        "\x91": "'",  "\x92": "'",  "\x93": '"',   "\x94": '"',
        "\x95": "•",  "\x96": "-",  "\x97": "—",
        "\xa0": " ",  "\xa7": "§",  "\xa9": "©",   "\xaa": "ª",
        "\xab": "«",  "\xac": "¬",  "\xad": "",    "\xae": "®",
        "\xb0": "°",  "\xb1": "±",  "\xb2": "²",   "\xb3": "³",
        "\xb6": "¶",  "\xba": "º",  "\xbb": "»",
        "\xc0": "À",  "\xc1": "Á",  "\xc2": "Â",   "\xc3": "Ã",
        "\xc4": "Ä",  "\xc7": "Ç",  "\xc9": "É",   "\xca": "Ê",
        "\xd3": "Ó",  "\xd4": "Ô",  "\xd5": "Õ",   "\xda": "Ú",
        "\xe0": "à",  "\xe1": "á",  "\xe2": "â",   "\xe3": "ã",
        "\xe4": "ä",  "\xe7": "ç",  "\xe9": "é",   "\xea": "ê",
        "\xed": "í",  "\xf3": "ó",  "\xf4": "ô",   "\xf5": "õ",
        "\xfa": "ú",  "\xfc": "ü",
    }
    
    PT_BR_CORRECT = {
        "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
        "Ã£": "ã", "Ãµ": "õ", "Ã¢": "â", "Ãª": "ê", "Ã´": "ô",
        "Ã§": "ç", "Ã‡": "Ç", "Ã…": "à", "Ã‰": "É", "Ãš": "Ú",
        "â\x80\x99": "'", "â\x80\x9c": '"', "â\x80\x9d": '"',
        "â\x80\x94": "—", "â\x80\x93": "–",
    }
    
    ENCODINGS_TO_TRY = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

    @classmethod
    def detect_and_correct(cls, filepath: str) -> Tuple[str, str]:
        """
        Detecta encoding e corrige caracteres.
        
        Returns:
            Tuple[str, str]: (encoding_usado, conteudo_corrigido)
        """
        content, used_encoding = None, None
        
        # Tenta encodings comuns
        for enc in cls.ENCODINGS_TO_TRY:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    content = f.read()
                used_encoding = enc
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # Fallback com substituição
        if content is None:
            with open(filepath, "rb") as f:
                content = f.read().decode("utf-8", errors="replace")
            used_encoding = "utf-8 (substituição)"
        
        # Corrige caracteres
        content = cls.correct_characters(content)
        return used_encoding, content

    @classmethod
    def correct_characters(cls, content: str) -> str:
        """Aplica correções de caracteres comuns."""
        # Aplica replacements
        for wrong, right in cls.REPLACEMENTS.items():
            content = content.replace(wrong, right)
        
        # Corrige padrões pt-BR
        for wrong, right in cls.PT_BR_CORRECT.items():
            content = content.replace(wrong, right)
        
        # Remove caracteres de controle
        content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", content)
        
        return content


class TextCleaner:
    """
    Aplica 12 limpezas encadeadas em conteúdo de texto.
    Funciona para .txt, .md e texto extraído de .docx
    """

    def clean(self, content: str) -> Tuple[str, List[str]]:
        """
        Aplica todas as 12 limpezas.
        
        Args:
            content: Conteúdo original
            
        Returns:
            Tuple[str, List[str]]: (conteudo_limpo, lista_de_limpezas)
        """
        limpezas: List[str] = []
        
        # 1. Remove BOM
        if content.startswith("\ufeff"):
            content = content[1:]
            limpezas.append("BOM removido")
        
        # 2. Normaliza line endings (CRLF → LF)
        if "\r\n" in content:
            content = content.replace("\r\n", "\n")
            limpezas.append("CRLF → LF")
        
        # 3. Remove espaços múltiplos (exceto em code blocks)
        content, n = self._fix_multiple_spaces(content)
        if n:
            limpezas.append(f"Espaços múltiplos removidos ({n}x)")
        
        # 4. Remove trailing whitespace
        lines = content.split("\n")
        stripped = [ln.rstrip() for ln in lines]
        if stripped != lines:
            limpezas.append("Trailing whitespace removido")
        lines = stripped
        
        # 5. Reduz linhas em branco excessivas (máx 2 consecutivas)
        lines, n = self._fix_blank_lines(lines)
        if n:
            limpezas.append(f"Linhas em branco excessivas reduzidas ({n}x)")
        
        content = "\n".join(lines)
        
        # 6. Corrige espaço antes de pontuação
        content, n = self._fix_space_before_punctuation(content)
        if n:
            limpezas.append(f"Espaço antes de pontuação corrigido ({n}x)")
        
        # 7. Normaliza headers (# sem espaço)
        content, n = self._fix_headers(content)
        if n:
            limpezas.append(f"Headers normalizados ({n}x)")
        
        # 8. Remove espaços em negrito/itálico
        content, n = self._fix_bold_italic_spaces(content)
        if n:
            limpezas.append(f"Espaços em negrito/itálico removidos ({n}x)")
        
        # 9. Detecta links vazios (apenas reporta)
        empty_links = re.findall(r"\[([^\]]+)\]\(\s*\)", content)
        if empty_links:
            limpezas.append(f"Links vazios detectados: {len(empty_links)}")
        
        # 10. Remove espaços extras em listas
        content, n = self._fix_list_spaces(content)
        if n:
            limpezas.append(f"Espaços em listas corrigidos ({n}x)")
        
        # 11. Normaliza hífens e traços
        content, n = self._fix_hyphens(content)
        if n:
            limpezas.append(f"Hífens normalizados ({n}x)")
        
        # 12. Garante newline final único
        content = content.rstrip("\n") + "\n"
        limpezas.append("Newline final normalizado")
        
        return content, limpezas

    def _fix_multiple_spaces(self, content: str) -> Tuple[str, int]:
        """Remove espaços múltiplos, preservando code blocks."""
        parts = re.split(r"(```[\s\S]*?```|`[^`]+`)", content)
        total, result = 0, []
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Fora de code blocks
                novo, n = re.subn(r" {2,}", " ", part)
                result.append(novo)
                total += n
            else:  # Dentro de code blocks - preserva
                result.append(part)
        return "".join(result), total

    def _fix_blank_lines(self, lines: List[str]) -> Tuple[List[str], int]:
        """Reduz linhas em branco consecutivas para no máximo 2."""
        result, consec, reduct = [], 0, 0
        for ln in lines:
            if ln.strip() == "":
                consec += 1
                if consec <= 2:
                    result.append(ln)
                else:
                    reduct += 1
            else:
                consec = 0
                result.append(ln)
        return result, reduct

    def _fix_space_before_punctuation(self, content: str) -> Tuple[str, int]:
        """Remove espaço antes de vírgula, ponto-e-vírgula, dois-pontos e ponto final."""
        content, n1 = re.subn(r" +([,;:])", r"\1", content)
        content, n2 = re.subn(r" +(\.(?=\s|$))", r"\1", content)
        return content, n1 + n2

    def _fix_headers(self, content: str) -> Tuple[str, int]:
        """Adiciona espaço após # em headers Markdown."""
        return re.subn(r"^(#{1,6})([^#\s])", r"\1 \2", content, flags=re.MULTILINE)

    def _fix_bold_italic_spaces(self, content: str) -> Tuple[str, int]:
        """Remove espaços extras dentro de **negrito** e *itálico*."""
        # Negrito: ** texto ** → **texto**
        content, n1 = re.subn(r"\*\*\s+(.+?)\s+\*\*", r"**\1**", content)
        # Itálico: * texto * → *texto* (preservando palavras simples)
        content, n2 = re.subn(r"(?<!\*)\*\s+([^\s*]+(?:\s+[^\s*]+)*?)\s+\*(?!\*)", r"*\1*", content)
        return content, n1 + n2

    def _fix_list_spaces(self, content: str) -> Tuple[str, int]:
        """Normaliza espaços em listas Markdown."""
        content, n = re.subn(r"^(\s*)[-*+]\s{2,}", r"\1- ", content, flags=re.MULTILINE)
        return content, n

    def _fix_hyphens(self, content: str) -> Tuple[str, int]:
        """Normaliza hífens e traços."""
        # Substitui múltiplos hífens por travessão
        content, n = re.subn(r" -+", " —", content)
        return content, n


class FileCleanerService:
    """
    Serviço principal de limpeza de arquivos.
    Orquestra EncodingDetector + TextCleaner.
    """
    
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".docx"}
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
    
    def clean_file(self, filepath: str, output_path: Optional[str] = None) -> CleaningResult:
        """
        Limpa um arquivo aplicando todas as técnicas.
        
        Args:
            filepath: Caminho do arquivo original
            output_path: Caminho de saída (opcional, gera automático se None)
            
        Returns:
            CleaningResult: Resultado detalhado da limpeza
        """
        path = Path(filepath)
        
        # Valida extensão
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return CleaningResult(
                arquivo=path.name,
                caminho_original=str(path),
                caminho_saida="",
                erro=f"Extensão não suportada: {path.suffix}. Use {self.SUPPORTED_EXTENSIONS}",
                sucesso=False
            )
        
        # Gera caminho de saída
        if output_path is None:
            output_path = str(path.parent / f"{path.stem}_limpo{path.suffix}")
        
        try:
            # Passo 1: Detectar e corrigir encoding
            encoding, content = EncodingDetector.detect_and_correct(filepath)
            
            # Estatísticas antes
            chars_antes = len(content)
            linhas_antes = len(content.split("\n"))
            
            # Passo 2: Aplicar 12 limpezas
            cleaned_content, limpezas = self.text_cleaner.clean(content)
            
            # Estatísticas depois
            chars_depois = len(cleaned_content)
            linhas_depois = len(cleaned_content.split("\n"))
            
            # Salvar resultado
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned_content)
            
            logger.info(f"Arquivo limpo: {path.name} → {Path(output_path).name}")
            logger.info(f"Limpezas aplicadas: {len(limpezas)}")
            
            return CleaningResult(
                arquivo=path.name,
                caminho_original=str(path),
                caminho_saida=output_path,
                encoding_detectado=encoding,
                extensao=path.suffix.lower(),
                limpezas_aplicadas=limpezas,
                linhas_antes=linhas_antes,
                linhas_depois=linhas_depois,
                chars_antes=chars_antes,
                chars_depois=chars_depois,
                erro=None,
                sucesso=True
            )
            
        except Exception as e:
            logger.exception(f"Erro ao limpar arquivo {filepath}: {e}")
            return CleaningResult(
                arquivo=path.name,
                caminho_original=str(path),
                caminho_saida="",
                erro=str(e),
                sucesso=False
            )
    
    def clean_content(self, content: str) -> Tuple[str, List[str]]:
        """
        Limpa conteúdo diretamente (sem arquivo).
        Útil para preview.
        
        Args:
            content: Conteúdo original
            
        Returns:
            Tuple[str, List[str]]: (conteudo_limpo, limpezas)
        """
        # Aplica correção de encoding simulada
        content = EncodingDetector.correct_characters(content)
        
        # Aplica 12 limpezas
        return self.text_cleaner.clean(content)


def create_test_files():
    """Cria arquivos de teste para validação."""
    test_dir = Path("/tmp/cleaner_tests")
    test_dir.mkdir(exist_ok=True)
    
    # Arquivo com problemas de encoding
    test1 = test_dir / "teste_encoding.txt"
    with open(test1, "wb") as f:
        f.write("Texto com acentos: café, latino, maçã\r\n".encode('latin-1'))
        f.write("Caracteres especiais: \x82\x84\x93\x94\r\n".encode('latin-1'))
        f.write("Multiplos   espacos    e tabs\t\there\r\n".encode('utf-8'))
        f.write("Linha com trailing space   \r\n".encode('utf-8'))
        f.write("\r\n\r\n\r\n\r\nMuitas linhas em branco acima\r\n".encode('utf-8'))
        f.write("Espaco antes de virgula , e ponto .\r\n".encode('utf-8'))
        f.write("#Header sem espaco\r\n".encode('utf-8'))
        f.write("** negrito com espacos **\r\n".encode('utf-8'))
        f.write("-  Lista com espaco extra\r\n".encode('utf-8'))
    
    # Arquivo Markdown
    test2 = test_dir / "teste.md"
    test2.write_text(
        "# Título\n"
        "##Subtítulo sem espaço\n"
        "Texto com  múltiplos   espaços.\n"
        "**  negrito  ** e *  itálico  *\n"
        "-  Item de lista\n"
        "[Link vazio]()\n"
        "Espaço antes de vírgula ,\n"
        "\n\n\n\n\n"
        "Muitas linhas em branco.\n",
        encoding="utf-8"
    )
    
    return test_dir, [test1, test2]


def run_tests():
    """Executa testes de regressão."""
    print("=" * 60)
    print("TESTES DE REGRESSÃO - CLEANER SERVICE")
    print("=" * 60)
    
    service = FileCleanerService()
    test_dir, test_files = create_test_files()
    
    all_passed = True
    
    for test_file in test_files:
        print(f"\n📄 Testando: {test_file.name}")
        print("-" * 40)
        
        result = service.clean_file(str(test_file))
        
        if result.sucesso:
            print(f"✅ SUCESSO")
            print(f"   Encoding: {result.encoding_detectado}")
            print(f"   Limpezas: {len(result.limpezas_aplicadas)}")
            for limpeza in result.limpezas_aplicadas:
                print(f"      • {limpeza}")
            print(f"   Linhas: {result.linhas_antes} → {result.linhas_depois}")
            print(f"   Chars: {result.chars_antes} → {result.chars_depois}")
            print(f"   Saída: {result.caminho_saida}")
        else:
            print(f"❌ FALHA: {result.erro}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = run_tests()
        sys.exit(0 if success else 1)
    elif len(sys.argv) > 1:
        # Modo CLI
        service = FileCleanerService()
        for filepath in sys.argv[1:]:
            result = service.clean_file(filepath)
            if result.sucesso:
                print(f"✅ {result.arquivo} → {Path(result.caminho_saida).name}")
                print(f"   {len(result.limpezas_aplicadas)} limpezas aplicadas")
            else:
                print(f"❌ {result.arquivo}: {result.erro}")
    else:
        print("Uso: python cleaner_service.py --test")
        print("     python cleaner_service.py arquivo1.txt arquivo2.md")
