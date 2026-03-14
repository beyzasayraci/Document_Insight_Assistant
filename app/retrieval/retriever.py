from __future__ import annotations

from typing import List, Dict, Any
import json
from pathlib import Path

import numpy as np

from app.retrieval.embedder import Embedder

#InMemoryRetriever, metinleri vektörlere dönüştürmek için Embedder'ı kullanır ve bu vektörleri bellekte tutar. build() yöntemi, verilen metin parçalarını embedder ile vektörlere dönüştürür ve bunları records ile birlikte saklar. retrieve() yöntemi, bir sorgu alır, onun embedding'ini oluşturur ve saklanan embedding'lerle benzerlik skorlarını hesaplayarak en alakalı parçaları döndürür. save() yöntemi ise embedding'leri ve ilgili metin parçalarını belirtilen dizine kaydeder.
class InMemoryRetriever:
    def __init__(self, embedder: Embedder):
        self.embedder = embedder
        self.embeddings: np.ndarray | None = None
        self.records: List[Dict[str, Any]] = []
    
    def build(self, chunks: List[Dict[str, Any]]) -> None:
        if not chunks:
            self.records = []
            self.embeddings = None
            return

        self.records = chunks
        texts = [c["text"] for c in chunks]
        self.embeddings = self.embedder.embed_texts(texts)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.embeddings is None or not self.records:
            raise RuntimeError("Önce build() çağırmalısın.")

        q = self.embedder.embed_query(query)
        scores = self.embeddings @ q
        ranked_idx = np.argsort(scores)[::-1][:top_k]

        results: List[Dict[str, Any]] = []
        for idx in ranked_idx:
            item = dict(self.records[idx])
            item["score"] = float(scores[idx])
            results.append(item)

        return results

    def save(self, out_dir: str) -> None:
        if self.embeddings is None:
            raise RuntimeError("Kaydetmeden önce build() çağırmalısın.")

        out = Path(out_dir).expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)

        np.save(out / "embeddings.npy", self.embeddings)
        (out / "chunks.json").write_text(
            json.dumps(self.records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
