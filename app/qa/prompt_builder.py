from __future__ import annotations

from typing import List, Dict, Any


def build_qa_messages(
    question: str,
    retrieved_chunks: List[Dict[str, Any]],
    answer_language: str,
) -> list[dict]:
    context_parts = []

    for i, chunk in enumerate(retrieved_chunks, start=1):
        context_parts.append(
            f"""[Source {i}]
File: {chunk.get("source_file")}
Page: {chunk.get("page_number")}
Chunk ID: {chunk.get("chunk_id")}
Text:
{chunk.get("text", "").strip()}"""
        )

    context = "\n\n".join(context_parts).strip()

    system_prompt = f"""
You are a document question-answering assistant.

Rules:
- Answer only from the provided retrieved document chunks.
- Do not invent, assume, or infer unsupported facts.
- Use only one language in the final answer.
- The final answer must be entirely in {answer_language}.
- Never use any other language in the final answer.
- Keep the answer concise, clear, and grounded in the document.
- Prefer a short answer first, then a brief explanation if needed.
- If the retrieved context does not explicitly support the answer, say that clearly.
- If the user's assumption is incorrect, correct it explicitly.
- If the exact answer is not available but closely related evidence exists, provide that evidence and explain the limitation.
- Distinguish between the document's core metadata/content and incidental mentions in the body, references, footnotes, bibliography, or citations.
- If the question asks for a list (such as references, citations, names, items, sources, or entities), extract as many relevant items as possible from all provided context chunks.
- Do not stop after only a few examples if more relevant items are clearly visible in the retrieved context.
- Prefer explicit evidence over guesswork.
- When possible, mention the source file name and page number.
""".strip()

    user_prompt = f"""
Question:
{question}

Retrieved document context:
{context}

Instructions:
1. First determine whether the answer is explicitly supported by the retrieved context.
2. If it is supported, answer clearly and briefly.
3. If it is not fully supported, say that clearly and provide the closest relevant evidence from the context.
4. Answer only in {answer_language}.
5. Do not use any other language in the final answer.
6. If the question asks for a list, gather all relevant items visible across all retrieved chunks.

FINAL ANSWER LANGUAGE: {answer_language.upper()} ONLY
""".strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]