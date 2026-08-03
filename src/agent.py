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
        # Step 1: Retrieve top-k relevant chunks
        results = self.store.search(question, top_k=top_k)

        # Step 2: Build context from retrieved chunks
        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(f"[{i}] {r['content']}")

        context = "\n\n".join(context_parts)

        # Step 3: Build prompt and call LLM
        prompt = (
            "You are a helpful assistant. Use the following context to answer the question.\n"
            "If the answer is not in the context, say 'I don't know'.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        return self.llm_fn(prompt)
