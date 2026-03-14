from __future__ import annotations

from typing import List, Dict, Any
import requests

from app.qa.prompt_builder import build_qa_messages
from app.utils.language_utils import detect_question_language, answer_matches_language


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

    def _chat(self, messages: list[dict]) -> Dict[str, Any]:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 300,
            },
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def _rewrite_in_language(self, text: str, target_language: str) -> str:
        rewrite_messages = [
            {
                "role": "system",
                "content": (
                    f"You are a rewriting assistant. "
                    f"Rewrite the given answer strictly in {target_language}. "
                    f"Do not add new information. "
                    f"Do not remove important meaning. "
                    f"Output only the rewritten answer. "
                    f"Use only {target_language}."
                ),
            },
            {
                "role": "user",
                "content": f"Rewrite this answer strictly in {target_language}:\n\n{text}",
            },
        ]

        data = self._chat(rewrite_messages)
        return data.get("message", {}).get("content", "").strip()

    def answer(self, question: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        answer_language = detect_question_language(question)
        messages = build_qa_messages(question, retrieved_chunks, answer_language)

        data = self._chat(messages)

        answer_text = (
            data.get("message", {}).get("content", "").strip()
            or "This information could not be found in the uploaded documents."
        )

        rewritten = False

        if not answer_matches_language(answer_text, answer_language):
            rewritten_answer = self._rewrite_in_language(answer_text, answer_language)
            if rewritten_answer:
                answer_text = rewritten_answer
                rewritten = True

        return {
            "answer": answer_text,
            "messages": messages,
            "raw_response": data,
            "answer_language": answer_language,
            "rewritten_for_language": rewritten,
        }