from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        # Tách câu dựa trên ". ", "! ", "? " hoặc ".\n"
        # Dùng re.split với pattern giữ lại dấu câu
        parts = re.split(r'(?<=[.!?])\s+|(?<=\.)\n', text)

        # Lọc bỏ các phần rỗng
        sentences = [s.strip() for s in parts if s.strip()]

        if not sentences:
            return [text.strip()]

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk_text = " ".join(group).strip()
            if chunk_text:
                chunks.append(chunk_text)

        return chunks if chunks else [text.strip()]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, list(self.separators))

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Base case: văn bản đã đủ nhỏ
        if len(current_text) <= self.chunk_size:
            return [current_text] if current_text else []

        # Base case: không còn separator nào
        if not remaining_separators:
            # Chia thô theo chunk_size
            result = []
            for i in range(0, len(current_text), self.chunk_size):
                part = current_text[i : i + self.chunk_size]
                if part:
                    result.append(part)
            return result

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # Thử tách theo separator hiện tại
        if separator == "":
            # Separator rỗng: chia từng ký tự (chỉ dùng khi không còn lựa chọn)
            parts = list(current_text)
        else:
            parts = current_text.split(separator)

        if len(parts) <= 1:
            # Không tách được, thử separator tiếp theo
            return self._split(current_text, next_separators)

        # Gộp các phần nhỏ lại thành chunks, nếu phần nào quá lớn thì chia đệ quy
        result: list[str] = []
        current_chunk = ""

        for i, part in enumerate(parts):
            # Thêm separator lại (trừ phần cuối)
            segment = part if i == len(parts) - 1 else part + separator

            if len(current_chunk) + len(segment) <= self.chunk_size:
                current_chunk += segment
            else:
                # Lưu chunk hiện tại nếu có
                if current_chunk.strip():
                    result.append(current_chunk.rstrip(separator))
                current_chunk = segment

                # Nếu segment đơn lẻ cũng quá lớn, chia đệ quy
                if len(segment) > self.chunk_size:
                    sub_chunks = self._split(segment, next_separators)
                    result.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1] if sub_chunks else ""

        if current_chunk.strip():
            result.append(current_chunk.rstrip(separator))

        return [c for c in result if c]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = _dot(vec_a, vec_b)
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(x * x for x in vec_b))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot_product / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        result = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count > 0 else 0.0
            result[name] = {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks,
            }

        return result
