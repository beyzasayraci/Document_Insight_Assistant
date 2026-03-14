from __future__ import annotations

from typing import List, Dict, Any
import re


class TextChunker:
    def __init__(
        self,
        target_chunk_size: int = 1200,
        max_chunk_size: int = 1600,
        chunk_overlap: int = 200,
        min_chunk_size: int = 150,
    ):
        if min_chunk_size >= target_chunk_size:
            raise ValueError("min_chunk_size, target_chunk_size'dan küçük olmalı.")
        if target_chunk_size > max_chunk_size:
            raise ValueError("target_chunk_size, max_chunk_size'dan büyük olamaz.")
        if chunk_overlap >= target_chunk_size:
            raise ValueError("chunk_overlap, target_chunk_size'dan küçük olmalı.")

        self.target_chunk_size = target_chunk_size
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    #Metni normalize eder, gereksiz boşlukları temizler ve satır sonlarını standartlaştırır.
    def _normalize_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
    #Metni paragraflara böler, her paragrafı normalize eder ve boş paragrafları filtreler.
    def _split_paragraphs(self, text: str) -> List[str]:
        text = self._normalize_text(text)
        if not text:
            return []
        paragraphs = [p.strip() for p in text.split("\n\n")]
        return [p for p in paragraphs if p]
    #Metni nokta, soru işareti veya ünlem işaretlerinden sonra bölerek cümlelere ayırır. Eğer cümleler çok uzun ise kelime bazında bölme yapar.
    def _split_sentences(self, text: str) -> List[str]:
        text = text.strip()
        if not text:
            return []
        parts = re.split(r"(?<=[\.\?!])\s+", text)
        return [p.strip() for p in parts if p.strip()]
    #Uzun metinleri kelime bazında bölerek daha küçük parçalara ayırır. Her parça target_chunk_size'ı aşmamalıdır.
    def _split_long_text_by_words(self, text: str) -> List[str]:
        words = text.split()
        if not words:
            return []

        pieces: List[str] = []
        current = ""

        for word in words:
            candidate = word if not current else f"{current} {word}"
            if len(candidate) <= self.target_chunk_size:
                current = candidate
            else:
                if current.strip():
                    pieces.append(current.strip())
                current = word

        if current.strip():
            pieces.append(current.strip())

        return pieces
    #Paragrafı cümlelere bölerek veya gerekirse kelime bazında bölerek daha küçük parçalara ayırır. Her parça target_chunk_size'ı aşmamalıdır. Parçalar daha sonra chunk'lara dönüştürülürken overlap ve minimum boyut kurallarına göre birleştirilebilir veya ayrılabilir.
    def _paragraph_to_units(self, paragraph: str) -> List[str]:
        paragraph = paragraph.strip()
        if not paragraph:
            return []

        if len(paragraph) <= self.target_chunk_size:
            return [paragraph]

        sentences = self._split_sentences(paragraph)
        if not sentences:
            return self._split_long_text_by_words(paragraph)

        units: List[str] = []
        current = ""

        for sentence in sentences:
            candidate = sentence if not current else f"{current} {sentence}"

            if len(candidate) <= self.target_chunk_size:
                current = candidate
                continue

            if current.strip():
                units.append(current.strip())

            if len(sentence) > self.max_chunk_size:
                units.extend(self._split_long_text_by_words(sentence))
                current = ""
            else:
                current = sentence

        if current.strip():
            units.append(current.strip())

        return units

    def _text_to_units(self, text: str) -> List[str]:
        paragraphs = self._split_paragraphs(text)
        units: List[str] = []

        for paragraph in paragraphs:
            units.extend(self._paragraph_to_units(paragraph))

        return [u for u in units if u.strip()]
    #chunk'lar arasında overlap oluşturmak için birimlerin sonundan başlayarak chunk_overlap karakter uzunluğunda birim seçer. Bu, sonraki chunk'ın başlangıcında bu birimlerin tekrar kullanılmasını sağlar. Eğer overlap için yeterli birim yoksa mevcut birimleri kullanır.
    def _collect_overlap_units(self, units: List[str]) -> List[str]:
        if not units:
            return []

        selected: List[str] = []
        total_len = 0

        for unit in reversed(units):
            unit_len = len(unit)

            if total_len + unit_len > self.chunk_overlap and selected:
                break

            selected.insert(0, unit)
            total_len += unit_len

            if total_len >= self.chunk_overlap:
                break

        return selected
    #Uzunluğu target_chunk_size'ı aşmayan chunk'lar oluşturur. Eğer chunk çok küçükse, bir sonraki chunk ile birleştirilir (max_chunk_size'ı aşmamak kaydıyla). Chunk'lar arasında chunk_overlap kadar overlap bırakılır.
    def _merge_small_chunks(self, chunks: List[str]) -> List[str]:
        if not chunks:
            return []

        merged: List[str] = []

        for chunk in chunks:
            if not merged:
                merged.append(chunk)
                continue

            if (
                len(chunk) < self.min_chunk_size
                and len(merged[-1]) + len(chunk) + 2 <= self.max_chunk_size
            ):
                merged[-1] = f"{merged[-1]}\n\n{chunk}".strip()
            else:
                merged.append(chunk)

        return merged

    def _units_to_chunks(self, units: List[str]) -> List[str]:
        if not units:
            return []

        chunks: List[str] = []
        current_units: List[str] = []

        for unit in units:
            if not current_units:
                current_units = [unit]
                continue

            candidate = "\n\n".join(current_units + [unit])

            if len(candidate) <= self.target_chunk_size:
                current_units.append(unit)
                continue

            chunk_text = "\n\n".join(current_units).strip()
            if chunk_text:
                chunks.append(chunk_text)

            overlap_units = self._collect_overlap_units(current_units)
            candidate_units = overlap_units + [unit]
            candidate_text = "\n\n".join(candidate_units).strip()

            if len(candidate_text) > self.max_chunk_size:
                current_units = [unit]
            else:
                current_units = candidate_units

        if current_units:
            chunk_text = "\n\n".join(current_units).strip()
            if chunk_text:
                chunks.append(chunk_text)

        return self._merge_small_chunks(chunks)

    def chunk_text(self, text: str) -> List[str]:
        text = self._normalize_text(text)
        if not text:
            return []

        units = self._text_to_units(text)
        chunks = self._units_to_chunks(units)

        return [chunk.strip() for chunk in chunks if chunk.strip()]
    #Verilen sayfa metnini chunk'lara böler. Her chunk, sayfa numarası, kaynak dosya adı, çıkarma yöntemi ve karakter uzunluğu gibi metadata ile birlikte bir sözlük olarak döndürülür. Chunk'lar target_chunk_size'ı aşmamalıdır ve gerektiğinde chunk_overlap kadar overlap içerebilir.
    def chunk_document_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_chunks: List[Dict[str, Any]] = []

        for page in pages:
            page_text = page.get("text", "")
            page_number = page.get("page_number")
            source_file = page.get("source_file")
            extraction_method = page.get("extraction_method")

            text_chunks = self.chunk_text(page_text)

            for local_idx, chunk_text in enumerate(text_chunks, start=1):
                chunk_id = f"{source_file}_p{page_number}_c{local_idx}"

                all_chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "text": chunk_text,
                        "source_file": source_file,
                        "page_number": page_number,
                        "chunk_index": local_idx,
                        "extraction_method": extraction_method,
                        "char_length": len(chunk_text),
                    }
                )

        return all_chunks