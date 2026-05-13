"""
Pacote de serviços do PDF Tools.

Módulos:
- extractor_service: Extração de texto com streaming
- pdf_splitter: Divisão de PDFs com preview
"""

from core.services.extractor_service import StreamingPDFExtractor, PDFTextExtractor
from core.services.pdf_splitter import PDFSplitterService, PagePreview, SplitResult

__all__ = [
    "StreamingPDFExtractor",
    "PDFTextExtractor",
    "PDFSplitterService",
    "PagePreview",
    "SplitResult",
]
