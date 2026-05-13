"""
Módulo de validação do core.

Exporta validadores disponíveis.
"""

from .pdf_validator import PDFValidator, validate_pdf

__all__ = [
    "PDFValidator",
    "validate_pdf",
]
