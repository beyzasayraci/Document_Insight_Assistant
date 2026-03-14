from __future__ import annotations

import re

# Bu dosya, dil tespiti ve dile bağlı yardımcı işlemleri tek bir yerde toplar.
# OCR/extraction sonrası metnin hangi dilde olduğunu anlamak ve uygun işlem akışını
# seçmek için kullanılır.
TURKISH_CHARS = set("çğıöşüÇĞİÖŞÜ")

TR_COMMON = {
    "ve", "bir", "bu", "belge", "belirtilen", "göre", "için", "olarak",
    "değil", "değildir", "bulunmamaktadır", "bulunuyor", "tarih", "sayfa",
    "dosya", "kaynak", "cevap", "soru", "belirsiz", "açıkça"
}

EN_COMMON = {
    "the", "is", "are", "this", "that", "document", "page", "file",
    "source", "answer", "question", "date", "not", "found", "clear",
    "unclear", "subject", "receipt", "invoice"
}


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]+\b", text.lower()))


def detect_question_language(question: str) -> str:
    q = question.strip()

    if any(ch in TURKISH_CHARS for ch in q):
        return "Turkish"

    words = _tokenize(q)

    tr_score = len(words & TR_COMMON)
    en_score = len(words & EN_COMMON)

    if tr_score > en_score:
        return "Turkish"

    return "English"


def answer_matches_language(text: str, expected_language: str) -> bool:
    words = _tokenize(text)

    tr_score = len(words & TR_COMMON)
    en_score = len(words & EN_COMMON)
    has_tr_chars = any(ch in TURKISH_CHARS for ch in text)

    if expected_language == "English":
        if has_tr_chars:
            return False
        if tr_score > en_score:
            return False
        return True

    if expected_language == "Turkish":
        if has_tr_chars:
            return True
        if tr_score >= en_score:
            return True
        return False

    return True