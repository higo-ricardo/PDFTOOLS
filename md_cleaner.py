#!/usr/bin/env python3
"""
Markdown Cleaner — Pipeline integrado de limpeza, encoding e extração jurídica.
v1.2.0

Novidades em v1.2.0:
  - AlternativasExtractor: segmenta alternativas A-E (Q-005 de regex.md)
  - InteractiveReviewer: revisão no terminal [s/n/r/p/q]
  - Watch debounce: --watch-debounce evita duplo disparo em salvamentos rápidos
  - HTMLReportGenerator: relatório HTML com pizza SVG, tabela filtrável e diff visual
  - 10 áreas jurídicas ativas (+ Constitucional, Trabalhista, Previdenciário,
    Empresarial e Financeiro/LRF — JUR-011…015 de regex.md)
"""

import html as html_module
import json
import hashlib
import logging
import math
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# ENCODING DETECTOR
# ─────────────────────────────────────────────────────────────────────────────
class EncodingDetector:
    """Detecta e corrige encoding de arquivos de texto em pt-BR."""

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
        content, used_encoding = None, None
        for enc in cls.ENCODINGS_TO_TRY:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    content = f.read()
                used_encoding = enc
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        if content is None:
            with open(filepath, "rb") as f:
                content = f.read().decode("utf-8", errors="replace")
            used_encoding = "utf-8 (substituição)"
        content = cls.correct_characters(content)
        return used_encoding, content

    @classmethod
    def correct_characters(cls, content: str) -> str:
        for wrong, right in cls.REPLACEMENTS.items():
            content = content.replace(wrong, right)
        for wrong, right in cls.PT_BR_CORRECT.items():
            content = content.replace(wrong, right)
        content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", content)
        return content


# ─────────────────────────────────────────────────────────────────────────────
# RESULTADO DE LIMPEZA
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class CleaningResult:
    arquivo: str
    encoding_original: str = "utf-8"
    limpezas: List[str] = field(default_factory=list)
    linhas_antes: int = 0
    linhas_depois: int = 0
    chars_antes: int = 0
    chars_depois: int = 0
    erro: Optional[str] = None
    salvo: bool = False
    backup: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# MARKDOWN CLEANER
# ─────────────────────────────────────────────────────────────────────────────
class MarkdownCleaner:
    """Aplica 12 limpezas encadeadas a conteúdo Markdown."""

    def clean(self, content: str) -> Tuple[str, List[str]]:
        limpezas: List[str] = []

        if content.startswith("\ufeff"):
            content = content[1:]
            limpezas.append("BOM removido")
        if "\r\n" in content:
            content = content.replace("\r\n", "\n")
            limpezas.append("CRLF → LF")
        content, n = self._fix_multiple_spaces(content)
        if n:
            limpezas.append(f"Espaços múltiplos removidos ({n}x)")
        lines = content.split("\n")
        stripped = [ln.rstrip() for ln in lines]
        if stripped != lines:
            limpezas.append("Trailing whitespace removido")
        lines = stripped
        lines, n = self._fix_blank_lines(lines)
        if n:
            limpezas.append(f"Linhas em branco excessivas reduzidas ({n}x)")
        content = "\n".join(lines)
        content, n = self._fix_space_before_punctuation(content)
        if n:
            limpezas.append(f"Espaço antes de pontuação corrigido ({n}x)")
        content, n = self._fix_headers(content)
        if n:
            limpezas.append(f"Headers normalizados ({n}x)")
        content, n = self._fix_bold_italic_spaces(content)
        if n:
            limpezas.append(f"Espaços em negrito/itálico removidos ({n}x)")
        empty = re.findall(r"\[([^\]]+)\]\(\s*\)", content)
        if empty:
            limpezas.append(f"Links vazios detectados: {len(empty)}")
        content = content.rstrip("\n") + "\n"
        return content, limpezas

    def _fix_multiple_spaces(self, content: str) -> Tuple[str, int]:
        parts = re.split(r"(```[\s\S]*?```|`[^`]+`)", content)
        total, result = 0, []
        for i, part in enumerate(parts):
            if i % 2 == 0:
                novo, n = re.subn(r" {2,}", " ", part)
                result.append(novo)
                total += n
            else:
                result.append(part)
        return "".join(result), total

    def _fix_blank_lines(self, lines: List[str]) -> Tuple[List[str], int]:
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
        content, n1 = re.subn(r" +([,;:])", r"\1", content)
        content, n2 = re.subn(r" +(\.(?=\s|$))", r"\1", content)
        return content, n1 + n2

    def _fix_headers(self, content: str) -> Tuple[str, int]:
        return re.subn(r"^(#{1,6})([^#\s])", r"\1 \2", content, flags=re.MULTILINE)

    def _fix_bold_italic_spaces(self, content: str) -> Tuple[str, int]:
        content, n1 = re.subn(r"\*\*\s+(.+?)\s+\*\*", r"**\1**", content)
        content, n2 = re.subn(r"\*\s+(.+?)\s+\*",     r"*\1*",   content)
        return content, n1 + n2


# ─────────────────────────────────────────────────────────────────────────────
# GABARITO EXTRACTOR  (GAB-001 … GAB-006)
# ─────────────────────────────────────────────────────────────────────────────
class GabaritoExtractor:
    """Extrai metadados de gabarito usando padrões GAB-001…GAB-006 de regex.md."""

    PAT_CE   = re.compile(r"\[?\s*(?:Gabarito|Resposta|Res\.?|Gab\.?)\s*[:.]?\s*\]?\s*(Certo|Errado)\b", re.I)
    PAT_ME   = re.compile(r"\[?\s*(?:Gabarito|Resposta|Res\.?|Gab\.?)\s*[:.]?\s*\]?\s*\b([A-Ea-e])\b",   re.I)
    PAT_MARK = re.compile(r"^[\s]*(?:\*|\->|→|✓|✔)\s*\(?([A-Ea-e])\)?[\.\)]", re.M)
    PAT_JUST = re.compile(r"^(?:Justificativa|Comentário|Explica[çc][aã]o|Fundamenta[çc][aã]o)\s*:", re.M | re.I)
    PAT_BANCA= re.compile(r"\b(CEBRASPE|CESPE|FCC|VUNESP|FGV|CESGRANRIO|ESAF|IDECAN|AOCP|IBFC)\b", re.I)
    PAT_ANO  = re.compile(r"\b(?:ano|prova|edital|concurso)\s*[:/\-]?\s*(20\d{2}|19\d{2})\b", re.I)

    def extract(self, text: str) -> Dict[str, str]:
        result = {"gabarito": "", "tipo": "", "banca": "", "ano": "", "justificativa_presente": "não"}
        if self.PAT_JUST.search(text):
            result["justificativa_presente"] = "sim"
        m = self.PAT_CE.search(text)
        if m:
            result["gabarito"] = "C" if m.group(1).lower() == "certo" else "E"
            result["tipo"] = "certo_errado"
        else:
            m = self.PAT_ME.search(text) or self.PAT_MARK.search(text)
            if m:
                result["gabarito"] = m.group(1).upper()
                result["tipo"] = "multipla_escolha"
        m = self.PAT_BANCA.search(text)
        if m:
            result["banca"] = m.group(1).upper()
        m = self.PAT_ANO.search(text)
        if m:
            result["ano"] = m.group(1)
        return result


# ─────────────────────────────────────────────────────────────────────────────
# ALTERNATIVAS EXTRACTOR  (Q-005 de regex.md)
# ─────────────────────────────────────────────────────────────────────────────
class AlternativasExtractor:
    """
    Segmenta alternativas A–E de um bloco de texto de questão (padrão Q-005).

    Requisitos para retornar resultado não-vazio:
      - Ao menos 2 alternativas encontradas
      - Sequência deve começar em A e ser contígua (A,B,C…)
    """

    # Q-005: detecta início de alternativa — A) B. (C) a) etc.
    PAT_START = re.compile(r"^[ \t]*\(?([A-Ea-e])\)?[\.)][ \t]+", re.MULTILINE)

    def extract(self, text: str) -> Dict[str, str]:
        """Retorna {"A": "texto…", "B": "texto…", …} ou {} se não encontrar."""
        matches = list(self.PAT_START.finditer(text))
        if len(matches) < 2:
            return {}

        alternativas: Dict[str, str] = {}
        for i, m in enumerate(matches):
            letra  = m.group(1).upper()
            start  = m.end()
            end    = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            conteudo = re.sub(r"\n+", " ", text[start:end].strip()).strip()
            alternativas[letra] = conteudo

        # Valida sequência contígua a partir de A
        letras    = sorted(alternativas.keys())
        esperadas = [chr(ord("A") + i) for i in range(len(letras))]
        if letras != esperadas or letras[0] != "A":
            return {}

        return alternativas


# ─────────────────────────────────────────────────────────────────────────────
# DUPLICATE DETECTOR
# ─────────────────────────────────────────────────────────────────────────────
class DuplicateDetector:
    """Detecta duplicatas exatas (MD5) e fuzzy (SequenceMatcher)."""

    def __init__(self, threshold: float = 0.85, fuzzy_limit: int = 500):
        self.threshold   = threshold
        self.fuzzy_limit = fuzzy_limit

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower().strip())

    def _fingerprint(self, text: str) -> str:
        return hashlib.md5(self._normalize(text).encode("utf-8")).hexdigest()

    def find_exact(self, questions: List[str]) -> Dict[str, List[int]]:
        buckets: Dict[str, List[int]] = {}
        for i, q in enumerate(questions):
            buckets.setdefault(self._fingerprint(q), []).append(i)
        return {h: idxs for h, idxs in buckets.items() if len(idxs) > 1}

    def find_fuzzy(self, questions: List[str]) -> List[Tuple[int, int, float]]:
        if len(questions) > self.fuzzy_limit:
            logger.warning(
                f"[DUP] {len(questions)} questões > limite fuzzy ({self.fuzzy_limit}). "
                f"Use --sem-duplicatas."
            )
            return []
        exact_pairs: set = set()
        for idxs in self.find_exact(questions).values():
            for a in range(len(idxs)):
                for b in range(a + 1, len(idxs)):
                    exact_pairs.add((idxs[a], idxs[b]))
        results = []
        for i in range(len(questions)):
            for j in range(i + 1, len(questions)):
                if (i, j) in exact_pairs:
                    continue
                ratio = SequenceMatcher(
                    None,
                    self._normalize(questions[i])[:600],
                    self._normalize(questions[j])[:600],
                ).ratio()
                if ratio >= self.threshold:
                    results.append((i, j, ratio))
        return results

    def report(self, questions: List[str], labels: Optional[List[str]] = None) -> Dict:
        def label(i: int) -> str:
            return f"{labels[i]} (#{i})" if labels and i < len(labels) else f"#{i}"
        exact = self.find_exact(questions)
        fuzzy = self.find_fuzzy(questions)
        return {
            "total_questoes": len(questions),
            "duplicatas_exatas": sum(len(v) - 1 for v in exact.values()),
            "pares_fuzzy": len(fuzzy),
            "grupos_exatos": [
                {"hash": h[:8], "indices": idxs, "labels": [label(i) for i in idxs]}
                for h, idxs in exact.items()
            ],
            "pares_fuzzy_detalhe": [
                {"i": i, "j": j, "score": round(s, 3),
                 "label_i": label(i), "label_j": label(j)}
                for i, j, s in sorted(fuzzy, key=lambda x: -x[2])
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# HTML REPORT GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
class HTMLReportGenerator:
    """
    Relatório HTML autossuficiente (sem CDN externo):
      - Cards de resumo
      - Gráfico de pizza SVG por área jurídica
      - Tabela de questões ordenável + filtros por área/banca/ano
      - Seção de duplicatas com diff visual highlight (SequenceMatcher)
      - Log de processamento de arquivos
    """

    COLORS = [
        "#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f",
        "#edc948","#b07aa1","#ff9da7","#9c755f","#bab0ac",
    ]

    def generate(
        self,
        results: List[CleaningResult],
        questoes_por_area: Dict[str, List["Questao"]],
        dup_report: Optional[Dict],
        diretorio: str,
    ) -> str:
        dist    = {AREAS[k]["titulo"]: len(qs) for k, qs in questoes_por_area.items() if qs}
        total_q = sum(dist.values())
        total_d = (dup_report or {}).get("duplicatas_exatas", 0) + \
                  (dup_report or {}).get("pares_fuzzy", 0)

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relatório md-cleaner — {datetime.now():%Y-%m-%d}</title>
<style>{self._css()}</style>
</head>
<body>
<header>
  <h1>📄 md-cleaner — Relatório de Processamento</h1>
  <p class="sub">Gerado em {datetime.now():%d/%m/%Y %H:%M:%S} · <code>{html_module.escape(diretorio)}</code></p>
</header>

<section>
  <div class="cards">
    {self._card("📁 Arquivos", len(results), "processados")}
    {self._card("📝 Questões", total_q, "extraídas")}
    {self._card("🗂️ Áreas",    len(dist), "ativas")}
    {self._card("🔁 Duplicatas", total_d, "detectadas")}
  </div>
</section>

<section>
  <h2>Distribuição por Área</h2>
  <div class="row">
    {self._svg_pie(dist)}
    {self._area_table(dist)}
  </div>
</section>

<section>
  <h2>Questões Extraídas</h2>
  {self._filtros(questoes_por_area)}
  {self._questoes_table(questoes_por_area)}
</section>

{self._dup_section(questoes_por_area, dup_report)}

<section>
  <h2>Log de Processamento</h2>
  {self._log_table(results)}
</section>

<script>{self._js()}</script>
</body>
</html>"""

    # ── componentes ──────────────────────────────────────────────────────────

    def _card(self, title: str, value, label: str) -> str:
        return (f'<div class="card"><div class="ct">{title}</div>'
                f'<div class="cv">{value}</div><div class="cl">{label}</div></div>')

    def _svg_pie(self, dist: Dict[str, int]) -> str:
        total = sum(dist.values())
        if not total:
            return '<div class="pie-wrap"><p style="color:#999">Sem dados</p></div>'
        cx = cy = r = 88
        paths, legend = [], []
        angle = -math.pi / 2
        for (lbl, val), color in zip(dist.items(), self.COLORS):
            if not val:
                continue
            pct = val / total
            ea  = angle + pct * 2 * math.pi
            x1, y1 = cx + r * math.cos(angle), cy + r * math.sin(angle)
            x2, y2 = cx + r * math.cos(ea),    cy + r * math.sin(ea)
            lg = 1 if pct > 0.5 else 0
            paths.append(
                f'<path d="M{cx},{cy}L{x1:.1f},{y1:.1f}A{r},{r} 0 {lg},1 {x2:.1f},{y2:.1f}Z"'
                f' fill="{color}" stroke="#fff" stroke-width="2">'
                f'<title>{html_module.escape(lbl)}: {val} ({pct:.1%})</title></path>'
            )
            legend.append(
                f'<div class="li"><span class="ld" style="background:{color}"></span>'
                f'{html_module.escape(lbl)}: <strong>{val}</strong></div>'
            )
            angle = ea
        return (f'<div class="pie-wrap">'
                f'<svg viewBox="0 0 176 176" width="176" height="176">{"".join(paths)}</svg>'
                f'<div class="legend">{"".join(legend)}</div></div>')

    def _area_table(self, dist: Dict[str, int]) -> str:
        total = sum(dist.values()) or 1
        rows = "".join(
            f'<tr><td>{html_module.escape(a)}</td><td class="num">{c}</td>'
            f'<td><div class="bar"><div class="bf" style="width:{c/total*100:.0f}%"></div></div></td></tr>'
            for a, c in sorted(dist.items(), key=lambda x: -x[1])
        )
        return (f'<table class="sort" style="min-width:300px">'
                f'<thead><tr><th>Área</th><th>Qtd</th><th>%</th></tr></thead>'
                f'<tbody>{rows}</tbody></table>')

    def _filtros(self, qpa: Dict[str, List["Questao"]]) -> str:
        bancas = sorted({q.banca for qs in qpa.values() for q in qs if q.banca})
        anos   = sorted({q.ano   for qs in qpa.values() for q in qs if q.ano})
        areas  = sorted({AREAS[k]["titulo"] for k, qs in qpa.items() if qs})

        def opts(vals: List[str]) -> str:
            return "".join(f'<option value="{html_module.escape(v)}">{html_module.escape(v)}</option>'
                           for v in vals)

        return (f'<div class="filtros">'
                f'<label>Área <select id="fa" onchange="filtrar()">'
                f'<option value="">Todas</option>{opts(areas)}</select></label>'
                f'<label>Banca <select id="fb" onchange="filtrar()">'
                f'<option value="">Todas</option>{opts(bancas)}</select></label>'
                f'<label>Ano <select id="fy" onchange="filtrar()">'
                f'<option value="">Todos</option>{opts(anos)}</select></label>'
                f'<button onclick="limpar()">Limpar</button></div>')

    def _questoes_table(self, qpa: Dict[str, List["Questao"]]) -> str:
        rows = []
        for area_key, questoes in qpa.items():
            titulo = AREAS[area_key]["titulo"]
            for q in questoes:
                alts    = ", ".join(q.alternativas.keys()) if q.alternativas else "—"
                preview = html_module.escape(q.texto[:180].replace("\n", " "))
                rows.append(
                    f'<tr data-area="{html_module.escape(titulo)}"'
                    f' data-banca="{html_module.escape(q.banca)}"'
                    f' data-ano="{html_module.escape(q.ano)}">'
                    f'<td class="num">{html_module.escape(q.numero)}</td>'
                    f'<td>{html_module.escape(titulo)}</td>'
                    f'<td class="num gab">{html_module.escape(q.gabarito) or "—"}</td>'
                    f'<td class="num">{alts}</td>'
                    f'<td>{html_module.escape(q.banca) or "—"}</td>'
                    f'<td class="num">{html_module.escape(q.ano) or "—"}</td>'
                    f'<td class="num">{q.score_classificacao}</td>'
                    f'<td class="pv">{preview}…</td></tr>'
                )
        if not rows:
            return '<p style="color:#999">Nenhuma questão extraída.</p>'
        return (f'<div class="tw"><table class="sort" id="tq">'
                f'<thead><tr><th>Nº</th><th>Área</th><th>Gab.</th>'
                f'<th>Alts</th><th>Banca</th><th>Ano</th><th>Score</th><th>Prévia</th>'
                f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')

    def _dup_section(self, qpa: Dict[str, List["Questao"]], dr: Optional[Dict]) -> str:
        if not dr:
            return ""
        total = dr.get("duplicatas_exatas", 0) + dr.get("pares_fuzzy", 0)
        if total == 0:
            return '<section><h2>Duplicatas</h2><p style="color:#59a14f">✓ Nenhuma duplicata detectada.</p></section>'

        todas: List["Questao"] = [q for qs in qpa.values() for q in qs]
        blocos: List[str] = []

        for grp in dr.get("grupos_exatos", []):
            idxs = grp["indices"]
            if len(idxs) < 2 or max(idxs) >= len(todas):
                continue
            qa, qb = todas[idxs[0]], todas[idxs[1]]
            ha, hb = self._diff_html(qa.texto, qb.texto)
            blocos.append(
                f'<div class="dp"><div class="db de">Duplicata Exata</div>'
                f'<div class="dc">'
                f'<div class="dcol"><strong>Q{html_module.escape(qa.numero)}</strong><pre>{ha}</pre></div>'
                f'<div class="dcol"><strong>Q{html_module.escape(qb.numero)}</strong><pre>{hb}</pre></div>'
                f'</div></div>'
            )

        for par in dr.get("pares_fuzzy_detalhe", [])[:10]:
            i, j, score = par["i"], par["j"], par["score"]
            if max(i, j) >= len(todas):
                continue
            qa, qb = todas[i], todas[j]
            ha, hb = self._diff_html(qa.texto, qb.texto)
            blocos.append(
                f'<div class="dp"><div class="db df">Similar — {score:.1%}</div>'
                f'<div class="dc">'
                f'<div class="dcol"><strong>Q{html_module.escape(qa.numero)}</strong><pre>{ha}</pre></div>'
                f'<div class="dcol"><strong>Q{html_module.escape(qb.numero)}</strong><pre>{hb}</pre></div>'
                f'</div></div>'
            )

        badge = f'<span class="bc">{total}</span>'
        return f'<section><h2>Duplicatas {badge}</h2>{"".join(blocos)}</section>'

    def _log_table(self, results: List[CleaningResult]) -> str:
        rows = "".join(
            f'<tr class="{"er" if r.erro else ""}"><td>{html_module.escape(r.arquivo)}</td>'
            f'<td>{html_module.escape(r.encoding_original)}</td>'
            f'<td class="num">{r.chars_antes - r.chars_depois:+,}</td>'
            f'<td>{"❌ " + html_module.escape(r.erro) if r.erro else "✓ " + html_module.escape("; ".join(r.limpezas[:3]))}</td></tr>'
            for r in results
        )
        return (f'<table class="sort">'
                f'<thead><tr><th>Arquivo</th><th>Encoding</th><th>Δ chars</th><th>Limpezas</th></tr></thead>'
                f'<tbody>{rows}</tbody></table>')

    def _diff_html(self, a: str, b: str, max_chars: int = 500) -> Tuple[str, str]:
        a, b = a[:max_chars], b[:max_chars]
        sm   = SequenceMatcher(None, a, b, autojunk=False)
        ra: List[str] = []
        rb: List[str] = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            ca = html_module.escape(a[i1:i2])
            cb = html_module.escape(b[j1:j2])
            if op == "equal":
                ra.append(ca); rb.append(cb)
            elif op == "replace":
                ra.append(f'<mark class="dl">{ca}</mark>')
                rb.append(f'<mark class="in">{cb}</mark>')
            elif op == "delete":
                ra.append(f'<mark class="dl">{ca}</mark>')
            elif op == "insert":
                rb.append(f'<mark class="in">{cb}</mark>')
        return "".join(ra), "".join(rb)

    # ── CSS ──────────────────────────────────────────────────────────────────

    def _css(self) -> str:
        return """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     font-size:14px;color:#222;background:#f7f8fa;line-height:1.6}
header{background:#1a2236;color:#fff;padding:20px 28px}
header h1{font-size:1.35rem;font-weight:700}
header .sub{margin-top:4px;opacity:.7;font-size:12px}
code{background:#e8ebf4;padding:1px 5px;border-radius:3px;font-size:12px}
section{max-width:1160px;margin:20px auto;padding:0 20px}
h2{font-size:1.05rem;font-weight:700;margin-bottom:12px;
   border-bottom:2px solid #e0e4ef;padding-bottom:5px;color:#1a2236}
.row{display:flex;gap:28px;flex-wrap:wrap;align-items:flex-start}
/* cards */
.cards{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:4px}
.card{background:#fff;border:1px solid #dde2ef;border-radius:10px;
      padding:16px 22px;min-width:130px;text-align:center}
.ct{font-size:11px;color:#666;font-weight:600;text-transform:uppercase}
.cv{font-size:1.9rem;font-weight:800;color:#1a2236;margin:3px 0}
.cl{font-size:11px;color:#999}
/* pie */
.pie-wrap{display:flex;gap:20px;align-items:center;flex-wrap:wrap}
.legend{display:flex;flex-direction:column;gap:5px}
.li{display:flex;align-items:center;gap:7px;font-size:12px}
.ld{width:11px;height:11px;border-radius:2px;flex-shrink:0}
/* bar */
.bar{height:9px;background:#e8ebf4;border-radius:5px;min-width:70px}
.bf{height:9px;background:#4e79a7;border-radius:5px}
/* tables */
.tw{overflow-x:auto}
table{width:100%;border-collapse:collapse;background:#fff;
      border:1px solid #dde2ef;border-radius:8px;overflow:hidden;margin-bottom:4px}
th{background:#1a2236;color:#fff;padding:9px 11px;text-align:left;
   cursor:pointer;user-select:none;font-size:12px;white-space:nowrap}
th:hover{background:#2d3f5e}
th.asc::after{content:" ▲";font-size:9px}
th.desc::after{content:" ▼";font-size:9px}
td{padding:7px 11px;border-bottom:1px solid #eef0f6;vertical-align:top}
tr:last-child td{border-bottom:none}
tr:hover td{background:#f0f3fb}
tr.er td{background:#fff0f0}
.num{text-align:center;white-space:nowrap}
.pv{max-width:320px;color:#555;font-size:12px}
.gab{font-weight:700;color:#4e79a7}
/* filtros */
.filtros{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;margin-bottom:10px}
.filtros label{display:flex;flex-direction:column;font-size:11px;
               font-weight:600;color:#666;gap:3px}
.filtros select,.filtros button{padding:5px 9px;border:1px solid #cdd2e0;
   border-radius:6px;font-size:13px;background:#fff;cursor:pointer}
.filtros button{background:#1a2236;color:#fff;border-color:#1a2236}
.filtros button:hover{background:#2d3f5e}
/* duplicatas */
.dp{background:#fff;border:1px solid #dde2ef;border-radius:8px;margin-bottom:14px;overflow:hidden}
.db{padding:5px 12px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase}
.de{background:#ffeaea;color:#c0392b}
.df{background:#fff4e0;color:#a0620a}
.dc{display:grid;grid-template-columns:1fr 1fr}
.dcol{padding:10px 14px;border-top:1px solid #eef0f6;font-size:12px}
.dcol:first-child{border-right:1px solid #eef0f6}
.dcol pre{white-space:pre-wrap;font-family:inherit;margin-top:5px;
          max-height:160px;overflow-y:auto;color:#333}
mark.dl{background:#ffd7d7;border-radius:2px}
mark.in{background:#d4f4dd;border-radius:2px}
.bc{background:#e15759;color:#fff;border-radius:99px;
    padding:1px 7px;font-size:12px;font-weight:700;margin-left:7px}
@media(max-width:680px){.dc{grid-template-columns:1fr}.dcol:first-child{border-right:none}}"""

    # ── JS ───────────────────────────────────────────────────────────────────

    def _js(self) -> str:
        # raw string evita que \- e \d sejam interpretados como escapes Python
        return r"""
document.querySelectorAll('table.sort').forEach(function(tbl){
  tbl.querySelectorAll('th').forEach(function(th,ci){
    th.addEventListener('click',function(){
      var asc=!th.classList.contains('asc');
      tbl.querySelectorAll('th').forEach(function(h){h.classList.remove('asc','desc');});
      th.classList.add(asc?'asc':'desc');
      var tb=tbl.querySelector('tbody');
      Array.from(tb.querySelectorAll('tr')).sort(function(a,b){
        var va=a.cells[ci]?a.cells[ci].innerText.trim():'';
        var vb=b.cells[ci]?b.cells[ci].innerText.trim():'';
        var na=parseFloat(va.replace(/[^\d.\-]/g,'')),nb=parseFloat(vb.replace(/[^\d.\-]/g,''));
        if(!isNaN(na)&&!isNaN(nb))return asc?na-nb:nb-na;
        return asc?va.localeCompare(vb,'pt'):vb.localeCompare(va,'pt');
      }).forEach(function(r){tb.appendChild(r);});
    });
  });
});
function filtrar(){
  var fa=document.getElementById('fa'),fb=document.getElementById('fb'),fy=document.getElementById('fy');
  var va=fa?fa.value:'',vb=fb?fb.value:'',vy=fy?fy.value:'';
  var tq=document.getElementById('tq');
  if(!tq)return;
  tq.querySelectorAll('tbody tr').forEach(function(tr){
    tr.style.display=(!va||tr.dataset.area===va)&&(!vb||tr.dataset.banca===vb)&&(!vy||tr.dataset.ano===vy)?'':'none';
  });
}
function limpar(){
  ['fa','fb','fy'].forEach(function(id){var e=document.getElementById(id);if(e)e.value='';});
  filtrar();
}"""


# ─────────────────────────────────────────────────────────────────────────────
# ÁREAS JURÍDICAS  (10 áreas ativas — JUR-001 … JUR-015 de regex.md)
# ─────────────────────────────────────────────────────────────────────────────
AREAS: Dict[str, Dict] = {
    # ── áreas originais ──────────────────────────────────────────────────────
    "direito_tributario": {
        "titulo": "Direito Tributário",
        "headers": ["DIREITO TRIBUTARIO","TRIBUTARIO","DIREITO TRIBUTÁRIO"],
        "keywords": ["icms","iptu","iss","ipva","ipi","ir","cofins","pis","csll","ctn",
                     "tributario","tributário","imposto","tributo","fisco",
                     "contribuinte","lançamento","obrigação tributária"],
    },
    "direito_administrativo": {
        "titulo": "Direito Administrativo",
        "headers": ["DIREITO ADMINISTRATIVO","ADMINISTRATIVO"],
        "keywords": ["licitacao","licitação","servidor publico","servidor público",
                     "improbidade","concurso","autarquia","fundação pública",
                     "ato administrativo","poder de polícia","administração pública",
                     "lei 8112","lei 8666","lei 14133"],
    },
    "direito_civil": {
        "titulo": "Direito Civil",
        "headers": ["DIREITO CIVIL","CIVIL"],
        "keywords": ["codigo civil","código civil","contratos","obrigacoes","obrigações",
                     "familia","família","propriedade","posse","usucapião",
                     "sucessões","responsabilidade civil","dano moral"],
    },
    "direito_penal": {
        "titulo": "Direito Penal",
        "headers": ["DIREITO PENAL","PENAL"],
        "keywords": ["codigo penal","código penal","crime","pena","homicidio","homicídio",
                     "furto","roubo","estelionato","peculato","corrupção",
                     "lavagem de dinheiro","tráfico","reclusão"],
    },
    "processual": {
        "titulo": "Direito Processual",
        "headers": ["PROCESSO","PROCESSUAL","CPC","CPP"],
        "keywords": ["recurso","apelacao","apelação","embargos","sentenca","sentença",
                     "liminar","tutela","mandado de segurança","habeas corpus",
                     "agravo","cpc","cpp","prazo processual"],
    },
    # ── novas áreas (JUR-011 … JUR-015) ─────────────────────────────────────
    "direito_constitucional": {
        "titulo": "Direito Constitucional",
        "headers": ["DIREITO CONSTITUCIONAL","CONSTITUCIONAL"],
        "keywords": ["constituição","constituicao","direitos fundamentais",
                     "mandado de injunção","controle de constitucionalidade",
                     "adi","adc","adpf","stf","cf/88","cf 88",
                     "emenda constitucional","cláusula pétrea","separação de poderes"],
    },
    "direito_trabalho": {
        "titulo": "Direito do Trabalho",
        "headers": ["DIREITO DO TRABALHO","TRABALHISTA","CLT","TRABALHO"],
        "keywords": ["clt","empregado","empregador","fgts","hora extra",
                     "jornada de trabalho","rescisão contratual","tst",
                     "reclamatória trabalhista","salário","férias","aviso prévio",
                     "consolidação das leis do trabalho"],
    },
    "direito_previdenciario": {
        "titulo": "Direito Previdenciário",
        "headers": ["DIREITO PREVIDENCIÁRIO","PREVIDENCIÁRIO","PREVIDENCIA","PREVIDÊNCIA"],
        "keywords": ["inss","previdência social","previdencia social","aposentadoria",
                     "benefício previdenciário","rgps","rpps",
                     "contribuição previdenciária","período de carência",
                     "loas","auxílio-doença","salário-maternidade"],
    },
    "direito_empresarial": {
        "titulo": "Direito Empresarial",
        "headers": ["DIREITO EMPRESARIAL","EMPRESARIAL","COMERCIAL","DIREITO COMERCIAL"],
        "keywords": ["sociedade limitada","sociedade anônima","ltda","s.a.","falência",
                     "recuperação judicial","empresário individual","eireli",
                     "contrato social","dissolução","código comercial","debenture"],
    },
    "direito_financeiro": {
        "titulo": "Direito Financeiro / LRF",
        "headers": ["DIREITO FINANCEIRO","LRF","RESPONSABILIDADE FISCAL","FINANCEIRO"],
        "keywords": ["lrf","lei de responsabilidade fiscal","lei complementar 101",
                     "orçamento","loa","ldo","ppa","déficit fiscal",
                     "superávit","receita pública","despesa pública",
                     "execução orçamentária","tesouro nacional"],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# QUESTÃO
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Questao:
    numero: str
    texto: str
    area: str = ""
    gabarito: str = ""
    tipo_gabarito: str = ""
    banca: str = ""
    ano: str = ""
    justificativa: bool = False
    alternativas: Dict[str, str] = field(default_factory=dict)
    score_classificacao: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# QUESTION PROCESSOR
# ─────────────────────────────────────────────────────────────────────────────
class QuestionProcessor:
    """Extrai, classifica e enriquece questões jurídicas de Markdown."""

    QUESTION_PATTERN = re.compile(
        r"(?:QUESTAO|Quest[^\d]+|QUESTÃO|Item|item|^\s*\d+[\.\)\-])\s*(\d+)",
        re.MULTILINE | re.IGNORECASE,
    )

    def __init__(self, areas: Optional[Dict] = None, extrair_gabarito: bool = True):
        self.areas         = areas or AREAS
        self.gab_extractor = GabaritoExtractor() if extrair_gabarito else None
        self.alt_extractor = AlternativasExtractor()

    def extract(self, content: str) -> List[str]:
        content = re.sub(r"\r\n", "\n", content)
        content = re.sub(r"\n{3,}", "\n\n", content)
        questions: List[str] = []
        matches = list(self.QUESTION_PATTERN.finditer(content))
        for i, m in enumerate(matches):
            start  = max(0, m.start() - 30)
            end    = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            q_text = content[start:end].strip()
            q_text = self._clean_header(q_text)
            if 50 < len(q_text) < 10_000:
                questions.append(q_text)
        return questions

    def classify(self, questions: List[str]) -> Dict[str, List[Questao]]:
        collected: Dict[str, List[Questao]] = {k: [] for k in self.areas}
        for q_text in questions:
            q_lower = q_text.lower()
            best_score, best_area = 0, None
            for ak, cfg in self.areas.items():
                score  = sum(2 for kw in cfg["keywords"] if kw.lower() in q_lower)
                score += sum(10 for h  in cfg["headers"]  if h.lower()  in q_lower)
                if score > best_score:
                    best_score, best_area = score, ak
            if best_area and best_score >= 3:
                m = self.QUESTION_PATTERN.search(q_text)
                q = Questao(numero=m.group(1) if m else "?",
                            texto=q_text, area=best_area,
                            score_classificacao=best_score)
                if self.gab_extractor:
                    meta       = self.gab_extractor.extract(q_text)
                    q.gabarito      = meta["gabarito"]
                    q.tipo_gabarito = meta["tipo"]
                    q.banca         = meta["banca"]
                    q.ano           = meta["ano"]
                    q.justificativa = meta["justificativa_presente"] == "sim"
                q.alternativas = self.alt_extractor.extract(q_text)
                collected[best_area].append(q)
        return collected

    def _clean_header(self, text: str) -> str:
        for i, ln in enumerate(text.split("\n")):
            if re.search(r"^##\s*Quest", ln, re.IGNORECASE):
                return "\n".join(text.split("\n")[i:]).strip()
        return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# INTERACTIVE REVIEWER
# ─────────────────────────────────────────────────────────────────────────────
class InteractiveReviewer:
    """
    Revisão interativa de questões no terminal após a extração.

    Comandos por questão:
      [s] Confirmar   [n] Descartar   [r] Reclassificar
      [p] Pular       [q] Encerrar (aprova restantes automaticamente)
    """

    def revisar(self, classificadas: Dict[str, List[Questao]]) -> Dict[str, List[Questao]]:
        if not sys.stdin.isatty():
            logger.warning("[INTERATIVO] stdin não é terminal — revisão ignorada.")
            return classificadas

        total     = sum(len(qs) for qs in classificadas.values())
        aprovadas: Dict[str, List[Questao]] = {k: [] for k in AREAS}
        idx       = 0
        area_keys = list(classificadas.keys())
        areas_lst = list(AREAS.items())

        print(f"\n{'='*64}")
        print(f"  REVISÃO INTERATIVA — {total} questão(ões)")
        print(f"  [s]im  [n]ão  [r]eclassificar  [p]ular  [q]uit")
        print(f"{'='*64}\n")

        for area_key in area_keys:
            questoes = classificadas[area_key]
            for qi, q in enumerate(questoes):
                idx += 1
                self._exibir(q, area_key, idx, total)
                while True:
                    try:
                        resp = input("  → ").strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        resp = "q"

                    if resp == "s":
                        aprovadas[area_key].append(q); print("  ✓ Confirmada\n"); break
                    elif resp == "n":
                        print("  ✗ Descartada\n"); break
                    elif resp == "p":
                        aprovadas[area_key].append(q); print("  → Pulada\n"); break
                    elif resp == "r":
                        nova = self._escolher_area(areas_lst)
                        if nova:
                            q.area = nova
                            aprovadas.setdefault(nova, []).append(q)
                            print(f"  ✎ → {AREAS[nova]['titulo']}\n")
                        break
                    elif resp == "q":
                        print("\n  Encerrando — restantes aprovadas automaticamente.")
                        aprovadas[area_key].extend(questoes[qi + 1:])
                        for ak in area_keys[area_keys.index(area_key) + 1:]:
                            aprovadas[ak].extend(classificadas[ak])
                        tot_ap = sum(len(v) for v in aprovadas.values())
                        print(f"  Total aprovadas: {tot_ap}/{total}\n")
                        return aprovadas
                    else:
                        print("  ? Use: s / n / r / p / q")

        tot_ap = sum(len(v) for v in aprovadas.values())
        print(f"\n  Revisão concluída: {tot_ap}/{total} aprovadas.\n")
        return aprovadas

    def _exibir(self, q: Questao, area_key: str, idx: int, total: int):
        titulo = AREAS.get(area_key, {}).get("titulo", area_key)
        print(f"  ── Q{q.numero}  [{idx}/{total}]  {titulo}  (score: {q.score_classificacao})")
        parts = list(filter(None, [q.banca, q.ano,
                                   f"Gab: {q.gabarito}" if q.gabarito else "",
                                   f"Alts: {','.join(q.alternativas.keys())}" if q.alternativas else ""]))
        if parts:
            print(f"     {' · '.join(parts)}")
        preview = q.texto[:420].replace("\n", " ")
        print(f"\n  {preview}{'…' if len(q.texto) > 420 else ''}\n")

    def _escolher_area(self, areas_lst: List[Tuple[str, Dict]]) -> Optional[str]:
        print("\n  Áreas disponíveis:")
        for i, (key, cfg) in enumerate(areas_lst, 1):
            print(f"    {i:2}. {cfg['titulo']}")
        print("     0. Cancelar")
        try:
            n = int(input("  Número: ").strip())
            if 1 <= n <= len(areas_lst):
                return areas_lst[n - 1][0]
        except (ValueError, EOFError):
            pass
        return None


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────────────────
class PipelineOrchestrator:
    """Orquestra encoding → limpeza → extração → gabarito → duplicatas → relatório."""

    def __init__(
        self,
        base_dir: str,
        dry_run: bool = False,
        sufixo: str = "_limpo",
        in_place: bool = False,
        extrair_gabarito: bool = True,
        dup_threshold: float = 0.85,
    ):
        self.base_dir     = Path(base_dir)
        self.dry_run      = dry_run
        self.sufixo       = sufixo
        self.in_place     = in_place
        self.cleaner      = MarkdownCleaner()
        self.q_proc       = QuestionProcessor(extrair_gabarito=extrair_gabarito)
        self.dup_det      = DuplicateDetector(threshold=dup_threshold)
        self.html_gen     = HTMLReportGenerator()
        self.interactive  = InteractiveReviewer()
        self.results: List[CleaningResult] = []

    # ── run ──────────────────────────────────────────────────────────────────

    def run(
        self,
        extrair_questoes: bool = True,
        detectar_duplicatas: bool = True,
        interactive: bool = False,
        relatorio_html: Optional[str] = None,
    ) -> List[CleaningResult]:
        self._banner()
        md_files = self._coletar()
        if not md_files:
            print("  [AVISO] Nenhum arquivo .md encontrado."); return []
        print(f"  [INFO] {len(md_files)} arquivo(s)\n")

        for fp in md_files:
            self.results.append(self._processar(fp))

        qpa: Dict[str, List[Questao]] = {k: [] for k in AREAS}
        dr:  Optional[Dict] = None

        if extrair_questoes:
            qpa = self._extrair(md_files, interactive=interactive)
            if detectar_duplicatas:
                dr = self._duplicatas(qpa)

        self._relatorio_final()

        if relatorio_html:
            html = self.html_gen.generate(self.results, qpa, dr, str(self.base_dir))
            Path(relatorio_html).write_text(html, encoding="utf-8")
            print(f"  [HTML] {relatorio_html}")

        return self.results

    # ── watch (com debounce) ─────────────────────────────────────────────────

    def watch(
        self,
        interval: int = 2,
        debounce: float = 5.0,
        extrair_questoes: bool = True,
        detectar_duplicatas: bool = True,
        interactive: bool = False,
        relatorio_html: Optional[str] = None,
    ):
        """
        Monitora alterações e só processa arquivo quando ele fica estável
        por `debounce` segundos — evita duplo disparo em editores que salvam
        via arquivo temporário → rename (ex: VSCode, Vim).
        """
        mtimes:  Dict[str, float] = {}
        pending: Dict[str, float] = {}  # path → hora da última mudança

        for f in self._coletar():
            mtimes[str(f)] = f.stat().st_mtime

        print(f"\n{'='*62}")
        print(f"  WATCH MODE — {self.base_dir}")
        print(f"  Polling: {interval}s  |  Debounce: {debounce}s  |  Ctrl+C para parar")
        print(f"{'='*62}\n")

        try:
            while True:
                time.sleep(interval)
                now = time.time()

                for f in self._coletar():
                    key = str(f)
                    try:
                        mt = f.stat().st_mtime
                    except OSError:
                        continue
                    prev = mtimes.get(key)
                    if prev is None:
                        mtimes[key] = mt        # novo arquivo — apenas registra
                    elif prev != mt:
                        mtimes[key] = mt
                        pending[key] = now      # marca como pendente

                # Arquivos estáveis há >= debounce segundos
                prontos = [fp for fp, t in list(pending.items()) if now - t >= debounce]
                if prontos:
                    ts = datetime.now().strftime("%H:%M:%S")
                    print(f"\n[{ts}] {len(prontos)} arquivo(s) prontos para processar…")
                    changed: List[Path] = []
                    for fp in prontos:
                        del pending[fp]
                        p = Path(fp)
                        self.results.append(self._processar(p))
                        changed.append(p)

                    qpa: Dict[str, List[Questao]] = {k: [] for k in AREAS}
                    dr: Optional[Dict] = None
                    if extrair_questoes:
                        qpa = self._extrair(changed, interactive=interactive)
                        if detectar_duplicatas:
                            dr = self._duplicatas(qpa)
                    if relatorio_html:
                        html = self.html_gen.generate(self.results, qpa, dr, str(self.base_dir))
                        Path(relatorio_html).write_text(html, encoding="utf-8")
                        print(f"  [HTML] Atualizado: {relatorio_html}")

                if pending:
                    print(f"  [{len(pending)} arquivo(s) aguardando debounce…]", end="\r")

        except KeyboardInterrupt:
            print("\n\n[WATCH] Encerrado.")

    # ── privados ─────────────────────────────────────────────────────────────

    def _banner(self):
        modo = "IN-PLACE (+.bak)" if self.in_place else ("DRY-RUN" if self.dry_run else "PRODUÇÃO")
        print(f"\n{'='*62}")
        print(f"  MARKDOWN CLEANER  v1.2.0")
        print(f"  Dir : {self.base_dir}  |  Modo: {modo}")
        print(f"{'='*62}\n")

    def _coletar(self) -> List[Path]:
        return [
            f for f in self.base_dir.glob("*.md")
            if not f.name.startswith("questoes_")
            and not f.name.startswith("relatorio")
            and not f.name.endswith(f"{self.sufixo}.md")
        ]

    def _processar(self, filepath: Path) -> CleaningResult:
        r = CleaningResult(arquivo=filepath.name)
        print(f"  [ARQ] {filepath.name}")
        try:
            enc, content = EncodingDetector.detect_and_correct(str(filepath))
            r.encoding_original = enc
            r.chars_antes  = len(content)
            r.linhas_antes = content.count("\n")
            if enc not in ("utf-8", "utf-8-sig"):
                r.limpezas.append(f"Encoding: {enc} → utf-8")
                print(f"        [ENC] {enc} → utf-8")
            cleaned, limpezas = self.cleaner.clean(content)
            r.limpezas.extend(limpezas)
            r.chars_depois  = len(cleaned)
            r.linhas_depois = cleaned.count("\n")
            for lp in limpezas:
                print(f"        [FIX] {lp}")
            if not self.dry_run and cleaned.strip():
                if self.in_place:
                    bak = Path(str(filepath) + ".bak")
                    filepath.rename(bak)
                    filepath.write_text(cleaned, encoding="utf-8")
                    r.salvo = True; r.backup = bak.name
                    print(f"        [OK] Sobrescrito (.bak → {bak.name})")
                else:
                    out = filepath.parent / f"{filepath.stem}{self.sufixo}.md"
                    out.write_text(cleaned, encoding="utf-8")
                    r.salvo = True
                    print(f"        [OK] → {out.name}")
            elif self.dry_run:
                print("        [DRY] Não salvo")
        except Exception as e:
            r.erro = str(e); print(f"        [ERRO] {e}")
        return r

    def _extrair(
        self,
        md_files: List[Path],
        interactive: bool = False,
    ) -> Dict[str, List[Questao]]:
        print(f"\n{'='*62}")
        print(f"  FASE 2: EXTRAÇÃO DE QUESTÕES ({len(AREAS)} áreas)")
        print(f"{'='*62}\n")

        if not self.dry_run:
            for f in self.base_dir.glob("questoes_*.md"):
                f.unlink()

        todas: Dict[str, List[Questao]] = {k: [] for k in AREAS}

        for filepath in md_files:
            print(f"  [ARQ] {filepath.name}")
            try:
                _, content = EncodingDetector.detect_and_correct(str(filepath))
            except Exception as e:
                print(f"        [ERRO] {e}"); continue
            questions = self.q_proc.extract(content)
            if not questions:
                print("        [INFO] Sem questões"); continue
            print(f"        [QTD] {len(questions)}")
            for ak, qs in self.q_proc.classify(questions).items():
                todas[ak].extend(qs)

        # Revisão interativa (antes de salvar em disco)
        if interactive:
            todas = self.interactive.revisar(todas)

        # Persistência por área
        for area_key, questoes in todas.items():
            if not questoes or self.dry_run:
                continue
            out = self.base_dir / f"questoes_{area_key}.md"
            with open(out, "w", encoding="utf-8") as f:
                f.write(f"# {AREAS[area_key]['titulo']}\n\n")
                f.write("> Extraídas pelo Markdown Cleaner v1.2.0\n\n---\n\n")
                for q in questoes:
                    f.write(f"### Questão {q.numero}\n\n")
                    meta = []
                    if q.gabarito: meta.append(f"**Gabarito:** {q.gabarito}")
                    if q.banca:    meta.append(f"**Banca:** {q.banca}")
                    if q.ano:      meta.append(f"**Ano:** {q.ano}")
                    if q.score_classificacao: meta.append(f"**Score:** {q.score_classificacao}")
                    if meta:
                        f.write("> " + " · ".join(meta) + "\n\n")
                    if q.alternativas:
                        f.write("**Alternativas:**\n\n")
                        for lt, tx in q.alternativas.items():
                            f.write(f"- **{lt})** {tx}\n")
                        f.write("\n")
                    f.write(f"{q.texto}\n\n---\n\n")

            com_gab = sum(1 for q in questoes if q.gabarito)
            com_alt = sum(1 for q in questoes if q.alternativas)
            print(f"  [ÁREA] {AREAS[area_key]['titulo']:<38}"
                  f" {len(questoes):>3}q  |  {com_gab} gab  |  {com_alt} alts")

        return todas

    def _duplicatas(self, qpa: Dict[str, List[Questao]]) -> Dict:
        print(f"\n{'='*62}")
        print(f"  FASE 3: DETECÇÃO DE DUPLICATAS")
        print(f"{'='*62}\n")
        todas = [q for qs in qpa.values() for q in qs]
        if len(todas) < 2:
            print("  Menos de 2 questões — verificação ignorada.")
            return {"duplicatas_exatas": 0, "pares_fuzzy": 0,
                    "grupos_exatos": [], "pares_fuzzy_detalhe": []}
        labels = [f"Q{q.numero}/{AREAS.get(q.area,{}).get('titulo',q.area)}" for q in todas]
        rel    = self.dup_det.report([q.texto for q in todas], labels)
        ne, nf = rel["duplicatas_exatas"], rel["pares_fuzzy"]
        if ne == 0 and nf == 0:
            print("  ✓ Nenhuma duplicata detectada.")
        else:
            if ne:
                print(f"  Duplicatas exatas : {ne}")
                for g in rel["grupos_exatos"]:
                    print(f"    hash {g['hash']}… → {g['labels']}")
            if nf:
                print(f"  Similares (>={self.dup_det.threshold:.0%}) : {nf}")
                for p in rel["pares_fuzzy_detalhe"][:5]:
                    print(f"    {p['label_i']}  ≈  {p['label_j']}  [{p['score']:.1%}]")
                if nf > 5:
                    print(f"    … +{nf-5} par(es)")
        return rel

    def _relatorio_final(self):
        print(f"\n{'='*62}  RELATÓRIO FINAL")
        total  = len(self.results)
        erros  = sum(1 for r in self.results if r.erro)
        salvos = sum(1 for r in self.results if r.salvo)
        baks   = sum(1 for r in self.results if r.backup)
        lps    = sum(len(r.limpezas) for r in self.results)
        delta  = sum(r.chars_antes - r.chars_depois for r in self.results if not r.erro)
        print(f"  Arquivos: {total}  |  Salvos: {salvos}"
              f"{'  |  Backups: '+str(baks) if baks else ''}  |  Erros: {erros}")
        print(f"  Limpezas: {lps}  |  Chars removidos: {delta:,}\n")

    def salvar_relatorio_json(self, output_path: str):
        data = {"timestamp": datetime.now().isoformat(), "versao": "1.2.0",
                "diretorio": str(self.base_dir), "dry_run": self.dry_run,
                "in_place": self.in_place,
                "arquivos": [asdict(r) for r in self.results]}
        Path(output_path).write_text(json.dumps(data, indent=2, ensure_ascii=False), "utf-8")
        print(f"  [JSON] {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="md_cleaner.py",
        description="Pipeline de limpeza e extração jurídica para Markdown — v1.2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python md_cleaner.py /pasta
  python md_cleaner.py /pasta --in-place
  python md_cleaner.py /pasta --interactive
  python md_cleaner.py /pasta --relatorio-html relatorio.html
  python md_cleaner.py /pasta --watch --watch-debounce 5
  python md_cleaner.py /pasta --watch --in-place --relatorio-html rel.html
  python md_cleaner.py /pasta --dup-threshold 0.90 --relatorio dados.json
        """,
    )
    parser.add_argument("diretorio",      nargs="?", default=".", help="Diretório com .md")
    parser.add_argument("--in-place",     action="store_true", help="Sobrescreve original com .bak")
    parser.add_argument("--dry-run",      action="store_true", help="Preview sem salvar")
    parser.add_argument("--interactive",  action="store_true", help="Revisão questão a questão")
    parser.add_argument("--sem-questoes", action="store_true", help="Pula extração")
    parser.add_argument("--sem-gabarito", action="store_true", help="Pula gabarito")
    parser.add_argument("--sem-duplicatas", action="store_true", help="Pula detecção de duplicatas")
    parser.add_argument("--dup-threshold", type=float, default=0.85, metavar="0-1")
    parser.add_argument("--watch",        action="store_true", help="Modo watch (Ctrl+C para parar)")
    parser.add_argument("--watch-interval", type=int,   default=2,   metavar="SEG")
    parser.add_argument("--watch-debounce", type=float, default=5.0, metavar="SEG",
                        help="Segundos de estabilidade antes de processar (padrão: 5)")
    parser.add_argument("--relatorio",       metavar="ARQ", help="Relatório JSON")
    parser.add_argument("--relatorio-html",  metavar="ARQ", help="Relatório HTML interativo")
    parser.add_argument("--sufixo",       default="_limpo")
    parser.add_argument("-v","--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    if args.in_place and args.dry_run:
        parser.error("--in-place e --dry-run são mutuamente exclusivos.")
    if args.interactive and args.watch:
        parser.error("--interactive e --watch não podem ser combinados.")

    base_dir = Path(args.diretorio).resolve()
    if not base_dir.exists():
        print(f"[ERRO] Diretório não encontrado: {base_dir}"); sys.exit(1)

    orch = PipelineOrchestrator(
        base_dir,
        dry_run          = args.dry_run,
        sufixo           = args.sufixo,
        in_place         = args.in_place,
        extrair_gabarito = not args.sem_gabarito,
        dup_threshold    = args.dup_threshold,
    )

    if args.watch:
        orch.watch(
            interval         = args.watch_interval,
            debounce         = args.watch_debounce,
            extrair_questoes = not args.sem_questoes,
            detectar_duplicatas = not args.sem_duplicatas,
            relatorio_html   = args.relatorio_html,
        )
    else:
        orch.run(
            extrair_questoes    = not args.sem_questoes,
            detectar_duplicatas = not args.sem_duplicatas,
            interactive         = args.interactive,
            relatorio_html      = args.relatorio_html,
        )

    if args.relatorio:
        orch.salvar_relatorio_json(args.relatorio)


if __name__ == "__main__":
    main()
