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
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        retrieved = self.store.search(question, top_k=top_k)
        if not retrieved:
            return "Không có thông tin trong tài liệu"

        context_sections = []
        for index, item in enumerate(retrieved, start=1):
            context_sections.append(f"Chunk {index}: {item['content']}")

        context = "\n\n".join(context_sections)
        prompt = (
            "Bạn là một trợ lý thông minh. Hãy trả lời câu hỏi chỉ dựa trên ngữ cảnh dưới đây. "
            "Nếu không tìm thấy thông tin liên quan, hãy trả lời: \"Không có thông tin trong tài liệu\".\n\n"
            f"[Ngữ cảnh]\n{context}\n\n[Câu hỏi]\n{question}"
        )
        return self.llm_fn(prompt)
