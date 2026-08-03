from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self._store = store
        self._llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # Retrieve top-k relevant chunks from the store
        results = self._store.search(question, top_k=top_k)
        # Build context from retrieved chunks
        context_parts = []
        for r in results:
            source = r.get("metadata", {}).get("source", "unknown")
            context_parts.append(f"[{source}] {r['content']}")
        context = "\n".join(context_parts)
        # Build RAG prompt
        prompt = (
            f"Dựa trên ngữ cảnh sau đây, hãy trả lời câu hỏi.\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n\n"
            f"Trả lời:"
        )
        return self._llm_fn(prompt)
