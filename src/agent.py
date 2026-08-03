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
        # Retrieve top-k relevant chunks
        results = self.store.search(question, top_k=top_k)

        # Build context from retrieved chunks — đánh số [1][2] kèm nguồn (doc_id + file)
        context_parts: list[str] = []
        for i, result in enumerate(results, 1):
            doc_id = result["metadata"].get("doc_id", "unknown")
            source = result["metadata"].get("source", "")
            context_parts.append(
                f"[{i}] (Nguồn: {doc_id} | File: {source})\n{result['content']}"
            )
        context = "\n\n".join(context_parts)

        # Build prompt with context — yêu cầu model trích dẫn bằng [1][2]
        prompt = (
            f"Based on the following context, answer the question.\n"
            f"IMPORTANT: Cite your sources using the reference numbers [1], [2], etc. "
            f"so the answer can be traced back to the correct chunk and file.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )

        # Call LLM and return the answer
        return self.llm_fn(prompt)

