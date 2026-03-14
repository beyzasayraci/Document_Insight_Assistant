from __future__ import annotations

from typing import List, Dict, Any
import requests

from app.qa.prompt_builder import build_qa_messages


class AnswerService:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "qwen2.5:7b",
        timeout_seconds: int = 120,
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
    #answer() yöntemi, bir soru ve ilgili metin parçalarını alır, bu bilgileri kullanarak bir mesaj dizisi oluşturur ve ardından bu mesajları belirtilen LLM API'sine gönderir. API'den gelen yanıtı işler ve cevabı döndürür. Eğer API yanıtında beklenen formatta bir mesaj yoksa, varsayılan bir cevap döndürülür.   
    def answer(self, question: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        messages = build_qa_messages(question, retrieved_chunks)

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 220,
            },
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        data = response.json()

        answer_text = (
            data.get("message", {}).get("content", "").strip()
            or "This information could not be found in the uploaded documents."
        )

        return {
            "answer": answer_text,
            "messages": messages,
            "raw_response": data,
        }
