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
        # Lưu tham chiếu đến store và llm_fn
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # Bước 1: Truy xuất các chunks liên quan nhất từ store
        results = self.store.search(question, top_k=top_k)

        # Bước 2: Xây dựng prompt với ngữ cảnh từ các chunks
        if results:
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(f"[Chunk {i}]: {result['content']}")
            context = "\n".join(context_parts)
        else:
            context = "Không có thông tin liên quan."

        prompt = (
            f"Dựa vào các đoạn văn bản sau đây:\n\n"
            f"{context}\n\n"
            f"Hãy trả lời câu hỏi: {question}"
        )

        # Bước 3: Gọi LLM để sinh câu trả lời
        return self.llm_fn(prompt)
