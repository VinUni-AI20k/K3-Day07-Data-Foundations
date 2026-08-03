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
        if not question or not question.strip():
            raise ValueError("question must not be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        retrieved_chunks = self.store.search(question, top_k=top_k)

        context_parts: list[str] = []

        for index, result in enumerate(retrieved_chunks, start=1):
            # Support stores that return either plain strings or objects/dicts.
            if isinstance(result, str):
                chunk_text = result
            elif isinstance(result, dict):
                chunk_text = str(
                    result.get("text")
                    or result.get("content")
                    or result.get("chunk")
                    or ""
                )
            else:
                chunk_text = str(
                    getattr(result, "text", None)
                    or getattr(result, "content", None)
                    or result
                )

            if chunk_text.strip():
                context_parts.append(
                    f"[Context {index}]\n{chunk_text.strip()}"
                )

        if not context_parts:
            return (
                "I could not find relevant information in the knowledge base "
                "to answer this question."
            )

        context = "\n\n".join(context_parts)

        prompt = f"""You are a knowledge-base assistant.

Answer the user's question using only the context provided below.
If the context does not contain enough information, clearly say that you do not
have enough information. Do not invent facts.

Context:
{context}

Question:
{question.strip()}

Answer:
"""

        return self.llm_fn(prompt)