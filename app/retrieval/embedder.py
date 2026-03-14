from __future__ import annotations

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    #Embedder, metinleri vektörlere dönüştürmek için SentenceTransformer modelini kullanır. embed_texts() metni bir liste olarak alır ve her metin için bir embedding döndürür. embed_query() ise tek bir sorgu metni alır ve onun embedding'ini döndürür. Her iki yöntem de embedding'leri normalize eder ve float32 formatında numpy dizisi olarak döndürür.
    def __init__(self, model_name_or_path: str = "BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name_or_path)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        emb = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return emb.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        emb = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return emb[0].astype(np.float32)