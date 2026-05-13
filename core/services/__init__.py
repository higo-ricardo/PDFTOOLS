"""
Pacote de serviços do PDF Tools.

Módulos:
- extractor_service: Extração de texto com streaming
- pdf_splitter: Divisão de PDFs (páginas, bookmarks, intervalos, específicas)
- pdf_merger: Mesclagem de PDFs com preview e reordenação
- cleaner_service: Limpeza de arquivos txt, md, docx (encoding + 12 técnicas)
- image_extractor: Extração de imagens de PDFs (PNG, JPG, TIFF) com metadados
"""

from core.services.extractor_service import StreamingPDFExtractor, PDFTextExtractor
from core.services.pdf_splitter import (
    PDFSplitterService, 
    PagePreview, 
    SplitResult,
    BookmarkInfo
)
from core.services.pdf_merger import PDFMergerService, MergeResult, PDFFileInfo
from core.services.cleaner_service import FileCleanerService, EncodingDetector, TextCleaner
from core.services.image_extractor import ImageExtractorService, ExtractionResult, ImageMetadata

__all__ = [
    "StreamingPDFExtractor",
    "PDFTextExtractor",
    "PDFSplitterService",
    "PagePreview",
    "SplitResult",
    "BookmarkInfo",
    "PDFMergerService",
    "MergeResult",
    "PDFFileInfo",
    "FileCleanerService",
    "EncodingDetector",
    "TextCleaner",
    "ImageExtractorService",
    "ExtractionResult",
    "ImageMetadata",
]
