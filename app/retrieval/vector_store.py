from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import faiss

#VectorStore, embedding'leri saklamak ve benzerlik araması yapmak için FAISS kütüphanesini kullanır. build_index() yöntemi, verilen embedding'leri normalize eder ve bir FAISS index'i oluşturur. search() yöntemi, bir sorgu embedding'i alır, onu normalize eder ve index'te benzer embedding'leri arar, ardından ilgili metadata ile birlikte sonuçları döndürür. _normalize() yöntemi, embedding'leri normalize etmek için kullanılır. Eğer embedding'ler boşsa, normalize işlemi atlanır.
class VectorStore:
    def __init__(self):
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self.dimension: int | None = None

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        if vectors.size == 0:
            return vectors

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.clip(norms, 1e-12, None)
        return vectors / norms

    def build_index(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        if embeddings.ndim != 2:
            raise ValueError("Embeddings shape (n, dim) olmalı.")
        if len(embeddings) != len(metadata):
            raise ValueError("Embeddings ve metadata uzunlukları eşleşmeli.")
        if len(embeddings) == 0:
            raise ValueError("Boş embedding ile index kurulamaz.")

        embeddings = embeddings.astype(np.float32)
        embeddings = self._normalize(embeddings)

        self.dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings)

        self.metadata = metadata

    def search(self, query_embedding: np.ndarray, top_k: int = 4) -> List[Dict[str, Any]]:
        if self.index is None:
            raise RuntimeError("Index henüz oluşturulmadı.")

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        query_embedding = query_embedding.astype(np.float32)
        query_embedding = self._normalize(query_embedding)

        scores, indices = self.index.search(query_embedding, top_k)

        results: List[Dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            item = dict(self.metadata[idx])
            item["score"] = float(score)
            results.append(item)

        return results