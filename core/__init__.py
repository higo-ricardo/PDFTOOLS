"""
Módulo core - Lógica de negócios para processamento de PDFs.
"""

from .pdf_extractor import PDFTextExtractor
from .pdf_compressor import PDFCompressor, CompressionLevel

__all__ = ['PDFTextExtractor', 'PDFCompressor', 'CompressionLevel']
