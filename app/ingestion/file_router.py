from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Dict, Any

import fitz

from app.config import (
    MIN_PDF_TEXT_LENGTH,
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_PDF_EXTENSIONS,
    GLM_MODEL_DIR,
    OCR_TASK,
)
from app.extraction.pdf_extractor import (
    extract_text_from_pdf,
    pdf_has_meaningful_text,
)
from app.extraction.ocr_extractor import OCRExtractor


class FileRouter:
    def __init__(self):
        self.ocr_extractor = OCRExtractor(
            glm_model_dir=GLM_MODEL_DIR,
            task=OCR_TASK,
        )
    # Tarama yapılmış PDF'ler için OCR çıkarımı yapar.
    def _ocr_scanned_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        #PyMuPDF kullanarak PDF'i sayfa sayfa işleyerek her sayfayı geçici bir görüntü dosyasına dönüştürür ve ardından OCR çıkarımı yapar.
        with fitz.open(pdf_path) as doc, TemporaryDirectory() as tmpdir:
            for page_index, page in enumerate(doc):
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                image_path = Path(tmpdir) / f"page_{page_index + 1}.png"
                pix.save(str(image_path))
                #OCR çıkarımı yapar ve sonuçları sayfa numarası, kaynak dosya adı ve çıkarma yöntemi (OCR) ile birlikte sonuç listesine kaydeder.
                ocr_result = self.ocr_extractor.extract_text_from_image(image_path)
                ocr_result["page_number"] = page_index + 1
                ocr_result["source_file"] = pdf_path.name
                results.append(ocr_result)

        return results
    #Verilen dosya yoluna göre uygun çıkarım yöntemini seçer ve metin çıkarır. Desteklenmeyen dosya türleri için hata fırlatır.
    def route_and_extract(self, file_path: str | Path) -> List[Dict[str, Any]]:
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        #Dosya uzantısına göre uygun çıkarım yöntemini seçer ve metin çıkarır. Desteklenmeyen dosya türleri için hata fırlatır.
        if suffix in SUPPORTED_IMAGE_EXTENSIONS:
            return [self.ocr_extractor.extract_text_from_image(file_path)]

        if suffix in SUPPORTED_PDF_EXTENSIONS:
            if pdf_has_meaningful_text(file_path, min_length=MIN_PDF_TEXT_LENGTH):
                return extract_text_from_pdf(file_path)

            return self._ocr_scanned_pdf(file_path)

        raise ValueError(f"Desteklenmeyen dosya tipi: {suffix}")