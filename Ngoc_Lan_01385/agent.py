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
        """
        Answer a question using the knowledge base.

        Steps:
            1. Retrieve top-k relevant chunks from the store.
            2. Build a prompt with the chunks as context.
            3. Call the LLM to generate an answer.

        Returns the generated answer as a string.
        """
        # Step 1: Retrieve top-k relevant chunks
        retrieved_chunks = self.store.search_with_filter(question, top_k=top_k)

        # Step 2: Build a prompt with the retrieved chunks
        context = "\n\n".join(chunk["content"] for chunk in retrieved_chunks)
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"

        # Step 3: Call the LLM to generate an answer
        answer = self.llm_fn(prompt)
        return answer
