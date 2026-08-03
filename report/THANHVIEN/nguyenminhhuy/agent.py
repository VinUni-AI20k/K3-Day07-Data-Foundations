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

    def __init__(
        self,
        store: EmbeddingStore,
        llm_fn: Callable[[str], str],
    ) -> None:
        self._store = store
        self._llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        retrieved_chunks = self._store.search(
            query=question,
            top_k=top_k,
        )

        context_blocks: list[str] = []

        for index, result in enumerate(retrieved_chunks, start=1):
            metadata = result.get("metadata", {})
            source = (
                metadata.get("source_url")
                or metadata.get("source")
                or "unknown"
            )

            context_blocks.append(
                f"[Chunk {index} | Source: {source}]\n"
                f"{result['content']}"
            )

        context = "\n\n".join(context_blocks)

        if not context:
            context = "No relevant context was retrieved."

        prompt = f"""You are a knowledge-base assistant.

    Answer the question using only the context below.
    If the context does not contain enough information, say that the
    available documents do not provide enough information.
    Do not invent facts.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

        return self._llm_fn(prompt)
