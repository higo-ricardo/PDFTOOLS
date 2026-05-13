"""
Estrategia de nomeacao para arquivos gerados.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional


class NamingStrategy:
    """
    Gera nomes no padrao: {base_name}_{sufixo}.{ext}

    Recursos:
    - Extensao normalizada (com/sem ponto na entrada).
    - Timestamp opcional no nome final.
    - Tratamento de conflito via sufixo incremental: _1, _2, _3...
    """

    def __init__(self, include_timestamp: bool = False, timestamp_format: str = "%Y%m%d_%H%M%S"):
        self.include_timestamp = include_timestamp
        self.timestamp_format = timestamp_format

    def build_filename(
        self,
        base_name: str,
        suffix: str,
        ext: str,
        include_timestamp: Optional[bool] = None,
    ) -> str:
        """
        Constroi nome base sem diretorio.

        Exemplo:
            relatorio_limpo.pdf
            relatorio_limpo_20260513_102530.pdf
        """
        ts_flag = self.include_timestamp if include_timestamp is None else include_timestamp

        clean_base = self._sanitize_part(base_name)
        clean_suffix = self._sanitize_part(suffix)
        clean_ext = self._normalize_ext(ext)

        stem = f"{clean_base}_{clean_suffix}"
        if ts_flag:
            stem = f"{stem}_{datetime.now().strftime(self.timestamp_format)}"

        return f"{stem}{clean_ext}"

    def build_path(
        self,
        directory: str | Path,
        base_name: str,
        suffix: str,
        ext: str,
        include_timestamp: Optional[bool] = None,
        resolve_conflict: bool = True,
    ) -> Path:
        """
        Monta caminho final com tratamento de conflito opcional.
        """
        directory_path = Path(directory)
        filename = self.build_filename(
            base_name=base_name,
            suffix=suffix,
            ext=ext,
            include_timestamp=include_timestamp,
        )
        candidate = directory_path / filename

        if not resolve_conflict:
            return candidate

        return self.resolve_conflict(candidate)

    def resolve_conflict(self, candidate: str | Path) -> Path:
        """
        Resolve conflitos de nome no filesystem.

        Se o arquivo existir, tenta:
            nome.ext
            nome_1.ext
            nome_2.ext
            ...
        """
        path = Path(candidate)
        if not path.exists():
            return path

        parent = path.parent
        stem = path.stem
        suffix = path.suffix

        counter = 1
        while True:
            conflict_candidate = parent / f"{stem}_{counter}{suffix}"
            if not conflict_candidate.exists():
                return conflict_candidate
            counter += 1

    @staticmethod
    def _normalize_ext(ext: str) -> str:
        normalized = (ext or "").strip()
        if not normalized:
            raise ValueError("A extensao nao pode ser vazia.")
        return normalized if normalized.startswith(".") else f".{normalized}"

    @staticmethod
    def _sanitize_part(value: str) -> str:
        text = (value or "").strip()
        if not text:
            raise ValueError("Nome base e sufixo nao podem ser vazios.")
        return text.replace("/", "_").replace("\\", "_")

