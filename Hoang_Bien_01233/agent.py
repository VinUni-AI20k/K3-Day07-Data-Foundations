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
        relevant_chunks = self.store.search(question, top_k=top_k)

        context_texts = [f"- {chunk['content']}" for chunk in relevant_chunks]
        context = "\n".join(context_texts)
        
        prompt = (
            f"Sử dụng thông tin được cung cấp dưới đây để trả lời câu hỏi.\n\n"
            f"Thông tin:\n{context}\n\n"
            f"Câu hỏi: {question}\n"
            f"Trả lời:"
        )
        
        # 3. Call LLM
        return self.llm_fn(prompt)