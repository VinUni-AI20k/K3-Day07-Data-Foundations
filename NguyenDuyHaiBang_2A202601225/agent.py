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

    NO_CONTEXT_ANSWER = "Không tìm thấy ngữ cảnh liên quan trong cơ sở tri thức."

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    @staticmethod
    def _source_of(result: dict) -> str:
        metadata = result.get("metadata") or {}
        return str(metadata.get("source_url") or metadata.get("source") or metadata.get("doc_id") or "unknown")

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return self.NO_CONTEXT_ANSWER

        context = "\n\n".join(
            f"[{index}] (score={result['score']:.3f}, source={self._source_of(result)})\n{result['content']}"
            for index, result in enumerate(results, start=1)
        )
        prompt = (
            "Answer the question using ONLY the context below.\n"
            "If the context does not contain the answer, say so instead of guessing.\n"
            "Cite the context number(s) you relied on.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
