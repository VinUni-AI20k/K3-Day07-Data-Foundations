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
        results = self.store.search(question, top_k=top_k)
        context_parts = []
        for result in results:
            content = result.get("content", "")
            if content:
                context_parts.append(content)
        context = "\n\n---\n\n".join(context_parts) or "(Không tìm thấy ngữ cảnh phù hợp.)"

        prompt = (
            "Bạn là trợ lý trả lời câu hỏi dựa trên ngữ cảnh được truy xuất. "
            "Chỉ sử dụng thông tin trong ngữ cảnh; nếu không đủ thông tin, "
            "hãy nói rõ rằng không tìm thấy câu trả lời trong tài liệu.\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n\n"
            "Câu trả lời:"
        )
        return self.llm_fn(prompt)
