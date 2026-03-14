from pathlib import Path
from typing import Dict, Any, List
import re

import easyocr
import numpy as np
from langdetect import detect_langs
from PIL import Image, ImageFilter, ImageOps


class OCRExtractor:
    def __init__(
        self,
        languages: list[str] | None = None,
        rerun_with_detected_language: bool = False,
        language_detection_threshold: float = 0.9,
        preprocessing_threshold: int | None = None,
        median_filter_size: int = 3,
    ):
        self.languages = languages or ["tr", "en"]
        self.rerun_with_detected_language = rerun_with_detected_language
        self.language_detection_threshold = language_detection_threshold
        self.preprocessing_threshold = preprocessing_threshold
        self.median_filter_size = median_filter_size

        self.readers: dict[tuple[str, ...], easyocr.Reader] = {}
        self.readers[tuple(self.languages)] = easyocr.Reader(self.languages)

    def _preprocess_image(self, image_path: str | Path) -> np.ndarray:
        image_path = Path(image_path)
        img = Image.open(image_path).convert("L")

        # 1) kontrastı artırma
        img = ImageOps.autocontrast(img)

        # 2) hafif gürültü azaltma
        if self.median_filter_size and self.median_filter_size > 0:
            img = img.filter(ImageFilter.MedianFilter(size=self.median_filter_size))

        # 3) threshold uygulama
        if self.preprocessing_threshold is not None:
            img = img.point(lambda p: 255 if p > self.preprocessing_threshold else 0)

        return np.array(img)

    def _normalize_lines(self, lines: List[str]) -> str:
        normalized = []
        for line in lines:
            line = re.sub(r"\s+", " ", line).strip()
            if line:
                normalized.append(line)
        return "\n".join(normalized).strip()

    def _estimate_text_quality(self, text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        if not cleaned:
            return {
                "low_confidence_extraction": True,
                "quality_reason": "empty_text",
                "text_length": 0,
                "suspicious_char_ratio": 1.0,
            }

        total_chars = len(cleaned)
        suspicious_chars = re.findall(
            r"[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ\s\.,:;!?%/\-\(\)\[\]&']",
            cleaned,
        )
        suspicious_ratio = len(suspicious_chars) / max(total_chars, 1)

        low_confidence = total_chars < 20 or suspicious_ratio > 0.15
        reason = "ok"
        if total_chars < 20:
            reason = "too_short"
        elif suspicious_ratio > 0.15:
            reason = "high_suspicious_char_ratio"

        return {
            "low_confidence_extraction": low_confidence,
            "quality_reason": reason,
            "text_length": total_chars,
            "suspicious_char_ratio": round(suspicious_ratio, 4),
        }

    def _get_reader(self, languages: list[str]) -> easyocr.Reader:
        key = tuple(languages)
        if key not in self.readers:
            self.readers[key] = easyocr.Reader(languages)
        return self.readers[key]

    def _detect_language(self, text: str) -> tuple[str, float] | None:
        if detect_langs is None:
            return None
        try:
            langs = detect_langs(text)
        except Exception:
            return None

        if not langs:
            return None

        best = langs[0]
        return best.lang, best.prob

    def _extract_text(
        self,
        source: str | Path | np.ndarray,
        languages: list[str] | None = None,
    ) -> str:
        langs = languages or self.languages
        reader = self._get_reader(langs)

        if isinstance(source, (str, Path)):
            results = reader.readtext(str(source), detail=0, paragraph=False)
        else:
            results = reader.readtext(source, detail=0, paragraph=False)

        return self._normalize_lines(results)

    def extract_text_from_image(self, image_path: str | Path) -> Dict[str, Any]:
        image_path = Path(image_path)

        raw_text = self._extract_text(image_path)
        raw_quality = self._estimate_text_quality(raw_text)

        processed = self._preprocess_image(image_path)
        pre_text = self._extract_text(processed)
        pre_quality = self._estimate_text_quality(pre_text)

        use_preprocessed = (
            pre_quality["suspicious_char_ratio"] <= raw_quality["suspicious_char_ratio"]
            and not pre_quality["low_confidence_extraction"]
        )

        text = pre_text if use_preprocessed else raw_text
        quality = pre_quality if use_preprocessed else raw_quality
        extraction_method = (
            "easyocr_preprocessed_multilang" if use_preprocessed else "easyocr_raw_multilang"
        )
        source_for_rerun = processed if use_preprocessed else image_path

        detected_language = None
        detected_language_prob = None

        if (
            self.rerun_with_detected_language
            and not quality["low_confidence_extraction"]
            and quality["text_length"] >= 80
        ):
            detected = self._detect_language(text)
            if detected:
                lang, prob = detected
                detected_language = lang
                detected_language_prob = prob

                if lang in self.languages and prob >= self.language_detection_threshold:
                    if not (len(self.languages) == 1 and self.languages[0] == lang):
                        rerun_text = self._extract_text(source_for_rerun, [lang])
                        rerun_quality = self._estimate_text_quality(rerun_text)

                        if rerun_quality["suspicious_char_ratio"] <= quality["suspicious_char_ratio"]:
                            text = rerun_text
                            quality = rerun_quality
                            extraction_method = f"easyocr_preprocessed_rerun_{lang}"

        return {
            "page_number": 1,
            "text": text,
            "source_file": image_path.name,
            "extraction_method": extraction_method,
            "detected_language": detected_language,
            "detected_language_prob": detected_language_prob,
            **quality,
        }