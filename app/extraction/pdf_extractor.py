from pathlib import Path
from typing import List, Dict, Any

import fitz


def extract_text_from_pdf(pdf_path: str | Path) -> List[Dict[str, Any]]:
    #PDF dosyasından metin çıkarın ve sayfa numarası, metin, kaynak dosya adı ve çıkarma yöntemini içeren sözlüklerden oluşan bir liste döndürün.
    pdf_path = Path(pdf_path)
    results: List[Dict[str, Any]] = []
    #PyMuPDF kullanarak PDF'den metin çıkarma
    doc = fitz.open(pdf_path)

    try:
        for page_index, page in enumerate(doc):
            #Geçerli sayfadan metni çıkarın ve meta verilerle birlikte sonuç listesine kaydedin.
            text = page.get_text("text")
            #Sayfa numarasını + kaynak dosya adını + çıkarma yöntemini (pymupdf) ekler.
            results.append(
                {
                    "page_number": page_index + 1,
                    "text": text.strip(),
                    "source_file": pdf_path.name,
                    "extraction_method": "pymupdf",
                }
            )
    finally:
        doc.close()

    return results

def extract_full_text_from_pdf(pdf_path: str | Path) -> str:
    #PDF dosyasının tüm sayfalarındaki metinler "\n\n" kullanılarak birleştirilir ve tek bir dizeye dönüştürülür.
    pages = extract_text_from_pdf(pdf_path)
    return "\n\n".join(page["text"] for page in pages if page["text"])

#PDF'den çıkarılan toplam metin 30 karakter veya daha fazlaysa:
#Doğru döndürür → PDF "anlamlı" metin içerir.
#30'dan az ise:
#Yanlış döndürür → PDF büyük olasılıkla taranmış/resim içeriyor veya boş (veya çok kısa).
def pdf_has_meaningful_text(pdf_path: str | Path, min_length: int = 30) -> bool:
    text = extract_full_text_from_pdf(pdf_path)
    return len(text.strip()) >= min_length