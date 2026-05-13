"""
Serviço de extração de imagens de PDFs.

Permite extrair imagens de arquivos PDF com opções de:
- Formatos: PNG, JPG, TIFF
- Manter resolução original ou redimensionar
- Extrair metadados das imagens
- Salvar em pasta organizada com nomes sequenciais

Autor: PDF Tools Team
Versão: 1.0.0
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


@dataclass
class ImageMetadata:
    """Metadados de uma imagem extraída."""
    width: int
    height: int
    colorspace: str
    bits_per_component: int
    xref: int
    page_number: int
    image_index: int
    file_size: int
    format: str
    dpi: Optional[float] = None
    creation_date: Optional[str] = None
    additional_info: Dict[str, Any] = None


@dataclass
class ExtractedImage:
    """Imagem extraída com seus dados."""
    filename: str
    path: str
    metadata: ImageMetadata
    image_data: bytes
    success: bool
    message: str


@dataclass
class ExtractionResult:
    """Resultado da extração de imagens."""
    output_dir: str
    total_images: int
    successful_extractions: int
    failed_extractions: int
    images: List[ExtractedImage]
    metadata_file: Optional[str]
    success: bool
    message: str


class ImageExtractorService:
    """
    Serviço para extração de imagens de PDFs.
    
    Responsável por:
    - Extrair imagens em diversos formatos
    - Manter ou redimensionar resolução
    - Extrair metadados
    - Organizar em pasta com nomes sequenciais
    """
    
    SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'tiff', 'tif']
    
    def __init__(self):
        """Inicializa o serviço de extração."""
        pass
    
    def extract_images(
        self,
        file_path: str,
        output_dir: Optional[str] = None,
        output_format: str = 'png',
        resize_to: Optional[Tuple[int, int]] = None,
        maintain_original_resolution: bool = True,
        extract_metadata: bool = True,
        progress_callback: Optional[callable] = None
    ) -> ExtractionResult:
        """
        Extrai todas as imagens de um PDF.
        
        Args:
            file_path: Caminho do arquivo PDF.
            output_dir: Diretório de saída (padrão: pasta '{nome_pdf}_imagens' no mesmo diretório).
            output_format: Formato de saída ('png', 'jpg', 'tiff').
            resize_to: Tupla (largura, altura) para redimensionar (opcional).
            maintain_original_resolution: Se True, mantém resolução original.
            extract_metadata: Se True, extrai e salva metadados.
            progress_callback: Callback para atualizar progresso (recebe porcentagem).
            
        Returns:
            ExtractionResult: Resultado da extração.
        """
        try:
            # Valida formato
            output_format = output_format.lower()
            if output_format in ['jpeg']:
                output_format = 'jpg'
            if output_format in ['tif']:
                output_format = 'tiff'
            
            if output_format not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Formato não suportado: {output_format}. Use: {self.SUPPORTED_FORMATS}")
            
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Define diretório de saída (padrão: mesmo diretório do arquivo original)
            if output_dir is None:
                base_name = Path(file_path).stem
                parent_dir = Path(file_path).parent
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = str(parent_dir / f"{base_name}_imagens_{timestamp}")
            
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"Extraindo imagens de {file_path} para {output_dir}")
            
            extracted_images: List[ExtractedImage] = []
            successful = 0
            failed = 0
            image_counter = 0
            metadata_list = []
            
            for page_num in range(total_pages):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_index, img_info in enumerate(image_list):
                    image_counter += 1
                    
                    try:
                        xref = img_info[0]
                        
                        # Extrai imagem
                        base_image = doc.extract_image(xref)
                        
                        if not base_image:
                            failed += 1
                            continue
                        
                        # Dados da imagem
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        width = base_image["width"]
                        height = base_image["height"]
                        colorspace = base_image.get("cs", "Unknown")
                        bpc = base_image.get("bpc", 8)
                        
                        # Processa imagem com PIL para controle de formato e redimensionamento
                        img_stream = BytesIO(image_bytes)
                        
                        try:
                            pil_image = Image.open(img_stream)
                        except Exception:
                            # Se não conseguir abrir com PIL, usa dados brutos
                            pil_image = None
                        
                        # Redimensiona se necessário
                        if not maintain_original_resolution and resize_to:
                            if pil_image:
                                pil_image = pil_image.resize(resize_to, Image.Resampling.LANCZOS)
                                width, height = resize_to
                        
                        # Converte para formato desejado
                        output_filename = f"imagem_{image_counter:04d}.{output_format}"
                        output_path = os.path.join(output_dir, output_filename)
                        
                        if pil_image:
                            # Converte modo se necessário para JPG
                            if output_format == 'jpg' and pil_image.mode in ('RGBA', 'P'):
                                pil_image = pil_image.convert('RGB')
                            
                            # Salva imagem (JPEG usa 'JPEG' não 'JPG')
                            save_kwargs = {}
                            if output_format == 'jpg':
                                save_kwargs['quality'] = 95
                            elif output_format == 'tiff':
                                save_kwargs['compression'] = 'tiff_lzw'
                            
                            # PIL usa JPEG, não JPG
                            pil_format = 'JPEG' if output_format == 'jpg' else output_format.upper()
                            pil_image.save(output_path, format=pil_format, **save_kwargs)
                            final_image_data = open(output_path, 'rb').read()
                        else:
                            # Usa dados brutos convertidos
                            if output_format != image_ext:
                                # Precisa converter
                                if pil_image is None:
                                    # Tenta criar da imagem bruta
                                    img_stream.seek(0)
                                    try:
                                        pil_image = Image.open(img_stream)
                                        if output_format == 'jpg' and pil_image.mode in ('RGBA', 'P'):
                                            pil_image = pil_image.convert('RGB')
                                        pil_image.save(output_path, format=output_format.upper())
                                        final_image_data = open(output_path, 'rb').read()
                                    except:
                                        # Fallback: salva como está
                                        final_image_data = image_bytes
                                        output_filename = f"imagem_{image_counter:04d}.{image_ext}"
                                        output_path = os.path.join(output_dir, output_filename)
                                        with open(output_path, 'wb') as f:
                                            f.write(image_bytes)
                            else:
                                final_image_data = image_bytes
                                with open(output_path, 'wb') as f:
                                    f.write(image_bytes)
                        
                        # Extrai metadados
                        metadata = None
                        if extract_metadata:
                            metadata = ImageMetadata(
                                width=width,
                                height=height,
                                colorspace=str(base_image.get("cs-name", colorspace)),
                                bits_per_component=bpc,
                                xref=xref,
                                page_number=page_num + 1,
                                image_index=img_index + 1,
                                file_size=os.path.getsize(output_path),
                                format=output_format.upper(),
                                dpi=self._calculate_dpi(pil_image) if pil_image else None,
                                additional_info={
                                    'original_format': image_ext,
                                    'pdf_page': page_num + 1,
                                    'image_in_page': img_index + 1
                                }
                            )
                            metadata_list.append(self._metadata_to_dict(metadata))
                        
                        extracted_images.append(ExtractedImage(
                            filename=output_filename,
                            path=output_path,
                            metadata=metadata,
                            image_data=final_image_data,
                            success=True,
                            message="Imagem extraída com sucesso"
                        ))
                        successful += 1
                        
                    except Exception as e:
                        logger.warning(f"Falha ao extrair imagem {image_counter}: {e}")
                        import traceback
                        traceback.print_exc()
                        extracted_images.append(ExtractedImage(
                            filename=f"imagem_{image_counter:04d}.{output_format}",
                            path="",
                            metadata=None,
                            image_data=b"",
                            success=False,
                            message=f"Erro: {str(e)}"
                        ))
                        failed += 1
                    
                    # Atualiza progresso
                    if progress_callback:
                        total_images_estimated = max(image_counter, 1)
                        progress = int((image_counter / max(total_pages * 5, 1)) * 100)
                        progress_callback(min(progress, 95))
                
                # Garbage collection
                if (page_num + 1) % 10 == 0:
                    import gc
                    gc.collect()
            
            doc.close()
            
            # Salva arquivo de metadados
            metadata_file = None
            if extract_metadata and metadata_list:
                metadata_file = os.path.join(output_dir, "metadados_imagens.json")
                import json
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'pdf_source': os.path.basename(file_path),
                        'extraction_date': datetime.now().isoformat(),
                        'total_images': successful,
                        'format': output_format.upper(),
                        'images': metadata_list
                    }, f, indent=2, ensure_ascii=False)
            
            if progress_callback:
                progress_callback(100)
            
            logger.info(f"Extração concluída: {successful} sucesso, {failed} falhas")
            
            return ExtractionResult(
                output_dir=output_dir,
                total_images=successful + failed,
                successful_extractions=successful,
                failed_extractions=failed,
                images=extracted_images,
                metadata_file=metadata_file,
                success=successful > 0,
                message=f"{successful} imagem(s) extraída(s) com sucesso" + (f", {failed} falha(s)" if failed > 0 else "")
            )
            
        except Exception as e:
            logger.exception(f"Erro na extração de imagens: {e}")
            return ExtractionResult(
                output_dir="",
                total_images=0,
                successful_extractions=0,
                failed_extractions=0,
                images=[],
                metadata_file=None,
                success=False,
                message=f"Erro na extração: {str(e)}"
            )
    
    def _calculate_dpi(self, image: Optional[Image.Image]) -> Optional[float]:
        """Calcula DPI da imagem se disponível."""
        if image and hasattr(image, 'info') and 'dpi' in image.info:
            return image.info['dpi'][0]
        return None
    
    def _metadata_to_dict(self, metadata: ImageMetadata) -> Dict:
        """Converte metadados para dicionário serializável."""
        return {
            'width': metadata.width,
            'height': metadata.height,
            'colorspace': metadata.colorspace,
            'bits_per_component': metadata.bits_per_component,
            'xref': metadata.xref,
            'page_number': metadata.page_number,
            'image_index': metadata.image_index,
            'file_size': metadata.file_size,
            'format': metadata.format,
            'dpi': metadata.dpi,
            'creation_date': metadata.creation_date,
            'additional_info': metadata.additional_info
        }
    
    def get_image_count(self, file_path: str) -> Dict[str, int]:
        """
        Conta o número de imagens em um PDF.
        
        Args:
            file_path: Caminho do arquivo PDF.
            
        Returns:
            Dict: Contagem de imagens por página e total.
        """
        try:
            doc = fitz.open(file_path)
            total_images = 0
            pages_with_images = 0
            total_pages = len(doc)
            
            page_counts = {}
            for page_num in range(total_pages):
                page = doc[page_num]
                images = page.get_images(full=True)
                count = len(images)
                page_counts[page_num + 1] = count
                total_images += count
                if count > 0:
                    pages_with_images += 1
            
            doc.close()
            
            return {
                'total_images': total_images,
                'pages_with_images': pages_with_images,
                'total_pages': total_pages,
                'per_page': page_counts
            }
            
        except Exception as e:
            logger.exception(f"Erro ao contar imagens: {e}")
            return {'error': str(e), 'total_images': 0}
