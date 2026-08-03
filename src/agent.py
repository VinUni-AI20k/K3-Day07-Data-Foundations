from typing import Callable

from .store import EmbeddingStore

PROMPT_TEMPLATE = """Bạn là trợ lý trả lời câu hỏi dựa trên tài liệu được cung cấp.

Chỉ dùng thông tin trong NGỮ CẢNH dưới đây. Nếu ngữ cảnh không đủ để trả lời,
hãy nói rõ "Không tìm thấy thông tin trong tài liệu" thay vì suy đoán.
Khi trả lời, ghi rõ đã dựa vào nguồn nào (số thứ tự / source).

NGỮ CẢNH:
{context}

CÂU HỎI: {question}

TRẢ LỜI:"""

NO_CONTEXT = "(không truy xuất được tài liệu nào liên quan)"


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
        self.last_results: list[dict] = []  # giữ lại để truy vết nguồn sau khi trả lời

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        self.last_results = results
        prompt = PROMPT_TEMPLATE.format(
            context=self._build_context(results),
            question=question,
        )
        return self.llm_fn(prompt)

    @staticmethod
    def _build_context(results: list[dict]) -> str:
        """Ghép các chunk truy xuất được thành ngữ cảnh có đánh số + nguồn (để grounding)."""
        if not results:
            return NO_CONTEXT

        blocks = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata") or {}
            source = metadata.get("source") or metadata.get("source_url") or metadata.get("doc_id", "n/a")
            blocks.append(
                f"[{index}] source={source} score={result.get('score', 0.0):.3f}\n{result.get('content', '')}"
            )
        return "\n\n".join(blocks)
